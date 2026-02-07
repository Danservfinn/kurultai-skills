---
name: agent-collaboration
description: This skill enables Claude Code to collaborate with OpenClaw agents deployed at kublai.kurult.ai. Use this skill when delegating tasks to the persistent agent network (Kublai, Mongke, Ogedei, Temujin, Jochi, Chagatai), monitoring ongoing agent work, or coordinating multi-step workflows. Supports dual transport — Gateway API (primary, programmatic) and Signal messaging (fallback, user-mediated).
---

# Agent Collaboration (v0.2)

Collaborate with the OpenClaw agent network at `kublai.kurult.ai` to execute plans, delegate tasks, and coordinate work.

**Architecture version**: Kurultai v0.2 (embedded Signal, Neo4j memory, Authentik SSO)

## Agent Network

| Agent | ID | Role | Specialty | v0.2 Status |
|-------|-----|------|-----------|-------------|
| **@kublai** | `main` | Squad Lead | Coordination, delegation, quality review, human interface | Active |
| **@mongke** | `researcher` | Researcher | Deep research, evidence gathering, competitive analysis | Active |
| **@ogedei** | `writer` | Writer | Content creation, editing, file consistency monitoring | Active |
| **@temujin** | `developer` | Developer | Code implementation, automation, security review | Active |
| **@jochi** | `analyst` | Analyst | Data analysis, AST-based code analysis, metrics, strategy | Active |
| **@chagatai** | `ops` | Operations | Admin tasks, scheduling, process management | Active (limited) |

### v0.2 Capability Boundaries

Not all agent behaviors from v0.1 are available. These are **deferred to v0.3**:

| Feature | Status | Reason |
|---------|--------|--------|
| Jochi-Temujin direct collaboration | Deferred | Requires proven agentToAgent messaging |
| Chagatai background synthesis | Deferred | Requires content generation pipeline |
| Ogedei proactive improvement | Deferred | Requires operational baseline data |
| Self-improvement/Kaizen | Deferred | Requires stable reflection system |
| HMAC-SHA256 message signing | Keys generated, middleware deferred | Signing middleware in v0.3 |

**Safe to delegate in v0.2**: Research tasks (Mongke), writing/docs (Ogedei), code implementation (Temujin), data analysis (Jochi), simple ops tasks (Chagatai). All routed through Kublai.

---

## Transport Layer

v0.2 provides two communication paths. Use the Gateway API when possible; fall back to Signal for async/offline scenarios.

### Transport 1: Gateway API (Primary)

Direct programmatic access to the OpenClaw gateway. Faster, more reliable, supports structured responses.

```bash
# Send via gateway API
./scripts/send_signal.sh "$(cat plan.md)" --gateway

# Or call the API directly
curl -X POST "$OPENCLAW_GATEWAY_URL/api/message" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "main",
    "message": "...",
    "plan_id": "plan-20260206-001"
  }'
```

**Requirements**: `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` environment variables set.

**When running locally** (Claude Code outside Railway):
```bash
# Use the external URL through Authentik
curl -X POST "https://kublai.kurult.ai/api/message" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "main", "message": "..."}'
```

### Transport 2: Signal Messaging (Fallback)

Signal messages are sent via the **embedded signal-cli** inside the moltbot container. From outside the container, use the gateway API's Signal relay endpoint:

```bash
# Send Signal message via gateway relay
./scripts/send_signal.sh "$(cat plan.md)" --signal

# Or call the relay endpoint directly
curl -X POST "$OPENCLAW_GATEWAY_URL/api/signal/send" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "+19194133445",
    "message": "..."
  }'
```

**User relay fallback**: If both programmatic paths are unavailable, the user can paste messages directly from their Signal app into Claude Code.

### Transport Selection

| Scenario | Transport | Reason |
|----------|-----------|--------|
| Programmatic task delegation | Gateway API | Structured, fast, authenticated |
| Monitoring agent progress | Gateway API | Can poll status endpoint |
| User wants to see messages in Signal | Signal relay | Visible in user's Signal app |
| Gateway unreachable | Signal (user relay) | User pastes responses manually |
| Long-running async tasks | Signal | Agents report via Signal naturally |

