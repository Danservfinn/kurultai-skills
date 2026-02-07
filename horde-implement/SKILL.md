---
name: horde-implement
description: >
  General-purpose plan executor and implementation pipeline. Two entry paths:
  (A) Generate mode — takes a request, generates a plan via senior-prompt-engineer, then executes.
  (B) Execute mode — takes an existing structured markdown plan (like kurultai_0.2.md), parses it
  into phases and tasks, and executes with phase gating via horde-gate-testing.
  Both paths converge at the execution engine with subagent dispatch, browser automation,
  checkpoint/resume, implementation-status audit, horde-test, and horde-review.
integrations:
  - horde-swarm
  - horde-gate-testing
  - horde-test
  - horde-review
  - senior-prompt-engineer
  - subagent-driven-development
  - dispatching-parallel-agents
  - implementation-status
  - systematic-debugging
---

# Implement

General-purpose plan executor. Transforms requests or existing plans into executed implementations through AI-driven orchestration, subagent swarm execution, and phased gate testing.

## Process Guard

**Before dispatching agents**, run: `pgrep -fc "claude.*--disallowedTools"`. If count > 50, run `pkill -f "claude.*--disallowedTools"` first. This prevents orphaned subagent accumulation from causing ENFILE (file table overflow).

## Overview

```
                         /implement
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
     PATH A: GENERATE              PATH B: EXECUTE
     (from request)                (from existing plan)
              │                           │
     senior-prompt-engineer        Plan Parser
     generates plan                extracts phases/tasks
              │                           │
              └─────────────┬─────────────┘
                            ▼
                    EXECUTION ENGINE
                   ┌────────────────┐
                   │ Phase Loop     │
                   │  ├─ Subagent   │ ← Task subagents per phase
                   │  │  executors  │
                   │  ├─ Browser    │ ← Orchestrator handles inline
                   │  │  tasks      │
                   │  ├─ Gate test  │ ← horde-gate-testing (selective)
                   │  └─ Checkpoint │ ← JSON state persistence
                   └────────────────┘
                            │
                    POST-EXECUTION
                   ┌────────────────┐
                   │ impl-status    │ ← 100% completion audit
                   │ horde-test     │ ← comprehensive testing
                   │ horde-review   │ ← multi-domain review
                   └────────────────┘
```

## When to Use

Invoke `/implement` when you want to:

- **Execute an existing plan document** (deployment plans, migration plans, feature specs)
- Build a new feature or component from a request
- Set up deployments, CI/CD, or infrastructure
- Refactor existing code or infrastructure
- Any task that can be broken into discrete implementation steps

## Detecting Entry Path

On invocation, determine the entry path:

**Path B (Execute mode)** if ANY of these are true:
- User provides a file path to a plan document (`.md` file in `docs/plans/` or similar)
- User says "implement this plan", "execute this", "follow this document"
- The argument references an existing structured markdown file with phases/tasks

**Path A (Generate mode)** if:
- User provides a request description without referencing an existing plan
- User says "build", "create", "implement" + feature description

---

## Path A: Generate Mode

When no existing plan is provided, generate one.

### A.1: Plan Generation

Dispatch `senior-prompt-engineer` to analyze the request:

```
Skill("senior-prompt-engineer", """
Analyze this implementation request and create a comprehensive plan.

User Request: {user_request}

Context:
- Current directory: {cwd}
- Relevant files: {file_list}

Create a plan with:
1. Clear objective statement
2. Phase breakdown (use ## Phase N: Name format)
3. Tasks per phase (use ### Task N.M: Name format)
4. Exit criteria per phase (use ### Exit Criteria Phase N format with checkboxes)
5. Dependencies between phases
6. Success criteria

Format as structured markdown suitable for Path B execution.
""")
```

### A.2: Save and Hand Off

Save the generated plan to `docs/plans/{date}-{slug}.md`, then proceed to Path B execution.

---

## Path B: Plan Ingestion

### B.1: Plan Parser Protocol

Read the plan document and extract the execution structure. The plan may exceed context limits, so parse in two passes.

**Pass 1: Build Plan Index (~500 tokens)**

