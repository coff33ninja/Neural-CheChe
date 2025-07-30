"""
Data models for the validation system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class ValidationResult:
    """Result of move validation"""
    is_valid: bool
    violations: List[str]
    magical_pieces: List[str]
    timestamp: datetime
    board_hash_before: str
    board_hash_after: str
    move_description: str = ""
    
    def has_violations(self) -> bool:
        """Check if there are any violations"""
        return len(self.violations) > 0 or len(self.magical_pieces) > 0
    
    def get_violation_summary(self) -> str:
        """Get a summary of all violations"""
        summary = []
        if self.violations:
            summary.append(f"Violations: {', '.join(self.violations)}")
        if self.magical_pieces:
            summary.append(f"Magical pieces: {', '.join(self.magical_pieces)}")
        return "; ".join(summary) if summary else "No violations"


@dataclass
class ValidationViolation:
    """Details of a specific validation violation"""
    violation_type: str
    description: str
    game_type: str
    agent_name: str
    generation: int
    move_number: int
    board_before: str
    board_after: str
    attempted_move: str
    timestamp: datetime
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'violation_type': self.violation_type,
            'description': self.description,
            'game_type': self.game_type,
            'agent_name': self.agent_name,
            'generation': self.generation,
            'move_number': self.move_number,
            'board_before': self.board_before,
            'board_after': self.board_after,
            'attempted_move': self.attempted_move,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity
        }


@dataclass
class PieceComparison:
    """Comparison between two board states"""
    pieces_added: Dict[str, int]  # piece_type -> count
    pieces_removed: Dict[str, int]  # piece_type -> count
    pieces_moved: List[str]  # list of piece movements
    captured_pieces: List[str]  # pieces that were captured
    is_valid_transition: bool
    violation_reasons: List[str]
    
    def get_net_piece_change(self) -> Dict[str, int]:
        """Get net change in piece counts"""
        net_change = {}
        
        # Add pieces that were added
        for piece, count in self.pieces_added.items():
            net_change[piece] = net_change.get(piece, 0) + count
        
        # Subtract pieces that were removed
        for piece, count in self.pieces_removed.items():
            net_change[piece] = net_change.get(piece, 0) - count
        
        return net_change
    
    def has_magical_pieces(self) -> bool:
        """Check if any pieces were magically created"""
        net_change = self.get_net_piece_change()
        return any(count > 0 for count in net_change.values())