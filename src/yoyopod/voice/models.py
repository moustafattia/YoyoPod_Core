"""Compatibility shims for the relocated canonical voice models."""

from yoyopod.integrations.voice.models import (
    VoiceCaptureRequest,
    VoiceCaptureResult,
    VoiceSettings,
    VoiceTranscript,
)

__all__ = [
    "VoiceCaptureRequest",
    "VoiceCaptureResult",
    "VoiceSettings",
    "VoiceTranscript",
]
