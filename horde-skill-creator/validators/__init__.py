"""
Validation Components for Supercharged Skill Creator

This package provides 7 core validation components that are auto-included
in every generated skill to ensure robustness and reliability.

Components:
    1. timeout_handler - Timeout enforcement for operations
    2. schema_validator - Runtime type validation
    3. capability_checker - MCP server and dependency availability
    4. circuit_breaker - Failure cascade prevention
    5. preflight - Pre-operation confirmation prompts
    6. conflict_resolver - Concurrent operation conflict handling
    7. degradation - Graceful degradation when services fail

Example:
    ```python
    from validators import (
        with_timeout,
        TimeoutType,
        validate,
        CapabilityChecker,
        CircuitBreaker,
        preflight_check,
        OperationRisk,
        ConflictResolver,
        with_fallbacks,
    )

    # Combine multiple validators
    checker = CapabilityChecker()
    breaker = CircuitBreaker("api", failure_threshold=5)

    @with_timeout(TimeoutType.MEDIUM)
    @validate
    @preflight_check(risk=OperationRisk.HIGH)
    @breaker.protect
    def critical_operation(data: dict) -> dict:
        return process(data)
    ```
"""

from .timeout_handler import (
    DEFAULT_TIMEOUTS,
    SkillTimeoutError,
    TimeoutConfig,
    TimeoutManager,
    TimeoutStats,
    TimeoutType,
    clear_stats,
    get_all_stats,
    get_stats,
    timeout_context,
    with_timeout,
)

from .schema_validator import (
    ValidationError,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    SchemaBuilder,
    TypeValidator,
    validate,
    validate_email,
    validate_length,
    validate_pattern,
    validate_range,
    validate_schema,
    validate_url,
    validate_uuid,
    validate_value,
)

from .capability_checker import (
    CapabilityBreakerOpen,
    CapabilityChecker,
    CapabilityReport,
    CapabilityResult,
    CapabilityStatus,
    DegradationLevel,
    ResourceType,
    check_env_var,
    check_file_exists,
    check_mcp_server,
    check_package_installed,
)

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerOpen,
    CircuitBreakerStats,
    CircuitState,
    circuit_breaker,
    get_breaker,
)

from .preflight import (
    ConfirmationPrompt,
    ConfirmationResult,
    OperationCategory,
    OperationMetadata,
    OperationRisk,
    PreflightChecker,
    confirm_before_execute,
    preflight_check,
)

from .conflict_resolver import (
    Conflict,
    ConflictError,
    ConflictResolver,
    ConflictType,
    MergeStrategy,
    ResolutionResult,
    ResolutionStrategy,
    RetryConfig,
    merge_dicts,
    resolve_with_retry,
    retry_operation,
)

from .degradation import (
    CachedFallback,
    Degrade,
    DegradationEvent,
    DegradationLevel,
    DegradationManager,
    DegradationStrategy,
    FallbackResult,
    FunctionFallback,
    StaticFallback,
    cached_result,
    degrade_gracefully,
    get_manager,
    with_fallbacks,
)

__all__ = [
    # timeout_handler
    "TimeoutType",
    "SkillTimeoutError",
    "TimeoutConfig",
    "TimeoutStats",
    "TimeoutManager",
    "with_timeout",
    "timeout_context",
    "get_stats",
    "get_all_stats",
    "clear_stats",
    "DEFAULT_TIMEOUTS",
    # schema_validator
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationError",
    "ValidationResult",
    "TypeValidator",
    "validate",
    "validate_schema",
    "validate_value",
    "SchemaBuilder",
    "validate_email",
    "validate_url",
    "validate_uuid",
    "validate_range",
    "validate_length",
    "validate_pattern",
    # capability_checker
    "CapabilityStatus",
    "DegradationLevel",
    "ResourceType",
    "CapabilityResult",
    "CapabilityReport",
    "CapabilityChecker",
    "check_mcp_server",
    "check_env_var",
    "check_file_exists",
    "check_package_installed",
    # circuit_breaker
    "CircuitState",
    "CircuitBreakerError",
    "CircuitBreakerOpen",
    "CircuitBreakerStats",
    "CircuitBreaker",
    "circuit_breaker",
    "get_breaker",
    # preflight
    "OperationRisk",
    "OperationCategory",
    "OperationMetadata",
    "ConfirmationResult",
    "ConfirmationPrompt",
    "PreflightChecker",
    "preflight_check",
    "confirm_before_execute",
    # conflict_resolver
    "ResolutionStrategy",
    "ConflictType",
    "Conflict",
    "ConflictError",
    "ResolutionResult",
    "RetryConfig",
    "MergeStrategy",
    "ConflictResolver",
    "resolve_with_retry",
    "merge_dicts",
    "retry_operation",
    # degradation
    "DegradationLevel",
    "FallbackResult",
    "DegradationEvent",
    "DegradationStrategy",
    "FunctionFallback",
    "CachedFallback",
    "StaticFallback",
    "DegradationManager",
    "Degrade",
    "with_fallbacks",
    "degrade_gracefully",
    "cached_result",
    "get_manager",
]

__version__ = "1.0.0"
