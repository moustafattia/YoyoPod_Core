from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Callable, cast

from yoyopod.core.bus import Bus
from yoyopod.core.events import (
    WorkerDomainStateChangedEvent,
    WorkerMessageReceivedEvent,
)
from yoyopod.core.scheduler import MainThreadScheduler
from yoyopod.core.workers.process import WorkerProcessConfig
from yoyopod.core.workers.supervisor import WorkerSupervisor


def _write_worker(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "fake_worker.py"
    path.write_text(body, encoding="utf-8")
    return path


def _poll_until(assertion: Callable[[], bool], *, timeout_seconds: float = 2.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if assertion():
            return
        time.sleep(0.01)
    assert assertion()


def test_supervisor_publishes_worker_messages_on_main_bus(tmp_path: Path) -> None:
    worker = _write_worker(
        tmp_path,
        """
import json
import sys
sys.stdout.write(json.dumps({
    "schema_version": 1,
    "kind": "event",
    "type": "fake.ready",
    "request_id": None,
    "timestamp_ms": 1,
    "deadline_ms": 0,
    "payload": {"ready": True},
}) + "\\n")
sys.stdout.flush()
for line in sys.stdin:
    pass
""".strip(),
    )
    bus = Bus()
    scheduler = MainThreadScheduler()
    state_events: list[WorkerDomainStateChangedEvent] = []
    message_events: list[WorkerMessageReceivedEvent] = []
    bus.subscribe(WorkerDomainStateChangedEvent, state_events.append)
    bus.subscribe(WorkerMessageReceivedEvent, message_events.append)
    supervisor = WorkerSupervisor(scheduler=scheduler, bus=bus)
    supervisor.register(
        "voice",
        WorkerProcessConfig(name="voice", argv=[sys.executable, "-u", str(worker)]),
    )

    supervisor.start("voice")
    try:
        _poll_until(lambda: supervisor.poll() >= 1)
        bus.drain()
        snapshot = supervisor.snapshot()
    finally:
        supervisor.stop_all(grace_seconds=0.1)

    assert state_events[0] == WorkerDomainStateChangedEvent(
        domain="voice",
        state="running",
        reason="started",
    )
    assert message_events == [
        WorkerMessageReceivedEvent(
            domain="voice",
            kind="event",
            type="fake.ready",
            request_id=None,
            payload={"ready": True},
        )
    ]
    assert cast(int, snapshot["voice"]["received_messages"]) >= 1


def test_supervisor_marks_crashed_worker_degraded(tmp_path: Path) -> None:
    worker = _write_worker(tmp_path, "raise SystemExit(7)")
    bus = Bus()
    scheduler = MainThreadScheduler()
    events: list[WorkerDomainStateChangedEvent] = []
    bus.subscribe(WorkerDomainStateChangedEvent, events.append)
    supervisor = WorkerSupervisor(
        scheduler=scheduler,
        bus=bus,
        restart_backoff_seconds=60.0,
    )
    supervisor.register(
        "voice",
        WorkerProcessConfig(name="voice", argv=[sys.executable, "-u", str(worker)]),
    )

    supervisor.start("voice")
    supervisor.wait_until_exited("voice", timeout_seconds=2.0)
    supervisor.poll()
    bus.drain()

    assert supervisor.snapshot()["voice"]["state"] == "degraded"
    assert events[-1].domain == "voice"
    assert events[-1].state == "degraded"
    assert events[-1].reason == "process_exited"


def test_supervisor_request_timeout_sends_cancel(tmp_path: Path) -> None:
    worker = _write_worker(
        tmp_path,
        """
import json
import sys
for line in sys.stdin:
    msg = json.loads(line)
    if msg["type"] == "voice.cancel":
        sys.stdout.write(json.dumps({
            "schema_version": 1,
            "kind": "result",
            "type": "voice.cancelled",
            "request_id": msg.get("request_id"),
            "timestamp_ms": 1,
            "deadline_ms": 0,
            "payload": {"cancelled": True},
        }) + "\\n")
        sys.stdout.flush()
""".strip(),
    )
    bus = Bus()
    scheduler = MainThreadScheduler()
    message_events: list[WorkerMessageReceivedEvent] = []
    bus.subscribe(WorkerMessageReceivedEvent, message_events.append)
    supervisor = WorkerSupervisor(scheduler=scheduler, bus=bus)
    supervisor.register(
        "voice",
        WorkerProcessConfig(name="voice", argv=[sys.executable, "-u", str(worker)]),
    )

    supervisor.start("voice")
    try:
        assert supervisor.send_request(
            "voice",
            type="voice.transcribe",
            payload={"path": "/tmp/a.wav"},
            request_id="req-timeout",
            timeout_seconds=0.01,
        )
        time.sleep(0.05)
        supervisor.poll()
        _poll_until(lambda: supervisor.poll() >= 1)
        bus.drain()
        snapshot = supervisor.snapshot()
    finally:
        supervisor.stop_all(grace_seconds=0.1)

    assert snapshot["voice"]["request_timeouts"] == 1
    assert snapshot["voice"]["pending_requests"] == 0
    assert any(message.type == "voice.cancelled" for message in message_events)
