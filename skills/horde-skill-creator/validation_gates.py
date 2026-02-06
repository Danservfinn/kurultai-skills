"""
Validation Gates System for Supercharged Skill Creator

Implements 6 validation gates for the skill creation workflow, each with
specific validation criteria, failure actions, and retry policies.

Gate Sequence:
1. Feasibility Gate (after Intent Gathering)
2. Completeness Gate (after Parallel Exploration)
3. Robustness Gate (after Adversarial Review)
4. Viability Gate (after Synthesis)
5. Spec Complete Gate (after Detailed Design)
6. Deploy Ready Gate (after Package & Validate)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GateStatus(Enum):
    """Status of a validation gate check."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class Phase(Enum):
    """Workflow phases."""
    INTENT_GATHERING = "intent_gathering"
    PARALLEL_EXPLORATION = "parallel_exploration"
    ADVERSARIAL_REVIEW = "adversarial_review"
    SYNTHESIS = "synthesis"
    DETAILED_DESIGN = "detailed_design"
    PACKAGE_VALIDATE = "package_validate"


class FailAction(Enum):
    """Actions to take on gate failure."""
    HALT = "halt"  # Stop the workflow
    RETRY = "retry"  # Retry the gate
    ESCALATE = "escalate"  # Escalate to human review
    PROCEED_WITH_WARNING = "proceed_with_warning"  # Continue but flag
    ROLLBACK = "rollback"  # Rollback to previous phase
    ALTERNATE_PATH = "alternate_path"  # Try alternative approach


class RetryPolicyType(Enum):
    """Retry policy types."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE = "immediate"
    NO_RETRY = "no_retry"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    threshold: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GateResult:
    """Result of a gate validation."""
    gate_name: str
    status: GateStatus
    validations: List[ValidationResult]
    overall_score: float
    passed: bool
    failure_reason: Optional[str] = None
    action_taken: Optional[FailAction] = None
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetryPolicy:
    """Retry policy configuration."""
    policy_type: RetryPolicyType = RetryPolicyType.EXPONENTIAL_BACKOFF
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_multiplier: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1


@dataclass
class FailActionConfig:
    """Configuration for failure actions."""
    primary_action: FailAction
    secondary_actions: List[FailAction] = field(default_factory=list)
    escalation_threshold: int = 3  # Escalate after N retries
    halt_on_escalation: bool = True
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class GateSpec:
    """Specification for a validation gate."""
    name: str
    phase: Phase
    description: str
    validations: List[Dict[str, Any]]
    thresholds: Dict[str, float]
    fail_action: FailActionConfig
    retry_policy: RetryPolicy
    required: bool = True
    timeout_seconds: float = 300.0


# =============================================================================
# Gate Specifications
# =============================================================================

GATES: Dict[str, GateSpec] = {
    "gate_1_feasibility": GateSpec(
        name="gate_1_feasibility",
        phase=Phase.INTENT_GATHERING,
        description="Validates that the skill intent is clear, feasible, and well-scoped",
        validations=[
            {
                "name": "intent_clarity",
                "description": "Intent statement is unambiguous and actionable",
                "validator": "validate_intent_clarity",
                "weight": 1.0
            },
            {
                "name": "scope_bounded",
                "description": "Scope is appropriately bounded for a single skill",
                "validator": "validate_scope_bounded",
                "weight": 1.0
            },
            {
                "name": "domain_feasibility",
                "description": "Domain expertise is available or acquirable",
                "validator": "validate_domain_feasibility",
                "weight": 0.8
            },
            {
                "name": "dependency_check",
                "description": "Required dependencies and tools are identified",
                "validator": "validate_dependencies",
                "weight": 0.6
            }
        ],
        thresholds={
            "min_overall_score": 0.75,
            "min_individual_score": 0.6,
            "critical_checks": ["intent_clarity", "scope_bounded"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.RETRY,
            secondary_actions=[FailAction.ESCALATE],
            escalation_threshold=2
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.EXPONENTIAL_BACKOFF,
            max_retries=2,
            base_delay=2.0,
            backoff_multiplier=2.0
        )
    ),

    "gate_2_completeness": GateSpec(
        name="gate_2_completeness",
        phase=Phase.PARALLEL_EXPLORATION,
        description="Validates that exploration has covered all necessary dimensions",
        validations=[
            {
                "name": "perspective_coverage",
                "description": "Multiple expert perspectives have been explored",
                "validator": "validate_perspective_coverage",
                "weight": 1.0
            },
            {
                "name": "alternatives_considered",
                "description": "Alternative approaches have been documented",
                "validator": "validate_alternatives",
                "weight": 0.9
            },
            {
                "name": "edge_cases_identified",
                "description": "Edge cases and failure modes are identified",
                "validator": "validate_edge_cases",
                "weight": 0.8
            },
            {
                "name": "context_completeness",
                "description": "Relevant context and constraints are captured",
                "validator": "validate_context",
                "weight": 0.7
            }
        ],
        thresholds={
            "min_overall_score": 0.7,
            "min_individual_score": 0.5,
            "critical_checks": ["perspective_coverage"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.RETRY,
            secondary_actions=[FailAction.ESCALATE, FailAction.ALTERNATE_PATH],
            escalation_threshold=3
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.EXPONENTIAL_BACKOFF,
            max_retries=3,
            base_delay=3.0
        )
    ),

    "gate_3_robustness": GateSpec(
        name="gate_3_robustness",
        phase=Phase.ADVERSARIAL_REVIEW,
        description="Validates that the design survives adversarial scrutiny",
        validations=[
            {
                "name": "adversarial_challenges",
                "description": "Adversarial challenges have been addressed",
                "validator": "validate_adversarial_challenges",
                "weight": 1.0
            },
            {
                "name": "security_review",
                "description": "Security implications are reviewed",
                "validator": "validate_security_review",
                "weight": 1.0
            },
            {
                "name": "failure_resilience",
                "description": "Failure modes have mitigation strategies",
                "validator": "validate_failure_resilience",
                "weight": 0.9
            },
            {
                "name": "assumption_scrutiny",
                "description": "Assumptions have been challenged and validated",
                "validator": "validate_assumptions",
                "weight": 0.8
            }
        ],
        thresholds={
            "min_overall_score": 0.75,
            "min_individual_score": 0.6,
            "critical_checks": ["adversarial_challenges", "security_review"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.RETRY,
            secondary_actions=[FailAction.ROLLBACK, FailAction.ESCALATE],
            escalation_threshold=2
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.EXPONENTIAL_BACKOFF,
            max_retries=2,
            base_delay=5.0
        )
    ),

    "gate_4_viability": GateSpec(
        name="gate_4_viability",
        phase=Phase.SYNTHESIS,
        description="Validates that the synthesized design is viable and coherent",
        validations=[
            {
                "name": "synthesis_coherence",
                "description": "Synthesized design is internally coherent",
                "validator": "validate_synthesis_coherence",
                "weight": 1.0
            },
            {
                "name": "tradeoff_rationale",
                "description": "Tradeoffs have clear rationale",
                "validator": "validate_tradeoffs",
                "weight": 0.9
            },
            {
                "name": "implementation_path",
                "description": "Implementation path is clear and achievable",
                "validator": "validate_implementation_path",
                "weight": 1.0
            },
            {
                "name": "constraint_satisfaction",
                "description": "All constraints are satisfied or documented",
                "validator": "validate_constraints",
                "weight": 0.8
            }
        ],
        thresholds={
            "min_overall_score": 0.8,
            "min_individual_score": 0.65,
            "critical_checks": ["synthesis_coherence", "implementation_path"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.RETRY,
            secondary_actions=[FailAction.ROLLBACK, FailAction.ESCALATE],
            escalation_threshold=2
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.EXPONENTIAL_BACKOFF,
            max_retries=2,
            base_delay=3.0
        )
    ),

    "gate_5_spec_complete": GateSpec(
        name="gate_5_spec_complete",
        phase=Phase.DETAILED_DESIGN,
        description="Validates that the specification is complete and actionable",
        validations=[
            {
                "name": "spec_completeness",
                "description": "Specification covers all required sections",
                "validator": "validate_spec_completeness",
                "weight": 1.0
            },
            {
                "name": "api_contracts",
                "description": "API contracts are fully specified",
                "validator": "validate_api_contracts",
                "weight": 1.0
            },
            {
                "name": "error_handling",
                "description": "Error cases are fully specified",
                "validator": "validate_error_handling",
                "weight": 0.9
            },
            {
                "name": "testing_strategy",
                "description": "Testing strategy is comprehensive",
                "validator": "validate_testing_strategy",
                "weight": 0.8
            },
            {
                "name": "documentation_complete",
                "description": "Documentation requirements are met",
                "validator": "validate_documentation",
                "weight": 0.7
            }
        ],
        thresholds={
            "min_overall_score": 0.85,
            "min_individual_score": 0.7,
            "critical_checks": ["spec_completeness", "api_contracts"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.HALT,
            secondary_actions=[FailAction.ESCALATE],
            escalation_threshold=1
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.NO_RETRY,
            max_retries=0
        )
    ),

    "gate_6_deploy_ready": GateSpec(
        name="gate_6_deploy_ready",
        phase=Phase.PACKAGE_VALIDATE,
        description="Validates that the package is ready for deployment",
        validations=[
            {
                "name": "package_integrity",
                "description": "Package structure and metadata are valid",
                "validator": "validate_package_integrity",
                "weight": 1.0
            },
            {
                "name": "tests_passing",
                "description": "All tests pass with required coverage",
                "validator": "validate_tests",
                "weight": 1.0
            },
            {
                "name": "dependencies_resolved",
                "description": "All dependencies are resolved and compatible",
                "validator": "validate_dependencies_resolved",
                "weight": 1.0
            },
            {
                "name": "security_check",
                "description": "Security and vulnerability checks pass",
                "validator": "validate_security",
                "weight": 1.0
            },
            {
                "name": "documentation_deployable",
                "description": "Documentation is deployable",
                "validator": "validate_documentation_deployable",
                "weight": 0.8
            },
            {
                "name": "performance_baseline",
                "description": "Performance meets baseline requirements",
                "validator": "validate_performance",
                "weight": 0.7
            }
        ],
        thresholds={
            "min_overall_score": 0.9,
            "min_individual_score": 0.8,
            "critical_checks": ["package_integrity", "tests_passing", "security_check"]
        },
        fail_action=FailActionConfig(
            primary_action=FailAction.HALT,
            secondary_actions=[FailAction.ESCALATE],
            escalation_threshold=1
        ),
        retry_policy=RetryPolicy(
            policy_type=RetryPolicyType.FIXED_DELAY,
            max_retries=1,
            base_delay=5.0
        )
    )
}


# =============================================================================
# Circuit Breaker
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures and repeated failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Requests are blocked after threshold failures
    - HALF_OPEN: Allow one request through to test recovery
    """

    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before attempting recovery
            half_open_max_calls: Number of calls to allow in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0

    @property
    def state(self) -> State:
        """Get current state, potentially transitioning based on time."""
        if self._state == self.State.OPEN:
            if (datetime.utcnow() - self._last_failure_time).total_seconds() >= self.recovery_timeout:
                self._state = self.State.HALF_OPEN
                self._half_open_calls = 0
                logger.info("Circuit breaker entering HALF_OPEN state")
        return self._state

    def record_success(self) -> None:
        """Record a successful operation."""
        if self._state == self.State.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._state = self.State.CLOSED
                self._failure_count = 0
                logger.info("Circuit breaker returning to CLOSED state")
        elif self._state == self.State.CLOSED:
            self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()

        if self._failure_count >= self.failure_threshold:
            self._state = self.State.OPEN
            logger.warning(
                f"Circuit breaker OPENED after {self._failure_count} failures"
            )

    def allow_request(self) -> bool:
        """Check if a request should be allowed through."""
        return self.state in (self.State.CLOSED, self.State.HALF_OPEN)

    def reset(self) -> None:
        """Reset the circuit breaker to initial state."""
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        logger.info("Circuit breaker reset to CLOSED state")


