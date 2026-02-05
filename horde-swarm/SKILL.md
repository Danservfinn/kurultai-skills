---
name: horde-swarm
description: Dispatch a swarm of specialized subagents to work on a prompt in parallel using the Task tool. Use when the user asks to "swarm this", "use multiple agents", "parallel agents", "agent swarm", "run these in parallel", "distribute across agents", or wants multiple perspectives on a complex task.
---

# Horde Swarm

## Overview

Dispatch a coordinated swarm of specialized subagents to work on a task in parallel. This skill uses the Task tool with subagent types to orchestrate multiple agents simultaneously, then synthesizes their outputs into a cohesive response.

**Core Pattern:** Analyze → Select Agents → Dispatch in Parallel → Synthesize → Deliver

**When NOT to Use:**
- Sequential tasks (where step B depends on step A output)
- Simple tasks that don't benefit from multiple perspectives
- Tightly coupled components that need coordinated implementation

## When to Use

Invoke this skill when:
- User asks to "swarm" a task or use "multiple agents"
- User wants parallel execution of independent subtasks
- A complex problem benefits from multiple perspectives (architecture + security + performance)
- User wants comprehensive analysis from different domain experts
- The task can be decomposed into independent workstreams

## Agent Type Registry

This skill supports 35+ specialized subagent types organized into 8 categories. Use the format `domain:role` when specified, or the standalone agent name.

### Backend Agents
| Agent Type | Description |
|------------|-------------|
| `backend-development:backend-architect` | API design, microservices, system architecture |
| `backend-development:event-sourcing-architect` | Event sourcing, CQRS patterns |
| `backend-development:graphql-architect` | GraphQL schema design, federation |
| `backend-development:tdd-orchestrator` | Test-driven development workflows |
| `backend-development:temporal-python-pro` | Temporal workflow orchestration |
| `backend-development:microservices-patterns` | Microservices design patterns |
| `backend-development:saga-orchestration` | Distributed transaction patterns |

### Frontend Agents
| Agent Type | Description |
|------------|-------------|
| `frontend-mobile-development:frontend-developer` | React, Next.js, UI components |
| `frontend-mobile-development:mobile-developer` | React Native, Flutter, mobile apps |

### Python Agents
| Agent Type | Description |
|------------|-------------|
| `python-development:fastapi-pro` | FastAPI, async Python, SQLAlchemy |
| `python-development:django-pro` | Django, DRF, Django Channels |
| `python-development:python-pro` | Python optimization, advanced patterns |

### Data & ML Agents
| Agent Type | Description |
|------------|-------------|
| `senior-data-engineer` | Data pipelines, ETL, data architecture |
| `senior-ml-engineer` | ML model deployment, MLOps |
| `data-scientist` | Statistical modeling, experimentation, analytics |

### Infrastructure & DevOps Agents
| Agent Type | Description |
|------------|-------------|
| `senior-devops` | CI/CD, infrastructure automation, cloud architecture |
| `mlops-engineer` | ML infrastructure, model serving, experiment tracking |
| `database-migrations:database-admin` | Database operations, migrations, optimization |
| `database-migrations:database-optimizer` | Query optimization, indexing, performance tuning |

### Specialized Analysis Agents
| Agent Type | Description |
|------------|-------------|
| `dependency-manager` | Dependency analysis, vulnerability scanning, license compliance |
| `url-context-validator` | URL validation and contextual appropriateness analysis |
| `url-link-extractor` | Link extraction and cataloging from codebases |
| `web-accessibility-checker` | WCAG compliance, accessibility testing |

### Modern Framework Specialists
| Agent Type | Description |
|------------|-------------|
| `nextjs-architecture-expert` | Next.js App Router, Server Components, performance |
| `react-performance-optimizer` | React performance patterns, Core Web Vitals |
| `architecture-modernizer` | Monolith decomposition, modernization strategies |

### Specialized Agents
| Agent Type | Description |
|------------|-------------|
| `agent-orchestration:context-manager` | AI context engineering, memory systems |
| `security-auditor` | Security reviews, vulnerability assessment |
| `code-simplifier` | Code refactoring, simplification |
| `documentation-expert` | Technical writing, documentation |
| `agent-sdk-dev:agent-sdk-verifier-ts` | TypeScript Agent SDK verification |
| `agent-sdk-dev:agent-sdk-verifier-py` | Python Agent SDK verification |
| `feature-dev:code-reviewer` | Comprehensive code review with confidence filtering |
| `feature-dev:code-explorer` | Deep codebase analysis and feature tracing |
| `feature-dev:code-architect` | Feature architecture design |
| `superpowers:code-reviewer` | Multi-domain code review (security, performance, architecture) |
| `architect-reviewer` | Architectural consistency and SOLID principles |
| `url-context-validator` | URL validation and contextual appropriateness |
| `url-link-extractor` | URL/link extraction and cataloging |

## Swarm Patterns

### Pattern 1: Multi-Perspective Analysis

Use when you need comprehensive analysis from different angles.

**Agents to dispatch:**
1. `backend-development:backend-architect` - Architecture perspective
2. `security-auditor` - Security perspective
3. `python-development:python-pro` - Implementation perspective

**Example:**
```
User: "Design a user authentication system"

Swarm:
- Backend Architect: Design the auth flow, token management, session handling
- Security Auditor: Review for OWASP compliance, JWT best practices, password hashing
- Python Pro: Implement FastAPI endpoints, Pydantic models, async handlers

Synthesize: Combine into unified design with security hardening and clean implementation
```

### Pattern 2: Divide and Conquer

Use when the task decomposes into independent subtasks.

**Agents to dispatch:**
1. Subagent for component A
2. Subagent for component B
3. Subagent for component C

**Example:**
```
User: "Build a full-stack task management app"

Swarm:
- Frontend Developer: React components, state management, UI
- Backend Architect: API design, database schema, endpoints
- Python Pro: FastAPI implementation, models, business logic

Synthesize: Integrate frontend and backend into complete application
```

### Pattern 3: Expert Review Chain

Use when you need primary implementation + expert validation.

**Agents to dispatch:**
1. Primary implementation agent
2. Review specialist
3. Documentation specialist

**Example:**
```
User: "Create a GraphQL API for our e-commerce platform"

Swarm:
- GraphQL Architect: Design schema, resolvers, federation
- Security Auditor: Review for injection vulnerabilities, depth limiting
- Documentation Expert: Generate API documentation, usage examples

Synthesize: Production-ready GraphQL API with security hardening and docs
```

