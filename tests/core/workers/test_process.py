from __future__ import annotations

import sys
from pathlib import Path

from yoyopod.core.workers.process import WorkerProcessConfig, WorkerProcessRuntime


def _write_worker(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "fake_worker.py"
    path.write_text(body, encoding="utf-8")
    return path


def test_worker_process_round_trips_envelopes(tmp_path: Path) -> None:
    worker = _write_worker(
        tmp_path,
        """
import json
import sys

for line in sys.stdin:
    msg = json.loads(line)
    sys.stdout.write(json.dumps({
        "schema_version": 1,
        "kind": "result",
        "type": "voice.transcribe",
        "request_id": msg["request_id"],
        "timestamp_ms": 1001,
        "deadline_ms": 0,
        "payload": {"path": msg["payload"]["path"], "ok": True},
    }) + "\\n")
    sys.stdout.flush()
""".strip(),
    )
    runtime = WorkerProcessRuntime(
        WorkerProcessConfig(
            name="echo",
            argv=[sys.executable, "-u", str(worker)],
            receive_queue_size=4,
        )
    )

    runtime.start()
    try:
        assert runtime.send_command(
            type="voice.transcribe",
            payload={"path": "/tmp/audio.wav"},
            request_id="req-1",
            timestamp_ms=1000,
            deadline_ms=5000,
        )
        messages = runtime.wait_for_messages(count=1, timeout_seconds=2.0)
    finally:
        runtime.stop(grace_seconds=0.2)

    assert len(messages) == 1
    assert messages[0].kind == "result"
    assert messages[0].type == "voice.transcribe"
    assert messages[0].request_id == "req-1"
    assert messages[0].payload == {"path": "/tmp/audio.wav", "ok": True}
    snapshot = runtime.snapshot()
    assert snapshot.received_messages == 1
    assert snapshot.protocol_errors == 0


def test_worker_process_counts_malformed_stdout(tmp_path: Path) -> None:
    worker = _write_worker(
        tmp_path,
        """
import sys
sys.stdout.write("not json\\n")
sys.stdout.flush()
""".strip(),
    )
    runtime = WorkerProcessRuntime(
        WorkerProcessConfig(name="bad", argv=[sys.executable, "-u", str(worker)])
    )

    runtime.start()
    try:
        assert runtime.wait_until_exited(timeout_seconds=2.0)
        runtime.drain_messages()
        snapshot = runtime.snapshot()
    finally:
        runtime.stop(grace_seconds=0.1)

    assert snapshot.protocol_errors >= 1
    assert snapshot.received_messages == 0


def test_worker_process_stop_is_bounded_for_stuck_worker(tmp_path: Path) -> None:
    worker = _write_worker(
        tmp_path,
        """
import time
time.sleep(60)
""".strip(),
    )
    runtime = WorkerProcessRuntime(
        WorkerProcessConfig(name="stuck", argv=[sys.executable, "-u", str(worker)])
    )

    runtime.start()
    runtime.stop(grace_seconds=0.05)

    snapshot = runtime.snapshot()
    assert snapshot.running is False
    assert snapshot.terminated is True
