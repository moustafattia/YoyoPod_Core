"""Canonical public seam for voice interaction models and services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yoyopod.integrations.voice.manager import VoiceManager, VoiceService
    from yoyopod.integrations.voice.models import (
        VoiceCaptureRequest,
        VoiceCaptureResult,
        VoiceSettings,
        VoiceTranscript,
    )


_PUBLIC_EXPORTS = {
    "VoiceCaptureRequest": ("yoyopod.integrations.voice.models", "VoiceCaptureRequest"),
    "VoiceCaptureResult": ("yoyopod.integrations.voice.models", "VoiceCaptureResult"),
    "VoiceManager": ("yoyopod.integrations.voice.manager", "VoiceManager"),
    "VoiceService": ("yoyopod.integrations.voice.manager", "VoiceService"),
    "VoiceSettings": ("yoyopod.integrations.voice.models", "VoiceSettings"),
    "VoiceTranscript": ("yoyopod.integrations.voice.models", "VoiceTranscript"),
}


def __getattr__(name: str) -> Any:
    """Load public voice exports lazily to avoid compatibility import cycles."""

    try:
        module_name, attribute = _PUBLIC_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    module = __import__(module_name, fromlist=[attribute])
    return getattr(module, attribute)


__all__ = [
    "VoiceCaptureRequest",
    "VoiceCaptureResult",
    "VoiceManager",
    "VoiceService",
    "VoiceSettings",
    "VoiceTranscript",
]
