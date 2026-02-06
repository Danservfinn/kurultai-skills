# horde-test Skill Specification

> **Version:** 1.0.0
> **Status:** Specification Complete
> **Last Updated:** 2026-02-05

## 1. Skill Overview

**Name:** horde-test
**Description:** Execute comprehensive testing plans using horde-swarm to dispatch parallel test agents across multiple test categories (unit, integration, e2e, performance, security, accessibility).
**Engine:** horde-swarm
**Integration:** horde-implement Phase 6 (Testing and Validation)

### 1.1 Purpose

horde-test provides automated testing execution with parallel agent dispatch, enabling comprehensive validation of implementations across multiple dimensions:
- **Correctness** via unit and integration tests
- **Security** via vulnerability scanning
- **Performance** via load and stress tests
- **Accessibility** via WCAG compliance checks

### 1.2 Target Users

- Developers implementing features who need validation
- Team leads managing code quality gates
- QA engineers defining test strategies
- DevOps engineers automating CI/CD pipelines

## 2. Interface Specification

### 2.1 Input Contract

**Invocation Method:** `Skill("horde-test", prompt)`

**Input Schema (YAML/JSON Test Plan):**

```yaml
plan_id: string           # Required: Unique identifier
version: string           # Required: Semantic version (e.g., "1.0.0")
context:                  # Optional: Inherited from horde-implement
  implementation_files: [string]
  test_requirements: [string]
  coverage_target: number (0-100)

scope:                    # Optional: File filtering
  include_patterns: [string]  # Glob patterns
  exclude_patterns: [string]  # Glob patterns
  max_files: number

suites:                   # Required: Test suites to execute
  - name: string          # Required: Unique suite name
    category: enum        # Required: unit | integration | e2e | performance | security | accessibility
    files: [string]       # Required: Files/paths to test
    dependencies: [string] # Optional: Suite names that must pass first
    config:               # Optional: Suite-specific config
      timeout: number     # Seconds (default: 300)
      retries: number     # Retry attempts (default: 0)
      parallel: boolean   # Run in parallel (default: true)
      coverage: boolean   # Track coverage (default: true)

execution:                # Optional: Execution configuration
  max_parallel_suites: number  # Max concurrent suites (default: 4)
  fail_fast: boolean           # Stop on first failure (default: false)
  continue_on_failure: boolean # Continue despite failures (default: true)
  timeout: number              # Global timeout seconds (default: 3600)

coverage:                 # Optional: Coverage configuration
  enabled: boolean        # Default: true
  targets:
    line: number          # Line coverage target (default: 80)
    branch: number        # Branch coverage target (default: 70)
    function: number      # Function coverage target (default: 90)
  fail_on_missed: boolean # Fail if targets not met (default: true)

success_criteria:         # Required: Success conditions
  min_pass_rate: number       # Minimum pass percentage (default: 100)
  critical_suites: [string]   # Suites that must 100% pass
  no_critical_failures: boolean # Fail on critical test failure (default: true)
```

### 2.2 Output Contract

**Output Schema (Test Results):**

```yaml
execution_id: string      # Unique execution identifier (UUID)
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
  pass_rate: number       # Percentage (0-100)

suites:
  - name: string
    category: enum        # unit | integration | e2e | performance | security | accessibility
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
    artifacts:
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
  coverage_xml: string    # Path to coverage XML (Cobertura)
  coverage_json: string   # Path to coverage JSON
  logs: string            # Path to execution logs

success: boolean          # Overall success status
message: string           # Human-readable summary
```

### 2.3 Validation Rules

**Required Field Validation:**
- `plan_id` must be non-empty string
- `version` must follow semantic versioning (e.g., "1.0.0")
- `suites` must contain at least one suite
- Each suite must have `name`, `category`, and `files`

**Category Validation:**
- Valid categories: `unit`, `integration`, `e2e`, `performance`, `security`, `accessibility`

