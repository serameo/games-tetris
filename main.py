"""Entry point for Tetris Battle.

Run with:
    python main.py

Requires `pygame` (see requirements.txt). This file is intentionally
thin: all game logic lives in the `game` package so it can be unit
tested independently of pygame/display (see tests/).

Phase 5 scope: two-player mode now has two real, independent, simultaneous
PlayerBoards, split-screen side by side, with Player 2 on WASD + Space
(hard drop) instead of Player 1's arrow keys + Enter. The two-player
win/lose rule (one player's loss makes the other the winner; reaching
the Level 30 win threshold also ends the round) lives in game/match.py.

Carried over from earlier phases: line-clear flash, per-level gravity
speed, hard drop, a GAME OVER / WIN / DRAW round-over screen with Enter
to return to the menu, and an Escape confirm prompt (Resume / Back to
Main Menu / Exit Game).
"""

import sys

import pygame

from game.config import (
    WINDOW_WIDTH_1P,
    WINDOW_WIDTH_2P,
    WINDOW_HEIGHT,
    FPS,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)
from game.game_state import GameState, State
from game.player import PlayerBoard
from game.match import determine_round_outcome
from game import renderer

# Player 1: arrow keys to move/rotate/soft-drop, Enter to hard-drop.
P1_KEYS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "rotate": pygame.K_UP,
    "soft_drop": pygame.K_DOWN,
    "hard_drop": (pygame.K_RETURN, pygame.K_KP_ENTER),
}

# Player 2 (two-player mode only): WASD to move/rotate/soft-drop, Space to hard-drop.
P2_KEYS = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "rotate": pygame.K_w,
    "soft_drop": pygame.K_s,
    "hard_drop": (pygame.K_SPACE,),
}


def start_round(game_state: GameState):
    """Create one PlayerBoard per player for a freshly confirmed player count."""
    return [PlayerBoard(BOARD_WIDTH, BOARD_HEIGHT) for _ in range(game_state.player_count)]


def handle_gameplay_key(player_board, event_key, keymap) -> None:
    """Apply one player's key mapping to their board for a single KEYDOWN event."""
    if player_board is None:
        return
    if event_key == keymap["left"]:
        player_board.move(-1, 0)
    elif event_key == keymap["right"]:
        player_board.move(1, 0)
    elif event_key == keymap["rotate"]:
        player_board.rotate()
    elif event_key == keymap["soft_drop"]:
        player_board.soft_drop()
    elif event_key in keymap["hard_drop"]:
        player_board.hard_drop()


def check_round_end(game_state: GameState, player_boards) -> None:
    """End the round via game_state.end_round(...) if the outcome is decided."""
    if len(player_boards) == 1:
        pb = player_boards[0]
        if pb.won:
            game_state.end_round("YOU WIN!")
        elif pb.game_over:
            game_state.end_round("GAME OVER")
    elif len(player_boards) == 2:
        p1, p2 = player_boards
        outcome = determine_round_outcome(p1.game_over, p1.won, p2.game_over, p2.won)
        if outcome is not None:
            game_state.end_round(outcome)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Tetris Battle")

    screen = pygame.display.set_mode((WINDOW_WIDTH_1P, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    panel_font = pygame.font.SysFont(None, 28)

    game_state = GameState()

    player_boards = []   # one PlayerBoard per player, once a round has started
    fall_timers = []     # matching per-player gravity accumulators

    def reset_to_menu_view():
        nonlocal player_boards, fall_timers, screen
        player_boards = []
        fall_timers = []
        screen = pygame.display.set_mode((WINDOW_WIDTH_1P, WINDOW_HEIGHT))

    running = True
    while running:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state.state == State.CONFIRM_EXIT:
                        game_state.cancel_exit_confirm()
                    else:
                        game_state.request_exit_confirm()
                elif game_state.state == State.MENU:
                    if event.key == pygame.K_UP:
                        game_state.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        game_state.move_selection(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game_state.confirm()
                        player_boards = start_round(game_state)
                        fall_timers = [0.0] * len(player_boards)
                        window_width = (
                            WINDOW_WIDTH_1P if game_state.player_count == 1 else WINDOW_WIDTH_2P
                        )
                        screen = pygame.display.set_mode((window_width, WINDOW_HEIGHT))
                elif game_state.state == State.PLAYING:
                    if len(player_boards) >= 1:
                        handle_gameplay_key(player_boards[0], event.key, P1_KEYS)
                    if len(player_boards) >= 2:
                        handle_gameplay_key(player_boards[1], event.key, P2_KEYS)
                elif game_state.state == State.ROUND_OVER:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game_state.restart()
                        reset_to_menu_view()
                elif game_state.state == State.CONFIRM_EXIT:
                    if event.key == pygame.K_UP:
                        game_state.move_confirm_exit_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        game_state.move_confirm_exit_selection(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game_state.choose_confirm_exit()
                        if game_state.state == State.MENU:
                            reset_to_menu_view()

        if game_state.should_quit:
            running = False
            continue

        if game_state.state == State.PLAYING and player_boards:
            for i, pb in enumerate(player_boards):
                pb.update(dt)  # advances that player's line-clear flash timer, if any
                if not pb.is_flashing:
                    fall_timers[i] += dt
                    if fall_timers[i] >= pb.fall_interval:
                        fall_timers[i] -= pb.fall_interval
                        pb.soft_drop()
            check_round_end(game_state, player_boards)

        if game_state.state == State.MENU:
            renderer.draw_menu(screen, game_state, font)
        elif game_state.state == State.PLAYING and player_boards:
            panels = [
                {
                    "score": pb.score,
                    "level": pb.level,
                    "game_over": pb.game_over,
                    "won": pb.won,
                    "next_piece_type": pb.next_piece_type,
                }
                for pb in player_boards
            ]
            active_pieces = [None if pb.is_flashing else pb.active_piece for pb in player_boards]
            flashes = [
                (pb.flash_rows, pb.flash_on) if pb.is_flashing else None for pb in player_boards
            ]
            renderer.draw_playing(
                screen,
                game_state,
                [pb.board for pb in player_boards],
                active_pieces,
                panels,
                panel_font,
                flashes,
            )
        elif game_state.state == State.ROUND_OVER:
            renderer.draw_round_over(screen, game_state.round_over_message, font)
        elif game_state.state == State.CONFIRM_EXIT:
            renderer.draw_confirm_exit(screen, game_state, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
