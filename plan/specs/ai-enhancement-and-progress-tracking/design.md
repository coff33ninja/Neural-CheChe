# Design Document

## Overview

This design document outlines the enhancement of the Neural CheChe AI training system to address critical gameplay integrity, progress visualization, data persistence, and user experience improvements. The solution integrates seamlessly with the existing modular architecture while adding robust move validation, comprehensive progress tracking, detailed move history logging, and enhanced GUI capabilities.

## Architecture

### High-Level Architecture

The enhancement follows the existing modular structure and adds new components:

```
neural_cheche/
├── validation/              # NEW: Move validation system
│   ├── move_validator.py   # Core validation logic
│   └── piece_tracker.py    # Piece state tracking
├── progress/               # NEW: Progress tracking system
│   ├── progress_manager.py # Progress visualization manager
│   ├── cli_progress.py     # CLI progress bars (tqdm)
│   └── gui_progress.py     # GUI progress indicators
├── history/                # NEW: Move history system
│   ├── move_logger.py      # JSON move logging
│   ├── backup_manager.py   # Backup and persistence
│   └── score_tracker.py    # Score tracking and analysis
├── utils/
│   └── visualization.py    # ENHANCED: GUI improvements
└── games/
    ├── chess/
    │   └── chess_renderer.py # ENHANCED: Captured pieces display
    └── base_game.py         # ENHANCED: Validation hooks
```

### Integration Points

The enhancements integrate with existing components:
- **LeagueManager**: Orchestrates new validation and progress systems
- **BaseGame**: Extended with validation hooks and piece tracking
- **VisualizationManager**: Enhanced with progress bars and captured pieces
- **Competition**: Integrated with move logging and score tracking

## Components and Interfaces

### 1. Move Validation System

#### MoveValidator Class
```python
class MoveValidator:
    def __init__(self, game_type: str)
    def validate_move(self, board_before: Any, board_after: Any, move: Any) -> ValidationResult
    def check_piece_integrity(self, board_before: Any, board_after: Any) -> bool
    def detect_magical_pieces(self, board_before: Any, board_after: Any) -> List[str]
    def log_violation(self, violation: ValidationViolation) -> None
```

#### PieceTracker Class
```python
class PieceTracker:
    def __init__(self, game_type: str)
    def track_board_state(self, board: Any) -> Dict[str, int]
    def compare_states(self, before: Dict, after: Dict) -> PieceComparison
    def validate_piece_changes(self, comparison: PieceComparison, move: Any) -> bool
    def get_captured_pieces(self, before: Dict, after: Dict) -> List[str]
```

### 2. Progress Tracking System

#### ProgressManager Class
```python
class ProgressManager:
    def __init__(self, config: Dict)
    def initialize_cli_progress(self, total_generations: int) -> None
    def initialize_gui_progress(self, visualization_manager: VisualizationManager) -> None
    def update_generation_progress(self, current: int, metrics: Dict) -> None
    def update_phase_progress(self, phase: str, progress: float) -> None
    def display_generational_growth(self, historical_data: List[Dict]) -> None
```

#### CLIProgress Class
```python
class CLIProgress:
    def __init__(self, total_generations: int)
    def create_generation_bar(self) -> tqdm
    def create_phase_bar(self, phase_name: str, total_steps: int) -> tqdm
    def update_metrics(self, metrics: Dict) -> None
    def close_all_bars(self) -> None
```

#### GUIProgress Class
```python
class GUIProgress:
    def __init__(self, visualization_manager: VisualizationManager)
    def draw_generation_progress(self, screen: pygame.Surface, x: int, y: int) -> None
    def draw_phase_progress(self, screen: pygame.Surface, x: int, y: int) -> None
    def draw_growth_chart(self, screen: pygame.Surface, data: List[Dict]) -> None
    def adapt_to_window_size(self, width: int, height: int) -> None
```

### 3. Move History System

#### MoveLogger Class
```python
class MoveLogger:
    def __init__(self, backup_directory: str)
    def log_move(self, move_data: MoveData) -> None
    def start_game_log(self, game_info: GameInfo) -> str
    def end_game_log(self, game_id: str, result: GameResult) -> None
    def create_backup(self, game_id: str) -> str
```

#### BackupManager Class
```python
class BackupManager:
    def __init__(self, base_directory: str)
    def create_backup_structure(self) -> None
    def save_game_history(self, game_data: Dict, timestamp: str) -> str
    def save_generation_summary(self, generation: int, summary: Dict) -> str
    def cleanup_old_backups(self, retention_days: int) -> None
```

#### ScoreTracker Class
```python
class ScoreTracker:
    def __init__(self)
    def update_current_scores(self, player1_score: float, player2_score: float) -> None
    def record_game_result(self, result: GameResult) -> None
    def get_historical_trends(self, agent_name: str) -> List[Dict]
    def calculate_performance_metrics(self, timeframe: str) -> Dict
```

### 4. Enhanced Visualization Components

#### Enhanced VisualizationManager
```python
# New methods added to existing class
def display_captured_pieces(self, captured_white: List, captured_black: List, x: int, y: int) -> None
def display_progress_bars(self, progress_data: Dict) -> None
def display_score_panel(self, current_scores: Dict, historical: List) -> None
def handle_window_resize(self, new_width: int, new_height: int) -> None
def adapt_layout_to_size(self, width: int, height: int) -> Dict
```

