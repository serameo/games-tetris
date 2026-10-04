import unittest

from game.config import (
    fall_interval_for_level,
    score_threshold_for_level,
    cumulative_score_to_complete_level,
)


class TestFallIntervalForLevel(unittest.TestCase):
    def test_level_1_is_base_interval(self):
        self.assertAlmostEqual(fall_interval_for_level(1), 1.0)

    def test_decreases_by_step_per_level(self):
        self.assertAlmostEqual(fall_interval_for_level(2), 0.99)
        self.assertAlmostEqual(fall_interval_for_level(3), 0.98)

    def test_level_30_matches_expected_value(self):
        self.assertAlmostEqual(fall_interval_for_level(30), 1.0 - 0.01 * 29)

    def test_never_drops_below_floor(self):
        self.assertGreaterEqual(fall_interval_for_level(10_000), 0.01)


class TestScoreThresholdForLevel(unittest.TestCase):
    def test_level_1_threshold(self):
        self.assertEqual(score_threshold_for_level(1), 30)

    def test_threshold_increases_by_step(self):
        self.assertEqual(score_threshold_for_level(2), 40)
        self.assertEqual(score_threshold_for_level(3), 50)
        self.assertEqual(score_threshold_for_level(10), 120)


class TestCumulativeScoreToCompleteLevel(unittest.TestCase):
    def test_level_1(self):
        self.assertEqual(cumulative_score_to_complete_level(1), 30)

    def test_level_2_adds_level_2_threshold(self):
        self.assertEqual(cumulative_score_to_complete_level(2), 30 + 40)

    def test_level_3(self):
        self.assertEqual(cumulative_score_to_complete_level(3), 30 + 40 + 50)

    def test_is_strictly_increasing(self):
        prev = 0
        for level in range(1, 31):
            total = cumulative_score_to_complete_level(level)
            self.assertGreater(total, prev)
            prev = total


if __name__ == "__main__":
    unittest.main()
