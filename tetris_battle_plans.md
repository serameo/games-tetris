# Tetris Battle - Main Development Plan

## 1. Overview

Tetris Battle is a Windows desktop game written in Python, supporting both
single-player and two-player (local, same-screen) modes. This document is
the top-level plan. Detailed rules live in `tetris_battle_rules.md`. Each
development phase has its own file: `tetris_battle_phase01.md`,
`tetris_battle_phase02.md`, etc.

## 2. Confirmed Technical Decisions

| Decision | Choice |
|---|---|
| Language | Python 3 |
| Graphics / game loop library | Pygame |
| Two-player screen layout | Split-screen, single window, two boards side by side |
| Standalone `.exe` build (PyInstaller) | Not included for now; can be added as a later phase on request |
| Target OS | Windows |

## 3. Software & Tooling to Install

- Python 3.11+ (any recent Python 3 release)
- `pygame` (graphics, input, game loop, sound)
- `pytest` (unit testing framework)
- A virtual environment (`venv`) to isolate dependencies
- (Optional, editor-side) `black` / `flake8` for formatting and linting  -  not required, can be added if wanted

## 4. Required File Structure

```
tetris_battle/
|-- main.py                  # Entry point, launches the game
|-- requirements.txt         # pygame, pytest
|-- game/
|   |-- __init__.py
|   |-- config.py            # Board size, speeds, scoring table, level thresholds
|   |-- board.py             # Board grid, collision checks, line clearing
|   |-- tetrimino.py         # Tetrimino shapes, rotations, spawning
|   |-- player.py            # Per-player state: board, active piece, score, level
|   |-- game_state.py        # Overall game state machine (menu / playing / game over)
|   |-- input_handler.py     # Keyboard mapping for player 1 and player 2
|   `-- renderer.py          # Drawing the boards, pieces, UI, menu
|-- tests/
|   |-- __init__.py
|   |-- test_board.py
|   |-- test_tetrimino.py
|   |-- test_player.py
|   `-- test_game_state.py
|-- tetris_battle_plans.md
|-- tetris_battle_rules.md
|-- tetris_battle_phase01.md
|-- tetris_battle_phase02.md
`-- ...
```

This structure may be adjusted slightly as development proceeds, but any
change will be reflected here before the phase that changes it starts.

## 5. Testing Policy

- Every function that contains logic (not simple getters) must have at
  least one unit test in `pytest`.
- All existing tests must pass before a phase is considered complete.
- If a function is modified in a later phase, its tests must be re-run,
  and updated/added if its behavior changed.
- Tests run headless (no Pygame window needs to open) by testing the
  `game/` logic modules directly, separate from `renderer.py`.

## 6. Development Phases (summary)

| Phase | Goal |
|---|---|
| 1 | Project skeleton, dependencies, a running Pygame window, main menu (choose 1P / 2P), empty 9x18 board(s) rendered |
| 2 | Tetrimino system: shapes, rotation, spawning, movement, collision, locking  -  single player only |
| 3 | Line clearing, scoring table, leveling (score thresholds, configurable), drop-speed progression |
| 4 | Full single-player game loop: game over (block-out) and win (level 30) conditions, restart flow |
| 5 | Two-player mode: split-screen boards, Player 2 controls (WASD), independent simultaneous play, 2P win/lose rule |
| 6 | Polish: next-piece preview window, "shiny metal panel" block visuals, pause menu, minor UX |

Each phase has its own detailed plan file (see `tetris_battle_phase01.md`
onward). **Development of a phase will not begin until the previous
phase's plan is confirmed, and no phase will be marked complete until
its code is tested and any issues found in testing are fixed.**

## 7. Open Questions / Things to Confirm Later

- Whether ghost-piece (drop preview shadow) is wanted  -  not in the
  original spec, will ask before Phase 2 if relevant.
- Whether a hold-piece feature is wanted  -  not in the original spec,
  assumed **not included** unless requested.
- Exact pause/restart key bindings  -  will be proposed in Phase 4/6 for
  confirmation.
