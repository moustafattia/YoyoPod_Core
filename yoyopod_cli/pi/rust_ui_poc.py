"""Whisplay-only Rust UI PoC validation command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from yoyopod.ui.rust_sidecar.protocol import UiEnvelope
from yoyopod.ui.rust_sidecar.supervisor import RustUiSidecarSupervisor


def _default_worker_path() -> Path:
    suffix = ".exe" if __import__("os").name == "nt" else ""
    return Path("workers") / "ui" / "rust" / "build" / f"yoyopod-rust-ui-poc{suffix}"


def rust_ui_poc(
    worker: Annotated[
        Path,
        typer.Option("--worker", help="Path to the Rust UI PoC worker binary."),
    ] = _default_worker_path(),
    frames: Annotated[
        int,
        typer.Option("--frames", min=1, help="Number of test scene frames to send."),
    ] = 10,
    hardware: Annotated[
        str,
        typer.Option("--hardware", help="Worker hardware mode: mock or whisplay."),
    ] = "whisplay",
) -> None:
    """Run the Rust UI PoC against Whisplay hardware."""

    argv = [str(worker), "--hardware", hardware]
    supervisor = RustUiSidecarSupervisor(argv=argv)
    ready = supervisor.start()
    typer.echo(f"Rust UI PoC ready: {ready.payload}")

    try:
        for counter in range(1, frames + 1):
            supervisor.send(
                UiEnvelope.command(
                    "ui.show_test_scene",
                    {"counter": counter},
                    request_id=f"frame-{counter}",
                )
            )
        supervisor.send(UiEnvelope.command("ui.health", request_id="health"))
        health = supervisor.read_event()
        typer.echo(
            "Rust UI PoC health: "
            f"frames={health.payload.get('frames')} "
            f"button_events={health.payload.get('button_events')}"
        )
    finally:
        supervisor.stop()
