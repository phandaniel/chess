import pygame
import chess
import chess.pgn
import chess.engine
import os
import time
import random

# --- Constants ---
WIDTH, HEIGHT = 1000, 800
BOARD_SIZE = 600
SQUARE_SIZE = BOARD_SIZE // 8
OFFSET_X = 50
OFFSET_Y = 100

# Colors
WHITE = (235, 235, 208)
DARK = (119, 149, 86)
HIGHLIGHT = (186, 202, 68)
BLACK = (0, 0, 0)
TEXT_COLOR = (50, 50, 50)
UI_BG = (240, 240, 240)
STOCKFISH_PATH = "stockfish/stockfish.exe" # User needs to place stockfish here

# Piece-Square Tables (simplified for basic AI)
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

# Assets
PIECE_IMAGES = {}

def load_assets():
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']
    for piece in pieces:
        filename = f"assets/{'w' if piece.isupper() else 'b'}{piece.upper()}.png"
        if os.path.exists(filename):
            try:
                PIECE_IMAGES[piece] = pygame.transform.scale(pygame.image.load(filename), (SQUARE_SIZE, SQUARE_SIZE))
            except Exception as e:
                print(f"Error loading {filename}: {e}")

class ChessAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn:
                return -99999
            else:
                return 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = self.piece_values[piece.piece_type]
                # Add positional value for pawns
                if piece.piece_type == chess.PAWN:
                    if piece.color == chess.WHITE:
                        val += PAWN_TABLE[63 - square]
                    else:
                        val += PAWN_TABLE[square]
                
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if maximizing_player:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board):
        best_move = None
        best_value = -float('inf') if board.turn == chess.WHITE else float('inf')
        
        moves = list(board.legal_moves)
        if not moves: return None
        random.shuffle(moves)

        for move in moves:
            board.push(move)
            board_value = self.minimax(board, self.depth - 1, -float('inf'), float('inf'), not board.turn)
            board.pop()
            
            if board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
        return best_move

class StockfishAI:
    def __init__(self, path, depth=10):
        self.path = path
        self.depth = depth
        self.engine = None
        if os.path.exists(path):
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(path)
            except Exception as e:
                print(f"Could not start Stockfish: {e}")

    def get_best_move(self, board):
        if not self.engine: return None
        result = self.engine.play(board, chess.engine.Limit(depth=self.depth))
        return result.move

    def quit(self):
        if self.engine:
            self.engine.quit()

