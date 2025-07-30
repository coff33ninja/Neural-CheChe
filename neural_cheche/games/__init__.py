"""
Games module for Neural CheChe
Provides game implementations and interfaces
"""

from .base_game import BaseGame
from .chess.chess_game import ChessGame
from .checkers.checkers_game import CheckersGame

__all__ = ['BaseGame', 'ChessGame', 'CheckersGame']