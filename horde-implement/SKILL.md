---
name: implement
description: This skill should be used when the user invokes "/implement" to automatically generate an implementation plan using senior-prompt-engineer, create structured tasks, and deploy a subagent swarm using subagent-driven-development to execute the plan. The skill handles the full pipeline from prompt engineering through task creation to autonomous execution across software development, infrastructure, content creation, and data processing domains.
integrations:
  - senior-prompt-engineer
  - subagent-driven-development
  - dispatching-parallel-agents
---

# Implement

Automatically transform user requests into executed implementations through AI-driven planning and subagent swarm execution.

## Overview

This skill provides a complete implementation pipeline:

1. **Prompt Engineering** - Uses `senior-prompt-engineer` to analyze the request and generate a comprehensive implementation plan
2. **Task Decomposition** - Breaks the plan into discrete, trackable tasks
3. **Subagent Swarm Deployment** - Uses `subagent-driven-development` to execute tasks with parallel subagents
4. **Autonomous Execution** - Automatically proceeds through the full pipeline without user intervention

## When to Use

Invoke `/implement` when you want to:

- Build a new feature or component
- Refactor existing code or infrastructure
- Set up deployments, CI/CD, or infrastructure
- Create content, documentation, or marketing materials
- Build data pipelines, ETL processes, or ML workflows
- Fix bugs or resolve technical issues
- Any task that can be broken into discrete implementation steps

## Workflow

### Phase 1: Request Analysis and Plan Generation

Dispatch `senior-prompt-engineer` to analyze the user request and generate an implementation plan.

**Prompt Structure for senior-prompt-engineer:**

```
Analyze the following implementation request and create a comprehensive plan.

User Request: {user_request}

Context:
- Current directory: {cwd}
- Relevant files (if any): {file_list}

Create an implementation plan that includes:
1. Clear objective statement
2. Domain classification (software, infrastructure, content, data)
3. Task breakdown with dependencies
4. Technical approach and patterns
5. Success criteria
6. Risk mitigation strategies

Format the plan as a structured markdown document suitable for subagent execution.
```

### Phase 2: Task Extraction and Creation

Parse the generated plan and create trackable tasks:

1. **Extract tasks** from the plan's task breakdown section
2. **Identify dependencies** between tasks
3. **Create TodoWrite entries** for each task with:
   - Task ID
   - Description
   - Dependencies (blocked_by)
   - Estimated complexity

### Phase 3: Subagent Swarm Deployment

Use `subagent-driven-development` to execute the implementation plan:

1. **Dispatch implementer subagent** per task with:
   - Full task description from the plan
   - Context from previous completed tasks
   - Success criteria from the plan

2. **Execute verification subagent** after each task:
   - Confirm tests pass
   - Verify implementation matches spec
   - Check for regressions

3. **Execute domain specialist review**:
   - Route to appropriate specialist based on task type
   - Verify technical correctness
   - Ensure best practices followed

4. **Execute code quality review**:
   - Check style, patterns, maintainability
   - Ensure documentation is updated

### Phase 4: Completion and Summary

After all tasks complete:

1. **Generate implementation summary**:
   - What was implemented
   - Files changed/created
   - Tests added
   - Any issues encountered

2. **Present results** to user with:
   - High-level summary
   - Link to detailed changes
   - Next steps (if any)

## Domain Routing

Automatically detect domain from the plan and route to appropriate specialists:

**For Skill invocation (use `Skill()` tool):**

| Domain | Keywords | Skills to Invoke |
|--------|----------|------------------|
| Software | code, API, component, refactor, bug | `code-reviewer`, `senior-backend`, `senior-frontend` |
| Infrastructure | deploy, CI/CD, Docker, Kubernetes | `senior-devops` |
| Content | write, document, blog, copy | `content-research-writer` |
| Data | ETL, pipeline, analysis, ML | `senior-data-engineer`, `senior-data-scientist` |
| Testing | test, spec, verify | `generate-tests` |
| Quality | review, audit, check | `code-reviewer` |

**For Task subagent dispatch (use `Task(subagent_type=...)`):**

| Domain | Keywords | Subagent Type |
|--------|----------|---------------|
| Backend | API, endpoint, database, schema | `backend-development:backend-architect` |
| Frontend | component, UI, React, accessibility | `frontend-mobile-development:frontend-developer` |
| DevOps | infrastructure, deployment, CI/CD | `senior-devops` (as skill) |
| Data Engineering | pipeline, ETL, analytics | `senior-data-engineer` (as skill) |

**Key distinction:**
- **Skills** are invoked via `Skill("skill-name", "prompt")` - these are workflow capabilities
- **Subagent types** are dispatched via `Task(subagent_type="domain:agent", prompt="...")` - these are specialized agent implementations

## Task State Management

Track task progress through states:

```
                    ┌─────────────┐
                    │   pending   │
                    └──────┬──────┘
                           │ start
                           ▼
                    ┌─────────────┐     max retries      ┌──────────┐
                    │ in_progress │─────────────────────▶│ escalated│
                    └──────┬──────┘    exceeded          └──────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌──────────┐
        │completed│  │  failed │  │partial   │
        └─────────┘  └────┬────┘  │complete  │
                          │       └────┬─────┘
                    retry │            │ continue
                    with  │            │
                    backoff▼            ▼
                    ┌───────────────────────┐
                    │      retrying         │
                    │  (attempt N of 3)     │
                    └───────────────────────┘
```

