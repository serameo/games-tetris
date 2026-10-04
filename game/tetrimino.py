"""Tetrimino shapes and the piece object that falls on the board.

No pygame dependency, so this can be unit tested without a display.

Each shape is stored as a list of rotation states. A rotation state is a
list of (dx, dy) integer offsets, relative to the piece's own (x, y)
anchor, describing which cells are filled. Rotating moves to the next
state in the list (wrapping around); there is no wall-kick system, so a
rotation that would collide is simply rejected by the caller.
"""

from typing import List, Tuple

from game.config import (
    COLOR_PIECE_O,
    COLOR_PIECE_I,
    COLOR_PIECE_S,
    COLOR_PIECE_Z,
    COLOR_PIECE_T,
    COLOR_PIECE_L,
    COLOR_PIECE_J,
)

Offset = Tuple[int, int]


class Tetrimino:
    """A single falling piece: a type, position, and rotation state."""

    # Shapes match the orientations given in the original game spec.
    SHAPES = {
        "O": {
            "color": COLOR_PIECE_O,
            "rotations": [
                [(0, 0), (1, 0), (0, 1), (1, 1)],
            ],
        },
        "I": {
            "color": COLOR_PIECE_I,
            "rotations": [
                [(0, 0), (1, 0), (2, 0), (3, 0)],  # horizontal
                [(0, 0), (0, 1), (0, 2), (0, 3)],  # vertical
            ],
        },
        "S": {
            "color": COLOR_PIECE_S,
            "rotations": [
                [(1, 0), (2, 0), (0, 1), (1, 1)],  # horizontal
                [(0, 0), (0, 1), (1, 1), (1, 2)],  # vertical
            ],
        },
        "Z": {
            "color": COLOR_PIECE_Z,
            "rotations": [
                [(0, 0), (1, 0), (1, 1), (2, 1)],  # horizontal
                [(1, 0), (0, 1), (1, 1), (0, 2)],  # vertical
            ],
        },
        "T": {
            "color": COLOR_PIECE_T,
            "rotations": [
                [(0, 0), (1, 0), (2, 0), (1, 1)],  # nub pointing down
                [(0, 0), (0, 1), (1, 1), (0, 2)],  # nub pointing right
                [(1, 0), (0, 1), (1, 1), (2, 1)],  # nub pointing up
                [(1, 0), (0, 1), (1, 1), (1, 2)],  # nub pointing left
            ],
        },
        "L": {
            "color": COLOR_PIECE_L,
            "rotations": [
                [(0, 0), (0, 1), (0, 2), (1, 2)],
                [(0, 0), (1, 0), (2, 0), (0, 1)],
                [(0, 0), (1, 0), (1, 1), (1, 2)],
                [(2, 0), (0, 1), (1, 1), (2, 1)],
            ],
        },
        "J": {
            "color": COLOR_PIECE_J,
            "rotations": [
                [(1, 0), (1, 1), (0, 2), (1, 2)],
                [(0, 0), (0, 1), (1, 1), (2, 1)],
                [(0, 0), (1, 0), (0, 1), (0, 2)],
                [(0, 0), (1, 0), (2, 0), (2, 1)],
            ],
        },
    }

    def __init__(self, piece_type: str, x: int, y: int, rotation: int = 0):
        if piece_type not in self.SHAPES:
            raise ValueError(f"Unknown piece type: {piece_type!r}")
        self.type = piece_type
        self.x = x
        self.y = y
        num_rotations = len(self.SHAPES[piece_type]["rotations"])
        self.rotation_index = rotation % num_rotations

    @property
    def color(self):
        return self.SHAPES[self.type]["color"]

    def cells(self) -> List[Offset]:
        """Absolute (x, y) board coordinates occupied by this piece."""
        shape = self.SHAPES[self.type]["rotations"][self.rotation_index]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]

    def moved(self, dx: int, dy: int) -> "Tetrimino":
        """Return a new Tetrimino translated by (dx, dy); does not check collisions."""
        return Tetrimino(self.type, self.x + dx, self.y + dy, self.rotation_index)

    def rotated(self) -> "Tetrimino":
        """Return a new Tetrimino advanced to the next rotation state.

        Does not check collisions; the caller is responsible for rejecting
        the result if it would overlap the board or go out of bounds.
        """
        num_rotations = len(self.SHAPES[self.type]["rotations"])
        next_index = (self.rotation_index + 1) % num_rotations
        return Tetrimino(self.type, self.x, self.y, next_index)

    @classmethod
    def spawn(cls, piece_type: str, board_width: int, rotation: int = 0) -> "Tetrimino":
        """Create a new piece horizontally centered at the top of the board."""
        rotations = cls.SHAPES[piece_type]["rotations"]
        shape = rotations[rotation % len(rotations)]
        bbox_width = max(dx for dx, _dy in shape) + 1
        spawn_x = (board_width - bbox_width) // 2
        return cls(piece_type, x=spawn_x, y=0, rotation=rotation)


PIECE_TYPES: List[str] = list(Tetrimino.SHAPES.keys())
