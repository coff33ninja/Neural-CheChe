"""
Abstract base class for all games in Neural CheChe
Defines the interface that all games must implement
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ..error_handling import ErrorHandler, ErrorCategory, ErrorSeverity
from ..error_handling.decorators import graceful_degradation


class BaseGame(ABC):
    """Abstract base class for all games"""

    def __init__(self):
        self.name = self.__class__.__name__.lower().replace("game", "")
        self.error_handler = ErrorHandler()

    @abstractmethod
    def create_board(self):
        """Create a new game board in starting position"""
        pass

    @abstractmethod
    def get_legal_moves(self, board):
        """Get all legal moves for the current position"""
        pass

    @abstractmethod
    def make_move(self, board, move):
        """Make a move on the board (modifies board in place)"""
        pass

    @abstractmethod
    def is_game_over(self, board):
        """Check if the game is over"""
        pass

    @abstractmethod
    def get_winner(self, board):
        """Get the winner (1 for player 1, -1 for player 2, 0 for draw)"""
        pass

    @abstractmethod
    def get_current_player(self, board):
        """Get the current player (1 or -1)"""
        pass

    @abstractmethod
    def board_to_tensor(self, board, history=None):
        """Convert board state to neural network input tensor"""
        pass

    @abstractmethod
    def get_reward(self, board):
        """Get reward for current position (-1 to 1)"""
        pass

    @abstractmethod
    def copy_board(self, board):
        """Create a deep copy of the board"""
        pass

    @abstractmethod
    def get_board_string(self, board):
        """Get string representation of board for debugging"""
        pass

    def get_action_size(self):
        """Get the number of possible actions for this game"""
        return getattr(self, "action_size", 4096)  # Default fallback

    def get_board_size(self):
        """Get the board dimensions (height, width)"""
        return (8, 8)  # Standard for chess and checkers

    # Validation hooks - can be overridden by specific games
    @graceful_degradation(
        fallback_value=True, log_errors=True, component="validate_move_hook"
    )
    def validate_move_hook(
        self, board_before: Any, board_after: Any, move: Any
    ) -> bool:
        """
        Hook for custom move validation logic

        Args:
            board_before: Board state before the move
            board_after: Board state after the move
            move: The move that was made

        Returns:
            True if move is valid, False otherwise
        """
        try:
            # Default implementation - assume all moves are valid
            # Specific games can override this for custom validation
            return True
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM,
                component=f"BaseGame_{self.name}",
                context={"operation": "validate_move_hook"},
            )
            return True

    @graceful_degradation(
        fallback_value=True, log_errors=True, component="pre_move_validation"
    )
    def pre_move_validation(self, board: Any, move: Any) -> bool:
        """
        Validate move before it's executed

        Args:
            board: Current board state
            move: Move to validate

        Returns:
            True if move can be executed
        """
        try:
            # Default implementation - assume all moves are valid
            # Specific games can override this for custom validation
            return True
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM,
                component=f"BaseGame_{self.name}",
                context={"operation": "pre_move_validation"},
            )
            return True

    @graceful_degradation(
        fallback_value=True, log_errors=True, component="post_move_validation"
    )
    def post_move_validation(
        self, board_before: Any, board_after: Any, move: Any
    ) -> bool:
        """
        Validate move after it's executed

        Args:
            board_before: Board state before the move
            board_after: Board state after the move
            move: The move that was made

        Returns:
            True if move was valid, False otherwise
        """
        try:
            # Default implementation - use the move validation hook
            return self.validate_move_hook(board_before, board_after, move)
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM,
                component=f"BaseGame_{self.name}",
                context={"operation": "post_move_validation"},
            )
            return True

    @graceful_degradation(
        fallback_value={}, log_errors=True, component="get_piece_state"
    )
    def get_piece_state(self, board: Any) -> Dict[str, Any]:
        """
        Extract piece state information from board for validation

        Args:
            board: Current board state

        Returns:
            Dictionary containing piece state information
        """
        try:
            # Default implementation - return basic board information
            # Specific games should override this to provide detailed piece information
            return {
                "board_string": str(board),
                "current_player": (
                    self.get_current_player(board)
                    if hasattr(self, "get_current_player")
                    else 1
                ),
                "game_over": (
                    self.is_game_over(board) if hasattr(self, "is_game_over") else False
                ),
            }
        except Exception as e:
            self.error_handler.handle_error(
                error=e,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.LOW,
                component=f"BaseGame_{self.name}",
                context={"operation": "get_piece_state"},
            )
            return {}

    def get_captured_pieces_from_move(
        self, board_before: Any, board_after: Any, move: Any
    ) -> List[str]:
        """
        Determine what pieces were captured in a move

        Args:
            board_before: Board state before move
            board_after: Board state after move
            move: The move that was made

        Returns:
            List of captured piece descriptions
        """
        # Default implementation - no pieces captured
        # Specific games should override this
        return []
