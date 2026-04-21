"""
Screen and stack coordination helpers for YoyoPod.
"""

from __future__ import annotations

from loguru import logger

from yoyopod.coordinators.registry import CoordinatorRuntime


class ScreenCoordinator:
    """Own small screen-stack and refresh operations for the app."""

    _NOW_PLAYING_ROUTE = "now_playing"
    _POWER_ROUTE = "power"
    _CALL_ROUTE = "call"
    _INCOMING_CALL_ROUTE = "incoming_call"
    _OUTGOING_CALL_ROUTE = "outgoing_call"
    _IN_CALL_ROUTE = "in_call"
    _CALL_DETAIL_ROUTES = (
        _IN_CALL_ROUTE,
        _INCOMING_CALL_ROUTE,
        _OUTGOING_CALL_ROUTE,
    )
    _CALL_ROUTES = (
        _CALL_ROUTE,
        _OUTGOING_CALL_ROUTE,
        _INCOMING_CALL_ROUTE,
        _IN_CALL_ROUTE,
    )

    def __init__(self, runtime: CoordinatorRuntime) -> None:
        self.runtime = runtime

    def _current_route_name(self) -> str | None:
        """Return the current route name from the screen stack."""
        if self.runtime.screen_manager is None:
            return None
        current_screen = self.runtime.screen_manager.current_screen
        if current_screen is None:
            return None
        return current_screen.route_name

    def _is_route_visible(self, route_name: str) -> bool:
        """Return True when the provided route is active."""
        return self._current_route_name() == route_name

    def _get_screen(self, route_name: str) -> object | None:
        """Return a registered screen by route name."""
        if self.runtime.screen_manager is None:
            return None
        return self.runtime.screen_manager.screens.get(route_name)

    def _set_screen_fields(self, route_name: str, **field_values: object) -> None:
        """Set dynamic state fields on a registered screen when available."""
        screen = self._get_screen(route_name)
        if screen is None:
            return
        for field_name, value in field_values.items():
            setattr(screen, field_name, value)

    def _push_route_if_needed(self, route_name: str, message: str) -> None:
        """Push a route only when it is not already visible."""
        screen_manager = self.runtime.screen_manager
        if screen_manager is None or self._is_route_visible(route_name):
            return
        screen_manager.push_screen(route_name)
        logger.info(message)

    def get_call_voip_manager(self) -> object | None:
        """Return the shared VoIP manager from call-related routes."""
        for route_name in self._CALL_ROUTES:
            screen = self._get_screen(route_name)
            voip_manager = getattr(screen, "voip_manager", None)
            if voip_manager is not None:
                return voip_manager
        return None

    def pop_call_screens(self) -> None:
        """Pop all call-related screens from the stack."""
        screen_manager = self.runtime.screen_manager
        if screen_manager is None:
            return

        while self._current_route_name() in self._CALL_DETAIL_ROUTES:
            if not screen_manager.pop_screen():
                break
            if not screen_manager.screen_stack:
                break

        logger.debug("Call screens cleared from stack")

    def update_now_playing_if_needed(self) -> None:
        """Refresh the now playing screen for periodic progress updates."""
        if not self._is_route_visible(self._NOW_PLAYING_ROUTE):
            return

        if self.runtime.music_backend and self.runtime.music_backend.is_connected:
            playback_state = self.runtime.music_backend.get_playback_state()
            if playback_state == "playing":
                self.refresh_current_screen()

    def update_in_call_if_needed(self) -> None:
        """Refresh the in-call screen for live duration and mute updates."""
        if self._is_route_visible(self._IN_CALL_ROUTE):
            self.refresh_current_screen()

    def update_power_screen_if_needed(self) -> None:
        """Refresh the power screen for live runtime metrics when visible."""
        if self._is_route_visible(self._POWER_ROUTE):
            self.refresh_current_screen()

    def refresh_current_screen(self) -> None:
        """Refresh whichever screen is currently visible."""
        screen_manager = self.runtime.screen_manager
        if screen_manager is None:
            return

        current_screen = screen_manager.get_current_screen()
        if current_screen is None:
            return

        screen_manager.refresh_current_screen()
        logger.debug("  -> Current screen refreshed")

    def refresh_now_playing_screen(self) -> None:
        """Refresh the now playing screen if it is currently visible."""
        if self._is_route_visible(self._NOW_PLAYING_ROUTE):
            self.refresh_current_screen()
            logger.debug("  → Now playing screen refreshed")

    def refresh_call_screen_if_visible(self) -> None:
        """Refresh the VoIP status screen if it is currently visible."""
        if self._is_route_visible(self._CALL_ROUTE):
            self.refresh_current_screen()
            logger.debug("  → Call screen refreshed")

    def show_incoming_call(self, caller_address: str, caller_name: str) -> None:
        """Update and show the incoming call screen."""
        self._set_screen_fields(
            self._INCOMING_CALL_ROUTE,
            caller_address=caller_address,
            caller_name=caller_name,
            ring_animation_frame=0,
        )
        self._push_route_if_needed(self._INCOMING_CALL_ROUTE, "  → Pushed incoming call screen")

    def show_in_call(self) -> None:
        """Show the active in-call screen if it is not already visible."""
        self._push_route_if_needed(self._IN_CALL_ROUTE, "  → Pushed in-call screen")

    def show_outgoing_call(self, callee_address: str, callee_name: str) -> None:
        """Update and show the outgoing-call screen."""
        self._set_screen_fields(
            self._OUTGOING_CALL_ROUTE,
            callee_address=callee_address,
            callee_name=callee_name or "Unknown",
            ring_animation_frame=0,
        )
        self._push_route_if_needed(self._OUTGOING_CALL_ROUTE, "  → Pushed outgoing call screen")
