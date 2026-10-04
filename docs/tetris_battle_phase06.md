# Tetris Battle - Phase 6: Next-Piece Preview and Shiny Metal Visuals

## Goal

The last planned phase: show each player which Tetrimino is coming up
next, and give every block the "shiny metal panel" look described in
the original spec, instead of flat colored squares.

## Scope delivered

1. **Next-piece preview** (`game/player.py`):
   - `PlayerBoard` now looks one piece ahead: `next_piece_type` always
     holds the type of whichever piece will spawn after the current one.
   - Internally, spawning was reworked around this: one piece type is
     drawn for the active piece and one more up front for the preview;
     each time a piece locks and a new one spawns, the previously
     "next" type becomes active and a fresh type is drawn to refill the
     preview. While a line-clear flash is in progress, `next_piece_type`
     is left untouched (nothing is consumed until the flash finishes and
     a piece actually spawns).
   - This is internal bookkeeping only, so no behavior from earlier
     phases changed -- it only adds a value to look at.
2. **"Shiny metal panel" visuals** (`game/renderer.py`):
   - New `draw_metal_block()`: instead of a flat filled square, each
     cell gets a lighter highlight along its top/left edges, a darker
     shadow along its bottom/right edges, and a thin diagonal glint
     line -- a simple beveled, reflective look built entirely from
     `pygame.draw` calls (no external image files, since this sandbox
     has no internet access to fetch any).
   - Both the locked board cells and the currently-falling piece now
     draw through this helper instead of a plain rectangle fill.
   - New `draw_next_piece_preview()`: draws a small version of the
     upcoming piece (its spawn orientation) using the same metal-block
     style, at 18px per cell instead of the board's 30px.
   - `draw_side_panel()` now shows a "Next:" label and that preview
     under the score/level text, when a `next_piece_type` is present in
     its info dict.
3. **`main.py`** -- each player's panel dict now includes
   `"next_piece_type": pb.next_piece_type`, so both players see their
   own upcoming piece in two-player mode too.

## Out of scope

None -- this was the last phase in the original plan
(`tetris_battle_plans.md`). Anything further (ghost piece, hold piece,
sound, a proper start-up settings screen, etc.) would be a new addition
beyond the original spec, not a continuation of the existing plan.

## Unit tests

- `tests/test_player.py` gained a `TestPlayerBoardNextPiecePreview`
  class: `next_piece_type` matches the second queued piece from the
  very start; it correctly becomes the active piece after a lock (with
  a fresh value drawn to refill the preview); and it stays unchanged
  while a line-clear flash is in progress (not consumed until the flash
  actually finishes and a new piece spawns).
- All **103 tests** pass (100 from Phases 1-5 + 3 new) via
  `python -m unittest discover -s tests`, stable across 5 consecutive
  runs. The full existing suite was also re-run repeatedly after the
  `PlayerBoard` spawn-logic rework to make sure the one-piece-ahead
  change didn't silently alter any earlier phase's behavior -- it
  didn't, since every existing test's piece sequence only needed at
  most one deterministic spawn event.

## A note on testing pygame itself

Same limitation as every phase: no internet access in this sandbox, so
`pygame` could not be installed here, and the visual/geometry code in
`renderer.py` (the metal-block bevel effect and the preview box
placement) has no automated tests, consistent with every other phase's
pygame-dependent code. `main.py` and `renderer.py` were checked with
`python -m py_compile` only. The preview box's size was hand-checked to
fit comfortably inside the existing 150px-wide side panel (the widest
piece, I, is 4 cells x 18px = 72px, well under the panel width), but
please run on your machine to confirm:

- The metal-block bevel/glint effect actually looks good at this scale
  (30px board cells, 18px preview cells) -- colors, border thickness,
  etc. are all easy to retune in `draw_metal_block()` if not.
- The "Next:" preview doesn't visually crowd the score/level text above
  it, in both single- and two-player mode (including Player 2's panel,
  which is now on the left side of the screen since the Phase 5 layout
  addendum).

## Definition of Done

- [ ] Both single- and two-player modes show a "Next:" preview of the
      upcoming piece beside the score/level.
- [ ] The preview updates correctly every time a piece locks.
- [ ] Locked and falling blocks have a visible beveled/shiny look
      instead of flat squares.
- [ ] All unit tests pass.
