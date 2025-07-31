"""
User notification system for errors and recovery actions
"""

import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass


class NotificationLevel(Enum):
    """Notification levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification channels"""
    CONSOLE = "console"
    GUI = "gui"
    LOG = "log"
    SYSTEM = "system"


@dataclass
class Notification:
    """Represents a user notification"""
    level: NotificationLevel
    title: str
    message: str
    timestamp: datetime
    channel: NotificationChannel
    component: str
    action_required: bool = False
    auto_dismiss: bool = True
    dismiss_after: float = 5.0  # seconds
    callback: Optional[Callable] = None


class UserNotifier:
    """Manages user notifications for errors and system events"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize user notifier"""
        self.config = config or self._get_default_config()
        
        # Notification storage
        self.active_notifications: List[Notification] = []
        self.notification_history: List[Notification] = []
        
        # Notification rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # GUI notification callback (set by GUI system)
        self.gui_notification_callback: Optional[Callable] = None
        
        print("🔔 UserNotifier initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default notification configuration"""
        return {
            'enable_notifications': True,
            'console_notifications': True,
            'gui_notifications': True,
            'system_notifications': False,
            'notification_levels': ['warning', 'error', 'critical'],
            'rate_limit_window': 60,  # seconds
            'max_notifications_per_window': 5,
            'auto_dismiss_timeout': 5.0,
            'show_recovery_notifications': True,
            'show_progress_notifications': False,
            'notification_sound': False
        }
    
    def notify(self, 
               level: NotificationLevel,
               title: str,
               message: str,
               component: str,
               channel: NotificationChannel = NotificationChannel.CONSOLE,
               action_required: bool = False,
               callback: Optional[Callable] = None) -> bool:
        """Send a notification to the user"""
        
        if not self.config.get('enable_notifications', True):
            return False
        
        # Check if this notification level is enabled
        enabled_levels = self.config.get('notification_levels', ['warning', 'error', 'critical'])
        if level.value not in enabled_levels:
            return False
        
        # Check rate limiting
        if self._is_rate_limited(component, level):
            return False
        
        # Create notification
        notification = Notification(
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            channel=channel,
            component=component,
            action_required=action_required,
            auto_dismiss=not action_required,
            dismiss_after=self.config.get('auto_dismiss_timeout', 5.0),
            callback=callback
        )
        
        # Send notification through appropriate channels
        success = self._send_notification(notification)
        
        if success:
            # Add to active notifications
            self.active_notifications.append(notification)
            
            # Add to history
            self.notification_history.append(notification)
            
            # Trim history if too large
            if len(self.notification_history) > 100:
                self.notification_history.pop(0)
            
            # Auto-dismiss if configured
            if notification.auto_dismiss:
                # In a real implementation, you'd use a timer
                # For now, we'll just mark it for later cleanup
                pass
        
        return success
    
    def _is_rate_limited(self, component: str, level: NotificationLevel) -> bool:
        """Check if notifications are rate limited for this component/level"""
        key = f"{component}_{level.value}"
        current_time = time.time()
        window = self.config.get('rate_limit_window', 60)
        max_notifications = self.config.get('max_notifications_per_window', 5)
        
        if key not in self.rate_limits:
            self.rate_limits[key] = {
                'count': 0,
                'window_start': current_time
            }
        
        rate_info = self.rate_limits[key]
        
        # Reset window if expired
        if current_time - rate_info['window_start'] > window:
            rate_info['count'] = 0
            rate_info['window_start'] = current_time
        
        # Check limit
        if rate_info['count'] >= max_notifications:
            return True
        
        # Increment count
        rate_info['count'] += 1
        return False
    
    def _send_notification(self, notification: Notification) -> bool:
        """Send notification through the specified channel"""
        success = False
        
        try:
            if notification.channel == NotificationChannel.CONSOLE:
                success = self._send_console_notification(notification)
            
            elif notification.channel == NotificationChannel.GUI:
                success = self._send_gui_notification(notification)
            
            elif notification.channel == NotificationChannel.SYSTEM:
                success = self._send_system_notification(notification)
            
            elif notification.channel == NotificationChannel.LOG:
                success = self._send_log_notification(notification)
            
            # Also send to console for high-priority notifications
            if notification.level in [NotificationLevel.ERROR, NotificationLevel.CRITICAL]:
                if notification.channel != NotificationChannel.CONSOLE:
                    self._send_console_notification(notification)
            
            return success
            
        except Exception as e:
            print(f"⚠️ Failed to send notification: {e}")
            return False
    
    def _send_console_notification(self, notification: Notification) -> bool:
        """Send notification to console"""
        if not self.config.get('console_notifications', True):
            return False
        
        try:
            # Choose emoji and color based on level
            if notification.level == NotificationLevel.CRITICAL:
                prefix = "🚨 CRITICAL"
            elif notification.level == NotificationLevel.ERROR:
                prefix = "❌ ERROR"
            elif notification.level == NotificationLevel.WARNING:
                prefix = "⚠️ WARNING"
            else:
                prefix = "ℹ️ INFO"
            
            # Format message
            timestamp = notification.timestamp.strftime("%H:%M:%S")
            console_message = f"[{timestamp}] {prefix} - {notification.component}: {notification.title}"
            
            if notification.message != notification.title:
                console_message += f"\n  {notification.message}"
            
            if notification.action_required:
                console_message += "\n  ⚡ Action required!"
            
            print(console_message)
            return True
            
        except Exception as e:
            print(f"⚠️ Console notification failed: {e}")
            return False
    
    def _send_gui_notification(self, notification: Notification) -> bool:
        """Send notification to GUI"""
        if not self.config.get('gui_notifications', True):
            return False
        
        try:
            if self.gui_notification_callback:
                self.gui_notification_callback(notification)
                return True
            else:
                # Fallback to console if GUI callback not available
                return self._send_console_notification(notification)
                
        except Exception as e:
            print(f"⚠️ GUI notification failed: {e}")
            return False
    
    def _send_system_notification(self, notification: Notification) -> bool:
        """Send system notification (OS-level)"""
        if not self.config.get('system_notifications', False):
            return False
        
        try:
            # Try to use system notifications
            import platform
            
            if platform.system() == "Windows":
                # Windows toast notification
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        notification.title,
                        notification.message,
                        duration=int(notification.dismiss_after),
                        threaded=True
                    )
                    return True
                except ImportError:
                    pass
            
            elif platform.system() == "Darwin":  # macOS
                # macOS notification
                try:
                    import subprocess
                    subprocess.run([
                        'osascript', '-e',
                        f'display notification "{notification.message}" with title "{notification.title}"'
                    ])
                    return True
                except Exception:
                    pass
            
            elif platform.system() == "Linux":
                # Linux notification
                try:
                    import subprocess
                    subprocess.run([
                        'notify-send',
                        notification.title,
                        notification.message
                    ])
                    return True
                except Exception:
                    pass
            
            # Fallback to console
            return self._send_console_notification(notification)
            
        except Exception as e:
            print(f"⚠️ System notification failed: {e}")
            return False
    
    def _send_log_notification(self, notification: Notification) -> bool:
        """Send notification to log file"""
        try:
            # This would integrate with the error logger
            # For now, just print to console
            return self._send_console_notification(notification)
            
        except Exception as e:
            print(f"⚠️ Log notification failed: {e}")
            return False
    
    def notify_error(self, component: str, error_message: str, 
                    recovery_attempted: bool = False, recovery_successful: bool = False):
        """Convenience method for error notifications"""
        title = f"Error in {component}"
        
        if recovery_attempted:
            if recovery_successful:
                title = f"Error Recovered in {component}"
                level = NotificationLevel.WARNING
                message = f"{error_message}\n✅ Recovery successful"
            else:
                title = f"Error Recovery Failed in {component}"
                level = NotificationLevel.ERROR
                message = f"{error_message}\n❌ Recovery failed"
        else:
            level = NotificationLevel.ERROR
            message = error_message
        
        self.notify(
            level=level,
            title=title,
            message=message,
            component=component,
            channel=NotificationChannel.CONSOLE
        )
    
    def notify_recovery(self, component: str, recovery_action: str, success: bool):
        """Convenience method for recovery notifications"""
        if not self.config.get('show_recovery_notifications', True):
            return
        
        if success:
            self.notify(
                level=NotificationLevel.INFO,
                title=f"Recovery Successful",
                message=f"{component}: {recovery_action}",
                component=component,
                channel=NotificationChannel.CONSOLE
            )
        else:
            self.notify(
                level=NotificationLevel.WARNING,
                title=f"Recovery Failed",
                message=f"{component}: {recovery_action}",
                component=component,
                channel=NotificationChannel.CONSOLE
            )
    
    def notify_progress(self, component: str, message: str):
        """Convenience method for progress notifications"""
        if not self.config.get('show_progress_notifications', False):
            return
        
        self.notify(
            level=NotificationLevel.INFO,
            title=f"Progress Update",
            message=f"{component}: {message}",
            component=component,
            channel=NotificationChannel.CONSOLE
        )
    
    def set_gui_callback(self, callback: Callable):
        """Set GUI notification callback"""
        self.gui_notification_callback = callback
        print("🔔 GUI notification callback registered")
    
    def dismiss_notification(self, notification: Notification):
        """Dismiss an active notification"""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
            
            # Call callback if provided
            if notification.callback:
                try:
                    notification.callback()
                except Exception as e:
                    print(f"⚠️ Notification callback failed: {e}")
    
    def dismiss_all_notifications(self):
        """Dismiss all active notifications"""
        self.active_notifications.clear()
        print("🔔 All notifications dismissed")
    
    def get_active_notifications(self) -> List[Notification]:
        """Get list of active notifications"""
        return self.active_notifications.copy()
    
    def get_notification_history(self, count: Optional[int] = None) -> List[Notification]:
        """Get notification history"""
        if count is None:
            return self.notification_history.copy()
        else:
            return self.notification_history[-count:] if count > 0 else []
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total_notifications = len(self.notification_history)
        
        # Count by level
        level_counts = {}
        for notification in self.notification_history:
            level = notification.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count by component
        component_counts = {}
        for notification in self.notification_history:
            component = notification.component
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            'total_notifications': total_notifications,
            'active_notifications': len(self.active_notifications),
            'notifications_by_level': level_counts,
            'notifications_by_component': component_counts,
            'recent_notifications': [
                {
                    'level': n.level.value,
                    'title': n.title,
                    'component': n.component,
                    'timestamp': n.timestamp.isoformat()
                }
                for n in self.notification_history[-10:]
            ]
        }
    
    def clear_notification_history(self):
        """Clear notification history"""
        self.notification_history.clear()
        print("🧹 Notification history cleared")