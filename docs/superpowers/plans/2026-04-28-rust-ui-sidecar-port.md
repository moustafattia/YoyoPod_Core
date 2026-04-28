# Rust UI Sidecar Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move Whisplay one-button UI ownership into the Rust sidecar while the Python app remains the runtime owner for music, calls, voice, power, and network services.

**Architecture:** Python publishes typed runtime snapshots and app events into the Rust UI worker. Rust owns the active screen, focus index, screen stack, one-button action handling, transitions, and rendering; it emits narrow `ui.intent` events when the runtime must perform domain work.

**Tech Stack:** Python 3.12 app runtime, existing worker supervisor NDJSON protocol, Rust 1.82 sidecar, existing LVGL C shim, Whisplay GPIO/SPI hardware backend.

---

### Task 1: Rust UI State Machine

**Files:**
- Create: `workers/ui/rust/src/ui_state.rs`
- Modify: `workers/ui/rust/src/main.rs`
- Test: `workers/ui/rust/src/ui_state.rs`

- [x] **Step 1: Write failing Rust tests**

Add unit tests proving that:
- a default snapshot starts on `hub`
- `Advance` cycles Hub focus
- `Select` on Hub `Listen` pushes `listen`
- `Back` returns from `listen` to `hub`
- incoming-call snapshots preempt the active screen with `incoming_call`
- selecting incoming call emits a `call.answer` intent without directly mutating Python call state

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml ui_state -- --nocapture`
Expected: FAIL because `ui_state` does not exist.

- [x] **Step 2: Implement minimal state machine**

Add typed snapshot structs for `music`, `call`, `voice`, `power`, `network`, `hub`, `playlists`, `contacts`, and overlays. Add `UiScreen`, `UiIntent`, and `UiRuntime` with `apply_snapshot`, `handle_input`, `active_view`, `take_intents`, and stack navigation helpers.

- [x] **Step 3: Verify Rust state tests pass**

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml ui_state -- --nocapture`
Expected: PASS.

### Task 2: Rust Worker Commands

**Files:**
- Modify: `workers/ui/rust/src/worker.rs`
- Modify: `workers/ui/rust/src/render.rs`
- Modify: `workers/ui/rust/src/lvgl_bridge.rs`
- Test: `workers/ui/rust/src/worker.rs`

- [x] **Step 1: Write failing worker tests**

Add unit tests proving that:
- `ui.runtime_snapshot` renders the active Rust-owned screen and increments frames
- `ui.input_action` applies one semantic input action and emits `ui.intent` when the action needs Python runtime work
- `ui.tick` polls the hardware button, advances the one-button machine, and flushes dirty screens

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml worker -- --nocapture`
Expected: FAIL because commands are missing.

- [x] **Step 2: Implement worker command handling**

Add command handlers for `ui.runtime_snapshot`, `ui.input_action`, and `ui.tick`. Keep legacy `ui.show_test_scene`, `ui.show_hub`, `ui.poll_input`, and `ui.health` working.

- [x] **Step 3: Verify worker tests pass**

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml worker -- --nocapture`
Expected: PASS.

### Task 3: Python Snapshot and Intent Bridge

**Files:**
- Create: `yoyopod/ui/rust_sidecar/state.py`
- Create: `yoyopod/ui/rust_sidecar/coordinator.py`
- Modify: `yoyopod/ui/rust_sidecar/__init__.py`
- Modify: `yoyopod/config/models/app.py`
- Test: `tests/ui/test_rust_sidecar_state.py`
- Test: `tests/ui/test_rust_sidecar_coordinator.py`
- Test: `tests/config/test_config_models.py`

- [x] **Step 1: Write failing Python tests**

Add tests proving that:
- `RustUiRuntimeSnapshot.from_app(app)` serializes current app context into the Rust snapshot payload
- the coordinator sends `ui.runtime_snapshot` through the worker supervisor without creating tracked request timeouts
- `ui.intent` events dispatch to registered Python runtime services
- config exposes an opt-in sidecar flag and worker path

Run: `uv run pytest -q tests/ui/test_rust_sidecar_state.py tests/ui/test_rust_sidecar_coordinator.py tests/config/test_config_models.py`
Expected: FAIL because bridge files and config fields are missing.

- [x] **Step 2: Implement Python bridge**

Add the snapshot model, coordinator, and config fields. The coordinator should be opt-in and should not replace the production Python screen manager until enabled.

- [x] **Step 3: Verify Python bridge tests pass**

Run: `uv run pytest -q tests/ui/test_rust_sidecar_state.py tests/ui/test_rust_sidecar_coordinator.py tests/config/test_config_models.py`
Expected: PASS.

### Task 4: Full Verification and Commit

**Files:**
- Modify docs only if command names or hardware deploy instructions change.

- [x] **Step 1: Run Rust tests**

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml`
Expected: PASS.

- [x] **Step 2: Run Rust hardware-feature tests**

Run: `cargo test --manifest-path workers/ui/rust/Cargo.toml --features whisplay-hardware`
Expected: PASS.

- [ ] **Step 3: Run required pre-commit gates**

Run:
`uv run python scripts/quality.py gate`
`uv run pytest -q`
Expected: both PASS.

- [ ] **Step 4: Commit**

Run:
`git add docs/superpowers/plans/2026-04-28-rust-ui-sidecar-port.md workers/ui/rust/src yoyopod/ui/rust_sidecar yoyopod/config/models/app.py tests/ui tests/config/test_config_models.py`
`git commit -m "feat: add rust ui sidecar state machine"`
