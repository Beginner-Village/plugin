"""
PluginDescriptor: Core component for storing plugin information and managing instances.
Stores plugin class, metadata, config schema, tool schemas, and live instance reference.
"""

import inspect
from typing import Dict, Optional, Any, Type, List
from dataclasses import dataclass, field
import logging

from hiagent_plugin_sdk.schema import Metadata, ToolMetadata
from hiagent_plugin_sdk.utils import get_fn_schema

logger = logging.getLogger(__name__)


@dataclass
class PluginInstanceConfig:
    """Configuration for a plugin instance."""
    config_data: Dict[str, Any] = field(default_factory=dict)
    instance_id: str = ""
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None


class PluginDescriptor:
    """
    Stores comprehensive information about a plugin and manages its lifecycle.
    
    Responsibilities:
    - Hold plugin class reference and metadata
    - Extract and store tool schemas from plugin methods
    - Manage plugin instance lifecycle
    - Validate plugin configuration
    - Provide access to plugin tools and their schemas
    """
    
    def __init__(
        self, 
        name: str, 
        plugin_class: Type[Any], 
        metadata: Metadata,
        wheel_info: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize PluginDescriptor.
        
        Args:
            name: Plugin name
            plugin_class: The plugin class
            metadata: Plugin metadata from wheel
            wheel_info: Information about the source wheel
        """
        self.name = name
        self.plugin_class = plugin_class
        self.metadata = metadata
        self.wheel_info = wheel_info or {}
        
        # Plugin instance management
        self.instance: Optional[Any] = None
        self.instance_config: Optional[PluginInstanceConfig] = None
        self.is_configured = False
        
        # Tool schemas (extracted from plugin methods)
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Configuration schema
        self.config_schema: Dict[str, Any] = metadata.config_schema or {}
        
        # Extract tool information from plugin class
        self._extract_tool_schemas()
        
    def _extract_tool_schemas(self):
        """Extract tool schemas from plugin class methods."""
        try:
            # Get all public methods from the plugin class
            for method_name, method in inspect.getmembers(self.plugin_class, inspect.isfunction):
                # Skip private methods and common object methods
                if method_name.startswith('_') or method_name in ['configure', 'cleanup']:
                    continue
                
                try:
                    # Check if this method corresponds to a tool in metadata
                    tool_metadata = None
                    for tool_name, tool_meta in self.metadata.tools.items():
                        if (tool_meta.func_name == method_name or 
                            tool_name == method_name or 
                            tool_name.replace('-', '_') == method_name):
                            tool_metadata = tool_meta
                            break
                    
                    if tool_metadata:
                        # Use metadata schema if available, otherwise extract from method
                        if tool_metadata.input_schema and tool_metadata.output_schema:
                            schema = {
                                'input_schema': tool_metadata.input_schema,
                                'output_schema': tool_metadata.output_schema,
                                'description': tool_metadata.description,
                                'method_name': method_name,
                                'metadata': tool_metadata
                            }
                        else:
                            # Extract schema from method signature
                            extracted_schema = get_fn_schema(method)
                            schema = {
                                'input_schema': extracted_schema.get('input_schema', {}),
                                'output_schema': extracted_schema.get('output_schema', {}),
                                'description': tool_metadata.description or extracted_schema.get('description', ''),
                                'method_name': method_name,
                                'metadata': tool_metadata
                            }
                        
                        tool_key = tool_metadata.name or method_name
                        self.tool_schemas[tool_key] = schema
                        logger.debug(f"Extracted schema for tool: {tool_key}")
                        
                except Exception as e:
                    logger.warning(f"Failed to extract schema for method {method_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract tool schemas for plugin {self.name}: {e}")
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema dictionary or None if not found
        """
        return self.tool_schemas.get(tool_name)
    
    def get_all_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get schemas for all tools in this plugin.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return self.tool_schemas.copy()
    
    def get_tool_names(self) -> List[str]:
        """
        Get list of all tool names in this plugin.
        
        Returns:
            List of tool names
        """
        return list(self.tool_schemas.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """
        Check if plugin has a specific tool.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self.tool_schemas
    
    def configure_instance(self, config_data: Dict[str, Any], instance_id: str = "") -> bool:
        """
        Configure and create a plugin instance.
        
        Args:
            config_data: Configuration data for the plugin
            instance_id: Optional instance identifier
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Validate configuration against schema if available
            if self.config_schema:
                # TODO: Add proper JSON schema validation here
                pass
            
            # Create plugin instance
            if self.instance:
                # Clean up existing instance
                if hasattr(self.instance, 'cleanup'):
                    self.instance.cleanup()
            
            # Create new instance
            self.instance = self.plugin_class()
            
            # Configure instance if it has a configure method
            if hasattr(self.instance, 'configure'):
                self.instance.configure(config_data)
            
            # Store instance configuration
            from datetime import datetime
            self.instance_config = PluginInstanceConfig(
                config_data=config_data,
                instance_id=instance_id or f"{self.name}_{datetime.now().timestamp()}",
                created_at=datetime.now().isoformat()
            )
            
            self.is_configured = True
            logger.info(f"Successfully configured plugin instance: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure plugin instance {self.name}: {e}")
            self.is_configured = False
            return False
    
    def get_instance(self) -> Optional[Any]:
        """
        Get the configured plugin instance.
        
        Returns:
            Plugin instance or None if not configured
        """
        if not self.is_configured or not self.instance:
            logger.warning(f"Plugin {self.name} is not configured or has no instance")
            return None
        
        # Update last used timestamp
        if self.instance_config:
            from datetime import datetime
            self.instance_config.last_used_at = datetime.now().isoformat()
        
        return self.instance
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a specific tool on the plugin instance.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found or plugin not configured
            Exception: If tool execution fails
        """
        if not self.has_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not found in plugin '{self.name}'")
        
        instance = self.get_instance()
        if not instance:
            raise ValueError(f"Plugin '{self.name}' is not configured")
        
        # Get the method name for this tool
        tool_schema = self.tool_schemas[tool_name]
        method_name = tool_schema['method_name']
        
        if not hasattr(instance, method_name):
            raise ValueError(f"Method '{method_name}' not found in plugin instance")
        
        try:
            method = getattr(instance, method_name)
            result = method(**kwargs)
            logger.info(f"Successfully called tool '{tool_name}' on plugin '{self.name}'")
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool '{tool_name}' on plugin '{self.name}': {e}")
            raise
    
    def validate_tool_input(self, tool_name: str, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for a specific tool.
        
        Args:
            tool_name: Name of the tool
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.has_tool(tool_name):
            return False
        
        try:
            tool_schema = self.tool_schemas[tool_name]
            input_schema = tool_schema.get('input_schema', {})
            
            # TODO: Implement proper JSON schema validation
            # For now, just check if required fields are present
            required_fields = input_schema.get('required', [])
            for field in required_fields:
                if field not in input_data:
                    logger.error(f"Required field '{field}' missing for tool '{tool_name}'")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate input for tool '{tool_name}': {e}")
            return False
    
    def cleanup(self):
        """Clean up plugin instance and resources."""
        try:
            if self.instance:
                # Call plugin's cleanup method if available
                if hasattr(self.instance, 'cleanup'):
                    self.instance.cleanup()
                
                # Clear instance reference
                self.instance = None
            
            # Reset configuration state
            self.instance_config = None
            self.is_configured = False
            
            logger.info(f"Cleaned up plugin descriptor for: {self.name}")
            
        except Exception as e:
            logger.error(f"Error during plugin descriptor cleanup for {self.name}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert plugin descriptor to dictionary representation.
        
        Returns:
            Dictionary representation of the plugin descriptor
        """
        return {
            'name': self.name,
            'metadata': {
                'name': self.metadata.name,
                'category': self.metadata.category,
                'description': self.metadata.description,
                'icon': self.metadata.icon,
                'meta_version': self.metadata.meta_version,
                'labels': self.metadata.labels.dict() if self.metadata.labels else {}
            },
            'wheel_info': self.wheel_info,
            'config_schema': self.config_schema,
            'tool_schemas': {
                name: {
                    'description': schema.get('description', ''),
                    'input_schema': schema.get('input_schema', {}),
                    'output_schema': schema.get('output_schema', {}),
                    'method_name': schema.get('method_name', '')
                } for name, schema in self.tool_schemas.items()
            },
            'is_configured': self.is_configured,
            'instance_config': {
                'instance_id': self.instance_config.instance_id,
                'created_at': self.instance_config.created_at,
                'last_used_at': self.instance_config.last_used_at
            } if self.instance_config else None
        }
    
    def __repr__(self) -> str:
        return f"PluginDescriptor(name='{self.name}', tools={list(self.tool_schemas.keys())}, configured={self.is_configured})"