## Execution Workflow

### Step 1: Analyze the Request

Determine:
1. What is the core task?
2. Which domains does it touch? (backend, frontend, security, data, etc.)
3. Can it be decomposed into independent subtasks?
4. What expertise is needed?

**Decision Check:** If subtasks are dependent (output of A needed for B), do NOT use swarm. Use sequential skill invocation instead.

### Step 2: Select Swarm Composition

Choose 2-4 subagent types based on:
- **Complexity:** More complex = more specialized agents
- **Domains:** Cover all relevant technical areas
- **Dependencies:** Only parallelize independent work

**Common Compositions:**

| Task Type | Recommended Swarm |
|-----------|-------------------|
| API Design | backend-architect + security-auditor + python-pro |
| Frontend Feature | frontend-developer + web-accessibility-checker |
| Full-Stack Feature | frontend-developer + backend-architect + python-pro |
| Data Pipeline | senior-data-engineer + python-pro + backend-architect |
| Security Review | security-auditor + backend-architect + python-pro |
| Performance Optimization | python-pro + senior-backend + code-simplifier |
| ML Model Deployment | senior-ml-engineer + mlops-engineer + backend-architect |
| Database Migration | database-migrations:database-admin + database-migrations:database-optimizer + backend-architect |
| Accessibility Audit | web-accessibility-checker + frontend-developer + ux-researcher-designer |
| Legacy Modernization | architecture-modernizer + senior-backend + code-simplifier |
| Dependency Security Audit | dependency-manager + security-auditor + backend-architect |
| Next.js Architecture | nextjs-architecture-expert + react-performance-optimizer + frontend-developer |
| Infrastructure Review | senior-devops + security-auditor + backend-architect |
| Code Quality Review | code-reviewer + code-simplifier + architect-reviewer |

### Step 3: Dispatch Tasks

Use the Task tool with `subagent_type` parameter. Dispatch all tasks in a single response for parallel execution.

**Complete Working Example:**

```python
# User asks: "Design a secure API for user authentication"

# Dispatch all three tasks in parallel (single response, multiple Task calls)
Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Design the architecture for a user authentication API.

Requirements:
- Support email/password login
- JWT token-based sessions
- Password reset flow
- Consider scalability for 10k+ concurrent users

Output:
1. High-level architecture diagram description
2. Key endpoints needed
3. Data models
4. Session management approach""",
    description="Design auth API architecture"
)

Task(
    subagent_type="security-auditor",
    prompt="""Security review for user authentication API.

Focus areas:
- Password storage (hashing algorithm)
- JWT security (secret management, expiration)
- OWASP Top 10 compliance
- Rate limiting for brute force protection
- Secure password reset flow

Output:
1. Security requirements list
2. Potential vulnerabilities to address
3. Hardening recommendations
4. Compliance checklist""",
    description="Security audit auth API"
)

Task(
    subagent_type="python-development:fastapi-pro",
    prompt="""Implement FastAPI endpoints for user authentication.

Requirements:
- /auth/login endpoint
- /auth/logout endpoint
- /auth/refresh endpoint
- /auth/forgot-password endpoint

Output:
1. Complete FastAPI route implementations
2. Pydantic models for requests/responses
3. Dependency injection for auth middleware
4. Error handling patterns""",
    description="Implement FastAPI auth endpoints"
)
```

**Key Rules:**
- Always dispatch parallel tasks in a SINGLE response (multiple Task tool calls in one turn)
- Each task gets a focused, clear prompt with specific deliverables
- Use `description` parameter for task tracking
- Expected timeout: 2-3 minutes per task

### Step 4: Synthesize Results

After all agents return:

1. **Review outputs** from each agent
2. **Identify conflicts** or contradictions
3. **Extract best ideas** from each perspective
4. **Merge into cohesive solution**
5. **Present unified response** with attribution

**Synthesis Template:**
```markdown
## Executive Summary
Brief overview of the swarm's collective output

## Architecture (from Backend Architect)
Key architectural decisions and rationale

## Security Considerations (from Security Auditor)
Security hardening recommendations

## Implementation (from Python Pro)
Concrete implementation guidance

## Integrated Solution
Combined recommendations with all perspectives integrated

## Next Steps
Prioritized action items
```

## Usage Examples

### Example 1: API Design Swarm

**User Request:** "Design a REST API for a payment processing system"

**Swarm Dispatch:**
```python
# Parallel tasks
Task(subagent_type="backend-development:backend-architect", ...)
Task(subagent_type="security-auditor", ...)
Task(subagent_type="payment-processing:payment-integration", ...)
```

**Synthesized Output:**
- Architecture: Resource-oriented design with clear boundaries
- Security: PCI compliance, tokenization, idempotency keys
- Payment: Stripe integration patterns, webhook handling

### Example 2: Code Review Swarm

**User Request:** "Review this authentication module"

**Swarm Dispatch:**
```python
Task(subagent_type="security-auditor", ...)
Task(subagent_type="python-development:python-pro", ...)
Task(subagent_type="code-simplifier:code-simplifier", ...)
```

**Synthesized Output:**
- Security: JWT vulnerabilities found, recommend httpOnly cookies
- Python: Async patterns need improvement, suggest type hints
- Simplification: Reduce nesting, extract helper functions

### Example 3: Feature Implementation Swarm

**User Request:** "Build a real-time notification system"

**Swarm Dispatch:**
```python
Task(subagent_type="backend-development:backend-architect", ...)
Task(subagent_type="frontend-mobile-development:frontend-developer", ...)
Task(subagent_type="python-development:fastapi-pro", ...)
```

**Synthesized Output:**
- Backend: WebSocket architecture with Redis pub/sub
- Frontend: React hooks for real-time updates, connection management
- Implementation: FastAPI WebSocket endpoints with proper error handling

### Example 4: Meta-Swarm Architecture Review (50+ Agents)

**User Request:** "Perform comprehensive architecture review of our enterprise platform"

