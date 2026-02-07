---
title: Horde Debug
link: horde-debug
type: skill
tags: [debugging, root-cause, golden-horde, multi-agent, autonomous, health-monitoring]
ontological_relations:
  - relates_to: [[golden-horde]]
  - relates_to: [[systematic-debugging]]
  - relates_to: [[horde-health]]
  - relates_to: [[jochi]]
version: 1.0.0
uuid: AUTO_GENERATED
created_at: AUTO_GENERATED
updated_at: AUTO_GENERATED
authors: ["Kurultai Project"]
---

# Horde Debug

> **Multi-agent root cause debugging using swarm discovery and expertise routing.**
>
> Find root causes systematically. Fix what's actually broken. Stop guessing.

## Overview

`horde-debug` is a systematic debugging skill that combines:
- **Golden-horde patterns**: Swarm discovery, expertise routing, review loop
- **Systematic debugging**: 4-phase root cause methodology
- **Iron law enforcement**: No fixes without verified root cause

### When to Use

| Trigger | Example | Command |
|---------|---------|---------|
| **horde-health alert** | Health check fails | Auto-invoked |
| **Jochi autonomous** | Scheduled check detects anomaly | Auto-invoked |
| **Manual debugging** | "Tests failing intermittently" | `claude skill:horde-debug "Intermittent test failures"` |

### What It Does

1. **Gathers evidence** in parallel (logs, metrics, configs, traces)
2. **Routes to specialists** based on issue domain
3. **Validates hypotheses** through adversarial review
4. **Applies minimal fixes** targeting root cause only
5. **Verifies thoroughly** with regression checks

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   TRIGGER   │───▶│ SWARM       │───▶│ SPECIALISTS │
│             │    │ DISCOVERY   │    │ (parallel)  │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
              ┌─────────────────────┘
              ▼
          ┌─────────────┐    ┌─────────────┐
          │ EXPERTISE   │───▶│ HYPOTHESIS  │
          │ ROUTING     │    │ COMMITTEE   │
          └─────────────┘    └─────────────┘
              │
              ▼
          ┌─────────────┐    ┌─────────────┐
          │ REVIEW      │───▶│ WATCHDOG    │
          │ LOOP        │    │ VERIFICATION│
          └─────────────┘    └─────────────┘
```

## Workflow

### Phase 1: Root Cause Identification
- Swarm discovery: Parallel evidence gathering
- Expertise routing: Assign to domain specialists
- Output: Ranked root cause candidates

### Phase 2: Pattern Recognition
- Cross-correlate findings
- Identify systemic patterns
- Output: Pattern analysis report

### Phase 3: Hypothesis Verification
- Review loop: Adversarial debate
- Evidence chain validation
- Output: Verified root cause

### Phase 4: Implementation & Validation
- Fix design with rollback plan
- Apply (auto or supervised)
- Watchdog verification

## Configuration

Create `.horde-debug.yaml` in your project root:

```yaml
project:
  root: /path/to/project
  tech_stack: auto  # or nodejs, python, go, rust

monitoring:
  health_check_url: http://localhost:3000/health
  log_location: ./logs

testing:
  test_command: npm test
  test_timeout: 300

autonomy:
  level: semi-auto  # supervised, semi-auto, full-auto
```

## Agent Types

| Tier | Agents | Role |
|------|--------|------|
| 1 | backend-investigator, network-diagnostician, database-analyst, infrastructure-engineer, log-forensic-analyst | Domain specialists |
| 2 | plan, agent-expert, docs | Coordination |
| 3 | chaos-engineer, compliance-auditor, cost-analyst, general-purpose | Quality & safety |

## Output

The skill returns:

1. **JSON result** (machine-readable for Jochi):
   ```json
   {
     "root_cause": "...",
     "confidence": 0.95,
     "fix_applied": true,
     "verification": "passed"
   }
   ```

2. **Markdown report** (human-readable):
   - Executive summary
   - Root cause with evidence
   - Fix description
   - Verification results

## Examples

### Example 1: Service Down

```bash
claude skill:horde-debug "Moltbot returning 500 errors"
```

### Example 2: Test Failures

```bash
claude skill:horde-debug \
  --issue="Integration tests failing" \
  --context="tests/integration"
```

### Example 3: With Logs

```bash
claude skill:horde-debug \
  --logs=./logs/error.log \
  --service=moltbot-railway
```

## Integration

### horde-health
Auto-invoked when health check fails. Receives alert context as input.

### Jochi
Scheduled or event-driven invocation. Returns JSON result for automation.

## The Iron Law

**NO FIXES WITHOUT ROOT CAUSE**

Every fix requires:
1. ✅ Explicit root cause statement
2. ✅ Evidence chain supporting it
3. ✅ Verified hypothesis
4. ✅ Rollback plan

Random fixes are rejected by the review loop.

## See Also

- [[golden-horde]] - Multi-agent orchestration patterns
- [[horde-health]] - Health monitoring
- [[jochi]] - Autonomous runner
- [[systematic-debugging]] - Root cause methodology
