"""
horde-prompt: Dynamic prompt generation for horde agent types.

Analyzes task description + target agent type + context → produces
token-efficient, task-specific prompt.

Usage:
    from horde_prompt import generate_prompt, list_agents

    result = generate_prompt(
        task="Design a REST API for user authentication",
        agent_type="backend-architect",
        context={"framework": "fastapi"},
        token_budget="standard"
    )

    print(result["prompt"])
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re


# ============================================================================
# Agent Type Registry
# ============================================================================

AGENT_REGISTRY = {
    # ========================================================================
    # Tier 1: Implementation Agents (35+)
    # ========================================================================

    # Backend Agents
    "backend-architect": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "API design (REST, GraphQL, gRPC)",
            "Microservices architecture",
            "System design and scalability",
            "Database design and optimization",
            "Event-driven architecture",
            "API gateway patterns"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs scalable backend systems with APIs, microservices, and databases."
    },
    "event-sourcing-architect": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "Event sourcing patterns",
            "CQRS implementation",
            "Event store design",
            "Projection strategies",
            "Event versioning and evolution"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs event-sourced systems with CQRS, projections, and event evolution."
    },
    "graphql-architect": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "GraphQL schema design",
            "Federation patterns",
            "Query optimization (dataloaders)",
            "Relay cursor pagination",
            "Subscription design"
        ],
        "output_format": "graphql_schema",
        "anti_sycophancy": False,
        "base_prompt": "Designs GraphQL APIs with federation, optimization, and pagination."
    },
    "tdd-orchestrator": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "Test-driven development workflow",
            "Red-green-refactor cycle",
            "Test architecture and organization",
            "Mocking and test doubles",
            "Coverage strategies"
        ],
        "output_format": "test_code",
        "anti_sycophancy": False,
        "base_prompt": "Implements features using strict TDD with red-green-refactor cycles."
    },
    "temporal-python-pro": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "Temporal workflow orchestration",
            "Activity design",
            "Saga patterns",
            "Workflow retry policies",
            "Long-running processes"
        ],
        "output_format": "python_code",
        "anti_sycophancy": False,
        "base_prompt": "Implements durable Temporal workflows with activities and retries."
    },
    "microservices-patterns": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "Service boundary design",
            "Inter-service communication",
            "Service mesh patterns",
            "Distributed tracing",
            "API composition"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs microservices with proper boundaries and communication patterns."
    },
    "saga-orchestration": {
        "tier": "implementation",
        "domain": "backend",
        "expertise": [
            "Saga pattern implementation",
            "Choreography vs orchestration",
            "Compensation transactions",
            "Saga coordination",
            "Failure recovery"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Implements saga patterns for distributed transactions."
    },

    # Frontend Agents
    "frontend-developer": {
        "tier": "implementation",
        "domain": "frontend",
        "expertise": [
            "React/Next.js components",
            "State management (Redux, Zustand)",
            "Responsive design",
            "Accessibility (WCAG)",
            "Performance optimization"
        ],
        "output_format": "jsx_code",
        "anti_sycophancy": False,
        "base_prompt": "Builds React components with state management and accessibility."
    },
    "mobile-developer": {
        "tier": "implementation",
        "domain": "frontend",
        "expertise": [
            "React Native development",
            "iOS/Android patterns",
            "Mobile navigation",
            "Offline sync",
            "Push notifications"
        ],
        "output_format": "react_native_code",
        "anti_sycophancy": False,
        "base_prompt": "Develops React Native apps with navigation and offline support."
    },

    # Python Agents
    "fastapi-pro": {
        "tier": "implementation",
        "domain": "python",
        "expertise": [
            "FastAPI framework patterns",
            "Async Python (asyncio)",
            "Pydantic models",
            "Dependency injection",
            "OpenAPI documentation"
        ],
        "output_format": "python_code",
        "anti_sycophancy": False,
        "base_prompt": "Implements FastAPI endpoints with async patterns and Pydantic."
    },
    "django-pro": {
        "tier": "implementation",
        "domain": "python",
        "expertise": [
            "Django models and ORM",
            "DRF (Django REST Framework)",
            "Django Channels (WebSockets)",
            "Middleware patterns",
            "Admin customization"
        ],
        "output_format": "python_code",
        "anti_sycophancy": False,
        "base_prompt": "Implements Django apps with DRF and real-time features."
    },
    "python-pro": {
        "tier": "implementation",
        "domain": "python",
        "expertise": [
            "Python 3.12+ features",
            "Async programming",
            "Type hints",
            "Performance optimization",
            "Testing strategies"
        ],
        "output_format": "python_code",
        "anti_sycophancy": False,
        "base_prompt": "Writes idiomatic Python with async and type hints."
    },

    # Data & ML Agents
    "senior-data-engineer": {
        "tier": "implementation",
        "domain": "data",
        "expertise": [
            "Data pipeline design (ETL/ELT)",
            "Airflow orchestration",
            "Data modeling",
            "Warehouse design (snowflake, bigquery)",
            "Data quality validation"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs data pipelines with Airflow and warehouse patterns."
    },
    "senior-ml-engineer": {
        "tier": "implementation",
        "domain": "ml",
        "expertise": [
            "Model deployment (serving)",
            "MLOps pipelines",
            "Feature stores",
            "Model monitoring",
            "A/B testing infrastructure"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Deploys ML models with monitoring and A/B testing."
    },
    "data-scientist": {
        "tier": "implementation",
        "domain": "data",
        "expertise": [
            "Statistical modeling",
            "Experimentation design",
            "A/B testing analysis",
            "Exploratory data analysis",
            "Feature engineering"
        ],
        "output_format": "python_code",
        "anti_sycophancy": False,
        "base_prompt": "Analyzes data with statistical methods and experimentation."
    },

    # DevOps Agents
    "senior-devops": {
        "tier": "implementation",
        "domain": "devops",
        "expertise": [
            "CI/CD pipelines",
            "Infrastructure as Code (Terraform)",
            "Container orchestration (Kubernetes)",
            "Monitoring and observability",
            "Cloud architecture (AWS/GCP/Azure)"
        ],
        "output_format": "config_code",
        "anti_sycophancy": False,
        "base_prompt": "Designs CI/CD and infrastructure with Kubernetes and Terraform."
    },
    "mlops-engineer": {
        "tier": "implementation",
        "domain": "devops",
        "expertise": [
            "ML infrastructure",
            "Model serving infrastructure",
            "Experiment tracking",
            "Feature pipelines",
            "Model monitoring"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Builds ML infrastructure for model serving and tracking."
    },

    # Database Agents
    "database-admin": {
        "tier": "implementation",
        "domain": "database",
        "expertise": [
            "Database operations",
            "Migration strategies",
            "Backup and recovery",
            "High availability",
            "Database security"
        ],
        "output_format": "sql_code",
        "anti_sycophancy": False,
        "base_prompt": "Manages database operations with migrations and HA."
    },
    "database-optimizer": {
        "tier": "implementation",
        "domain": "database",
        "expertise": [
            "Query optimization",
            "Indexing strategies",
            "Performance tuning",
            "Execution plan analysis",
            "Schema normalization"
        ],
        "output_format": "sql_code",
        "anti_sycophancy": False,
        "base_prompt": "Optimizes database queries with indexing and tuning."
    },

    # Security & Analysis Agents
    "security-auditor": {
        "tier": "implementation",
        "domain": "security",
        "expertise": [
            "OWASP Top 10 compliance",
            "Threat modeling",
            "Vulnerability assessment",
            "Security architecture review",
            "Penetration testing patterns"
        ],
        "output_format": "security_report",
        "anti_sycophancy": True,
        "base_prompt": "Audits code for security vulnerabilities and compliance."
    },
    "dependency-manager": {
        "tier": "implementation",
        "domain": "analysis",
        "expertise": [
            "Dependency analysis",
            "Vulnerability scanning",
            "License compliance",
            "Version conflict resolution",
            "Supply chain security"
        ],
        "output_format": "analysis_report",
        "anti_sycophancy": True,
        "base_prompt": "Analyzes dependencies for vulnerabilities and licenses."
    },
    "web-accessibility-checker": {
        "tier": "implementation",
        "domain": "frontend",
        "expertise": [
            "WCAG 2.1 compliance",
            "ARIA implementation",
            "Screen reader compatibility",
            "Keyboard navigation",
            "Color contrast"
        ],
        "output_format": "accessibility_report",
        "anti_sycophancy": True,
        "base_prompt": "Audits UI for WCAG compliance and accessibility."
    },

    # Documentation Agents
    "documentation-expert": {
        "tier": "implementation",
        "domain": "documentation",
        "expertise": [
            "Technical writing",
            "API documentation",
            "Architecture documentation",
            "README and guides",
            "Inline code documentation"
        ],
        "output_format": "markdown_docs",
        "anti_sycophancy": False,
        "base_prompt": "Creates comprehensive technical documentation from codebases."
    },

    # Frontend Framework Agents
    "nextjs-architecture-expert": {
        "tier": "implementation",
        "domain": "frontend",
        "expertise": [
            "Next.js App Router",
            "Server Components",
            "Performance optimization",
            "Streaming and SSR",
            "Route handlers"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Architects Next.js applications with App Router and Server Components."
    },
    "react-performance-optimizer": {
        "tier": "implementation",
        "domain": "frontend",
        "expertise": [
            "React performance patterns",
            "Bundle optimization",
            "Core Web Vitals",
            "Memoization strategies",
            "Rendering optimization"
        ],
        "output_format": "optimization_report",
        "anti_sycophancy": False,
        "base_prompt": "Optimizes React applications for performance and Core Web Vitals."
    },

    # Architecture Agents
    "architecture-modernizer": {
        "tier": "implementation",
        "domain": "architecture",
        "expertise": [
            "Monolith decomposition",
            "Microservices migration",
            "Refactoring strategies",
            "Legacy system analysis",
            "Modernization roadmaps"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Modernizes legacy architectures through strategic refactoring."
    },

    # Code Quality Agents
    "code-simplifier": {
        "tier": "implementation",
        "domain": "refactoring",
        "expertise": [
            "Code simplification",
            "Clarity improvements",
            "Maintainability enhancements",
            "Complexity reduction",
            "Readability optimization"
        ],
        "output_format": "code_diff",
        "anti_sycophancy": False,
        "base_prompt": "Simplifies complex code while preserving all functionality."
    },

    # Validation Agents
    "url-context-validator": {
        "tier": "implementation",
        "domain": "validation",
        "expertise": [
            "URL validation",
            "Context analysis",
            "Link appropriateness checking",
            "Content relevance",
            "Safety verification"
        ],
        "output_format": "validation_report",
        "anti_sycophancy": True,
        "base_prompt": "Validates URLs and checks contextual appropriateness."
    },
    "url-link-extractor": {
        "tier": "implementation",
        "domain": "analysis",
        "expertise": [
            "Link extraction",
            "URL cataloging",
            "Site mapping",
            "Internal link analysis",
            "External link discovery"
        ],
        "output_format": "link_catalog",
        "anti_sycophancy": False,
        "base_prompt": "Extracts and catalogs all URLs from website codebases."
    },

    # Feature Development Sub-agents
    "feature-dev-code-reviewer": {
        "tier": "implementation",
        "domain": "review",
        "expertise": [
            "Feature code review",
            "Bug detection",
            "Quality assessment",
            "Implementation verification",
            "Edge case analysis"
        ],
        "output_format": "review_report",
        "anti_sycophancy": True,
        "base_prompt": "Reviews feature implementations for bugs and quality issues."
    },
    "feature-dev-code-explorer": {
        "tier": "implementation",
        "domain": "analysis",
        "expertise": [
            "Codebase exploration",
            "Feature tracing",
            "Architecture mapping",
            "Dependency analysis",
            "Implementation discovery"
        ],
        "output_format": "analysis_report",
        "anti_sycophancy": False,
        "base_prompt": "Explores codebases to understand feature implementation."
    },
    "feature-dev-code-architect": {
        "tier": "implementation",
        "domain": "architecture",
        "expertise": [
            "Feature architecture",
            "Design patterns",
            "Implementation blueprints",
            "Interface specification",
            "Component design"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs comprehensive implementation blueprints for features."
    },

    # ========================================================================
    # Tier 2: System Agents (10+)
    # ========================================================================

    "Plan": {
        "tier": "system",
        "domain": "planning",
        "expertise": [
            "Implementation planning",
            "Task decomposition",
            "Dependency mapping",
            "Architecture design",
            "Multi-step coordination"
        ],
        "output_format": "structured_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Designs implementation plans with task breakdown and dependencies."
    },
    "Explore": {
        "tier": "system",
        "domain": "exploration",
        "expertise": [
            "Codebase exploration",
            "File pattern matching",
            "Architecture discovery",
            "Dependency tracing",
            "Quick reconnaissance"
        ],
        "output_format": "exploration_report",
        "anti_sycophancy": False,
        "base_prompt": "Explores codebases for patterns and architecture."
    },
    "Bash": {
        "tier": "system",
        "domain": "execution",
        "expertise": [
            "Command execution",
            "Git operations",
            "Build systems",
            "Terminal workflows",
            "Script automation"
        ],
        "output_format": "bash_code",
        "anti_sycophancy": False,
        "base_prompt": "Executes terminal commands and git operations."
    },
    "general-purpose": {
        "tier": "system",
        "domain": "general",
        "expertise": [
            "Flexible problem solving",
            "Cross-domain reasoning",
            "Task adaptation",
            "Creative solutions",
            "Context switching"
        ],
        "output_format": "flexible",
        "anti_sycophancy": False,
        "base_prompt": "Handles diverse tasks with flexible problem solving."
    },
    "code-reviewer": {
        "tier": "system",
        "domain": "review",
        "expertise": [
            "Multi-domain code review",
            "Security analysis",
            "Performance assessment",
            "Architecture evaluation",
            "Best practices enforcement"
        ],
        "output_format": "review_report",
        "anti_sycophancy": True,
        "base_prompt": "Reviews code across security, performance, and architecture."
    },
    "agent-expert": {
        "tier": "system",
        "domain": "agent-development",
        "expertise": [
            "Agent design",
            "Prompt engineering for agents",
            "Agent orchestration",
            "Agent capability specification",
            "Multi-agent workflow design"
        ],
        "output_format": "agent_specification",
        "anti_sycophancy": False,
        "base_prompt": "Designs and specifies agent types with clear capabilities and prompts."
    },
    "context-manager": {
        "tier": "system",
        "domain": "agent-orchestration",
        "expertise": [
            "Context window management",
            "Vector databases",
            "Knowledge graphs",
            "Dynamic context routing",
            "Memory optimization"
        ],
        "output_format": "architecture_markdown",
        "anti_sycophancy": False,
        "base_prompt": "Manages dynamic context across multi-agent workflows."
    },

    # ========================================================================
    # Tier 3: Judgment Agents (15+)
    # ========================================================================

    "cost-analyst": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Token/compute cost estimation",
            "Infrastructure costs (cloud, DB, CDN)",
            "Development time vs maintenance tradeoffs",
            "Cost-per-request modeling",
            "Budget optimization"
        ],
        "output_format": "cost_breakdown",
        "anti_sycophancy": True,
        "base_prompt": "Evaluates proposals through cost lens with tradeoff analysis."
    },
    "chaos-engineer": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Failure mode identification",
            "Resilience testing strategies",
            "Stress test design",
            "Cascading failure analysis",
            "Recovery planning"
        ],
        "output_format": "risk_assessment",
        "anti_sycophancy": True,
        "base_prompt": "Identifies failure modes and designs resilience tests."
    },
    "compliance-auditor": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "SOC2 compliance verification",
            "GDPR requirements assessment",
            "HIPAA validation",
            "Regulatory gap analysis",
            "Compliance documentation"
        ],
        "output_format": "compliance_report",
        "anti_sycophancy": True,
        "base_prompt": "Verifies regulatory compliance (SOC2/GDPR/HIPAA)."
    },
    "migration-strategist": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Migration risk assessment",
            "Rollback strategy design",
            "Zero-downtime approaches",
            "Data migration planning",
            "Cutover strategies"
        ],
        "output_format": "migration_plan",
        "anti_sycophancy": True,
        "base_prompt": "Assesses migration risk and plans rollback strategies."
    },
    "api-contract-designer": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "API contract design",
            "Schema compatibility validation",
            "Versioning strategy",
            "Interface specifications",
            "Contract testing requirements"
        ],
        "output_format": "api_contract",
        "anti_sycophancy": True,
        "base_prompt": "Designs API contracts and validates schema compatibility."
    },
    "performance-profiler": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Bottleneck identification",
            "Benchmark design",
            "Performance budgets",
            "Optimization prioritization",
            "Profiling strategy"
        ],
        "output_format": "performance_report",
        "anti_sycophancy": True,
        "base_prompt": "Profiles bottlenecks and sets performance budgets."
    },
    "tech-debt-assessor": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Tech debt quantification",
            "Prioritization frameworks",
            "Debt-to-feature ratio analysis",
            "Remediation planning",
            "Debt tracking"
        ],
        "output_format": "debt_report",
        "anti_sycophancy": True,
        "base_prompt": "Quantifies technical debt and prioritizes remediation."
    },
    "integration-tester": {
        "tier": "judgment",
        "domain": "judgment",
        "expertise": [
            "Integration test strategy",
            "Contract validation",
            "Cross-service testing",
            "End-to-end scenarios",
            "Test environment design"
        ],
        "output_format": "test_plan",
        "anti_sycophancy": True,
        "base_prompt": "Designs integration test strategies for cross-service validation."
    },
}


# ============================================================================
# Pattern Protocols
# ============================================================================

PATTERN_PROTOCOLS = {
    "review-loop": """