**Phase 1: Dispatch Domain Coordinators (Level 2)**
```python
# Security Domain
Task(
    subagent_type="senior-architect",
    prompt="""Coordinate comprehensive security architecture review.

Your Level 1 swarm (dispatch these in parallel):
1. Security Auditor: Overall security posture assessment
2. Penetration Tester: Attack surface analysis
3. Compliance Specialist: Regulatory compliance (SOC2, GDPR)
4. Threat Modeler: Threat modeling and risk assessment

Each Level 1 agent should spawn 2-3 Level 0 specialists as needed.

Synthesize all security findings into a unified security assessment.
Report: Critical risks, compliance gaps, remediation priorities.""",
    description="Security domain coordination"
)

# Backend Domain
Task(
    subagent_type="senior-architect",
    prompt="""Coordinate backend architecture review.

Your Level 1 swarm:
1. Backend Architect: API design and service boundaries
2. Database Specialist: Schema design, query optimization
3. Performance Engineer: Bottleneck identification
4. Scalability Expert: Horizontal scaling strategy
5. Integration Specialist: Third-party integration patterns

Synthesize into backend architecture assessment.
Report: Architecture strengths, scalability limits, technical debt.""",
    description="Backend domain coordination"
)

# Frontend Domain
Task(
    subagent_type="senior-architect",
    prompt="""Coordinate frontend architecture review.

Your Level 1 swarm:
1. Frontend Developer: Component architecture
2. UX Designer: User experience patterns
3. Accessibility Auditor: WCAG compliance
4. Performance Specialist: Bundle optimization, Core Web Vitals

Synthesize into frontend architecture assessment.
Report: Architecture health, performance metrics, improvement areas.""",
    description="Frontend domain coordination"
)

# Data Domain
Task(
    subagent_type="senior-architect",
    prompt="""Coordinate data architecture review.

Your Level 1 swarm:
1. Data Engineer: Pipeline architecture
2. Data Scientist: Analytics infrastructure
3. ML Engineer: Model serving architecture
4. Data Governance: Data quality and lineage

Synthesize into data architecture assessment.
Report: Data architecture maturity, pipeline reliability, ML ops readiness.""",
    description="Data domain coordination"
)

# DevOps Domain
Task(
    subagent_type="senior-devops",
    prompt="""Coordinate DevOps architecture review.

Your Level 1 swarm:
1. Infrastructure Engineer: Cloud architecture, IaC
2. CI/CD Specialist: Pipeline design and optimization
3. Observability Engineer: Monitoring, logging, tracing
4. SRE: Reliability engineering practices

Synthesize into DevOps architecture assessment.
Report: Infrastructure maturity, deployment reliability, observability coverage.""",
    description="DevOps domain coordination"
)
```

**Phase 2: Chief Architect Synthesis (Level 3)**
```python
Task(
    subagent_type="senior-architect",
    prompt="""Synthesize comprehensive enterprise architecture review.

Inputs from 5 domain coordinators:
- Security Domain Assessment
- Backend Domain Assessment
- Frontend Domain Assessment
- Data Domain Assessment
- DevOps Domain Assessment

Cross-domain analysis:
1. Identify integration points and dependencies
2. Detect cross-domain risks (e.g., security affecting performance)
3. Prioritize investments across domains
4. Create unified roadmap

Final deliverable:
- Executive summary (1 page)
- Domain assessments (5 sections)
- Cross-domain risk matrix
- Prioritized investment roadmap
- 90/180/365 day improvement plan""",
    description="Chief architect synthesis"
)
```

### Example 5: Red Team Swarm

**User Request:** "Design a secure user authentication system"

**Phase 1: Primary Solutions**
```python
Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Design user authentication architecture.

Requirements:
- Email/password login
- JWT token management
- Password reset flow
- Session handling

Output your best architectural solution.""",
    description="Auth architecture proposal"
)

Task(
    subagent_type="security-auditor",
    prompt="""Design security-hardened authentication.

Focus on:
- OWASP compliance
- Brute force protection
- Token security
- Password storage

Output your security-first solution.""",
    description="Security-first auth proposal"
)

Task(
    subagent_type="python-development:fastapi-pro",
    prompt="""Design implementable authentication system.

Focus on:
- FastAPI implementation patterns
- Pydantic models
- Async handling
- Error management

Output your implementation-focused solution.""",
    description="Implementation auth proposal"
)
```

**Phase 2: Red Team Attack**
```python
Task(
    subagent_type="security-auditor",
    prompt="""RED TEAM: Destroy the authentication architecture proposal.

Attack vectors to explore:
- Session fixation
- Token prediction
- Timing attacks
- Race conditions
- Social engineering vectors
- Insider threats

Be ruthless. Find every weakness. Rate each: CRITICAL/HIGH/MEDIUM/LOW.""",
    description="Red team attack on auth"
)

Task(
    subagent_type="senior-backend",
    prompt="""RED TEAM: Attack the scalability and reliability of the auth proposals.

Find:
- Bottlenecks under load
- Single points of failure
- Database deadlock scenarios
- Cache stampede risks
- Distributed system edge cases

Rate severity and provide reproduction steps.""",
    description="Red team scalability attack"
)
```

**Phase 3: Defense and Iteration**
```python
# Original agents respond to criticisms
# Continue until convergence or max iterations
```

**Phase 4: Final Synthesis**
```python
Task(
    subagent_type="senior-architect",
    prompt="""Synthesize hardened authentication design.

Incorporate:
- Original proposals
- Red team findings
- Defensive improvements
- Remaining risk acceptance

Output production-ready design with security justification.""",
    description="Hardened auth synthesis"
)
```

### Example 6: Expert Panel with Consensus

**User Request:** "Should we use microservices or monolith for our new platform?"

**Round 1: Position Statements**
```python
panel = [
    ("backend-development:backend-architect", "You are the Pragmatist. Prioritize delivery speed and team productivity."),
    ("security-auditor", "You are the Conservative. Prioritize security, compliance, and risk minimization."),
    ("senior-devops", "You are the Operator. Prioritize operational simplicity and reliability."),
    ("python-development:python-pro", "You are the Optimizer. Prioritize performance and resource efficiency."),
    ("code-simplifier:code-simplifier", "You are the Minimalist. Prioritize simplicity and maintainability.")
]

for agent_type, persona in panel:
    Task(
        subagent_type=agent_type,
        prompt=f"""{persona}

Debate topic: Microservices vs Monolith architecture

Provide your position statement:
1. Your recommendation (microservices/monolith/hybrid)
2. Key arguments supporting your position (3-5 points)
3. Risks you see in the alternative approach
4. Conditions under which you'd change your mind

Use Chain-of-Thought reasoning before stating your position.""",
        description=f"Panel position: {persona.split(' - ')[0]}"
    )
```

**Round 2-4: Structured Debate**
```python
# Continue debate rounds with rebuttals and counter-rebuttals
# Track confidence scores and reliability ratings
```

