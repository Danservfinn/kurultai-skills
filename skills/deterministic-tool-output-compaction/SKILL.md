---
name: deterministic-tool-output-compaction
description: Verify, install, and use the noisegate CLI to deterministically compact noisy agent tool output (test logs, package installs, docker builds) while leaving exact source material untouched
category: ops-automation
---

# Deterministic Tool Output Compaction with noisegate

## Goal

Compact noisy tool output (pytest logs, package installs, docker builds) deterministically — no LLM summarization — while preserving failure lines, exit codes, and exact source material. Fail open (return unchanged output) whenever the tool is missing, the interface does not match, or the output class is ambiguous.

## Inputs

- A noisy tool output stream or log file (e.g. `noisy.log`)
- The command name that produced the output (e.g. `pytest`, `npm`, `docker logs`)
- Optional: a Hermes tool-result JSON envelope (see step 7 for the expected shape)
- No API key required. Requires network access to PyPI for install/verification.

## Steps

1. **Verify the tool exists before depending on it.** Check the PyPI package `noisegate-hermes` is real and inspectable:
   ```bash
   curl -fsS https://pypi.org/pypi/noisegate-hermes/json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["info"]["version"], d["info"]["summary"])'
   ```
   If this fails (404, network error), stop and report that the skill cannot run — do not invent substitute commands.

2. **Install and run the health check.** Install the CLI (standalone use does not require Hermes):
   ```bash
   uvx --from noisegate-hermes noisegate doctor
   ```
   or install into the current environment:
   ```bash
   uv tool install noisegate-hermes   # or: pip install noisegate-hermes
   noisegate doctor
   ```
   `doctor` must report a healthy state and will surface ignored env values such as `NOISEGATE_ARTIFACTS=maybe`. If installing into Hermes specifically, use `uvx --from noisegate-hermes noisegate install-hermes --dry-run` first to preview the exact commands, then run without `--dry-run`.

3. **Verify the interface matches expectations before use.** Confirm the subcommands and flags this skill relies on actually exist:
   ```bash
   noisegate --help
   noisegate reduce --help
   noisegate wrap --help
   noisegate reduce-json --help 2>&1
   ```
   If `reduce`, `wrap`, `--metadata`, or `--raw`/`--full` are absent from help output, stop and report the mismatch — do not use undocumented flags.

4. **Classify the output before compacting.** Leave exact and skip compaction for: file reads, diffs/patches, `rg`/`grep`/`ag`/`ack` search output, skill documents, memory/MCP/web retrieval results, complete JSON documents, and unknown tools. Only compact known noisy classes: `pytest`/`unittest`, `apt`/`pip`/`uv`/`npm`/`pnpm`/`yarn`, `git status`/`git log`, docker build/logs, and generic long output (head/tail fallback).

5. **Compact a saved log file:**
   ```bash
   noisegate reduce --command "pytest" < noisy.log
   ```
   Add `--metadata` to get a single JSON diagnostic object on stderr containing `command_class`, reducer, unchanged reason, and chars/lines saved — stdout is unchanged.

6. **Compact a live command while preserving its exit code:**
   ```bash
   noisegate wrap -- pytest -q
   ```
   `wrap` runs the command without a shell, captures up to 4 MiB of combined output by default (`--max-capture-bytes <n>` to change), writes compacted output to stdout, and exits with the wrapped command's exit code. If capture is truncated, a `[noisegate: capture truncated]` marker is added.

7. **Compact a Hermes tool-result envelope.** The expected envelope shape is a JSON object with a `result` field holding a string (or a nested `result` object), optionally `tool_name`, and optionally exit hints (`exit`, `exit_code`, `returncode`, `return_code`):
   ```json
   {"tool_name": "terminal", "result": "...3000 lines of pytest output...", "exit_code": 1}
   ```
   Pipe it through:
   ```bash
   noisegate reduce-json < hermes-tool-result.json
   ```
   Bad JSON fails open: it is written back unchanged. Non-text results (lists, `null`) pass through as valid JSON.

8. **Bypass when exact bytes matter:**
   ```bash
   NOISEGATE_BYPASS=1 noisegate reduce < exact-output.txt
   noisegate wrap --raw -- cat exact-output.txt
   noisegate wrap --full -- ./another-exact-command
   ```
   Or embed the marker line `[noisegate:bypass]` at the top of the stream.

9. **Verify with the smoke test** (from the README):
   ```bash
   python3 - <<'PY' | noisegate reduce --command "pytest"
   for i in range(260):
       print(f"line {i:03d}")
   print("FAILED tests/test_demo.py::test_keeps_signal")
   print("AssertionError: signal survived")
   PY
   printf '%s\n' '[noisegate:bypass]' 'line that must stay exact' | noisegate reduce --command "pytest"
   ```
   Assert: long noisy output shrinks, the `FAILED` line stays visible, bypass output stays byte-identical.

## Outputs

- Compacted signal-rich output on stdout, preserving failure lines and exit codes
- stderr JSON diagnostics (with `--metadata`) explaining compaction decisions
- Unchanged original output when compaction would lose signal, the tool is ambiguous, or JSON is malformed

## Failure modes

- Package `noisegate-hermes` not on PyPI or CLI interface differs from documented flags — skill aborts at steps 1–3; report rather than substitute
- Compacting exact source material (diffs, code search, retrieved context) loses signal — prevented by step 4 classification; when in doubt, bypass
- Capture truncation beyond the 4 MiB default cap — `[noisegate: capture truncated]` marker added; raise with `--max-capture-bytes`
- Ambiguous tool identity or malformed JSON fails open, returning unchanged output
- Secret-looking output is refused from artifact storage even when `NOISEGATE_ARTIFACTS=1`
- Ignored env values (e.g. `NOISEGATE_ARTIFACTS=maybe`) — check `noisegate doctor` output

## Source

https://github.com/tosko4/noisegate (README), PyPI package `noisegate-hermes`. Extracted 2026-08-31. Interface verified against README CLI reference; re-verify with `--help` (step 3) before relying on any flag.