---

## v0.2 Signal Architecture

Signal runs **embedded inside** the moltbot container as a child process. There is **no separate signal-cli-daemon service**.

```
moltbot-railway-template container
  Node.js Gateway (:8080) ──> signal-cli (child process, :8081 localhost only)
                                    │
                                    v
                            Signal Network (E2EE)
```

- signal-cli bound to `127.0.0.1:8081` — no external network exposure
- Managed by OpenClaw auto-spawn pattern (autoStart: true)
- Device registration persisted at `/data/.signal` on Railway volume
- Allowlisted senders: `+15165643945` (self), `+19194133445` (authorized)

**The old `signal-cli-native-production.up.railway.app` RPC endpoint no longer exists.** All external Signal communication goes through the gateway API relay.

---

## Workflow: Plan Handoff

Send implementation plans to **@kublai** (Squad Lead), who coordinates the agent network.

### Step 1: Always Route Through Kublai

**All plans go to @kublai first.** Kublai will:
- Review the plan for clarity and feasibility
- Delegate to the appropriate specialist agent via `agentToAgent`
- Monitor progress and coordinate handoffs
- Perform quality review before completion

### Step 2: Compose the Plan

Use the structured plan format:

```markdown
---PLAN-HANDOFF---
Plan ID: plan-20260206-001
Priority: high
To: @kublai
X-Agent-Auth:

## Objective
Implement rate limiting middleware for the API gateway

## Context
The API is experiencing abuse. Need to add rate limiting before the next deploy.

## Suggested Approach
This looks like a job for @temujin (code/automation). Steps:
1. Review existing middleware in /src/middleware/
2. Implement token bucket rate limiter with 100 req/min default
3. Add Redis backing store for distributed rate limiting
4. Write unit tests for the rate limiter
5. Update API documentation

## Success Criteria
- [ ] Rate limiter blocks requests over threshold
- [ ] Redis state persists across restarts
- [ ] All tests pass
- [ ] Documentation updated

## Constraints
- Time: Complete within 24 hours
- Scope: API gateway only, not individual routes
- Resources: Redis already deployed

## Handoff Protocol
Report progress to: Claude Code (via gateway API or Signal)
Checkpoint frequency: after each major step
On completion: Send HANDBACK-REPORT
---END-PLAN---
```

**Note**: The `X-Agent-Auth` field is reserved for v0.3 HMAC-SHA256 message signing. Leave it empty for now — agents will validate it once signing middleware is deployed.

### Step 3: Send via Preferred Transport

```bash
# Primary: Gateway API
./scripts/send_signal.sh "$(cat plan.md)" --gateway

# Fallback: Signal relay
./scripts/send_signal.sh "$(cat plan.md)" --signal

# Last resort: print for user to paste into Signal
./scripts/send_signal.sh "$(cat plan.md)" --dry-run
```

### Step 4: Monitor Progress

```bash
# Check status via gateway API
./scripts/receive_signal.sh --gateway --plan plan-20260206-001

# Check moltbot logs for agent activity
./scripts/receive_signal.sh --logs --since 5m

# Stream live agent output
./scripts/receive_signal.sh --logs --follow
```

---

## Workflow: Status Monitoring

Request status on ongoing work:

```markdown
---STATUS-REQUEST---
Plan ID: plan-20260206-001
To: @temujin
X-Agent-Auth:

What is the current progress on the rate limiter implementation?
---END-REQUEST---
```

Expected response format:
```markdown
---STATUS-UPDATE---
Plan ID: plan-20260206-001
Agent: @temujin

## Progress
- [x] Step 1: Reviewed middleware, using Express rate-limit pattern
- [x] Step 2: Token bucket implemented (90%)
- [ ] Step 3: Redis integration in progress
- [ ] Step 4-5: Not started

## Blockers
None - proceeding on schedule

## Next Action
Redis integration, ETA 2 hours
---END-STATUS---
```

