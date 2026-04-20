"""Runtime services that keep ``YoyoPodApp`` thin and compositional."""

from yoyopod.runtime.loop import RuntimeLoopService
from yoyopod.runtime.models import PendingShutdown, PowerAlert, RecoveryState
from yoyopod.runtime.power_service import PowerRuntimeService
from yoyopod.runtime.recovery import RecoverySupervisor
from yoyopod.runtime.responsiveness import (
    ResponsivenessWatchdog,
    ResponsivenessWatchdogDecision,
    evaluate_responsiveness_status,
)
from yoyopod.runtime.screen_power import ScreenPowerService
from yoyopod.runtime.shutdown import ShutdownLifecycleService

__all__ = [
    "PendingShutdown",
    "PowerAlert",
    "PowerRuntimeService",
    "RecoveryState",
    "RecoverySupervisor",
    "ResponsivenessWatchdog",
    "ResponsivenessWatchdogDecision",
    "RuntimeBootService",
    "RuntimeLoopService",
    "ScreenPowerService",
    "ShutdownLifecycleService",
    "evaluate_responsiveness_status",
]


def __getattr__(name: str):
    """Load heavyweight runtime services lazily to avoid package import cycles."""

    if name == "RuntimeBootService":
        from yoyopod.runtime.boot import RuntimeBootService

        return RuntimeBootService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
