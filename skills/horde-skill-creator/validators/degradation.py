"""
Graceful Degradation

Manages degradation levels for skills when dependencies are unavailable
or operations fail. Enables skills to continue operating at reduced
capacity instead of failing completely.

Example:
    ```python
    from degradation import (
        DegradationLevel,
        Degrade,
        degrade_gracefully,
        with_fallbacks,
        DegradationManager,
    )

    @with_fallbacks([
        lambda: primary_api(),
        lambda: cache.get_result(),
        lambda: default_response(),
    ])
    def get_data():
        return primary_api()

    # Or use degradation levels
    @degrade_gracefully(level=DegradationLevel.DEGRADED)
    def process_data(data):
        # Will attempt degraded mode if primary fails
        return complex_processing(data)
    ```

Degradation Levels:
    - FULL: All capabilities available, normal operation
    - DEGRADED: Some capabilities limited, reduced functionality
    - MINIMAL: Core functionality only, basic operations
    - OFFLINE: Cannot operate, cached/offline responses only
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, ParamSpec, TypeVar
from functools import wraps

# Type variables
P = ParamSpec("P")
R = TypeVar("R")

# Set up logging
logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """Levels of service degradation.

    FULL: All features available
        - Primary data sources
        - All optional features
        - Normal performance

    DEGRADED: Reduced functionality
        - Fallback data sources
        - Non-critical features disabled
        - Slower but acceptable performance

    MINIMAL: Core functionality only
        - Cached/offline data
        - Essential features only
        - Minimal performance expectations

    OFFLINE: No live service
        - Pre-cached responses only
        - Static/configured responses
        - No external dependencies
    """

    FULL = auto()
    DEGRADED = auto()
    MINIMAL = auto()
    OFFLINE = auto()


class FallbackResult:
    """Result from a fallback attempt.

    Attributes:
        success: Whether the fallback succeeded
        value: The returned value (if successful)
        error: Exception that occurred (if failed)
        level: Degradation level of this fallback
        fallback_index: Which fallback was used
    """

    def __init__(
        self,
        success: bool,
        value: Any = None,
        error: Exception | None = None,
        level: DegradationLevel = DegradationLevel.FULL,
        fallback_index: int = 0,
    ) -> None:
        self.success = success
        self.value = value
        self.error = error
        self.level = level
        self.fallback_index = fallback_index

    def __bool__(self) -> bool:
        """Truthiness indicates success."""
        return self.success

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "level": self.level.name,
            "fallback_index": self.fallback_index,
            "error": str(self.error) if self.error else None,
        }


@dataclass
class DegradationEvent:
    """Record of a degradation event.

    Attributes:
        level: The degradation level that was triggered
        reason: Why degradation occurred
        timestamp: When the event occurred
        duration: How long degradation lasted
        recovered: Whether service has recovered
    """

    level: DegradationLevel
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration: timedelta | None = None
    recovered: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level.name,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "duration": str(self.duration) if self.duration else None,
            "recovered": self.recovered,
        }


class DegradationStrategy(ABC):
    """Base class for degradation strategies."""

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> FallbackResult:
        """Execute the fallback strategy."""
        pass

    @property
    @abstractmethod
    def level(self) -> DegradationLevel:
        """Return the degradation level of this strategy."""
        pass


class FunctionFallback(DegradationStrategy):
    """Fallback that executes a provided function."""

    def __init__(
        self,
        func: Callable[..., Any],
        level: DegradationLevel = DegradationLevel.DEGRADED,
    ) -> None:
        """Initialize the function fallback.

        Args:
            func: Function to call as fallback
            level: Degradation level of this fallback
        """
        self.func = func
        self._level = level

    def execute(self, *args: Any, **kwargs: Any) -> FallbackResult:
        """Execute the fallback function."""
        try:
            result = self.func(*args, **kwargs)
            return FallbackResult(success=True, value=result, level=self._level)
        except Exception as e:
            return FallbackResult(success=False, error=e, level=self._level)

    @property
    def level(self) -> DegradationLevel:
        return self._level


class CachedFallback(DegradationStrategy):
    """Fallback that returns cached/stored values."""

    def __init__(
        self,
        cache: dict[str, Any],
        default_key: str | None = None,
        level: DegradationLevel = DegradationLevel.MINIMAL,
    ) -> None:
        """Initialize the cached fallback.

        Args:
            cache: Cache dictionary to pull from
            default_key: Default key if none provided
            level: Degradation level
        """
        self.cache = cache
        self.default_key = default_key
        self._level = level

    def execute(self, *args: Any, **kwargs: Any) -> FallbackResult:
        """Execute the cached fallback."""
        key = kwargs.get("cache_key", self.default_key)

        if key and key in self.cache:
            return FallbackResult(
                success=True,
                value=self.cache[key],
                level=self._level,
            )

        return FallbackResult(
            success=False,
            error=KeyError(f"Cache key '{key}' not found"),
            level=self._level,
        )

    @property
    def level(self) -> DegradationLevel:
        return self._level


class StaticFallback(DegradationStrategy):
    """Fallback that returns a static value."""

    def __init__(
        self,
        value: Any,
        level: DegradationLevel = DegradationLevel.OFFLINE,
    ) -> None:
        """Initialize the static fallback.

        Args:
            value: Static value to return
            level: Degradation level
        """
        self.value = value
        self._level = level

    def execute(self, *args: Any, **kwargs: Any) -> FallbackResult:  # noqa: ARG002
        """Execute the static fallback."""
        return FallbackResult(
            success=True,
            value=self.value,
            level=self._level,
        )

    @property
    def level(self) -> DegradationLevel:
        return self._level


class DegradationManager:
    """Manages degradation state and fallback strategies.

    Tracks current degradation level, manages fallback chains,
    and logs degradation events.

    Example:
        ```python
        manager = DegradationManager(service_name="my_service")

        @manager.operation(fallbacks=[
            lambda: primary_api(),
            lambda: backup_api(),
            lambda: cached_data.get(),
        ])
        def get_user_data(user_id: str):
            return primary_api().get_user(user_id)
        ```
    """

    def __init__(
        self,
        service_name: str,
        initial_level: DegradationLevel = DegradationLevel.FULL,
        auto_recovery: bool = True,
        recovery_check_interval: float = 60.0,
    ) -> None:
        """Initialize the degradation manager.

        Args:
            service_name: Name of the service being managed
            initial_level: Starting degradation level
            auto_recovery: Whether to attempt auto-recovery
            recovery_check_interval: Seconds between recovery checks
        """
        self.service_name = service_name
        self._current_level = initial_level
        self.auto_recovery = auto_recovery
        self.recovery_check_interval = recovery_check_interval

        # Event tracking
        self._events: list[DegradationEvent] = []
        self._level_changed_at: datetime = datetime.now()

        # Recovery checkers
        self._recovery_checkers: dict[DegradationLevel, Callable[[], bool]] = {}

    @property
    def current_level(self) -> DegradationLevel:
        """Get the current degradation level."""
        return self._current_level

    @property
    def is_degraded(self) -> bool:
        """Check if service is currently degraded."""
        return self._current_level != DegradationLevel.FULL

    @property
    def downtime_duration(self) -> timedelta:
        """Get duration since last degradation started."""
        if not self.is_degraded:
            return timedelta(0)
        return datetime.now() - self._level_changed_at

    def set_level(self, level: DegradationLevel, reason: str = "") -> None:
        """Set the current degradation level.

        Args:
            level: New degradation level
            reason: Reason for the change
        """
        old_level = self._current_level

        if old_level != level:
            # End previous event
            if self._events:
                self._events[-1].duration = datetime.now() - self._level_changed_at

            # Create new event
            event = DegradationEvent(level=level, reason=reason)
            self._events.append(event)

            self._current_level = level
            self._level_changed_at = datetime.now()

            logger.info(
                f"{self.service_name}: degradation level changed "
                f"{old_level.name} -> {level.name}: {reason}"
            )

    def recover(self, reason: str = "recovery") -> bool:
        """Attempt to recover to full operation.

        Args:
            reason: Reason for recovery

        Returns:
            True if recovered successfully
        """
        # Run recovery checkers
        for level, checker in self._recovery_checkers.items():
            if level >= self._current_level:
                try:
                    if not checker():
                        logger.warning(f"{self.service_name}: recovery check for {level.name} failed")
                        return False
                except Exception as e:
                    logger.error(f"{self.service_name}: recovery check error: {e}")
                    return False

        self.set_level(DegradationLevel.FULL, reason)
        if self._events:
            self._events[-1].recovered = True
        return True

    def register_recovery_checker(
        self,
        level: DegradationLevel,
        checker: Callable[[], bool],
    ) -> None:
        """Register a recovery checker for a degradation level.

        Args:
            level: Degradation level to check
            checker: Function that returns True if recovery is possible
        """
        self._recovery_checkers[level] = checker

    def get_events(
        self,
        limit: int | None = None,
        since: datetime | None = None,
    ) -> list[DegradationEvent]:
        """Get degradation events.

        Args:
            limit: Maximum number of events to return
            since: Only return events after this time

        Returns:
            List of degradation events
        """
        events = self._events

        if since:
            events = [e for e in events if e.timestamp >= since]

        if limit:
            events = events[-limit:]

        return events

    def get_stats(self) -> dict[str, Any]:
        """Get degradation statistics."""
        total_events = len(self._events)
        degraded_events = [e for e in self._events if e.level != DegradationLevel.FULL]

        total_downtime = timedelta()
        for event in degraded_events:
            if event.duration:
                total_downtime += event.duration
            elif event.level == self._current_level and not event.recovered:
                # Currently degraded
                total_downtime += self.downtime_duration

        return {
            "service_name": self.service_name,
            "current_level": self._current_level.name,
            "is_degraded": self.is_degraded,
            "current_downtime": str(self.downtime_duration),
            "total_events": total_events,
            "degraded_events": len(degraded_events),
            "total_downtime": str(total_downtime),
        }

    def operation(
        self,
        fallbacks: list[Callable[..., Any]] | None = None,
        fallback_strategies: list[DegradationStrategy] | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator to add degradation handling to an operation.

        Args:
            fallbacks: List of fallback functions to try
            fallback_strategies: List of DegradationStrategy objects

        Returns:
            Decorated function with degradation handling

        Example:
            ```python
            @manager.operation(fallbacks=[
                lambda: primary_database.query(),
                lambda: cache.get("query_result"),
                lambda: [],
            ])
            def get_items():
                return primary_database.query()
            ```
        """
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Try primary function
                try:
                    result = func(*args, **kwargs)
                    # If successful and we were degraded, try to recover
                    if self.is_degraded and self.auto_recovery:
                        self.recover("operation succeeded")
                    return result
                except Exception as primary_error:
                    logger.warning(
                        f"{self.service_name}: primary operation failed: {primary_error}"
                    )

                    # Try fallbacks
                    strategies: list[DegradationStrategy] = []

                    if fallback_strategies:
                        strategies.extend(fallback_strategies)

                    if fallbacks:
                        for i, fb in enumerate(fallbacks):
                            level = [
                                DegradationLevel.DEGRADED,
                                DegradationLevel.MINIMAL,
                                DegradationLevel.OFFLINE,
                            ][min(i, 2)]
                            strategies.append(FunctionFallback(fb, level))

                    for strategy in strategies:
                        result = strategy.execute(*args, **kwargs)
                        if result.success:
                            # Update degradation level
                            if strategy.level != self._current_level:
                                self.set_level(strategy.level, "fallback activated")
                            return result.value

                    # All fallbacks failed
                    self.set_level(DegradationLevel.OFFLINE, "all fallbacks exhausted")
                    raise primary_error

            return wrapper

        return decorator


