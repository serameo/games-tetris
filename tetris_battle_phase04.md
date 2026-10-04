# Tetris Battle - Phase 4: Game Over / Win Screen and Restart

## Goal

Turn the game_over/won stub flags from Phases 2-3 into a real screen:
a ROUND_OVER state that shows "GAME OVER" or "YOU WIN!" and lets the
player press Enter to return to the main menu and start a new round.
Two-player mode is still out of scope for win/lose rules (Phase 5) --
this phase only wires up the single-player ending.

## Scope delivered

1. `game/game_state.py` -- added a `ROUND_OVER` state:
   - `end_round(message)` -- transitions PLAYING -> ROUND_OVER, storing
     the outcome text ("GAME OVER" or "YOU WIN!"). No effect unless
     currently PLAYING (so it is safe to call every frame once the flag
     is set).
   - `restart()` -- transitions ROUND_OVER -> MENU (resets selection,
     player count, and the stored message). No effect outside ROUND_OVER.
2. `game/renderer.py` -- `draw_round_over()`: a big centered outcome
   message plus a "Press Enter to return to the menu" hint. The message
   is highlighted in a different color on a win.
3. `main.py`:
   - Each frame, if `player_board.won` or `player_board.game_over` is
     set, calls `game_state.end_round(...)` with the right message.
   - In the ROUND_OVER state, Enter calls `game_state.restart()` and
     clears the boards, resizing the window back to the 1-player size
     and returning to the main menu.
   - Refactored board setup into a small `start_round()` helper, used
     both when first confirming the menu and (implicitly) whenever a
     new round starts after a restart.

## Out of scope for this phase

- Two-player win/lose rule ("if one player loses, the other wins") --
  Phase 5, once two-player boards actually have pieces and controls.
- Any restart confirmation dialog, high-score tracking, or animations
  on the round-over screen -- not requested, keeping this minimal.

## Unit tests

- `tests/test_game_state.py`: `end_round()` transitions from PLAYING and
  stores the message; is ignored from MENU; is ignored (a no-op) once
  already in ROUND_OVER (so a stray repeated call can't overwrite the
  message); `restart()` returns to MENU and clears `selected_index`,
  `player_count`, and `round_over_message`; `restart()` is ignored
  outside ROUND_OVER (e.g. while still PLAYING).
- All **68 tests** pass (63 from Phases 1-3 + 5 new) via
  `python -m unittest discover -s tests`.

## ASCII-only note

Per your request, this file and all other `tetris_battle_*.md` files
(plus two code comments that had stray characters) have been re-saved
using ASCII-only characters -- no em-dashes, arrows, or other non-ASCII
symbols. Going forward all `.md` files for this project will be written
this way.

## A note on testing pygame itself

Same limitation as before: no internet access in this sandbox, so
`pygame` could not be installed here. `main.py` and `renderer.py` were
checked with `python -m py_compile` only. Please run on your machine to
confirm the round-over screen looks right and Enter correctly returns
you to the menu and lets you start a fresh round.

## Definition of Done

- [ ] Losing (block-out) shows "GAME OVER".
- [ ] Reaching Level 30's score shows "YOU WIN!".
- [ ] Pressing Enter on either screen returns to the main menu.
- [ ] Starting a new round from the menu resets score/level/board fully.
- [ ] All unit tests pass.
- [ ] Plan reviewed and confirmed before Phase 5 (two-player mode:
      split-screen piece control, Player 2/WASD, 2P win/lose rule) begins.

## Addendum: line-clear flash (added after initial Phase 4 testing)

After testing, a line-clear flash was requested: a completed row should
blink for about 1 second before it is actually removed, instead of
disappearing instantly.

- `game/config.py`: `LINE_CLEAR_FLASH_DURATION` (1.0s), 
  `LINE_CLEAR_FLASH_BLINK_INTERVAL` (0.1s), `COLOR_LINE_FLASH` (white).
- `game/board.py`: new `full_row_indices()` (which rows are currently
  full, without clearing them).
- `game/player.py` (`PlayerBoard`):
  - Locking a piece that completes one or more rows now sets
    `is_flashing = True` and records `flash_rows` instead of clearing
    and scoring immediately. No new piece spawns yet, and moves/rotate/
    drop are frozen (same pattern as the `game_over`/`won` freeze).
  - A new `update(dt)` method must be called once per frame; once the
    flash duration elapses, it performs the actual clear, scoring, and
    leveling, then spawns the next piece (or ends the round).
  - `flash_on` (property) toggles on/off every `LINE_CLEAR_FLASH_BLINK_INTERVAL`
    seconds, for the renderer to blink the row.
