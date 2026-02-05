# Horde Swarm

The foundational execution engine for parallel subagent dispatch in the Kurultai CLI.

## Overview

Horde Swarm is the core engine that powers all other horde skills. It provides a robust, configurable parallel execution layer for multi-agent workflows, enabling complex tasks to be broken down and executed simultaneously by specialized subagents.

## What is Horde Swarm?

Horde Swarm implements the **Decompose → Dispatch → Aggregate → Synthesize** pattern:

1. **Decompose**: Break complex tasks into independent sub-tasks
2. **Dispatch**: Execute sub-tasks in parallel using specialized subagents
3. **Aggregate**: Collect and combine results from all subagents
4. **Synthesize**: Produce a coherent final output

Unlike traditional sequential execution, Horde Swarm leverages parallelism to dramatically reduce execution time for complex, multi-faceted tasks.

## When to Use Horde Swarm

Use Horde Swarm when you need to:

- **Analyze large codebases** across multiple domains (architecture, security, performance)
- **Generate multiple content variants** in parallel (documentation, tests, code)
- **Review code** from multiple perspectives simultaneously
- **Process large datasets** by partitioning work across agents
- **Execute complex workflows** with independent sub-tasks
- **Improve reliability** through redundant parallel execution

### Ideal Use Cases

| Scenario | Subagents | Benefit |
|----------|-----------|---------|
| Full codebase audit | Architecture, Security, Performance, QA | Complete assessment in parallel |
| Multi-file refactoring | One agent per file/module | Faster refactoring |
| Documentation generation | API docs, Guides, READMEs | Consistent documentation |
| Test generation | Unit tests, Integration tests, E2E tests | Comprehensive coverage |
| Security review | OWASP checks, Dependency audit, Secret scan | Thorough security analysis |

## How to Use It

### Installation

```bash
kurultai install horde-swarm
```

### Basic Usage

```yaml
# In your skill or workflow
engine: horde-swarm

task: "Analyze this codebase for production readiness"

subagents:
  - name: "backend_review"
    type: "backend-development:backend-architect"
    task: "Review backend architecture"
    context:
      files: ["/src/**/*.py"]

  - name: "security_review"
    type: "security-audit:security-reviewer"
    task: "Perform security audit"
    context:
      files: ["/src/**/*.py"]

  - name: "performance_review"
    type: "performance-engineer:performance-analyst"
    task: "Analyze performance"
    context:
      files: ["/src/**/*.py"]
```

### Advanced Configuration

```yaml
engine: horde-swarm

execution:
  max_parallel_agents: 5
  default_timeout: 600
  continue_on_failure: true
  aggregation_strategy: "merge"

retry:
  enabled: true
  max_attempts: 3
  backoff_strategy: "exponential"

subagents:
  - name: "agent_1"
    type: "backend-development:backend-architect"
    task: "Task description"
    context: {...}
    timeout: 300
    retries: 2
    priority: 1
```

### Example: Codebase Analysis

```yaml
# Complete example: Production readiness review
engine: horde-swarm

task: "Perform production readiness review"

decomposition:
  strategy: "by_domain"
  domains: ["architecture", "security", "performance", "testing"]

subagents:
  - name: "arch_review"
    type: "backend-development:backend-architect"
    task: |
      Review the codebase architecture focusing on:
      - Service boundaries and responsibilities
      - API design patterns
      - Data flow and integration points
      - Scalability considerations
    context:
      files: ["/src/api/**/*.py", "/src/services/**/*.py"]
      focus_areas:
        - REST API conventions
        - Microservices boundaries
        - Database access patterns

  - name: "security_review"
    type: "security-audit:security-reviewer"
    task: |
      Perform comprehensive security audit:
      - Check for OWASP Top 10 vulnerabilities
      - Review authentication and authorization
      - Validate input sanitization
      - Check for hardcoded secrets
    context:
      files: ["/src/**/*.py"]
      check_list:
        - OWASP Top 10
        - Authentication flows
        - Authorization checks
        - Input validation
        - Secrets management

  - name: "perf_review"
    type: "performance-engineer:performance-analyst"
    task: |
      Analyze performance characteristics:
      - Database query efficiency
      - API response times
      - Resource utilization patterns
      - Caching strategies
    context:
      files: ["/src/**/*.py"]
      metrics:
        - query_complexity
        - n_plus_one_detection
        - caching_coverage

  - name: "test_review"
    type: "qa-engineer:test-analyst"
    task: |
      Review test coverage and quality:
      - Unit test coverage
      - Integration test completeness
      - Test data management
      - Mocking strategies
    context:
      files: ["/tests/**/*.py"]
      coverage_threshold: 80

aggregation:
  strategy: "merge"
  output_schema:
    executive_summary: "string"
    architecture_findings: "array"
    security_findings: "array"
    performance_findings: "array"
    test_findings: "array"
    recommendations: "array"
    confidence_level: "high|medium|low"
```

### Example: Parallel Content Generation

