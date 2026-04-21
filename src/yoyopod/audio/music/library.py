"""Backward-compatible shim for local music service imports."""

from __future__ import annotations

from yoyopod.integrations.music import library as _canonical

os = _canonical.os
random = _canonical.random
deque = _canonical.deque
logger = _canonical.logger
AUDIO_EXTENSIONS = _canonical.AUDIO_EXTENSIONS
LEGACY_LIBRARY_ROOTS = _canonical.LEGACY_LIBRARY_ROOTS
LEGACY_PLAYLIST_SCHEMES = _canonical.LEGACY_PLAYLIST_SCHEMES
LEGACY_TRACK_SCHEMES = _canonical.LEGACY_TRACK_SCHEMES
LocalLibraryItem = _canonical.LocalLibraryItem
LocalMusicService = _canonical.LocalMusicService

__all__ = [
    "AUDIO_EXTENSIONS",
    "LEGACY_LIBRARY_ROOTS",
    "LEGACY_PLAYLIST_SCHEMES",
    "LEGACY_TRACK_SCHEMES",
    "LocalLibraryItem",
    "LocalMusicService",
]
