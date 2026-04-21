"""Compatibility export for callers still importing communication.messaging.store."""

from yoyopod.integrations.call.message_store import VoIPMessageStore

__all__ = ["VoIPMessageStore"]
