"""Compatibility exports for the cloud HTTP backend."""

from __future__ import annotations

from yoyopod.cloud.client import CloudClientError, CloudDeviceClient

CloudHttpClient = CloudDeviceClient

__all__ = ["CloudClientError", "CloudDeviceClient", "CloudHttpClient"]
