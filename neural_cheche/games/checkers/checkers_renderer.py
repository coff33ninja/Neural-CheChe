"""
Checkers visualization and rendering
"""

import pygame
from typing import List, Dict, Any


class CheckersRenderer:
    """Handles checkers board rendering and visualization"""
    
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
        self.info_font = pygame.font.SysFont("arial", 20)
        
        # Captured pieces tracking
        self.captured_pieces = {"white": [], "black": []}
    
    def draw_board(self, screen, board, offset_x, offset_y, title="Checkers", 
                   last_move=None, policy=None):
        """Draw the checkers board with pieces"""
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
        
        # Draw policy heatmap if provided
        if policy:
            self._draw_policy_heatmap(screen, board, policy, offset_x, offset_y)
        
        # Draw pieces
        self._draw_pieces(screen, board, offset_x, offset_y)
        
        # Draw title
        title_surf = self.info_font.render(title, True, self.BLACK_COL)
        screen.blit(title_surf, (offset_x + 150, offset_y - 30))
    
    def _draw_pieces(self, screen, board, offset_x, offset_y):
        """Draw checkers pieces on the board"""
        try:
            fen = board.fen
            parts = fen.split(':')
            if len(parts) >= 3:
                white_pieces = parts[1][1:].split(',') if len(parts[1]) > 1 else []
                black_pieces = parts[2][1:].split(',') if len(parts[2]) > 1 else []
                
                # Draw white pieces
                for piece_str in white_pieces:
                    if piece_str and piece_str.isdigit():
                        pos = int(piece_str)
                        if 1 <= pos <= 50:
                            row, col = self._pos_to_coords(pos)
                            if 0 <= row < 8 and 0 <= col < 8:
                                center = (
                                    offset_x + col * self.square_size + self.square_size // 2,
                                    offset_y + row * self.square_size + self.square_size // 2
                                )
                                pygame.draw.circle(
                                    screen, self.WHITE_COL, center, self.square_size // 2 - 5
                                )
                                pygame.draw.circle(
                                    screen, self.BLACK_COL, center, self.square_size // 2 - 5, 2
                                )
                
                # Draw black pieces
                for piece_str in black_pieces:
                    if piece_str and piece_str.isdigit():
                        pos = int(piece_str)
                        if 1 <= pos <= 50:
                            row, col = self._pos_to_coords(pos)
                            if 0 <= row < 8 and 0 <= col < 8:
                                center = (
                                    offset_x + col * self.square_size + self.square_size // 2,
                                    offset_y + row * self.square_size + self.square_size // 2
                                )
                                pygame.draw.circle(
                                    screen, self.BLACK_COL, center, self.square_size // 2 - 5
                                )
                                pygame.draw.circle(
                                    screen, self.WHITE_COL, center, self.square_size // 2 - 5, 2
                                )
        except Exception as e:
            print(f"[CheckersRenderer] Error drawing pieces: {e}")
            # Draw error message
            error_text = self.info_font.render("Board Error", True, self.RED)
            screen.blit(error_text, (offset_x + 100, offset_y + 200))
    
    def _pos_to_coords(self, pos):
        """Convert draughts position (1-50) to 8x8 coordinates"""
        row = (pos - 1) // 5
        col = ((pos - 1) % 5) * 2 + (1 if row % 2 == 0 else 0)
        return row, col
    
    def _draw_policy_heatmap(self, screen, board, policy, offset_x, offset_y):
        """Draw policy heatmap showing move probabilities"""
        max_prob = max(policy.values()) if policy else 1.0
        
        for move, prob in policy.items():
            try:
                # Handle different move formats
                if hasattr(move, 'end'):
                    to_pos = move.end
                elif isinstance(move, tuple):
                    to_pos = move[1]
                else:
                    continue
                
                row, col = self._pos_to_coords(to_pos)
                if 0 <= row < 8 and 0 <= col < 8:
                    alpha = int(255 * prob / max_prob) if max_prob > 0 else 0
                    color = (0, 255, 0, alpha)
                    s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    s.fill(color)
                    screen.blit(s, (
                        offset_x + col * self.square_size,
                        offset_y + row * self.square_size
                    ))
            except Exception:
                continue
    
    def draw_game_info(self, screen, board, x, y):
        """Draw game information"""
        try:
            pieces = board.get_pieces()
            player1_pieces = len([p for p in pieces if p.player == 1])
            player2_pieces = len([p for p in pieces if p.player == 2])
            player1_kings = len([p for p in pieces if p.player == 1 and p.king])
            player2_kings = len([p for p in pieces if p.player == 2 and p.king])
            
            # Display piece counts
            info_lines = [
                f"Player 1: {player1_pieces} pieces ({player1_kings} kings)",
                f"Player 2: {player2_pieces} pieces ({player2_kings} kings)",
                f"Current player: {board.turn}",
                f"Legal moves: {len(list(board.legal_moves())) if not board.is_over() else 0}"
            ]
            
            for i, line in enumerate(info_lines):
                text_surf = self.info_font.render(line, True, self.BLACK_COL)
                screen.blit(text_surf, (x, y + i * 20))
            
            # Game status
            if board.is_over():
                winner = board.who_won()
                status = f"Game Over - Winner: Player {winner}" if winner else "Game Over - Draw"
                status_surf = self.info_font.render(status, True, self.RED)
                screen.blit(status_surf, (x, y + len(info_lines) * 20))
                
        except Exception as e:
            error_surf = self.info_font.render(f"Info Error: {e}", True, self.RED)
            screen.blit(error_surf, (x, y))
    
    def update_captured_pieces(self, board_before, board_after, move) -> None:
        """
        Update captured pieces tracking based on a move
        
        Args:
            board_before: Board state before the move
            board_after: Board state after the move
            move: The move that was made
        """
        try:
            # Count pieces before and after
            before_pieces = self._count_pieces(board_before)
            after_pieces = self._count_pieces(board_after)
            
            # Find captured pieces
            for player in [1, 2]:
                for piece_type in ['man', 'king']:
                    before_count = before_pieces.get(f"player{player}_{piece_type}", 0)
                    after_count = after_pieces.get(f"player{player}_{piece_type}", 0)
                    
                    if before_count > after_count:
                        # Pieces were captured
                        captured_count = before_count - after_count
                        piece_name = f"{'white' if player == 1 else 'black'}_{piece_type}"
                        
                        for _ in range(captured_count):
                            if player == 1:
                                self.captured_pieces["white"].append(piece_name)
                            else:
                                self.captured_pieces["black"].append(piece_name)
            
        except Exception as e:
            print(f"⚠️ Error updating captured pieces: {e}")
    
    def _count_pieces(self, board) -> Dict[str, int]:
        """Count pieces on the board"""
        try:
            pieces = board.get_pieces()
            counts = {
                'player1_man': 0, 'player1_king': 0,
                'player2_man': 0, 'player2_king': 0
            }
            
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
            
            return counts
            
        except Exception as e:
            print(f"⚠️ Error counting pieces: {e}")
            return {}
    
    def get_captured_pieces(self) -> Dict[str, List[str]]:
        """Get current captured pieces"""
        return self.captured_pieces.copy()
    
    def reset_captured_pieces(self) -> None:
        """Reset captured pieces tracking"""
        self.captured_pieces = {"white": [], "black": []}
    
    def draw_board_with_captured_pieces(self, screen, board, offset_x: int, offset_y: int, 
                                       title: str = "Checkers", last_move = None, 
                                       policy: Dict = None, captured_pieces_renderer = None) -> None:
        """
        Draw the checkers board with captured pieces display
        
        Args:
            screen: Pygame surface to draw on
            board: Checkers board to render
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
                    "checkers"
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
            piece_values = {"man": 1, "king": 2}
            
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