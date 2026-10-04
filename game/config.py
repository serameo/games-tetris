"""Configuration constants for Tetris Battle.

Keeping all tunable numbers here means Phase 1's "level thresholds are
configurable" requirement is satisfied by editing this one file.
This module has no dependency on pygame so it can be imported and unit
tested without pygame installed.
"""

# --- Board dimensions (in cells) ---------------------------------------
BOARD_WIDTH = 9
BOARD_HEIGHT = 18

# --- Rendering layout ----------------------------------------------------
CELL_SIZE = 30            # pixels per cell
BOARD_MARGIN = 40         # space around/between boards
SIDE_PANEL_WIDTH = 150    # reserved for score/level/preview UI per board

BOARD_PIXEL_WIDTH = BOARD_WIDTH * CELL_SIZE
BOARD_PIXEL_HEIGHT = BOARD_HEIGHT * CELL_SIZE

WINDOW_WIDTH_1P = BOARD_MARGIN * 2 + BOARD_PIXEL_WIDTH + SIDE_PANEL_WIDTH
# Two-player: margin, P2 panel, P2 board, margin (gap), P1 board, P1 panel, margin.
WINDOW_WIDTH_2P = BOARD_MARGIN * 3 + (BOARD_PIXEL_WIDTH + SIDE_PANEL_WIDTH) * 2
WINDOW_HEIGHT = BOARD_MARGIN * 2 + BOARD_PIXEL_HEIGHT

FPS = 60

# --- Colors (R, G, B) ----------------------------------------------------
COLOR_BACKGROUND = (15, 15, 20)
COLOR_GRID_LINE = (60, 60, 70)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_SELECTED = (255, 215, 0)
COLOR_EMPTY_CELL = (25, 25, 32)

# Tetrimino colors, per the spec (O=yellow, I=cyan, S=green, Z=red,
# T=purple, L=blue, J=orange)
COLOR_PIECE_O = (255, 213, 0)
COLOR_PIECE_I = (0, 200, 220)
COLOR_PIECE_S = (0, 200, 0)
COLOR_PIECE_Z = (220, 30, 30)
COLOR_PIECE_T = (160, 30, 200)
COLOR_PIECE_L = (30, 90, 220)
COLOR_PIECE_J = (230, 130, 20)

# --- Falling speed ---------------------------------------------------------
BASE_FALL_INTERVAL = 1.0     # seconds per row, at level 1
FALL_INTERVAL_STEP = 0.01    # each level is this much faster than the previous
MIN_FALL_INTERVAL = 0.01     # safety floor so the interval never hits zero/negative

# --- Leveling / scoring (all configurable here) ---------------------------
LEVEL_1_THRESHOLD = 10       # points needed to go from level 1 to level 2
LEVEL_THRESHOLD_STEP = 3    # each subsequent level needs this many more points
MAX_LEVEL = 3

LINE_CLEAR_SCORES = {
    1: 1,
    2: 3,
    3: 5,
    4: 7,
}

# --- Line-clear flash (visual pause before a completed row is removed) ---
LINE_CLEAR_FLASH_DURATION = 1.0        # seconds a completed row blinks before clearing
LINE_CLEAR_FLASH_BLINK_INTERVAL = 0.2  # seconds between each on/off toggle
COLOR_LINE_FLASH = (192, 192, 192)


def fall_interval_for_level(level: int) -> float:
    """Return the drop interval, in seconds, for the given 1-indexed level."""
    interval = BASE_FALL_INTERVAL - FALL_INTERVAL_STEP * (level - 1)
    return max(interval, MIN_FALL_INTERVAL)


def score_threshold_for_level(level: int) -> int:
    """Return the score needed to advance FROM this level to the next.

    Level 1 -> 30, Level 2 -> 40, Level 3 -> 50, ... (step configurable above).
    """
    return LEVEL_1_THRESHOLD + LEVEL_THRESHOLD_STEP * (level - 1)


def cumulative_score_to_complete_level(level: int) -> int:
    """Return the TOTAL (cumulative, never-reset) score needed to complete
    the given level - i.e. to advance past it (or, if `level == MAX_LEVEL`,
    to win the game).

    This sums `score_threshold_for_level(i)` for every level from 1 up to
    and including `level`, since scoring is cumulative across the whole
    game rather than resetting each level.
    """
    return sum(score_threshold_for_level(i) for i in range(1, level + 1))
