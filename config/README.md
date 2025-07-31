# Neural CheChe Configuration System

The Neural CheChe configuration system provides comprehensive control over all aspects of the AI training process. This document explains how to configure and customize the system for your specific needs.

## Configuration Structure

The configuration system is organized into six main sections:

- **Core**: Fundamental training parameters
- **Validation**: Move validation and anti-cheating settings
- **Progress**: Progress tracking and display settings
- **History**: Move logging and backup settings
- **GUI**: Graphical interface and visualization settings
- **Error Handling**: Error handling and recovery settings

## Quick Start

### Using Default Configuration

```python
from neural_cheche.league import LeagueManager

# Use default configuration
league_manager = LeagueManager()
```

### Using Configuration File

```python
from neural_cheche.league import LeagueManager

# Load from configuration file
league_manager = LeagueManager(config_file='config/my_config.json')
```

### Using ConfigManager Directly

```python
from neural_cheche.config import ConfigManager
from neural_cheche.league import LeagueManager

# Create and customize configuration
config_manager = ConfigManager()
config_manager.set_core_config('learning_rate', 0.005)
config_manager.validation.set('log_violations', True)

# Use with LeagueManager
league_manager = LeagueManager(config_manager=config_manager)
```

## Configuration Sections

### Core Configuration

Controls fundamental training parameters:

```json
{
  "core": {
    "learning_rate": 0.001,
    "buffer_capacity": 100000,
    "batch_size": 64,
    "training_steps_per_generation": 50,
    "games_per_generation": 6,
    "challenger_interval": 5,
    "wildcard_interval": 3,
    "challenger_threshold": 0.55,
    "move_delay": 0.1,
    "max_moves_per_game": 200,
    "save_interval": 10,
    "device": "auto",
    "random_seed": null,
    "model_architecture": "default"
  }
}
```

**Key Parameters:**
- `learning_rate`: Neural network learning rate (0.0001-0.1)
- `buffer_capacity`: Maximum experiences in replay buffer
- `batch_size`: Training batch size (8-512)
- `games_per_generation`: Number of games per training generation
- `challenger_interval`: How often to introduce challenger agents
- `move_delay`: Delay between moves for visualization (seconds)

### Validation Configuration

Controls move validation and anti-cheating measures:

```json
{
  "validation": {
    "enable_move_validation": true,
    "strict_piece_checking": true,
    "log_violations": true,
    "violation_log_path": "logs/violations.json",
    "max_retries": 3,
    "enable_magical_piece_detection": true,
    "enable_board_state_validation": true,
    "validation_timeout": 5.0,
    "detailed_violation_logging": true,
    "auto_fix_minor_violations": false
  }
}
```

**Key Parameters:**
- `enable_move_validation`: Enable/disable move validation system
- `strict_piece_checking`: Strict validation of piece movements
- `log_violations`: Log validation violations to file
- `magical_piece_detection`: Detect illegal piece creation
- `validation_timeout`: Maximum time for validation (seconds)

### Progress Configuration

Controls progress tracking and display:

```json
{
  "progress": {
    "enable_cli_progress": true,
    "enable_gui_progress": true,
    "update_frequency": 0.1,
    "show_detailed_metrics": true,
    "display_growth_charts": true,
    "progress_bar_style": "modern",
    "cli_progress_width": 80,
    "gui_progress_height": 20,
    "metrics_history_length": 100,
    "enable_performance_metrics": true,
    "show_eta": true,
    "show_rate": true,
    "refresh_rate": 10.0
  }
}
```

**Key Parameters:**
- `enable_cli_progress`: Show command-line progress bars
- `enable_gui_progress`: Show GUI progress indicators
- `update_frequency`: How often to update progress (seconds)
- `show_detailed_metrics`: Display detailed training metrics
- `display_growth_charts`: Show historical performance charts

### History Configuration

Controls move logging and backup systems:

```json
{
  "history": {
    "enable_move_logging": true,
    "backup_directory": "move_history/",
    "backup_frequency": "per_game",
    "retention_days": 30,
    "compress_backups": false,
    "detailed_logging": true,
    "log_board_states": true,
    "log_policy_distributions": true,
    "log_evaluation_scores": true,
    "max_log_file_size": 100,
    "backup_format": "json",
    "enable_incremental_backups": true,
    "backup_compression_level": 6,
    "auto_cleanup_enabled": true
  }
}
```

**Key Parameters:**
- `enable_move_logging`: Enable/disable move history logging
- `backup_frequency`: When to create backups ("per_move", "per_game", "per_generation", "manual")
- `retention_days`: How long to keep backup files
- `compress_backups`: Enable backup compression
- `detailed_logging`: Include detailed move information

### GUI Configuration

Controls graphical interface and visualization:

```json
{
  "gui": {
    "enable_visualization": true,
    "adaptive_layout": true,
    "minimum_window_size": [800, 600],
    "default_window_size": [1200, 800],
    "maximum_window_size": [1920, 1080],
    "show_captured_pieces": true,
    "progress_bar_style": "modern",
    "auto_resize_elements": true,
    "theme": "default",
    "font_size": 12,
    "board_size": 400,
    "piece_size": 40,
    "animation_speed": 1.0,
    "show_move_hints": true,
    "show_coordinates": true,
    "highlight_last_move": true,
    "enable_sound": false,
    "fullscreen_mode": false,
    "vsync_enabled": true,
    "fps_limit": 60
  }
}
```

