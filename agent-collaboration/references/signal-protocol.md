# Signal Communication Protocol (v0.2)

Reference for communicating with OpenClaw agents. Updated for Kurultai v0.2 architecture.

## v0.2 Architecture Change

**Signal runs embedded inside the moltbot container** as a child process. The previous standalone `signal-cli-native-production.up.railway.app` RPC endpoint **no longer exists**.

All external communication now goes through:
1. **Gateway API** (primary) — `$OPENCLAW_GATEWAY_URL/api/message`
2. **Signal relay** (fallback) — `$OPENCLAW_GATEWAY_URL/api/signal/send`
3. **User relay** (last resort) — user pastes Signal messages manually

## Connection Details

**Gateway API**: `$OPENCLAW_GATEWAY_URL/api/message` (authenticated via Bearer token)
**External URL**: `https://kublai.kurult.ai` (behind Authentik SSO)
**Signal Account**: `+15165643945` (embedded in moltbot, localhost-only)
**Signal Group Name**: `Kublai Klub`
**Signal Group ID**: `BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=`

## Gateway API Reference

### Send Message to Agent

```bash
curl -X POST "$OPENCLAW_GATEWAY_URL/api/message" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "main",
    "message": "Your message here",
    "plan_id": "plan-20260206-001"
  }'
```

Valid recipient IDs: `main`, `researcher`, `writer`, `developer`, `analyst`, `ops`

### Send Signal Message via Relay

```bash
curl -X POST "$OPENCLAW_GATEWAY_URL/api/signal/send" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "+19194133445",
    "message": "Your message here"
  }'
```

### Send to Signal Group via Relay

```bash
curl -X POST "$OPENCLAW_GATEWAY_URL/api/signal/send" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "groupId": "BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=",
    "message": "Group message here"
  }'
```

### Check Plan Status

```bash
curl "$OPENCLAW_GATEWAY_URL/api/plans/$PLAN_ID/status" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN"
```

### Check Recent Messages

```bash
curl "$OPENCLAW_GATEWAY_URL/api/messages/recent" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN"
```

## Message Types

### 1. Plan Handoff

```markdown
---PLAN-HANDOFF---
Plan ID: [unique-identifier]
Priority: high | medium | low
To: @kublai
X-Agent-Auth:

## Objective
[Clear statement of what needs to be accomplished]

## Context
[Background information the agent needs]

## Suggested Approach
[Hint at specialist + steps]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]

## Constraints
- [Time, scope, resources]

## Handoff Protocol
Report progress to: Claude Code (via gateway API or Signal)
Checkpoint frequency: [after each step | hourly | on completion]
On completion: Send HANDBACK-REPORT
---END-PLAN---
```

### 2. Status Request

```markdown
---STATUS-REQUEST---
Plan ID: [reference to original plan]
To: @[agent]
X-Agent-Auth:

[What status is being requested]
---END-REQUEST---
```

### 3. Status Update

```markdown
---STATUS-UPDATE---
Plan ID: [reference to original plan]
Agent: @[reporting agent]

## Progress
- [x] Step 1: [completion notes]
- [ ] Step 2: [in progress]
- [ ] Step 3: [not started]

## Blockers
[None | Description]

## Next Action
[What happens next and when]
---END-STATUS---
```

### 4. Handback Report

```markdown
---HANDBACK-REPORT---
Plan ID: [original plan reference]
Agent: @[completing agent]
Status: completed | partial | blocked
X-Agent-Auth:

## Deliverables
- [Deliverable 1]: [location in /data/workspace/souls/{agent_id}/]
- [Deliverable 2]: [location or description]

## Summary
[Brief narrative of what was accomplished]

## Success Criteria Met
- [x] [Criteria 1]
- [ ] [Unmet criteria with explanation]

## Files Modified
- [path/to/file1] - [what changed]

## Open Items
[Remaining work or "None"]

## Learnings
[Insights for future tasks]
---END-HANDBACK---
```

