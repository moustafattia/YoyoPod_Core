"""Compatibility shim for relocated mpv playback adapters."""

from yoyopod.backends.music import mpv as _canonical

threading = _canonical.threading
time = _canonical.time
logger = _canonical.logger
MusicBackend = _canonical.MusicBackend
MpvBackend = _canonical.MpvBackend
MockMusicBackend = _canonical.MockMusicBackend
_coerce_time_position_ms = _canonical._coerce_time_position_ms

__all__ = ["MockMusicBackend", "MpvBackend", "MusicBackend"]