**State Definitions:**
- `pending`: Task created but not started
- `in_progress`: Task currently being executed
- `completed`: Task finished successfully
- `failed`: Task failed, awaiting retry decision
- `retrying`: Task in retry with exponential backoff
- `partial_complete`: Task partially completed (some deliverables ready)
- `escalated`: Max retries exceeded, requires human intervention

**Retry Policy:**
- Max 3 retry attempts per task
- Exponential backoff: 1s, 2s, 4s between attempts
- Circuit breaker: After 3 failures, escalate to user

**Dependency Cycle Detection:**
- Before execution, run topological sort on task graph
- If cycle detected, halt and report circular dependencies to user
- Require user to resolve dependency graph before proceeding

**On task failure:**
1. Capture error context in structured format:
   ```json
   {
     "error_type": "transient|permanent|architectural",
     "component": "task-id",
     "message": "error description",
     "timestamp": "ISO8601",
     "trace_id": "trace-id",
     "recovery_hints": ["suggested actions"]
   }
   ```
2. Use `systematic-debugging` to analyze root cause
3. Dispatch fix subagent with debugging context
4. Retry with exponential backoff (max 3 attempts)
5. Escalate to user if retries exhausted or error is architectural

**Error Taxonomy:**
- **Transient**: Network issues, temporary unavailability → Auto-retry
- **Permanent**: Invalid configuration, missing dependencies → Escalate after analysis
- **Architectural**: Design flaws, fundamental issues → Immediate escalation

## Execution Configuration

**Parallelism:**
- Execute independent tasks in parallel (no hard limit - use resource monitoring)
- Respect task dependencies (blocked tasks wait)
- Dynamic concurrency based on available resources

**Context Passing:**
- Pass completed task outputs to dependent tasks via structured context object
- Maintain shared context across the swarm
- Context schema: `{ plan_summary, completed_tasks[], current_task, shared_artifacts{}, dependencies_resolved[] }`

**Review Gates:**
- Verification after each task
- Specialist review for domain-specific tasks
- Quality review before marking complete

## State Persistence and Checkpointing

**Checkpoint Pattern:**
- Create checkpoint after each phase completion (plan generation, task extraction, each task execution)
- Store checkpoint to durable storage: `.claude/implement-checkpoints/{session_id}/{phase}.json`
- Checkpoint includes: task states, context, completed work, errors encountered

**Recovery Procedures:**
- On session interruption, scan for latest checkpoint on next `/implement` invocation
- If checkpoint found within 24 hours, offer resume from checkpoint
- If resuming, validate task states and continue from last completed phase

**TodoWrite Integration:**
- Each task maps to a TodoWrite entry
- Task state transitions update TodoWrite atomically
- On recovery, sync state from TodoWrite if checkpoint is stale

## Observability and Monitoring

**Structured Logging:**
```json
{
  "timestamp": "ISO8601",
  "session_id": "uuid",
  "phase": "plan_generation|task_execution|review",
  "event": "subagent_start|subagent_complete|error",
  "task_id": "task-identifier",
  "subagent_type": "implementer|verifier|reviewer",
  "duration_ms": 1234,
  "status": "success|failure"
}
```

**Metrics:**
- Active subagents count
- Task queue depth
- Completion rate by domain
- Average time per task
- Retry count per task
- Error rate by phase

**Health Checks:**
- Controller process heartbeat every 30 seconds
- Subagent liveness check (timeout if no response)
- Resource usage monitoring

**Trace Propagation:**
- Generate trace ID at session start
- Propagate trace ID through all subagent dispatches
- Include trace ID in all log entries

## Resource Controls

**Retry Policy:**
- Max 3 retry attempts per task
- Exponential backoff: 1s, 2s, 4s between retries
- Circuit breaker: After 3 failures on same task, escalate to user

## Example Usage

**User:** `/implement Create a user authentication API with JWT tokens`

**Skill Execution:**
1. Dispatch `senior-prompt-engineer` to create auth API plan
2. Extract tasks: setup project structure, implement JWT middleware, create login endpoint, create register endpoint, add tests
3. Create TodoWrite tasks with dependencies
4. Deploy subagent swarm via `subagent-driven-development`
5. Execute tasks with verification and reviews
6. Present completed implementation summary

## Error Handling

**Plan Generation Fails:**
- Retry with additional context
- Ask clarifying questions if request is ambiguous

**Task Execution Fails:**
- Capture full error context
- Use `systematic-debugging` for root cause
- Dispatch fix subagent
- Retry with fix applied

**Multiple Failures:**
- Escalate to user with context
- Present partial results
- Recommend next steps

## Integration Points

**Required Skills:**
- `senior-prompt-engineer` - Plan generation
- `subagent-driven-development` - Task execution
- `dispatching-parallel-agents` - Parallel subagent management

**Optional Skills (auto-detected by domain):**
- `code-reviewer` - Code review
- `senior-backend` - Backend implementation
- `senior-frontend` - Frontend implementation
- `senior-devops` - Infrastructure tasks
- `senior-data-engineer` - Data pipelines
- `content-research-writer` - Content creation
- `systematic-debugging` - Error analysis