Scan the document for structural markers:

```
Phase headers:     ## Phase {id}: {name}        (id can be: -1, 0, 1, 1.5, etc.)
Task headers:      ### Task {id}: {name}         (id matches phase: 1.1, 1.2, 1.5.1)
Exit criteria:     ### Exit Criteria Phase {id}   (checklist items below)
Appendix headers:  ### Appendix {letter}: {name}
Duration markers:  **Duration**: {time}
Dependency markers: **Dependencies**: {text}
```

Produce a plan index:

```json
{
  "plan_name": "Kurultai v0.2: Complete Railway Deployment Plan",
  "source_file": "docs/plans/kurultai_0.2.md",
  "total_phases": 10,
  "phases": [
    {
      "id": "-1",
      "name": "Wipe and Rebuild",
      "line_start": 188,
      "line_end": 331,
      "task_count": 4,
      "tasks": ["-1.1", "-1.2", "-1.3", "-1.4"],
      "has_exit_criteria": true,
      "duration": "30 minutes",
      "dependencies": [],
      "risk_level": "HIGH"
    }
  ],
  "appendices": ["A", "B", "C", "D", "E", "F", "G", "H"],
  "estimated_total_time": "4-6 hours"
}
```

**Pass 2: Classify Phase Boundaries for Gate Testing**

For each phase transition, determine gate depth:

| Transition | Gate Depth | Criteria |
|------------|-----------|----------|
| Phase N exports code/schemas consumed by N+1 | `STANDARD` | horde-gate-testing |
| Phase N is code, N+1 deploys that code | `DEEP` | horde-gate-testing + verification |
| Phases are independent systems | `LIGHT` | Exit criteria only |
| Phase is purely validation/verification | `NONE` | Just advance |

Store gate classifications in the plan index.

### B.2: Context Windowing

The full plan will not fit in a subagent's context. Use this strategy:

**For the orchestrator:** Hold only the plan index (~500 tokens). Read phase slices on demand.

**For phase executor subagents:** Pass:
1. The specific phase slice (from `line_start` to `line_end`)
2. Relevant appendix sections (if tasks reference them)
3. A summary of completed prior phases (task names + status, ~100 tokens)
4. Shared artifacts from prior phases (env vars set, files created, services deployed)

**To extract a phase slice:**
```
Read(file_path=plan_source, offset=phase.line_start, limit=phase.line_end - phase.line_start)
```

### B.3: Task Type Classification

Within each phase, classify tasks for routing:

| Type | Detection | Executor |
|------|-----------|----------|
| `bash` | Contains ```bash code blocks with CLI commands | Subagent (Bash tool) |
| `code_write` | Contains Python/JS/Docker code to create as files | Subagent (Write/Edit tools) |
| `config` | Environment variables, YAML, JSON configuration | Subagent (Bash for `railway variables set`, Write for files) |
| `browser` | References web UI, dashboard, console, admin panel; contains URLs like `console.neo4j.io` | Orchestrator (Playwright MCP) |
| `verify` | Contains curl commands, test assertions, "Expected:" patterns | Subagent (Bash tool) |
| `human_required` | Account creation, payment, CAPTCHA, OAuth first-time consent | Pause for user |

---

## Execution Engine

### Phase Loop

The orchestrator executes phases sequentially:

```
FOR each phase in plan_index.phases:
  1. CHECK checkpoint — skip if phase already completed
  2. READ phase slice from plan document
  3. CLASSIFY tasks within the phase
  4. DISPATCH non-browser tasks to subagent executor(s)
     - Independent tasks: dispatch in parallel
     - Dependent tasks: dispatch sequentially
     - Conservative default: if dependency unclear, sequential
  5. EXECUTE browser tasks inline (orchestrator handles directly)
  6. VERIFY exit criteria (if phase has them)
  7. RUN gate test (if gate depth requires it)
  8. CHECKPOINT phase completion
  9. ADVANCE to next phase
