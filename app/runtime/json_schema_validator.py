"""
JSONSchemaValidator: Utility for validating request bodies against JSON Schema.
Uses the jsonschema library for comprehensive validation of input data.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from jsonschema import Draft7Validator, ValidationError, SchemaError
from jsonschema.exceptions import best_match

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of JSON Schema validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


class JSONSchemaValidator:
    """
    Validates request bodies and data against JSON Schema specifications.
    
    Responsibilities:
    - Validate data against JSON Schema using jsonschema library
    - Provide detailed error messages and validation results
    - Support different JSON Schema draft versions
    - Handle schema preprocessing and normalization
    - Offer both strict and lenient validation modes
    """
    
    def __init__(self, draft_version: str = "draft7"):
        """
        Initialize JSONSchemaValidator.
        
        Args:
            draft_version: JSON Schema draft version to use
        """
        self.draft_version = draft_version
        self._validator_cache: Dict[str, Draft7Validator] = {}
        
    def validate(
        self, 
        data: Any, 
        schema: Dict[str, Any], 
        strict: bool = True
    ) -> ValidationResult:
        """
        Validate data against a JSON Schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            strict: Whether to use strict validation mode
            
        Returns:
            ValidationResult containing validation status and any errors
        """
        try:
            # Normalize the schema
            normalized_schema = self._normalize_schema(schema)
            
            # Create or get cached validator
            schema_hash = self._hash_schema(normalized_schema)
            if schema_hash not in self._validator_cache:
                self._validator_cache[schema_hash] = Draft7Validator(normalized_schema)
            
            validator = self._validator_cache[schema_hash]
            
            # Check if schema itself is valid
            try:
                validator.check_schema(normalized_schema)
            except SchemaError as e:
                logger.error(f"Invalid schema: {e}")
                result = ValidationResult(False)
                result.add_error(f"Invalid schema: {str(e)}")
                return result
            
            # Validate the data
            result = ValidationResult(True)
            validation_errors = list(validator.iter_errors(data))
            
            if validation_errors:
                result.is_valid = False
                
                # Process validation errors
                for error in validation_errors:
                    error_message = self._format_validation_error(error)
                    result.add_error(error_message)
                
                # Add best match error as the primary error
                best_error = best_match(validation_errors)
                if best_error and len(result.errors) > 1:
                    primary_error = self._format_validation_error(best_error)
                    # Move primary error to the front
                    if primary_error in result.errors:
                        result.errors.remove(primary_error)
                        result.errors.insert(0, f"Primary issue: {primary_error}")
            
            # Add warnings for non-strict mode
            if not strict:
                self._add_non_strict_warnings(data, normalized_schema, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            result = ValidationResult(False)
            result.add_error(f"Validation failed: {str(e)}")
            return result
    
    def validate_multiple(
        self, 
        data_list: List[Tuple[Any, Dict[str, Any]]], 
        strict: bool = True
    ) -> List[ValidationResult]:
        """
        Validate multiple data/schema pairs.
        
        Args:
            data_list: List of (data, schema) tuples to validate
            strict: Whether to use strict validation mode
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for i, (data, schema) in enumerate(data_list):
            try:
                result = self.validate(data, schema, strict)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to validate item {i}: {e}")
                result = ValidationResult(False)
                result.add_error(f"Validation failed for item {i}: {str(e)}")
                results.append(result)
        
        return results
    
    def is_valid(self, data: Any, schema: Dict[str, Any]) -> bool:
        """
        Quick validation check - returns only boolean result.
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            
        Returns:
            True if valid, False otherwise
        """
        result = self.validate(data, schema)
        return result.is_valid
    
    def get_validation_errors(self, data: Any, schema: Dict[str, Any]) -> List[str]:
        """
        Get list of validation error messages.
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            
        Returns:
            List of error messages
        """
        result = self.validate(data, schema)
        return result.errors
    
    def _normalize_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize schema for validation.
        
        Args:
            schema: Raw JSON Schema
            
        Returns:
            Normalized schema
        """
        if not isinstance(schema, dict):
            logger.warning("Schema is not a dictionary, wrapping in object schema")
            return {"type": "object", "properties": {}}
        
        normalized = schema.copy()
        
        # Ensure schema has a type if it doesn't already
        if 'type' not in normalized and 'properties' in normalized:
            normalized['type'] = 'object'
        
        # Add default $schema if not present
        if '$schema' not in normalized:
            normalized['$schema'] = 'https://json-schema.org/draft/2019-09/schema'
        
        return normalized
    
    def _hash_schema(self, schema: Dict[str, Any]) -> str:
        """
        Create a hash of the schema for caching.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Hash string
        """
        import json
        import hashlib
        
        # Create a stable string representation
        schema_str = json.dumps(schema, sort_keys=True, separators=(',', ':'))
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """
        Format a validation error into a readable message.
        
        Args:
            error: ValidationError from jsonschema
            
        Returns:
            Formatted error message
        """
        try:
            # Build path to the invalid field
            if error.absolute_path:
                path_str = '.'.join(str(p) for p in error.absolute_path)
                field_info = f"at '{path_str}'"
            else:
                field_info = "at root level"
            
            # Get the validation failure reason
            if error.validator == 'required':
                missing_fields = error.validator_value
                if isinstance(missing_fields, list):
                    field_list = ', '.join(f"'{f}'" for f in missing_fields)
                    return f"Missing required field(s): {field_list}"
                else:
                    return f"Missing required field: '{missing_fields}'"
            
            elif error.validator == 'type':
                expected_type = error.validator_value
                actual_type = type(error.instance).__name__
                return f"Type error {field_info}: expected {expected_type}, got {actual_type}"
            
            elif error.validator == 'enum':
                allowed_values = error.validator_value
                return f"Invalid value {field_info}: must be one of {allowed_values}"
            
            elif error.validator == 'minimum':
                minimum = error.validator_value
                return f"Value too small {field_info}: must be >= {minimum}"
            
            elif error.validator == 'maximum':
                maximum = error.validator_value
                return f"Value too large {field_info}: must be <= {maximum}"
            
            elif error.validator == 'minLength':
                min_length = error.validator_value
                return f"String too short {field_info}: must be at least {min_length} characters"
            
            elif error.validator == 'maxLength':
                max_length = error.validator_value
                return f"String too long {field_info}: must be at most {max_length} characters"
            
            elif error.validator == 'pattern':
                pattern = error.validator_value
                return f"String format invalid {field_info}: must match pattern '{pattern}'"
            
            elif error.validator == 'format':
                format_name = error.validator_value
                return f"Format error {field_info}: must be valid {format_name} format"
            
            elif error.validator == 'additionalProperties':
                return f"Additional properties not allowed {field_info}"
            
            else:
                # Generic error message
                return f"Validation error {field_info}: {error.message}"
                
        except Exception as e:
            logger.warning(f"Error formatting validation message: {e}")
            return f"Validation error: {error.message}"
    
    def _add_non_strict_warnings(
        self, 
        data: Any, 
        schema: Dict[str, Any], 
        result: ValidationResult
    ):
        """
        Add warnings for non-strict validation mode.
        
        Args:
            data: Validated data
            schema: Schema used for validation
            result: ValidationResult to add warnings to
        """
        try:
            # Check for extra properties in objects
            if isinstance(data, dict) and schema.get('type') == 'object':
                defined_props = set(schema.get('properties', {}).keys())
                data_props = set(data.keys())
                extra_props = data_props - defined_props
                
                if extra_props and not schema.get('additionalProperties', True):
                    result.add_warning(f"Extra properties found: {list(extra_props)}")
            
            # Check for missing optional properties with defaults
            if isinstance(data, dict) and schema.get('type') == 'object':
                properties = schema.get('properties', {})
                for prop_name, prop_schema in properties.items():
                    if (prop_name not in data and 
                        'default' in prop_schema and 
                        prop_name not in schema.get('required', [])):
                        result.add_warning(f"Optional property '{prop_name}' not provided, default value available")
                        
        except Exception as e:
            logger.debug(f"Error adding non-strict warnings: {e}")
    
    def validate_config_schema(self, config_data: Dict[str, Any], config_schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration data against configuration schema.
        
        Args:
            config_data: Configuration data to validate
            config_schema: Configuration schema
            
        Returns:
            ValidationResult
        """
        try:
            # Add some config-specific validation logic
            result = self.validate(config_data, config_schema, strict=True)
            
            # Additional config-specific checks
            if result.is_valid and isinstance(config_data, dict):
                # Check for empty required string values
                for key, value in config_data.items():
                    if isinstance(value, str) and not value.strip():
                        prop_schema = config_schema.get('properties', {}).get(key, {})
                        if key in config_schema.get('required', []):
                            result.add_warning(f"Required field '{key}' has empty value")
            
            return result
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            result = ValidationResult(False)
            result.add_error(f"Configuration validation failed: {str(e)}")
            return result
    
    def validate_tool_input(
        self, 
        input_data: Dict[str, Any], 
        input_schema: Dict[str, Any],
        tool_name: str = ""
    ) -> ValidationResult:
        """
        Validate tool input data against input schema.
        
        Args:
            input_data: Input data to validate
            input_schema: Input schema for the tool
            tool_name: Name of the tool (for error context)
            
        Returns:
            ValidationResult
        """
        try:
            result = self.validate(input_data, input_schema, strict=True)
            
            # Add tool-specific context to errors
            if not result.is_valid and tool_name:
                updated_errors = []
                for error in result.errors:
                    updated_errors.append(f"Tool '{tool_name}': {error}")
                result.errors = updated_errors
            
            return result
            
        except Exception as e:
            logger.error(f"Tool input validation error: {e}")
            result = ValidationResult(False)
            error_msg = f"Tool input validation failed: {str(e)}"
            if tool_name:
                error_msg = f"Tool '{tool_name}': {error_msg}"
            result.add_error(error_msg)
            return result
    
    def clear_cache(self):
        """Clear the validator cache."""
        self._validator_cache.clear()
        logger.debug("Validator cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the current size of the validator cache."""
        return len(self._validator_cache)