**Round 5: Bayesian Consensus**
```python
Task(
    subagent_type="senior-architect",
    prompt="""Calculate Bayesian consensus from expert panel.

Panel inputs with confidence and reliability scores:
[Include all panel outputs with metadata]

Calculate:
1. Weighted recommendation using Bayesian formula
2. Uncertainty quantification
3. Confidence intervals
4. Areas of agreement vs disagreement

Final output:
- Consensus recommendation with confidence level
- Minority dissenting views
- Key assumptions requiring validation
- Decision tree for architecture selection""",
    description="Bayesian consensus calculation"
)
```

## Best Practices

1. **Use as many agents as needed:** Deploy agents based on task needs, not arbitrary limits
2. **Clear task boundaries:** Each agent should have independent work
3. **Specific prompts:** Give each agent a focused, clear prompt
4. **Synthesize, don't concatenate:** Merge insights, don't just list them
5. **Attribute clearly:** Credit which agent contributed which insight
6. **Design for synthesis:** Structure agent outputs to be combinable (consistent formats, clear recommendations)

## Supercharged Patterns

### Pattern 4: Recursive Meta-Swarm (Level 0-3 Architecture)

For ultra-complex tasks requiring 50+ agents, use a hierarchical swarm structure where parent agents orchestrate child swarms.

**Architecture Levels:**
- **Level 0 (Leaf Agents):** Individual specialists performing concrete work
- **Level 1 (Domain Swarms):** 3-5 related agents coordinated by a domain lead
- **Level 2 (Meta-Swarm):** Domain leads reporting to integration coordinators
- **Level 3 (Orchestrator):** Final synthesis and decision authority

**Example: Enterprise Architecture Review (50+ agents)**
```
Level 3: Chief Architect (1 agent)
    |
Level 2: Domain Coordinators (5 agents)
    |-- Security Domain Lead
    |-- Backend Domain Lead
    |-- Frontend Domain Lead
    |-- Data Domain Lead
    |-- DevOps Domain Lead
    |
Level 1: Specialized Swarms (15 agents)
    |-- Security Swarm: 3 agents (auditor, pentester, compliance)
    |-- Backend Swarm: 4 agents (architect, API designer, performance, scalability)
    |-- Frontend Swarm: 3 agents (UI, UX, accessibility)
    |-- Data Swarm: 3 agents (engineer, scientist, ML engineer)
    |-- DevOps Swarm: 2 agents (infra, CI/CD)
    |
Level 0: Deep Specialists (30+ agents)
    |-- Each Level 1 agent spawns 2-3 deep specialists as needed
```

**Execution Flow:**
```python
# Phase 1: Dispatch Level 2 coordinators in parallel
Task(subagent_type="senior-architect", prompt="Coordinate security domain review...")
Task(subagent_type="senior-architect", prompt="Coordinate backend domain review...")
# ... etc for each domain

# Phase 2: Each coordinator dispatches their Level 1 swarm
# (Handled automatically by coordinator agents)

# Phase 3: Level 1 agents dispatch Level 0 specialists as needed
# (Dynamic expansion based on findings)

# Phase 4: Synthesis bubbles up from Level 0 → 1 → 2 → 3
```

### Pattern 5: Dynamic Agent Composition Engine

Automatically determine optimal swarm composition based on task complexity analysis.

**Complexity Scoring:**
```python
def calculate_complexity(task_description):
    score = 0
    score += len(task_description.split()) * 0.1  # Length factor
    score += task_description.count("and") * 2      # Multiplicity
    score += task_description.count(",") * 1.5      # List complexity
    score += 10 if "architecture" in task_description else 0
    score += 15 if "security" in task_description else 0
    score += 8 if "performance" in task_description else 0
    score += 12 if "integration" in task_description else 0
    return score

def determine_swarm_size(score):
    if score < 20: return 2
    elif score < 40: return 3
    elif score < 60: return 4
    elif score < 100: return 6
    else: return 8  # Triggers meta-swarm pattern
```

**Dynamic Composition Rules:**
| Complexity | Base Agents | Specialists | Pattern |
|------------|-------------|-------------|---------|
| 0-20 | 2 | 0 | Simple |
| 20-40 | 3 | 0 | Standard |
| 40-60 | 3 | 1 | Enhanced |
| 60-100 | 4 | 2 | Comprehensive |
| 100+ | 6+ | 4+ | Meta-Swarm |

### Pattern 6: Chain-of-Thought Amplification

Force agents to externalize their reasoning before delivering conclusions, enabling cross-agent reasoning validation.

**Prompt Template:**
```
Before providing your final answer, complete these reasoning steps:

1. DECOMPOSITION: Break the problem into sub-problems
2. ASSUMPTIONS: List all assumptions you're making
3. CONSTRAINTS: Identify limiting factors and trade-offs
4. OPTIONS: Generate at least 3 alternative approaches
5. ANALYSIS: Evaluate each option against criteria
6. SELECTION: Justify your recommended approach
7. UNCERTAINTY: State confidence level (0-100%) and unknowns

Only after completing all steps, provide your final output.
```

**Cross-Agent Validation:**
```python
# After receiving CoT outputs, dispatch validators
Task(subagent_type="senior-architect",
     prompt="Review the reasoning chains from 3 agents. Identify logical fallacies, missed assumptions, or incomplete analysis.")

Task(subagent_type="security-auditor",
     prompt="Review the reasoning chains for security blind spots in the thinking process itself.")
```

### Pattern 7: Red Team Swarm

Adversarial swarm pattern where agents actively try to find flaws in each other's work.

**Structure:**
```
Phase 1: Primary swarm produces initial solutions
    - Agent A: Solution proposal
    - Agent B: Alternative solution
    - Agent C: Third approach

Phase 2: Red team analysis (parallel)
    - Red Team 1: Attack Agent A's solution
    - Red Team 2: Attack Agent B's solution
    - Red Team 3: Attack Agent C's solution
    - Cross-Validator: Find flaws red teams missed

Phase 3: Defense and iteration
    - Original agents respond to criticisms
    - Iterate until convergence or exhaustion

Phase 4: Synthesis of hardened solution
```

**Red Team Prompt:**
```
Your role is ADVERSARIAL REVIEW. Your goal is to DESTROY this solution by finding:
- Logical inconsistencies
- Security vulnerabilities
- Scalability bottlenecks
- Edge cases not handled
- Hidden assumptions
- Failure modes

Be ruthless. The solution's author is not your friend. Find every weakness.
Rate severity: CRITICAL | HIGH | MEDIUM | LOW
```

### Pattern 8: Expert Panel Swarm