```

### Task Dispatch to Phase Executors

Each phase is executed by dispatching a Task subagent:

```python
Task(
    subagent_type="general-purpose",
    description=f"Execute Phase {phase.id}",
    prompt=f"""
## You are executing Phase {phase.id}: {phase.name}

## Plan Context
Previously completed phases: {completed_phases_summary}
Shared artifacts: {shared_artifacts}

## Phase Instructions
{phase_slice_content}

## Your Task
Execute ALL tasks in this phase sequentially:
{task_list_with_descriptions}

For each task:
1. Read the task instructions carefully
2. Execute the commands/code as specified
3. Verify the task completed successfully
4. Report what was done and any artifacts created

## Output Format
Report for each task:
- Task ID and name
- Status: completed/failed
- What was done (commands run, files created/modified)
- Artifacts: list of files created, services deployed, env vars set
- Errors: any issues encountered

## Important
- Execute tasks in order unless explicitly marked as parallelizable
- If a task fails, report the error and continue to the next task
- Do NOT skip verification steps within tasks
"""
)
```

**Subagent type selection by domain:**

| Phase Domain | Subagent Type |
|-------------|---------------|
| Backend code | `backend-development:backend-architect` |
| Frontend code | `frontend-mobile-development:frontend-developer` |
| Infrastructure/deploy | `general-purpose` |
| Database/schema | `backend-development:backend-architect` |
| Mixed/general | `general-purpose` |

### Browser Task Handling

Browser tasks MUST be handled by the orchestrator directly — subagents do not have access to MCP browser tools.

**Detection keywords:** "dashboard", "console", "admin panel", "Navigate to", URLs in task text.

**Execution order:** Prefer CLI/API alternatives first. Only use browser automation when no CLI exists.

| Operation | Prefer | Browser Only If |
|-----------|--------|-----------------|
| Railway operations | `railway` CLI | CLI lacks the feature |
| Authentik admin | `ak` CLI or API (`/api/v3/`) | API doesn't support it |
| Neo4j AuraDB | No CLI for free tier | Always browser |
| Git/GitHub | `git`/`gh` CLI | Never browser |
| Docker | `docker` CLI | Never browser |

**Browser execution template (using Playwright MCP):**
```
1. mcp__plugin_playwright_playwright__browser_navigate → target URL
2. mcp__plugin_playwright_playwright__browser_snapshot → verify page loaded
3. Check: login page or dashboard?
   - If login needed + env var credentials available → fill form
   - If login needed + no credentials → PAUSE for user
4. Execute interactions (click, fill, select)
5. mcp__plugin_playwright_playwright__browser_snapshot → verify success
6. Extract output data (connection strings, IDs, URLs)
```

**Auth strategy by service:**

| Service | Auth Approach | Fallback |
|---------|--------------|----------|
| Railway | CLI (already authenticated) | Pre-authenticated Chrome |
| Authentik | Form fill from `AUTHENTIK_BOOTSTRAP_PASSWORD` env var | Pause for user |
| Neo4j AuraDB | Pre-authenticated Chrome session | Pause for user |
| Generic | Pre-authenticated Chrome session | Pause for user |

**Fallback ladder when browser automation fails:**
1. **Retry** (up to 3 times with wait)
2. **Alternative approach** (try API/CLI instead)
3. **Partial automation** (navigate to page, ask user to complete)
4. **Human handoff** (capture context, screenshot, tell user what to do)

---

## Phase Gate System

Two levels of verification run between phases.

### Level 1: Exit Criteria Verification (every phase)

Extract criteria from `### Exit Criteria Phase N` sections. Each checkbox item is one criterion.

**Classification:**

| Category | Detection | How Verified |
|----------|-----------|-------------|
| `automated` | Contains commands, URLs, ports, "returns", "responds", "exists" | Execute command via Bash, check exit code |
| `semi_automated` | "no errors", "logs show", "tests pass" | Execute command, interpret output |
| `subjective` | "sound", "clean", "appropriate" | Agent assessment with logged rationale |

**Verification protocol:**
1. Run all `automated` criteria (Bash commands, curl checks)
2. Run all `semi_automated` criteria (execute + interpret)
3. Assess `subjective` criteria (brief review of artifacts)

