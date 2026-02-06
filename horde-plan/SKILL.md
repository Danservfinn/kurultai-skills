---
name: horde-plan
version: "1.1"
description: Create comprehensive implementation plans using plan mode with EnterPlanMode/ExitPlanMode. For complex projects, invokes golden-horde multi-agent deliberation to validate architecture before task breakdown. Integrates with tasks and hands off to horde-implement for execution.
integrations:
  - horde-swarm
  - golden-horde
---

# Horde Plan

Create comprehensive implementation plans using plan mode with task breakdown, dependency mapping, and hands off to horde-implement for execution.

**New in v1.1:** For complex projects, horde-plan can invoke golden-horde patterns (Adversarial Debate, Consensus Deliberation) to validate architectural decisions *before* task breakdown. This produces an Architecture Decision Record (ADR) that constrains the plan, preventing the #1 failure mode: wrong architecture discovered only during implementation.

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

**Task Structure Template:**
```markdown
### Task N: [Task Title]

**Description:** [What this task accomplishes]

**Files:**
- Create: `path/to/new/file.ext`
- Modify: `path/to/existing/file.ext`
- Reference: `path/to/reference/file.ext`

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests passing

**Dependencies:** None / Task M, Task N

**Domain:** [Backend/Frontend/DevOps/etc.]

**Notes:** [Any important context]
```

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

Create the plan document with structure for ExitPlanMode:

**Plan Template:**
```markdown
# [Feature Name] Implementation Plan

> **Plan Status:** Draft
> **Created:** 2026-02-04
> **Estimated Tasks:** N
> **Estimated Phases:** N

## Overview

**Goal:** [One sentence description]

**Architecture:** [2-3 sentence approach]

**Tech Stack:** [Key technologies]

## Phase Breakdown

### Phase 1: [Phase Name]

**Status:** Pending
**Tasks:** N
**Parallelizable:** Yes/No

#### Task 1.1: [Task Title]
**Description:** [What]
**Files:** [List]
**Acceptance:** [Criteria]
**Dependencies:** None

[... remaining tasks ...]

### Phase 2: [Phase Name]
[... same structure ...]

## Dependencies

```
Phase 1 (Setup)
    ├── Phase 2 (Core) - depends on Phase 1
    │   ├── Phase 3 (Integration) - depends on Phase 2
    │   └── Phase 4 (Testing) - depends on Phase 2
    └── Phase 5 (Documentation) - can run parallel
```

## Execution Handoff

Once approved, this plan will be executed using:
- **Skill:** `horde-implement`
- **Pipeline:** senior-prompt-engineer → subagent-driven-development → implementation-status → horde-review
- **Mode:** Same-session parallel dispatch with review gates and completion audit

## Appendix A: Architecture Decision Record (if validated planning was used)

> **Decision:** [Chosen approach]
> **Validated by:** [N]-agent [pattern name] deliberation
> **Confidence:** [High/Medium/Low]

[Full ADR content from Phase 2.5]

## Approval

- [ ] Requirements understood
- [ ] Architecture validated (if ADR present)
- [ ] Task breakdown acceptable
- [ ] Dependencies correct
- [ ] Ready for execution

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

## Integration with Horde-Implement

After plan approval, the skill automatically hands off to `horde-implement`:

```
User: "Yes, proceed"

Claude:
Using horde-implement to execute [feature-name] plan.

[Invokes horde-implement with:
- Plan file reference
- All tasks pre-created via TaskCreate
- Dependency mapping established
- Review gates configured]
```

**Handoff Template:**
```markdown
## Execution Handoff

I'm now using **horde-implement** to execute this plan.

**Plan Reference:** `docs/plans/YYYY-MM-DD-[feature].md`
**Total Tasks:** N
**Current Phase:** Phase 1

horde-implement will:
1. Use senior-prompt-engineer to refine the implementation approach
2. Deploy subagent-driven-development for parallel task execution
3. Apply review gates at each task completion
4. Track progress and handle errors with systematic-debugging
5. Upon completion, run implementation-status to verify 100% completion
6. Only after 100% verification, run horde-review for comprehensive validation

[Proceeds with implementation]
```

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

Before exiting plan mode, verify:

- [ ] **Complete breakdown** - All work is captured in tasks
- [ ] **Clear acceptance** - Each task has success criteria
- [ ] **Reasonable dependencies** - Dependencies are real, not artificial
- [ ] **File paths specified** - Implementation knows where to work
- [ ] **Test coverage planned** - Testing is explicit in tasks
- [ ] **Integration points clear** - How pieces connect is documented

## Common Patterns

### Pattern 1: CRUD Feature

```markdown
### Phase 1: Database Schema
- Task 1.1: Create table migration
- Task 1.2: Create model definitions

