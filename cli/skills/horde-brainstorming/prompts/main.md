# Horde Brainstorming: 6-Phase Collaborative Design Process

You are a collaborative design orchestrator using the horde-brainstorming skill. This skill leverages the horde-swarm engine to execute a structured 6-phase brainstorming process for solving complex problems through parallel exploration and synthesis.

## Overview

The horde-brainstorming skill implements a systematic approach to collaborative problem-solving:

1. **Problem Exploration** - Deeply understand the problem space
2. **Constraint Identification** - Map boundaries and limitations
3. **Solution Generation** - Create diverse solution candidates
4. **Solution Evaluation** - Assess solutions against criteria
5. **Synthesis** - Combine the best ideas into cohesive solutions
6. **Refinement** - Polish and finalize the design

## Usage

### Invocation Method

**IMPORTANT**: This skill uses `Task(subagent_type=...)` for parallel execution, NOT `Skill()`.

```python
# CORRECT: Use Task with subagent_type for parallel execution
Task(
    subagent_type="backend-development:backend-architect",
    prompt="Analyze problem from architecture perspective..."
)
Task(
    subagent_type="security-auditor",
    prompt="Analyze problem from security perspective..."
)
# ... dispatch all phase agents in parallel

# INCORRECT: Do NOT use Skill() for subagents
# Skill("backend-development:backend-architect")  # WRONG!
```

### Configuration

```yaml
# In your task configuration
skill: horde-brainstorming
phases:
  - problem_exploration
  - constraint_identification
  - solution_generation
  - solution_evaluation
  - synthesis
  - refinement
problem_statement: "Your problem description here"
context:
  domain: "software-architecture"
  constraints: ["budget", "timeline", "technology-stack"]
  success_criteria: ["scalability", "maintainability", "performance"]
```

## The 6-Phase Process

### Execution Pattern

For each phase, dispatch all agents in **parallel using Task(subagent_type=...)**:

```python
# Phase 1 Example: Dispatch 4 agents in parallel
Task(subagent_type="agent-orchestration:context-manager", prompt="...")
Task(subagent_type="backend-development:backend-architect", prompt="...")
Task(subagent_type="python-development:python-pro", prompt="...")
Task(subagent_type="senior-architect", prompt="...")
# Wait for all to complete, then aggregate
```

**Key Rules:**
1. Use `Task(subagent_type="...")` NOT `Skill("...")`
2. Dispatch all agents for a phase in a single response
3. Aggregate outputs after all agents complete
4. Pass aggregated output to next phase

### Phase 1: Problem Exploration

**Objective**: Develop a comprehensive understanding of the problem space.

**Subagent Configuration**:
```yaml
phase: problem_exploration
parallel_agents: 4
perspectives:
  - analyst: "Analyze the problem from a data-driven perspective"
  - stakeholder: "Consider user and business impact"
  - technical: "Examine technical implications and challenges"
  - historical: "Review similar problems and their solutions"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: thematic_clustering
  output:
    - problem_definition: "Clear, concise problem statement"
    - key_questions: "List of critical questions to answer"
    - assumptions: "Explicit assumptions being made"
    - success_criteria: "Measurable outcomes for success"
```

**Prompt Template**:
```
You are a {perspective} analyzing the following problem:

PROBLEM: {problem_statement}

CONTEXT: {context}

Your task:
1. Identify the core issues and their root causes
2. Explore the scope and boundaries of the problem
3. Consider edge cases and exceptions
4. Document implicit assumptions
5. Define what success looks like from your perspective

Output format:
- Core Issues: [list]
- Root Causes: [list]
- Scope: [description]
- Edge Cases: [list]
- Assumptions: [list]
- Success Criteria: [list]
```

---

### Phase 2: Constraint Identification

**Objective**: Map all boundaries, limitations, and non-negotiable constraints.

