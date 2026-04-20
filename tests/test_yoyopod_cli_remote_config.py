"""Tests for yoyopod_cli.remote_config — show/edit pi-deploy.local.yaml."""
from __future__ import annotations

from typer.testing import CliRunner

from yoyopod_cli.remote_config import app


def test_show_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["show", "--help"])
    assert result.exit_code == 0


def test_edit_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["edit", "--help"])
    assert result.exit_code == 0


def test_show_outputs_yaml(monkeypatch) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["show"])
    assert result.exit_code == 0
    assert "project_dir" in result.output
