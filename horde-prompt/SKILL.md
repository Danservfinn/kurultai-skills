---
name: horde-prompt
version: "1.0"
description: >
  Standalone utility for generating optimized prompts for horde agent types.
  Analyzes task description + target agent type + context → produces
  token-efficient, task-specific prompt. Used by skill authors when creating
  or maintaining horde skills. Supports 60+ agent types across 3 tiers
  (implementation, system, judgment) with dynamic prompt generation.
integrations:
  - golden-horde
  - horde-swarm
  - horde-skill-creator
tags:
  - prompt-engineering
  - agent-orchestration
  - utility
  - token-optimization
author: kurultai
---

# Horde Prompt

Standalone utility for generating optimized prompts for horde agent types. Analyzes task descriptions, target agent types, and execution context to produce token-efficient, task-specific prompts.

## Overview

**Primary Use Case:** Skill authors who need to generate optimized prompts when creating or maintaining horde skills.

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: task_description + agent_type + [context]           │
│                             ↓                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  horde-prompt Analysis Engine                          │  │
│  │  ├─ Task Complexity Scorer                            │  │
│  │  ├─ Agent Type Selector                               │  │
│  │  ├─ Context Analyzer                                  │  │
│  │  └─ Prompt Generator                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                             ↓                               │
│  OUTPUT: optimized_prompt + metadata                       │
└─────────────────────────────────────────────────────────────┘
```

## When to Use

Invoke `/horde-prompt` when:
- Creating a new skill and need agent prompts
- Optimizing existing prompts for token efficiency
- Generating prompts for new agent types
- Adapting prompts for specific task contexts

**Examples:**
```bash
# Generate prompt for backend architect
/horde-prompt "Design a REST API for user authentication" --agent backend-architect

# Generate with context
/horde-prompt "Review this code for security issues" --agent security-auditor --context '{"codebase": "fastapi", "focus": "owasp"}'

# Optimize existing prompt
/horde-prompt --optimize --agent cost-analyst
```

## Input/Output Contract

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_description` | string | Yes | The task the agent will perform |
| `agent_type` | string | Yes | Target agent type (e.g., `backend-architect`, `cost-analyst`) |
| `context` | dict | No | Additional context (codebase type, constraints, etc.) |
| `token_budget` | string | No | `minimal` | `standard` | `verbose` (default: standard) |
| `pattern` | string | No | Golden-horde pattern for protocol injection |

### Output

```json
{
  "prompt": "ROLE: backend-architect\n...",
  "estimated_tokens": 127,
  "compression_ratio": 0.65,
  "agent_tier": "implementation",
  "confidence": 0.92,
  "optimizations_applied": ["compact_syntax", "context_injection", "structured_output"]
}
```

## Agent Type Registry

horde-prompt supports 60+ agent types organized by tier:

### Tier 1: Implementation Agents (35+)

| Domain | Agent Types |
|--------|-------------|
| Backend | `backend-architect`, `event-sourcing-architect`, `graphql-architect`, `tdd-orchestrator`, `temporal-python-pro`, `microservices-patterns`, `saga-orchestration` |
| Frontend | `frontend-developer`, `mobile-developer` |
| Python | `fastapi-pro`, `django-pro`, `python-pro` |
| Data/ML | `senior-data-engineer`, `senior-ml-engineer`, `data-scientist` |
| DevOps | `senior-devops`, `mlops-engineer` |
| Database | `database-admin`, `database-optimizer` |
| Security | `security-auditor` |
| Analysis | `dependency-manager`, `url-context-validator`, `web-accessibility-checker` |

### Tier 2: System Agents (10+)

| Agent Type | Best For |
|------------|----------|
| `Plan` | Planning phases, architecture design |
| `Explore` | Codebase exploration, file patterns |
| `Bash` | Command execution, git operations |
| `general-purpose` | Catch-all, judgment roles |
| `code-reviewer` | Multi-subagent code review |

### Tier 3: Judgment Agents (15+)

| Agent Type | Evaluation Focus |
|------------|------------------|
| `cost-analyst` | Token/compute/infra costs |
| `chaos-engineer` | Failure modes, resilience |
| `compliance-auditor` | SOC2/GDPR/HIPAA compliance |
| `migration-strategist` | Migration risk, rollback strategies |
| `api-contract-designer` | API contracts, schema compatibility |
| `performance-profiler` | Bottlenecks, benchmarks |
| `tech-debt-assessor` | Tech debt quantification |
| `integration-tester` | Integration test strategies |

## Agent Coverage

horde-prompt supports 47+ agent types across 3 tiers, covering 100% of golden-horde agent types:

| Tier | Count | Examples |
|------|-------|----------|
| Implementation | 36+ | backend-architect, documentation-expert, nextjs-architecture-expert, react-performance-optimizer, architecture-modernizer, code-simplifier |
| System | 7+ | Plan, Explore, Bash, general-purpose, agent-expert, context-manager, code-reviewer |
| Judgment | 8+ | cost-analyst, chaos-engineer, compliance-auditor, migration-strategist, api-contract-designer, performance-profiler, tech-debt-assessor, integration-tester |

**Coverage:** 100% of golden-horde agent types as of v1.0. All newly added agents (documentation-expert, nextjs-architecture-expert, react-performance-optimizer, architecture-modernizer, code-simplifier, url-context-validator, url-link-extractor, feature-dev-code-reviewer, feature-dev-code-explorer, feature-dev-code-architect, agent-expert, context-manager) are included.

## Prompt Generation Process

### Step 1: Task Analysis

```
task_description → complexity_score (0-100)

Factors:
- Task length (words)
- Technical complexity (keywords)
- Domain specificity
- Constraint count

Score < 20: minimal prompt sufficient
Score 20-50: standard prompt
Score > 50: verbose + examples
```

### Step 2: Agent Type Selection

```
agent_type lookup:
├── Verify agent exists in registry
├── Retrieve tier (implementation/system/judgment)
├── Get domain expertise
└── Load base prompt template
```

### Step 3: Context Injection

```
context analysis:
├── Extract relevant constraints
├── Identify domain-specific patterns
├── Determine output format requirements
└── Inject task-specific guidance
```

### Step 4: Prompt Generation

```
Dynamic prompt = base_template
                + domain_expertise
                + task_guidance
                + context_constraints
                + output_format
                + message_protocol (if golden-horde)
```

### Step 5: Token Optimization

```
Apply optimizations based on token_budget:
├── minimal: KEY:value syntax, no examples
├── standard: Balanced syntax, key examples
└── verbose: Full prose, multiple examples
```

## Prompt Syntax

### Compact (Minimal)

```
ROLE: backend-architect
DOMAIN: api|microservices|scalability
TASK: {task_description}
OUTPUT: architecture|specs|endpoints
```

### Standard (Default)

```
You are a Backend Architect specializing in API design and microservices.

DOMAIN EXPERTISE:
- RESTful API design patterns
- Microservices architecture
- Database design and optimization
- Scalability and performance

TASK: {task_description}

OUTPUT FORMAT:
Provide:
1. High-level architecture
2. API endpoints specification
3. Data models
4. Integration considerations
```

### Verbose (with Examples)

```
[Full prose introduction with examples and detailed guidance]
```

## Pattern-Specific Protocols

When `pattern` is specified, inject protocol instructions:

| Pattern | Protocol |
|---------|----------|
| `review-loop` | Iteration instructions, feedback format |
| `adversarial-debate` | Position advocacy, rebuttal structure |
| `assembly-line` | Handoff protocols, backward communication |
| `consensus-deliberation` | Independent analysis, challenge protocol |
| `watchdog` | Violation detection, correction protocol |

## Usage Examples

### Example 1: Generate Prompt for New Skill

```bash
/horde-prompt "Create a GraphQL API for e-commerce product catalog" --agent graphql-architect
```

Output:
```
ROLE: graphql-architect
DOMAIN: graphql|federation|schema-design

TASK: Create a GraphQL API for e-commerce product catalog

EXPERTISE:
- GraphQL schema design with type definitions
- Federation patterns for microservices
- Query optimization (dataloaders, batching)
- Relay cursor-based pagination

OUTPUT:
- Type definitions (Product, Category, etc.)
- Query/Mutation definitions
- Federation entity specifications
- Performance optimization strategies
```

### Example 2: Generate with Context

```bash
/horde-prompt "Optimize database queries for slow dashboard" --agent database-optimizer --context '{"db_type": "postgresql", "slow_queries": 15}'
```

### Example 3: Generate for Golden-Horde Pattern

```bash
/horde-prompt "Review this authentication system" --agent security-auditor --pattern review-loop
```

Output includes review-loop protocol:
```
[Base prompt]

REVIEW LOOP PROTOCOL:
- You are the reviewer in a 2-agent review loop
- Identify at least 2 specific security issues
- Provide severity (CRITICAL/HIGH/MEDIUM/LOW)
- Include remediation for each finding
- Send feedback via SendMessage
- Continue until producer addresses findings or max rounds reached
```

## Optimization Techniques

### Token Compression

| Technique | Savings | Applied When |
|-----------|---------|--------------|
| Compact syntax | 40-50% | token_budget=minimal |
| List shorthand | 15-20% | 3+ items |
| Inheritance | 30-40% | Shared patterns |
| Example reference | 50-100% | Standard examples available |