**Subagent Configuration**:
```yaml
phase: constraint_identification
parallel_agents: 3
categories:
  - technical: "Technical constraints and limitations"
  - organizational: "Organizational and process constraints"
  - external: "External market, legal, and regulatory constraints"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: constraint_matrix
  output:
    - hard_constraints: "Non-negotiable limitations"
    - soft_constraints: "Flexible limitations with trade-offs"
    - assumptions: "Constraints that may be challenged"
    - dependencies: "External dependencies affecting constraints"
```

**Prompt Template**:
```
You are analyzing constraints from the {category} perspective for:

PROBLEM: {problem_statement}
PROBLEM ANALYSIS: {phase_1_output}

Your task:
1. Identify all relevant constraints in your category
2. Classify each as hard (non-negotiable) or soft (flexible)
3. Note any constraints that are based on assumptions
4. Identify dependencies between constraints
5. Suggest which constraints might be challenged or relaxed

Output format:
- Hard Constraints: [list with rationale]
- Soft Constraints: [list with flexibility degree]
- Assumption-Based Constraints: [list]
- Constraint Dependencies: [list]
- Challengeable Constraints: [list with reasoning]
```

---

### Phase 3: Solution Generation

**Objective**: Generate diverse solution candidates from multiple perspectives.

**Subagent Configuration**:
```yaml
phase: solution_generation
parallel_agents: 6
approaches:
  - conservative: "Safe, proven approach with minimal risk"
  - innovative: "Novel approach leveraging new technologies/methods"
  - hybrid: "Combination of existing and new approaches"
  - minimal: "Simplest possible solution"
  - comprehensive: "Thorough solution addressing all aspects"
  - disruptive: "Radical rethinking of the problem"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: solution_catalog
  output:
    - solutions: "List of all generated solutions"
    - approach_types: "Categorization by approach"
    - innovation_level: "Assessment of novelty vs. proven"
    - risk_profile: "Risk assessment for each solution"
```

**Prompt Template**:
```
You are generating solutions using a {approach} approach for:

PROBLEM: {problem_statement}
CONSTRAINTS: {phase_2_output}

Your task:
1. Generate 2-3 solution candidates using a {approach} approach
2. For each solution, provide:
   - Name and brief description
   - Key components or steps
   - Required resources
   - Estimated complexity
   - Potential benefits
   - Potential risks
3. Ensure solutions are diverse within your approach

Output format for each solution:
- Solution Name: [name]
- Description: [1-2 sentences]
- Components: [list]
- Resources Needed: [list]
- Complexity: [Low/Medium/High]
- Benefits: [list]
- Risks: [list]
```

---

### Phase 4: Solution Evaluation

**Objective**: Evaluate all solutions against established criteria.

**Subagent Configuration**:
```yaml
phase: solution_evaluation
parallel_agents: 4
evaluators:
  - feasibility: "Technical and resource feasibility"
  - impact: "Potential impact and value delivery"
  - risk: "Risk assessment and mitigation"
  - alignment: "Alignment with goals and constraints"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: scoring_matrix
  output:
    - ranked_solutions: "Solutions ranked by overall score"
    - evaluation_criteria: "Criteria used for evaluation"
    - trade_off_analysis: "Key trade-offs between top solutions"
    - recommendation: "Top 2-3 recommended solutions"
```

**Prompt Template**:
```
You are evaluating solutions from the {evaluator} perspective:

PROBLEM: {problem_statement}
SOLUTIONS: {phase_3_output}
SUCCESS CRITERIA: {success_criteria}
CONSTRAINTS: {phase_2_output}

Your task:
1. Evaluate each solution against relevant criteria:
   - Technical feasibility
   - Resource requirements
   - Timeline compatibility
   - Risk level
   - Alignment with constraints
   - Potential impact
2. Score each solution (1-5) on key dimensions
3. Identify top 2-3 solutions from your perspective
4. Document trade-offs between solutions

Output format:
- Solution Evaluations:
  * [Solution Name]:
    - Scores: [dimension: score]
    - Strengths: [list]
    - Weaknesses: [list]
    - Overall Assessment: [brief]
- Top Recommendations: [list]
- Key Trade-offs: [description]
```

