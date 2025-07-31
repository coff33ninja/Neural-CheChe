"""
Visualization and GUI management
"""

import pygame
from typing import Dict, Any
from .captured_pieces_renderer import CapturedPiecesRenderer
from .responsive_layout import ResponsiveLayoutManager
from ..error_handling import ErrorHandler, ErrorCategory, ErrorSeverity
from ..error_handling.decorators import handle_errors, graceful_degradation


class VisualizationManager:
    """Manages the pygame visualization system"""

    def __init__(self, window_width=1400, window_height=800, square_size=60):
        self.window_width = window_width
        self.window_height = window_height
        self.square_size = square_size

        # Initialize error handler
        self.error_handler = ErrorHandler()

        try:
            # Initialize pygame
            pygame.init()
            self.screen = pygame.display.set_mode(
                (window_width, window_height), pygame.RESIZABLE
            )
            pygame.display.set_caption("Neural CheChe: AI vs AI Training")

            # Fonts
            self.font = pygame.font.SysFont("arial", 16)
            self.large_font = pygame.font.SysFont("arial", 24, bold=True)
            self.small_font = pygame.font.SysFont("arial", 14)
            self.title_font = pygame.font.SysFont("arial", 20, bold=True)

            # Colors
            self.WHITE = (255, 255, 255)
            self.BLACK = (0, 0, 0)
            self.RED = (200, 20, 20)
            self.BLUE = (20, 20, 200)
            self.GREEN = (0, 255, 0)
            self.LIGHT_GRAY = (240, 240, 240)
            self.DARK_GRAY = (100, 100, 100)
            self.GOLD = (255, 215, 0)

            # Game state tracking
            self.current_game_number = 0
            self.current_generation = 0
            self.current_phase = "Training"

            # Move information tracking
            self.last_moves = {
                "chess": {"alpha": None, "beta": None},
                "checkers": {"alpha": None, "beta": None},
            }

            # Progress tracking
            self.generation_progress = 0.0
            self.phase_progress = 0.0
            self.progress_metrics = {}

            # Board positions - side by side layout
            self.chess_offset_x = 50
            self.checkers_offset_x = (
                50 + (8 * square_size) + 300
            )  # Chess board + captured pieces + spacing
            self.board_offset_y = 120  # More space at top for game info

            # Ensure both boards are properly positioned
            self.ensure_both_boards_visible()

            # Captured pieces renderer
            self.captured_pieces_renderer = CapturedPiecesRenderer()

            # Responsive layout manager
            self.layout_manager = ResponsiveLayoutManager()
            self.current_layout = self.layout_manager.calculate_optimal_layout(
                window_width, window_height
            )

            # Apply initial layout
            self._apply_layout(self.current_layout)

            # Layout areas (will be updated by responsive layout)
            self.captured_pieces_area = self.current_layout.get(
                "captured_pieces_areas",
                {
                    "chess": {
                        "x": self.chess_offset_x + 8 * square_size + 20,
                        "y": self.board_offset_y,
                        "width": 220,
                        "height": 400,
                    },
                    "checkers": {
                        "x": self.checkers_offset_x + 8 * square_size + 20,
                        "y": self.board_offset_y,
                        "width": 220,
                        "height": 400,
                    },
                },
            )

            # Score panel area
            self.score_panel_area = self.current_layout.get(
                "score_panel_area",
                {
                    "x": 50,
                    "y": window_height - 150,
                    "width": window_width - 100,
                    "height": 80,
                },
            )

            self.gui_initialized = True

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.HIGH,
                component="VisualizationManager",
                context={
                    "operation": "initialization",
                    "window_size": f"{window_width}x{window_height}",
                },
            )
            self.gui_initialized = False
            self.screen = None

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="clear_screen"
    )
    def clear_screen(self):
        """Clear the screen with white background"""
        if not self.gui_initialized or not self.screen:
            return
        try:
            self.screen.fill(self.WHITE)
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "clear_screen"},
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_info"
    )
    def display_info(self, text, x, y, color=None):
        """Display text information at specified position"""
        if not self.gui_initialized or not self.screen:
            return
        try:
            if color is None:
                color = self.BLACK
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (x, y))
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_info", "text": str(text)[:50]},
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_title"
    )
    def display_title(self, text, x, y, color=None):
        """Display large title text"""
        if not self.gui_initialized or not self.screen:
            return
        try:
            if color is None:
                color = self.BLACK
            text_surf = self.large_font.render(text, True, color)
            self.screen.blit(text_surf, (x, y))
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_title", "text": str(text)[:50]},
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_game_over"
    )
    def display_game_over(self, message, game_type):
        """Display game over message"""
        if not self.gui_initialized or not self.screen:
            return
        try:
            offset_x = (
                self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
            )
            # Display game over message below the board, not overlapping
            text_surf = self.large_font.render(message, True, self.RED)
            message_y = self.board_offset_y + 8 * self.square_size + 20  # Below board
            self.screen.blit(text_surf, (offset_x + 50, message_y))
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_game_over",
                    "game_type": game_type,
                    "message": str(message)[:50],
                },
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_generation_info"
    )
    def display_generation_info(self, generation, phase, wins_info):
        """Display current generation and training information - enhanced version"""
        if not self.gui_initialized or not self.screen:
            return
        try:
            # Update internal state
            self.current_generation = generation
            self.current_phase = phase

            # Display the header
            self.display_game_header()

            # Display win statistics in the global state area
            if wins_info:
                global_state = {
                    "match_stats": {
                        "total": wins_info.get("alpha", {}).get("chess", 0)
                        + wins_info.get("alpha", {}).get("checkers", 0)
                        + wins_info.get("beta", {}).get("chess", 0)
                        + wins_info.get("beta", {}).get("checkers", 0),
                        "alpha_wins": wins_info.get("alpha", {}).get("chess", 0)
                        + wins_info.get("alpha", {}).get("checkers", 0),
                        "beta_wins": wins_info.get("beta", {}).get("chess", 0)
                        + wins_info.get("beta", {}).get("checkers", 0),
                    }
                }
                self._display_global_state_info(global_state)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_generation_info",
                    "generation": generation,
                    "phase": str(phase),
                },
            )

    @handle_errors(
        category=ErrorCategory.GUI,
        severity=ErrorSeverity.MEDIUM,
        component="window_resize",
        recovery_scenario="gui_initialization_failed",
        max_retries=1,
        suppress_errors=True,
    )
    def handle_window_resize(self, new_width: int, new_height: int) -> None:
        """Handle window resize events with error recovery"""
        try:
            if not self.gui_initialized:
                return

            # Update window dimensions
            self.window_width = new_width
            self.window_height = new_height

            # Recreate the screen with new dimensions
            self.screen = pygame.display.set_mode(
                (new_width, new_height), pygame.RESIZABLE
            )

            # Recalculate layout
            self.current_layout = self.layout_manager.calculate_optimal_layout(
                new_width, new_height
            )
            self._apply_layout(self.current_layout)

            # Ensure both boards remain visible and properly spaced
            self.ensure_both_boards_visible()

            # Update captured pieces renderer for new window size
            self.captured_pieces_renderer.adapt_to_window_size(new_width, new_height)

            # Update layout areas based on new board positions
            board_width = 8 * self.square_size
            self.captured_pieces_area = self.current_layout.get(
                "captured_pieces_areas",
                {
                    "chess": {
                        "x": self.chess_offset_x + board_width + 20,
                        "y": self.board_offset_y,
                        "width": 220,
                        "height": 400,
                    },
                    "checkers": {
                        "x": self.checkers_offset_x + board_width + 20,
                        "y": self.board_offset_y,
                        "width": 220,
                        "height": 400,
                    },
                },
            )

            self.score_panel_area = self.current_layout.get(
                "score_panel_area",
                {
                    "x": 50,
                    "y": new_height - 150,
                    "width": new_width - 100,
                    "height": 80,
                },
            )

            print(f"🖥️ Window resized to {new_width}x{new_height} - Layout adapted")

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.MEDIUM,
                component="VisualizationManager",
                context={
                    "operation": "handle_window_resize",
                    "new_size": f"{new_width}x{new_height}",
                },
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_captured_pieces"
    )
    def display_captured_pieces(
        self, captured_white: list, captured_black: list, game_type: str
    ) -> None:
        """Display captured pieces for both players"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            area = self.captured_pieces_area.get(game_type, {})
            if not area:
                return

            # Display captured pieces using the renderer
            self.captured_pieces_renderer.draw_captured_area(
                self.screen, captured_white, area["x"], area["y"], "white"
            )
            self.captured_pieces_renderer.draw_captured_area(
                self.screen,
                captured_black,
                area["x"],
                area["y"] + area["height"] // 2,
                "black",
            )

            # Display material advantage
            advantage = self.captured_pieces_renderer.calculate_material_advantage(
                captured_white, captured_black
            )
            self.captured_pieces_renderer.draw_advantage_indicator(
                self.screen,
                advantage,
                area["x"] + area["width"] - 50,
                area["y"] + area["height"] // 2,
            )

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_captured_pieces",
                    "game_type": game_type,
                },
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_progress_bars"
    )
    def display_progress_bars(self, progress_data: Dict[str, Any]) -> None:
        """Display progress bars and metrics - enhanced version"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Update internal progress state
            self.generation_progress = progress_data.get("generation_progress", 0)
            self.phase_progress = progress_data.get("phase_progress", 0)
            self.progress_metrics = progress_data.get("metrics", {})

            # Use the enhanced progress bar display
            self.display_enhanced_progress_bars()

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_progress_bars"},
            )

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="display_score_panel"
    )
    def display_score_panel(
        self, current_scores: Dict[str, Any], historical: list
    ) -> None:
        """Display current scores and historical trends"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            area = self.score_panel_area

            # Draw score panel background
            pygame.draw.rect(
                self.screen,
                (240, 240, 240),
                (area["x"], area["y"], area["width"], area["height"]),
            )

            # Display current scores
            score_text = "Current Scores - "
            for player, score in current_scores.items():
                score_text += f"{player}: {score:.3f} | "

            self.display_info(score_text, area["x"] + 10, area["y"] + 10)

            # Display trend information
            if historical:
                trend_text = f"Games Played: {len(historical)} | "
                if len(historical) > 1:
                    recent_avg = sum(h.get("score", 0) for h in historical[-5:]) / min(
                        5, len(historical)
                    )
                    trend_text += f"Recent Avg: {recent_avg:.3f}"

                self.display_info(trend_text, area["x"] + 10, area["y"] + 35)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_score_panel"},
            )

    def _draw_progress_bar(
        self, x: int, y: int, width: int, height: int, progress: float, label: str
    ):
        """Draw a progress bar with label"""
        try:
            # Background
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height))

            # Progress fill
            fill_width = int(width * max(0, min(1, progress)))
            if fill_width > 0:
                pygame.draw.rect(self.screen, (0, 200, 0), (x, y, fill_width, height))

            # Border
            pygame.draw.rect(self.screen, self.BLACK, (x, y, width, height), 2)

            # Label
            self.display_info(f"{label}: {progress:.1%}", x, y - 20)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_draw_progress_bar", "label": label},
            )

    def _apply_layout(self, layout: Dict[str, Any]):
        """Apply responsive layout configuration"""
        try:
            # Update board positions based on layout
            if "board_positions" in layout:
                positions = layout["board_positions"]
                self.chess_offset_x = positions.get("chess_x", self.chess_offset_x)
                self.checkers_offset_x = positions.get(
                    "checkers_x", self.checkers_offset_x
                )
                self.board_offset_y = positions.get("board_y", self.board_offset_y)

            # Update square size if needed
            if "square_size" in layout:
                self.square_size = layout["square_size"]

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_apply_layout"},
            )

    @graceful_degradation(
        fallback_value=True, log_errors=True, component="process_events"
    )
    def process_events(self) -> bool:
        """Process pygame events and return False if quit requested"""
        if not self.gui_initialized:
            return True

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_window_resize(event.w, event.h)
            return True

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.MEDIUM,
                component="VisualizationManager",
                context={"operation": "process_events"},
            )
            return True

    @graceful_degradation(
        fallback_value=None, log_errors=True, component="refresh_display"
    )
    def refresh_display(self):
        """Refresh the display"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            pygame.display.flip()
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "refresh_display"},
            )

    @handle_errors(
        category=ErrorCategory.GUI,
        severity=ErrorSeverity.LOW,
        component="cleanup",
        max_retries=1,
        suppress_errors=True,
    )
    def cleanup(self):
        """Clean up pygame resources"""
        try:
            if self.gui_initialized:
                pygame.quit()
                self.gui_initialized = False
                print("🧹 GUI cleanup completed")
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "cleanup"},
            )

    def display_thinking_indicator(self, game_type, player, move_count):
        """Display thinking indicator for AI"""
        offset_x = (
            self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        )

        # Animated dots - positioned below the board
        dots = "." * ((move_count % 3) + 1)
        thinking_text = f"🤖 {player} AI is thinking{dots}"
        thinking_y = self.board_offset_y + 8 * self.square_size + 40  # Below board
        self.display_info(thinking_text, offset_x, thinking_y, self.RED)

        # Move progress
        progress_text = f"Move {move_count + 1}"
        self.display_info(progress_text, offset_x, thinking_y + 20, self.BLUE)

    def display_move_statistics(self, game_type, move_count, max_moves):
        """Display move statistics"""
        offset_x = (
            self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        )

        # Position below the board, after other move info
        stats_y = self.board_offset_y + 8 * self.square_size + 80
        progress_text = f"Progress: {move_count}/{max_moves} moves"
        self.display_info(progress_text, offset_x, stats_y, self.BLUE)

    def display_policy_info(self, policy, game_type, max_moves=3):
        """Display top moves from policy"""
        if not policy:
            return

        offset_x = (
            self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        )

        # Position to the right of the board if space allows
        policy_x = offset_x + 8 * self.square_size + 20
        policy_y = self.board_offset_y + 100

        # If not enough space to the right, position below
        if policy_x + 200 > self.window_width:
            policy_x = offset_x
            policy_y = self.board_offset_y + 8 * self.square_size + 100

        # Sort moves by probability
        top_moves = sorted(policy.items(), key=lambda x: x[1], reverse=True)[:max_moves]

        self.display_info("Top Moves:", policy_x, policy_y, self.BLACK)
        for i, (move, prob) in enumerate(top_moves):
            text = f"{move}: {prob:.3f}"
            self.display_info(text, policy_x, policy_y + 20 + i * 18, self.BLACK)

    def update_window_title(self, generation, game_type, phase):
        """Update the pygame window title"""
        title = f"Neural CheChe - Gen {generation} - {phase} - Game #{self.current_game_number}"
        pygame.display.set_caption(title)

    def set_game_number(self, game_number):
        """Set the current game number"""
        self.current_game_number = game_number

    def wait_with_events(self, delay_seconds):
        """Wait for specified time while processing events"""
        if not self.gui_initialized:
            return True

        import time

        start_time = time.time()
        while time.time() - start_time < delay_seconds:
            if not self.process_events():
                return False
            time.sleep(0.01)  # Small sleep to prevent busy waiting
        return True

    def display_training_stats(self, stats, x=50, y=600):
        """Display training statistics"""
        if not self.gui_initialized or not self.screen or not stats:
            return

        stats_lines = [
            f"Buffer Size: {stats.get('buffer_size', 0)}",
            f"Mean Reward: {stats.get('mean_reward', 0):.3f}",
            f"Training Loss: {stats.get('training_loss', 0):.4f}",
            f"GPU Memory: {stats.get('gpu_memory', 'N/A')}",
        ]

        for i, line in enumerate(stats_lines):
            self.display_info(line, x, y + i * 20)

    def display_network_info(self, net_info, x=400, y=600):
        """Display neural network information"""
        if not self.gui_initialized or not self.screen or not net_info:
            return

        info_lines = [
            f"Parameters: {net_info.get('total_parameters', 0):,}",
            f"Model Size: {net_info.get('model_size_mb', 0):.1f}MB",
            f"Device: {net_info.get('device', 'Unknown')}",
            f"Learning Rate: {net_info.get('learning_rate', 0):.6f}",
        ]

        for i, line in enumerate(info_lines):
            self.display_info(line, x, y + i * 20)

    def __enter__(self):
        """Context manager entry"""
        return self

    def display_move_info_top(
        self, game_type, player_name, move_from, move_to, player_type="Alpha"
    ):
        """Display move information above the board - enhanced version"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            self.display_move_with_player_info(
                game_type, player_name, move_from, move_to, player_type, "top"
            )

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_move_info_top",
                    "game_type": game_type,
                    "player_name": player_name,
                },
            )

    def display_move_info_bottom(
        self, game_type, player_name, move_from, move_to, player_type="Beta"
    ):
        """Display move information below the board - enhanced version"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            self.display_move_with_player_info(
                game_type, player_name, move_from, move_to, player_type, "bottom"
            )

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_move_info_bottom",
                    "game_type": game_type,
                    "player_name": player_name,
                },
            )

    def display_game_result_with_moves(self, game_type, winner_info, last_moves):
        """Display game result with information about who won and their last moves - enhanced version"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Use the enhanced game result display
            self.display_game_result_enhanced(game_type, winner_info, last_moves)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_game_result_with_moves",
                    "game_type": game_type,
                },
            )

    def clear_move_info_areas(self, game_type):
        """Clear the move information areas around a specific board"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            offset_x = (
                self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
            )
            board_width = 8 * self.square_size

            # Clear area above board
            top_rect = pygame.Rect(offset_x, self.board_offset_y - 80, board_width, 80)
            pygame.draw.rect(self.screen, self.WHITE, top_rect)

            # Clear area below board
            bottom_rect = pygame.Rect(
                offset_x, self.board_offset_y + 8 * self.square_size, board_width, 100
            )
            pygame.draw.rect(self.screen, self.WHITE, bottom_rect)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "clear_move_info_areas", "game_type": game_type},
            )
            pygame.draw.rect(self.screen, self.WHITE, bottom_rect)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "clear_move_info_areas",
                    "game_type": game_type,
                },
            )

    def display_complete_game_state(
        self,
        chess_state=None,
        checkers_state=None,
        current_player_info=None,
        game_status=None,
    ):
        """Display complete game state with proper layout management"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Clear the screen
            self.clear_screen()

            # Ensure proper board positioning
            self.ensure_both_boards_visible()

            # Display chess game if provided
            if chess_state:
                self._display_single_game_state("chess", chess_state)

            # Display checkers game if provided
            if checkers_state:
                self._display_single_game_state("checkers", checkers_state)

            # Display current player information
            if current_player_info:
                self._display_current_player_info(current_player_info)

            # Display overall game status
            if game_status:
                self._display_game_status(game_status)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_complete_game_state"},
            )

    def _display_single_game_state(self, game_type, game_state):
        """Display state for a single game (chess or checkers)"""
        try:
            board = game_state.get("board")
            last_move = game_state.get("last_move")
            move_info = game_state.get("move_info")
            game_over = game_state.get("game_over", False)
            winner_info = game_state.get("winner_info")

            # Get the appropriate renderer
            if game_type == "chess":
                from ..games.chess.chess_renderer import ChessRenderer

                renderer = ChessRenderer(self.square_size)
                offset_x = self.chess_offset_x
            else:
                from ..games.checkers.checkers_renderer import CheckersRenderer

                renderer = CheckersRenderer(self.square_size)
                offset_x = self.checkers_offset_x

            # Draw the board
            if board:
                renderer.draw_board(
                    self.screen,
                    board,
                    offset_x,
                    self.board_offset_y,
                    title=game_type.title(),
                    last_move=last_move,
                )

            # Display move information
            if move_info:
                if move_info.get("top_player"):
                    top_info = move_info["top_player"]
                    self.display_move_info_top(
                        game_type,
                        top_info.get("name", "Player"),
                        top_info.get("move_from", "?"),
                        top_info.get("move_to", "?"),
                        top_info.get("type", "Alpha"),
                    )

                if move_info.get("bottom_player"):
                    bottom_info = move_info["bottom_player"]
                    self.display_move_info_bottom(
                        game_type,
                        bottom_info.get("name", "Player"),
                        bottom_info.get("move_from", "?"),
                        bottom_info.get("move_to", "?"),
                        bottom_info.get("type", "Beta"),
                    )

            # Display game over information
            if game_over and winner_info:
                last_moves = game_state.get("last_moves", {})
                self.display_game_result_with_moves(game_type, winner_info, last_moves)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "_display_single_game_state",
                    "game_type": game_type,
                },
            )

    def _display_current_player_info(self, player_info):
        """Display information about the current player"""
        try:
            info_y = 20
            player_text = f"Current Turn: {player_info.get('name', 'Unknown')} ({player_info.get('type', 'Player')})"
            self.display_info(player_text, 50, info_y, self.BLUE)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_display_current_player_info"},
            )

    def _display_game_status(self, status):
        """Display overall game status"""
        try:
            status_y = self.window_height - 180

            # Display generation and phase info
            if "generation" in status:
                gen_text = f"Generation: {status['generation']}"
                if "phase" in status:
                    gen_text += f" | Phase: {status['phase']}"
                self.display_info(gen_text, 50, status_y, self.BLACK)

            # Display match statistics
            if "match_stats" in status:
                stats = status["match_stats"]
                stats_text = f"Matches: {stats.get('total', 0)} | "
                stats_text += f"Chess: {stats.get('chess_wins', 0)} | "
                stats_text += f"Checkers: {stats.get('checkers_wins', 0)}"
                self.display_info(stats_text, 50, status_y + 20, self.BLACK)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_display_game_status"},
            )

    def ensure_both_boards_visible(self):
        """Ensure both chess and checkers boards are visible and properly spaced"""
        try:
            board_width = 8 * self.square_size
            captured_width = 220
            spacing = 50

            # Calculate total width needed
            total_width_needed = 2 * board_width + 2 * captured_width + 3 * spacing

            # Adjust positions if window is too narrow
            if total_width_needed > self.window_width:
                # Reduce spacing and captured area width
                spacing = 20
                captured_width = 180
                total_width_needed = 2 * board_width + 2 * captured_width + 3 * spacing

                if total_width_needed > self.window_width:
                    # Stack boards vertically if still too narrow
                    self.chess_offset_x = 50
                    self.checkers_offset_x = 50
                    self.board_offset_y = 120
                    # Second board below first
                    self.checkers_offset_y = self.board_offset_y + board_width + 100
                else:
                    # Side by side with reduced spacing
                    self.chess_offset_x = spacing
                    self.checkers_offset_x = (
                        spacing + board_width + captured_width + spacing
                    )
            else:
                # Standard side by side layout
                self.chess_offset_x = spacing
                self.checkers_offset_x = (
                    spacing + board_width + captured_width + spacing
                )

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "ensure_both_boards_visible"},
            )

    def display_game_header(self):
        """Display game number and generation info at the top center"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Calculate center position between the two boards
            center_x = (
                self.chess_offset_x + self.checkers_offset_x + 8 * self.square_size
            ) // 2
            header_y = 20

            # Game number
            game_text = f"Game #{self.current_game_number}"
            game_surface = self.title_font.render(game_text, True, self.BLACK)
            game_rect = game_surface.get_rect(center=(center_x, header_y))
            self.screen.blit(game_surface, game_rect)

            # Generation and phase info
            gen_text = f"Generation {self.current_generation} - {self.current_phase}"
            gen_surface = self.font.render(gen_text, True, self.BLUE)
            gen_rect = gen_surface.get_rect(center=(center_x, header_y + 30))
            self.screen.blit(gen_surface, gen_rect)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_game_header"},
            )

    def display_enhanced_progress_bars(self):
        """Display enhanced progress bars showing generational growth"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Position progress bars at the bottom
            progress_y = self.window_height - 120
            progress_width = (self.window_width - 150) // 2
            progress_height = 25

            # Generation progress bar
            gen_x = 50
            self._draw_enhanced_progress_bar(
                gen_x,
                progress_y,
                progress_width,
                progress_height,
                self.generation_progress,
                "Generation Progress",
                self.GREEN,
            )

            # Phase progress bar
            phase_x = gen_x + progress_width + 50
            self._draw_enhanced_progress_bar(
                phase_x,
                progress_y,
                progress_width,
                progress_height,
                self.phase_progress,
                "Phase Progress",
                self.BLUE,
            )

            # Display metrics below progress bars
            metrics_y = progress_y + 35
            if self.progress_metrics:
                metrics_text = " | ".join(
                    [f"{k}: {v}" for k, v in list(self.progress_metrics.items())[:4]]
                )
                metrics_surface = self.small_font.render(metrics_text, True, self.BLACK)
                self.screen.blit(metrics_surface, (50, metrics_y))

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_enhanced_progress_bars"},
            )

    def _draw_enhanced_progress_bar(self, x, y, width, height, progress, label, color):
        """Draw an enhanced progress bar with gradient and label"""
        try:
            # Background
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, (x, y, width, height))

            # Progress fill with gradient effect
            fill_width = int(width * max(0, min(1, progress)))
            if fill_width > 0:
                # Main progress bar
                pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

                # Highlight effect
                highlight_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(
                    self.screen, highlight_color, (x, y, fill_width, height // 3)
                )

            # Border
            pygame.draw.rect(self.screen, self.BLACK, (x, y, width, height), 2)

            # Label and percentage
            label_text = f"{label}: {progress:.1%}"
            label_surface = self.small_font.render(label_text, True, self.BLACK)
            self.screen.blit(label_surface, (x, y - 18))

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_draw_enhanced_progress_bar", "label": label},
            )

    def update_game_state(
        self,
        game_number=None,
        generation=None,
        phase=None,
        generation_progress=None,
        phase_progress=None,
        metrics=None,
    ):
        """Update the current game state information"""
        try:
            if game_number is not None:
                self.current_game_number = game_number
            if generation is not None:
                self.current_generation = generation
            if phase is not None:
                self.current_phase = phase
            if generation_progress is not None:
                self.generation_progress = generation_progress
            if phase_progress is not None:
                self.phase_progress = phase_progress
            if metrics is not None:
                self.progress_metrics = metrics

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "update_game_state"},
            )

    def display_move_with_player_info(
        self,
        game_type,
        player_name,
        move_from,
        move_to,
        player_type="Alpha",
        position="top",
    ):
        """Display move information with clear player identification"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            offset_x = (
                self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
            )

            # Choose position and color based on player type and position
            if position == "top":
                info_y = self.board_offset_y - 50
                color = (
                    self.BLUE if player_type in ["Alpha", "Champion"] else self.GREEN
                )
            else:  # bottom
                info_y = self.board_offset_y + 8 * self.square_size + 20
                color = (
                    self.RED if player_type in ["Beta", "Challenger"] else self.GREEN
                )

            # Clear the area first
            clear_rect = pygame.Rect(offset_x, info_y, 8 * self.square_size, 40)
            pygame.draw.rect(self.screen, self.WHITE, clear_rect)

            # Format move text with player info
            move_text = f"{player_type}/{player_name}: {move_from} → {move_to}"

            # Draw text with background for better visibility
            text_surface = self.font.render(move_text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.x = offset_x + 10
            text_rect.y = info_y + 10

            # Background rectangle
            bg_rect = text_rect.inflate(10, 4)
            pygame.draw.rect(self.screen, self.LIGHT_GRAY, bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 2)

            # Draw text
            self.screen.blit(text_surface, text_rect)

            # Store move info for later reference
            player_key = "alpha" if player_type in ["Alpha", "Champion"] else "beta"
            self.last_moves[game_type][player_key] = {
                "player_name": player_name,
                "player_type": player_type,
                "move_from": move_from,
                "move_to": move_to,
                "position": position,
            }

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_move_with_player_info",
                    "game_type": game_type,
                    "player_name": player_name,
                },
            )

    def display_game_result_enhanced(self, game_type, winner_info, final_moves=None):
        """Display enhanced game result with winner information and final moves"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            offset_x = (
                self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
            )

            # Winner information
            winner_name = winner_info.get("name", "Unknown")
            winner_type = winner_info.get("type", "Player")

            # Position winner announcement in center of board area
            winner_y = self.board_offset_y + 4 * self.square_size - 20

            # Winner text with prominent display
            winner_text = f"🏆 {winner_type}/{winner_name} WINS!"
            winner_surface = self.large_font.render(winner_text, True, self.GOLD)
            winner_rect = winner_surface.get_rect()
            winner_rect.centerx = offset_x + 4 * self.square_size
            winner_rect.y = winner_y

            # Background for winner text
            bg_rect = winner_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, self.BLACK, bg_rect)
            pygame.draw.rect(self.screen, self.GOLD, bg_rect, 3)

            # Draw winner text
            self.screen.blit(winner_surface, winner_rect)

            # Display final moves if available
            if final_moves:
                moves_y = winner_y + 40
                for i, (player, move_info) in enumerate(final_moves.items()):
                    if move_info:
                        move_text = f"{player}: {move_info.get('from', '?')} → {move_info.get('to', '?')}"
                        move_surface = self.small_font.render(
                            move_text, True, self.BLACK
                        )
                        move_rect = move_surface.get_rect()
                        move_rect.centerx = offset_x + 4 * self.square_size
                        move_rect.y = moves_y + i * 20
                        self.screen.blit(move_surface, move_rect)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "display_game_result_enhanced",
                    "game_type": game_type,
                },
            )

    def display_comprehensive_game_state(
        self, chess_state=None, checkers_state=None, global_state=None
    ):
        """Display comprehensive game state for both boards simultaneously"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Clear screen
            self.clear_screen()

            # Display header with game number and generation
            self.display_game_header()

            # Display both game boards with their states
            if chess_state:
                self._display_enhanced_game_state("chess", chess_state)

            if checkers_state:
                self._display_enhanced_game_state("checkers", checkers_state)

            # Display progress bars
            self.display_enhanced_progress_bars()

            # Display global state information
            if global_state:
                self._display_global_state_info(global_state)

            # Refresh display
            self.refresh_display()

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "display_comprehensive_game_state"},
            )

    def _display_enhanced_game_state(self, game_type, game_state):
        """Display enhanced state for a single game"""
        try:
            offset_x = (
                self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
            )

            # Game title
            title_y = self.board_offset_y - 30
            title_text = f"{game_type.title()} Game"
            title_surface = self.title_font.render(title_text, True, self.BLACK)
            title_rect = title_surface.get_rect()
            title_rect.centerx = offset_x + 4 * self.square_size
            title_rect.y = title_y
            self.screen.blit(title_surface, title_rect)

            # Display move information if available
            move_info = game_state.get("move_info", {})
            if move_info:
                # Top player (Alpha/Champion)
                if "top_player" in move_info:
                    top_info = move_info["top_player"]
                    self.display_move_with_player_info(
                        game_type,
                        top_info.get("name", "Player"),
                        top_info.get("move_from", "?"),
                        top_info.get("move_to", "?"),
                        top_info.get("type", "Alpha"),
                        "top",
                    )

                # Bottom player (Beta/Challenger)
                if "bottom_player" in move_info:
                    bottom_info = move_info["bottom_player"]
                    self.display_move_with_player_info(
                        game_type,
                        bottom_info.get("name", "Player"),
                        bottom_info.get("move_from", "?"),
                        bottom_info.get("move_to", "?"),
                        bottom_info.get("type", "Beta"),
                        "bottom",
                    )

            # Display captured pieces if available
            captured_pieces = game_state.get("captured_pieces", {})
            if captured_pieces:
                captured_x = offset_x + 8 * self.square_size + 20
                captured_y = self.board_offset_y

                self.captured_pieces_renderer.draw_captured_pieces_panel(
                    self.screen,
                    captured_pieces.get("white", []),
                    captured_pieces.get("black", []),
                    captured_x,
                    captured_y,
                    game_type,
                )

            # Display game result if game is over
            if game_state.get("game_over", False):
                winner_info = game_state.get("winner_info", {})
                final_moves = game_state.get("final_moves", {})
                self.display_game_result_enhanced(game_type, winner_info, final_moves)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={
                    "operation": "_display_enhanced_game_state",
                    "game_type": game_type,
                },
            )

    def _display_global_state_info(self, global_state):
        """Display global state information"""
        try:
            # Display at bottom left, above progress bars
            info_y = self.window_height - 180
            info_x = 50

            # Current players info
            if "current_players" in global_state:
                players = global_state["current_players"]
                players_text = f"Players: {players.get('alpha', 'Unknown')} vs {players.get('beta', 'Unknown')}"
                players_surface = self.font.render(players_text, True, self.BLACK)
                self.screen.blit(players_surface, (info_x, info_y))

            # Match statistics
            if "match_stats" in global_state:
                stats = global_state["match_stats"]
                stats_text = f"Matches: {stats.get('total', 0)} | Alpha: {stats.get('alpha_wins', 0)} | Beta: {stats.get('beta_wins', 0)}"
                stats_surface = self.small_font.render(stats_text, True, self.DARK_GRAY)
                self.screen.blit(stats_surface, (info_x, info_y + 20))

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="VisualizationManager",
                context={"operation": "_display_global_state_info"},
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
