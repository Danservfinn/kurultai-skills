"""
Context analysis utilities for horde-prompt.

Extracts relevant context from task descriptions and analyzes
complexity to determine optimal prompt structure.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ContextAnalysis:
    """Result from context analysis."""
    domains: List[str]
    frameworks: List[str]
    constraints: List[str]
    complexity_score: int
    suggested_token_budget: str


# Domain keywords
DOMAIN_KEYWORDS = {
    "backend": ["api", "rest", "graphql", "microservices", "database", "sql", "server"],
    "frontend": ["react", "vue", "angular", "ui", "component", "css", "frontend"],
    "python": ["python", "fastapi", "django", "flask", "async", "pydantic"],
    "security": ["security", "auth", "owasp", "vulnerability", "encryption", "compliance"],
    "devops": ["deployment", "kubernetes", "docker", "ci/cd", "terraform", "aws", "gcp"],
    "data": ["pipeline", "etl", "data warehouse", "snowflake", "bigquery", "airflow"],
    "ml": ["model", "training", "inference", "mlflow", "feature", "prediction"],
}


# Framework keywords
FRAMEWORK_KEYWORDS = {
    "fastapi": ["fastapi", "pydantic"],
    "django": ["django", "drf", "django-rest-framework"],
    "react": ["react", "next.js", "jsx", "tsx"],
    "vue": ["vue", "vuex"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mongodb": ["mongodb", "mongo"],
    "aws": ["aws", "lambda", "s3", "rds"],
    "gcp": ["gcp", "cloud run", "bigquery"],
}


# Constraint indicators
CONSTRAINT_PATTERNS = [
    r"must\s+(?:not\s+)?(?:use|include|support)",
    r"(?:constraint|requirement|limit):?\s+\S+",
    r"budget:\s*\S+",
    r"deadline:\s*\S+",
    r"within\s+\d+\s+(?:hours|days|weeks)",
    r"compliance:\s*\S+",
]


def extract_context(task: str) -> Dict[str, Any]:
    """
    Extract contextual information from task description.

    Args:
        task: Task description

    Returns:
        Dictionary with extracted context
    """
    context = {
        "domains": [],
        "frameworks": [],
        "constraints": [],
    }

    task_lower = task.lower()

    # Extract domains
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in task_lower for kw in keywords):
            context["domains"].append(domain)

    # Extract frameworks
    for framework, keywords in FRAMEWORK_KEYWORDS.items():
        if any(kw in task_lower for kw in keywords):
            context["frameworks"].append(framework)

    # Extract constraints
    for pattern in CONSTRAINT_PATTERNS:
        matches = re.findall(pattern, task, re.IGNORECASE)
        context["constraints"].extend(matches)

    return context


def analyze_complexity(task: str, context: Optional[Dict[str, Any]] = None) -> ContextAnalysis:
    """
    Analyze task complexity and suggest optimal prompt budget.

    Args:
        task: Task description
        context: Optional pre-extracted context

    Returns:
        ContextAnalysis with recommendations
    """
    if context is None:
        context = extract_context(task)

    # Base complexity from task length
    word_count = len(task.split())
    complexity = min(word_count // 2, 30)

    # Add complexity for multiple domains
    complexity += len(context["domains"]) * 5

    # Add complexity for constraints
    complexity += len(context["constraints"]) * 3

    # Add complexity for technical keywords
    technical_indicators = [
        "architecture", "scalability", "distributed", "microservices",
        "optimization", "migration", "integration", "security"
    ]
    for indicator in technical_indicators:
        if indicator in task.lower():
            complexity += 5

    # Cap at 100
    complexity = min(complexity, 100)

    # Suggest token budget based on complexity
    if complexity < 20:
        suggested_budget = "minimal"
    elif complexity < 50:
        suggested_budget = "standard"
    else:
        suggested_budget = "verbose"

    return ContextAnalysis(
        domains=context["domains"],
        frameworks=context["frameworks"],
        constraints=context["constraints"],
        complexity_score=complexity,
        suggested_token_budget=suggested_budget
    )


def suggest_agent_type(task: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Suggest appropriate agent types based on task context.

    Args:
        task: Task description
        context: Optional pre-extracted context

    Returns:
        List of suggested agent types, ranked by relevance
    """
    if context is None:
        context = extract_context(task)

    suggestions = []

    # Map domains to agent types
    domain_agents = {
        "backend": ["backend-architect", "event-sourcing-architect", "graphql-architect"],
        "frontend": ["frontend-developer", "mobile-developer"],
        "python": ["fastapi-pro", "django-pro", "python-pro"],
        "security": ["security-auditor"],
        "devops": ["senior-devops", "mlops-engineer"],
        "data": ["senior-data-engineer", "data-scientist"],
        "ml": ["senior-ml-engineer", "data-scientist"],
    }

    # Add suggestions for detected domains
    for domain in context["domains"]:
        if domain in domain_agents:
            suggestions.extend(domain_agents[domain])

    # Remove duplicates and return
    return list(dict.fromkeys(suggestions))