Simulate a panel of experts with conflicting viewpoints, forcing comprehensive exploration of solution space.

**Panel Composition:**
```python
# For architecture decisions
panel = [
    ("backend-development:backend-architect", "Pragmatist - prioritize delivery speed"),
    ("security-auditor", "Conservative - prioritize safety"),
    ("python-development:python-pro", "Optimizer - prioritize performance"),
    ("code-simplifier:code-simplifier", "Minimalist - prioritize simplicity"),
    ("senior-devops", "Operator - prioritize maintainability")
]

# Each agent gets the same prompt but with their persona prepended
```

**Structured Debate Format:**
```
Round 1: Position Statements (all agents in parallel)
Round 2: Rebuttals (agents respond to 2 other positions)
Round 3: Counter-Rebuttals (defend against attacks)
Round 4: Consensus Building (find common ground)
Round 5: Final Recommendations (converged or minority reports)
```

## Consensus Mechanisms

### Bayesian Weighted Aggregation

When agents disagree, weight their opinions by historical accuracy and confidence.

**Formula:**
```
Weighted Score = Σ(agent_confidence × agent_reliability × recommendation_score)
                 ─────────────────────────────────────────────────────────────
                 Σ(agent_confidence × agent_reliability)

Where:
- agent_confidence: Self-reported 0-100%
- agent_reliability: Historical accuracy (default 0.5, updates over time)
- recommendation_score: Numerical value of recommendation
```

**Implementation:**
```python
def bayesian_aggregate(recommendations):
    """
    recommendations: [
        {"agent": "architect", "confidence": 0.9, "reliability": 0.8, "score": 8},
        {"agent": "security", "confidence": 0.7, "reliability": 0.9, "score": 3},
        {"agent": "performance", "confidence": 0.8, "reliability": 0.7, "score": 7}
    ]
    """
    weighted_sum = sum(r["confidence"] * r["reliability"] * r["score"]
                       for r in recommendations)
    weight_sum = sum(r["confidence"] * r["reliability"]
                     for r in recommendations)

    return weighted_sum / weight_sum if weight_sum > 0 else 0
```

### Uncertainty Quantification

Explicitly track and report uncertainty in swarm outputs.

**Uncertainty Sources:**
1. **Agent disagreement variance:** Standard deviation of recommendations
2. **Confidence spread:** Range of self-reported confidence levels
3. **Knowledge gaps:** Explicit unknowns identified by agents
4. **Assumption count:** Number of unverified assumptions

**Uncertainty Report Template:**
```markdown
## Consensus Analysis

**Aggregated Recommendation:** Use Redis with persistence
**Confidence:** 72% (moderate-high)

**Uncertainty Breakdown:**
- Agent Agreement: 65% (3 of 4 agents agree)
- Average Confidence: 80%
- Confidence Spread: 60-95%
- Explicit Assumptions: 4
- Knowledge Gaps: 2 (Redis cluster behavior under partition, exact failover timing)

**Alternative Views:**
- Security Auditor (25% weight): Recommends database-only (confidence: 60%)
- Reasoning: "Redis adds attack surface, complexity not justified"

**Recommendation:** Proceed with Redis + persistence, but implement database fallback
and monitor for the identified knowledge gaps.
```

## Hallucination Detection

### Cross-Validation Pattern

Detect factual errors through independent verification.

```python
# Phase 1: Primary agents produce outputs
primary_outputs = dispatch_swarm(task, agents=[A, B, C])

# Phase 2: Cross-validation swarm
validators = [
    Task(subagent_type="senior-backend",
         prompt=f"Verify these technical claims: {extract_claims(primary_outputs)}"),
    Task(subagent_type="security-auditor",
         prompt=f"Verify these security claims: {extract_security_claims(primary_outputs)}"),
    Task(subagent_type="python-development:python-pro",
         prompt=f"Verify these implementation claims: {extract_impl_claims(primary_outputs)}")
]

# Phase 3: Flag discrepancies for review
discrepancies = find_conflicts(primary_outputs, validator_outputs)
```

### Consistency Networks

Build a graph of claims and detect contradictions.

```
Claim A: "Use JWT for authentication"
Claim B: "JWT tokens cannot be revoked"
Claim C: "Implement token revocation endpoint"

CONTRADICTION DETECTED: B contradicts C (if JWT can't be revoked, revocation endpoint is impossible)
```

### Fact-Check Swarm

Specialized agents for verifying different claim types.

```python
fact_checkers = {
    "technical": "senior-backend",
    "security": "security-auditor",
    "performance": "python-development:python-pro",
    "api_design": "backend-development:backend-architect",
    "best_practice": "code-simplifier:code-simplifier"
}

# Extract claims by category and dispatch verifiers
for category, agent_type in fact_checkers.items():
    claims = extract_claims_by_category(output, category)
    if claims:
        Task(subagent_type=agent_type,
             prompt=f"Verify these {category} claims: {claims}")
```

## Advanced Execution Workflow

### Dynamic Swarm Sizing

Automatically expand swarm based on task complexity and intermediate findings.

**Auto-Expansion Triggers:**
```python
expansion_triggers = {
    "complexity_threshold": 50,  # Score above which to add specialists
    "uncertainty_threshold": 0.3,  # Uncertainty above which to add validators
    "conflict_detected": True,  # Disagreement triggers mediator
    "security_critical": True,  # Security tasks always get extra audit
    "performance_critical": True,  # Performance tasks get optimization specialist
    "novel_domain": True,  # Unfamiliar domains get researcher
}

def evaluate_expansion(outputs, triggers):
    additional_agents = []

    if calculate_disagreement(outputs) > triggers["uncertainty_threshold"]:
        additional_agents.append("mediator")
        additional_agents.append("tie_breaker")

    if any("security" in o.lower() for o in outputs):
        additional_agents.append("security-auditor")

    return additional_agents
```

### Adaptive Agent Selection

Select agents based on task characteristics, not just domain.

```python
def select_agents_adaptive(task_description, available_agents):
    # Extract task characteristics
    characteristics = {
        "security_focus": "security" in task_description.lower(),
        "performance_critical": any(w in task_description.lower()
                                     for w in ["scale", "performance", "fast"]),
        "legacy_code": any(w in task_description.lower()
                           for w in ["refactor", "legacy", "old"]),
        "greenfield": any(w in task_description.lower()
                          for w in ["new", "create", "build"]),
        "integration_heavy": any(w in task_description.lower()
                                 for w in ["integrate", "connect", "api"]),
    }

    # Score each agent by match
    agent_scores = {}
    for agent in available_agents:
        score = 0
        if characteristics["security_focus"] and agent == "security-auditor":
            score += 10
        if characteristics["performance_critical"] and "pro" in agent:
            score += 5
        # ... etc
        agent_scores[agent] = score

    # Select top N agents
    return sorted(agent_scores, key=agent_scores.get, reverse=True)[:4]
```

