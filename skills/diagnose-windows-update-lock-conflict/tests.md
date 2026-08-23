# Tests

Manual checklist. Run on the affected Windows machine after applying the skill.

1. **Untracked dir identified**: `git status --short` in `<REPO>` shows `?? bin/` before the fix, and shows no output after Step 8.
2. **PATH rewrite is exact and non-destructive**: after Step 6, `reg query HKCU\Environment /v Path` shows (a) no `<REPO>\bin` entry, (b) a `<REPO>\venv\Scripts` entry, and (c) every pre-existing non-target entry — including any `%VAR%`-style entries, verified literally in the registry output — unchanged compared to `path-backup.txt`.
3. **Resolution fixed**: in a newly opened terminal, `Get-Command <TOOL>` returns a path under `<REPO>\venv\Scripts\`, not `<REPO>\bin\`.
4. **Stash cleanup verified**: `git stash list` outputs nothing after Step 8; before dropping, `git stash show --include-untracked -p "stash@{0}"` ran without a PowerShell parse error (quoted ref).
5. **Update succeeds**: `<TOOL> update` completes with no `failed to remove`, no `permission denied`, and no `Local changes detected — stashing` message; a second consecutive run also produces no autostash.
6. **Backup exists**: `$HOME\path-backup.txt` contains the pre-change PATH and can be diffed against the current registry value to show only the intended entry changed.