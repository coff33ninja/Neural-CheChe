"""
Configuration for the GUI and visualization system
"""

from typing import Dict, Any, Tuple
from .base_config import BaseConfig


class GUIConfig(BaseConfig):
    """Configuration for GUI and visualization system"""
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default GUI configuration"""
        return {
            'enable_visualization': True,
            'adaptive_layout': True,
            'minimum_window_size': [800, 600],
            'default_window_size': [1200, 800],
            'maximum_window_size': [1920, 1080],
            'show_captured_pieces': True,
            'progress_bar_style': 'modern',
            'auto_resize_elements': True,
            'theme': 'default',
            'font_size': 12,
            'board_size': 400,
            'piece_size': 40,
            'animation_speed': 1.0,
            'show_move_hints': True,
            'show_coordinates': True,
            'highlight_last_move': True,
            'enable_sound': False,
            'fullscreen_mode': False,
            'vsync_enabled': True,
            'fps_limit': 60
        }
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        return {
            'enable_visualization': {
                'type': bool,
                'required': True
            },
            'adaptive_layout': {
                'type': bool,
                'required': True
            },
            'minimum_window_size': {
                'type': list,
                'required': True,
                'validator': lambda x: len(x) == 2 and all(isinstance(i, int) and i > 0 for i in x),
                'validator_message': 'Window size must be [width, height] with positive integers'
            },
            'default_window_size': {
                'type': list,
                'required': True,
                'validator': lambda x: len(x) == 2 and all(isinstance(i, int) and i > 0 for i in x),
                'validator_message': 'Window size must be [width, height] with positive integers'
            },
            'maximum_window_size': {
                'type': list,
                'required': True,
                'validator': lambda x: len(x) == 2 and all(isinstance(i, int) and i > 0 for i in x),
                'validator_message': 'Window size must be [width, height] with positive integers'
            },
            'show_captured_pieces': {
                'type': bool,
                'required': True
            },
            'progress_bar_style': {
                'type': str,
                'required': True,
                'choices': ['modern', 'classic', 'minimal', 'detailed']
            },
            'auto_resize_elements': {
                'type': bool,
                'required': True
            },
            'theme': {
                'type': str,
                'required': True,
                'choices': ['default', 'dark', 'light', 'high_contrast', 'colorblind']
            },
            'font_size': {
                'type': int,
                'required': True,
                'min_value': 8,
                'max_value': 24
            },
            'board_size': {
                'type': int,
                'required': True,
                'min_value': 200,
                'max_value': 800
            },
            'piece_size': {
                'type': int,
                'required': True,
                'min_value': 20,
                'max_value': 80
            },
            'animation_speed': {
                'type': float,
                'required': True,
                'min_value': 0.1,
                'max_value': 5.0
            },
            'show_move_hints': {
                'type': bool,
                'required': True
            },
            'show_coordinates': {
                'type': bool,
                'required': True
            },
            'highlight_last_move': {
                'type': bool,
                'required': True
            },
            'enable_sound': {
                'type': bool,
                'required': True
            },
            'fullscreen_mode': {
                'type': bool,
                'required': True
            },
            'vsync_enabled': {
                'type': bool,
                'required': True
            },
            'fps_limit': {
                'type': int,
                'required': True,
                'min_value': 30,
                'max_value': 144
            }
        }
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for GUI configuration fields"""
        return {
            'enable_visualization': 'Enable the graphical user interface',
            'adaptive_layout': 'Automatically adapt layout to window size changes',
            'minimum_window_size': 'Minimum allowed window size [width, height]',
            'default_window_size': 'Default window size when application starts [width, height]',
            'maximum_window_size': 'Maximum allowed window size [width, height]',
            'show_captured_pieces': 'Display captured pieces for each player',
            'progress_bar_style': 'Visual style for progress bars',
            'auto_resize_elements': 'Automatically resize UI elements with window',
            'theme': 'Visual theme (default, dark, light, high_contrast, colorblind)',
            'font_size': 'Font size for UI text',
            'board_size': 'Size of the game board in pixels',
            'piece_size': 'Size of game pieces in pixels',
            'animation_speed': 'Speed multiplier for animations',
            'show_move_hints': 'Show visual hints for possible moves',
            'show_coordinates': 'Show board coordinates (A-H, 1-8)',
            'highlight_last_move': 'Highlight the last move made',
            'enable_sound': 'Enable sound effects',
            'fullscreen_mode': 'Start in fullscreen mode',
            'vsync_enabled': 'Enable vertical sync for smooth rendering',
            'fps_limit': 'Maximum frames per second'
        }
    
    def is_visualization_enabled(self) -> bool:
        """Check if visualization is enabled"""
        return self.get('enable_visualization', True)
    
    def get_window_size(self, size_type: str = 'default') -> Tuple[int, int]:
        """Get window size as tuple"""
        size_key = f'{size_type}_window_size'
        size_list = self.get(size_key, [1200, 800])
        return tuple(size_list)
    
    def should_show_captured_pieces(self) -> bool:
        """Check if captured pieces should be displayed"""
        return self.get('show_captured_pieces', True)
    
    def is_adaptive_layout_enabled(self) -> bool:
        """Check if adaptive layout is enabled"""
        return self.get('adaptive_layout', True)
    
    def get_theme(self) -> str:
        """Get the current theme"""
        return self.get('theme', 'default')
    
    def get_board_size(self) -> int:
        """Get the board size in pixels"""
        return self.get('board_size', 400)
    
    def get_piece_size(self) -> int:
        """Get the piece size in pixels"""
        return self.get('piece_size', 40)
    
    def validate_window_sizes(self) -> None:
        """Validate that window sizes are in correct order"""
        min_size = self.get_window_size('minimum')
        default_size = self.get_window_size('default')
        max_size = self.get_window_size('maximum')
        
        if default_size[0] < min_size[0] or default_size[1] < min_size[1]:
            raise ValueError("Default window size cannot be smaller than minimum size")
        
        if default_size[0] > max_size[0] or default_size[1] > max_size[1]:
            raise ValueError("Default window size cannot be larger than maximum size")