"""
Comprehensive error handling and recovery system for Neural CheChe
"""

from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory
from .recovery_manager import RecoveryManager, RecoveryStrategy
from .error_logger import ErrorLogger
from .user_notifier import UserNotifier, NotificationLevel, NotificationChannel
from .system_integration import SystemErrorHandler, get_system_error_handler, handle_system_error

__all__ = [
    'ErrorHandler',
    'ErrorSeverity', 
    'ErrorCategory',
    'RecoveryManager',
    'RecoveryStrategy',
    'ErrorLogger',
    'UserNotifier',
    'NotificationLevel',
    'NotificationChannel',
    'SystemErrorHandler',
    'get_system_error_handler',
    'handle_system_error'
]