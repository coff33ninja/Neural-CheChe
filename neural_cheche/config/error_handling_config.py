"""
Configuration for error handling and recovery mechanisms
"""

from typing import Dict, Any
from .base_config import BaseConfig


class ErrorHandlingConfig(BaseConfig):
    """Configuration for error handling and recovery mechanisms"""
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default error handling configuration"""
        return {
            'graceful_degradation': True,
            'retry_failed_operations': True,
            'log_errors': True,
            'continue_on_component_failure': True,
            'max_retry_attempts': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True,
            'error_log_path': 'logs/errors.log',
            'detailed_error_logging': True,
            'notify_user_on_error': True,
            'auto_recovery_enabled': True,
            'fallback_mode_enabled': True,
            'error_reporting_enabled': False,
            'crash_dump_enabled': True,
            'memory_cleanup_on_error': True
        }
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        return {
            'graceful_degradation': {
                'type': bool,
                'required': True
            },
            'retry_failed_operations': {
                'type': bool,
                'required': True
            },
            'log_errors': {
                'type': bool,
                'required': True
            },
            'continue_on_component_failure': {
                'type': bool,
                'required': True
            },
            'max_retry_attempts': {
                'type': int,
                'required': True,
                'min_value': 0,
                'max_value': 10
            },
            'retry_delay': {
                'type': float,
                'required': True,
                'min_value': 0.1,
                'max_value': 10.0
            },
            'exponential_backoff': {
                'type': bool,
                'required': True
            },
            'error_log_path': {
                'type': str,
                'required': True,
                'validator': lambda x: len(x) > 0,
                'validator_message': 'Error log path cannot be empty'
            },
            'detailed_error_logging': {
                'type': bool,
                'required': True
            },
            'notify_user_on_error': {
                'type': bool,
                'required': True
            },
            'auto_recovery_enabled': {
                'type': bool,
                'required': True
            },
            'fallback_mode_enabled': {
                'type': bool,
                'required': True
            },
            'error_reporting_enabled': {
                'type': bool,
                'required': True
            },
            'crash_dump_enabled': {
                'type': bool,
                'required': True
            },
            'memory_cleanup_on_error': {
                'type': bool,
                'required': True
            }
        }
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for error handling configuration fields"""
        return {
            'graceful_degradation': 'Continue operation with reduced functionality when components fail',
            'retry_failed_operations': 'Automatically retry failed operations',
            'log_errors': 'Log all errors to file for debugging',
            'continue_on_component_failure': 'Continue training even if non-critical components fail',
            'max_retry_attempts': 'Maximum number of retry attempts for failed operations',
            'retry_delay': 'Initial delay (seconds) between retry attempts',
            'exponential_backoff': 'Use exponential backoff for retry delays',
            'error_log_path': 'Path to the error log file',
            'detailed_error_logging': 'Include stack traces and detailed context in error logs',
            'notify_user_on_error': 'Show error notifications to the user',
            'auto_recovery_enabled': 'Attempt automatic recovery from common errors',
            'fallback_mode_enabled': 'Enable fallback modes when primary systems fail',
            'error_reporting_enabled': 'Enable anonymous error reporting for debugging',
            'crash_dump_enabled': 'Create crash dumps for severe errors',
            'memory_cleanup_on_error': 'Clean up memory when errors occur'
        }
    
    def should_retry_on_failure(self) -> bool:
        """Check if operations should be retried on failure"""
        return self.get('retry_failed_operations', True)
    
    def get_max_retries(self) -> int:
        """Get maximum number of retry attempts"""
        return self.get('max_retry_attempts', 3)
    
    def get_retry_delay(self) -> float:
        """Get initial retry delay in seconds"""
        return self.get('retry_delay', 1.0)
    
    def should_use_exponential_backoff(self) -> bool:
        """Check if exponential backoff should be used"""
        return self.get('exponential_backoff', True)
    
    def should_continue_on_failure(self) -> bool:
        """Check if training should continue when components fail"""
        return self.get('continue_on_component_failure', True)
    
    def should_use_graceful_degradation(self) -> bool:
        """Check if graceful degradation is enabled"""
        return self.get('graceful_degradation', True)
    
    def should_log_errors(self) -> bool:
        """Check if errors should be logged"""
        return self.get('log_errors', True)
    
    def should_notify_user(self) -> bool:
        """Check if user should be notified of errors"""
        return self.get('notify_user_on_error', True)
    
    def is_auto_recovery_enabled(self) -> bool:
        """Check if automatic recovery is enabled"""
        return self.get('auto_recovery_enabled', True)
    
    def calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay for given attempt number"""
        base_delay = self.get_retry_delay()
        
        if self.should_use_exponential_backoff():
            return base_delay * (2 ** (attempt - 1))
        else:
            return base_delay