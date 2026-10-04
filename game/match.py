"""Two-player match/round outcome logic.

No pygame dependency, so this can be unit tested without a display.
"""

from typing import Optional


def determine_round_outcome(
    p1_game_over: bool,
    p1_won: bool,
    p2_game_over: bool,
    p2_won: bool,
) -> Optional[str]:
    """Return the round-over message once the two-player round should end.

    Returns None if the round should continue.

    Rules (per tetris_battle_rules.md):
      - If a player loses (block-out), the other player wins.
      - If a player reaches the Level 30 win threshold, they win.
      - If both conditions happen to apply to both players at once
        (e.g. simultaneous block-out, or somehow both reaching the win
        threshold on the same check), the round is a draw rather than
        picking one arbitrarily.

    A block-out loss is checked before a win threshold: if one player is
    blocked out while the other has separately reached the win
    threshold, the outcome only depends on who is left standing, so
    checking loss first vs. win first gives the same message either way.
    """
    if p1_game_over and p2_game_over:
        return "DRAW!"
    if p1_game_over:
        return "PLAYER 2 WINS!"
    if p2_game_over:
        return "PLAYER 1 WINS!"

    if p1_won and p2_won:
        return "DRAW!"
    if p1_won:
        return "PLAYER 1 WINS!"
    if p2_won:
        return "PLAYER 2 WINS!"

    return None
