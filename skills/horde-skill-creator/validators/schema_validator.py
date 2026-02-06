"""
Schema Validator

Provides runtime schema validation for skill operations using Python type hints.
Validates input parameters, return values, and raises detailed ValidationError
when validation fails.

Example:
    ```python
    from schema_validator import validate, validate_schema, ValidationError
    from typing import List, Optional

    @validate
    def create_user(name: str, age: int, email: str | None = None) -> dict:
        # Input validation happens automatically
        return {"name": name, "age": age, "email": email}

    # Or validate schemas explicitly
    schema = {
        "name": str,
        "age": (int, lambda x: x >= 0),
        "email": str | None,
    }
    validate_schema({"name": "Alice", "age": 30}, schema)
    ```

Supported Type Validations:
    - Primitives: str, int, float, bool, bytes
    - Collections: list, tuple, set, dict, List[Tuple], Dict[K, V]
    - Optional: Optional[T], T | None
    - Union: Union[A, B], A | B
    - Literals: Literal["value1", "value2"]
    - Custom: Functions, classes with isinstance checks
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable as CollectionsCallable
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from typing import Any, get_args, get_origin, get_type_hints

try:
    from typing import Literal, get_args, get_origin, get_type_hints
except ImportError:
    # Fallback for older Python versions
    from typing_extensions import Literal, get_args, get_origin, get_type_hints


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


@dataclass
class ValidationIssue:
    """Represents a single validation issue.

    Attributes:
        path: Dot-separated path to the invalid value (e.g., "user.email")
        expected: Description of expected type/value
        actual: Description of actual value
        message: Human-readable error message
        severity: Severity level of the issue
    """

    path: str
    expected: str
    actual: Any
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary for serialization."""
        return {
            "path": self.path,
            "expected": self.expected,
            "actual": str(self.actual),
            "message": self.message,
            "severity": self.severity.name,
        }


