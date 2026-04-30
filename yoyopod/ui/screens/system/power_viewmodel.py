"""Viewmodel builders for the Setup screen."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from yoyopod.integrations.power import PowerManager
    from yoyopod.integrations.power.models import PowerSnapshot


@dataclass(frozen=True, slots=True)
class PowerScreenState:
    """Prepared power/setup state consumed by the Setup screen."""

    snapshot: "PowerSnapshot | None" = None
    status: dict[str, object] = field(default_factory=dict)
    network_enabled: bool = False
    network_rows: tuple[tuple[str, str], ...] = ()
    gps_rows: tuple[tuple[str, str], ...] = ()
    playback_devices: tuple[str, ...] = ()
    capture_devices: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PowerScreenActions:
    """Focused actions exposed to the Setup screen."""

    refresh_voice_devices: Callable[[], None] | None = None
    refresh_gps: Callable[[], bool] | None = None
    persist_speaker_device: Callable[[str | None], bool] | None = None
    persist_capture_device: Callable[[str | None], bool] | None = None
    volume_up: Callable[[int], int | None] | None = None
    volume_down: Callable[[int], int | None] | None = None
    mute: Callable[[], bool] | None = None
    unmute: Callable[[], bool] | None = None


_VOICE_PAGE_SIGNATURE_FIELDS = (
    "commands_enabled",
    "ai_requests_enabled",
    "screen_read_enabled",
    "speaker_device_id",
    "capture_device_id",
    "mic_muted",
    "output_volume",
)


def _disabled_gps_rows() -> list[tuple[str, str]]:
    return [
        ("Fix", "Disabled"),
        ("Lat", "--"),
        ("Lng", "--"),
        ("Alt", "--"),
        ("Speed", "--"),
    ]


def _runtime_snapshot(network_runtime: object | None) -> object | None:
    if network_runtime is None:
        return None
    is_available = getattr(network_runtime, "is_available", None)
    if callable(is_available) and not is_available():
        return None
    snapshot = getattr(network_runtime, "snapshot", None)
    if not callable(snapshot):
        return None
    value = snapshot()
    if isinstance(value, dict):
        return value
    return None


def _build_network_rows_from_runtime(network_runtime: object | None) -> list[tuple[str, str]]:
    """Build cellular rows from the Rust-owned network snapshot."""

    snapshot = _runtime_snapshot(network_runtime)
    if snapshot is None or not bool(snapshot.get("enabled", False)):
        return [("Status", "Disabled")]

    status_text = {
        "online": "Online",
        "registered": "Registered",
        "connecting": "Connecting",
        "degraded": "Degraded",
        "offline": "Offline",
        "disabled": "Disabled",
    }.get(str(snapshot.get("network_status", "") or "").strip(), "Offline")

    signal = snapshot.get("signal")
    signal_data = signal if isinstance(signal, dict) else {}
    signal_bars = max(0, min(4, int(signal_data.get("bars", 0) or 0)))
    signal_text = "Unknown"
    if signal_data.get("csq") is not None or signal_bars > 0:
        signal_text = f"{signal_bars}/4"

    return [
        ("Status", status_text),
        ("Carrier", str(snapshot.get("carrier", "") or "Unknown")),
        ("Type", str(snapshot.get("network_type", "") or "Unknown")),
        ("Signal", signal_text),
        ("PPP", "Up" if bool(snapshot.get("connected", False)) else "Down"),
    ]


def _build_gps_rows_from_runtime(network_runtime: object | None) -> list[tuple[str, str]]:
    """Build GPS rows from the Rust-owned network snapshot."""

    snapshot = _runtime_snapshot(network_runtime)
    if snapshot is None or not bool(snapshot.get("enabled", False)):
        return _disabled_gps_rows()
    if not bool(snapshot.get("gps_enabled", False)):
        return _disabled_gps_rows()

    gps = snapshot.get("gps")
    gps_data = gps if isinstance(gps, dict) else {}
    if str(snapshot.get("gps_status", "") or "").strip() != "fix":
        fix_status = {
            "disabled": "Disabled",
            "starting": "Starting",
            "searching": "Searching",
            "unavailable": "Unavailable",
        }.get(str(snapshot.get("gps_status", "") or "").strip(), "Searching")
        return [
            ("Fix", fix_status),
            ("Lat", "--"),
            ("Lng", "--"),
            ("Alt", "--"),
            ("Speed", "--"),
        ]

    return [
        ("Fix", "Yes"),
        ("Lat", f"{float(gps_data.get('lat', 0.0) or 0.0):.6f}"),
        ("Lng", f"{float(gps_data.get('lng', 0.0) or 0.0):.6f}"),
        ("Alt", f"{float(gps_data.get('altitude', 0.0) or 0.0):.1f}m"),
        ("Speed", f"{float(gps_data.get('speed', 0.0) or 0.0):.1f}km/h"),
    ]


def build_power_screen_state_provider(
    *,
    power_manager: "PowerManager | None" = None,
    network_runtime: object | None = None,
    status_provider: Callable[[], dict[str, object]] | None = None,
    playback_device_options_provider: Callable[[], list[str]] | None = None,
    capture_device_options_provider: Callable[[], list[str]] | None = None,
) -> Callable[[], PowerScreenState]:
    """Build a prepared-state provider for the Setup screen."""

    def provider() -> PowerScreenState:
        power_snapshot = power_manager.get_snapshot() if power_manager is not None else None
        try:
            status = dict(status_provider() if status_provider is not None else {})
        except Exception:
            status = {}

        network_snapshot = _runtime_snapshot(network_runtime)
        return PowerScreenState(
            snapshot=power_snapshot,
            status=status,
            network_enabled=bool(network_snapshot is not None and network_snapshot.get("enabled", False)),
            network_rows=tuple(_build_network_rows_from_runtime(network_runtime)),
            gps_rows=tuple(_build_gps_rows_from_runtime(network_runtime)),
            playback_devices=tuple(
                playback_device_options_provider() if playback_device_options_provider is not None else []
            ),
            capture_devices=tuple(
                capture_device_options_provider() if capture_device_options_provider is not None else []
            ),
        )

    return provider


def build_power_screen_actions(
    *,
    network_runtime: object | None = None,
    refresh_voice_device_options_action: Callable[[], None] | None = None,
    persist_speaker_device_action: Callable[[str | None], bool] | None = None,
    persist_capture_device_action: Callable[[str | None], bool] | None = None,
    volume_up_action: Callable[[int], int | None] | None = None,
    volume_down_action: Callable[[int], int | None] | None = None,
    mute_action: Callable[[], bool] | None = None,
    unmute_action: Callable[[], bool] | None = None,
) -> PowerScreenActions:
    """Build the focused actions for the Setup screen."""

    def refresh_gps() -> bool:
        snapshot = _runtime_snapshot(network_runtime)
        if snapshot is None or not bool(snapshot.get("enabled", False)):
            return False
        if not bool(snapshot.get("gps_enabled", False)):
            return False

        query_gps = getattr(network_runtime, "query_gps", None)
        if not callable(query_gps):
            return False
        return bool(query_gps())

    return PowerScreenActions(
        refresh_voice_devices=refresh_voice_device_options_action,
        refresh_gps=refresh_gps,
        persist_speaker_device=persist_speaker_device_action,
        persist_capture_device=persist_capture_device_action,
        volume_up=volume_up_action,
        volume_down=volume_down_action,
        mute=mute_action,
        unmute=unmute_action,
    )
