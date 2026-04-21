"""Typed application events for YoyoPod orchestration and scaffold work."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

FocusOwner = Literal["call", "music", "voice"]


@dataclass(frozen=True, slots=True)
class StateChangedEvent:
    """Published when one entity changes in the Phase A scaffold state store."""

    entity: str
    old: Any
    new: Any
    attrs: dict[str, Any]
    last_changed_at: float


@dataclass(frozen=True, slots=True)
class LifecycleEvent:
    """Published when the scaffold app shell changes lifecycle phase."""

    phase: str
    detail: str = ""


@dataclass(frozen=True, slots=True)
class ScreenChangedEvent:
    """Published when the active screen route changes."""

    screen_name: str | None


@dataclass(frozen=True, slots=True)
class UserActivityEvent:
    """Published when user input activity should wake or keep the screen alive."""

    action_name: str | None = None


@dataclass(frozen=True, slots=True)
class AudioFocusGrantedEvent:
    """Published when one domain is granted audio focus."""

    owner: FocusOwner
    preempted: FocusOwner | None = None


@dataclass(frozen=True, slots=True)
class AudioFocusLostEvent:
    """Published when one domain loses audio focus."""

    owner: FocusOwner
    preempted_by: FocusOwner | None = None


@dataclass(frozen=True, slots=True)
class RecoveryAttemptCompletedEvent:
    """Published when a background backend recovery attempt finishes."""

    manager: Literal["music", "network"]
    recovered: bool
    recovery_now: float


@dataclass(frozen=True, slots=True)
class BackendStoppedEvent:
    """Published when one integration-owned backend becomes unavailable."""

    domain: str
    reason: str = ""


_call_events = import_module("yoyopod.integrations.call.events")
IncomingCallEvent = _call_events.IncomingCallEvent
CallStateChangedEvent = _call_events.CallStateChangedEvent
CallEndedEvent = _call_events.CallEndedEvent
RegistrationChangedEvent = _call_events.RegistrationChangedEvent
VoIPAvailabilityChangedEvent = _call_events.VoIPAvailabilityChangedEvent

_music_events = import_module("yoyopod.integrations.music.events")
TrackChangedEvent = _music_events.TrackChangedEvent
PlaybackStateChangedEvent = _music_events.PlaybackStateChangedEvent
MusicAvailabilityChangedEvent = _music_events.MusicAvailabilityChangedEvent

_network_events = import_module("yoyopod.integrations.network.events")
NetworkModemReadyEvent = _network_events.NetworkModemReadyEvent
NetworkRegisteredEvent = _network_events.NetworkRegisteredEvent
NetworkPppUpEvent = _network_events.NetworkPppUpEvent
NetworkPppDownEvent = _network_events.NetworkPppDownEvent
NetworkSignalUpdateEvent = _network_events.NetworkSignalUpdateEvent

_location_events = import_module("yoyopod.integrations.location.events")
NetworkGpsFixEvent = _location_events.NetworkGpsFixEvent
NetworkGpsNoFixEvent = _location_events.NetworkGpsNoFixEvent