## Limitations

- Agents work independently (no inter-agent communication)
- Synthesis is manual (you combine the outputs)
- Not suitable for tasks with tight coupling between components
- Each agent has its own context window limit
- Synthesis complexity increases with agent count (consider hierarchical patterns for 20+ agents)

## Error Handling

### Agent Failure Scenarios

**Single Agent Failure (2 of 3 succeed):**
1. Note the failure in synthesis: "[Security review unavailable due to agent timeout]"
2. Proceed with outputs from successful agents
3. Present partial results to user with disclaimer
4. Offer to retry the specific failed agent

**Multiple Agent Failures (2+ of 3 fail):**
1. Halt synthesis - insufficient perspectives for quality output
2. Report failure pattern to user
3. Offer retry with same agents OR sequential fallback
4. If persistent failures, use single `Skill()` invocation instead

**Timeout Handling:**
- Default timeout: 180 seconds per agent
- If agent times out: Mark as "incomplete" and proceed with others
- Never wait indefinitely for slow agents

### Conflict Resolution

When agents return contradictory recommendations:

**Step 1: Identify the conflict**
```
[Backend Architect] recommends: Use Redis for session storage
[Security Auditor] recommends: Use database-backed sessions only
```

**Step 2: Analyze trade-offs**
- Performance vs Security
- Complexity vs Maintainability
- Cost vs Reliability

**Step 3: Present options to user**
```markdown
## Conflict Detected

**Option A: Prioritize Performance** (Backend Architect)
- Use Redis for session storage
- Pros: Fast, scalable
- Cons: Additional failure point, data durability concerns

**Option B: Prioritize Security** (Security Auditor)
- Use database-backed sessions
- Pros: Durable, single source of truth
- Cons: Slower, database load

**Option C: Hybrid** (Compromise)
- Use Redis with persistence enabled
- Database as fallback for critical sessions
```

**Step 4: Document resolution**
Note which option was chosen and why in the final output.

## Integration with Other Skills

### horde-learn Integration

Before swarming a complex task, use `horde-learn` to extract insights from relevant documentation:

```python
# Step 1: Learn from existing documentation
Skill("horde-learn", "Extract patterns from: /docs/architecture-guide.md")

# Step 2: Use extracted patterns in swarm prompts
Task(subagent_type="backend-development:backend-architect",
     prompt="Design API following patterns: [extracted patterns]")
```

**Advanced Integration Pattern:**
```python
# Pre-swarm insight extraction for knowledge-intensive tasks
insights = Skill("horde-learn", """
Extract from:
1. /docs/architecture/decisions/ - All ADRs
2. /docs/api/guidelines.md
3. /docs/security/requirements.md

Focus: Patterns relevant to authentication system design
""")

# Use insights to inform swarm composition
if "microservices" in insights:
    swarm_agents.append("backend-development:microservices-patterns")
if "event-sourcing" in insights:
    swarm_agents.append("backend-development:event-sourcing-architect")
if "high-security" in insights:
    swarm_agents.append("security-auditor")

# Dispatch informed swarm
for agent in swarm_agents:
    Task(subagent_type=agent,
         prompt=f"Design auth system using context: {insights}")
```

### dispatching-parallel-agents Skill

If available, `dispatching-parallel-agents` provides similar functionality with more automation. Use this skill for:
- Manual control over agent selection
- Custom synthesis requirements
- Learning/debugging swarm patterns

### horde-plan Integration

Use `horde-plan` to create comprehensive implementation plans before dispatching swarms for execution:

```python
# Step 1: Create detailed implementation plan
Skill("horde-plan", """
Create implementation plan for: User authentication system

Requirements:
- JWT-based authentication
- Password reset flow
- OAuth integration
- Rate limiting

Output: Phased implementation plan with dependencies
""")

# Step 2: Dispatch swarm to execute plan phases in parallel where possible
Task(subagent_type="backend-development:backend-architect",
     prompt="Implement Phase 1: Core auth architecture from plan: [plan_details]")

Task(subagent_type="security-auditor",
     prompt="Review and harden Phase 2: Security layer from plan: [plan_details]")

Task(subagent_type="python-development:fastapi-pro",
     prompt="Implement Phase 3: FastAPI endpoints from plan: [plan_details]")
```

**Plan-to-Swarm Workflow:**
1. Use `horde-plan` to create structured implementation plan
2. Parse plan to identify parallelizable tasks
3. Dispatch appropriate agent swarm for each phase
4. Synthesize results between phases
5. Use `implementation-status` to verify completion

### code-reviewer Skill Integration

Integrate comprehensive code review into swarm workflows:

```python
# Phase 1: Implementation swarm
Task(subagent_type="python-development:fastapi-pro",
     prompt="Implement feature X")

Task(subagent_type="frontend-mobile-development:frontend-developer",
     prompt="Build UI for feature X")

# Phase 2: Parallel review swarm
Task(subagent_type="feature-dev:code-reviewer",
     prompt="Review implementation for bugs, logic errors, security issues")

Task(subagent_type="security-auditor",
     prompt="Security-focused review of implementation")

Task(subagent_type="code-simplifier",
     prompt="Review for simplification opportunities")

# Phase 3: Address findings
# (Iterative improvement based on review outputs)
```

### implementation-status Integration

Use `implementation-status` to audit swarm work before final delivery:

```python
# After swarm completes implementation
Skill("implementation-status", """
Audit implementation against original plan:
- Plan path: .claude/plans/feature-implementation.md
- Check all phases complete
- Identify any missing deliverables
""")

# If 100% complete, proceed to critical review
Skill("horde-review", """
Review completed implementation:
- Files changed: [list]
- Domains: Backend, Security, Frontend
""")
```

### Skill-to-Swarm Mapping Reference

| Skill | Use Case | Corresponding Swarm Agents |
|-------|----------|---------------------------|
| `horde-learn` | Pre-swarm knowledge extraction | N/A (prerequisite) |
| `horde-plan` | Implementation planning | senior-architect, senior-backend |
| `code-reviewer` | Post-implementation review | feature-dev:code-reviewer, superpowers:code-reviewer |
| `implementation-status` | Completion audit | N/A (validation) |
| `horde-review` | Final validation | Domain specialists based on implementation |
| `generate-tests` | Test generation | senior-backend, python-development:python-pro |
| `senior-prompt-engineer` | Prompt optimization | agent-orchestration:context-manager |
| `systematic-debugging` | Error recovery and root cause analysis | N/A (error handler) |