**Gate decision:**
- All criteria passed → **GATE OPEN**
- Any `automated`/`semi_automated` failed → **GATE BLOCKED** → tiered recovery
- Any `subjective` uncertain → **GATE HELD** → present to user

**Tiered recovery for blocked gates:**
1. **Auto-retry** (transient failures: timeout, not-ready) — wait 30s, retry, max 2 attempts
2. **Re-execute task** (identify which task produced the failing artifact, re-dispatch)
3. **User escalation** (present failure report, options: fix+retry / override / abort)

### Level 2: horde-gate-testing (selective)

Run between phases classified as `STANDARD` or `DEEP` gate depth.

**Invoke after exit criteria pass:**

```python
Skill("horde-gate-testing", f"""
Plan: {plan_source_file}
Current phase: Phase {N} — {phase_name}
Next phase: Phase {N+1} — {next_phase_name}

Phase {N} produced:
- Files: {files_changed_or_created}
- Services: {services_deployed}
- Schemas: {schema_changes}
- Config: {config_changes}

Phase {N+1} expects:
{next_phase_dependency_summary}

Test the integration surface between these phases.
Verify Phase {N}'s outputs satisfy Phase {N+1}'s inputs.
""")
```

**Process gate test results:**
- `PASS` → advance to next phase
- `WARN` → advance, log risks to checkpoint, report to user
- `FAIL` → dispatch fix subagents for identified issues, re-test

**When to use which gate depth:**

```
determine_gate_depth(phase_n, phase_n_plus_1):
  IF phase_n exports code/schemas AND phase_n_plus_1 imports them:
    RETURN "STANDARD"  → horde-gate-testing
  IF phase_n is implementation AND phase_n_plus_1 is deployment:
    RETURN "DEEP"      → horde-gate-testing + extra verification
  IF phases operate on independent systems:
    RETURN "LIGHT"     → exit criteria only
  IF phase_n_plus_1 is purely verification:
    RETURN "NONE"      → just advance
  DEFAULT:
    RETURN "LIGHT"     → conservative
```

**Example gate depth map for kurultai_0.2.md:**

| Transition | Depth | Reason |
|-----------|-------|--------|
| Phase -1 → 0 | LIGHT | Cleanup → setup, independent |
| Phase 0 → 1 | LIGHT | Env setup → neo4j, independent |
| Phase 1 → 1.5 | STANDARD | Neo4j schema → task dependency engine |
| Phase 1.5 → 2 | STANDARD | Task engine → capability acquisition |
| Phase 2 → 3 | DEEP | Code → Railway deployment |
| Phase 3 → 4 | LIGHT | Deploy → signal verify |
| Phase 4 → 4.5 | LIGHT | Signal → notion, independent |
| Phase 4.5 → 5 | LIGHT | Notion → authentik, independent |
| Phase 5 → 6 | STANDARD | Auth → monitoring, cross-cutting |
| Phase 6 → 7 | NONE | Monitoring → testing, natural |

---

## Checkpoint & Resume

### Checkpoint Storage

**Location:** `.claude/plan-executor/checkpoints/`
**File:** `{plan_hash_8chars}_{plan_name_slug}.checkpoint.json`
**Backup:** `{same}.prev.json` (previous checkpoint for corruption recovery)

### Checkpoint Format

```json
{
  "version": "1.0",
  "plan": {
    "name": "Plan name",
    "source_file": "/path/to/plan.md",
    "content_hash": "a1b2c3d4",
    "total_phases": 10,
    "phase_ids": ["-1", "0", "1", "1.5", "2", ...]
  },
  "execution": {
    "id": "exec_20260206_143022",
    "started_at": "2026-02-06T14:30:22Z",
    "last_updated_at": "2026-02-06T16:45:33Z",
    "current_phase": "2",
    "status": "in_progress"
  },
  "phases": {
    "-1": {
      "status": "completed",
      "tasks": [
        {"id": "t-1.1", "name": "Pre-Deletion Backup", "status": "completed", "artifacts": []}
      ],
      "gate": {"status": "passed", "depth": "LIGHT"}
    },
    "2": {
      "status": "in_progress",
      "tasks": [
        {"id": "t2.1", "status": "completed", "artifacts": ["railway-deploy.log"]},
        {"id": "t2.2", "status": "in_progress"},
        {"id": "t2.3", "status": "pending"}
      ],
      "gate": {"status": "pending", "depth": "DEEP"}
    }
  },
  "shared_artifacts": {
    "env_vars_set": ["RAILWAY_TOKEN", "NEO4J_URI"],
    "services_deployed": [{"name": "authentik-server", "url": "..."}],
    "files_created": ["authentik-server/Dockerfile"]
  },
  "error_log": []
}
```

