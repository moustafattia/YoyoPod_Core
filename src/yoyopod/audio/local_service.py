"""Backward-compatible shim for local music service imports."""

from __future__ import annotations

from yoyopod.integrations.music.library import (
    AUDIO_EXTENSIONS,
    LEGACY_LIBRARY_ROOTS,
    LEGACY_PLAYLIST_SCHEMES,
    LEGACY_TRACK_SCHEMES,
    LocalLibraryItem,
    LocalMusicService,
)

__all__ = [
    "AUDIO_EXTENSIONS",
    "LocalLibraryItem",
    "LocalMusicService",
    "LEGACY_LIBRARY_ROOTS",
    "LEGACY_PLAYLIST_SCHEMES",
    "LEGACY_TRACK_SCHEMES",
]