```yaml
engine: horde-swarm

task: "Generate comprehensive documentation"

subagents:
  - name: "api_docs"
    type: "technical-writer:api-documentarian"
    task: "Generate API reference documentation"
    context:
      openapi_spec: "/docs/openapi.yaml"

  - name: "guide_docs"
    type: "technical-writer:guide-author"
    task: "Write getting started guide"
    context:
      target_audience: "developers"
      complexity: "beginner"

  - name: "readme"
    type: "technical-writer:readme-specialist"
    task: "Create project README"
    context:
      include_badges: true
      sections: ["installation", "usage", "contributing"]

aggregation:
  strategy: "concatenate"
  output_file: "documentation_bundle.md"
```

## Integration with Other Horde Skills

Horde Swarm serves as the execution engine for specialized horde skills:

### horde-analyze
```yaml
skill: horde-analyze
engine: horde-swarm

# horde-analyze configures subagents for code analysis
# horde-swarm handles parallel execution
```

### horde-generate
```yaml
skill: horde-generate
engine: horde-swarm

# horde-generate configures subagents for content generation
# horde-swarm handles parallel dispatch
```

### horde-test
```yaml
skill: horde-test
engine: horde-swarm

# horde-test configures subagents for test execution
# horde-swarm handles parallel test runs
```

### horde-review
```yaml
skill: horde-review
engine: horde-swarm

# horde-review configures subagents for code review
# horde-swarm handles parallel review dispatch
```

## Configuration Options

### Global Configuration

Configure Horde Swarm in `~/.kurultai/config.yaml`:

```yaml
skills:
  horde-swarm:
    max_parallel_agents: 10
    default_timeout: 300
    enable_caching: true
    continue_on_failure: false
    retry:
      enabled: true
      max_attempts: 3
      backoff_strategy: exponential
```

### Per-Invocation Configuration

Override global settings for specific invocations:

```yaml
engine: horde-swarm

execution:
  max_parallel_agents: 5        # Limit concurrent agents
  default_timeout: 600          # Increase timeout
  continue_on_failure: true     # Continue on subagent failure
  aggregation_strategy: "vote"  # Use voting aggregation
```

### Configuration Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_parallel_agents` | integer | 10 | Maximum concurrent subagents (1-50) |
| `default_timeout` | integer | 300 | Default subagent timeout in seconds |
| `enable_caching` | boolean | true | Cache identical subagent calls |
| `continue_on_failure` | boolean | false | Continue execution if subagents fail |
| `max_failures` | integer | 3 | Maximum failures before aborting |
| `retry.enabled` | boolean | true | Enable automatic retries |
| `retry.max_attempts` | integer | 3 | Maximum retry attempts |
| `retry.backoff_strategy` | string | "exponential" | Backoff: "fixed", "exponential", "linear" |

### Aggregation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `merge` | Combine results into unified structure | Multi-domain analysis |
| `concatenate` | Join results sequentially | Documentation generation |
| `vote` | Majority vote from redundant agents | Reliability improvement |
| `reduce` | Progressive combination with function | Data processing |

## Best Practices

### Task Decomposition

1. **Ensure Independence**: Design sub-tasks that can execute without blocking each other
2. **Right Granularity**: Not too small (overhead) nor too large (underutilization)
3. **Clear Boundaries**: Define well-defined inputs and outputs for each sub-task
4. **Minimize Dependencies**: Reduce data dependencies between subagents

### Subagent Configuration

1. **Specific Tasks**: Give each subagent a clear, achievable goal
2. **Scoped Context**: Provide relevant context without overwhelming
3. **Appropriate Timeouts**: Set realistic timeouts based on task complexity
4. **Type Selection**: Choose subagent types that match the task domain

### Error Handling

1. **Define Strategy**: Choose appropriate failure mode for your use case
2. **Handle Partial Results**: Design for graceful degradation
3. **Monitor Failures**: Track which subagents fail and why
4. **Set Thresholds**: Configure max_failures based on tolerance

### Performance Optimization

1. **Limit Parallelism**: Don't exceed system capacity
2. **Use Caching**: Enable caching for repeated operations
3. **Optimize Context**: Pass only necessary files and data
4. **Monitor Resources**: Watch memory and CPU usage

### Result Aggregation

1. **Define Schema**: Specify expected output format upfront
2. **Handle Conflicts**: Define rules for resolving conflicting results
3. **Preserve Metadata**: Track which subagent produced which result
4. **Validate Output**: Ensure aggregated result meets quality criteria

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Horde Swarm Engine                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Decomposer  │→│   Dispatcher  │→│  Aggregator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                 ↓                  ↓              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Parallel Execution Layer                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │Agent 1  │ │Agent 2  │ │Agent 3  │ │Agent N  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Retry Handler │  │Error Handler │  │   Synthesizer │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

#### Subagent Timeouts
```yaml
# Increase timeout for slow operations
subagents:
  - name: "slow_agent"
    timeout: 600  # 10 minutes
```

#### Memory Issues
```yaml
# Reduce parallel agents
execution:
  max_parallel_agents: 3
```

#### Partial Failures
```yaml
# Continue on failure and capture partial results
execution:
  continue_on_failure: true
error_handling:
  capture_partial_results: true
```

#### Inconsistent Results
```yaml
# Use voting strategy for reliability
aggregation:
  strategy: "vote"
  min_agents: 3
```

## Contributing

Contributions to Horde Swarm are welcome! Please see the [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Repository

https://github.com/kurultai/horde-swarm
