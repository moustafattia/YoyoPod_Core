"""GPS backend wrapper built on the existing SIM7600 transport path."""

from __future__ import annotations

from typing import Any

from yoyopod.network.gps import GpsReader
from yoyopod.network.transport import SerialTransport


class GpsBackend:
    """Own a GPS reader plus its serial transport for scaffold usage."""

    def __init__(self, config: object, *, transport: object | None = None) -> None:
        self._transport = transport or SerialTransport(
            port=str(getattr(config, "serial_port")),
            baud_rate=int(getattr(config, "baud_rate", 115200)),
        )
        self._owns_transport = transport is None
        self._reader = GpsReader(self._transport)

    def enable(self) -> bool:
        """Enable the GPS engine and return whether the modem accepted it."""

        self._ensure_open()
        return self._reader.enable()

    def disable(self) -> None:
        """Disable the GPS engine."""

        self._ensure_open()
        self._reader.disable()

    def get_fix(self) -> Any | None:
        """Return the latest GPS fix, or `None` when there is no fix."""

        self._ensure_open()
        return self._reader.query()

    def close(self) -> None:
        """Close the owned serial transport when this backend created it."""

        if self._owns_transport:
            self._transport.close()

    def _ensure_open(self) -> None:
        is_open = getattr(self._transport, "is_open", None)
        if is_open is True:
            return
        if callable(is_open) and is_open():
            return
        self._transport.open()
