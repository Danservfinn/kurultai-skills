---
name: horde-plan
version: "1.2"
description: >
  Create comprehensive implementation plans optimized for horde-implement execution.
  Plans follow a strict output contract (heading levels, exit criteria, task type hints,
  gate depth signals) ensuring automatic parsing by horde-implement's Plan Parser.
  For complex projects, invokes golden-horde deliberation to validate architecture
  before task breakdown. Structured handoff with plan manifest for zero-loss execution.
integrations:
  - horde-swarm
  - golden-horde
  - horde-implement
---

# Horde Plan

Create comprehensive implementation plans using plan mode with task breakdown, dependency mapping, and structured handoff to horde-implement for execution.

**New in v1.2:** Plans now follow a strict **Plan Output Contract** ensuring zero-friction parsing by horde-implement. Heading levels, exit criteria, task type hints, gate depth signals, and YAML frontmatter plan manifest are all standardized. Plans produced by horde-plan v1.2 can be executed by horde-implement Path B without any manual reformatting.

**v1.1:** Golden-horde pre-planning deliberation (Adversarial Debate, Consensus Deliberation) for complex projects. ADR constrains task breakdown.

## Quick Start

**Fast Plan (default):**
```bash
User: "/horde-plan Create a user authentication system with JWT tokens"

Claude:
1. Analyzes requirements + scores complexity
2. Enters plan mode (EnterPlanMode)
3. Creates task breakdown with phases
4. Maps dependencies (TaskCreate with addBlockedBy)
5. Generates plan.md
6. Exits plan mode for approval (ExitPlanMode)
7. Hands off to horde-implement for execution
```

**Validated Plan (complex projects):**
```bash
User: "/horde-plan --validated Build a HIPAA-compliant telemedicine platform"
  — or auto-detected when complexity is high —

Claude:
1. Analyzes requirements + scores complexity → HIGH
2. Offers validated planning with golden-horde deliberation
3. User approves → spawns golden-horde team (Adversarial Debate or Consensus)
4. Agents deliberate architecture → produce Architecture Decision Record (ADR)
5. Presents ADR to user for approval
6. Enters plan mode, uses ADR to constrain task breakdown
7. Standard planning workflow (phases, tasks, dependencies)
8. Plan document includes ADR as appendix
9. Exits plan mode → hands off to horde-implement
```

## When to Use

**Use this skill when:**
- Starting any new feature implementation (3+ tasks)
- Complex refactoring that spans multiple files
- System design or architecture work
- Multi-phase development work
- Work that benefits from task tracking

**Don't use when:**
- Single-line fixes or trivial changes
- Simple one-file additions
- Questions about existing code
- Exploratory work (use horde-brainstorming instead)

**Decision Flow:**
```
Is this a multi-step implementation task?
├── Yes → Use horde-plan
│   └── Score complexity (see Complexity Scoring below)
│       ├── Score < 15 → Fast plan (single-agent, current workflow)
│       ├── Score 15-30 → Offer validated plan (Adversarial Debate, 2-3 agents)
│       ├── Score 31-50 → Recommend validated plan (Consensus Deliberation, 3-4 agents)
│       └── Score 51+ → Strongly recommend validated plan + hierarchical decomposition
└── No → Can you do it directly?
    ├── Yes → Do it now
    └── No → Use horde-brainstorming first
```

## When to Use vs Alternatives

| Skill | Use When | Key Difference |
|-------|----------|----------------|
| **horde-plan** (this skill) | Creating implementation plans with task tracking | Uses EnterPlanMode, hands off to horde-implement |
| **horde-implement** | Executing an implementation plan | Uses senior-prompt-engineer + subagent-driven-development |
| **horde-brainstorming** | Exploring multiple approaches before planning | Research and options generation, not structured planning |
| **writing-plans** | Writing detailed step-by-step plans | Focuses on bite-sized TDD steps, less task tracking |

## Plan Output Contract (horde-implement compatibility)

**Every plan produced by horde-plan MUST follow this format** to ensure zero-friction parsing by horde-implement's Plan Parser.

### Required Heading Levels

```
# {Plan Title}                          ← H1: Document title
## Phase {id}: {name}                   ← H2: Phase headers (id: -1, 0, 1, 1.5, 2, ...)
### Task {phase_id}.{n}: {name}         ← H3: Task headers (1.1, 1.2, 1.5.1, ...)
### Exit Criteria Phase {id}            ← H3: Exit criteria per phase (checkbox items)
### Appendix {letter}: {name}           ← H3: Reference appendices (A, B, C, ...)
```

**WRONG**: `### Phase 1:` (h3) / `#### Task 1.1:` (h4) — parser won't find phases.
**RIGHT**: `## Phase 1:` (h2) / `### Task 1.1:` (h3) — matches parser regex.

### Required Phase Metadata

After every phase header:
```markdown
## Phase 1: Core Implementation
**Duration**: 2-3 hours
**Dependencies**: Phase 0
**Parallelizable**: Yes (Tasks 1.1-1.3 independent)
```

### Required Exit Criteria

Every phase MUST end with exit criteria:
```markdown
### Exit Criteria Phase 1
- [ ] All API endpoints return 200 on health check
- [ ] Database migrations applied successfully
- [ ] Unit tests pass with >80% coverage
```

Use verifiable language: "returns", "responds", "exists", "passes" — not "looks good" or "seems correct".

### Task Content for Type Classification

horde-implement auto-classifies tasks by content. Ensure tasks contain:

| Task Type | Required Content | Example |
|-----------|-----------------|---------|
| `bash` | ` ```bash ` code block with commands | `pip install`, `railway up` |
| `code_write` | File path + ` ```python/js/ts ` code block | `# src/models/user.py` |
| `config` | Env var format or config file content | `DATABASE_URL=...` |
| `browser` | URL + navigation steps | `Navigate to https://...` |
| `verify` | Command + `Expected:` pattern | `curl ... # Expected: 200` |
| `human_required` | Explicit `**HUMAN_REQUIRED**` marker | Account creation, CAPTCHA |

**WRONG**: "Set up the database" — no code block, unclassifiable.
**RIGHT**: Task with ````bash\nrails db:migrate\n```\n` — classified as `bash`.

### Gate Depth Signals

Between phases, gate depth is inferred from content. Help the parser:

| Signal | Gate Depth | How to Signal |
|--------|-----------|---------------|
| Phase N creates code, N+1 deploys it | `DEEP` | Exit criteria reference deployment |
| Phase N exports schema, N+1 imports it | `STANDARD` | Task references files from prior phase |
| Phases work on different subsystems | `LIGHT` | `**Dependencies**: None` |
| Phase is purely verification | `NONE` | All tasks are `verify` type |

### YAML Frontmatter Plan Manifest

