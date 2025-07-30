"""
Neural CheChe: AI vs AI Training System

A sophisticated AI training system that teaches neural networks to play both 
Chess and Checkers through self-play, strategic discussions, and competitive evolution.
"""

__version__ = "2.0.0"
__author__ = "Neural CheChe Team"

from .league import LeagueManager
from .config import Config, load_config, save_config
from .games import ChessGame, CheckersGame
from .core import GameNet, MCTS, SharedReplayBuffer
from .utils import safe_device, get_gpu_info

__all__ = [
    'LeagueManager',
    'Config', 'load_config', 'save_config',
    'ChessGame', 'CheckersGame',
    'GameNet', 'MCTS', 'SharedReplayBuffer',
    'safe_device', 'get_gpu_info'
]