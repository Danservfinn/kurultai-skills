"""
Manifest validation logic for Kurultai CLI.

This module provides validation functions and exception classes for
parsing and validating skill manifests.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml
from pydantic import ValidationError as PydanticValidationError

from kurultai.models.skill import (
    Dependency,
    SkillManifest,
    SkillType,
    validate_semver,
)


class ManifestValidationError(Exception):
    """Exception raised when a skill manifest fails validation.

    Attributes:
        message: Human-readable error message
        field: The field that failed validation (if applicable)
        errors: List of all validation errors
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.field = field
        self.errors = errors or []

    def __str__(self) -> str:
        if self.field:
            return f"Validation error in field '{self.field}': {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "message": self.message,
            "field": self.field,
            "errors": self.errors,
        }


class ValidationError:
    """Represents a single validation error.

    Attributes:
        message: Error message
        field: Field path where error occurred
        error_type: Type of validation error
        value: The invalid value (if applicable)
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_type: str = "validation_error",
        value: Any = None,
    ):
        self.message = message
        self.field = field
        self.error_type = error_type
        self.value = value

    def __str__(self) -> str:
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "message": self.message,
            "type": self.error_type,
        }
        if self.field:
            result["field"] = self.field
        if self.value is not None:
            result["value"] = str(self.value)
        return result


class ValidationErrorCollection:
    """Collection of validation errors.

    Provides methods for collecting, formatting, and reporting multiple
    validation errors together.
    """

    def __init__(self):
        self.errors: List[ValidationError] = []

    def add(
        self,
        message: str,
        field: Optional[str] = None,
        error_type: str = "validation_error",
        value: Any = None,
    ) -> None:
        """Add a validation error to the collection."""
        self.errors.append(ValidationError(message, field, error_type, value))

    def add_error(self, error: ValidationError) -> None:
        """Add a ValidationError object to the collection."""
        self.errors.append(error)

    def extend(self, errors: List[ValidationError]) -> None:
        """Extend the collection with multiple errors."""
        self.errors.extend(errors)

    def has_errors(self) -> bool:
        """Check if there are any errors in the collection."""
        return len(self.errors) > 0

    def is_valid(self) -> bool:
        """Check if the collection has no errors."""
        return len(self.errors) == 0

    def get_errors_for_field(self, field: str) -> List[ValidationError]:
        """Get all errors for a specific field."""
        return [e for e in self.errors if e.field == field]

    def get_field_names(self) -> Set[str]:
        """Get all field names that have errors."""
        return {e.field for e in self.errors if e.field is not None}

    def raise_if_invalid(self, message: Optional[str] = None) -> None:
        """Raise ManifestValidationError if there are any errors."""
        if self.has_errors():
            raise ManifestValidationError(
                message=message or f"Validation failed with {len(self.errors)} error(s)",
                errors=[e.to_dict() for e in self.errors],
            )

    def format_errors(self) -> str:
        """Format all errors into a human-readable string."""
        if not self.errors:
            return "No validation errors."

        lines = [f"Validation failed with {len(self.errors)} error(s):"]
        for i, error in enumerate(self.errors, 1):
            prefix = f"  {i}."
            if error.field:
                lines.append(f"{prefix} [{error.field}] {error.message}")
            else:
                lines.append(f"{prefix} {error.message}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.errors)

    def __iter__(self):
        return iter(self.errors)

    def __bool__(self) -> bool:
        return self.is_valid()


def validate_skill_name(name: str) -> bool:
    """Validate a skill name follows naming conventions.

    Skill names must:
    - Start with a lowercase letter
    - Contain only lowercase letters, numbers, hyphens, and underscores
    - Be between 1 and 100 characters

    Args:
        name: The skill name to validate.

    Returns:
        True if the name is valid, False otherwise.
    """
    if not name:
        return False
    if len(name) > 100:
        return False
    return bool(re.match(r"^[a-z][a-z0-9-_]*$", name))


def validate_skill_type(skill_type: str) -> bool:
    """Validate a skill type value.

    Args:
        skill_type: The type string to validate.

    Returns:
        True if the type is valid, False otherwise.
    """
    try:
        SkillType(skill_type)
        return True
    except ValueError:
        return False


def validate_dependencies(dependencies: Dict[str, Any]) -> ValidationErrorCollection:
    """Validate a dependencies dictionary.

    Args:
        dependencies: Dictionary mapping dependency names to version constraints.

    Returns:
        ValidationErrorCollection containing any validation errors.
    """
    errors = ValidationErrorCollection()

    if not isinstance(dependencies, dict):
        errors.add(
            "Dependencies must be a dictionary",
            field="dependencies",
            error_type="type_error",
            value=dependencies,
        )
        return errors

    valid_prefixes = [">=", "<=", ">", "<", "^", "~", "="]

    for name, constraint in dependencies.items():
        # Validate dependency name
        if not validate_skill_name(name):
            errors.add(
                f"Invalid dependency name: '{name}'. Must start with lowercase letter "
                "and contain only lowercase letters, numbers, hyphens, and underscores",
                field=f"dependencies.{name}",
                error_type="invalid_name",
                value=name,
            )

        # Validate constraint
        if not isinstance(constraint, str):
            errors.add(
                f"Version constraint for '{name}' must be a string",
                field=f"dependencies.{name}",
                error_type="type_error",
                value=constraint,
            )
            continue

        # Handle optional prefix
        constraint_str = constraint
        if constraint_str.startswith("optional:"):
            constraint_str = constraint_str[9:]

        # Check for valid prefix
        version_part = constraint_str
        for prefix in valid_prefixes:
            if constraint_str.startswith(prefix):
                version_part = constraint_str[len(prefix) :]
                break

        # Validate version part
        if not validate_semver(version_part):
            errors.add(
                f"Invalid version constraint: '{constraint}'. "
                "Must be a valid semantic version with optional prefix",
                field=f"dependencies.{name}",
                error_type="invalid_version",
                value=constraint,
            )

    return errors


def validate_entry_point(entry_point: str) -> ValidationErrorCollection:
    """Validate an entry point path.

    Args:
        entry_point: The entry point path to validate.

    Returns:
        ValidationErrorCollection containing any validation errors.
    """
    errors = ValidationErrorCollection()

    if not isinstance(entry_point, str):
        errors.add(
            "Entry point must be a string",
            field="entry_point",
            error_type="type_error",
        )
        return errors

    if not entry_point:
        errors.add(
            "Entry point cannot be empty",
            field="entry_point",
            error_type="empty_value",
        )
        return errors

    # Check for dangerous patterns
    dangerous_patterns = ["..", "~", "$", "`", "|", ";", "&"]
    for pattern in dangerous_patterns:
        if pattern in entry_point:
            errors.add(
                f"Entry point contains dangerous pattern: '{pattern}'",
                field="entry_point",
                error_type="security_error",
                value=entry_point,
            )

    return errors


def validate_tags(tags: List[Any]) -> ValidationErrorCollection:
    """Validate a list of tags.

    Args:
        tags: List of tag strings to validate.

    Returns:
        ValidationErrorCollection containing any validation errors.
    """
    errors = ValidationErrorCollection()

    if not isinstance(tags, (list, tuple)):
        errors.add(
            "Tags must be a list",
            field="tags",
            error_type="type_error",
            value=tags,
        )
        return errors

    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            errors.add(
                f"Tag at index {i} must be a string",
                field=f"tags[{i}]",
                error_type="type_error",
                value=tag,
            )
            continue

        tag = tag.strip().lower()
        if not tag:
            errors.add(
                f"Tag at index {i} cannot be empty",
                field=f"tags[{i}]",
                error_type="empty_value",
            )
            continue

        if not re.match(r"^[a-z0-9-_]+$", tag):
            errors.add(
                f"Tag '{tag}' must contain only lowercase letters, "
                "numbers, hyphens, and underscores",
                field=f"tags[{i}]",
                error_type="invalid_format",
                value=tag,
            )

    return errors


def validate_url(url: str, field_name: str = "url") -> ValidationErrorCollection:
    """Validate a URL string.

    Args:
        url: The URL to validate.
        field_name: The name of the field being validated (for error messages).

    Returns:
        ValidationErrorCollection containing any validation errors.
    """
    errors = ValidationErrorCollection()

    if not isinstance(url, str):
        errors.add(
            f"{field_name} must be a string",
            field=field_name,
            error_type="type_error",
            value=url,
        )
        return errors

    if not url:
        errors.add(
            f"{field_name} cannot be empty",
            field=field_name,
            error_type="empty_value",
        )
        return errors

    # Basic URL validation pattern
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        errors.add(
            f"Invalid URL format: '{url}'",
            field=field_name,
            error_type="invalid_format",
            value=url,
        )

    return errors


def validate_manifest_structure(data: Dict[str, Any]) -> ValidationErrorCollection:
    """Validate the basic structure of a manifest dictionary.

    This performs preliminary validation before creating the Pydantic model,
    providing more helpful error messages for common issues.

    Args:
        data: The manifest dictionary to validate.

    Returns:
        ValidationErrorCollection containing any validation errors.
    """
    errors = ValidationErrorCollection()

    # Check if data is a dictionary
    if not isinstance(data, dict):
        errors.add(
            "Manifest must be a YAML object/dictionary",
            error_type="type_error",
            value=type(data).__name__,
        )
        return errors

    # Check required fields
    required_fields = ["name", "version", "description", "author", "type"]
    for field in required_fields:
        if field not in data:
            errors.add(
                f"Required field '{field}' is missing",
                field=field,
                error_type="missing_field",
            )
        elif data[field] is None:
            errors.add(
                f"Required field '{field}' cannot be null",
                field=field,
                error_type="null_value",
            )
        elif isinstance(data[field], str) and not data[field].strip():
            errors.add(
                f"Required field '{field}' cannot be empty",
                field=field,
                error_type="empty_value",
            )

    # If we have missing required fields, don't continue with other validations
    if errors.has_errors():
        return errors

    # Validate name
    if "name" in data and not validate_skill_name(data["name"]):
        errors.add(
            f"Invalid skill name: '{data['name']}'. Must start with lowercase letter "
            "and contain only lowercase letters, numbers, hyphens, and underscores",
            field="name",
            error_type="invalid_name",
            value=data["name"],
        )

    # Validate version
    if "version" in data and not validate_semver(data["version"]):
        errors.add(
            f"Invalid semantic version: '{data['version']}'. "
            "Expected format: MAJOR.MINOR.PATCH[-prerelease][+build]",
            field="version",
            error_type="invalid_version",
            value=data["version"],
        )

    # Validate type
    if "type" in data and not validate_skill_type(data["type"]):
        valid_types = [t.value for t in SkillType]
        errors.add(
            f"Invalid skill type: '{data['type']}'. Must be one of: {valid_types}",
            field="type",
            error_type="invalid_type",
            value=data["type"],
        )

    # Validate description length
    if "description" in data and isinstance(data["description"], str):
        if len(data["description"].strip()) < 10:
            errors.add(
                "Description must be at least 10 characters long",
                field="description",
                error_type="too_short",
                value=data["description"],
            )

    # Validate optional fields
    if "dependencies" in data:
        dep_errors = validate_dependencies(data["dependencies"])
        errors.extend(list(dep_errors))

    if "entry_point" in data and data["entry_point"] is not None:
        ep_errors = validate_entry_point(data["entry_point"])
        errors.extend(list(ep_errors))

    if "tags" in data:
        tag_errors = validate_tags(data["tags"])
        errors.extend(list(tag_errors))

    if "homepage" in data and data["homepage"] is not None:
        url_errors = validate_url(data["homepage"], "homepage")
        errors.extend(list(url_errors))

    if "repository" in data and data["repository"] is not None:
        url_errors = validate_url(data["repository"], "repository")
        errors.extend(list(url_errors))

    return errors


def validate_manifest(data: Union[Dict[str, Any], str, Path]) -> SkillManifest:
    """Validate and parse a skill manifest.

    This is the main entry point for manifest validation. It accepts
    a dictionary, YAML string, or file path and returns a validated
    SkillManifest object.

    Args:
        data: Manifest data as dictionary, YAML string, or file path.

    Returns:
        Validated SkillManifest object.

    Raises:
        ManifestValidationError: If validation fails with helpful error messages.
    """
    # Handle file path
    if isinstance(data, (str, Path)) and not isinstance(data, dict):
        path = Path(data)
        if path.exists() and path.suffix in (".yaml", ".yml"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ManifestValidationError(
                    f"Failed to parse YAML file: {e}",
                    errors=[{"message": str(e), "type": "yaml_parse_error"}],
                )
            except IOError as e:
                raise ManifestValidationError(
                    f"Failed to read manifest file: {e}",
                    errors=[{"message": str(e), "type": "file_error"}],
                )

    # Handle YAML string
    if isinstance(data, str):
        try:
            data = yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ManifestValidationError(
                f"Failed to parse YAML: {e}",
                errors=[{"message": str(e), "type": "yaml_parse_error"}],
            )

    # Preliminary structure validation
    structure_errors = validate_manifest_structure(data)
    if structure_errors.has_errors():
        raise ManifestValidationError(
            message=structure_errors.format_errors(),
            errors=[e.to_dict() for e in structure_errors.errors],
        )

    # Pydantic model validation
    try:
        manifest = SkillManifest.model_validate(data)
    except PydanticValidationError as e:
        # Convert Pydantic errors to our format
        errors = []
        for err in e.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append({
                "field": field,
                "message": err["msg"],
                "type": err["type"],
                "value": str(err.get("input", "")),
            })

        raise ManifestValidationError(
            message=f"Manifest validation failed: {e.title}",
            errors=errors,
        )

    return manifest


def validate_manifest_file(path: Union[str, Path]) -> SkillManifest:
    """Validate a skill manifest file.

    Convenience function for validating a manifest from a file path.

    Args:
        path: Path to the YAML manifest file.

    Returns:
        Validated SkillManifest object.

    Raises:
        ManifestValidationError: If validation fails.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    if not path.is_file():
        raise ManifestValidationError(
            f"Path is not a file: {path}",
            errors=[{"message": "Not a file", "type": "not_a_file"}],
        )

    return validate_manifest(path)


def validate_manifest_dict(data: Dict[str, Any]) -> SkillManifest:
    """Validate a skill manifest dictionary.

    Convenience function for validating a manifest from a dictionary.

    Args:
        data: Manifest data as dictionary.

    Returns:
        Validated SkillManifest object.

    Raises:
        ManifestValidationError: If validation fails.
    """
    return validate_manifest(data)
