---
name: yoyopod-rust-artifact
description: Deploy and test Rust runtime/worker binaries from GitHub Actions artifacts instead of building on Raspberry Pi
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash(git status:*)
  - Bash(git branch --show-current:*)
  - Bash(git rev-parse:*)
  - Bash(git push:*)
  - Bash(gh run:*)
  - Bash(gh pr:*)
  - Bash(mkdir:*)
  - Bash(chmod:*)
  - Bash(ssh:*)
  - Bash(scp:*)
  - Bash(yoyopod remote:*)
---

## Rule

Rust binaries for hardware validation must come from GitHub Actions artifacts
for the exact commit being tested. Do not run `cargo build`,
`yoyopod build rust-runtime`, `yoyopod build rust-ui-host`,
`yoyopod build rust-ui-poc`, or any other Rust compile on the Raspberry Pi
Zero 2W unless the user explicitly overrides this rule.

Native C shim work is different only for LVGL:
`yoyopod remote sync --clean-native` may still rebuild the LVGL C shim on the
Pi when native/CMake inputs change.

## Current Rust Artifact Contract

Use the artifact whose suffix equals the exact commit under test, not a pull
request merge SHA.

| Artifact | Pi install path | Purpose |
| --- | --- | --- |
| `yoyopod-runtime-<sha>` | `/opt/yoyopod-dev/checkout/yoyopod_rs/runtime/build/yoyopod-runtime` | Top-level Rust runtime entrypoint when `YOYOPOD_DEV_RUNTIME=rust`. |
| `yoyopod-ui-host-<sha>` | `/opt/yoyopod-dev/checkout/yoyopod_rs/ui-host/build/yoyopod-ui-host` | Whisplay UI worker and LVGL renderer. |
| `yoyopod-media-host-<sha>` | `/opt/yoyopod-dev/checkout/yoyopod_rs/media-host/build/yoyopod-media-host` | Rust media/mpv worker. |
| `yoyopod-voip-host-<sha>` | `/opt/yoyopod-dev/checkout/yoyopod_rs/voip-host/build/yoyopod-voip-host` | Rust Liblinphone/SIP worker. |

`yoyopod_rs/network-host/` is part of the Rust port, but only treat it as a
deployable artifact when the CI workflow uploads `yoyopod-network-host-<sha>`.
Do not invent an artifact name that CI does not produce.

## Steps

1. **Check local git status.** Run `git status --short`. If there are local
   changes, commit them first or stop and ask the user whether this is a
   dirty-tree exception.

2. **Resolve branch and commit.**

   ```bash
   git branch --show-current
   git rev-parse HEAD
   ```

3. **Push the commit.** Run `git push`. If there is no upstream, run
   `git push -u origin <branch>`.

4. **Find the successful CI run for the exact commit.**

   ```bash
   gh run list --workflow CI --branch <branch> --json databaseId,headSha,status,conclusion --limit 20
   ```

   Use only a run whose `headSha` equals the commit from step 2 and whose
   conclusion is `success`. If the run is still queued or in progress, wait.
   If it failed, inspect the failed job before hardware deploy.

5. **Download the needed artifacts locally.** For a full Rust-runtime hardware
   run, download at least runtime, UI, media, and VoIP:

   ```bash
   mkdir -p .artifacts/rust/<sha>
   gh run download <run-id> --name yoyopod-runtime-<sha> --dir .artifacts/rust/<sha>/runtime
   gh run download <run-id> --name yoyopod-ui-host-<sha> --dir .artifacts/rust/<sha>/ui-host
   gh run download <run-id> --name yoyopod-media-host-<sha> --dir .artifacts/rust/<sha>/media-host
   gh run download <run-id> --name yoyopod-voip-host-<sha> --dir .artifacts/rust/<sha>/voip-host
   chmod +x .artifacts/rust/<sha>/runtime/yoyopod-runtime
   chmod +x .artifacts/rust/<sha>/ui-host/yoyopod-ui-host
   chmod +x .artifacts/rust/<sha>/media-host/yoyopod-media-host
   chmod +x .artifacts/rust/<sha>/voip-host/yoyopod-voip-host
   ```

