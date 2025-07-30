"""
Legacy configuration compatibility layer for Neural CheChe
Provides backward compatibility with the old Config class interface
"""

from typing import Dict, Any, Optional
from .config_manager import ConfigManager


class Config:
    """Legacy Config class for backward compatibility"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize with optional config dictionary"""
        self._config_manager = ConfigManager()
        
        if config_dict:
            self._load_from_dict(config_dict)
        
        # Legacy properties for backward compatibility
        self.enable_visualization = self._config_manager.gui.is_visualization_enabled()
        self.mcts_simulations = self._config_manager.get_core_config('mcts_simulations', 100)
        self.training_steps_per_generation = self._config_manager.get_core_config('training_steps_per_generation', 100)
        self.move_delay = self._config_manager.get_core_config('move_delay', 0.1)
        self.device = self._config_manager.get_core_config('device', 'auto')
    
    def _load_from_dict(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary"""
        # Load core settings
        if 'core' in config_dict:
            for key, value in config_dict['core'].items():
                self._config_manager.set_core_config(key, value)
        
        # Load subsystem configurations
        for subsystem in ['validation', 'progress', 'history', 'gui', 'error_handling']:
            if subsystem in config_dict:
                config_section = getattr(self._config_manager, subsystem)
                config_section.update(config_dict[subsystem])
        
        # Handle legacy flat structure
        legacy_mappings = {
            'learning_rate': ('core', 'learning_rate'),
            'buffer_capacity': ('core', 'buffer_capacity'),
            'batch_size': ('core', 'batch_size'),
            'enable_visualization': ('gui', 'enable_visualization'),
            'enable_cli_progress': ('progress', 'enable_cli_progress'),
            'enable_gui_progress': ('progress', 'enable_gui_progress'),
            'mcts_simulations': ('core', 'mcts_simulations'),
            'training_steps_per_generation': ('core', 'training_steps_per_generation'),
            'move_delay': ('core', 'move_delay'),
            'device': ('core', 'device')
        }
        
        for legacy_key, (section, new_key) in legacy_mappings.items():
            if legacy_key in config_dict:
                if section == 'core':
                    self._config_manager.set_core_config(new_key, config_dict[legacy_key])
                else:
                    config_section = getattr(self._config_manager, section)
                    config_section.set(new_key, config_dict[legacy_key])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return self._config_manager.get_complete_config()
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information for the configuration"""
        return {
            'Learning Rate': self._config_manager.get_core_config('learning_rate', 0.001),
            'Buffer Capacity': self._config_manager.get_core_config('buffer_capacity', 100000),
            'Batch Size': self._config_manager.get_core_config('batch_size', 32),
            'MCTS Simulations': self.mcts_simulations,
            'Training Steps': self.training_steps_per_generation,
            'Move Delay': self.move_delay,
            'Visualization': 'Enabled' if self.enable_visualization else 'Disabled',
            'Device': self.device or 'Auto-detect'
        }
    
    def save_to_file(self, filepath: str):
        """Save configuration to file"""
        self._config_manager.save_to_file(filepath)
    
    def load_from_file(self, filepath: str):
        """Load configuration from file"""
        self._config_manager.load_from_file(filepath)
        # Update legacy properties
        self._update_legacy_properties()
    
    def _update_legacy_properties(self):
        """Update legacy properties from config manager"""
        self.enable_visualization = self._config_manager.gui.is_visualization_enabled()
        self.mcts_simulations = self._config_manager.get_core_config('mcts_simulations', 100)
        self.training_steps_per_generation = self._config_manager.get_core_config('training_steps_per_generation', 100)
        self.move_delay = self._config_manager.get_core_config('move_delay', 0.1)
        self.device = self._config_manager.get_core_config('device', 'auto')


def load_config(filepath: str) -> Config:
    """Load configuration from file"""
    config = Config()
    config.load_from_file(filepath)
    return config


def save_config(config: Config, filepath: str):
    """Save configuration to file"""
    config.save_to_file(filepath)


def get_preset_configs() -> Dict[str, Config]:
    """Get preset configurations"""
    presets = {}
    
    # Default configuration
    default_config = Config({
        'core': {
            'learning_rate': 0.001,
            'buffer_capacity': 100000,
            'batch_size': 32,
            'training_steps_per_generation': 100,
            'games_per_generation': 20,
            'challenger_interval': 5,
            'wildcard_interval': 10,
            'challenger_threshold': 0.6,
            'move_delay': 0.1,
            'max_moves_per_game': 200,
            'save_interval': 10,
            'mcts_simulations': 100,
            'device': 'auto'
        },
        'validation': {
            'enable_validation': True,
            'log_violations': True,
            'max_retries': 3
        },
        'progress': {
            'enable_cli_progress': True,
            'enable_gui_progress': False,
            'update_frequency': 1.0
        },
        'history': {
            'enable_logging': True,
            'backup_directory': 'backups',
            'retention_days': 30
        },
        'gui': {
            'enable_visualization': True,
            'window_width': 1200,
            'window_height': 800,
            'fps_limit': 60
        },
        'error_handling': {
            'continue_on_component_failure': True,
            'max_retries': 3,
            'log_errors': True
        }
    })
    presets['default'] = default_config
    
    # Training configuration (optimized for training speed)
    training_config = Config({
        'core': {
            'learning_rate': 0.002,
            'buffer_capacity': 50000,
            'batch_size': 64,
            'training_steps_per_generation': 150,
            'games_per_generation': 30,
            'challenger_interval': 3,
            'wildcard_interval': 8,
            'challenger_threshold': 0.65,
            'move_delay': 0.05,
            'max_moves_per_game': 150,
            'save_interval': 5,
            'mcts_simulations': 50,
            'device': 'auto'
        },
        'validation': {
            'enable_validation': True,
            'log_violations': False,
            'max_retries': 2
        },
        'progress': {
            'enable_cli_progress': True,
            'enable_gui_progress': False,
            'update_frequency': 0.5
        },
        'history': {
            'enable_logging': False,
            'backup_directory': 'backups',
            'retention_days': 7
        },
        'gui': {
            'enable_visualization': False,
            'window_width': 800,
            'window_height': 600,
            'fps_limit': 30
        },
        'error_handling': {
            'continue_on_component_failure': True,
            'max_retries': 2,
            'log_errors': True
        }
    })
    presets['training'] = training_config
    
    # Fast configuration (minimal features for quick testing)
    fast_config = Config({
        'core': {
            'learning_rate': 0.005,
            'buffer_capacity': 10000,
            'batch_size': 16,
            'training_steps_per_generation': 25,
            'games_per_generation': 10,
            'challenger_interval': 2,
            'wildcard_interval': 5,
            'challenger_threshold': 0.55,
            'move_delay': 0.01,
            'max_moves_per_game': 100,
            'save_interval': 2,
            'mcts_simulations': 25,
            'device': 'auto'
        },
        'validation': {
            'enable_validation': False,
            'log_violations': False,
            'max_retries': 1
        },
        'progress': {
            'enable_cli_progress': True,
            'enable_gui_progress': False,
            'update_frequency': 2.0
        },
        'history': {
            'enable_logging': False,
            'backup_directory': 'backups',
            'retention_days': 1
        },
        'gui': {
            'enable_visualization': False,
            'window_width': 600,
            'window_height': 400,
            'fps_limit': 30
        },
        'error_handling': {
            'continue_on_component_failure': True,
            'max_retries': 1,
            'log_errors': False
        }
    })
    presets['fast'] = fast_config
    
    # Visualization configuration (optimized for visual demonstration)
    visualization_config = Config({
        'core': {
            'learning_rate': 0.001,
            'buffer_capacity': 75000,
            'batch_size': 32,
            'training_steps_per_generation': 75,
            'games_per_generation': 15,
            'challenger_interval': 4,
            'wildcard_interval': 8,
            'challenger_threshold': 0.6,
            'move_delay': 0.5,
            'max_moves_per_game': 200,
            'save_interval': 5,
            'mcts_simulations': 75,
            'device': 'auto'
        },
        'validation': {
            'enable_validation': True,
            'log_violations': True,
            'max_retries': 3
        },
        'progress': {
            'enable_cli_progress': True,
            'enable_gui_progress': True,
            'update_frequency': 0.5
        },
        'history': {
            'enable_logging': True,
            'backup_directory': 'backups',
            'retention_days': 14
        },
        'gui': {
            'enable_visualization': True,
            'window_width': 1400,
            'window_height': 900,
            'fps_limit': 60
        },
        'error_handling': {
            'continue_on_component_failure': True,
            'max_retries': 3,
            'log_errors': True
        }
    })
    presets['visualization'] = visualization_config
    
    return presets