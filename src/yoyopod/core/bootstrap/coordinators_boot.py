"""Coordinator-runtime construction during startup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from yoyopod.core import ScreenChangedEvent
from yoyopod.core.app_state import AppRuntimeState, AppStateRuntime
from yoyopod.integrations.call.coordinator import CallCoordinator
from yoyopod.integrations.music.coordinator import PlaybackCoordinator
from yoyopod.integrations.power.coordinator import PowerCoordinator
from yoyopod.ui.screens.coordinator import ScreenCoordinator

if TYPE_CHECKING:
    from yoyopod.core.application import YoyoPodApp


class CoordinatorsBoot:
    """Build coordinator helpers around the initialized runtime."""

    def __init__(self, app: "YoyoPodApp") -> None:
        self.app = app

    def ensure_coordinators(self) -> None:
        """Create the coordinator runtime once the screens and managers exist."""

        if self.app.app_state_runtime is not None:
            return

        assert self.app.music_fsm is not None
        assert self.app.call_fsm is not None
        assert self.app.call_interruption_policy is not None
        assert self.app.context is not None
        current_screen = (
            self.app.screen_manager.get_current_screen()
            if self.app.screen_manager is not None
            else None
        )
        current_route_name = current_screen.route_name if current_screen is not None else None
        initial_ui_state = AppRuntimeState.ui_state_for_screen_name(current_route_name) or AppRuntimeState.IDLE
        self.app.app_state_runtime = AppStateRuntime(
            music_fsm=self.app.music_fsm,
            call_fsm=self.app.call_fsm,
            call_interruption_policy=self.app.call_interruption_policy,
            ui_state=initial_ui_state,
            voip_ready=self.app._voip_registered,
        )
        self.app.screen_coordinator = ScreenCoordinator(
            screen_manager=self.app.screen_manager,
            now_playing_screen=self.app.now_playing_screen,
            call_screen=self.app.call_screen,
            incoming_call_screen=self.app.incoming_call_screen,
            outgoing_call_screen=self.app.outgoing_call_screen,
            in_call_screen=self.app.in_call_screen,
        )
        self.app.call_coordinator = CallCoordinator(
            runtime=self.app.app_state_runtime,
            screen_coordinator=self.app.screen_coordinator,
            auto_resume_after_call=self.app.auto_resume_after_call,
            config_manager=self.app.config_manager,
            context=self.app.context,
            music_backend=self.app.music_backend,
            voip_manager_provider=lambda: self.app.voip_manager,
            call_history_store=self.app.call_history_store,
            initial_voip_registered=self.app._voip_registered,
        )
        self.app.playback_coordinator = PlaybackCoordinator(
            runtime=self.app.app_state_runtime,
            screen_coordinator=self.app.screen_coordinator,
            local_music_service=self.app.local_music_service,
        )
        self.app.power_coordinator = PowerCoordinator(
            runtime=self.app.app_state_runtime,
            screen_coordinator=self.app.screen_coordinator,
            power_manager=self.app.power_manager,
            screen_manager=self.app.screen_manager,
            context=self.app.context,
            cloud_manager=self.app.cloud_manager,
        )
        if self.app.screen_manager is not None:
            self.app.screen_manager.on_screen_changed = (
                lambda screen_name: self.app.scheduler.run_on_main(
                    lambda: self.app.bus.publish(ScreenChangedEvent(screen_name=screen_name))
                )
            )
            self.app.bus.publish(ScreenChangedEvent(screen_name=current_route_name))