#### CapturedPiecesRenderer
```python
class CapturedPiecesRenderer:
    def __init__(self, piece_size: int = 30)
    def draw_captured_area(self, screen: pygame.Surface, pieces: List, x: int, y: int, color: str) -> None
    def calculate_material_advantage(self, white_pieces: List, black_pieces: List) -> int
    def draw_advantage_indicator(self, screen: pygame.Surface, advantage: int, x: int, y: int) -> None
```

## Data Models

### ValidationResult
```python
@dataclass
class ValidationResult:
    is_valid: bool
    violations: List[str]
    magical_pieces: List[str]
    timestamp: datetime
    board_hash_before: str
    board_hash_after: str
```

### MoveData
```python
@dataclass
class MoveData:
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
```

### ProgressMetrics
```python
@dataclass
class ProgressMetrics:
    generation: int
    phase: str
    win_rates: Dict[str, float]
    training_loss: float
    games_played: int
    average_game_length: float
    skill_improvement: float
    timestamp: datetime
```

### GameResult
```python
@dataclass
class GameResult:
    game_id: str
    winner: str
    final_score: Dict[str, float]
    total_moves: int
    game_duration: float
    termination_reason: str
    captured_pieces: Dict[str, List[str]]
    final_board_state: str
```

## Error Handling

### Validation Error Handling
- **Magical Piece Detection**: Log violation, force AI to select alternative move, continue training
- **Invalid Move Attempts**: Reject move, request new move from AI, track violation statistics
- **Board State Corruption**: Restore from last valid state, log incident, continue with backup

### Progress Tracking Error Handling
- **CLI Progress Bar Failures**: Fall back to simple text updates, log error
- **GUI Rendering Issues**: Disable problematic visual elements, maintain core functionality
- **Metrics Calculation Errors**: Use default values, log calculation failures

### History Logging Error Handling
- **JSON Serialization Failures**: Use fallback serialization, log problematic data
- **Backup Storage Issues**: Try alternative storage locations, notify user of risks
- **File System Errors**: Implement retry logic, graceful degradation

### GUI Error Handling
- **Window Resize Issues**: Maintain minimum viable layout, log resize problems
- **Rendering Failures**: Skip problematic elements, maintain game visibility
- **Memory Issues**: Implement cleanup routines, reduce visual complexity if needed

## Testing Strategy

### Unit Testing
- **Move Validation**: Test magical piece detection with crafted board states
- **Progress Tracking**: Verify progress calculations and display accuracy
- **History Logging**: Test JSON serialization and backup creation
- **GUI Components**: Test rendering and resize behavior

### Integration Testing
- **End-to-End Validation**: Full game with validation enabled
- **Progress Integration**: Complete training cycle with progress tracking
- **History Persistence**: Multi-generation training with full logging
- **GUI Responsiveness**: Window resize and layout adaptation testing

### Performance Testing
- **Validation Overhead**: Measure impact on game performance
- **Progress Rendering**: Test GUI performance with complex progress displays
- **Logging Performance**: Measure JSON logging impact on training speed
- **Memory Usage**: Monitor memory consumption with all features enabled

### Compatibility Testing
- **Cross-Platform GUI**: Test window management on Windows, Mac, Linux
- **Different Screen Sizes**: Test layout adaptation across resolutions
- **CLI Environment**: Test progress bars in different terminal environments
- **File System**: Test backup creation across different file systems

## Implementation Phases

### Phase 1: Core Validation System
1. Implement MoveValidator and PieceTracker classes
2. Integrate validation hooks into BaseGame
3. Add violation logging and reporting
4. Test with existing chess and checkers games

### Phase 2: Progress Tracking Infrastructure
1. Create ProgressManager and CLI progress components
2. Integrate tqdm-based progress bars
3. Add progress metrics calculation
4. Test with training loop integration

### Phase 3: GUI Enhancements
1. Implement captured pieces display
2. Add GUI progress indicators
3. Enhance window resize handling
4. Test visual layout adaptation

### Phase 4: History and Backup System
1. Create move logging infrastructure
2. Implement JSON backup system
3. Add score tracking and analysis
4. Test data persistence and retrieval

### Phase 5: Integration and Polish
1. Integrate all components with LeagueManager
2. Add configuration options for all features
3. Implement comprehensive error handling
4. Performance optimization and testing

## Configuration Options

### Validation Configuration
```json
{
  "validation": {
    "enable_move_validation": true,
    "strict_piece_checking": true,
    "log_violations": true,
    "violation_log_path": "logs/violations.json"
  }
}
```

### Progress Configuration
```json
{
  "progress": {
    "enable_cli_progress": true,
    "enable_gui_progress": true,
    "update_frequency": 0.1,
    "show_detailed_metrics": true
  }
}
```

### History Configuration
```json
{
  "history": {
    "enable_move_logging": true,
    "backup_directory": "backups/",
    "backup_frequency": "per_game",
    "retention_days": 30,
    "compress_backups": true
  }
}
```

### GUI Configuration
```json
{
  "gui": {
    "adaptive_layout": true,
    "minimum_window_size": [800, 600],
    "show_captured_pieces": true,
    "progress_bar_style": "modern",
    "auto_resize_elements": true
  }
}
```