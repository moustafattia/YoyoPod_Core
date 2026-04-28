# Rust UI PoC

The Rust UI PoC is an opt-in Whisplay-only hardware I/O test. It does not
replace the production Python LVGL UI.

## Build

```bash
yoyopod build rust-ui-poc
```

For host-only protocol tests:

```bash
yoyopod build rust-ui-poc --no-hardware-feature
```

CI also builds the Whisplay worker on a native Linux ARM64 runner and uploads it
as the `yoyopod-rust-ui-poc-${{ github.sha }}` artifact. Use that artifact, or a
binary built on another ARM64 Linux board, when the Pi Zero 2W is too slow to
compile the Rust dependencies directly.

## Required Whisplay Environment

The first hardware backend reads explicit GPIO/SPI settings:

- `YOYOPOD_WHISPLAY_SPI_BUS`
- `YOYOPOD_WHISPLAY_SPI_CS`
- `YOYOPOD_WHISPLAY_SPI_HZ`
- `YOYOPOD_WHISPLAY_DC_GPIO`
- `YOYOPOD_WHISPLAY_RESET_GPIO`
- `YOYOPOD_WHISPLAY_BACKLIGHT_GPIO`
- `YOYOPOD_WHISPLAY_BUTTON_GPIO`
- `YOYOPOD_WHISPLAY_BUTTON_ACTIVE_LOW`

The button default is GPIO 26, active low, matching the current Python fallback.

## Run On Pi

```bash
yoyopod pi rust-ui-poc --worker workers/ui/rust/build/yoyopod-rust-ui-poc --frames 10
```

If the worker came from CI artifacts, make it executable after copying it to the
Pi:

```bash
chmod +x workers/ui/rust/build/yoyopod-rust-ui-poc
```

Expected result:

- the Whisplay display shows changing test frames
- the command prints a `ui.ready` payload
- the command prints a `ui.health` payload
