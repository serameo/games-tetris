"""Board grid for a single player's play field.

No pygame dependency, so this can be unit tested without a display.
"""

from typing import List, Optional, Tuple

from game.config import BOARD_WIDTH, BOARD_HEIGHT


class Board:
    """A width x height grid of cells.

    Each cell is either None (empty) or a value identifying the locked
    Tetrimino block occupying it (e.g. a color). In Phase 1 the board is
    always empty; locking pieces into it is added in a later phase.
    """

    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT):
        if width <= 0 or height <= 0:
            raise ValueError("Board width and height must be positive")
        self.width = width
        self.height = height
        self._grid = [[None for _ in range(width)] for _ in range(height)]

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Optional[object]:
        """Return the contents of cell (x, y); None means empty.

        Raises IndexError if (x, y) is outside the board.
        """
        if not self.is_in_bounds(x, y):
            raise IndexError(
                f"Cell ({x}, {y}) is out of bounds for a "
                f"{self.width}x{self.height} board"
            )
        return self._grid[y][x]

    def set_cell(self, x: int, y: int, value: Optional[object]) -> None:
        """Set the contents of cell (x, y).

        Raises IndexError if (x, y) is outside the board.
        """
        if not self.is_in_bounds(x, y):
            raise IndexError(
                f"Cell ({x}, {y}) is out of bounds for a "
                f"{self.width}x{self.height} board"
            )
        self._grid[y][x] = value

    def is_empty(self, x: int, y: int) -> bool:
        return self.get_cell(x, y) is None

    def all_cells_empty(self) -> bool:
        return all(cell is None for row in self._grid for cell in row)

    def is_row_full(self, y: int) -> bool:
        if not (0 <= y < self.height):
            raise IndexError(f"Row {y} is out of bounds for height {self.height}")
        return all(cell is not None for cell in self._grid[y])

    def full_row_indices(self) -> List[int]:
        """Return the (0-indexed) row numbers that are currently full."""
        return [y for y in range(self.height) if self.is_row_full(y)]

    def clear_full_rows(self) -> int:
        """Remove every full row, shifting the rows above it down.

        New empty rows are inserted at the top to keep the board's size
        constant. Returns the number of rows cleared.
        """
        kept_rows = [row for row in self._grid if not all(cell is not None for cell in row)]
        cleared = self.height - len(kept_rows)
        if cleared:
            new_rows = [[None for _ in range(self.width)] for _ in range(cleared)]
            self._grid = new_rows + kept_rows
        return cleared

    def dimensions(self) -> Tuple[int, int]:
        return self.width, self.height
