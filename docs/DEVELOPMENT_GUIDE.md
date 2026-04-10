# Development Guide

This guide holds the operational detail that does not belong on the repo landing page.

## Python Environment

```bash
uv sync --extra dev
```

## System Dependencies

Raspberry Pi OS packages expected by the current stack:

- `mpv`
- `liblinphone-dev`
- `pkg-config`
- `cmake`
- `alsa-utils`
- `i2c-tools`
- `pisugar-server`

Example:

```bash
sudo apt install mpv liblinphone-dev pkg-config cmake alsa-utils i2c-tools
yoyoctl build liblinphone
yoyoctl build lvgl
```

## Configuration

Tracked config files live under `config/`:

- `config/yoyopod_config.yaml`
- `config/voip_config.yaml`
- `config/liblinphone_factory.conf`
- `config/contacts.yaml`

Key settings:

- `config/yoyopod_config.yaml`
  - `display.*` hardware and renderer selection
  - `audio.music_dir`
  - `audio.mpv_socket`
  - `audio.mpv_binary`
  - `audio.alsa_device`
  - `audio.default_volume`
  - `input.whisplay_*_ms`
  - `power.*`
  - `logging.*`
- `config/voip_config.yaml`
  - SIP account, transport, STUN, Liblinphone messaging and media config
- `config/contacts.yaml`
  - contact list and speed-dial style entries

## Running

Production app:

```bash
python yoyopod.py
```

Simulation:

```bash
python yoyopod.py --simulate
```

Installed console entrypoint:

```bash
yoyopod
```

Useful demos:

```bash
python demos/demo_voip.py --simulate
python demos/demo_playlists.py
python demos/demo_runtime_state.py --simulate
```

## Validation

Local validation:

```bash
python -m compileall yoyopy tests demos scripts
uv run pytest -q
```

Pi smoke:

```bash
yoyoctl pi smoke
yoyoctl pi smoke --with-music --with-voip
yoyoctl pi smoke --with-power --with-rtc
yoyoctl pi lvgl soak
```

## Raspberry Pi Workflow

Preferred remote helper:

```bash
yoyoctl remote config show
yoyoctl remote status
yoyoctl remote preflight --branch main --with-music --with-voip --with-lvgl-soak
yoyoctl remote sync --branch main
yoyoctl remote smoke --with-music --with-voip
yoyoctl remote service status
yoyoctl remote logs --lines 200
```

The detailed deploy and validation flows live in:

- `docs/PI_DEV_WORKFLOW.md`
- `docs/RPI_SMOKE_VALIDATION.md`
- `rules/deploy.md`

## Logging

The app writes:

- `logs/yoyopod.log`
- `logs/yoyopod_errors.log`

Pi deploy defaults live in:

- `deploy/pi-deploy.yaml`
- `deploy/pi-deploy.local.yaml` for gitignored machine-local overrides

Useful remote log commands:

```bash
yoyoctl remote logs --lines 200
yoyoctl remote logs --errors
yoyoctl remote logs --filter voip
yoyoctl remote logs --follow --filter ERROR
```

## Package Layout

```text
yoyopy/
  app.py
  main.py
  fsm.py
  app_context.py
  coordinators/
  audio/
    history.py
    local_service.py
    volume.py
    music/
      backend.py
      ipc.py
      models.py
      process.py
  config/
    manager.py
    models.py
  voip/
    backend.py
    history.py
    manager.py
    models.py
  ui/
    display/
    input/
    lvgl_binding/
    screens/
    web_server.py
```

## Current Active Docs

- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/POWER_MODULE.md`
- `docs/LOCAL_FIRST_MUSIC_PLAN.md`
- `docs/MPV_DEPENDENCIES.md`
- `docs/LVGL_MIGRATION_PLAN.md`

Historical milestone notes are archived under `docs/archive/`.
