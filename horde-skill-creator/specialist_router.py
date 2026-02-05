"""
Specialist Router for Supercharged Skill Creator

Maps skill creation task types to appropriate OpenClaw agents based on the
architecture defined in ARCHITECTURE.md.

Agents:
- Kublai (main) - Coordinator, synthesis
- Möngke (researcher) - Research, requirements, specifications
- Chagatai (writer) - Documentation, content writing
- Temüjin (developer) - Implementation, testing
- Jochi (analyst) - Validation, quality assessment, packaging
- Ögedei (ops) - Deployment, operations
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from functools import lru_cache

import httpx

# Configure logging
logger = logging.getLogger(__name__)


class AgentID(Enum):
    """OpenClaw agent identifiers."""
    MAIN = "main"              # Kublai - Coordinator
    RESEARCHER = "researcher"  # Möngke - Research Specialist
    WRITER = "writer"          # Chagatai - Content Writer
    DEVELOPER = "developer"    # Temüjin - Software Developer
    ANALYST = "analyst"        # Jochi - Data Analyst
    OPS = "ops"                # Ögedei - DevOps Engineer


class TaskType(Enum):
    """Task types for skill creation workflow."""
    # Phase 1 - Requirements
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    DEPENDENCY_RESEARCH = "dependency_research"
    SIMILAR_SKILLS_SEARCH = "similar_skills_search"

    # Phase 2 - Specification
    SPECIFICATION_DESIGN = "specification_design"
    INTERFACE_DEFINITION = "interface_definition"
    PARAMETER_SCHEMA = "parameter_schema"

    # Phase 3 - Planning
    IMPLEMENTATION_PLANNING = "implementation_planning"
    ARCHITECTURE_DESIGN = "architecture_design"
    FILE_STRUCTURE = "file_structure"

    # Phase 4 - Implementation
    CORE_IMPLEMENTATION = "core_implementation"
    VALIDATION_LOGIC = "validation_logic"
    ERROR_HANDLING = "error_handling"

    # Phase 5 - Testing
    TEST_DESIGN = "test_design"
    TEST_IMPLEMENTATION = "test_implementation"
    QUALITY_VALIDATION = "quality_validation"
    SECURITY_ASSESSMENT = "security_assessment"

    # Phase 6 - Documentation
    USER_DOCUMENTATION = "user_documentation"
    API_DOCUMENTATION = "api_documentation"
    EXAMPLE_CREATION = "example_creation"
    README_GENERATION = "readme_generation"

    # Phase 7 - Packaging
    PACKAGE_CREATION = "package_creation"
    QUALITY_REVIEW = "quality_review"
    MANIFEST_GENERATION = "manifest_generation"
    CATALOG_REGISTRATION = "catalog_registration"


class SkillDomain(Enum):
    """Skill domains for specialized routing."""
    # Backend domains
    API_DESIGN = "api_design"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    EVENT_DRIVEN = "event_driven"
    MICROSERVICES = "microservices"

    # Frontend domains
    UI_COMPONENTS = "ui_components"
    VISUALIZATION = "visualization"
    INTERACTION = "interaction"

    # Data domains
    DATA_ANALYSIS = "data_analysis"
    DATA_PROCESSING = "data_processing"
    DATA_VALIDATION = "data_validation"

    # General
    GENERAL = "general"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


# Routing table: task_type -> [primary_agent, fallback_agent]
ROUTING_TABLE: dict[TaskType, list[AgentID]] = {
    # Phase 1 - Requirements (Möngke primary)
    TaskType.REQUIREMENTS_ANALYSIS: [AgentID.RESEARCHER, AgentID.MAIN],
    TaskType.DEPENDENCY_RESEARCH: [AgentID.RESEARCHER, AgentID.DEVELOPER],
    TaskType.SIMILAR_SKILLS_SEARCH: [AgentID.RESEARCHER, AgentID.ANALYST],

    # Phase 2 - Specification (Möngke + Chagatai)
    TaskType.SPECIFICATION_DESIGN: [AgentID.RESEARCHER, AgentID.WRITER],
    TaskType.INTERFACE_DEFINITION: [AgentID.RESEARCHER, AgentID.DEVELOPER],
    TaskType.PARAMETER_SCHEMA: [AgentID.RESEARCHER, AgentID.ANALYST],

    # Phase 3 - Planning (Temüjin primary)
    TaskType.IMPLEMENTATION_PLANNING: [AgentID.DEVELOPER, AgentID.RESEARCHER],
    TaskType.ARCHITECTURE_DESIGN: [AgentID.DEVELOPER, AgentID.RESEARCHER],
    TaskType.FILE_STRUCTURE: [AgentID.DEVELOPER, AgentID.MAIN],

    # Phase 4 - Implementation (Temüjin primary)
    TaskType.CORE_IMPLEMENTATION: [AgentID.DEVELOPER, AgentID.MAIN],
    TaskType.VALIDATION_LOGIC: [AgentID.DEVELOPER, AgentID.ANALYST],
    TaskType.ERROR_HANDLING: [AgentID.DEVELOPER, AgentID.ANALYST],

    # Phase 5 - Testing (Jochi + Temüjin)
    TaskType.TEST_DESIGN: [AgentID.ANALYST, AgentID.DEVELOPER],
    TaskType.TEST_IMPLEMENTATION: [AgentID.DEVELOPER, AgentID.ANALYST],
    TaskType.QUALITY_VALIDATION: [AgentID.ANALYST, AgentID.MAIN],
    TaskType.SECURITY_ASSESSMENT: [AgentID.ANALYST, AgentID.DEVELOPER],

    # Phase 6 - Documentation (Chagatai primary)
    TaskType.USER_DOCUMENTATION: [AgentID.WRITER, AgentID.MAIN],
    TaskType.API_DOCUMENTATION: [AgentID.WRITER, AgentID.RESEARCHER],
    TaskType.EXAMPLE_CREATION: [AgentID.WRITER, AgentID.DEVELOPER],
    TaskType.README_GENERATION: [AgentID.WRITER, AgentID.MAIN],

    # Phase 7 - Packaging (Jochi primary)
    TaskType.PACKAGE_CREATION: [AgentID.ANALYST, AgentID.OPS],
    TaskType.QUALITY_REVIEW: [AgentID.ANALYST, AgentID.MAIN],
    TaskType.MANIFEST_GENERATION: [AgentID.OPS, AgentID.ANALYST],
    TaskType.CATALOG_REGISTRATION: [AgentID.ANALYST, AgentID.OPS],
}


# Domain-based agent preferences
DOMAIN_ROUTING: dict[SkillDomain, list[AgentID]] = {
    # Backend domains
    SkillDomain.API_DESIGN: [AgentID.RESEARCHER, AgentID.DEVELOPER],
    SkillDomain.DATABASE: [AgentID.DEVELOPER, AgentID.ANALYST],
    SkillDomain.AUTHENTICATION: [AgentID.DEVELOPER, AgentID.ANALYST],
    SkillDomain.EVENT_DRIVEN: [AgentID.DEVELOPER, AgentID.RESEARCHER],
    SkillDomain.MICROSERVICES: [AgentID.DEVELOPER, AgentID.RESEARCHER],

    # Frontend domains
    SkillDomain.UI_COMPONENTS: [AgentID.DEVELOPER, AgentID.WRITER],
    SkillDomain.VISUALIZATION: [AgentID.DEVELOPER, AgentID.ANALYST],
    SkillDomain.INTERACTION: [AgentID.DEVELOPER, AgentID.WRITER],

    # Data domains
    SkillDomain.DATA_ANALYSIS: [AgentID.ANALYST, AgentID.RESEARCHER],
    SkillDomain.DATA_PROCESSING: [AgentID.DEVELOPER, AgentID.ANALYST],
    SkillDomain.DATA_VALIDATION: [AgentID.ANALYST, AgentID.DEVELOPER],

    # General
    SkillDomain.GENERAL: [AgentID.MAIN, AgentID.RESEARCHER],
    SkillDomain.AUTOMATION: [AgentID.DEVELOPER, AgentID.OPS],
    SkillDomain.INTEGRATION: [AgentID.DEVELOPER, AgentID.RESEARCHER],
}


@dataclass
class AgentInfo:
    """Information about an agent."""
    agent_id: AgentID
    name: str
    role: str
    capabilities: list[str]


@dataclass
class RoutingResult:
    """Result of routing a task to an agent."""
    agent_id: AgentID
    agent_name: str
    is_fallback: bool
    reason: str
    available: bool


# Agent metadata
AGENT_INFO: dict[AgentID, AgentInfo] = {
    AgentID.MAIN: AgentInfo(
        agent_id=AgentID.MAIN,
        name="Kublai",
        role="Coordinator",
        capabilities=[
            "orchestration", "synthesis", "decision_making",
            "research_fallback", "documentation_fallback"
        ]
    ),
    AgentID.RESEARCHER: AgentInfo(
        agent_id=AgentID.RESEARCHER,
        name="Möngke",
        role="Research Specialist",
        capabilities=[
            "requirements_analysis", "dependency_research",
            "specification_design", "domain_knowledge"
        ]
    ),
    AgentID.WRITER: AgentInfo(
        agent_id=AgentID.WRITER,
        name="Chagatai",
        role="Content Writer",
        capabilities=[
            "documentation", "technical_writing",
            "readme_generation", "example_creation"
        ]
    ),
    AgentID.DEVELOPER: AgentInfo(
        agent_id=AgentID.DEVELOPER,
        name="Temüjin",
        role="Software Developer",
        capabilities=[
            "implementation", "testing", "architecture_design",
            "error_handling", "validation_logic"
        ]
    ),
    AgentID.ANALYST: AgentInfo(
        agent_id=AgentID.ANALYST,
        name="Jochi",
        role="Data Analyst",
        capabilities=[
            "validation", "quality_assessment", "testing",
            "packaging", "data_analysis", "security_review"
        ]
    ),
    AgentID.OPS: AgentInfo(
        agent_id=AgentID.OPS,
        name="Ögedei",
        role="DevOps Engineer",
        capabilities=[
            "packaging", "deployment", "manifest_generation",
            "infrastructure", "operations"
        ]
    ),
}


class CircuitBreaker:
    """
    Circuit breaker for agent availability.

    Tracks failures and prevents repeated attempts to unavailable agents.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 300,
    ):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Seconds before retrying an open circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self._failures: dict[AgentID, int] = {}
        self._last_failure: dict[AgentID, datetime] = {}

    def is_available(self, agent: AgentID) -> bool:
        """
        Check if an agent is available (circuit not open).

        Args:
            agent: The agent to check

        Returns:
            True if the agent is available, False if circuit is open
        """
        failures = self._failures.get(agent, 0)

        if failures >= self.failure_threshold:
            last_fail = self._last_failure.get(agent)
            if last_fail:
                elapsed = (datetime.now(timezone.utc) - last_fail).total_seconds()
                if elapsed < self.timeout_seconds:
                    logger.debug(
                        f"Circuit open for {agent.value} "
                        f"({elapsed}s elapsed, {self.timeout_seconds}s timeout)"
                    )
                    return False
                # Timeout expired, reset
                self._reset(agent)

        return True

    def record_success(self, agent: AgentID) -> None:
        """
        Record a successful interaction, resetting failures.

        Args:
            agent: The agent that succeeded
        """
        self._failures[agent] = 0
        logger.debug(f"Recorded success for {agent.value}, circuit closed")

    def record_failure(self, agent: AgentID) -> None:
        """
        Record a failed interaction.

        Args:
            agent: The agent that failed
        """
        self._failures[agent] = self._failures.get(agent, 0) + 1
        self._last_failure[agent] = datetime.now(timezone.utc)

        failures = self._failures[agent]
        if failures >= self.failure_threshold:
            logger.warning(
                f"Circuit opened for {agent.value} "
                f"({failures} failures)"
            )
        else:
            logger.debug(
                f"Recorded failure for {agent.value} "
                f"({failures}/{self.failure_threshold})"
            )

    def _reset(self, agent: AgentID) -> None:
        """Reset the circuit breaker for an agent."""
        self._failures[agent] = 0
        logger.debug(f"Reset circuit breaker for {agent.value}")

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        self._failures.clear()
        self._last_failure.clear()
        logger.debug("Reset all circuit breakers")


