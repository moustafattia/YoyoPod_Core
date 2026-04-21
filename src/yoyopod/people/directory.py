"""Compatibility shim for historical people-directory import path."""

from __future__ import annotations

from yoyopod.integrations.contacts.directory import PeopleDirectory, PeopleManager

__all__ = ["PeopleDirectory", "PeopleManager"]
