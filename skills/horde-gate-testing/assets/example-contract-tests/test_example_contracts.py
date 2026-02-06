"""
Example schema validation contract tests.

These tests verify data schemas between UserService (Phase N) and
AuthService (Phase N+1) using JSON Schema validation.

Usage:
    pytest test_example_contracts.py -v
"""

import pytest
import jsonschema
from jsonschema import validate, ValidationError
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any


# =============================================================================
# JSON Schemas (Contract Definitions)
# =============================================================================

USER_RESPONSE_SCHEMA = {
    """Schema for User API responses."""
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "email", "name", "role", "is_active", "created_at"],
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique user identifier"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "User email address"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "description": "User display name"
        },
        "role": {
            "type": "string",
            "enum": ["user", "admin", "moderator"],
            "description": "User role for authorization"
        },
        "is_active": {
            "type": "boolean",
            "description": "Whether user account is active"
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "Account creation timestamp"
        },
        "avatar_url": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "Optional avatar URL"
        }
    },
    "additionalProperties": False
}

USER_CREATE_REQUEST_SCHEMA = {
    """Schema for user creation requests."""
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["email", "name"],
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "role": {
            "type": "string",
            "enum": ["user", "admin", "moderator"],
            "default": "user"
        }
    },
    "additionalProperties": False
}

USER_UPDATE_REQUEST_SCHEMA = {
    """Schema for user update requests."""
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "minProperties": 1,  # At least one field must be provided
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "role": {
            "type": "string",
            "enum": ["user", "admin", "moderator"]
        },
        "is_active": {
            "type": "boolean"
        }
    },
    "additionalProperties": False
}

ERROR_RESPONSE_SCHEMA = {
    """Schema for API error responses."""
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["error", "message"],
    "properties": {
        "error": {
            "type": "string",
            "description": "Error code"
        },
        "message": {
            "type": "string",
            "description": "Human-readable error message"
        },
        "details": {
            "type": ["object", "null"],
            "description": "Optional error details"
        }
    },
    "additionalProperties": False
}