class SpecialistRouter:
    """
    Routes skill creation tasks to appropriate OpenClaw agents.

    The router considers:
    1. Task type (from ROUTING_TABLE)
    2. Skill domain (from DOMAIN_ROUTING)
    3. Agent availability (via webhook API)
    4. Circuit breaker state (to avoid failing agents)
    5. Fallback hierarchy (specialist -> backup -> main)
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        gateway_url: Optional[str] = None,
        gateway_token: Optional[str] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize the specialist router.

        Args:
            webhook_url: Base URL for webhook API (e.g., "https://domain.com/api")
            gateway_url: OpenClaw gateway URL for agent availability
            gateway_token: Auth token for gateway
            circuit_breaker: Circuit breaker instance (creates new if None)
            http_client: HTTP client for API calls (creates new if None)
        """
        self.webhook_url = webhook_url
        self.gateway_url = gateway_url
        self.gateway_token = gateway_token
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self._http_client = http_client
        self._agent_cache: dict[AgentID, bool] = {}
        self._cache_expiry: dict[AgentID, datetime] = {}

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                headers={"Content-Type": "application/json"}
            )
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "SpecialistRouter":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def route_specialist(
        self,
        task_type: TaskType | str,
        skill_domain: SkillDomain | str = SkillDomain.GENERAL,
    ) -> RoutingResult:
        """
        Route a task to the appropriate agent.

        This is a synchronous method that uses cached availability data.
        For real-time availability checks, use route_specialist_async().

        Args:
            task_type: The type of task to route
            skill_domain: The skill domain (affects backup agent selection)

        Returns:
            RoutingResult with selected agent and routing metadata
        """
        # Normalize string inputs
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type)
            except ValueError:
                logger.warning(f"Unknown task type: {task_type}, using general routing")
                task_type = TaskType.CORE_IMPLEMENTATION

        if isinstance(skill_domain, str):
            try:
                skill_domain = SkillDomain(skill_domain)
            except ValueError:
                skill_domain = SkillDomain.GENERAL

        # Get primary and fallback agents from routing table
        agent_chain = self._build_agent_chain(task_type, skill_domain)

        # Find first available agent (considering circuit breaker)
        for i, agent_id in enumerate(agent_chain):
            agent = AGENT_INFO[agent_id]

            # Check circuit breaker
            if not self.circuit_breaker.is_available(agent_id):
                logger.debug(f"Agent {agent_id.value} skipped (circuit open)")
                continue

            # Use cached availability if available
            cached_available = self._agent_cache.get(agent_id)
            cache_valid = self._is_cache_valid(agent_id)

            is_fallback = i > 0
            if cache_valid and cached_available:
                return RoutingResult(
                    agent_id=agent_id,
                    agent_name=agent.name,
                    is_fallback=is_fallback,
                    reason="Routing via cache" if is_fallback else "Primary agent from routing table",
                    available=True,
                )

            # If no cache, assume available (will be verified asynchronously)
            return RoutingResult(
                agent_id=agent_id,
                agent_name=agent.name,
                is_fallback=is_fallback,
                reason="Primary agent" if not is_fallback else f"Fallback agent #{i}",
                available=True,  # Optimistically assume available
            )

        # Last resort: main agent
        main_agent = AGENT_INFO[AgentID.MAIN]
        return RoutingResult(
            agent_id=AgentID.MAIN,
            agent_name=main_agent.name,
            is_fallback=True,
            reason="Last resort fallback",
            available=True,
        )

    async def route_specialist_async(
        self,
        task_type: TaskType | str,
        skill_domain: SkillDomain | str = SkillDomain.GENERAL,
        use_cache: bool = True,
    ) -> RoutingResult:
        """
        Route a task to the appropriate agent with real-time availability check.

        Args:
            task_type: The type of task to route
            skill_domain: The skill domain (affects backup agent selection)
            use_cache: Whether to use cached availability data

        Returns:
            RoutingResult with selected agent and real-time availability
        """
        # Normalize string inputs
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type)
            except ValueError:
                logger.warning(f"Unknown task type: {task_type}")
                task_type = TaskType.CORE_IMPLEMENTATION

        if isinstance(skill_domain, str):
            try:
                skill_domain = SkillDomain(skill_domain)
            except ValueError:
                skill_domain = SkillDomain.GENERAL

        # Get primary and fallback agents
        agent_chain = self._build_agent_chain(task_type, skill_domain)

        # Check availability for each agent in the chain
        for i, agent_id in enumerate(agent_chain):
            # Check circuit breaker first
            if not self.circuit_breaker.is_available(agent_id):
                logger.debug(f"Skipping {agent_id.value} (circuit open)")
                continue

            # Check real-time availability
            available = await self.check_agent_availability(
                agent_id, use_cache=use_cache
            )

            if available:
                agent = AGENT_INFO[agent_id]
                return RoutingResult(
                    agent_id=agent_id,
                    agent_name=agent.name,
                    is_fallback=i > 0,
                    reason="Primary agent" if i == 0 else f"Fallback agent #{i}",
                    available=True,
                )

        # No agent available - return main with available=False
        main_agent = AGENT_INFO[AgentID.MAIN]
        return RoutingResult(
            agent_id=AgentID.MAIN,
            agent_name=main_agent.name,
            is_fallback=True,
            reason="No agents available, would queue",
            available=False,
        )

    def _build_agent_chain(
        self,
        task_type: TaskType,
        skill_domain: SkillDomain,
    ) -> list[AgentID]:
        """
        Build the chain of agents to try for a task.

        Chain priority:
        1. Task-type specific agents from ROUTING_TABLE
        2. Domain-specific agents from DOMAIN_ROUTING
        3. Main agent as final fallback

        Args:
            task_type: The task type
            skill_domain: The skill domain

        Returns:
            List of AgentIDs in priority order
        """
        agent_chain: list[AgentID] = []

        # Add task-type specific agents
        if task_type in ROUTING_TABLE:
            task_agents = ROUTING_TABLE[task_type]
            for agent in task_agents:
                if agent not in agent_chain:
                    agent_chain.append(agent)

        # Add domain-specific agents if not already included
        if skill_domain in DOMAIN_ROUTING:
            domain_agents = DOMAIN_ROUTING[skill_domain]
            for agent in domain_agents:
                if agent not in agent_chain:
                    agent_chain.append(agent)

        # Ensure main is always last
        if AgentID.MAIN not in agent_chain:
            agent_chain.append(AgentID.MAIN)

        return agent_chain

    async def check_agent_availability(
        self,
        agent_id: AgentID,
        use_cache: bool = True,
        cache_ttl_seconds: int = 30,
    ) -> bool:
        """
        Check if an agent is available via webhook API.

        Args:
            agent_id: The agent to check
            use_cache: Whether to use cached availability data
            cache_ttl_seconds: Cache time-to-live in seconds

        Returns:
            True if the agent is available, False otherwise
        """
        # Check cache first
        if use_cache:
            cached = self._agent_cache.get(agent_id)
            if cached is not None and self._is_cache_valid(agent_id, cache_ttl_seconds):
                return cached

        # Fetch real-time availability
        available = await self._fetch_agent_availability(agent_id)

        # Update cache
        self._agent_cache[agent_id] = available
        self._cache_expiry[agent_id] = (
            datetime.now(timezone.utc) + timedelta(seconds=cache_ttl_seconds)
        )

        return available

    def _is_cache_valid(
        self,
        agent_id: AgentID,
        ttl_seconds: int = 30,
    ) -> bool:
        """Check if cached availability data is still valid."""
        expiry = self._cache_expiry.get(agent_id)
        if expiry is None:
            return False
        return datetime.now(timezone.utc) < expiry

    async def _fetch_agent_availability(self, agent_id: AgentID) -> bool:
        """
        Fetch agent availability from webhook API.

        Args:
            agent_id: The agent to check

        Returns:
            True if available, False otherwise
        """
        # Try webhook API first
        if self.webhook_url:
            try:
                url = f"{self.webhook_url}/agents/{agent_id.value}"
                response = await self.http_client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "offline")
                    return status in ("idle", "working")
            except Exception as e:
                logger.debug(f"Webhook availability check failed: {e}")

        # Try gateway API as backup
        if self.gateway_url:
            try:
                headers = {}
                if self.gateway_token:
                    headers["Authorization"] = f"Bearer {self.gateway_token}"

                url = f"{self.gateway_url}/agents/{agent_id.value}/status"
                response = await self.http_client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("available", False)
            except Exception as e:
                logger.debug(f"Gateway availability check failed: {e}")

        # Assume available if we can't check (optimistic)
        return True

    def record_agent_success(self, agent_id: AgentID) -> None:
        """
        Record a successful interaction with an agent.

        Resets the circuit breaker for the agent.

        Args:
            agent_id: The agent that succeeded
        """
        self.circuit_breaker.record_success(agent_id)

    def record_agent_failure(self, agent_id: AgentID) -> None:
        """
        Record a failed interaction with an agent.

        Increments the circuit breaker failure count.

        Args:
            agent_id: The agent that failed
        """
        self.circuit_breaker.record_failure(agent_id)

    def get_agent_info(self, agent_id: AgentID) -> AgentInfo:
        """
        Get information about an agent.

        Args:
            agent_id: The agent to query

        Returns:
            AgentInfo with agent details
        """
        return AGENT_INFO[agent_id]

    def get_all_agents(self) -> list[AgentInfo]:
        """Get information about all agents."""
        return list(AGENT_INFO.values())

    def clear_cache(self) -> None:
        """Clear the availability cache."""
        self._agent_cache.clear()
        self._cache_expiry.clear()
        logger.debug("Cleared availability cache")

    def reset_circuit_breakers(self) -> None:
        """Reset all circuit breakers."""
        self.circuit_breaker.reset_all()