**Size constraint:** Checkpoint stores task-level state only, not command outputs. Verbose logs go to separate artifact files. Target: under 50KB.

### When to Checkpoint

Write checkpoint (atomic: write temp → rename prev → rename active) at:
- Execution start (all phases pending)
- Each task completion or failure
- Each gate verification result
- Each phase completion
- Session end (graceful)

### Resume Protocol

On `/implement` invocation, check for existing checkpoints:

```
1. DISCOVER: List .claude/plan-executor/checkpoints/*.checkpoint.json
2. If none found → fresh execution
3. If found → read checkpoint, present to user:

   "Found checkpoint for '{plan_name}'
    Last active: {time_ago}
    Completed: Phases {list}
    Current: Phase {N} ({completed_tasks}/{total_tasks} tasks done)

    Options:
    1. Resume from Phase {N}
    2. Restart from a specific phase
    3. Start fresh (discard checkpoint)"

4. VALIDATE: Re-run exit criteria for most recent completed phase
   - If pass → resume from first pending task
   - If fail → report what changed, ask user for decision

5. STALE CHECK:
   - Checkpoint > 24 hours old → warn
   - Plan file hash changed → warn "plan was edited since last execution"
   - If changes only affect future phases → safe to resume
   - If changes affect completed phases → warn, let user decide
```

**In-progress tasks on resume:** Treated as pending (re-executed). Partial task state is unreliable.

### Phase Skip / Start-At

When user requests starting at a specific phase:

1. Read exit criteria for all skipped phases
2. Run automated criteria against current state (quick validation)
3. If all pass → proceed with skipped phases marked `skipped_verified`
4. If some fail → report which prerequisites are missing, offer options

---

## Post-Execution Pipeline

After all phases complete, run the quality pipeline.

### Implementation Status Audit

Invoke `implementation-status` to verify 100% completion:

```
Skill("implementation-status", """
Plan: {plan_source_file}
Context: {implementation_summary}
Audit all phases for completion status.
""")
```

- **100% complete** → proceed to testing
- **Partial** → present status matrix, offer to complete remaining work or proceed

### Testing & Validation

**Only after 100% completion confirmed.** Invoke `horde-test`:

```
Skill("horde-test", """
Execute comprehensive test plan for implementation.

Files changed: {all_artifacts_from_checkpoint}
Test types: unit, integration, e2e, edge cases
Coverage target: >80%

Report: Full test results with coverage analysis
""")
```

- **All pass** → proceed to review
- **Failures** → dispatch fix tasks, re-test

### Critical Review

**Only after tests pass.** Invoke `horde-review`:

```
Skill("horde-review", """
Review the implementation of {plan_name}.

Files changed: {artifacts}
Scope: {review_domains based on plan type}

Perform multi-domain analysis.
""")
```

Review domain routing:
- **Backend changes** → Backend, Architecture, Security, Performance
- **Frontend changes** → UX, Frontend, Architecture
- **Infrastructure** → DevOps, Architecture, Security
- **Fullstack** → All applicable domains

---

## Domain Routing

**For Skill invocation:**

| Domain | Keywords | Skills |
|--------|----------|--------|
| Software | code, API, component, refactor | `code-reviewer`, `senior-backend`, `senior-frontend` |
| Infrastructure | deploy, CI/CD, Docker | `senior-devops` |
| Content | write, document, blog | `content-research-writer` |
| Data | ETL, pipeline, ML | `senior-data-engineer`, `senior-data-scientist` |
| Testing | test, spec, verify | `generate-tests` |

**For Task subagent dispatch:**

