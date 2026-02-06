# horde-test Implementation Plan

> **Phase:** 3 - Implementation Planning
> **Status:** In Progress
> **Created:** 2026-02-05

## Overview

This document provides the detailed implementation plan for the horde-test skill, breaking down the work into discrete, trackable tasks for execution via subagent-driven-development.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         horde-test Skill                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Parser     │  │     DAG      │  │    Swarm Dispatcher      │  │
│  │   Module     │→ │   Builder    │→ │    (horde-swarm)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│         │                 │                      │                  │
│         ▼                 ▼                      ▼                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Result Aggregator                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │  Merge   │  │ Coverage │  │  Report  │  │ Validate │    │   │
│  │  │  Results │→ │  Merge   │→ │ Generate │→ │ Criteria │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Task Breakdown

### Task 1: Create Prompts Directory and Main Prompt

**Description:** Create the prompts directory structure and main execution prompt for horde-test.

**Files to Create:**
- `prompts/main.md` - Main execution prompt

**Acceptance Criteria:**
- [ ] Prompt implements 6-phase execution flow
- [ ] Defines subagent dispatch patterns for each test category
- [ ] Includes result aggregation logic
- [ ] Documents error handling patterns

**Estimated Time:** 30 minutes
**Dependencies:** None

---

### Task 2: Create Test Plan Parser Module

**Description:** Implement YAML/JSON test plan parsing with schema validation.

**Files to Create:**
- `lib/parser.py` - Test plan parser
- `lib/validator.py` - Schema validation

**Acceptance Criteria:**
- [ ] Can parse YAML and JSON test plans
- [ ] Validates against JSON Schema
- [ ] Provides helpful error messages for invalid plans
- [ ] Returns structured TestPlan object

**Estimated Time:** 45 minutes
**Dependencies:** Task 1

---

### Task 3: Create DAG Builder Module

**Description:** Build execution DAG from test suite dependencies.

**Files to Create:**
- `lib/dag.py` - DAG builder and topological sort

**Acceptance Criteria:**
- [ ] Builds dependency graph from suite dependencies
- [ ] Performs topological sort for execution order
- [ ] Detects circular dependencies
- [ ] Identifies parallelizable groups

**Estimated Time:** 45 minutes
**Dependencies:** Task 2

---

### Task 4: Create Swarm Dispatcher

**Description:** Implement horde-swarm integration for parallel test execution.

**Files to Create:**
- `lib/dispatcher.py` - Swarm dispatcher

**Acceptance Criteria:**
- [ ] Maps test categories to subagent types
- [ ] Dispatches agents in parallel groups
- [ ] Tracks execution progress
- [ ] Handles agent timeouts and failures

**Estimated Time:** 60 minutes
**Dependencies:** Task 3

---

### Task 5: Create Result Aggregator

**Description:** Implement result collection and aggregation from multiple agents.

**Files to Create:**
- `lib/aggregator.py` - Result aggregator
- `lib/coverage.py` - Coverage merge utilities

**Acceptance Criteria:**
- [ ] Collects results from all test agents
- [ ] Merges coverage reports
- [ ] Calculates pass rates and statistics
- [ ] Handles partial results from failed agents

**Estimated Time:** 60 minutes
**Dependencies:** Task 4

---

### Task 6: Create Report Generator

**Description:** Generate HTML, Markdown, and coverage reports.

**Files to Create:**
- `lib/reports.py` - Report generator
- `templates/report.html` - HTML report template

**Acceptance Criteria:**
- [ ] Generates HTML report with test details
- [ ] Generates Markdown report for GitHub
- [ ] Generates coverage XML (Cobertura format)
- [ ] Generates coverage JSON for automation

**Estimated Time:** 45 minutes
**Dependencies:** Task 5

---

### Task 7: Create Success Criteria Validator

**Description:** Validate test results against success criteria.

**Files to Create:**
- `lib/validator.py` - Success criteria validator

**Acceptance Criteria:**
- [ ] Checks coverage targets
- [ ] Verifies pass rates
- [ ] Validates critical suites
- [ ] Returns detailed validation report

**Estimated Time:** 30 minutes
**Dependencies:** Task 5

---

### Task 8: Create Main Entry Point

**Description:** Create the main skill entry point that orchestrates all modules.

**Files to Create:**
- `lib/__init__.py` - Package init
- `lib/main.py` - Main orchestrator

**Acceptance Criteria:**
- [ ] Orchestrates all phases
- [ ] Handles errors gracefully
- [ ] Returns structured results
- [ ] Logs execution progress

**Estimated Time:** 45 minutes
**Dependencies:** Tasks 2-7

---

### Task 9: Create Example Test Plans

**Description:** Create example test plans for documentation.

**Files to Create:**
- `examples/basic.yaml` - Basic test plan
- `examples/comprehensive.yaml` - Full-featured example
- `examples/security-only.yaml` - Security-focused example

**Acceptance Criteria:**
- [ ] Examples cover different use cases
- [ ] Examples are valid and tested
- [ ] Examples include comments

**Estimated Time:** 30 minutes
**Dependencies:** Task 8

---

### Task 10: Create README Documentation

**Description:** Create comprehensive README for the skill.

**Files to Create:**
- `README.md` - Skill documentation

**Acceptance Criteria:**
- [ ] Installation instructions
- [ ] Usage examples
- [ ] Configuration reference
- [ ] Troubleshooting guide

**Estimated Time:** 30 minutes
**Dependencies:** Task 9

## Execution Order

```
Task 1 (Prompts)
    │
    ▼
Task 2 (Parser)
    │
    ▼
Task 3 (DAG Builder)
    │
    ▼
Task 4 (Dispatcher)
    │
    ▼
Task 5 (Aggregator) ─────┐
    │                    │
    ▼                    ▼
Task 6 (Reports)    Task 7 (Validator)
    │                    │
    └──────────┬─────────┘
               ▼
          Task 8 (Main)
               │
               ▼
          Task 9 (Examples)
               │
               ▼
          Task 10 (README)
```

## Parallel Opportunities

Tasks 6 and 7 can be executed in parallel after Task 5 completes.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| horde-swarm integration complexity | Test with simple dispatch first |
| Coverage merge issues | Use standard formats (Cobertura) |
| Schema validation errors | Provide detailed error messages |
| Agent timeout handling | Implement retry with backoff |

## Success Criteria

- All 10 tasks completed
- Parser validates test plans correctly
- DAG builder handles dependencies
- Dispatcher executes tests in parallel
- Reports generated in all formats
- Success criteria validation works
- Examples run successfully