# Convenience functions

@lru_cache(maxsize=128)
def get_agent_for_task_type(task_type: TaskType) -> AgentID:
    """
    Get the primary agent for a task type (cached).

    Args:
        task_type: The task type

    Returns:
        Primary AgentID for the task
    """
    if task_type in ROUTING_TABLE:
        return ROUTING_TABLE[task_type][0]
    return AgentID.MAIN


def get_fallback_agent(primary_agent: AgentID) -> Optional[AgentID]:
    """
    Get the fallback agent for a primary agent.

    Args:
        primary_agent: The primary agent ID

    Returns:
        Fallback AgentID or None
    """
    fallback_map: dict[AgentID, Optional[AgentID]] = {
        AgentID.RESEARCHER: AgentID.MAIN,
        AgentID.WRITER: AgentID.MAIN,
        AgentID.DEVELOPER: AgentID.ANALYST,
        AgentID.ANALYST: AgentID.MAIN,
        AgentID.OPS: AgentID.DEVELOPER,
        AgentID.MAIN: None,  # No fallback for main
    }
    return fallback_map.get(primary_agent)


# CLI for testing

def main() -> None:
    """CLI for testing the specialist router."""
    import json

    # Demonstrate routing for all task types
    print("Specialist Router - Task to Agent Mapping\n")
    print("=" * 60)

    router = SpecialistRouter()

    for task in TaskType:
        result = router.route_specialist(task)
        domain = SkillDomain.GENERAL

        print(f"\nTask: {task.value}")
        print(f"  Agent: {result.agent_name} ({result.agent_id.value})")
        print(f"  Fallback: {result.is_fallback}")
        print(f"  Reason: {result.reason}")

    # Print routing table as JSON
    print("\n" + "=" * 60)
    print("\nRouting Table (JSON):")
    routing_json = {
        task.value: [a.value for a in agents]
        for task, agents in ROUTING_TABLE.items()
    }
    print(json.dumps(routing_json, indent=2))


if __name__ == "__main__":
    main()
