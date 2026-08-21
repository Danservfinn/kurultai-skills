# Manual checklist

1. `./repro.sh glm-5.2` against a provider exhibiting the bug returns JSON where `jq '.choices[0].message.tool_calls' response-suspect.json` is `null` and `.choices[0].finish_reason` is `"stop"`.
2. `jq -r '.choices[0].message.content' response-suspect.json | jq 'has("tool_calls")'` prints `true` for the suspect model and errors (or prints `false`) for the control model.
3. The control-model run produces a structured `tool_calls` array with `finish_reason == "tool_calls"`, confirming the fault is model-specific.
4. `grep -E "tool_turns=0.*finish_reason=stop|finish_reason=stop.*tool_turns=0" "$TURN_LOG"` matches at least one turn from the suspect model.
5. `bug-report.md` contains: an expected-vs-actual JSON pair, the curl reproduction, a scope table with at least one failing and one working model, and a suggested server-side fix mentioning `finish_reason: "tool_calls"`.
6. Running `repro.sh` with an unset `PROVIDER_API_KEY` fails with an auth error (401), confirming the script surfaces missing-key failures rather than silently producing a misleading response.