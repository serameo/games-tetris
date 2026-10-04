import unittest

from game.match import determine_round_outcome


class TestDetermineRoundOutcome(unittest.TestCase):
    def test_no_outcome_when_both_still_playing(self):
        self.assertIsNone(determine_round_outcome(False, False, False, False))

    def test_player1_game_over_means_player2_wins(self):
        self.assertEqual(determine_round_outcome(True, False, False, False), "PLAYER 2 WINS!")

    def test_player2_game_over_means_player1_wins(self):
        self.assertEqual(determine_round_outcome(False, False, True, False), "PLAYER 1 WINS!")

    def test_both_game_over_is_a_draw(self):
        self.assertEqual(determine_round_outcome(True, False, True, False), "DRAW!")

    def test_player1_win_condition(self):
        self.assertEqual(determine_round_outcome(False, True, False, False), "PLAYER 1 WINS!")

    def test_player2_win_condition(self):
        self.assertEqual(determine_round_outcome(False, False, False, True), "PLAYER 2 WINS!")

    def test_both_win_condition_is_a_draw(self):
        self.assertEqual(determine_round_outcome(False, True, False, True), "DRAW!")

    def test_loss_and_opponent_win_agree_on_the_winner(self):
        # If one player is blocked out while the other separately reached
        # the win threshold, both signals point to the same winner.
        self.assertEqual(determine_round_outcome(True, False, False, True), "PLAYER 2 WINS!")
        self.assertEqual(determine_round_outcome(False, True, True, False), "PLAYER 1 WINS!")


if __name__ == "__main__":
    unittest.main()
