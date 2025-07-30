"""
Backup Manager - Handles data persistence and backup organization
"""

import json
import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from .data_models import GenerationSummary, HistoryEncoder


class BackupManager:
    """Manages backup creation, organization, and cleanup"""
    
    def __init__(self, base_directory: str = "backups"):
        self.base_directory = Path(base_directory)
        self.compress_backups = True
        self.retention_days = 30
        
        # Create backup structure
        self.create_backup_structure()
        
        print(f"💾 BackupManager initialized with directory: {self.base_directory}")
    
    def create_backup_structure(self) -> None:
        """Create organized backup directory structure"""
        try:
            # Main backup directories
            directories = [
                "generations",      # Per-generation summaries
                "daily",           # Daily backups
                "weekly",          # Weekly archives
                "models",          # Model checkpoints
                "logs",            # Training logs
                "analysis",        # Analysis reports
                "compressed"       # Compressed archives
            ]
            
            self.base_directory.mkdir(parents=True, exist_ok=True)
            
            for directory in directories:
                (self.base_directory / directory).mkdir(exist_ok=True)
            
            # Create index file
            index_file = self.base_directory / "backup_index.json"
            if not index_file.exists():
                initial_index = {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_backups": 0,
                    "generations_backed_up": [],
                    "backup_structure": directories
                }
                
                with open(index_file, 'w') as f:
                    json.dump(initial_index, f, indent=2)
            
            print(f"📁 Backup structure created with {len(directories)} directories")
            
        except Exception as e:
            print(f"⚠️ Failed to create backup structure: {e}")
    
    def save_game_history(self, game_data: Dict[str, Any], timestamp: str) -> str:
        """
        Save game history with timestamp
        
        Args:
            game_data: Complete game data to backup
            timestamp: Timestamp string for the backup
            
        Returns:
            Path to the saved backup file
        """
        try:
            # Create filename
            game_id = game_data.get('game_info', {}).get('game_id', 'unknown')
            filename = f"game_{game_id}_{timestamp}.json"
            
            # Determine backup location (daily for now)
            backup_file = self.base_directory / "daily" / filename
            
            # Add backup metadata
            backup_data = {
                "backup_info": {
                    "created_at": datetime.now().isoformat(),
                    "backup_type": "game_history",
                    "original_game_id": game_id,
                    "timestamp": timestamp
                },
                "game_data": game_data
            }
            
            # Save to file
            if self.compress_backups:
                # Save as compressed JSON
                compressed_file = backup_file.with_suffix('.json.gz')
                with gzip.open(compressed_file, 'wt', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, cls=HistoryEncoder)
                backup_path = str(compressed_file)
            else:
                # Save as regular JSON
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, cls=HistoryEncoder)
                backup_path = str(backup_file)
            
            # Update index
            self._update_backup_index("game_history", backup_path)
            
            print(f"💾 Saved game history backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"⚠️ Failed to save game history: {e}")
            return ""
    
    def save_generation_summary(self, generation: int, summary: Dict[str, Any]) -> str:
        """
        Save generation training summary
        
        Args:
            generation: Generation number
            summary: Summary data to backup
            
        Returns:
            Path to the saved summary file
        """
        try:
            # Create generation summary
            generation_summary = GenerationSummary(
                generation=generation,
                start_time=datetime.fromisoformat(summary.get('start_time', datetime.now().isoformat())),
                end_time=datetime.now(),
                total_games=summary.get('total_games', 0),
                total_moves=summary.get('total_moves', 0),
                agents_trained=summary.get('agents_trained', []),
                champion_changes=summary.get('champion_changes', []),
                performance_metrics=summary.get('performance_metrics', {}),
                validation_summary=summary.get('validation_summary', {}),
                backup_files=summary.get('backup_files', [])
            )
            
            # Save generation summary
            filename = f"generation_{generation:04d}_summary.json"
            summary_file = self.base_directory / "generations" / filename
            
            summary_data = {
                "backup_info": {
                    "created_at": datetime.now().isoformat(),
                    "backup_type": "generation_summary",
                    "generation": generation
                },
                "summary": generation_summary.to_dict()
            }
            
            if self.compress_backups:
                compressed_file = summary_file.with_suffix('.json.gz')
                with gzip.open(compressed_file, 'wt', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=2, cls=HistoryEncoder)
                backup_path = str(compressed_file)
            else:
                with open(summary_file, 'w') as f:
                    json.dump(summary_data, f, indent=2, cls=HistoryEncoder)
                backup_path = str(summary_file)
            
            # Update index
            self._update_backup_index("generation_summary", backup_path, generation)
            
            print(f"📊 Saved generation {generation} summary: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"⚠️ Failed to save generation summary: {e}")
            return ""
    
    def create_weekly_archive(self) -> str:
        """
        Create weekly archive of daily backups
        
        Returns:
            Path to the created archive
        """
        try:
            # Get current week info
            now = datetime.now()
            week_start = now - timedelta(days=now.weekday())
            week_str = week_start.strftime("%Y_W%U")
            
            archive_name = f"weekly_archive_{week_str}.tar.gz"
            archive_path = self.base_directory / "weekly" / archive_name
            
            # Create archive of daily backups
            daily_dir = self.base_directory / "daily"
            
            if daily_dir.exists() and any(daily_dir.iterdir()):
                import tarfile
                
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(daily_dir, arcname="daily_backups")
                
                print(f"📦 Created weekly archive: {archive_path}")
                
                # Clean up daily files after archiving (optional)
                # self._cleanup_daily_after_archive(daily_dir)
                
                return str(archive_path)
            else:
                print("⚠️ No daily backups found to archive")
                return ""
            
        except Exception as e:
            print(f"⚠️ Failed to create weekly archive: {e}")
            return ""
    
    def backup_model_checkpoint(self, model_path: str, generation: int, agent_name: str) -> str:
        """
        Backup a model checkpoint
        
        Args:
            model_path: Path to the model file
            generation: Generation number
            agent_name: Name of the agent
            
        Returns:
            Path to the backup location
        """
        try:
            if not os.path.exists(model_path):
                print(f"⚠️ Model file not found: {model_path}")
                return ""
            
            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{agent_name}_gen_{generation:04d}_{timestamp}.pth"
            backup_path = self.base_directory / "models" / backup_filename
            
            # Copy the model file
            shutil.copy2(model_path, backup_path)
            
            # Create metadata file
            metadata = {
                "original_path": model_path,
                "agent_name": agent_name,
                "generation": generation,
                "backup_time": datetime.now().isoformat(),
                "file_size": os.path.getsize(model_path)
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"🤖 Backed up model: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"⚠️ Failed to backup model: {e}")
            return ""
    
    def cleanup_old_backups(self, retention_days: int = None) -> None:
        """
        Clean up old backup files
        
        Args:
            retention_days: Number of days to keep backups (uses instance default if None)
        """
        try:
            retention_days = retention_days or self.retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            cleaned_files = 0
            total_size_freed = 0
            
            # Clean up daily backups
            daily_dir = self.base_directory / "daily"
            if daily_dir.exists():
                for file_path in daily_dir.iterdir():
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files += 1
                            total_size_freed += file_size
            
            # Clean up old model backups (keep more recent ones)
            models_dir = self.base_directory / "models"
            if models_dir.exists():
                model_cutoff = datetime.now() - timedelta(days=retention_days * 2)  # Keep models longer
                for file_path in models_dir.iterdir():
                    if file_path.suffix in ['.pth', '.json'] and file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < model_cutoff:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files += 1
                            total_size_freed += file_size
            
            size_mb = total_size_freed / (1024 * 1024)
            print(f"🧹 Cleaned up {cleaned_files} old backup files, freed {size_mb:.1f}MB")
            
        except Exception as e:
            print(f"⚠️ Error during backup cleanup: {e}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics"""
        try:
            stats = {
                "backup_directory": str(self.base_directory),
                "total_size_mb": 0,
                "file_counts": {},
                "oldest_backup": None,
                "newest_backup": None,
                "compression_enabled": self.compress_backups,
                "retention_days": self.retention_days
            }
            
            # Analyze each backup directory
            for subdir in ["daily", "weekly", "generations", "models"]:
                dir_path = self.base_directory / subdir
                if dir_path.exists():
                    files = list(dir_path.iterdir())
                    stats["file_counts"][subdir] = len([f for f in files if f.is_file()])
                    
                    # Calculate size
                    for file_path in files:
                        if file_path.is_file():
                            stats["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
            
            # Get backup index info
            index_file = self.base_directory / "backup_index.json"
            if index_file.exists():
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                    stats["total_backups"] = index_data.get("total_backups", 0)
                    stats["generations_backed_up"] = len(index_data.get("generations_backed_up", []))
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error getting backup statistics: {e}")
            return {"error": str(e)}
    
    def restore_game_backup(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        Restore a game backup
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            Restored game data or None if failed
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                print(f"⚠️ Backup file not found: {backup_path}")
                return None
            
            # Load backup data
            if backup_file.suffix == '.gz':
                with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
            
            print(f"📥 Restored backup from: {backup_path}")
            return backup_data.get("game_data", backup_data)
            
        except Exception as e:
            print(f"⚠️ Failed to restore backup: {e}")
            return None
    
    def _update_backup_index(self, backup_type: str, backup_path: str, generation: int = None) -> None:
        """Update the backup index with new backup information"""
        try:
            index_file = self.base_directory / "backup_index.json"
            
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
            else:
                index_data = {
                    "created_at": datetime.now().isoformat(),
                    "total_backups": 0,
                    "generations_backed_up": [],
                    "backup_types": {}
                }
            
            # Update index
            index_data["last_updated"] = datetime.now().isoformat()
            index_data["total_backups"] = index_data.get("total_backups", 0) + 1
            
            if backup_type not in index_data.get("backup_types", {}):
                index_data.setdefault("backup_types", {})[backup_type] = []
            
            index_data["backup_types"][backup_type].append({
                "path": backup_path,
                "created_at": datetime.now().isoformat(),
                "generation": generation
            })
            
            if generation is not None:
                generations = index_data.setdefault("generations_backed_up", [])
                if generation not in generations:
                    generations.append(generation)
                    generations.sort()
            
            # Save updated index
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
        except Exception as e:
            print(f"⚠️ Failed to update backup index: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Perform any final cleanup
        print("💾 BackupManager cleanup completed")