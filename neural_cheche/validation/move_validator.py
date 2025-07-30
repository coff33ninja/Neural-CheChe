"""
Core move validation system to prevent illegal AI moves
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, List, Dict, Optional

from .data_models import ValidationResult, ValidationViolation, PieceComparison
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
    
    def validate_move(self, board_before: Any, board_after: Any, move: Any, 
                     agent_name: str = "Unknown", generation: int = 0, 
                     move_number: int = 0) -> ValidationResult:
        """
        Validate that a move is legal and doesn't create magical pieces
        
        Args:
            board_before: Board state before the move
            board_after: Board state after the move
            move: The move that was made
            agent_name: Name of the AI agent making the move
            generation: Current training generation
            move_number: Move number in the game
            
        Returns:
            ValidationResult with validation details
        """
        timestamp = datetime.now()
        violations = []
        magical_pieces = []
        
        # Generate board hashes for tracking
        board_hash_before = self._generate_board_hash(board_before)
        board_hash_after = self._generate_board_hash(board_after)
        
        try:
            # Check piece integrity
            if not self.check_piece_integrity(board_before, board_after):
                violations.append("Piece integrity violation detected")
            
            # Detect magical pieces
            detected_magical = self.detect_magical_pieces(board_before, board_after)
            if detected_magical:
                magical_pieces.extend(detected_magical)
                violations.append(f"Magical pieces detected: {', '.join(detected_magical)}")
            
            # Validate piece changes are legal for this game type
            piece_comparison = self.piece_tracker.compare_states(
                self.piece_tracker.track_board_state(board_before),
                self.piece_tracker.track_board_state(board_after)
            )
            
            if not self.piece_tracker.validate_piece_changes(piece_comparison, move):
                violations.append("Illegal piece transition detected")
            
            # Create validation result
            is_valid = len(violations) == 0 and len(magical_pieces) == 0
            
            result = ValidationResult(
                is_valid=is_valid,
                violations=violations,
                magical_pieces=magical_pieces,
                timestamp=timestamp,
                board_hash_before=board_hash_before,
                board_hash_after=board_hash_after,
                move_description=str(move)
            )
            
            # Log violations if any
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
                    timestamp=timestamp
                )
                self.log_violation(violation)
            
            return result
            
        except Exception as e:
            # Handle validation errors gracefully
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
                severity="ERROR"
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
                move_description=str(move)
            )
    
    def check_piece_integrity(self, board_before: Any, board_after: Any) -> bool:
        """
        Check that no pieces were illegally created or destroyed
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            
        Returns:
            True if piece integrity is maintained
        """
        try:
            before_state = self.piece_tracker.track_board_state(board_before)
            after_state = self.piece_tracker.track_board_state(board_after)
            
            comparison = self.piece_tracker.compare_states(before_state, after_state)
            
            # Check for illegal piece creation (magical pieces)
            net_change = comparison.get_net_piece_change()
            
            # In normal gameplay, pieces can only be removed (captured) or moved
            # New pieces should never appear except through promotion
            for piece_type, change in net_change.items():
                if change > 0:  # Positive change means pieces were added
                    # Check if this is a legal promotion (pawn to queen, etc.)
                    if not self._is_legal_promotion(piece_type, board_before, board_after):
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error checking piece integrity: {e}")
            return False
    
    def detect_magical_pieces(self, board_before: Any, board_after: Any) -> List[str]:
        """
        Detect pieces that were magically created
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            
        Returns:
            List of magical piece descriptions
        """
        magical_pieces = []
        
        try:
            before_state = self.piece_tracker.track_board_state(board_before)
            after_state = self.piece_tracker.track_board_state(board_after)
            
            comparison = self.piece_tracker.compare_states(before_state, after_state)
            net_change = comparison.get_net_piece_change()
            
            for piece_type, change in net_change.items():
                if change > 0:  # Pieces were added
                    # Check if this is a legal addition (promotion, etc.)
                    if not self._is_legal_piece_addition(piece_type, change, board_before, board_after):
                        magical_pieces.append(f"{piece_type} (+{change})")
            
            return magical_pieces
            
        except Exception as e:
            print(f"Error detecting magical pieces: {e}")
            return [f"Detection error: {str(e)}"]
    
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
                with open(self.violation_log_path, 'r') as f:
                    violations = json.load(f)
            
            # Add new violation
            violations.append(violation.to_dict())
            self.violations_count += 1
            
            # Save updated violations
            with open(self.violation_log_path, 'w') as f:
                json.dump(violations, f, indent=2)
            
            print(f"⚠️ Validation violation logged: {violation.description}")
            
        except Exception as e:
            print(f"Error logging violation: {e}")
    
    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get statistics about violations"""
        try:
            if not os.path.exists(self.violation_log_path):
                return {"total_violations": 0, "violation_types": {}}
            
            with open(self.violation_log_path, 'r') as f:
                violations = json.load(f)
            
            stats = {
                "total_violations": len(violations),
                "violation_types": {},
                "agents_with_violations": set(),
                "recent_violations": []
            }
            
            for violation in violations:
                v_type = violation.get('violation_type', 'UNKNOWN')
                stats["violation_types"][v_type] = stats["violation_types"].get(v_type, 0) + 1
                stats["agents_with_violations"].add(violation.get('agent_name', 'Unknown'))
            
            # Convert set to list for JSON serialization
            stats["agents_with_violations"] = list(stats["agents_with_violations"])
            
            # Get recent violations (last 10)
            stats["recent_violations"] = violations[-10:] if len(violations) > 10 else violations
            
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
    
    def _is_legal_promotion(self, piece_type: str, board_before: Any, board_after: Any) -> bool:
        """
        Check if a piece addition is due to legal promotion
        
        This is game-specific and should be overridden by game implementations
        """
        # Default implementation - assume no promotions are legal
        # This will be overridden by specific game validators
        return False
    
    def _is_legal_piece_addition(self, piece_type: str, count: int, 
                                board_before: Any, board_after: Any) -> bool:
        """
        Check if piece addition is legal (promotion, etc.)
        
        This is game-specific and should be overridden by game implementations
        """
        # Default implementation - no piece additions are legal
        return False