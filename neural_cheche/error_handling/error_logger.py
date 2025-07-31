"""
Comprehensive error logging system
"""

import csv
import json
import gzip
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class ErrorLogger:
    """Comprehensive error logging with multiple output formats"""

    def __init__(
        self, log_directory: str = "logs", config: Optional[Dict[str, Any]] = None
    ):
        """Initialize error logger"""
        self.log_directory = Path(log_directory)
        self.config = config or self._get_default_config()

        # Create log directory
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Log files
        self.error_log_file = self.log_directory / "errors.log"
        self.error_json_file = self.log_directory / "errors.json"
        self.summary_file = self.log_directory / "error_summary.json"

        # In-memory storage for recent errors
        self.recent_errors: List[Dict[str, Any]] = []
        self.error_counts: Dict[str, int] = {}

        # Initialize log files
        self._initialize_log_files()

        print(f"📝 ErrorLogger initialized with directory: {log_directory}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration"""
        return {
            "log_to_file": True,
            "log_to_json": True,
            "max_log_file_size": 10 * 1024 * 1024,  # 10MB
            "max_recent_errors": 100,
            "include_traceback": True,
            "include_context": True,
            "rotate_logs": True,
            "compression": False,
        }

    def _initialize_log_files(self):
        """Initialize log files if they don't exist"""
        try:
            # Initialize JSON error log
            if not self.error_json_file.exists():
                with open(self.error_json_file, "w") as f:
                    json.dump([], f)

            # Initialize summary file
            if not self.summary_file.exists():
                initial_summary = {
                    "created": datetime.now().isoformat(),
                    "total_errors": 0,
                    "last_updated": datetime.now().isoformat(),
                    "error_categories": {},
                    "error_components": {},
                }
                with open(self.summary_file, "w") as f:
                    json.dump(initial_summary, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to initialize log files: {e}")

    def log_error(
        self,
        error_info: Dict[str, Any],
        include_traceback: Optional[bool] = None,
        include_context: Optional[bool] = None,
    ):
        """Log error with comprehensive information"""

        # Use config defaults if not specified
        include_traceback = (
            include_traceback
            if include_traceback is not None
            else self.config.get("include_traceback", True)
        )
        include_context = (
            include_context
            if include_context is not None
            else self.config.get("include_context", True)
        )

        # Prepare log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_id": error_info.get("error_id", "unknown"),
            "category": error_info.get("category", "unknown"),
            "severity": error_info.get("severity", "unknown"),
            "component": error_info.get("component", "unknown"),
            "message": error_info.get("message", "No message provided"),
            "recovery_attempted": error_info.get("recovery_attempted", False),
            "recovery_successful": error_info.get("recovery_successful", False),
        }

        # Add optional fields
        if include_traceback and "traceback" in error_info:
            log_entry["traceback"] = error_info["traceback"]

        if include_context and "context" in error_info:
            log_entry["context"] = error_info["context"]

        # Log to different outputs
        if self.config.get("log_to_file", True):
            self._log_to_text_file(log_entry)

        if self.config.get("log_to_json", True):
            self._log_to_json_file(log_entry)

        # Add to recent errors
        self._add_to_recent_errors(log_entry)

        # Update summary
        self._update_summary(log_entry)

        # Check for log rotation
        if self.config.get("rotate_logs", True):
            self._check_log_rotation()

    def _log_to_text_file(self, log_entry: Dict[str, Any]):
        """Log to text file"""
        try:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                # Format log entry
                log_line = f"[{log_entry['timestamp']}] {log_entry['severity'].upper()} - {log_entry['component']}: {log_entry['message']}\n"

                if "context" in log_entry and log_entry["context"]:
                    log_line += f"  Context: {log_entry['context']}\n"

                if "traceback" in log_entry and log_entry["traceback"]:
                    log_line += f"  Traceback: {log_entry['traceback']}\n"

                if log_entry["recovery_attempted"]:
                    recovery_status = (
                        "SUCCESS" if log_entry["recovery_successful"] else "FAILED"
                    )
                    log_line += f"  Recovery: {recovery_status}\n"

                log_line += "\n"

                f.write(log_line)
                f.flush()

        except Exception as e:
            print(f"⚠️ Failed to log to text file: {e}")

    def _log_to_json_file(self, log_entry: Dict[str, Any]):
        """Log to JSON file"""
        try:
            # Read existing entries
            entries = []
            if self.error_json_file.exists():
                try:
                    with open(self.error_json_file, "r", encoding="utf-8") as f:
                        entries = json.load(f)
                except json.JSONDecodeError:
                    entries = []

            # Add new entry
            entries.append(log_entry)

            # Write back to file
            with open(self.error_json_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Failed to log to JSON file: {e}")

    def _add_to_recent_errors(self, log_entry: Dict[str, Any]):
        """Add error to recent errors list"""
        self.recent_errors.append(log_entry)

        # Trim if too many
        max_recent = self.config.get("max_recent_errors", 100)
        if len(self.recent_errors) > max_recent:
            self.recent_errors.pop(0)

        # Update error counts
        category = log_entry.get("category", "unknown")
        component = log_entry.get("component", "unknown")

        self.error_counts[f"category_{category}"] = (
            self.error_counts.get(f"category_{category}", 0) + 1
        )
        self.error_counts[f"component_{component}"] = (
            self.error_counts.get(f"component_{component}", 0) + 1
        )

    def _update_summary(self, log_entry: Dict[str, Any]):
        """Update error summary file"""
        try:
            # Read current summary
            summary = {}
            if self.summary_file.exists():
                with open(self.summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)

            # Update summary
            summary["total_errors"] = summary.get("total_errors", 0) + 1
            summary["last_updated"] = datetime.now().isoformat()

            # Update category counts
            category = log_entry.get("category", "unknown")
            if "error_categories" not in summary:
                summary["error_categories"] = {}
            summary["error_categories"][category] = (
                summary["error_categories"].get(category, 0) + 1
            )

            # Update component counts
            component = log_entry.get("component", "unknown")
            if "error_components" not in summary:
                summary["error_components"] = {}
            summary["error_components"][component] = (
                summary["error_components"].get(component, 0) + 1
            )

            # Write updated summary
            with open(self.summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Failed to update error summary: {e}")

    def _check_log_rotation(self):
        """Check if log files need rotation"""
        max_size = self.config.get("max_log_file_size", 10 * 1024 * 1024)

        # Check text log file
        if (
            self.error_log_file.exists()
            and self.error_log_file.stat().st_size > max_size
        ):
            self._rotate_log_file(self.error_log_file)

        # Check JSON log file
        if (
            self.error_json_file.exists()
            and self.error_json_file.stat().st_size > max_size
        ):
            self._rotate_log_file(self.error_json_file)

    def _rotate_log_file(self, log_file: Path):
        """Rotate a log file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            rotated_path = log_file.parent / rotated_name

            # Move current log to rotated name
            log_file.rename(rotated_path)

            # Compress if enabled
            if self.config.get("compression", False):
                self._compress_log_file(rotated_path)

            print(f"🔄 Log file rotated: {rotated_name}")

        except Exception as e:
            print(f"⚠️ Failed to rotate log file: {e}")

    def _compress_log_file(self, log_file: Path):
        """Compress a log file"""
        try:

            compressed_path = log_file.with_suffix(log_file.suffix + ".gz")

            with open(log_file, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original file
            log_file.unlink()

            print(f"🗜️ Log file compressed: {compressed_path.name}")

        except Exception as e:
            print(f"⚠️ Failed to compress log file: {e}")

    def get_recent_errors(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent errors"""
        if count is None:
            return self.recent_errors.copy()
        else:
            return self.recent_errors[-count:] if count > 0 else []

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        try:
            if self.summary_file.exists():
                with open(self.summary_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {
                    "total_errors": 0,
                    "error_categories": {},
                    "error_components": {},
                }
        except Exception as e:
            print(f"⚠️ Failed to read error summary: {e}")
            return {"error": str(e)}

    def search_errors(
        self,
        category: Optional[str] = None,
        component: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search errors with filters"""
        try:
            # Load all errors from JSON file
            if not self.error_json_file.exists():
                return []

            with open(self.error_json_file, "r", encoding="utf-8") as f:
                all_errors = json.load(f)

            # Apply filters
            filtered_errors = []
            for error in all_errors:
                # Category filter
                if category and error.get("category") != category:
                    continue

                # Component filter
                if component and error.get("component") != component:
                    continue

                # Severity filter
                if severity and error.get("severity") != severity:
                    continue

                # Time filters
                error_time = error.get("timestamp")
                if start_time and error_time < start_time:
                    continue
                if end_time and error_time > end_time:
                    continue

                filtered_errors.append(error)

            return filtered_errors

        except Exception as e:
            print(f"⚠️ Failed to search errors: {e}")
            return []

    def clear_logs(self):
        """Clear all log files"""
        try:
            # Clear text log
            if self.error_log_file.exists():
                self.error_log_file.unlink()

            # Clear JSON log
            if self.error_json_file.exists():
                with open(self.error_json_file, "w") as f:
                    json.dump([], f)

            # Reset summary
            initial_summary = {
                "created": datetime.now().isoformat(),
                "total_errors": 0,
                "last_updated": datetime.now().isoformat(),
                "error_categories": {},
                "error_components": {},
            }
            with open(self.summary_file, "w") as f:
                json.dump(initial_summary, f, indent=2)

            # Clear in-memory data
            self.recent_errors.clear()
            self.error_counts.clear()

            print("🧹 All error logs cleared")

        except Exception as e:
            print(f"⚠️ Failed to clear logs: {e}")

    def export_errors(self, output_file: str, format: str = "json"):
        """Export errors to file"""
        try:
            if format.lower() == "json":
                # Export as JSON
                if self.error_json_file.exists():
                    shutil.copy2(self.error_json_file, output_file)
                else:
                    with open(output_file, "w") as f:
                        json.dump([], f)

            elif format.lower() == "csv":
                # Export as CSV

                # Load errors
                errors = []
                if self.error_json_file.exists():
                    with open(self.error_json_file, "r") as f:
                        errors = json.load(f)

                # Write CSV
                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    if errors:
                        fieldnames = errors[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(errors)

            print(f"📤 Errors exported to: {output_file}")

        except Exception as e:
            print(f"⚠️ Failed to export errors: {e}")
