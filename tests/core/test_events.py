"""Tests for new scaffold events exported from `yoyopod.core.events`."""

from __future__ import annotations

from yoyopod.core import LifecycleEvent, StateChangedEvent


def test_scaffold_events_are_constructible() -> None:
    lifecycle = LifecycleEvent(phase="ready", detail="booted")
    changed = StateChangedEvent(
        entity="call.state",
        old="idle",
        new="ringing",
        attrs={"caller": "Ada"},
        last_changed_at=1.5,
    )

    assert lifecycle.phase == "ready"
    assert changed.entity == "call.state"
