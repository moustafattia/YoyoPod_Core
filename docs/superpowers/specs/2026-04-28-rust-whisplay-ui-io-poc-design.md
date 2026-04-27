# Rust Whisplay UI I/O PoC - Design Spec

## Problem

YoYoPod's long-term direction is to move the app runtime to Rust. The first
blocker is proving that Rust can own the UI hardware layer reliably before any
real screen or runtime migration starts.

Today, Python owns the runtime, screen manager, display HAL, input HAL, LVGL
binding, and Whisplay driver integration. The Whisplay production path depends
on the Python `WhisPlay` driver plus the C LVGL shim. A Rust runtime cannot be
credible until the hardware behavior below the UI HAL can be replaced or wrapped
without regressions.

## Goal

Build a Whisplay-only Rust sidecar proof of concept that proves three things:

1. Rust can draw pixels to the Whisplay display.
2. Rust can read the Whisplay one-button input and emit the same semantic
   actions as the current Python input adapter.
3. Python can supervise the Rust process and exchange simple commands/events
   with it without destabilizing the main runtime.

This is a hardware I/O proof, not a screen migration.

## Non-Goals

- Do not port real YoYoPod screens.
- Do not introduce Slint, LVGL-rs, or a Rust widget toolkit yet.
- Do not support browser simulation.
- Do not support Pimoroni or four-button input.
- Do not move VoIP, music, power, network, or app state into Rust.
- Do not replace the production LVGL path until the PoC has passed on hardware.

## Scope

The PoC targets only PiSugar Whisplay hardware in the one-button interaction
profile. It should run on the dev lane and be opt-in behind a clearly named
config flag or CLI command. Existing LVGL production behavior remains the normal
runtime path.

The PoC may be launched either as:

- a standalone `yoyopod rust-ui-poc` style command, or
- an optional sidecar started by Python during app setup.

The standalone command is preferred for the first iteration because it isolates
hardware bring-up from app boot complexity.

## Architecture

```text
Python coordinator / CLI
        |
        | stdin/stdout protocol
        v
Rust Whisplay UI sidecar
        |- display output adapter
        |  |- RGB565 framebuffer
        |  |- Whisplay display init
        |  `- full-frame flush first, partial flush later
        |
        |- one-button input adapter
        |  |- GPIO/device polling
        |  |- debounce
        |  |- single tap / double tap / long hold grammar
        |  `- semantic input events
        |
        `- health/status loop
