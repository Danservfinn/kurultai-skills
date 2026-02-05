"""
Skill manifest models for Kurultai CLI.

This module defines Pydantic models for parsing and validating skill manifests.
"""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class SkillType(str, Enum):
    """Valid skill types in the Kurultai ecosystem."""

    ENGINE = "engine"
    SKILL = "skill"
    WORKFLOW = "workflow"


class Dependency(BaseModel):
    """Represents a parsed skill dependency.

    Attributes:
        name: The name of the dependency
        version_constraint: The version constraint string (e.g., ">=1.0.0", "^2.0.0")
        is_optional: Whether this is an optional dependency
    """

    name: str = Field(..., description="Name of the dependency")
    version_constraint: str = Field(
        ..., description="Version constraint (e.g., '>=1.0.0', '^2.0.0')"
    )
    is_optional: bool = Field(default=False, description="Whether dependency is optional")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate dependency name follows naming conventions."""
        if not v:
            raise ValueError("Dependency name cannot be empty")
        if not re.match(r"^[a-z][a-z0-9-_]*$", v):
            raise ValueError(
                f"Dependency name '{v}' must start with lowercase letter and "
                "contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v

    @field_validator("version_constraint")
    @classmethod
    def validate_version_constraint(cls, v: str) -> str:
        """Validate version constraint format."""
        if not v:
            raise ValueError("Version constraint cannot be empty")

        # Valid constraint prefixes
        valid_prefixes = [">=", "<=", ">", "<", "^", "~", "="]

        # Check if it starts with a valid prefix or is a plain version
        has_prefix = any(v.startswith(prefix) for prefix in valid_prefixes)

        if has_prefix:
            version_part = v.lstrip("".join(valid_prefixes))
        else:
            version_part = v

        # Validate the version part is valid semver
        if not validate_semver(version_part):
            raise ValueError(
                f"Version constraint '{v}' does not contain a valid semantic version"
            )

        return v

    def __str__(self) -> str:
        """String representation of the dependency."""
        prefix = "optional:" if self.is_optional else ""
        return f"{prefix}{self.name}@{self.version_constraint}"

    def __hash__(self) -> int:
        """Make Dependency hashable for use in sets."""
        return hash((self.name, self.version_constraint, self.is_optional))

    def __eq__(self, other: object) -> bool:
        """Equality comparison for Dependency."""
        if not isinstance(other, Dependency):
            return NotImplemented
        return (
            self.name == other.name
            and self.version_constraint == other.version_constraint
            and self.is_optional == other.is_optional
        )


class SkillManifest(BaseModel):
    """Pydantic model for skill manifest validation.

    This model defines the complete schema for skill.yaml files in the
    Kurultai ecosystem. It supports engines, skills, and workflows.

    Attributes:
        name: Unique identifier for the skill (required)
        version: Semantic version string (required)
        description: Human-readable description (required)
        author: Author or organization name (required)
        type: Skill type - "engine", "skill", or "workflow" (required)
        dependencies: Mapping of dependency names to version constraints (optional)
        entry_point: Main entry point for the skill (optional)
        prompts_dir: Directory containing prompt templates (default: "prompts")
        tags: List of categorization tags (optional)
        homepage: URL to project homepage (optional)
        repository: URL to source code repository (optional)
    """

    # Required fields
    name: str = Field(
        ...,
        description="Unique skill name (lowercase letters, numbers, hyphens, underscores)",
        min_length=1,
        max_length=100,
    )
    version: str = Field(
        ...,
        description="Semantic version (e.g., '1.0.0', '2.1.0-beta.1')",
    )
    description: str = Field(
        ...,
        description="Human-readable description of the skill",
        min_length=10,
        max_length=1000,
    )
    author: str = Field(
        ...,
        description="Author or organization name",
        min_length=1,
        max_length=100,
    )
    type: SkillType = Field(
        ...,
        description="Type of skill: engine, skill, or workflow",
    )

    # Optional fields
    dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="Dependency name to version constraint mapping",
    )
    entry_point: Optional[str] = Field(
        default=None,
        description="Main entry point file or module path",
    )
    prompts_dir: str = Field(
        default="prompts",
        description="Directory containing prompt templates",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Categorization tags for discovery",
    )
    homepage: Optional[str] = Field(
        default=None,
        description="URL to project homepage",
    )
    repository: Optional[str] = Field(
        default=None,
        description="URL to source code repository",
    )

    # Internal field for parsed dependencies
    _parsed_dependencies: Optional[List[Dependency]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate skill name follows naming conventions."""
        if not v:
            raise ValueError("Skill name cannot be empty")
        if not re.match(r"^[a-z][a-z0-9-_]*$", v):
            raise ValueError(
                f"Skill name '{v}' must start with lowercase letter and "
                "contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version follows semantic versioning."""
        if not validate_semver(v):
            raise ValueError(
                f"Version '{v}' is not a valid semantic version. "
                "Expected format: MAJOR.MINOR.PATCH[-prerelease][+build]"
            )
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description meets minimum requirements."""
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags."""
        normalized = []
        for tag in v:
            tag = tag.strip().lower()
            if tag:
                if not re.match(r"^[a-z0-9-_]+$", tag):
                    raise ValueError(
                        f"Tag '{tag}' must contain only lowercase letters, "
                        "numbers, hyphens, and underscores"
                    )
                normalized.append(tag)
        return normalized

    @field_validator("homepage", "repository")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v is None:
            return v

        # Basic URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(v):
            raise ValueError(f"Invalid URL format: '{v}'")

        return v

    @model_validator(mode="after")
    def validate_entry_point_for_type(self) -> SkillManifest:
        """Validate entry point requirements based on skill type."""
        # Engines and workflows typically require entry points
        if self.type in (SkillType.ENGINE, SkillType.WORKFLOW) and not self.entry_point:
            # This is a warning-level validation, not an error
            # We don't raise here to allow flexibility in manifest design
            pass

        # If entry_point is provided, validate it has a reasonable format
        if self.entry_point:
            if "/" in self.entry_point or "\\" in self.entry_point:
                # It's a path - validate it doesn't contain dangerous patterns
                dangerous = ["..", "~", "$", "`"]
                for pattern in dangerous:
                    if pattern in self.entry_point:
                        raise ValueError(
                            f"Entry point contains dangerous pattern: '{pattern}'"
                        )

        return self

    @property
    def parsed_dependencies(self) -> List[Dependency]:
        """Get parsed dependency objects.

        Returns:
            List of Dependency objects parsed from the dependencies dict.
        """
        if self._parsed_dependencies is None:
            self._parsed_dependencies = []
            for name, constraint in self.dependencies.items():
                is_optional = constraint.startswith("optional:")
                if is_optional:
                    constraint = constraint[9:]  # Remove "optional:" prefix

                self._parsed_dependencies.append(
                    Dependency(
                        name=name,
                        version_constraint=constraint,
                        is_optional=is_optional,
                    )
                )
        return self._parsed_dependencies

    def get_required_dependencies(self) -> List[Dependency]:
        """Get only the required (non-optional) dependencies.

        Returns:
            List of required Dependency objects.
        """
        return [dep for dep in self.parsed_dependencies if not dep.is_optional]

    def get_optional_dependencies(self) -> List[Dependency]:
        """Get only the optional dependencies.

        Returns:
            List of optional Dependency objects.
        """
        return [dep for dep in self.parsed_dependencies if dep.is_optional]

    def has_dependency(self, name: str) -> bool:
        """Check if the skill has a specific dependency.

        Args:
            name: The dependency name to check for.

        Returns:
            True if the dependency exists, False otherwise.
        """
        return any(dep.name == name for dep in self.parsed_dependencies)

    def get_dependency(self, name: str) -> Optional[Dependency]:
        """Get a specific dependency by name.

        Args:
            name: The dependency name to look up.

        Returns:
            The Dependency object if found, None otherwise.
        """
        for dep in self.parsed_dependencies:
            if dep.name == name:
                return dep
        return None

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert manifest to a dictionary suitable for YAML serialization.

        Returns:
            Dictionary representation of the manifest.
        """
        data = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "type": self.type.value,
        }

        if self.dependencies:
            data["dependencies"] = self.dependencies

        if self.entry_point:
            data["entry_point"] = self.entry_point

        if self.prompts_dir != "prompts":
            data["prompts_dir"] = self.prompts_dir

        if self.tags:
            data["tags"] = self.tags

        if self.homepage:
            data["homepage"] = self.homepage

        if self.repository:
            data["repository"] = self.repository

        return data

    def __str__(self) -> str:
        """String representation of the skill manifest."""
        return f"{self.name}@{self.version} ({self.type.value})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"SkillManifest("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"type='{self.type.value}', "
            f"author='{self.author}'"
            f")"
        )


def validate_semver(version: str) -> bool:
    """Validate a semantic version string.

    Follows the Semantic Versioning 2.0.0 specification:
    https://semver.org/

    Valid formats:
        - 1.0.0
        - 1.0.0-alpha
        - 1.0.0-alpha.1
        - 1.0.0-0.3.7
        - 1.0.0-x.7.z.92
        - 1.0.0+build
        - 1.0.0+build.1
        - 1.0.0-alpha+build

    Args:
        version: The version string to validate.

    Returns:
        True if the version is valid semver, False otherwise.
    """
    if not version:
        return False

    # Semver 2.0.0 regex pattern
    # Matches: MAJOR.MINOR.PATCH[-prerelease][+build]
    semver_pattern = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"  # MAJOR.MINOR.PATCH
        r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"  # prerelease
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # build metadata
    )

    return bool(semver_pattern.match(version))


def parse_semver(version: str) -> Optional[Dict[str, Union[int, str, None]]]:
    """Parse a semantic version string into its components.

    Args:
        version: The version string to parse.

    Returns:
        Dictionary with major, minor, patch, prerelease, and build components,
        or None if the version is invalid.
    """
    if not validate_semver(version):
        return None

    # Extract components
    # First, split by + to separate build metadata
    if "+" in version:
        version_part, build = version.split("+", 1)
    else:
        version_part, build = version, None

    # Then split by - to separate prerelease
    if "-" in version_part:
        core_part, prerelease = version_part.split("-", 1)
    else:
        core_part, prerelease = version_part, None

    # Parse core version numbers
    major, minor, patch = map(int, core_part.split("."))

    return {
        "major": major,
        "minor": minor,
        "patch": patch,
        "prerelease": prerelease,
        "build": build,
    }


def compare_versions(v1: str, v2: str) -> int:
    """Compare two semantic version strings.

    Args:
        v1: First version string.
        v2: Second version string.

    Returns:
        -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2.

    Raises:
        ValueError: If either version is not valid semver.
    """
    p1 = parse_semver(v1)
    p2 = parse_semver(v2)

    if p1 is None:
        raise ValueError(f"Invalid semantic version: '{v1}'")
    if p2 is None:
        raise ValueError(f"Invalid semantic version: '{v2}'")

    # Compare major, minor, patch
    for key in ["major", "minor", "patch"]:
        a = p1[key]  # type: ignore[literal-required]
        b = p2[key]  # type: ignore[literal-required]
        if a < b:
            return -1
        if a > b:
            return 1

    # Compare prerelease versions
    pre1 = p1["prerelease"]
    pre2 = p2["prerelease"]

    # A version without prerelease has higher precedence
    if pre1 is None and pre2 is not None:
        return 1
    if pre1 is not None and pre2 is None:
        return -1
    if pre1 is None and pre2 is None:
        return 0

    # Both have prerelease - compare identifiers
    ids1 = pre1.split(".")  # type: ignore[union-attr]
    ids2 = pre2.split(".")  # type: ignore[union-attr]

    for i in range(min(len(ids1), len(ids2))):
        id1, id2 = ids1[i], ids2[i]

        # Numeric identifiers are compared as integers
        is_num1 = id1.isdigit()
        is_num2 = id2.isdigit()

        if is_num1 and is_num2:
            n1, n2 = int(id1), int(id2)
            if n1 < n2:
                return -1
            if n1 > n2:
                return 1
        elif is_num1:
            # Numeric identifiers have lower precedence
            return -1
        elif is_num2:
            return 1
        else:
            # Compare as strings
            if id1 < id2:
                return -1
            if id1 > id2:
                return 1

    # Longer prerelease has higher precedence if all else equal
    if len(ids1) < len(ids2):
        return -1
    if len(ids1) > len(ids2):
        return 1

    return 0


def satisfies_constraint(version: str, constraint: str) -> bool:
    """Check if a version satisfies a version constraint.

    Supports common constraint formats:
        - Exact: "1.0.0"
        - Greater than: ">1.0.0"
        - Greater than or equal: ">=1.0.0"
        - Less than: "<1.0.0"
        - Less than or equal: "<=1.0.0"
        - Caret (compatible): "^1.0.0" (allows minor/patch updates)
        - Tilde (approximately): "~1.0.0" (allows patch updates)

    Args:
        version: The version to check.
        constraint: The constraint to satisfy.

    Returns:
        True if the version satisfies the constraint.

    Raises:
        ValueError: If version or constraint is invalid.
    """
    if not validate_semver(version):
        raise ValueError(f"Invalid version: '{version}'")

    # Parse the constraint
    constraint = constraint.strip()

    # Handle exact version
    if validate_semver(constraint):
        return compare_versions(version, constraint) == 0

    # Handle prefixed constraints
    prefixes = {
        ">=": lambda v, c: compare_versions(v, c) >= 0,
        "<=": lambda v, c: compare_versions(v, c) <= 0,
        ">": lambda v, c: compare_versions(v, c) > 0,
        "<": lambda v, c: compare_versions(v, c) < 0,
        "=": lambda v, c: compare_versions(v, c) == 0,
    }

    for prefix, comparator in prefixes.items():
        if constraint.startswith(prefix):
            target = constraint[len(prefix) :].strip()
            if not validate_semver(target):
                raise ValueError(f"Invalid version in constraint: '{target}'")
            return comparator(version, target)

    # Handle caret (^) - allows changes that do not modify left-most non-zero digit
    if constraint.startswith("^"):
        target = constraint[1:].strip()
        if not validate_semver(target):
            raise ValueError(f"Invalid version in constraint: '{target}'")

        target_parsed = parse_semver(target)
        version_parsed = parse_semver(version)

        if target_parsed["major"] == 0:
            # 0.x.x - only patch changes allowed
            if version_parsed["minor"] != target_parsed["minor"]:  # type: ignore[literal-required]
                return False
            return version_parsed["patch"] >= target_parsed["patch"]  # type: ignore[literal-required]
        else:
            # 1.x.x or higher - minor/patch changes allowed
            if version_parsed["major"] != target_parsed["major"]:  # type: ignore[literal-required]
                return False
            if version_parsed["minor"] < target_parsed["minor"]:  # type: ignore[literal-required]
                return False
            return True

    # Handle tilde (~) - allows patch-level changes
    if constraint.startswith("~"):
        target = constraint[1:].strip()
        if not validate_semver(target):
            raise ValueError(f"Invalid version in constraint: '{target}'")

        target_parsed = parse_semver(target)
        version_parsed = parse_semver(version)

        if version_parsed["major"] != target_parsed["major"]:  # type: ignore[literal-required]
            return False
        if version_parsed["minor"] != target_parsed["minor"]:  # type: ignore[literal-required]
            return False
        return version_parsed["patch"] >= target_parsed["patch"]  # type: ignore[literal-required]

    raise ValueError(f"Invalid constraint format: '{constraint}'")