# =============================================================================
# Validation Gate Implementation
# =============================================================================

class ValidationGate:
    """
    Main validation gate class that orchestrates gate checks.

    Each gate validates the output of a workflow phase before proceeding
    to the next phase.
    """

    def __init__(
        self,
        gates: Optional[Dict[str, GateSpec]] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        custom_validators: Optional[Dict[str, Callable]] = None
    ):
        """
        Initialize ValidationGate.

        Args:
            gates: Custom gate specifications (defaults to GATES)
            circuit_breaker: Custom circuit breaker (creates default if None)
            custom_validators: Custom validation functions
        """
        self.gates = gates or GATES
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.custom_validators = custom_validators or {}
        self._gate_history: Dict[str, List[GateResult]] = {}
        self._current_gate: Optional[str] = None

    def validate(
        self,
        phase: Union[Phase, str],
        data: Dict[str, Any],
        gate_name: Optional[str] = None
    ) -> GateResult:
        """
        Validate phase output against its gate.

        Args:
            phase: The phase being validated
            data: Phase output data to validate
            gate_name: Optional specific gate name (auto-detected if None)

        Returns:
            GateResult with validation outcome

        Raises:
            ValueError: If no gate found for phase
            CircuitBreakerOpenError: If circuit breaker is open
        """
        # Normalize phase
        if isinstance(phase, str):
            try:
                phase = Phase(phase)
            except ValueError:
                raise ValueError(f"Invalid phase: {phase}")

        # Auto-detect gate if not specified
        if gate_name is None:
            gate_name = self._get_gate_for_phase(phase)

        # Check circuit breaker
        if not self.circuit_breaker.allow_request():
            error_msg = (
                f"Circuit breaker is OPEN for gate '{gate_name}'. "
                f"Too many recent failures. Please wait before retrying."
            )
            logger.error(error_msg)
            return GateResult(
                gate_name=gate_name,
                status=GateStatus.FAILED,
                validations=[],
                overall_score=0.0,
                passed=False,
                failure_reason="Circuit breaker is open",
                action_taken=FailAction.HALT
            )

        # Get gate specification
        gate_spec = self.gates.get(gate_name)
        if gate_spec is None:
            raise ValueError(f"No gate found with name: {gate_name}")

        self._current_gate = gate_name
        logger.info(f"Running gate '{gate_name}' for phase '{phase.value}'")

        # Run validations
        result = self._run_validations(gate_spec, data)

        # Record result for circuit breaker
        if result.passed:
            self.circuit_breaker.record_success()
        else:
            self.circuit_breaker.record_failure()

        # Store history
        if gate_name not in self._gate_history:
            self._gate_history[gate_name] = []
        self._gate_history[gate_name].append(result)

        return result

    def _run_validations(
        self,
        gate_spec: GateSpec,
        data: Dict[str, Any]
    ) -> GateResult:
        """Run all validations for a gate."""
        validations: List[ValidationResult] = []
        status = GateStatus.RUNNING

        for validation_spec in gate_spec.validations:
            validator_name = validation_spec["validator"]
            validator = self._get_validator(validator_name)
            threshold = gate_spec.thresholds.get(
                f"min_{validation_spec['name']}_score",
                gate_spec.thresholds.get("min_individual_score", 0.6)
            )

            try:
                result = validator(validation_spec, data, threshold)
                validations.append(result)
            except Exception as e:
                logger.error(f"Validator '{validator_name}' failed: {e}")
                validations.append(ValidationResult(
                    check_name=validation_spec["name"],
                    passed=False,
                    score=0.0,
                    threshold=threshold,
                    message=f"Validator error: {str(e)}",
                    details={"error": str(e)}
                ))

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            validations,
            gate_spec.validations
        )

        # Check if gate passed
        min_score = gate_spec.thresholds.get("min_overall_score", 0.75)
        critical_checks = gate_spec.thresholds.get("critical_checks", [])
        passed = (
            overall_score >= min_score and
            all(v.passed for v in validations if v.check_name in critical_checks) and
            all(v.score >= gate_spec.thresholds.get("min_individual_score", 0.5)
                for v in validations if v.check_name in critical_checks)
        )

        # Determine status and action
        if passed:
            status = GateStatus.PASSED
            action_taken = None
            failure_reason = None
        else:
            status = GateStatus.FAILED
            action_taken = gate_spec.fail_action.primary_action
            failure_reason = self._generate_failure_reason(validations, gate_spec)

        return GateResult(
            gate_name=gate_spec.name,
            status=status,
            validations=validations,
            overall_score=overall_score,
            passed=passed,
            failure_reason=failure_reason,
            action_taken=action_taken
        )

    def check(
        self,
        criteria: Union[str, List[str], Callable],
        threshold: float,
        data: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """
        Helper method to check validation criteria.

        Args:
            criteria: Validation criteria as string, list, or callable
            threshold: Pass threshold (0.0 to 1.0)
            data: Data to validate against

        Returns:
            Tuple of (passed, score, message)
        """
        if callable(criteria):
            try:
                result = criteria(data)
                if isinstance(result, tuple):
                    return result
                return (result >= threshold, result, f"Score: {result}")
            except Exception as e:
                return (False, 0.0, f"Criteria function error: {e}")

        if isinstance(criteria, list):
            # All criteria must pass
            scores = []
            messages = []
            for criterion in criteria:
                passed, score, msg = self.check(criterion, threshold, data)
                scores.append(score)
                messages.append(msg)
            avg_score = sum(scores) / len(scores) if scores else 0.0
            all_passed = all(s >= threshold for s in scores)
            return (all_passed, avg_score, "; ".join(messages))

        # String criteria - check if field exists and meets threshold
        if isinstance(criteria, str):
            value = self._get_nested_value(data, criteria)
            if value is None:
                return (False, 0.0, f"Required field missing: {criteria}")

            # If value is numeric, check against threshold
            if isinstance(value, (int, float)):
                score = min(1.0, max(0.0, value))
                return (score >= threshold, score, f"Score for {criteria}: {score}")

            # If value is boolean, convert to score
            if isinstance(value, bool):
                score = 1.0 if value else 0.0
                return (score >= threshold, score, f"Boolean check {criteria}: {value}")

            # If value is a list/string, check non-empty
            if isinstance(value, (list, str)):
                score = 1.0 if len(value) > 0 else 0.0
                return (score >= threshold, score, f"Presence check {criteria}: {score}")

        return (False, 0.0, f"Unknown criteria type: {type(criteria)}")

    def fail(
        self,
        action: Union[FailAction, str],
        result: GateResult,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle gate failure with specified action.

        Args:
            action: Action to take on failure
            result: The gate result that failed
            context: Additional context for the action

        Returns:
            Action result with next steps
        """
        if isinstance(action, str):
            try:
                action = FailAction(action)
            except ValueError:
                raise ValueError(f"Invalid fail action: {action}")

        response = {
            "action": action.value,
            "gate": result.gate_name,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }

        if action == FailAction.HALT:
            response["message"] = self._format_halt_message(result)
            response["next_steps"] = ["Resolve validation failures", "Retry gate"]

        elif action == FailAction.RETRY:
            response["message"] = self._format_retry_message(result)
            response["next_steps"] = ["Fix identified issues", "Re-run validation"]

        elif action == FailAction.ESCALATE:
            response["message"] = self._format_escalation_message(result)
            response["next_steps"] = [
                "Review by human operator",
                "Manual intervention may be required"
            ]
            # Send notification (would integrate with notification system)
            logger.warning(f"ESCALATION required for gate '{result.gate_name}'")

        elif action == FailAction.PROCEED_WITH_WARNING:
            response["message"] = self._format_warning_message(result)
            response["next_steps"] = ["Proceed with caution", "Address warnings later"]
            response["warnings"] = [v.message for v in result.validations if not v.passed]

        elif action == FailAction.ROLLBACK:
            response["message"] = self._format_rollback_message(result)
            response["next_steps"] = [
                f"Rollback to previous phase",
                "Review and fix issues",
                "Re-run affected phases"
            ]
            response["rollback_phase"] = self._get_previous_phase(result.gate_name)

        elif action == FailAction.ALTERNATE_PATH:
            response["message"] = self._format_alternate_path_message(result)
            response["next_steps"] = ["Consider alternative implementation approach"]

        return response

    def retry(
        self,
        policy: Union[RetryPolicy, str, None],
        result: GateResult,
        attempt: int = 1
    ) -> Dict[str, Any]:
        """
        Execute retry policy for failed gate.

        Args:
            policy: Retry policy to use
            result: The failed gate result
            attempt: Current retry attempt number

        Returns:
            Retry information with delay and next steps
        """
        gate_spec = self.gates.get(result.gate_name)
        if gate_spec is None:
            return {"error": f"Unknown gate: {result.gate_name}"}

        # Use gate's retry policy if none specified
        if isinstance(policy, str):
            policy = RetryPolicy(RetryPolicyType(policy))
        if policy is None:
            policy = gate_spec.retry_policy

        # Check if we've exceeded max retries
        if attempt > policy.max_retries:
            logger.warning(
                f"Max retries ({policy.max_retries}) exceeded for gate '{result.gate_name}'"
            )
            # Escalate instead
            return self.fail(FailAction.ESCALATE, result, {"retry_attempts": attempt})

        # Calculate delay
        delay = self._calculate_retry_delay(policy, attempt)

        response = {
            "attempt": attempt,
            "max_retries": policy.max_retries,
            "delay_seconds": delay,
            "policy_type": policy.policy_type.value,
            "message": f"Retry attempt {attempt} of {policy.max_retries} after {delay:.1f}s delay",
            "next_steps": [
                f"Wait {delay:.1f} seconds",
                "Re-run validation",
                "Ensure issues are addressed before retry"
            ]
        }

        # Update result status for retry
        result.status = GateStatus.RETRYING
        result.retry_count = attempt

        return response

    def _get_validator(self, validator_name: str) -> Callable:
        """Get validator function by name."""
        # Check custom validators first
        if validator_name in self.custom_validators:
            return self.custom_validators[validator_name]

        # Check built-in validators
        if validator_name in BUILT_IN_VALIDATORS:
            return BUILT_IN_VALIDATORS[validator_name]

        raise ValueError(f"Unknown validator: {validator_name}")

    def _get_gate_for_phase(self, phase: Phase) -> str:
        """Get gate name for a given phase."""
        for gate_name, gate_spec in self.gates.items():
            if gate_spec.phase == phase:
                return gate_name
        raise ValueError(f"No gate found for phase: {phase.value}")

    def _calculate_overall_score(
        self,
        validations: List[ValidationResult],
        validation_specs: List[Dict[str, Any]]
    ) -> float:
        """Calculate weighted overall score from validations."""
        if not validations:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for validation, spec in zip(validations, validation_specs):
            weight = spec.get("weight", 1.0)
            total_weight += weight
            weighted_sum += validation.score * weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _generate_failure_reason(
        self,
        validations: List[ValidationResult],
        gate_spec: GateSpec
    ) -> str:
        """Generate human-readable failure reason."""
        failed = [v for v in validations if not v.passed]
        critical_failed = [
            v for v in failed
            if v.check_name in gate_spec.thresholds.get("critical_checks", [])
        ]

        if critical_failed:
            return (
                f"Critical validations failed: {', '.join(v.check_name for v in critical_failed)}. "
                f"Details: {'; '.join(v.message for v in critical_failed)}"
            )

        return (
            f"Validations failed: {', '.join(v.check_name for v in failed)}. "
            f"Details: {'; '.join(v.message for v in failed)}"
        )

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _get_previous_phase(self, gate_name: str) -> Optional[str]:
        """Get the phase before the current gate."""
        gate_order = [
            "gate_1_feasibility",
            "gate_2_completeness",
            "gate_3_robustness",
            "gate_4_viability",
            "gate_5_spec_complete",
            "gate_6_deploy_ready"
        ]
        try:
            idx = gate_order.index(gate_name)
            if idx > 0:
                return self.gates[gate_order[idx - 1]].phase.value
        except ValueError:
            pass
        return None

    def _calculate_retry_delay(self, policy: RetryPolicy, attempt: int) -> float:
        """Calculate delay before retry based on policy."""
        if policy.policy_type == RetryPolicyType.IMMEDIATE:
            return 0.0
        elif policy.policy_type == RetryPolicyType.FIXED_DELAY:
            delay = policy.base_delay
        elif policy.policy_type == RetryPolicyType.LINEAR_BACKOFF:
            delay = policy.base_delay * attempt
        elif policy.policy_type == RetryPolicyType.EXPONENTIAL_BACKOFF:
            delay = policy.base_delay * (policy.backoff_multiplier ** (attempt - 1))
        else:
            delay = policy.base_delay

        # Apply max delay cap
        delay = min(delay, policy.max_delay)

        # Add jitter if enabled
        if policy.jitter:
            import random
            jitter_amount = delay * policy.jitter_factor
            delay = delay - jitter_amount + (random.random() * 2 * jitter_amount)

        return max(0.0, delay)

    # Message formatting methods
    def _format_halt_message(self, result: GateResult) -> str:
        return f"Workflow HALTED at gate '{result.gate_name}'. {result.failure_reason}"

    def _format_retry_message(self, result: GateResult) -> str:
        return f"Gate '{result.gate_name}' failed. Please address issues and retry."

    def _format_escalation_message(self, result: GateResult) -> str:
        return f"ESCALATION: Gate '{result.gate_name}' requires human review. {result.failure_reason}"

    def _format_warning_message(self, result: GateResult) -> str:
        return f"WARNING: Proceeding past gate '{result.gate_name}' with validation failures."

    def _format_rollback_message(self, result: GateResult) -> str:
        return f"ROLLBACK: Initiating rollback due to gate '{result.gate_name}' failure."

    def _format_alternate_path_message(self, result: GateResult) -> str:
        return f"ALTERNATE PATH: Consider alternative approach due to gate '{result.gate_name}' failure."

    def get_gate_history(self, gate_name: Optional[str] = None) -> List[GateResult]:
        """Get history of gate results."""
        if gate_name:
            return self._gate_history.get(gate_name, [])
        return [
            result
            for results in self._gate_history.values()
            for result in results
        ]

    def reset_circuit_breaker(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.circuit_breaker.reset()


# =============================================================================
# Built-in Validators
# =============================================================================

def _create_validation_result(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float,
    passed: bool,
    score: float,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """Helper to create validation results."""
    return ValidationResult(
        check_name=spec["name"],
        passed=passed,
        score=score,
        threshold=threshold,
        message=message,
        details=details or {}
    )


# Gate 1 Validators

def validate_intent_clarity(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that intent statement is clear and unambiguous."""
    intent = data.get("intent", "")
    if not intent:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "Intent statement is missing"
        )

    # Check for clarity indicators
    score = 0.0
    issues = []

    # Length check (too short or too long)
    if 20 < len(intent) < 500:
        score += 0.3
    else:
        issues.append("Intent length should be between 20-500 characters")

    # Contains actionable verb
    actionable_verbs = ["create", "build", "implement", "design", "develop",
                       "generate", "produce", "construct", "formulate"]
    if any(verb in intent.lower() for verb in actionable_verbs):
        score += 0.3
    else:
        issues.append("Intent should contain an actionable verb")

    # Specific outcome mentioned
    outcome_indicators = ["that will", "to", "for", "which", "who", "what"]
    if any(indicator in intent.lower() for indicator in outcome_indicators):
        score += 0.2
    else:
        issues.append("Intent should specify the outcome")

    # No ambiguous words
    ambiguous = ["maybe", "might", "possibly", "could", "should", "somewhat"]
    if not any(amb in intent.lower() for amb in ambiguous):
        score += 0.2
    else:
        issues.append("Intent contains ambiguous language")

    passed = score >= threshold
    message = f"Intent clarity score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "intent_length": len(intent)}
    )


