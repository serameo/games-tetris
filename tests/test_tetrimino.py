import unittest

from game.tetrimino import Tetrimino, PIECE_TYPES


class TestTetriminoCells(unittest.TestCase):
    def test_o_piece_cells_at_origin(self):
        piece = Tetrimino("O", x=0, y=0)
        self.assertEqual(set(piece.cells()), {(0, 0), (1, 0), (0, 1), (1, 1)})

    def test_cells_translate_with_position(self):
        piece = Tetrimino("O", x=3, y=5)
        self.assertEqual(set(piece.cells()), {(3, 5), (4, 5), (3, 6), (4, 6)})

    def test_unknown_piece_type_raises(self):
        with self.assertRaises(ValueError):
            Tetrimino("X", x=0, y=0)


class TestTetriminoMovement(unittest.TestCase):
    def test_moved_returns_new_translated_piece(self):
        piece = Tetrimino("I", x=2, y=0, rotation=0)
        moved = piece.moved(1, 2)
        self.assertEqual((moved.x, moved.y), (3, 2))
        # Original is untouched (immutable-style API)
        self.assertEqual((piece.x, piece.y), (2, 0))

    def test_moved_keeps_rotation(self):
        piece = Tetrimino("I", x=2, y=0, rotation=1)
        moved = piece.moved(0, 1)
        self.assertEqual(moved.rotation_index, 1)


class TestTetriminoRotation(unittest.TestCase):
    def test_o_piece_rotation_is_a_no_op_shape(self):
        piece = Tetrimino("O", x=0, y=0)
        rotated = piece.rotated()
        self.assertEqual(set(rotated.cells()), set(piece.cells()))

    def test_i_piece_cycles_between_two_states(self):
        piece = Tetrimino("I", x=0, y=0, rotation=0)
        once = piece.rotated()
        twice = once.rotated()
        self.assertEqual(once.rotation_index, 1)
        self.assertEqual(twice.rotation_index, 0)
        self.assertEqual(set(twice.cells()), set(piece.cells()))

    def test_t_piece_cycles_through_four_states(self):
        piece = Tetrimino("T", x=0, y=0, rotation=0)
        indices = [piece.rotation_index]
        current = piece
        for _ in range(4):
            current = current.rotated()
            indices.append(current.rotation_index)
        self.assertEqual(indices, [0, 1, 2, 3, 0])

    def test_rotation_does_not_mutate_original(self):
        piece = Tetrimino("T", x=0, y=0, rotation=0)
        piece.rotated()
        self.assertEqual(piece.rotation_index, 0)


class TestTetriminoSpawn(unittest.TestCase):
    def test_spawn_is_horizontally_centered_on_board(self):
        piece = Tetrimino.spawn("O", board_width=9)
        self.assertEqual(piece.y, 0)
        xs = [x for x, _y in piece.cells()]
        self.assertEqual(min(xs), 3)
        self.assertEqual(max(xs), 4)

    def test_spawn_i_piece_horizontal_centered(self):
        piece = Tetrimino.spawn("I", board_width=9, rotation=0)
        xs = [x for x, _y in piece.cells()]
        self.assertEqual(min(xs), 2)
        self.assertEqual(max(xs), 5)

    def test_spawn_all_piece_types_stay_in_bounds(self):
        board_width = 9
        for piece_type in PIECE_TYPES:
            for rotation in range(len(Tetrimino.SHAPES[piece_type]["rotations"])):
                piece = Tetrimino.spawn(piece_type, board_width, rotation=rotation)
                for x, _y in piece.cells():
                    self.assertGreaterEqual(x, 0)
                    self.assertLess(x, board_width)


if __name__ == "__main__":
    unittest.main()
