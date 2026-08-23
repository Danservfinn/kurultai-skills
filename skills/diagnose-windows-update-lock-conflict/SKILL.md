---
name: diagnose-windows-update-lock-conflict
description: Diagnose and fix a git-based updater on Windows that repeatedly fails because a running executable in an untracked bin/ directory blocks updates and causes stash churn
category: ops-automation
---

# Diagnose Windows Update Lock Conflict

## Goal

Stop a git-based updater (e.g. `hermes update`) on Windows from repeatedly autostashing and failing with `failed to remove bin/<tool>.exe: Invalid argument`. Root cause is typically a User PATH entry pointing at an untracked repo-level `bin\` directory whose EXE is running, so git cannot remove it. Fix by repointing PATH to the proper install location (e.g. `venv\Scripts`), then cleaning up the untracked directory and stale stashes.

## Inputs

- Shell access on the Windows machine (PowerShell)
- The failing update command (e.g. `hermes update`) and its captured output
- The git repository of the tool (e.g. `C:\Users\<user>\AppData\Local\hermes\hermes-agent`)
- Ability to edit User environment variables (no admin required for User PATH)

## Steps

1. Run the failing update command and capture full output. Note warnings such as `failed to remove bin/hermes.exe: Invalid argument` and `untracked files could not be removed (permission denied)`. Answer `n` if prompted to restore stashed changes.
2. In the tool's repository, run `git status --short`. Confirm an untracked directory appears (e.g. `?? bin/`).
3. Run `git stash list`, then inspect each stash with `git stash show --include-untracked -p "stash@{0}"` (quote the stash ref — PowerShell treats `{ }` as a script-block delimiter). Confirm the stashes contain the untracked executables (e.g. `bin/hermes.exe`, `bin/hermes-acp.exe`) and note any genuine user files you must preserve before discarding anything.
4. Run `Get-Command <tool>` to find which executable path is actually invoked at runtime.
5. Compare the invoked path against the tool's proper install location (e.g. `<REPO>\venv\Scripts`). Confirm PATH resolves to the untracked repo-level binary.
6. Back up the current User PATH to a file, then rewrite it: remove the repo-level `bin` entry and add the `venv\Scripts` entry. Use the registry API (`Get-Item`/`Set-Item` on `HKCU:\Environment`) with `ExpandString` kind — do NOT use `[Environment]::SetEnvironmentVariable`, which flattens `%VAR%` references in `REG_EXPAND_SZ` values, and do NOT use `setx`, which truncates at 1024 characters. Match PATH entries exactly (whole-entry comparison), not by prefix.
7. Open a new terminal (old terminals retain the stale PATH) and verify `Get-Command <tool>` resolves to the correct path.
8. Stop any process still running from the repo-level `bin\` (Windows refuses to delete a running EXE). After confirming stash contents hold nothing worth keeping (Step 3), remove the obsolete untracked `bin\` directory and drop the stale updater stashes with `git stash drop "stash@{N}"` (or `git stash clear` only after every stash has been inspected). Verify `git status --short` is clean and `git stash list` is empty.
9. Re-run the update command and confirm it completes without stash or permission warnings.

## Outputs

- Clean git working tree (`git status --short` empty)
- Correct PATH resolution for the tool (`Get-Command <tool>` points at `venv\Scripts`)
- Successful update run with no autostash or permission warnings
- Empty stash list

## Failure modes

- Windows refuses to delete an EXE while it is running: stop the process or repoint PATH and open a new terminal before cleanup.
- Old terminal sessions retain the stale PATH until reopened.
- `git stash clear` and `Remove-Item -Recurse -Force` are irreversible: inspect every stash first; stashes may contain genuine user customizations, not just updater binaries.
- `[Environment]::SetEnvironmentVariable` flattens `%VAR%` references in the User PATH (REG_EXPAND_SZ); `setx` truncates PATH at 1024 chars. Use the registry API with `ExpandString` instead.
- Inexact PATH matching (prefix or regex-substring) can corrupt entries like `<REPO>\bin\extra`; compare whole entries only.
- Unquoted `stash@{0}` fails in PowerShell; always quote stash refs.

## Source

Discord thread `discord/1485307775444844625/1540567795669143652` — "Windows Update; Output while Updating" (Srikanth Kamath, 2026-08-23). Resolved case: Hermes Agent v0.20.5, Python 3.11.16, Windows 11, git install method.