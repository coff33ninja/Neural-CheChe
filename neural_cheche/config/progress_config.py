"""
Configuration for the progress tracking system
"""

from typing import Dict, Any
from .base_config import BaseConfig


class ProgressConfig(BaseConfig):
    """Configuration for progress tracking system"""
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default progress configuration"""
        return {
            'enable_cli_progress': True,
            'enable_gui_progress': True,
            'update_frequency': 0.1,
            'show_detailed_metrics': True,
            'display_growth_charts': True,
            'progress_bar_style': 'modern',
            'cli_progress_width': 80,
            'gui_progress_height': 20,
            'metrics_history_length': 100,
            'enable_performance_metrics': True,
            'show_eta': True,
            'show_rate': True,
            'refresh_rate': 10.0
        }
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        return {
            'enable_cli_progress': {
                'type': bool,
                'required': True
            },
            'enable_gui_progress': {
                'type': bool,
                'required': True
            },
            'update_frequency': {
                'type': float,
                'required': True,
                'min_value': 0.01,
                'max_value': 5.0
            },
            'show_detailed_metrics': {
                'type': bool,
                'required': True
            },
            'display_growth_charts': {
                'type': bool,
                'required': True
            },
            'progress_bar_style': {
                'type': str,
                'required': True,
                'choices': ['modern', 'classic', 'minimal', 'detailed']
            },
            'cli_progress_width': {
                'type': int,
                'required': True,
                'min_value': 40,
                'max_value': 200
            },
            'gui_progress_height': {
                'type': int,
                'required': True,
                'min_value': 10,
                'max_value': 50
            },
            'metrics_history_length': {
                'type': int,
                'required': True,
                'min_value': 10,
                'max_value': 1000
            },
            'enable_performance_metrics': {
                'type': bool,
                'required': True
            },
            'show_eta': {
                'type': bool,
                'required': True
            },
            'show_rate': {
                'type': bool,
                'required': True
            },
            'refresh_rate': {
                'type': float,
                'required': True,
                'min_value': 1.0,
                'max_value': 60.0
            }
        }
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for progress configuration fields"""
        return {
            'enable_cli_progress': 'Enable command-line progress bars using tqdm',
            'enable_gui_progress': 'Enable graphical progress indicators in GUI mode',
            'update_frequency': 'How often (seconds) to update progress displays',
            'show_detailed_metrics': 'Show detailed training metrics in progress displays',
            'display_growth_charts': 'Show generational growth charts in GUI',
            'progress_bar_style': 'Visual style for progress bars (modern, classic, minimal, detailed)',
            'cli_progress_width': 'Width of CLI progress bars in characters',
            'gui_progress_height': 'Height of GUI progress bars in pixels',
            'metrics_history_length': 'Number of historical metric points to keep',
            'enable_performance_metrics': 'Track and display performance metrics',
            'show_eta': 'Show estimated time of arrival in progress displays',
            'show_rate': 'Show processing rate in progress displays',
            'refresh_rate': 'Maximum refresh rate (Hz) for progress displays'
        }
    
    def is_progress_enabled(self) -> bool:
        """Check if any progress tracking is enabled"""
        return self.get('enable_cli_progress', True) or self.get('enable_gui_progress', True)
    
    def should_show_cli_progress(self) -> bool:
        """Check if CLI progress should be shown"""
        return self.get('enable_cli_progress', True)
    
    def should_show_gui_progress(self) -> bool:
        """Check if GUI progress should be shown"""
        return self.get('enable_gui_progress', True)
    
    def get_update_interval(self) -> float:
        """Get the progress update interval in seconds"""
        return self.get('update_frequency', 0.1)
    
    def get_progress_style(self) -> str:
        """Get the progress bar style"""
        return self.get('progress_bar_style', 'modern')