"""Runtime metrics storage for input, queue, and responsiveness markers."""

from __future__ import annotations

import time
from typing import Any


class RuntimeMetricsStore:
    """Track small runtime markers that status and diagnostics need to read."""

    def __init__(self) -> None:
        self.last_input_activity_at = 0.0
        self.last_input_activity_action_name: str | None = None
        self.last_input_handled_at = 0.0
        self.last_input_handled_action_name: str | None = None
        self.last_responsiveness_capture_at = 0.0
        self.last_responsiveness_capture_reason: str | None = None
        self.last_responsiveness_capture_scope: str | None = None
        self.last_responsiveness_capture_summary: str | None = None
        self.last_responsiveness_capture_artifacts: dict[str, str] = {}

    @staticmethod
    def _queue_depth(queue_obj: object) -> int | None:
        """Return a best-effort queue depth for runtime diagnostics."""

        qsize = getattr(queue_obj, "qsize", None)
        if not callable(qsize):
            return None

        try:
            return int(qsize())
        except (NotImplementedError, TypeError, ValueError):
            return None

    def pending_main_thread_callback_count(
        self,
        regular_queue: object,
        safety_queue: object,
    ) -> int | None:
        """Return the combined generic and safety callback backlog."""

        callback_backlog = self._queue_depth(regular_queue)
        safety_backlog = self._queue_depth(safety_queue)
        if callback_backlog is None and safety_backlog is None:
            return None
        return max(0, callback_backlog or 0) + max(0, safety_backlog or 0)

    def note_input_activity(
        self,
        action: object,
        _data: Any | None = None,
        *,
        captured_at: float | None = None,
    ) -> None:
        """Record raw or semantic input activity before the coordinator drains it."""

        self.last_input_activity_at = time.monotonic() if captured_at is None else captured_at
        self.last_input_activity_action_name = getattr(action, "value", None)

    def note_handled_input(
        self,
        *,
        action_name: str | None,
        handled_at: float,
    ) -> None:
        """Record semantic user activity after the coordinator handles it."""

        self.last_input_handled_at = handled_at
        self.last_input_handled_action_name = action_name

    def record_responsiveness_capture(
        self,
        *,
        captured_at: float,
        reason: str,
        suspected_scope: str,
        summary: str,
        artifacts: dict[str, str] | None = None,
    ) -> None:
        """Persist the latest automatic hang-evidence capture metadata."""

        self.last_responsiveness_capture_at = captured_at
        self.last_responsiveness_capture_reason = reason
        self.last_responsiveness_capture_scope = suspected_scope
        self.last_responsiveness_capture_summary = summary
        self.last_responsiveness_capture_artifacts = dict(artifacts or {})
