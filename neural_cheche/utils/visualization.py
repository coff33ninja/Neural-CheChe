"""
Visualization and GUI management
"""

import pygame
import time
from typing import Dict, Any
from .captured_pieces_renderer import CapturedPiecesRenderer
from .responsive_layout import ResponsiveLayoutManager


class VisualizationManager:
    """Manages the pygame visualization system"""
    
    def __init__(self, window_width=1240, window_height=700, square_size=60):
        self.window_width = window_width
        self.window_height = window_height
        self.square_size = square_size
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Neural CheChe: AI vs AI Training")
        
        # Fonts
        self.font = pygame.font.SysFont("arial", 20)
        self.large_font = pygame.font.SysFont("arial", 48, bold=True)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (200, 20, 20)
        self.BLUE = (20, 20, 200)
        self.GREEN = (0, 255, 0)
        
        # Board positions
        self.chess_offset_x = 50
        self.checkers_offset_x = 670
        self.board_offset_y = 70
        
        # Captured pieces renderer
        self.captured_pieces_renderer = CapturedPiecesRenderer()
        
        # Responsive layout manager
        self.layout_manager = ResponsiveLayoutManager()
        self.current_layout = self.layout_manager.calculate_optimal_layout(window_width, window_height)
        
        # Apply initial layout
        self._apply_layout(self.current_layout)
        
        # Layout areas (will be updated by responsive layout)
        self.captured_pieces_area = self.current_layout.get('captured_pieces_areas', {
            'chess': {'x': 500, 'y': 70, 'width': 220, 'height': 400},
            'checkers': {'x': 1020, 'y': 70, 'width': 220, 'height': 400}
        })
        
        # Score panel area
        self.score_panel_area = self.current_layout.get('score_panel_area', 
                                                       {'x': 50, 'y': 500, 'width': 1140, 'height': 80})
    
    def clear_screen(self):
        """Clear the screen with white background"""
        self.screen.fill(self.WHITE)
    
    def display_info(self, text, x, y, color=None):
        """Display text information at specified position"""
        if color is None:
            color = self.BLACK
        text_surf = self.font.render(text, True, color)
        self.screen.blit(text_surf, (x, y))
    
    def display_title(self, text, x, y, color=None):
        """Display large title text"""
        if color is None:
            color = self.BLACK
        text_surf = self.large_font.render(text, True, color)
        self.screen.blit(text_surf, (x, y))
    
    def display_game_over(self, message, game_type):
        """Display game over message"""
        offset_x = self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        text_surf = self.large_font.render(message, True, self.RED)
        self.screen.blit(text_surf, (offset_x + 50, self.board_offset_y + 4 * self.square_size))
    
    def display_generation_info(self, generation, phase, wins_info):
        """Display current generation and training information"""
        info_y = 20
        
        # Generation info
        gen_text = f"Generation: {generation} | Phase: {phase}"
        self.display_info(gen_text, 50, info_y, self.BLUE)
        
        # Win statistics
        if wins_info:
            wins_text = f"Alpha Wins - Chess: {wins_info['alpha']['chess']}, Checkers: {wins_info['alpha']['checkers']}"
            self.display_info(wins_text, 50, info_y + 25)
            
            wins_text2 = f"Beta Wins - Chess: {wins_info['beta']['chess']}, Checkers: {wins_info['beta']['checkers']}"
            self.display_info(wins_text2, 50, info_y + 45)
    
    def display_thinking_indicator(self, game_type, player, move_count):
        """Display thinking indicator for AI"""
        offset_x = self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        
        # Animated dots
        dots = "." * ((move_count % 3) + 1)
        thinking_text = f"🤖 {player} AI is thinking{dots}"
        self.display_info(thinking_text, offset_x, 450, self.RED)
        
        # Move progress
        progress_text = f"Move {move_count + 1}"
        self.display_info(progress_text, offset_x, 470, self.BLUE)
    
    def display_move_statistics(self, game_type, move_count, max_moves):
        """Display move statistics"""
        offset_x = self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        
        progress_text = f"Progress: {move_count}/{max_moves} moves"
        self.display_info(progress_text, offset_x, 490, self.BLUE)
    
    def display_policy_info(self, policy, game_type, max_moves=5):
        """Display top moves from policy"""
        if not policy:
            return
        
        offset_x = self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        
        # Sort moves by probability
        top_moves = sorted(policy.items(), key=lambda x: x[1], reverse=True)[:max_moves]
        
        for i, (move, prob) in enumerate(top_moves):
            text = f"Move: {move}, Prob: {prob:.3f}"
            self.display_info(text, offset_x, 550 + i * 20)
    
    def update_window_title(self, generation, game_type, phase):
        """Update the pygame window title"""
        title = f"Neural CheChe - Gen {generation} - {phase} - {game_type.title()}"
        pygame.display.set_caption(title)
    
    def process_events(self):
        """Process pygame events and return True if should continue"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def refresh_display(self):
        """Refresh the display"""
        pygame.display.flip()
    
    def wait_with_events(self, delay_seconds):
        """Wait for specified time while processing events"""
        start_time = time.time()
        while time.time() - start_time < delay_seconds:
            if not self.process_events():
                return False
            time.sleep(0.01)  # Small sleep to prevent busy waiting
        return True
    
    def display_training_stats(self, stats, x=50, y=600):
        """Display training statistics"""
        if not stats:
            return
        
        stats_lines = [
            f"Buffer Size: {stats.get('buffer_size', 0)}",
            f"Mean Reward: {stats.get('mean_reward', 0):.3f}",
            f"Training Loss: {stats.get('training_loss', 0):.4f}",
            f"GPU Memory: {stats.get('gpu_memory', 'N/A')}"
        ]
        
        for i, line in enumerate(stats_lines):
            self.display_info(line, x, y + i * 20)
    
    def display_network_info(self, net_info, x=400, y=600):
        """Display neural network information"""
        if not net_info:
            return
        
        info_lines = [
            f"Parameters: {net_info.get('total_parameters', 0):,}",
            f"Model Size: {net_info.get('model_size_mb', 0):.1f}MB",
            f"Device: {net_info.get('device', 'Unknown')}",
            f"Learning Rate: {net_info.get('learning_rate', 0):.6f}"
        ]
        
        for i, line in enumerate(info_lines):
            self.display_info(line, x, y + i * 20)
    
    def render_progress_overlay(self, progress_manager):
        """Render progress tracking overlay"""
        if not progress_manager or not progress_manager.gui_progress:
            return
        
        try:
            # Render all progress elements
            progress_manager.gui_progress.render_all_progress(self.screen)
            
        except Exception as e:
            # Fallback display
            error_text = f"Progress display error: {str(e)[:30]}"
            self.display_info(error_text, 50, self.window_height - 30, self.RED)
    
    def handle_window_resize(self, new_width: int, new_height: int) -> None:
        """Handle window resize events with responsive layout"""
        try:
            # Update window dimensions
            self.window_width = new_width
            self.window_height = new_height
            
            # Recreate screen surface
            self.screen = pygame.display.set_mode((new_width, new_height))
            
            # Calculate new responsive layout
            new_layout = self.layout_manager.calculate_optimal_layout(new_width, new_height)
            
            # Apply the new layout
            self._apply_layout(new_layout)
            self.current_layout = new_layout
            
            print(f"📐 Layout adapted to {new_width}x{new_height} ({new_layout.get('layout_category', 'unknown')})")
            
        except Exception as e:
            print(f"⚠️ Error handling window resize: {e}")
            # Fallback to old method
            self._update_layout_for_size(new_width, new_height)
    
    def _update_layout_for_size(self, width: int, height: int) -> None:
        """Update layout elements for new window size"""
        try:
            # Minimum size constraints
            min_width = 800
            min_height = 600
            
            if width < min_width or height < min_height:
                print(f"⚠️ Window too small ({width}x{height}), minimum is {min_width}x{min_height}")
                return
            
            # Calculate new board positions
            board_size = min(width // 3, height // 2, 400)  # Adaptive board size
            
            # Chess board position (left side)
            self.chess_offset_x = 50
            self.checkers_offset_x = width // 2 + 50
            self.board_offset_y = 70
            
            # Update square size
            self.square_size = max(40, min(80, board_size // 8))
            
        except Exception as e:
            print(f"⚠️ Error updating layout: {e}")
            
        # Update captured pieces areas
        self._update_captured_pieces_areas(width, height)
        
        # Update score panel area
        self._update_score_panel_area(width, height)
    
    def display_captured_pieces(self, captured_white: list, captured_black: list, 
                               game_type: str, x: int = None, y: int = None) -> None:
        """
        Display captured pieces for both players
        
        Args:
            captured_white: List of white pieces captured by black
            captured_black: List of black pieces captured by white
            game_type: Type of game ("chess" or "checkers")
            x: Optional X position (uses default layout if None)
            y: Optional Y position (uses default layout if None)
        """
        try:
            # Use default positions if not specified
            if x is None or y is None:
                area = self.captured_pieces_area.get(game_type, self.captured_pieces_area['chess'])
                x = area['x']
                y = area['y']
            
            # Draw the captured pieces panel
            self.captured_pieces_renderer.draw_captured_pieces_panel(
                self.screen, captured_white, captured_black, x, y, game_type
            )
            
        except Exception as e:
            print(f"⚠️ Error displaying captured pieces: {e}")
            # Fallback display
            fallback_text = f"Captured: W:{len(captured_white)} B:{len(captured_black)}"
            self.display_info(fallback_text, x or 50, y or 50, self.BLACK)
    
    def display_progress_bars(self, progress_data: dict) -> None:
        """
        Display progress bars and indicators
        
        Args:
            progress_data: Dictionary containing progress information
        """
        try:
            if not progress_data:
                return
            
            # This integrates with the existing progress system
            # The actual progress rendering is handled by the progress manager
            # This method is here for compatibility and future enhancements
            
            # Display basic progress info if progress manager is not available
            if 'current_generation' in progress_data and 'total_generations' in progress_data:
                progress_text = f"Generation: {progress_data['current_generation']}/{progress_data['total_generations']}"
                self.display_info(progress_text, 50, self.window_height - 100, self.BLUE)
            
            if 'current_phase' in progress_data:
                phase_text = f"Phase: {progress_data['current_phase']}"
                self.display_info(phase_text, 50, self.window_height - 80, self.BLUE)
            
        except Exception as e:
            print(f"⚠️ Error displaying progress bars: {e}")
    
    def display_score_panel(self, current_scores: dict, historical: list = None) -> None:
        """
        Display real-time scoring panel
        
        Args:
            current_scores: Dictionary of current scores
            historical: Optional list of historical score data
        """
        try:
            area = self.score_panel_area
            
            # Draw background
            pygame.draw.rect(self.screen, (240, 240, 240), 
                           (area['x'], area['y'], area['width'], area['height']))
            pygame.draw.rect(self.screen, self.BLACK, 
                           (area['x'], area['y'], area['width'], area['height']), 2)
            
            # Title
            title_text = "Live Scores"
            title_surface = self.font.render(title_text, True, self.BLACK)
            self.screen.blit(title_surface, (area['x'] + 10, area['y'] + 5))
            
            # Display current scores
            if current_scores:
                score_y = area['y'] + 30
                for i, (player, score) in enumerate(current_scores.items()):
                    score_text = f"{player}: {score:.3f}"
                    score_color = self.BLUE if i % 2 == 0 else self.RED
                    score_surface = self.font.render(score_text, True, score_color)
                    self.screen.blit(score_surface, (area['x'] + 10 + i * 200, score_y))
            
            # Display historical trend (simplified)
            if historical and len(historical) > 1:
                trend_text = "Trend: "
                if historical[-1] > historical[0]:
                    trend_text += "↗ Improving"
                    trend_color = self.GREEN
                elif historical[-1] < historical[0]:
                    trend_text += "↘ Declining"
                    trend_color = self.RED
                else:
                    trend_text += "→ Stable"
                    trend_color = self.BLACK
                
                trend_surface = self.font.render(trend_text, True, trend_color)
                self.screen.blit(trend_surface, (area['x'] + 400, area['y'] + 30))
            
        except Exception as e:
            print(f"⚠️ Error displaying score panel: {e}")
    
    def adapt_layout_to_size(self, width: int, height: int) -> dict:
        """
        Adapt layout to window size and return layout information
        
        Args:
            width: Window width
            height: Window height
            
        Returns:
            Dictionary with layout information
        """
        try:
            # Update internal layout
            self._update_layout_for_size(width, height)
            
            # Return layout information
            layout_info = {
                'window_size': (width, height),
                'board_positions': {
                    'chess': (self.chess_offset_x, self.board_offset_y),
                    'checkers': (self.checkers_offset_x, self.board_offset_y)
                },
                'square_size': self.square_size,
                'captured_pieces_areas': self.captured_pieces_area.copy(),
                'score_panel_area': self.score_panel_area.copy()
            }
            
            return layout_info
            
        except Exception as e:
            print(f"⚠️ Error adapting layout: {e}")
            return {}
    
    def _update_captured_pieces_areas(self, width: int, height: int) -> None:
        """Update captured pieces display areas based on window size"""
        try:
            # Chess captured pieces area (right of chess board)
            chess_board_right = self.chess_offset_x + (self.square_size * 8) + 20
            self.captured_pieces_area['chess'] = {
                'x': chess_board_right,
                'y': self.board_offset_y,
                'width': 220,
                'height': min(400, height - self.board_offset_y - 100)
            }
            
            # Checkers captured pieces area (right of checkers board)
            checkers_board_right = self.checkers_offset_x + (self.square_size * 8) + 20
            if checkers_board_right + 220 <= width:
                self.captured_pieces_area['checkers'] = {
                    'x': checkers_board_right,
                    'y': self.board_offset_y,
                    'width': 220,
                    'height': min(400, height - self.board_offset_y - 100)
                }
            else:
                # If not enough space, place below chess captured pieces
                self.captured_pieces_area['checkers'] = {
                    'x': self.captured_pieces_area['chess']['x'],
                    'y': self.captured_pieces_area['chess']['y'] + self.captured_pieces_area['chess']['height'] + 10,
                    'width': 220,
                    'height': 200
                }
            
            # Update captured pieces renderer for new window size
            self.captured_pieces_renderer.adapt_to_window_size(width, height)
            
        except Exception as e:
            print(f"⚠️ Error updating captured pieces areas: {e}")
    
    def _update_score_panel_area(self, width: int, height: int) -> None:
        """Update score panel area based on window size"""
        try:
            # Score panel at the bottom
            panel_height = 80
            margin = 50
            
            self.score_panel_area = {
                'x': margin,
                'y': height - panel_height - margin,
                'width': width - 2 * margin,
                'height': panel_height
            }
            
        except Exception as e:
            print(f"⚠️ Error updating score panel area: {e}")
    
    def get_layout_info(self) -> dict:
        """Get current layout information"""
        return {
            'window_size': (self.window_width, self.window_height),
            'board_positions': {
                'chess': (self.chess_offset_x, self.board_offset_y),
                'checkers': (self.checkers_offset_x, self.board_offset_y)
            },
            'square_size': self.square_size,
            'captured_pieces_areas': self.captured_pieces_area.copy(),
            'score_panel_area': self.score_panel_area.copy()
        }
    
    def render_complete_game_view(self, game_data: dict) -> None:
        """
        Render a complete game view with all elements
        
        Args:
            game_data: Dictionary containing all game display data
        """
        try:
            # Clear screen
            self.clear_screen()
            
            # Render captured pieces if available
            if 'captured_pieces' in game_data:
                captured = game_data['captured_pieces']
                game_type = game_data.get('game_type', 'chess')
                
                self.display_captured_pieces(
                    captured.get('white', []),
                    captured.get('black', []),
                    game_type
                )
            
            # Render score panel if available
            if 'current_scores' in game_data:
                self.display_score_panel(
                    game_data['current_scores'],
                    game_data.get('historical_scores', [])
                )
            
            # Render progress if available
            if 'progress_data' in game_data:
                self.display_progress_bars(game_data['progress_data'])
            
            # Render progress overlay if progress manager is available
            if 'progress_manager' in game_data:
                self.render_progress_overlay(game_data['progress_manager'])
            
        except Exception as e:
            print(f"⚠️ Error rendering complete game view: {e}")
    
    def _apply_layout(self, layout: Dict[str, Any]) -> None:
        """
        Apply a responsive layout configuration
        
        Args:
            layout: Layout configuration from ResponsiveLayoutManager
        """
        try:
            if not self.layout_manager.validate_layout(layout):
                print("⚠️ Invalid layout configuration, using fallback")
                layout = self.layout_manager._get_fallback_layout(self.window_width, self.window_height)
            
            # Update square size
            self.square_size = layout['square_size']
            
            # Update board positions
            board_positions = layout['board_positions']
            self.chess_offset_x = board_positions['chess'][0]
            self.board_offset_y = board_positions['chess'][1]
            self.checkers_offset_x = board_positions['checkers'][0]
            
            # Update layout areas
            self.captured_pieces_area = layout['captured_pieces_areas']
            self.score_panel_area = layout['score_panel_area']
            
            # Update captured pieces renderer for new layout
            if hasattr(self, 'captured_pieces_renderer'):
                self.captured_pieces_renderer.adapt_to_window_size(
                    self.window_width, self.window_height
                )
            
            # Update fonts based on layout
            font_sizes = self.layout_manager.adapt_fonts_to_layout(layout)
            self._update_fonts(font_sizes)
            
        except Exception as e:
            print(f"⚠️ Error applying layout: {e}")
    
    def _update_fonts(self, font_sizes: Dict[str, int]) -> None:
        """
        Update fonts based on responsive layout
        
        Args:
            font_sizes: Dictionary with font size recommendations
        """
        try:
            # Update existing fonts
            self.font = pygame.font.SysFont("arial", font_sizes.get('info_font', 20))
            self.large_font = pygame.font.SysFont("arial", font_sizes.get('title_font', 48), bold=True)
            
            # Update captured pieces renderer fonts if needed
            if hasattr(self, 'captured_pieces_renderer'):
                # The captured pieces renderer will adapt its own fonts
                pass
            
        except Exception as e:
            print(f"⚠️ Error updating fonts: {e}")
    
    def get_responsive_layout_info(self) -> Dict[str, Any]:
        """Get current responsive layout information"""
        try:
            layout_info = self.current_layout.copy()
            layout_info.update({
                'element_priorities': self.layout_manager.get_element_priorities(self.current_layout),
                'cache_info': self.layout_manager.get_cache_info()
            })
            return layout_info
        except Exception as e:
            print(f"⚠️ Error getting layout info: {e}")
            return {}
    
    def should_show_element(self, element_name: str, min_priority: int = 5) -> bool:
        """
        Check if an element should be shown based on current layout
        
        Args:
            element_name: Name of the element to check
            min_priority: Minimum priority threshold
            
        Returns:
            True if element should be shown
        """
        try:
            return self.layout_manager.should_show_element(element_name, self.current_layout, min_priority)
        except Exception as e:
            print(f"⚠️ Error checking element visibility: {e}")
            return True  # Default to showing element
    
    def force_layout_recalculation(self) -> None:
        """Force recalculation of the current layout"""
        try:
            # Clear cache and recalculate
            self.layout_manager.clear_cache()
            new_layout = self.layout_manager.calculate_optimal_layout(self.window_width, self.window_height)
            self._apply_layout(new_layout)
            self.current_layout = new_layout
            print("🔄 Layout recalculated")
        except Exception as e:
            print(f"⚠️ Error forcing layout recalculation: {e}")
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
