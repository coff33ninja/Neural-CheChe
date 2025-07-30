"""
Responsive Layout Manager - Handles dynamic layout adaptation for different screen sizes
"""

from typing import Dict, Tuple, Any
import pygame


class ResponsiveLayoutManager:
    """Manages responsive layout adaptation for different window sizes"""
    
    # Layout breakpoints
    BREAKPOINTS = {
        'small': 800,
        'medium': 1200,
        'large': 1600,
        'xlarge': 2000
    }
    
    # Minimum dimensions
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    MIN_SQUARE_SIZE = 30
    MAX_SQUARE_SIZE = 80
    
    def __init__(self):
        self.current_layout = 'medium'
        self.layout_cache = {}
        
    def get_layout_size(self, width: int, height: int) -> str:
        """
        Determine layout size category based on window dimensions
        
        Args:
            width: Window width
            height: Window height
            
        Returns:
            Layout size category
        """
        if width < self.BREAKPOINTS['small']:
            return 'small'
        elif width < self.BREAKPOINTS['medium']:
            return 'medium'
        elif width < self.BREAKPOINTS['large']:
            return 'large'
        else:
            return 'xlarge'
    
    def calculate_optimal_layout(self, width: int, height: int) -> Dict[str, Any]:
        """
        Calculate optimal layout for given window dimensions
        
        Args:
            width: Window width
            height: Window height
            
        Returns:
            Dictionary containing layout configuration
        """
        try:
            # Check cache first
            cache_key = f"{width}x{height}"
            if cache_key in self.layout_cache:
                return self.layout_cache[cache_key]
            
            # Enforce minimum dimensions
            width = max(width, self.MIN_WINDOW_WIDTH)
            height = max(height, self.MIN_WINDOW_HEIGHT)
            
            layout_size = self.get_layout_size(width, height)
            
            # Calculate layout based on size category
            if layout_size == 'small':
                layout = self._calculate_small_layout(width, height)
            elif layout_size == 'medium':
                layout = self._calculate_medium_layout(width, height)
            elif layout_size == 'large':
                layout = self._calculate_large_layout(width, height)
            else:  # xlarge
                layout = self._calculate_xlarge_layout(width, height)
            
            # Add common layout properties
            layout.update({
                'window_size': (width, height),
                'layout_category': layout_size,
                'responsive_enabled': True
            })
            
            # Cache the result
            self.layout_cache[cache_key] = layout
            
            return layout
            
        except Exception as e:
            print(f"⚠️ Error calculating optimal layout: {e}")
            return self._get_fallback_layout(width, height)
    
    def _calculate_small_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Calculate layout for small screens (< 800px)"""
        # Compact layout - single column, smaller elements
        margin = 10
        square_size = max(self.MIN_SQUARE_SIZE, min(40, (width - 4 * margin) // 16))
        
        # Single board at a time or stacked vertically
        board_width = square_size * 8
        board_height = square_size * 8
        
        return {
            'square_size': square_size,
            'margin': margin,
            'board_positions': {
                'chess': (margin, margin + 50),
                'checkers': (margin, margin + 50 + board_height + 20)
            },
            'captured_pieces_areas': {
                'chess': {
                    'x': margin + board_width + 10,
                    'y': margin + 50,
                    'width': min(180, width - board_width - 3 * margin),
                    'height': board_height
                },
                'checkers': {
                    'x': margin + board_width + 10,
                    'y': margin + 50 + board_height + 20,
                    'width': min(180, width - board_width - 3 * margin),
                    'height': board_height
                }
            },
            'score_panel_area': {
                'x': margin,
                'y': height - 60 - margin,
                'width': width - 2 * margin,
                'height': 60
            },
            'progress_area': {
                'x': margin,
                'y': height - 130 - margin,
                'width': width - 2 * margin,
                'height': 60
            },
            'layout_style': 'compact_vertical'
        }
    
    def _calculate_medium_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Calculate layout for medium screens (800-1200px)"""
        # Standard layout - side by side boards
        margin = 20
        available_width = width - 2 * margin
        square_size = max(self.MIN_SQUARE_SIZE, min(60, available_width // 20))
        
        board_width = square_size * 8
        board_spacing = 50
        
        chess_x = margin
        checkers_x = chess_x + board_width + board_spacing
        
        return {
            'square_size': square_size,
            'margin': margin,
            'board_positions': {
                'chess': (chess_x, margin + 50),
                'checkers': (checkers_x, margin + 50)
            },
            'captured_pieces_areas': {
                'chess': {
                    'x': chess_x + board_width + 10,
                    'y': margin + 50,
                    'width': 200,
                    'height': board_width
                },
                'checkers': {
                    'x': min(checkers_x + board_width + 10, width - 220),
                    'y': margin + 50,
                    'width': 200,
                    'height': board_width
                }
            },
            'score_panel_area': {
                'x': margin,
                'y': height - 80 - margin,
                'width': width - 2 * margin,
                'height': 80
            },
            'progress_area': {
                'x': margin,
                'y': height - 170 - margin,
                'width': width - 2 * margin,
                'height': 80
            },
            'layout_style': 'standard_horizontal'
        }
    
    def _calculate_large_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Calculate layout for large screens (1200-1600px)"""
        # Spacious layout with larger elements
        margin = 30
        square_size = max(50, min(self.MAX_SQUARE_SIZE, (width - 6 * margin) // 20))
        
        board_width = square_size * 8
        board_spacing = 80
        
        chess_x = margin
        checkers_x = chess_x + board_width + board_spacing
        
        return {
            'square_size': square_size,
            'margin': margin,
            'board_positions': {
                'chess': (chess_x, margin + 60),
                'checkers': (checkers_x, margin + 60)
            },
            'captured_pieces_areas': {
                'chess': {
                    'x': chess_x + board_width + 20,
                    'y': margin + 60,
                    'width': 240,
                    'height': board_width
                },
                'checkers': {
                    'x': checkers_x + board_width + 20,
                    'y': margin + 60,
                    'width': 240,
                    'height': board_width
                }
            },
            'score_panel_area': {
                'x': margin,
                'y': height - 100 - margin,
                'width': width - 2 * margin,
                'height': 100
            },
            'progress_area': {
                'x': margin,
                'y': height - 210 - margin,
                'width': width - 2 * margin,
                'height': 100
            },
            'layout_style': 'spacious_horizontal'
        }
    
    def _calculate_xlarge_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Calculate layout for extra large screens (> 1600px)"""
        # Ultra-wide layout with maximum spacing
        margin = 50
        square_size = min(self.MAX_SQUARE_SIZE, (width - 8 * margin) // 24)
        
        board_width = square_size * 8
        board_spacing = 120
        
        # Center the boards
        total_board_width = 2 * board_width + board_spacing + 2 * 260  # Include captured pieces
        start_x = (width - total_board_width) // 2
        
        chess_x = start_x
        checkers_x = chess_x + board_width + board_spacing + 260
        
        return {
            'square_size': square_size,
            'margin': margin,
            'board_positions': {
                'chess': (chess_x, margin + 80),
                'checkers': (checkers_x, margin + 80)
            },
            'captured_pieces_areas': {
                'chess': {
                    'x': chess_x + board_width + 30,
                    'y': margin + 80,
                    'width': 260,
                    'height': board_width
                },
                'checkers': {
                    'x': checkers_x + board_width + 30,
                    'y': margin + 80,
                    'width': 260,
                    'height': board_width
                }
            },
            'score_panel_area': {
                'x': margin,
                'y': height - 120 - margin,
                'width': width - 2 * margin,
                'height': 120
            },
            'progress_area': {
                'x': margin,
                'y': height - 250 - margin,
                'width': width - 2 * margin,
                'height': 120
            },
            'layout_style': 'ultra_wide'
        }
    
    def _get_fallback_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Get a safe fallback layout"""
        return {
            'square_size': 50,
            'margin': 20,
            'board_positions': {
                'chess': (20, 70),
                'checkers': (420, 70)
            },
            'captured_pieces_areas': {
                'chess': {'x': 420, 'y': 70, 'width': 200, 'height': 400},
                'checkers': {'x': 820, 'y': 70, 'width': 200, 'height': 400}
            },
            'score_panel_area': {'x': 20, 'y': height - 100, 'width': width - 40, 'height': 80},
            'progress_area': {'x': 20, 'y': height - 190, 'width': width - 40, 'height': 80},
            'window_size': (width, height),
            'layout_category': 'fallback',
            'layout_style': 'safe_fallback',
            'responsive_enabled': False
        }
    
    def adapt_fonts_to_layout(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt font sizes based on layout
        
        Args:
            layout: Layout configuration
            
        Returns:
            Dictionary with font size recommendations
        """
        try:
            square_size = layout.get('square_size', 50)
            layout_category = layout.get('layout_category', 'medium')
            
            # Base font sizes
            if layout_category == 'small':
                base_multiplier = 0.8
            elif layout_category == 'medium':
                base_multiplier = 1.0
            elif layout_category == 'large':
                base_multiplier = 1.2
            else:  # xlarge
                base_multiplier = 1.4
            
            font_sizes = {
                'piece_font': max(20, int(square_size * 0.8 * base_multiplier)),
                'title_font': max(16, int(24 * base_multiplier)),
                'info_font': max(12, int(16 * base_multiplier)),
                'small_font': max(10, int(12 * base_multiplier))
            }
            
            return font_sizes
            
        except Exception as e:
            print(f"⚠️ Error adapting fonts: {e}")
            return {
                'piece_font': 30,
                'title_font': 20,
                'info_font': 16,
                'small_font': 12
            }
    
    def get_element_priorities(self, layout: Dict[str, Any]) -> Dict[str, int]:
        """
        Get element display priorities based on layout
        
        Args:
            layout: Layout configuration
            
        Returns:
            Dictionary with element priorities (higher = more important)
        """
        layout_category = layout.get('layout_category', 'medium')
        
        if layout_category == 'small':
            # On small screens, prioritize essential elements
            return {
                'game_boards': 10,
                'current_scores': 8,
                'progress_bars': 6,
                'captured_pieces': 4,
                'detailed_stats': 2,
                'decorative_elements': 1
            }
        elif layout_category == 'medium':
            # Standard priorities
            return {
                'game_boards': 10,
                'captured_pieces': 8,
                'current_scores': 7,
                'progress_bars': 6,
                'detailed_stats': 4,
                'decorative_elements': 3
            }
        else:  # large or xlarge
            # On large screens, show everything
            return {
                'game_boards': 10,
                'captured_pieces': 9,
                'current_scores': 8,
                'progress_bars': 7,
                'detailed_stats': 6,
                'decorative_elements': 5
            }
    
    def should_show_element(self, element_name: str, layout: Dict[str, Any], 
                           min_priority: int = 5) -> bool:
        """
        Determine if an element should be shown based on layout and priority
        
        Args:
            element_name: Name of the element
            layout: Layout configuration
            min_priority: Minimum priority threshold
            
        Returns:
            True if element should be shown
        """
        priorities = self.get_element_priorities(layout)
        element_priority = priorities.get(element_name, 0)
        return element_priority >= min_priority
    
    def clear_cache(self) -> None:
        """Clear the layout cache"""
        self.layout_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            'cache_size': len(self.layout_cache),
            'cached_layouts': list(self.layout_cache.keys())
        }
    
    def validate_layout(self, layout: Dict[str, Any]) -> bool:
        """
        Validate that a layout configuration is valid
        
        Args:
            layout: Layout configuration to validate
            
        Returns:
            True if layout is valid
        """
        try:
            required_keys = [
                'square_size', 'margin', 'board_positions', 
                'captured_pieces_areas', 'score_panel_area'
            ]
            
            # Check required keys
            for key in required_keys:
                if key not in layout:
                    print(f"⚠️ Layout missing required key: {key}")
                    return False
            
            # Validate square size
            if not (self.MIN_SQUARE_SIZE <= layout['square_size'] <= self.MAX_SQUARE_SIZE):
                print(f"⚠️ Invalid square size: {layout['square_size']}")
                return False
            
            # Validate board positions
            board_positions = layout['board_positions']
            if 'chess' not in board_positions or 'checkers' not in board_positions:
                print("⚠️ Missing board positions")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error validating layout: {e}")
            return False