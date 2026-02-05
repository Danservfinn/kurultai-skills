# Horde Brainstorming Skill

A 6-phase collaborative design process for complex problem solving, built on the horde-swarm execution engine.

## Overview

The `horde-brainstorming` skill implements a structured, parallel approach to collaborative problem-solving. It breaks down complex design challenges into six distinct phases, each executed by multiple specialized subagents working in parallel, with intelligent aggregation of results between phases.

## The 6-Phase Process

### Phase 1: Problem Exploration
Deeply understand the problem space by analyzing it from multiple perspectives simultaneously.

**Key Activities:**
- Analyze root causes and core issues
- Explore scope and boundaries
- Identify edge cases and exceptions
- Document implicit assumptions
- Define success criteria

**Parallel Agents:** 4 (Analyst, Stakeholder, Technical, Historical perspectives)

### Phase 2: Constraint Identification
Map all boundaries, limitations, and non-negotiable constraints that will shape the solution space.

**Key Activities:**
- Identify technical constraints
- Document organizational limitations
- Note external market/regulatory constraints
- Classify constraints as hard or soft
- Identify challengeable assumptions

**Parallel Agents:** 3 (Technical, Organizational, External perspectives)

### Phase 3: Solution Generation
Generate diverse solution candidates from multiple creative approaches.

**Key Activities:**
- Generate solutions from 6 different approaches
- Ensure diversity in solution types
- Document benefits and risks for each
- Assess complexity and resource needs

**Parallel Agents:** 6 (Conservative, Innovative, Hybrid, Minimal, Comprehensive, Disruptive approaches)

### Phase 4: Solution Evaluation
Evaluate all solutions against established criteria to identify the most promising candidates.

**Key Activities:**
- Score solutions on multiple dimensions
- Assess feasibility and impact
- Analyze risks and trade-offs
- Rank solutions by overall value

**Parallel Agents:** 4 (Feasibility, Impact, Risk, Alignment evaluators)

### Phase 5: Synthesis
Combine the best elements from multiple solutions into cohesive hybrid solutions.

**Key Activities:**
- Identify complementary elements
- Create 2-3 hybrid solutions
- Ensure coherence and feasibility
- Document component provenance

**Parallel Agents:** 3 (Integrator, Optimizer, Validator)

### Phase 6: Refinement
Polish and finalize the design with detailed implementation specifications.

**Key Activities:**
- Add implementation details
- Create step-by-step roadmap
- Define risk mitigation strategies
- Establish success metrics

**Parallel Agents:** 3 (Detailer, Reviewer, Planner)

## When to Use Horde Brainstorming

Use this skill when facing:

- **Complex Feature Design**: Multi-faceted features requiring careful consideration
- **Architecture Decisions**: High-impact technical choices with long-term implications
- **System Redesigns**: Major refactoring or modernization efforts
- **Product Strategy**: Defining direction for significant product initiatives
- **Process Improvements**: Redesigning workflows or operational procedures
- **Integration Planning**: Designing how multiple systems should interact

### Ideal Problem Characteristics

- Multiple valid approaches exist
- Decision has significant long-term impact
- Problem spans multiple domains or concerns
- Trade-offs between competing priorities
- Requires buy-in from multiple stakeholders

## Installation

```bash
kurultai install horde-brainstorming
```

This will install the skill and its dependency on `horde-swarm`.

## Usage

### Basic Usage

```yaml
skill: horde-brainstorming
problem_statement: |
  Design a caching strategy for our API that balances
  performance with data consistency requirements.
context:
  domain: backend-architecture
  constraints:
    - "Sub-50ms response time requirement"
    - "Data consistency for financial transactions"
  success_criteria:
    - "Cache hit rate > 90%"
    - "Zero data inconsistency for transactions"
```

### Advanced Configuration

```yaml
skill: horde-brainstorming
title: "API Caching Strategy Design"
problem_statement: |
  Design a caching strategy for our API that balances
  performance with data consistency requirements.

context:
  domain: backend-architecture
  constraints:
    - "Sub-50ms response time requirement"
    - "Data consistency for financial transactions"
    - "Must work with existing Redis infrastructure"
    - "Budget for max 500MB cache per node"
  success_criteria:
    - "Cache hit rate > 90%"
    - "Zero data inconsistency for transactions"
    - "Horizontal scalability"

phases:
  problem_exploration:
    parallel_agents: 4
    perspectives:
      - analyst
      - stakeholder
      - technical
      - historical

  constraint_identification:
    parallel_agents: 3
    categories:
      - technical
      - organizational
      - external

  solution_generation:
    parallel_agents: 6
    approaches:
      - conservative
      - innovative
      - hybrid
      - minimal
      - comprehensive
      - disruptive

  solution_evaluation:
    parallel_agents: 4
    evaluators:
      - feasibility
      - impact
      - risk
      - alignment

  synthesis:
    parallel_agents: 3
    synthesizers:
      - integrator
      - optimizer
      - validator

  refinement:
    parallel_agents: 3
    refiners:
      - detailer
      - reviewer
      - planner

swarm:
  engine: horde-swarm
  max_parallel_phases: 2
  aggregation_timeout: 300
  output_format: structured_yaml
```

## Integration with Horde-Swarm

The horde-brainstorming skill is built on top of the horde-swarm execution engine. It uses:

- **Parallel Execution**: Multiple subagents work simultaneously within each phase
- **Hierarchical Aggregation**: Results from parallel agents are intelligently combined
- **Phase Dependencies**: Later phases automatically receive outputs from earlier phases
- **Structured Output**: Consistent YAML output format for programmatic use

### Execution Flow

