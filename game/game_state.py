"""Top-level game state machine for Tetris Battle.

No pygame dependency, so this can be unit tested without a display.
"""

from enum import Enum, auto
from typing import List, Optional


class State(Enum):
    MENU = auto()
    PLAYING = auto()
    ROUND_OVER = auto()
    CONFIRM_EXIT = auto()


class GameState:
    """Tracks which screen is active and the current menu selection.

    States: MENU (choose 1P/2P) -> PLAYING (the falling-piece game) ->
    ROUND_OVER (a "GAME OVER" / "YOU WIN!" screen) -> back to MENU.
    Pressing Escape from any of those opens CONFIRM_EXIT, a small
    Resume / Back to Main Menu / Exit Game prompt, which then returns to
    whichever state it was opened from (Resume), goes to MENU (Back to
    Main Menu), or sets `should_quit` (Exit Game) for main.py to act on.
    """

    MENU_OPTIONS: List[str] = ["1 Player", "2 Players"]
    CONFIRM_EXIT_OPTIONS: List[str] = ["Resume", "Back to Main Menu", "Exit Game"]

    def __init__(self) -> None:
        self.state: State = State.MENU
        self.selected_index: int = 0
        self.player_count: Optional[int] = None
        self.round_over_message: Optional[str] = None

        # Escape / exit-confirm state.
        self.confirm_exit_index: int = 0
        self._pre_confirm_state: Optional[State] = None
        self.should_quit: bool = False

    # --- main menu -----------------------------------------------------------

    def move_selection(self, direction: int) -> None:
        """Move the menu cursor. direction: -1 for up, +1 for down.

        Wraps around at the ends of the option list. No effect outside
        the MENU state.
        """
        if self.state != State.MENU:
            return
        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")
        count = len(self.MENU_OPTIONS)
        self.selected_index = (self.selected_index + direction) % count

    def confirm(self) -> None:
        """Confirm the current menu selection and start the game.

        No effect outside the MENU state.
        """
        if self.state != State.MENU:
            return
        self.player_count = self.selected_index + 1
        self.state = State.PLAYING

    def current_option(self) -> str:
        return self.MENU_OPTIONS[self.selected_index]

    # --- round over ------------------------------------------------------------

    def end_round(self, message: str) -> None:
        """Transition from PLAYING to ROUND_OVER with an outcome message.

        No effect outside the PLAYING state (so calling this repeatedly
        once the round has already ended is harmless).
        """
        if self.state != State.PLAYING:
            return
        self.state = State.ROUND_OVER
        self.round_over_message = message

    def restart(self) -> None:
        """Return to the main menu from the round-over screen.

        No effect outside the ROUND_OVER state.
        """
        if self.state != State.ROUND_OVER:
            return
        self.reset_to_menu()

    def reset_to_menu(self) -> None:
        """Return to the main menu (used after a round ends, or on demand)."""
        self.state = State.MENU
        self.selected_index = 0
        self.player_count = None
        self.round_over_message = None

    # --- escape / exit confirm ---------------------------------------------------

    def request_exit_confirm(self) -> None:
        """Open the Escape confirm prompt, remembering the state to return to.

        No effect if the prompt is already open (so a stray repeated
        Escape press can't lose track of the original state).
        """
        if self.state == State.CONFIRM_EXIT:
            return
        self._pre_confirm_state = self.state
        self.confirm_exit_index = 0
        self.state = State.CONFIRM_EXIT

    def move_confirm_exit_selection(self, direction: int) -> None:
        """Move the cursor in the Escape confirm prompt. -1 up, +1 down.

        Wraps around. No effect outside CONFIRM_EXIT.
        """
        if self.state != State.CONFIRM_EXIT:
            return
        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")
        count = len(self.CONFIRM_EXIT_OPTIONS)
        self.confirm_exit_index = (self.confirm_exit_index + direction) % count

    def current_confirm_exit_option(self) -> str:
        return self.CONFIRM_EXIT_OPTIONS[self.confirm_exit_index]

    def choose_confirm_exit(self) -> None:
        """Act on the highlighted Escape-confirm option.

        No effect outside CONFIRM_EXIT.
        """
        if self.state != State.CONFIRM_EXIT:
            return
        option = self.current_confirm_exit_option()
        if option == "Resume":
            self.state = self._pre_confirm_state
        elif option == "Back to Main Menu":
            self.reset_to_menu()
        elif option == "Exit Game":
            self.should_quit = True
        self._pre_confirm_state = None

    def cancel_exit_confirm(self) -> None:
        """Resume without changing the selection (Escape pressed again).

        No effect outside CONFIRM_EXIT.
        """
        if self.state != State.CONFIRM_EXIT:
            return
        self.state = self._pre_confirm_state
        self._pre_confirm_state = None
