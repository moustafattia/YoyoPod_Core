"""Compatibility shim for callers importing ``yoyopod.voice.service``."""

from __future__ import annotations

from yoyopod.integrations.voice import VoiceManager, VoiceService

__all__ = ["VoiceService", "VoiceManager"]