class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bot vs Stockfish - Arena")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        self.ai = ChessAI(depth=3)
        self.stockfish = StockfishAI(STOCKFISH_PATH, depth=10)
        
        self.ai_enabled = False
        self.bot_vs_stockfish = False
        self.error_message = ""
        self.error_timer = 0
        
        self.selected_square = None
        self.legal_moves = []
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 32, bold=True)
        load_assets()

    def get_square_under_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        x, y = mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            file = x // SQUARE_SIZE
            rank = 7 - (y // SQUARE_SIZE)
            return chess.square(file, rank)
        return None

    def draw_board(self):
        self.screen.fill(UI_BG)
        pygame.draw.rect(self.screen, BLACK, (OFFSET_X - 2, OFFSET_Y - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), 2)
        
        for rank in range(8):
            for file in range(8):
                color = WHITE if (rank + file) % 2 == 0 else DARK
                rect = pygame.Rect(OFFSET_X + file * SQUARE_SIZE, OFFSET_Y + (7 - rank) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

                if self.selected_square == chess.square(file, rank):
                    pygame.draw.rect(self.screen, HIGHLIGHT, rect)

                if self.board.move_stack:
                    last_move = self.board.peek()
                    if chess.square(file, rank) in [last_move.from_square, last_move.to_square]:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        s.fill((255, 255, 0, 100))
                        self.screen.blit(s, rect.topleft)

                if chess.square(file, rank) in [m.to_square for m in self.legal_moves]:
                    pygame.draw.circle(self.screen, (0, 0, 0, 30), rect.center, 12)

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                pos = (OFFSET_X + file * SQUARE_SIZE, OFFSET_Y + (7 - rank) * SQUARE_SIZE)
                
                piece_symbol = piece.symbol()
                if piece_symbol in PIECE_IMAGES:
                    self.screen.blit(PIECE_IMAGES[piece_symbol], pos)
                else:
                    label = self.large_font.render(piece_symbol, True, BLACK)
                    self.screen.blit(label, (pos[0] + SQUARE_SIZE//4, pos[1] + SQUARE_SIZE//4))

    def draw_ui(self):
        status = "Game Over" if self.board.is_game_over() else ("White's Turn" if self.board.turn else "Black's Turn")
        if self.board.is_check():
            status += " (CHECK)"
        
        status_label = self.large_font.render(status, True, TEXT_COLOR)
        self.screen.blit(status_label, (WIDTH // 2 - status_label.get_width() // 2, 30))

        # Error Message Overlay
        if self.error_message and time.time() < self.error_timer:
            err_label = self.font.render(self.error_message, True, (200, 0, 0))
            self.screen.blit(err_label, (WIDTH // 2 - err_label.get_width() // 2, 80))

        info_x = 700
        controls = [
            "CONTROLS:",
            "U: Undo Move",
            "S: Save Game",
            "L: Load Game",
            "A: Toggle Bot (Black)",
            "V: Bot (White) vs Stockfish (Black)",
            "R: Reset Game",
            "",
            f"Bot Active: {self.ai_enabled}",
            f"Stockfish Battle: {self.bot_vs_stockfish}",
            f"Stockfish Found: {self.stockfish.engine is not None}",
            "",
            "PGN History:"
        ]
        for i, text in enumerate(controls):
            label = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(label, (info_x, 150 + i * 30))

        pgn_moves = []
        temp_board = chess.Board()
        for i, move in enumerate(self.board.move_stack):
            san = temp_board.san(move)
            if i % 2 == 0:
                pgn_moves.append(f"{i//2 + 1}. {san}")
            else:
                pgn_moves[-1] += f" {san}"
            temp_board.push(move)
        
        for i, text in enumerate(pgn_moves[-12:]):
            label = self.font.render(text, True, (100, 100, 100))
            self.screen.blit(label, (info_x, 500 + i * 20))

    def handle_click(self):
        if self.board.is_game_over(): return
        if self.bot_vs_stockfish: return # No manual moves in bot vs bot
        
        square = self.get_square_under_mouse()
        if square is None:
            self.selected_square = None
            self.legal_moves = []
            return

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
        else:
            move = chess.Move(self.selected_square, square)
            if chess.Move(self.selected_square, square, promotion=chess.QUEEN) in self.board.legal_moves:
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.legal_moves = []
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
                else:
                    self.selected_square = None
                    self.legal_moves = []

    def run(self):
        running = True
        while running:
            # Handle AI Moves
            if not self.board.is_game_over():
                if self.bot_vs_stockfish:
                    # Automated Bot vs Stockfish
                    self.draw_board()
                    self.draw_pieces()
                    self.draw_ui()
                    pygame.display.flip()
                    
                    if self.board.turn == chess.WHITE:
                        # My Bot plays White
                        move = self.ai.get_best_move(self.board)
                    else:
                        # Stockfish plays Black
                        move = self.stockfish.get_best_move(self.board)
                    
                    if move:
                        self.board.push(move)
                        time.sleep(0.5) # Add a small delay so we can see the moves
                
                elif self.ai_enabled and self.board.turn == chess.BLACK:
                    # Manual Player vs Bot
                    self.draw_board()
                    self.draw_pieces()
                    self.draw_ui()
                    pygame.display.flip()
                    move = self.ai.get_best_move(self.board)
                    if move:
                        self.board.push(move)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        if len(self.board.move_stack) > 0:
                            self.board.pop()
                            if (self.ai_enabled or self.bot_vs_stockfish) and len(self.board.move_stack) > 0:
                                self.board.pop()
                            self.selected_square = None
                            self.legal_moves = []
                    elif event.key == pygame.K_a:
                        self.ai_enabled = not self.ai_enabled
                        self.bot_vs_stockfish = False
                    elif event.key == pygame.K_v:
                        if self.stockfish.engine:
                            self.bot_vs_stockfish = not self.bot_vs_stockfish
                            self.ai_enabled = False
                        else:
                            abs_path = os.path.abspath(STOCKFISH_PATH)
                            self.error_message = f"Missing: {abs_path}"
                            self.error_timer = time.time() + 7
                            print(f"Stockfish not found at: {abs_path}")
                    elif event.key == pygame.K_r:
                        self.board.reset()

            self.draw_board()
            self.draw_pieces()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        self.stockfish.quit()
        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()

