# The Horde Skills Ecosystem

This document explains in detail how the horde skills work together, with **horde-swarm** as the centerpiece that powers all other skills.

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [horde-swarm: The Engine](#horde-swarm-the-engine)
3. [How Other Skills Use horde-swarm](#how-other-skills-use-horde-swarm)
4. [Skill Composition Patterns](#skill-composition-patterns)
5. [Workflow Examples](#workflow-examples)
6. [Technical Implementation](#technical-implementation)

---

## Core Philosophy

The horde skills are designed around a single principle:

> **Complex problems are best solved by multiple specialized agents working in parallel, with their outputs synthesized into a unified result.**

This is inspired by:
- **Ensemble methods** in machine learning (multiple models voting)
- **Wisdom of crowds** (diverse perspectives reduce bias)
- **Specialization** (experts in different domains)

### Why Parallel Agents?

| Approach | Limitations | Parallel Agents |
|----------|-------------|-----------------|
| Single generalist | Limited expertise, cognitive load | Multiple specialists |
| Sequential agents | Slow, no cross-pollination | Simultaneous, shared context |
| Monolithic system | Brittle, hard to extend | Modular, composable |

---

## horde-swarm: The Engine

**horde-swarm** is not just another skill - it's the **execution substrate** that enables all other horde skills to function.

### What horde-swarm Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    HORDE-SWARM ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: A task + a set of agents to dispatch                    │
│                                                                  │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Task        │───▶│ Agent Selection │───▶│ Parallel        │ │
│  │ Analysis    │    │ & Routing       │    │ Execution       │ │
│  └─────────────┘    └─────────────────┘    └────────┬────────┘ │
│                                                     │           │
│                          ┌──────────────────────────┼────────┐ │
│                          │                          │        │ │
│                          ▼                          ▼        ▼ │
│                    ┌─────────┐                ┌─────────┐      │
│                    │ Agent 1 │◄──────────────▶│ Agent 2 │      │
│                    │ Output  │   (isolated)   │ Output  │      │
│                    └────┬────┘                └────┬────┘      │
│                         │                          │           │
│                         └──────────┬───────────────┘           │
│                                    │                            │
│                                    ▼                            │
│                          ┌─────────────────┐                   │
│                          │  SYNTHESIZER    │                   │
│                          │                 │                   │
│                          │  • Consensus    │                   │
│                          │  • Deduplication│                   │
│                          │  • Conflict     │                   │
│                          │    resolution   │                   │
│                          │  • Format       │                   │
│                          │    unification  │                   │
│                          └────────┬────────┘                   │
│                                   │                             │
│                                   ▼                             │
│                          ┌─────────────────┐                   │
│                          │  UNIFIED OUTPUT │                   │
│                          │  to user/next   │                   │
│                          │  skill          │                   │
│                          └─────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Task Analyzer

Analyzes the input task to determine:
- **Complexity**: How many agents are needed?
- **Domain**: Which specializations are relevant?
- **Pattern**: Which swarm pattern to use?

```python
class TaskAnalyzer:
    def analyze(self, task: str) -> TaskProfile:
        return TaskProfile(
            complexity=self.assess_complexity(task),
            domains=self.identify_domains(task),
            recommended_pattern=self.select_pattern(task),
            estimated_tokens=self.estimate_tokens(task)
        )
```

#### 2. Agent Router

Routes tasks to appropriate agents based on:
- **Capability matching**: Which agents can handle this task?
- **Load balancing**: Which agents are available?
- **Context affinity**: Which agents have relevant context?

```python
class AgentRouter:
    def route(self, task: TaskProfile, available_agents: List[Agent]) -> List[Agent]:
        scored = [
            (agent, self.score_compatibility(agent, task))
            for agent in available_agents
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, score in scored[:task.recommended_agent_count]]
```

#### 3. Parallel Executor

Executes agents in parallel with:
- **Concurrency control**: Limit simultaneous agents
- **Timeout handling**: Kill hung agents
- **Error isolation**: One agent failing doesn't crash others
- **Resource limits**: Memory, CPU, token budgets

```python
class ParallelExecutor:
    def execute(self, agents: List[Agent], task: str) -> List[Result]:
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {
                executor.submit(self.run_agent, agent, task): agent
                for agent in agents
            }

            results = []
            for future in as_completed(futures, timeout=self.timeout):
                agent = futures[future]
                try:
                    result = future.result()
                    results.append(Result.success(agent, result))
                except Exception as e:
                    results.append(Result.failure(agent, e))

            return results
```

#### 4. Synthesizer

Combines multiple agent outputs into a unified result:

```python
class Synthesizer:
    def synthesize(self, results: List[Result]) -> UnifiedResult:
        # Step 1: Deduplicate similar outputs
        unique = self.deduplicate(results)

        # Step 2: Resolve conflicts
        resolved = self.resolve_conflicts(unique)

        # Step 3: Build consensus
        consensus = self.build_consensus(resolved)

        # Step 4: Format output
        formatted = self.format_output(consensus)

        return UnifiedResult(
            content=formatted,
            sources=[r.agent for r in results],
            confidence=self.calculate_confidence(results),
            dissent=self.identify_dissent(results)
        )
```

### Swarm Patterns

horde-swarm supports multiple execution patterns:

#### Pattern 1: Multi-Perspective

Get different viewpoints on the same problem.

```
Task: "Review this API design"

Agent 1 (Backend): "RESTful, but needs pagination"
Agent 2 (Frontend): "Good structure, missing CORS headers"
Agent 3 (Security): "No rate limiting, vulnerable to DoS"

Synthesizer combines into unified review with all perspectives.
```

#### Pattern 2: Divide and Conquer

Split large tasks into chunks processed in parallel.

```
Task: "Analyze 1000 log files"

Chunk 1 (Files 1-250)   → Agent 1
Chunk 2 (Files 251-500) → Agent 2
Chunk 3 (Files 501-750) → Agent 3
Chunk 4 (Files 751-1000)→ Agent 4

Synthesizer combines findings into comprehensive report.
```

#### Pattern 3: Expert Review Panel

Specialized experts review a completed work.

```
Task: "Review this system design document"

Architect:   "Scalable, but single point of failure"
Security:    "Good auth, needs audit logging"
Performance: "Cache layer missing, will bottleneck"
DevOps:      "Deployable, but no rollback strategy"

Synthesizer creates consolidated review with priorities.
```

#### Pattern 4: Sequential Refinement

Each agent builds on previous agent's output.

```
Task: "Write a technical blog post"

Researcher → "Gather facts and sources"
Writer     → "Draft post using facts"
Editor     → "Polish and improve"
SEO        → "Optimize for search"

Synthesizer chains outputs sequentially.
```

---

## How Other Skills Use horde-swarm

### horde-brainstorming → horde-swarm

**Phase 2: Parallel Domain Exploration**

```python
class HordeBrainstorming:
    def phase_2_explore(self, problem: str, context: dict):
        # Use horde-swarm to dispatch domain specialists
        return self.swarm.dispatch(
            task=f"Explore technical approaches for: {problem}",
            agents=[
                BackendArchitect(context),
                FrontendDeveloper(context),
                DevOpsEngineer(context),
                SecurityReviewer(context),
                DataEngineer(context)
            ],
            pattern="multi-perspective"
        )
```

Each specialist explores the problem from their domain, then the synthesizer combines their findings into a comprehensive options list.

### horde-plan → horde-swarm

**Multi-Perspective Planning**

```python
class HordePlan:
    def create_plan(self, design: str):
        # Dispatch different planning perspectives
        results = self.swarm.dispatch(
            task=f"Create implementation plan for: {design}",
            agents=[
                TaskDecomposer(),      # Break into tasks
                DependencyAnalyzer(),  # Identify dependencies
                EffortEstimator(),     # Estimate hours
                RiskAssessor()         # Identify risks
            ],
            pattern="multi-perspective"
        )

        # Synthesize into unified plan
        return self.build_plan_from_results(results)
```

### horde-implement → horde-swarm

**Parallel Code Generation**

```python
class HordeImplement:
    def implement(self, plan: Plan):
        # Generate code for different components in parallel
        results = self.swarm.dispatch(
            task=f"Implement according to plan: {plan}",
            agents=[
                ModelGenerator(plan.models),
                APIEndpointGenerator(plan.endpoints),
                TestGenerator(plan.test_cases),
                DocumentationGenerator(plan.docs)
            ],
            pattern="divide-conquer"
        )

        # Synthesize into cohesive codebase
        return self.assemble_codebase(results)
```

### horde-learn → horde-swarm

**Parallel Research**

```python
class HordeLearn:
    def research(self, sources: List[str], query: str):
        # Dispatch researchers to different sources
        results = self.swarm.dispatch(
            task=f"Extract insights about: {query}",
            agents=[
                WebResearcher(sources[0]),
                WebResearcher(sources[1]),
                DocumentAnalyzer(sources[2]),
                CodebaseAnalyzer(sources[3])
            ],
            pattern="divide-conquer"
        )

        # Synthesize into knowledge base
        return self.build_knowledge_base(results)
```

### horde-gate-testing → horde-swarm

**Parallel Validation**

```python
class HordeGateTesting:
    def test(self, codebase: str):
        # Run different test types in parallel
        results = self.swarm.dispatch(
            task=f"Validate codebase: {codebase}",
            agents=[
                UnitTestRunner(),
                IntegrationTestRunner(),
                SecurityAuditor(),
                PerformanceTester(),
                AccessibilityChecker()
            ],
            pattern="expert-panel"
        )

        # Synthesize into test report
        return self.generate_test_report(results)
```

---

## Skill Composition Patterns

### Pattern 1: Sequential Pipeline

```
horde-brainstorming → horde-plan → horde-implement → horde-gate-testing

Use case: Complete feature development
Output of each skill feeds into the next
```

### Pattern 2: Fan-Out / Fan-In

```
                    ┌→ horde-learn (research)
                    │
horde-swarm ────────┼→ horde-learn (competitor analysis)
(dispatch)          │
                    └→ horde-learn (market trends)

                    ↓

              horde-brainstorming (synthesize insights)

Use case: Research-driven design
```

### Pattern 3: Nested Swarm

```
horde-swarm (outer)
  ├→ Agent 1: horde-swarm (inner) for subtask A
  ├→ Agent 2: horde-swarm (inner) for subtask B
  └→ Agent 3: horde-swarm (inner) for subtask C

Use case: Complex multi-level problems
```

### Pattern 4: Feedback Loop

```
horde-implement → horde-gate-testing → [if failed] → horde-implement
                                         ↓
                                    [if passed] → Done

Use case: Iterative refinement
```

---

## Workflow Examples

### Example 1: Build a Feature

```yaml
workflow: feature-development
name: "Build User Authentication"

steps:
  - name: Design
    skill: horde-brainstorming
    input: "Design a secure user authentication system with MFA"
    output: design_spec

  - name: Plan
    skill: horde-plan
    input: "{{design_spec}}"
    output: implementation_plan

  - name: Implement
    skill: horde-implement
    input: "{{implementation_plan}}"
    output: codebase

  - name: Test
    skill: horde-gate-testing
    input: "{{codebase}}"
    output: test_results

  - name: Iterate (if needed)
    condition: "{{test_results.failed}}"
    skill: horde-implement
    input: "Fix these issues: {{test_results.issues}}"
```

### Example 2: Competitive Analysis

```yaml
workflow: competitive-analysis
name: "Analyze Competitor Landscape"

steps:
  - name: Research
    skill: horde-learn
    parallel:
      - input: "https://competitor1.com"
        output: comp1_data
      - input: "https://competitor2.com"
        output: comp2_data
      - input: "https://competitor3.com"
        output: comp3_data

  - name: Synthesize
    skill: horde-brainstorming
    input: "Synthesize competitive insights from {{comp1_data}}, {{comp2_data}}, {{comp3_data}}"
    output: analysis_report

  - name: Recommend
    skill: horde-plan
    input: "Create strategic recommendations based on {{analysis_report}}"
    output: strategy_plan
```

### Example 3: Code Review

```yaml
workflow: comprehensive-review
name: "Review Pull Request"

steps:
  - name: Multi-Perspective Review
    skill: horde-swarm
    config:
      pattern: expert-panel
      agents:
        - code-reviewer
        - security-reviewer
        - performance-reviewer
        - accessibility-reviewer
    input: "Review this PR: {{pr_url}}"
    output: review_findings

  - name: Synthesize Review
    skill: horde-brainstorming
    input: "Consolidate these review findings: {{review_findings}}"
    output: unified_review
```

---

## Technical Implementation

### Skill Manifest

Each horde skill declares its relationship to horde-swarm:

```yaml
# horde-brainstorming/skill.yaml
skill:
  id: horde-brainstorming
  version: 2.0.0

  # Declare horde-swarm dependency
  horde:
    compatible: true
    requires: horde-swarm>=1.0.0
    uses_patterns:
      - multi-perspective
      - expert-panel

  # Runtime configuration
  runtime:
    max_agents: 5
    default_timeout: 300
    synthesis_model: claude-sonnet-4
```

### Runtime Integration

```python
# How skills access the horde-swarm engine

class HordeSkill:
    def __init__(self, context: SkillContext):
        self.context = context
        # Access the shared swarm engine
        self.swarm = context.get_engine("horde-swarm")

    def execute(self, task: str) -> Result:
        # Use swarm for parallel execution
        results = self.swarm.dispatch(
            task=task,
            agents=self.get_specialists(),
            pattern=self.get_pattern()
        )
        return self.process_results(results)
```

### State Management

Skills share state through the operational memory:

```python
# Shared context across skills
shared_context = {
    "workflow_id": "uuid-123",
    "artifacts": {
        "design_spec": {...},
        "implementation_plan": {...},
        "codebase": {...}
    },
    "agent_outputs": {
        "backend_architect": {...},
        "security_reviewer": {...}
    }
}

# Each skill can read/write to shared context
class HordeSkill:
    def execute(self, task: str):
        # Read previous skill outputs
        previous_output = self.context.get_artifact("design_spec")

        # Do work...

        # Write output for next skill
        self.context.set_artifact("implementation_plan", result)
```

---

## Summary

The horde skills ecosystem works because:

1. **horde-swarm is the engine** that enables parallel agent execution
2. **Each skill specializes** in a specific phase of the workflow
3. **Skills compose** through shared context and output chaining
4. **Patterns are reusable** across different problem domains
5. **Synthesis unifies** diverse outputs into coherent results

The key insight is that **horde-swarm is not just a skill - it's the foundation** that makes the entire ecosystem possible. Without it, each horde skill would need to implement its own parallel execution logic. With it, they can focus on their specific domain expertise while leveraging shared infrastructure for parallel execution.
