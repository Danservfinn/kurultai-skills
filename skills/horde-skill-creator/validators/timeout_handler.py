"""
Timeout Handler Validator

Provides timeout enforcement for skill operations with configurable timeout values
per operation type. Uses asyncio for async operations and threading for sync operations.

Example:
    ```python
    from timeout_handler import with_timeout, TimeoutType, TimeoutError

    @with_timeout(TimeoutType.QUICK)
    async def quick_lookup(user_id: str) -> dict:
        # Will timeout after 5 seconds
        return await fetch_user(user_id)

    @with_timeout(TimeoutType.LONG_RUNNING, timeout_seconds=180)
    async def data_export(date_range: tuple) -> str:
        # Custom timeout of 180 seconds
        return await generate_report(date_range)

    # Sync operations also supported
    @with_timeout(TimeoutType.MEDIUM)
    def sync_operation(x: int) -> int:
        return heavy_computation(x)
    ```

Timeout Types:
    - MICRO: 2 seconds - For tiny, predictable operations
    - QUICK: 5 seconds - For simple lookups and validations
    - MEDIUM: 15 seconds - For typical API calls and processing
    - LONG_RUNNING: 60 seconds - For complex operations
    - BATCH: 300 seconds (5 min) - For bulk operations
    - CUSTOM: User-defined timeout value
"""

from __future__ import annotations

import asyncio
import functools
import signal
import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, overload

# Type variables for generic decorators
P = ParamSpec("P")
R = TypeVar("R")


class TimeoutType(Enum):
    """Predefined timeout categories for different operation types."""

    MICRO = auto()       # 2 seconds - Tiny, predictable operations
    QUICK = auto()       # 5 seconds - Simple lookups, validations
    MEDIUM = auto()      # 15 seconds - Typical API calls
    LONG_RUNNING = auto()  # 60 seconds - Complex operations
    BATCH = auto()       # 300 seconds (5 min) - Bulk operations
    CUSTOM = auto()      # User-defined timeout


# Default timeout values in seconds
DEFAULT_TIMEOUTS: dict[TimeoutType, float] = {
    TimeoutType.MICRO: 2.0,
    TimeoutType.QUICK: 5.0,
    TimeoutType.MEDIUM: 15.0,
    TimeoutType.LONG_RUNNING: 60.0,
    TimeoutType.BATCH: 300.0,
}


class SkillTimeoutError(TimeoutError):
    """Raised when an operation exceeds its timeout limit.

    Attributes:
        operation: Name of the operation that timed out
        timeout: The timeout value in seconds
        elapsed: Actual time elapsed before timeout
    """

    def __init__(self, operation: str, timeout: float, elapsed: float | None = None) -> None:
        self.operation = operation
        self.timeout = timeout
        self.elapsed = elapsed
        message = (
            f"Operation '{operation}' timed out after {timeout:.1f}s"
            + (f" (elapsed: {elapsed:.1f}s)" if elapsed else "")
        )
        super().__init__(message)


@dataclass
class TimeoutConfig:
    """Configuration for timeout behavior.

    Attributes:
        timeout_type: The category of timeout to apply
        timeout_seconds: Custom timeout value (required for CUSTOM type)
        raise_on_timeout: Whether to raise an exception or return None
        grace_period: Additional time after soft timeout before hard stop
        warn_threshold: Fraction of timeout after which to log warnings
    """

    timeout_type: TimeoutType = TimeoutType.MEDIUM
    timeout_seconds: float | None = None
    raise_on_timeout: bool = True
    grace_period: float = 0.0
    warn_threshold: float = 0.8

    def get_timeout(self) -> float:
        """Get the effective timeout value in seconds."""
        if self.timeout_type == TimeoutType.CUSTOM:
            if self.timeout_seconds is None:
                raise ValueError("timeout_seconds must be provided for CUSTOM timeout type")
            return self.timeout_seconds
        return DEFAULT_TIMEOUTS.get(self.timeout_type, DEFAULT_TIMEOUTS[TimeoutType.MEDIUM])


