import unittest

from game.player import PlayerBoard
from game.tetrimino import Tetrimino
from game.config import (
    MAX_LEVEL,
    fall_interval_for_level,
    cumulative_score_to_complete_level,
    LINE_CLEAR_FLASH_DURATION,
    LINE_CLEAR_FLASH_BLINK_INTERVAL,
)


class TestPlayerBoardSpawnAndMovement(unittest.TestCase):
    def test_initial_active_piece_matches_sequence(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        self.assertEqual(pb.active_piece.type, "O")
        self.assertTrue(pb.board.all_cells_empty())
        self.assertFalse(pb.game_over)

    def test_move_left_and_right_within_bounds(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        start_x = pb.active_piece.x
        self.assertTrue(pb.move(-1, 0))
        self.assertEqual(pb.active_piece.x, start_x - 1)
        self.assertTrue(pb.move(1, 0))
        self.assertEqual(pb.active_piece.x, start_x)

    def test_move_blocked_at_left_wall(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        # Walk the piece all the way to the left wall.
        while pb.move(-1, 0):
            pass
        self.assertEqual(pb.active_piece.x, 0)
        blocked_x = pb.active_piece.x
        self.assertFalse(pb.move(-1, 0))
        self.assertEqual(pb.active_piece.x, blocked_x)

    def test_move_blocked_at_right_wall(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        while pb.move(1, 0):
            pass
        cells_x = [x for x, _y in pb.active_piece.cells()]
        self.assertEqual(max(cells_x), pb.board.width - 1)
        self.assertFalse(pb.move(1, 0))

    def test_move_down_without_locking_when_space_available(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        start_y = pb.active_piece.y
        moved = pb.move(0, 1)
        self.assertTrue(moved)
        self.assertEqual(pb.active_piece.y, start_y + 1)
        # Still the same piece, not locked into the board.
        self.assertTrue(pb.board.all_cells_empty())


class TestPlayerBoardNextPiecePreview(unittest.TestCase):
    def test_next_piece_type_is_the_second_queued_piece(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O", "I"])
        self.assertEqual(pb.active_piece.type, "O")
        self.assertEqual(pb.next_piece_type, "I")

    def test_next_piece_becomes_active_after_a_lock_and_refills(self):
        pb = PlayerBoard(board_width=9, board_height=4, piece_sequence=["O", "I", "T"])
        self.assertEqual(pb.active_piece.type, "O")
        self.assertEqual(pb.next_piece_type, "I")

        pb.hard_drop()  # locks the O piece; no full rows on a 9-wide board

        self.assertEqual(pb.active_piece.type, "I")
        self.assertEqual(pb.next_piece_type, "T")

    def test_next_piece_type_unchanged_while_flashing(self):
        pb = PlayerBoard(board_width=4, board_height=2, piece_sequence=["O", "I", "T"])
        pb.board.set_cell(0, 0, "pre")
        pb.board.set_cell(3, 0, "pre")
        pb.board.set_cell(0, 1, "pre")
        pb.board.set_cell(3, 1, "pre")

        pb.soft_drop()  # locks + starts flashing; no spawn yet

        self.assertTrue(pb.is_flashing)
        self.assertEqual(pb.next_piece_type, "I")  # not consumed until the flash ends


class TestPlayerBoardHardDrop(unittest.TestCase):
    def test_hard_drop_falls_to_lowest_row_and_locks(self):
        # height=5: an O piece (2 rows tall) spawned at y=0 can fall until
        # its bottom row is row 4, i.e. from y=0 to y=3 -- 3 rows of travel.
        pb = PlayerBoard(board_width=9, board_height=5, piece_sequence=["O", "O"])
        rows_dropped = pb.hard_drop()
        self.assertEqual(rows_dropped, 3)
        self.assertFalse(pb.board.all_cells_empty())
        for x, y in [(3, 3), (4, 3), (3, 4), (4, 4)]:
            self.assertIsNotNone(pb.board.get_cell(x, y))
        self.assertEqual(pb.active_piece.type, "O")  # the next queued piece spawned

    def test_hard_drop_when_already_resting_locks_with_zero_travel(self):
        pb = PlayerBoard(board_width=9, board_height=2, piece_sequence=["O", "O"])
        rows_dropped = pb.hard_drop()
        self.assertEqual(rows_dropped, 0)
        for x, y in [(3, 0), (4, 0), (3, 1), (4, 1)]:
            self.assertIsNotNone(pb.board.get_cell(x, y))

    def test_hard_drop_starts_flash_when_it_completes_rows(self):
        pb = PlayerBoard(board_width=4, board_height=2, piece_sequence=["O", "O"])
        pb.board.set_cell(0, 0, "pre")
        pb.board.set_cell(3, 0, "pre")
        pb.board.set_cell(0, 1, "pre")
        pb.board.set_cell(3, 1, "pre")

        pb.hard_drop()

        self.assertTrue(pb.is_flashing)
        self.assertEqual(pb.score, 0)  # not scored until the flash finishes

    def test_hard_drop_ignored_when_not_active(self):
        pb = PlayerBoard(board_width=9, board_height=2, piece_sequence=["O", "O"])
        pb.soft_drop()  # locks immediately (height 2) -> game_over
        self.assertTrue(pb.game_over)
        self.assertEqual(pb.hard_drop(), 0)


class TestPlayerBoardRotation(unittest.TestCase):
    def test_rotate_advances_rotation_index(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["T"])
        self.assertEqual(pb.active_piece.rotation_index, 0)
        self.assertTrue(pb.rotate())
        self.assertEqual(pb.active_piece.rotation_index, 1)

    def test_rotate_rejected_when_it_would_leave_the_board(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["L"])
        # Manually place the piece near the right wall in a rotation state
        # whose *next* state would stick out past the board edge.
        pb.active_piece = Tetrimino("L", x=7, y=0, rotation=2)
        self.assertFalse(pb._collides(pb.active_piece))  # sanity: current spot is legal

        rotated_ok = pb.rotate()

        self.assertFalse(rotated_ok)
        self.assertEqual(pb.active_piece.rotation_index, 2)
        self.assertEqual(pb.active_piece.x, 7)


class TestPlayerBoardLockingAndGameOver(unittest.TestCase):
    def test_soft_drop_locks_piece_and_spawns_next(self):
        pb = PlayerBoard(board_width=9, board_height=4, piece_sequence=["O", "I"])
        self.assertTrue(pb.soft_drop())  # y: 0 -> 1
        self.assertTrue(pb.soft_drop())  # y: 1 -> 2
        locked = pb.soft_drop()          # blocked -> locks, spawns "I"
        self.assertFalse(locked)
        self.assertFalse(pb.game_over)
        self.assertEqual(pb.active_piece.type, "I")
        # The O piece should have locked in at rows 2-3, columns 3-4.
        for x, y in [(3, 2), (4, 2), (3, 3), (4, 3)]:
            self.assertIsNotNone(pb.board.get_cell(x, y))

    def test_game_over_when_spawn_immediately_collides(self):
        pb = PlayerBoard(board_width=9, board_height=2, piece_sequence=["O", "O"])
        locked = pb.soft_drop()  # no room to move down at all -> locks immediately
        self.assertFalse(locked)
        self.assertTrue(pb.game_over)
        for x, y in [(3, 0), (4, 0), (3, 1), (4, 1)]:
            self.assertIsNotNone(pb.board.get_cell(x, y))

    def test_moves_and_rotation_ignored_after_game_over(self):
        pb = PlayerBoard(board_width=9, board_height=2, piece_sequence=["O", "O"])
        pb.soft_drop()
        self.assertTrue(pb.game_over)
        self.assertFalse(pb.move(-1, 0))
        self.assertFalse(pb.rotate())
        self.assertFalse(pb.soft_drop())


class TestPlayerBoardScoringAndLeveling(unittest.TestCase):
    def test_no_score_change_when_no_line_clears(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.soft_drop()
        self.assertEqual(pb.score, 0)
        self.assertEqual(pb.level, 1)
        self.assertEqual(pb.lines_cleared_total, 0)

    def test_locking_clears_full_rows_and_scores_them(self):
        # width=4, height=2: an O piece fills the middle two columns of
        # both rows; pre-filling the two outer columns completes both rows.
        # A second "O" is queued for the next spawn, since this 2-row board
        # is too short for any other piece type to spawn without colliding
        # with the board edges (irrelevant on the real 18-row board).
        pb = PlayerBoard(board_width=4, board_height=2, piece_sequence=["O", "O"])
        pb.board.set_cell(0, 0, "pre")
        pb.board.set_cell(3, 0, "pre")
        pb.board.set_cell(0, 1, "pre")
        pb.board.set_cell(3, 1, "pre")

        moved = pb.soft_drop()  # can't move down (height=2) -> locks + starts flashing

        self.assertFalse(moved)
        # Locking completed rows starts a flash; nothing is scored/cleared yet.
        self.assertTrue(pb.is_flashing)
        self.assertEqual(sorted(pb.flash_rows), [0, 1])
        self.assertEqual(pb.score, 0)
        self.assertEqual(pb.lines_cleared_total, 0)
        self.assertFalse(pb.board.all_cells_empty())

        pb.update(LINE_CLEAR_FLASH_DURATION)  # flash finishes -> rows actually clear

        self.assertFalse(pb.is_flashing)
        self.assertEqual(pb.lines_cleared_total, 2)
        self.assertEqual(pb.score, 3)  # LINE_CLEAR_SCORES[2] == 3
        self.assertTrue(pb.board.all_cells_empty())  # both rows cleared
        self.assertFalse(pb.game_over)

    def test_level_advances_when_cumulative_threshold_reached(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.score = 30
        pb._maybe_advance_level()
        self.assertEqual(pb.level, 2)

    def test_level_does_not_advance_below_threshold(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.score = 29
        pb._maybe_advance_level()
        self.assertEqual(pb.level, 1)

    def test_level_can_advance_multiple_steps_at_once(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.score = cumulative_score_to_complete_level(3)
        pb._maybe_advance_level()
        self.assertEqual(pb.level, 4)

    def test_fall_interval_tracks_level(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        self.assertAlmostEqual(pb.fall_interval, fall_interval_for_level(1))
        pb.level = 5
        self.assertAlmostEqual(pb.fall_interval, fall_interval_for_level(5))

    def test_win_flag_set_at_max_level_threshold(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.level = MAX_LEVEL
        pb.score = cumulative_score_to_complete_level(MAX_LEVEL)
        pb._maybe_advance_level()
        self.assertTrue(pb.won)

    def test_win_stub_locks_final_piece_without_spawning_new_one(self):
        pb = PlayerBoard(board_width=4, board_height=2, piece_sequence=["O"])
        pb.level = MAX_LEVEL
        # One 2-line clear (worth 3 points) away from the win threshold.
        pb.score = cumulative_score_to_complete_level(MAX_LEVEL) - 3
        pb.board.set_cell(0, 0, "pre")
        pb.board.set_cell(3, 0, "pre")
        pb.board.set_cell(0, 1, "pre")
        pb.board.set_cell(3, 1, "pre")
        piece_before = pb.active_piece

        pb.soft_drop()  # locks and starts flashing; not won yet
        self.assertTrue(pb.is_flashing)
        self.assertFalse(pb.won)

        pb.update(LINE_CLEAR_FLASH_DURATION)  # flash finishes -> score/level applied

        self.assertTrue(pb.won)
        self.assertFalse(pb.game_over)
        self.assertIs(pb.active_piece, piece_before)  # no new piece spawned

    def test_moves_ignored_after_win(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.level = MAX_LEVEL
        pb.score = cumulative_score_to_complete_level(MAX_LEVEL)
        pb._maybe_advance_level()
        self.assertTrue(pb.won)
        self.assertFalse(pb.move(-1, 0))
        self.assertFalse(pb.rotate())
        self.assertFalse(pb.soft_drop())


class TestPlayerBoardLineClearFlash(unittest.TestCase):
    def _make_ready_to_clear(self):
        """A 4x2 board one soft_drop away from completing both rows."""
        pb = PlayerBoard(board_width=4, board_height=2, piece_sequence=["O", "I"])
        pb.board.set_cell(0, 0, "pre")
        pb.board.set_cell(3, 0, "pre")
        pb.board.set_cell(0, 1, "pre")
        pb.board.set_cell(3, 1, "pre")
        return pb

    def test_partial_flash_time_does_not_clear_yet(self):
        pb = self._make_ready_to_clear()
        pb.soft_drop()
        self.assertTrue(pb.is_flashing)

        pb.update(LINE_CLEAR_FLASH_DURATION / 2)

        self.assertTrue(pb.is_flashing)
        self.assertEqual(pb.score, 0)
        self.assertFalse(pb.board.all_cells_empty())

    def test_flash_completes_after_enough_accumulated_time(self):
        pb = self._make_ready_to_clear()
        pb.soft_drop()
        # Simulate several small frame steps rather than one big jump.
        step = LINE_CLEAR_FLASH_DURATION / 4
        for _ in range(3):
            pb.update(step)
            self.assertTrue(pb.is_flashing)
        pb.update(step + 0.001)  # pushes total time just past the duration

        self.assertFalse(pb.is_flashing)
        self.assertEqual(pb.score, 3)
        self.assertTrue(pb.board.all_cells_empty())

    def test_update_is_a_no_op_when_not_flashing(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        pb.update(5.0)  # large dt, but nothing is flashing
        self.assertFalse(pb.is_flashing)
        self.assertEqual(pb.score, 0)

    def test_moves_and_drop_ignored_while_flashing(self):
        pb = self._make_ready_to_clear()
        pb.soft_drop()
        self.assertTrue(pb.is_flashing)
        self.assertFalse(pb.move(-1, 0))
        self.assertFalse(pb.rotate())
        self.assertFalse(pb.soft_drop())
        self.assertEqual(pb.hard_drop(), 0)

    def test_flash_on_toggles_over_time(self):
        pb = self._make_ready_to_clear()
        pb.soft_drop()
        seen = set()
        step = LINE_CLEAR_FLASH_BLINK_INTERVAL / 2
        for _ in range(6):
            seen.add(pb.flash_on)
            pb.update(step)
        self.assertIn(True, seen)
        self.assertIn(False, seen)

    def test_flash_on_is_false_when_not_flashing(self):
        pb = PlayerBoard(board_width=9, board_height=18, piece_sequence=["O"])
        self.assertFalse(pb.flash_on)


if __name__ == "__main__":
    unittest.main()
