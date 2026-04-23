# Slot Deploy (OTA-Ready)

This is the operator guide for the slot-deploy path.

Use slot deploy when you want immutable release directories under `/opt/yoyopod`,
atomic `current`/`previous` flips, and rollback support. Keep the legacy
`~/yoyopod-core` checkout as the control plane for `yoyopod remote ...`; the
running app moves to `/opt/yoyopod`.

## Current Status

The slot-deploy flow is now the preferred deployment path for provisioned boards.
The legacy `yoyopod remote sync` and `yoyopod@.service` flow still exists for
working-tree debugging and older boards, but slot deploy is the path intended for
repeatable OTA-style updates.

Current contract:

- every release lives in `/opt/yoyopod/releases/<version>/`
- `current` points at the active release
- `previous` points at the last release for rollback
- the Pi hydrates its own slot-local `venv/` during deploy
- tracked repo `config/` is bundled into every slot
- `YOYOPOD_STATE_DIR` exists for persistent state, but runtime config is still read
  from the slot's bundled `./config`

## On-Device Layout

```text
/opt/yoyopod/
|-- releases/
|   |-- 2026.04.23-hydrate-local5/
|   |   |-- app/
|   |   |-- assets/
|   |   |-- bin/launch
|   |   |-- config/
|   |   |-- manifest.json
|   |   |-- runtime-requirements.txt
|   |   `-- venv/
|   `-- 2026.04.23-fd711617/
|-- current -> releases/2026.04.23-hydrate-local5
|-- previous -> releases/2026.04.23-fd711617
|-- bin/rollback.sh
`-- state/
    |-- config/
    |-- logs/
    `-- tmp/
```

What each piece is for:

- `app/`: copied `yoyopod/` and `yoyopod_cli/` source trees
- `config/`: tracked repo config shipped with the release
- `runtime-requirements.txt`: dependency contract used for Pi-side hydration
- `venv/`: slot-local runtime Python environment
- `state/`: persistent board-owned state that must survive updates

## Before You Start

### Dev machine prerequisites

Run these once on the machine that will push releases:

```bash
uv sync --extra dev
uv run yoyopod setup verify-host --with-remote-tools
```

Create or update your local remote override:

```bash
yoyopod remote config edit
```

Recommended local settings:

- `host`: your SSH alias or Pi IP
- `user`: the Pi login user that should run the app
- `project_dir`: stable checkout path on the Pi, usually `~/yoyopod-core`
- `slot.root`: `/opt/yoyopod` unless you intentionally use another root

### Pi prerequisites

The Pi still needs a stable checkout path because `yoyopod remote ...` SSH
commands begin by `cd`-ing into `project_dir` before they operate on `/opt/yoyopod`.

Default expectation:

```bash
~/yoyopod-core
```

If you choose a different path, it must match `project_dir` in your deploy config.

## Fresh Board Install

Use this when the board does not already have a YoYoPod deployment.

### 1. Clone the repo to the stable control-plane path on the Pi

SSH to the Pi and clone into the configured `project_dir`:

```bash
ssh tifo@rpi-zero
git clone <repo-url> ~/yoyopod-core
cd ~/yoyopod-core
```

### 2. Install the board prerequisites

From the dev machine, run the repo-owned setup flow against that checkout:

```bash
uv run yoyopod remote setup --with-pisugar
uv run yoyopod remote verify-setup --with-pisugar
```

Add `--with-network` and/or `--with-voice` if that board needs the modem or
voice stack.

### 3. Bootstrap the slot-deploy root

On the Pi, from the repo checkout:

```bash
cd ~/yoyopod-core
sudo -E ./deploy/scripts/bootstrap_pi.sh
```

If you intentionally use a non-default root:

```bash
sudo -E ./deploy/scripts/bootstrap_pi.sh --root=/srv/yoyopod-alt
```

That value must match `slot.root` in `deploy/pi-deploy.local.yaml`.

### 4. Build the first slot locally

On the dev machine:

```bash
uv run python scripts/build_release.py --output build/releases --channel dev
```

Or set the version explicitly:

```bash
uv run python scripts/build_release.py --output build/releases --channel dev --version 2026.04.23-mybuild
```

### 5. Push the first release

The first slot deploy has no rollback target yet, so `--first-deploy` is required:

```bash
uv run yoyopod remote release push build/releases/<version> --first-deploy
```

If you have not stored `host` and `user` locally yet:

```bash
uv run yoyopod remote --host rpi-zero --user tifo release push build/releases/<version> --first-deploy
```

### 6. Enable boot-time startup

After the first successful push:

```bash
ssh tifo@rpi-zero
sudo systemctl enable yoyopod-slot.service
```

### 7. Verify board state

```bash
uv run yoyopod remote release status
ssh tifo@rpi-zero 'systemctl status yoyopod-slot.service --no-pager -l'
```

Expected result:

- `current=<version>`
- `health=ok`
- `yoyopod-slot.service` is `active`

## Migrating an Existing `~/yoyopod-core` Board

Use this when the board already runs the legacy working-tree deployment under
`~/yoyopod-core`.

### Migration checklist

Before cutover, verify these points:

- the stable checkout path on the Pi is correct and reachable
- any important local config edits under `~/yoyopod-core/config/` are reviewed
- you understand that slot deploy runs the bundled slot `config/`, not `state/config/`
- you have a maintenance window for the first cutover because `--first-deploy`
  has no rollback target yet

### 1. Preserve old board-owned files

On the Pi:

```bash
cd ~/yoyopod-core
sudo -E ./deploy/scripts/bootstrap_pi.sh --migrate
```

This preserves:

