"""
Circuit Breaker

Implements the circuit breaker pattern to prevent cascading failures when
dependent services become unavailable. Tracks failure counts, automatically
opens circuits after thresholds, and provides half-open state for recovery testing.

Example:
    ```python
    from circuit_breaker import CircuitBreaker, CircuitBreakerOpen

    breaker = CircuitBreaker(
        name="api_service",
        failure_threshold=5,
        timeout_seconds=60,
    )

    @breaker.protect
    def call_external_api(data):
        return requests.post("https://api.example.com", json=data)

    try:
        result = call_external_api({"key": "value"})
    except CircuitBreakerOpen:
        # Circuit is open, use fallback
        result = get_cached_result()
    ```

States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Circuit is open, requests fail fast
    - HALF_OPEN: Testing if service has recovered
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from threading import Lock
from typing import Any, Callable, ParamSpec, TypeVar

# Type variables
P = ParamSpec("P")
R = TypeVar("R")


class CircuitState(Enum):
    """States of the circuit breaker."""

    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Failing fast
    HALF_OPEN = auto()   # Testing recovery


class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""

    pass


class CircuitBreakerOpen(CircuitBreakerError):
    """Raised when circuit is open and request is rejected.

    Attributes:
        breaker_name: Name of the circuit breaker
        opened_at: When the circuit opened
        remaining_timeout: Seconds until circuit will attempt recovery
    """

    def __init__(
        self,
        breaker_name: str,
        opened_at: datetime,
        remaining_timeout: float,
    ) -> None:
        self.breaker_name = breaker_name
        self.opened_at = opened_at
        self.remaining_timeout = remaining_timeout
        super().__init__(
            f"Circuit '{breaker_name}' is open. "
            f"Recovery attempt in {remaining_timeout:.1f}s"
        )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes in half-open to close circuit
        timeout_seconds: Seconds to wait before attempting recovery
        half_open_max_calls: Max calls allowed in half-open state
        window_size: Size of sliding window for failure tracking
        exponential_backoff: Enable exponential backoff on retries
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    half_open_max_calls: int = 3
    window_size: int = 100
    exponential_backoff: bool = False


@dataclass
class CallResult:
    """Result of a protected call.

    Attributes:
        success: Whether the call succeeded
        duration: Call duration in seconds
        timestamp: When the call occurred
        error: Exception if call failed
    """

    success: bool
    duration: float
    timestamp: datetime
    error: Exception | None = None


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker.

    Attributes:
        total_calls: Total number of calls made
        successful_calls: Number of successful calls
        failed_calls: Number of failed calls
        rejected_calls: Number of calls rejected (circuit open)
        current_state: Current circuit state
        last_failure_time: Time of last failure
        last_success_time: Time of last success
        opened_count: Number of times circuit opened
        closed_count: Number of times circuit closed
    """

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    current_state: CircuitState = CircuitState.CLOSED
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    opened_count: int = 0
    closed_count: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate (0.0 to 1.0)."""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "current_state": self.current_state.name,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "opened_count": self.opened_count,
            "closed_count": self.closed_count,
        }


class CircuitBreaker:
    """Circuit breaker implementation for failure protection.

    Prevents cascading failures by automatically opening circuits when
    failure thresholds are exceeded and attempting recovery after timeouts.

    Example:
        ```python
        breaker = CircuitBreaker(
            name="database",
            failure_threshold=5,
            timeout_seconds=30,
        )

        @breaker.protect
        def query_database(sql):
            return db.execute(sql)
        ```
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60.0,
        half_open_max_calls: int = 3,
        window_size: int = 100,
    ) -> None:
        """Initialize the circuit breaker.

        Args:
            name: Identifier for this circuit breaker
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open to close circuit
            timeout_seconds: Seconds before recovery attempt
            half_open_max_calls: Max calls allowed during testing
            window_size: Size of sliding window for tracking
        """
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
            half_open_max_calls=half_open_max_calls,
            window_size=window_size,
        )

        # State
        self._state = CircuitState.CLOSED
        self._opened_at: datetime | None = None
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0

        # History for sliding window
        self._call_history: deque[CallResult] = deque(maxlen=window_size)

        # Threading safety
        self._lock = Lock()

        # Statistics
        self.stats = CircuitBreakerStats()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)."""
        return self.state != CircuitState.CLOSED

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._opened_at is None:
            return True

        elapsed = (datetime.now() - self._opened_at).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def _record_call(self, result: CallResult) -> None:
        """Record a call result in history."""
        self._call_history.append(result)

        # Update statistics
        self.stats.total_calls += 1
        if result.success:
            self.stats.successful_calls += 1
            self.stats.last_success_time = result.timestamp
        else:
            self.stats.failed_calls += 1
            self.stats.last_failure_time = result.timestamp

    def _open_circuit(self) -> None:
        """Open the circuit (start rejecting calls)."""
        self._state = CircuitState.OPEN
        self._opened_at = datetime.now()
        self.stats.opened_count += 1
        self.stats.current_state = CircuitState.OPEN

    def _close_circuit(self) -> None:
        """Close the circuit (resume normal operation)."""
        self._state = CircuitState.CLOSED
        self._opened_at = None
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self.stats.closed_count += 1
        self.stats.current_state = CircuitState.CLOSED

    def _half_open_circuit(self) -> None:
        """Move to half-open state (testing recovery)."""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        self._half_open_calls = 0
        self.stats.current_state = CircuitState.HALF_OPEN

    def _handle_success(self) -> None:
        """Handle a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def _handle_failure(self) -> None:
        """Handle a failed call."""
        self._failure_count += 1

        if self._state == CircuitState.HALF_OPEN:
            # Recovery failed, open circuit again
            self._open_circuit()
        elif self._failure_count >= self.config.failure_threshold:
            self._open_circuit()

    def _before_call(self) -> None:
        """Check circuit state before allowing a call."""
        # Check if we should attempt recovery
        if self._state == CircuitState.OPEN and self._should_attempt_reset():
            self._half_open_circuit()

        # Reject calls if circuit is open
        if self._state == CircuitState.OPEN:
            remaining = self.config.timeout_seconds
            if self._opened_at:
                elapsed = (datetime.now() - self._opened_at).total_seconds()
                remaining = max(0, self.config.timeout_seconds - elapsed)

            self.stats.rejected_calls += 1
            raise CircuitBreakerOpen(
                self.name,
                self._opened_at or datetime.now(),
                remaining,
            )

        # Limit calls in half-open state
        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.config.half_open_max_calls:
                self.stats.rejected_calls += 1
                raise CircuitBreakerOpen(
                    self.name,
                    self._opened_at or datetime.now(),
                    0,
                )
            self._half_open_calls += 1

    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute a function through the circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function return value

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from the wrapped function
        """
        with self._lock:
            self._before_call()

        start_time = time.time()
        timestamp = datetime.now()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            with self._lock:
                self._record_call(CallResult(
                    success=True,
                    duration=duration,
                    timestamp=timestamp,
                ))
                self._handle_success()

            return result

        except Exception as e:
            duration = time.time() - start_time

            with self._lock:
                self._record_call(CallResult(
                    success=False,
                    duration=duration,
                    timestamp=timestamp,
                    error=e,
                ))
                self._handle_failure()

            raise

    async def call_async(
        self,
        func: Callable[P, Any],  # Awaitable[R]
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Any:
        """Execute an async function through the circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function return value

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from the wrapped function
        """
        with self._lock:
            self._before_call()

        start_time = time.time()
        timestamp = datetime.now()

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            with self._lock:
                self._record_call(CallResult(
                    success=True,
                    duration=duration,
                    timestamp=timestamp,
                ))
                self._handle_success()

            return result

        except Exception as e:
            duration = time.time() - start_time

            with self._lock:
                self._record_call(CallResult(
                    success=False,
                    duration=duration,
                    timestamp=timestamp,
                    error=e,
                ))
                self._handle_failure()

            raise

    def protect(self, func: Callable[P, R]) -> Callable[P, R]:
        """Decorator to protect a function with this circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Wrapped function with circuit breaker protection

        Example:
            ```python
            @breaker.protect
            def external_service_call():
                return requests.get("https://api.example.com")
            ```
        """
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return await self.call_async(func, *args, **kwargs)
            return async_wrapper  # type: ignore[return-value]
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return self.call(func, *args, **kwargs)
            return sync_wrapper

    def reset(self) -> None:
        """Manually reset the circuit to closed state."""
        with self._lock:
            self._close_circuit()

    def get_stats(self) -> CircuitBreakerStats:
        """Get current statistics."""
        with self._lock:
            return CircuitBreakerStats(
                total_calls=self.stats.total_calls,
                successful_calls=self.stats.successful_calls,
                failed_calls=self.stats.failed_calls,
                rejected_calls=self.stats.rejected_calls,
                current_state=self._state,
                last_failure_time=self.stats.last_failure_time,
                last_success_time=self.stats.last_success_time,
                opened_count=self.stats.opened_count,
                closed_count=self.stats.closed_count,
            )

    def get_history(self, limit: int | None = None) -> list[CallResult]:
        """Get call history.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of call results
        """
        with self._lock:
            history = list(self._call_history)
            if limit:
                return history[-limit:]
            return history


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers.

    Example:
        ```python
        registry = CircuitBreakerRegistry()

        # Get or create a breaker
        breaker = registry.get("api_service", failure_threshold=5)

        # Use it
        @breaker.protect
        def call_api():
            pass
        ```
    """

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = Lock()

    def register(self, breaker: CircuitBreaker) -> CircuitBreaker:
        """Register a circuit breaker."""
        with self._lock:
            self._breakers[breaker.name] = breaker
        return breaker

    def get(
        self,
        name: str,
        **config: Any,
    ) -> CircuitBreaker:
        """Get or create a circuit breaker.

        Args:
            name: Name of the breaker
            **config: Configuration for new breaker if needed

        Returns:
            CircuitBreaker instance
        """
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, **config)
            return self._breakers[name]

    def remove(self, name: str) -> CircuitBreaker | None:
        """Remove a circuit breaker from registry."""
        with self._lock:
            return self._breakers.pop(name, None)

    def get_all(self) -> dict[str, CircuitBreaker]:
        """Get all registered breakers."""
        with self._lock:
            return self._breakers.copy()

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all breakers."""
        with self._lock:
            return {
                name: breaker.get_stats().to_dict()
                for name, breaker in self._breakers.items()
            }

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# Global registry
_global_registry = CircuitBreakerRegistry()


def get_breaker(name: str, **config: Any) -> CircuitBreaker:
    """Get or create a circuit breaker from the global registry."""
    return _global_registry.get(name, **config)


def circuit_breaker(
    name: str | None = None,
    **config: Any,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add circuit breaker protection to a function.

    Args:
        name: Name for the circuit breaker (defaults to function name)
        **config: Circuit breaker configuration

    Example:
        ```python
        @circuit_breaker(failure_threshold=5, timeout_seconds=30)
        def external_api_call():
            return requests.get("https://api.example.com")
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        breaker_name = name or f"{func.__module__}.{func.__qualname__}"
        breaker = get_breaker(breaker_name, **config)
        return breaker.protect(func)

    return decorator


__all__ = [
    "CircuitState",
    "CircuitBreakerError",
    "CircuitBreakerOpen",
    "CircuitBreakerConfig",
    "CallResult",
    "CircuitBreakerStats",
    "CircuitBreaker",
    "CircuitBreakerRegistry",
    # Global functions
    "get_breaker",
    "circuit_breaker",
    "_global_registry",
]
