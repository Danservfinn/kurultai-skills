"""
Pre-flight Confirmation

Generates interactive confirmation prompts before executing operations
based on risk assessment. Supports different risk levels, operation
categories, and user approval workflows.

Example:
    ```python
    from preflight import (
        PreflightCheck,
        OperationRisk,
        confirm_before_execute,
        preflight_check,
    )

    @preflight_check(risk=OperationRisk.DESTRUCTIVE)
    def delete_user(user_id: str):
        # User will be prompted before this runs
        return db.users.delete(user_id)

    @preflight_check(risk=OperationRisk.SAFE)
    def get_user(user_id: str):
        # No confirmation needed for safe operations
        return db.users.get(user_id)
    ```

Risk Levels:
    - SAFE: No confirmation needed (read-only, idempotent)
    - LOW: Optional confirmation (non-destructive writes)
    - MEDIUM: Confirmation required (destructive, reversible)
    - HIGH: Explicit confirmation required (destructive, irreversible)
    - CRITICAL: Multi-step confirmation required (system-wide impact)
"""

from __future__ import annotations

import asyncio
import inspect
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, ParamSpec, TypeVar

# Type variables
P = ParamSpec("P")
R = TypeVar("R")


class OperationRisk(Enum):
    """Risk levels for operations requiring confirmation.

    SAFE: No confirmation needed
        - Read-only operations
        - Idempotent operations
        - Local-only effects

    LOW: Optional confirmation
        - Non-destructive writes
        - Reversible changes
        - Resource creation

    MEDIUM: Confirmation required
        - Destructive operations
        - Data modification
        - External service calls

    HIGH: Explicit confirmation required
        - Irreversible destructive operations
        - Data deletion
        - Production changes

    CRITICAL: Multi-step confirmation
        - System-wide changes
        - Security-critical operations
        - High-cost operations
    """

    SAFE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class OperationCategory(Enum):
    """Categories of operations for risk assessment."""

    READ = auto()           # Read data
    WRITE = auto()          # Write/create data
    UPDATE = auto()         # Update existing data
    DELETE = auto()         # Delete data
    NETWORK = auto()        # Network calls
    FILE = auto()           # File operations
    SYSTEM = auto()         # System operations
    PAYMENT = auto()        # Payment/financial operations
    SECURITY = auto()       # Security-critical operations
    ADMIN = auto()          # Administrative operations


@dataclass
class OperationMetadata:
    """Metadata about an operation for confirmation prompts.

    Attributes:
        name: Human-readable operation name
        description: Detailed description of what will happen
        risk_level: Assessed risk level
        category: Operation category
        affected_resources: List of resources that will be affected
        estimated_duration: Estimated execution time
        estimated_cost: Estimated monetary cost (if applicable)
        reversible: Whether the operation can be undone
        side_effects: List of potential side effects
    """

    name: str
    description: str
    risk_level: OperationRisk = OperationRisk.LOW
    category: OperationCategory = OperationCategory.WRITE
    affected_resources: list[str] = field(default_factory=list)
    estimated_duration: str | None = None
    estimated_cost: float | None = None
    reversible: bool = True
    side_effects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level.name,
            "category": self.category.name,
            "affected_resources": self.affected_resources,
            "estimated_duration": self.estimated_duration,
            "estimated_cost": self.estimated_cost,
            "reversible": self.reversible,
            "side_effects": self.side_effects,
        }


@dataclass
class ConfirmationResult:
    """Result of a pre-flight confirmation request.

    Attributes:
        approved: Whether the operation was approved
        denied: Whether the operation was denied
        deferred: Whether confirmation was deferred
        user_input: Additional input provided by user
        timestamp: When the confirmation was recorded
    """

    approved: bool
    denied: bool
    deferred: bool
    user_input: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_response(self) -> bool:
        """Check if user provided a definitive response."""
        return self.approved or self.denied

    @classmethod
    def approve(cls, user_input: str | None = None) -> "ConfirmationResult":
        """Create an approval result."""
        return cls(approved=True, denied=False, deferred=False, user_input=user_input)

    @classmethod
    def deny(cls, user_input: str | None = None) -> "ConfirmationResult":
        """Create a denial result."""
        return cls(approved=False, denied=True, deferred=False, user_input=user_input)

    @classmethod
    def defer(cls) -> "ConfirmationResult":
        """Create a deferred result."""
        return cls(approved=False, denied=False, deferred=True)


