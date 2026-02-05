---
name: implementation-status
description: Audits active implementation plans for completion status and generates completion prompts. Use PROACTIVELY when the user wants to check implementation progress, audit a plan's completion status, or generate prompts to finish incomplete implementations.
---

# Implementation Status Skill

This skill audits active implementation plans and generates completion prompts using subagent-driven-development patterns.

## When to Use

Use this skill when:
- The user wants to check progress on an implementation plan
- An implementation was interrupted and needs to resume
- The user needs a prompt to finish incomplete work
- Testing and final verification is needed

## When to Use vs Alternatives

| Skill | Use When | Don't Use When |
|-------|----------|----------------|
| **implementation-status** (this skill) | Auditing existing implementation progress, resuming interrupted work, generating completion prompts for partial implementations | Starting fresh implementation (use `executing-plans` or `subagent-driven-development` instead) |
| **executing-plans** | Executing a complete plan from start to finish in a fresh context | Auditing partial progress or resuming existing work |
| **subagent-driven-development** | Implementing independent tasks in parallel with subagents | You need to first assess what remains to be done |

**Decision Flow**:
1. Have an implementation plan and need to check what's done? → **Use this skill (implementation-status)**
2. Plan audited and have completion prompt? → **Use `subagent-driven-development`** to execute
3. Starting fresh with a new plan? → **Use `executing-plans`** or **`subagent-driven-development`**

## Workflow

### Step 1: Audit Plan Completion

1. Read the active plan document (e.g., `docs/plans/neo4j.md`)
2. Use `TaskCreate` to create audit tasks for each phase with explicit task structure:

   **TaskCreate Example:**
   ```typescript
   TaskCreate(
     name="Audit Phase X",
     description="Check if phase tasks are implemented",
     inputs={
       "phase": "Phase X: Name",
       "files": ["path/to/file1.py", "path/to/file2.py"],
       "expected_markers": ["class Foo", "def bar()"]
     },
     expected_output="JSON with status, implemented, missing, issues"
   )
   ```

   **TaskUpdate Example:**
   ```typescript
   TaskUpdate(
     name="Audit Phase X",
     status="completed",
     outputs={
       "status": "partial",
       "implemented": ["src/auth/login.py"],
       "missing": ["src/auth/logout.py"],
       "issues": ["Missing error handling in login()"]
     }
   )
   ```

3. Dispatch audit subagents by ACTUALLY INVOKING the `subagent-driven-development` skill:

   ```
   Skill(skill="subagent-driven-development", args="Audit Phase X: Check if phase tasks are implemented. Review files at [paths]. Report: status, implemented items, missing items, issues.")
   ```

   Create parallel audit tasks for each phase:
   - **Audit subagent**: Checks if phase tasks are implemented
   - **Verification subagent**: Confirms implementation quality
   - **Gap analysis subagent**: Identifies missing pieces

4. **OPTIONAL**: Use the `audit_phase.py` script for automated file existence and marker checking:

   ```bash
   python3 /Users/kurultai/.claude/skills/implementation-status/scripts/audit_phase.py '{"name":"Phase 1","requirements":{"files":["src/main.py"],"markers":{"src/main.py":["class Foo"]}}}'
   ```

5. Run audits in parallel where phases are independent

   For parallel execution, use the `Task` tool to create independent audit tasks. See the `dispatching-parallel-agents` skill for detailed orchestration patterns.

   **Example: Parallel Audit Task Creation**

   When auditing multiple independent phases, dispatch them concurrently:

   ```typescript
   // Create audit tasks for independent phases - these run in parallel
   Task(description="Audit Phase 1: Check authentication implementation. Review files at src/auth/. Report: status, implemented items, missing items, issues.", ...)
   Task(description="Audit Phase 2: Check database schema. Review files at src/db/. Report: status, implemented items, missing items, issues.", ...)
   Task(description="Audit Phase 3: Check API endpoints. Review files at src/api/. Report: status, implemented items, missing items, issues.", ...)
   // These run in parallel when dispatched together
   ```

   **Key Principles for Parallel Audits** (from `dispatching-parallel-agents`):
   - Each phase audit must be independent (no shared state between phases)
   - Give each subagent a focused scope (one phase per agent)
   - Provide clear output expectations (status matrix format)
   - Agents return summaries that you compile into the final report

   **When to Use Parallel Audits:**
   - 3+ phases with no dependencies between them
   - Each phase can be verified without context from other phases
   - Different subsystems/files for each phase

   **When NOT to Use Parallel Audits:**
   - Phases have dependencies (Phase 2 depends on Phase 1 completion)
   - Shared state between phases (same files edited in multiple phases)
   - Need full context across all phases to understand implementation

   For complex parallel orchestration, reference the `dispatching-parallel-agents` skill.

### Step 2: Compile Status Report

Create a status matrix using standardized terminology (Complete/Partial/Missing):

| Phase | Status | Implemented | Missing | Blockers |
|-------|--------|-------------|---------|----------|
| Phase 1 | Complete | Files... | Tasks... | None/X |
| Phase 2 | Partial | Files... | Tasks... | None/X |
| Phase 3 | Missing | Files... | Tasks... | None/X |

