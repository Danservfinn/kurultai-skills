---
name: horde-test
description: Execute comprehensive testing plans using horde-swarm to dispatch parallel test agents across multiple test categories (unit, integration, e2e, performance, security, accessibility). Integrates with horde-implement Phase 6 to provide automated testing and validation with coverage tracking and result aggregation.
version: 1.0.0
author: kurultai
integrations:
  - horde-swarm
  - horde-implement
  - horde-gate-testing
tags:
  - testing
  - validation
  - coverage
  - parallel-execution
---

# horde-test

Execute comprehensive testing plans using parallel test agents across multiple test categories with coverage tracking and result aggregation.

## Overview

horde-test is a testing execution engine that leverages horde-swarm to run comprehensive test suites in parallel. It supports multiple test categories, tracks coverage metrics, and generates unified reports. Designed to integrate seamlessly with horde-implement Phase 6 (Testing and Validation).

## When to Use

Invoke horde-test when you need to:

- Run comprehensive test suites across multiple categories
- Execute tests in parallel for faster feedback
- Track and enforce coverage thresholds
- Validate implementations meet quality criteria
- Generate unified test reports from multiple sources

## Test Categories

| Category | Subagent Type | Purpose |
|----------|--------------|---------|
| unit | python-development:python-pro | Individual component validation |
| integration | backend-development:backend-architect | Cross-component interaction testing |
| e2e | frontend-mobile-development:frontend-developer | Full workflow validation |
| performance | python-development:python-pro | Load and stress testing |
| security | security-auditor | Security vulnerability scanning |
| accessibility | web-accessibility-checker | WCAG compliance testing |

## Input Schema

```yaml
# Test Plan Schema (YAML or JSON)
plan_id: string           # Unique identifier for this test plan
version: string           # Semantic version of the test plan
context:                  # Inherited from horde-implement Phase 6
  implementation_files:   # Files that were implemented
    - string
  test_requirements:      # Specific test requirements
    - string
  coverage_target: number # Target coverage percentage (0-100)

scope:
  include_patterns:       # File patterns to include
    - string
  exclude_patterns:       # File patterns to exclude
    - string
  max_files: number       # Limit number of files to test

suites:                   # Test suites to execute
  - name: string          # Suite name
    category: enum        # unit | integration | e2e | performance | security | accessibility
    files:                # Files to test
      - string
    dependencies:         # Other suites that must pass first
      - string
    config:               # Category-specific configuration
      timeout: number     # Seconds
      retries: number     # Retry attempts on failure
      parallel: boolean   # Run tests in parallel
      coverage: boolean   # Track coverage for this suite

execution:
  max_parallel_suites: number    # Max concurrent test suites
  fail_fast: boolean             # Stop on first failure
  continue_on_failure: boolean   # Continue despite failures
  timeout: number                # Global timeout in seconds

coverage:
  enabled: boolean
  targets:
    line: number        # Line coverage target (0-100)
    branch: number      # Branch coverage target (0-100)
    function: number    # Function coverage target (0-100)
  fail_on_missed: boolean

success_criteria:
  min_pass_rate: number       # Minimum pass percentage (0-100)
  critical_suites:            # Suites that must 100% pass
    - string
  no_critical_failures: boolean
```

## Output Schema

```yaml
# Test Results Schema
execution_id: string      # Unique execution identifier
timestamp: string         # ISO 8601 timestamp
duration_ms: number       # Total execution time

summary:
  total_suites: number
  passed_suites: number
  failed_suites: number
  total_tests: number
  passed_tests: number
  failed_tests: number
  skipped_tests: number
  pass_rate: number       # Percentage

suites:
  - name: string
    category: enum
    status: enum          # passed | failed | skipped | error
    duration_ms: number
    tests:
      - name: string
        status: enum      # passed | failed | skipped | error
        duration_ms: number
        message: string   # Error message if failed
        stack_trace: string
    coverage:
      line: number
      branch: number
      function: number
    artifacts:            # Generated files
      - path: string
        type: string

coverage:
  overall:
    line: number
    branch: number
    function: number
  by_file:
    - file: string
      line: number
      branch: number
      function: number
  meets_targets: boolean

artifacts:
  report_html: string     # Path to HTML report
  report_markdown: string # Path to Markdown report
  coverage_xml: string    # Path to coverage XML
  coverage_json: string   # Path to coverage JSON
  logs: string            # Path to execution logs

success: boolean          # Overall success status
message: string           # Human-readable summary
```

## Usage Examples

### Basic Usage

```yaml
# test-plan.yaml
plan_id: "auth-api-tests"
version: "1.0.0"

scope:
  include_patterns:
    - "src/auth/**/*.py"
    - "tests/auth/**/*.py"

suites:
  - name: "unit-tests"
    category: unit
    files:
      - "tests/auth/test_*.py"
    config:
      coverage: true

  - name: "integration-tests"
    category: integration
    files:
      - "tests/auth/integration/"
    dependencies:
      - "unit-tests"

coverage:
  enabled: true
  targets:
    line: 80
    branch: 70
    function: 90

success_criteria:
  min_pass_rate: 95
```