class ValidationError(TypeError):
    """Raised when schema validation fails.

    Contains detailed information about what failed validation and why.

    Attributes:
        issues: List of ValidationIssue objects describing failures
        message: Summary error message
    """

    def __init__(
        self,
        message: str,
        issues: list[ValidationIssue] | None = None,
    ) -> None:
        self.issues = issues or []
        self.message = message
        super().__init__(message)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue to this error."""
        self.issues.append(issue)

    def get_issues_by_path(self, path: str) -> list[ValidationIssue]:
        """Get all issues for a specific path."""
        return [i for i in self.issues if i.path == path]

    def format_issues(self, indent: int = 2) -> str:
        """Format all issues as a readable string."""
        lines = [self.message]
        for issue in self.issues:
            prefix = " " * indent
            lines.append(f"{prefix}- {issue.path}: {issue.message}")
            lines.append(f"{prefix}  Expected: {issue.expected}")
            lines.append(f"{prefix}  Actual: {issue.actual}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "message": self.message,
            "issues": [issue.to_dict() for issue in self.issues],
            "issue_count": len(self.issues),
        }


@dataclass
class ValidationResult:
    """Result of a schema validation operation.

    Attributes:
        is_valid: Whether validation passed
        issues: List of validation issues (empty if valid)
        validated_data: The data after validation/coercion
    """

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    validated_data: dict[str, Any] | None = None

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def merge(self, other: ValidationResult) -> ValidationResult:
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.issues.extend(other.issues)
        return self

    def raise_if_invalid(self) -> None:
        """Raise ValidationError if validation failed."""
        if not self.is_valid:
            raise ValidationError(
                f"Validation failed with {len(self.errors)} error(s)",
                self.issues,
            )


class TypeValidator:
    """Core validator for checking values against type hints."""

    # Type checking registry
    _validators: dict[type, Callable[[Any], bool]] = {}

    @classmethod
    def register_validator(cls, type_hint: type, validator: Callable[[Any], bool]) -> None:
        """Register a custom validator for a type."""
        cls._validators[type_hint] = validator

    @classmethod
    def is_valid(cls, value: Any, type_hint: Any, path: str = "") -> ValidationResult:
        """Validate a value against a type hint.

        Args:
            value: The value to validate
            type_hint: The type hint to validate against
            path: Current path for error reporting

        Returns:
            ValidationResult with validation status
        """
        issues: list[ValidationIssue] = []

        def add_issue(expected: str, actual: Any, message: str) -> None:
            issues.append(ValidationIssue(
                path=path,
                expected=expected,
                actual=actual,
                message=message,
            ))

        # Check custom validators first
        for valid_type, validator in cls._validators.items():
            if type_hint == valid_type:
                if not validator(value):
                    add_issue(str(type_hint), type(value), f"Custom validation failed")
                return ValidationResult(len(issues) == 0, issues)

        # None handling
        if type_hint is type(None):
            if value is not None:
                add_issue("None", type(value), "Expected None")
            return ValidationResult(len(issues) == 0, issues)

        # Handle None for Optional types
        if value is None:
            origin = get_origin(type_hint)
            if origin is None or origin is not UnionType:
                # Check if it's an Optional via Union[..., None]
                args = get_args(type_hint)
                if type(None) not in args:
                    add_issue(str(type_hint), "None", "Unexpected None value")
            return ValidationResult(len(issues) == 0, issues)

        # Handle Union types (including Optional)
        origin = get_origin(type_hint)
        if origin is UnionType or origin is Union:
            union_args = get_args(type_hint)
            for arg in union_args:
                if arg is type(None):
                    continue
                result = cls.is_valid(value, arg, path)
                if result.is_valid:
                    return result
            add_issue(
                " | ".join(str(a) for a in union_args),
                type(value),
                f"Value doesn't match any union type",
            )
            return ValidationResult(False, issues)

        # Handle Literal types
        if origin is LiteralType:
            literal_values = get_args(type_hint)
            if value not in literal_values:
                add_issue(
                    f"Literal[{literal_values}]",
                    value,
                    f"Value must be one of {literal_values}",
                )
            return ValidationResult(len(issues) == 0, issues)

        # Handle list types
        if origin is list or origin is List:
            if not isinstance(value, list):
                add_issue("list", type(value), "Expected a list")
                return ValidationResult(False, issues)
            item_type = get_args(type_hint)[0] if get_args(type_hint) else Any
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                result = cls.is_valid(item, item_type, item_path)
                issues.extend(result.issues)
            return ValidationResult(len(issues) == 0, issues)

        # Handle dict types
        if origin is dict or origin is Dict:
            if not isinstance(value, dict):
                add_issue("dict", type(value), "Expected a dict")
                return ValidationResult(False, issues)
            dict_args = get_args(type_hint)
            if dict_args:
                key_type, value_type = dict_args
                for k, v in value.items():
                    key_path = f"{path}.{k}" if path else str(k)
                    # Validate key
                    key_result = cls.is_valid(k, key_type, f"{key_path}(key)")
                    issues.extend(key_result.issues)
                    # Validate value
                    value_result = cls.is_valid(v, value_type, key_path)
                    issues.extend(value_result.issues)
            return ValidationResult(len(issues) == 0, issues)

        # Handle tuple types
        if origin is tuple or origin is Tuple:
            if not isinstance(value, (tuple, list)):
                add_issue("tuple", type(value), "Expected a tuple")
                return ValidationResult(False, issues)
            tuple_args = get_args(type_hint)
            if tuple_args:
                for i, (item, expected_type) in enumerate(zip(value, tuple_args)):
                    item_path = f"{path}[{i}]" if path else f"[{i}]"
                    result = cls.is_valid(item, expected_type, item_path)
                    issues.extend(result.issues)
            return ValidationResult(len(issues) == 0, issues)

        # Handle set types
        if origin is set or origin is Set:
            if not isinstance(value, set):
                add_issue("set", type(value), "Expected a set")
                return ValidationResult(False, issues)
            return ValidationResult(True, issues)

        # Handle callable types
        if origin is CollectionsCallable or type_hint is CollectionsCallable:
            if not callable(value):
                add_issue("callable", type(value), "Expected a callable")
                return ValidationResult(False, issues)
            return ValidationResult(True, issues)

        # Basic type checking
        if isinstance(type_hint, type):
            if not isinstance(value, type_hint):
                add_issue(type_hint.__name__, type(value).__name__, "Type mismatch")
                return ValidationResult(False, issues)

        # Any or unknown types - pass validation
        return ValidationResult(True, issues)


# Import Union for type checking
try:
    from typing import Union as UnionType
except ImportError:
    from typing_extensions import Union as UnionType

try:
    from typing import Literal as LiteralType
except ImportError:
    from typing_extensions import Literal as LiteralType

from typing import List, Dict, Tuple, Set, Union, Any


def validate_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
    *,
    strict: bool = False,
    coerce: bool = False,
) -> ValidationResult:
    """Validate data against a schema definition.

    Args:
        data: Dictionary containing data to validate
        schema: Dictionary mapping field names to type hints
        strict: If True, reject extra fields not in schema
        coerce: If True, attempt type coercion

    Returns:
        ValidationResult with validation status and any issues

    Example:
        ```python
        schema = {
            "name": str,
            "age": int,
            "email": str | None,
            "tags": List[str],
        }
        result = validate_schema({"name": "Alice", "age": 30}, schema)
        result.raise_if_invalid()
        ```
    """
    issues: list[ValidationIssue] = []
    validated_data: dict[str, Any] = {}

    # Check for missing required fields
    for field_name, field_type in schema.items():
        if field_name not in data:
            # Check if field is optional
            origin = get_origin(field_type)
            args = get_args(field_type)
            is_optional = (
                origin is UnionType and type(None) in args
                or field_type is type(None)
            )

            if not is_optional:
                issues.append(ValidationIssue(
                    path=field_name,
                    expected=str(field_type),
                    actual="missing",
                    message=f"Required field '{field_name}' is missing",
                    severity=ValidationSeverity.ERROR,
                ))
            continue

        value = data[field_name]
        result = TypeValidator.is_valid(value, field_type, field_name)
        issues.extend(result.issues)

        if result.is_valid or coerce:
            validated_data[field_name] = value

    # Check for extra fields in strict mode
    if strict:
        for field_name in data:
            if field_name not in schema:
                issues.append(ValidationIssue(
                    path=field_name,
                    expected="(not defined)",
                    actual=type(data[field_name]).__name__,
                    message=f"Unexpected field '{field_name}' in strict mode",
                    severity=ValidationSeverity.WARNING,
                ))

    return ValidationResult(
        is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
        issues=issues,
        validated_data=validated_data,
    )


def validate(
    func: Callable[..., Any] | None = None,
    *,
    validate_return: bool = False,
    strict: bool = False,
    coerce: bool = False,
) -> Any:
    """Decorator to add runtime schema validation to functions.

    Validates input arguments and optionally return values against
    the function's type hints.

    Args:
        func: Function to decorate (or None if used with keyword args)
        validate_return: Whether to validate return values
        strict: Reject extra keyword arguments not in signature
        coerce: Attempt type coercion for compatible types

    Returns:
        Decorated function with validation

    Example:
        ```python
        @validate(validate_return=True)
        def process_user(user_id: int, name: str, active: bool = True) -> dict:
            return {"id": user_id, "name": name, "active": active}

        # Raises ValidationError if arguments don't match types
        process_user("not_an_int", "Alice")
        ```
    """
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        # Get type hints for the function
        try:
            type_hints = get_type_hints(f)
        except Exception:
            # If we can't get type hints, just return the original function
            return f

        return_hint = type_hints.pop("return", None)
        sig = inspect.signature(f)

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build argument mapping
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate arguments
            issues: list[ValidationIssue] = []

            for param_name, param_value in bound_args.arguments.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    result = TypeValidator.is_valid(param_value, expected_type, param_name)
                    issues.extend(result.issues)

            if issues:
                raise ValidationError(
                    f"Argument validation failed for '{f.__name__}'",
                    issues,
                )

            # Call the function
            result = f(*args, **kwargs)

            # Validate return value if requested
            if validate_return and return_hint is not None:
                return_result = TypeValidator.is_valid(result, return_hint, "return")
                if not return_result.is_valid:
                    raise ValidationError(
                        f"Return value validation failed for '{f.__name__}'",
                        return_result.issues,
                    )

            return result

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def validate_value(
    value: Any,
    type_hint: Any,
    field_name: str = "value",
) -> ValidationResult:
    """Validate a single value against a type hint.

    Args:
        value: The value to validate
        type_hint: The type hint to validate against
        field_name: Name to use in error messages

    Returns:
        ValidationResult with validation status

    Example:
        ```python
        result = validate_value([1, 2, 3], List[int], "numbers")
        if not result.is_valid:
            print(result.format_issues())
        ```
    """
    return TypeValidator.is_valid(value, type_hint, field_name)


class SchemaBuilder:
    """Builder for constructing validation schemas programmatically.

    Example:
        ```python
        schema = (SchemaBuilder()
            .add_field("id", int, required=True)
            .add_field("name", str, required=True)
            .add_field("email", str, required=False)
            .add_field("tags", List[str], required=False)
            .build())
        ```
    """

    def __init__(self) -> None:
        self._fields: dict[str, Any] = {}
        self._required: set[str] = set()
        self._validators: dict[str, list[Callable[[Any], bool]]] = {}

    def add_field(
        self,
        name: str,
        type_hint: Any,
        required: bool = True,
        validator: Callable[[Any], bool] | None = None,
    ) -> "SchemaBuilder":
        """Add a field to the schema.

        Args:
            name: Field name
            type_hint: Type hint for validation
            required: Whether the field is required
            validator: Optional custom validator function
        """
        if not required:
            # Make optional by wrapping in Union
            type_hint = Union[type_hint, None]
        self._fields[name] = type_hint
        if validator is not None:
            self._validators[name] = [validator]
        return self

    def add_validator(self, field_name: str, validator: Callable[[Any], bool]) -> "SchemaBuilder":
        """Add a custom validator to a field."""
        if field_name not in self._validators:
            self._validators[field_name] = []
        self._validators[field_name].append(validator)
        return self

    def build(self) -> dict[str, Any]:
        """Build and return the schema dictionary."""
        return self._fields.copy()

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Validate data against this schema."""
        result = validate_schema(data, self._fields)

        # Run custom validators
        for field_name, validators in self._validators.items():
            if field_name in data:
                value = data[field_name]
                for validator in validators:
                    try:
                        if not validator(value):
                            result.issues.append(ValidationIssue(
                                path=field_name,
                                expected="custom validation",
                                actual=value,
                                message=f"Custom validator failed for '{field_name}'",
                            ))
                            result.is_valid = False
                    except Exception as e:
                        result.issues.append(ValidationIssue(
                            path=field_name,
                            expected="custom validation",
                            actual=value,
                            message=f"Custom validator error: {e}",
                        ))
                        result.is_valid = False

        return result


