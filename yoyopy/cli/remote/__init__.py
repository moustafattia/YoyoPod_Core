"""yoyopy/cli/remote/__init__.py — remote command group (SSH wrapper commands)."""

from __future__ import annotations

import typer

from yoyopy.cli.remote.infra import config, power, service
from yoyopy.cli.remote.lvgl import lvgl_soak
from yoyopy.cli.remote.ops import preflight, smoke, status, sync

remote_app = typer.Typer(
    name="remote",
    help="Commands that SSH to the Raspberry Pi from the dev machine.",
    no_args_is_help=True,
)

remote_app.command()(status)
remote_app.command()(sync)
remote_app.command()(smoke)
remote_app.command()(preflight)
remote_app.command(name="lvgl-soak")(lvgl_soak)
remote_app.command()(power)
remote_app.command()(config)
remote_app.command()(service)
