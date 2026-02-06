---
name: agent-collaboration
description: This skill enables Claude Code to collaborate with OpenClaw agents deployed at kublai.kurult.ai via Signal messaging. Use this skill when implementing plans that benefit from persistent agent execution, delegating research or content tasks to specialized agents, monitoring ongoing agent work, or coordinating multi-step workflows between Claude Code and the OpenClaw agent network (Kublai, Mongke, Ogedei, Temujin, Jochi, Chagatai).
---

# Agent Collaboration

Collaborate with the OpenClaw agent network at `kublai.kurult.ai` to execute plans, delegate tasks, and coordinate work via Signal messaging.

## Agent Network

| Agent | Role | Specialty |
|-------|------|-----------|
| **@kublai** | Squad Lead | Coordination, delegation, quality review, human interface |
| **@mongke** | Researcher | Deep research, evidence gathering, competitive analysis |
| **@ogedei** | Writer | Content creation, editing, documentation |
| **@temujin** | Developer | Code implementation, automation, security review |
| **@jochi** | Analyst | Data analysis, SEO, metrics, strategic thinking |
| **@chagatai** | Operations | Admin tasks, scheduling, process management |

## Workflow: Plan Handoff

Send implementation plans to **@kublai** (Squad Lead), who coordinates the agent network and delegates to specialists.

### Step 1: Always Route Through Kublai

**All plans go to @kublai first.** Kublai will:
- Review the plan for clarity and feasibility
- Delegate to the appropriate specialist agent
- Monitor progress and coordinate handoffs
- Perform quality review before completion

Specialist agents (for reference):
- **@mongke** - Research, evidence gathering
- **@ogedei** - Writing, content creation
- **@temujin** - Code, automation, security
- **@jochi** - Analysis, metrics, strategy
- **@chagatai** - Operations, scheduling

### Step 2: Compose the Plan

Use the structured plan format:

```markdown
---PLAN-HANDOFF---
Plan ID: plan-20260202-001
Priority: high
To: @kublai

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
Report progress to: Claude Code (via Signal group)
Checkpoint frequency: after each major step
On completion: Send HANDBACK-REPORT
---END-PLAN---
```

**Note**: The "Suggested Approach" section hints at which specialist might handle it, but Kublai makes the final delegation decision.

### Step 3: Send via Signal DM

Send directly to the Kublai coordinator via DM (default):
```bash
./scripts/send_signal.sh "$(cat plan.md)"
```

Or send to the group if preferred:
```bash
./scripts/send_signal.sh "$(cat plan.md)" --group "BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA="
```

### Step 4: Monitor Progress

Agents report status via Signal. Track:
- Acknowledgment of plan receipt
- Checkpoint updates after each step
- Blocker notifications requiring intervention
- Completion handback report

## Workflow: Status Monitoring

Request status on ongoing work:

```markdown
---STATUS-REQUEST---
Plan ID: plan-20260202-001
To: @temujin

What is the current progress on the rate limiter implementation?
---END-REQUEST---
```

Expected response format:
```markdown
---STATUS-UPDATE---
Plan ID: plan-20260202-001
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

## Workflow: Course Correction

When agent work needs redirection:

```markdown
---COURSE-CORRECTION---
Plan ID: plan-20260202-001
To: @temujin
Severity: moderate

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

## Workflow: Receiving Handbacks

When agents complete work, they send handback reports:

```markdown
---HANDBACK-REPORT---
Plan ID: plan-20260202-001
Agent: @temujin
Status: completed

## Deliverables
- Rate limiter middleware: /data/workspace/deliverables/code/rate-limiter/
- Tests: /data/workspace/deliverables/code/rate-limiter/tests/
- Documentation: /data/workspace/deliverables/docs/rate-limiting.md

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
2. Verify success criteria are actually met
3. Pull relevant files to local environment if needed
4. Acknowledge receipt and close the plan

## Receiving Agent Responses

Agent responses can be retrieved via Railway logs using the `receive_signal.sh` script:

```bash
# Check for messages in last 5 minutes (default)
./scripts/receive_signal.sh

# Check last hour
./scripts/receive_signal.sh --since 1h

# Stream messages live
./scripts/receive_signal.sh --follow

# Raw logs (for debugging)
./scripts/receive_signal.sh --raw --since 10m
```

**Requirements**: Railway CLI installed and linked to the project (`railway link`).

**Alternative methods** (if Railway CLI unavailable):
1. **User relay**: User pastes agent responses from Signal into Claude Code
2. **Control UI history**: View at `https://kublai.kurult.ai/sessions`
3. **Workspace files**: Agents write to `/data/workspace/deliverables/`

## Quick Reference

### Signal Communication
- **Default Recipient**: `+19194133445` (DM to Kublai coordinator)
- **Bot Account**: `+15165643945`
- **Group (optional)**: Kublai Klub (`BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=`)

### Environment Variables
```bash
SIGNAL_RPC_URL=https://signal-cli-native-production.up.railway.app/api/v1/rpc
SIGNAL_ACCOUNT=+15165643945
SIGNAL_RECIPIENT=+19194133445
```

### Workspace Paths
```
/data/workspace/
├── tasks/inbox/       # Drop new tasks here
├── tasks/assigned/    # Agent picks up
├── tasks/in-progress/ # Active work
├── deliverables/      # Completed work output
└── memory/[agent]/    # Agent working memory
```

### Message Markers
| Marker | Purpose |
|--------|---------|
| `---PLAN-HANDOFF---` | Send plan to agent |
| `---STATUS-UPDATE---` | Progress report |
| `---HANDBACK-REPORT---` | Work completion |
| `---ASSISTANCE-REQUEST---` | Agent needs help |
| `---COURSE-CORRECTION---` | Redirect agent work |

## Security Considerations

**Plan Content**: Plans sent via Signal may contain sensitive information (file paths, API references, business logic). Ensure plans don't include:
- API keys, tokens, or credentials
- Database connection strings
- Internal IP addresses or infrastructure details
- Customer data or PII

**Agent Trust**: Handback reports come through Signal and should be verified:
- Check that deliverable paths exist and contain expected content
- Verify claimed success criteria against actual implementation
- Be skeptical of "completed" status without supporting evidence

**Signal CLI Exposure**: The `signal-cli-native-production.up.railway.app` endpoint is publicly accessible without authentication. This is intentional for the bot architecture but means anyone who discovers this URL could send messages to the Signal group. Monitor for unexpected messages.

## Resources

### scripts/send_signal.sh
Send messages via signal-cli JSON-RPC. No authentication required.

```bash
# Send DM to default recipient (+19194133445)
./scripts/send_signal.sh "Hello Kublai"

# Send DM to specific number
./scripts/send_signal.sh "Message" --dm +1234567890

# Send to group instead
./scripts/send_signal.sh "Group message" --group "BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA="
```

**Dependencies**: `curl`, `jq`

### scripts/receive_signal.sh
Receive messages by polling Railway logs. Parses signal-cli-native logs for message content.

```bash
# Check last 5 minutes
./scripts/receive_signal.sh

# Check last hour
./scripts/receive_signal.sh --since 1h

# Stream live
./scripts/receive_signal.sh --follow
```

**Dependencies**: Railway CLI (`railway`), must be linked to project

### references/signal-protocol.md
Complete reference for message formats, agent directory, workspace paths, and error handling procedures.

### assets/plan-template.md
Template for composing plan handoff messages with all required fields.

### assets/handback-template.md
Template for agent completion reports.
