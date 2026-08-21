# Commands

Placeholders:
- `$PROVIDER_BASE_URL` — provider base URL, e.g. `https://api.mor.org/api/v1`
- `$PROVIDER_API_KEY` — API key (export before running)
- `$MODEL` — suspect model name
- `$CONTROL_MODEL` — known-good control model
- `$TURN_LOG` — path to agent turn log

## Step 1–3: reproduction script and control run

Save as `repro.sh`, then run for suspect and control models:

```bash
cat > repro.sh <<'EOF'
#!/bin/bash
# Usage: ./repro.sh <model>
MODEL="$1"
curl -s "$PROVIDER_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $PROVIDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL"'",
    "messages": [{"role": "user", "content": "Run df -h to check disk usage"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "terminal",
        "description": "Execute a shell command",
        "parameters": {
          "type": "object",
          "properties": {"command": {"type": "string"}},
          "required": ["command"]
        }
      }
    }],
    "tool_choice": "auto"
  }'
EOF
chmod +x repro.sh
export PROVIDER_BASE_URL="https://api.mor.org/api/v1"
export PROVIDER_API_KEY="<key>"
./repro.sh "$MODEL" > response-suspect.json
./repro.sh "$CONTROL_MODEL" > response-control.json
```

## Step 2: parse the response

```bash
jq '.choices[0].finish_reason, .choices[0].message.tool_calls, .choices[0].message.content' response-suspect.json
# text-echo signature: "stop", null, "{\"tool_calls\": [...]}"
jq -r '.choices[0].message.content' response-suspect.json | jq 'has("tool_calls")'
```

## Step 4: check agent turn logs

```bash
grep -E "Turn ended.*finish_reason=stop.*tool_turns=0" "$TURN_LOG"
grep -E "tool_turns=0" "$TURN_LOG" | tail -5
```

## Step 5: spec deviation checklist

```bash
jq '.choices[0].message.tool_calls[0] | {has_id: has("id"), has_type: has("type"), arguments_type: (.function.arguments | type)}' response-control.json
jq -r '.choices[0].message.content' response-suspect.json | jq '.tool_calls[0] | {has_id: has("id"), has_type: has("type"), arguments_type: (.arguments | type)}'
```

## Step 6: write the bug report

```bash
touch bug-report.md
$EDITOR bug-report.md   # or generate with an LLM pass from the collected JSON