- `game/renderer.py`: `draw_board()` now accepts `flash_rows`/`flash_on`
  and draws those rows solid white (on) or blanked (off) instead of
  their real contents while flashing. `draw_playing()` passes this
  through per board via a new `flashes` parameter.
- `main.py`: calls `player_board.update(dt)` every frame, pauses gravity
  while `is_flashing` is True, and hides the (already-locked) active
  piece during the flash so it isn't drawn twice.

### Additional unit tests

`tests/test_board.py` gained `full_row_indices()` coverage.
`tests/test_player.py` gained a `TestPlayerBoardLineClearFlash` class:
partial flash time does not clear early, enough accumulated time (via
several small `update()` steps, not just one big jump) does clear,
`update()` is a no-op when nothing is flashing, moves/rotate/drop are
frozen while flashing, and `flash_on` actually toggles between `True`
and `False` over time. The two existing tests that locked a piece into
a full row were updated to first assert the mid-flash state (nothing
scored/cleared yet) and then call `update(LINE_CLEAR_FLASH_DURATION)`
to finish the clear before checking the final score/level/win state.

All **75 tests** pass (68 before this addendum + 7 new), stable across
5 consecutive runs.

### Note

This addendum, this whole file, and the rest of the project's `.md`
files are ASCII-only, per your standing request from Phase 3.

## Addendum 2: softer blink, hard drop, and Escape confirm

After trying the flash, three more changes were requested:

1. **Softer blink**: `LINE_CLEAR_FLASH_BLINK_INTERVAL` changed from 0.1s
   to 0.2s (fewer, calmer toggles over the same 1-second flash).

2. **Hard drop**: `PlayerBoard.hard_drop()` moves the active piece down
   repeatedly until it can't move further, then locks it immediately
   (same locking/flash/scoring path as a normal `soft_drop` lock).
   Returns how many rows it fell. Wired to **Enter** for Player 1 during
   play. Player 2's **Space Bar** hard drop will be wired in Phase 5,
   once two-player pieces and controls exist -- `hard_drop()` itself is
   already generic per-`PlayerBoard`, so no further logic changes will
   be needed there, just the key binding.

3. **Escape confirm prompt**: Escape no longer quits immediately. It now
   opens a small prompt (a new `CONFIRM_EXIT` state in
   `game/game_state.py`) with three choices: **Resume**, **Back to Main
   Menu**, **Exit Game** -- navigated with Up/Down and chosen with
   Enter. Pressing Escape again while the prompt is open is a shortcut
   for Resume. This works from the main menu, mid-game, and the round-
   over screen alike. Choosing "Exit Game" sets a `should_quit` flag
   that `main.py` checks to close the window (rather than the state
   machine calling `sys.exit()` itself, which would make it impossible
   to unit test).

Note: because the game naturally only updates gravity/flash timers while
`game_state.state == PLAYING`, opening the Escape prompt automatically
pauses the falling piece and any in-progress line-clear flash -- no
extra pause logic was needed.

### Additional unit tests

`tests/test_player.py` gained a `TestPlayerBoardHardDrop` class: falling
to the correct lowest row and locking, dropping with zero travel when
already resting, starting a flash when the drop completes a row instead
of scoring immediately, and being ignored (returns 0) when the board
isn't active (game over, won, or already flashing).

`tests/test_game_state.py` gained a `TestGameStateConfirmExit` class
covering: opening the prompt from MENU and PLAYING; the prompt being
idempotent (a repeated Escape doesn't lose the original state or reset
the selection); wrapping selection up/down; choosing each of the three
options (Resume returns to the prior state, Back to Main Menu resets
like `restart()`, Exit Game sets `should_quit`); the prompt's actions
being no-ops outside `CONFIRM_EXIT`; and canceling (a second Escape)
correctly returning to PLAYING or ROUND_OVER as appropriate.

All **92 tests** pass (75 before this addendum + 17 new), stable across
5 consecutive runs.

### A note on what wasn't changed

The Escape prompt currently always shows all three options, even when
opened from the main menu itself (where "Back to Main Menu" is a bit
redundant with "Resume"). Left as-is for simplicity/consistency; happy
to trim it to just "Resume" / "Exit Game" when opened from the menu if
you'd prefer.