**Key Parameters:**
- `enable_visualization`: Enable/disable GUI visualization
- `adaptive_layout`: Automatically adapt layout to window size
- `show_captured_pieces`: Display captured pieces
- `animation_speed`: Speed of move animations (0.1-2.0)
- `board_size`: Size of game board in pixels

### Error Handling Configuration

Controls error handling and recovery behavior:

```json
{
  "error_handling": {
    "detailed_error_logging": true,
    "log_errors": true,
    "error_log_path": "logs/errors.log",
    "notify_user_on_error": true,
    "continue_on_component_failure": true,
    "graceful_degradation": true,
    "max_retry_attempts": 3,
    "retry_delay": 1.0,
    "auto_recovery_enabled": true,
    "fallback_to_defaults": true
  }
}
```

**Key Parameters:**
- `continue_on_component_failure`: Continue training if components fail
- `graceful_degradation`: Disable failed components instead of crashing
- `max_retry_attempts`: Number of times to retry failed operations
- `auto_recovery_enabled`: Automatically attempt to recover from errors

## Preset Configurations

The system includes several preset configurations for common use cases:

### Development (`config/examples/development.json`)
- Enhanced debugging and logging
- Detailed violation tracking
- Frequent saves and backups
- GUI visualization enabled

### Production (`config/examples/production.json`)
- Optimized for performance
- Minimal logging overhead
- Automatic error recovery
- GUI disabled for speed

### Minimal (`config/examples/minimal.json`)
- Lowest resource usage
- Basic functionality only
- Suitable for testing or limited hardware

### GUI Focused (`config/examples/gui_focused.json`)
- Rich visual experience
- Interactive training
- Enhanced visualization features

## Configuration Management

### Creating Configuration Files

```python
from neural_cheche.config import ConfigManager

# Create configuration manager
config_manager = ConfigManager()

# Create example configuration with documentation
config_manager.create_example_config(
    'config/my_config.json', 
    include_docs=True
)
```

### Validating Configuration

```python
# Validate all configuration sections
if config_manager.validate_all_configs():
    print("Configuration is valid")
else:
    print("Configuration has errors")

# Validate specific configuration file
if config_manager.validate_config_file('config/my_config.json'):
    print("File is valid")
```

### Merging Configurations

```python
# Merge configurations
config_manager.merge_configs(
    'config/base.json',
    'config/custom.json',
    'config/merged.json'
)
```

### Getting System Requirements

```python
# Check system requirements based on configuration
requirements = config_manager.get_system_requirements()
print(f"Disk space needed: {requirements['disk_space_mb']} MB")
print(f"Memory needed: {requirements['memory_mb']} MB")
print(f"Features required: {requirements['features_required']}")
```

## Advanced Usage

### Custom Configuration Classes

You can extend the configuration system by creating custom configuration classes:

```python
from neural_cheche.config.base_config import BaseConfig

class MyCustomConfig(BaseConfig):
    def _get_defaults(self):
        return {
            'my_setting': 'default_value',
            'my_number': 42
        }
    
    def _get_validation_rules(self):
        return {
            'my_setting': {'type': str, 'required': True},
            'my_number': {'type': int, 'min_value': 0, 'max_value': 100}
        }
```

### Runtime Configuration Changes

```python
# Change configuration at runtime
config_manager.set_core_config('learning_rate', 0.005)
config_manager.validation.set('log_violations', False)

# Save changes
config_manager.save_to_file('config/updated_config.json')
```

### Configuration Monitoring

```python
# Get configuration summary
summary = config_manager.get_config_summary()
print(f"Validation enabled: {summary['validation_enabled']}")
print(f"GUI enabled: {summary['gui_enabled']}")

# Get system status
status = league_manager.get_system_status()
for system, details in status.items():
    print(f"{system}: {details}")
```

## Troubleshooting

### Common Configuration Issues

1. **Invalid JSON Format**: Ensure your configuration file is valid JSON
2. **Missing Required Fields**: Check that all required fields are present
3. **Invalid Values**: Verify that values are within acceptable ranges
4. **File Permissions**: Ensure the system can read/write configuration files
5. **Cross-Dependencies**: Some features require others to be enabled

### Debugging Configuration

```python
# Enable detailed error logging
config_manager.error_handling.set('detailed_error_logging', True)

# Check field information
field_info = config_manager.validation.get_field_info('enable_move_validation')
print(field_info)

# List all configuration fields
all_fields = config_manager.validation.list_all_fields()
for field_name, info in all_fields.items():
    print(f"{field_name}: {info}")
```

### Reset to Defaults

```python
# Reset all configurations to defaults
config_manager.reset_to_defaults()

# Reset specific field to default
config_manager.validation.reset_field_to_default('log_violations')
```

## Best Practices

1. **Start with Presets**: Use preset configurations as starting points
2. **Validate Early**: Always validate configuration before training
3. **Document Changes**: Keep track of configuration modifications
4. **Test Configurations**: Test new configurations with short training runs
5. **Backup Configurations**: Keep backups of working configurations
6. **Monitor Resources**: Check system requirements for your configuration
7. **Use Version Control**: Track configuration changes in version control

## Support

For additional help with configuration:

1. Check the example configurations in `config/examples/`
2. Use the built-in validation and documentation features
3. Review the configuration schema with `export_config_schema()`
4. Enable detailed error logging for troubleshooting