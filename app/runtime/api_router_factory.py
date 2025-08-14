"""
APIRouterFactory: Core component for dynamically constructing FastAPI endpoints.
Creates FastAPI endpoints per plugin per tool using schemas and method signatures.
"""

import inspect
from typing import Dict, Any, Optional, Callable, Type, Union
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, create_model, Field
import logging
import json

from app.runtime.plugin_descriptor import PluginDescriptor
from app.runtime.json_schema_validator import JSONSchemaValidator
from app.runtime.result_serializer import ResultSerializer

logger = logging.getLogger(__name__)


class APIRouterFactory:
    """
    Dynamically constructs FastAPI endpoints for plugin tools.
    
    Responsibilities:
    - Generate FastAPI routers for plugins
    - Create endpoints for each tool in a plugin
    - Handle request/response validation and serialization
    - Support streaming and non-streaming tool execution
    - Integrate with plugin instance management
    """
    
    def __init__(self, base_path: str = "/plugins"):
        """
        Initialize APIRouterFactory.
        
        Args:
            base_path: Base path prefix for all plugin endpoints
        """
        self.base_path = base_path.rstrip('/')
        self.validator = JSONSchemaValidator()
        self.serializer = ResultSerializer()
        self.created_routers: Dict[str, APIRouter] = {}
        
    def create_plugin_router(
        self, 
        plugin_descriptor: PluginDescriptor,
        router_prefix: Optional[str] = None
    ) -> APIRouter:
        """
        Create a FastAPI router for a specific plugin.
        
        Args:
            plugin_descriptor: Plugin descriptor containing metadata and tools
            router_prefix: Optional custom prefix for the router
            
        Returns:
            FastAPI APIRouter configured for the plugin
        """
        plugin_name = plugin_descriptor.name
        prefix = router_prefix or f"{self.base_path}/{plugin_name}"
        
        router = APIRouter(
            prefix=prefix,
            tags=[f"plugin:{plugin_name}"],
            responses={
                404: {"description": "Plugin or tool not found"},
                422: {"description": "Validation error"},
                500: {"description": "Internal server error"}
            }
        )
        
        # Add plugin info endpoint
        self._add_plugin_info_endpoint(router, plugin_descriptor)
        
        # Create endpoints for each tool
        for tool_name, tool_schema in plugin_descriptor.get_all_tool_schemas().items():
            self._add_tool_endpoint(router, plugin_descriptor, tool_name, tool_schema)
        
        # Store the created router
        self.created_routers[plugin_name] = router
        
        logger.info(f"Created API router for plugin '{plugin_name}' with {len(plugin_descriptor.get_tool_names())} tools")
        return router
    
    def _add_plugin_info_endpoint(self, router: APIRouter, plugin_descriptor: PluginDescriptor):
        """Add an info endpoint for the plugin."""
        
        @router.get("/info", summary=f"Get {plugin_descriptor.name} plugin information")
        async def get_plugin_info():
            """Get plugin metadata and available tools."""
            return {
                "plugin": plugin_descriptor.to_dict(),
                "status": "available" if plugin_descriptor.is_configured else "needs_configuration",
                "tools": list(plugin_descriptor.get_tool_names())
            }
    
    def _add_tool_endpoint(
        self, 
        router: APIRouter, 
        plugin_descriptor: PluginDescriptor, 
        tool_name: str, 
        tool_schema: Dict[str, Any]
    ):
        """Add an endpoint for a specific tool."""
        
        # Create Pydantic models for request/response validation
        input_model = self._create_pydantic_model_from_schema(
            tool_schema.get('input_schema', {}),
            f"{plugin_descriptor.name}_{tool_name}_Input"
        )
        
        # Determine if this tool supports streaming
        tool_metadata = tool_schema.get('metadata')
        supports_streaming = (tool_metadata and 
                            hasattr(tool_metadata, 'stream_func_name') and 
                            tool_metadata.stream_func_name)
        
        # Create the endpoint handler
        async def tool_endpoint(
            request_data: input_model,
            request: Request,
            stream: bool = False
        ):
            """Execute plugin tool."""
            try:
                # Convert Pydantic model to dict
                input_data = request_data.dict() if hasattr(request_data, 'dict') else {}
                
                # Validate input data
                if not plugin_descriptor.validate_tool_input(tool_name, input_data):
                    raise HTTPException(
                        status_code=422, 
                        detail=f"Invalid input data for tool '{tool_name}'"
                    )
                
                # Check if plugin is configured
                if not plugin_descriptor.is_configured:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Plugin '{plugin_descriptor.name}' is not configured"
                    )
                
                # Handle streaming vs non-streaming execution
                if stream and supports_streaming:
                    return await self._handle_streaming_tool_call(
                        plugin_descriptor, tool_name, input_data, tool_metadata
                    )
                else:
                    return await self._handle_regular_tool_call(
                        plugin_descriptor, tool_name, input_data
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error executing tool '{tool_name}' on plugin '{plugin_descriptor.name}': {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Configure endpoint path and method
        endpoint_path = f"/{tool_name}"
        description = tool_schema.get('description', f"Execute {tool_name} tool")
        
        # Add the endpoint to the router
        router.add_api_route(
            endpoint_path,
            tool_endpoint,
            methods=["POST"],
            summary=f"Execute {tool_name}",
            description=description,
            response_model=None,  # Dynamic response model
            status_code=200
        )
        
        # Add streaming endpoint if supported
        if supports_streaming:
            
            @router.post(f"/{tool_name}/stream", summary=f"Stream {tool_name}")
            async def stream_tool_endpoint(request_data: input_model):
                """Execute plugin tool with streaming response."""
                return await tool_endpoint(request_data, None, stream=True)
        
        logger.debug(f"Added endpoint for tool '{tool_name}' in plugin '{plugin_descriptor.name}'")
    
    async def _handle_regular_tool_call(
        self, 
        plugin_descriptor: PluginDescriptor, 
        tool_name: str, 
        input_data: Dict[str, Any]
    ) -> JSONResponse:
        """Handle regular (non-streaming) tool execution."""
        
        try:
            # Execute the tool
            result = plugin_descriptor.call_tool(tool_name, **input_data)
            
            # Serialize the result
            serialized_result = self.serializer.serialize(result)
            
            return JSONResponse(
                content={
                    "success": True,
                    "result": serialized_result,
                    "tool": tool_name,
                    "plugin": plugin_descriptor.name
                },
                status_code=200
            )
            
        except Exception as e:
            logger.error(f"Error in regular tool call: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_streaming_tool_call(
        self, 
        plugin_descriptor: PluginDescriptor, 
        tool_name: str, 
        input_data: Dict[str, Any],
        tool_metadata: Any
    ) -> StreamingResponse:
        """Handle streaming tool execution."""
        
        try:
            instance = plugin_descriptor.get_instance()
            if not instance:
                raise HTTPException(status_code=400, detail="Plugin not configured")
            
            # Get the streaming method
            stream_method_name = tool_metadata.stream_func_name
            if not hasattr(instance, stream_method_name):
                raise HTTPException(
                    status_code=500, 
                    detail=f"Streaming method '{stream_method_name}' not found"
                )
            
            stream_method = getattr(instance, stream_method_name)
            
            # Create streaming generator
            async def generate_stream():
                try:
                    # Execute streaming method
                    stream_result = stream_method(**input_data)
                    
                    # Handle different types of streaming results
                    if inspect.isasyncgen(stream_result):
                        # Async generator
                        async for chunk in stream_result:
                            serialized_chunk = self.serializer.serialize(chunk)
                            yield f"data: {json.dumps(serialized_chunk)}\n\n"
                    elif inspect.isgenerator(stream_result):
                        # Regular generator
                        for chunk in stream_result:
                            serialized_chunk = self.serializer.serialize(chunk)
                            yield f"data: {json.dumps(serialized_chunk)}\n\n"
                    else:
                        # Single result, treat as one chunk
                        serialized_result = self.serializer.serialize(stream_result)
                        yield f"data: {json.dumps(serialized_result)}\n\n"
                    
                except Exception as e:
                    error_data = {"error": str(e), "type": e.__class__.__name__}
                    yield f"data: {json.dumps(error_data)}\n\n"
                finally:
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in streaming tool call: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _create_pydantic_model_from_schema(
        self, 
        json_schema: Dict[str, Any], 
        model_name: str
    ) -> Type[BaseModel]:
        """Create a Pydantic model from a JSON schema."""
        
        try:
            if not json_schema or json_schema.get('type') != 'object':
                # Return a basic model for empty or non-object schemas
                return create_model(model_name, **{})
            
            # Extract properties and create field definitions
            properties = json_schema.get('properties', {})
            required_fields = set(json_schema.get('required', []))
            
            field_definitions = {}
            
            for field_name, field_schema in properties.items():
                # Determine field type
                field_type = self._json_type_to_python_type(field_schema)
                
                # Create field with description and default
                field_info = Field(
                    description=field_schema.get('description', ''),
                    example=field_schema.get('example')
                )
                
                # Handle required vs optional fields
                if field_name in required_fields:
                    field_definitions[field_name] = (field_type, field_info)
                else:
                    # Make optional with default
                    default_value = field_schema.get('default')
                    if default_value is not None:
                        field_definitions[field_name] = (field_type, default_value)
                    else:
                        field_definitions[field_name] = (Optional[field_type], None)
            
            # Create and return the model
            return create_model(model_name, **field_definitions)
            
        except Exception as e:
            logger.warning(f"Failed to create Pydantic model from schema: {e}")
            # Return a basic model as fallback
            return create_model(model_name, **{})
    
    def _json_type_to_python_type(self, field_schema: Dict[str, Any]) -> Type:
        """Convert JSON schema type to Python type."""
        
        json_type = field_schema.get('type', 'string')
        
        type_mapping = {
            'string': str,
            'integer': int,
            'number': float,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        python_type = type_mapping.get(json_type, str)
        
        # Handle array items
        if json_type == 'array' and 'items' in field_schema:
            item_type = self._json_type_to_python_type(field_schema['items'])
            return list  # TODO: Could be improved to List[item_type]
        
        return python_type
    
    def get_router(self, plugin_name: str) -> Optional[APIRouter]:
        """
        Get the created router for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            APIRouter or None if not found
        """
        return self.created_routers.get(plugin_name)
    
    def get_all_routers(self) -> Dict[str, APIRouter]:
        """
        Get all created routers.
        
        Returns:
            Dictionary mapping plugin names to their routers
        """
        return self.created_routers.copy()
    
    def remove_router(self, plugin_name: str) -> bool:
        """
        Remove a router for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if removed, False if not found
        """
        if plugin_name in self.created_routers:
            del self.created_routers[plugin_name]
            logger.info(f"Removed router for plugin: {plugin_name}")
            return True
        return False
    
    def update_plugin_router(self, plugin_descriptor: PluginDescriptor) -> APIRouter:
        """
        Update or recreate a router for a plugin.
        
        Args:
            plugin_descriptor: Updated plugin descriptor
            
        Returns:
            New APIRouter for the plugin
        """
        plugin_name = plugin_descriptor.name
        
        # Remove existing router if present
        self.remove_router(plugin_name)
        
        # Create new router
        return self.create_plugin_router(plugin_descriptor)
    
    def create_combined_router(self, plugin_descriptors: Dict[str, PluginDescriptor]) -> APIRouter:
        """
        Create a combined router including all plugins.
        
        Args:
            plugin_descriptors: Dictionary of plugin descriptors
            
        Returns:
            Combined APIRouter with all plugin endpoints
        """
        main_router = APIRouter()
        
        # Add individual plugin routers
        for plugin_name, descriptor in plugin_descriptors.items():
            plugin_router = self.create_plugin_router(descriptor)
            main_router.include_router(plugin_router)
        
        # Add a general plugins list endpoint
        @main_router.get(f"{self.base_path}", summary="List all available plugins")
        async def list_plugins():
            """Get list of all loaded plugins and their status."""
            plugins_info = {}
            
            for name, descriptor in plugin_descriptors.items():
                plugins_info[name] = {
                    "name": name,
                    "description": descriptor.metadata.description,
                    "category": descriptor.metadata.category,
                    "tools": descriptor.get_tool_names(),
                    "is_configured": descriptor.is_configured,
                    "endpoint_prefix": f"{self.base_path}/{name}"
                }
            
            return {
                "plugins": plugins_info,
                "total_count": len(plugins_info),
                "base_path": self.base_path
            }
        
        return main_router
