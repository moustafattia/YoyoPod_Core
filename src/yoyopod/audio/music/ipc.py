"""Compatibility shim for relocated mpv IPC transport."""

from yoyopod.backends.music import ipc as _canonical

json = _canonical.json
queue = _canonical.queue
socket = _canonical.socket
threading = _canonical.threading
logger = _canonical.logger
MpvIpcClient = _canonical.MpvIpcClient

__all__ = ["MpvIpcClient"]