# Global manager
_global_manager = DegradationManager("default")


def get_manager(name: str = "default") -> DegradationManager:
    """Get or create a degradation manager."""
    if name == "default" and _global_manager.service_name == "default":
        return _global_manager
    return DegradationManager(name)


class Degrade:
    """Context manager for temporary degradation.

    Example:
        ```python
        with Degrade(DegradationLevel.DEGRADED, reason="maintenance"):
            # Operations here will use degraded mode
            result = operation_with_degraded_fallbacks()
        ```
    """

    def __init__(
        self,
        level: DegradationLevel,
        reason: str = "",
        manager: DegradationManager | None = None,
    ) -> None:
        """Initialize the degradation context.

        Args:
            level: Degradation level to set
            reason: Reason for degradation
            manager: Manager to use (defaults to global)
        """
        self.level = level
        self.reason = reason
        self.manager = manager or _global_manager
        self._previous_level: DegradationLevel | None = None

    def __enter__(self) -> "Degrade":
        self._previous_level = self.manager.current_level
        self.manager.set_level(self.level, self.reason)
        return self

    def __exit__(self, *args: Any) -> None:  # noqa: ARG002
        if self._previous_level is not None:
            self.manager.set_level(self._previous_level, "context exit")


def with_fallbacks(
    fallbacks: list[Callable[..., Any]],
    manager: DegradationManager | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add fallback chain to a function.

    Args:
        fallbacks: List of fallback functions to try in order
        manager: Degradation manager to use

    Example:
        ```python
        @with_fallbacks([
            lambda: primary_api(),
            lambda: cache.get(),
            lambda: [],
        ])
        def get_data():
            return primary_api()
        ```
    """
    mgr = manager or _global_manager

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        return mgr.operation(fallbacks=fallbacks)(func)

    return decorator


def degrade_gracefully(
    level: DegradationLevel = DegradationLevel.DEGRADED,
    fallback: Callable[..., Any] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add graceful degradation to a function.

    Args:
        level: Degradation level to use
        fallback: Fallback function to call on failure

    Example:
        ```python
        @degrade_gracefully(level=DegradationLevel.MINIMAL)
        def process_data(data):
            return complex_processing(data)
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if fallback:
                    logger.warning(f"Degrading to {level.name}: {e}")
                    _global_manager.set_level(level, str(e))
                    return fallback(*args, **kwargs)
                raise

        return wrapper

    return decorator


def cached_result(
    cache: dict[str, Any],
    key_func: Callable[..., str] | None = None,
    default: Any = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to cache results for offline fallback.

    Args:
        cache: Cache dictionary to store results
        key_func: Function to generate cache key (uses args by default)
        default: Default value to return on cache miss

    Example:
        ```python
        cache = {}

        @cached_result(cache, key_func=lambda user_id: f"user:{user_id}")
        def get_user(user_id: str):
            return api.get_user(user_id)
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            try:
                result = func(*args, **kwargs)
                cache[key] = result
                return result
            except Exception:
                # Return cached result if available
                if key in cache:
                    _global_manager.set_level(
                        DegradationLevel.MINIMAL,
                        "using cached result",
                    )
                    return cache[key]
                if default is not None:
                    return default
                raise

        return wrapper

    return decorator


__all__ = [
    "DegradationLevel",
    "FallbackResult",
    "DegradationEvent",
    "DegradationStrategy",
    "FunctionFallback",
    "CachedFallback",
    "StaticFallback",
    "DegradationManager",
    # Context manager and decorators
    "Degrade",
    "with_fallbacks",
    "degrade_gracefully",
    "cached_result",
    # Global manager
    "get_manager",
    "_global_manager",
]
