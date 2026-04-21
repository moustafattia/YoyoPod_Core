"""Compatibility shim for the relocated network integration models."""

from __future__ import annotations

from yoyopod.integrations.network.models import (
    GpsCoordinate,
    ModemPhase,
    ModemState,
    SignalInfo,
)

__all__ = ["GpsCoordinate", "ModemPhase", "ModemState", "SignalInfo"]
