"""Tests for the thin Python facade around the Rust network host."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from yoyopod.core import AppContext
from yoyopod.core.events import WorkerDomainStateChangedEvent, WorkerMessageReceivedEvent
from yoyopod.integrations.network.rust_host import RustNetworkFacade


class _Supervisor:
    def __init__(self) -> None:
        self.registered: list[tuple[str, object]] = []
        self.started: list[str] = []
        self.stopped: list[tuple[str, float]] = []
        self.sent: list[tuple[str, str, dict[str, Any] | None, str | None]] = []

    def register(self, domain: str, config: object) -> None:
        self.registered.append((domain, config))

    def start(self, domain: str) -> bool:
        self.started.append(domain)
        return True

    def stop(self, domain: str, *, grace_seconds: float = 1.0) -> None:
        self.stopped.append((domain, grace_seconds))

    def send_command(
        self,
        domain: str,
        *,
        type: str,
        payload: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> bool:
        self.sent.append((domain, type, payload, request_id))
        return True


def _snapshot(
    *,
    enabled: bool = True,
    gps_enabled: bool = True,
    connected: bool = False,
    gps_has_fix: bool = False,
    state: str | None = None,
    network_status: str | None = None,
    gps_status: str | None = None,
) -> dict[str, Any]:
    raw_state = state or ("online" if connected else "registered")
    raw_network_status = network_status or ("online" if connected else "registered")
    raw_gps_status = gps_status or ("fix" if gps_has_fix else "searching")
    return {
        "enabled": enabled,
        "gps_enabled": gps_enabled,
        "config_dir": "config/test-device",
        "state": raw_state,
        "sim_ready": enabled,
        "registered": enabled,
        "carrier": "Telekom.de" if enabled else "",
        "network_type": "4G" if enabled else "",
        "signal": {"csq": 20 if enabled else None, "bars": 3 if enabled else 0},
        "ppp": {
            "up": connected,
            "interface": "ppp0" if enabled else "",
            "pid": 1234 if connected else None,
            "default_route_owned": connected,
            "last_failure": "",
        },
        "gps": {
            "has_fix": gps_has_fix,
            "lat": 48.8566 if gps_has_fix else None,
            "lng": 2.3522 if gps_has_fix else None,
            "altitude": 35.0 if gps_has_fix else None,
            "speed": 0.0 if gps_has_fix else None,
            "timestamp": "2026-04-30T10:00:00Z" if gps_has_fix else None,
            "last_query_result": "fix" if gps_has_fix else "idle",
        },
        "connected": connected,
        "gps_has_fix": gps_has_fix,
        "connection_type": "4g" if enabled else "none",
        "network_status": raw_network_status,
        "gps_status": raw_gps_status if enabled and gps_enabled else "disabled",
        "recovering": False,
        "retryable": True,
        "reconnect_attempts": 0,
        "next_retry_at_ms": None,
        "error_code": "",
        "error_message": "",
        "updated_at_ms": 1,
    }


def test_facade_registers_worker_with_config_dir() -> None:
    supervisor = _Supervisor()
    app = SimpleNamespace(
        worker_supervisor=supervisor,
        config_dir="config/test-device",
        context=AppContext(),
    )
    facade = RustNetworkFacade(app, worker_domain="network")

    assert facade.start_worker("yoyopod_rs/network-host/build/yoyopod-network-host")

    assert supervisor.started == ["network"]
    domain, config = supervisor.registered[0]
    assert domain == "network"
    assert getattr(config, "argv") == [
        "yoyopod_rs/network-host/build/yoyopod-network-host",
        "--config-dir",
        "config/test-device",
    ]


def test_facade_sends_query_gps_without_request_tracking() -> None:
    supervisor = _Supervisor()
    app = SimpleNamespace(
        worker_supervisor=supervisor,
        context=AppContext(),
    )
    facade = RustNetworkFacade(app, worker_domain="network")

    assert facade.query_gps() is True
    assert supervisor.sent == [("network", "network.query_gps", {}, None)]


def test_facade_applies_health_result_snapshot_to_cache_and_context() -> None:
    supervisor = _Supervisor()
    app = SimpleNamespace(
        worker_supervisor=supervisor,
        context=AppContext(),
        cloud_manager=None,
    )
    facade = RustNetworkFacade(app, worker_domain="network")
    snapshot = _snapshot(connected=True)

    facade.handle_worker_message(
        WorkerMessageReceivedEvent(
            domain="network",
            kind="result",
            type="network.health",
            request_id="health-1",
            payload={"snapshot": snapshot},
        )
    )

    assert facade.snapshot() == snapshot
    assert app.context.network.enabled is True
    assert app.context.network.connected is True
    assert app.context.network.connection_type == "4g"
    assert app.context.network.signal_strength == 3


def test_facade_clears_context_when_worker_is_unavailable_but_keeps_last_raw_snapshot() -> None:
    supervisor = _Supervisor()
    app = SimpleNamespace(
        worker_supervisor=supervisor,
        context=AppContext(),
        cloud_manager=None,
    )
    facade = RustNetworkFacade(app, worker_domain="network")

    facade.handle_worker_message(
        WorkerMessageReceivedEvent(
            domain="network",
            kind="event",
            type="network.snapshot",
            request_id=None,
            payload=_snapshot(connected=True, gps_has_fix=True),
        )
    )

    facade.handle_worker_state_change(
        WorkerDomainStateChangedEvent(
            domain="network",
            state="degraded",
            reason="process_exited",
        )
    )

    assert facade.snapshot() is not None
    assert facade.is_available() is False
    assert app.context.network.enabled is False
    assert app.context.network.connected is False
    assert app.context.network.connection_type == "none"
