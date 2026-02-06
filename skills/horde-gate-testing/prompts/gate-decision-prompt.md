# Gate Decision Prompt

## Purpose

Make a PASS/WARN/FAIL gate decision for a phase handoff based on test results, risk assessment, and project context. This is the final checkpoint before a phase is considered complete.

## Task Description

You are a subagent responsible for making the final gate decision for a phase handoff. Evaluate all available evidence - test results, risk assessments, and project context - to render a decision with clear justification.

## Input Parameters

- `{{PHASE_NAME}}`: Name of the phase
- `{{PHASE_NUMBER}}`: Phase number for reference
- `{{TEST_SUMMARY}}`: Summary of all test results (pass/fail counts, coverage)
- `{{RISK_LIST}}`: List of identified risks with severity levels
- `{{PROJECT_CONTEXT}}`: Project-specific context (criticality, timeline, standards)
- `{{PREVIOUS_GATE_DECISIONS}}`: Decisions from previous phases (for context)

## Instructions

1. **Review test summary** - verify all required tests have passed
2. **Evaluate risk list** - consider severity and impact of each risk
3. **Apply decision criteria** - use the criteria below to determine status
4. **Consider project context** - factor in criticality and timeline
5. **Render decision** - PASS, WARN, or FAIL with justification
6. **Provide recommendations** - next steps based on decision

## Decision Criteria

### PASS

All of the following must be true:

- [ ] All contract tests pass (100%)
- [ ] No HIGH severity risks exist
- [ ] No MEDIUM severity risks exist
- [ ] Test coverage meets or exceeds project threshold (default: 80%)
- [ ] Integration surface is stable and documented

**Outcome**: Phase is approved for handoff. Subsequent phases may proceed.

### WARN

All of the following must be true:

- [ ] All contract tests pass (100%)
- [ ] No HIGH severity risks exist
- [ ] One or more MEDIUM severity risks exist
- [ ] Test coverage is within 10% of project threshold
- [ ] Integration surface is stable

**Outcome**: Phase is conditionally approved. Subsequent phases may proceed, but MEDIUM risks should be addressed before the next gate.

### FAIL

Any of the following will result in FAIL:

- [ ] Any contract test fails
- [ ] Any HIGH severity risk exists
- [ ] Test coverage is more than 10% below project threshold
- [ ] Integration surface is unstable or undocumented
- [ ] Breaking changes without migration plan

**Outcome**: Phase is NOT approved. Issues must be resolved and gate re-evaluated before subsequent phases proceed.

## Output Format

Provide your gate decision in this exact format:

```markdown
## Gate Decision Report: {{PHASE_NAME}}

### Decision

**Status**: PASS | WARN | FAIL

**Confidence**: HIGH | MEDIUM | LOW

**Decision Summary**: [One-sentence summary of the decision]

### Decision Justification

#### Test Results Evaluation

| Test Category | Required | Actual | Status |
|---------------|----------|--------|--------|
| Contract Tests | 100% pass | X% pass | Met/Not Met |
| Test Coverage | >=80% | X% | Met/Not Met |
| Existence Tests | All pass | X/X passed | Met/Not Met |
| Signature Tests | All pass | X/X passed | Met/Not Met |
| Schema Tests | All pass | X/X passed | Met/Not Met |

#### Risk Evaluation

| Risk Level | Count | Threshold | Status |
|------------|-------|-----------|--------|
| HIGH | X | 0 | Acceptable/Exceeded |
| MEDIUM | X | 0 for PASS, <=2 for WARN | Acceptable/Exceeded |
| LOW | X | No limit | Acceptable |

#### Criteria Assessment

| Criterion | Required | Actual | Met |
|-----------|----------|--------|-----|
| All tests pass | Yes | Yes/No | Yes/No |
| No HIGH risks | Yes | Yes/No | Yes/No |
| No MEDIUM risks (PASS) or acceptable (WARN) | Yes | Yes/No | Yes/No |
| Coverage threshold | >=80% | X% | Yes/No |
| Stable API | Yes | Yes/No | Yes/No |

### Detailed Reasoning

[Paragraph explaining the decision rationale, referencing specific test failures or risks that influenced the decision]

### Recommendations

#### If PASS

- [ ] Proceed with next phase
- [ ] Monitor for any issues during integration
- [ ] Address any LOW risks when convenient

#### If WARN

- [ ] Proceed with next phase with caution
- [ ] Address MEDIUM risks before next gate:
  1. [Specific risk to address]
  2. [Specific risk to address]
- [ ] Set timeline for risk remediation
- [ ] Document known issues for downstream teams

#### If FAIL

- [ ] Do NOT proceed with next phase
- [ ] Required fixes before re-evaluation:
  1. [Critical fix needed]
  2. [Critical fix needed]
- [ ] Re-run tests after fixes
- [ ] Re-evaluate gate after fixes complete

### Next Steps

1. [Immediate action item]
2. [Follow-up action item]
3. [Long-term consideration]

### Sign-off

- **Decision**: PASS | WARN | FAIL
- **Date**: [Current date]
- **Gate**: Phase {{PHASE_NUMBER}} handoff
```