def validate_scope_bounded(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that scope is appropriately bounded."""
    scope = data.get("scope", {})
    if not scope:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "Scope definition is missing"
        )

    score = 0.0
    issues = []

    # Has boundaries
    if scope.get("in_scope") or scope.get("out_of_scope"):
        score += 0.4
    else:
        issues.append("Scope should define in-scope and out-of-scope items")

    # Reasonable number of in-scope items
    in_scope = scope.get("in_scope", [])
    if 1 <= len(in_scope) <= 10:
        score += 0.3
    elif len(in_scope) > 10:
        issues.append("Too many in-scope items - consider splitting")
        score += 0.1
    else:
        issues.append("No in-scope items defined")

    # Has exclusions
    out_of_scope = scope.get("out_of_scope", [])
    if len(out_of_scope) > 0:
        score += 0.3
    else:
        issues.append("Consider defining out-of-scope exclusions")

    passed = score >= threshold
    message = f"Scope bounded score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "in_scope_count": len(in_scope), "out_of_scope_count": len(out_of_scope)}
    )


def validate_domain_feasibility(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that domain expertise is available."""
    domain = data.get("domain", {})
    if not domain:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "Domain information is missing"
        )

    score = 0.0
    issues = []

    # Domain identified
    if domain.get("name"):
        score += 0.4
    else:
        issues.append("Domain name not specified")

    # Expertise availability
    expertise = domain.get("expertise", {})
    if expertise.get("available"):
        score += 0.4
    elif expertise.get("source"):
        score += 0.2
        issues.append("Expertise source identified but availability uncertain")
    else:
        issues.append("Domain expertise availability not addressed")

    # Knowledge sources
    sources = domain.get("knowledge_sources", [])
    if sources:
        score += 0.2
    else:
        issues.append("No knowledge sources identified")

    passed = score >= threshold
    message = f"Domain feasibility score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "domain": domain.get("name"), "sources_count": len(sources)}
    )