**Dependency Validation:**
- Dependencies must reference existing suite names
- Circular dependencies are detected and rejected

**Coverage Target Validation:**
- All percentage values must be 0-100
- Line coverage >= Branch coverage (enforced warning)

## 3. Subagent Type Mapping

Each test category maps to a specialized subagent type:

| Category | Subagent Type | Expertise |
|----------|---------------|-----------|
| `unit` | `python-development:python-pro` | Python testing, pytest, fixtures |
| `integration` | `backend-development:backend-architect` | API testing, database integration |
| `e2e` | `frontend-mobile-development:frontend-developer` | End-to-end workflows, UI testing |
| `performance` | `python-development:python-pro` | Load testing, profiling, benchmarks |
| `security` | `security-auditor` | OWASP, vulnerability scanning |
| `accessibility` | `web-accessibility-checker` | WCAG compliance, ARIA |

## 4. Execution Flow

### 4.1 Phase 1: Parse & Validate

1. Load test plan from YAML/JSON
2. Validate against schema
3. Check required fields present
4. Validate category values
5. Build dependency graph
6. Detect circular dependencies

### 4.2 Phase 2: Build Execution DAG

1. Topological sort of suites based on dependencies
2. Identify parallelizable groups (suites with no inter-dependencies)
3. Calculate execution waves

### 4.3 Phase 3: Dispatch Swarm

1. For each execution wave:
   - Map suite categories to subagent types
   - Dispatch `Task(subagent_type=..., prompt=...)` for each suite
   - Track execution progress
   - Enforce timeouts

### 4.4 Phase 4: Aggregate Results

1. Collect results from all agents
2. Merge coverage reports
3. Calculate pass rates per suite and overall
4. Identify failed/skipped tests

### 4.5 Phase 5: Validate Success Criteria

1. Check coverage targets (line, branch, function)
2. Verify pass rates meet minimum threshold
3. Validate critical suites passed
4. Check for critical failures

### 4.6 Phase 6: Generate Reports

1. Generate HTML report with interactive visualization
2. Generate Markdown report for documentation
3. Export coverage in XML (Cobertura) format
4. Export coverage in JSON format

## 5. Error Handling

### 5.1 Validation Errors

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `INVALID_SCHEMA` | YAML/JSON syntax error | Fix syntax, re-run |
| `MISSING_REQUIRED_FIELD` | Required field omitted | Add missing field |
| `INVALID_CATEGORY` | Unknown test category | Use valid category from list |
| `CIRCULAR_DEPENDENCY` | Suite dependencies form cycle | Fix dependency graph |
| `INVALID_DEPENDENCY` | Dependency references non-existent suite | Fix suite name |
| `INVALID_COVERAGE_TARGET` | Coverage value outside 0-100 | Use valid percentage |

### 5.2 Execution Errors

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `AGENT_TIMEOUT` | Test exceeded timeout | Increase timeout or optimize tests |
| `AGENT_FAILURE` | Subagent crashed | Check logs, retry with fixes |
| `COVERAGE_TOOL_MISSING` | coverage.py not installed | Install Python coverage tools |
| `RESOURCE_EXHAUSTION` | Too many parallel agents | Reduce max_parallel_suites |
| `MERGE_CONFLICT` | Coverage merge failed | Check coverage file formats |

## 6. Integration Points

### 6.1 horde-implement Phase 6

horde-test is automatically invoked by horde-implement during Phase 6 (Testing and Validation):

```python
# From horde-implement
Skill("horde-test", f"""
Execute comprehensive test plan for implementation:

Context:
- Implementation files: {files_changed}
- Coverage target: {coverage_target}

Test Plan:
```yaml
plan_id: "implement-phase-6-{timestamp}"
version: "1.0.0"
context:
  implementation_files: {implementation_files}
  coverage_target: {coverage_target}
suites: {test_suites}
coverage:
  enabled: true
  targets:
    line: {line_target}
    branch: {branch_target}
