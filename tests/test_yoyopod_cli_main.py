"""Tests for the yoyopod entry point and bare-invocation behavior."""
from __future__ import annotations

from typer.testing import CliRunner

from yoyopod_cli.main import app


def test_help_lists_yoyopod() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "yoyopod" in result.output.lower()


def test_version_flag_present() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
