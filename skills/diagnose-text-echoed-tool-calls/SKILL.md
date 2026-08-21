---
name: diagnose-text-echoed-tool-calls
description: Diagnose whether an OpenAI-compatible provider is returning tool calls as text content instead of the tool_calls field, isolate provider-side vs client-side fault, and produce a minimal bug report.
category: ops-automation
---

# Diagnose text-echoed tool calls

## Goal

Determine whether an OpenAI-compatible provider is emitting tool invocations as a JSON string inside `choices[0].message.content` instead of a structured `choices[0].message.tool_calls[]` array, confirm the fault is provider-side (model-specific adapter bug) rather than client-side, and write a minimal bug report plus an optional client-side recovery feature request.

## Inputs

- Provider `base_url` (e.g. `https://api.mor.org/api/v1`) and API key in `$PROVIDER_API_KEY`
- Suspect model name (e.g. `glm-5.2`, `Kimi K3`)
- A known-good control model on the same provider (e.g. a Claude model)
- Agent turn logs showing `finish_reason`, `tool_turns`, and response length

## Steps

1. Write a minimal reproduction script that curls the provider's `/chat/completions` endpoint with one function tool (`terminal`, parameter `command: string`) and the prompt "Run df -h to check disk usage", with `tool_choice: "auto"`. Save the full JSON response to a file.
2. Parse the saved response with `jq`. Check whether the tool invocation is a stringified JSON object inside `choices[0].message.content` with `finish_reason == "stop"`, instead of a structured `choices[0].message.tool_calls` array with `finish_reason == "tool_calls"`.
3. Repeat the identical curl with the control model on the same provider and key. If the control model returns proper `tool_calls`, the fault is model-specific within the provider's adapter layer, not account-wide or client-wide.
4. Grep the agent turn logs for the signature: `tool_turns=0`, `finish_reason=stop`, and a non-empty text response whose stored content is a JSON object with a top-level `tool_calls` key.
5. Compare the malformed payload against the OpenAI Chat Completions spec and enumerate deviations: missing `id`, missing `type: "function"` wrapper, `arguments` as nested object instead of JSON-encoded string, `finish_reason: "stop"` instead of `"tool_calls"`.
6. Write a bug report markdown containing: expected vs actual response JSON, the curl reproduction, a scope table (affected vs working models on the same provider), and a suggested server-side fix (move content into `tool_calls[]`, add `id`/`type` wrapper, JSON-encode `arguments`, set `finish_reason: "tool_calls"`).
7. Optionally file a client-side feature request for an opt-in recovery path: when `finish_reason ∈ {stop, length}`, `tool_calls` is empty, and `content` is valid JSON with a top-level `tool_calls` key, parse and promote it — failing closed (surface raw content) on any schema mismatch.

## Outputs

- `repro.sh` — minimal curl reproduction script
- `response-suspect.json`, `response-control.json` — raw provider responses
- Diagnosis: provider adapter bug vs client bug
- `bug-report.md` — bug report for the provider
- Optional: client-side recovery feature request

## Failure modes

- Model intermittently emits proper `tool_calls`, masking the issue — run the reproduction 2–3 times before concluding.
- Client-side config error (wrong `base_url`, tool registry gating) mimics the failure — always verify with raw curl before blaming the provider.
- Unrelated log warnings mislead the diagnosis (e.g. `check_react_requirements` gates the emoji-reaction tool, not ReAct tool prompting — ignore it).
- Missing or invalid API key: curl returns 401; confirm `$PROVIDER_API_KEY` is set before starting.

## Source

Discord thread 1485307775444844625/1540100375024107571 (2026-08-21), with attachments `mor-bug-report.md` and `hermes-upstream-report.md`.