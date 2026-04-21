"""Compatibility shim for relocated music playback models."""

from yoyopod.backends.music.models import MusicConfig, PlaybackQueue, Playlist, Track

__all__ = ["MusicConfig", "PlaybackQueue", "Playlist", "Track"]