REVIEW LOOP PROTOCOL:
- You are in a review loop with a producer agent
- Review artifacts thoroughly and identify specific issues
- Provide feedback with actionable, specific guidance
- Continue iterations until satisfactory or max rounds reached
- Send feedback via SendMessage with clear issue tags
""",
    "adversarial-debate": """
ADVERSARIAL DEBATE PROTOCOL:
- You are advocating for a specific position in a structured debate
- Make the strongest possible case for your assigned position
- Address opponent's rebuttals directly
- Challenge assumptions and provide evidence
- A judge will rule on contested points
""",
    "assembly-line": """
ASSEMBLY LINE PROTOCOL:
- You are a stage in a multi-stage pipeline
- Your output feeds into the next stage
- Send completed work forward via SendMessage
- If input is inadequate, send back with specific requirements
- Maintain backward communication for clarification
""",
    "consensus-deliberation": """
CONSENSUS DELIBERATION PROTOCOL:
- Provide independent analysis first
- Then challenge other experts' findings
- Work toward genuine consensus (not averaging)
- Converge on recommendations with reasoning
- Document disagreements and their rationale
""",
    "watchdog": """
WATCHDOG PROTOCOL:
- Monitor implementers at checkpoints
- Identify constraint violations in real-time
- Send corrections immediately via SendMessage
- Severity levels: CRITICAL (must fix) | HIGH (should fix) | MEDIUM | LOW
- Track violations and patterns
""",
}


# ============================================================================
# Complexity Scorer
# ============================================================================

def score_task_complexity(task: str) -> int:
    """
    Score task complexity (0-100).

    Factors:
    - Task length (words)
    - Technical keywords
    - Constraint indicators
    - Domain complexity
    """
    if not task:
        return 0

    score = 0

    # Length factor (0-20 points)
    word_count = len(task.split())
    score += min(word_count // 2, 20)

    # Technical complexity keywords (0-40 points)
    technical_keywords = [
        "architecture", "scalability", "distributed", "microservices",
        "security", "compliance", "performance", "optimization",
        "migration", "integration", "api", "database", "infrastructure",
        "deployment", "testing", "monitoring", "authentication"
    ]
    for keyword in technical_keywords:
        if keyword.lower() in task.lower():
            score += 2

    # Constraint indicators (0-20 points)
    constraint_indicators = [
        "constraint", "requirement", "must", "should", "limit",
        "budget", "deadline", "compliance", "standard"
    ]
    for indicator in constraint_indicators:
        if indicator.lower() in task.lower():
            score += 3

    # Domain complexity (0-20 points)
    domain_keywords = [
        "hipaa", "gdpr", "soc2", "payment", "fintech", "healthcare",
        "blockchain", "ml", "ai", "real-time", "high-availability"
    ]
    for keyword in domain_keywords:
        if keyword.lower() in task.lower():
            score += 4

    return min(score, 100)


# ============================================================================
# Prompt Generator
# ============================================================================

@dataclass
class PromptResult:
    """Result from generate_prompt."""
    prompt: str
    estimated_tokens: int
    compression_ratio: float
    agent_tier: str
    confidence: float
    optimizations_applied: List[str]


def generate_prompt(
    task: str,
    agent_type: str,
    context: Optional[Dict[str, Any]] = None,
    token_budget: str = "standard",
    pattern: Optional[str] = None
) -> PromptResult:
    """
    Generate an optimized prompt for the given task and agent type.

    Args:
        task: Task description
        agent_type: Agent type from registry
        context: Additional context (framework, constraints, etc.)
        token_budget: "minimal" | "standard" | "verbose"
        pattern: Golden-horde pattern for protocol injection

    Returns:
        PromptResult with generated prompt and metadata
    """
    # Normalize agent_type
    agent_type = agent_type.lower().replace("_", "-")

    # Look up agent in registry
    agent_info = AGENT_REGISTRY.get(agent_type)
    if not agent_info:
        # Try with underscores
        agent_type = agent_type.replace("-", "_")
        agent_info = AGENT_REGISTRY.get(agent_type)

    if not agent_info:
        raise ValueError(f"Unknown agent type: {agent_type}. Use list_agents() to see available types.")

    # Score task complexity
    complexity = score_task_complexity(task)

    # Build prompt based on token_budget
    prompt_parts = []
    optimizations = []

    if token_budget == "minimal":
        # Compact syntax
        prompt_parts.append(f"ROLE: {agent_type}")

        if agent_info["domain"] != "general":
            domains = {
                "backend": "api|microservices|scalability",
                "frontend": "react|components|ux",
                "python": "fastapi|django|async",
                "data": "pipelines|etl|warehouse",
                "ml": "models|deployment|mlops",
                "devops": "cicd|kubernetes|terraform",
                "security": "owasp|vulnerabilities|compliance",
                "database": "sql|indexing|optimization",
                "judgment": "evaluate|assess|recommend"
            }
            prompt_parts.append(f"DOMAIN: {domains.get(agent_info['domain'], agent_info['domain'])}")

        prompt_parts.append(f"TASK: {task}")

        # Output format hint
        output_formats = {
            "architecture_markdown": "architecture|specs",
            "python_code": "code",
            "sql_code": "sql",
            "security_report": "findings|severity",
            "cost_breakdown": "cost|drivers|alternatives"
        }
        prompt_parts.append(f"OUTPUT: {output_formats.get(agent_info['output_format'], 'structured_output')}")

        optimizations.append("compact_syntax")
        optimizations.append("removed_explanations")

    elif token_budget == "verbose":
        # Full prose with examples
        prompt_parts.append(f"You are a {agent_type} in a multi-agent system.")
        prompt_parts.append(f"\n{agent_info['base_prompt']}\n")

        prompt_parts.append("EXPERTISE:")
        for item in agent_info["expertise"]:
            prompt_parts.append(f"- {item}")

        prompt_parts.append(f"\nTASK: {task}")

        # Add context if provided
        if context:
            prompt_parts.append("\nCONTEXT:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")

        prompt_parts.append("\nOUTPUT FORMAT:")
        prompt_parts.append("Provide a detailed response with:")
        prompt_parts.append("- Clear structure with headings")
        prompt_parts.append("- Specific recommendations")
        prompt_parts.append("- Rationale for decisions")
        prompt_parts.append("- Actionable next steps")

        optimizations.append("full_prose")
        optimizations.append("included_examples")

    else:  # standard
        # Balanced approach
        prompt_parts.append(f"You are a {agent_type}.")

        prompt_parts.append(f"\nEXPERTISE:")
        expertise_list = agent_info["expertise"][:3]  # Top 3
        prompt_parts.append(", ".join(expertise_list))

        prompt_parts.append(f"\n\nTASK: {task}")

        # Add context if provided
        if context:
            prompt_parts.append(f"\n\nCONTEXT: {context}")

        # Output section
        prompt_parts.append("\n\nOUTPUT:")
        output_guide = {
            "architecture_markdown": "Architecture with specs and endpoints",
            "python_code": "Implementation with tests",
            "security_report": "Findings with severity and remediation",
            "cost_breakdown": "Cost range, drivers, and alternatives"
        }
        prompt_parts.append(output_guide.get(agent_info['output_format'], "Structured response"))

        optimizations.append("balanced_syntax")
        optimizations.append("key_expertise_only")

    # Add anti-sycophancy for judgment/reviewer agents
    if agent_info.get("anti_sycophancy") and token_budget != "minimal":
        prompt_parts.append("\n\nEVALUATION PROTOCOL:")
        prompt_parts.append("IF issues_found > 0:")
        prompt_parts.append("  Report all issues with severity and specific remediation")
        prompt_parts.append("ELSE:")
        prompt_parts.append("  State 'No issues found. Verified: [checklist of verified aspects]'")
        optimizations.append("anti_sycophancy_conditional")

    # Add pattern protocol if specified
    if pattern and pattern in PATTERN_PROTOCOLS:
        prompt_parts.append(f"\n\n{PATTERN_PROTOCOLS[pattern]}")
        optimizations.append(f"pattern_{pattern}")

    # Join and estimate tokens
    prompt = "\n".join(prompt_parts)
    estimated_tokens = len(prompt) // 4  # Rough estimate: 4 chars per token

    # Calculate compression ratio (vs verbose baseline)
    verbose_estimate = len(prompt) // 2  # Verbose would be ~2x
    compression_ratio = 1.0 - (estimated_tokens / verbose_estimate)

    # Confidence based on agent info completeness
    confidence = 0.95 if agent_info else 0.7
    if complexity > 50 and token_budget == "minimal":
        confidence -= 0.1  # Reduce confidence for complex tasks with minimal prompts

    return PromptResult(
        prompt=prompt,
        estimated_tokens=estimated_tokens,
        compression_ratio=round(compression_ratio, 2),
        agent_tier=agent_info.get("tier", "unknown"),
        confidence=round(confidence, 2),
        optimizations_applied=optimizations
    )


def list_agents(tier: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List available agent types, optionally filtered by tier or domain.

    Args:
        tier: Filter by tier ("implementation", "system", "judgment")
        domain: Filter by domain ("backend", "frontend", "python", etc.)

    Returns:
        List of agent type dictionaries
    """
    agents = []

    for agent_type, info in AGENT_REGISTRY.items():
        # Apply filters
        if tier and info.get("tier") != tier:
            continue
        if domain and info.get("domain") != domain:
            continue

        agents.append({
            "type": agent_type,
            "tier": info.get("tier"),
            "domain": info.get("domain"),
            "expertise_count": len(info.get("expertise", [])),
            "output_format": info.get("output_format"),
        })

    return sorted(agents, key=lambda x: (x["tier"], x["type"]))


