# Examples

## Example 1 — Hermes on Windows 11 (the source case)

Input: `hermes update` output containing `warning: failed to remove bin/hermes.exe: Invalid argument`, `untracked files could not be removed (permission denied)`, and an autostash `hermes-update-autostash-20260822-033035`.

Execution:
- `git status --short` in `C:\Users\Srika\AppData\Local\hermes\hermes-agent` → `?? bin/`
- `git stash show --include-untracked -p "stash@{0}"` → contains `bin/hermes.exe`, `bin/hermes-acp.exe`, nothing else
- `Get-Command hermes` → `...\hermes-agent\bin\hermes.exe`
- Proper location confirmed: `...\hermes-agent\venv\Scripts\hermes.exe` exists
- PATH backup saved, User PATH entry `...\hermes-agent\bin` replaced with `...\hermes-agent\venv\Scripts` via registry `Set-Item` with `ExpandString`
- New terminal: `Get-Command hermes` → `...\venv\Scripts\hermes.exe`
- Gateway processes stopped, `bin\` removed, stashes dropped
- `hermes update` completes clean; `git status --short` empty; `git stash list` empty

## Example 2 — Updater stash churn with a genuine user file

Input: same warnings, but `git stash show --include-untracked -p "stash@{0}"` reveals `bin/hermes.exe` plus `config/local-overrides.toml` (a real user customization).

Execution: before any `git stash drop`/`clear`, extract the user file:

```powershell
git show "stash@{0}^3:config/local-overrides.toml" > local-overrides.toml.bak
```

Then drop only the updater stashes, restore the user file to its proper location, and proceed with PATH fix and cleanup. Do not run `git stash clear` until every stash is inspected.

## Example 3 — PATH rewrite with %VAR% entries present

Input: User PATH contains `%JAVA_HOME%\bin`, `C:\Users\Srika\AppData\Local\hermes\hermes-agent\bin`, and `C:\Users\Srika\AppData\Local\hermes\bin`.

Execution: back up PATH first (`Get-ItemProperty HKCU:\Environment | Select-Object -ExpandProperty Path | Out-File path-backup.txt`). Rewrite via `Set-ItemProperty` with `-Type ExpandString`, splitting on `;` and comparing entries with `-eq` (exact match) so `%JAVA_HOME%\bin` survives verbatim and `hermes-agent\bin` is removed without touching `hermes-agent\bin\extra`-style entries. Verify with `reg query HKCU\Environment /v Path` that `%JAVA_HOME%\bin` is still literal.