def validate_dependencies(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that dependencies are identified."""
    dependencies = data.get("dependencies", {})
    if not dependencies:
        # Not critical - can proceed without explicit dependencies
        return _create_validation_result(
            spec, data, threshold, True, 0.5,
            "No explicit dependencies identified (may be needed later)",
            {"warning": "missing_dependencies"}
        )

    score = 0.0
    issues = []

    # Has tools/libraries listed
    tools = dependencies.get("tools", [])
    libraries = dependencies.get("libraries", [])
    if tools or libraries:
        score += 0.5
    else:
        issues.append("Consider listing required tools and libraries")

    # Versions specified where applicable
    versioned = sum(1 for item in tools + libraries if isinstance(item, dict) and "version" in item)
    if versioned > 0:
        score += 0.3
    else:
        issues.append("Specify versions for dependencies where applicable")

    # External services identified
    services = dependencies.get("services", [])
    if services:
        score += 0.2

    passed = score >= threshold
    message = f"Dependencies score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "tools_count": len(tools), "libraries_count": len(libraries)}
    )


# Gate 2 Validators

def validate_perspective_coverage(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that multiple perspectives were explored."""
    exploration = data.get("exploration", {})
    if not exploration:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "Exploration data is missing"
        )

    score = 0.0
    issues = []

    perspectives = exploration.get("perspectives", [])
    if not perspectives:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No perspectives were explored"
        )

    # Minimum number of perspectives
    if len(perspectives) >= 3:
        score += 0.5
    elif len(perspectives) >= 2:
        score += 0.3
        issues.append("Consider exploring more perspectives (recommended: 3+)")
    else:
        issues.append("Only one perspective explored - need more diversity")

    # Perspective diversity (different roles/types)
    types = set(p.get("role", p.get("type", "unknown")) for p in perspectives)
    if len(types) >= 3:
        score += 0.3
    elif len(types) >= 2:
        score += 0.2

    # Each perspective has substantive content
    substantial = sum(1 for p in perspectives if len(p.get("content", "")) > 100)
    if substantial == len(perspectives):
        score += 0.2
    elif substantial >= len(perspectives) / 2:
        score += 0.1

    passed = score >= threshold
    message = f"Perspective coverage score: {score:.2f} ({len(perspectives)} perspectives)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "perspective_count": len(perspectives), "unique_types": len(types)}
    )


