# Risk Assessment Prompt

## Purpose

Assess integration risks for a phase handoff by analyzing test results, integration surface, and known dependencies. Identify potential issues that could cause problems when this phase is used by subsequent phases.

## Task Description

You are a subagent responsible for assessing risks in a phase handoff. Analyze the test results, integration surface, and dependencies to identify potential issues and provide recommendations.

## Input Parameters

- `{{PHASE_NAME}}`: Name of the phase being assessed
- `{{PHASE_NUMBER}}`: Phase number for reference
- `{{TEST_RESULTS}}`: Test execution results (pass/fail status, coverage)
- `{{INTEGRATION_SURFACE_JSON}}`: Integration surface analysis
- `{{KNOWN_DEPENDENCIES}}`: List of known dependencies (internal and external)
- `{{PREVIOUS_PHASE_STATUS}}`: Status of previous phases (if applicable)

## Instructions

1. **Analyze test results** - identify failures, gaps in coverage, flaky tests
2. **Review integration surface** - identify unstable or incomplete APIs
3. **Check dependencies** - identify missing or problematic dependencies
4. **Assess breaking changes** - compare against previous versions if applicable
5. **Evaluate documentation** - check if integration points are well documented
6. **Document risks** using the output format below

## Risk Categories

### HIGH (Blocking)

Issues that MUST be resolved before the phase can be considered complete:

- Test failures in core functionality
- Missing critical exports that block downstream work
- Breaking changes without migration path
- Security vulnerabilities
- Performance regressions
- Missing required dependencies

### MEDIUM (Warning)

Issues that should be addressed but don't block completion:

- Incomplete test coverage for edge cases
- Missing documentation for complex APIs
- Partial implementations of non-critical features
- Known bugs with workarounds
- Deprecated APIs without clear alternatives

### LOW (Info)

Minor issues or recommendations for improvement:

- Style inconsistencies
- Missing optional features
- Documentation typos
- Non-critical performance concerns

## What to Assess

### Missing Exports

- Required functions/classes not exported
- Missing type definitions
- Incomplete module exports
- Missing re-exports from submodules

### Untested Code

- Functions without contract tests
- Edge cases not covered
- Error paths not tested
- Async behavior not verified
- Type constraints not validated

### Breaking Changes

- Changed function signatures
- Removed exports
- Modified return types
- Altered error handling behavior
- Changed default values

### Dependency Issues

- Missing required dependencies
- Version conflicts
- Deprecated dependencies
- Unstable or pre-release dependencies
- Circular dependencies

### Integration Concerns

- Unclear API contracts
- Missing error handling
- Incomplete documentation
- Undocumented assumptions
- Brittle integration points

## Output Format

Provide your risk assessment in this exact format:

```markdown
## Risk Assessment Report: {{PHASE_NAME}}

### Summary
- **Overall Risk Level**: HIGH | MEDIUM | LOW
- **Blocking Issues**: X
- **Warning Issues**: X
- **Info Issues**: X
- **Recommendation**: PROCEED_WITH_CAUTION | PROCEED | DO_NOT_PROCEED

### Risk List

#### HIGH Risks (Blocking)

| ID | Issue | Category | Impact | Recommendation |
|----|-------|----------|--------|----------------|
| R1 | [Description of blocking issue] | [Missing Exports/Breaking Change/etc] | [What it blocks] | [Specific action to resolve] |
| R2 | [Description of blocking issue] | [Category] | [Impact] | [Recommendation] |

#### MEDIUM Risks (Warning)

| ID | Issue | Category | Impact | Recommendation |
|----|-------|----------|--------|----------------|
| W1 | [Description of warning issue] | [Category] | [Impact] | [Recommendation] |
| W2 | [Description of warning issue] | [Category] | [Impact] | [Recommendation] |

#### LOW Risks (Info)

| ID | Issue | Category | Recommendation |
|----|-------|----------|----------------|
| I1 | [Description of info issue] | [Category] | [Recommendation] |
| I2 | [Description of info issue] | [Category] | [Recommendation] |

### Detailed Risk Descriptions

#### R1: [Risk Title]

- **Severity**: HIGH
- **Category**: [Missing Exports/Untested Code/Breaking Changes/etc]
- **Description**: [Detailed explanation]
- **Location**: [File/line reference]
- **Impact**: [What could go wrong]
- **Probability**: High/Medium/Low
- **Recommendation**: [Specific steps to fix]
- **Effort to Fix**: Small/Medium/Large

#### W1: [Risk Title]

- **Severity**: MEDIUM
- **Category**: [Category]
- **Description**: [Detailed explanation]
- **Impact**: [Potential consequences]
- **Recommendation**: [Suggested action]

### Test Analysis

| Test Category | Status | Coverage | Gaps |
|---------------|--------|----------|------|
| Existence Tests | Pass/Fail | X% | [What's missing] |
| Signature Tests | Pass/Fail | X% | [What's missing] |
| Schema Tests | Pass/Fail | X% | [What's missing] |

### Dependency Analysis

| Dependency | Status | Risk Level | Notes |
|------------|--------|------------|-------|
| [dep name] | OK/Warning/Critical | Low/Medium/High | [Notes] |

### Integration Surface Stability

| Export | Stability | Notes |
|--------|-----------|-------|
| [export name] | Stable/Unstable/Experimental | [Notes] |

### Recommendations Summary

#### Must Fix (Before Handoff)

1. [Action item with priority]
2. [Action item with priority]

#### Should Fix (Before Next Phase)

1. [Action item]
2. [Action item]

#### Nice to Have

1. [Action item]
2. [Action item]
```

