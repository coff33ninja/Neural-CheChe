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

    def __init__(self, window_width=1240, window_height=700, square_size=60):
        self.window_width = window_width
        self.window_height = window_height
        self.square_size = square_size

        # Initialize error handler
        self.error_handler = ErrorHandler()

        try:
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
            self.current_layout = self.layout_manager.calculate_optimal_layout(
                window_width, window_height
            )

            # Apply initial layout
            self._apply_layout(self.current_layout)

            # Layout areas (will be updated by responsive layout)
            self.captured_pieces_area = self.current_layout.get(
                "captured_pieces_areas",
                {
                    "chess": {"x": 500, "y": 70, "width": 220, "height": 400},
                    "checkers": {"x": 1020, "y": 70, "width": 220, "height": 400},
                },
            )

            # Score panel area
            self.score_panel_area = self.current_layout.get(
                "score_panel_area", {"x": 50, "y": 500, "width": 1140, "height": 80}
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
            text_surf = self.large_font.render(message, True, self.RED)
            self.screen.blit(
                text_surf, (offset_x + 50, self.board_offset_y + 4 * self.square_size)
            )
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
        """Display current generation and training information"""
        if not self.gui_initialized or not self.screen:
            return
        try:
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

            # Recalculate layout
            self.current_layout = self.layout_manager.calculate_optimal_layout(
                new_width, new_height
            )
            self._apply_layout(self.current_layout)

            # Update layout areas
            self.captured_pieces_area = self.current_layout.get(
                "captured_pieces_areas",
                {
                    "chess": {"x": 500, "y": 70, "width": 220, "height": 400},
                    "checkers": {"x": 1020, "y": 70, "width": 220, "height": 400},
                },
            )

            self.score_panel_area = self.current_layout.get(
                "score_panel_area", {"x": 50, "y": 500, "width": 1140, "height": 80}
            )

            print(f"🖥️ Window resized to {new_width}x{new_height}")

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
        """Display progress bars and metrics"""
        if not self.gui_initialized or not self.screen:
            return

        try:
            # Display generation progress
            gen_progress = progress_data.get("generation_progress", 0)
            self._draw_progress_bar(
                50, 600, 300, 20, gen_progress, "Generation Progress"
            )

            # Display phase progress
            phase_progress = progress_data.get("phase_progress", 0)
            self._draw_progress_bar(400, 600, 300, 20, phase_progress, "Phase Progress")

            # Display metrics
            metrics = progress_data.get("metrics", {})
            y_offset = 630
            for key, value in metrics.items():
                self.display_info(f"{key}: {value}", 50, y_offset)
                y_offset += 20

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

        # Animated dots
        dots = "." * ((move_count % 3) + 1)
        thinking_text = f"🤖 {player} AI is thinking{dots}"
        self.display_info(thinking_text, offset_x, 450, self.RED)

        # Move progress
        progress_text = f"Move {move_count + 1}"
        self.display_info(progress_text, offset_x, 470, self.BLUE)

    def display_move_statistics(self, game_type, move_count, max_moves):
        """Display move statistics"""
        offset_x = (
            self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        )

        progress_text = f"Progress: {move_count}/{max_moves} moves"
        self.display_info(progress_text, offset_x, 490, self.BLUE)

    def display_policy_info(self, policy, game_type, max_moves=5):
        """Display top moves from policy"""
        if not policy:
            return

        offset_x = (
            self.chess_offset_x if game_type == "chess" else self.checkers_offset_x
        )

        # Sort moves by probability
        top_moves = sorted(policy.items(), key=lambda x: x[1], reverse=True)[:max_moves]

        for i, (move, prob) in enumerate(top_moves):
            text = f"Move: {move}, Prob: {prob:.3f}"
            self.display_info(text, offset_x, 550 + i * 20)

    def update_window_title(self, generation, game_type, phase):
        """Update the pygame window title"""
        title = f"Neural CheChe - Gen {generation} - {phase} - {game_type.title()}"
        pygame.display.set_caption(title)

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