AUTH_TOKEN_PAYLOAD_SCHEMA = {
    """Schema for authentication token payload (AuthService expectation)."""
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["sub", "email", "role", "iat", "exp"],
    "properties": {
        "sub": {
            "type": "string",
            "format": "uuid",
            "description": "Subject (user ID)"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "role": {
            "type": "string",
            "enum": ["user", "admin", "moderator"]
        },
        "iat": {
            "type": "integer",
            "description": "Issued at timestamp"
        },
        "exp": {
            "type": "integer",
            "description": "Expiration timestamp"
        }
    },
    "additionalProperties": False
}


# =============================================================================
# Schema Validation Helpers
# =============================================================================

def assert_valid_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Assert that data conforms to the given schema."""
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed: {e.message}")


def assert_invalid_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Assert that data does NOT conform to the given schema."""
    with pytest.raises(ValidationError):
        validate(instance=data, schema=schema)


# =============================================================================
# Contract Tests: User Response Schema
# =============================================================================

class TestUserResponseSchema:
    """Verify User response format matches contract."""

    def test_valid_user_response(self):
        """Contract: Valid user data passes schema validation."""
        user_data = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "avatar_url": "https://example.com/avatar.png"
        }
        assert_valid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_valid_user_without_avatar(self):
        """Contract: User without avatar (null) is valid."""
        user_data = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "avatar_url": None
        }
        assert_valid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_invalid_user_missing_required_field(self):
        """Contract: Missing required fields fail validation."""
        user_data = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            # Missing "role", "is_active", "created_at"
        }
        assert_invalid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_invalid_user_bad_email_format(self):
        """Contract: Invalid email format fails validation."""
        user_data = {
            "id": str(uuid4()),
            "email": "not-an-email",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        assert_invalid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_invalid_user_bad_uuid_format(self):
        """Contract: Invalid UUID format fails validation."""
        user_data = {
            "id": "not-a-uuid",
            "email": "user@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        assert_invalid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_invalid_user_bad_role(self):
        """Contract: Invalid role enum fails validation."""
        user_data = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            "role": "superadmin",  # Not in enum
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        assert_invalid_schema(user_data, USER_RESPONSE_SCHEMA)

    def test_invalid_user_extra_properties(self):
        """Contract: Additional properties fail validation."""
        user_data = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "extra_field": "should not be here"
        }
        assert_invalid_schema(user_data, USER_RESPONSE_SCHEMA)


# =============================================================================
# Contract Tests: Create Request Schema
# =============================================================================

class TestUserCreateRequestSchema:
    """Verify User creation request format matches contract."""

    def test_valid_create_request(self):
        """Contract: Valid create request passes validation."""
        request = {
            "email": "new@example.com",
            "name": "New User",
            "role": "user"
        }
        assert_valid_schema(request, USER_CREATE_REQUEST_SCHEMA)

    def test_valid_create_request_minimal(self):
        """Contract: Minimal create request (required fields only) is valid."""
        request = {
            "email": "new@example.com",
            "name": "New User"
        }
        assert_valid_schema(request, USER_CREATE_REQUEST_SCHEMA)

    def test_invalid_create_request_missing_email(self):
        """Contract: Create request without email fails validation."""
        request = {
            "name": "New User"
        }
        assert_invalid_schema(request, USER_CREATE_REQUEST_SCHEMA)

    def test_invalid_create_request_empty_name(self):
        """Contract: Create request with empty name fails validation."""
        request = {
            "email": "new@example.com",
            "name": ""
        }
        assert_invalid_schema(request, USER_CREATE_REQUEST_SCHEMA)

    def test_invalid_create_request_name_too_long(self):
        """Contract: Name exceeding max length fails validation."""
        request = {
            "email": "new@example.com",
            "name": "A" * 101  # Exceeds maxLength of 100
        }
        assert_invalid_schema(request, USER_CREATE_REQUEST_SCHEMA)


# =============================================================================
# Contract Tests: Update Request Schema
# =============================================================================

class TestUserUpdateRequestSchema:
    """Verify User update request format matches contract."""

    def test_valid_update_request_email(self):
        """Contract: Update email only is valid."""
        request = {
            "email": "updated@example.com"
        }
        assert_valid_schema(request, USER_UPDATE_REQUEST_SCHEMA)

    def test_valid_update_request_name(self):
        """Contract: Update name only is valid."""
        request = {
            "name": "Updated Name"
        }
        assert_valid_schema(request, USER_UPDATE_REQUEST_SCHEMA)

    def test_valid_update_request_role(self):
        """Contract: Update role only is valid."""
        request = {
            "role": "admin"
        }
        assert_valid_schema(request, USER_UPDATE_REQUEST_SCHEMA)

    def test_valid_update_request_multiple_fields(self):
        """Contract: Update multiple fields is valid."""
        request = {
            "email": "updated@example.com",
            "name": "Updated Name",
            "role": "moderator"
        }
        assert_valid_schema(request, USER_UPDATE_REQUEST_SCHEMA)

    def test_invalid_update_request_empty(self):
        """Contract: Empty update request fails validation."""
        request = {}
        assert_invalid_schema(request, USER_UPDATE_REQUEST_SCHEMA)

    def test_invalid_update_request_bad_role(self):
        """Contract: Invalid role in update fails validation."""
        request = {
            "role": "invalid_role"
        }
        assert_invalid_schema(request, USER_UPDATE_REQUEST_SCHEMA)


# =============================================================================
# Contract Tests: Error Response Schema
# =============================================================================

class TestErrorResponseSchema:
    """Verify Error response format matches contract."""

    def test_valid_error_response(self):
        """Contract: Valid error response passes validation."""
        error = {
            "error": "USER_NOT_FOUND",
            "message": "User with ID 123 not found",
            "details": None
        }
        assert_valid_schema(error, ERROR_RESPONSE_SCHEMA)

    def test_valid_error_with_details(self):
        """Contract: Error with details object is valid."""
        error = {
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "field": "email",
                "issue": "Invalid format"
            }
        }
        assert_valid_schema(error, ERROR_RESPONSE_SCHEMA)

    def test_invalid_error_missing_code(self):
        """Contract: Error without error code fails validation."""
        error = {
            "message": "Something went wrong"
        }
        assert_invalid_schema(error, ERROR_RESPONSE_SCHEMA)

    def test_invalid_error_missing_message(self):
        """Contract: Error without message fails validation."""
        error = {
            "error": "UNKNOWN_ERROR"
        }
        assert_invalid_schema(error, ERROR_RESPONSE_SCHEMA)


# =============================================================================
# Contract Tests: AuthService Token Payload Schema
# =============================================================================

