---
name: horde-plan
description: Create comprehensive implementation plans using plan mode with EnterPlanMode/ExitPlanMode. Use when starting any multi-step feature implementation, complex refactoring, or system design work. Integrates with tasks and hands off to horde-implement for execution.
---

# Horde Plan

Create comprehensive implementation plans using plan mode with task breakdown, dependency mapping, and hands off to horde-implement for execution.

## Quick Start

```bash
# Invoke the skill
User: "/horde-plan Create a user authentication system with JWT tokens"

Claude:
1. Enters plan mode (EnterPlanMode)
2. Analyzes requirements
3. Creates task breakdown with phases
4. Maps dependencies (TaskCreate with addBlockedBy)
5. Generates plan.md
6. Exits plan mode for approval (ExitPlanMode)
7. Hands off to horde-implement for execution
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
Complexity: High

Areas affected:
- [Component 1]
- [Component 2]
- [Database/API/etc.]

This will:
- Create detailed task breakdown
- Map all dependencies
- Generate execution plan for horde-implement
- Take 5-10 minutes to plan thoroughly

Type 'PROCEED' to continue or 'no' to cancel.
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
- **Pipeline:** senior-prompt-engineer → subagent-driven-development
- **Mode:** Same-session parallel dispatch with review gates

## Approval

- [ ] Requirements understood
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
- **Pipeline:** senior-prompt-engineer → subagent-driven-development
- **Mode:** Same-session parallel dispatch with review gates
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

## Integration Notes

**Required Tools:**
- `EnterPlanMode` - Signal planning state
- `ExitPlanMode` - Request approval and handoff
- `TaskCreate` - Create trackable tasks
- `TaskList` - Show task progress
- `TaskUpdate` - Update task status

**Complementary Skills:**
- `horde-brainstorming` - Use before planning for complex features
- `horde-implement` - Use after planning for execution (hands off to subagent-driven-development)
- `implementation-status` - Use to check plan completion status

**File Locations:**
- Plans saved to: `docs/plans/YYYY-MM-DD-[feature].md`
- Task tracking: In-memory via TaskCreate/TaskList
