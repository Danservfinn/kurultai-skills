# Signal Communication Protocol

Reference for communicating with OpenClaw agents via Signal messaging.

## Connection Details

**Signal-CLI RPC Endpoint**: `https://signal-cli-native-production.up.railway.app/api/v1/rpc`
**Signal Account**: `+15165643945`
**Signal Group Name**: `Kublai Klub`
**Signal Group ID**: `BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=`

**Note**: The OpenClaw gateway at `kublai.kurult.ai` is behind Authentik OAuth proxy. For programmatic access, use the signal-cli JSON-RPC endpoint directly.

## JSON-RPC API Reference

### Send Message to Group
```bash
curl -X POST "https://signal-cli-native-production.up.railway.app/api/v1/rpc" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send",
    "params": {
      "account": "+15165643945",
      "groupId": "BROemHVncLgSz8tReUKBz6V3BeDhDB0EXaJd+sRp6oA=",
      "message": "Your message here"
    },
    "id": 1
  }'
```

### Send Direct Message
```bash
curl -X POST "https://signal-cli-native-production.up.railway.app/api/v1/rpc" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send",
    "params": {
      "account": "+15165643945",
      "recipient": ["+19194133445"],
      "message": "Your message here"
    },
    "id": 1
  }'
```

### List Groups
```bash
curl -X POST "https://signal-cli-native-production.up.railway.app/api/v1/rpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"listGroups","params":{"account":"+15165643945"},"id":1}'
```

## Message Types

### 1. Plan Handoff

Send an implementation plan to @kublai (Squad Lead) for delegation and execution.

```markdown
---PLAN-HANDOFF---
Plan ID: [unique-identifier]
Priority: high | medium | low
To: @kublai

## Objective
[Clear statement of what needs to be accomplished]

## Context
[Background information the agent needs]

## Steps
1. [Step with clear success criteria]
2. [Step with clear success criteria]
3. [Step with clear success criteria]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]

## Constraints
- [Time limit, if any]
- [Resources available]
- [Scope boundaries]

## Handoff Protocol
Report progress to: [Signal group or DM]
Checkpoint frequency: [after each step | hourly | on completion]
Escalate blockers to: @kublai
---END-PLAN---
```

### 2. Status Update

Request or provide status on ongoing work.

```markdown
---STATUS-UPDATE---
Plan ID: [reference to original plan]
Agent: [reporting agent]
Timestamp: [ISO 8601]

## Progress
- [x] Step 1: [completion notes]
- [ ] Step 2: [in progress - 60%]
- [ ] Step 3: [not started]

## Blockers
[None | Description of what's blocking progress]

## Decisions Made
- [Decision 1]: [rationale]

## Next Action
[What happens next and when]
---END-STATUS---
```

### 3. Handback Report

Agent reports completion back to Claude Code.

```markdown
---HANDBACK-REPORT---
Plan ID: [original plan reference]
Agent: [completing agent]
Status: completed | partial | blocked

## Deliverables
- [Deliverable 1]: [location or description]
- [Deliverable 2]: [location or description]

## Summary
[Brief narrative of what was accomplished]

## Success Criteria Met
- [x] [Criteria 1]
- [x] [Criteria 2]

## Files Modified
- [path/to/file1] - [what changed]
- [path/to/file2] - [what changed]

## Open Items
[Any remaining work or follow-up needed]

## Learnings
[Insights for future similar tasks]
---END-HANDBACK---
```

### 4. Assistance Request

OpenClaw agent requests Claude Code help.

```markdown
---ASSISTANCE-REQUEST---
From: @[agent-name]
Plan ID: [if related to existing plan]
Urgency: high | medium | low

## Problem
[Clear description of the issue]

## What I've Tried
1. [Attempt 1 and result]
2. [Attempt 2 and result]

## Specific Help Needed
[Exactly what assistance is required]

## Context Files
- [path/to/relevant/file]
- [path/to/relevant/file]
---END-REQUEST---
```

### 5. Course Correction

Claude Code provides guidance to redirect work.

```markdown
---COURSE-CORRECTION---
Plan ID: [reference]
To: @[agent]
Severity: minor | moderate | major

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

| Agent | Role | Best For |
|-------|------|----------|
| @kublai | Squad Lead | Coordination, delegation, quality review |
| @mongke | Deep Researcher | Research, evidence gathering, analysis |
| @ogedei | Content Writer | Writing, editing, documentation |
| @temujin | Developer | Code implementation, automation, security |
| @jochi | Analyst | Data analysis, SEO, metrics, strategy |
| @chagatai | Operations | Admin, scheduling, process management |

## Workspace Paths

```
/data/workspace/
├── tasks/           # Task queue and tracking
│   ├── inbox/       # New tasks
│   ├── assigned/    # Tasks assigned to agents
│   ├── in-progress/ # Active work
│   ├── review/      # Awaiting review
│   └── done/        # Completed
├── memory/          # Agent working memory
│   └── [agent]/     # Per-agent memory
│       ├── WORKING.md
│       └── [date].md
├── deliverables/    # Completed work output
│   ├── research/
│   ├── content/
│   ├── code-review/
│   └── security/
└── souls/           # Agent personality files
```

## Response Timeouts

| Message Type | Expected Response |
|--------------|-------------------|
| Plan Handoff | Acknowledgment within 15 minutes |
| Status Update | Immediate if agent is active |
| Assistance Request | Within 1 heartbeat cycle (15 min) |
| Course Correction | Acknowledgment required |

## Error Handling

If no response received:

1. Check agent heartbeat status in OpenClaw Control UI
2. Verify Signal channel connectivity
3. Retry via alternative agent (@kublai can redirect)
4. If persistent, escalate to human via direct Signal DM