def validate_alternatives(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that alternative approaches were considered."""
    exploration = data.get("exploration", {})
    alternatives = exploration.get("alternatives", [])

    score = 0.0
    issues = []

    if not alternatives:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No alternative approaches were documented"
        )

    # Minimum alternatives
    if len(alternatives) >= 2:
        score += 0.5
    else:
        issues.append("Only one alternative - consider more options")
        score += 0.2

    # Alternatives have comparison
    has_comparison = any(a.get("pros") and a.get("cons") for a in alternatives)
    if has_comparison:
        score += 0.3
    else:
        issues.append("Alternatives should have pros/cons analysis")

    # Rationale for chosen approach
    chosen = exploration.get("chosen_approach_rationale")
    if chosen:
        score += 0.2
    else:
        issues.append("Include rationale for chosen approach")

    passed = score >= threshold
    message = f"Alternatives score: {score:.2f} ({len(alternatives)} alternatives)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "alternatives_count": len(alternatives)}
    )


def validate_edge_cases(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that edge cases were identified."""
    exploration = data.get("exploration", {})
    edge_cases = exploration.get("edge_cases", [])

    score = 0.0
    issues = []

    # Edge cases identified
    if len(edge_cases) >= 3:
        score += 0.5
    elif len(edge_cases) >= 1:
        score += 0.3
        issues.append("Consider more edge cases")
    else:
        issues.append("No edge cases identified")

    # Edge cases have handling strategies
    with_handling = sum(1 for ec in edge_cases if ec.get("handling"))
    if with_handling == len(edge_cases) and len(edge_cases) > 0:
        score += 0.3
    elif with_handling > 0:
        score += 0.1

    # Failure modes considered
    failure_modes = exploration.get("failure_modes", [])
    if failure_modes:
        score += 0.2

    passed = score >= threshold
    message = f"Edge cases score: {score:.2f} ({len(edge_cases)} cases)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "edge_cases_count": len(edge_cases), "failure_modes_count": len(failure_modes)}
    )


def validate_context(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that relevant context was captured."""
    context = data.get("context", {})

    score = 0.0
    issues = []

    # Constraints documented
    constraints = context.get("constraints", [])
    if constraints:
        score += 0.3
    else:
        issues.append("No constraints documented")

    # Stakeholders identified
    stakeholders = context.get("stakeholders", [])
    if stakeholders:
        success_criteria = context.get("success_criteria")
        if success_criteria:
            score += 0.3
        else:
            score += 0.1
            issues.append("Define success criteria")
    else:
        issues.append("Stakeholders not identified")

    # Environment/context factors
    environment = context.get("environment", {})
    if environment:
        score += 0.2

    # Assumptions documented
    assumptions = context.get("assumptions", [])
    if assumptions:
        score += 0.2

    passed = score >= threshold
    message = f"Context completeness score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues}
    )


# Gate 3 Validators

def validate_adversarial_challenges(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that adversarial challenges were addressed."""
    adversarial = data.get("adversarial_review", {})

    score = 0.0
    issues = []

    challenges = adversarial.get("challenges", [])
    if not challenges:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No adversarial challenges documented"
        )

    # Multiple challenges
    if len(challenges) >= 3:
        score += 0.4
    elif len(challenges) >= 1:
        score += 0.2
        issues.append("More adversarial challenges should be explored")

    # Challenges have responses
    addressed = sum(1 for c in challenges if c.get("response") or c.get("mitigation"))
    if addressed == len(challenges):
        score += 0.4
    elif addressed > 0:
        score += 0.2
        issues.append("Some challenges lack mitigation strategies")

    # Red team perspective present
    has_red_team = adversarial.get("red_team_perspective")
    if has_red_team:
        score += 0.2

    passed = score >= threshold
    message = f"Adversarial challenges score: {score:.2f} ({len(challenges)} challenges)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "challenges_count": len(challenges), "addressed_count": addressed}
    )


def validate_security_review(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that security implications were reviewed."""
    security = data.get("security_review", {})

    score = 0.0
    issues = []

    # Security concerns documented
    concerns = security.get("concerns", [])
    if concerns:
        score += 0.3
    else:
        issues.append("No security concerns documented")

    # Mitigations in place
    mitigations = security.get("mitigations", [])
    if mitigations:
        score += 0.3
    else:
        issues.append("No security mitigations proposed")

    # Data handling considered
    data_handling = security.get("data_handling")
    if data_handling:
        score += 0.2
    else:
        issues.append("Data handling not addressed")

    # Attack surface analyzed
    attack_surface = security.get("attack_surface")
    if attack_surface:
        score += 0.2

    passed = score >= threshold
    message = f"Security review score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "concerns_count": len(concerns), "mitigations_count": len(mitigations)}
    )


def validate_failure_resilience(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that failure modes have resilience strategies."""
    resilience = data.get("resilience", {})

    score = 0.0
    issues = []

    failure_modes = resilience.get("failure_modes", [])
    if not failure_modes:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No failure modes analyzed"
        )

    # Failure modes have strategies
    with_strategies = sum(1 for fm in failure_modes if fm.get("strategy"))
    if with_strategies == len(failure_modes):
        score += 0.5
    elif with_strategies > 0:
        score += 0.3
        issues.append("Some failure modes lack resilience strategies")

    # Graceful degradation considered
    graceful_degradation = resilience.get("graceful_degradation")
    if graceful_degradation:
        score += 0.3
    else:
        issues.append("Graceful degradation not addressed")

    # Recovery mechanisms
    recovery = resilience.get("recovery_mechanisms")
    if recovery:
        score += 0.2

    passed = score >= threshold
    message = f"Failure resilience score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "failure_modes_count": len(failure_modes)}
    )


