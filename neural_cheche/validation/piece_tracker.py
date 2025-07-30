"""
Piece tracking system for board state monitoring
"""

from typing import Any, Dict, List
from .data_models import PieceComparison


class PieceTracker:
    """Tracks piece states and validates transitions between board states"""
    
    def __init__(self, game_type: str):
        self.game_type = game_type.lower()
        
        # Game-specific piece mappings
        if self.game_type == "chess":
            self.piece_symbols = {
                'p': 'black_pawn', 'r': 'black_rook', 'n': 'black_knight',
                'b': 'black_bishop', 'q': 'black_queen', 'k': 'black_king',
                'P': 'white_pawn', 'R': 'white_rook', 'N': 'white_knight',
                'B': 'white_bishop', 'Q': 'white_queen', 'K': 'white_king'
            }
        elif self.game_type == "checkers":
            self.piece_symbols = {
                'b': 'black_man', 'B': 'black_king',
                'w': 'white_man', 'W': 'white_king'
            }
        else:
            self.piece_symbols = {}
    
    def track_board_state(self, board: Any) -> Dict[str, int]:
        """
        Extract piece counts from board state
        
        Args:
            board: Game board object
            
        Returns:
            Dictionary mapping piece types to counts
        """
        piece_counts = {}
        
        try:
            if self.game_type == "chess":
                piece_counts = self._track_chess_board(board)
            elif self.game_type == "checkers":
                piece_counts = self._track_checkers_board(board)
            else:
                # Generic tracking - convert board to string and count characters
                piece_counts = self._track_generic_board(board)
            
            return piece_counts
            
        except Exception as e:
            print(f"Error tracking board state: {e}")
            return {}
    
    def compare_states(self, before: Dict[str, int], after: Dict[str, int]) -> PieceComparison:
        """
        Compare two board states and identify changes
        
        Args:
            before: Piece counts before move
            after: Piece counts after move
            
        Returns:
            PieceComparison object with detailed analysis
        """
        pieces_added = {}
        pieces_removed = {}
        pieces_moved = []
        captured_pieces = []
        violation_reasons = []
        
        # Get all piece types from both states
        all_pieces = set(before.keys()) | set(after.keys())
        
        for piece_type in all_pieces:
            before_count = before.get(piece_type, 0)
            after_count = after.get(piece_type, 0)
            
            if after_count > before_count:
                # Pieces were added
                pieces_added[piece_type] = after_count - before_count
            elif before_count > after_count:
                # Pieces were removed (captured)
                pieces_removed[piece_type] = before_count - after_count
                captured_pieces.extend([piece_type] * (before_count - after_count))
        
        # Check for violations
        is_valid_transition = True
        
        # Check for illegal piece creation
        for piece_type, count in pieces_added.items():
            if not self._is_legal_piece_creation(piece_type, count, before, after):
                is_valid_transition = False
                violation_reasons.append(f"Illegal creation of {count} {piece_type}")
        
        # Check for impossible piece removal
        for piece_type, count in pieces_removed.items():
            if before.get(piece_type, 0) < count:
                is_valid_transition = False
                violation_reasons.append(f"Attempted to remove {count} {piece_type} but only {before.get(piece_type, 0)} existed")
        
        return PieceComparison(
            pieces_added=pieces_added,
            pieces_removed=pieces_removed,
            pieces_moved=pieces_moved,
            captured_pieces=captured_pieces,
            is_valid_transition=is_valid_transition,
            violation_reasons=violation_reasons
        )
    
    def validate_piece_changes(self, comparison: PieceComparison, move: Any) -> bool:
        """
        Validate that piece changes are legal for the given move
        
        Args:
            comparison: PieceComparison object
            move: The move that was made
            
        Returns:
            True if changes are valid
        """
        # Basic validation - no magical pieces should be created
        if comparison.has_magical_pieces():
            return False
        
        # Game-specific validation
        if self.game_type == "chess":
            return self._validate_chess_changes(comparison, move)
        elif self.game_type == "checkers":
            return self._validate_checkers_changes(comparison, move)
        
        # Default validation - only allow piece removal (captures)
        return len(comparison.pieces_added) == 0
    
    def get_captured_pieces(self, before: Dict[str, int], after: Dict[str, int]) -> List[str]:
        """
        Get list of pieces that were captured
        
        Args:
            before: Piece counts before move
            after: Piece counts after move
            
        Returns:
            List of captured piece types
        """
        captured = []
        
        for piece_type in before:
            before_count = before.get(piece_type, 0)
            after_count = after.get(piece_type, 0)
            
            if before_count > after_count:
                # This piece type was captured
                captured.extend([piece_type] * (before_count - after_count))
        
        return captured
    
    def _track_chess_board(self, board) -> Dict[str, int]:
        """Track pieces on a chess board"""
        piece_counts = {}
        
        try:
            # If using python-chess library
            if hasattr(board, 'piece_at'):
                import chess
                for square in chess.SQUARES:
                    piece = board.piece_at(square)
                    if piece:
                        piece_key = piece.symbol()
                        piece_name = self.piece_symbols.get(piece_key, piece_key)
                        piece_counts[piece_name] = piece_counts.get(piece_name, 0) + 1
            else:
                # Generic string-based tracking
                board_str = str(board)
                for char in board_str:
                    if char in self.piece_symbols:
                        piece_name = self.piece_symbols[char]
                        piece_counts[piece_name] = piece_counts.get(piece_name, 0) + 1
        
        except Exception as e:
            print(f"Error tracking chess board: {e}")
        
        return piece_counts
    
    def _track_checkers_board(self, board) -> Dict[str, int]:
        """Track pieces on a checkers board"""
        piece_counts = {}
        
        try:
            # If using draughts library
            if hasattr(board, 'pieces'):
                # Count pieces by type and color
                for piece in board.pieces:
                    piece_key = self._get_checkers_piece_key(piece)
                    piece_name = self.piece_symbols.get(piece_key, piece_key)
                    piece_counts[piece_name] = piece_counts.get(piece_name, 0) + 1
            else:
                # Generic string-based tracking
                board_str = str(board)
                for char in board_str:
                    if char in self.piece_symbols:
                        piece_name = self.piece_symbols[char]
                        piece_counts[piece_name] = piece_counts.get(piece_name, 0) + 1
        
        except Exception as e:
            print(f"Error tracking checkers board: {e}")
        
        return piece_counts
    
    def _track_generic_board(self, board) -> Dict[str, int]:
        """Generic board tracking by counting characters"""
        piece_counts = {}
        board_str = str(board)
        
        for char in board_str:
            if char.isalpha():  # Assume letters represent pieces
                piece_counts[char] = piece_counts.get(char, 0) + 1
        
        return piece_counts
    
    def _get_checkers_piece_key(self, piece) -> str:
        """Get the key for a checkers piece"""
        try:
            # This depends on the specific checkers library implementation
            if hasattr(piece, 'color') and hasattr(piece, 'king'):
                if piece.color == 'black':
                    return 'B' if piece.king else 'b'
                else:
                    return 'W' if piece.king else 'w'
            else:
                return str(piece)
        except Exception:
            return str(piece)
    
    def _is_legal_piece_creation(self, piece_type: str, count: int, 
                                before: Dict[str, int], after: Dict[str, int]) -> bool:
        """
        Check if piece creation is legal (e.g., pawn promotion)
        """
        if self.game_type == "chess":
            # In chess, only pawn promotion is legal piece creation
            if "queen" in piece_type.lower() or "rook" in piece_type.lower() or \
               "bishop" in piece_type.lower() or "knight" in piece_type.lower():
                # Check if corresponding pawns were removed
                pawn_type = "white_pawn" if "white" in piece_type else "black_pawn"
                pawns_removed = before.get(pawn_type, 0) - after.get(pawn_type, 0)
                return pawns_removed >= count
        
        elif self.game_type == "checkers":
            # In checkers, men can be promoted to kings
            if "king" in piece_type.lower():
                # Check if corresponding men were removed
                man_type = piece_type.replace("king", "man")
                men_removed = before.get(man_type, 0) - after.get(man_type, 0)
                return men_removed >= count
        
        # By default, no piece creation is legal
        return False
    
    def _validate_chess_changes(self, comparison: PieceComparison, move: Any) -> bool:
        """Validate chess-specific piece changes"""
        # Allow pawn promotion
        for piece_type in comparison.pieces_added:
            if not self._is_legal_piece_creation(piece_type, 
                                               comparison.pieces_added[piece_type],
                                               {}, {}):  # We already checked this in comparison
                return False
        
        return True
    
    def _validate_checkers_changes(self, comparison: PieceComparison, move: Any) -> bool:
        """Validate checkers-specific piece changes"""
        # Allow king promotion
        for piece_type in comparison.pieces_added:
            if not self._is_legal_piece_creation(piece_type,
                                               comparison.pieces_added[piece_type],
                                               {}, {}):  # We already checked this in comparison
                return False
        
        return True