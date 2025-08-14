"""
SchemaLoader: Utility for parsing YAML metadata and returning structured dictionaries.
Handles loading and validation of plugin metadata, configuration schemas, and tool schemas.
"""

import os
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class SchemaLoader:
    """
    Utility for loading and parsing YAML metadata files.
    
    Responsibilities:
    - Load YAML files and return structured dictionaries
    - Validate YAML syntax and structure
    - Handle different metadata formats
    - Provide fallback and error handling
    - Support both file paths and string content
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize SchemaLoader.
        
        Args:
            encoding: Default encoding for reading files
        """
        self.encoding = encoding
        self.supported_extensions = ['.yaml', '.yml', '.json']
        
    def load_from_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load structured data from a file.
        
        Args:
            file_path: Path to the metadata file
            
        Returns:
            Dictionary containing parsed data or None if loading failed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            if not file_path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                return None
            
            # Check file extension
            if file_path.suffix not in self.supported_extensions:
                logger.warning(f"Unsupported file extension: {file_path.suffix}")
            
            with open(file_path, 'r', encoding=self.encoding) as file:
                content = file.read()
            
            return self.load_from_string(content, file_path.suffix)
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return None
    
    def load_from_string(self, content: str, file_extension: str = '.yaml') -> Optional[Dict[str, Any]]:
        """
        Load structured data from a string.
        
        Args:
            content: String content to parse
            file_extension: File extension to determine parser type
            
        Returns:
            Dictionary containing parsed data or None if parsing failed
        """
        try:
            if not content.strip():
                logger.warning("Empty content provided")
                return {}
            
            # Determine parser based on file extension
            if file_extension in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
            elif file_extension == '.json':
                data = json.loads(content)
            else:
                # Default to YAML
                logger.info(f"Unknown extension {file_extension}, trying YAML parser")
                data = yaml.safe_load(content)
            
            if data is None:
                logger.warning("Parsed data is None, returning empty dict")
                return {}
            
            if not isinstance(data, dict):
                logger.error(f"Expected dictionary, got {type(data)}")
                return None
            
            return data
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing content: {e}")
            return None
    
    def load_plugin_metadata(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load plugin metadata with specific validation.
        
        Args:
            file_path: Path to the metadata file
            
        Returns:
            Validated plugin metadata dictionary or None if invalid
        """
        data = self.load_from_file(file_path)
        
        if data is None:
            return None
        
        # Validate required plugin metadata fields
        required_fields = ['name', 'meta_version']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing required metadata fields: {missing_fields}")
            return None
        
        # Set defaults for optional fields
        defaults = {
            'description': '',
            'category': 'general',
            'icon': '',
            'labels': {},
            'config_schema': {},
            'tools': {},
            'package_info': {}
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        logger.info(f"Loaded plugin metadata for: {data.get('name', 'unknown')}")
        return data
    
    def load_tool_schema(self, tool_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Load and validate tool schema data.
        
        Args:
            tool_data: Raw tool data dictionary
            
        Returns:
            Validated tool schema or None if invalid
        """
        try:
            if not isinstance(tool_data, dict):
                logger.error("Tool data must be a dictionary")
                return None
            
            # Required fields for a tool
            required_fields = ['name']
            missing_fields = []
            
            for field in required_fields:
                if field not in tool_data:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"Missing required tool fields: {missing_fields}")
                return None
            
            # Set defaults for optional fields
            tool_defaults = {
                'description': '',
                'labels': {},
                'input_schema': {},
                'output_schema': {},
                'func_name': None,
                'stream_func_name': None,
                'runtime_features': []
            }
            
            validated_tool = {}
            for key, default_value in tool_defaults.items():
                validated_tool[key] = tool_data.get(key, default_value)
            
            # Copy over required fields
            for field in required_fields:
                validated_tool[field] = tool_data[field]
            
            return validated_tool
            
        except Exception as e:
            logger.error(f"Failed to validate tool schema: {e}")
            return None
    
    def load_config_schema(self, schema_data: Union[Dict[str, Any], str]) -> Optional[Dict[str, Any]]:
        """
        Load and validate configuration schema.
        
        Args:
            schema_data: Configuration schema as dict or JSON string
            
        Returns:
            Validated configuration schema or None if invalid
        """
        try:
            if isinstance(schema_data, str):
                schema_dict = json.loads(schema_data)
            elif isinstance(schema_data, dict):
                schema_dict = schema_data.copy()
            else:
                logger.error(f"Invalid schema data type: {type(schema_data)}")
                return None
            
            # Validate JSON Schema structure
            if not self._validate_json_schema(schema_dict):
                logger.error("Invalid JSON Schema structure")
                return None
            
            return schema_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config schema JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load config schema: {e}")
            return None
    
    def _validate_json_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Basic validation of JSON Schema structure.
        
        Args:
            schema: Schema dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for basic JSON Schema structure
            if not isinstance(schema, dict):
                return False
            
            # If it has a type, it should be valid
            if 'type' in schema:
                valid_types = ['object', 'array', 'string', 'number', 'integer', 'boolean', 'null']
                if schema['type'] not in valid_types:
                    logger.error(f"Invalid schema type: {schema['type']}")
                    return False
            
            # If it has properties, validate them
            if 'properties' in schema:
                if not isinstance(schema['properties'], dict):
                    logger.error("Schema properties must be a dictionary")
                    return False
                
                # Recursively validate property schemas
                for prop_name, prop_schema in schema['properties'].items():
                    if not self._validate_json_schema(prop_schema):
                        logger.error(f"Invalid schema for property: {prop_name}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def load_multiple_files(self, directory: Union[str, Path], pattern: str = "*.yaml") -> Dict[str, Dict[str, Any]]:
        """
        Load multiple metadata files from a directory.
        
        Args:
            directory: Directory containing metadata files
            pattern: Glob pattern for matching files
            
        Returns:
            Dictionary mapping filenames to their parsed content
        """
        try:
            directory = Path(directory)
            
            if not directory.exists() or not directory.is_dir():
                logger.error(f"Directory not found or not a directory: {directory}")
                return {}
            
            results = {}
            
            # Find matching files
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    data = self.load_from_file(file_path)
                    if data is not None:
                        results[file_path.name] = data
                    else:
                        logger.warning(f"Failed to load file: {file_path}")
            
            logger.info(f"Loaded {len(results)} files from {directory}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to load multiple files from {directory}: {e}")
            return {}
    
    def save_to_file(self, data: Dict[str, Any], file_path: Union[str, Path], format_type: str = 'yaml') -> bool:
        """
        Save structured data to a file.
        
        Args:
            data: Dictionary to save
            file_path: Target file path
            format_type: Output format ('yaml' or 'json')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=self.encoding) as file:
                if format_type.lower() == 'json':
                    json.dump(data, file, indent=2, ensure_ascii=False)
                else:
                    yaml.safe_dump(data, file, default_flow_style=False, 
                                  allow_unicode=True, indent=2)
            
            logger.info(f"Saved data to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data to {file_path}: {e}")
            return False
    
    def validate_schema_compatibility(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
        """
        Check if two schemas are compatible.
        
        Args:
            schema1: First schema to compare
            schema2: Second schema to compare
            
        Returns:
            True if compatible, False otherwise
        """
        try:
            # Basic compatibility checks
            
            # Check types
            type1 = schema1.get('type')
            type2 = schema2.get('type')
            
            if type1 and type2 and type1 != type2:
                logger.warning(f"Schema type mismatch: {type1} vs {type2}")
                return False
            
            # Check required fields compatibility
            required1 = set(schema1.get('required', []))
            required2 = set(schema2.get('required', []))
            
            # Schema2 cannot require fields that schema1 doesn't have
            if required2 - required1:
                missing_required = required2 - required1
                logger.warning(f"Schema2 requires additional fields: {missing_required}")
                return False
            
            # Check properties compatibility
            props1 = schema1.get('properties', {})
            props2 = schema2.get('properties', {})
            
            for prop_name in props2:
                if prop_name in props1:
                    # Recursively check property compatibility
                    if not self.validate_schema_compatibility(props1[prop_name], props2[prop_name]):
                        logger.warning(f"Property '{prop_name}' is incompatible")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating schema compatibility: {e}")
            return False
    
    def merge_schemas(self, base_schema: Dict[str, Any], overlay_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two schemas, with overlay taking precedence.
        
        Args:
            base_schema: Base schema
            overlay_schema: Schema to overlay on base
            
        Returns:
            Merged schema
        """
        try:
            merged = base_schema.copy()
            
            for key, value in overlay_schema.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursively merge dictionaries
                    merged[key] = self.merge_schemas(merged[key], value)
                else:
                    # Overlay value takes precedence
                    merged[key] = value
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging schemas: {e}")
            return base_schema
