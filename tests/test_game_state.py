import unittest

from game.game_state import GameState, State


class TestGameState(unittest.TestCase):
    def test_starts_in_menu(self):
        gs = GameState()
        self.assertEqual(gs.state, State.MENU)
        self.assertEqual(gs.selected_index, 0)
        self.assertIsNone(gs.player_count)

    def test_move_selection_down_and_wrap(self):
        gs = GameState()
        self.assertEqual(gs.current_option(), "1 Player")
        gs.move_selection(1)
        self.assertEqual(gs.selected_index, 1)
        self.assertEqual(gs.current_option(), "2 Players")
        gs.move_selection(1)  # wraps back to 0
        self.assertEqual(gs.selected_index, 0)

    def test_move_selection_up_and_wrap(self):
        gs = GameState()
        gs.move_selection(-1)  # wraps to the last option
        self.assertEqual(gs.selected_index, len(GameState.MENU_OPTIONS) - 1)

    def test_move_selection_invalid_direction_raises(self):
        gs = GameState()
        with self.assertRaises(ValueError):
            gs.move_selection(2)

    def test_move_selection_ignored_outside_menu(self):
        gs = GameState()
        gs.confirm()  # -> PLAYING
        before = gs.selected_index
        gs.move_selection(1)
        self.assertEqual(gs.selected_index, before)

    def test_confirm_one_player(self):
        gs = GameState()
        gs.confirm()
        self.assertEqual(gs.state, State.PLAYING)
        self.assertEqual(gs.player_count, 1)

    def test_confirm_two_player(self):
        gs = GameState()
        gs.move_selection(1)
        gs.confirm()
        self.assertEqual(gs.state, State.PLAYING)
        self.assertEqual(gs.player_count, 2)

    def test_confirm_ignored_outside_menu(self):
        gs = GameState()
        gs.confirm()
        gs.move_selection(1)  # no-op, still PLAYING
        gs.confirm()  # no-op, already PLAYING
        self.assertEqual(gs.player_count, 1)

    def test_reset_to_menu(self):
        gs = GameState()
        gs.confirm()
        gs.reset_to_menu()
        self.assertEqual(gs.state, State.MENU)
        self.assertEqual(gs.selected_index, 0)
        self.assertIsNone(gs.player_count)


class TestGameStateRoundOver(unittest.TestCase):
    def test_end_round_transitions_from_playing(self):
        gs = GameState()
        gs.confirm()
        gs.end_round("GAME OVER")
        self.assertEqual(gs.state, State.ROUND_OVER)
        self.assertEqual(gs.round_over_message, "GAME OVER")

    def test_end_round_ignored_outside_playing(self):
        gs = GameState()
        gs.end_round("GAME OVER")  # still in MENU
        self.assertEqual(gs.state, State.MENU)
        self.assertIsNone(gs.round_over_message)

    def test_end_round_ignored_once_already_ended(self):
        gs = GameState()
        gs.confirm()
        gs.end_round("GAME OVER")
        gs.end_round("YOU WIN!")  # already ROUND_OVER, should be a no-op
        self.assertEqual(gs.round_over_message, "GAME OVER")

    def test_restart_returns_to_menu_and_clears_state(self):
        gs = GameState()
        gs.move_selection(1)
        gs.confirm()
        gs.end_round("YOU WIN!")
        gs.restart()
        self.assertEqual(gs.state, State.MENU)
        self.assertEqual(gs.selected_index, 0)
        self.assertIsNone(gs.player_count)
        self.assertIsNone(gs.round_over_message)

    def test_restart_ignored_outside_round_over(self):
        gs = GameState()
        gs.confirm()
        gs.restart()  # still PLAYING, not ROUND_OVER
        self.assertEqual(gs.state, State.PLAYING)


class TestGameStateConfirmExit(unittest.TestCase):
    def test_request_exit_confirm_from_playing(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        self.assertEqual(gs.state, State.CONFIRM_EXIT)
        self.assertEqual(gs.confirm_exit_index, 0)
        self.assertEqual(gs.current_confirm_exit_option(), "Resume")

    def test_request_exit_confirm_from_menu(self):
        gs = GameState()
        gs.request_exit_confirm()
        self.assertEqual(gs.state, State.CONFIRM_EXIT)

    def test_request_exit_confirm_is_idempotent(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        gs.move_confirm_exit_selection(1)  # select "Back to Main Menu"
        gs.request_exit_confirm()  # should be a no-op: still CONFIRM_EXIT
        self.assertEqual(gs.state, State.CONFIRM_EXIT)
        # Selection wasn't reset by the second (ignored) call.
        self.assertEqual(gs.current_confirm_exit_option(), "Back to Main Menu")

    def test_move_confirm_exit_selection_wraps(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        gs.move_confirm_exit_selection(-1)  # wraps to the last option
        self.assertEqual(gs.confirm_exit_index, len(GameState.CONFIRM_EXIT_OPTIONS) - 1)
        self.assertEqual(gs.current_confirm_exit_option(), "Exit Game")

    def test_move_confirm_exit_selection_ignored_outside_confirm(self):
        gs = GameState()
        gs.move_confirm_exit_selection(1)  # still MENU, not CONFIRM_EXIT
        self.assertEqual(gs.confirm_exit_index, 0)

    def test_move_confirm_exit_selection_invalid_direction_raises(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        with self.assertRaises(ValueError):
            gs.move_confirm_exit_selection(2)

    def test_choose_resume_returns_to_playing(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        gs.choose_confirm_exit()  # "Resume" is selected by default
        self.assertEqual(gs.state, State.PLAYING)
        self.assertFalse(gs.should_quit)

    def test_choose_back_to_main_menu_resets(self):
        gs = GameState()
        gs.move_selection(1)
        gs.confirm()
        gs.request_exit_confirm()
        gs.move_confirm_exit_selection(1)  # "Back to Main Menu"
        gs.choose_confirm_exit()
        self.assertEqual(gs.state, State.MENU)
        self.assertIsNone(gs.player_count)
        self.assertFalse(gs.should_quit)

    def test_choose_exit_game_sets_should_quit(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        gs.move_confirm_exit_selection(-1)  # "Exit Game" (wraps to the last option)
        gs.choose_confirm_exit()
        self.assertTrue(gs.should_quit)

    def test_choose_confirm_exit_ignored_outside_confirm(self):
        gs = GameState()
        gs.confirm()
        gs.choose_confirm_exit()  # still PLAYING, not CONFIRM_EXIT
        self.assertEqual(gs.state, State.PLAYING)
        self.assertFalse(gs.should_quit)

    def test_cancel_exit_confirm_returns_to_previous_state(self):
        gs = GameState()
        gs.confirm()
        gs.request_exit_confirm()
        gs.move_confirm_exit_selection(1)  # change selection before canceling
        gs.cancel_exit_confirm()
        self.assertEqual(gs.state, State.PLAYING)
        self.assertFalse(gs.should_quit)

    def test_cancel_exit_confirm_from_round_over(self):
        gs = GameState()
        gs.confirm()
        gs.end_round("GAME OVER")
        gs.request_exit_confirm()
        gs.cancel_exit_confirm()
        self.assertEqual(gs.state, State.ROUND_OVER)
        self.assertEqual(gs.round_over_message, "GAME OVER")

    def test_cancel_exit_confirm_ignored_outside_confirm(self):
        gs = GameState()
        gs.confirm()
        gs.cancel_exit_confirm()  # still PLAYING, not CONFIRM_EXIT
        self.assertEqual(gs.state, State.PLAYING)


if __name__ == "__main__":
    unittest.main()
