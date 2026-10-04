import unittest

from game.board import Board
from game.config import BOARD_WIDTH, BOARD_HEIGHT


class TestBoard(unittest.TestCase):
    def test_default_dimensions(self):
        board = Board()
        self.assertEqual(board.dimensions(), (BOARD_WIDTH, BOARD_HEIGHT))

    def test_custom_dimensions(self):
        board = Board(width=5, height=10)
        self.assertEqual(board.dimensions(), (5, 10))

    def test_starts_all_empty(self):
        board = Board()
        self.assertTrue(board.all_cells_empty())
        for y in range(board.height):
            for x in range(board.width):
                self.assertIsNone(board.get_cell(x, y))

    def test_set_and_get_cell(self):
        board = Board()
        board.set_cell(3, 4, "yellow")
        self.assertEqual(board.get_cell(3, 4), "yellow")
        self.assertFalse(board.all_cells_empty())

    def test_is_empty(self):
        board = Board()
        self.assertTrue(board.is_empty(0, 0))
        board.set_cell(0, 0, "red")
        self.assertFalse(board.is_empty(0, 0))

    def test_out_of_bounds_get_raises(self):
        board = Board()
        with self.assertRaises(IndexError):
            board.get_cell(-1, 0)
        with self.assertRaises(IndexError):
            board.get_cell(0, -1)
        with self.assertRaises(IndexError):
            board.get_cell(board.width, 0)
        with self.assertRaises(IndexError):
            board.get_cell(0, board.height)

    def test_out_of_bounds_set_raises(self):
        board = Board()
        with self.assertRaises(IndexError):
            board.set_cell(-1, 0, "blue")
        with self.assertRaises(IndexError):
            board.set_cell(0, board.height, "blue")

    def test_invalid_dimensions_raise(self):
        with self.assertRaises(ValueError):
            Board(width=0, height=10)
        with self.assertRaises(ValueError):
            Board(width=10, height=-1)


class TestBoardLineClearing(unittest.TestCase):
    def test_no_full_rows_clears_nothing(self):
        board = Board(width=4, height=4)
        board.set_cell(0, 3, "x")
        cleared = board.clear_full_rows()
        self.assertEqual(cleared, 0)
        self.assertEqual(board.get_cell(0, 3), "x")

    def test_is_row_full(self):
        board = Board(width=3, height=2)
        self.assertFalse(board.is_row_full(0))
        for x in range(3):
            board.set_cell(x, 0, "x")
        self.assertTrue(board.is_row_full(0))
        self.assertFalse(board.is_row_full(1))

    def test_is_row_full_out_of_bounds_raises(self):
        board = Board(width=3, height=2)
        with self.assertRaises(IndexError):
            board.is_row_full(5)

    def test_full_row_indices(self):
        board = Board(width=2, height=3)
        self.assertEqual(board.full_row_indices(), [])
        for x in range(2):
            board.set_cell(x, 1, "x")
        self.assertEqual(board.full_row_indices(), [1])
        for x in range(2):
            board.set_cell(x, 2, "y")
        self.assertEqual(board.full_row_indices(), [1, 2])

    def test_clear_single_full_row(self):
        board = Board(width=3, height=3)
        for x in range(3):
            board.set_cell(x, 2, "x")  # bottom row full
        board.set_cell(0, 1, "y")      # a cell above, should shift down
        cleared = board.clear_full_rows()
        self.assertEqual(cleared, 1)
        # The row that was above the cleared row is now the bottom row.
        self.assertEqual(board.get_cell(0, 2), "y")
        self.assertTrue(board.all_cells_empty() is False)
        # Top rows are now empty (new rows inserted at the top).
        self.assertTrue(all(board.get_cell(x, 0) is None for x in range(3)))

    def test_clear_multiple_full_rows_preserves_order(self):
        board = Board(width=2, height=4)
        # Fill rows 1 and 3 fully; row 0 has a marker cell; row 2 empty.
        board.set_cell(0, 0, "top")
        for x in range(2):
            board.set_cell(x, 1, "full1")
        for x in range(2):
            board.set_cell(x, 3, "full3")
        cleared = board.clear_full_rows()
        self.assertEqual(cleared, 2)
        # Remaining non-full rows (original row 0 and row 2) shift down by
        # the number of rows cleared, keeping their relative order, with
        # new empty rows inserted on top.
        self.assertIsNone(board.get_cell(0, 0))
        self.assertIsNone(board.get_cell(1, 0))
        self.assertIsNone(board.get_cell(0, 1))
        self.assertIsNone(board.get_cell(1, 1))
        self.assertEqual(board.get_cell(0, 2), "top")  # original row 0
        self.assertIsNone(board.get_cell(0, 3))         # original (empty) row 2


if __name__ == "__main__":
    unittest.main()