class TimeoutStats:
    """Tracks timeout statistics for operations.

    Attributes:
        total_calls: Total number of times the operation was called
        timeouts: Number of times the operation timed out
        completions: Number of times the operation completed successfully
        avg_duration: Average duration of successful completions
        max_duration: Maximum duration observed
    """

    def __init__(self) -> None:
        self.total_calls: int = 0
        self.timeouts: int = 0
        self.completions: int = 0
        self._total_duration: float = 0.0
        self.max_duration: float = 0.0

    def record_call(self) -> None:
        """Record that the operation was called."""
        self.total_calls += 1

    def record_timeout(self) -> None:
        """Record that the operation timed out."""
        self.timeouts += 1

    def record_completion(self, duration: float) -> None:
        """Record a successful completion with its duration."""
        self.completions += 1
        self._total_duration += duration
        self.max_duration = max(self.max_duration, duration)

    @property
    def avg_duration(self) -> float:
        """Calculate average duration of successful completions."""
        return self._total_duration / self.completions if self.completions > 0 else 0.0

    @property
    def timeout_rate(self) -> float:
        """Calculate the rate of timeouts (0.0 to 1.0)."""
        return self.timeouts / self.total_calls if self.total_calls > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary for serialization."""
        return {
            "total_calls": self.total_calls,
            "timeouts": self.timeouts,
            "completions": self.completions,
            "avg_duration": self.avg_duration,
            "max_duration": self.max_duration,
            "timeout_rate": self.timeout_rate,
        }


# Global registry for operation statistics
_timeout_stats: dict[str, TimeoutStats] = {}


def get_stats(operation_name: str) -> TimeoutStats | None:
    """Get timeout statistics for a specific operation.

    Args:
        operation_name: Name of the operation to get stats for

    Returns:
        TimeoutStats object or None if operation not tracked
    """
    return _timeout_stats.get(operation_name)


def get_all_stats() -> dict[str, dict[str, Any]]:
    """Get timeout statistics for all tracked operations.

    Returns:
        Dictionary mapping operation names to their stats
    """
    return {name: stats.to_dict() for name, stats in _timeout_stats.items()}


def clear_stats(operation_name: str | None = None) -> None:
    """Clear timeout statistics.

    Args:
        operation_name: Specific operation to clear, or None to clear all
    """
    if operation_name:
        _timeout_stats.pop(operation_name, None)
    else:
        _timeout_stats.clear()


class _TimeoutContext:
    """Context manager for enforcing timeouts on sync operations."""

    def __init__(self, timeout: float, operation: str, raise_on_timeout: bool = True) -> None:
        self.timeout = timeout
        self.operation = operation
        self.raise_on_timeout = raise_on_timeout
        self.start_time: float | None = None
        self._original_handler: Callable[[int, Any], Any] | None = None

    def _timeout_handler(self, signum: int, frame: Any) -> None:  # noqa: ARG002
        """Signal handler for timeout."""
        elapsed = time.time() - self.start_time if self.start_time else None
        raise SkillTimeoutError(self.operation, self.timeout, elapsed)

    def __enter__(self) -> "_TimeoutContext":
        self.start_time = time.time()
        self._original_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(int(self.timeout))
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:  # noqa: ANN401
        signal.alarm(0)
        if self._original_handler is not None:
            signal.signal(signal.SIGALRM, self._original_handler)
        if isinstance(exc_val, SkillTimeoutError) and not self.raise_on_timeout:
            return True  # Suppress the exception
        return None


@overload
def with_timeout(
    timeout_type: TimeoutType = TimeoutType.MEDIUM,
    *,
    timeout_seconds: float | None = None,
    raise_on_timeout: bool = True,
    grace_period: float = 0.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def with_timeout(
    timeout_type: TimeoutType = TimeoutType.MEDIUM,
    *,
    timeout_seconds: float | None = None,
    raise_on_timeout: bool = True,
    grace_period: float = 0.0,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]: ...


def with_timeout(
    timeout_type: TimeoutType = TimeoutType.MEDIUM,
    *,
    timeout_seconds: float | None = None,
    raise_on_timeout: bool = True,
    grace_period: float = 0.0,
) -> Any:
    """Decorator to add timeout enforcement to functions and coroutines.

    The decorator automatically detects whether the function is async or sync
    and applies the appropriate timeout mechanism.

    Args:
        timeout_type: Category of timeout from TimeoutType enum
        timeout_seconds: Custom timeout value (required for CUSTOM type)
        raise_on_timeout: If True, raise SkillTimeoutError; otherwise return None
        grace_period: Additional time before hard timeout

    Returns:
        Decorated function with timeout enforcement

    Raises:
        SkillTimeoutError: When operation exceeds timeout (if raise_on_timeout=True)
        ValueError: When CUSTOM type specified without timeout_seconds

    Example:
        ```python
        @with_timeout(TimeoutType.QUICK)
        async def fetch_user(user_id: str) -> dict:
            return await db.get_user(user_id)

        @with_timeout(TimeoutType.CUSTOM, timeout_seconds=30)
        def process_batch(items: list) -> list:
            return [process(x) for x in items]
        ```
    """
    config = TimeoutConfig(
        timeout_type=timeout_type,
        timeout_seconds=timeout_seconds,
        raise_on_timeout=raise_on_timeout,
        grace_period=grace_period,
    )
    timeout = config.get_timeout()

    def decorator(func: Callable[P, R] | Callable[P, Awaitable[R]]) -> Callable[P, R] | Callable[P, Awaitable[R]]:
        operation_name = f"{func.__module__}.{func.__qualname__}"

        # Initialize stats for this operation
        if operation_name not in _timeout_stats:
            _timeout_stats[operation_name] = TimeoutStats()

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                _timeout_stats[operation_name].record_call()
                start_time = time.time()

                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout + grace_period,
                    )
                    duration = time.time() - start_time
                    _timeout_stats[operation_name].record_completion(duration)
                    return result
                except asyncio.TimeoutError as e:
                    elapsed = time.time() - start_time
                    _timeout_stats[operation_name].record_timeout()
                    if raise_on_timeout:
                        raise SkillTimeoutError(operation_name, timeout, elapsed) from e
                    return None  # type: ignore[return-value]

            return async_wrapper  # type: ignore[return-value]
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                _timeout_stats[operation_name].record_call()
                start_time = time.time()

                # Use threading timeout for sync functions to avoid signal issues
                result: Any = None
                exception: Exception | None = None

                def run_func() -> None:
                    nonlocal result, exception
                    try:
                        result = func(*args, **kwargs)
                    except Exception as e:
                        exception = e

                thread = threading.Thread(target=run_func, daemon=True)
                thread.start()
                thread.join(timeout=timeout + grace_period)

                if thread.is_alive():
                    elapsed = time.time() - start_time
                    _timeout_stats[operation_name].record_timeout()
                    if raise_on_timeout:
                        raise SkillTimeoutError(operation_name, timeout, elapsed)
                    return None  # type: ignore[return-value]

                if exception is not None:
                    raise exception

                duration = time.time() - start_time
                _timeout_stats[operation_name].record_completion(duration)
                return result

            return sync_wrapper

    return decorator


def timeout_context(
    timeout: float,
    operation: str = "operation",
    raise_on_timeout: bool = True,
) -> _TimeoutContext:
    """Create a context manager for timeout enforcement.

    Useful for adding timeout protection to code blocks without decorators.

    Args:
        timeout: Timeout value in seconds
        operation: Name of the operation for error messages
        raise_on_timeout: Whether to raise exception on timeout

    Example:
        ```python
        with timeout_context(5.0, "database_query"):
            result = expensive_database_operation()
        ```
    """
    return _TimeoutContext(timeout, operation, raise_on_timeout)


class TimeoutManager:
    """Manager for coordinating timeouts across multiple operations.

    Provides higher-level timeout management for complex workflows
    with multiple dependent operations.

    Example:
        ```python
        manager = TimeoutManager(default_timeout=10.0)

        with manager.operation("fetch_users", timeout=5.0):
            users = fetch_all_users()

        with manager.operation("process_data"):
            results = process_users(users)

        print(manager.get_report())
        ```
    """

    def __init__(self, default_timeout: float = 30.0) -> None:
        self.default_timeout = default_timeout
        self._operations: list[dict[str, Any]] = []

    def operation(
        self,
        name: str,
        timeout: float | None = None,
        raise_on_timeout: bool = True,
    ) -> _TimeoutContext:
        """Create a timeout context for a named operation.

        Args:
            name: Name of the operation for tracking
            timeout: Timeout in seconds (uses default if None)
            raise_on_timeout: Whether to raise on timeout

        Returns:
            Timeout context manager
        """
        actual_timeout = timeout if timeout is not None else self.default_timeout
        self._operations.append({"name": name, "timeout": actual_timeout})
        return timeout_context(actual_timeout, name, raise_on_timeout)

    def get_report(self) -> dict[str, Any]:
        """Generate a report of all tracked operations.

        Returns:
            Dictionary with operation statistics
        """
        return {
            "total_operations": len(self._operations),
            "operations": self._operations.copy(),
        }


__all__ = [
    "TimeoutType",
    "SkillTimeoutError",
    "TimeoutConfig",
    "TimeoutStats",
    "with_timeout",
    "timeout_context",
    "TimeoutManager",
    "get_stats",
    "get_all_stats",
    "clear_stats",
    "DEFAULT_TIMEOUTS",
]
