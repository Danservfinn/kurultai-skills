# Completion Prompt Template

This template generates prompts for finishing incomplete implementations using subagent-driven-development patterns.

## Template Variables

- `{{PLAN_NAME}}`: Name of the implementation plan (e.g., "neo4j.md")
- `{{PLAN_PATH}}`: Path to the plan document (e.g., `docs/plans/neo4j.md`)
- `{{INCOMPLETE_PHASES}}`: List of incomplete phases with their tasks
- `{{COMPLETED_PHASES}}`: List of completed phases for context
- `{{BLOCKERS}}`: Any identified blockers or dependencies
- `{{AUDIT_SUMMARY}}`: Summary from the status audit

## Generated Prompt Template

```markdown
# Complete Implementation: {{PLAN_NAME}}

## Context

This is a completion prompt for an interrupted implementation.

**Original Plan**: {{PLAN_PATH}}

**Audit Summary**:
{{AUDIT_SUMMARY}}

## Completed Work (For Reference)

{{COMPLETED_PHASES}}

## Remaining Work

{{INCOMPLETE_PHASES}}

## Implementation Instructions

### Phase-by-Phase Completion

For each incomplete phase:

1. **Read the plan section** for the phase in {{PLAN_PATH}}
2. **Use subagent-driven-development patterns**:
   - Create focused subagents for each task
   - Dispatch subagents in parallel where tasks are independent
   - Use sequential dispatch where dependencies exist
3. **Verify each task** before marking complete

### Subagent Dispatch Strategy

**Parallel Opportunities**:
- Tasks within the same phase that don't depend on each other
- Independent phases (check dependencies in plan)

**Sequential Requirements**:
- Tasks that build on previous task outputs
- Phases that depend on earlier phase completion

### Verification Requirements

Each completed task must have:
- [ ] Implementation matches plan specifications
- [ ] Tests written and passing
- [ ] Integration points verified
- [ ] Documentation updated

{{#if BLOCKERS}}
## Known Blockers

{{BLOCKERS}}

Resolve blockers before proceeding with dependent work.
{{/if}}

## Output Format

For each phase completed, provide:

```markdown
### Phase X: [Phase Name] - COMPLETE

**Implemented**:
- [File/Feature]: [Brief description]

**Tests**:
- [Test file]: [Status]

**Verification**:
- [How it was verified]
```

## Final Deliverables

1. All phases marked complete
2. Test suite passes
3. Integration verified
4. Documentation updated
5. Summary of changes

---

**Begin with**: Read {{PLAN_PATH}} and identify the first incomplete phase to implement.
```

## Usage

To generate a completion prompt:

1. Run the implementation-status skill to audit the plan
2. Extract the status matrix and incomplete phases
3. Fill in the template variables above
4. Present the generated prompt to the user

## Example

**Input Variables**:
- PLAN_NAME: "Neo4j Multi-Agent System"
- PLAN_PATH: `docs/plans/neo4j.md`
- INCOMPLETE_PHASES: "Phase 3 (Graph Schema), Phase 4 (Memory Nodes)"
- COMPLETED_PHASES: "Phase 1 (Setup), Phase 2 (Connection)"
- BLOCKERS: "None"
- AUDIT_SUMMARY: "2/4 phases complete, on track"

**Output**: A ready-to-use prompt that guides completion of Phases 3-4 using subagent-driven-development patterns.
