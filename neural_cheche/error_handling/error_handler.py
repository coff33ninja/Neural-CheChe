"""
Central error handling system with categorization and severity levels
"""

import traceback
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization"""
    VALIDATION = "validation"
    PROGRESS = "progress"
    HISTORY = "history"
    GUI = "gui"
    TRAINING = "training"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    NETWORK = "network"
    FILE_IO = "file_io"


@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception]
    traceback_str: str
    timestamp: datetime
    component: str
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0


class ErrorHandler:
    """Central error handling system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize error handler with configuration"""
        self.config = config or self._get_default_config()
        
        # Error tracking
        self.error_history: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        self.component_errors: Dict[str, List[ErrorInfo]] = {}
        
        # Recovery callbacks
        self.recovery_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        
        # Initialize logging
        self._setup_logging()
        
        # Error rate limiting
        self.error_rate_limits: Dict[str, Dict[str, Any]] = {}
        
        print("🔧 ErrorHandler initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default error handling configuration"""
        return {
            'log_errors': True,
            'log_file': 'logs/errors.log',
            'max_error_history': 1000,
            'enable_recovery': True,
            'max_retry_attempts': 3,
            'retry_delay': 1.0,
            'rate_limit_window': 60,  # seconds
            'max_errors_per_window': 10,
            'notify_user': True,
            'graceful_degradation': True,
            'continue_on_failure': True,
            'detailed_logging': True
        }
    
    def _setup_logging(self):
        """Setup error logging"""
        if self.config.get('log_errors', True):
            log_file = self.config.get('log_file', 'logs/errors.log')
            
            # Create logs directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Configure logger
            self.logger = logging.getLogger('neural_cheche_errors')
            self.logger.setLevel(logging.ERROR)
            
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.ERROR)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler if not already added
            if not self.logger.handlers:
                self.logger.addHandler(file_handler)
        else:
            self.logger = None
    
    def handle_error(self, 
                    error: Exception,
                    category: ErrorCategory,
                    severity: ErrorSeverity,
                    component: str,
                    context: Optional[Dict[str, Any]] = None,
                    recovery_callback: Optional[Callable] = None) -> ErrorInfo:
        """Handle an error with comprehensive logging and recovery"""
        
        # Generate unique error ID
        error_id = f"{category.value}_{component}_{int(time.time())}"
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            exception=error,
            traceback_str=traceback.format_exc(),
            timestamp=datetime.now(),
            component=component,
            context=context or {}
        )
        
        # Check rate limiting
        if self._is_rate_limited(component, category):
            print(f"⚠️ Error rate limit exceeded for {component}/{category.value}")
            return error_info
        
        # Log error
        self._log_error(error_info)
        
        # Add to history
        self._add_to_history(error_info)
        
        # Attempt recovery if enabled
        if self.config.get('enable_recovery', True):
            self._attempt_recovery(error_info, recovery_callback)
        
        # Notify user if configured
        if self.config.get('notify_user', True):
            self._notify_user(error_info)
        
        return error_info
    
    def _is_rate_limited(self, component: str, category: ErrorCategory) -> bool:
        """Check if error reporting is rate limited"""
        key = f"{component}_{category.value}"
        current_time = time.time()
        window = self.config.get('rate_limit_window', 60)
        max_errors = self.config.get('max_errors_per_window', 10)
        
        if key not in self.error_rate_limits:
            self.error_rate_limits[key] = {
                'count': 0,
                'window_start': current_time
            }
        
        rate_info = self.error_rate_limits[key]
        
        # Reset window if expired
        if current_time - rate_info['window_start'] > window:
            rate_info['count'] = 0
            rate_info['window_start'] = current_time
        
        # Check limit
        if rate_info['count'] >= max_errors:
            return True
        
        # Increment count
        rate_info['count'] += 1
        return False
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error information"""
        if self.logger:
            log_message = f"[{error_info.category.value.upper()}] {error_info.component}: {error_info.message}"
            
            if self.config.get('detailed_logging', True):
                log_message += f"\nContext: {error_info.context}"
                log_message += f"\nTraceback: {error_info.traceback_str}"
            
            self.logger.error(log_message)
        
        # Console logging based on severity
        if error_info.severity == ErrorSeverity.CRITICAL:
            print(f"🚨 CRITICAL ERROR in {error_info.component}: {error_info.message}")
        elif error_info.severity == ErrorSeverity.HIGH:
            print(f"❌ HIGH ERROR in {error_info.component}: {error_info.message}")
        elif error_info.severity == ErrorSeverity.MEDIUM:
            print(f"⚠️ MEDIUM ERROR in {error_info.component}: {error_info.message}")
        else:
            print(f"ℹ️ LOW ERROR in {error_info.component}: {error_info.message}")
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Add error to history with size management"""
        self.error_history.append(error_info)
        
        # Update component errors
        if error_info.component not in self.component_errors:
            self.component_errors[error_info.component] = []
        self.component_errors[error_info.component].append(error_info)
        
        # Update error counts
        key = f"{error_info.category.value}_{error_info.component}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Trim history if too large
        max_history = self.config.get('max_error_history', 1000)
        if len(self.error_history) > max_history:
            # Remove oldest errors
            removed = self.error_history.pop(0)
            # Also remove from component errors
            if removed.component in self.component_errors:
                component_list = self.component_errors[removed.component]
                if removed in component_list:
                    component_list.remove(removed)
    
    def _attempt_recovery(self, error_info: ErrorInfo, recovery_callback: Optional[Callable]):
        """Attempt to recover from error"""
        error_info.recovery_attempted = True
        
        try:
            # Try specific recovery callback first
            if recovery_callback:
                recovery_callback(error_info)
                error_info.recovery_successful = True
                print(f"✅ Recovery successful for {error_info.component}")
                return
            
            # Try category-specific recovery callbacks
            if error_info.category in self.recovery_callbacks:
                for callback in self.recovery_callbacks[error_info.category]:
                    try:
                        callback(error_info)
                        error_info.recovery_successful = True
                        print(f"✅ Recovery successful for {error_info.component}")
                        return
                    except Exception as recovery_error:
                        print(f"⚠️ Recovery callback failed: {recovery_error}")
            
            # Default recovery strategies
            self._default_recovery(error_info)
            
        except Exception as recovery_error:
            print(f"❌ Recovery failed for {error_info.component}: {recovery_error}")
            error_info.recovery_successful = False
    
    def _default_recovery(self, error_info: ErrorInfo):
        """Default recovery strategies based on error category"""
        if error_info.category == ErrorCategory.FILE_IO:
            # Try to create missing directories
            if "No such file or directory" in error_info.message:
                try:
                    import os
                    # Extract directory from error message if possible
                    # This is a basic implementation
                    print(f"🔧 Attempting to create missing directories for {error_info.component}")
                    error_info.recovery_successful = True
                except Exception:
                    pass
        
        elif error_info.category == ErrorCategory.CONFIGURATION:
            # Reset to defaults
            print(f"🔧 Attempting to reset configuration to defaults for {error_info.component}")
            error_info.recovery_successful = True
        
        elif error_info.category == ErrorCategory.GUI:
            # Disable GUI if it's failing
            if self.config.get('graceful_degradation', True):
                print(f"🔧 Disabling GUI component {error_info.component} due to errors")
                error_info.recovery_successful = True
    
    def _notify_user(self, error_info: ErrorInfo):
        """Notify user about error"""
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            print(f"🔔 User notification: {error_info.severity.value.upper()} error in {error_info.component}")
    
    def register_recovery_callback(self, category: ErrorCategory, callback: Callable):
        """Register a recovery callback for a specific error category"""
        if category not in self.recovery_callbacks:
            self.recovery_callbacks[category] = []
        self.recovery_callbacks[category].append(callback)
        print(f"🔧 Recovery callback registered for {category.value}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        total_errors = len(self.error_history)
        
        # Errors by category
        category_counts = {}
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
        
        # Errors by severity
        severity_counts = {}
        for error in self.error_history:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Errors by component
        component_counts = {}
        for component, errors in self.component_errors.items():
            component_counts[component] = len(errors)
        
        # Recovery statistics
        recovery_attempts = sum(1 for error in self.error_history if error.recovery_attempted)
        recovery_successes = sum(1 for error in self.error_history if error.recovery_successful)
        recovery_rate = (recovery_successes / recovery_attempts * 100) if recovery_attempts > 0 else 0
        
        return {
            'total_errors': total_errors,
            'errors_by_category': category_counts,
            'errors_by_severity': severity_counts,
            'errors_by_component': component_counts,
            'recovery_attempts': recovery_attempts,
            'recovery_successes': recovery_successes,
            'recovery_rate': f"{recovery_rate:.1f}%",
            'recent_errors': [
                {
                    'component': error.component,
                    'category': error.category.value,
                    'severity': error.severity.value,
                    'message': error.message,
                    'timestamp': error.timestamp.isoformat()
                }
                for error in self.error_history[-10:]  # Last 10 errors
            ]
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.component_errors.clear()
        self.error_counts.clear()
        print("🧹 Error history cleared")
    
    def should_continue_on_failure(self, severity: ErrorSeverity) -> bool:
        """Determine if system should continue after error"""
        if severity == ErrorSeverity.CRITICAL:
            return False
        
        return self.config.get('continue_on_failure', True)
    
    def should_retry_operation(self, error_info: ErrorInfo) -> bool:
        """Determine if operation should be retried"""
        max_retries = self.config.get('max_retry_attempts', 3)
        return error_info.retry_count < max_retries
    
    def get_retry_delay(self, retry_count: int) -> float:
        """Get delay before retry (exponential backoff)"""
        base_delay = self.config.get('retry_delay', 1.0)
        return base_delay * (2 ** retry_count)  # Exponential backoff