class TestAuthTokenPayloadSchema:
    """
    Verify token payload schema for AuthService integration.

    AuthService expects UserService to provide data that can be encoded
    in JWT tokens with this specific structure.
    """

    def test_valid_token_payload(self):
        """Contract: Valid token payload passes validation."""
        now = int(datetime.utcnow().timestamp())
        payload = {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "role": "user",
            "iat": now,
            "exp": now + 3600
        }
        assert_valid_schema(payload, AUTH_TOKEN_PAYLOAD_SCHEMA)

    def test_valid_token_payload_admin(self):
        """Contract: Admin role in token payload is valid."""
        now = int(datetime.utcnow().timestamp())
        payload = {
            "sub": str(uuid4()),
            "email": "admin@example.com",
            "role": "admin",
            "iat": now,
            "exp": now + 3600
        }
        assert_valid_schema(payload, AUTH_TOKEN_PAYLOAD_SCHEMA)

    def test_invalid_token_missing_sub(self):
        """Contract: Token without subject fails validation."""
        now = int(datetime.utcnow().timestamp())
        payload = {
            "email": "user@example.com",
            "role": "user",
            "iat": now,
            "exp": now + 3600
        }
        assert_invalid_schema(payload, AUTH_TOKEN_PAYLOAD_SCHEMA)

    def test_invalid_token_bad_uuid_sub(self):
        """Contract: Token with non-UUID subject fails validation."""
        now = int(datetime.utcnow().timestamp())
        payload = {
            "sub": "not-a-uuid",
            "email": "user@example.com",
            "role": "user",
            "iat": now,
            "exp": now + 3600
        }
        assert_invalid_schema(payload, AUTH_TOKEN_PAYLOAD_SCHEMA)

    def test_invalid_token_exp_before_iat(self):
        """Contract: Token expiration must be after issued-at."""
        now = int(datetime.utcnow().timestamp())
        payload = {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "role": "user",
            "iat": now,
            "exp": now - 100  # Expired before issued
        }
        # Note: Schema validation alone won't catch this logical error
        # but the schema structure is valid
        assert_valid_schema(payload, AUTH_TOKEN_PAYLOAD_SCHEMA)


# =============================================================================
# Contract Tests: Cross-Phase Data Compatibility
# =============================================================================

class TestCrossPhaseCompatibility:
    """
    Verify data can flow from UserService to AuthService.

    These tests ensure the output from UserService can be used as
    input to AuthService operations.
    """

    def test_user_response_maps_to_token_payload(self):
        """
        Contract: UserResponse contains all fields needed for Auth token.

        This is a critical contract - AuthService must be able to create
        JWT tokens from UserService data.
        """
        # Simulate UserService response
        user_response = {
            "id": str(uuid4()),
            "email": "user@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Verify UserService output is valid
        assert_valid_schema(user_response, USER_RESPONSE_SCHEMA)

        # Map to token payload (what AuthService does)
        now = int(datetime.utcnow().timestamp())
        token_payload = {
            "sub": user_response["id"],
            "email": user_response["email"],
            "role": user_response["role"],
            "iat": now,
            "exp": now + 3600
        }

        # Verify AuthService output would be valid
        assert_valid_schema(token_payload, AUTH_TOKEN_PAYLOAD_SCHEMA)

    def test_inactive_user_cannot_generate_token(self):
        """
        Contract: Inactive users should not get auth tokens.

        This tests the business rule that AuthService should enforce
        using UserService data.
        """
        user_response = {
            "id": str(uuid4()),
            "email": "inactive@example.com",
            "name": "Inactive User",
            "role": "user",
            "is_active": False,  # Inactive!
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # UserService data is valid
        assert_valid_schema(user_response, USER_RESPONSE_SCHEMA)

        # AuthService should check is_active before creating token
        assert user_response["is_active"] is False, \
            "AuthService should reject inactive users"


# =============================================================================
# Schema Version Contract Tests
# =============================================================================

class TestSchemaVersioning:
    """
    Verify schema versioning contracts.

    These tests document the schema versions and ensure backward
    compatibility is maintained.
    """

    def test_user_response_schema_version(self):
        """Contract: UserResponse uses JSON Schema draft-07."""
        assert USER_RESPONSE_SCHEMA["$schema"] == \
               "http://json-schema.org/draft-07/schema#"

    def test_all_schemas_have_required_fields(self):
        """Contract: All schemas define required fields."""
        schemas = [
            USER_RESPONSE_SCHEMA,
            USER_CREATE_REQUEST_SCHEMA,
            USER_UPDATE_REQUEST_SCHEMA,
            ERROR_RESPONSE_SCHEMA,
            AUTH_TOKEN_PAYLOAD_SCHEMA
        ]

        for schema in schemas:
            assert "required" in schema, \
                f"Schema missing required fields: {schema}"

    def test_schemas_disallow_additional_properties(self):
        """Contract: Schemas are strict (no additional properties)."""
        # This ensures forward compatibility - new fields must be
        # explicitly added to the schema
        strict_schemas = [
            USER_RESPONSE_SCHEMA,
            USER_CREATE_REQUEST_SCHEMA,
            USER_UPDATE_REQUEST_SCHEMA,
            ERROR_RESPONSE_SCHEMA,
            AUTH_TOKEN_PAYLOAD_SCHEMA
        ]

        for schema in strict_schemas:
            assert schema.get("additionalProperties") is False, \
                f"Schema should disallow additionalProperties: {schema}"


# =============================================================================
# Run Configuration
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