class ConfirmationPrompt:
    """Generator for user-facing confirmation prompts."""

    def __init__(self, metadata: OperationMetadata) -> None:
        """Initialize prompt with operation metadata.

        Args:
            metadata: Operation metadata for prompt generation
        """
        self.metadata = metadata

    def generate(self, include_details: bool = True) -> str:
        """Generate a confirmation prompt for the user.

        Args:
            include_details: Whether to include detailed information

        Returns:
            Formatted prompt string
        """
        risk_indicator = self._get_risk_indicator()
        lines = [
            f"{risk_indicator} Operation: {self.metadata.name}",
            "",
            f"Description: {self.metadata.description}",
        ]

        if include_details:
            lines.extend([
                "",
                "Details:",
                f"  Category: {self.metadata.category.name}",
                f"  Risk Level: {self.metadata.risk_level.name}",
            ])

            if self.metadata.affected_resources:
                lines.append(f"  Affected Resources:")
                for resource in self.metadata.affected_resources:
                    lines.append(f"    - {resource}")

            if self.metadata.estimated_duration:
                lines.append(f"  Estimated Duration: {self.metadata.estimated_duration}")

            if self.metadata.estimated_cost is not None:
                lines.append(f"  Estimated Cost: ${self.metadata.estimated_cost:.2f}")

            lines.append(f"  Reversible: {'Yes' if self.metadata.reversible else 'No'}")

            if self.metadata.side_effects:
                lines.append(f"  Potential Side Effects:")
                for effect in self.metadata.side_effects:
                    lines.append(f"    - {effect}")

        # Add confirmation instructions based on risk
        lines.extend([
            "",
            self._get_confirmation_instruction(),
        ])

        return "\n".join(lines)

    def _get_risk_indicator(self) -> str:
        """Get emoji/icon indicator for risk level."""
        indicators = {
            OperationRisk.SAFE: "✓",
            OperationRisk.LOW: "⚠",
            OperationRisk.MEDIUM: "⚠⚠",
            OperationRisk.HIGH: "🚨",
            OperationRisk.CRITICAL: "☢️",
        }
        return indicators.get(self.metadata.risk_level, "⚠")

    def _get_confirmation_instruction(self) -> str:
        """Get confirmation instruction based on risk level."""
        if self.metadata.risk_level == OperationRisk.SAFE:
            return "Proceeding with operation..."
        elif self.metadata.risk_level == OperationRisk.LOW:
            return "Press Enter to continue or 'n' to cancel."
        elif self.metadata.risk_level == OperationRisk.MEDIUM:
            return "Type 'yes' to confirm or 'no' to cancel."
        elif self.metadata.risk_level == OperationRisk.HIGH:
            return f"Type '{self.metadata.name.upper()}' to confirm or 'no' to cancel."
        else:  # CRITICAL
            return (
                f"Type 'CONFIRM {self.metadata.name.upper()}' to proceed. "
                "This operation cannot be undone."
            )

    def generate_json(self) -> str:
        """Generate prompt as JSON for programmatic consumption."""
        return json.dumps({
            "metadata": self.metadata.to_dict(),
            "prompt": self.generate(include_details=True),
            "confirmation_required": self.metadata.risk_level != OperationRisk.SAFE,
        }, indent=2)