def validate_assumptions(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that assumptions were challenged."""
    assumptions = data.get("assumptions_review", {})

    score = 0.0
    issues = []

    assumptions_list = assumptions.get("assumptions", [])
    if not assumptions_list:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No assumptions were documented and challenged"
        )

    # Assumptions were challenged
    challenged = sum(1 for a in assumptions_list if a.get("challenge"))
    if challenged == len(assumptions_list):
        score += 0.5
    elif challenged > 0:
        score += 0.3
        issues.append("Some assumptions were not challenged")

    # Validated assumptions
    validated = sum(1 for a in assumptions_list if a.get("validated"))
    if validated > 0:
        score += 0.3

    # Invalid/wrong assumptions identified
    invalidated = sum(1 for a in assumptions_list if a.get("invalidated"))
    if invalidated > 0:
        score += 0.2

    passed = score >= threshold
    message = f"Assumption scrutiny score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "assumptions_count": len(assumptions_list), "challenged_count": challenged}
    )


# Gate 4 Validators

def validate_synthesis_coherence(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that the synthesis is coherent."""
    synthesis = data.get("synthesis", {})

    score = 0.0
    issues = []

    # Has core design
    core_design = synthesis.get("core_design")
    if core_design:
        score += 0.4
    else:
        issues.append("Core design not defined")

    # Components integrate properly
    components = synthesis.get("components", [])
    if components:
        # Check for integration points
        has_integration = any(c.get("integrations") for c in components)
        if has_integration:
            score += 0.3
        else:
            score += 0.1
            issues.append("Component integration not clear")
    else:
        issues.append("No components defined")

    # No contradictions
    contradictions = synthesis.get("identified_contradictions", [])
    unresolved = [c for c in contradictions if not c.get("resolved")]
    if not unresolved:
        score += 0.3
    else:
        issues.append(f"{len(unresolved)} unresolved contradictions")

    passed = score >= threshold
    message = f"Synthesis coherence score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "components_count": len(components), "unresolved_contradictions": len(unresolved)}
    )


def validate_tradeoffs(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that tradeoffs have clear rationale."""
    synthesis = data.get("synthesis", {})

    score = 0.0
    issues = []

    tradeoffs = synthesis.get("tradeoffs", [])
    if not tradeoffs:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "No tradeoffs documented"
        )

    # Tradeoffs have rationale
    with_rationale = sum(1 for t in tradeoffs if t.get("rationale"))
    if with_rationale == len(tradeoffs):
        score += 0.5
    elif with_rationale > 0:
        score += 0.3
        issues.append("Some tradeoffs lack rationale")

    # Tradeoffs document what was given up
    complete = sum(1 for t in tradeoffs if t.get("chosen") and t.get("rejected"))
    if complete == len(tradeoffs):
        score += 0.3
    elif complete > 0:
        score += 0.1

    # Impact assessment
    with_impact = sum(1 for t in tradeoffs if t.get("impact"))
    if with_impact > 0:
        score += 0.2

    passed = score >= threshold
    message = f"Tradeoffs score: {score:.2f} ({len(tradeoffs)} tradeoffs)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "tradeoffs_count": len(tradeoffs)}
    )


def validate_implementation_path(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that implementation path is clear."""
    synthesis = data.get("synthesis", {})

    score = 0.0
    issues = []

    # Has implementation steps
    steps = synthesis.get("implementation_steps", [])
    if steps:
        score += 0.4
    else:
        issues.append("No implementation steps defined")

    # Steps are ordered
    if steps and all(s.get("order") for s in steps):
        score += 0.3
    elif steps:
        issues.append("Implementation steps not clearly ordered")
        score += 0.1

    # Dependencies between steps identified
    if any(s.get("depends_on") for s in steps):
        score += 0.2

    # Milestones defined
    milestones = synthesis.get("milestones", [])
    if milestones:
        score += 0.1

    passed = score >= threshold
    message = f"Implementation path score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "steps_count": len(steps), "milestones_count": len(milestones)}
    )


def validate_constraints(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that all constraints are satisfied."""
    synthesis = data.get("synthesis", {})

    score = 0.0
    issues = []

    constraints = synthesis.get("constraints", [])
    all_constraints = data.get("context", {}).get("constraints", [])

    # All original constraints addressed
    addressed = sum(1 for c in all_constraints if any(
        sc.get("original") == c for sc in constraints
    ))
    if all_constraints and addressed == len(all_constraints):
        score += 0.5
    elif all_constraints:
        score += 0.2
        issues.append(f"{len(all_constraints) - addressed} constraints not addressed")

    # Constraints have satisfaction status
    with_status = sum(1 for c in constraints if c.get("satisfied") is not None)
    if with_status == len(constraints):
        score += 0.3
    elif constraints:
        score += 0.1

    # Unacceptable constraints documented
    unacceptable = [c for c in constraints if c.get("satisfied") is False]
    documented = sum(1 for c in unacceptable if c.get("reason"))
    if documented == len(unacceptable):
        score += 0.2

    passed = score >= threshold
    message = f"Constraints satisfaction score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "constraints_count": len(constraints)}
    )


# Gate 5 Validators

def validate_spec_completeness(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that specification is complete."""
    detailed_design = data.get("detailed_design", {})

    score = 0.0
    issues = []

    required_sections = [
        "overview",
        "interface",
        "implementation",
        "testing",
        "documentation"
    ]

    present_sections = [s for s in required_sections if detailed_design.get(s)]

    # All required sections present
    if len(present_sections) == len(required_sections):
        score += 0.5
    else:
        missing = set(required_sections) - set(present_sections)
        issues.append(f"Missing sections: {', '.join(missing)}")
        score += (len(present_sections) / len(required_sections)) * 0.5

    # Each section has content
    complete_sections = sum(
        1 for s in present_sections
        if detailed_design.get(s) and len(str(detailed_design.get(s))) > 50
    )
    if complete_sections == len(present_sections):
        score += 0.3
    elif complete_sections > 0:
        score += 0.15
        issues.append("Some sections lack sufficient content")

    # Version information present
    if detailed_design.get("version"):
        score += 0.2

    passed = score >= threshold
    message = f"Spec completeness score: {score:.2f} ({len(present_sections)}/{len(required_sections)} sections)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "present_sections": present_sections, "missing_sections": list(set(required_sections) - set(present_sections))}
    )


def validate_api_contracts(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that API contracts are fully specified."""
    detailed_design = data.get("detailed_design", {})
    interface = detailed_design.get("interface", {})

    score = 0.0
    issues = []

    # Has API definition
    api = interface.get("api")
    if not api:
        return _create_validation_result(
            spec, data, threshold, False, 0.0,
            "API contracts not defined"
        )

    # Functions/methods specified
    functions = api.get("functions", api.get("methods", []))
    if functions:
        score += 0.3
    else:
        issues.append("No functions/methods defined")

    # Each function has signature
    with_signature = sum(1 for f in functions if f.get("signature") or f.get("parameters"))
    if functions and with_signature == len(functions):
        score += 0.3
    elif functions:
        score += 0.1
        issues.append("Some functions lack complete signatures")

    # Return types specified
    with_returns = sum(1 for f in functions if f.get("return_type") or f.get("returns"))
    if with_returns == len(functions):
        score += 0.2

    # Error cases specified
    with_errors = sum(1 for f in functions if f.get("errors") or f.get("exceptions"))
    if with_errors == len(functions):
        score += 0.2
    elif with_errors > 0:
        score += 0.1
        issues.append("Some functions lack error specifications")

    passed = score >= threshold
    message = f"API contracts score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "functions_count": len(functions)}
    )


def validate_error_handling(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that error cases are fully specified."""
    detailed_design = data.get("detailed_design", {})

    score = 0.0
    issues = []

    error_handling = detailed_design.get("error_handling", {})

    # Error types defined
    error_types = error_handling.get("error_types", [])
    if error_types:
        score += 0.4
    else:
        issues.append("No error types defined")

    # Error handling strategies
    strategies = error_handling.get("strategies", {})
    if strategies:
        score += 0.3
    else:
        issues.append("No error handling strategies specified")

    # Recovery procedures
    recovery = error_handling.get("recovery")
    if recovery:
        score += 0.3

    passed = score >= threshold
    message = f"Error handling score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "error_types_count": len(error_types)}
    )


