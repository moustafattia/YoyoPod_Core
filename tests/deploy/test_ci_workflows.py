from __future__ import annotations

from pathlib import Path

CI_YML = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def test_slot_arm64_change_detector_matches_python_release_builder() -> None:
    workflow = CI_YML.read_text(encoding="utf-8")

    assert "build_release\\.py" in workflow
    assert "scripts/(build_release|build_slot_artifact_ci)\\.sh" not in workflow


def test_slot_arm64_pr_build_is_label_gated() -> None:
    workflow = CI_YML.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "contains(github.event.pull_request.labels.*.name, 'build-arm-slot')" in workflow
    assert "github.event_name == 'push'" in workflow


def test_rust_ui_ci_builds_arm64_binary_artifact() -> None:
    workflow = CI_YML.read_text(encoding="utf-8")

    assert "runs-on: ubuntu-24.04-arm" in workflow
    assert "cargo build --release --features whisplay-hardware --locked" in workflow
    assert "uses: actions/upload-artifact@v4" in workflow
    assert "name: yoyopod-rust-ui-poc-${{ github.sha }}" in workflow
    assert "workers/ui/rust/build/yoyopod-rust-ui-poc" in workflow
