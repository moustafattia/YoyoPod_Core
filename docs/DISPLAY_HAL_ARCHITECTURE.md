# YoyoPod Display HAL Architecture

**Last updated:** 2026-04-22
**Status:** Current implementation

This document describes the live display abstraction used by the LVGL-only
Whisplay runtime.

## Goals

- keep screen code hardware-agnostic
- preserve the backward-compatible `Display` facade
- use one render contract for both hardware and simulation
- avoid duplicate preview-only layout engines

## Current Files

- `src/yoyopod/ui/display/hal.py`: HAL interface
- `src/yoyopod/ui/display/manager.py`: `Display` facade
- `src/yoyopod/ui/display/factory.py`: adapter selection and simulation startup
- `src/yoyopod/ui/display/adapters/whisplay.py`: Whisplay hardware adapter plus simulation mirror
- `src/yoyopod/ui/display/rgb565.py`: framebuffer and PNG helpers used by the adapter

## Architecture

```text
Display
  -> get_display(...)
     -> WhisplayDisplayAdapter
        -> LVGL backend
        -> hardware SPI flushes or browser preview transport
        -> RGB565 framebuffer screenshots
```

## Supported Runtime Surfaces

### Whisplay hardware

- `240x280`
- portrait
- PiSugar Whisplay HAT
- LVGL-only production path

### Whisplay-profile simulation

- `240x280`
- portrait
- browser preview via `src/yoyopod/ui/display/adapters/simulation_web/server.py`
- same LVGL/RGB565 render contract as hardware

## Backward Compatibility Contract

Concrete screens and app code still create `Display(...)`, not hardware-specific adapters.

The facade exposes:

- dimensions and orientation
- shared color constants
- LVGL-aware display lifecycle
- RGB565 region flushes
- screenshots and cleanup

Immediate raw drawing primitives still exist on the facade for compatibility,
but the Whisplay adapter now rejects them at runtime because live rendering is
scene-driven through LVGL.

## Selection Rules

`factory.py` currently chooses hardware using:

1. explicit `display.hardware` config
2. `YOYOPOD_DISPLAY`
3. Whisplay driver path detection
4. simulation fallback

If `simulate=True`, simulation always uses the Whisplay-profile adapter.

## Production Contract

- Non-simulated Whisplay runs require `display.whisplay_renderer=lvgl`.
- If the Whisplay driver, board init, or LVGL backend is unavailable, startup fails loudly.
- There is no supported PIL renderer or alternate production display backend in the current runtime.

## Summary

The display HAL is implemented and frozen around one runtime surface: Whisplay
hardware plus its Whisplay-profile simulation mirror.