def validate_testing_strategy(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that testing strategy is comprehensive."""
    detailed_design = data.get("detailed_design", {})
    testing = detailed_design.get("testing", {})

    score = 0.0
    issues = []

    # Test types defined
    test_types = testing.get("test_types", [])
    required_types = ["unit", "integration"]
    present_types = [t for t in required_types if any(
        tt.get("type") == t or t in str(tt).lower() for tt in test_types
    )]

    if len(present_types) == len(required_types):
        score += 0.4
    else:
        missing = set(required_types) - set(present_types)
        issues.append(f"Missing test types: {', '.join(missing)}")
        score += 0.2

    # Test coverage targets
    coverage = testing.get("coverage")
    if coverage:
        score += 0.3
    else:
        issues.append("No test coverage targets specified")

    # Test data strategy
    test_data = testing.get("test_data")
    if test_data:
        score += 0.3

    passed = score >= threshold
    message = f"Testing strategy score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "test_types_count": len(test_types)}
    )


def validate_documentation(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that documentation requirements are met."""
    detailed_design = data.get("detailed_design", {})
    documentation = detailed_design.get("documentation", {})

    score = 0.0
    issues = []

    # User docs planned
    user_docs = documentation.get("user")
    if user_docs:
        score += 0.3
    else:
        issues.append("User documentation not planned")

    # Developer docs planned
    dev_docs = documentation.get("developer")
    if dev_docs:
        score += 0.3
    else:
        issues.append("Developer documentation not planned")

    # API docs planned
    api_docs = documentation.get("api")
    if api_docs:
        score += 0.2

    # Examples planned
    examples = documentation.get("examples")
    if examples:
        score += 0.2

    passed = score >= threshold
    message = f"Documentation score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues}
    )


# Gate 6 Validators

def validate_package_integrity(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that package structure and metadata are valid."""
    package = data.get("package", {})

    score = 0.0
    issues = []

    # Package structure valid
    structure = package.get("structure")
    if structure:
        score += 0.3
    else:
        issues.append("Package structure not defined")

    # Metadata complete
    metadata = package.get("metadata", {})
    required_metadata = ["name", "version", "description"]
    present_metadata = [m for m in required_metadata if metadata.get(m)]

    if len(present_metadata) == len(required_metadata):
        score += 0.4
    else:
        missing = set(required_metadata) - set(present_metadata)
        issues.append(f"Missing metadata: {', '.join(missing)}")
        score += 0.2

    # Manifest valid
    manifest = package.get("manifest")
    if manifest:
        score += 0.3

    passed = score >= threshold
    message = f"Package integrity score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "missing_metadata": list(set(required_metadata) - set(present_metadata))}
    )


def validate_tests(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that all tests pass with required coverage."""
    package = data.get("package", {})
    tests = package.get("tests", {})

    score = 0.0
    issues = []

    # Tests exist
    test_count = tests.get("count", 0)
    if test_count > 0:
        score += 0.3
    else:
        issues.append("No tests found")
        return _create_validation_result(
            spec, data, threshold, False, score,
            f"Tests score: {score:.2f}. No tests found",
            {"issues": issues}
        )

    # All tests passing
    passing = tests.get("passing", test_count)
    if passing == test_count:
        score += 0.4
    else:
        issues.append(f"{test_count - passing} tests failing")
        score += 0.1

    # Coverage meets threshold
    coverage = tests.get("coverage", 0.0)
    min_coverage = 0.8
    if coverage >= min_coverage:
        score += 0.3
    else:
        issues.append(f"Coverage {coverage:.1%} below {min_coverage:.1%}")
        score += 0.1

    passed = score >= threshold
    message = f"Tests score: {score:.2f} ({passing}/{test_count} passing, {coverage:.1%} coverage)" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "test_count": test_count, "passing": passing, "coverage": coverage}
    )


def validate_dependencies_resolved(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that all dependencies are resolved and compatible."""
    package = data.get("package", {})
    dependencies = package.get("dependencies", {})

    score = 0.0
    issues = []

    # All dependencies resolved
    resolved = dependencies.get("resolved", [])
    unresolved = dependencies.get("unresolved", [])

    if not unresolved:
        score += 0.5
    else:
        issues.append(f"{len(unresolved)} unresolved dependencies")
        score += 0.2

    # No conflicts
    conflicts = dependencies.get("conflicts", [])
    if not conflicts:
        score += 0.3
    else:
        issues.append(f"{len(conflicts)} dependency conflicts")
        score += 0.1

    # Versions locked
    locked = dependencies.get("locked")
    if locked:
        score += 0.2

    passed = score >= threshold
    message = f"Dependencies score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "unresolved_count": len(unresolved), "conflicts_count": len(conflicts)}
    )


def validate_security(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that security and vulnerability checks pass."""
    package = data.get("package", {})
    security = package.get("security", {})

    score = 0.0
    issues = []

    # No vulnerabilities
    vulnerabilities = security.get("vulnerabilities", [])
    critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
    high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]

    if not critical_vulns and not high_vulns:
        score += 0.5
    else:
        issues.append(f"{len(critical_vulns)} critical, {len(high_vulns)} high severity vulnerabilities")
        return _create_validation_result(
            spec, data, threshold, False, score,
            f"Security score: {score:.2f}. Critical/high vulnerabilities found",
            {"issues": issues, "critical_vulns": len(critical_vulns), "high_vulns": len(high_vulns)}
        )

    # Security scan passed
    scan_passed = security.get("scan_passed", True)
    if scan_passed:
        score += 0.3
    else:
        issues.append("Security scan failed")

    # No sensitive data exposure
    no_exposure = security.get("no_exposure", True)
    if no_exposure:
        score += 0.2

    passed = score >= threshold
    message = f"Security score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "vulnerabilities_count": len(vulnerabilities)}
    )


