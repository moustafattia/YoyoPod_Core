"""Compatibility facade for relocated audio and music seams."""

from yoyopod.audio.manager import AudioDevice, AudioManager, MusicManager
from yoyopod.audio.volume import OutputVolumeController
from yoyopod.audio.volume_controller import AudioVolumeController
from yoyopod.backends.music import MockMusicBackend, MpvBackend, MusicBackend
from yoyopod.backends.music import MusicConfig, PlaybackQueue, Playlist, Track
from yoyopod.integrations.music.history import RecentTrackEntry, RecentTrackHistoryStore
from yoyopod.integrations.music.library import LocalLibraryItem, LocalMusicService

__all__ = [
    "AudioDevice",
    "AudioManager",
    "MusicManager",
    "AudioVolumeController",
    "LocalLibraryItem",
    "LocalMusicService",
    "MockMusicBackend",
    "MpvBackend",
    "MusicBackend",
    "MusicConfig",
    "PlaybackQueue",
    "OutputVolumeController",
    "Playlist",
    "RecentTrackEntry",
    "RecentTrackHistoryStore",
    "Track",
]