### Quality Preservation

- **Semantic scaffolding preserved**: Critical phrases ("step by step", "carefully") maintained
- **Anti-sycophancy**: Conditional logic (not quotas) for judgment agents
- **Output structure**: Explicit format requirements maintained
- **Domain expertise**: Agent-specific knowledge injected

## Integration with Other Skills

### With horde-skill-creator

horde-skill-creator uses horde-prompt to generate agent prompts when creating new skills:

```
horde-skill-creator → needs agent prompts → horde-prompt
```

### With golden-horde

Skill authors can use horde-prompt to generate prompts for custom golden-horde patterns:

```python
# In custom skill
from horde_prompt import generate_prompt

prompt = generate_prompt(
    task_description="Evaluate architecture...",
    agent_type="cost-analyst",
    pattern="adversarial-debate",
    token_budget="standard"
)

Task(subagent_type="general-purpose", prompt=prompt)
```

### Standalone Usage

Skill authors can invoke directly to iterate on prompts:

```bash
# Try different token budgets
/horde-prompt "Task..." --agent backend-architect --token-budget minimal
/horde-prompt "Task..." --agent backend-architect --token-budget verbose

# Compare outputs
# Choose optimal balance of tokens vs. specificity
```

## File Structure

```
horde-prompt/
├── SKILL.md                    # This file
├── CLAUDE.md                   # Usage notes for skill authors
├── prompts.py                  # Agent registry + generation logic
├── optimizers/
│   ├── __init__.py
│   ├── compressor.py           # Token compression
│   ├── context_analyzer.py     # Context extraction
│   └── pattern_injectors.py    # Pattern protocols
├── tests/
│   ├── test_generation.py      # Prompt generation tests
│   ├── test_compression.py     # Token efficiency tests
│   └── fixtures/               # Test cases
└── examples/
    ├── backend_prompts.md      # Example prompts by domain
    ├── judgment_prompts.md     # Example judgment agent prompts
    └── patterns.md             # Pattern protocol examples
```

## API Reference

### `generate_prompt(task, agent_type, context=None, token_budget='standard', pattern=None)`

Generate an optimized prompt for the given task and agent type.

**Parameters:**
- `task` (str): Task description
- `agent_type` (str): Agent type from registry
- `context` (dict, optional): Additional context
- `token_budget` (str): `minimal` | `standard` | `verbose`
- `pattern` (str, optional): Golden-horde pattern for protocol injection

**Returns:**
```python
{
    "prompt": str,              # Generated prompt
    "estimated_tokens": int,    # Estimated token count
    "compression_ratio": float, # Tokens saved vs. verbose baseline
    "agent_tier": str,          # Tier classification
    "confidence": float,        # Generation confidence (0-1)
    "optimizations": list       # Applied optimizations
}
```

### `list_agents(tier=None, domain=None)`

List available agent types, optionally filtered.

**Parameters:**
- `tier` (str, optional): Filter by tier (`implementation`, `system`, `judgment`)
- `domain` (str, optional): Filter by domain (`backend`, `frontend`, `security`, etc.)

**Returns:** List of agent type dictionaries with metadata.

### `validate_prompt(prompt, agent_type)`

Validate a prompt against agent type requirements.

**Returns:** Validation result with issues and suggestions.

## Best Practices

### For Skill Authors

1. **Start with `standard` token budget** - Balance between brevity and clarity
2. **Use `pattern` parameter** for golden-horde agents - Ensures proper protocol
3. **Provide context** - Domain, constraints, frameworks improve prompt quality
4. **Test with minimal first** - Verify compact prompts work before adding verbosity
5. **Iterate on compression** - Use validation to find optimal token budget

### Token Budget Guidelines

| Budget | Use When | Target Tokens |
|--------|----------|---------------|
| `minimal` | Well-defined tasks, simple contexts | 50-80 |
| `standard` | Most tasks, balanced approach | 100-150 |
| `verbose` | Complex tasks, novel domains | 200-300 |

### Anti-Sycophancy Patterns

For judgment/reviewer agents, use conditional logic:

```
IF issues_found > 0:
    report all issues with severity and remediation
ELSE:
    state "No issues found. Verified: [checklist_items]"
```

NOT:
```
MUST find at least 2 issues  # Causes fabrication
```

## See Also

- **golden-horde**: Master orchestration skill that uses optimized prompts
- **horde-swarm**: Agent type registry reference
- **horde-skill-creator**: Skill creation workflow that uses horde-prompt
- **CLAUDE.md**: Detailed usage examples for skill authors