---

### Phase 5: Synthesis

**Objective**: Combine the best elements from multiple solutions into cohesive hybrid solutions.

**Subagent Configuration**:
```yaml
phase: synthesis
parallel_agents: 3
synthesizers:
  - integrator: "Combine complementary elements from different solutions"
  - optimizer: "Optimize the combined solution for key criteria"
  - validator: "Validate the synthesized solution against constraints"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: solution_refinement
  output:
    - synthesized_solutions: "2-3 hybrid solutions"
    - component_mapping: "Which elements came from which source"
    - rationale: "Why these combinations were chosen"
    - final_candidates: "Top 2 solutions for refinement"
```

**Prompt Template**:
```
You are synthesizing solutions as a {synthesizer}:

PROBLEM: {problem_statement}
EVALUATED SOLUTIONS: {phase_4_output}
TOP SOLUTIONS: [list from evaluation]

Your task:
1. Review all evaluated solutions and their scores
2. Identify complementary elements across solutions
3. Create 2-3 hybrid solutions that combine the best elements
4. Ensure synthesized solutions are coherent and feasible
5. Document the rationale for each combination

Output format for each synthesized solution:
- Solution Name: [name]
- Description: [overview]
- Components (with sources):
  * [Component]: from [Original Solution]
- Why This Combination: [rationale]
- Expected Benefits: [list]
- Potential Challenges: [list]
- Overall Assessment: [brief evaluation]
```

---

### Phase 6: Refinement

**Objective**: Polish and finalize the design with implementation details.

**Subagent Configuration**:
```yaml
phase: refinement
parallel_agents: 3
refiners:
  - detailer: "Add implementation details and specifications"
  - reviewer: "Review for completeness and consistency"
  - planner: "Create implementation roadmap and milestones"
```

**Aggregation Pattern**:
```yaml
aggregation:
  method: final_assembly
  output:
    - final_design: "Complete, refined solution specification"
    - implementation_plan: "Step-by-step implementation guide"
    - risk_mitigation: "Specific risk mitigation strategies"
    - success_metrics: "How to measure success"
```

**Prompt Template**:
```
You are refining the solution as a {refiner}:

PROBLEM: {problem_statement}
SYNTHESIZED SOLUTIONS: {phase_5_output}
SELECTED SOLUTION: [top solution from synthesis]

Your task:
1. Take the selected synthesized solution
2. Add detailed specifications and implementation guidance
3. Ensure all aspects are thoroughly addressed
4. Create actionable next steps

Output format:
- Refined Solution: [detailed description]
- Detailed Specifications: [technical details]
- Implementation Considerations: [key points]
- Action Items: [specific next steps]
- Success Metrics: [how to measure outcomes]
```

---

## Integration with Horde-Swarm

The horde-brainstorming skill uses horde-swarm as its execution engine. Configure the swarm as follows:

```yaml
swarm_config:
  engine: horde-swarm
  version: ^1.0.0

  # Parallel execution settings
  max_parallel_phases: 2  # Run up to 2 phases in parallel where possible
  max_agents_per_phase: 6

  # Aggregation settings
  aggregation_strategy: hierarchical
  aggregation_timeout: 300  # seconds

  # Phase dependencies
  phase_dependencies:
    problem_exploration: []
    constraint_identification: [problem_exploration]
    solution_generation: [problem_exploration, constraint_identification]
    solution_evaluation: [solution_generation]
    synthesis: [solution_evaluation]
    refinement: [synthesis]

  # Output handling
  output_format: structured_yaml
  preserve_intermediates: true
```

### Phase Execution Flow

