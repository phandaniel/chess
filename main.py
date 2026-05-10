import chess
import chess.pgn
import chess.engine
import os
import time
import random

# --- Constants ---
if os.name == 'nt':
    STOCKFISH_PATH = "stockfish/stockfish.exe"
else:
    STOCKFISH_PATH = "stockfish/stockfish"

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
        self.bot_vs_bot = False
        self.error_message = ""

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_board(self):
        self.clear_screen()
        last_move = self.board.peek() if self.board.move_stack else None
        
        # Colors (Modern Balanced)
        LIGHT_SQ = "\033[48;5;252m" # Silver/Light Grey
        DARK_SQ  = "\033[48;5;240m" # Slate/Dark Grey
        MOVE_SQ  = "\033[48;5;221m" # Muted Yellow
        RESET    = "\033[0m"
        
        # Piece Colors
        WHITE_P  = "\033[38;5;231m\033[1m" # Pure White Bold
        BLACK_P  = "\033[38;5;16m\033[1m"  # Pure Black Bold
        
        INFO_COLOR = "\033[38;5;141m"
        CMD_COLOR  = "\033[38;5;244m"

        # 3x6 Proportional Pieces (Clean & Bold)
        PIECES = {
            chess.PAWN:   ["      ", "  ▄█▄ ", "      "],
            chess.KNIGHT: ["  ▄██ ", "   ██ ", "  ███ "],
            chess.BISHOP: ["   █  ", "  ███ ", "   █  "],
            chess.ROOK:   ["  █ █ ", "  ███ ", "  ███ "],
            chess.QUEEN:  ["  █▄█ ", "  ███ ", "  ███ "],
            chess.KING:   ["  ▄█▄ ", "  ███ ", "  ▄█▄ "]
        }
        
        # Borders (Clean Single Line)
        top_border = "     ┌" + "──────┬" * 7 + "──────┐"
        mid_border = "     ├" + "──────┼" * 7 + "──────┤"
        bot_border = "     └" + "──────┴" * 7 + "──────┘"

        print(f"\n        a      b      c      d      e      f      g      h")
        print(top_border)
        
        for rank in range(8, 0, -1):
            for sub_row in range(3):
                if sub_row == 1:
                    line = f"  {rank}  │"
                else:
                    line = "     │"
                
                for file in range(1, 9):
                    sq = chess.square(file-1, rank-1)
                    piece = self.board.piece_at(sq)
                    is_move = last_move and (sq == last_move.from_square or sq == last_move.to_square)
                    bg = MOVE_SQ if is_move else (LIGHT_SQ if (rank + file) % 2 == 0 else DARK_SQ)
                    
                    if piece:
                        p_col = WHITE_P if piece.color == chess.WHITE else BLACK_P
                        pattern = PIECES[piece.piece_type][sub_row]
                        line += f"{bg}{p_col}{pattern}{RESET}│"
                    else:
                        line += f"{bg}      {RESET}│"
                
                if sub_row == 1:
                    print(line + f"  {rank}")
                else:
                    print(line)

            if rank > 1:
                print(mid_border)
            else:
                print(bot_border)
        
        print("        a      b      c      d      e      f      g      h")

        # Game Info
        turn_text = f"{'White' if self.board.turn == chess.WHITE else 'Black'}"
        print(f"\n   TURN: {INFO_COLOR}{turn_text}{RESET}", end=" | ")
        if self.board.is_check():
            print("\033[1;31m--- CHECK! ---\033[0m", end=" | ")
        
        # Last move info
        if last_move:
            # san() requires the move to be legal in the current board state.
            # Since last_move is already pushed, we pop it, get the SAN, and push it back.
            move = self.board.pop()
            san_str = self.board.san(move)
            self.board.push(move)
            print(f"Last Move: {san_str}", end="")
        print()

        if self.error_message:
            print(f"\n   \033[1;31mError: {self.error_message}\033[0m")
            self.error_message = ""
        
        print(f"\n   {CMD_COLOR}Controls:{RESET}")
        print(f"   {CMD_COLOR}- Move: e2e4, Nf3{RESET}      {CMD_COLOR}- 'u': Undo{RESET}      {CMD_COLOR}- 'r': Reset{RESET}      {CMD_COLOR}- 'q': Quit{RESET}")
        print(f"   {CMD_COLOR}- 'a': Basic AI (B){RESET}  {CMD_COLOR}- 'b': Bot vs Bot{RESET}  {CMD_COLOR}- 'v': Bot vs Stockfish{RESET}")
        
        status_line = f"\n   AI: {'\033[1;32mON\033[0m' if self.ai_enabled else 'OFF'} | "
        status_line += f"Bot vs Bot: {'\033[1;32mON\033[0m' if self.bot_vs_bot else 'OFF'} | "
        status_line += f"Stockfish Battle: {'\033[1;32mON\033[0m' if self.bot_vs_stockfish else 'OFF'} | "
        status_line += f"Stockfish Engine: {'\033[1;32mFound\033[0m' if self.stockfish.engine else 'Not Found'}"
        print(status_line)

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
                if (self.ai_enabled or self.bot_vs_stockfish or self.bot_vs_bot) and len(self.board.move_stack) > 0:
                    self.board.pop()
        elif user_input == 'r':
            self.board.reset()
        elif user_input == 'a':
            self.ai_enabled = not self.ai_enabled
            self.bot_vs_stockfish = False
            self.bot_vs_bot = False
        elif user_input == 'b':
            self.bot_vs_bot = not self.bot_vs_bot
            self.ai_enabled = False
            self.bot_vs_stockfish = False
        elif user_input == 'v':
            if self.stockfish.engine:
                self.bot_vs_stockfish = not self.bot_vs_stockfish
                self.ai_enabled = False
                self.bot_vs_bot = False
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

            if self.bot_vs_bot:
                move = self.ai.get_best_move(self.board)
                if move:
                    print(f"\nBot plays: {self.board.san(move)}")
                    self.board.push(move)
                    time.sleep(1.0) # Pace for humans to follow
                continue

            if self.bot_vs_stockfish:
                if self.board.turn == chess.WHITE:
                    move = self.ai.get_best_move(self.board)
                    print(f"\nBasic AI plays: {self.board.san(move)}")
                else:
                    move = self.stockfish.get_best_move(self.board)
                    print(f"\nStockfish plays: {self.board.san(move)}")
                
                if move:
                    self.board.push(move)
                    time.sleep(1.0) # Pace for humans to follow
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
