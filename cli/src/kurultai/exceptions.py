"""Custom exceptions for Kurultai CLI.

This module defines the exception hierarchy for the Kurultai CLI,
providing specific error types for different failure scenarios.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class KurultaiError(Exception):
    """Base exception for all Kurultai CLI errors.

    Attributes:
        message: Human-readable error description
        details: Additional error context or data
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            details: Additional error context or data
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class CircularDependencyError(KurultaiError):
    """Raised when a circular dependency is detected.

    Attributes:
        cycle: List of skill names forming the circular dependency
    """

    def __init__(
        self,
        message: str,
        cycle: List[str],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            cycle: List of skill names forming the circular dependency
            details: Additional error context
        """
        super().__init__(message, details)
        self.cycle = cycle

    def __str__(self) -> str:
        """String representation showing the dependency cycle."""
        cycle_str = " -> ".join(self.cycle + [self.cycle[0]])
        return f"{self.message}: {cycle_str}"


class DependencyConflictError(KurultaiError):
    """Raised when conflicting versions of the same skill are required.

    Attributes:
        skill_name: Name of the skill with conflicting versions
        required_versions: List of version constraints causing the conflict
        resolution_path: Dependency path showing how conflict was detected
    """

    def __init__(
        self,
        message: str,
        skill_name: str,
        required_versions: List[str],
        resolution_path: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            skill_name: Name of the skill with conflicting versions
            required_versions: List of version constraints causing the conflict
            resolution_path: Dependency path showing how conflict was detected
            details: Additional error context
        """
        super().__init__(message, details)
        self.skill_name = skill_name
        self.required_versions = required_versions
        self.resolution_path = resolution_path or []

    def __str__(self) -> str:
        """String representation showing the conflict details."""
        versions_str = ", ".join(f"'{v}'" for v in self.required_versions)
        path_str = ""
        if self.resolution_path:
            path_str = f" (via: {' -> '.join(self.resolution_path)})"
        return f"{self.message}: {self.skill_name} requires versions {versions_str}{path_str}"


class ResolutionError(KurultaiError):
    """Raised when dependency resolution fails.

    This can occur due to network issues, registry unavailability,
    or inability to satisfy version constraints.
    """

    def __init__(
        self,
        message: str,
        skill_name: Optional[str] = None,
        version_constraint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            skill_name: Name of the skill that failed to resolve
            version_constraint: The version constraint that could not be satisfied
            details: Additional error context
        """
        super().__init__(message, details)
        self.skill_name = skill_name
        self.version_constraint = version_constraint

    def __str__(self) -> str:
        """String representation including resolution context."""
        if self.skill_name and self.version_constraint:
            return f"{self.message}: {self.skill_name}@{self.version_constraint}"
        elif self.skill_name:
            return f"{self.message}: {self.skill_name}"
        return self.message


class SkillNotFoundError(KurultaiError):
    """Raised when a skill cannot be found in the registry.

    Attributes:
        skill_name: Name of the skill that was not found
        version_constraint: Optional version constraint that was requested
        registry_url: URL of the registry that was searched
    """

    def __init__(
        self,
        message: str,
        skill_name: str,
        version_constraint: Optional[str] = None,
        registry_url: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            skill_name: Name of the skill that was not found
            version_constraint: Optional version constraint that was requested
            registry_url: URL of the registry that was searched
            details: Additional error context
        """
        super().__init__(message, details)
        self.skill_name = skill_name
        self.version_constraint = version_constraint
        self.registry_url = registry_url

    def __str__(self) -> str:
        """String representation including skill and registry info."""
        version_str = f"@{self.version_constraint}" if self.version_constraint else ""
        registry_str = f" in {self.registry_url}" if self.registry_url else ""
        return f"{self.message}: {self.skill_name}{version_str}{registry_str}"


class LockFileError(KurultaiError):
    """Raised when lock file operations fail.

    This includes parsing errors, write failures, or version mismatches.
    """

    def __init__(
        self,
        message: str,
        lock_file_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            lock_file_path: Path to the lock file that caused the error
            details: Additional error context
        """
        super().__init__(message, details)
        self.lock_file_path = lock_file_path

    def __str__(self) -> str:
        """String representation including lock file path."""
        if self.lock_file_path:
            return f"{self.message} (lock file: {self.lock_file_path})"
        return self.message


class ValidationError(KurultaiError):
    """Raised when skill manifest validation fails."""

    pass


class ConfigError(KurultaiError):
    """Raised when configuration loading or validation fails."""

    pass