## Enhanced Error Handling

### Swarm Recovery Patterns

**Pattern 1: Graceful Degradation**
```python
# When 1 of 3 agents fail, continue with partial results
successful = [r for r in results if r.status == "success"]
if len(successful) >= 2:
    # Proceed with synthesis, noting missing perspective
    synthesis = f"""
    [Synthesis based on {len(successful)} of 3 agents]

    NOTE: {3 - len(successful)} agent(s) failed to respond.
    Missing perspectives: [list failed agent types]
    Consider re-running for complete analysis.
    """
```

**Pattern 2: Retry with Escalation**
```python
# First failure: Retry same agent
# Second failure: Escalate to more capable agent
# Third failure: Proceed without that perspective

def dispatch_with_retry(agent_type, prompt, max_retries=2):
    for attempt in range(max_retries):
        result = Task(subagent_type=agent_type, prompt=prompt)
        if result.status == "success":
            return result

    # Escalation mapping
    escalation = {
        "python-development:fastapi-pro": "python-development:python-pro",
        "frontend-mobile-development:frontend-developer": "senior-fullstack",
        "backend-development:backend-architect": "senior-architect"
    }

    if agent_type in escalation:
        return Task(subagent_type=escalation[agent_type], prompt=prompt)

    return None  # Proceed without this perspective
```

**Pattern 3: Conflict Resolution Swarm**
```python
# When agents disagree, dispatch a mediator swarm
conflicts = detect_conflicts(results)
if conflicts:
    mediator_results = [
        Task(subagent_type="senior-architect",
             prompt=f"Mediate this conflict: {conflicts}"),
        Task(subagent_type="cto-advisor",
             prompt=f"Executive decision on: {conflicts}"),
        Task(subagent_type="senior-backend",
             prompt=f"Technical analysis of trade-offs: {conflicts}")
    ]
    # Synthesize mediator outputs for final resolution
```

### Automatic Debugging on Failure

When an agent fails, returns errors, or produces unexpected results, dispatch `systematic-debugging` to analyze and recover:

**Trigger Conditions:**
- Agent returns error or exception
- Agent output contradicts other agents (conflict detected)
- Agent times out or stalls
- Agent produces output that fails validation

**Integration Pattern:**
```python
# Primary swarm dispatch
results = [
    Task(subagent_type="backend-architect", prompt="Implement API..."),
    Task(subagent_type="security-auditor", prompt="Review security...")
]

# Check for failures
failed = [r for r in results if r.status == "failed" or r.has_errors()]

if failed:
    # Dispatch debugger in parallel with remaining work
    debug_results = [
        Task(subagent_type="systematic-debugging",
             prompt=f"Agent {f.agent_type} failed with: {f.error}. Analyze root cause and recommend fix.")
        for f in failed
    ]

    # Apply fixes and retry
    for debug in debug_results:
        if debug.fix_available:
            retry_agent(debug.original_agent, debug.fix_context)
```

**Debugger Output Format:**
- Root cause analysis
- Fix recommendation (context to add, different approach, or escalate)
- Confidence score (0-100%)
- Retry strategy

**When to Escalate to User:**
- Debugger confidence < 60%
- Same agent fails 3 times despite debugging
- Root cause is architectural/design flaw

### Timeout and Resource Management

**Adaptive Timeout Calculation:**
```python
def calculate_timeout(task_complexity, agent_type):
    base_timeout = 180  # 3 minutes

    # Complexity multiplier
    complexity_multipliers = {
        "low": 1.0,
        "medium": 1.5,
        "high": 2.5,
        "extreme": 4.0
    }

    # Agent type adjustments
    agent_overhead = {
        "senior-architect": 60,  # Extra time for complex reasoning
        "security-auditor": 30,  # Security analysis takes longer
        "python-development:python-pro": 0  # Standard timing
    }

    multiplier = complexity_multipliers.get(task_complexity, 1.0)
    overhead = agent_overhead.get(agent_type, 0)

    return int(base_timeout * multiplier + overhead)
```

**Resource Tracking:**
```python
# Track swarm execution metrics for optimization
class SwarmMetrics:
    def __init__(self):
        self.dispatched_agents = 0
        self.completed_agents = 0
        self.failed_agents = 0

    def record_dispatch(self, agent_type):
        self.dispatched_agents += 1

    def record_completion(self, agent_type, duration_ms):
        self.used_agents += 1
        self.used_tokens += actual_tokens

## Swarm Templates

Ready-to-use swarm configurations for common scenarios. Copy and adapt these templates for your specific needs.

### Template 1: Database Migration Review

**Use Case:** Reviewing database schema changes and migration safety

```python
# Database Migration Review Swarm
Task(
    subagent_type="database-migrations:database-admin",
    prompt="""Review database migration for safety and best practices.

Migration details:
- [Describe migration: adding columns, indexes, schema changes]
- Database: [PostgreSQL/MySQL/etc.]
- Table size: [approximate row count]
- Migration type: [Online/Offline required]

Review for:
1. Lock safety (will it acquire dangerous locks?)
2. Performance impact on large tables
3. Rollback strategy
4. Data integrity risks
5. Index creation strategy

Output: Migration safety report with recommendations""",
    description="DB migration safety review"
)

Task(
    subagent_type="database-migrations:database-optimizer",
    prompt="""Analyze migration performance implications.

Migration: [same details as above]

Focus:
1. Query performance after migration
2. Index optimization opportunities
3. Statistics update requirements
4. Query plan changes expected
5. Connection pool impact

Output: Performance optimization recommendations""",
    description="Migration performance analysis"
)

Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Review application-level migration handling.

Migration: [same details]
Application: [framework/stack]

Check:
1. ORM compatibility
2. Connection handling during migration
3. Application deployment coordination
4. Feature flags needed
5. Zero-downtime feasibility

Output: Application integration recommendations""",
    description="App-level migration review"
)
```

### Template 2: ML Model Deployment

**Use Case:** Deploying ML models to production with MLOps best practices

```python
# ML Model Deployment Swarm
Task(
    subagent_type="senior-ml-engineer",
    prompt="""Design ML model deployment architecture.

