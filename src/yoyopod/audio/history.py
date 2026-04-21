"""Backward-compatible shim for recent-track history imports."""

from __future__ import annotations

from yoyopod.integrations.music.history import RecentTrackEntry, RecentTrackHistoryStore

__all__ = ["RecentTrackEntry", "RecentTrackHistoryStore"]