def validate_documentation_deployable(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that documentation is deployable."""
    package = data.get("package", {})
    documentation = package.get("documentation", {})

    score = 0.0
    issues = []

    # Documentation generated
    generated = documentation.get("generated")
    if generated:
        score += 0.5
    else:
        issues.append("Documentation not generated")

    # All docs present
    required_docs = ["readme", "api"]
    present_docs = [d for d in required_docs if documentation.get(d)]

    if len(present_docs) == len(required_docs):
        score += 0.3
    else:
        missing = set(required_docs) - set(present_docs)
        issues.append(f"Missing docs: {', '.join(missing)}")
        score += 0.1

    # Examples working
    examples = documentation.get("examples_working")
    if examples:
        score += 0.2

    passed = score >= threshold
    message = f"Documentation deployable score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues, "missing_docs": list(set(required_docs) - set(present_docs))}
    )


def validate_performance(
    spec: Dict[str, Any],
    data: Dict[str, Any],
    threshold: float
) -> ValidationResult:
    """Validate that performance meets baseline requirements."""
    package = data.get("package", {})
    performance = package.get("performance", {})

    score = 0.0
    issues = []

    # Baseline tests run
    baseline_run = performance.get("baseline_run")
    if baseline_run:
        score += 0.3
    else:
        issues.append("Performance baseline not established")

    # Meets requirements
    meets_requirements = performance.get("meets_requirements", True)
    if meets_requirements:
        score += 0.4
    else:
        issues.append("Performance does not meet requirements")
        score += 0.1

    # No regressions
    no_regressions = performance.get("no_regressions", True)
    if no_regressions:
        score += 0.3

    passed = score >= threshold
    message = f"Performance score: {score:.2f}" + (
        f". Issues: {', '.join(issues)}" if issues else ""
    )

    return _create_validation_result(
        spec, data, threshold, passed, score, message,
        {"issues": issues}
    )


# Registry of all built-in validators
BUILT_IN_VALIDATORS: Dict[str, Callable] = {
    # Gate 1
    "validate_intent_clarity": validate_intent_clarity,
    "validate_scope_bounded": validate_scope_bounded,
    "validate_domain_feasibility": validate_domain_feasibility,
    "validate_dependencies": validate_dependencies,

    # Gate 2
    "validate_perspective_coverage": validate_perspective_coverage,
    "validate_alternatives": validate_alternatives,
    "validate_edge_cases": validate_edge_cases,
    "validate_context": validate_context,

    # Gate 3
    "validate_adversarial_challenges": validate_adversarial_challenges,
    "validate_security_review": validate_security_review,
    "validate_failure_resilience": validate_failure_resilience,
    "validate_assumptions": validate_assumptions,

    # Gate 4
    "validate_synthesis_coherence": validate_synthesis_coherence,
    "validate_tradeoffs": validate_tradeoffs,
    "validate_implementation_path": validate_implementation_path,
    "validate_constraints": validate_constraints,

    # Gate 5
    "validate_spec_completeness": validate_spec_completeness,
    "validate_api_contracts": validate_api_contracts,
    "validate_error_handling": validate_error_handling,
    "validate_testing_strategy": validate_testing_strategy,
    "validate_documentation": validate_documentation,

    # Gate 6
    "validate_package_integrity": validate_package_integrity,
    "validate_tests": validate_tests,
    "validate_dependencies_resolved": validate_dependencies_resolved,
    "validate_security": validate_security,
    "validate_documentation_deployable": validate_documentation_deployable,
    "validate_performance": validate_performance,
}


# =============================================================================
# Error Communication Templates
# =============================================================================

ERROR_TEMPLATES = {
    "gate_failed": """
Gate Validation Failed: {gate_name}

{description}

Validations:
{validation_summary}

Overall Score: {score:.2f} / Required: {threshold:.2f}

Action: {action}

Next Steps:
{next_steps}
""",

    "circuit_breaker_open": """
Circuit Breaker Open: {gate_name}

The gate '{gate_name}' has failed {failure_count} times and the circuit breaker
has opened to prevent cascading failures.

Please wait {recovery_time} seconds before attempting again, or manually reset
the circuit breaker if issues have been resolved.
""",

    "escalation_required": """
ESCALATION REQUIRED: {gate_name}

{description}

The gate '{gate_name}' requires human review due to:
{failure_reason}

Escalation Details:
- Gate: {gate_name}
- Phase: {phase}
- Timestamp: {timestamp}
- Retry Attempts: {retry_count}

Please review and provide guidance before proceeding.
""",

    "retry_scheduled": """
Retry Scheduled: {gate_name}

Validation failed for gate '{gate_name}'. A retry has been scheduled.

Retry Details:
- Attempt: {attempt} of {max_retries}
- Delay: {delay:.1f} seconds
- Policy: {policy}

Please address the identified issues before the retry:
{issues}
""",

    "rollback_initiated": """
Rollback Initiated: {gate_name}

Due to validation failure at gate '{gate_name}', a rollback to the previous
phase is being initiated.

Rollback Details:
- From Phase: {current_phase}
- To Phase: {rollback_phase}
- Reason: {reason}

Please review and fix the issues before re-running the affected phases.
"""
}


def format_error(template_name: str, **kwargs) -> str:
    """Format an error template with the provided context."""
    template = ERROR_TEMPLATES.get(template_name)
    if not template:
        return f"Unknown error template: {template_name}"

    return template.format(**kwargs)


# =============================================================================
# Utility Functions
# =============================================================================

def create_validation_gate(
    custom_gates: Optional[Dict[str, GateSpec]] = None,
    custom_validators: Optional[Dict[str, Callable]] = None
) -> ValidationGate:
    """
    Factory function to create a ValidationGate instance.

    Args:
        custom_gates: Optional custom gate specifications
        custom_validators: Optional custom validator functions

    Returns:
        Configured ValidationGate instance
    """
    circuit_breaker = CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=60.0
    )
    return ValidationGate(
        gates=custom_gates,
        circuit_breaker=circuit_breaker,
        custom_validators=custom_validators
    )


def run_gate_sequence(
    data_by_phase: Dict[Phase, Dict[str, Any]],
    gate: Optional[ValidationGate] = None
) -> List[GateResult]:
    """
    Run all gates in sequence for a complete workflow.

    Args:
        data_by_phase: Dictionary mapping phases to their output data
        gate: Optional ValidationGate instance (creates default if None)

    Returns:
        List of gate results in order
    """
    if gate is None:
        gate = create_validation_gate()

    results = []
    gate_order = [
        Phase.INTENT_GATHERING,
        Phase.PARALLEL_EXPLORATION,
        Phase.ADVERSARIAL_REVIEW,
        Phase.SYNTHESIS,
        Phase.DETAILED_DESIGN,
        Phase.PACKAGE_VALIDATE
    ]

    for phase in gate_order:
        if phase not in data_by_phase:
            logger.warning(f"No data provided for phase: {phase.value}")
            continue

        result = gate.validate(phase, data_by_phase[phase])
        results.append(result)

        # Stop if gate failed and action is HALT
        if not result.passed and result.action_taken == FailAction.HALT:
            logger.info(f"Workflow halted at gate: {result.gate_name}")
            break

    return results


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Validation Gates System for Supercharged Skill Creator")
    print("=" * 60)

    # Create a validation gate
    gate = create_validation_gate()

    # Example data for Gate 1
    example_intent_data = {
        "intent": "Create a skill that analyzes text sentiment",
        "scope": {
            "in_scope": ["sentiment analysis", "text classification"],
            "out_of_scope": ["entity recognition", "translation"]
        },
        "domain": {
            "name": "NLP",
            "expertise": {"available": True},
            "knowledge_sources": ["documentation", "examples"]
        },
        "dependencies": {
            "tools": ["python", "nltk"],
            "libraries": ["transformers"]
        }
    }

    # Run Gate 1
    result = gate.validate(Phase.INTENT_GATHERING, example_intent_data)

    print(f"\nGate: {result.gate_name}")
    print(f"Status: {result.status.value}")
    print(f"Passed: {result.passed}")
    print(f"Overall Score: {result.overall_score:.2f}")

    print("\nValidations:")
    for v in result.validations:
        print(f"  - {v.check_name}: {v.score:.2f} - {v.message}")

    if not result.passed:
        action = gate.fail(result.action_taken, result)
        print(f"\nAction: {action['action']}")
        print(f"Message: {action['message']}")
