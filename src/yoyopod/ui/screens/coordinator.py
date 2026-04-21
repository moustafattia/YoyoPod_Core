"""
Screen and stack coordination helpers for YoyoPod.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from yoyopod.ui.screens.manager import ScreenManager
    from yoyopod.ui.screens.music.now_playing import NowPlayingScreen
    from yoyopod.ui.screens.voip.in_call import InCallScreen
    from yoyopod.ui.screens.voip.incoming_call import IncomingCallScreen
    from yoyopod.ui.screens.voip.outgoing_call import OutgoingCallScreen
    from yoyopod.ui.screens.voip.quick_call import CallScreen


class ScreenCoordinator:
    """Own small screen-stack and refresh operations for the app."""

    def __init__(
        self,
        *,
        screen_manager: "ScreenManager | None",
        now_playing_screen: "NowPlayingScreen | None",
        call_screen: "CallScreen | None",
        incoming_call_screen: "IncomingCallScreen | None",
        outgoing_call_screen: "OutgoingCallScreen | None",
        in_call_screen: "InCallScreen | None",
    ) -> None:
        self.screen_manager = screen_manager
        self.now_playing_screen = now_playing_screen
        self.call_screen = call_screen
        self.incoming_call_screen = incoming_call_screen
        self.outgoing_call_screen = outgoing_call_screen
        self.in_call_screen = in_call_screen

    def pop_call_screens(self) -> None:
        """Pop all call-related screens from the stack."""
        if self.screen_manager is None:
            return

        call_screens = [
            self.in_call_screen,
            self.incoming_call_screen,
            self.outgoing_call_screen,
        ]

        while self.screen_manager.current_screen in call_screens:
            self.screen_manager.pop_screen()
            if not self.screen_manager.screen_stack:
                break

        logger.debug("Call screens cleared from stack")

    def refresh_current_screen_for_visible_tick(self) -> bool:
        """Refresh the current screen when it opts into periodic visible ticks."""
        if self.screen_manager is None:
            return False

        current_screen = self.screen_manager.get_current_screen()
        if current_screen is None:
            return False

        if not self.screen_manager.refresh_current_screen_for_visible_tick():
            return False

        logger.debug(
            "  -> Visible tick refreshed {}",
            current_screen.route_name or getattr(current_screen, "name", "unknown"),
        )
        return True

    def update_now_playing_if_needed(self) -> None:
        """Compatibility wrapper over the generic visible-tick refresh path."""
        self.refresh_current_screen_for_visible_tick()

    def update_in_call_if_needed(self) -> None:
        """Compatibility wrapper over the generic visible-tick refresh path."""
        self.refresh_current_screen_for_visible_tick()

    def update_power_screen_if_needed(self) -> None:
        """Compatibility wrapper over the generic visible-tick refresh path."""
        self.refresh_current_screen_for_visible_tick()

    def refresh_current_screen(self) -> None:
        """Refresh whichever screen is currently visible."""
        if self.screen_manager is None:
            return

        current_screen = self.screen_manager.get_current_screen()
        if current_screen is None:
            return

        self.screen_manager.refresh_current_screen()
        logger.debug("  -> Current screen refreshed")

    def refresh_now_playing_screen(self) -> None:
        """Refresh the now playing screen if it is currently visible."""
        if self.screen_manager is not None and self.screen_manager.current_screen == self.now_playing_screen:
            assert self.now_playing_screen is not None
            self.now_playing_screen.render()
            logger.debug("  -> Now playing screen refreshed")

    def refresh_call_screen_if_visible(self) -> None:
        """Refresh the VoIP status screen if it is currently visible."""
        if self.screen_manager is not None and self.screen_manager.current_screen == self.call_screen:
            assert self.call_screen is not None
            self.call_screen.render()
            logger.debug("  -> Call screen refreshed")

    def show_incoming_call(self, caller_address: str, caller_name: str) -> None:
        """Update and show the incoming call screen."""
        if self.screen_manager is None or self.incoming_call_screen is None:
            return

        self.incoming_call_screen.caller_address = caller_address
        self.incoming_call_screen.caller_name = caller_name
        self.incoming_call_screen.ring_animation_frame = 0

        if self.screen_manager.current_screen != self.incoming_call_screen:
            self.screen_manager.push_screen("incoming_call")
            logger.info("  -> Pushed incoming call screen")

    def show_in_call(self) -> None:
        """Show the active in-call screen if it is not already visible."""
        if self.screen_manager is None or self.in_call_screen is None:
            return

        if self.screen_manager.current_screen != self.in_call_screen:
            self.screen_manager.push_screen("in_call")
            logger.info("  -> Pushed in-call screen")

    def show_outgoing_call(self, callee_address: str, callee_name: str) -> None:
        """Update and show the outgoing-call screen."""
        if self.screen_manager is None or self.outgoing_call_screen is None:
            return

        self.outgoing_call_screen.callee_address = callee_address
        self.outgoing_call_screen.callee_name = callee_name or "Unknown"
        self.outgoing_call_screen.ring_animation_frame = 0

        if self.screen_manager.current_screen != self.outgoing_call_screen:
            self.screen_manager.push_screen("outgoing_call")
            logger.info("  -> Pushed outgoing call screen")
