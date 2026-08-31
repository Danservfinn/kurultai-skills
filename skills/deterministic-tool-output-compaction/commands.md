# Commands

Placeholders: `<py-log>` = any noisy log file; `<cmd>` = command name string (e.g. `pytest`); `<args...>` = command and arguments; `<envelope.json>` = Hermes tool-result JSON file; `<exact-file>` = output that must stay byte-identical; `<n>` = byte count.

## Step 1 — verify package on PyPI
```bash
curl -fsS https://pypi.org/pypi/noisegate-hermes/json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["info"]["version"], d["info"]["summary"])'
```

## Step 2 — install and health check
```bash
uvx --from noisegate-hermes noisegate doctor
uv tool install noisegate-hermes && noisegate doctor
uvx --from noisegate-hermes noisegate install-hermes --dry-run
```

## Step 3 — verify interface
```bash
noisegate --help
noisegate reduce --help
noisegate wrap --help
noisegate reduce-json --help
```

## Step 5 — compact a saved log
```bash
noisegate reduce --command "<cmd>" < <py-log>
noisegate reduce --command "<cmd>" --metadata < <py-log>
```

## Step 6 — wrap a live command
```bash
noisegate wrap -- <args...>
noisegate wrap --metadata -- <args...>
noisegate wrap --max-capture-bytes <n> -- <args...>
```

## Step 7 — envelope compaction
```bash
noisegate reduce-json < <envelope.json>
noisegate reduce-json --metadata < <envelope.json>
```

## Step 8 — bypass
```bash
NOISEGATE_BYPASS=1 noisegate reduce < <exact-file>
noisegate wrap --raw -- cat <exact-file>
noisegate wrap --full -- <args...>
printf '%s\n' '[noisegate:bypass]' 'exact line' | noisegate reduce --command "pytest"
```

## Step 9 — smoke test
```bash
python3 - <<'PY' | noisegate reduce --command "pytest"
for i in range(260):
    print(f"line {i:03d}")
print("FAILED tests/test_demo.py::test_keeps_signal")
print("AssertionError: signal survived")
PY
printf '%s\n' '[noisegate:bypass]' 'line that must stay exact' | noisegate reduce --command "pytest"