Every plan document MUST begin with a machine-readable manifest:

```yaml
---
plan_manifest:
  version: "1.0"
  created_by: "horde-plan"
  plan_name: "Feature Name"
  total_phases: 5
  total_tasks: 14
  phases:
    - id: "1"
      name: "Database & Models"
      task_count: 3
      parallelizable: false
      gate_depth: "STANDARD"
    - id: "2"
      name: "Backend API"
      task_count: 4
      parallelizable: true
      gate_depth: "LIGHT"
  task_transfer:
    mode: "transfer"
    task_ids: []  # populated with TaskCreate IDs after planning
---
```

**Fallback resilience:** If frontmatter is missing, horde-implement falls back to markdown parsing. But frontmatter saves ~1500 tokens by eliminating re-discovery.

### Validation Checklist (run before ExitPlanMode)

- [ ] All phase headers use `## Phase {id}:` format
- [ ] All task headers use `### Task {id}.{n}:` format
- [ ] Every phase has `### Exit Criteria Phase {id}` with checkboxes
- [ ] Every task contains code blocks, URLs, or explicit action verbs
- [ ] Duration and Dependencies on every phase
- [ ] YAML frontmatter plan_manifest present
- [ ] Appendices use `### Appendix {letter}:` format

---

## Pre-Flight Confirmation

Before entering plan mode, present confirmation based on complexity:

**Simple Plan** (3-5 tasks, single file/component):
```
[⚠] Entering Plan Mode

I'll create an implementation plan for: [brief description]

Estimated tasks: 3-5
Estimated phases: 1-2
Complexity: Low

Press Enter to continue or Ctrl+C to cancel.
```

**Moderate Plan** (6-15 tasks, multiple files):
```
[⚠⚠] Entering Plan Mode

I'll create an implementation plan for: [brief description]

Estimated tasks: 6-15
Estimated phases: 2-4
Complexity: Medium
Integration points: [list]

Type 'yes' to continue or 'no' to cancel.
```

**Complex Plan** (15+ tasks, cross-cutting concerns):
```
[⚠⚠⚠] Entering Plan Mode - COMPLEX WORK

I'll create an implementation plan for: [brief description]

Estimated tasks: 15+
Estimated phases: 4-8
Complexity: High (score: [N])

Areas affected:
- [Component 1]
- [Component 2]
- [Database/API/etc.]

Planning options:
1. Fast plan (5-10 min) - Single-agent analysis
2. Validated plan (8-15 min) - Multi-agent architecture deliberation
   Agents will debate the architecture approach before task breakdown.
   Produces an Architecture Decision Record (ADR) as plan appendix.

I recommend option 2 for this level of complexity.

Type '1' for fast, '2' for validated, or 'no' to cancel.
```

**Auto-Validated** (triggers detected: compliance, financial, security, migration):
```
[⚠⚠⚠] Entering Plan Mode - HIGH-STAKES WORK

I'll create an implementation plan for: [brief description]

Detected: [HIPAA compliance / financial transactions / security-critical / data migration]

This project has high-risk characteristics. I strongly recommend
validated planning with golden-horde deliberation:
- [Domain specialist 1] validates [concern 1]
- [Domain specialist 2] validates [concern 2]
- Architecture Decision Record (ADR) produced before task breakdown

Estimated time: 10-15 minutes
Alternative: Fast plan in 5 minutes (you validate architecture yourself)

Type 'validated' to proceed with deliberation, 'fast' for single-agent, or 'no' to cancel.
```

## The Horde Plan Workflow

### Phase 1: Enter Plan Mode

Use the EnterPlanMode tool to signal planning state:

```
I'm using horde-plan to create an implementation plan.

[Directory check: Ensuring docs/plans/ directory exists...]

[EnterPlanMode invoked]
```

**Pre-planning validation:**
- Verify `docs/plans/` directory exists, create if needed
- Check write permissions
- Generate unique filename with timestamp if collision detected

### Phase 2: Requirements Analysis

Before writing the plan, understand what needs to be built:

1. **Identify the core requirement** - What is being built?
2. **Gather context** - Read relevant files, understand existing patterns
3. **Identify constraints** - Technology choices, time constraints, dependencies
4. **Ask clarifying questions** if requirements are ambiguous

**Clarification Questions Template:**
```
Before I create the plan, I need to understand:

1. **Scope**: Should this include [X feature] or just [Y core]?
2. **Integration**: Does this need to integrate with [existing system]?
3. **Priority**: Is [feature A] more important than [feature B]?
4. **Constraints**: Any specific technologies or patterns to follow?

You can answer now or I'll make reasonable assumptions.
```

### Phase 2.5: Complexity Scoring & Pre-Planning Deliberation (NEW)

After requirements analysis (Phase 2), score the project's complexity to decide whether to invoke golden-horde deliberation before task breakdown.

#### Complexity Scoring

Score the project based on these factors:

```
Complexity Score Calculation:
  Base: min(estimated_task_count, 50)
  + (number_of_subsystems × 3)
  + (number_of_hard_dependencies)
  + (10 if security_requirements)
  + (8 if compliance_requirements: HIPAA, PCI-DSS, SOC2, GDPR)
  + (12 if novel_architecture: new patterns, unfamiliar tech)
  + (8 if multi_team_coordination)
  + (6 if data_migration)

Thresholds:
  0-14:  Low    → Fast plan (single-agent, skip to Phase 3)
  15-30: Medium → Offer Adversarial Debate (2 advocates + 1 judge)
  31-50: High   → Recommend Consensus Deliberation (3-4 experts)
  51+:   Very High → Strongly recommend Consensus + hierarchical decomposition
```

**Auto-detect triggers** (override score to >= 30 regardless of calculated score):
- Keywords: HIPAA, PCI-DSS, SOC2, GDPR, "compliance", "regulatory"
- Financial: "payment", "billing", "transaction", "fintech"
- Migration: "migrate from", "rewrite", "monolith to microservices"
- User explicit: `--validated` flag

**Skip deliberation when:**
- User says "fast" or "quick plan"
- Score < 15 (trivial complexity)
- Requirements specify exact technology (no architecture decision needed)
- Incremental feature on established patterns

#### Pre-Planning Deliberation Workflow

When the user opts into (or score triggers) validated planning:

**Step 1: Identify the Architecture Question**

Extract the core decision that needs deliberation:
```
Architecture question: "What approach should we use for [X]?"

Examples:
- "WebSocket vs SSE vs polling for real-time sync?"
- "Monolith vs microservices for this scale?"
- "PostgreSQL vs DynamoDB for the event store?"
- "JWT vs session-based auth with this security profile?"
```

If there's no clear A-vs-B decision, frame it as: "What architecture best satisfies [constraint 1], [constraint 2], and [constraint 3]?"