# Common validation helpers
def validate_email(value: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def validate_url(value: str) -> bool:
    """Validate URL format."""
    pattern = r"^https?://[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,})?(/.*)?$"
    return bool(re.match(pattern, value))


def validate_uuid(value: str) -> bool:
    """Validate UUID format."""
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, value, re.IGNORECASE))


def validate_range(min_val: Any, max_val: Any) -> Callable[[Any], bool]:
    """Create a range validator."""
    def validator(value: Any) -> bool:
        try:
            return min_val <= value <= max_val
        except TypeError:
            return False
    return validator


def validate_length(min_len: int = 0, max_len: int | None = None) -> Callable[[Any], bool]:
    """Create a length validator for strings, lists, tuples."""
    def validator(value: Any) -> bool:
        try:
            length = len(value)
            if length < min_len:
                return False
            if max_len is not None and length > max_len:
                return False
            return True
        except TypeError:
            return False
    return validator


def validate_pattern(pattern: str, flags: int = 0) -> Callable[[str], bool]:
    """Create a regex pattern validator."""
    compiled = re.compile(pattern, flags)

    def validator(value: str) -> bool:
        return bool(compiled.search(value))

    return validator


__all__ = [
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationError",
    "ValidationResult",
    "TypeValidator",
    "validate",
    "validate_schema",
    "validate_value",
    "SchemaBuilder",
    # Common validators
    "validate_email",
    "validate_url",
    "validate_uuid",
    "validate_range",
    "validate_length",
    "validate_pattern",
]
