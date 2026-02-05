# Risk Matrix for Phase Gate Testing

Risk assessment criteria and decision matrix for evaluating phase gate results.

---

## Risk Levels

### HIGH

Critical issues that will likely cause integration failures or production problems.

| Category | Examples | Impact |
|----------|----------|--------|
| **Breaking Changes** | Removed or renamed public functions, changed function signatures, modified return types | Consumer code will fail to compile or runtime errors will occur |
| **Missing Critical Exports** | Required functions, classes, or constants not exported | Consumer cannot complete its implementation |
| **Test Failures** | Contract tests fail, integration scenarios fail | Integration contract is violated |
| **Security Vulnerabilities** | Exposed secrets, missing auth checks, injection vulnerabilities | Security breach risk |
| **Data Loss Risk** | Schema migrations that could lose data, missing backup procedures | Irreversible data loss |

**Action Required**: Must fix before proceeding. Gate status: **FAIL**.

---

### MEDIUM

Issues that may cause problems but have workarounds or limited impact.

| Category | Examples | Impact |
|----------|----------|--------|
| **Untested Code** | Code paths not covered by contract tests | Potential bugs in edge cases |
| **Complex Dependencies** | Circular dependencies, tight coupling | Harder to maintain and test |
| **Performance Concerns** | Slow queries, unbounded loops, memory leaks | Degraded performance at scale |
| **Incomplete Error Handling** | Missing error cases, generic error messages | Poor debugging experience |
| **Undocumented Behavior** | Behavior exists but not documented | Misuse by consumers |
| **Deprecated Features** | Reliance on deprecated APIs | Future breaking changes |

**Action Required**: Document risks and mitigation. May proceed with caution. Gate status: **WARN**.

---

### LOW

Minor issues that do not affect functionality but should be addressed for quality.

| Category | Examples | Impact |
|----------|----------|--------|
| **Style Issues** | Inconsistent naming, formatting | Code readability |
| **Missing Documentation** | Undocumented functions, missing examples | Developer experience |
| **Minor Inconsistencies** | Slight deviations from conventions | Maintainability |
| **Missing Tests** | Tests for non-critical paths | Test coverage metrics |
| **Typo in Comments** | Spelling errors in documentation | Professionalism |

**Action Required**: Address when convenient. Does not affect gate status.

---

## Decision Matrix

| Test Results | Risk Level | Decision | Gate Status |
|--------------|------------|----------|-------------|
| All Pass | No risks | Proceed to next phase | **PASS** |
| All Pass | Low risks only | Proceed, address low risks when convenient | **PASS** |
| All Pass | Medium risks | Proceed with caution, document mitigation | **WARN** |
| All Pass | High risks | Do not proceed, fix high risks first | **FAIL** |
| Any Fail | Any | Do not proceed, fix failures first | **FAIL** |

### Decision Rules

1. **Any test failure = FAIL**: If any contract test fails, the gate fails regardless of risk level.
2. **High risk = FAIL**: If any high-risk issue is identified, the gate fails regardless of test results.
3. **Medium risk = WARN**: If tests pass but medium risks exist, the gate warns but allows progression.
4. **Low risk = PASS**: Low risks alone do not affect gate status.

---

## Risk Assessment Process

### Step 1: Identify Risks

Review the integration surface for potential risks:

```markdown
- [ ] Breaking changes to public APIs
- [ ] Missing required exports
- [ ] Security vulnerabilities
- [ ] Performance concerns
- [ ] Untested code paths
- [ ] Documentation gaps
- [ ] Error handling gaps
```

### Step 2: Classify Risks

Assign each risk a level (HIGH, MEDIUM, LOW):

```markdown
| Risk | Level | Rationale |
|------|-------|-----------|
| Function `create_user` renamed to `add_user` | HIGH | Breaking change for Phase 2 |
| Missing validation for edge case | MEDIUM | Has workaround, low probability |
| Typo in documentation | LOW | Does not affect functionality |
```

### Step 3: Determine Gate Status

Apply the decision matrix:

```markdown
Test Results: All Pass
Highest Risk Level: HIGH
Decision: FAIL
Rationale: Breaking change detected despite tests passing (tests may not cover the renamed function)
```

---

## Risk Categories in Detail

### Breaking Changes

Changes that require consumers to modify their code.

**Examples**:
- Renaming functions, classes, or modules
- Changing function signatures (parameters, types)
- Changing return types
- Removing previously exported items
- Changing behavior of existing functions