**Status Definitions:**
- **Complete**: All tasks implemented, all files exist, tests pass
- **Partial**: Some tasks implemented, some files exist, or partial test coverage
- **Missing**: No implementation found, no files exist, or not started

### Step 3: Generate Completion Prompt

Use the internal completion prompt template to create a comprehensive completion prompt:

1. Read `/Users/kurultai/.claude/skills/implementation-status/prompts/completion-prompt-template.md`
2. Fill in the template variables based on audit results:
   - `{{PLAN_NAME}}`: Name of the implementation plan
   - `{{PLAN_PATH}}`: Path to the plan document
   - `{{INCOMPLETE_PHASES}}`: List of incomplete phases with their tasks
   - `{{COMPLETED_PHASES}}`: List of completed phases for context
   - `{{BLOCKERS}}`: Any identified blockers or dependencies
   - `{{AUDIT_SUMMARY}}`: Summary from the status audit

The generated prompt should:
- List all incomplete phases with specific tasks
- Include testing requirements at the end
- Use subagent-driven-development patterns
- Specify parallel dispatch opportunities
- **Handle partial completions**: For phases marked "Partial", explicitly state what is already implemented vs what remains

**Partial Completion Handling Example:**
```markdown
## Phase 2: Database Schema (PARTIAL - Resume from Task 3)

**Already Implemented:**
- [x] User table created
- [x] Basic migrations set up

**Remaining Tasks:**
- [ ] Add indexes for performance
- [ ] Create migration rollback scripts
- [ ] Add seed data
```

**Output File Location**: Save the generated completion prompt to `docs/plans/[plan-name]-completion.md` for reference and versioning.

To execute the completion work, ACTUALLY INVOKE `subagent-driven-development` skill:

```
Skill(skill="subagent-driven-development", args="[paste the generated completion prompt here]")
```

### Step 4: Output Results

Provide the user with:
1. **Status Summary**: What's complete vs incomplete
2. **Completion Prompt**: Ready-to-use prompt for remaining work
3. **Recommended Approach**: Sequential vs parallel execution

## Audit Subagent Templates

The `prompts/` directory contains ready-to-use prompt templates for dispatching audit subagents:

### Available Prompts

1. **`prompts/audit-subagent-prompt.md`** - For checking if phase tasks are implemented
   - Verifies file existence and content
   - Checks task completion status
   - Reports implementation percentage

2. **`prompts/verification-subagent-prompt.md`** - For verifying implementation quality
   - Analyzes code quality and correctness
   - Checks error handling and security
   - Validates tests and integration

3. **`prompts/gap-analysis-subagent-prompt.md`** - For identifying what's missing
   - Compares plan vs implementation
   - Identifies missing files and functionality
   - Estimates effort to complete gaps

4. **`prompts/completion-prompt-template.md`** - For generating completion prompts
   - Template for finishing incomplete work
   - Uses subagent-driven-development patterns

### Quick Reference Template

```markdown
**Task**: Audit [Phase X] for implementation status

**Check**:
- [ ] Required files exist at specified paths
- [ ] Files contain expected implementations
- [ ] Tests exist and pass
- [ ] Integration points work
- [ ] Documentation complete

**Report**:
- Status: Complete/Partial/Missing
- Implemented: [list]
- Missing: [list]
- Issues: [list]
```

### Using the Prompts with Task Tool

When dispatching subagents, use the full prompt files:

```typescript
// Read the prompt template
const auditPrompt = readFile("/Users/kurultai/.claude/skills/implementation-status/prompts/audit-subagent-prompt.md");

// Dispatch with Task tool
Task(
  description=auditPrompt + "\n\nParameters:\n- PHASE_NAME: \"Phase 1: Setup\"\n- PLAN_PATH: \"docs/plans/example.md\"\n- IMPLEMENTATION_PATHS: [\"src/file1.ts\", \"src/file2.ts\"]",
  ...
)
```

## Example Usage

**User**: "Check the status of neo4j.md implementation"

**Claude**:
1. Read `docs/plans/neo4j.md`
2. Create audit tasks for all 11 phases
3. Dispatch audit subagents in parallel
4. Compile results
5. Generate completion prompt using the internal template at `prompts/completion-prompt-template.md`
6. Save completion prompt to `docs/plans/neo4j-completion.md`
7. Output status + completion prompt

## Output Format

```markdown
## Implementation Status: [Plan Name]

### Summary
- **Complete**: X/Y phases
- **Partial**: Z phases
- **Missing**: W phases

### Detailed Status
[Status matrix]

### Completion Prompt
Saved to: `docs/plans/[plan-name]-completion.md`

```
[Paste-ready prompt to finish implementation]
```

### Recommended Next Steps
1. [Priority order]
```

## Integration with Subagent-Driven-Development

This skill complements `subagent-driven-development`:
- Use `implementation-status` to audit current state
- ACTUALLY INVOKE `subagent-driven-development` skill to finish implementation:

```
Skill(skill="subagent-driven-development", args="[paste the completion prompt here]")
```

- Both skills use parallel subagent dispatch patterns

**Important**: Do NOT just copy patterns from `subagent-driven-development`. Actually invoke it using the Skill tool with the completion prompt as the args.
