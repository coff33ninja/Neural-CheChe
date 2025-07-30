"""
Chess game implementation using python-chess
"""

import chess
import numpy as np
import torch
from typing import Any, List, Dict
from ..base_game import BaseGame


class ChessGame(BaseGame):
    """Chess game implementation"""
    
    def __init__(self):
        super().__init__()
        self.action_size = 4672  # Standard chess action space
    
    def create_board(self):
        """Create a new chess board"""
        return chess.Board()
    
    def get_legal_moves(self, board):
        """Get all legal moves"""
        return list(board.legal_moves)
    
    def make_move(self, board, move):
        """Make a move on the board with validation"""
        # Store board state before move for validation
        board_before = board.copy()
        
        # Execute the move
        board.push(move)
        
        # Perform post-move validation
        if not self.post_move_validation(board_before, board, move):
            # If validation fails, undo the move
            board.pop()
            raise ValueError(f"Invalid move detected: {move}")
        
        return True
    
    def is_game_over(self, board):
        """Check if game is over"""
        return board.is_game_over()
    
    def get_winner(self, board):
        """Get winner: 1 for white, -1 for black, 0 for draw"""
        if board.is_checkmate():
            return -1 if board.turn == chess.WHITE else 1
        return 0  # Draw or ongoing game
    
    def get_current_player(self, board):
        """Get current player: 1 for white, -1 for black"""
        return 1 if board.turn == chess.WHITE else -1
    
    def copy_board(self, board):
        """Create a deep copy of the board"""
        return board.copy()
    
    def get_board_string(self, board):
        """Get string representation"""
        return str(board)
    
    def board_to_tensor(self, board, history=None, device=None):
        """Convert board to neural network input tensor"""
        if history is None:
            history = []
        
        planes = []
        
        # Create 8 historical planes (current + 7 previous positions)
        for i in range(8):
            if i == 0:
                state = board
            elif i <= len(history):
                state = history[-i]
            else:
                state = board  # Pad with current if not enough history
            
            plane = np.zeros((14, 8, 8))
            
            # Encode pieces (12 piece types + turn + move count)
            for sq in range(64):
                piece = state.piece_at(sq)
                if piece:
                    row, col = 7 - sq // 8, sq % 8
                    piece_idx = {"p": 0, "n": 1, "b": 2, "r": 3, "q": 4, "k": 5}[
                        piece.symbol().lower()
                    ]
                    if piece.color == chess.BLACK:
                        piece_idx += 6
                    plane[piece_idx, row, col] = 1
            
            # Turn and move count planes
            plane[12] = 1 if state.turn == chess.WHITE else 0
            plane[13] = state.fullmove_number / 100
            
            planes.append(plane)
        
        tensor = torch.tensor(np.concatenate(planes, axis=0), dtype=torch.float32)
        if device is not None:
            tensor = tensor.to(device)
        return tensor
    
    def get_reward(self, board):
        """Enhanced reward function with endgame penalties"""
        if board.is_checkmate():
            return -1 if board.turn == chess.WHITE else 1
        
        # Penalty for stalemate when winning
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            material = self._calculate_material_advantage(board)
            if abs(material) > 5:  # Significant advantage
                penalty = -0.7 if material > 0 else 0.7
                return penalty if board.turn == chess.WHITE else -penalty
            return 0
        
        # Penalty for repetition when winning
        if board.is_fivefold_repetition():
            material = self._calculate_material_advantage(board)
            if abs(material) > 3:
                penalty = -0.5 if material > 0 else 0.5
                return penalty if board.turn == chess.WHITE else -penalty
            return -0.2 if board.turn == chess.WHITE else 0.2
        
        return 0
    
    def _calculate_material_advantage(self, board):
        """Calculate material advantage for white"""
        piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9
        }
        
        material = 0
        for piece_type, value in piece_values.items():
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            material += (white_count - black_count) * value
        
        return material
    
    # Chess-specific validation methods
    def validate_move_hook(self, board_before: Any, board_after: Any, move: Any) -> bool:
        """
        Chess-specific move validation
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            move: The move that was made
            
        Returns:
            True if move is valid for chess
        """
        try:
            # Check that the move is legal according to chess rules
            if move not in board_before.legal_moves:
                return False
            
            # Validate piece integrity - no magical pieces created
            return self._validate_chess_piece_integrity(board_before, board_after, move)
            
        except Exception as e:
            print(f"Chess validation error: {e}")
            return False
    
    def get_captured_pieces_from_move(self, board_before: Any, board_after: Any, move: Any) -> List[str]:
        """
        Determine what pieces were captured in a chess move
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            move: The move that was made
            
        Returns:
            List of captured piece descriptions
        """
        captured_pieces = []
        
        try:
            # Check if a piece was captured on the destination square
            if board_before.piece_at(move.to_square):
                captured_piece = board_before.piece_at(move.to_square)
                piece_name = self._get_piece_name(captured_piece)
                captured_pieces.append(piece_name)
            
            # Check for en passant capture
            if board_before.is_en_passant(move):
                # En passant captures a pawn that's not on the destination square
                captured_pieces.append("pawn")
            
            return captured_pieces
            
        except Exception as e:
            print(f"Error determining captured pieces: {e}")
            return []
    
    def get_piece_state(self, board: Any) -> Dict[str, Any]:
        """
        Extract detailed piece state for chess
        
        Args:
            board: Chess board to analyze
            
        Returns:
            Dictionary with detailed piece information
        """
        piece_state = super().get_piece_state(board)
        
        try:
            # Add chess-specific information
            piece_counts = {}
            material_balance = 0
            
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    piece_name = self._get_piece_name(piece)
                    piece_counts[piece_name] = piece_counts.get(piece_name, 0) + 1
                    
                    # Calculate material balance
                    piece_value = self._get_piece_value(piece.piece_type)
                    if piece.color == chess.WHITE:
                        material_balance += piece_value
                    else:
                        material_balance -= piece_value
            
            piece_state.update({
                'piece_counts': piece_counts,
                'material_balance': material_balance,
                'in_check': board.is_check(),
                'castling_rights': {
                    'white_kingside': board.has_kingside_castling_rights(chess.WHITE),
                    'white_queenside': board.has_queenside_castling_rights(chess.WHITE),
                    'black_kingside': board.has_kingside_castling_rights(chess.BLACK),
                    'black_queenside': board.has_queenside_castling_rights(chess.BLACK)
                },
                'en_passant_square': board.ep_square,
                'halfmove_clock': board.halfmove_clock,
                'fullmove_number': board.fullmove_number
            })
            
        except Exception as e:
            print(f"Error extracting chess piece state: {e}")
        
        return piece_state
    
    def _validate_chess_piece_integrity(self, board_before: Any, board_after: Any, move: Any) -> bool:
        """
        Validate that no illegal pieces were created in chess
        
        Args:
            board_before: Board before move
            board_after: Board after move
            move: The move made
            
        Returns:
            True if piece integrity is maintained
        """
        try:
            # Count pieces before and after
            before_counts = self._count_chess_pieces(board_before)
            after_counts = self._count_chess_pieces(board_after)
            
            # Check each piece type
            for piece_type in chess.PIECE_TYPES:
                for color in [chess.WHITE, chess.BLACK]:
                    piece_key = f"{color}_{piece_type}"
                    before_count = before_counts.get(piece_key, 0)
                    after_count = after_counts.get(piece_key, 0)
                    
                    # Pieces can only decrease (captures) or stay same, except for promotions
                    if after_count > before_count:
                        # Check if this is a legal promotion
                        if not self._is_legal_chess_promotion(piece_type, color, move, board_before):
                            return False
            
            return True
            
        except Exception as e:
            print(f"Error validating chess piece integrity: {e}")
            return False
    
    def _count_chess_pieces(self, board: Any) -> Dict[str, int]:
        """Count all pieces on the chess board"""
        counts = {}
        
        for piece_type in chess.PIECE_TYPES:
            for color in [chess.WHITE, chess.BLACK]:
                piece_key = f"{color}_{piece_type}"
                count = len(board.pieces(piece_type, color))
                if count > 0:
                    counts[piece_key] = count
        
        return counts
    
    def _is_legal_chess_promotion(self, piece_type: int, color: bool, move: Any, board_before: Any) -> bool:
        """
        Check if piece creation is due to legal pawn promotion
        
        Args:
            piece_type: Type of piece created
            color: Color of the piece
            move: The move made
            board_before: Board state before move
            
        Returns:
            True if this is a legal promotion
        """
        try:
            # Only queens, rooks, bishops, and knights can be created through promotion
            if piece_type not in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                return False
            
            # Check if this move is a promotion
            if hasattr(move, 'promotion') and move.promotion == piece_type:
                # Verify a pawn is being promoted
                moving_piece = board_before.piece_at(move.from_square)
                if moving_piece and moving_piece.piece_type == chess.PAWN:
                    # Check if pawn is reaching the promotion rank
                    if color == chess.WHITE and chess.square_rank(move.to_square) == 7:
                        return True
                    elif color == chess.BLACK and chess.square_rank(move.to_square) == 0:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking chess promotion: {e}")
            return False
    
    def _get_piece_name(self, piece) -> str:
        """Get human-readable piece name"""
        piece_names = {
            chess.PAWN: "pawn", chess.ROOK: "rook", chess.KNIGHT: "knight",
            chess.BISHOP: "bishop", chess.QUEEN: "queen", chess.KING: "king"
        }
        
        color = "white" if piece.color == chess.WHITE else "black"
        piece_type = piece_names.get(piece.piece_type, "unknown")
        
        return f"{color}_{piece_type}"
    
    def _get_piece_value(self, piece_type: int) -> int:
        """Get the point value of a piece type"""
        values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }
        return values.get(piece_type, 0)