# horde-test

Execute comprehensive testing plans using horde-swarm to dispatch parallel test agents across multiple test categories (unit, integration, e2e, performance, security, accessibility).

## Overview

horde-test is a testing execution engine that leverages the horde-swarm skill to run comprehensive test suites in parallel. It is designed to integrate seamlessly with horde-implement Phase 6 (Testing and Validation) but can also be used standalone for any testing workflow.

## Features

- **Multi-Category Testing**: Supports unit, integration, e2e, performance, security, and accessibility tests
- **Parallel Execution**: Dispatches test agents in parallel using horde-swarm
- **Dependency Management**: Build execution DAGs from test suite dependencies
- **Coverage Tracking**: Merge and track line, branch, and function coverage
- **Flexible Configuration**: YAML/JSON test plans with comprehensive options
- **Rich Reporting**: HTML, Markdown, and machine-readable coverage reports

## Installation

```bash
# Via kurultai CLI (when available)
kurultai install horde-test

# Manual installation
git clone https://github.com/kurultai/horde-test.git
ln -s $(pwd)/horde-test ~/.claude/skills/horde-test
```

## Quick Start

### 1. Create a Test Plan

Create a `test-plan.yaml` file:

```yaml
plan_id: "my-project-tests"
version: "1.0.0"

suites:
  - name: "unit-tests"
    category: unit
    files:
      - "tests/unit/"
    config:
      coverage: true

  - name: "integration-tests"
    category: integration
    files:
      - "tests/integration/"
    dependencies:
      - "unit-tests"

coverage:
  enabled: true
  targets:
    line: 80
    branch: 70

success_criteria:
  min_pass_rate: 95
```

### 2. Run the Tests

```python
Skill("horde-test", """
Execute test plan from file: test-plan.yaml
""")
```

## Test Plan Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `plan_id` | string | Unique identifier for the test plan |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `suites` | array | List of test suites to execute |

### Test Suites

Each suite has the following structure:

```yaml
- name: string           # Unique suite name
  category: enum         # unit | integration | e2e | performance | security | accessibility
  files: [string]        # Files/paths to test
  dependencies: [string] # Suites that must pass first (optional)
  config:
    timeout: number      # Seconds (default: 300)
    retries: number      # Retry attempts (default: 0)
    parallel: boolean    # Run in parallel (default: true)
    coverage: boolean    # Track coverage (default: true)
```

### Test Categories

| Category | Subagent Type | Use Case |
|----------|--------------|----------|
| `unit` | python-development:python-pro | Individual component tests |
| `integration` | backend-development:backend-architect | Cross-component tests |
| `e2e` | frontend-mobile-development:frontend-developer | End-to-end workflows |
| `performance` | python-development:python-pro | Load/stress tests |
| `security` | security-auditor | Security scans |
| `accessibility` | web-accessibility-checker | WCAG compliance |

### Coverage Configuration

```yaml
coverage:
  enabled: true
  targets:
    line: 80       # Line coverage target (%)
    branch: 70     # Branch coverage target (%)
    function: 90   # Function coverage target (%)
  fail_on_missed: true  # Fail if targets not met
```

### Success Criteria

```yaml
success_criteria:
  min_pass_rate: 95              # Minimum pass percentage
  critical_suites:               # Suites that must 100% pass
    - "security-scan"
  no_critical_failures: true     # Fail on any critical test failure
```

## Examples

### Basic Example

```yaml
plan_id: "basic-example"
version: "1.0.0"

suites:
  - name: "unit-tests"
    category: unit
    files:
      - "tests/unit/"

coverage:
  enabled: true
  targets:
    line: 80
```

### With Dependencies

```yaml
plan_id: "with-deps"
version: "1.0.0"

suites:
  - name: "unit"
    category: unit
    files: ["tests/unit/"]

  - name: "integration"
    category: integration
    files: ["tests/integration/"]
    dependencies: ["unit"]

  - name: "e2e"
    category: e2e
    files: ["tests/e2e/"]
    dependencies: ["integration"]
```

### Security Audit

```yaml
plan_id: "security-audit"
version: "1.0.0"

suites:
  - name: "sast"
    category: security
    files: ["src/"]

  - name: "dependencies"
    category: security
    files: ["requirements.txt", "package.json"]

success_criteria:
  min_pass_rate: 100
  critical_suites: ["sast", "dependencies"]
```

## Integration with horde-implement

horde-test is automatically invoked by horde-implement in Phase 6:

```python
# From horde-implement SKILL.md Phase 6
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
  implementation_files: {files_changed}
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
""")
```

## Output

### HTML Report

An interactive HTML report is generated with:
- Summary statistics
- Suite-by-suite breakdown
- Individual test results
- Coverage visualization
- Failure details with stack traces

### Markdown Report

GitHub-friendly Markdown format for CI/CD integration.

### Coverage Reports

- **JSON**: Machine-readable coverage data
- **XML**: Cobertura format for CI/CD tools

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HORDE_TEST_TIMEOUT` | 300 | Default test timeout (seconds) |
| `HORDE_TEST_MAX_PARALLEL` | 4 | Max parallel test suites |
| `HORDE_TEST_FAIL_FAST` | false | Stop on first failure |

## Troubleshooting

### Test Plan Validation Errors

```
Error: Missing required fields: suites
```
→ Ensure your test plan has all required fields.

### Circular Dependencies

```
Error: Circular dependency detected: A -> B -> A
```
→ Fix the dependency graph in your test plan.

### Agent Timeouts

```
Error: Suite 'X' timed out after 300s
```
→ Increase the timeout in suite config.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.
