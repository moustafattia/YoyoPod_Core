"""Deterministic parsing for local voice commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class VoiceCommandIntent(StrEnum):
    """Supported first-pass local voice intents."""

    CALL_CONTACT = "call_contact"
    READ_SCREEN = "read_screen"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE_MIC = "mute_mic"
    UNMUTE_MIC = "unmute_mic"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class VoiceCommandMatch:
    """Structured result from matching a transcript to a local intent."""

    intent: VoiceCommandIntent
    transcript: str
    contact_name: str = ""

    @property
    def is_command(self) -> bool:
        """Return True when the transcript mapped to a known command."""

        return self.intent is not VoiceCommandIntent.UNKNOWN


def match_voice_command(transcript: str) -> VoiceCommandMatch:
    """Map a transcript to the first supported local voice command."""

    normalized = " ".join(transcript.strip().lower().split())
    if not normalized:
        return VoiceCommandMatch(VoiceCommandIntent.UNKNOWN, transcript=transcript)
    if normalized.startswith("call "):
        contact_name = transcript.strip()[5:].strip()
        if contact_name:
            return VoiceCommandMatch(
                VoiceCommandIntent.CALL_CONTACT,
                transcript=transcript,
                contact_name=contact_name,
            )
    if normalized in {"read screen", "read the screen"}:
        return VoiceCommandMatch(VoiceCommandIntent.READ_SCREEN, transcript=transcript)
    if normalized in {"volume up", "turn volume up", "increase volume"}:
        return VoiceCommandMatch(VoiceCommandIntent.VOLUME_UP, transcript=transcript)
    if normalized in {"volume down", "turn volume down", "decrease volume"}:
        return VoiceCommandMatch(VoiceCommandIntent.VOLUME_DOWN, transcript=transcript)
    if normalized in {"mute mic", "mute microphone"}:
        return VoiceCommandMatch(VoiceCommandIntent.MUTE_MIC, transcript=transcript)
    if normalized in {"unmute mic", "unmute microphone"}:
        return VoiceCommandMatch(VoiceCommandIntent.UNMUTE_MIC, transcript=transcript)
    return VoiceCommandMatch(VoiceCommandIntent.UNKNOWN, transcript=transcript)