### Phase 2: Backend API
- Task 2.1: Create endpoint
- Task 2.2: Add validation
- Task 2.3: Add error handling

### Phase 3: Frontend Integration
- Task 3.1: Create API client
- Task 3.2: Build UI components
- Task 3.3: Connect to state

### Phase 4: Testing
- Task 4.1: Unit tests
- Task 4.2: Integration tests
- Task 4.3: E2E tests
```

### Pattern 2: Infrastructure Work

```markdown
### Phase 1: Planning
- Task 1.1: Design architecture
- Task 1.2: Create diagrams

### Phase 2: Implementation
- Task 2.1: Configure services
- Task 2.2: Set up networking
- Task 2.3: Add monitoring

### Phase 3: Validation
- Task 3.1: Test failover
- Task 3.2: Load testing
- Task 3.3: Security review
```

### Pattern 3: Refactoring

```markdown
### Phase 1: Analysis
- Task 1.1: Map current structure
- Task 1.2: Identify coupling points

### Phase 2: Refactor
- Task 2.1: Extract module
- Task 2.2: Update imports
- Task 2.3: Add tests

### Phase 3: Verification
- Task 3.1: Run existing tests
- Task 3.2: Add new tests
- Task 3.3: Performance comparison
```

## Example Output

**User:** "/horde-plan Add user profile management with avatar uploads"

**Claude:**

```
I'm using horde-plan to create an implementation plan.

[⚠⚠] Entering Plan Mode

I'll create an implementation plan for: User Profile Management with Avatar Uploads

Estimated tasks: 12-15
Estimated phases: 5
Complexity: Medium

Integration points:
- User authentication (existing)
- Database (PostgreSQL)
- Object storage (S3-compatible)
- Profile API endpoints
- Avatar upload UI

Type 'yes' to continue or 'no' to cancel.

[User: yes]

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

## Phase Breakdown

### Phase 1: Database & Models

**Status:** Pending
**Tasks:** 3
**Parallelizable:** No (sequential migrations)

#### Task 1.1: Extend User Schema
**Description:** Add profile fields to users table
**Files:**
- Create: `migrations/002_add_profile_fields.sql`
- Modify: `src/models/user.py`
**Acceptance:**
- [ ] display_name, bio, location columns added
- [ ] Avatar URL column added
- [ ] Migration runs successfully
**Dependencies:** None

#### Task 1.2: Create Pydantic Models
**Description:** Request/response schemas for profile data
**Files:**
- Create: `src/schemas/profile.py`
**Acceptance:**
- [ ] UserProfileCreate schema
- [ ] UserProfileResponse schema
- [ ] AvatarUploadResponse schema
**Dependencies:** Task 1.1

#### Task 1.3: Add Repository Layer
**Description:** Database access methods for profiles
**Files:**
- Create: `src/repositories/profile.py`
**Acceptance:**
- [ ] get_profile() method
- [ ] update_profile() method
- [ ] upload_avatar() method
**Dependencies:** Task 1.2

### Phase 2: Backend API

**Status:** Pending
**Tasks:** 4
**Parallelizable:** Yes (except 2.4)

#### Task 2.1: GET Profile Endpoint
**Description:** Retrieve current user's profile
**Files:**
- Create: `src/api/v1/profile.py`
**Acceptance:**
- [ ] GET /api/v1/profile returns user profile
- [ ] 404 if profile doesn't exist
- [ ] Requires authentication
**Dependencies:** Task 1.3
**Domain:** Backend

#### Task 2.2: PATCH Profile Endpoint
**Description:** Update profile fields
**Files:**
- Modify: `src/api/v1/profile.py`
**Acceptance:**
- [ ] PATCH /api/v1/profile updates allowed fields
- [ ] Validation on display_name length
- [ ] Returns updated profile
**Dependencies:** Task 2.1
**Domain:** Backend

#### Task 2.3: Avatar Upload Endpoint
**Description:** Handle avatar image uploads
**Files:**
- Modify: `src/api/v1/profile.py`
- Create: `src/services/storage.py`
**Acceptance:**
- [ ] POST /api/v1/profile/avatar accepts image
- [ ] Validates file type (jpg, png, webp)
- [ ] Validates file size (< 5MB)
- [ ] Stores in S3 and returns URL
**Dependencies:** Task 2.2
**Domain:** Backend

#### Task 2.4: Avatar Deletion
**Description:** Remove avatar and revert to default
**Files:**
- Modify: `src/api/v1/profile.py`
**Acceptance:**
- [ ] DELETE /api/v1/profile/avatar removes avatar
- [ ] S3 object deleted
- [ ] Profile updated to default avatar
**Dependencies:** Task 2.3
**Domain:** Backend

### Phase 3: Storage Integration

