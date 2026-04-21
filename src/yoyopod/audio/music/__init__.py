"""Compatibility facade for the relocated music domain seams."""

from yoyopod.backends.music import MockMusicBackend, MpvBackend, MusicBackend
from yoyopod.backends.music import MusicConfig, PlaybackQueue, Playlist, Track
from yoyopod.integrations.music.history import RecentTrackEntry, RecentTrackHistoryStore
from yoyopod.integrations.music.library import LocalLibraryItem, LocalMusicService

__all__ = [
    "MockMusicBackend",
    "MpvBackend",
    "MusicBackend",
    "MusicConfig",
    "PlaybackQueue",
    "Playlist",
    "LocalLibraryItem",
    "LocalMusicService",
    "RecentTrackEntry",
    "RecentTrackHistoryStore",
    "Track",
]
