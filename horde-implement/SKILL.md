---
name: horde-implement
description: This skill should be used when the user invokes "/implement" to automatically generate an implementation plan using senior-prompt-engineer, create structured tasks, and deploy a subagent swarm using subagent-driven-development to execute the plan. After implementation, invokes implementation-status to audit completion before running horde-review. The skill handles the full pipeline from prompt engineering through task creation to autonomous execution, audit, and review across software development, infrastructure, content creation, and data processing domains.
integrations:
  - horde-swarm
  - senior-prompt-engineer
  - subagent-driven-development
  - dispatching-parallel-agents
  - implementation-status
  - horde-review
---

# Implement

Automatically transform user requests into executed implementations through AI-driven planning and subagent swarm execution.

## Overview

This skill provides a complete implementation pipeline:

1. **Prompt Engineering** - Uses `senior-prompt-engineer` to analyze the request and generate a comprehensive implementation plan
2. **Task Decomposition** - Breaks the plan into discrete, trackable tasks
3. **Subagent Swarm Deployment** - Uses `subagent-driven-development` to execute tasks with parallel subagents
4. **Autonomous Execution** - Automatically proceeds through the full pipeline without user intervention
5. **Implementation Status Audit** - Uses `implementation-status` to verify 100% completion before testing
6. **Testing and Validation** - Designs and executes comprehensive test suite (unit, integration, e2e) with coverage targets
7. **Critical Review** - Uses `horde-review` to validate the tested implementation across all relevant domains (only after tests pass)

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

### Phase 5: Implementation Status Audit

Before proceeding to testing, invoke `implementation-status` to verify completion:

1. **Invoke implementation-status** to audit the implementation:
   - Provide the plan path and context
   - Request comprehensive audit of all phases/tasks
   - Get completion percentage (Complete/Partial/Missing for each phase)

2. **Process audit results**:
   - If **100% complete** (all phases marked "Complete"): Proceed to Phase 6
   - If **partial completion** (some phases marked "Partial" or "Missing"):
     - Present status matrix to user
     - Ask whether to:
       - Complete remaining work first (recommended)
       - Proceed to testing with incomplete implementation (not recommended)
     - If user chooses to complete: Return to Phase 3 with remaining tasks

3. **Audit output format** (expected from `implementation-status`):
   ```markdown
   | Phase | Status | Implemented | Missing | Blockers |
   |-------|--------|-------------|---------|----------|
   | Phase 1 | Complete | Files... | None | None |
   | Phase 2 | Complete | Files... | None | None |
   ```

### Phase 6: Testing and Validation

**Only after Phase 5 confirms 100% completion**, design and execute comprehensive testing:

1. **Design Testing Plan** (using `generate-tests` or `Task(subagent_type=...)`):
   - Analyze implementation to identify test requirements
   - Design test strategy covering:
     - **Unit tests** - Individual component validation
     - **Integration tests** - Cross-component interaction
     - **End-to-end tests** - Full workflow validation
     - **Edge case tests** - Boundary conditions and error handling
     - **Performance tests** - Load and stress testing (if applicable)
   - Define test success criteria and coverage targets

2. **Execute Testing Plan**:
   - Generate test cases and test code
   - Run tests and collect results
   - Measure coverage against targets

3. **Process Test Results**:
   - If **all tests pass** and **coverage meets targets**: Proceed to Phase 7
   - If **tests fail** or **coverage insufficient**:
     - Present test failure report
     - Dispatch fix tasks for failing tests
     - Return to Phase 3 to address gaps
     - Re-run Phase 6 after fixes

4. **Testing output format**:
   ```markdown
   | Test Category | Tests Run | Passed | Failed | Coverage |
   |---------------|-----------|--------|--------|----------|
   | Unit          | 45        | 45     | 0      | 92%      |
   | Integration   | 12        | 12     | 0      | 88%      |
   | E2E           | 8         | 8      | 0      | 100%     |
   | **Total**     | **65**    | **65** | **0**  | **90%**  |
   ```

**Dispatch Pattern for Testing:**
```python
# Design testing plan
Skill("generate-tests", """
Design comprehensive test plan for:
- Implementation: [files changed]
- Test types: unit, integration, e2e, edge cases
- Coverage target: >80%
- Output: Test plan with test cases
""")

# Execute tests (parallel dispatch)
Task(
    subagent_type="python-development:python-pro",
    prompt="""Implement and run unit tests:
- Files to test: [list]
- Coverage target: >80%
- Run: pytest with coverage
- Report: Pass/fail status and coverage"""
)
Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Implement and run integration tests:
- API endpoints: [list]
- Database interactions: [list]
- External service mocks: [list]
- Report: Pass/fail status"""
)
```

### Phase 7: Critical Review

**Only after Phase 6 (Testing) confirms all tests pass**, invoke `horde-review` for comprehensive validation:

1. **Determine review scope** based on implementation type:
   - **Backend changes**: Backend, Architecture, Security, Performance, DevOps
   - **Frontend changes**: UX & Accessibility, Frontend, Architecture
   - **Fullstack changes**: All domains applicable
   - **Infrastructure**: DevOps, Architecture (possibly Security)

2. **Invoke horde-review** with the implemented artifact:
   - Provide context: what was built, files changed
   - Request multi-domain analysis based on scope
   - Parallel dispatch of specialist skills

3. **Present consolidated review report**:
   - Executive summary of review findings
   - Findings by domain with severity levels
   - Cross-cutting concerns
   - Prioritized improvement list

4. **Handle review outcomes**:
   - All findings passed → Implementation verified complete
   - Issues found → Present to user for approval to fix
   - User approves fixes → Return to Phase 3 with improvement tasks

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
7. Invoke `implementation-status` to audit completion (verifies 100% before review)
8. If 100% complete: Invoke `horde-review` for comprehensive validation across Backend, Architecture, Security, and DevOps domains
9. If not 100% complete: Offer to complete remaining work first
10. Present consolidated review report with findings and improvement recommendations

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
- `implementation-status` - Completion audit before review (Phase 5)
- `horde-review` - Comprehensive post-implementation validation (Phase 6, only after 100% completion)