**Status:** Pending
**Tasks:** 2
**Parallelizable:** Yes

#### Task 3.1: Configure S3 Client
**Description:** Set up boto3 S3 client with MinIO
**Files:**
- Create: `src/config/storage.py`
**Acceptance:**
- [ ] S3 client configured from env vars
- [ ] Bucket existence check on startup
- [ ] Presigned URL generation
**Dependencies:** None
**Domain:** DevOps

#### Task 3.2: Image Processing Pipeline
**Description:** Resize and optimize avatars
**Files:**
- Create: `src/services/images.py`
**Acceptance:**
- [ ] Resize to standard sizes (64, 128, 256)
- [ ] Convert to WebP with fallback
- [ ] Strip EXIF data
**Dependencies:** None
**Domain:** Backend

### Phase 4: Frontend UI

**Status:** Pending
**Tasks:** 3
**Parallelizable:** Yes

#### Task 4.1: Profile Page Layout
**Description:** Create profile management page
**Files:**
- Create: `src/app/profile/page.tsx`
- Create: `src/app/profile/components/ProfileForm.tsx`
**Acceptance:**
- [ ] Form with display name, bio, location
- [ ] Avatar preview and upload area
- [ ] Save/cancel buttons
**Dependencies:** None
**Domain:** Frontend

#### Task 4.2: Avatar Upload Component
**Description:** Drag-drop avatar upload
**Files:**
- Create: `src/app/profile/components/AvatarUpload.tsx`
**Acceptance:**
- [ ] Dropzone integration
- [ ] Image preview before upload
- [ ] Progress indicator
- [ ] Error handling
**Dependencies:** Task 4.1
**Domain:** Frontend

#### Task 4.3: API Client Integration
**Description:** Connect UI to profile API
**Files:**
- Create: `src/lib/api/profile.ts`
- Modify: `src/app/profile/page.tsx`
**Acceptance:**
- [ ] getProfile() fetches current profile
- [ ] updateProfile() sends changes
- [ ] uploadAvatar() handles file upload
**Dependencies:** Task 4.2
**Domain:** Frontend

### Phase 5: Testing & Docs

**Status:** Pending
**Tasks:** 2
**Parallelizable:** Yes

#### Task 5.1: Test Coverage
**Description:** Unit and integration tests
**Files:**
- Create: `tests/api/test_profile.py`
- Create: `tests/services/test_images.py`
**Acceptance:**
- [ ] API endpoint tests
- [ ] Image processing tests
- [ ] Storage mock tests
- [ ] >80% coverage
**Dependencies:** All Phase 2-4 tasks

#### Task 5.2: Documentation
**Description:** API docs and usage guide
**Files:**
- Create: `docs/api/profile.md`
- Create: `docs/setup/avatar-storage.md`
**Acceptance:**
- [ ] OpenAPI spec complete
- [ ] Setup instructions for S3/MinIO
- [ ] Example curl commands
**Dependencies:** All Phase 2-4 tasks

## Dependencies

```
Phase 1 (Database & Models)
    ├── Phase 2 (Backend API) - depends on Phase 1
    │   ├── Phase 4 (Frontend UI) - depends on Phase 2
    │   └── Phase 5 (Testing) - depends on Phase 2
    └── Phase 3 (Storage) - independent, can run parallel
```

## Execution Handoff

Once approved, this plan will be executed using:
- **Skill:** `horde-implement`
- **Pipeline:** senior-prompt-engineer → subagent-driven-development → implementation-status → horde-review
- **Mode:** Same-session parallel dispatch with review gates and completion audit
- **Specialist Routing:** Backend (2.x), DevOps (3.1), Frontend (4.x)

## Approval

- [ ] Requirements understood
- [ ] Task breakdown acceptable
- [ ] Dependencies correct
- [ ] Ready for execution

**Ready to proceed?**

---

[ExitPlanMode invoked with:
- allowedPrompts: [
    "Run pytest",
    "Run npm test",
    "Git commands",
    "Python/Node commands"
  ]
]

Plan complete! Here's what I'll build:

**Summary:** User profile management system with avatar uploads, spanning database schema, REST API, S3 storage, and React UI.

**Tasks:** 14 total across 5 phases
**Estimated effort:** 6-8 hours

**Next Steps:**
1. Review the plan above
2. If approved, I'll use horde-implement to execute
3. Each task will have review gates before proceeding
4. Progress tracked via TaskList throughout

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
  └── horde-plan (create structured plan)
        ├── [Phase 2.5] golden-horde deliberation (validate architecture)
        └── horde-implement (execute plan)
```

**File Locations:**
- Plans saved to: `docs/plans/YYYY-MM-DD-[feature].md`
- Task tracking: In-memory via TaskCreate/TaskList
