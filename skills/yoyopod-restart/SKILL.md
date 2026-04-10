---
name: yoyopod-restart
description: Kill and relaunch the app on Raspberry Pi
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash(yoyoctl remote:*)
---

## Config

Use `deploy/pi-deploy.yaml` as the shared deploy contract and `deploy/pi-deploy.local.yaml` for machine-specific overrides such as host, SSH user, project dir, and branch. `yoyoctl remote` merges them directly, and `yoyoctl remote config edit` is the preferred way to create or update the local override.

If the file does not exist yet, run `yoyoctl remote config edit` first. That command creates `deploy/pi-deploy.local.yaml` automatically before opening it.

## Steps

1. **Restart and verify the app.** Run:
   ```bash
   yoyoctl remote restart
   ```

2. **Handle failures.** If the restart fails, run:
   ```bash
   yoyoctl remote logs --lines 20
   ```
   Include the relevant error output in your response.

Report whether the restart succeeded.