| Domain | Subagent Type |
|--------|---------------|
| Backend | `backend-development:backend-architect` |
| Frontend | `frontend-mobile-development:frontend-developer` |
| Security | `security-auditor` |
| General | `general-purpose` |

---

## Task State Management

```
pending → in_progress → completed
                     → failed → retrying (max 3) → escalated
                     → partial_complete → continue
```

**Retry policy:** Max 3 attempts, exponential backoff (1s, 2s, 4s). After 3 failures → escalate to user.

**Error taxonomy:**
- **Transient** (timeout, connection refused) → auto-retry
- **Permanent** (invalid config, missing dependency) → escalate after analysis
- **Architectural** (design flaw) → immediate escalation

**On failure:**
1. Capture error context (type, message, component, recovery hints)
2. Use `systematic-debugging` if root cause unclear
3. Dispatch fix subagent
4. Retry with fix applied
5. Escalate if retries exhausted

---

## Error Handling

**Plan parsing fails:** Ask clarifying questions. Suggest plan format conventions.

**Phase executor fails:** Capture output, analyze failure, re-dispatch or escalate.

**Browser automation fails:** Follow fallback ladder (retry → CLI alternative → partial automation → human handoff).

**Gate test fails:** Dispatch fix subagents for specific integration issues, re-run gate.

**Context limit approaching:** Complete current task, write checkpoint, inform user to resume.

**Multiple failures in same phase:** Escalate to user with full context, present options (fix/skip/abort).

---

## Integration Points

**Required:**
- `horde-gate-testing` — Phase boundary integration testing
- `subagent-driven-development` — Task execution via subagent swarm
- `dispatching-parallel-agents` — Parallel subagent management

**Conditional (by entry path):**
- `senior-prompt-engineer` — Plan generation (Path A only)

**Post-execution (always):**
- `implementation-status` — Completion audit
- `horde-test` — Comprehensive testing
- `horde-review` — Multi-domain critical review

**On error:**
- `systematic-debugging` — Root cause analysis

**Domain specialists (auto-detected):**
- `senior-backend`, `senior-frontend`, `senior-devops`
- `senior-data-engineer`, `senior-data-scientist`
- `code-reviewer`, `content-research-writer`

---

## Examples

### Example 1: Execute an Existing Plan

**User:** `/implement docs/plans/kurultai_0.2.md`

**Execution:**
1. Detect Path B (file path provided)
2. Parse plan → 10 phases, ~30 tasks, 8 appendices
3. Check for checkpoint → none found, fresh execution
4. Classify gate depths → 4 STANDARD/DEEP, 6 LIGHT/NONE
5. Begin phase loop:
   - Phase -1: dispatch executor subagent, run tasks, exit criteria → LIGHT gate → advance
   - Phase 0: dispatch executor, env setup, exit criteria → LIGHT gate → advance
   - Phase 1: dispatch executor, Neo4j setup, exit criteria → horde-gate-testing (STANDARD) → advance
   - ...continue through all phases...
   - Phase 3: browser tasks for Authentik UI handled inline by orchestrator
6. Checkpoint after each phase
7. All phases complete → implementation-status audit → horde-test → horde-review
8. Present final report

### Example 2: Generate and Execute from Request

**User:** `/implement Create a user authentication API with JWT tokens`

**Execution:**
1. Detect Path A (no file path, feature request)
2. Dispatch `senior-prompt-engineer` to generate plan
3. Save plan to `docs/plans/2026-02-06-jwt-auth-api.md`
4. Hand off to Path B execution engine
5. Parse plan → 4 phases, 12 tasks
6. Execute with gate testing at code→test boundary
7. Post-execution pipeline: audit → test → review

### Example 3: Resume Interrupted Execution

**User:** `/implement docs/plans/kurultai_0.2.md`

**Execution:**
1. Detect Path B
2. Check for checkpoint → found! Last active 2 hours ago
3. Present: "Completed Phases -1 through 1.5, Phase 2 in progress (2/5 tasks done). Resume?"
4. User confirms resume
5. Validate Phase 1.5 exit criteria → pass
6. Resume Phase 2 from task 2.3
7. Continue execution normally
