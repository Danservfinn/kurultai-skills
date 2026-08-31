## Example 1: Compact a large pytest log before feeding it to an agent

Input: `noisy.log`, 4,000 lines of pytest output ending in `FAILED tests/test_api.py::test_auth`.

```bash
# 1. Verify the tool
curl -fsS https://pypi.org/pypi/noisegate-hermes/json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["info"]["version"])'
# 2. Health check
uvx --from noisegate-hermes noisegate doctor
# 3. Compact with diagnostics
noisegate reduce --command "pytest" --metadata < noisy.log > compact.log
```

Expected: `compact.log` is far smaller, contains the `FAILED tests/test_api.py::test_auth` line, and stderr carries one JSON object with `command_class` and chars saved.

## Example 2: Wrap a docker build, keep the exit code

Input: a docker build that fails with exit code 1 after 2,000 lines of layer output.

```bash
noisegate wrap --metadata -- docker build -t app .
echo "exit=$?"
```

Expected: stdout is compacted build output including the error lines; `exit=1` matches the wrapped command. If output exceeded 4 MiB, `[noisegate: capture truncated]` appears.

## Example 3: Hermes envelope, and a case that must stay exact

Input A: `hermes-tool-result.json`:
```json
{"tool_name": "terminal", "result": "line 000\nline 001\n...\nFAILED tests/test_demo.py::test_x\nAssertionError: boom", "exit_code": 1}
```
```bash
noisegate reduce-json --metadata < hermes-tool-result.json
```

Input B: the same envelope but the result is `rg` search output:
```json
{"tool_name": "search_files", "result": "src/a.py:42:def signal():\nsrc/b.py:7:signal = 1"}
```
Per step 4, do not compact this — code search output stays exact. If it ever passes through noisegate, the tool itself refuses; verify with `--metadata` showing an unchanged reason.