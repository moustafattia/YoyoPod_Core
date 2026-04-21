"""Compatibility shim for relocated mpv process management."""

from yoyopod.backends.music import process as _canonical

subprocess = _canonical.subprocess
Path = _canonical.Path
logger = _canonical.logger
MpvProcess = _canonical.MpvProcess

__all__ = ["MpvProcess"]