---

## Workflow: Course Correction

When agent work needs redirection:

```markdown
---COURSE-CORRECTION---
Plan ID: plan-20260206-001
To: @temujin
Severity: moderate
X-Agent-Auth:

## Issue Detected
Using in-memory store instead of Redis for rate limiting

## Current Approach
Token bucket with local Map() storage

## Recommended Approach
Use ioredis with sliding window algorithm for better distributed support

## Rationale
Multiple API instances will have inconsistent rate limits without shared state

## Impact on Plan
- Steps affected: 2, 3
- Timeline impact: +2 hours for refactor
---END-CORRECTION---
```

---

## Workflow: Receiving Handbacks

When agents complete work, they send handback reports:

```markdown
---HANDBACK-REPORT---
Plan ID: plan-20260206-001
Agent: @temujin
Status: completed
X-Agent-Auth:

## Deliverables
- Rate limiter middleware: /data/workspace/souls/developer/rate-limiter/
- Tests: /data/workspace/souls/developer/rate-limiter/tests/
- Documentation: /data/workspace/souls/developer/docs/rate-limiting.md

## Summary
Implemented sliding window rate limiter with Redis backing. Added IP-based and
API key-based limiting. All tests passing, documentation updated.

## Success Criteria Met
- [x] Rate limiter blocks requests over threshold
- [x] Redis state persists across restarts
- [x] All tests pass (12/12)
- [x] Documentation updated

## Files Modified
- src/middleware/rate-limit.ts - new file
- src/middleware/index.ts - added export
- docs/api/rate-limiting.md - new file

## Open Items
Consider adding per-route configuration (not in original scope)

## Learnings
ioredis MULTI/EXEC provides atomic operations needed for accurate counting
---END-HANDBACK---
```

### Processing Handbacks

