"""
Configuration for the move history and backup system
"""

from typing import Dict, Any
import os
from .base_config import BaseConfig


class HistoryConfig(BaseConfig):
    """Configuration for move history and backup system"""
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default history configuration"""
        return {
            'enable_move_logging': True,
            'backup_directory': 'move_history/',
            'backup_frequency': 'per_game',
            'retention_days': 30,
            'compress_backups': False,
            'detailed_logging': True,
            'log_board_states': True,
            'log_policy_distributions': True,
            'log_evaluation_scores': True,
            'max_log_file_size': 100,  # MB
            'backup_format': 'json',
            'enable_incremental_backups': True,
            'backup_compression_level': 6,
            'auto_cleanup_enabled': True
        }
    
    def _get_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration fields"""
        return {
            'enable_move_logging': {
                'type': bool,
                'required': True
            },
            'backup_directory': {
                'type': str,
                'required': True,
                'validator': lambda x: len(x) > 0,
                'validator_message': 'Backup directory cannot be empty'
            },
            'backup_frequency': {
                'type': str,
                'required': True,
                'choices': ['per_move', 'per_game', 'per_generation', 'manual']
            },
            'retention_days': {
                'type': int,
                'required': True,
                'min_value': 1,
                'max_value': 365
            },
            'compress_backups': {
                'type': bool,
                'required': True
            },
            'detailed_logging': {
                'type': bool,
                'required': True
            },
            'log_board_states': {
                'type': bool,
                'required': True
            },
            'log_policy_distributions': {
                'type': bool,
                'required': True
            },
            'log_evaluation_scores': {
                'type': bool,
                'required': True
            },
            'max_log_file_size': {
                'type': int,
                'required': True,
                'min_value': 1,
                'max_value': 1000
            },
            'backup_format': {
                'type': str,
                'required': True,
                'choices': ['json', 'msgpack', 'pickle']
            },
            'enable_incremental_backups': {
                'type': bool,
                'required': True
            },
            'backup_compression_level': {
                'type': int,
                'required': True,
                'min_value': 1,
                'max_value': 9
            },
            'auto_cleanup_enabled': {
                'type': bool,
                'required': True
            }
        }
    
    def get_documentation(self) -> Dict[str, str]:
        """Get documentation for history configuration fields"""
        return {
            'enable_move_logging': 'Enable comprehensive move logging to JSON files',
            'backup_directory': 'Directory where move history and backups are stored',
            'backup_frequency': 'When to create backups (per_move, per_game, per_generation, manual)',
            'retention_days': 'Number of days to keep backup files before cleanup',
            'compress_backups': 'Compress backup files to save disk space',
            'detailed_logging': 'Include detailed information in move logs',
            'log_board_states': 'Log complete board states before and after moves',
            'log_policy_distributions': 'Log AI policy distributions for move analysis',
            'log_evaluation_scores': 'Log position evaluation scores',
            'max_log_file_size': 'Maximum size (MB) for individual log files before rotation',
            'backup_format': 'Format for backup files (json, msgpack, pickle)',
            'enable_incremental_backups': 'Create incremental backups to save space',
            'backup_compression_level': 'Compression level (1-9) when compression is enabled',
            'auto_cleanup_enabled': 'Automatically clean up old backup files'
        }
    
    def ensure_backup_directory(self) -> None:
        """Ensure the backup directory exists"""
        backup_dir = self.get('backup_directory')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['daily', 'games', 'generations', 'summaries']
        for subdir in subdirs:
            os.makedirs(os.path.join(backup_dir, subdir), exist_ok=True)
    
    def is_logging_enabled(self) -> bool:
        """Check if move logging is enabled"""
        return self.get('enable_move_logging', True)
    
    def should_compress_backups(self) -> bool:
        """Check if backups should be compressed"""
        return self.get('compress_backups', False)
    
    def get_backup_frequency(self) -> str:
        """Get the backup frequency setting"""
        return self.get('backup_frequency', 'per_game')
    
    def get_retention_period(self) -> int:
        """Get the backup retention period in days"""
        return self.get('retention_days', 30)
    
    def get_max_file_size_bytes(self) -> int:
        """Get maximum log file size in bytes"""
        return self.get('max_log_file_size', 100) * 1024 * 1024  # Convert MB to bytes
    
    def should_log_detailed_info(self) -> bool:
        """Check if detailed logging is enabled"""
        return self.get('detailed_logging', True)