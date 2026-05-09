# Chess Program Design Document

## 1. Objective
To build a fully functional, pure CLI (Command Line Interface) chess program in Python. The game supports two-player local matches and a basic AI opponent, as well as integration with Stockfish. It enforces all standard chess rules and provides essential features like undo/redo, move history, and AI battle mode.

## 2. Core Technologies
*   **Language:** Python 3.x
*   **Interface:** Pure CLI (Standard Console Output/Input).
*   **Game Logic & Rule Validation:** `python-chess` library. This handles all move generation, legal move validation, complex rules (castling, en passant, promotion), and PGN/FEN handling.

## 3. Architecture Overview
The application follows a Model-View-Controller (MVC) pattern adapted for CLI.

### 3.1. Engine (Model)
Powered by `python-chess`.
*   **Board Representation:** The `chess.Board` object maintains the full state of the game.
*   **Move Validation:** Leverages `board.legal_moves` for absolute rule compliance.
*   **Serialization:** Uses FEN (Forsyth-Edwards Notation) for saving/loading and PGN (Portable Game Notation) for move history.

### 3.2. User Interface (View & Controller)
Handles rendering and user interactions via the terminal.
*   **Renderer:**
    *   Prints the board using Unicode characters (`board.unicode()`).
    *   Displays turn information and status (check, checkmate).
*   **Event Handler:**
    *   Accepts text input for moves (SAN or UCI format).
    *   Processes single-character commands for undo, reset, and AI toggles.

### 3.3. Artificial Intelligence
*   **Basic AI:** Minimax algorithm with Alpha-Beta pruning, implemented in `ChessAI`.
*   **Stockfish:** Integration via `chess.engine` for high-level play.

## 4. Implementation Plan (Refactored for CLI)

### Phase 1: Environment & Logic
1.  Install `python-chess`.
2.  Initialize a `chess.Board`.
3.  Implement basic board printing and move input.

### Phase 2: Game Features
1.  Implement Undo functionality using `board.pop()`.
2.  Add status indicators (whose turn, check/checkmate notifications).
3.  Implement AI battle mode (Basic AI vs Stockfish).

### Phase 3: AI Development
1.  Implement a basic move evaluator.
2.  Develop the Minimax search algorithm.
3.  Optimize with Alpha-Beta pruning.

### Phase 4: Refinement
1.  Add clear-screen functionality for a cleaner CLI experience.
2.  Improve error handling for invalid move inputs.

## 5. Verification & Testing
*   **Manual Playtesting:** Verify move validation by playing through various scenarios.
*   **Command Testing:** Ensure all CLI commands (undo, reset, ai, quit) function correctly.
*   **AI vs AI:** Run the AI against Stockfish to test stability and performance.