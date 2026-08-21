## Example 1: GLM 5.2 on Morpheus (the canonical case)

Input:
- `base_url`: `https://api.mor.org/api/v1`, key in `$MOR_API_KEY`
- Suspect model: `glm-5.2`
- Control model: `claude-opus-4.7`
- Turn log line: `Turn ended: reason=text_response(finish_reason=stop) tool_turns=0 last_msg_role=assistant response_len=1186`

Run:
```
./repro.sh glm-5.2 > response-suspect.json
./repro.sh claude-opus-4.7 > response-control.json
jq '.choices[0].message.tool_calls, .choices[0].finish_reason' response-suspect.json
```

Result: suspect response has `tool_calls: null`, `finish_reason: "stop"`, and `content` equal to `{"tool_calls": [{"name": "terminal", "arguments": {"command": "df -h"}}]}`. Control response has a structured `tool_calls` array with `finish_reason: "tool_calls"`. Diagnosis: provider adapter bug, model-specific. Write `bug-report.md` with the scope table (GLM-5.2/GLM-5.1/Kimi K3 fail; Claude Opus 4.7 and other Anthropic models work).

## Example 2: Suspected provider bug that is actually client config

Input:
- `base_url`: `https://api.mor.org/api/v1` (but agent config points at `https://api.mor.org/v1`)
- Suspect model: `Kimi K3`
- No control model tested yet

Run the raw curl first. If curl against the correct URL returns proper `tool_calls` while the agent still fails, the fault is client-side: wrong `base_url` in the agent's provider config. Fix the config; do not file a provider bug report. This is why step 1 uses raw curl before reading agent logs as authoritative.

## Example 3: Intermittent emission

Input:
- Suspect model: `glm-5.1`, control: `claude-opus-4.7`, same provider

First curl returns proper `tool_calls`; second returns text-echoed content. Run the reproduction three times and record per-attempt results in the bug report (`attempt 1: tool_calls OK; attempts 2–3: text-echoed`). Intermittency strengthens the adapter-bug diagnosis (race in the provider's translation layer) but requires the repeated-trials evidence in the report.