1. Review deliverables at specified paths
2. Verify success criteria are actually met (don't trust self-reports blindly)
3. Pull relevant files to local environment if needed
4. Acknowledge receipt and close the plan

---

## Receiving Agent Responses

```bash
# Primary: Poll gateway API for plan status
./scripts/receive_signal.sh --gateway --plan plan-20260206-001

# Check moltbot logs for recent agent activity
./scripts/receive_signal.sh --logs --since 5m

# Stream agent activity live
./scripts/receive_signal.sh --logs --follow

# Raw moltbot logs (for debugging)
./scripts/receive_signal.sh --logs --raw --since 10m
```

**Requirements**: Railway CLI installed and linked to the project (`railway link`).

**Alternative methods** (if Railway CLI unavailable):
1. **User relay**: User pastes agent responses from Signal into Claude Code
2. **Control UI history**: View at `https://kublai.kurult.ai/sessions` (behind Authentik SSO)
3. **Workspace files**: Agents write to `/data/workspace/souls/{agent_id}/`

---

## Quick Reference

### Communication Channels
- **Gateway API**: `$OPENCLAW_GATEWAY_URL/api/message` (primary, programmatic)
- **Signal Account**: `+15165643945` (embedded in moltbot, not externally accessible)
- **Signal Group**: Kublai Klub (`BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=`)
- **Authorized User**: `+19194133445`

### Environment Variables
```bash
# Gateway API (primary transport)
OPENCLAW_GATEWAY_URL=http://moltbot-railway-template.railway.internal:8080
OPENCLAW_GATEWAY_TOKEN=<your-token>

# Signal (configured on moltbot service, not set locally)
SIGNAL_ACCOUNT=+15165643945
SIGNAL_ALLOW_FROM=+15165643945,+19194133445
```

### v0.2 Workspace Paths
```
/data/workspace/
├── souls/                # Per-agent working directories
│   ├── main/             # Kublai (squad lead)
│   │   └── MEMORY.md     # Personal memory
│   ├── researcher/       # Mongke
│   ├── writer/           # Ogedei
│   ├── developer/        # Temujin
│   ├── analyst/          # Jochi
│   └── ops/              # Chagatai
└── deliverables/         # Completed work output (legacy, being migrated)
```

### v0.2 Memory Architecture
| Tier | Storage | Access | Contents |
|------|---------|--------|----------|
| **Personal** | Files (`/data/workspace/souls/{id}/MEMORY.md`) | Agent-only | Preferences, personal history |
| **Operational** | Neo4j (shared) | All 6 agents | Research, patterns, analysis, task graph |

### Inter-Agent Communication
| Channel | Mechanism | When |
|---------|-----------|------|
| Kublai → Specialists | `agentToAgent` (moltbot.json) | Task delegation |
| Specialist → Kublai | `agentToAgent` return | Results, status |
| Claude Code → Kublai | Gateway API or Signal relay | Plan handoff |
| Kublai → Claude Code | Signal message or gateway response | Handback reports |

### Message Markers
| Marker | Purpose |
|--------|---------|
| `---PLAN-HANDOFF---` | Send plan to agent |
| `---STATUS-UPDATE---` | Progress report |
| `---STATUS-REQUEST---` | Request progress update |
| `---HANDBACK-REPORT---` | Work completion |
| `---ASSISTANCE-REQUEST---` | Agent needs help |
| `---COURSE-CORRECTION---` | Redirect agent work |

---

## Security Considerations

### Plan Content
Plans may contain sensitive information. Ensure plans don't include:
- API keys, tokens, or credentials
- Database connection strings
- Internal IP addresses or infrastructure details
- Customer data or PII

Kublai sanitizes PII via `PIISanitizer` before delegating to specialist agents.

### Agent Trust
Handback reports should be verified:
- Check that deliverable paths exist and contain expected content
- Verify claimed success criteria against actual implementation
- Be skeptical of "completed" status without supporting evidence
- In v0.3, HMAC signatures will provide cryptographic verification

### v0.2 Security Model
- signal-cli bound to `127.0.0.1:8081` — localhost only, no external exposure
- Gateway API authenticated via `OPENCLAW_GATEWAY_TOKEN`
- Authentik SSO protects web UI at `kublai.kurult.ai`
- QR linking endpoint protected by `X-Signal-Token` header
- Sender allowlists in moltbot.json (`allowFrom`, `groupAllowFrom`)
- HMAC-SHA256 agent keys generated and stored in Neo4j (signing enforcement in v0.3)

### v0.3 HMAC Readiness
All message templates include an `X-Agent-Auth` field. Currently empty. When v0.3 deploys signing middleware:
1. Agents will populate `X-Agent-Auth` with HMAC-SHA256 signatures
2. Recipients will verify signatures against Neo4j-stored agent keys
3. No structural changes to message formats needed — just populate the field

---

## Resources

### scripts/send_signal.sh
Send messages via Gateway API (primary) or Signal relay (fallback).

```bash
# Gateway API (primary)
./scripts/send_signal.sh "Hello Kublai" --gateway

# Signal relay via gateway
./scripts/send_signal.sh "Hello Kublai" --signal

# Dry run (print message without sending)
./scripts/send_signal.sh "Hello Kublai" --dry-run

# Send to specific agent (gateway only)
./scripts/send_signal.sh "Status?" --gateway --to researcher
```

**Dependencies**: `curl`, `jq`

### scripts/receive_signal.sh
Receive messages via Gateway API polling or moltbot Railway logs.

```bash
# Gateway API status check
./scripts/receive_signal.sh --gateway --plan plan-20260206-001

# Moltbot logs (last 5 minutes)
./scripts/receive_signal.sh --logs --since 5m

# Stream live
./scripts/receive_signal.sh --logs --follow
```

**Dependencies**: `curl`, `jq`, Railway CLI (for --logs mode)

### references/signal-protocol.md
Complete reference for message formats, agent directory, workspace paths, and error handling.

### assets/plan-template.md
Template for composing plan handoff messages.

### assets/handback-template.md
Template for agent completion reports.
