"""
Game utility functions
"""

import chess
import draughts
import numpy as np


def get_reward(board, game_type):
    """Enhanced reward function with penalty rules for better AI learning"""
    if game_type == "chess":
        if board.is_checkmate():
            return -1 if board.turn == chess.WHITE else 1
        
        # Penalty rules for poor endgame play
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            # Calculate material advantage
            material = sum(
                (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK))) * val
                for pt, val in [(chess.PAWN, 1), (chess.KNIGHT, 3), (chess.BISHOP, 3), (chess.ROOK, 5), (chess.QUEEN, 9)]
            )
            
            # Penalty for stalemating when winning
            if abs(material) > 5:  # Significant material advantage
                penalty = -0.7 if material > 0 else 0.7  # Harsh penalty for failing to convert
                return penalty if board.turn == chess.WHITE else -penalty
            return 0
        
        # Penalty for repetition when winning
        if board.is_fivefold_repetition():
            material = sum(
                (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK))) * val
                for pt, val in [(chess.PAWN, 1), (chess.KNIGHT, 3), (chess.BISHOP, 3), (chess.ROOK, 5), (chess.QUEEN, 9)]
            )
            if abs(material) > 3:  # Penalty for repetition with advantage
                penalty = -0.5 if material > 0 else 0.5
                return penalty if board.turn == chess.WHITE else -penalty
            return -0.2 if board.turn == chess.WHITE else 0.2  # Small penalty for repetition
        
        return 0
    else:
        # Enhanced Draughts/Checkers logic with penalty rules
        if board.is_over():
            winner = board.who_won()
            return 1 if winner == 1 else -1 if winner == 2 else 0
        
        # Evaluate position based on piece count and advancement
        pieces = board.get_pieces()
        player1_pieces = len([p for p in pieces if p.player == 1])
        player2_pieces = len([p for p in pieces if p.player == 2])
        player1_kings = len([p for p in pieces if p.player == 1 and p.king])
        player2_kings = len([p for p in pieces if p.player == 2 and p.king])
        
        # Enhanced positional evaluation
        piece_advantage = (player1_pieces - player2_pieces) + 2 * (player1_kings - player2_kings)
        
        # Penalty for excessive piece trading when ahead
        total_pieces = player1_pieces + player2_pieces
        if total_pieces < 8 and abs(piece_advantage) > 2:  # Endgame with advantage
            # Encourage decisive play
            return min(0.4, max(-0.4, piece_advantage * 0.08))
        
        return min(0.3, max(-0.3, piece_advantage * 0.05))


def analyze_game_patterns(experiences, game_type):
    """Analyze patterns in AI's move choices for self-understanding"""
    if not experiences:
        return {}
    
    analysis = {
        'total_moves': len(experiences),
        'game_type': game_type,
        'move_quality_distribution': [],
        'strategic_patterns': {}
    }
    
    # Analyze move quality based on policy confidence
    for experience in experiences:
        _, policy_str, reward, _ = experience[:4]  # Unpack safely, ignore unused vars
        # Parse policy string to get move probabilities
        try:
            # This would need to be adapted based on your policy format
            if isinstance(policy_str, dict):
                policy_confidence = len(policy_str) / 100  # Simplified metric
            else:
                policy_confidence = len(str(policy_str)) / 100  # Simplified metric
            analysis['move_quality_distribution'].append(policy_confidence)
        except Exception:
            # More specific exception handling
            continue
    
    # Calculate strategic insights
    if analysis['move_quality_distribution']:
        analysis['strategic_patterns'] = {
            'avg_confidence': sum(analysis['move_quality_distribution']) / len(analysis['move_quality_distribution']),
            'consistency': 1.0 - (max(analysis['move_quality_distribution']) - min(analysis['move_quality_distribution'])),
            'final_outcome': reward
        }
    
    return analysis


def get_draughts_info():
    """Get information about the draughts module"""
    return {
        "module_name": draughts.__name__,
        "available_attributes": [attr for attr in dir(draughts) if not attr.startswith('_')],
        "module_doc": getattr(draughts, '__doc__', 'No documentation available')
    }


def create_draughts_board():
    """Create a new draughts board using the draughts module"""
    # Use the draughts module's available constructors
    available_attrs = dir(draughts)
    
    # Try common draughts class names
    for class_name in ['Game', 'Board', 'Checkers', 'DraughtsGame']:
        if class_name in available_attrs:
            try:
                cls = getattr(draughts, class_name)
                return cls()
            except Exception:
                continue
    
    # If no constructor works, return None
    return None


def analyze_draughts_position(board):
    """Analyze a draughts position using draughts-specific features"""
    if not hasattr(board, 'get_pieces'):
        return {"error": "Not a draughts board"}
    
    pieces = board.get_pieces()
    analysis = {
        "total_pieces": len(pieces),
        "player1_pieces": len([p for p in pieces if p.player == 1]),
        "player2_pieces": len([p for p in pieces if p.player == 2]),
        "player1_kings": len([p for p in pieces if p.player == 1 and p.king]),
        "player2_kings": len([p for p in pieces if p.player == 2 and p.king]),
        "current_player": board.turn,
        "game_over": board.is_over(),
        "legal_moves": len(list(board.legal_moves())) if not board.is_over() else 0
    }
    
    if board.is_over():
        analysis["winner"] = board.who_won()
    
    return analysis


def create_move_history_tensor(board, history, max_history=8):
    """Create enhanced state representation with move history for context"""
    # This would create a tensor stack of the last N board positions
    # Each position becomes a layer in the input tensor
    history_planes = []
    
    for i in range(max_history):
        if i < len(history):
            # Use historical position
            hist_board = history[-(i + 1)]
        else:
            # Pad with current position if not enough history
            hist_board = board
        
        # Convert board to tensor representation (simplified)
        if hasattr(hist_board, 'fen'):  # Chess board
            plane = np.zeros((8, 8))  # Simplified representation
            # In a real implementation, this would be much more detailed
        else:  # Checkers board
            plane = np.zeros((8, 8))
        
        history_planes.append(plane)
    
    return np.stack(history_planes, axis=0)


def calculate_game_complexity(board, game_type):
    """Calculate the complexity of the current game position"""
    if game_type == "chess":
        # Chess complexity metrics
        legal_moves = len(list(board.legal_moves))
        piece_count = len([sq for sq in chess.SQUARES if board.piece_at(sq)])
        
        # Simple complexity score
        complexity = legal_moves * 0.1 + piece_count * 0.05
        
        # Bonus for tactical positions
        if board.is_check():
            complexity += 2.0
        
        return min(10.0, complexity)
    
    elif game_type == "checkers":
        # Checkers complexity metrics
        legal_moves = len(list(board.legal_moves()))
        pieces = board.get_pieces()
        piece_count = len(pieces)
        king_count = len([p for p in pieces if p.king])
        
        complexity = legal_moves * 0.2 + piece_count * 0.1 + king_count * 0.3
        
        return min(10.0, complexity)
    
    return 1.0  # Default complexity


if __name__ == '__main__':
    # Test the draughts functionality
    game = create_draughts_board()
    if game:
        print("New draughts game analysis:", analyze_draughts_position(game))
    else:
        print("Could not create draughts board - checking available classes...")
        print("Draughts module info:", get_draughts_info())