# Tetris Battle - Phase 1: Project Skeleton & Main Menu

## Goal

Get a runnable Pygame window with a working main menu, and empty boards
drawn on screen. No Tetrimino gameplay yet  -  this phase proves the
project structure, window, and navigation work before any game logic is
built.

## Scope

1. **Project setup**
   - Create the file structure listed in `tetris_battle_plans.md`.
   - `requirements.txt` with `pygame` and `pytest`.
   - `game/config.py` with constants: board width (9), board height (18),
     window size, colors, base fall speed (1.0s), speed step (0.01s),
     starting level-up threshold (30), threshold increment (10), max
     level (30), scoring table (1/3/5/7).

2. **Window & game loop**
   - `main.py` opens a Pygame window and runs a basic game loop
     (event polling, clear screen, flip display) at a fixed frame rate
     (e.g. 60 FPS).
   - Clean shutdown on window close / Esc.

3. **Main menu**
   - Simple menu screen with two options: "1 Player" and "2 Players".
   - Keyboard navigation (Up/Down to move selection, Enter to confirm).
   - Selecting an option transitions to a "playing" state (boards shown,
     but empty  -  no pieces yet).

4. **Board rendering**
   - `game/board.py`: a `Board` class holding a 9x18 grid (empty in this
     phase) and a method to query cell state.
   - `game/renderer.py`: draws the grid lines / cell boundaries for one
     board; in 2-player mode, draws two boards side by side.

5. **Game state machine (initial)**
   - `game/game_state.py`: minimal state machine with states `MENU` and
     `PLAYING` (more states added in later phases).

## Out of scope for this phase

- Tetrimino shapes, spawning, movement, rotation, collision.
- Scoring, leveling, timers.
- Win/lose logic.
- Two-player independent piece control (boards are shown side by side,
  but nothing falls yet).

## Unit Tests

- `tests/test_board.py`: board initializes with correct width/height,
  all cells empty, cell-query function works for in-range and
  out-of-range coordinates.
- `tests/test_game_state.py`: state machine starts in `MENU`, moves to
  `PLAYING` on confirm with the correct player-count recorded, menu
  selection wraps/moves correctly between the two options.
- These tests exercise `game/board.py` and `game/game_state.py`
  directly (no Pygame window needed), per the testing policy in
  `tetris_battle_plans.md`.

## Definition of Done

- [ ] `python main.py` opens a window showing the main menu.
- [ ] Menu can be navigated and confirms into 1P or 2P mode.
- [ ] 1P mode shows one empty 9x18 board; 2P mode shows two, side by side.
- [ ] All unit tests for this phase pass (`pytest`).
- [ ] Plan reviewed and confirmed before Phase 2 begins.

## Questions before starting (if any arise during implementation)

None currently  -  will flag here if something in this phase turns out to
be ambiguous once implementation starts.
