"""Per-player game logic: a board, the falling Tetrimino, scoring and level.

No pygame dependency, so this can be unit tested without a display.

Full game-over/win *screens* are handled one level up (game_state.py /
main.py). Here, `game_over` and `won` are simple flags: once either is
True, the board stops responding to moves/rotation/drop.

Line clears are not instant: locking a piece that completes one or more
rows enters a brief "flashing" state (is_flashing=True) during which
those rows blink but are not yet removed and no new piece is spawned.
The caller must call `update(dt)` every frame so the flash can time out
and the actual clear (scoring, leveling, next spawn) can happen.

`next_piece_type` always holds the type of whichever piece will spawn
next, one piece ahead of `active_piece`, so a renderer can show a
"next piece" preview.
"""

import random
from typing import List, Optional, Sequence

from game.board import Board
from game.config import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    MAX_LEVEL,
    LINE_CLEAR_SCORES,
    LINE_CLEAR_FLASH_DURATION,
    LINE_CLEAR_FLASH_BLINK_INTERVAL,
    fall_interval_for_level,
    cumulative_score_to_complete_level,
)
from game.tetrimino import Tetrimino, PIECE_TYPES


class PlayerBoard:
    """Owns one player's Board, active Tetrimino, score, and level."""

    def __init__(
        self,
        board_width: int = BOARD_WIDTH,
        board_height: int = BOARD_HEIGHT,
        rng: Optional[random.Random] = None,
        piece_sequence: Optional[Sequence[str]] = None,
    ):
        self.board = Board(board_width, board_height)
        self._rng = rng or random.Random()
        # If given, pieces are drawn from this list first (in order) --
        # used by tests for deterministic piece sequences. Once the list
        # is exhausted, drawing falls back to the random generator.
        self._piece_queue: List[str] = list(piece_sequence) if piece_sequence else []
        self.game_over = False
        self.won = False
        self.score = 0        # cumulative, never resets
        self.level = 1
        self.lines_cleared_total = 0

        # Line-clear flash state.
        self.is_flashing = False
        self.flash_rows: List[int] = []
        self.flash_timer = 0.0

        # One piece is drawn for the active piece, and one more up front
        # so `next_piece_type` is always ready for a preview.
        self.active_piece: Tetrimino = self._spawn_piece(self._draw_piece_type())
        self.next_piece_type: str = self._draw_piece_type()

    # --- piece spawning ----------------------------------------------------

    def _draw_piece_type(self) -> str:
        """Pull the next raw piece type from the test queue, or at random."""
        if self._piece_queue:
            return self._piece_queue.pop(0)
        return self._rng.choice(PIECE_TYPES)

    def _spawn_piece(self, piece_type: str) -> Tetrimino:
        return Tetrimino.spawn(piece_type, self.board.width)

    def _collides(self, piece: Tetrimino) -> bool:
        for x, y in piece.cells():
            if not self.board.is_in_bounds(x, y):
                return True
            if not self.board.is_empty(x, y):
                return True
        return False

    # --- player actions ------------------------------------------------------

    def _is_active(self) -> bool:
        return not self.game_over and not self.won and not self.is_flashing

    def move(self, dx: int, dy: int) -> bool:
        """Try to translate the active piece. Returns True if it moved."""
        if not self._is_active():
            return False
        candidate = self.active_piece.moved(dx, dy)
        if self._collides(candidate):
            return False
        self.active_piece = candidate
        return True

    def rotate(self) -> bool:
        """Try to rotate the active piece one step. Returns True if it rotated."""
        if not self._is_active():
            return False
        candidate = self.active_piece.rotated()
        if self._collides(candidate):
            return False
        self.active_piece = candidate
        return True

    def soft_drop(self) -> bool:
        """Try to move the active piece down one row.

        If it can move down, it does, and this returns True. If it is
        blocked, the piece is locked into the board. If that completes
        one or more rows, a flash is started (see `update`) instead of
        clearing immediately; otherwise the next piece spawns right away.
        Either way this returns False when the piece did not move down.
        """
        if not self._is_active():
            return False
        if self.move(0, 1):
            return True
        self._lock_active_piece()
        return False

    def hard_drop(self) -> int:
        """Instantly drop the active piece to its lowest valid row, then lock it.

        Locking proceeds exactly as with `soft_drop` (may start a line-clear
        flash instead of spawning immediately). Returns how many rows the
        piece fell; 0 if the piece was already resting or the board isn't
        currently accepting input (game over, won, or mid-flash).
        """
        if not self._is_active():
            return 0
        rows_dropped = 0
        while self.move(0, 1):
            rows_dropped += 1
        self._lock_active_piece()
        return rows_dropped

    def update(self, dt: float) -> None:
        """Advance time-based state. Must be called once per frame.

        Currently this only drives the line-clear flash timer; call it
        regardless of whether a flash is active (it is a no-op otherwise).
        """
        if not self.is_flashing:
            return
        self.flash_timer += dt
        if self.flash_timer >= LINE_CLEAR_FLASH_DURATION:
            self._finish_line_clear()

    @property
    def flash_on(self) -> bool:
        """Whether the flashing rows should currently render "lit" (for blinking)."""
        if not self.is_flashing:
            return False
        toggles = int(self.flash_timer / LINE_CLEAR_FLASH_BLINK_INTERVAL)
        return toggles % 2 == 0

    # --- locking, scoring, leveling ------------------------------------------

    @property
    def fall_interval(self) -> float:
        """Current drop interval in seconds, based on the player's level."""
        return fall_interval_for_level(self.level)

    def _lock_active_piece(self) -> None:
        for x, y in self.active_piece.cells():
            self.board.set_cell(x, y, self.active_piece.color)

        full_rows = self.board.full_row_indices()
        if full_rows:
            # Don't clear or score yet -- let the rows flash first.
            self.is_flashing = True
            self.flash_rows = full_rows
            self.flash_timer = 0.0
            return

        self._spawn_next_piece_or_end_game()

    def _finish_line_clear(self) -> None:
        lines_cleared = self.board.clear_full_rows()
        self.is_flashing = False
        self.flash_rows = []
        self.flash_timer = 0.0

        if lines_cleared:
            self.lines_cleared_total += lines_cleared
            self.score += LINE_CLEAR_SCORES.get(lines_cleared, 0)
            self._maybe_advance_level()

        if self.won:
            # Level 30's score requirement was just reached: the game is won,
            # so no further piece is spawned.
            return

        self._spawn_next_piece_or_end_game()

    def _spawn_next_piece_or_end_game(self) -> None:
        piece_type = self.next_piece_type
        self.next_piece_type = self._draw_piece_type()
        new_piece = self._spawn_piece(piece_type)
        if self._collides(new_piece):
            self.game_over = True
            # Leave active_piece as-is so rendering doesn't crash; a real
            # GAME_OVER screen is driven by game_state.py / main.py.
        else:
            self.active_piece = new_piece

    def _maybe_advance_level(self) -> None:
        while self.level < MAX_LEVEL and self.score >= cumulative_score_to_complete_level(self.level):
            self.level += 1
        if self.level == MAX_LEVEL and self.score >= cumulative_score_to_complete_level(MAX_LEVEL):
            self.won = True
