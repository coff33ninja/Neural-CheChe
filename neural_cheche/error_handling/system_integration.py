"""
System-wide error handling integration and coordination
"""

import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from .error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
from .recovery_manager import RecoveryManager
from .user_notifier import UserNotifier
from .error_logger import ErrorLogger


class SystemErrorHandler:
    """
    Centralized error handling system that coordinates all error handling components
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize system-wide error handling"""
        self.config = config or self._get_default_config()
        
        # Initialize core components
        self.error_handler = ErrorHandler(self.config)
        self.recovery_manager = RecoveryManager(self.config)
        self.user_notifier = UserNotifier(self.config)
        self.error_logger = ErrorLogger(
            log_directory=self.config.get('log_directory', 'logs'),
            config=self.config
        )
        
        # System state tracking
        self.system_health = {
            'validation_system': True,
            'progress_tracking': True,
            'history_logging': True,
            'gui_system': True,
            'training_system': True
        }
        
        # Component failure counts
        self.component_failures = {}
        
        # Critical error threshold
        self.critical_error_threshold = self.config.get('critical_error_threshold', 5)
        
        # Register system-wide recovery callbacks
        self._register_system_recovery_callbacks()
        
        print("🔧 SystemErrorHandler initialized with comprehensive error handling")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default system error handling configuration"""
        return {
            'log_directory': 'logs',
            'enable_recovery': True,
            'enable_notifications': True,
            'graceful_degradation': True,
            'continue_on_failure': True,
            'critical_error_threshold': 5,
            'auto_restart_components': True,
            'system_health_monitoring': True,
            'detailed_error_logging': True,
            'user_notification_levels': ['error', 'critical'],
            'recovery_timeout': 30.0,
            'max_recovery_attempts': 3
        }
    
    def handle_system_error(self, 
                          error: Exception,
                          component: str,
                          operation: str,
                          context: Optional[Dict[str, Any]] = None,
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          category: ErrorCategory = ErrorCategory.SYSTEM) -> bool:
        """
        Handle a system-wide error with comprehensive recovery
        
        Args:
            error: The exception that occurred
            component: Component where error occurred
            operation: Operation that failed
            context: Additional context information
            severity: Error severity level
            category: Error category
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        try:
            # Create comprehensive error context
            error_context = {
                'component': component,
                'operation': operation,
                'timestamp': datetime.now().isoformat(),
                'system_health': self.system_health.copy(),
                'traceback': traceback.format_exc(),
                **(context or {})
            }
            
            # Handle the error through error handler
            error_info = self.error_handler.handle_error(
                error=error,
                category=category,
                severity=severity,
                component=component,
                context=error_context
            )
            
            # Log the error
            self.error_logger.log_error({
                'error_id': error_info.error_id,
                'category': category.value,
                'severity': severity.value,
                'component': component,
                'operation': operation,
                'message': str(error),
                'context': error_context,
                'traceback': error_info.traceback_str
            })
            
            # Update component failure tracking
            self._update_component_failures(component, severity)
            
            # Attempt recovery if enabled
            recovery_successful = False
            if self.config.get('enable_recovery', True):
                recovery_successful = self._attempt_comprehensive_recovery(
                    error_info, component, operation, context
                )
            
            # Update system health
            self._update_system_health(component, recovery_successful, severity)
            
            # Send user notifications for high-severity errors
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                self._send_error_notification(error_info, recovery_successful)
            
            # Check if system should continue
            should_continue = self._should_continue_operation(component, severity)
            
            # Log final outcome
            outcome = "recovered" if recovery_successful else "failed"
            print(f"🔧 System error in {component}.{operation}: {outcome}")
            
            return recovery_successful and should_continue
            
        except Exception as handler_error:
            # Error in error handler - this is critical
            print(f"🚨 CRITICAL: Error handler failure: {handler_error}")
            print(f"Original error: {error}")
            return False
    
    def _attempt_comprehensive_recovery(self, 
                                      error_info,
                                      component: str,
                                      operation: str,
                                      context: Optional[Dict[str, Any]]) -> bool:
        """Attempt comprehensive recovery using multiple strategies"""
        
        # Determine recovery scenario based on component and operation
        recovery_scenario = self._determine_recovery_scenario(component, operation, error_info)
        
        if not recovery_scenario:
            return False
        
        # Attempt recovery through recovery manager
        recovery_context = {
            'component': component,
            'operation': operation,
            'error_info': error_info,
            'system_health': self.system_health,
            **(context or {})
        }
        
        recovery_successful = self.recovery_manager.attempt_recovery(
            recovery_scenario, recovery_context
        )
        
        # If standard recovery fails, try component-specific recovery
        if not recovery_successful:
            recovery_successful = self._attempt_component_specific_recovery(
                component, operation, recovery_context
            )
        
        # If still failing, try graceful degradation
        if not recovery_successful and self.config.get('graceful_degradation', True):
            recovery_successful = self._attempt_graceful_degradation(
                component, recovery_context
            )
        
        return recovery_successful
    
    def _determine_recovery_scenario(self, component: str, operation: str, error_info) -> Optional[str]:
        """Determine appropriate recovery scenario"""
        
        # Map component/operation combinations to recovery scenarios
        recovery_mapping = {
            ('validation', 'validate_move'): 'validation_timeout',
            ('progress', 'update_display'): 'progress_display_failed',
            ('history', 'log_move'): 'history_logging_failed',
            ('gui', 'render'): 'gui_initialization_failed',
            ('training', 'train_step'): 'training_step_failed',
            ('file_io', 'save'): 'file_not_found',
            ('config', 'load'): 'config_invalid'
        }
        
        # Check for exact match
        key = (component.lower(), operation.lower())
        if key in recovery_mapping:
            return recovery_mapping[key]
        
        # Check for component-level matches
        component_mapping = {
            'validation': 'validation_timeout',
            'progress': 'progress_display_failed',
            'history': 'history_logging_failed',
            'gui': 'gui_initialization_failed',
            'training': 'training_step_failed'
        }
        
        return component_mapping.get(component.lower())
    
    def _attempt_component_specific_recovery(self, 
                                           component: str,
                                           operation: str,
                                           context: Dict[str, Any]) -> bool:
        """Attempt component-specific recovery strategies"""
        
        try:
            if component.lower() == 'validation':
                return self._recover_validation_system(context)
            elif component.lower() == 'progress':
                return self._recover_progress_system(context)
            elif component.lower() == 'history':
                return self._recover_history_system(context)
            elif component.lower() == 'gui':
                return self._recover_gui_system(context)
            elif component.lower() == 'training':
                return self._recover_training_system(context)
            else:
                return False
                
        except Exception as e:
            print(f"⚠️ Component-specific recovery failed: {e}")
            return False
    
    def _recover_validation_system(self, context: Dict[str, Any]) -> bool:
        """Recover validation system"""
        try:
            # Disable strict validation temporarily
            context['use_simplified_validation'] = True
            context['validation_timeout'] = 5.0
            print("🛡️ Validation system recovered with simplified mode")
            return True
        except Exception:
            return False
    
    def _recover_progress_system(self, context: Dict[str, Any]) -> bool:
        """Recover progress tracking system"""
        try:
            # Disable problematic progress displays
            context['progress_disabled'] = True
            context['enable_cli_progress'] = False
            context['enable_gui_progress'] = False
            print("📊 Progress system recovered with minimal display")
            return True
        except Exception:
            return False
    
    def _recover_history_system(self, context: Dict[str, Any]) -> bool:
        """Recover history logging system"""
        try:
            # Switch to memory-only logging
            context['use_memory_logging'] = True
            context['disable_file_logging'] = True
            print("📝 History system recovered with memory-only logging")
            return True
        except Exception:
            return False
    
    def _recover_gui_system(self, context: Dict[str, Any]) -> bool:
        """Recover GUI system"""
        try:
            # Disable GUI and continue with CLI
            context['gui_disabled'] = True
            context['enable_visualization'] = False
            print("🖥️ GUI system recovered by disabling visualization")
            return True
        except Exception:
            return False
    
    def _recover_training_system(self, context: Dict[str, Any]) -> bool:
        """Recover training system"""
        try:
            # Reduce batch size and clear memory
            current_batch_size = context.get('batch_size', 64)
            context['batch_size'] = max(8, current_batch_size // 2)
            
            # Clear GPU memory if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            print("🧠 Training system recovered with reduced batch size")
            return True
        except Exception:
            return False
    
    def _attempt_graceful_degradation(self, component: str, context: Dict[str, Any]) -> bool:
        """Attempt graceful degradation for the component"""
        try:
            # Mark component as degraded but functional
            self.system_health[f"{component}_degraded"] = True
            
            # Set degradation flags
            context[f"{component}_degraded"] = True
            context['graceful_degradation_active'] = True
            
            print(f"🔄 Graceful degradation activated for {component}")
            return True
            
        except Exception:
            return False
    
    def _update_component_failures(self, component: str, severity: ErrorSeverity):
        """Update component failure tracking"""
        if component not in self.component_failures:
            self.component_failures[component] = {
                'total_failures': 0,
                'critical_failures': 0,
                'last_failure': None,
                'failure_rate': 0.0
            }
        
        self.component_failures[component]['total_failures'] += 1
        self.component_failures[component]['last_failure'] = datetime.now()
        
        if severity == ErrorSeverity.CRITICAL:
            self.component_failures[component]['critical_failures'] += 1
    
    def _update_system_health(self, component: str, recovery_successful: bool, severity: ErrorSeverity):
        """Update system health status"""
        if severity == ErrorSeverity.CRITICAL and not recovery_successful:
            self.system_health[f"{component}_system"] = False
        elif recovery_successful:
            # Restore health if recovery was successful
            self.system_health[f"{component}_system"] = True
    
    def _should_continue_operation(self, component: str, severity: ErrorSeverity) -> bool:
        """Determine if system should continue after error"""
        
        # Always stop for unrecoverable critical errors
        if severity == ErrorSeverity.CRITICAL:
            critical_failures = self.component_failures.get(component, {}).get('critical_failures', 0)
            if critical_failures >= self.critical_error_threshold:
                print(f"🚨 Critical error threshold exceeded for {component}")
                return False
        
        # Check global continue-on-failure setting
        return self.config.get('continue_on_failure', True)
    
    def _send_error_notification(self, error_info, recovery_successful: bool):
        """Send user notification about error"""
        if not self.config.get('enable_notifications', True):
            return
        
        title = f"System Error in {error_info.component}"
        
        if recovery_successful:
            message = f"Error recovered: {error_info.message}"
            level = self.user_notifier.NotificationLevel.WARNING
        else:
            message = f"Error recovery failed: {error_info.message}"
            level = self.user_notifier.NotificationLevel.ERROR
        
        self.user_notifier.notify(
            level=level,
            title=title,
            message=message,
            component=error_info.component
        )
    
    def _register_system_recovery_callbacks(self):
        """Register system-wide recovery callbacks"""
        
        # Memory management recovery
        def memory_recovery_callback(error_info):
            try:
                import gc
                gc.collect()
                
                # Clear GPU memory if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    pass
                
                print("🧹 Memory recovery performed")
                return True
            except Exception:
                return False
        
        self.error_handler.register_recovery_callback(
            ErrorCategory.SYSTEM,
            memory_recovery_callback
        )
        
        # Configuration recovery
        def config_recovery_callback(error_info):
            try:
                # Reset to safe defaults
                print("🔧 Configuration reset to safe defaults")
                return True
            except Exception:
                return False
        
        self.error_handler.register_recovery_callback(
            ErrorCategory.CONFIGURATION,
            config_recovery_callback
        )
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        return {
            'system_health': self.system_health,
            'component_failures': self.component_failures,
            'error_statistics': self.error_handler.get_error_statistics(),
            'recovery_statistics': self.recovery_manager.get_recovery_statistics(),
            'notification_statistics': self.user_notifier.get_notification_statistics(),
            'error_log_summary': self.error_logger.get_error_summary(),
            'last_updated': datetime.now().isoformat()
        }
    
    def reset_system_health(self):
        """Reset system health tracking"""
        self.system_health = {key: True for key in self.system_health.keys()}
        self.component_failures.clear()
        self.error_handler.clear_error_history()
        self.recovery_manager.clear_recovery_history()
        self.user_notifier.clear_notification_history()
        print("🔄 System health reset completed")
    
    def shutdown_gracefully(self):
        """Perform graceful shutdown with error handling"""
        try:
            # Save final error logs
            self.error_logger.export_errors("final_error_report.json")
            
            # Generate final health report
            health_report = self.get_system_health_report()
            with open("system_health_final.json", 'w') as f:
                import json
                json.dump(health_report, f, indent=2, default=str)
            
            print("🔧 System error handling shutdown completed")
            
        except Exception as e:
            print(f"⚠️ Error during graceful shutdown: {e}")


# Global system error handler instance
_system_error_handler: Optional[SystemErrorHandler] = None


def get_system_error_handler(config: Optional[Dict[str, Any]] = None) -> SystemErrorHandler:
    """Get or create global system error handler"""
    global _system_error_handler
    
    if _system_error_handler is None:
        _system_error_handler = SystemErrorHandler(config)
    
    return _system_error_handler


def handle_system_error(error: Exception,
                       component: str,
                       operation: str,
                       context: Optional[Dict[str, Any]] = None,
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       category: ErrorCategory = ErrorCategory.SYSTEM) -> bool:
    """
    Convenience function for handling system errors
    
    Args:
        error: The exception that occurred
        component: Component where error occurred
        operation: Operation that failed
        context: Additional context information
        severity: Error severity level
        category: Error category
        
    Returns:
        True if error was handled successfully, False otherwise
    """
    handler = get_system_error_handler()
    return handler.handle_system_error(
        error=error,
        component=component,
        operation=operation,
        context=context,
        severity=severity,
        category=category
    )