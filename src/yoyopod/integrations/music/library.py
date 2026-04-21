"""Canonical export for the local-music library service."""

from yoyopod.audio.music.library import (
    AUDIO_EXTENSIONS,
    LEGACY_LIBRARY_ROOTS,
    LEGACY_PLAYLIST_SCHEMES,
    LEGACY_TRACK_SCHEMES,
    LocalLibraryItem,
    LocalMusicService,
)

__all__ = [
    "AUDIO_EXTENSIONS",
    "LEGACY_LIBRARY_ROOTS",
    "LEGACY_PLAYLIST_SCHEMES",
    "LEGACY_TRACK_SCHEMES",
    "LocalLibraryItem",
    "LocalMusicService",
]