Model details:
- Framework: [TensorFlow/PyTorch/sklearn/etc.]
- Model size: [GB/parameters]
- Latency requirements: [p99 target]
- Throughput: [requests/second]
- Environment: [AWS/GCP/Azure/on-prem]

Design:
1. Model serving architecture (real-time vs batch)
2. Scaling strategy
3. A/B testing setup
4. Model versioning approach
5. Rollback procedures

Output: Deployment architecture document""",
    description="ML deployment architecture"
)

Task(
    subagent_type="mlops-engineer",
    prompt="""Design MLOps pipeline for model deployment.

Model: [same details]

Create:
1. CI/CD pipeline for model artifacts
2. Model registry integration
3. Monitoring and alerting setup
4. Data drift detection
5. Automated retraining triggers

Output: MLOps pipeline specification""",
    description="MLOps pipeline design"
)

Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Design API layer for model serving.

Model: [same details]

Define:
1. REST/gRPC API schema
2. Request/response validation
3. Error handling patterns
4. Rate limiting strategy
5. Authentication/authorization

Output: API design specification""",
    description="Model serving API design"
)
```

### Template 3: Accessibility Audit

**Use Case:** Comprehensive accessibility review of web application

```python
# Accessibility Audit Swarm
Task(
    subagent_type="web-accessibility-checker",
    prompt="""Perform WCAG compliance audit.

Application:
- URL: [application URL]
- Framework: [React/Vue/Angular/etc.]
- WCAG target level: [A/AA/AAA]

Audit:
1. Automated WCAG violations
2. Keyboard navigation issues
3. Screen reader compatibility
4. Color contrast compliance
5. Focus management
6. ARIA implementation

Output: WCAG compliance report with violation details""",
    description="WCAG compliance audit"
)

Task(
    subagent_type="ux-researcher-designer",
    prompt="""Evaluate accessibility from UX perspective.

Application: [same details]

Review:
1. User flow accessibility
2. Alternative text quality
3. Form labeling and error messaging
4. Time-based content handling
5. Cognitive accessibility
6. Mobile accessibility

Output: UX accessibility recommendations""",
    description="UX accessibility review"
)

Task(
    subagent_type="frontend-mobile-development:frontend-developer",
    prompt="""Review code-level accessibility implementation.

Codebase: [repository path]

Check:
1. Semantic HTML usage
2. ARIA attributes correctness
3. Keyboard event handling
4. Focus trap implementation
5. Skip links and landmarks
6. Component accessibility patterns

Output: Code-level fixes and patterns""",
    description="Frontend accessibility code review"
)
```

### Template 4: Legacy Code Modernization

**Use Case:** Modernizing legacy codebase with architectural improvements

```python
# Legacy Modernization Swarm
Task(
    subagent_type="architecture-modernizer",
    prompt="""Create modernization strategy for legacy codebase.

Current state:
- Language/Framework: [e.g., Java 8, jQuery, etc.]
- Architecture: [monolith/microservices]
- Pain points: [list key issues]
- Target state: [desired modern stack]

Develop:
1. Migration strategy (big bang vs incremental)
2. Service decomposition plan
3. Data migration approach
4. Risk mitigation strategies
5. Rollback procedures

Output: Modernization roadmap""",
    description="Modernization strategy"
)

Task(
    subagent_type="senior-backend",
    prompt="""Design target architecture for modernization.

Current: [legacy details]
Target: [modern stack details]

Design:
1. Clean architecture layers
2. API contracts and versioning
3. Database modernization
4. Testing strategy
5. Deployment architecture

Output: Target architecture specification""",
    description="Target architecture design"
)

Task(
    subagent_type="code-simplifier",
    prompt="""Identify immediate refactoring opportunities.

Codebase: [repository path]

Find:
1. Dead code elimination
2. Code duplication consolidation
3. Complexity reduction opportunities
4. Test coverage gaps
5. Dependency cleanup

Output: Immediate refactoring recommendations""",
    description="Refactoring opportunities"
)
```

### Template 5: Dependency Security Audit

**Use Case:** Auditing project dependencies for security vulnerabilities

```python
# Dependency Security Audit Swarm
Task(
    subagent_type="dependency-manager",
    prompt="""Analyze project dependencies for vulnerabilities.

Project:
- Language: [Python/Node.js/Java/etc.]
- Package files: [requirements.txt/package.json/etc.]
- Current versions: [list or file path]

Analyze:
1. Known CVEs in dependencies
2. License compliance issues
3. Outdated dependencies
4. Supply chain risks
5. Transitive dependency issues

Output: Dependency audit report""",
    description="Dependency vulnerability scan"
)

Task(
    subagent_type="security-auditor",
    prompt="""Security review of dependency usage.

Project: [same details]

Review:
1. Secrets/credentials in dependencies
2. Network access by dependencies
3. Privilege escalation risks
4. Malicious package detection
5. Pinning vs updating strategy

Output: Security risk assessment""",
    description="Dependency security review"
)

Task(
    subagent_type="backend-development:backend-architect",
    prompt="""Design secure dependency management strategy.

Project: [same details]

Create:
1. Dependency update policy
2. Automated scanning setup
3. Vulnerability response process
4. Private registry strategy
5. SBOM generation approach

Output: Dependency management strategy""",
    description="Secure dependency strategy"
)
```

### Template 6: Self-Healing Implementation Swarm

**Use Case:** Implementation tasks with automatic error recovery

```python
# Phase 1: Implementation
impl_results = [
    Task(subagent_type="python-development:fastapi-pro",
         prompt="Implement feature X..."),
    Task(subagent_type="frontend-mobile-development:frontend-developer",
         prompt="Build UI for feature X...")
]

# Phase 2: Debug failures (if any)
failures = [r for r in impl_results if r.status != "success"]
if failures:
    debug_results = [
        Task(subagent_type="systematic-debugging",
             prompt=f"Debug failure: {f.error}. Original task: {f.task}")
        for f in failures
    ]

    # Phase 3: Retry with fixes
    for debug in debug_results:
        if debug.confidence > 70:
            Task(subagent_type=debug.original_agent,
                 prompt=f"{debug.original_prompt}\n\nFix context: {debug.fix_context}")
```

### Template Usage Guide

1. **Select Template:** Choose the template matching your task type
2. **Fill Context:** Replace bracketed placeholders with your specific details
3. **Customize:** Add domain-specific requirements as needed
4. **Dispatch:** Send all tasks in a single response for parallel execution
5. **Synthesize:** Combine outputs into actionable recommendations
```
