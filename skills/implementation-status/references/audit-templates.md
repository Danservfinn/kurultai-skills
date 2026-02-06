# Audit Templates for Implementation Status

## Phase Audit Template

```markdown
**Phase**: [Phase Name]
**Status**: [Complete/Partial/Missing]

### Files Required
- [ ] File path 1
- [ ] File path 2
- [ ] File path 3

### Implementation Markers
- [ ] Marker 1 (e.g., "class OperationalMemory")
- [ ] Marker 2 (e.g., "def claim_task")
- [ ] Marker 3 (e.g., "RaceConditionError")

### Tests Required
- [ ] Test file exists
- [ ] Tests pass
- [ ] Coverage > 90%

### Issues Found
1. [Issue description]
2. [Issue description]
```

## Status Matrix Template

```markdown
| Phase | Status | Implemented | Missing | Blockers |
|-------|--------|-------------|---------|----------|
| Phase 1 | Complete | 5/5 files | None | None |
| Phase 2 | Partial | 2/3 files | client.py | None |
| Phase 3 | Missing | 0/4 files | All | Phase 2 |
```

## Completion Prompt Template

```markdown
## Completion Prompt: [Plan Name]

### Incomplete Phases
[List phases with specific missing tasks]

### Implementation Order
1. [Phase X] - [Rationale]
2. [Phase Y] - [Rationale]

### Testing Requirements
- Unit tests for all new modules
- Integration tests for phase interactions
- End-to-end test for complete workflow

### Dispatch Strategy
- Sequential for: [dependent phases]
- Parallel for: [independent phases]
```
