"""
Main configuration manager for the Neural CheChe system
"""

import json
import os
from typing import Dict, Any, Optional
from .base_config import ConfigValidationError
from .validation_config import ValidationConfig
from .progress_config import ProgressConfig
from .history_config import HistoryConfig
from .gui_config import GUIConfig
from .error_handling_config import ErrorHandlingConfig


class ConfigManager:
    """Main configuration manager that coordinates all system configurations"""
    
    def __init__(self, config_file: Optional[str]=None):
        """Initialize configuration manager"""
        self.config_file = config_file or 'config/neural_cheche_config.json'
        
        # Initialize all configuration components
        self.validation = ValidationConfig()
        self.progress = ProgressConfig()
        self.history = HistoryConfig()
        self.gui = GUIConfig()
        self.error_handling = ErrorHandlingConfig()
        
        # Core training configuration (not in separate class for simplicity)
        self._core_config = self._get_default_core_config()
        
        # Load configuration if file exists
        if os.path.exists(self.config_file):
            self.load_from_file(self.config_file)
    
    def _get_default_core_config(self) -> Dict[str, Any]:
        """Get default core training configuration"""
        return {
            'learning_rate': 0.001,
            'buffer_capacity': 100000,
            'batch_size': 64,
            'training_steps_per_generation': 50,
            'games_per_generation': 6,
            'challenger_interval': 5,
            'wildcard_interval': 3,
            'challenger_threshold': 0.55,
            'move_delay': 0.1,
            'max_moves_per_game': 200,
            'save_interval': 10,
            'device': 'auto',  # 'auto', 'cpu', 'cuda'
            'random_seed': None,
            'model_architecture': 'default'
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            'core': self._core_config,
            'validation': self.validation.to_dict(),
            'progress': self.progress.to_dict(),
            'history': self.history.to_dict(),
            'gui': self.gui.to_dict(),
            'error_handling': self.error_handling.to_dict()
        }
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            # Load each configuration section
            if 'core' in config_data:
                self._core_config.update(config_data['core'])
            
            if 'validation' in config_data:
                self.validation.update(config_data['validation'])
            
            if 'progress' in config_data:
                self.progress.update(config_data['progress'])
            
            if 'history' in config_data:
                self.history.update(config_data['history'])
            
            if 'gui' in config_data:
                self.gui.update(config_data['gui'])
            
            if 'error_handling' in config_data:
                self.error_handling.update(config_data['error_handling'])
            
            print(f"✅ Configuration loaded from {filepath}")
            
        except FileNotFoundError:
            print(f"⚠️ Configuration file {filepath} not found, using defaults")
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing configuration file {filepath}: {e}")
            raise
        except ConfigValidationError as e:
            print(f"❌ Configuration validation error: {e}")
            raise
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            raise
    
    def save_to_file(self, filepath: Optional[str]=None) -> None:
        """Save configuration to JSON file"""
        filepath = filepath or self.config_file
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save complete configuration
            config_data = self.get_complete_config()
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2, sort_keys=True)
            
            print(f"✅ Configuration saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            raise
    
    def validate_all_configs(self) -> bool:
        """Validate all configuration sections"""
        try:
            # Validate each configuration section
            configs = [
                ('validation', self.validation),
                ('progress', self.progress),
                ('history', self.history),
                ('gui', self.gui),
                ('error_handling', self.error_handling)
            ]
            
            for name, config in configs:
                try:
                    config._validate_config()
                except ConfigValidationError as e:
                    print(f"❌ Validation error in {name} config: {e}")
                    return False
            
            # Validate cross-configuration dependencies
            self._validate_cross_dependencies()
            
            print("✅ All configurations validated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def _validate_cross_dependencies(self) -> None:
        """Validate dependencies between different configuration sections"""
        # GUI progress requires GUI to be enabled
        if self.progress.get('enable_gui_progress') and not self.gui.get('enable_visualization'):
            raise ConfigValidationError(
                'progress.enable_gui_progress',
                True,
                'GUI progress requires visualization to be enabled'
            )
        
        # Validation logging requires logging to be enabled
        if self.validation.get('log_violations') and not self.error_handling.get('log_errors'):
            print("⚠️ Warning: Validation logging enabled but error logging disabled")
        
        # History backup directory should be writable
        if self.history.is_logging_enabled():
            backup_dir = self.history.get('backup_directory')
            try:
                os.makedirs(backup_dir, exist_ok=True)
                # Test write access
                test_file = os.path.join(backup_dir, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception:
                raise ConfigValidationError(
                    'history.backup_directory',
                    backup_dir,
                    'Backup directory is not writable'
                )
    
    def get_core_config(self, key: str, default: Any=None) -> Any:
        """Get core configuration value"""
        return self._core_config.get(key, default)
    
    def set_core_config(self, key: str, value: Any) -> None:
        """Set core configuration value"""
        self._core_config[key] = value
    
    def create_example_config(self, filepath: str, include_docs: bool=True) -> None:
        """Create an example configuration file with optional documentation"""
        if include_docs:
            example_config = {
                "_description": "Neural CheChe Configuration File",
                "_version": "1.0",
                "_created_by": "ConfigManager.create_example_config",
                "_documentation": {
                    "core": "Core training parameters that control the learning process",
                    "validation": "Move validation and anti-cheating settings to ensure fair gameplay",
                    "progress": "Progress tracking and display settings for monitoring training",
                    "history": "Move logging and backup settings for data persistence",
                    "gui": "Graphical interface settings for visualization",
                    "error_handling": "Error handling and recovery settings for system stability"
                },
                
                "core": {
                    "_description": "Core training configuration - controls the fundamental learning parameters",
                    **self._core_config,
                    "_field_docs": self._get_core_documentation()
                },
                
                "validation": {
                    "_description": "Move validation configuration - prevents AI cheating and ensures fair play",
                    **self.validation.to_dict(),
                    "_field_docs": self.validation.get_documentation()
                },
                
                "progress": {
                    "_description": "Progress tracking configuration - controls how training progress is displayed",
                    **self.progress.to_dict(),
                    "_field_docs": self.progress.get_documentation()
                },
                
                "history": {
                    "_description": "History and backup configuration - manages data persistence and logging",
                    **self.history.to_dict(),
                    "_field_docs": self.history.get_documentation()
                },
                
                "gui": {
                    "_description": "GUI and visualization configuration - controls the graphical interface",
                    **self.gui.to_dict(),
                    "_field_docs": self.gui.get_documentation()
                },
                
                "error_handling": {
                    "_description": "Error handling configuration - manages system stability and recovery",
                    **self.error_handling.to_dict(),
                    "_field_docs": self.error_handling.get_documentation()
                }
            }
        else:
            # Clean configuration without documentation
            example_config = self.get_complete_config()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(example_config, f, indent=2, sort_keys=True)
        
        print(f"✅ Example configuration created at {filepath}")
    
    def reset_to_defaults(self) -> None:
        """Reset all configurations to default values"""
        self.validation = ValidationConfig()
        self.progress = ProgressConfig()
        self.history = HistoryConfig()
        self.gui = GUIConfig()
        self.error_handling = ErrorHandlingConfig()
        self._core_config = self._get_default_core_config()
        
        print("✅ All configurations reset to defaults")
    
    def get_system_requirements(self) -> Dict[str, Any]:
        """Get system requirements based on current configuration"""
        requirements = {
            'disk_space_mb': 100,  # Base requirement
            'memory_mb': 512,  # Base requirement
            'features_required': []
        }
        
        # Add requirements based on enabled features
        if self.history.is_logging_enabled():
            requirements['disk_space_mb'] += 1000  # For move history
            requirements['features_required'].append('file_system_write')
        
        if self.gui.is_visualization_enabled():
            requirements['memory_mb'] += 256  # For GUI
            requirements['features_required'].append('display')
        
        if self.validation.is_validation_enabled():
            requirements['memory_mb'] += 128  # For validation
        
        if self.progress.is_progress_enabled():
            requirements['features_required'].append('terminal' if self.progress.should_show_cli_progress() else 'display')
        
        return requirements
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration status"""
        return {
            'validation_enabled': self.validation.is_validation_enabled(),
            'progress_enabled': self.progress.is_progress_enabled(),
            'history_enabled': self.history.is_logging_enabled(),
            'gui_enabled': self.gui.is_visualization_enabled(),
            'cli_progress': self.progress.should_show_cli_progress(),
            'gui_progress': self.progress.should_show_gui_progress(),
            'error_handling': {
                'graceful_degradation': self.error_handling.should_use_graceful_degradation(),
                'retry_on_failure': self.error_handling.should_retry_on_failure(),
                'continue_on_failure': self.error_handling.should_continue_on_failure()
            }
        }
    
    def _get_core_documentation(self) -> Dict[str, str]:
        """Get documentation for core configuration fields"""
        return {
            'learning_rate': 'Learning rate for neural network training (0.0001-0.1)',
            'buffer_capacity': 'Maximum number of experiences to store in replay buffer',
            'batch_size': 'Number of experiences to sample for each training step',
            'training_steps_per_generation': 'Number of training steps to perform per generation',
            'games_per_generation': 'Number of games to play per generation',
            'challenger_interval': 'How often to introduce challenger agents',
            'wildcard_interval': 'How often to introduce wildcard agents',
            'challenger_threshold': 'Win rate threshold for challenger promotion',
            'move_delay': 'Delay between moves in seconds (for visualization)',
            'max_moves_per_game': 'Maximum number of moves before declaring a draw',
            'save_interval': 'How often to save model checkpoints (in generations)',
            'device': 'Computing device to use (auto, cpu, cuda)',
            'random_seed': 'Random seed for reproducible results (null for random)',
            'model_architecture': 'Neural network architecture to use'
        }
    
    def export_config_schema(self, filepath: str) -> None:
        """Export configuration schema for validation and documentation"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Neural CheChe Configuration Schema",
            "description": "Configuration schema for the Neural CheChe AI training system",
            "type": "object",
            "properties": {
                "core": {
                    "type": "object",
                    "description": "Core training parameters",
                    "properties": self._get_core_schema_properties(),
                    "required": list(self._core_config.keys())
                },
                "validation": self.validation.get_schema(),
                "progress": self.progress.get_schema(),
                "history": self.history.get_schema(),
                "gui": self.gui.get_schema(),
                "error_handling": self.error_handling.get_schema()
            },
            "required": ["core", "validation", "progress", "history", "gui", "error_handling"]
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ Configuration schema exported to {filepath}")
    
    def _get_core_schema_properties(self) -> Dict[str, Any]:
        """Get JSON schema properties for core configuration"""
        return {
            "learning_rate": {"type": "number", "minimum": 0.0001, "maximum": 0.1},
            "buffer_capacity": {"type": "integer", "minimum": 1000, "maximum": 1000000},
            "batch_size": {"type": "integer", "minimum": 8, "maximum": 512},
            "training_steps_per_generation": {"type": "integer", "minimum": 1, "maximum": 1000},
            "games_per_generation": {"type": "integer", "minimum": 1, "maximum": 100},
            "challenger_interval": {"type": "integer", "minimum": 1, "maximum": 50},
            "wildcard_interval": {"type": "integer", "minimum": 1, "maximum": 50},
            "challenger_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "move_delay": {"type": "number", "minimum": 0.0, "maximum": 5.0},
            "max_moves_per_game": {"type": "integer", "minimum": 50, "maximum": 1000},
            "save_interval": {"type": "integer", "minimum": 1, "maximum": 100},
            "device": {"type": "string", "enum": ["auto", "cpu", "cuda"]},
            "random_seed": {"type": ["integer", "null"]},
            "model_architecture": {"type": "string"}
        }
    
    def validate_config_file(self, filepath: str) -> bool:
        """Validate a configuration file against the schema"""
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            # Basic structure validation
            required_sections = ['core', 'validation', 'progress', 'history', 'gui', 'error_handling']
            for section in required_sections:
                if section not in config_data:
                    print(f"❌ Missing required section: {section}")
                    return False
            
            # Create temporary config manager to validate
            temp_manager = ConfigManager()
            temp_manager.load_from_file(filepath)
            
            return temp_manager.validate_all_configs()
            
        except Exception as e:
            print(f"❌ Error validating configuration file: {e}")
            return False
    
    def merge_configs(self, other_config_file: str, output_file: str=None) -> None:
        """Merge another configuration file with current configuration"""
        try:
            with open(other_config_file, 'r') as f:
                other_config = json.load(f)
            
            current_config = self.get_complete_config()
            
            # Deep merge configurations
            merged_config = self._deep_merge_dicts(current_config, other_config)
            
            # Create new config manager with merged data
            temp_manager = ConfigManager()
            temp_manager._load_from_dict(merged_config)
            
            # Validate merged configuration
            if not temp_manager.validate_all_configs():
                print("❌ Merged configuration is invalid")
                return
            
            # Save merged configuration
            output_path = output_file or self.config_file
            temp_manager.save_to_file(output_path)
            
            print(f"✅ Configurations merged and saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Error merging configurations: {e}")
    
    def _deep_merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from dictionary (internal method)"""
        if 'core' in config_data:
            self._core_config.update(config_data['core'])
        
        if 'validation' in config_data:
            self.validation.update(config_data['validation'])
        
        if 'progress' in config_data:
            self.progress.update(config_data['progress'])
        
        if 'history' in config_data:
            self.history.update(config_data['history'])
        
        if 'gui' in config_data:
            self.gui.update(config_data['gui'])
        
        if 'error_handling' in config_data:
            self.error_handling.update(config_data['error_handling'])
    
    def create_preset_configs(self) -> None:
        """Create all preset configuration files"""
        presets = {
            'development': self._get_development_preset(),
            'production': self._get_production_preset(),
            'minimal': self._get_minimal_preset(),
            'gui_focused': self._get_gui_focused_preset(),
            'performance': self._get_performance_preset(),
            'debugging': self._get_debugging_preset()
        }
        
        for preset_name, preset_config in presets.items():
            filepath = f"config/examples/{preset_name}.json"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(preset_config, f, indent=2)
            
            print(f"✅ Created preset configuration: {filepath}")
    
    def _get_development_preset(self) -> Dict[str, Any]:
        """Get development preset configuration"""
        return {
            "_description": "Development Configuration - Enhanced debugging and logging",
            "_use_case": "Development and debugging with detailed logging",
            "core": {
                "learning_rate": 0.01,
                "games_per_generation": 4,
                "training_steps_per_generation": 20,
                "save_interval": 5,
                "move_delay": 0.05
            },
            "validation": {
                "enable_move_validation": True,
                "strict_piece_checking": True,
                "log_violations": True,
                "detailed_violation_logging": True,
                "validation_timeout": 10.0
            },
            "progress": {
                "enable_cli_progress": True,
                "enable_gui_progress": True,
                "update_frequency": 0.05,
                "show_detailed_metrics": True,
                "display_growth_charts": True
            },
            "history": {
                "enable_move_logging": True,
                "backup_frequency": "per_move",
                "detailed_logging": True,
                "log_board_states": True,
                "log_policy_distributions": True,
                "log_evaluation_scores": True,
                "retention_days": 7
            },
            "gui": {
                "enable_visualization": True,
                "show_captured_pieces": True,
                "show_move_hints": True,
                "show_coordinates": True,
                "highlight_last_move": True,
                "animation_speed": 0.5
            },
            "error_handling": {
                "detailed_error_logging": True,
                "notify_user_on_error": True,
                "continue_on_component_failure": False,
                "max_retry_attempts": 1
            }
        }
    
    def _get_production_preset(self) -> Dict[str, Any]:
        """Get production preset configuration"""
        return {
            "_description": "Production Configuration - Optimized for performance and stability",
            "_use_case": "Production training with optimal performance",
            "core": {
                "learning_rate": 0.001,
                "games_per_generation": 8,
                "training_steps_per_generation": 100,
                "save_interval": 20,
                "move_delay": 0.01
            },
            "validation": {
                "enable_move_validation": True,
                "strict_piece_checking": True,
                "log_violations": True,
                "detailed_violation_logging": False,
                "validation_timeout": 2.0
            },
            "progress": {
                "enable_cli_progress": True,
                "enable_gui_progress": False,
                "update_frequency": 0.5,
                "show_detailed_metrics": False,
                "display_growth_charts": False
            },
            "history": {
                "enable_move_logging": True,
                "backup_frequency": "per_generation",
                "detailed_logging": False,
                "log_board_states": False,
                "log_policy_distributions": False,
                "log_evaluation_scores": True,
                "compress_backups": True,
                "retention_days": 90
            },
            "gui": {
                "enable_visualization": False
            },
            "error_handling": {
                "detailed_error_logging": False,
                "notify_user_on_error": False,
                "continue_on_component_failure": True,
                "max_retry_attempts": 5,
                "auto_recovery_enabled": True
            }
        }
    
    def _get_minimal_preset(self) -> Dict[str, Any]:
        """Get minimal preset configuration"""
        return {
            "_description": "Minimal Configuration - Lowest resource usage",
            "_use_case": "Resource-constrained environments or basic testing",
            "core": {
                "buffer_capacity": 10000,
                "batch_size": 32,
                "games_per_generation": 2,
                "training_steps_per_generation": 10
            },
            "validation": {
                "enable_move_validation": True,
                "detailed_violation_logging": False,
                "validation_timeout": 1.0
            },
            "progress": {
                "enable_cli_progress": True,
                "enable_gui_progress": False,
                "update_frequency": 1.0,
                "show_detailed_metrics": False,
                "metrics_history_length": 10
            },
            "history": {
                "enable_move_logging": False
            },
            "gui": {
                "enable_visualization": False
            },
            "error_handling": {
                "detailed_error_logging": False,
                "max_retry_attempts": 1,
                "auto_recovery_enabled": False
            }
        }
    
    def _get_gui_focused_preset(self) -> Dict[str, Any]:
        """Get GUI-focused preset configuration"""
        return {
            "_description": "GUI-Focused Configuration - Enhanced visualization and user experience",
            "_use_case": "Interactive training with rich visual feedback",
            "core": {
                "move_delay": 0.5,
                "games_per_generation": 4
            },
            "validation": {
                "enable_move_validation": True,
                "log_violations": True
            },
            "progress": {
                "enable_cli_progress": False,
                "enable_gui_progress": True,
                "update_frequency": 0.1,
                "show_detailed_metrics": True,
                "display_growth_charts": True
            },
            "history": {
                "enable_move_logging": True,
                "backup_frequency": "per_game"
            },
            "gui": {
                "enable_visualization": True,
                "show_captured_pieces": True,
                "show_move_hints": True,
                "show_coordinates": True,
                "highlight_last_move": True,
                "animation_speed": 1.0,
                "theme": "default",
                "board_size": 500,
                "piece_size": 50
            },
            "error_handling": {
                "notify_user_on_error": True,
                "continue_on_component_failure": True
            }
        }
    
    def _get_performance_preset(self) -> Dict[str, Any]:
        """Get performance-optimized preset configuration"""
        return {
            "_description": "Performance Configuration - Maximum training speed",
            "_use_case": "High-performance training with minimal overhead",
            "core": {
                "learning_rate": 0.001,
                "games_per_generation": 12,
                "training_steps_per_generation": 200,
                "move_delay": 0.0
            },
            "validation": {
                "enable_move_validation": True,
                "detailed_violation_logging": False,
                "validation_timeout": 1.0
            },
            "progress": {
                "enable_cli_progress": True,
                "enable_gui_progress": False,
                "update_frequency": 1.0,
                "show_detailed_metrics": False
            },
            "history": {
                "enable_move_logging": False
            },
            "gui": {
                "enable_visualization": False
            },
            "error_handling": {
                "detailed_error_logging": False,
                "notify_user_on_error": False,
                "continue_on_component_failure": True,
                "max_retry_attempts": 3
            }
        }
    
    def _get_debugging_preset(self) -> Dict[str, Any]:
        """Get debugging preset configuration"""
        return {
            "_description": "Debugging Configuration - Maximum logging and error reporting",
            "_use_case": "Debugging and troubleshooting with maximum verbosity",
            "core": {
                "learning_rate": 0.005,
                "games_per_generation": 2,
                "training_steps_per_generation": 10,
                "save_interval": 1,
                "move_delay": 1.0
            },
            "validation": {
                "enable_move_validation": True,
                "strict_piece_checking": True,
                "log_violations": True,
                "detailed_violation_logging": True,
                "validation_timeout": 30.0,
                "auto_fix_minor_violations": False
            },
            "progress": {
                "enable_cli_progress": True,
                "enable_gui_progress": True,
                "update_frequency": 0.01,
                "show_detailed_metrics": True,
                "display_growth_charts": True,
                "enable_performance_metrics": True
            },
            "history": {
                "enable_move_logging": True,
                "backup_frequency": "per_move",
                "detailed_logging": True,
                "log_board_states": True,
                "log_policy_distributions": True,
                "log_evaluation_scores": True,
                "retention_days": 3,
                "compress_backups": False
            },
            "gui": {
                "enable_visualization": True,
                "show_captured_pieces": True,
                "show_move_hints": True,
                "show_coordinates": True,
                "highlight_last_move": True,
                "animation_speed": 0.1
            },
            "error_handling": {
                "detailed_error_logging": True,
                "notify_user_on_error": True,
                "continue_on_component_failure": False,
                "max_retry_attempts": 0,
                "auto_recovery_enabled": False,
                "crash_dump_enabled": True
            }
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for core configuration"""
        return {
            "type": "object",
            "description": "Core training parameters that control the learning process",
            "properties": self._get_core_schema_properties(),
            "required": list(self._core_config.keys())
        }
    
    def import_config_from_env(self) -> None:
        """Import configuration from environment variables"""
        env_mappings = {
            'NEURAL_CHECHE_LEARNING_RATE': ('learning_rate', float),
            'NEURAL_CHECHE_BATCH_SIZE': ('batch_size', int),
            'NEURAL_CHECHE_GAMES_PER_GEN': ('games_per_generation', int),
            'NEURAL_CHECHE_DEVICE': ('device', str),
            'NEURAL_CHECHE_RANDOM_SEED': ('random_seed', int),
        }
        
        for env_var, (config_key, value_type) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    if value_type is int and env_value.lower() == 'none':
                        self.set_core_config(config_key, None)
                    else:
                        self.set_core_config(config_key, value_type(env_value))
                    print(f"✅ Loaded {config_key} from environment: {env_value}")
                except ValueError as e:
                    print(f"⚠️ Invalid environment value for {env_var}: {env_value} ({e})")
    
    def export_config_template(self, filepath: str, file_format: str='json') -> None:
        """Export configuration template with all possible options"""
        template = {
            "_template_info": {
                "description": "Neural CheChe Configuration Template",
                "version": "1.0",
                "created_by": "ConfigManager.export_config_template",
                "format": file_format,
                "usage": "Copy this template and modify values as needed"
            },
            "_sections": {
                "core": "Core training parameters - controls fundamental learning",
                "validation": "Move validation - prevents AI cheating and ensures fair play",
                "progress": "Progress tracking - controls training progress display",
                "history": "History logging - manages data persistence and backups",
                "gui": "GUI settings - controls graphical interface",
                "error_handling": "Error handling - manages system stability and recovery"
            }
        }
        
        # Add all configuration sections with documentation
        for section_name, config_obj in [
            ('core', {'config': self._core_config, 'docs': self._get_core_documentation()}),
            ('validation', {'config': self.validation.to_dict(), 'docs': self.validation.get_documentation()}),
            ('progress', {'config': self.progress.to_dict(), 'docs': self.progress.get_documentation()}),
            ('history', {'config': self.history.to_dict(), 'docs': self.history.get_documentation()}),
            ('gui', {'config': self.gui.to_dict(), 'docs': self.gui.get_documentation()}),
            ('error_handling', {'config': self.error_handling.to_dict(), 'docs': self.error_handling.get_documentation()})
        ]:
            template[section_name] = {
                "_description": f"Configuration for {section_name}",
                "_fields": {}
            }
            
            for field_name, field_value in config_obj['config'].items():
                template[section_name]["_fields"][field_name] = {
                    "value": field_value,
                    "type": type(field_value).__name__,
                    "description": config_obj['docs'].get(field_name, "No description available")
                }
        
        # Save template
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if file_format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(template, f, indent=2, sort_keys=True)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
        print(f"✅ Configuration template exported to {filepath}")
    
    def compare_configs(self, other_config_file: str) -> Dict[str, Any]:
        """Compare current configuration with another configuration file"""
        try:
            with open(other_config_file, 'r') as f:
                other_config = json.load(f)
            
            current_config = self.get_complete_config()
            differences = {}
            
            # Find differences in each section
            for section in ['core', 'validation', 'progress', 'history', 'gui', 'error_handling']:
                section_diffs = {}
                
                current_section = current_config.get(section, {})
                other_section = other_config.get(section, {})
                
                # Find fields that differ
                all_keys = set(current_section.keys()) | set(other_section.keys())
                for key in all_keys:
                    current_value = current_section.get(key)
                    other_value = other_section.get(key)
                    
                    if current_value != other_value:
                        section_diffs[key] = {
                            'current': current_value,
                            'other': other_value,
                            'status': 'modified' if key in current_section and key in other_section
                                     else 'added' if key in other_section
                                     else 'removed'
                        }
                
                if section_diffs:
                    differences[section] = section_diffs
            
            return differences
            
        except Exception as e:
            print(f"❌ Error comparing configurations: {e}")
            return {}
    
    def backup_current_config(self, backup_dir: str='config/backups') -> str:
        """Create a timestamped backup of current configuration"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"config_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        os.makedirs(backup_dir, exist_ok=True)
        self.save_to_file(backup_path)
        
        print(f"✅ Configuration backed up to {backup_path}")
        return backup_path
    
    def restore_from_backup(self, backup_file: str) -> None:
        """Restore configuration from backup file"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Create backup of current config before restoring
        self.backup_current_config()
        
        # Load from backup
        self.load_from_file(backup_file)
        print(f"✅ Configuration restored from {backup_file}")
    
    def __str__(self) -> str:
        """String representation of configuration manager"""
        return f"ConfigManager(validation={self.validation.is_validation_enabled()}, " \
               f"progress={self.progress.is_progress_enabled()}, " \
               f"history={self.history.is_logging_enabled()}, " \
               f"gui={self.gui.is_visualization_enabled()})"
        return f"ConfigManager(validation={self.validation.is_validation_enabled()}, " \
               f"progress={self.progress.is_progress_enabled()}, " \
               f"history={self.history.is_logging_enabled()}, " \
               f"gui={self.gui.is_visualization_enabled()})"
