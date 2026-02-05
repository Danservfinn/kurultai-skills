---
name: horde-gate-testing
description: Run integration tests between implementation phases to catch integration issues early. Use PROACTIVELY when completing a phase and before starting the next phase.
integrations:
  - horde-swarm
---

# Phase Gate Testing Skill

This skill runs comprehensive integration tests between implementation phases (mid-plan execution) to catch integration issues early, rather than discovering them at the end.

## When to Use

Use this skill when:
- After completing any phase in a multi-phase implementation
- Before starting the next phase (gate between phases)
- When handoff between phases carries integration risk
- When phases have complex dependencies or contracts

## Installation

Before using this skill, install the required dependencies:

```bash
pip install -r requirements.txt
```

The phase-gate-testing skill requires Python 3.8+ and the following packages:
- `pydantic` - Data validation and settings management
- `typer` - CLI framework
- `rich` - Terminal formatting and output

## When to Use vs Alternatives

| Skill | Use When | Don't Use When |
|-------|----------|----------------|
| **phase-gate-testing** (this skill) | Testing integration between completed and upcoming phases, validating contracts before handoff, catching integration issues early | Auditing overall implementation status (use `implementation-status` instead) |
| **implementation-status** | Auditing existing implementation progress across all phases, checking completion percentages, generating completion prompts | Testing integration contracts between specific phases |
| **subagent-driven-development** | Implementing independent tasks in parallel, executing implementation work | You need to first verify phase integration before proceeding |

**Decision Flow**:
1. Just completed a phase and need to test it integrates with the next? → **Use this skill (phase-gate-testing)**
2. Need to check overall plan completion status? → **Use `implementation-status`**
3. Gate passed and ready to implement next phase? → **Use `subagent-driven-development`**

## Core Workflow

### Step 1: Integration Surface Detection

Identify what Phase N exports that Phase N+1 depends on:

1. Read the plan document (e.g., `docs/plans/neo4j.md`)
2. Identify the boundary between Phase N (completed) and Phase N+1 (upcoming)
3. Extract the integration surface:
   - **Exported functions/classes** from Phase N
   - **Data structures** passed between phases
   - **API contracts** (endpoints, request/response formats)
   - **Database schemas** or state changes
   - **Configuration** required by Phase N+1
   - **Events** or callbacks

**Integration Surface Checklist:**
```markdown
- [ ] Public APIs/functions exported by Phase N
- [ ] Data models/schemas shared between phases
- [ ] Configuration values Phase N+1 expects
- [ ] Side effects (database, files, external services)
- [ ] Error handling contracts
- [ ] Event/callback interfaces
```

### Step 2: Contract Test Generation

Create tests that verify Phase N meets Phase N+1's expectations:

1. **Interface Contract Tests**: Verify exported functions exist with correct signatures
2. **Data Contract Tests**: Verify data structures match expected schemas
3. **Behavior Contract Tests**: Verify functions behave as documented
4. **Error Contract Tests**: Verify error handling matches expectations

**Test Generation Template:**
```typescript
// Example contract test structure
ContractTest({
  phase: "Phase N",
  consumer: "Phase N+1",
  contracts: [
    {
      name: "API endpoint returns expected format",
      test: () => { /* verify response schema */ }
    },
    {
      name: "Function accepts required parameters",
      test: () => { /* verify function signature */ }
    },
    {
      name: "Error responses follow contract",
      test: () => { /* verify error format */ }
    }
  ]
})
```

### Step 3: Mock Generation

Create lightweight mocks for upcoming phases to test in isolation:

1. **Phase N+1 Consumer Mock**: Simulates how Phase N+1 will call Phase N
2. **Dependency Mocks**: Mock external dependencies Phase N relies on
3. **State Mocks**: Set up expected state for Phase N+1 to consume

**Mock Generation Principles:**
- Mocks should be minimal but realistic
- Capture the actual usage patterns from the plan
- Document assumptions Phase N+1 makes about Phase N

### Step 4: Test Execution

Run contract tests against Phase N implementation:

1. **Setup Test Environment**: Use mocks and test fixtures
2. **Execute Contract Tests**: Run all generated contract tests
3. **Execute Integration Scenarios**: Run end-to-end scenarios crossing the phase boundary
4. **Collect Results**: Document pass/fail for each test

**Test Execution Command:**
```bash
# Example: Run phase gate tests
python3 scripts/gate_orchestrator.py \
  --plan-path "docs/plans/neo4j.md" \
  --current-phase "Phase 1" \
  --next-phase "Phase 2" \
  --phase-paths "src/agent/" \
  --output "gate_report.md"
```

### Step 5: Decision Gate

Evaluate results and determine gate status:

| Status | Criteria | Action |
|--------|----------|--------|
| **PASS** | All contract tests pass, no integration risks detected | Proceed to Phase N+1 |
| **WARN** | Tests pass but risks detected (breaking changes, unclear contracts) | Proceed with caution, document risks |
| **FAIL** | Tests fail or critical integration issues found | Block progression, fix issues first |

**Risk Assessment Factors:**
- Breaking changes to existing interfaces
- Missing error handling coverage
- Undocumented assumptions
- Performance concerns at scale
- Security implications

### Step 6: Reporting

Generate gate report with findings and recommendations:

1. **Summary**: Overall gate status (PASS/WARN/FAIL)
2. **Test Results**: Detailed test outcomes
3. **Risk Assessment**: Identified risks and their severity
4. **Recommendations**: Specific actions before proceeding

## Integration with Other Skills

### Works with implementation-status
- Use `implementation-status` to confirm Phase N is complete
- Use `phase-gate-testing` to verify Phase N is ready for Phase N+1

**Integration Pattern:**
```
1. Skill("implementation-status", args="Check if Phase N is complete")
2. If complete → Skill("phase-gate-testing", args="Test Phase N→N+1 integration")
3. If gate passes → Skill("subagent-driven-development", args="Implement Phase N+1")
```

### Works with subagent-driven-development
- Use `phase-gate-testing` to find issues
- Use `subagent-driven-development` to fix issues found

**Fix Pattern:**
```
1. Gate fails with specific issues
2. Skill("subagent-driven-development", args="Fix integration issues: [list]")
3. Re-run gate tests
```

### Automatic Triggering
Consider triggering phase-gate-testing automatically:
- After `implementation-status` marks a phase complete
- Before dispatching subagents for the next phase
- As a pre-check in CI/CD pipelines

## Status Definitions

### PASS
- All contract tests pass
- No breaking changes detected
- Integration surface is stable and documented
- Phase N+1 can proceed with confidence

**PASS Output:**
```markdown
## Gate Result: PASS

Phase N is ready for Phase N+1. All contracts verified.
```

### WARN
- All tests pass but with caveats
- Non-breaking changes that need documentation
- Performance concerns at scale
- Missing edge case handling

**WARN Output:**
```markdown
## Gate Result: WARN

Phase N can proceed to Phase N+1 with caution.

### Risks Identified
1. [Risk description and mitigation]

### Recommendations
- [ ] Action item before proceeding
```

### FAIL
- One or more contract tests fail
- Breaking changes to existing interfaces
- Critical integration issues found
- Phase N+1 cannot proceed safely

**FAIL Output:**
```markdown
## Gate Result: FAIL

Phase N cannot proceed to Phase N+1. Issues must be resolved.

### Failed Tests
1. [Test name]: [Failure reason]

### Required Fixes
- [ ] Fix item

### Re-run Gate
Execute: `phase-gate-testing --phase-from "Phase N" --phase-to "Phase N+1"`
```

## Usage Examples

### Example 1: Testing Phase 1→2 Handoff in Neo4j Implementation

**Context**: Neo4j implementation plan has Phase 1 (Core Setup) completing, ready for Phase 2 (Agent Nodes).

**Execution:**
1. **Integration Surface Detection**:
   - Phase 1 exports: `Neo4jConnection` class, `initialize_schema()` function
   - Phase 2 expects: Working connection pool, base schema with `Agent` node type