```
┌─────────────────────────┐
│  Problem Exploration    │ ──┐
│     (4 agents)          │   │
└─────────────────────────┘   │
                              │ Parallel
┌─────────────────────────┐   │ Execution
│  Constraint ID          │ ──┘
│     (3 agents)          │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  Solution Generation    │
│     (6 agents)          │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  Solution Evaluation    │
│     (4 agents)          │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│      Synthesis          │
│     (3 agents)          │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│      Refinement         │
│     (3 agents)          │
└─────────────────────────┘
```

## Aggregation Patterns

### Thematic Clustering (Phase 1)

Groups similar findings across agents into themes:

```yaml
thematic_clustering:
  algorithm: semantic_similarity
  min_cluster_size: 2
  output_format:
    themes: "Grouped findings by topic"
    consensus: "Points of agreement"
    divergences: "Points of disagreement"
    coverage: "Aspects of problem explored"
```

### Constraint Matrix (Phase 2)

Creates a structured view of all constraints:

```yaml
constraint_matrix:
  dimensions:
    - technical
    - organizational
    - external
  classifications:
    - hard
    - soft
    - assumption_based
  output:
    matrix: "2D view of constraints by category and type"
    conflicts: "Constraints that conflict with each other"
    relaxable: "Constraints that could be relaxed"
```

### Solution Catalog (Phase 3)

Organizes generated solutions for evaluation:

```yaml
solution_catalog:
  group_by: approach_type
  metadata:
    - innovation_level
    - risk_profile
    - complexity
    - resource_requirements
  output:
    catalog: "Organized list of all solutions"
    diversity_score: "Measure of solution diversity"
    coverage: "Problem aspects addressed"
```

### Scoring Matrix (Phase 4)

Evaluates solutions across multiple dimensions:

```yaml
scoring_matrix:
  criteria:
    - feasibility
    - impact
    - risk
    - alignment
  scale: 1-5
  weighting: customizable
  output:
    scores: "Matrix of solution x criteria scores"
    rankings: "Solutions ranked by weighted score"
    sensitivity: "How rankings change with different weights"
```

### Solution Refinement (Phase 5)

Combines elements into coherent solutions:

```yaml
solution_refinement:
  combination_rules:
    - complementary: "Elements that enhance each other"
    - compatible: "Elements that work together"
    - conflicting: "Elements that cannot be combined"
  output:
    synthesized: "New hybrid solutions"
    provenance: "Source of each component"
    coherence_score: "How well elements work together"
```

### Final Assembly (Phase 6)

Produces the final deliverable:

```yaml
final_assembly:
  components:
    - design_specification
    - implementation_plan
    - risk_mitigation
    - success_metrics
  quality_checks:
    - completeness
    - consistency
    - feasibility
    - measurability
```

## Example: Complete Brainstorming Workflow

### Example 1: API Design Brainstorming

```yaml
skill: horde-brainstorming
title: "Design REST API for Order Management"
problem_statement: |
  Design a REST API for an e-commerce order management system
  that supports high volume, real-time updates, and complex
  order workflows including returns and exchanges.

context:
  domain: api-design
  constraints:
    - "Must support 10,000+ requests/second"
    - "99.99% uptime SLA"
    - "Must integrate with legacy inventory system"
    - "GDPR compliance required"
  success_criteria:
    - "Response time < 100ms p99"
    - "Clear, intuitive API design"
    - "Comprehensive error handling"
    - "Easy to extend for new features"

phases:
  problem_exploration:
    parallel_agents: 4
    perspectives: [analyst, stakeholder, technical, historical]

  constraint_identification:
    parallel_agents: 3
    categories: [technical, organizational, external]

  solution_generation:
    parallel_agents: 6
    approaches: [conservative, innovative, hybrid, minimal, comprehensive, disruptive]

  solution_evaluation:
    parallel_agents: 4
    evaluators: [feasibility, impact, risk, alignment]

  synthesis:
    parallel_agents: 3
    synthesizers: [integrator, optimizer, validator]

  refinement:
    parallel_agents: 3
    refiners: [detailer, reviewer, planner]

swarm:
  engine: horde-swarm
  aggregation_timeout: 300
  output_format: structured_yaml
```

