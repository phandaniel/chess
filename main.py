import chess
import chess.pgn
import chess.engine
import os
import time
import random

# --- Constants ---
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
        self.board = chess.Board()
        self.ai = ChessAI(depth=3)
        self.stockfish = StockfishAI(STOCKFISH_PATH, depth=10)
        
        self.ai_enabled = False
        self.bot_vs_stockfish = False
        self.error_message = ""

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_board(self):
        self.clear_screen()
        print("\n" + self.board.unicode(borders=True))
        print(f"\nTurn: {'White' if self.board.turn == chess.WHITE else 'Black'}")
        if self.board.is_check():
            print("--- CHECK! ---")
        if self.error_message:
            print(f"Error: {self.error_message}")
            self.error_message = ""
        
        print("\nControls:")
        print("  - Enter move (e.g., e2e4, Nf3)")
        print("  - 'u' to undo move")
        print("  - 'r' to reset board")
        print("  - 'a' to toggle Basic AI (Black)")
        print("  - 'v' to toggle Bot (White) vs Stockfish (Black)")
        print("  - 'q' to quit")
        print(f"\nBasic AI: {'ON' if self.ai_enabled else 'OFF'}")
        print(f"Stockfish Battle: {'ON' if self.bot_vs_stockfish else 'OFF'}")
        print(f"Stockfish Found: {'Yes' if self.stockfish.engine else 'No'}")

    def handle_input(self, user_input):
        user_input = user_input.strip().lower()
        if not user_input:
            return True

        if user_input == 'q':
            return False
        elif user_input == 'u':
            if len(self.board.move_stack) > 0:
                self.board.pop()
                # If AI was playing, pop its move too
                if (self.ai_enabled or self.bot_vs_stockfish) and len(self.board.move_stack) > 0:
                    self.board.pop()
        elif user_input == 'r':
            self.board.reset()
        elif user_input == 'a':
            self.ai_enabled = not self.ai_enabled
            self.bot_vs_stockfish = False
        elif user_input == 'v':
            if self.stockfish.engine:
                self.bot_vs_stockfish = not self.bot_vs_stockfish
                self.ai_enabled = False
            else:
                self.error_message = "Stockfish engine not found!"
        else:
            try:
                # Try to parse as SAN first, then UCI
                try:
                    move = self.board.parse_san(user_input)
                except ValueError:
                    move = self.board.parse_uci(user_input)
                
                if move in self.board.legal_moves:
                    self.board.push(move)
                else:
                    self.error_message = f"Illegal move: {user_input}"
            except ValueError:
                self.error_message = f"Invalid move format: {user_input}"
        
        return True

    def run(self):
        while True:
            self.display_board()
            
            if self.board.is_game_over():
                print(f"\nGame Over! Result: {self.board.result()}")
                input("Press Enter to continue...")
                self.board.reset()
                continue

            if self.bot_vs_stockfish:
                if self.board.turn == chess.WHITE:
                    move = self.ai.get_best_move(self.board)
                    print(f"Basic AI plays: {self.board.san(move)}")
                else:
                    move = self.stockfish.get_best_move(self.board)
                    print(f"Stockfish plays: {self.board.san(move)}")
                
                if move:
                    self.board.push(move)
                    time.sleep(1) # Delay to watch the game
                continue

            if self.ai_enabled and self.board.turn == chess.BLACK:
                move = self.ai.get_best_move(self.board)
                print(f"Basic AI plays: {self.board.san(move)}")
                if move:
                    self.board.push(move)
                    time.sleep(0.5)
                continue

            user_input = input("\nEnter move or command: ")
            if not self.handle_input(user_input):
                break

        self.stockfish.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
