"""
Conflict Resolver

Handles conflicts when multiple agents or operations attempt to access
or modify the same resources. Provides multiple resolution strategies
including retry, overwrite, merge, skip, fail, and fallback behaviors.

Example:
    ```python
    from conflict_resolver import (
        ConflictResolver,
        ResolutionStrategy,
        Conflict,
        resolve_with_retry,
    )

    resolver = ConflictResolver(default_strategy=ResolutionStrategy.MERGE)

    @resolver.protect()
    def update_document(doc_id: str, changes: dict):
        # Conflict detection and resolution happens automatically
        return docs.update(doc_id, changes)

    # Or handle conflicts explicitly
    try:
        result = operation()
    except Conflict as e:
        result = e.resolve(strategy=ResolutionStrategy.RETRY)
    ```

Resolution Strategies:
    - RETRY: Retry the operation with exponential backoff
    - OVERWRITE: Force the operation, discarding conflicting changes
    - MERGE: Attempt to merge conflicting changes intelligently
    - SKIP: Skip this operation, leaving existing state unchanged
    - FAIL: Raise an exception, failing the operation
    - FALLBACK: Execute an alternative fallback operation
"""

from __future__ import annotations

import asyncio
import functools
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, ParamSpec, TypeVar

# Type variables
P = ParamSpec("P")
R = TypeVar("R")


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    RETRY = auto()        # Retry with backoff
    OVERWRITE = auto()    # Force through, discard conflicts
    MERGE = auto()        # Intelligently merge changes
    SKIP = auto()         # Skip operation, keep existing
    FAIL = auto()         # Raise exception
    FALLBACK = auto()     # Execute alternative


class ConflictType(Enum):
    """Types of conflicts that can occur."""

    VERSION_CONFLICT = auto()     # Optimistic locking version mismatch
    WRITE_CONFLICT = auto()       # Concurrent write to same resource
    RESOURCE_LOCKED = auto()      # Resource is locked by another operation
    STATE_MISMATCH = auto()       # Expected state doesn't match actual
    VALIDATION_CONFLICT = auto()  # Validation fails due to external changes
    SCHEMA_CONFLICT = auto()      # Schema/schema version mismatch


