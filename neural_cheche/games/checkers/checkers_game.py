"""
Checkers game implementation using draughts library
"""

import draughts as pydraughts
import numpy as np
import torch
from typing import Any, List, Dict
from ..base_game import BaseGame


class CheckersGame(BaseGame):
    """Checkers/Draughts game implementation"""
    
    def __init__(self):
        super().__init__()
        self.action_size = 1000  # Standard checkers action space
    
    def create_board(self):
        """Create a new checkers board"""
        return pydraughts.Board()
    
    def get_legal_moves(self, board):
        """Get all legal moves"""
        return list(board.legal_moves())
    
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
            raise ValueError(f"Invalid checkers move detected: {move}")
        
        return True
    
    def is_game_over(self, board):
        """Check if game is over"""
        return board.is_over()
    
    def get_winner(self, board):
        """Get winner: 1 for player 1, -1 for player 2, 0 for draw"""
        if board.is_over():
            winner = board.who_won()
            return 1 if winner == 1 else -1 if winner == 2 else 0
        return 0
    
    def get_current_player(self, board):
        """Get current player: 1 for player 1, -1 for player 2"""
        return 1 if board.turn == 1 else -1
    
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
        
        # Create 8 historical planes
        for i in range(8):
            if i == 0:
                state = board
            elif i <= len(history):
                state = history[-i]
            else:
                state = board
            
            plane = np.zeros((14, 8, 8))
            
            # Parse FEN notation for draughts
            try:
                fen = state.fen
                parts = fen.split(':')
                if len(parts) >= 3:
                    white_pieces = parts[1][1:].split(',') if len(parts[1]) > 1 else []
                    black_pieces = parts[2][1:].split(',') if len(parts[2]) > 1 else []
                    
                    # Place white pieces
                    for piece_str in white_pieces:
                        if piece_str and piece_str.isdigit():
                            pos = int(piece_str)
                            if 1 <= pos <= 50:
                                row, col = self._pos_to_coords(pos)
                                if 0 <= row < 8 and 0 <= col < 8:
                                    plane[0, row, col] = 1  # White man
                    
                    # Place black pieces
                    for piece_str in black_pieces:
                        if piece_str and piece_str.isdigit():
                            pos = int(piece_str)
                            if 1 <= pos <= 50:
                                row, col = self._pos_to_coords(pos)
                                if 0 <= row < 8 and 0 <= col < 8:
                                    plane[2, row, col] = 1  # Black man
                
                plane[12] = 1 if state.turn == 1 else 0  # Player 1 to move
                plane[13] = 0  # Move count placeholder
            except Exception as e:
                print(f"[CheckersGame] Error parsing board: {e}")
            
            planes.append(plane)
        
        tensor = torch.tensor(np.concatenate(planes, axis=0), dtype=torch.float32)
        if device is not None:
            tensor = tensor.to(device)
        return tensor
    
    def _pos_to_coords(self, pos):
        """Convert draughts position (1-50) to 8x8 coordinates"""
        row = (pos - 1) // 5
        col = ((pos - 1) % 5) * 2 + (1 if row % 2 == 0 else 0)
        return row, col
    
    def get_reward(self, board):
        """Enhanced reward function for checkers"""
        if board.is_over():
            winner = board.who_won()
            return 1 if winner == 1 else -1 if winner == 2 else 0
        
        # Evaluate position based on piece count and advancement
        try:
            pieces = board.get_pieces()
            player1_pieces = len([p for p in pieces if p.player == 1])
            player2_pieces = len([p for p in pieces if p.player == 2])
            player1_kings = len([p for p in pieces if p.player == 1 and p.king])
            player2_kings = len([p for p in pieces if p.player == 2 and p.king])
            
            # Calculate piece advantage
            piece_advantage = (player1_pieces - player2_pieces) + 2 * (player1_kings - player2_kings)
            
            # Penalty for excessive piece trading when ahead
            total_pieces = player1_pieces + player2_pieces
            if total_pieces < 8 and abs(piece_advantage) > 2:  # Endgame with advantage
                return min(0.4, max(-0.4, piece_advantage * 0.08))
            
            return min(0.3, max(-0.3, piece_advantage * 0.05))
        except Exception:
            return 0
    
    # Checkers-specific validation methods
    def validate_move_hook(self, board_before: Any, board_after: Any, move: Any) -> bool:
        """
        Checkers-specific move validation
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            move: The move that was made
            
        Returns:
            True if move is valid for checkers
        """
        try:
            # For checkers, if the move was legal and executed successfully,
            # we trust the draughts library's validation
            # The draughts library already prevents illegal moves
            return True
            
        except Exception as e:
            print(f"Checkers validation error: {e}")
            return True  # Default to allowing the move
    
    def get_captured_pieces_from_move(self, board_before: Any, board_after: Any, move: Any) -> List[str]:
        """
        Determine what pieces were captured in a checkers move
        
        Args:
            board_before: Board state before move
            board_after: Board state after move
            move: The move that was made
            
        Returns:
            List of captured piece descriptions
        """
        captured_pieces = []
        
        try:
            # Count pieces before and after
            before_counts = self._count_checkers_pieces(board_before)
            after_counts = self._count_checkers_pieces(board_after)
            
            # Find pieces that were removed (captured)
            for piece_type, before_count in before_counts.items():
                after_count = after_counts.get(piece_type, 0)
                if before_count > after_count:
                    captured_count = before_count - after_count
                    captured_pieces.extend([piece_type] * captured_count)
            
            return captured_pieces
            
        except Exception as e:
            print(f"Error determining captured checkers pieces: {e}")
            return []
    
    def get_piece_state(self, board: Any) -> Dict[str, Any]:
        """
        Extract detailed piece state for checkers
        
        Args:
            board: Checkers board to analyze
            
        Returns:
            Dictionary with detailed piece information
        """
        piece_state = super().get_piece_state(board)
        
        try:
            piece_counts = self._count_checkers_pieces(board)
            
            # Calculate material balance
            player1_men = piece_counts.get('player1_man', 0)
            player1_kings = piece_counts.get('player1_king', 0)
            player2_men = piece_counts.get('player2_man', 0)
            player2_kings = piece_counts.get('player2_king', 0)
            
            material_balance = (player1_men + 2 * player1_kings) - (player2_men + 2 * player2_kings)
            
            piece_state.update({
                'piece_counts': piece_counts,
                'material_balance': material_balance,
                'total_pieces': sum(piece_counts.values()),
                'player1_total': player1_men + player1_kings,
                'player2_total': player2_men + player2_kings,
                'kings_ratio': (player1_kings + player2_kings) / max(1, sum(piece_counts.values()))
            })
            
        except Exception as e:
            print(f"Error extracting checkers piece state: {e}")
        
        return piece_state
    
    def _validate_checkers_piece_integrity(self, board_before: Any, board_after: Any, move: Any) -> bool:
        """
        Validate that no illegal pieces were created in checkers
        
        Args:
            board_before: Board before move
            board_after: Board after move
            move: The move made
            
        Returns:
            True if piece integrity is maintained
        """
        try:
            # For now, allow all moves that are legal according to the draughts library
            # The draughts library already handles piece integrity validation
            # We can add more specific checks here if needed
            return True
            
        except Exception as e:
            print(f"Error validating checkers piece integrity: {e}")
            return True  # Default to allowing the move
    
    def _count_checkers_pieces(self, board: Any) -> Dict[str, int]:
        """Count all pieces on the checkers board"""
        counts = {
            'player1_man': 0,
            'player1_king': 0,
            'player2_man': 0,
            'player2_king': 0
        }
        
        try:
            pieces = board.get_pieces()
            for piece in pieces:
                if piece.player == 1:
                    if piece.king:
                        counts['player1_king'] += 1
                    else:
                        counts['player1_man'] += 1
                elif piece.player == 2:
                    if piece.king:
                        counts['player2_king'] += 1
                    else:
                        counts['player2_man'] += 1
        except Exception as e:
            print(f"Error counting checkers pieces: {e}")
        
        return counts
    
    def _is_legal_checkers_promotion(self, piece_type: str, before_counts: Dict[str, int], after_counts: Dict[str, int]) -> bool:
        """
        Check if piece creation is due to legal king promotion
        
        Args:
            piece_type: Type of piece created
            before_counts: Piece counts before move
            after_counts: Piece counts after move
            
        Returns:
            True if this is a legal promotion
        """
        try:
            # Only kings can be created through promotion
            if 'king' not in piece_type:
                return False
            
            # Check if corresponding men were removed
            if piece_type == 'player1_king':
                men_type = 'player1_man'
            elif piece_type == 'player2_king':
                men_type = 'player2_man'
            else:
                return False
            
            kings_added = after_counts.get(piece_type, 0) - before_counts.get(piece_type, 0)
            men_removed = before_counts.get(men_type, 0) - after_counts.get(men_type, 0)
            
            # Kings added should equal men removed (promotion)
            return kings_added <= men_removed
            
        except Exception as e:
            print(f"Error checking checkers promotion: {e}")
            return False