**Step 2: Select Golden-Horde Pattern**

| Architecture Question Type | Pattern | Team Composition |
|---|---|---|
| Technology A vs B | Adversarial Debate | 2 domain specialists (advocate each side) + 1 senior architect (judge) |
| Multi-constraint decision (security + cost + perf) | Consensus Deliberation | 3 specialists (one per constraint domain) |
| Frontend/backend API boundary | Contract-First Negotiation | `frontend-developer` + `backend-architect` |
| Unknown scope ("how should we approach this?") | Consensus Deliberation | 3 generalists with different domain lenses |

**Step 3: Dispatch Golden-Horde Team**

Spawn the deliberation team using Task() subagent dispatch. Each agent gets the requirements context from Phase 2 plus their role-specific instructions.

**Adversarial Debate (for A-vs-B decisions):**
```python
# Advocate for Position A
Task(
    subagent_type="backend-development:backend-architect",  # or domain-appropriate
    description="Advocate for [Position A]",
    prompt="""You are an advocate in an architecture debate BEFORE implementation planning.

CONTEXT: [Requirements from Phase 2]
QUESTION: [Architecture question]

YOUR POSITION: Argue FOR [Position A].
Make the strongest possible case considering:
1. Technical fit for these specific requirements
2. Scalability and performance implications
3. Development velocity and team familiarity
4. Operational complexity and maintenance cost
5. Security implications

You MUST be specific to this project's requirements, not generic.
Output: A structured argument (max 500 words) with evidence.
Do NOT use the Task tool. Work independently and return your results."""
)

# Advocate for Position B
Task(
    subagent_type="backend-development:backend-architect",  # or domain-appropriate
    description="Advocate for [Position B]",
    prompt="""[Same structure, arguing FOR Position B]"""
)

# Judge
Task(
    subagent_type="general-purpose",
    description="Judge architecture debate",
    prompt="""You are the judge in an architecture debate BEFORE implementation planning.

CONTEXT: [Requirements from Phase 2]
QUESTION: [Architecture question]

You will receive two arguments shortly. Wait for both, then:
1. For each contested point, state which side won and why
2. Identify points both sides agree on
3. Issue a clear RULING with the chosen approach
4. Note any conditions or caveats

Your ruling will become the Architecture Decision Record (ADR) for this project.
No vague compromises. Pick a winner and justify it.
Do NOT use the Task tool. Work independently and return your results."""
)
```

**Consensus Deliberation (for multi-constraint decisions):**
```python
# Expert per constraint domain
Task(
    subagent_type="security-auditor",
    description="Security perspective on architecture",
    prompt="""You are a security expert evaluating architecture options BEFORE planning.

CONTEXT: [Requirements from Phase 2]
QUESTION: [Architecture question]

Provide your independent analysis:
1. Security implications of each approach
2. Compliance requirements and how each approach satisfies them
3. Attack surface comparison
4. Your recommended approach from a security perspective

Be specific to this project. Max 400 words.
Do NOT use the Task tool."""
)

Task(
    subagent_type="backend-development:backend-architect",
    description="Performance/scalability perspective",
    prompt="""[Same structure, from performance lens]"""
)

Task(
    subagent_type="general-purpose",
    description="Cost/operations perspective",
    prompt="""[Same structure, from cost/ops lens]"""
)
```

After all agents return, the orchestrator (horde-plan session) synthesizes their findings into a unified ADR.

**Step 4: Produce Architecture Decision Record (ADR)**

```markdown
## Architecture Decision Record

> **Decision:** [Chosen approach]
> **Status:** Approved by [N]-agent [pattern name]
> **Confidence:** [High/Medium/Low based on agent agreement]
> **Date:** [YYYY-MM-DD]

### Context
[1-2 sentences from requirements]

### Decision
[The chosen architecture approach, 2-3 sentences]

### Rationale
[Key arguments that won, referencing agent findings]

### Alternatives Considered
| Alternative | Why Not |
|---|---|
| [Option B] | [Key reasons from debate/deliberation] |

### Consequences
- [Positive consequence 1]
- [Positive consequence 2]
- [Risk/tradeoff to monitor]

### Dissenting Views
[Any unresolved disagreements, if applicable]
```

**Step 5: User Approves ADR**

Present the ADR to the user BEFORE entering plan mode:
```
Architecture deliberation complete.

[ADR content]

Accept this architecture and proceed with planning?
- 'yes' → Enter plan mode with ADR as constraint
- 'no' → Re-deliberate with different parameters
- 'fast' → Discard ADR, proceed with single-agent fast plan
```

**Step 6: Continue to Phase 3 (Task Breakdown)**

If user approves ADR, it becomes a hard constraint for task breakdown:
- Task breakdown MUST align with the chosen architecture
- ADR is included as appendix in the final plan document
- Plan template's "Architecture" field references the ADR

#### Deliberation Budget

| Pattern | Agents | Max Time | Token Budget |
|---|---|---|---|
| Adversarial Debate | 3 | 8 min | ~50k tokens |
| Consensus Deliberation | 3-4 | 10 min | ~80k tokens |
| Contract-First Negotiation | 2 | 6 min | ~35k tokens |

**Budget enforcement:** If deliberation exceeds budget, force synthesis from available agent outputs and present partial ADR with disclaimer.