def validate_prompt(prompt: str, agent_type: str) -> Dict[str, Any]:
    """
    Validate a prompt against agent type requirements.

    Returns validation result with issues and suggestions.
    """
    agent_info = AGENT_REGISTRY.get(agent_type)
    if not agent_info:
        return {"valid": False, "error": f"Unknown agent type: {agent_type}"}

    issues = []
    suggestions = []

    # Check for required elements based on tier
    if agent_info.get("tier") == "judgment":
        if "IF issues_found" not in prompt and "MUST find" not in prompt:
            issues.append("Missing anti-sycophancy instruction")
            suggestions.append("Add conditional logic: 'IF issues_found > 0: ... ELSE: ...'")

    if agent_info.get("tier") == "implementation":
        if "TASK:" not in prompt and "task" not in prompt.lower():
            issues.append("Missing clear task specification")
            suggestions.append("Add explicit TASK section")

    # Check token estimate
    estimated_tokens = len(prompt) // 4
    if estimated_tokens > 300:
        issues.append(f"Prompt is long (~{estimated_tokens} tokens)")
        suggestions.append("Consider compacting with minimal token_budget")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
        "estimated_tokens": estimated_tokens
    }


# ============================================================================
# CLI Interface (for skill invocation)
# ============================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate optimized prompts for horde agents")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--agent", required=True, help="Agent type")
    parser.add_argument("--context", help="Context as JSON string")
    parser.add_argument("--token-budget", choices=["minimal", "standard", "verbose"],
                        default="standard", help="Token budget level")
    parser.add_argument("--pattern", help="Golden-horde pattern for protocol")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format")

    args = parser.parse_args()

    if args.list:
        agents = list_agents()
        if args.format == "json":
            print(json.dumps(agents, indent=2))
        else:
            print("Available agent types:")
            print("-" * 60)
            for agent in agents:
                print(f"  {agent['type']:30s} [{agent['tier']:13s}] {agent['domain']}")
        exit(0)

    # Parse context
    context = json.loads(args.context) if args.context else None

    # Generate prompt
    result = generate_prompt(
        task=args.task,
        agent_type=args.agent,
        context=context,
        token_budget=args.token_budget,
        pattern=args.pattern
    )

    if args.format == "json":
        output = {
            "prompt": result.prompt,
            "estimated_tokens": result.estimated_tokens,
            "compression_ratio": result.compression_ratio,
            "agent_tier": result.agent_tier,
            "confidence": result.confidence,
            "optimizations": result.optimizations_applied
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("GENERATED PROMPT")
        print("=" * 60)
        print(result.prompt)
        print()
        print("-" * 60)
        print(f"Tokens: {result.estimated_tokens} | "
              f"Compression: {result.compression_ratio:.0%} | "
              f"Confidence: {result.confidence}")
        print(f"Optimizations: {', '.join(result.optimizations_applied)}")
