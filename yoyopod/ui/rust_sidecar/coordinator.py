"""Python runtime bridge for the Rust UI sidecar."""

from __future__ import annotations

from typing import Any

from loguru import logger

from yoyopod.core.events import WorkerMessageReceivedEvent
from yoyopod.core.workers import WorkerProcessConfig
from yoyopod.ui.rust_sidecar.state import RustUiRuntimeSnapshot


class RustUiSidecarCoordinator:
    """Translate Python runtime state and Rust UI intents across the worker seam."""

    def __init__(self, app: Any, *, worker_domain: str = "ui") -> None:
        self.app = app
        self.worker_domain = worker_domain

    def start_worker(
        self,
        worker_path: str,
        *,
        hardware: str = "mock",
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> bool:
        supervisor = getattr(self.app, "worker_supervisor", None)
        register = getattr(supervisor, "register", None)
        start = getattr(supervisor, "start", None)
        if not callable(register) or not callable(start):
            return False

        register(
            self.worker_domain,
            WorkerProcessConfig(
                name=self.worker_domain,
                argv=[worker_path, "--hardware", hardware],
                cwd=cwd,
                env=env,
            ),
        )
        return bool(start(self.worker_domain))

    def send_snapshot(self) -> bool:
        supervisor = getattr(self.app, "worker_supervisor", None)
        send_command = getattr(supervisor, "send_command", None)
        if not callable(send_command):
            return False
        return bool(
            send_command(
                self.worker_domain,
                type="ui.runtime_snapshot",
                payload=RustUiRuntimeSnapshot.from_app(self.app).to_payload(),
            )
        )

    def send_tick(self, *, renderer: str = "auto") -> bool:
        supervisor = getattr(self.app, "worker_supervisor", None)
        send_command = getattr(supervisor, "send_command", None)
        if not callable(send_command):
            return False
        return bool(
            send_command(
                self.worker_domain,
                type="ui.tick",
                payload={"renderer": renderer},
            )
        )

    def handle_worker_message(self, event: WorkerMessageReceivedEvent) -> None:
        if event.domain != self.worker_domain:
            return
        if event.type == "ui.intent":
            self._dispatch_intent(event.payload)
        elif event.type == "ui.screen_changed":
            logger.debug("Rust UI screen changed: {}", event.payload.get("screen"))

    def _dispatch_intent(self, payload: dict[str, Any]) -> None:
        domain = str(payload.get("domain", "")).strip()
        action = str(payload.get("action", "")).strip()
        data = payload.get("payload", {})
        if not isinstance(data, dict):
            data = {}
        if not domain or not action:
            return

        service_domain, service_name = self._map_service(domain, action)
        services = getattr(self.app, "services", None)
        call = getattr(services, "call", None)
        if not callable(call):
            return
        try:
            call(service_domain, service_name, data)
        except KeyError:
            logger.warning("No Python service registered for Rust UI intent {}.{}", domain, action)

    def _map_service(self, domain: str, action: str) -> tuple[str, str]:
        if domain == "music" and action == "play_pause":
            return "music", self._play_pause_service()
        if domain == "call" and action == "start":
            return "call", "dial"
        if domain == "call" and action == "toggle_mute":
            return "call", "mute"
        if domain == "voice" and action == "capture_start":
            return "call", "start_voice_note_recording"
        if domain == "voice" and action == "capture_stop":
            return "call", "stop_voice_note_recording"
        return domain, action

    def _play_pause_service(self) -> str:
        context = getattr(self.app, "context", None)
        playback = getattr(getattr(context, "media", None), "playback", None)
        if bool(getattr(playback, "is_playing", False)):
            return "pause"
        if bool(getattr(playback, "is_paused", False)):
            return "resume"
        return "play"