**Fallback:** If golden-horde dispatch fails (agents don't return, context overflow), fall back to single-agent planning with a note: "Validated planning unavailable, proceeding with fast plan."

---

### Phase 3: Task Breakdown

Decompose the work into discrete, trackable tasks:

**Task Breakdown Principles:**
- **Each task = 30 minutes to 2 hours** of work
- **Tasks are independent** where possible (for parallel dispatch)
- **Each task has clear acceptance criteria**
- **Tasks map to phases** for logical grouping

**Task Structure Template (horde-implement compatible):**
```markdown
### Task {phase_id}.{n}: [Task Title]
**Dependencies**: None / Task M.N

[Task body — MUST contain content enabling automatic type classification:]

For bash tasks: include ```bash code blocks
For code tasks: include file path + ```python/js/ts code
For config tasks: include env var format or config file content
For browser tasks: include URLs + navigation steps
For verify tasks: include commands + Expected: patterns
For human tasks: include **HUMAN_REQUIRED** marker

**Files:**
- Create: `path/to/new/file.ext`
- Modify: `path/to/existing/file.ext`

**Acceptance Criteria:**
- [ ] Criterion 1 (verifiable: "returns 200", "file exists", "tests pass")
- [ ] Criterion 2
```

**Task Type Classification Guide:**

When writing task bodies, include the right content so horde-implement routes to the correct executor:

| Want This Type | Include in Task Body |
|---------------|---------------------|
| `bash` | ` ```bash\npip install ...\n``` ` — a bash code block |
| `code_write` | ` # src/models/user.py\n```python\n...\n``` ` — file path + code |
| `config` | ` DATABASE_URL=postgresql://... ` — env var or config format |
| `browser` | ` Navigate to https://railway.app/dashboard ` — URL + steps |
| `verify` | ` ```bash\ncurl .../health\n# Expected: 200\n``` ` — command + assertion |
| `human_required` | ` **HUMAN_REQUIRED**: Create account at ... ` — explicit marker |

**Why this matters:** horde-implement's Plan Parser classifies tasks by content. A task that says "set up the database" with no code block is unclassifiable and gets routed to a generic agent. A task with `\`\`\`bash\nrails db:migrate\n\`\`\`` is classified as `bash` and routed to a Bash-capable executor.

**Standard Phases:**
1. **Phase 1: Setup & Foundation** - Project structure, dependencies, base configuration
2. **Phase 2: Core Implementation** - Main feature work
3. **Phase 3: Integration** - Connecting components
4. **Phase 4: Testing** - Test coverage and validation
5. **Phase 5: Documentation** - Docs, examples, guides
6. **Phase 6: Deployment** - Deploy configuration, migration

### Phase 4: Dependency Mapping

Use TaskCreate with dependency tracking:

```python
TaskCreate(
    subject="Create authentication API endpoint",
    description="Implement POST /api/auth/login with JWT tokens",
    activeForm="Creating authentication endpoint"
)
# Returns: taskId

# For dependent tasks:
TaskCreate(
    subject="Add token refresh logic",
    description="Implement token refresh endpoint",
    activeForm="Adding token refresh",
    addBlockedBy=["<taskId from auth endpoint>"]
)
```

**Dependency Mapping Rules:**
- **addBlockedBy** = tasks that MUST complete first
- **addBlocks** = tasks that depend on this one
- Minimize dependencies for maximum parallelism
- Only track HARD dependencies (not just ordering preferences)

### Phase 5: Plan Document Generation

Create the plan document following the **Plan Output Contract** above. The document MUST be parseable by horde-implement's Plan Parser.

**Plan Template:**
```markdown
---
plan_manifest:
  version: "1.0"
  created_by: "horde-plan"
  plan_name: "[Feature Name]"
  total_phases: N
  total_tasks: N
  phases:
    - id: "0"
      name: "Setup & Foundation"
      task_count: N
      parallelizable: false
      gate_depth: "LIGHT"
    - id: "1"
      name: "Core Implementation"
      task_count: N
      parallelizable: true
      gate_depth: "STANDARD"
    # ... one entry per phase
  task_transfer:
    mode: "transfer"
    task_ids: []  # populated after TaskCreate calls
---

# [Feature Name] Implementation Plan

> **Plan Status:** Draft
> **Created:** YYYY-MM-DD
> **Estimated Tasks:** N
> **Estimated Phases:** N

## Overview

**Goal:** [One sentence description]

**Architecture:** [2-3 sentence approach]

**Tech Stack:** [Key technologies]

## Phase 0: Setup & Foundation
**Duration**: 30-60 minutes
**Dependencies**: None
**Parallelizable**: No (sequential setup)

### Task 0.1: [Task Title]
**Dependencies**: None

[Description with appropriate content for type classification:]
```bash
# Include bash blocks for CLI tasks
pip install -r requirements.txt
```

**Files:**
- Create: `path/to/new/file.ext`
- Modify: `path/to/existing/file.ext`

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### Task 0.2: [Task Title]
**Dependencies**: Task 0.1

[Task content with code blocks, file paths, or URLs for type classification]

### Exit Criteria Phase 0
- [ ] Dependencies installed successfully
- [ ] Configuration files created and validated
- [ ] Development server starts without errors

## Phase 1: Core Implementation
**Duration**: 2-4 hours
**Dependencies**: Phase 0
**Parallelizable**: Yes (Tasks 1.1-1.3 independent)

### Task 1.1: [Task Title]
**Dependencies**: None

```python
# src/models/user.py — include code for code_write classification
class User(BaseModel):
    id: int
    email: str
```

**Files:**
- Create: `src/models/user.py`

**Acceptance Criteria:**
- [ ] Model validates input correctly
- [ ] Tests pass

### Task 1.2: [Another Task]
**Dependencies**: None

[Content with URLs for browser classification, or verification commands]
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Exit Criteria Phase 1
- [ ] All API endpoints return 200 on health check
- [ ] Database migrations applied successfully
- [ ] Unit tests pass with >80% coverage

## Phase 2: [Phase Name]
**Duration**: [estimate]
**Dependencies**: Phase 1
**Parallelizable**: [Yes/No]

[... same structure: tasks with content for type classification, exit criteria ...]

### Exit Criteria Phase 2
- [ ] [Verifiable criterion]
- [ ] [Verifiable criterion]

## Dependency Graph

```
Phase 0 (Setup)
    ├── Phase 1 (Core) — gate: STANDARD
    │   ├── Phase 2 (Integration) — gate: STANDARD
    │   └── Phase 3 (Testing) — gate: LIGHT
    └── Phase 4 (Documentation) — gate: NONE, can run parallel
```

### Appendix A: Architecture Decision Record (if validated planning was used)

> **Decision:** [Chosen approach]
> **Validated by:** [N]-agent [pattern name] deliberation
> **Confidence:** [High/Medium/Low]

[Full ADR content from Phase 2.5]

### Appendix B: [Additional Reference Material]

[Schemas, configs, or context referenced by tasks]

## Approval

- [ ] Plan Output Contract validated (heading levels, exit criteria, task content)
- [ ] Requirements understood
- [ ] Architecture validated (if ADR present)
- [ ] Task breakdown acceptable
- [ ] Dependencies correct
- [ ] Ready for execution via horde-implement

**Ready to proceed?** Use ExitPlanMode to approve.
```

**Save location:** `docs/plans/YYYY-MM-DD-[feature-name].md`

### Phase 6: Exit Plan Mode

Present plan for user approval using ExitPlanMode:

```
[ExitPlanMode invoked with:
- allowedPrompts for any bash commands during implementation
- pushToRemote if deployment is included
]

Plan complete! Here's what I'll build:

**Summary:** [2-3 sentence overview]
**Tasks:** N total across N phases
**Estimated effort:** [Time estimate]

**Next Steps:**
1. Review the plan above
2. If approved, I'll use horde-implement to execute
3. Each task will have review gates before proceeding
4. Progress tracked via TaskList throughout

Shall I proceed with execution?
```

## Structured Handoff to Horde-Implement

After plan approval, the skill performs a **structured handoff** to `horde-implement` Path B (Execute mode). This eliminates re-discovery overhead — horde-implement receives a pre-parsed plan with full metadata.

### Handoff Protocol

**Step 1: Update plan manifest with TaskCreate IDs**

After all tasks are created via TaskCreate during planning, update the YAML frontmatter:

```python
# After all TaskCreate calls, collect IDs
task_ids = [task1_id, task2_id, task3_id, ...]

# Update the plan_manifest.task_transfer.task_ids in the saved plan file
# (edit the YAML frontmatter to include actual task IDs)
```

**Step 2: Invoke horde-implement with structured prompt**

```
User: "Yes, proceed"

Claude:
Skill("horde-implement", """
Execute this plan via Path B (existing plan document).

Plan: docs/plans/YYYY-MM-DD-[feature].md
Entry: Path B (structured markdown with YAML frontmatter plan_manifest)

The plan includes:
- YAML frontmatter with phase index, gate depths, and task transfer IDs
- {N} phases with ## Phase headers
- {N} tasks with ### Task headers and typed content (bash/code/config/browser/verify)
- Exit criteria per phase (### Exit Criteria Phase {id})
- Dependency graph with gate depth annotations

Task transfer mode: transfer
TaskCreate IDs from planning: {task_ids}
These tasks can be claimed via TaskUpdate(taskId=X, owner="horde-implement", status="in_progress")

Proceed with phase-by-phase execution, gate testing, and post-execution pipeline.
""")
```

**Step 3: Task state transfer**

horde-implement **reuses** tasks created during planning (transfer mode):
- Claims ownership: `TaskUpdate(taskId=X, owner="horde-implement")`
- Updates status as work progresses
- Preserves lineage from planning → execution → review

**Why not Path A?** horde-plan already generated the plan. Invoking Path A would redundantly call senior-prompt-engineer to generate another plan. Always use Path B when horde-plan produced the plan.

### Handoff Announcement Template

```
Handing off to horde-implement (Path B: Execute)...

**Plan:** `docs/plans/YYYY-MM-DD-[feature].md`
**Phases:** N (gate depths: {DEEP: 1, STANDARD: 2, LIGHT: 1, NONE: 1})
**Tasks:** N (types: {bash: 4, code_write: 6, config: 2, verify: 2})
**Task IDs:** {list of TaskCreate IDs for transfer}

horde-implement will:
1. Parse plan manifest from YAML frontmatter (skip re-discovery)
2. Claim transferred tasks via TaskUpdate
3. Execute phases with gate testing at STANDARD/DEEP boundaries
4. Run post-execution: implementation-status → horde-test → horde-review
```

### Fallback

If horde-implement is not available or invocation fails:
1. Present the plan document path to the user
2. Suggest: "Run `/implement docs/plans/YYYY-MM-DD-[feature].md` in a new session"
3. Plan is self-contained — YAML frontmatter is optional (horde-implement falls back to markdown parsing)

## Task Domain Routing

When breaking down tasks, identify domains for specialist routing:

**For direct skill invocation (via `Skill()` tool):**

| Domain | Keywords | Skills to Invoke |
|--------|----------|------------------|
| Backend | API, endpoint, database, schema | `senior-backend` |
| Frontend | component, UI, React | `senior-frontend` |
| DevOps | deploy, Docker, CI/CD | `senior-devops` |
| Data | pipeline, ETL, analytics | `senior-data-engineer` |
| Security | auth, permissions, encryption | `security-auditor` (if available) |
| Code Review | review, quality, audit | `code-reviewer` |

**For Task subagent dispatch (via `subagent-driven-development`):**

| Domain | Keywords | Subagent Type for Task() |
|--------|----------|-------------------------|
| Backend | API, endpoint, database, schema | `backend-development:backend-architect` |
| Frontend | component, UI, React | `frontend-mobile-development:frontend-developer` |
| DevOps | deploy, Docker, CI/CD | `senior-devops` (as skill) |
| Data | pipeline, ETL, analytics | `senior-data-engineer` (as skill) |

**Key distinction:**
- **Skills** are invoked directly via `Skill("skill-name", "prompt")` during planning
- **Subagent types** are used by `subagent-driven-development` via `Task(subagent_type="domain:agent", ...)` during execution

## Quality Checks

Before exiting plan mode, verify against the **Plan Output Contract**:

- [ ] **Heading levels correct** - Phases are `##`, tasks are `###`, exit criteria are `###`
- [ ] **YAML frontmatter present** - plan_manifest with phase index and gate depths
- [ ] **Exit criteria per phase** - Every phase has `### Exit Criteria Phase {id}` with checkboxes
- [ ] **Task content typed** - Every task has code blocks, URLs, or explicit markers for type classification
- [ ] **Duration/Dependencies on phases** - Every phase has `**Duration**` and `**Dependencies**`
- [ ] **Complete breakdown** - All work is captured in tasks
- [ ] **Clear acceptance** - Each task has verifiable success criteria
- [ ] **Reasonable dependencies** - Dependencies are real, not artificial
- [ ] **File paths specified** - Implementation knows where to work
- [ ] **Test coverage planned** - Testing is explicit in tasks

## Common Patterns (horde-implement compatible)

### Pattern 1: CRUD Feature

```markdown
## Phase 1: Database Schema
**Duration**: 30-60 minutes
**Dependencies**: None
**Parallelizable**: No

### Task 1.1: Create table migration
**Dependencies**: None
```bash
alembic revision --autogenerate -m "add_users_table"
```
### Task 1.2: Create model definitions
**Dependencies**: Task 1.1
```python
# src/models/user.py
class User(Base):
    __tablename__ = "users"
```

### Exit Criteria Phase 1
- [ ] Migration applies without errors
- [ ] Model imports successfully

## Phase 2: Backend API
**Duration**: 1-2 hours
**Dependencies**: Phase 1
**Parallelizable**: Yes (Tasks 2.1-2.3 independent)

### Task 2.1: Create endpoint
### Task 2.2: Add validation
### Task 2.3: Add error handling

### Exit Criteria Phase 2
- [ ] All endpoints return correct status codes
- [ ] Validation rejects invalid input

## Phase 3: Frontend Integration
**Duration**: 1-2 hours
**Dependencies**: Phase 2
**Parallelizable**: Yes

### Task 3.1: Create API client
### Task 3.2: Build UI components
### Task 3.3: Connect to state

### Exit Criteria Phase 3
- [ ] UI renders profile data from API
- [ ] Form submission updates backend

## Phase 4: Testing
**Duration**: 1 hour
**Dependencies**: Phase 2, Phase 3
**Parallelizable**: Yes

### Task 4.1: Unit tests
### Task 4.2: Integration tests
### Task 4.3: E2E tests

### Exit Criteria Phase 4
- [ ] All tests pass
- [ ] Coverage >80%
```

### Pattern 2: Infrastructure Work

```markdown
## Phase 1: Planning
**Duration**: 30 minutes
**Dependencies**: None

### Task 1.1: Design architecture
### Task 1.2: Create diagrams

### Exit Criteria Phase 1
- [ ] Architecture diagram reviewed

## Phase 2: Implementation
**Duration**: 2-3 hours
**Dependencies**: Phase 1

### Task 2.1: Configure services
### Task 2.2: Set up networking
### Task 2.3: Add monitoring

### Exit Criteria Phase 2
- [ ] Services responding on expected ports
- [ ] Monitoring dashboard shows metrics

## Phase 3: Validation
**Duration**: 1 hour
**Dependencies**: Phase 2

### Task 3.1: Test failover
### Task 3.2: Load testing
### Task 3.3: Security review

### Exit Criteria Phase 3
- [ ] Failover completes in <30s
- [ ] Load test sustains target RPS
```

### Pattern 3: Refactoring

```markdown
## Phase 1: Analysis
**Duration**: 30 minutes
**Dependencies**: None

### Task 1.1: Map current structure
### Task 1.2: Identify coupling points

### Exit Criteria Phase 1
- [ ] Dependency graph documented

## Phase 2: Refactor
**Duration**: 1-2 hours
**Dependencies**: Phase 1

### Task 2.1: Extract module
### Task 2.2: Update imports
### Task 2.3: Add tests

### Exit Criteria Phase 2
- [ ] Existing tests still pass
- [ ] New module imports cleanly

## Phase 3: Verification
**Duration**: 30 minutes
**Dependencies**: Phase 2

### Task 3.1: Run existing tests
### Task 3.2: Add new tests
### Task 3.3: Performance comparison

### Exit Criteria Phase 3
- [ ] No performance regression >5%
- [ ] All tests pass
```

## Example Output (horde-implement compatible)

**User:** "/horde-plan Add user profile management with avatar uploads"

**Claude:**

```
I'm using horde-plan to create an implementation plan.

[⚠⚠] Entering Plan Mode

I'll create an implementation plan for: User Profile Management with Avatar Uploads

Estimated tasks: 12-15
Estimated phases: 5
Complexity: Medium (score: 18)

Integration points:
- User authentication (existing)
- Database (PostgreSQL)
- Object storage (S3-compatible)
- Profile API endpoints
- Avatar upload UI

Planning options:
1. Fast plan (5-10 min) - Single-agent analysis
2. Validated plan (8-15 min) - Multi-agent architecture deliberation

Type '1' for fast, '2' for validated, or 'no' to cancel.

[User: 1]

---
plan_manifest:
  version: "1.0"
  created_by: "horde-plan"
  plan_name: "User Profile Management"
  total_phases: 5
  total_tasks: 14
  phases:
    - id: "1"
      name: "Database & Models"
      task_count: 3
      parallelizable: false
      gate_depth: "STANDARD"
    - id: "2"
      name: "Backend API"
      task_count: 4
      parallelizable: true
      gate_depth: "STANDARD"
    - id: "3"
      name: "Storage Integration"
      task_count: 2
      parallelizable: true
      gate_depth: "LIGHT"
    - id: "4"
      name: "Frontend UI"
      task_count: 3
      parallelizable: true
      gate_depth: "LIGHT"
    - id: "5"
      name: "Testing & Docs"
      task_count: 2
      parallelizable: true
      gate_depth: "NONE"
  task_transfer:
    mode: "transfer"
    task_ids: []
---

# User Profile Management Implementation Plan

> **Plan Status:** Draft
> **Created:** 2026-02-04
> **Estimated Tasks:** 14
> **Estimated Phases:** 5

## Overview

**Goal:** Add user profile management with avatar upload capability to existing auth system.

**Architecture:** Extend existing User model with profile fields, add profile endpoints, implement S3-based avatar storage, create profile management UI.

**Tech Stack:** FastAPI, PostgreSQL, MinIO/S3, React, Dropzone

## Phase 1: Database & Models
**Duration**: 45-60 minutes
**Dependencies**: None
**Parallelizable**: No (sequential migrations)

### Task 1.1: Extend User Schema
**Dependencies**: None

Add profile fields to users table:
```bash
alembic revision --autogenerate -m "add_profile_fields"
alembic upgrade head
```

**Files:**
- Create: `migrations/002_add_profile_fields.sql`
- Modify: `src/models/user.py`

**Acceptance Criteria:**
- [ ] display_name, bio, location columns added
- [ ] Avatar URL column added
- [ ] Migration runs successfully

### Task 1.2: Create Pydantic Models
**Dependencies**: Task 1.1

Request/response schemas for profile data:
```python
# src/schemas/profile.py
class UserProfileCreate(BaseModel):
    display_name: str = Field(max_length=100)
    bio: Optional[str] = None
    location: Optional[str] = None
```

**Files:**
- Create: `src/schemas/profile.py`

**Acceptance Criteria:**
- [ ] UserProfileCreate schema validates input
- [ ] UserProfileResponse schema serializes output
- [ ] AvatarUploadResponse includes URL

### Task 1.3: Add Repository Layer
**Dependencies**: Task 1.2

Database access methods for profiles:
```python
# src/repositories/profile.py
class ProfileRepository:
    async def get_profile(self, user_id: int) -> UserProfile: ...
    async def update_profile(self, user_id: int, data: dict) -> UserProfile: ...
```

**Files:**
- Create: `src/repositories/profile.py`

**Acceptance Criteria:**
- [ ] get_profile() returns profile or raises NotFound
- [ ] update_profile() persists changes
- [ ] Tests pass for repository methods

### Exit Criteria Phase 1
- [ ] `alembic upgrade head` completes without errors
- [ ] `python -c "from src.models.user import User"` succeeds
- [ ] Profile schema validates sample input correctly

## Phase 2: Backend API
**Duration**: 1-2 hours
**Dependencies**: Phase 1
**Parallelizable**: Yes (Tasks 2.1-2.3 independent after 1.3)

### Task 2.1: GET Profile Endpoint
**Dependencies**: Task 1.3

```python
# src/api/v1/profile.py
@router.get("/api/v1/profile", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return await profile_repo.get_profile(current_user.id)
```

**Files:**
- Create: `src/api/v1/profile.py`

**Acceptance Criteria:**
- [ ] GET /api/v1/profile returns user profile
- [ ] Returns 404 if profile doesn't exist
- [ ] Requires authentication (401 without token)

### Task 2.2: PATCH Profile Endpoint
**Dependencies**: Task 2.1

```python
@router.patch("/api/v1/profile", response_model=UserProfileResponse)
async def update_profile(data: UserProfileCreate, ...):
    return await profile_repo.update_profile(current_user.id, data.dict())
```

**Files:**
- Modify: `src/api/v1/profile.py`

**Acceptance Criteria:**
- [ ] PATCH /api/v1/profile updates allowed fields
- [ ] Validation rejects display_name > 100 chars
- [ ] Returns updated profile

### Task 2.3: Avatar Upload Endpoint
**Dependencies**: Task 2.2

```python
@router.post("/api/v1/profile/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    # Validate type and size, store in S3
    ...
```

**Files:**
- Modify: `src/api/v1/profile.py`
- Create: `src/services/storage.py`

**Acceptance Criteria:**
- [ ] POST /api/v1/profile/avatar accepts image upload
- [ ] Rejects non-image files (validates Content-Type)
- [ ] Rejects files > 5MB
- [ ] Returns URL of stored avatar

### Task 2.4: Avatar Deletion
**Dependencies**: Task 2.3

```python
@router.delete("/api/v1/profile/avatar")
async def delete_avatar(current_user: User = Depends(get_current_user)):
    await storage.delete(current_user.avatar_key)
    ...
```

**Files:**
- Modify: `src/api/v1/profile.py`

**Acceptance Criteria:**
- [ ] DELETE /api/v1/profile/avatar removes avatar
- [ ] S3 object deleted
- [ ] Profile reverts to default avatar URL

### Exit Criteria Phase 2
- [ ] `curl -H "Authorization: Bearer $TOKEN" localhost:8000/api/v1/profile` returns 200
- [ ] All 4 endpoints respond with correct status codes
- [ ] Invalid requests return proper error responses

## Phase 3: Storage Integration
**Duration**: 30-60 minutes
**Dependencies**: None (can run parallel to Phase 2)
**Parallelizable**: Yes

### Task 3.1: Configure S3 Client
**Dependencies**: None

```python
# src/config/storage.py
S3_BUCKET = os.getenv("S3_BUCKET", "avatars")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
```

**Files:**
- Create: `src/config/storage.py`

**Acceptance Criteria:**
- [ ] S3 client configured from env vars
- [ ] Bucket existence check on startup
- [ ] Presigned URL generation works

### Task 3.2: Image Processing Pipeline
**Dependencies**: None

```python
# src/services/images.py
from PIL import Image
def resize_avatar(image_bytes: bytes, sizes=[64, 128, 256]) -> dict:
    ...
```

**Files:**
- Create: `src/services/images.py`

**Acceptance Criteria:**
- [ ] Resizes to standard sizes (64, 128, 256)
- [ ] Converts to WebP with JPEG fallback
- [ ] Strips EXIF data for privacy

### Exit Criteria Phase 3
- [ ] S3 client connects to MinIO without errors
- [ ] Image resize produces correct dimensions
- [ ] EXIF stripping verified on test image

## Phase 4: Frontend UI
**Duration**: 1-2 hours
**Dependencies**: Phase 2
**Parallelizable**: Yes

### Task 4.1: Profile Page Layout
**Dependencies**: None

```tsx
// src/app/profile/page.tsx
export default function ProfilePage() {
  return <ProfileForm />;
}
```

**Files:**
- Create: `src/app/profile/page.tsx`
- Create: `src/app/profile/components/ProfileForm.tsx`

**Acceptance Criteria:**
- [ ] Form renders with display name, bio, location fields
- [ ] Avatar preview area visible
- [ ] Save/cancel buttons functional

### Task 4.2: Avatar Upload Component
**Dependencies**: Task 4.1

```tsx
// src/app/profile/components/AvatarUpload.tsx
import { useDropzone } from 'react-dropzone';
```

**Files:**
- Create: `src/app/profile/components/AvatarUpload.tsx`

**Acceptance Criteria:**
- [ ] Drag-drop upload zone renders
- [ ] Image preview before upload
- [ ] Progress indicator during upload
- [ ] Error messages on failure

### Task 4.3: API Client Integration
**Dependencies**: Task 4.2

```typescript
// src/lib/api/profile.ts
export async function getProfile(): Promise<UserProfile> { ... }
export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> { ... }
export async function uploadAvatar(file: File): Promise<{ url: string }> { ... }
```

**Files:**
- Create: `src/lib/api/profile.ts`
- Modify: `src/app/profile/page.tsx`

**Acceptance Criteria:**
- [ ] getProfile() fetches and displays current profile
- [ ] updateProfile() sends changes and shows success
- [ ] uploadAvatar() handles file upload with progress

### Exit Criteria Phase 4
- [ ] Profile page renders without console errors
- [ ] Form submission updates backend (verified via API)
- [ ] Avatar upload displays new image after completion

## Phase 5: Testing & Docs
**Duration**: 1-2 hours
**Dependencies**: Phase 2, Phase 3, Phase 4
**Parallelizable**: Yes

### Task 5.1: Test Coverage
**Dependencies**: None (after phase deps satisfied)

```bash
pytest tests/api/test_profile.py tests/services/test_images.py -v --cov=src
# Expected: All tests pass, coverage >80%
```

**Files:**
- Create: `tests/api/test_profile.py`
- Create: `tests/services/test_images.py`

**Acceptance Criteria:**
- [ ] API endpoint tests for all 4 routes
- [ ] Image processing unit tests
- [ ] Storage mock tests
- [ ] Coverage >80%

### Task 5.2: Documentation
**Dependencies**: None (after phase deps satisfied)

**Files:**
- Create: `docs/api/profile.md`
- Create: `docs/setup/avatar-storage.md`

**Acceptance Criteria:**
- [ ] OpenAPI spec documents all endpoints
- [ ] Setup instructions for S3/MinIO
- [ ] Example curl commands for each endpoint

### Exit Criteria Phase 5
- [ ] `pytest` exits with code 0
- [ ] Coverage report shows >80%
- [ ] Documentation files exist and are non-empty

## Dependency Graph

```
Phase 1 (Database) — gate: STANDARD
    ├── Phase 2 (API) — gate: STANDARD
    │   ├── Phase 4 (Frontend) — gate: LIGHT
    │   └── Phase 5 (Testing) — gate: NONE
    └── Phase 3 (Storage) — gate: LIGHT, independent
```

## Approval

- [ ] Plan Output Contract validated
- [ ] Requirements understood
- [ ] Task breakdown acceptable
- [ ] Dependencies correct
- [ ] Ready for execution via horde-implement

**Ready to proceed?** Use ExitPlanMode to approve.

---

[ExitPlanMode invoked]

Plan complete! Here's what I'll build:

**Summary:** User profile management system with avatar uploads, spanning database schema, REST API, S3 storage, and React UI.

**Tasks:** 14 total across 5 phases
**Gate depths:** STANDARD (Phase 1→2), STANDARD (Phase 2→4), LIGHT (Phase 3, 4), NONE (Phase 5)

Handing off to horde-implement (Path B: Execute)...

**Plan:** `docs/plans/2026-02-04-user-profile-management.md`
**Phases:** 5 (STANDARD: 2, LIGHT: 2, NONE: 1)
**Tasks:** 14 (code_write: 8, bash: 3, verify: 2, config: 1)
**Task transfer:** 14 TaskCreate IDs transferred

Shall I proceed with execution?
```

## Red Flags

**Never:**
- Skip dependency mapping (blocks parallel dispatch)
- Create tasks > 4 hours (break down further)
- Skip acceptance criteria (unclear when done)
- Forget file paths (implementer won't know where to work)
- Mix unrelated work in same task
- Skip testing phase

**Always:**
- Use EnterPlanMode before planning
- Use ExitPlanMode for approval
- Create tasks via TaskCreate for tracking
- Map dependencies with addBlockedBy
- Specify exact file paths
- Include testing in every plan
- Hand off to horde-implement

## Plan Revision Workflow

### Phase 7: Handle Plan Rejection

When the user rejects or requests changes to the plan:

1. **Understand the feedback:**
   - What specific aspects need revision?
   - Is it the scope, approach, task breakdown, or dependencies?
   - Are there constraints not previously considered?

2. **Revision template:**
   ```
   I understand you'd like changes to the plan. Please help me understand:

   1. **Scope**: Is the scope too large, too small, or misdirected?
   2. **Approach**: Should I use a different technical approach?
   3. **Tasks**: Are tasks too granular, too coarse, or missing?
   4. **Dependencies**: Did I miss or mis-map any dependencies?
   5. **Constraints**: Are there new constraints (time, technology, resources)?

   Please describe what needs to change or say "revise it" and I'll apply reasonable fixes.
   ```

3. **Revision process:**
   - Update the plan document based on feedback
   - Adjust task breakdown and dependencies as needed
   - Re-present the revised plan for approval
   - Allow up to 3 revision cycles before suggesting breaking into smaller pieces

4. **Major changes:**
   - If fundamental approach changes, consider using `horde-brainstorming` first
   - If scope changes dramatically, create a new plan rather than revising

## Troubleshooting

**Issue:** User says requirements changed during planning
**Fix:** Re-run Phase 2 analysis, update task breakdown

**Issue:** Task seems too large/small
**Fix:** Split into smaller tasks or merge related tasks

**Issue:** Too many dependencies (no parallelism possible)
**Fix:** Re-evaluate dependencies - some may be ordering preferences not hard dependencies

**Issue:** User rejects plan
**Fix:** Use Phase 7 revision workflow above

**Issue:** Plan revision fails after 3 cycles
**Fix:** Suggest breaking work into smaller, independent plans

## Validated Planning Examples

### Example: HIPAA-Compliant Telemedicine Platform

```
User: "/horde-plan --validated Build a HIPAA-compliant telemedicine platform"

Claude:
1. Requirements analysis → Score: 42 (HIPAA +8, novel architecture +12, 4 subsystems)
2. Auto-recommend validated planning

   [⚠⚠⚠] Entering Plan Mode - HIGH-STAKES WORK
   Detected: HIPAA compliance
   Recommending validated planning with:
   - Healthcare compliance specialist
   - Security architect
   - Cloud infrastructure expert
   Estimated time: 10-15 minutes
   Type 'validated' to proceed...

3. User: "validated"

4. Dispatches golden-horde Consensus Deliberation:
   - Task(subagent_type="security-auditor", prompt="Security analysis of telemedicine architecture...")
   - Task(subagent_type="backend-development:backend-architect", prompt="Backend architecture for HIPAA...")
   - Task(subagent_type="general-purpose", prompt="Cloud infrastructure cost/compliance analysis...")

5. Synthesizes ADR:
   > Decision: AWS HIPAA-eligible services with encryption at rest (AES-256),
   > TLS 1.3 in transit, BAA with AWS, audit logs to immutable S3.
   > Confidence: High (3/3 agents agreed)

6. User approves ADR → enters plan mode → task breakdown constrained by ADR

7. Plan document includes ADR as Appendix A
```

### Example: Database Technology Selection

```
User: "/horde-plan Build an event store — should we use PostgreSQL or DynamoDB?"

Claude:
1. Requirements analysis → detects A-vs-B architecture question
2. Offers validated planning with Adversarial Debate

3. Dispatches:
   - Advocate-A (backend-architect): Argues for PostgreSQL
   - Advocate-B (backend-architect): Argues for DynamoDB
   - Judge (general-purpose as senior-architect): Rules on debate

4. ADR: "Use PostgreSQL with JSONB columns for events. DynamoDB's
   eventual consistency is incompatible with the strong ordering
   requirements identified in the requirements analysis."

5. Task breakdown uses PostgreSQL throughout — no ambiguity in implementation tasks
```

### Example: Fast Plan (No Deliberation)

```
User: "/horde-plan Add CRUD endpoints for the notifications model"

Claude:
1. Requirements analysis → Score: 8 (5 tasks, 1 subsystem, no risk flags)
2. Score < 15 → fast plan (no deliberation offered)
3. Standard single-agent planning workflow (unchanged from v1.0)
```

## Integration Notes

**Required Tools:**
- `EnterPlanMode` - Signal planning state
- `ExitPlanMode` - Request approval and handoff
- `TaskCreate` - Create trackable tasks
- `TaskList` - Show task progress
- `TaskUpdate` - Update task status
- `Task` - Dispatch golden-horde deliberation agents (Phase 2.5, validated planning only)

**Complementary Skills:**
- `golden-horde` - Pre-planning deliberation for complex projects (Phase 2.5)
- `horde-brainstorming` - Use before planning for exploratory ideation (Phase 0)
- `horde-implement` - Use after planning for execution (full pipeline: subagent-driven-development → implementation-status → horde-review)
- `implementation-status` - Use to check plan completion status (built into horde-implement before review)

**Skill Relationship:**
```
horde-brainstorming (explore options)
  └── horde-plan v1.2 (create structured plan)
        ├── [Phase 2.5] golden-horde deliberation (validate architecture)
        ├── [Output] Plan Output Contract (## phases, ### tasks, exit criteria, YAML manifest)
        └── horde-implement Path B (execute plan — zero re-discovery)
              ├── Plan Parser reads YAML frontmatter (skip structural inference)
              ├── Task transfer (reuse TaskCreate IDs via TaskUpdate)
              ├── Phase loop with gate testing (depths from manifest)
              └── Post-execution: implementation-status → horde-test → horde-review
```

**File Locations:**
- Plans saved to: `docs/plans/YYYY-MM-DD-[feature].md`
- Plan manifest: YAML frontmatter in plan document (machine + human readable)
- Task tracking: In-memory via TaskCreate/TaskList, transferred to horde-implement via task_ids
