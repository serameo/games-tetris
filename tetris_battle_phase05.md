# Tetris Battle - Phase 5: Two-Player Mode

## Goal

Give two-player mode a real, independent, simultaneous game for each
player -- split-screen boards side by side, Player 2 on WASD + Space,
and the two-player win/lose rule from the rules doc. Everything from
Phases 1-4 (line-clear flash, per-level speed, hard drop, round-over
screen, Escape confirm prompt) now applies equally to both players.

## Scope delivered

1. **`game/match.py`** (new) -- `determine_round_outcome(p1_game_over,
   p1_won, p2_game_over, p2_won)`: pure logic, no pygame, returns the
   round-over message once the round should end, or `None` to keep
   playing.
   - One player blocked out -> the other wins ("PLAYER 1 WINS!" /
     "PLAYER 2 WINS!").
   - Both blocked out at once -> "DRAW!".
   - One player reaches the Level 30 win threshold -> that player wins.
   - Both reach it at once -> "DRAW!".
   - (A loss and an opponent's win at the same check always agree on
     the same winner, so there's no real ambiguity there -- see the
     docstring for the reasoning.)
2. **`main.py`** -- restructured around a single list of `PlayerBoard`s
   (length 1 or 2) instead of a separate single-player path and an
   empty-placeholder two-player path:
   - `start_round()` now creates one real `PlayerBoard` per player.
   - Each player gets their own gravity accumulator, so their fall
     speed is independently based on their own level.
   - `handle_gameplay_key()` applies one player's key mapping for a
     KEYDOWN event; Player 1 keeps arrow keys + Enter, and a new
     `P2_KEYS` mapping (**W**=rotate, **A**=left, **D**=right,
     **S**=soft drop, **Space**=hard drop) is applied to the second
     board only when two-player mode is active.
   - `check_round_end()` calls `game/match.py` for two players (or the
     existing single-player win/game_over check for one).
3. **`game/renderer.py`** -- the round-over screen now highlights any
   message containing "WIN" (not just the exact string "YOU WIN!"), so
   "PLAYER 1 WINS!" / "PLAYER 2 WINS!" get the same highlight color;
   "DRAW!" and "GAME OVER" stay in the normal text color.

## Out of scope for this phase

- Next-piece preview window and the "shiny metal panel" visual style --
  Phase 6, the last planned phase.

## Unit tests

- `tests/test_match.py` (new): no outcome while both are still playing;
  each single-loss and single-win case; both-loss and both-win draws;
  and the "loss + opponent's separate win agree on the same winner"
  case.
- All **100 tests** pass (92 before this phase + 8 new) via
  `python -m unittest discover -s tests`, stable across 5 consecutive
  runs.

## A note on testing pygame itself

Same limitation as every phase so far: no internet access in this
sandbox, so `pygame` could not be installed here. `main.py` and
`renderer.py` were checked with `python -m py_compile` only. Please run
on your machine, ideally with a second person (or your other hand!) to
confirm:

- Both boards render side by side and fall independently.
- Player 2's WASD + Space controls work correctly on their own board
  and never affect Player 1's board (and vice versa).
- If Player 1's board blocks out, the screen shows "PLAYER 2 WINS!"
  (and vice versa).
- Escape still pauses both boards at once (gravity and flashing on
  both boards stop while the Resume / Back to Main Menu / Exit Game
  prompt is open), since that was already automatic from Phase 4's
  design (the state machine only advances gameplay while `PLAYING`).

## Definition of Done

- [ ] Two-player mode shows two independently-falling boards side by
      side, each with its own score/level panel.
- [ ] Player 2's WASD/Space controls only affect the right-hand board.
- [ ] One player losing ends the round immediately with the other
      player declared the winner.
- [ ] All unit tests pass.
- [ ] Plan reviewed and confirmed before Phase 6 (next-piece preview
      window, "shiny metal panel" visual style) begins -- the last
      planned phase.

## Addendum: mirrored two-player layout

After the initial Phase 5 delivery, the two-player layout was changed to
a mirrored arrangement instead of two identical left-to-right slots:

    [margin] [P2 panel] [P2 board] [P1 board] [P1 panel] [margin]

- The two play boards are adjacent (touching) in the middle.
- Player 2's score/level panel is outermost on the left; Player 1's is
  outermost on the right -- a mirror image of each other.
- Single-player mode is unchanged (board on the left, panel on its right).

Changes:
- `game/config.py`: `WINDOW_WIDTH_2P` recalculated for the new layout
  (no gap needed between the two boards, so the window is slightly
  narrower than before: 2 margins + 2 boards + 2 panels, instead of 3
  margins + 2 boards + 2 panels).
- `game/renderer.py`: `draw_side_panel()` now takes the panel's own
  top-left position directly (instead of computing it from the board's
  position), since a panel can now sit to the left OR right of its
  board. `draw_playing()` picks the mirrored render order only when
  there are exactly 2 boards; single-player keeps the original
  board-then-panel layout.

This is pure layout/geometry code inside `renderer.py`, which (like all
pygame-dependent code in this project) has no automated tests in this
sandbox -- see the note in the main Phase 5 section above. The
underlying arithmetic was hand-checked instead: for the default board
size, Player 2's board spans x=190-460px and Player 1's spans
x=460-730px, meeting exactly at x=460 with no gap or overlap, and the
total width matches the updated `WINDOW_WIDTH_2P` exactly. Please
confirm on your machine that this looks right, especially that neither
player's panel text overlaps the boards.

## Addendum 2: gap restored between the two boards

The touching-boards version from the first mirrored-layout addendum was
adjusted: the two boards now have a margin-width gap between them again,
same as the very first Phase 5 layout, just with the mirrored panel
positions kept (P2 panel/board on the left, P1 board/panel on the right).

    [margin] [P2 panel] [P2 board] [gap] [P1 board] [P1 panel] [margin]

- `game/config.py`: `WINDOW_WIDTH_2P` back to 3 margins (matching the
  original Phase 5 formula, since a margin-width gap was re-added
  between the boards).
- `game/renderer.py`: `draw_playing()` adds one `BOARD_MARGIN`-wide gap
  between the two players' board+panel groups.

Hand-checked arithmetic for the default board size: P2's board now spans
x=190-460px, and P1's spans x=500-770px -- a clean 40px gap between
them, with the total width still matching `WINDOW_WIDTH_2P` exactly.