**Detection**:
- Compare current exports to previous version
- Run consumer compatibility tests
- Review changelog for API changes

**Mitigation**:
- Use deprecation warnings before removal
- Maintain backward compatibility layers
- Provide migration guides

---

### Missing Critical Exports

Required functionality not available to consumers.

**Examples**:
- Function not exported from module
- Class not included in public API
- Constant or configuration missing
- Type definitions not published

**Detection**:
- Check all required exports are present
- Verify exports match plan specification
- Test import statements from consumer perspective

**Mitigation**:
- Add missing exports
- Update module's `__all__` or equivalent
- Publish type definitions

---

### Test Failures

Contract tests that do not pass.

**Examples**:
- Interface contract test fails
- Data contract test fails
- Behavior contract test fails
- Integration scenario fails

**Detection**:
- Run all contract tests
- Review test output for failures
- Check test coverage

**Mitigation**:
- Fix implementation to match contract
- Update tests if contract changed intentionally
- Add missing tests for new functionality

---

### Security Vulnerabilities

Security issues that could be exploited.

**Examples**:
- Hardcoded secrets in code
- Missing authentication checks
- Missing authorization checks
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure deserialization

**Detection**:
- Security scanning tools
- Code review for security patterns
- Penetration testing

**Mitigation**:
- Remove secrets, use environment variables
- Add auth checks to all endpoints
- Use parameterized queries
- Sanitize user input

---

### Data Loss Risk

Potential for losing data during migrations or operations.

**Examples**:
- Schema migration without backup
- DELETE without WHERE clause
- Dropping columns with data
- Truncating tables

**Detection**:
- Review migration scripts
- Test migrations on copy of production data
- Verify rollback procedures

**Mitigation**:
- Always backup before migrations
- Use transactions for atomic changes
- Test rollback procedures
- Perform migrations in stages

---

### Performance Concerns

Issues that may cause performance degradation.

**Examples**:
- N+1 query problems
- Unbounded result sets
- Missing database indexes
- Synchronous calls in async contexts
- Memory leaks

**Detection**:
- Load testing
- Query analysis
- Memory profiling
- Benchmarking

**Mitigation**:
- Add pagination
- Optimize queries
- Add indexes
- Use caching
- Fix memory leaks

---

### Untested Code

Code paths not covered by tests.

**Examples**:
- New functions without tests
- Error handling not tested
- Edge cases not covered
- Integration paths not tested

**Detection**:
- Code coverage reports
- Test review
- Mutation testing

**Mitigation**:
- Add unit tests
- Add integration tests
- Add contract tests
- Increase coverage targets

---

### Documentation Gaps

Missing or incomplete documentation.

**Examples**:
- Functions without docstrings
- APIs without documentation
- Missing usage examples
- Undocumented configuration options

**Detection**:
- Documentation coverage reports
- Review of public APIs
- User feedback

**Mitigation**:
- Add docstrings
- Update API documentation
- Add examples
- Create usage guides

---

## Risk Register Template

```markdown
## Risk Register: Phase N → Phase N+1

### Identified Risks

| ID | Risk | Level | Category | Owner | Mitigation | Status |
|----|------|-------|----------|-------|------------|--------|
| R1 | API endpoint renamed | HIGH | Breaking Change | @dev1 | Add alias | Open |
| R2 | Missing index on user_id | MEDIUM | Performance | @dev2 | Add migration | Open |
| R3 | No examples in docs | LOW | Documentation | @dev3 | Add examples | Open |

### Risk Trends

- **New Risks**: 3
- **Resolved**: 0
- **Open HIGH**: 1
- **Open MEDIUM**: 1
- **Open LOW**: 1

### Mitigation Progress

- [ ] R1: Add backward-compatible alias
- [ ] R2: Create and test index migration
- [ ] R3: Write usage examples
```

---

## Gate Decision Documentation

```markdown
## Gate Decision: Phase N → Phase N+1

### Summary
- **Gate Status**: WARN
- **Test Results**: All Pass (12/12)
- **Highest Risk**: MEDIUM

### Risks Accepted

| Risk | Mitigation | Accepted By |
|------|------------|-------------|
| Missing edge case tests | Will add tests in Phase N+1 | @tech-lead |
| Performance not benchmarked | Will benchmark before production | @tech-lead |

### Conditions for Proceeding

1. Document all medium risks in Phase N+1 ticket
2. Add performance benchmarking to Phase N+1 scope
3. Review risks in next gate

### Sign-off

- [ ] Tech Lead
- [ ] Product Owner
- [ ] QA Lead
```
