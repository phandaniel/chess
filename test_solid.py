
import chess

# Solid 3x3 Block Patterns
PIECE_BLOCKS = {
    chess.PAWN:   ["  ▄  ", "  █  ", " ▀▀▀ "],
    chess.KNIGHT: [" ▄██ ", "  ██ ", "  █  "],
    chess.BISHOP: ["  █  ", " ▄█▄ ", "  ▀  "],
    chess.ROOK:   [" █ █ ", " ███ ", " ▀▀▀ "],
    chess.QUEEN:  [" █▄█ ", "  █  ", " ▀▀▀ "],
    chess.KING:   [" ▄█▄ ", "  █  ", " ▀▀▀ "]
}

# Let's try even simpler/bolder
PIECE_BLOCKS_BOLD = {
    chess.PAWN:   ["     ", "  █  ", "     "],
    chess.KNIGHT: [" ██  ", "  █  ", "     "],
    chess.BISHOP: ["  █  ", " █ █ ", "     "],
    chess.ROOK:   [" █ █ ", " ███ ", "     "],
    chess.QUEEN:  [" █ █ ", "  █  ", " █ █ "],
    chess.KING:   ["  █  ", " ███ ", "  █  "]
}

def print_piece_test():
    WHITE_P = "\033[38;5;231m\033[1m"
    BLACK_P = "\033[38;5;232m\033[1m"
    BG_L = "\033[48;5;253m"
    BG_D = "\033[48;5;242m"
    RESET = "\033[0m"

    print("Solid Piece Test (White pieces on Dark/Light squares):")
    for pt, lines in PIECE_BLOCKS.items():
        print(f"\nPiece Type: {pt}")
        for line in lines:
            print(f"{BG_D}{WHITE_P}{line}{RESET} {BG_L}{WHITE_P}{line}{RESET}")

    print("\nSolid Piece Test (Black pieces on Dark/Light squares):")
    for pt, lines in PIECE_BLOCKS.items():
        print(f"\nPiece Type: {pt}")
        for line in lines:
            print(f"{BG_D}{BLACK_P}{line}{RESET} {BG_L}{BLACK_P}{line}{RESET}")

if __name__ == "__main__":
    print_piece_test()