6. **Make sure the Pi dev checkout is on the same commit.**

   ```bash
   yoyopod remote mode activate dev
   yoyopod remote sync --branch <branch> --sha <sha>
   ```

   Add `--clean-native` only when native C/CMake/shim inputs changed.

7. **Install the CI-built Rust binaries on the Pi.**

   ```bash
   ssh <user>@<host> 'mkdir -p /opt/yoyopod-dev/checkout/yoyopod_rs/runtime/build /opt/yoyopod-dev/checkout/yoyopod_rs/ui-host/build /opt/yoyopod-dev/checkout/yoyopod_rs/media-host/build /opt/yoyopod-dev/checkout/yoyopod_rs/voip-host/build'
   scp .artifacts/rust/<sha>/runtime/yoyopod-runtime <user>@<host>:/opt/yoyopod-dev/checkout/yoyopod_rs/runtime/build/yoyopod-runtime
   scp .artifacts/rust/<sha>/ui-host/yoyopod-ui-host <user>@<host>:/opt/yoyopod-dev/checkout/yoyopod_rs/ui-host/build/yoyopod-ui-host
   scp .artifacts/rust/<sha>/media-host/yoyopod-media-host <user>@<host>:/opt/yoyopod-dev/checkout/yoyopod_rs/media-host/build/yoyopod-media-host
   scp .artifacts/rust/<sha>/voip-host/yoyopod-voip-host <user>@<host>:/opt/yoyopod-dev/checkout/yoyopod_rs/voip-host/build/yoyopod-voip-host
   ssh <user>@<host> 'chmod +x /opt/yoyopod-dev/checkout/yoyopod_rs/runtime/build/yoyopod-runtime /opt/yoyopod-dev/checkout/yoyopod_rs/ui-host/build/yoyopod-ui-host /opt/yoyopod-dev/checkout/yoyopod_rs/media-host/build/yoyopod-media-host /opt/yoyopod-dev/checkout/yoyopod_rs/voip-host/build/yoyopod-voip-host'
   ```

8. **Select the Rust dev-lane owner and restart.** The dev service still has a
   Python fallback, so set the override before testing the Rust entrypoint:

   ```bash
   ssh <user>@<host> 'set -e; sudo touch /etc/default/yoyopod-dev; if sudo grep -q "^YOYOPOD_DEV_RUNTIME=" /etc/default/yoyopod-dev; then sudo sed -i "s/^YOYOPOD_DEV_RUNTIME=.*/YOYOPOD_DEV_RUNTIME=rust/" /etc/default/yoyopod-dev; else printf "%s\n" "YOYOPOD_DEV_RUNTIME=rust" | sudo tee -a /etc/default/yoyopod-dev >/dev/null; fi'
   yoyopod remote restart
   ```

9. **Validate the Rust path.**

   ```bash
   yoyopod remote validate --branch <branch> --sha <sha> --with-rust-ui-host --with-lvgl-soak
   ```

   For a direct UI worker check, run from the Pi checkout:

   ```bash
   ssh <user>@<host> 'cd /opt/yoyopod-dev/checkout && YOYOPOD_WHISPLAY_DC_GPIO=27 YOYOPOD_WHISPLAY_RESET_GPIO=4 YOYOPOD_WHISPLAY_BUTTON_GPIO=17 YOYOPOD_WHISPLAY_BUTTON_ACTIVE_LOW=0 LD_LIBRARY_PATH=/opt/yoyopod-dev/checkout/yoyopod/ui/lvgl_binding/native/build/lvgl/lib:/opt/yoyopod-dev/checkout/yoyopod/ui/lvgl_binding/native/build:$LD_LIBRARY_PATH /opt/yoyopod-dev/checkout/yoyopod_rs/ui-host/build/yoyopod-ui-host --hardware whisplay'
   ```

10. **Report exact provenance.** Include the branch, commit SHA, CI run ID,
    artifact names, Pi host, active runtime owner, command result, and whether
    the dev service was left running.
