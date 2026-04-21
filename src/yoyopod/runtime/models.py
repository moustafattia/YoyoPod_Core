"""Compatibility shims for relocated runtime model dataclasses."""

from yoyopod.core.recovery import RecoveryState
from yoyopod.integrations.power import PendingShutdown, PowerAlert

__all__ = ["PendingShutdown", "PowerAlert", "RecoveryState"]
