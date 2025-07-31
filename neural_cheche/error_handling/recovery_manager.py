"""
Recovery manager for handling common failure scenarios
"""

import time
import os
from enum import Enum
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass


class RecoveryStrategy(Enum):
    """Recovery strategies for different failure types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    DISABLE_COMPONENT = "disable_component"
    RESET_TO_DEFAULTS = "reset_to_defaults"
    RECREATE_RESOURCES = "recreate_resources"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class RecoveryAction:
    """Represents a recovery action"""
    strategy: RecoveryStrategy
    description: str
    action: Callable
    max_attempts: int = 3
    delay: float = 1.0
    success_callback: Optional[Callable] = None
    failure_callback: Optional[Callable] = None


class RecoveryManager:
    """Manages recovery strategies for common failure scenarios"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize recovery manager"""
        self.config = config or self._get_default_config()
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        
        # Register default recovery actions
        self._register_default_actions()
        
        print("🔄 RecoveryManager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default recovery configuration"""
        return {
            'enable_recovery': True,
            'max_recovery_attempts': 3,
            'recovery_delay': 1.0,
            'enable_graceful_degradation': True,
            'log_recovery_attempts': True
        }
    
    def _register_default_actions(self):
        """Register default recovery actions for common scenarios"""
        
        # File I/O recovery actions
        self.register_recovery_action(
            'file_not_found',
            RecoveryAction(
                strategy=RecoveryStrategy.RECREATE_RESOURCES,
                description="Create missing directories and files",
                action=self._create_missing_directories,
                max_attempts=2
            )
        )
        
        # Configuration recovery actions
        self.register_recovery_action(
            'config_invalid',
            RecoveryAction(
                strategy=RecoveryStrategy.RESET_TO_DEFAULTS,
                description="Reset configuration to defaults",
                action=self._reset_config_to_defaults,
                max_attempts=1
            )
        )
        
        # GUI recovery actions
        self.register_recovery_action(
            'gui_initialization_failed',
            RecoveryAction(
                strategy=RecoveryStrategy.DISABLE_COMPONENT,
                description="Disable GUI and continue with CLI only",
                action=self._disable_gui_component,
                max_attempts=1
            )
        )
        
        # Validation recovery actions
        self.register_recovery_action(
            'validation_timeout',
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Use simplified validation",
                action=self._use_simplified_validation,
                max_attempts=2
            )
        )
        
        # Progress tracking recovery actions
        self.register_recovery_action(
            'progress_display_failed',
            RecoveryAction(
                strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                description="Continue without progress display",
                action=self._disable_progress_display,
                max_attempts=1
            )
        )
        
        # History logging recovery actions
        self.register_recovery_action(
            'history_logging_failed',
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Use memory-only logging",
                action=self._use_memory_logging,
                max_attempts=2
            )
        )
        
        # Training recovery actions
        self.register_recovery_action(
            'training_step_failed',
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry training step with reduced batch size",
                action=self._retry_with_reduced_batch,
                max_attempts=3,
                delay=2.0
            )
        )
        
        # Memory recovery actions
        self.register_recovery_action(
            'out_of_memory',
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                description="Clear caches and reduce memory usage",
                action=self._clear_memory_caches,
                max_attempts=2
            )
        )
    
    def register_recovery_action(self, scenario: str, action: RecoveryAction):
        """Register a recovery action for a specific scenario"""
        if scenario not in self.recovery_actions:
            self.recovery_actions[scenario] = []
        
        self.recovery_actions[scenario].append(action)
        print(f"🔄 Recovery action registered for scenario: {scenario}")
    
    def attempt_recovery(self, scenario: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Attempt recovery for a specific scenario"""
        if not self.config.get('enable_recovery', True):
            print("⚠️ Recovery is disabled")
            return False
        
        if scenario not in self.recovery_actions:
            print(f"⚠️ No recovery actions registered for scenario: {scenario}")
            return False
        
        context = context or {}
        recovery_successful = False
        
        for action in self.recovery_actions[scenario]:
            print(f"🔄 Attempting recovery: {action.description}")
            
            for attempt in range(action.max_attempts):
                try:
                    # Execute recovery action
                    result = action.action(context)
                    
                    if result:
                        print(f"✅ Recovery successful: {action.description}")
                        recovery_successful = True
                        
                        # Log recovery attempt
                        self._log_recovery_attempt(scenario, action, attempt + 1, True)
                        
                        # Call success callback if provided
                        if action.success_callback:
                            action.success_callback(context)
                        
                        break
                    else:
                        print(f"⚠️ Recovery attempt {attempt + 1} failed: {action.description}")
                        
                        # Wait before retry
                        if attempt < action.max_attempts - 1:
                            time.sleep(action.delay)
                
                except Exception as e:
                    print(f"❌ Recovery action failed: {action.description} - {e}")
                    
                    # Log recovery attempt
                    self._log_recovery_attempt(scenario, action, attempt + 1, False, str(e))
                    
                    # Wait before retry
                    if attempt < action.max_attempts - 1:
                        time.sleep(action.delay)
            
            # If this action succeeded, we're done
            if recovery_successful:
                break
            
            # Call failure callback if all attempts failed
            if action.failure_callback:
                action.failure_callback(context)
        
        return recovery_successful
    
    def _log_recovery_attempt(self, scenario: str, action: RecoveryAction, 
                            attempt: int, success: bool, error: Optional[str] = None):
        """Log recovery attempt"""
        if self.config.get('log_recovery_attempts', True):
            log_entry = {
                'timestamp': time.time(),
                'scenario': scenario,
                'strategy': action.strategy.value,
                'description': action.description,
                'attempt': attempt,
                'success': success,
                'error': error
            }
            
            self.recovery_history.append(log_entry)
            
            # Keep only recent history
            if len(self.recovery_history) > 100:
                self.recovery_history.pop(0)
    
    # Default recovery action implementations
    
    def _create_missing_directories(self, context: Dict[str, Any]) -> bool:
        """Create missing directories and files"""
        try:
            # Extract directory paths from context
            directories = context.get('directories', [])
            files = context.get('files', [])
            
            # Create directories
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                print(f"📁 Created directory: {directory}")
            
            # Create empty files if needed
            for file_path in files:
                if not os.path.exists(file_path):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write('{}')  # Empty JSON for most cases
                    print(f"📄 Created file: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create missing resources: {e}")
            return False
    
    def _reset_config_to_defaults(self, context: Dict[str, Any]) -> bool:
        """Reset configuration to defaults"""
        try:
            config_manager = context.get('config_manager')
            if config_manager:
                config_manager.reset_to_defaults()
                print("🔧 Configuration reset to defaults")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Failed to reset configuration: {e}")
            return False
    
    def _disable_gui_component(self, context: Dict[str, Any]) -> bool:
        """Disable GUI component and continue with CLI"""
        try:
            # Set GUI disabled in context
            context['gui_disabled'] = True
            context['enable_visualization'] = False
            print("🖥️ GUI disabled, continuing with CLI only")
            return True
            
        except Exception as e:
            print(f"❌ Failed to disable GUI: {e}")
            return False
    
    def _use_simplified_validation(self, context: Dict[str, Any]) -> bool:
        """Use simplified validation when full validation fails"""
        try:
            context['use_simplified_validation'] = True
            context['validation_timeout'] = context.get('validation_timeout', 5.0) * 0.5
            print("🛡️ Switched to simplified validation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to switch to simplified validation: {e}")
            return False
    
    def _disable_progress_display(self, context: Dict[str, Any]) -> bool:
        """Disable progress display and continue without it"""
        try:
            context['progress_disabled'] = True
            context['enable_cli_progress'] = False
            context['enable_gui_progress'] = False
            print("📊 Progress display disabled")
            return True
            
        except Exception as e:
            print(f"❌ Failed to disable progress display: {e}")
            return False
    
    def _use_memory_logging(self, context: Dict[str, Any]) -> bool:
        """Use memory-only logging when file logging fails"""
        try:
            context['use_memory_logging'] = True
            context['disable_file_logging'] = True
            print("📝 Switched to memory-only logging")
            return True
            
        except Exception as e:
            print(f"❌ Failed to switch to memory logging: {e}")
            return False
    
    def _retry_with_reduced_batch(self, context: Dict[str, Any]) -> bool:
        """Retry training with reduced batch size"""
        try:
            current_batch_size = context.get('batch_size', 64)
            new_batch_size = max(8, current_batch_size // 2)
            context['batch_size'] = new_batch_size
            print(f"🧠 Reduced batch size from {current_batch_size} to {new_batch_size}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to reduce batch size: {e}")
            return False
    
    def _clear_memory_caches(self, context: Dict[str, Any]) -> bool:
        """Clear memory caches to free up memory"""
        try:
            # Clear GPU memory if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print("🧹 GPU memory cache cleared")
            except ImportError:
                pass
            
            # Clear Python garbage collection
            import gc
            gc.collect()
            print("🧹 Python garbage collection performed")
            
            context['memory_cleared'] = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to clear memory caches: {e}")
            return False
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        total_attempts = len(self.recovery_history)
        successful_attempts = sum(1 for entry in self.recovery_history if entry['success'])
        
        # Group by scenario
        scenario_stats = {}
        for entry in self.recovery_history:
            scenario = entry['scenario']
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {'attempts': 0, 'successes': 0}
            
            scenario_stats[scenario]['attempts'] += 1
            if entry['success']:
                scenario_stats[scenario]['successes'] += 1
        
        # Calculate success rates
        for scenario, stats in scenario_stats.items():
            stats['success_rate'] = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0
        
        return {
            'total_recovery_attempts': total_attempts,
            'successful_recoveries': successful_attempts,
            'overall_success_rate': f"{(successful_attempts / total_attempts * 100):.1f}%" if total_attempts > 0 else "0%",
            'scenario_statistics': scenario_stats,
            'recent_recoveries': self.recovery_history[-10:]  # Last 10 recovery attempts
        }
    
    def clear_recovery_history(self):
        """Clear recovery history"""
        self.recovery_history.clear()
        print("🧹 Recovery history cleared")