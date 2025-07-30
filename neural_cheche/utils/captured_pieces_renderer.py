"""
Captured Pieces Renderer - Displays captured pieces for each player
"""

import pygame
from typing import List, Dict, Any, Tuple


class CapturedPiecesRenderer:
    """Renders captured pieces display similar to traditional chess interfaces"""
    
    # Chess piece Unicode symbols (same as ChessRenderer)
    PIECE_SYMBOLS = {
        "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚",
        "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    }
    
    # Checkers piece symbols
    CHECKERS_SYMBOLS = {
        "white_man": "⚪", "white_king": "👑",
        "black_man": "⚫", "black_king": "♛"
    }
    
    # Piece values for material advantage calculation
    PIECE_VALUES = {
        "pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": 0,
        "man": 1, "king": 2  # Checkers values  # noqa: F601
    }
    
    # Colors
    WHITE_COL = (255, 255, 255)
    BLACK_COL = (0, 0, 0)
    LIGHT_GRAY = (220, 220, 220)
    DARK_GRAY = (100, 100, 100)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    BLUE = (0, 0, 200)
    GOLD = (255, 215, 0)
    
    def __init__(self, piece_size: int = 30):
        self.piece_size = piece_size
        self.spacing = 5
        
        # Initialize fonts
        try:
            self.piece_font = pygame.font.SysFont("segoeuisymbol", piece_size)
            self.label_font = pygame.font.SysFont("arial", 16, bold=True)
            self.value_font = pygame.font.SysFont("arial", 14)
        except Exception:
            # Fallback fonts
            self.piece_font = pygame.font.Font(None, piece_size)
            self.label_font = pygame.font.Font(None, 16)
            self.value_font = pygame.font.Font(None, 14)
    
    def draw_captured_area(self, screen: pygame.Surface, pieces: List[str], 
                          x: int, y: int, color: str, game_type: str = "chess") -> int:
        """
        Draw captured pieces area for one player
        
        Args:
            screen: Pygame surface to draw on
            pieces: List of captured piece names
            x: X position
            y: Y position
            color: Player color ("white" or "black")
            game_type: Type of game ("chess" or "checkers")
            
        Returns:
            Height of the drawn area
        """
        try:
            # Draw background area
            area_width = 200
            area_height = max(80, len(pieces) * (self.piece_size + self.spacing) // 6 + 60)
            
            # Background
            bg_color = self.LIGHT_GRAY if color == "white" else self.DARK_GRAY
            pygame.draw.rect(screen, bg_color, (x, y, area_width, area_height))
            pygame.draw.rect(screen, self.BLACK_COL, (x, y, area_width, area_height), 2)
            
            # Title
            title_text = f"{color.title()} Captured"
            title_color = self.BLACK_COL if color == "white" else self.WHITE_COL
            title_surface = self.label_font.render(title_text, True, title_color)
            screen.blit(title_surface, (x + 5, y + 5))
            
            # Draw pieces
            if pieces:
                pieces_drawn = self._draw_pieces_grid(screen, pieces, x + 5, y + 25, 
                                                    area_width - 10, game_type)
                
                # Calculate and display material advantage
                material_value = self._calculate_material_value(pieces, game_type)
                value_text = f"Material: {material_value}"
                value_surface = self.value_font.render(value_text, True, title_color)
                screen.blit(value_surface, (x + 5, y + area_height - 20))
            else:
                # No pieces captured
                no_pieces_text = "No pieces captured"
                no_pieces_surface = self.value_font.render(no_pieces_text, True, title_color)
                text_rect = no_pieces_surface.get_rect(center=(x + area_width // 2, y + area_height // 2))
                screen.blit(no_pieces_surface, text_rect)
            
            return area_height
            
        except Exception as e:
            print(f"⚠️ Error drawing captured area: {e}")
            # Fallback simple display
            error_text = f"{color} captured: {len(pieces)}"
            error_surface = self.label_font.render(error_text, True, self.BLACK_COL)
            screen.blit(error_surface, (x, y))
            return 30
    
    def _draw_pieces_grid(self, screen: pygame.Surface, pieces: List[str], 
                         x: int, y: int, width: int, game_type: str) -> int:
        """Draw pieces in a grid layout"""
        try:
            pieces_per_row = max(1, width // (self.piece_size + self.spacing))
            current_x = x
            current_y = y
            pieces_in_row = 0
            
            # Group pieces by type for better display
            piece_counts = {}
            for piece in pieces:
                piece_counts[piece] = piece_counts.get(piece, 0) + 1
            
            # Draw grouped pieces
            for piece_type, count in piece_counts.items():
                for i in range(count):
                    if pieces_in_row >= pieces_per_row:
                        current_x = x
                        current_y += self.piece_size + self.spacing
                        pieces_in_row = 0
                    
                    self._draw_single_piece(screen, piece_type, current_x, current_y, game_type)
                    
                    current_x += self.piece_size + self.spacing
                    pieces_in_row += 1
            
            return (current_y - y) + self.piece_size
            
        except Exception as e:
            print(f"⚠️ Error drawing pieces grid: {e}")
            return 0
    
    def _draw_single_piece(self, screen: pygame.Surface, piece: str, 
                          x: int, y: int, game_type: str) -> None:
        """Draw a single captured piece"""
        try:
            if game_type == "chess":
                symbol = self._get_chess_symbol(piece)
            else:
                symbol = self._get_checkers_symbol(piece)
            
            if symbol:
                # Draw piece background
                piece_bg = pygame.Rect(x, y, self.piece_size, self.piece_size)
                pygame.draw.rect(screen, self.WHITE_COL, piece_bg)
                pygame.draw.rect(screen, self.BLACK_COL, piece_bg, 1)
                
                # Draw piece symbol
                piece_surface = self.piece_font.render(symbol, True, self.BLACK_COL)
                piece_rect = piece_surface.get_rect(center=piece_bg.center)
                screen.blit(piece_surface, piece_rect)
            
        except Exception as e:
            print(f"⚠️ Error drawing single piece: {e}")
    
    def _get_chess_symbol(self, piece: str) -> str:
        """Get chess piece symbol"""
        # Handle different piece name formats
        piece_lower = piece.lower()
        
        # Map common piece names to symbols
        if "white" in piece_lower:
            if "pawn" in piece_lower:
                return self.PIECE_SYMBOLS["P"]
            elif "rook" in piece_lower:
                return self.PIECE_SYMBOLS["R"]
            elif "knight" in piece_lower:
                return self.PIECE_SYMBOLS["N"]
            elif "bishop" in piece_lower:
                return self.PIECE_SYMBOLS["B"]
            elif "queen" in piece_lower:
                return self.PIECE_SYMBOLS["Q"]
            elif "king" in piece_lower:
                return self.PIECE_SYMBOLS["K"]
        elif "black" in piece_lower:
            if "pawn" in piece_lower:
                return self.PIECE_SYMBOLS["p"]
            elif "rook" in piece_lower:
                return self.PIECE_SYMBOLS["r"]
            elif "knight" in piece_lower:
                return self.PIECE_SYMBOLS["n"]
            elif "bishop" in piece_lower:
                return self.PIECE_SYMBOLS["b"]
            elif "queen" in piece_lower:
                return self.PIECE_SYMBOLS["q"]
            elif "king" in piece_lower:
                return self.PIECE_SYMBOLS["k"]
        
        # Try direct symbol lookup
        return self.PIECE_SYMBOLS.get(piece, "?")
    
    def _get_checkers_symbol(self, piece: str) -> str:
        """Get checkers piece symbol"""
        piece_lower = piece.lower()
        
        if "white" in piece_lower:
            if "king" in piece_lower:
                return self.CHECKERS_SYMBOLS["white_king"]
            else:
                return self.CHECKERS_SYMBOLS["white_man"]
        elif "black" in piece_lower:
            if "king" in piece_lower:
                return self.CHECKERS_SYMBOLS["black_king"]
            else:
                return self.CHECKERS_SYMBOLS["black_man"]
        
        return self.CHECKERS_SYMBOLS.get(piece, "?")
    
    def calculate_material_advantage(self, white_pieces: List[str], 
                                   black_pieces: List[str], game_type: str = "chess") -> int:
        """
        Calculate material advantage
        
        Args:
            white_pieces: List of white captured pieces
            black_pieces: List of black captured pieces
            game_type: Type of game
            
        Returns:
            Material advantage (positive = white advantage, negative = black advantage)
        """
        try:
            white_value = self._calculate_material_value(white_pieces, game_type)
            black_value = self._calculate_material_value(black_pieces, game_type)
            
            # Return advantage for the player who captured more valuable pieces
            return black_value - white_value  # Black captured white pieces = white disadvantage
            
        except Exception as e:
            print(f"⚠️ Error calculating material advantage: {e}")
            return 0
    
    def _calculate_material_value(self, pieces: List[str], game_type: str) -> int:
        """Calculate total material value of captured pieces"""
        try:
            total_value = 0
            
            for piece in pieces:
                piece_lower = piece.lower()
                
                if game_type == "chess":
                    if "pawn" in piece_lower:
                        total_value += self.PIECE_VALUES["pawn"]
                    elif "knight" in piece_lower or "bishop" in piece_lower:
                        total_value += self.PIECE_VALUES["knight"]  # Both worth 3
                    elif "rook" in piece_lower:
                        total_value += self.PIECE_VALUES["rook"]
                    elif "queen" in piece_lower:
                        total_value += self.PIECE_VALUES["queen"]
                    elif "king" in piece_lower:
                        total_value += self.PIECE_VALUES["king"]
                else:  # checkers
                    if "king" in piece_lower:
                        total_value += self.PIECE_VALUES["king"]  # Checkers king
                    else:
                        total_value += self.PIECE_VALUES["man"]
            
            return total_value
            
        except Exception as e:
            print(f"⚠️ Error calculating material value: {e}")
            return 0
    
    def draw_advantage_indicator(self, screen: pygame.Surface, advantage: int, 
                               x: int, y: int, game_type: str = "chess") -> None:
        """
        Draw material advantage indicator
        
        Args:
            screen: Pygame surface to draw on
            advantage: Material advantage value
            x: X position
            y: Y position
            game_type: Type of game
        """
        try:
            if advantage == 0:
                # Equal material
                text = "Material: Equal"
                color = self.DARK_GRAY
            elif advantage > 0:
                # White advantage
                text = f"White +{advantage}"
                color = self.BLUE
            else:
                # Black advantage
                text = f"Black +{abs(advantage)}"
                color = self.RED
            
            # Draw background
            text_surface = self.label_font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.x = x
            text_rect.y = y
            
            # Background rectangle
            bg_rect = text_rect.inflate(10, 4)
            pygame.draw.rect(screen, self.LIGHT_GRAY, bg_rect)
            pygame.draw.rect(screen, color, bg_rect, 2)
            
            # Draw text
            screen.blit(text_surface, text_rect)
            
        except Exception as e:
            print(f"⚠️ Error drawing advantage indicator: {e}")
    
    def draw_captured_pieces_panel(self, screen: pygame.Surface, 
                                  white_captured: List[str], black_captured: List[str],
                                  x: int, y: int, game_type: str = "chess") -> Tuple[int, int]:
        """
        Draw complete captured pieces panel for both players
        
        Args:
            screen: Pygame surface to draw on
            white_captured: White pieces captured by black
            black_captured: Black pieces captured by white
            x: X position
            y: Y position
            game_type: Type of game
            
        Returns:
            Tuple of (width, height) of the drawn panel
        """
        try:
            panel_width = 220
            
            # Draw white captured pieces (captured by black)
            white_height = self.draw_captured_area(screen, white_captured, x, y, "white", game_type)
            
            # Draw black captured pieces (captured by white)
            black_y = y + white_height + 10
            black_height = self.draw_captured_area(screen, black_captured, x, black_y, "black", game_type)
            
            # Draw material advantage indicator
            advantage = self.calculate_material_advantage(white_captured, black_captured, game_type)
            advantage_y = black_y + black_height + 10
            self.draw_advantage_indicator(screen, advantage, x, advantage_y, game_type)
            
            total_height = white_height + black_height + 50  # Extra space for advantage indicator
            
            return panel_width, total_height
            
        except Exception as e:
            print(f"⚠️ Error drawing captured pieces panel: {e}")
            return 220, 100  # Fallback dimensions
    
    def adapt_to_window_size(self, window_width: int, window_height: int) -> None:
        """
        Adapt captured pieces display to window size
        
        Args:
            window_width: Current window width
            window_height: Current window height
        """
        try:
            # Adjust piece size based on window size
            if window_width < 1000:
                self.piece_size = 25
                self.spacing = 3
            elif window_width < 1200:
                self.piece_size = 30
                self.spacing = 5
            else:
                self.piece_size = 35
                self.spacing = 6
            
            # Recreate fonts with new size
            try:
                self.piece_font = pygame.font.SysFont("segoeuisymbol", self.piece_size)
                self.label_font = pygame.font.SysFont("arial", max(14, self.piece_size // 2), bold=True)
                self.value_font = pygame.font.SysFont("arial", max(12, self.piece_size // 3))
            except Exception:
                # Fallback fonts
                self.piece_font = pygame.font.Font(None, self.piece_size)
                self.label_font = pygame.font.Font(None, max(14, self.piece_size // 2))
                self.value_font = pygame.font.Font(None, max(12, self.piece_size // 3))
            
        except Exception as e:
            print(f"⚠️ Error adapting to window size: {e}")
    
    def get_panel_dimensions(self, white_captured: List[str], black_captured: List[str]) -> Tuple[int, int]:
        """
        Get the dimensions needed for the captured pieces panel
        
        Args:
            white_captured: White pieces captured
            black_captured: Black pieces captured
            
        Returns:
            Tuple of (width, height) needed
        """
        try:
            base_width = 220
            
            # Calculate height based on number of pieces
            white_rows = max(1, (len(white_captured) + 5) // 6)  # 6 pieces per row
            black_rows = max(1, (len(black_captured) + 5) // 6)
            
            white_height = 60 + (white_rows * (self.piece_size + self.spacing))
            black_height = 60 + (black_rows * (self.piece_size + self.spacing))
            
            total_height = white_height + black_height + 50  # Extra space for advantage
            
            return base_width, total_height
            
        except Exception as e:
            print(f"⚠️ Error calculating panel dimensions: {e}")
            return 220, 200  # Fallback dimensions