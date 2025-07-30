"""
Move Logger - Comprehensive JSON logging of AI moves and decisions
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .data_models import MoveData, GameInfo, GameResult, HistoryEncoder


class MoveLogger:
    """Logs AI moves and decisions to JSON files for analysis"""
    
    def __init__(self, backup_directory: str = "move_history"):
        self.backup_directory = Path(backup_directory)
        self.current_games: Dict[str, GameInfo] = {}
        self.current_moves: Dict[str, List[MoveData]] = {}
        
        # Create directory structure
        self._create_directory_structure()
        
        # Statistics
        self.total_moves_logged = 0
        self.total_games_logged = 0
        
        print(f"📝 MoveLogger initialized with directory: {self.backup_directory}")
    
    def _create_directory_structure(self) -> None:
        """Create the backup directory structure"""
        try:
            # Main directories
            self.backup_directory.mkdir(parents=True, exist_ok=True)
            (self.backup_directory / "games").mkdir(exist_ok=True)
            (self.backup_directory / "generations").mkdir(exist_ok=True)
            (self.backup_directory / "daily").mkdir(exist_ok=True)
            (self.backup_directory / "summaries").mkdir(exist_ok=True)
            
            print(f"📁 Directory structure created at {self.backup_directory}")
            
        except Exception as e:
            print(f"⚠️ Failed to create directory structure: {e}")
    
    def start_game_log(self, game_info: GameInfo) -> str:
        """
        Start logging a new game
        
        Args:
            game_info: Information about the game to log
            
        Returns:
            Game ID for this logging session
        """
        try:
            game_id = game_info.game_id or str(uuid.uuid4())
            
            # Store game info
            self.current_games[game_id] = game_info
            self.current_moves[game_id] = []
            
            # Create game log file
            game_file = self.backup_directory / "games" / f"{game_id}.json"
            
            initial_data = {
                "game_info": game_info.to_dict(),
                "moves": [],
                "result": None,
                "created_at": datetime.now().isoformat(),
                "status": "in_progress"
            }
            
            with open(game_file, 'w') as f:
                json.dump(initial_data, f, indent=2, cls=HistoryEncoder)
            
            print(f"🎮 Started logging game {game_id} ({game_info.game_type})")
            return game_id
            
        except Exception as e:
            print(f"⚠️ Failed to start game log: {e}")
            return game_info.game_id or "error"
    
    def log_move(self, move_data: MoveData) -> None:
        """
        Log a single move
        
        Args:
            move_data: Complete move data to log
        """
        try:
            game_id = move_data.game_id
            
            if game_id not in self.current_games:
                print(f"⚠️ Game {game_id} not found, cannot log move")
                return
            
            # Add to current moves
            self.current_moves[game_id].append(move_data)
            self.total_moves_logged += 1
            
            # Update game file
            game_file = self.backup_directory / "games" / f"{game_id}.json"
            
            if game_file.exists():
                with open(game_file, 'r') as f:
                    game_data = json.load(f)
                
                # Add the new move
                game_data["moves"].append(move_data.to_dict())
                game_data["last_updated"] = datetime.now().isoformat()
                
                # Write back to file
                with open(game_file, 'w') as f:
                    json.dump(game_data, f, indent=2, cls=HistoryEncoder)
            
            # Log to console (optional, can be disabled for performance)
            if move_data.move_number % 10 == 0:  # Every 10th move
                print(f"📝 Logged move {move_data.move_number} for game {game_id[:8]}")
            
        except Exception as e:
            print(f"⚠️ Failed to log move: {e}")
    
    def end_game_log(self, game_id: str, result: GameResult) -> None:
        """
        End logging for a game and finalize the log
        
        Args:
            game_id: ID of the game to finalize
            result: Final game result
        """
        try:
            if game_id not in self.current_games:
                print(f"⚠️ Game {game_id} not found, cannot end log")
                return
            
            # Update game file with final result
            game_file = self.backup_directory / "games" / f"{game_id}.json"
            
            if game_file.exists():
                with open(game_file, 'r') as f:
                    game_data = json.load(f)
                
                # Add final result
                game_data["result"] = result.to_dict()
                game_data["status"] = "completed"
                game_data["completed_at"] = datetime.now().isoformat()
                
                # Add summary statistics
                moves = self.current_moves.get(game_id, [])
                game_data["summary"] = {
                    "total_moves": len(moves),
                    "average_thinking_time": sum(m.thinking_time for m in moves) / max(1, len(moves)),
                    "total_captured_pieces": sum(len(m.captured_pieces) for m in moves),
                    "validation_violations": sum(1 for m in moves if not m.is_valid)
                }
                
                # Write final version
                with open(game_file, 'w') as f:
                    json.dump(game_data, f, indent=2, cls=HistoryEncoder)
            
            # Clean up current game data
            del self.current_games[game_id]
            del self.current_moves[game_id]
            
            self.total_games_logged += 1
            
            print(f"🏁 Completed logging for game {game_id} - {result.winner} won in {result.total_moves} moves")
            
        except Exception as e:
            print(f"⚠️ Failed to end game log: {e}")
    
    def create_backup(self, game_id: str) -> str:
        """
        Create a backup of a specific game
        
        Args:
            game_id: ID of the game to backup
            
        Returns:
            Path to the backup file
        """
        try:
            game_file = self.backup_directory / "games" / f"{game_id}.json"
            
            if not game_file.exists():
                print(f"⚠️ Game file {game_id} not found for backup")
                return ""
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_directory / "daily" / f"{game_id}_{timestamp}.json"
            
            # Copy the file
            with open(game_file, 'r') as src:
                game_data = json.load(src)
            
            with open(backup_file, 'w') as dst:
                json.dump(game_data, dst, indent=2, cls=HistoryEncoder)
            
            print(f"💾 Created backup: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            print(f"⚠️ Failed to create backup: {e}")
            return ""
    
    def get_game_history(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete history for a specific game
        
        Args:
            game_id: ID of the game
            
        Returns:
            Complete game data or None if not found
        """
        try:
            game_file = self.backup_directory / "games" / f"{game_id}.json"
            
            if game_file.exists():
                with open(game_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Failed to get game history: {e}")
            return None
    
    def get_recent_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent games
        
        Args:
            limit: Maximum number of games to return
            
        Returns:
            List of recent game data
        """
        try:
            games_dir = self.backup_directory / "games"
            game_files = list(games_dir.glob("*.json"))
            
            # Sort by modification time (most recent first)
            game_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            recent_games = []
            for game_file in game_files[:limit]:
                try:
                    with open(game_file, 'r') as f:
                        game_data = json.load(f)
                        recent_games.append(game_data)
                except Exception as e:
                    print(f"⚠️ Error reading {game_file}: {e}")
            
            return recent_games
            
        except Exception as e:
            print(f"⚠️ Failed to get recent games: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        try:
            games_dir = self.backup_directory / "games"
            total_files = len(list(games_dir.glob("*.json"))) if games_dir.exists() else 0
            
            return {
                "total_moves_logged": self.total_moves_logged,
                "total_games_logged": self.total_games_logged,
                "total_game_files": total_files,
                "active_games": len(self.current_games),
                "backup_directory": str(self.backup_directory),
                "directory_size_mb": self._get_directory_size() / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"⚠️ Error getting statistics: {e}")
            return {"error": str(e)}
    
    def _get_directory_size(self) -> int:
        """Get total size of backup directory in bytes"""
        try:
            total_size = 0
            for file_path in self.backup_directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> None:
        """
        Clean up old backup files
        
        Args:
            days_to_keep: Number of days to keep files
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cleaned_count = 0
            for backup_dir in ["daily", "games"]:
                dir_path = self.backup_directory / backup_dir
                if dir_path.exists():
                    for file_path in dir_path.glob("*.json"):
                        if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                            file_path.unlink()
                            cleaned_count += 1
            
            print(f"🧹 Cleaned up {cleaned_count} old backup files")
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Finalize any remaining games
        for game_id in list(self.current_games.keys()):
            print(f"⚠️ Finalizing incomplete game {game_id}")
            # Create a default result for incomplete games
            result = GameResult(
                game_id=game_id,
                winner="Incomplete",
                final_score={},
                total_moves=len(self.current_moves.get(game_id, [])),
                game_duration=0.0,
                termination_reason="System shutdown",
                captured_pieces={},
                final_board_state="Unknown",
                end_time=datetime.now()
            )
            self.end_game_log(game_id, result)