- `~/yoyopod-core/config/` -> `/opt/yoyopod/state/config/`
- `~/yoyopod-core/logs/` -> `/opt/yoyopod/state/logs/`

Important: those copied config files are preserved for reference and future
state-dir work, but the running slot still reads its own bundled `./config`.
If the old board depends on local config drift that is not tracked in git, bring
those changes into the repo's `config/` tree before the first slot build.

### 2. Build the first migration slot

On the dev machine:

```bash
uv run python scripts/build_release.py --output build/releases --channel dev
```

### 3. Cut over from the legacy service to the slot service

On the Pi, identify the legacy unit name first:

```bash
systemctl list-units 'yoyopod@*.service'
```

Then stop and disable it immediately before the first slot push:

```bash
sudo systemctl disable --now yoyopod@tifo.service
```

Now push the first slot release:

```bash
uv run yoyopod remote --host rpi-zero --user tifo release push build/releases/<version> --first-deploy
```

After the push succeeds:

```bash
ssh tifo@rpi-zero
sudo systemctl enable yoyopod-slot.service
```

### 4. Verify the migration result

```bash
uv run yoyopod remote --host rpi-zero --user tifo release status
ssh tifo@rpi-zero 'readlink -f /opt/yoyopod/current && systemctl is-active yoyopod-slot.service'
```

Expected result:

- `current=<version>`
- `health=ok`
- `yoyopod-slot.service` is active
- the old `yoyopod@<user>.service` is disabled

### 5. First post-migration follow-up deploy

After one more successful slot release, `previous` becomes meaningful and normal
rollback is available:

```bash
uv run python scripts/build_release.py --output build/releases --channel dev
uv run yoyopod remote release push build/releases/<next-version>
```

## Normal Day-Two Deploys

After the board has already been migrated or bootstrapped once:

```bash
uv run python scripts/build_release.py --output build/releases --channel dev
uv run yoyopod remote release push build/releases/<version>
uv run yoyopod remote release status
```

What happens during `release push`:

1. upload the new slot to `/opt/yoyopod/releases/<version>/`
2. repair `bin/launch` permissions on the Pi after upload
3. hydrate the slot-local `venv/`
4. copy the currently working native shim `.so` files into the new slot
5. run `yoyopod health preflight`
6. atomically flip `current` and `previous`
7. restart `yoyopod-slot.service`
8. run a shell-only live probe against the active systemd unit and active slot path

## Rollback

Manual rollback:

```bash
uv run yoyopod remote release rollback
```

Automatic rollback:

- `yoyopod-slot.service` has `OnFailure=yoyopod-rollback.service`
- after repeated crash loops, systemd invokes `/opt/yoyopod/bin/rollback.sh`

Check the current rollback state:

```bash
uv run yoyopod remote release status
ssh tifo@rpi-zero 'readlink -f /opt/yoyopod/current && readlink -f /opt/yoyopod/previous'
```

## Known Limits and Pitfalls

These are the issues found while bringing the flow up on a real Pi Zero 2W.

### Stable checkout is still required

Slot deploy moves the runtime to `/opt/yoyopod`, but remote commands still use
the stable `project_dir` checkout as their SSH entrypoint. Do not delete
`~/yoyopod-core` after migration unless the remote transport contract changes too.

### First deploy has no safety net

`--first-deploy` is an explicit acknowledgement that `previous` does not exist yet.
Do not promise rollback until a second successful slot release has completed.

### Pi Zero memory is tight

Starting extra Python processes just to ask "is the app healthy?" can tip the
board into OOM pressure during startup. The release live probe now uses shell and
systemd state instead of spawning a second Python health check on the Pi.

### Do not reuse stale native build directories

Copying full CMake build trees between slots carries stale `CMakeCache.txt`
paths and breaks `ensure-native`. Copy only the built native artifacts, or rebuild
from scratch in the new slot.

### Slot-local imports must be forced

Pi-side helper commands like `health preflight` and `build ensure-native` must
import from the slot's `app/` tree, not whatever still exists in
`~/yoyopod-core`. Otherwise a later SSH session can accidentally execute the wrong
code.

### Windows upload path needs permission repair

When `rsync` is unavailable or unreliable from Windows, the flow falls back to
`scp`. That path can drop the executable bit on `bin/launch`, so the deploy now
repairs it on the Pi after upload.

### `state/config` is not the live runtime config yet

Migration preserves old board config under `/opt/yoyopod/state/config/`, but the
running app still reads the slot's bundled `./config`. Treat state config as a
preserved backup until the runtime config loader moves to the state-dir contract.

### Fresh-board hydration is the slow path

With no current slot to copy from, the Pi has to create a fresh `venv/` and build
or confirm native runtime pieces locally. That first deploy is the slowest one.
Subsequent deploys are faster because they clone the current slot runtime forward.

## Field Notes From Bring-Up

The main issues discovered while getting this live were:

- `launch.sh` must call `yoyopod.main.main()` directly; `python -m yoyopod.main`
  is not a valid runtime entrypoint
- built slots must include the tracked repo `config/` tree
- the release live probe must not depend on reading only `manifest.json`; it has
  to confirm the active unit and active slot
- the root CLI entrypoint is too heavy for Pi-side deploy probes; use lighter
  subapps or shell checks
- native build caches are not portable across slot paths
- Windows transport needs a robust fallback when `rsync` closes unexpectedly

## Related Docs

- [docs/PI_DEV_WORKFLOW.md](PI_DEV_WORKFLOW.md)
- [docs/RELEASE_PROCESS.md](RELEASE_PROCESS.md)
- [docs/DEPLOYED_PI_DEPENDENCIES.md](DEPLOYED_PI_DEPENDENCIES.md)
- [rules/deploy.md](../rules/deploy.md)
