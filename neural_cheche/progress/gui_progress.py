"""
GUI Progress Tracking with pygame integration
"""

from typing import Dict, List, Any
import pygame
from datetime import datetime

from ..error_handling import ErrorHandler, ErrorCategory, ErrorSeverity
from ..error_handling.decorators import graceful_degradation


class GUIProgress:
    """GUI progress tracking with visual indicators"""

    def __init__(self, visualization_manager):
        self.vis_manager = visualization_manager
        
        # Initialize error handler
        self.error_handler = ErrorHandler()

        # Colors for progress bars and charts
        self.colors = {
            "progress_bg": (50, 50, 50),
            "progress_fill": (0, 150, 255),
            "progress_complete": (0, 200, 100),
            "text": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "chart_line": (255, 100, 100),
            "chart_grid": (100, 100, 100),
            "phase_colors": {
                "Game Generation": (100, 200, 100),
                "AI Training": (200, 100, 100),
                "Challenger System": (100, 100, 200),
                "Wildcard Challenge": (200, 200, 100),
            },
        }

        # Progress state
        self.current_generation = 0
        self.total_generations = 0
        self.current_phase = "Initializing"
        self.phase_progress = 0.0
        self.current_metrics: Dict[str, Any] = {}

        # Historical data for charts
        self.generation_data: List[Dict[str, Any]] = []

        # Layout configuration
        self.progress_area = {"x": 50, "y": 550, "width": 1140, "height": 120}

        # Fonts
        try:
            self.font_large = pygame.font.SysFont("arial", 24, bold=True)
            self.font_medium = pygame.font.SysFont("arial", 18)
            self.font_small = pygame.font.SysFont("arial", 14)
        except Exception as e:
            # Fallback to default font
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="GUIProgress",
                context={"operation": "font_initialization"}
            )
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)

    def update_generation(self, current: int, metrics: Dict[str, Any]) -> None:
        """
        Update generation progress

        Args:
            current: Current generation number
            metrics: Training metrics dictionary
        """
        self.current_generation = current
        self.current_metrics = metrics

        # Store data for growth chart
        data_point = {
            "generation": current,
            "timestamp": datetime.now().isoformat(),
            **metrics,
        }
        self.generation_data.append(data_point)

        # Keep only recent data for performance
        if len(self.generation_data) > 100:
            self.generation_data = self.generation_data[-100:]

    def update_phase(self, phase: str, progress: float) -> None:
        """
        Update phase progress

        Args:
            phase: Phase name
            progress: Progress percentage (0.0 to 1.0)
        """
        self.current_phase = phase
        self.phase_progress = progress

    @graceful_degradation(fallback_value=None, log_errors=True, component="generation_progress_draw")
    def draw_generation_progress(self, screen: pygame.Surface, x: int, y: int) -> None:
        """
        Draw generation progress bar

        Args:
            screen: Pygame surface to draw on
            x: X position
            y: Y position
        """
        try:
            bar_width = 400
            bar_height = 25

            # Background
            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(screen, self.colors["progress_bg"], bg_rect)
            pygame.draw.rect(screen, self.colors["text"], bg_rect, 2)

            # Progress fill
            if self.total_generations > 0:
                progress_ratio = self.current_generation / self.total_generations
                fill_width = int(bar_width * progress_ratio)

                if fill_width > 0:
                    fill_rect = pygame.Rect(x, y, fill_width, bar_height)
                    color = (
                        self.colors["progress_complete"]
                        if progress_ratio >= 1.0
                        else self.colors["progress_fill"]
                    )
                    pygame.draw.rect(screen, color, fill_rect)

            # Progress text
            progress_text = (
                f"Generation {self.current_generation}/{self.total_generations}"
            )
            if self.total_generations > 0:
                percentage = (self.current_generation / self.total_generations) * 100
                progress_text += f" ({percentage:.1f}%)"

            text_surface = self.font_medium.render(
                progress_text, True, self.colors["text"]
            )
            text_rect = text_surface.get_rect(
                center=(x + bar_width // 2, y + bar_height // 2)
            )
            screen.blit(text_surface, text_rect)

        except Exception as e:
            # Fallback text display
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="GUIProgress",
                context={"operation": "draw_generation_progress", "x": x, "y": y}
            )
            error_text = (
                f"Generation {self.current_generation}/{self.total_generations}"
            )
            text_surface = self.font_medium.render(
                error_text, True, self.colors["text"]
            )
            screen.blit(text_surface, (x, y))

    def draw_phase_progress(self, screen: pygame.Surface, x: int, y: int) -> None:
        """
        Draw current phase progress

        Args:
            screen: Pygame surface to draw on
            x: X position
            y: Y position
        """
        try:
            # Phase title
            phase_text = f"Current Phase: {self.current_phase}"
            title_surface = self.font_medium.render(
                phase_text, True, self.colors["text"]
            )
            screen.blit(title_surface, (x, y))

            # Phase progress bar
            bar_y = y + 25
            bar_width = 300
            bar_height = 15

            # Background
            bg_rect = pygame.Rect(x, bar_y, bar_width, bar_height)
            pygame.draw.rect(screen, self.colors["progress_bg"], bg_rect)
            pygame.draw.rect(screen, self.colors["text_secondary"], bg_rect, 1)

            # Progress fill
            fill_width = int(bar_width * self.phase_progress)
            if fill_width > 0:
                fill_rect = pygame.Rect(x, bar_y, fill_width, bar_height)
                phase_color = self.colors["phase_colors"].get(
                    self.current_phase, self.colors["progress_fill"]
                )
                pygame.draw.rect(screen, phase_color, fill_rect)

            # Progress percentage
            progress_pct = f"{self.phase_progress * 100:.1f}%"
            pct_surface = self.font_small.render(
                progress_pct, True, self.colors["text_secondary"]
            )
            screen.blit(pct_surface, (x + bar_width + 10, bar_y))

        except Exception as e:
            # Fallback display
            print(f"⚠️ Phase progress display error: {e}")
            error_text = (
                f"Phase: {self.current_phase} ({self.phase_progress * 100:.1f}%)"
            )
            text_surface = self.font_small.render(error_text, True, self.colors["text"])
            screen.blit(text_surface, (x, y))

    def draw_metrics_panel(self, screen: pygame.Surface, x: int, y: int) -> None:
        """
        Draw current metrics panel

        Args:
            screen: Pygame surface to draw on
            x: X position
            y: Y position
        """
        try:
            if not self.current_metrics:
                no_metrics_text = "No metrics available"
                text_surface = self.font_small.render(
                    no_metrics_text, True, self.colors["text_secondary"]
                )
                screen.blit(text_surface, (x, y))
                return

            # Metrics title
            title_surface = self.font_medium.render(
                "Current Metrics:", True, self.colors["text"]
            )
            screen.blit(title_surface, (x, y))

            # Display key metrics
            metrics_y = y + 25
            line_height = 18

            priority_metrics = [
                "win_rate",
                "training_loss",
                "games_played",
                "skill_score",
            ]

            for i, key in enumerate(priority_metrics):
                if key in self.current_metrics:
                    value = self.current_metrics[key]

                    # Format value based on type
                    if key == "win_rate":
                        display_text = f"Win Rate: {value:.1%}"
                    elif key == "training_loss":
                        display_text = f"Training Loss: {value:.4f}"
                    elif key == "games_played":
                        display_text = f"Games Played: {value}"
                    elif key == "skill_score":
                        display_text = f"Skill Score: {value:.2f}"
                    else:
                        display_text = f"{key}: {value}"

                    text_surface = self.font_small.render(
                        display_text, True, self.colors["text_secondary"]
                    )
                    screen.blit(text_surface, (x, metrics_y + i * line_height))

        except Exception as e:
            error_text = f"Metrics error: {str(e)[:30]}"
            text_surface = self.font_small.render(error_text, True, self.colors["text"])
            screen.blit(text_surface, (x, y))

    def draw_growth_chart(
        self, screen: pygame.Surface, data: List[Dict[str, Any]]
    ) -> None:
        """
        Draw generational growth chart

        Args:
            screen: Pygame surface to draw on
            data: Historical performance data
        """
        if not data or len(data) < 2:
            return

        try:
            # Chart area
            chart_x = 50
            chart_y = 50
            chart_width = 300
            chart_height = 150

            # Background
            chart_rect = pygame.Rect(chart_x, chart_y, chart_width, chart_height)
            pygame.draw.rect(screen, (30, 30, 30), chart_rect)
            pygame.draw.rect(screen, self.colors["text_secondary"], chart_rect, 1)

            # Title
            title_surface = self.font_small.render(
                "Performance Trend", True, self.colors["text"]
            )
            screen.blit(title_surface, (chart_x + 5, chart_y - 20))

            # Extract win rate data
            win_rates = []
            generations = []

            for point in data[-20:]:  # Last 20 generations
                if "win_rate" in point and "generation" in point:
                    win_rates.append(point["win_rate"])
                    generations.append(point["generation"])

            if len(win_rates) < 2:
                return

            # Normalize data to chart coordinates
            min_rate = min(win_rates)
            max_rate = max(win_rates)
            rate_range = max_rate - min_rate if max_rate > min_rate else 1

            points = []
            for i, rate in enumerate(win_rates):
                chart_x_pos = chart_x + (i / (len(win_rates) - 1)) * chart_width
                chart_y_pos = (
                    chart_y
                    + chart_height
                    - ((rate - min_rate) / rate_range) * chart_height
                )
                points.append((int(chart_x_pos), int(chart_y_pos)))

            # Draw grid lines
            for i in range(5):
                grid_y = chart_y + (i / 4) * chart_height
                pygame.draw.line(
                    screen,
                    self.colors["chart_grid"],
                    (chart_x, grid_y),
                    (chart_x + chart_width, grid_y),
                    1,
                )

            # Draw trend line
            if len(points) > 1:
                pygame.draw.lines(screen, self.colors["chart_line"], False, points, 2)

            # Draw data points
            for point in points:
                pygame.draw.circle(screen, self.colors["chart_line"], point, 3)

            # Y-axis labels
            for i in range(3):
                label_rate = min_rate + (i / 2) * rate_range
                label_text = f"{label_rate:.1%}"
                label_surface = self.font_small.render(
                    label_text, True, self.colors["text_secondary"]
                )
                label_y = chart_y + chart_height - (i / 2) * chart_height - 5
                screen.blit(label_surface, (chart_x - 40, label_y))

        except Exception as e:
            # Fallback text
            print(f"⚠️ Chart display error: {e}")
            error_text = f"Chart error: {str(e)[:20]}"
            text_surface = self.font_small.render(error_text, True, self.colors["text"])
            screen.blit(text_surface, (50, 50))

    def display_growth_chart(self, historical_data: List[Dict[str, Any]]) -> None:
        """
        Update the growth chart with new historical data

        Args:
            historical_data: List of historical performance data
        """
        # Store the data for rendering
        self.generation_data.extend(historical_data)

        # Keep only recent data for performance
        if len(self.generation_data) > 100:
            self.generation_data = self.generation_data[-100:]

    def adapt_to_window_size(self, width: int, height: int) -> None:
        """
        Adapt progress display to window size

        Args:
            width: Window width
            height: Window height
        """
        try:
            # Adjust progress area based on window size
            margin = 50

            self.progress_area = {
                "x": margin,
                "y": height - 150,  # Bottom area
                "width": width - 2 * margin,
                "height": 120,
            }

            # Ensure minimum size
            if self.progress_area["width"] < 400:
                self.progress_area["width"] = 400

            if self.progress_area["height"] < 80:
                self.progress_area["height"] = 80

        except Exception as e:
            print(f"⚠️ Error adapting to window size: {e}")

    def render_all_progress(self, screen: pygame.Surface) -> None:
        """
        Render all progress elements

        Args:
            screen: Pygame surface to draw on
        """
        try:
            # Get window dimensions
            width, height = screen.get_size()
            self.adapt_to_window_size(width, height)

            # Progress area background
            progress_bg = pygame.Rect(
                self.progress_area["x"],
                self.progress_area["y"],
                self.progress_area["width"],
                self.progress_area["height"],
            )
            pygame.draw.rect(screen, (20, 20, 20), progress_bg)
            pygame.draw.rect(screen, self.colors["text_secondary"], progress_bg, 1)

            # Draw progress elements
            base_x = self.progress_area["x"] + 10
            base_y = self.progress_area["y"] + 10

            # Generation progress
            self.draw_generation_progress(screen, base_x, base_y)

            # Phase progress
            self.draw_phase_progress(screen, base_x, base_y + 50)

            # Metrics panel
            metrics_x = base_x + 450
            self.draw_metrics_panel(screen, metrics_x, base_y)

            # Growth chart (if space allows)
            if width > 800:
                self.draw_growth_chart(screen, self.generation_data)

        except Exception as e:
            # Fallback minimal display
            print(f"⚠️ Progress rendering error: {e}")
            error_text = (
                f"Progress: Gen {self.current_generation}/{self.total_generations}"
            )
            text_surface = self.font_medium.render(
                error_text, True, self.colors["text"]
            )
            screen.blit(text_surface, (50, height - 50))

    def cleanup(self) -> None:
        """Clean up GUI progress resources"""
        # Clear data to free memory
        self.generation_data.clear()
        self.current_metrics.clear()

        print("🎮 GUI progress tracking cleanup completed")
