# horde-prompt: Usage Guide for Skill Authors

This guide provides practical examples for skill authors using horde-prompt.

## Quick Start

### Generate a Prompt for an Agent

```python
from horde_prompt import generate_prompt

result = generate_prompt(
    task="Design a REST API for user authentication with JWT tokens",
    agent_type="backend-architect",
    token_budget="standard"
)

print(result["prompt"])
```

### Available Token Budgets

| Budget | Description | Target Tokens | Use When |
|--------|-------------|---------------|----------|
| `minimal` | Compact KEY:value syntax | 50-80 | Well-defined tasks, simple contexts |
| `standard` | Balanced approach (default) | 100-150 | Most tasks |
| `verbose` | Full prose with examples | 200-300 | Complex tasks, novel domains |

## Common Patterns

### Pattern 1: Creating a New Skill

When creating a new horde skill, use horde-prompt to generate agent prompts:

```python
from horde_prompt import generate_prompt

# Generate prompt for the primary agent
primary_agent_prompt = generate_prompt(
    task="Implement the core feature logic",
    agent_type="python-pro",
    context={"framework": "fastapi"}
)

# Generate prompt for the reviewer
reviewer_prompt = generate_prompt(
    task="Review the implementation for bugs and security issues",
    agent_type="security-auditor",
    pattern="review-loop",
    token_budget="standard"
)
```

### Pattern 2: Golden-Horde Integration

For golden-horde patterns, always specify the `pattern` parameter:

```python
from horde_prompt import generate_prompt

# Review Loop pattern
prompt = generate_prompt(
    task="Review this architecture design",
    agent_type="cost-analyst",
    pattern="review-loop"
)

# The prompt will include review-loop protocol instructions:
# REVIEW LOOP PROTOCOL:
# - You are participating in an iterative review cycle
# - Review artifacts thoroughly and identify specific issues
# ...
```

### Pattern 3: Context-Aware Prompting

Provide context for better prompts:

```python
from horde_prompt import generate_prompt

prompt = generate_prompt(
    task="Optimize slow database queries",
    agent_type="database-optimizer",
    context={
        "db_type": "postgresql",
        "slow_queries": 15,
        "table_size": "10M rows"
    },
    token_budget="standard"
)
```

### Pattern 4: Finding the Right Agent

List agents to find the right one for your task:

```python
from horde_prompt import list_agents

# List all backend agents
backend_agents = list_agents(domain="backend")
for agent in backend_agents:
    print(f"{agent['type']} - {agent['tier']}")

# List all judgment agents
judgment_agents = list_agents(tier="judgment")
```

### Pattern 5: Golden-Horde Multi-Agent Team

When implementing golden-horde patterns with multiple agents, use horde-prompt to generate consistent prompts for all team members:

```python
from horde_prompt import generate_prompt

# Review Loop pattern with producer + reviewer
producer_prompt = generate_prompt(
    task="Produce initial artifact for user authentication system",
    agent_type="backend-architect",
    pattern="review-loop",
    token_budget="standard"
)

reviewer_prompt = generate_prompt(
    task="Review the artifact for security vulnerabilities",
    agent_type="security-auditor",
    pattern="review-loop",
    token_budget="standard"
)

# Both prompts include review-loop protocol instructions:
# REVIEW LOOP PROTOCOL:
# - You are in a review loop with a producer agent
# - Review artifacts thoroughly and identify specific issues
# - Provide feedback with actionable, specific guidance
# - Continue iterations until satisfactory or max rounds reached

# Generate for adversarial debate
proponent_prompt = generate_prompt(
    task="Advocate for PostgreSQL as the database choice",
    agent_type="database-admin",
    pattern="adversarial-debate"
)

opponent_prompt = generate_prompt(
    task="Advocate for MongoDB as the database choice",
    agent_type="database-admin",
    pattern="adversarial-debate"
)

# Both prompts include adversarial-debate protocol instructions
```

## Example: Creating a Custom Skill

Here's how to use horde-prompt when building a custom skill:

```python
# my_custom_skill/SKILL.md

# When spawning agents in your skill:

def spawn_review_agents(task_description):
    from horde_prompt import generate_prompt

    # Primary reviewer
    primary_prompt = generate_prompt(
        task=task_description,
        agent_type="security-auditor",
        pattern="review-loop"
    )

    Task(
        team_name="review-team",
        name="security-reviewer",
        subagent_type="security-auditor",
        prompt=primary_prompt["prompt"]
    )

    # Secondary reviewer
    secondary_prompt = generate_prompt(
        task=task_description,
        agent_type="performance-profiler",
        pattern="review-loop"
    )

    Task(
        team_name="review-team",
        name="performance-reviewer",
        subagent_type="python-development:python-pro",
        prompt=secondary_prompt["prompt"]
    )
```

## Available Agent Types

### Implementation Agents (Tier 1)