## Rules

1. **Be consistent** - apply criteria uniformly across phases
2. **Document reasoning** - explain why the decision was made
3. **Be actionable** - provide clear next steps
4. **Consider context** - project criticality may adjust thresholds
5. **No false passes** - failing tests or HIGH risks always result in FAIL
6. **Confidence matters** - indicate if decision is uncertain

## Example Decisions

### Example 1: PASS Decision

```markdown
## Gate Decision Report: Phase 1: Project Setup

### Decision

**Status**: PASS

**Confidence**: HIGH

**Decision Summary**: All tests pass, no risks identified, phase is ready for handoff.

### Decision Justification

#### Test Results Evaluation

| Test Category | Required | Actual | Status |
|---------------|----------|--------|--------|
| Contract Tests | 100% pass | 100% pass | Met |
| Test Coverage | >=80% | 92% | Met |
| Existence Tests | All pass | 8/8 passed | Met |
| Signature Tests | All pass | 5/5 passed | Met |
| Schema Tests | All pass | 3/3 passed | Met |

#### Risk Evaluation

| Risk Level | Count | Threshold | Status |
|------------|-------|-----------|--------|
| HIGH | 0 | 0 | Acceptable |
| MEDIUM | 0 | 0 | Acceptable |
| LOW | 1 | No limit | Acceptable |

#### Criteria Assessment

| Criterion | Required | Actual | Met |
|-----------|----------|--------|-----|
| All tests pass | Yes | Yes | Yes |
| No HIGH risks | Yes | Yes | Yes |
| No MEDIUM risks | Yes | Yes | Yes |
| Coverage threshold | >=80% | 92% | Yes |
| Stable API | Yes | Yes | Yes |

### Detailed Reasoning

Phase 1 has met all criteria for PASS status. All 16 contract tests pass successfully,
with 92% test coverage exceeding the 80% threshold. No HIGH or MEDIUM risks were
identified during risk assessment. The integration surface is stable and well-documented.
The single LOW risk (minor documentation improvement) does not impact handoff.

### Recommendations

- [ ] Proceed with Phase 2
- [ ] Address LOW risk (documentation improvement) when convenient
- [ ] Monitor integration with Phase 2

### Next Steps

1. Begin Phase 2 implementation
2. Use Phase 1 exports as integration points
3. Schedule Phase 2 gate review

### Sign-off

- **Decision**: PASS
- **Date**: 2024-01-15
- **Gate**: Phase 1 handoff
```

### Example 2: WARN Decision