```

Python remains the process supervisor and protocol peer. Rust owns only the
Whisplay display and one-button input for the duration of the PoC.

## Rust Sidecar Responsibilities

The Rust sidecar owns:

- hardware initialization for the Whisplay display path
- backlight setup if required for visible output
- an in-memory `240x280` RGB565 framebuffer
- a minimal software renderer for test shapes and text
- display flushes to the Whisplay panel
- one-button polling and gesture decoding
- protocol event emission
- clean shutdown when stdin closes or a shutdown command arrives

The first renderer only needs enough drawing support to prove correctness:

- clear screen
- filled rectangles
- simple status blocks
- monotonic counter
- optionally bitmap or minimal text if a small font path is practical

## Python Responsibilities

Python owns:

- starting and stopping the Rust process
- logging sidecar stderr
- sending test render commands
- receiving health and input events
- timing out startup if the sidecar does not become ready
- killing the sidecar on app shutdown or PoC command exit

The PoC should reuse the existing sidecar supervision patterns where practical,
but it should not couple itself to the VoIP sidecar protocol unless the common
pieces are already cleanly reusable.

## Protocol

Use newline-delimited JSON for the first PoC. The messages are tiny, human
readable, and easy to debug over SSH. Msgpack can be considered later if the
protocol becomes hot or high-volume.

Commands from Python to Rust:

```json
{"kind":"command","type":"show_test_scene","counter":1}
{"kind":"command","type":"set_backlight","brightness":0.8}
{"kind":"command","type":"shutdown"}
```

Events from Rust to Python:

```json
{"kind":"event","type":"ready","display":{"width":240,"height":280}}
{"kind":"event","type":"input","action":"advance","method":"single_tap","timestamp_ms":12345}
{"kind":"event","type":"input","action":"select","method":"double_tap","timestamp_ms":12590}
{"kind":"event","type":"input","action":"back","method":"long_hold","duration_ms":812}
{"kind":"event","type":"health","frames":10,"button_events":3}
{"kind":"event","type":"error","code":"display_init_failed","message":"..."}
```

The sidecar should treat unknown commands as protocol errors and keep running
unless the error makes hardware ownership unsafe.

## Input Behavior

The Rust input adapter must mirror the current Python one-button grammar:

- single tap emits `advance`
- double tap emits `select`
- long hold emits `back`
- optional raw PTT passthrough can be deferred until after the first PoC

The default timing values come from `config/device/hardware.yaml`:

- debounce: 50 ms
- double tap window: 300 ms
- long hold threshold: 800 ms

The sidecar should emit both raw activity diagnostics and semantic input events
during hardware validation so timing problems are visible in logs.

## Display Behavior

The first display milestone is full-frame flush. Partial flush can be added
after the sidecar proves stable.

The Rust framebuffer should match the current Whisplay dimensions and pixel
format:

- width: 240
- height: 280
- orientation: portrait
- framebuffer: RGB565

The PoC should record flush timing and report slow frames in stderr or health
events. This gives an early baseline against the current Python Whisplay adapter
metrics.

## Hardware Replacement Inventory

The implementation must identify replacements below the current HAL for:

- Whisplay display initialization
- SPI transfer to the panel
- GPIO control needed by reset, data/command, backlight, or board power
- GPIO input for the one physical button
- cleanup that leaves the display and GPIO lines in a sane state

If the Whisplay board protocol is not clear enough for pure Rust in the first
iteration, a temporary FFI bridge may be used only as a stepping stone. The
preferred end state is native Rust hardware I/O below the HAL.

## Error Handling

Startup failures should be explicit:

- missing GPIO/SPI permissions
- display init failure
- button input init failure
- malformed protocol command
- sidecar process exit before ready

Python must surface these as PoC failures, not silently fall back to the normal
LVGL UI path during the PoC command.

Runtime errors should be logged with enough hardware context to debug on the Pi:

- operation name
- errno or driver error
- display dimensions
- GPIO/SPI identifiers when available
- last successful health counters

## Testing

Host-side tests:

- Rust input state-machine unit tests for debounce, single tap, double tap, and
  long hold.
- Rust protocol encode/decode tests.
- Python supervisor tests using a fake sidecar process.
- Python protocol parser tests for ready, input, health, and error events.

Pi validation:

- sidecar starts and emits `ready`
- display shows changing test scene
- single tap emits `advance`
- double tap emits `select`
- long hold emits `back`
- sidecar shuts down cleanly
- repeated start/stop loop succeeds at least 20 times
- five-minute idle/display/input soak does not crash or leak obvious resources

## Acceptance Criteria

The PoC is successful when all of the following are true on Whisplay hardware:

- Rust renders visible output without using the Python `WhisPlay` runtime path.
- Rust emits correct one-button semantic events with current timing thresholds.
- Python starts, observes readiness, receives input events, and stops the
  sidecar cleanly.
- Hardware resources are released after shutdown.
- The normal Python LVGL runtime still works when the PoC is disabled.

## Follow-Up Decisions

After this PoC, choose the next Rust UI layer:

1. Rust-native framebuffer UI for maximum control and minimal dependencies.
2. Rust-owned LVGL through a C ABI or Rust bindings.
3. Slint or another retained UI toolkit if it proves compatible with the small
   display, one-button UX, and Pi Zero 2W resource limits.

The decision should be based on measured hardware behavior, not preference.