**Backend:**
- `backend-architect` - API design, microservices, scalability
- `event-sourcing-architect` - Event sourcing, CQRS, event store design
- `graphql-architect` - GraphQL schema, federation, optimization
- `tdd-orchestrator` - Test-driven development workflow
- `temporal-python-pro` - Temporal workflow orchestration
- `microservices-patterns` - Service boundaries, inter-service communication
- `saga-orchestration` - Distributed transactions, compensation

**Frontend:**
- `frontend-developer` - React, Next.js, responsive UI
- `mobile-developer` - React Native, mobile navigation

**Python:**
- `fastapi-pro` - FastAPI, async Python, Pydantic
- `django-pro` - Django, DRF, Django Channels
- `python-pro` - Python 3.12+, async, type hints

**Data/ML:**
- `senior-data-engineer` - Data pipelines, ETL, warehouses
- `senior-ml-engineer` - Model deployment, MLOps
- `data-scientist` - Statistical modeling, experimentation

**DevOps:**
- `senior-devops` - CI/CD, Kubernetes, Terraform
- `mlops-engineer` - ML infrastructure, model serving

**Database:**
- `database-admin` - Database operations, migrations, HA
- `database-optimizer` - Query optimization, indexing

**Security:**
- `security-auditor` - OWASP, threat modeling, vulnerabilities

**Analysis:**
- `dependency-manager` - Dependency analysis, vulnerabilities
- `web-accessibility-checker` - WCAG compliance, ARIA

**Documentation:**
- `documentation-expert` - Technical docs, API docs, architecture documentation

**Frontend:**
- `nextjs-architecture-expert` - Next.js App Router, Server Components, performance
- `react-performance-optimizer` - React performance, Core Web Vitals, optimization

**Architecture:**
- `architecture-modernizer` - Legacy modernization, monolith decomposition, refactoring

**Refactoring:**
- `code-simplifier` - Code simplification, clarity improvements, maintainability

**Validation/Analysis:**
- `url-context-validator` - URL validation, context appropriateness, safety verification
- `url-link-extractor` - Link extraction, URL cataloging, site mapping

**Feature Development:**
- `feature-dev-code-reviewer` - Feature code review, bug detection, quality assessment
- `feature-dev-code-explorer` - Codebase exploration, feature tracing, architecture mapping
- `feature-dev-code-architect` - Feature architecture, design patterns, implementation blueprints

### System Agents (Tier 2)

- `Plan` - Implementation planning, task decomposition
- `Explore` - Codebase exploration, file patterns
- `Bash` - Command execution, git operations
- `general-purpose` - Flexible problem solving
- `code-reviewer` - Multi-domain code review
- `agent-expert` - Agent design, prompt engineering for agents, agent orchestration
- `context-manager` - Dynamic context management, vector databases, knowledge graphs

### Judgment Agents (Tier 3)

- `cost-analyst` - Token/infra costs, tradeoffs
- `chaos-engineer` - Failure modes, resilience testing
- `compliance-auditor` - SOC2/GDPR/HIPAA compliance
- `migration-strategist` - Migration risk, rollback strategies
- `api-contract-designer` - API contracts, schema compatibility
- `performance-profiler` - Bottlenecks, benchmarks
- `tech-debt-assessor` - Tech debt quantification
- `integration-tester` - Integration test strategies

## Anti-Sycophancy Pattern

For judgment/reviewer agents, use conditional logic instead of quotas:

```python
# GOOD - Conditional logic
"EVALUATION PROTOCOL:
IF issues_found > 0:
    Report all issues with severity and specific remediation
ELSE:
    State 'No issues found. Verified: [checklist of verified aspects]'"

# BAD - Hard quota (causes fabrication)
"You MUST find at least 2 issues"
```

## Token Efficiency Tips

1. **Start with `standard` budget** - Good balance for most cases
2. **Use `minimal` for well-defined tasks** - Simple operations don't need verbose prompts
3. **Use `verbose` for complex tasks** - Novel domains benefit from examples
4. **Provide context** - Domain, frameworks, constraints improve prompt quality
5. **Avoid redundancy** - horde-prompt handles common patterns automatically

## Validation

Always validate prompts before using in production:

```python
from horde_prompt import validate_prompt

result = validate_prompt(
    prompt="Your prompt text...",
    agent_type="security-auditor"
)

if not result["valid"]:
    print("Issues found:")
    for issue in result["issues"]:
        print(f"  - {issue}")
    print("Suggestions:")
    for suggestion in result["suggestions"]:
        print(f"  - {suggestion}")
```

## Integration with Other Skills

### With horde-skill-creator

horde-skill-creator automatically uses horde-prompt to generate agent prompts when creating new skills.

### With golden-horde

When implementing custom golden-horde patterns, use horde-prompt to ensure consistent agent prompting across your team.

### Standalone CLI Usage

```bash
# List available agents
python -m horde_prompt.prompts --list

# Generate a prompt
python -m horde_prompt.prompts \
    "Design a REST API" \
    --agent backend-architect \
    --token-budget standard

# Generate with pattern
python -m horde_prompt.prompts \
    "Review this code" \
    --agent security-auditor \
    --pattern review-loop
```