2. **Contract Tests Generated**:
   - `test_connection_pool_available`: Verify connection pooling works
   - `test_agent_node_type_exists`: Verify Agent node type can be created
   - `test_schema_initialization_idempotent`: Verify safe to call multiple times

3. **Mock Generation**:
   - Mock Phase 2 agent creation scenarios
   - Mock concurrent connection usage

4. **Test Execution**:
   ```bash
   python3 scripts/gate_orchestrator.py \
     --plan-path "docs/plans/neo4j.md" \
     --current-phase "Phase 1: Core Setup" \
     --next-phase "Phase 2: Agent Nodes" \
     --phase-paths "src/agent/" \
     --output "gate_report.md"
   ```

5. **Gate Result**: PASS
   - All connection tests pass
   - Schema initialization verified
   - Ready for Phase 2 implementation

### Example 2: Testing API Contract Between Backend and Frontend Phases

**Context**: Phase 3 (Backend API) completing, Phase 4 (Frontend Integration) starting.

**Execution:**
1. **Integration Surface Detection**:
   - Phase 3 exports: REST API endpoints at `/api/v1/*`
   - Phase 4 expects: Specific JSON response formats, auth headers

2. **Contract Tests Generated**:
   - `test_api_response_schema`: Verify JSON structure matches spec
   - `test_auth_header_required`: Verify 401 on missing auth
   - `test_pagination_format`: Verify pagination metadata format

3. **Mock Generation**:
   - Mock frontend API client
   - Mock various frontend usage patterns

4. **Test Execution**:
   - Run API contract tests
   - Verify response codes and headers
   - Check CORS configuration

5. **Gate Result**: WARN
   - Tests pass but CORS headers missing for local development
   - Recommendation: Add CORS middleware before Phase 4 proceeds

## Output Format

### Gate Report Structure

```markdown
# Phase Gate Report: Phase N → Phase N+1

## Summary
- **Gate Status**: PASS/WARN/FAIL
- **Phase From**: [Phase N name]
- **Phase To**: [Phase N+1 name]
- **Test Date**: [Timestamp]
- **Test Duration**: [Duration]

## Integration Surface
### Phase N Exports
- [List of exported APIs, functions, data structures]

### Phase N+1 Expectations
- [List of expected contracts]

## Test Results
### Contract Tests
| Test Name | Status | Duration | Notes |
|-----------|--------|----------|-------|
| test_name_1 | PASS | 0.5s | |
| test_name_2 | FAIL | 0.2s | [Failure details] |

### Integration Scenarios
| Scenario | Status | Notes |
|----------|--------|-------|
| Scenario 1 | PASS | |
| Scenario 2 | WARN | [Warning details] |

## Risk Assessment
| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| [Risk description] | High/Med/Low | High/Med/Low | [Mitigation strategy] |

## Recommendations
### Immediate Actions
- [ ] Action item 1
- [ ] Action item 2

### Before Next Gate
- [ ] Preparation item 1

## Appendix
### Test Logs
[Link to detailed logs]

### Mocks Used
[Description of mocks generated]
```

## Quick Reference

### Gate Checklist
```markdown
Pre-Gate:
- [ ] Phase N marked complete (implementation-status)
- [ ] Plan document reviewed for integration points
- [ ] Test environment ready

During Gate:
- [ ] Integration surface documented
- [ ] Contract tests generated
- [ ] Mocks created
- [ ] Tests executed
- [ ] Results analyzed

Post-Gate:
- [ ] Gate report generated
- [ ] Status determined (PASS/WARN/FAIL)
- [ ] Recommendations documented
- [ ] Next steps communicated
```

### Common Integration Issues

| Issue | Detection | Resolution |
|-------|-----------|------------|
| Missing error handling | Contract test for error cases | Add error handling to Phase N |
| Breaking API changes | Interface contract tests | Document migration path |
| Performance degradation | Load tests in gate | Optimize before proceeding |
| Missing documentation | Documentation contract tests | Add docs before Phase N+1 |
| State management issues | State transition tests | Fix state handling in Phase N |
