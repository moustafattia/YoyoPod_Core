"""Tests for command-first YoYo voice routing."""

from __future__ import annotations

from yoyopod.integrations.voice.dictionary import VoiceCommandDictionary
from yoyopod.integrations.voice.router import (
    VoiceRouteKind,
    VoiceRouter,
)


def test_router_strips_activation_prefix_and_routes_command() -> None:
    router = VoiceRouter(
        dictionary=VoiceCommandDictionary.from_builtins(),
        activation_prefixes=("hey yoyo", "yoyo"),
        ask_fallback_enabled=True,
    )

    decision = router.route("hey yoyo call mama")

    assert decision.kind is VoiceRouteKind.COMMAND
    assert decision.normalized_text == "call mama"
    assert decision.command is not None
    assert decision.command.contact_name == "mama"
    assert decision.reason == "command_match"


def test_router_falls_back_to_ask_for_non_command() -> None:
    router = VoiceRouter(
        dictionary=VoiceCommandDictionary.from_builtins(),
        activation_prefixes=("hey yoyo", "yoyo"),
        ask_fallback_enabled=True,
    )

    decision = router.route("yoyo why is the sky blue")

    assert decision.kind is VoiceRouteKind.ASK_FALLBACK
    assert decision.normalized_text == "why is the sky blue"
    assert decision.command is None
    assert decision.reason == "ask_fallback"


def test_router_returns_local_help_when_fallback_disabled() -> None:
    router = VoiceRouter(
        dictionary=VoiceCommandDictionary.from_builtins(),
        activation_prefixes=("hey yoyo", "yoyo"),
        ask_fallback_enabled=False,
    )

    decision = router.route("tell me a story")

    assert decision.kind is VoiceRouteKind.LOCAL_HELP
    assert decision.normalized_text == "tell me a story"
    assert decision.reason == "no_command_no_fallback"