### 5. Assistance Request

```markdown
---ASSISTANCE-REQUEST---
From: @[agent-name]
Plan ID: [if related to existing plan]
Urgency: high | medium | low
X-Agent-Auth:

## Problem
[Clear description of the issue]

## What I've Tried
1. [Attempt 1 and result]
2. [Attempt 2 and result]

## Specific Help Needed
[Exactly what assistance is required]

## Context Files
- [path/to/relevant/file]
---END-REQUEST---
```

### 6. Course Correction

```markdown
---COURSE-CORRECTION---
Plan ID: [reference]
To: @[agent]
Severity: minor | moderate | major
X-Agent-Auth:

## Issue Detected
[What needs to change]

## Current Approach
[What the agent is doing]

## Recommended Approach
[What should be done instead]

## Rationale
[Why this change is needed]

## Impact on Plan
- Steps affected: [list]
- Timeline impact: [none | delay of X]
---END-CORRECTION---
```

## Agent Directory

| Agent | ID | Role | Best For |
|-------|-----|------|----------|
| @kublai | `main` | Squad Lead | Coordination, delegation, quality review |
| @mongke | `researcher` | Researcher | Research, evidence gathering, analysis |
| @ogedei | `writer` | Writer | Writing, editing, file consistency |
| @temujin | `developer` | Developer | Code implementation, automation, security |
| @jochi | `analyst` | Analyst | Data analysis, AST code analysis, metrics, strategy |
| @chagatai | `ops` | Operations | Admin, scheduling, process management |

## Inter-Agent Communication

| Channel | Mechanism | Direction |
|---------|-----------|-----------|
| Claude Code → Kublai | Gateway API or Signal relay | External → Internal |
| Kublai → Specialists | `agentToAgent` (moltbot.json) | Internal |
| Specialist → Kublai | `agentToAgent` return | Internal |
| Kublai → Claude Code | Signal message or gateway response | Internal → External |

## Workspace Paths (v0.2)

```
/data/workspace/
├── souls/                # Per-agent working directories
│   ├── main/             # Kublai
│   │   └── MEMORY.md     # Personal memory
│   ├── researcher/       # Mongke
│   ├── writer/           # Ogedei
│   ├── developer/        # Temujin
│   ├── analyst/          # Jochi
│   └── ops/              # Chagatai
└── deliverables/         # Legacy output directory (being migrated to souls/)
```

## Memory Architecture (v0.2)

| Tier | Storage | Access | Contents |
|------|---------|--------|----------|
| **Personal** | `/data/workspace/souls/{id}/MEMORY.md` | Agent-only | Preferences, personal history |
| **Operational** | Neo4j (shared) | All 6 agents | Research, patterns, analysis, task graph |

## Response Timeouts

| Message Type | Expected Response |
|--------------|-------------------|
| Plan Handoff | Acknowledgment within 15 minutes |
| Status Request | Immediate if agent is active |
| Assistance Request | Within 1 heartbeat cycle (15 min) |
| Course Correction | Acknowledgment required |

## Error Handling

If no response received:

1. Check gateway health: `curl $OPENCLAW_GATEWAY_URL/health`
2. Check agent status via gateway API
3. Check moltbot Railway logs: `railway logs --service moltbot-railway-template --since 5m`
4. Retry via alternative transport (Signal relay if gateway failed, or vice versa)
5. If persistent, user relay via Signal app

## Security (v0.2)

- Gateway API authenticated via `OPENCLAW_GATEWAY_TOKEN` Bearer token
- signal-cli bound to `127.0.0.1:8081` — no external network exposure
- Authentik SSO protects `kublai.kurult.ai` web endpoints
- QR linking endpoint protected by `X-Signal-Token` header
- Sender allowlists in moltbot.json
- `X-Agent-Auth` field reserved for v0.3 HMAC-SHA256 signing