## Rules

1. **Be objective** - base risks on evidence, not speculation
2. **Prioritize accurately** - don't over/under-state severity
3. **Be specific** - include exact locations and concrete impacts
4. **Suggest fixes** - don't just identify problems, provide solutions
5. **Consider downstream impact** - how will this affect future phases?
6. **Document assumptions** - note what you're assuming about usage

## Example Assessment

### Input

```
PHASE_NAME: "Phase 2: Neo4j Connection"
PHASE_NUMBER: 2
TEST_RESULTS:
  - existence_tests: 5/5 passed
  - signature_tests: 3/4 passed
  - schema_tests: 2/2 passed
  - coverage: 75%

INTEGRATION_SURFACE_JSON:
  - functions: [createClient]
  - classes: [Neo4jClient]
  - types: [Neo4jConfig]

KNOWN_DEPENDENCIES:
  - neo4j-driver: ^5.0.0
  - Internal: Phase 1 (Config)

PREVIOUS_PHASE_STATUS: Complete
```

### Output

```markdown
## Risk Assessment Report: Phase 2: Neo4j Connection

### Summary
- **Overall Risk Level**: MEDIUM
- **Blocking Issues**: 0
- **Warning Issues**: 2
- **Info Issues**: 1
- **Recommendation**: PROCEED_WITH_CAUTION

### Risk List

#### HIGH Risks (Blocking)

None identified.

#### MEDIUM Risks (Warning)

| ID | Issue | Category | Impact | Recommendation |
|----|-------|----------|--------|----------------|
| W1 | Signature test failure for runQuery optional params | Untested Code | Optional parameter handling may not work as expected | Fix test or implementation to handle optional params correctly |
| W2 | Test coverage at 75% (below 80% threshold) | Untested Code | Edge cases may have undetected bugs | Add tests for error handling paths |

#### LOW Risks (Info)

| ID | Issue | Category | Recommendation |
|----|-------|----------|----------------|
| I1 | No documentation for connection timeout behavior | Documentation | Add JSDoc comments explaining timeout behavior |

### Detailed Risk Descriptions

#### W1: Signature Test Failure for runQuery Optional Parameters

- **Severity**: MEDIUM
- **Category**: Untested Code
- **Description**: The signature test for runQuery's optional `params` parameter is failing. The test expects the parameter to be optional but the implementation may require it.
- **Location**: src/lib/neo4j-client.ts:45
- **Impact**: Downstream phases may need to always pass params, reducing API flexibility
- **Probability**: Medium
- **Recommendation**: Verify the params parameter has a default value or is truly optional in the implementation
- **Effort to Fix**: Small

#### W2: Test Coverage Below Threshold

- **Severity**: MEDIUM
- **Category**: Untested Code
- **Description**: Current test coverage is 75%, below the recommended 80% threshold for phase handoff
- **Impact**: Edge cases in error handling may not be caught
- **Probability**: Medium
- **Recommendation**: Add contract tests for error scenarios (connection failures, invalid configs)
- **Effort to Fix**: Medium

### Test Analysis

| Test Category | Status | Coverage | Gaps |
|---------------|--------|----------|------|
| Existence Tests | Pass | 100% | None |
| Signature Tests | Partial | 75% | runQuery optional params |
| Schema Tests | Pass | 100% | None |

### Dependency Analysis

| Dependency | Status | Risk Level | Notes |
|------------|--------|------------|-------|
| neo4j-driver | OK | Low | Stable 5.x release |
| Phase 1 (Config) | OK | Low | Complete and stable |

### Integration Surface Stability

| Export | Stability | Notes |
|--------|-----------|-------|
| Neo4jClient | Stable | Core class, unlikely to change |
| createClient | Stable | Factory function |
| Neo4jConfig | Stable | Interface definition |

### Recommendations Summary

#### Must Fix (Before Handoff)

None - no blocking issues.

#### Should Fix (Before Next Phase)

1. **Fix runQuery signature test** (Priority: High) - Ensure optional params work as documented
2. **Add error handling tests** (Priority: Medium) - Improve coverage to 80%+

#### Nice to Have

1. **Document timeout behavior** - Add inline documentation for connection timeouts
```

Return your risk assessment in the specified format.
