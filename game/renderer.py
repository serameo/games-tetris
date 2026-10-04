"""Drawing code for Tetris Battle. Requires pygame.

Kept separate from game logic (board.py, game_state.py) so that logic
can be unit tested without a display or pygame installed.
"""

import pygame

from game.config import (
    BOARD_WIDTH,
    CELL_SIZE,
    BOARD_MARGIN,
    SIDE_PANEL_WIDTH,
    COLOR_BACKGROUND,
    COLOR_GRID_LINE,
    COLOR_TEXT,
    COLOR_TEXT_SELECTED,
    COLOR_EMPTY_CELL,
    COLOR_LINE_FLASH,
)
from game.game_state import GameState
from game.tetrimino import Tetrimino


def _shade(color, factor: float):
    """Scale an (r, g, b) color by `factor`, clamped to 0-255 per channel."""
    return tuple(max(0, min(255, int(channel * factor))) for channel in color)


def draw_metal_block(screen, rect, color) -> None:
    """Draw one Tetrimino cell as a beveled "shiny metal panel".

    A flat fill, a lighter highlight along the top/left edges, a darker
    shadow along the bottom/right edges, and a thin diagonal glint line
    give the block a simple embossed, reflective look without needing any
    external image assets.
    """
    x, y, w, h = rect
    pygame.draw.rect(screen, color, rect)

    border = max(2, w // 8)
    highlight = _shade(color, 1.5)
    shadow = _shade(color, 0.55)
    glint = _shade(color, 1.9)

    pygame.draw.rect(screen, highlight, (x, y, w, border))          # top edge
    pygame.draw.rect(screen, highlight, (x, y, border, h))          # left edge
    pygame.draw.rect(screen, shadow, (x, y + h - border, w, border))  # bottom edge
    pygame.draw.rect(screen, shadow, (x + w - border, y, border, h))  # right edge
    pygame.draw.line(screen, glint, (x + 2, y + h - 2), (x + w - 2, y + 2), 1)


def draw_menu(screen, game_state: GameState, font) -> None:
    screen.fill(COLOR_BACKGROUND)

    title_font = pygame.font.SysFont(None, 64)
    title_surf = title_font.render("TETRIS BATTLE", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 120))
    screen.blit(title_surf, title_rect)

    start_y = 240
    spacing = 60
    for i, option in enumerate(GameState.MENU_OPTIONS):
        color = COLOR_TEXT_SELECTED if i == game_state.selected_index else COLOR_TEXT
        surf = font.render(option, True, color)
        rect = surf.get_rect(center=(screen.get_width() // 2, start_y + i * spacing))
        screen.blit(surf, rect)


def draw_board(screen, board, top_left, flash_rows=None, flash_on=False) -> None:
    """Draw one board's grid lines and cell contents at a given top-left pixel position.

    flash_rows: optional list of row indices currently mid line-clear-flash.
        Those rows are drawn solid white when flash_on is True, or blanked
        out (as if already cleared) when flash_on is False, producing a
        blink. The row's real cell contents are ignored while flashing --
        they are about to be removed anyway.
    """
    x0, y0 = top_left
    width_px = board.width * CELL_SIZE
    height_px = board.height * CELL_SIZE
    flash_rows = flash_rows or ()

    pygame.draw.rect(screen, COLOR_EMPTY_CELL, (x0, y0, width_px, height_px))

    for row in range(board.height):
#        if row in flash_rows:
#            color = COLOR_LINE_FLASH if flash_on else COLOR_EMPTY_CELL
#            rect = (x0, y0 + row * CELL_SIZE, width_px, CELL_SIZE)
#            pygame.draw.rect(screen, color, rect)
#            continue
        for col in range(board.width):
            cell = board.get_cell(col, row)
            if cell is not None:
                if row in flash_rows:
                    color = COLOR_LINE_FLASH if flash_on else COLOR_EMPTY_CELL
                    rect = (x0 + col * CELL_SIZE, y0 + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    draw_metal_block(screen, rect, color)
                    #continue
                else:
                    rect = (x0 + col * CELL_SIZE, y0 + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    draw_metal_block(screen, rect, cell)

    for col in range(board.width + 1):
        x = x0 + col * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID_LINE, (x, y0), (x, y0 + height_px))
    for row in range(board.height + 1):
        y = y0 + row * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID_LINE, (x0, y), (x0 + width_px, y))


def draw_active_piece(screen, piece, top_left) -> None:
    """Draw the currently falling Tetrimino, if any, over its board."""
    if piece is None:
        return
    x0, y0 = top_left
    for cx, cy in piece.cells():
        rect = (x0 + cx * CELL_SIZE, y0 + cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        draw_metal_block(screen, rect, piece.color)


def draw_next_piece_preview(screen, piece_type, top_left, cell_size: int = 18) -> None:
    """Draw a small preview of the given piece type in its spawn orientation."""
    if piece_type is None:
        return
    shape = Tetrimino.SHAPES[piece_type]["rotations"][0]
    color = Tetrimino.SHAPES[piece_type]["color"]
    x0, y0 = top_left
    for dx, dy in shape:
        rect = (x0 + dx * cell_size, y0 + dy * cell_size, cell_size, cell_size)
        draw_metal_block(screen, rect, color)


def draw_side_panel(screen, info, panel_top_left, font) -> None:
    """Draw the score/level/next-piece (and game-over/win stub text) at a given position.

    `info` is a plain dict: {"score": int, "level": int, "game_over": bool,
    "won": bool, "next_piece_type": str or None}. Kept as a dict (not a
    PlayerBoard) so the renderer stays decoupled from the game-logic
    module. `panel_top_left` is the panel's own top-left pixel position --
    the caller decides where that is (to its right or its left of the
    board), so this function does not need to know which side of a board
    it's on.
    """
    x0, y0 = panel_top_left

    lines = [f"Score: {info.get('score', 0)}", f"Level: {info.get('level', 1)}"]
    if info.get("won"):
        lines.append("YOU WIN!")
    elif info.get("game_over"):
        lines.append("GAME OVER")

    for i, line in enumerate(lines):
        surf = font.render(line, True, COLOR_TEXT)
        screen.blit(surf, (x0 + 8, y0 + i * 32))

    next_piece_type = info.get("next_piece_type")
    if next_piece_type is not None:
        label_y = y0 + len(lines) * 32 + 10
        label_surf = font.render("Next:", True, COLOR_TEXT)
        screen.blit(label_surf, (x0 + 8, label_y))
        draw_next_piece_preview(screen, next_piece_type, (x0 + 8, label_y + 28))


def draw_playing(
    screen,
    game_state: GameState,
    boards,
    active_pieces=None,
    panels=None,
    font=None,
    flashes=None,
) -> None:
    """Draw the playing screen: one board (1P), or two boards mirrored (2P).

    boards: list of Board objects (locked cells only). `boards[0]` is
        always Player 1 and `boards[1]` (if present) is always Player 2 --
        this function decides how to arrange them on screen.
    active_pieces: optional list, same length as boards, of the Tetrimino
        currently falling on that board (or None if nothing is falling
        there right now, e.g. mid line-clear-flash).
    panels: optional list, same length as boards, of score/level info
        dicts (see draw_side_panel), or None for a board with no panel
        to show yet. Ignored if `font` is not given.
    flashes: optional list, same length as boards, of (flash_rows, flash_on)
        tuples (see draw_board), or None for a board with nothing flashing.

    Layout:
      - One board: [margin][board][panel][margin], as in Phase 1-4.
      - Two boards: [margin][P2 panel][P2 board][gap][P1 board][P1 panel][margin] --
        mirrored, with a margin-width gap between the two boards, and
        each player's panel on the outer side of their own board.
    """
    screen.fill(COLOR_BACKGROUND)
    board_px_width = BOARD_WIDTH * CELL_SIZE

    if active_pieces is None:
        active_pieces = [None] * len(boards)
    if panels is None:
        panels = [None] * len(boards)
    if flashes is None:
        flashes = [None] * len(boards)

    if len(boards) == 2:
        # Player 2 (index 1) on the left, Player 1 (index 0) on the right;
        # each one's panel goes on the outer side of their own board.
        render_order = [(1, "left"), (0, "right")]
    else:
        render_order = [(i, "right") for i in range(len(boards))]

    y0 = BOARD_MARGIN
    x = BOARD_MARGIN
    for slot_i, (index, panel_side) in enumerate(render_order):
        if slot_i > 0:
            x += BOARD_MARGIN  # gap between players' board+panel groups

        if panel_side == "left":
            panel_x0 = x
            x += SIDE_PANEL_WIDTH
            board_x0 = x
            x += board_px_width
        else:
            board_x0 = x
            x += board_px_width
            panel_x0 = x
            x += SIDE_PANEL_WIDTH

        flash_rows, flash_on = flashes[index] if flashes[index] is not None else (None, False)
        draw_board(screen, boards[index], (board_x0, y0), flash_rows=flash_rows, flash_on=flash_on)
        draw_active_piece(screen, active_pieces[index], (board_x0, y0))
        if panels[index] is not None and font is not None:
            draw_side_panel(screen, panels[index], (panel_x0, y0), font)


def draw_round_over(screen, message: str, font) -> None:
    """Draw the round-over screen: a big outcome message and a hint to continue."""
    screen.fill(COLOR_BACKGROUND)

    message_font = pygame.font.SysFont(None, 72)
    message_color = COLOR_TEXT_SELECTED if "WIN" in message else COLOR_TEXT
    message_surf = message_font.render(message, True, message_color)
    message_rect = message_surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 30)
    )
    screen.blit(message_surf, message_rect)

    hint_surf = font.render("Press Enter to return to the menu", True, COLOR_TEXT)
    hint_rect = hint_surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 40)
    )
    screen.blit(hint_surf, hint_rect)


def draw_confirm_exit(screen, game_state: GameState, font) -> None:
    """Draw the Escape confirm prompt: Resume / Back to Main Menu / Exit Game."""
    screen.fill(COLOR_BACKGROUND)

    title_font = pygame.font.SysFont(None, 56)
    title_surf = title_font.render("Quit?", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 140))
    screen.blit(title_surf, title_rect)

    start_y = 240
    spacing = 60
    for i, option in enumerate(GameState.CONFIRM_EXIT_OPTIONS):
        color = COLOR_TEXT_SELECTED if i == game_state.confirm_exit_index else COLOR_TEXT
        surf = font.render(option, True, color)
        rect = surf.get_rect(center=(screen.get_width() // 2, start_y + i * spacing))
        screen.blit(surf, rect)
