"""
Data models for the move history and backup system
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import json


@dataclass
class MoveData:
    """Comprehensive data for a single move"""
    game_id: str
    generation: int
    agent_name: str
    game_type: str
    move_number: int
    move: str
    board_state_before: str
    board_state_after: str
    evaluation_score: float
    policy_distribution: Dict[str, float]
    thinking_time: float
    captured_pieces: List[str]
    timestamp: datetime
    is_valid: bool = True
    validation_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoveData':
        """Create from dictionary (JSON deserialization)"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class GameInfo:
    """Information about a game session"""
    game_id: str
    generation: int
    agent1_name: str
    agent2_name: str
    game_type: str
    start_time: datetime
    max_moves: int
    visualization_enabled: bool
    validation_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameInfo':
        """Create from dictionary (JSON deserialization)"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        return cls(**data)


@dataclass
class GameResult:
    """Final result of a completed game"""
    game_id: str
    winner: str
    final_score: Dict[str, float]
    total_moves: int
    game_duration: float
    termination_reason: str
    captured_pieces: Dict[str, List[str]]
    final_board_state: str
    end_time: datetime
    validation_violations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResult':
        """Create from dictionary (JSON deserialization)"""
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class GenerationSummary:
    """Summary of an entire generation's training"""
    generation: int
    start_time: datetime
    end_time: datetime
    total_games: int
    total_moves: int
    agents_trained: List[str]
    champion_changes: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    validation_summary: Dict[str, Any]
    backup_files: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationSummary':
        """Create from dictionary (JSON deserialization)"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


class HistoryEncoder(json.JSONEncoder):
    """Custom JSON encoder for history data"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)