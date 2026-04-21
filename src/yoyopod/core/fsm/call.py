"""Compatibility exports for relocated call-session primitives."""

from yoyopod.integrations.call.session import (
    CallFSM,
    CallInterruptionPolicy,
    CallSessionState,
)

__all__ = ["CallFSM", "CallInterruptionPolicy", "CallSessionState"]