```
Phase 1 & 2 (Parallel)
    |
    v
Phase 3 (Solution Generation)
    |
    v
Phase 4 (Evaluation)
    |
    v
Phase 5 (Synthesis)
    |
    v
Phase 6 (Refinement)
```

Phases 1 and 2 can run in parallel as they both only depend on the initial problem statement. Subsequent phases depend on previous phase outputs.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_parallel_phases` | integer | 2 | Maximum phases to run concurrently |
| `max_agents_per_phase` | integer | 6 | Maximum subagents per phase |
| `aggregation_timeout` | integer | 300 | Seconds to wait for aggregation |
| `preserve_intermediates` | boolean | true | Keep intermediate outputs |
| `output_format` | string | structured_yaml | Output format (yaml/json) |

## Sample Outputs

### Example: API Rate Limiting Design

**Input:**
```yaml
problem_statement: |
  Design a rate limiting system for our public API that
  prevents abuse while not impacting legitimate users.
```

**Phase 1 Output (Problem Exploration):**
```yaml
problem_definition: |
  The API needs protection against abusive traffic patterns
  while maintaining excellent experience for legitimate users
  with varying usage patterns.

key_questions:
  - What defines "abusive" vs "legitimate" usage?
  - How should different user tiers be treated?
  - What happens when limits are exceeded?
  - How can users monitor their usage?

assumptions:
  - Rate limits will vary by user tier
  - Some endpoints need stricter limits than others
  - Users should receive clear feedback when limited

success_criteria:
  - 99.9% of legitimate requests succeed
  - <0.1% false positive rate
  - Clear communication to limited users
  - Sub-millisecond overhead
```

**Phase 3 Output (Solution Generation):**
```yaml
solutions:
  - name: "Token Bucket per User"
    approach: conservative
    description: "Classic token bucket algorithm per user ID"
    complexity: Low
    benefits:
      - Well-understood algorithm
      - Allows traffic bursts
      - Easy to implement
    risks:
      - Requires distributed state
      - Memory overhead per user

  - name: "AI-Based Anomaly Detection"
    approach: innovative
    description: "ML model detects abnormal usage patterns"
    complexity: High
    benefits:
      - Adapts to usage patterns
      - Low false positive rate
    risks:
      - Complex to implement
      - Requires training data

  # ... more solutions
```

**Phase 6 Output (Refinement - Final):**
```yaml
final_design:
  name: "Hybrid Tiered Rate Limiting"
  description: |
    Multi-layer approach combining token bucket for standard
    limits with anomaly detection for abuse prevention.

  components:
    - name: "Token Bucket Service"
      implementation: "Redis-based sliding window"
      specs:
        - "Default: 100 req/min per user"
        - "Premium: 1000 req/min per user"
        - "Enterprise: Custom limits"

    - name: "Anomaly Detector"
      implementation: "Statistical outlier detection"
      specs:
        - "Tracks request patterns per IP + User"
        - "Flags >3 standard deviations from mean"
        - "Temporary blocks with exponential backoff"

    - name: "Response Handler"
      implementation: "Middleware"
      specs:
        - "429 status with Retry-After header"
        - "Rate limit headers in all responses"
        - "Dashboard for users to view limits"

implementation_plan:
  phase_1:
    duration: "1 week"
    tasks:
      - "Implement token bucket in Redis"
      - "Add middleware for rate limit headers"

  phase_2:
    duration: "2 weeks"
    tasks:
      - "Build anomaly detection service"
      - "Integrate with existing auth"

  phase_3:
    duration: "1 week"
    tasks:
      - "User dashboard for rate limits"
      - "Documentation and rollout"

success_metrics:
  - metric: "False positive rate"
    target: "< 0.1%"
  - metric: "P99 response time overhead"
    target: "< 1ms"
  - metric: "Abuse reduction"
    target: "> 95%"
```

## Best Practices

### 1. Craft Clear Problem Statements
A well-defined problem statement is crucial. Include:
- What needs to be solved
- Why it matters
- Any known context or constraints

### 2. Choose Appropriate Parallelism
- Simple problems: Reduce agents per phase
- Complex problems: Use maximum agents
- Time-sensitive: Reduce aggregation timeout

### 3. Review Intermediate Outputs
Check outputs from each phase before proceeding:
- Phase 1: Is the problem well-understood?
- Phase 2: Are all constraints captured?
- Phase 3: Is there sufficient diversity?

### 4. Iterate When Needed
For critical decisions, run multiple rounds:
- First round: Broad exploration
- Second round: Deep dive on top solutions
- Third round: Validate final design

### 5. Document Assumptions
Make all assumptions explicit so they can be:
- Validated with stakeholders
- Updated as new information arrives
- Challenged if circumstances change

## Troubleshooting

### Low Solution Diversity
**Symptoms:** Solutions are too similar
**Solutions:**
- Increase number of generation agents
- Use more diverse approach types
- Add explicit constraints to force creativity

### Poor Aggregation
**Symptoms:** Phase outputs don't combine well
**Solutions:**
- Check that output formats match expected schemas
- Increase aggregation timeout
- Review and clarify aggregation rules

### Incomplete Results
**Symptoms:** Missing sections in final output
**Solutions:**
- Ensure all phases complete successfully
- Check phase dependencies are satisfied
- Review swarm configuration

## Dependencies

- **horde-swarm**: ^1.0.0 (execution engine)

## Repository

https://github.com/kurultai/horde-brainstorming

## License

MIT License - See repository for details.

## Contributing

Contributions welcome! Please see the repository for guidelines.

## Support

For issues or questions:
- Open an issue in the repository
- Check existing documentation
- Review example workflows in `/examples`
