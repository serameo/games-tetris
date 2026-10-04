# Tetris Battle - Phase 3: Line Clearing, Scoring, Leveling

## Goal

Make locked pieces actually clear full rows, award points for it, and
progress the player through levels 1-30 with the corresponding
drop-speed increase, for single player. Two-player mode is unchanged
from Phase 2 (empty placeholder boards).

## Decision confirmed this phase

**Leveling uses a cumulative (never-reset) score**, not a per-level
counter. Concretely:

- `score_threshold_for_level(n)` (from Phase 1) still gives the amount
  *added* at level `n`  -  30, 40, 50, ...  -  but leveling now compares the
  player's **total** score against the **running sum** of these values.
- New helper: `cumulative_score_to_complete_level(n)` = sum of
  `score_threshold_for_level(i)` for `i = 1..n`. This is the total score
  needed to complete level `n` (advance past it, or  -  at `n == 30`  -  win).
  - Complete level 1: total score >= 30
  - Complete level 2: total score >= 30 + 40 = 70
  - Complete level 3: total score >= 70 + 50 = 120
  - ... and so on up through level 30 (win threshold = 5,250 total points).
- The displayed "Score" in-game is this same cumulative total  -  it never
  resets.

## Scope delivered

1. **`game/board.py`**  -  `clear_full_rows()`: removes every full row,
   shifts the rows above down, and backfills new empty rows at the top.
   Returns how many rows were cleared. Also added `is_row_full(y)`.
2. **`game/config.py`**  -  `cumulative_score_to_complete_level(level)`
   helper (see above).
3. **`game/player.py`** (`PlayerBoard`)  -  now tracks `score`, `level`,
   and `lines_cleared_total`:
   - Locking a piece calls `board.clear_full_rows()`, adds points from
     `LINE_CLEAR_SCORES` (1/3/5/7 per the rules doc) for however many
     rows cleared at once, then checks for a level-up.
   - `fall_interval` (property) returns the drop speed for the player's
     *current* level, using Phase 1's `fall_interval_for_level()`.
   - Reaching the Level 30 win threshold sets `won = True` (a stub, like
     `game_over`  -  see below) and the board stops spawning new pieces.
4. **`game/renderer.py`**  -  new `draw_side_panel()` shows "Score: N" /
   "Level: N" beside the board, plus a "GAME OVER" or "YOU WIN!" label
   when applicable.
5. **`main.py`**  -  gravity now runs at `player_board.fall_interval`
   (recomputed every frame, so it speeds up automatically as the level
   rises) instead of a fixed constant. The score/level panel is drawn
   next to the board.

## Out of scope for this phase (deferred, as before)

- A real GAME OVER / YOU WIN *screen* with a restart option  -  Phase 4.
  Right now, once `game_over` or `won` becomes `True`, that board simply
  stops responding to input; the panel just shows a text label.
- Two-player mode: still just empty boards, no piece, no scoring  -  Phase 5.
- Next-piece preview window and the "shiny metal panel" visuals  -  Phase 6.

## Unit Tests

- `tests/test_board.py`: `is_row_full()`, and `clear_full_rows()` for no
  full rows, a single full row (with a row above it correctly shifting
  down), and multiple full rows at once (order of surviving rows
  preserved).
- `tests/test_config.py`: `cumulative_score_to_complete_level()` for
  levels 1-3 and a monotonically-increasing check across all 30 levels.
- `tests/test_player.py`: locking with no line clear leaves score/level
  untouched; locking that completes 2 rows at once awards the correct
  points and actually empties the board; level advances exactly at the
  cumulative threshold (including jumping multiple levels at once from a
  big score jump) and not before; `fall_interval` reflects the current
  level; the win flag fires at the Level 30 threshold, locks the
  triggering piece without spawning a new one, and freezes moves/rotate/
  drop afterward  -  matching the same pattern as the Phase 2 `game_over` stub.
- All **63 tests** pass (45 from Phases 1-2 + 18 new) via
  `python -m unittest discover -s tests`, confirmed stable across 15
  consecutive runs (an earlier flaky test  -  a too-short 2-row test board
  occasionally spawning a piece too tall for it  -  was found and fixed).

## A note on testing pygame itself

Same limitation as Phase 2: this sandbox has no internet access, so
`pygame` could not be installed here. `main.py` and `renderer.py` were
checked with `python -m py_compile` only. Please run them on your
machine to confirm the score panel displays correctly and that the game
actually speeds up as you clear lines and level up.

## Definition of Done

- [ ] Clearing 1/2/3/4 lines at once awards 1/3/5/7 points respectively.
- [ ] The on-screen score updates immediately after a clear.
- [ ] Leveling up happens at the correct cumulative score, and the piece
      visibly falls faster afterward.
- [ ] Reaching the Level 30 threshold shows "YOU WIN!" and the board
      stops accepting input (full win screen is Phase 4).
- [ ] All unit tests pass.
- [ ] Plan reviewed and confirmed before Phase 4 (game over/win screens,
      restart flow) begins.
