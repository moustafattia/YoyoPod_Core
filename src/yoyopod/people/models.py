"""Compatibility shim for the relocated contacts models."""

from yoyopod.integrations.contacts.models import Contact, contacts_from_mapping, contacts_to_mapping

__all__ = ["Contact", "contacts_from_mapping", "contacts_to_mapping"]
