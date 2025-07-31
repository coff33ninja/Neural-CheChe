"""
Core move validation system to prevent illegal AI moves
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List

from .data_models import ValidationResult, ValidationViolation
from .piece_tracker import PieceTracker


class MoveValidator:
    """Validates AI moves to prevent illegal piece generation"""

    def __init__(self, game_type: str, log_violations: bool = True):
        self.game_type = game_type
        self.log_violations = log_violations
        self.piece_tracker = PieceTracker(game_type)
        self.violation_log_path = f"logs/violations_{game_type}.json"
        self.violations_count = 0

        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

    def validate_move(
        self,
        board_before: Any,
        board_after: Any,
        move: Any,
        agent_name: str = "Unknown",
        generation: int = 0,
        move_number: int = 0,
    ) -> ValidationResult:
        """
        Validate that a move is legal using PieceComparison from PieceTracker.
        """
        timestamp = datetime.now()
        board_hash_before = self._generate_board_hash(board_before)
        board_hash_after = self._generate_board_hash(board_after)
        try:
            before_state = self.piece_tracker.track_board_state(board_before)
            after_state = self.piece_tracker.track_board_state(board_after)
            comparison = self.piece_tracker.compare_states(before_state, after_state)

            violations = list(comparison.violation_reasons)
            magical_pieces = []
            # Use PieceComparison to detect magical pieces
            for piece_type, count in comparison.pieces_added.items():
                if count > 0 and not self.piece_tracker._is_legal_piece_creation(
                    piece_type, count, before_state, after_state
                ):
                    magical_pieces.append(f"{piece_type} (+{count})")

            is_valid = comparison.is_valid_transition and not magical_pieces

            result = ValidationResult(
                is_valid=is_valid,
                violations=violations,
                magical_pieces=magical_pieces,
                timestamp=timestamp,
                board_hash_before=board_hash_before,
                board_hash_after=board_hash_after,
                move_description=str(move),
            )

            if not is_valid and self.log_violations:
                violation = ValidationViolation(
                    violation_type="ILLEGAL_MOVE",
                    description=result.get_violation_summary(),
                    game_type=self.game_type,
                    agent_name=agent_name,
                    generation=generation,
                    move_number=move_number,
                    board_before=str(board_before),
                    board_after=str(board_after),
                    attempted_move=str(move),
                    timestamp=timestamp,
                )
                self.log_violation(violation)
            return result
        except Exception as e:
            error_violation = ValidationViolation(
                violation_type="VALIDATION_ERROR",
                description=f"Validation system error: {str(e)}",
                game_type=self.game_type,
                agent_name=agent_name,
                generation=generation,
                move_number=move_number,
                board_before=str(board_before),
                board_after=str(board_after),
                attempted_move=str(move),
                timestamp=timestamp,
                severity="ERROR",
            )
            if self.log_violations:
                self.log_violation(error_violation)
            return ValidationResult(
                is_valid=False,
                violations=[f"Validation error: {str(e)}"],
                magical_pieces=[],
                timestamp=timestamp,
                board_hash_before=board_hash_before,
                board_hash_after=board_hash_after,
                move_description=str(move),
            )

    def check_piece_integrity(self, board_before: Any, board_after: Any) -> bool:
        """
        Check if piece integrity is maintained between board states.
        Detects illegal piece creation beyond normal game rules.

        Args:
            board_before: Board state before the move
            board_after: Board state after the move

        Returns:
            True if piece integrity is maintained, False otherwise
        """
        try:
            before_state = self.piece_tracker.track_board_state(board_before)
            after_state = self.piece_tracker.track_board_state(board_after)
            comparison = self.piece_tracker.compare_states(before_state, after_state)

            # Check for any illegal piece additions
            for piece_type, count in comparison.pieces_added.items():
                if not self.piece_tracker._is_legal_piece_creation(
                    piece_type, count, before_state, after_state
                ):
                    return False

            return comparison.is_valid_transition

        except Exception as e:
            print(f"Error checking piece integrity: {e}")
            return False

    def detect_magical_pieces(self, board_before: Any, board_after: Any) -> List[str]:
        """
        Identify unauthorized piece generation (magical pieces).

        Args:
            board_before: Board state before the move
            board_after: Board state after the move

        Returns:
            List of magical pieces that were illegally created
        """
        magical_pieces = []

        try:
            before_state = self.piece_tracker.track_board_state(board_before)
            after_state = self.piece_tracker.track_board_state(board_after)
            comparison = self.piece_tracker.compare_states(before_state, after_state)

            # Identify pieces that were added illegally
            for piece_type, count in comparison.pieces_added.items():
                if not self.piece_tracker._is_legal_piece_creation(
                    piece_type, count, before_state, after_state
                ):
                    magical_pieces.append(f"{piece_type} (+{count})")

            return magical_pieces

        except Exception as e:
            print(f"Error detecting magical pieces: {e}")
            return []

    def log_violation(self, violation: ValidationViolation) -> None:
        """
        Log a validation violation to file

        Args:
            violation: The violation to log
        """
        try:
            # Load existing violations
            violations = []
            if os.path.exists(self.violation_log_path):
                with open(self.violation_log_path, "r") as f:
                    violations = json.load(f)

            # Add new violation
            violations.append(violation.to_dict())
            self.violations_count += 1

            # Save updated violations
            with open(self.violation_log_path, "w") as f:
                json.dump(violations, f, indent=2)

            print(f"⚠️ Validation violation logged: {violation.description}")

        except Exception as e:
            print(f"Error logging violation: {e}")

    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get statistics about violations"""
        try:
            if not os.path.exists(self.violation_log_path):
                return {"total_violations": 0, "violation_types": {}}

            with open(self.violation_log_path, "r") as f:
                violations = json.load(f)

            stats = {
                "total_violations": len(violations),
                "violation_types": {},
                "agents_with_violations": set(),
                "recent_violations": [],
            }

            for violation in violations:
                v_type = violation.get("violation_type", "UNKNOWN")
                stats["violation_types"][v_type] = (
                    stats["violation_types"].get(v_type, 0) + 1
                )
                stats["agents_with_violations"].add(
                    violation.get("agent_name", "Unknown")
                )

            # Convert set to list for JSON serialization
            stats["agents_with_violations"] = list(stats["agents_with_violations"])

            # Get recent violations (last 10)
            stats["recent_violations"] = (
                violations[-10:] if len(violations) > 10 else violations
            )

            return stats

        except Exception as e:
            print(f"Error getting violation statistics: {e}")
            return {"error": str(e)}

    def _generate_board_hash(self, board: Any) -> str:
        """Generate a hash of the board state for tracking"""
        try:
            board_str = str(board)
            return hashlib.md5(board_str.encode()).hexdigest()
        except Exception:
            return "hash_error"

    def _is_legal_promotion(
        self, piece_type: str, board_before: Any, board_after: Any
    ) -> bool:
        """
        Check if a piece addition is due to legal promotion

        This is game-specific and should be overridden by game implementations
        """
        # Default implementation - assume no promotions are legal
        # This will be overridden by specific game validators
        return False

    def _is_legal_piece_addition(
        self, piece_type: str, count: int, board_before: Any, board_after: Any
    ) -> bool:
        """
        Check if piece addition is legal (promotion, etc.)

        This is game-specific and should be overridden by game implementations
        """
        # Default implementation - no piece additions are legal
        return False
