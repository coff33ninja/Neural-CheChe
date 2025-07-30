"""
Configuration for the move validation system
"""

from typing import Dict, Any
import os
from .base_config import BaseConfig


class ValidationConfig(BaseConfig):
    """Configuration for move validation system"""
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default validation configuration"""
        return {
            'enable_move_validation': True,
            'strict_piece_checking': True,
            'log_violations': True,
            'violation_log_path': 'logs/violations.json',
            'max_retries': 3,
            'enable_magical_piece_detection': True,
            'enable_board_state_validation': True,
            'validation_timeout': 5.0,
            'detailed_violation_logging': True,
            'auto_fix_minor_violations': False
        }
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        return {
            'enable_move_validation': {
                'type': bool,
                'required': True
            },
            'strict_piece_checking': {
                'type': bool,
                'required': True
            },
            'log_violations': {
                'type': bool,
                'required': True
            },
            'violation_log_path': {
                'type': str,
                'required': True,
                'validator': lambda x: x.endswith('.json'),
                'validator_message': 'Violation log path must end with .json'
            },
            'max_retries': {
                'type': int,
                'required': True,
                'min_value': 0,
                'max_value': 10
            },
            'enable_magical_piece_detection': {
                'type': bool,
                'required': True
            },
            'enable_board_state_validation': {
                'type': bool,
                'required': True
            },
            'validation_timeout': {
                'type': float,
                'required': True,
                'min_value': 0.1,
                'max_value': 30.0
            },
            'detailed_violation_logging': {
                'type': bool,
                'required': True
            },
            'auto_fix_minor_violations': {
                'type': bool,
                'required': True
            }
        }
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for validation configuration fields"""
        return {
            'enable_move_validation': 'Enable/disable the entire move validation system',
            'strict_piece_checking': 'Enable strict checking for piece integrity and magical piece detection',
            'log_violations': 'Log validation violations to file for analysis',
            'violation_log_path': 'Path to the JSON file where violations are logged',
            'max_retries': 'Maximum number of retries when a move validation fails',
            'enable_magical_piece_detection': 'Detect and prevent AI from creating magical pieces',
            'enable_board_state_validation': 'Validate board state consistency before and after moves',
            'validation_timeout': 'Maximum time (seconds) to spend on move validation',
            'detailed_violation_logging': 'Include detailed information in violation logs',
            'auto_fix_minor_violations': 'Automatically fix minor violations when possible'
        }
    
    def ensure_log_directory(self) -> None:
        """Ensure the violation log directory exists"""
        log_path = self.get('violation_log_path')
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    def is_validation_enabled(self) -> bool:
        """Check if validation is enabled"""
        return self.get('enable_move_validation', True)
    
    def should_log_violations(self) -> bool:
        """Check if violation logging is enabled"""
        return self.get('log_violations', True) and self.is_validation_enabled()
    
    def get_retry_limit(self) -> int:
        """Get the maximum number of retries for failed moves"""
        return self.get('max_retries', 3)