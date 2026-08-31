# Manual verification checklist

Each assertion is gated on the tool existing. If assertion 1 fails, the skill is unverifiable in this environment — record that and stop.

1. **Package exists on PyPI.** `curl -fsS https://pypi.org/pypi/noisegate-hermes/json` returns HTTP 200 and prints a version via the step-1 command. If 404: the skill must not be used; this is a valid (expected-abort) outcome.

2. **Interface matches.** After install, `noisegate reduce --help` and `noisegate wrap --help` list `--metadata`; `wrap --help` lists `--raw`/`--full` and `--max-capture-bytes`. If any flag is missing, the skill aborts at step 3 by design.

3. **Doctor runs clean.** `noisegate doctor` exits 0 and reports healthy package/plugin state.

4. **Compaction shrinks and preserves signal.** Run the step-9 smoke test: the 262-line input produces visibly fewer lines on stdout AND the string `FAILED tests/test_demo.py::test_keeps_signal` is present (check with `| grep 'FAILED tests/'`).

5. **Bypass is byte-identical.** `printf '%s\n' '[noisegate:bypass]' 'line that must stay exact' | noisegate reduce --command "pytest"` outputs exactly the two input lines, byte for byte (compare against `printf '%s\n' '[noisegate:bypass]' 'line that must stay exact'` with `diff`).

6. **Exit code preserved.** `noisegate wrap -- sh -c 'echo out; exit 3'`; assert `echo $?` prints `3`.

7. **Bad JSON fails open.** `echo 'not json{' | noisegate reduce-json` returns the input unchanged on stdout.