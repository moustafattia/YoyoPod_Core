---
name: yoyopod-deploy
description: Git-based deploy to Raspberry Pi (push, pull, restart)
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash(git status:*)
  - Bash(git branch --show-current:*)
  - Bash(git push:*)
  - Bash(yoyoctl remote:*)
---

## Config

Use `deploy/pi-deploy.yaml` as the shared deploy contract and `deploy/pi-deploy.local.yaml` for machine-specific overrides such as host, SSH user, project dir, and branch. `yoyoctl remote` merges them directly, and `yoyoctl remote config edit` is the preferred way to create or update the local override.

If the file does not exist yet, run `yoyoctl remote config edit` first. That command creates `deploy/pi-deploy.local.yaml` automatically before opening it.

## Steps

1. **Check local git status.** Run `git status --short`. If there are uncommitted or unstaged changes, stop and tell the user: "You have uncommitted changes. Use `/yoyopod-sync` for a dirty-tree deploy, or commit first."

2. **Resolve the branch.** Run `git branch --show-current` and deploy that branch.

3. **Push the branch.** Run `git push`. If the branch has no upstream yet, run `git push -u origin <branch>`.

4. **Sync the committed branch onto the Pi.** Run:
   ```bash
   yoyoctl remote sync --branch <branch>
   ```

5. **Restart and verify the app.** Run:
   ```bash
   yoyoctl remote restart
   ```

6. **Handle failures.** If either command fails, run:
   ```bash
   yoyoctl remote logs --lines 20
   ```
   Include the relevant error output in your response.

Report the deployed branch and whether the final restart succeeded.