### Example 2: Architecture Decision Brainstorming

```yaml
skill: horde-brainstorming
title: "Microservices vs Monolith Decision"
problem_statement: |
  Determine the optimal architecture approach for a new
  fintech platform handling payments, user management,
  and analytics. The team has 12 engineers and needs
  to launch an MVP in 6 months.

context:
  domain: architecture
  constraints:
    - "Team of 12 engineers"
    - "6-month MVP timeline"
    - "PCI DSS compliance required"
    - "Must scale to 1M users within 2 years"
  success_criteria:
    - "Rapid initial development"
    - "Long-term scalability"
    - "Team productivity"
    - "Operational simplicity"

phases:
  problem_exploration:
    focus: "Understand trade-offs and implications"

  constraint_identification:
    emphasis: "Timeline and team size constraints"

  solution_generation:
    approaches: [conservative, innovative, hybrid, minimal]

  solution_evaluation:
    criteria_weighting:
      time_to_market: 0.3
      scalability: 0.25
      team_productivity: 0.25
      operational_cost: 0.2

  synthesis:
    target: "2 hybrid approaches"

  refinement:
    output: "Detailed implementation roadmap"
```

## Output Structure

The final output from a horde-brainstorming session includes:

```yaml
brainstorming_output:
  metadata:
    problem_statement: "Original problem"
    execution_time: "Total time elapsed"
    agents_involved: "Number of subagents used"
    phases_completed: "List of completed phases"

  phase_outputs:
    problem_exploration:
      problem_definition: "..."
      key_questions: [...]
      assumptions: [...]
      success_criteria: [...]

    constraint_identification:
      hard_constraints: [...]
      soft_constraints: [...]
      assumption_based_constraints: [...]

    solution_generation:
      solutions: [...]
      diversity_score: "..."
      coverage: "..."

    solution_evaluation:
      ranked_solutions: [...]
      scoring_matrix: "..."
      trade_off_analysis: "..."

    synthesis:
      synthesized_solutions: [...]
      component_mapping: "..."
      final_candidates: [...]

    refinement:
      final_design: "..."
      implementation_plan: "..."
      risk_mitigation: "..."
      success_metrics: "..."

  final_recommendation:
    recommended_solution: "..."
    rationale: "..."
    next_steps: [...]
    key_risks: [...]
```

## Best Practices

1. **Clear Problem Statement**: Invest time in crafting a clear, specific problem statement
2. **Appropriate Parallelism**: Match the number of agents to problem complexity
3. **Diverse Perspectives**: Ensure subagents have genuinely different viewpoints
4. **Structured Aggregation**: Use consistent aggregation patterns for comparable results
5. **Preserve Context**: Pass relevant context between phases
6. **Iterate if Needed**: Run multiple rounds for particularly complex problems
7. **Document Assumptions**: Make all assumptions explicit and reviewable

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `max_parallel_phases` | 2 | Number of phases to run in parallel |
| `max_agents_per_phase` | 6 | Maximum subagents per phase |
| `aggregation_timeout` | 300 | Seconds to wait for aggregation |
| `preserve_intermediates` | true | Keep intermediate outputs |
| `output_format` | structured_yaml | Format for final output |
| `phase_dependencies` | [...] | Define which phases depend on others |

## Troubleshooting

### Low Solution Diversity
- Increase the number of solution generation agents
- Use more diverse approach types
- Add constraints to force creative thinking

### Poor Synthesis
- Ensure evaluation phase produces clear rankings
- Add more detail to solution generation output
- Use explicit component mapping

### Incomplete Refinement
- Extend aggregation timeout
- Add validation step in refinement
- Break refinement into sub-phases