```markdown
## Gate Decision Report: Phase 2: Neo4j Connection

### Decision

**Status**: WARN

**Confidence**: MEDIUM

**Decision Summary**: All tests pass but 2 MEDIUM risks exist; conditional approval granted.

### Decision Justification

#### Test Results Evaluation

| Test Category | Required | Actual | Status |
|---------------|----------|--------|--------|
| Contract Tests | 100% pass | 100% pass | Met |
| Test Coverage | >=80% | 85% | Met |
| Existence Tests | All pass | 6/6 passed | Met |
| Signature Tests | All pass | 4/4 passed | Met |
| Schema Tests | All pass | 2/2 passed | Met |

#### Risk Evaluation

| Risk Level | Count | Threshold | Status |
|------------|-------|-----------|--------|
| HIGH | 0 | 0 | Acceptable |
| MEDIUM | 2 | <=2 for WARN | At Limit |
| LOW | 1 | No limit | Acceptable |

#### Criteria Assessment

| Criterion | Required | Actual | Met |
|-----------|----------|--------|-----|
| All tests pass | Yes | Yes | Yes |
| No HIGH risks | Yes | Yes | Yes |
| Acceptable MEDIUM risks | <=2 | 2 | Yes |
| Coverage threshold | >=80% | 85% | Yes |
| Stable API | Yes | Yes | Yes |

### Detailed Reasoning

Phase 2 meets all criteria for WARN status. All 12 contract tests pass with 85% coverage.
No HIGH risks exist. Two MEDIUM risks were identified:

1. Error handling for connection timeouts is not fully tested
2. Documentation for retry logic is incomplete

These risks do not block Phase 3 from proceeding but should be addressed before the
Phase 2->3 gate to prevent issues from compounding.

### Recommendations

- [ ] Proceed with Phase 3 with caution
- [ ] Address MEDIUM risks before Phase 2->3 gate:
  1. Add tests for connection timeout scenarios
  2. Document retry logic behavior and configuration
- [ ] Set 1-week timeline for risk remediation
- [ ] Document known issues for Phase 3 team

### Next Steps

1. Begin Phase 3 implementation
2. Monitor timeout behavior in Phase 3 integration
3. Schedule follow-up to address MEDIUM risks within 1 week
4. Re-verify risks are addressed before Phase 3 gate

### Sign-off

- **Decision**: WARN
- **Date**: 2024-01-20
- **Gate**: Phase 2 handoff
```

### Example 3: FAIL Decision

```markdown
## Gate Decision Report: Phase 3: Graph Schema

### Decision

**Status**: FAIL

**Confidence**: HIGH

**Decision Summary**: Test failures and HIGH risks identified; phase NOT ready for handoff.

### Decision Justification

#### Test Results Evaluation

| Test Category | Required | Actual | Status |
|---------------|----------|--------|--------|
| Contract Tests | 100% pass | 75% pass | Not Met |
| Test Coverage | >=80% | 65% | Not Met |
| Existence Tests | All pass | 4/4 passed | Met |
| Signature Tests | All pass | 3/5 passed | Not Met |
| Schema Tests | All pass | 2/2 passed | Met |

#### Risk Evaluation

| Risk Level | Count | Threshold | Status |
|------------|-------|-----------|--------|
| HIGH | 2 | 0 | Exceeded |
| MEDIUM | 3 | No limit | Acceptable |
| LOW | 2 | No limit | Acceptable |

#### Criteria Assessment

| Criterion | Required | Actual | Met |
|-----------|----------|--------|-----|
| All tests pass | Yes | No | No |
| No HIGH risks | Yes | No | No |
| Coverage threshold | >=80% | 65% | No |
| Stable API | Yes | No | No |

### Detailed Reasoning

Phase 3 FAILS gate criteria due to multiple critical issues:

1. **Test Failures**: 2 of 5 signature tests failed:
   - `createNode` signature test: Missing optional `properties` parameter
   - `defineRelationship` signature test: Return type mismatch

2. **HIGH Risks Identified**:
   - R1: Breaking change in Node interface - `labels` field renamed to `tags`
     without backward compatibility or migration path
   - R2: Missing export for `SchemaValidator` class required by downstream phases

3. **Insufficient Coverage**: 65% coverage is 15% below threshold, with error
   handling paths completely untested.

These issues would break Phase 4 integration and must be resolved before handoff.

### Recommendations

- [ ] Do NOT proceed with Phase 4
- [ ] Required fixes before re-evaluation:
  1. Fix `createNode` to accept optional `properties` parameter
  2. Fix `defineRelationship` return type to match contract
  3. Add backward compatibility for Node interface or provide migration guide
  4. Export `SchemaValidator` class
  5. Add error handling tests to reach 80% coverage
- [ ] Re-run all tests after fixes
- [ ] Re-evaluate gate after fixes complete

### Next Steps

1. Address all HIGH risks immediately
2. Fix failing tests
3. Add missing tests for coverage
4. Request re-evaluation when complete
5. Notify Phase 4 team of delay

### Sign-off

- **Decision**: FAIL
- **Date**: 2024-01-25
- **Gate**: Phase 3 handoff
```

Return your gate decision in the specified format.