class PreflightChecker:
    """Manages pre-flight checks and user confirmations.

    Example:
        ```python
        checker = PreflightChecker()

        @checker.check(risk=OperationRisk.HIGH)
        def delete_database():
            return db.drop_all_tables()
        ```
    """

    def __init__(
        self,
        auto_approve_safe: bool = True,
        default_risk: OperationRisk = OperationRisk.LOW,
    ) -> None:
        """Initialize the pre-flight checker.

        Args:
            auto_approve_safe: Automatically approve SAFE operations
            default_risk: Default risk level for unannotated operations
        """
        self.auto_approve_safe = auto_approve_safe
        self.default_risk = default_risk
        self._confirmation_callback: Callable[[OperationMetadata], ConfirmationResult] | None = None

    def set_confirmation_callback(
        self,
        callback: Callable[[OperationMetadata], ConfirmationResult],
    ) -> None:
        """Set a custom callback for obtaining user confirmation.

        Args:
            callback: Function that receives metadata and returns confirmation result
        """
        self._confirmation_callback = callback

    def assess_operation(
        self,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> OperationMetadata:
        """Assess an operation's risk and generate metadata.

        Args:
            func: Function to assess
            args: Function arguments
            kwargs: Function keyword arguments

        Returns:
            OperationMetadata with risk assessment
        """
        name = func.__name__.replace("_", " ").title()
        category = self._infer_category(func)
        risk = self._assess_risk_from_annotations(func) or self.default_risk

        # Extract affected resources from arguments
        resources = self._extract_affected_resources(args, kwargs)

        return OperationMetadata(
            name=name,
            description=self._generate_description(func, args, kwargs),
            risk_level=risk,
            category=category,
            affected_resources=resources,
            reversible=self._is_reversible(func),
        )

    def _infer_category(self, func: Callable[..., Any]) -> OperationCategory:
        """Infer operation category from function name and signature."""
        name_lower = func.__name__.lower()

        if any(word in name_lower for word in ["get", "fetch", "read", "list", "find", "show", "view"]):
            return OperationCategory.READ
        elif any(word in name_lower for word in ["delete", "remove", "drop", "destroy"]):
            return OperationCategory.DELETE
        elif any(word in name_lower for word in ["update", "modify", "change", "edit"]):
            return OperationCategory.UPDATE
        elif any(word in name_lower for word in ["create", "add", "insert", "new", "make"]):
            return OperationCategory.WRITE
        elif any(word in name_lower for word in ["send", "request", "call", "post", "fetch"]):
            return OperationCategory.NETWORK
        elif any(word in name_lower for word in ["pay", "charge", "refund", "purchase"]):
            return OperationCategory.PAYMENT
        elif any(word in name_lower for word in ["auth", "login", "password", "key", "token"]):
            return OperationCategory.SECURITY
        elif any(word in name_lower for word in ["admin", "manage", "config", "settings"]):
            return OperationCategory.ADMIN
        else:
            return OperationCategory.WRITE

    def _assess_risk_from_annotations(self, func: Callable[..., Any]) -> OperationRisk | None:
        """Assess risk level from function annotations."""
        # Check for explicit risk annotation
        if hasattr(func, "_preflight_risk"):
            return func._preflight_risk  # type: ignore

        # Infer from function name patterns
        name_lower = func.__name__.lower()

        # High-risk patterns
        if any(word in name_lower for word in ["delete", "drop", "destroy", "nuke"]):
            return OperationRisk.HIGH

        # Medium-risk patterns
        if any(word in name_lower for word in ["update", "modify", "change", "rebuild"]):
            return OperationRisk.MEDIUM

        # Safe patterns
        if any(word in name_lower for word in ["get", "fetch", "read", "list", "show", "check"]):
            return OperationRisk.SAFE

        return None

    def _extract_affected_resources(
        self,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> list[str]:
        """Extract affected resources from function arguments."""
        resources = []

        # Look for common resource argument patterns
        for value in list(args) + list(kwargs.values()):
            if isinstance(value, str):
                # Check for common resource patterns
                if "/" in value or value.endswith((".db", ".json", ".yaml", ".yml")):
                    resources.append(value)
                elif value.startswith(("http://", "https://")):
                    resources.append(value)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, str):
                        resources.append(item)

        return list(set(resources))[:10]  # Limit to 10 resources

    def _generate_description(
        self,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> str:
        """Generate a human-readable description of the operation."""
        name = func.__name__.replace("_", " ")
        sig = inspect.signature(func)

        # Get parameter values
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Build description with relevant parameters
        param_parts = []
        for param_name, param_value in list(bound_args.arguments.items())[:5]:
            if isinstance(param_value, str):
                param_parts.append(f"{param_name}='{param_value[:50]}'")
            elif not isinstance(param_value, (dict, list, bytes)):
                param_parts.append(f"{param_name}={param_value}")

        param_str = ", ".join(param_parts)
        if param_str:
            return f"{name} with {param_str}"
        return name

    def _is_reversible(self, func: Callable[..., Any]) -> bool:
        """Check if an operation is likely reversible."""
        name_lower = func.__name__.lower()
        irreversible = ["delete", "drop", "destroy", "remove"]
        return not any(word in name_lower for word in irreversible)

    def request_confirmation(
        self,
        metadata: OperationMetadata,
    ) -> ConfirmationResult:
        """Request user confirmation for an operation.

        Args:
            metadata: Operation metadata

        Returns:
            ConfirmationResult with user's decision
        """
        # Auto-approve safe operations if configured
        if self.auto_approve_safe and metadata.risk_level == OperationRisk.SAFE:
            return ConfirmationResult.approve()

        # Use custom callback if set
        if self._confirmation_callback:
            return self._confirmation_callback(metadata)

        # Generate prompt and request confirmation
        prompt = ConfirmationPrompt(metadata)
        print(prompt.generate())

        # Default CLI-based confirmation
        return self._cli_confirmation(metadata.risk_level, metadata.name)

    def _cli_confirmation(
        self,
        risk: OperationRisk,
        operation_name: str,
    ) -> ConfirmationResult:
        """Get confirmation via CLI input."""
        try:
            if risk == OperationRisk.LOW:
                response = input("Continue? [Y/n]: ").strip().lower()
                if response in ("", "y", "yes"):
                    return ConfirmationResult.approve()
                return ConfirmationResult.deny()

            elif risk == OperationRisk.MEDIUM:
                response = input("Type 'yes' to confirm: ").strip().lower()
                if response == "yes":
                    return ConfirmationResult.approve()
                return ConfirmationResult.deny()

            elif risk == OperationRisk.HIGH:
                expected = operation_name.upper()
                response = input(f"Type '{expected}' to confirm: ").strip()
                if response.upper() == expected:
                    return ConfirmationResult.approve()
                return ConfirmationResult.deny()

            else:  # CRITICAL
                expected = f"CONFIRM {operation_name.upper()}"
                response = input(f"Type '{expected}' to proceed: ").strip()
                if response.upper() == expected:
                    return ConfirmationResult.approve()
                return ConfirmationResult.deny()

        except (EOFError, KeyboardInterrupt):
            return ConfirmationResult.deny()

    def check(
        self,
        risk: OperationRisk = OperationRisk.LOW,
        **metadata_kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator to add pre-flight checking to a function.

        Args:
            risk: Risk level for the operation
            **metadata_kwargs: Additional metadata fields

        Returns:
            Decorated function

        Example:
            ```python
            @checker.check(risk=OperationRisk.HIGH, reversible=False)
            def delete_user(user_id: str):
                return db.delete(user_id)
            ```
        """
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            # Store risk for assessment
            func._preflight_risk = risk  # type: ignore

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Assess operation
                metadata = self.assess_operation(func, args, kwargs)

                # Override with decorator settings
                metadata.risk_level = risk
                for key, value in metadata_kwargs.items():
                    if hasattr(metadata, key):
                        setattr(metadata, key, value)

                # Request confirmation
                result = self.request_confirmation(metadata)

                if not result.approved:
                    raise PermissionError(
                        f"Operation '{metadata.name}' was not approved"
                    )

                # Execute the function
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Global pre-flight checker instance
_global_checker = PreflightChecker()


def preflight_check(
    risk: OperationRisk = OperationRisk.LOW,
    **metadata_kwargs: Any,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to add pre-flight confirmation to a function.

    Uses the global pre-flight checker.

    Args:
        risk: Risk level for the operation
        **metadata_kwargs: Additional metadata fields

    Example:
        ```python
        @preflight_check(risk=OperationRisk.HIGH)
        def delete_database():
            db.drop_all_tables()
        ```
    """
    return _global_checker.check(risk=risk, **metadata_kwargs)


def confirm_before_execute(
    func: Callable[P, R],
    risk: OperationRisk = OperationRisk.LOW,
) -> Callable[P, R]:
    """Simple decorator to confirm before executing a function.

    Example:
        ```python
        @confirm_before_execute(risk=OperationRisk.MEDIUM)
        def clear_cache():
            cache.clear()
        ```
    """
    return preflight_check(risk=risk)(func)


__all__ = [
    "OperationRisk",
    "OperationCategory",
    "OperationMetadata",
    "ConfirmationResult",
    "ConfirmationPrompt",
    "PreflightChecker",
    # Convenience functions
    "preflight_check",
    "confirm_before_execute",
    "_global_checker",
]
