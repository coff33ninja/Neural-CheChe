"""
Base configuration class with validation and default value handling
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os
from dataclasses import dataclass


@dataclass
class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails"""
    field_name: str
    value: Any
    message: str
    
    def __str__(self):
        return f"Configuration error in '{self.field_name}': {self.message} (value: {self.value})"


class BaseConfig(ABC):
    """Base class for all configuration objects"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]]=None):
        """Initialize configuration with optional dictionary"""
        self._config = config_dict or {}
        self._defaults = self._get_defaults()
        self._validate_config()
    
    @abstractmethod
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values"""
        pass
    
    @abstractmethod
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        pass
    
    def _validate_config(self):
        """Validate configuration against rules"""
        rules = self._get_validation_rules()
        
        for field_name, rule in rules.items():
            value = self.get(field_name)
            
            # Check required fields
            if rule.get('required', False) and value is None:
                raise ConfigValidationError(
                    field_name, value, "Required field is missing"
                )
            
            # Check type validation
            if value is not None and 'type' in rule:
                expected_type = rule['type']
                if not isinstance(value, expected_type):
                    raise ConfigValidationError(
                        field_name, value, f"Expected type {expected_type.__name__}, got {type(value).__name__}"
                    )
            
            # Check range validation for numeric values
            if value is not None and isinstance(value, (int, float)):
                if 'min_value' in rule and value < rule['min_value']:
                    raise ConfigValidationError(
                        field_name, value, f"Value must be >= {rule['min_value']}"
                    )
                if 'max_value' in rule and value > rule['max_value']:
                    raise ConfigValidationError(
                        field_name, value, f"Value must be <= {rule['max_value']}"
                    )
            
            # Check choices validation
            if value is not None and 'choices' in rule:
                if value not in rule['choices']:
                    raise ConfigValidationError(
                        field_name, value, f"Value must be one of {rule['choices']}"
                    )
            
            # Custom validation function
            if value is not None and 'validator' in rule:
                validator = rule['validator']
                if not validator(value):
                    raise ConfigValidationError(
                        field_name, value, rule.get('validator_message', 'Custom validation failed')
                    )
    
    def get(self, key: str, default: Any=None) -> Any:
        """Get configuration value with fallback to defaults"""
        if key in self._config:
            return self._config[key]
        elif key in self._defaults:
            return self._defaults[key]
        else:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation"""
        old_value = self._config.get(key)
        self._config[key] = value
        
        try:
            self._validate_config()
        except ConfigValidationError:
            # Restore old value if validation fails
            if old_value is not None:
                self._config[key] = old_value
            else:
                self._config.pop(key, None)
            raise
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        old_config = self._config.copy()
        self._config.update(config_dict)
        
        try:
            self._validate_config()
        except ConfigValidationError:
            # Restore old configuration if validation fails
            self._config = old_config
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = self._defaults.copy()
        result.update(self._config)
        return result
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'BaseConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(filepath):
            return cls()
        
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        return cls(config_dict)
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for configuration fields"""
        return getattr(self, '_documentation', {})
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for this configuration"""
        rules = self._get_validation_rules()
        properties = {}
        required = []
        
        for field_name, rule in rules.items():
            prop = {}
            
            # Add type information
            if 'type' in rule:
                if rule['type'] is int:
                    prop['type'] = 'integer'
                elif rule['type'] is float:
                    prop['type'] = 'number'
                elif rule['type'] is bool:
                    prop['type'] = 'boolean'
                elif rule['type'] is str:
                    prop['type'] = 'string'
                elif rule['type'] is list:
                    prop['type'] = 'array'
                elif rule['type'] is dict:
                    prop['type'] = 'object'
            
            # Add range constraints
            if 'min_value' in rule:
                prop['minimum'] = rule['min_value']
            if 'max_value' in rule:
                prop['maximum'] = rule['max_value']
            
            # Add choices
            if 'choices' in rule:
                prop['enum'] = rule['choices']
            
            # Add description
            docs = self.get_documentation()
            if field_name in docs:
                prop['description'] = docs[field_name]
            
            # Add default value
            if field_name in self._defaults:
                prop['default'] = self._defaults[field_name]
            
            properties[field_name] = prop
            
            # Track required fields
            if rule.get('required', False):
                required.append(field_name)
        
        return {
            'type': 'object',
            'properties': properties,
            'required': required,
            'additionalProperties': False
        }
    
    def validate_against_schema(self, data: Dict[str, Any]) -> bool:
        """Validate data against this configuration's schema"""
        try:
            # Create temporary instance to validate
            self.__class__(data)
            return True
        except ConfigValidationError:
            return False
    
    def get_field_info(self, field_name: str) -> Dict[str, Any]:
        """Get detailed information about a configuration field"""
        rules = self._get_validation_rules()
        docs = self.get_documentation()
        
        if field_name not in rules:
            return {}
        
        rule = rules[field_name]
        info = {
            'name': field_name,
            'current_value': self.get(field_name),
            'default_value': self._defaults.get(field_name),
            'required': rule.get('required', False),
            'description': docs.get(field_name, 'No description available')
        }
        
        # Add type information
        if 'type' in rule:
            info['type'] = rule['type'].__name__
        
        # Add constraints
        if 'min_value' in rule:
            info['min_value'] = rule['min_value']
        if 'max_value' in rule:
            info['max_value'] = rule['max_value']
        if 'choices' in rule:
            info['choices'] = rule['choices']
        
        return info
    
    def list_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """List all configuration fields with their information"""
        rules = self._get_validation_rules()
        return {field_name: self.get_field_info(field_name) for field_name in rules.keys()}
    
    def reset_field_to_default(self, field_name: str) -> None:
        """Reset a specific field to its default value"""
        if field_name in self._defaults:
            self.set(field_name, self._defaults[field_name])
        elif field_name in self._config:
            del self._config[field_name]
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"{self.__class__.__name__}({self.to_dict()})"
    
    def __repr__(self) -> str:
        """Detailed representation of configuration"""
        return self.__str__()
