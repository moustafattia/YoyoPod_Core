"""Compatibility shim for the relocated live recovery service."""

from yoyopod.core.recovery import RecoveryState, RuntimeRecoveryService

RecoverySupervisor = RuntimeRecoveryService

__all__ = ["RecoveryState", "RecoverySupervisor", "RuntimeRecoveryService"]
