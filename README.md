# CLI Chess

A pure CLI-based chess application in Python using `python-chess`.

## Features
- Play against another human locally.
- Play against a basic Minimax-based AI.
- Watch a battle between the basic AI and Stockfish.
- Standard chess rules enforced.
- Undo moves, reset board.
- Supports SAN (e.g., Nf3) and UCI (e.g., g1f3) move input.

## Requirements
- Python 3.x
- `python-chess` library (`pip install python-chess`)

## How to Play
Run the game:
```bash
python main.py
```

### Controls
- Enter a move in SAN (e.g., `e4`, `Nf3`) or UCI (e.g., `e2e4`) format.
- `u`: Undo the last move.
- `r`: Reset the board to the starting position.
- `a`: Toggle the basic AI (plays as Black).
- `v`: Toggle a match between the basic AI (White) and Stockfish (Black).
- `q`: Quit the game.

## Stockfish Integration
To use Stockfish, place the Stockfish executable in a `stockfish/` directory and update `STOCKFISH_PATH` in `main.py` if necessary.
