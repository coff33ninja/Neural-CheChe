"""
Chess visualization and rendering
"""

import pygame
import chess
from typing import List, Dict, Any, Tuple


class ChessRenderer:
    """Handles chess board rendering and visualization"""
    
    # Chess piece Unicode symbols
    PIECE_SYMBOLS = {
        "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚",
        "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    }
    
    # Colors
    LIGHT_BROWN = (240, 217, 181)
    DARK_BROWN = (181, 136, 99)
    WHITE_COL = (255, 255, 255)
    BLACK_COL = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (200, 20, 20)
    BLUE = (20, 20, 200)
    
    def __init__(self, square_size=60):
        self.square_size = square_size
        self.piece_font = pygame.font.SysFont("segoeuisymbol", 45)
        self.info_font = pygame.font.SysFont("arial", 20)
        
        # Captured pieces tracking
        self.captured_pieces = {"white": [], "black": []}
    
    def draw_board(self, screen, board, offset_x, offset_y, title="Chess", 
                   last_move=None, policy=None):
        """Draw the chess board with pieces"""
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = self.LIGHT_BROWN if (row + col) % 2 == 0 else self.DARK_BROWN
                pygame.draw.rect(
                    screen, color,
                    (offset_x + col * self.square_size, 
                     offset_y + row * self.square_size,
                     self.square_size, self.square_size)
                )
                
                # Highlight last move
                if last_move and chess.square(col, 7 - row) in [
                    last_move.from_square, last_move.to_square
                ]:
                    pygame.draw.rect(
                        screen, self.GREEN,
                        (offset_x + col * self.square_size,
                         offset_y + row * self.square_size,
                         self.square_size, self.square_size), 3
                    )
        
        # Draw policy heatmap if provided
        if policy:
            self._draw_policy_heatmap(screen, board, policy, offset_x, offset_y)
        
        # Draw pieces
        self._draw_pieces(screen, board, offset_x, offset_y)
        
        # Draw title
        title_surf = self.info_font.render(title, True, self.BLACK_COL)
        screen.blit(title_surf, (offset_x + 150, offset_y - 30))
    
    def _draw_pieces(self, screen, board, offset_x, offset_y):
        """Draw chess pieces on the board"""
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece:
                row, col = 7 - chess.square_rank(sq), chess.square_file(sq)
                symbol = self.PIECE_SYMBOLS[piece.symbol()]
                
                # Enhanced piece rendering with outline
                if piece.color == chess.BLACK:
                    outline_surf = self.piece_font.render(symbol, True, self.WHITE_COL)
                    text_surf = self.piece_font.render(symbol, True, self.BLACK_COL)
                    # Draw outline
                    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        screen.blit(outline_surf, (
                            offset_x + col * self.square_size + 8 + dx,
                            offset_y + row * self.square_size + 5 + dy
                        ))
                    screen.blit(text_surf, (
                        offset_x + col * self.square_size + 8,
                        offset_y + row * self.square_size + 5
                    ))
                else:
                    outline_surf = self.piece_font.render(symbol, True, self.BLACK_COL)
                    text_surf = self.piece_font.render(symbol, True, self.WHITE_COL)
                    # Draw outline
                    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        screen.blit(outline_surf, (
                            offset_x + col * self.square_size + 8 + dx,
                            offset_y + row * self.square_size + 5 + dy
                        ))
                    screen.blit(text_surf, (
                        offset_x + col * self.square_size + 8,
                        offset_y + row * self.square_size + 5
                    ))
    
    def _draw_policy_heatmap(self, screen, board, policy, offset_x, offset_y):
        """Draw policy heatmap showing move probabilities"""
        max_prob = max(policy.values()) if policy else 1.0
        
        for move, prob in policy.items():
            from_sq = move.from_square
            to_sq = move.to_square
            
            # Draw destination square with full alpha
            to_row, to_col = 7 - chess.square_rank(to_sq), chess.square_file(to_sq)
            alpha = int(255 * prob / max_prob) if max_prob > 0 else 0
            color = (0, 255, 0, alpha)
            s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            s.fill(color)
            screen.blit(s, (
                offset_x + to_col * self.square_size,
                offset_y + to_row * self.square_size
            ))
            
            # Draw source square with reduced alpha (yellow)
            from_row, from_col = 7 - chess.square_rank(from_sq), chess.square_file(from_sq)
            from_alpha = int(128 * prob / max_prob) if max_prob > 0 else 0
            from_color = (255, 255, 0, from_alpha)
            from_s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            from_s.fill(from_color)
            screen.blit(from_s, (
                offset_x + from_col * self.square_size,
                offset_y + from_row * self.square_size
            ))
    
    def draw_game_info(self, screen, board, x, y):
        """Draw game information (piece counts, status, etc.)"""
        # Count pieces by type
        piece_counts = {"white": {}, "black": {}}
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece:
                color_key = "white" if piece.color == chess.WHITE else "black"
                piece_type = piece.symbol().lower()
                piece_counts[color_key][piece_type] = (
                    piece_counts[color_key].get(piece_type, 0) + 1
                )
        
        # Display piece counts
        y_pos = y
        for color in ["white", "black"]:
            if piece_counts[color]:
                pieces_text = f"{color.capitalize()}: "
                for piece_type, count in piece_counts[color].items():
                    symbol = self.PIECE_SYMBOLS[
                        piece_type.upper() if color == "white" else piece_type
                    ]
                    pieces_text += f"{symbol}×{count} "
                
                text_color = self.BLACK_COL if color == "white" else self.RED
                text_surf = self.info_font.render(pieces_text, True, text_color)
                screen.blit(text_surf, (x, y_pos))
                y_pos += 20
        
        # Display game status
        status_text = ""
        if board.is_check():
            status_text = "CHECK!"
        elif board.is_checkmate():
            status_text = "CHECKMATE!"
        elif board.is_stalemate():
            status_text = "STALEMATE"
        elif board.is_insufficient_material():
            status_text = "INSUFFICIENT MATERIAL"
        
        if status_text:
            status_surf = self.info_font.render(status_text, True, self.RED)
            screen.blit(status_surf, (x, y_pos))
    
    def draw_move_info(self, screen, board, last_move, x, y):
        """Draw information about the last move"""
        if last_move:
            try:
                piece = board.piece_at(last_move.to_square)
                if piece:
                    piece_symbol = self.PIECE_SYMBOLS[piece.symbol()]
                    move_text = f"Last move: {piece_symbol} {last_move}"
                else:
                    move_text = f"Last move: {last_move}"
                
                move_surf = self.info_font.render(move_text, True, self.BLACK_COL)
                screen.blit(move_surf, (x, y))
                
                # Show whose turn it is
                color_text = "White" if piece and piece.color == chess.WHITE else "Black"
                color_surf = self.info_font.render(
                    f"{color_text} to move",
                    True,
                    self.BLACK_COL if piece and piece.color == chess.WHITE else self.RED
                )
                screen.blit(color_surf, (x, y + 20))
            except Exception:
                move_surf = self.info_font.render(f"Move: {last_move}", True, self.BLACK_COL)
                screen.blit(move_surf, (x, y))
    
    def update_captured_pieces(self, board_before: chess.Board, board_after: chess.Board, move: chess.Move) -> None:
        """
        Update captured pieces tracking based on a move
        
        Args:
            board_before: Board state before the move
            board_after: Board state after the move
            move: The move that was made
        """
        try:
            # Check if a piece was captured on the destination square
            captured_piece = board_before.piece_at(move.to_square)
            if captured_piece:
                piece_name = self._get_piece_name(captured_piece)
                if captured_piece.color == chess.WHITE:
                    self.captured_pieces["white"].append(piece_name)
                else:
                    self.captured_pieces["black"].append(piece_name)
            
            # Check for en passant capture
            if board_before.is_en_passant(move):
                # En passant captures a pawn
                if board_before.turn == chess.WHITE:
                    self.captured_pieces["black"].append("black_pawn")
                else:
                    self.captured_pieces["white"].append("white_pawn")
            
        except Exception as e:
            print(f"⚠️ Error updating captured pieces: {e}")
    
    def get_captured_pieces(self) -> Dict[str, List[str]]:
        """Get current captured pieces"""
        return self.captured_pieces.copy()
    
    def reset_captured_pieces(self) -> None:
        """Reset captured pieces tracking"""
        self.captured_pieces = {"white": [], "black": []}
    
    def draw_board_with_captured_pieces(self, screen: pygame.Surface, board: chess.Board, 
                                       offset_x: int, offset_y: int, title: str = "Chess",
                                       last_move: chess.Move = None, policy: Dict = None,
                                       captured_pieces_renderer = None) -> None:
        """
        Draw the chess board with captured pieces display
        
        Args:
            screen: Pygame surface to draw on
            board: Chess board to render
            offset_x: X offset for the board
            offset_y: Y offset for the board
            title: Title to display
            last_move: Last move made (for highlighting)
            policy: Policy distribution for move visualization
            captured_pieces_renderer: CapturedPiecesRenderer instance
        """
        try:
            # Draw the main board
            self.draw_board(screen, board, offset_x, offset_y, title, last_move, policy)
            
            # Draw captured pieces if renderer is available
            if captured_pieces_renderer:
                # Calculate position for captured pieces (to the right of the board)
                board_width = self.square_size * 8
                captured_x = offset_x + board_width + 20
                captured_y = offset_y
                
                # Draw captured pieces panel
                captured_pieces_renderer.draw_captured_pieces_panel(
                    screen, 
                    self.captured_pieces["white"], 
                    self.captured_pieces["black"],
                    captured_x, 
                    captured_y, 
                    "chess"
                )
            
        except Exception as e:
            print(f"⚠️ Error drawing board with captured pieces: {e}")
            # Fallback to regular board drawing
            self.draw_board(screen, board, offset_x, offset_y, title, last_move, policy)
    
    def calculate_material_advantage(self) -> int:
        """
        Calculate material advantage based on captured pieces
        
        Returns:
            Material advantage (positive = white advantage, negative = black advantage)
        """
        try:
            piece_values = {
                "pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": 0
            }
            
            white_captured_value = 0
            black_captured_value = 0
            
            # Calculate value of white pieces captured by black
            for piece in self.captured_pieces["white"]:
                piece_type = piece.split("_")[1] if "_" in piece else piece
                white_captured_value += piece_values.get(piece_type, 0)
            
            # Calculate value of black pieces captured by white
            for piece in self.captured_pieces["black"]:
                piece_type = piece.split("_")[1] if "_" in piece else piece
                black_captured_value += piece_values.get(piece_type, 0)
            
            # Return advantage for white (positive = white advantage)
            return black_captured_value - white_captured_value
            
        except Exception as e:
            print(f"⚠️ Error calculating material advantage: {e}")
            return 0
    
    def get_captured_pieces_summary(self) -> str:
        """Get a text summary of captured pieces"""
        try:
            white_count = len(self.captured_pieces["white"])
            black_count = len(self.captured_pieces["black"])
            advantage = self.calculate_material_advantage()
            
            summary = f"Captured - White: {white_count}, Black: {black_count}"
            if advantage > 0:
                summary += f" (White +{advantage})"
            elif advantage < 0:
                summary += f" (Black +{abs(advantage)})"
            else:
                summary += " (Equal)"
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Error creating captured pieces summary: {e}")
            return "Captured pieces: Error"
    
    def _get_piece_name(self, piece: chess.Piece) -> str:
        """Get standardized piece name for captured pieces tracking"""
        color = "white" if piece.color == chess.WHITE else "black"
        piece_names = {
            chess.PAWN: "pawn", chess.ROOK: "rook", chess.KNIGHT: "knight",
            chess.BISHOP: "bishop", chess.QUEEN: "queen", chess.KING: "king"
        }
        piece_type = piece_names.get(piece.piece_type, "unknown")
        return f"{color}_{piece_type}"