# Commands

Placeholders:
- `<TOOL>` — executable name, e.g. `hermes`
- `<REPO>` — full path to the tool's git repository, e.g. `C:\Users\Srika\AppData\Local\hermes\hermes-agent` (quote any path containing spaces)
- `<N>` — stash index number

All commands are PowerShell on Windows.

## Step 1 — Capture failing update

```powershell
<TOOL> update 2>&1 | Tee-Object update-failure.log
```

Answer `n` if prompted to restore stashed changes.

## Step 2 — Identify untracked directory

```powershell
cd "<REPO>"
git status --short
```

## Step 3 — Inspect stashes (quote refs!)

```powershell
git stash list
git stash show --include-untracked -p "stash@{0}"
# repeat per stash; to extract a genuine user file from a stash's untracked tree:
# git show "stash@{0}^3:<path>" > <path>.bak
```

## Step 4 — Find invoked executable

```powershell
Get-Command <TOOL> | Select-Object -ExpandProperty Source
```

## Step 5 — Confirm proper install location

```powershell
Test-Path "<REPO>\venv\Scripts\<TOOL>.exe"
```

## Step 6 — Back up and rewrite User PATH (registry API only)

Back up first. Do NOT use `[Environment]::SetEnvironmentVariable` (flattens `%VAR%` in REG_EXPAND_SZ) or `setx` (truncates at 1024 chars).

```powershell
# Backup (raw registry value, preserves %VAR% literals)
reg query HKCU\Environment /v Path > "$HOME\path-backup.txt"

$bad  = '<REPO>\bin'
$good = '<REPO>\venv\Scripts'

$key = Get-Item HKCU:\Environment
$raw = $key.GetValue('Path', '', 'DoNotExpandEnvironmentNames')
$entries = $raw -split ';' | Where-Object { $_ -ne '' }
$entries = $entries | Where-Object { $_ -ne $bad }        # exact whole-entry match only
if ($entries -notcontains $good) { $entries += $good }
$new = ($entries -join ';')

Set-ItemProperty -Path HKCU:\Environment -Name Path -Value $new -Type ExpandString

# Verify %VAR% entries survived literally:
reg query HKCU\Environment /v Path
```

## Step 7 — Verify in a NEW terminal

```powershell
Get-Command <TOOL> | Select-Object -ExpandProperty Source
```

## Step 8 — Stop locks, clean up (destructive — confirm each)

```powershell
# Stop any process running from the repo-level bin (Windows locks running EXEs):
Get-Process | Where-Object { $_.Path -like '<REPO>\bin\*' } | Stop-Process -Confirm

# Remove obsolete untracked bin/ (irreversible; quote the path):
Remove-Item -Recurse -Force "<REPO>\bin"

# Drop stashes one by one, only after inspecting each in Step 3:
git stash drop "stash@{0}"
# git stash clear   # ONLY if every stash was inspected and holds nothing worth keeping

git status --short
git stash list
```

## Step 9 — Confirm update succeeds

```powershell
<TOOL> update