success_criteria:
  min_pass_rate: 100
  no_critical_failures: true
```
""")
```

### 6.2 horde-gate-testing

horde-gate-testing validates test results at phase gates between implementation phases.

### 6.3 horde-swarm

horde-test uses horde-swarm as its execution engine for parallel agent dispatch.

## 7. Configuration

### 7.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HORDE_TEST_TIMEOUT` | 300 | Default test timeout (seconds) |
| `HORDE_TEST_MAX_PARALLEL` | 4 | Max parallel test suites |
| `HORDE_TEST_FAIL_FAST` | false | Stop on first failure |
| `HORDE_TEST_COVERAGE_DIR` | .coverage | Coverage data directory |

### 7.2 Coverage Integration

Supports `.coveragerc` configuration:

```ini
[run]
source = src
omit = */tests/*, */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
```

## 8. Success Criteria

horde-test evaluates success based on:

1. **Pass Rate**: Percentage of tests that passed >= `min_pass_rate`
2. **Coverage Targets**: Line/branch/function coverage >= targets
3. **Critical Suites**: All suites in `critical_suites` must 100% pass
4. **No Critical Failures**: No failures in security/critical tests

**Overall Success:** All criteria must be met for `success: true`

## 9. Limitations

- Requires horde-swarm for parallel execution
- Coverage tracking requires language-specific tools (coverage.py for Python)
- Security testing may require additional environment configuration
- Performance testing needs representative test data

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-05 | Initial specification |

## 11. Appendix: JSON Schema

### Test Plan JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Horde Test Plan",
  "type": "object",
  "required": ["plan_id", "version", "suites", "success_criteria"],
  "properties": {
    "plan_id": { "type": "string", "minLength": 1 },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "context": {
      "type": "object",
      "properties": {
        "implementation_files": { "type": "array", "items": { "type": "string" } },
        "test_requirements": { "type": "array", "items": { "type": "string" } },
        "coverage_target": { "type": "number", "minimum": 0, "maximum": 100 }
      }
    },
    "scope": {
      "type": "object",
      "properties": {
        "include_patterns": { "type": "array", "items": { "type": "string" } },
        "exclude_patterns": { "type": "array", "items": { "type": "string" } },
        "max_files": { "type": "integer", "minimum": 1 }
      }
    },
    "suites": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "category", "files"],
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "category": { "enum": ["unit", "integration", "e2e", "performance", "security", "accessibility"] },
          "files": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
          "dependencies": { "type": "array", "items": { "type": "string" } },
          "config": {
            "type": "object",
            "properties": {
              "timeout": { "type": "integer", "minimum": 1 },
              "retries": { "type": "integer", "minimum": 0 },
              "parallel": { "type": "boolean" },
              "coverage": { "type": "boolean" }
            }
          }
        }
      }
    },
    "execution": {
      "type": "object",
      "properties": {
        "max_parallel_suites": { "type": "integer", "minimum": 1 },
        "fail_fast": { "type": "boolean" },
        "continue_on_failure": { "type": "boolean" },
        "timeout": { "type": "integer", "minimum": 1 }
      }
    },
    "coverage": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "targets": {
          "type": "object",
          "properties": {
            "line": { "type": "number", "minimum": 0, "maximum": 100 },
            "branch": { "type": "number", "minimum": 0, "maximum": 100 },
            "function": { "type": "number", "minimum": 0, "maximum": 100 }
          }
        },
        "fail_on_missed": { "type": "boolean" }
      }
    },
    "success_criteria": {
      "type": "object",
      "required": ["min_pass_rate"],
      "properties": {
        "min_pass_rate": { "type": "number", "minimum": 0, "maximum": 100 },
        "critical_suites": { "type": "array", "items": { "type": "string" } },
        "no_critical_failures": { "type": "boolean" }
      }
    }
  }
}
```
