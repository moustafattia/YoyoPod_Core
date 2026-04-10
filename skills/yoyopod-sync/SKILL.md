---
name: yoyopod-sync
description: Quick rsync deploy to Raspberry Pi (no commit needed)
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash(yoyoctl remote:*)
---

## Config

Use `deploy/pi-deploy.yaml` as the shared deploy contract and `deploy/pi-deploy.local.yaml` for machine-specific overrides such as host, SSH user, project dir, and branch. `yoyoctl remote` merges them directly, and `yoyoctl remote config edit` is the preferred way to create or update the local override.

If the file does not exist yet, run `yoyoctl remote config edit` first. That command creates `deploy/pi-deploy.local.yaml` automatically before opening it.

## Steps

1. **Sync the dirty working tree and restart.** Run:
   ```bash
   yoyoctl remote rsync
   ```

2. **If the user explicitly wants sync without restart,** run:
   ```bash
   yoyoctl remote rsync --skip-restart
   ```

3. **Handle failures.** If the rsync or restart step fails, run:
   ```bash
   yoyoctl remote logs --lines 20
   ```
   Include the relevant error output in your response.

Report whether the dirty-tree sync and restart succeeded.
