# Tetris Battle - Phase 2: Tetrimino System (Single Player)

## Goal

Give the single-player board a real, playable falling piece: all 7
Tetrimino shapes with their rotations, movement, wall/floor collision,
gravity, and locking into the board. Two-player mode still shows empty
placeholder boards (no falling piece)  -  Player 2 controls and full
2-player piece logic are Phase 5.

## Scope delivered

1. **`game/tetrimino.py`**  -  the `Tetrimino` class and `SHAPES` table
   with all 7 pieces (O, I, S, Z, T, L, J) and every rotation state
   listed in the original spec. `spawn()` centers a new piece
   horizontally at the top of the board. `moved()` and `rotated()`
   return new, translated/rotated pieces without checking collisions  - 
   collision checking is the caller's job (`PlayerBoard`).
2. **`game/player.py`**  -  the `PlayerBoard` class: owns a `Board` and
   the active piece.
   - `move(dx, dy)` / `rotate()`  -  apply and reject on collision.
   - `soft_drop()`  -  move down one row, or lock + spawn the next piece
     if blocked.
   - Locking writes the piece's cells into the board with its color.
   - If a freshly spawned piece immediately collides, `game_over` is
     set to `True` (a real game-over *screen* is Phase 4  -  for now the
     board simply stops responding to further moves).
3. **`game/renderer.py`**  -  `draw_active_piece()` draws the falling
   piece over its board; `draw_playing()` now accepts an optional list
   of active pieces (one per board).
4. **`main.py`**  -  single-player mode now:
   - Falls automatically at the Level 1 speed from `tetris_battle_rules.md`
     (1.00s per row  -  level-based speed-up is Phase 3).
   - Up = rotate, Left/Right = move, Down = soft drop, matching
     `tetris_battle_rules.md`.
   - Two-player mode is unchanged from Phase 1 (empty boards, no
     falling piece yet).

## Out of scope for this phase (by design, deferred to later phases)

- Line clearing, scoring, leveling, and speed progression (Phase 3).
- A real game-over/win screen and restart flow (Phase 4)  -  right now
  `game_over` is just an internal flag.
- Two-player piece control (Phase 5).
- Next-piece preview window and the "shiny metal panel" visual style
  (Phase 6)  -  pieces currently render as flat colored squares.
- Wall-kick rotation (e.g. nudging a piece sideways so a rotation near
  a wall still succeeds). Not in the original spec, so rotation is
  simply rejected if it would collide. Flagging this in case you'd like
  it added later.

## Unit Tests

- `tests/test_tetrimino.py`: cell coordinates for a piece at a given
  position, `moved()`/`rotated()` return new pieces without mutating
  the original, the O piece's rotation is a no-op, the I piece cycles
  between its 2 states, the T piece cycles through all 4 states,
  `spawn()` centers each piece type/rotation and keeps it in bounds.
- `tests/test_player.py`: movement left/right/down, blocked movement at
  both walls, rotation (including a rotation correctly rejected when it
  would put a cell outside the board), locking a piece into the board
  and spawning the next one, and the `game_over` stub triggering when a
  new piece has no room to spawn (plus moves/rotation/drop all being
  ignored once `game_over` is `True`).
- All 45 tests (23 from Phase 1 + 22 new) pass via
  `python -m unittest discover -s tests`.

## A note on testing pygame itself

This sandbox has no internet access, so `pygame` could not be installed
here to test `main.py`/`renderer.py` by actually running them. All
`game/` logic files (`tetrimino.py`, `player.py`, `board.py`,
`game_state.py`, `config.py`) have no pygame dependency and are fully
unit-tested above. `main.py` and `renderer.py` were checked with
`python -m py_compile` (valid syntax) but need to be run on your machine
(`pip install -r requirements.txt` then `python main.py`) to confirm the
falling piece looks and feels right.

## Definition of Done

- [ ] `python main.py` -> choose "1 Player" -> a piece spawns, falls on
      its own, and responds to Up/Left/Right/Down.
- [ ] Moving into a wall stops the piece at the wall.
- [ ] Rotating near a wall is rejected rather than crashing or moving
      the piece outside the board.
- [ ] A piece that can't drop further locks in place and a new one spawns.
- [ ] All unit tests pass (`pytest` or `python -m unittest discover -s tests`).
- [ ] Plan reviewed and confirmed before Phase 3 (line clearing, scoring,
      leveling) begins.

## Questions / things to confirm

- Should soft drop (Down key) award any points for cells dropped, like
  classic Tetris sometimes does? The original spec doesn't mention this,
  so it currently awards nothing. Will keep it that way unless you'd
  like it added in Phase 3's scoring work.
