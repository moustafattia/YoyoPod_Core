"""Legacy voice public package entrypoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yoyopod.integrations.voice import (
        VoiceCaptureRequest,
        VoiceCaptureResult,
        VoiceManager,
        VoiceService,
        VoiceSettings,
        VoiceTranscript,
    )


_LAZY_EXPORTS = {
    "VoiceCaptureRequest": "yoyopod.integrations.voice",
    "VoiceCaptureResult": "yoyopod.integrations.voice",
    "VoiceManager": "yoyopod.integrations.voice",
    "VoiceService": "yoyopod.integrations.voice",
    "VoiceSettings": "yoyopod.integrations.voice",
    "VoiceTranscript": "yoyopod.integrations.voice",
}


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = __import__(module_name, fromlist=[name])
    return getattr(module, name)


__all__ = [
    "VoiceCaptureRequest",
    "VoiceCaptureResult",
    "VoiceManager",
    "VoiceService",
    "VoiceSettings",
    "VoiceTranscript",
]