@dataclass
class Conflict:
    """Represents a conflict that occurred during an operation.

    Attributes:
        conflict_type: Type of conflict
        resource: Resource the conflict occurred on
        current_state: Current state of the resource
        attempted_state: State that was attempted
        message: Human-readable conflict description
        timestamp: When the conflict occurred
        metadata: Additional conflict information
    """

    conflict_type: ConflictType
    resource: str
    current_state: dict[str, Any] | None
    attempted_state: dict[str, Any] | None
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def resolve(
        self,
        strategy: ResolutionStrategy,
        **kwargs: Any,
    ) -> Any:
        """Resolve the conflict using the specified strategy.

        Args:
            strategy: Resolution strategy to apply
            **kwargs: Strategy-specific parameters

        Returns:
            Result of conflict resolution
        """
        resolver = ConflictResolver()
        return resolver.resolve(self, strategy, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert conflict to dictionary."""
        return {
            "conflict_type": self.conflict_type.name,
            "resource": self.resource,
            "current_state": self.current_state,
            "attempted_state": self.attempted_state,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConflictError(Exception):
    """Raised when a conflict cannot be resolved.

    Attributes:
        conflict: The conflict that caused the error
        strategy: The strategy that was attempted
    """

    def __init__(self, conflict: Conflict, strategy: ResolutionStrategy) -> None:
        self.conflict = conflict
        self.strategy = strategy
        super().__init__(
            f"Conflict on '{conflict.resource}' using {strategy.name}: {conflict.message}"
        )


@dataclass
class ResolutionResult:
    """Result of a conflict resolution attempt.

    Attributes:
        strategy_used: The strategy that was applied
        success: Whether resolution was successful
        resolved_state: The final state after resolution
        attempts: Number of resolution attempts made
        fallback_used: Whether fallback was executed
    """

    strategy_used: ResolutionStrategy
    success: bool
    resolved_state: dict[str, Any] | None
    attempts: int
    fallback_used: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "strategy_used": self.strategy_used.name,
            "success": self.success,
            "resolved_state": self.resolved_state,
            "attempts": self.attempts,
            "fallback_used": self.fallback_used,
            "error": self.error,
        }


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        exponential: bool = True,
        jitter: bool = True,
    ) -> None:
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries
            exponential: Use exponential backoff
            jitter: Add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt."""
        import random

        if self.exponential:
            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        else:
            delay = self.base_delay

        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class MergeStrategy:
    """Strategies for merging conflicting states."""

    @staticmethod
    def last_write_wins(current: dict[str, Any], attempted: dict[str, Any]) -> dict[str, Any]:
        """Simple last-write-wins merge."""
        result = current.copy()
        result.update(attempted)
        return result

    @staticmethod
    def first_write_wins(current: dict[str, Any], attempted: dict[str, Any]) -> dict[str, Any]:
        """First-write-wins (current has priority)."""
        return current.copy()

    @staticmethod
    def deep_merge(current: dict[str, Any], attempted: dict[str, Any]) -> dict[str, Any]:
        """Deep merge for nested dictionaries."""
        result = current.copy()

        for key, value in attempted.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = MergeStrategy.deep_merge(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    @staticmethod
    def array_merge(
        current: dict[str, Any],
        attempted: dict[str, Any],
        dedupe: bool = True,
    ) -> dict[str, Any]:
        """Merge arrays/lists by concatenation."""
        result = current.copy()

        for key, value in attempted.items():
            if key in result and isinstance(result[key], list) and isinstance(value, list):
                combined = result[key] + value
                if dedupe:
                    seen = set()
                    unique = []
                    for item in combined:
                        item_hash = str(item)
                        if item_hash not in seen:
                            seen.add(item_hash)
                            unique.append(item)
                    result[key] = unique
                else:
                    result[key] = combined
            else:
                result[key] = value

        return result


class ConflictResolver:
    """Main conflict resolution handler.

    Provides methods to detect, prevent, and resolve conflicts in
    concurrent operations.

    Example:
        ```python
        resolver = ConflictResolver(default_strategy=ResolutionStrategy.MERGE)

        @resolver.protect(resource=lambda args: args[0])
        def update_data(key: str, value: Any):
            data[key] = value
        ```
    """

    def __init__(
        self,
        default_strategy: ResolutionStrategy = ResolutionStrategy.FAIL,
        retry_config: RetryConfig | None = None,
        merge_func: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the conflict resolver.

        Args:
            default_strategy: Default strategy for unconfigured conflicts
            retry_config: Configuration for retry strategy
            merge_func: Custom merge function for MERGE strategy
        """
        self.default_strategy = default_strategy
        self.retry_config = retry_config or RetryConfig()
        self.merge_func = merge_func or MergeStrategy.deep_merge
        self._lock_table: dict[str, str] = {}  # resource -> operation_id

    def detect_conflict(
        self,
        resource: str,
        expected_state: dict[str, Any] | None,
        actual_state: dict[str, Any],
    ) -> Conflict | None:
        """Detect if a conflict exists for a resource.

        Args:
            resource: Resource identifier
            expected_state: Expected state (version, etag, etc.)
            actual_state: Actual current state

        Returns:
            Conflict object if conflict detected, None otherwise
        """
        # Check version conflict
        if expected_state and actual_state:
            expected_version = expected_state.get("version")
            actual_version = actual_state.get("version")
            if expected_version and actual_version and expected_version != actual_version:
                return Conflict(
                    conflict_type=ConflictType.VERSION_CONFLICT,
                    resource=resource,
                    current_state=actual_state,
                    attempted_state=expected_state,
                    message=f"Version mismatch: expected {expected_version}, got {actual_version}",
                )

        # Check if resource is locked
        if resource in self._lock_table:
            return Conflict(
                conflict_type=ConflictType.RESOURCE_LOCKED,
                resource=resource,
                current_state=actual_state,
                attempted_state=expected_state,
                message=f"Resource locked by operation {self._lock_table[resource]}",
            )

        return None

    def acquire_lock(self, resource: str, operation_id: str) -> bool:
        """Attempt to acquire a lock on a resource.

        Args:
            resource: Resource identifier
            operation_id: Unique operation identifier

        Returns:
            True if lock acquired, False if already locked
        """
        if resource in self._lock_table:
            return False
        self._lock_table[resource] = operation_id
        return True

    def release_lock(self, resource: str, operation_id: str) -> bool:
        """Release a lock on a resource.

        Args:
            resource: Resource identifier
            operation_id: Operation identifier that holds the lock

        Returns:
            True if lock was released, False if not the lock holder
        """
        if self._lock_table.get(resource) == operation_id:
            del self._lock_table[resource]
            return True
        return False

    def resolve(
        self,
        conflict: Conflict,
        strategy: ResolutionStrategy,
        **kwargs: Any,
    ) -> ResolutionResult:
        """Resolve a conflict using the specified strategy.

        Args:
            conflict: The conflict to resolve
            strategy: Resolution strategy to use
            **kwargs: Strategy-specific parameters

        Returns:
            ResolutionResult with outcome
        """
        attempts = 0

        if strategy == ResolutionStrategy.RETRY:
            return self._retry_resolve(conflict, **kwargs)

        elif strategy == ResolutionStrategy.OVERWRITE:
            return ResolutionResult(
                strategy_used=strategy,
                success=True,
                resolved_state=conflict.attempted_state,
                attempts=1,
            )

        elif strategy == ResolutionStrategy.MERGE:
            if conflict.current_state and conflict.attempted_state:
                merged = self.merge_func(conflict.current_state, conflict.attempted_state)
                return ResolutionResult(
                    strategy_used=strategy,
                    success=True,
                    resolved_state=merged,
                    attempts=1,
                )
            return ResolutionResult(
                strategy_used=strategy,
                success=False,
                resolved_state=conflict.current_state,
                attempts=1,
                error="Cannot merge: missing state information",
            )

        elif strategy == ResolutionStrategy.SKIP:
            return ResolutionResult(
                strategy_used=strategy,
                success=True,
                resolved_state=conflict.current_state,
                attempts=1,
            )

        elif strategy == ResolutionStrategy.FAIL:
            raise ConflictError(conflict, strategy)

        elif strategy == ResolutionStrategy.FALLBACK:
            fallback_func = kwargs.get("fallback")
            if fallback_func:
                try:
                    result = fallback_func(conflict)
                    return ResolutionResult(
                        strategy_used=strategy,
                        success=True,
                        resolved_state=result,
                        attempts=1,
                        fallback_used=True,
                    )
                except Exception as e:
                    return ResolutionResult(
                        strategy_used=strategy,
                        success=False,
                        resolved_state=conflict.current_state,
                        attempts=1,
                        fallback_used=True,
                        error=str(e),
                    )
            return ResolutionResult(
                strategy_used=strategy,
                success=False,
                resolved_state=conflict.current_state,
                attempts=1,
                error="No fallback function provided",
            )

        else:
            # Use default strategy
            return self.resolve(conflict, self.default_strategy, **kwargs)

    def _retry_resolve(
        self,
        conflict: Conflict,
        retry_func: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> ResolutionResult:
        """Resolve conflict using retry strategy."""
        max_attempts = kwargs.get("max_attempts", self.retry_config.max_attempts)

        for attempt in range(max_attempts):
            attempts = attempt + 1
            delay = self.retry_config.get_delay(attempt)

            time.sleep(delay)

            # Try to acquire lock if resource-based
            if conflict.resource:
                op_id = kwargs.get("operation_id", f"retry_{attempt}")
                if self.acquire_lock(conflict.resource, op_id):
                    return ResolutionResult(
                        strategy_used=ResolutionStrategy.RETRY,
                        success=True,
                        resolved_state=conflict.attempted_state,
                        attempts=attempts,
                    )

        return ResolutionResult(
            strategy_used=ResolutionStrategy.RETRY,
            success=False,
            resolved_state=conflict.current_state,
            attempts=max_attempts,
            error="Max retry attempts exceeded",
        )

    def protect(
        self,
        resource: Callable[..., str] | str | None = None,
        strategy: ResolutionStrategy | None = None,
        **strategy_kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator to add conflict protection to a function.

        Args:
            resource: Resource identifier or function to extract it from args
            strategy: Conflict resolution strategy
            **strategy_kwargs: Additional strategy parameters

        Returns:
            Decorated function with conflict protection

        Example:
            ```python
            @resolver.protect(resource=lambda args: f"user:{args[0]}")
            def update_user(user_id: str, data: dict):
                db.users.update(user_id, data)
            ```
        """
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Determine resource
                if callable(resource):
                    resource_id = resource(*args, **kwargs)
                elif isinstance(resource, str):
                    resource_id = resource
                else:
                    resource_id = f"{func.__name__}"

                # Attempt to acquire lock
                op_id = f"{func.__name__}_{time.time()}"
                if not self.acquire_lock(resource_id, op_id):
                    # Conflict detected
                    conflict = Conflict(
                        conflict_type=ConflictType.RESOURCE_LOCKED,
                        resource=resource_id,
                        current_state=None,
                        attempted_state=None,
                        message=f"Resource locked during {func.__name__}",
                    )

                    resolution_strategy = strategy or self.default_strategy
                    result = self.resolve(conflict, resolution_strategy, **strategy_kwargs)

                    if not result.success:
                        raise ConflictError(conflict, resolution_strategy)

                    # If SKIP was used, return early
                    if resolution_strategy == ResolutionStrategy.SKIP:
                        return None  # type: ignore[return-value]

                try:
                    return func(*args, **kwargs)
                finally:
                    self.release_lock(resource_id, op_id)

            return wrapper

        return decorator


def resolve_with_retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    exponential: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add retry-based conflict resolution.

    Example:
        ```python
        @resolve_with_retry(max_attempts=5)
        def update_record(id: str, data: dict):
            return db.update(id, data)
        ```
    """
    resolver = ConflictResolver(
        default_strategy=ResolutionStrategy.RETRY,
        retry_config=RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            exponential=exponential,
        ),
    )
    return resolver.protect(strategy=ResolutionStrategy.RETRY)


def merge_dicts(current: dict[str, Any], attempted: dict[str, Any]) -> dict[str, Any]:
    """Helper function to merge two dictionaries."""
    return MergeStrategy.deep_merge(current, attempted)


def retry_operation(
    func: Callable[P, R],
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[P, R]:
    """Retry an operation on failure with exponential backoff.

    Example:
        ```python
        result = retry_operation(lambda: api_call(), max_attempts=5)
        ```
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        config = RetryConfig(max_attempts=max_attempts)
        last_exception = None

        for attempt in range(config.max_attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < config.max_attempts - 1:
                    delay = config.get_delay(attempt)
                    time.sleep(delay)

        raise last_exception  # type: ignore[misc]

    return wrapper


__all__ = [
    "ResolutionStrategy",
    "ConflictType",
    "Conflict",
    "ConflictError",
    "ResolutionResult",
    "RetryConfig",
    "MergeStrategy",
    "ConflictResolver",
    # Helper functions
    "resolve_with_retry",
    "merge_dicts",
    "retry_operation",
]
