"""
Progress Manager - Coordinates CLI and GUI progress tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

from .cli_progress import CLIProgress
from .gui_progress import GUIProgress
from ..error_handling import ErrorHandler, ErrorCategory, ErrorSeverity
from ..error_handling.decorators import handle_errors


class ProgressManager:
    """Manages progress tracking for both CLI and GUI interfaces"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enable_cli = config.get("enable_cli_progress", True)
        self.enable_gui = config.get("enable_gui_progress", True)
        self.update_frequency = config.get("update_frequency", 0.1)
        self.show_detailed_metrics = config.get("show_detailed_metrics", True)

        # Initialize error handler
        self.error_handler = ErrorHandler()

        # Progress tracking components
        self.cli_progress: Optional[CLIProgress] = None
        self.gui_progress: Optional[GUIProgress] = None

        # Progress state
        self.current_generation = 0
        self.total_generations = 0
        self.current_phase = "Initializing"
        self.phase_progress = 0.0

        # Historical data for growth tracking
        self.generation_history: List[Dict[str, Any]] = []
        self.metrics_history: List[Dict[str, Any]] = []

        # Create progress data directory with error handling
        try:
            os.makedirs("progress_data", exist_ok=True)
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.FILE_IO,
                severity=ErrorSeverity.MEDIUM,
                component="ProgressManager",
                context={"operation": "create_progress_directory"},
            )

        # Load historical data if available
        self._load_historical_data()

    @handle_errors(
        category=ErrorCategory.PROGRESS,
        severity=ErrorSeverity.LOW,
        component="cli_progress_init",
        recovery_scenario="progress_display_failed",
        max_retries=1,
        suppress_errors=True,
    )
    def initialize_cli_progress(self, total_generations: int) -> None:
        """
        Initialize CLI progress tracking

        Args:
            total_generations: Total number of generations to train
        """
        if not self.enable_cli:
            return

        try:
            self.total_generations = total_generations
            self.cli_progress = CLIProgress(total_generations)
            print("📊 CLI progress tracking initialized")

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.PROGRESS,
                severity=ErrorSeverity.LOW,
                component="ProgressManager",
                context={
                    "operation": "initialize_cli_progress",
                    "total_generations": total_generations,
                },
            )
            self.enable_cli = False

    @handle_errors(
        category=ErrorCategory.GUI,
        severity=ErrorSeverity.LOW,
        component="gui_progress_init",
        recovery_scenario="gui_initialization_failed",
        max_retries=1,
        suppress_errors=True,
    )
    def initialize_gui_progress(self, visualization_manager) -> None:
        """
        Initialize GUI progress tracking

        Args:
            visualization_manager: The VisualizationManager instance
        """
        if not self.enable_gui or not visualization_manager:
            return

        try:
            self.gui_progress = GUIProgress(visualization_manager)
            print("🎮 GUI progress tracking initialized")

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.GUI,
                severity=ErrorSeverity.LOW,
                component="ProgressManager",
                context={"operation": "initialize_gui_progress"},
            )
            self.enable_gui = False

    def update_generation_progress(self, current: int, metrics: Dict[str, Any]) -> None:
        """
        Update progress for the current generation

        Args:
            current: Current generation number
            metrics: Dictionary of training metrics
        """
        self.current_generation = current

        # Update CLI progress with error handling
        if self.cli_progress:
            try:
                safe_metrics = metrics if metrics is not None else {}
                self.cli_progress.update_generation(current, safe_metrics)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.PROGRESS,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "update_cli_generation",
                        "generation": current,
                    },
                )

        # Update GUI progress with error handling
        if self.gui_progress:
            try:
                safe_metrics = metrics if metrics is not None else {}
                self.gui_progress.update_generation(current, safe_metrics)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.GUI,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "update_gui_generation",
                        "generation": current,
                    },
                )

        # Store metrics for historical tracking
        safe_metrics = metrics if metrics is not None else {}
        metrics_entry = {
            "generation": current,
            "timestamp": datetime.now().isoformat(),
            **safe_metrics,
        }
        self.metrics_history.append(metrics_entry)

        # Save progress data periodically
        if current % 5 == 0:  # Save every 5 generations
            self._save_progress_data()

    def update_phase_progress(self, phase: str, progress: float) -> None:
        """
        Update progress for the current training phase

        Args:
            phase: Name of the current phase
            progress: Progress percentage (0.0 to 1.0)
        """
        self.current_phase = phase
        self.phase_progress = progress

        # Update CLI progress with error handling
        if self.cli_progress:
            try:
                self.cli_progress.update_phase(phase, progress)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.PROGRESS,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "update_cli_phase",
                        "phase": phase,
                        "progress": progress,
                    },
                )

        # Update GUI progress with error handling
        if self.gui_progress:
            try:
                self.gui_progress.update_phase(phase, progress)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.GUI,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "update_gui_phase",
                        "phase": phase,
                        "progress": progress,
                    },
                )

    def display_generational_growth(
        self, historical_data: List[Dict[str, Any]]
    ) -> None:
        """
        Display generational growth trends

        Args:
            historical_data: List of historical performance data
        """
        # Add to our historical data
        self.generation_history.extend(historical_data)

        # Display in CLI with error handling
        if self.cli_progress:
            try:
                self.cli_progress.display_growth_summary(historical_data)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.PROGRESS,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "display_cli_growth",
                        "data_points": len(historical_data),
                    },
                )

        # Display in GUI with error handling
        if self.gui_progress:
            try:
                self.gui_progress.display_growth_chart(historical_data)
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.GUI,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={
                        "operation": "display_gui_growth",
                        "data_points": len(historical_data),
                    },
                )

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current progress metrics"""
        return {
            "current_generation": self.current_generation,
            "total_generations": self.total_generations,
            "current_phase": self.current_phase,
            "phase_progress": self.phase_progress,
            "completion_percentage": (
                self.current_generation / max(1, self.total_generations)
            )
            * 100,
            "historical_data_points": len(self.generation_history),
        }

    def get_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends from historical data"""
        if len(self.metrics_history) < 2:
            return {"trend": "insufficient_data"}

        try:
            # Get recent metrics
            recent_metrics = self.metrics_history[-10:]  # Last 10 generations

            # Calculate trends
            win_rates = [
                m.get("win_rate", 0) for m in recent_metrics if "win_rate" in m
            ]
            training_losses = [
                m.get("training_loss", 0)
                for m in recent_metrics
                if "training_loss" in m
            ]

            trends = {
                "win_rate_trend": self._calculate_trend(win_rates),
                "loss_trend": self._calculate_trend(training_losses),
                "recent_generations": len(recent_metrics),
                "improvement_rate": 0.0,
            }

            # Calculate improvement rate
            if len(win_rates) >= 2:
                trends["improvement_rate"] = (win_rates[-1] - win_rates[0]) / len(
                    win_rates
                )

            return trends

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.PROGRESS,
                severity=ErrorSeverity.LOW,
                component="ProgressManager",
                context={"operation": "calculate_performance_trends"},
            )
            return {"trend": "calculation_error", "error": str(e)}

    def cleanup(self) -> None:
        """Clean up progress tracking resources"""
        # Save final progress data
        self._save_progress_data()

        # Cleanup CLI progress with error handling
        if self.cli_progress:
            try:
                self.cli_progress.cleanup()
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.PROGRESS,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={"operation": "cleanup_cli_progress"},
                )

        # Cleanup GUI progress with error handling
        if self.gui_progress:
            try:
                self.gui_progress.cleanup()
            except Exception as e:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.GUI,
                    severity=ErrorSeverity.LOW,
                    component="ProgressManager",
                    context={"operation": "cleanup_gui_progress"},
                )

        print("📊 Progress tracking cleanup completed")

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "stable"

        # Simple linear trend calculation
        first_half = sum(values[: len(values) // 2]) / max(1, len(values) // 2)
        second_half = sum(values[len(values) // 2 :]) / max(
            1, len(values) - len(values) // 2
        )

        diff = second_half - first_half

        if diff > 0.05:  # 5% improvement threshold
            return "improving"
        elif diff < -0.05:  # 5% decline threshold
            return "declining"
        else:
            return "stable"

    def _load_historical_data(self) -> None:
        """Load historical progress data from disk"""
        try:
            # Load generation history
            gen_history_path = "progress_data/generation_history.json"
            if os.path.exists(gen_history_path):
                with open(gen_history_path, "r") as f:
                    self.generation_history = json.load(f)

            # Load metrics history
            metrics_history_path = "progress_data/metrics_history.json"
            if os.path.exists(metrics_history_path):
                with open(metrics_history_path, "r") as f:
                    self.metrics_history = json.load(f)

            print(f"📈 Loaded {len(self.generation_history)} historical generations")

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.FILE_IO,
                severity=ErrorSeverity.LOW,
                component="ProgressManager",
                context={"operation": "load_historical_data"},
            )
            self.generation_history = []
            self.metrics_history = []

    @handle_errors(
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.MEDIUM,
        component="progress_data_save",
        recovery_scenario="file_not_found",
        max_retries=2,
        suppress_errors=True,
    )
    def _save_progress_data(self) -> None:
        """Save progress data to disk"""
        try:
            # Save generation history
            gen_history_path = "progress_data/generation_history.json"
            with open(gen_history_path, "w") as f:
                json.dump(self.generation_history, f, indent=2)

            # Save metrics history
            metrics_history_path = "progress_data/metrics_history.json"
            with open(metrics_history_path, "w") as f:
                json.dump(self.metrics_history, f, indent=2)

            # Save current state
            state_path = "progress_data/current_state.json"
            current_state = {
                "current_generation": self.current_generation,
                "total_generations": self.total_generations,
                "current_phase": self.current_phase,
                "phase_progress": self.phase_progress,
                "last_updated": datetime.now().isoformat(),
            }

            with open(state_path, "w") as f:
                json.dump(current_state, f, indent=2)

        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.FILE_IO,
                severity=ErrorSeverity.MEDIUM,
                component="ProgressManager",
                context={"operation": "save_progress_data"},
            )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