### Integration with horde-implement

```python
# From horde-implement Phase 6
Skill("horde-test", """
Execute comprehensive test plan for implementation:

Context:
- Implementation files: [list from Phase 3-5]
- Test requirements: unit, integration, e2e
- Coverage target: >80%

Test Plan:
```yaml
plan_id: "implement-phase-6"
version: "1.0.0"
context:
  implementation_files:
    {files_changed}
  coverage_target: 80

suites:
  - name: "unit"
    category: unit
    files: {test_files}
  - name: "integration"
    category: integration
    files: {integration_test_files}

coverage:
  enabled: true
  targets:
    line: 80
    branch: 70

success_criteria:
  min_pass_rate: 100
  no_critical_failures: true
```

Report: Full test results with coverage analysis
""")
```

### Parallel Security Testing

```yaml
plan_id: "security-audit"
version: "1.0.0"

suites:
  - name: "owasp-top-10"
    category: security
    files:
      - "src/"
    config:
      timeout: 600
      parallel: false  # Security tests often sequential

  - name: "dependency-scan"
    category: security
    files:
      - "requirements.txt"
      - "package.json"

success_criteria:
  min_pass_rate: 100
  critical_suites:
    - "owasp-top-10"
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Parse & Validate                                  │
│  - Load test plan                                           │
│  - Validate schema                                          │
│  - Check dependencies form valid DAG                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Build Execution DAG                               │
│  - Topological sort of suites                               │
│  - Identify parallelizable groups                           │
│  - Detect circular dependencies                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Dispatch Swarm                                    │
│  - Launch test agents via horde-swarm                       │
│  - Each category uses appropriate subagent type             │
│  - Track execution progress                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Aggregate Results                                 │
│  - Collect results from all agents                          │
│  - Merge coverage reports                                   │
│  - Calculate pass rates                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: Validate Success Criteria                         │
│  - Check coverage targets                                   │
│  - Verify pass rates                                        │
│  - Validate critical suites                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: Generate Reports                                  │
│  - HTML report for humans                                   │
│  - Markdown for documentation                               │
│  - Coverage XML for CI/CD                                   │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

### Test Plan Validation Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `invalid_schema` | YAML/JSON syntax error | Fix syntax, re-run |
| `missing_required_field` | Required field omitted | Add missing field |
| `invalid_category` | Unknown test category | Use valid category |
| `circular_dependency` | Suite dependencies cycle | Fix dependency graph |

### Execution Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `agent_timeout` | Test exceeded timeout | Increase timeout or optimize |
| `agent_failure` | Subagent crashed | Check logs, retry |
| `coverage_tool_missing` | coverage.py not installed | Install dependencies |
| `resource_exhaustion` | Too many parallel agents | Reduce parallelism |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HORDE_TEST_TIMEOUT` | 300 | Default test timeout (seconds) |
| `HORDE_TEST_MAX_PARALLEL` | 4 | Max parallel test suites |
| `HORDE_TEST_FAIL_FAST` | false | Stop on first failure |
| `HORDE_TEST_COVERAGE_DIR` | .coverage | Coverage data directory |

### Coverage Configuration

```yaml
# .coveragerc integration
coverage:
  config_file: ".coveragerc"  # Use existing config
  omit:
    - "*/tests/*"
    - "*/venv/*"
  include:
    - "src/*"
```

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| horde-implement | Called in Phase 6 for automated testing |
| horde-gate-testing | Validates test results at phase gates |
| horde-swarm | Provides parallel execution engine |
| generate-tests | Can generate test plans for horde-test |

## Success Criteria

horde-test evaluates success based on:

1. **Pass Rate**: Percentage of tests that passed
2. **Coverage Targets**: Line/branch/function coverage thresholds
3. **Critical Suites**: Must achieve 100% pass rate
4. **No Critical Failures**: Security/critical tests must pass

## Output Artifacts

### HTML Report

Interactive report with:
- Test suite summaries
- Individual test details
- Coverage visualization
- Failure stack traces
- Execution timeline

### Markdown Report

GitHub-friendly format:
- Summary tables
- Failed test details
- Coverage badges
- Links to artifacts

### Coverage Reports

- **XML**: Cobertura format for CI/CD integration
- **JSON**: Machine-readable for automation
- **HTML**: Human-readable coverage visualization

## Best Practices

1. **Start with Unit Tests**: Fast feedback, isolated failures
2. **Define Clear Dependencies**: Ensure proper execution order
3. **Set Realistic Timeouts**: Balance speed vs. completeness
4. **Use Coverage Targets**: Enforce quality standards
5. **Review Failed Tests**: Don't just re-run, understand failures
6. **Version Test Plans**: Track changes to test requirements

## Limitations

- Requires horde-swarm for parallel execution
- Coverage tracking requires language-specific tools
- Security testing may require additional configuration
- Performance testing needs representative test data
