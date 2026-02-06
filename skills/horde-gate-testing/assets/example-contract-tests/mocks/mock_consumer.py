"""
Mock consumer for AuthService (Phase N+1).

This module provides mock implementations that simulate how AuthService
will consume UserService exports. Used for testing integration contracts.

Usage:
    from mocks.mock_consumer import MockAuthService

    auth_service = MockAuthService(user_service_client)
    auth_service.authenticate_user("user@example.com", "password")
"""

from typing import Optional, Dict, Any, Callable
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt


# =============================================================================
# Mock Data Models
# =============================================================================

@dataclass
class AuthToken:
    """Mock authentication token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@dataclass
class AuthUser:
    """Mock authenticated user representation."""
    id: UUID
    email: str
    role: str
    is_active: bool


# =============================================================================
# Mock AuthService Consumer
# =============================================================================

class MockAuthService:
    """
    Mock AuthService that consumes UserService exports.

    This mock simulates how the real AuthService will:
    1. Look up users by email for authentication
    2. Validate user credentials
    3. Generate auth tokens with user claims
    4. Check user permissions based on role

    Usage:
        auth = MockAuthService(mock_user_service)
        token = auth.authenticate_user("test@example.com", "password")
    """

    def __init__(self, user_service_client: Any):
        """
        Initialize with UserService client.

        Args:
            user_service_client: Client for UserService (Phase N export)
        """
        self._user_client = user_service_client
        self._secret_key = "mock-secret-key"
        self._token_algorithm = "HS256"

    def authenticate_user(self, email: str, password: str) -> Optional[AuthToken]:
        """
        Authenticate user by email and password.

        Contract Tested:
            - UserService provides email lookup
            - UserService returns user with is_active status
            - UserService data includes role for authorization

        Args:
            email: User email address
            password: User password (would be hashed in real impl)

        Returns:
            AuthToken if authentication succeeds, None otherwise
        """
        # Contract: UserService must provide email lookup
        user = self._user_client.get_user_by_email(email)

        if user is None:
            return None

        # Contract: UserService must provide is_active field
        if not user.is_active:
            return None

        # In real implementation, would verify password hash here
        # For mock, we assume password is correct

        # Contract: UserService must provide id, email, role for token
        return self._generate_token(user)

    def get_user_from_token(self, token: str) -> Optional[AuthUser]:
        """
        Decode token and return authenticated user.

        Contract Tested:
            - Token contains user ID (sub claim)
            - UserService can lookup user by ID

        Args:
            token: JWT access token

        Returns:
            AuthUser if token valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._token_algorithm]
            )

            # Contract: Token subject must be valid user ID
            user_id = UUID(payload["sub"])
            user = self._user_client.get_user_by_id(user_id)

            if user is None:
                return None

            return AuthUser(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )

        except jwt.InvalidTokenError:
            return None

    def check_permission(self, user: AuthUser, required_role: str) -> bool:
        """
        Check if user has required permission level.

        Contract Tested:
            - UserService provides role field
            - Role values match expected enum

        Args:
            user: Authenticated user
            required_role: Minimum required role level

        Returns:
            True if user has permission, False otherwise
        """
        role_hierarchy = {
            "user": 1,
            "moderator": 2,
            "admin": 3
        }

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def _generate_token(self, user: Any) -> AuthToken:
        """Generate JWT token for user."""
        now = datetime.utcnow()
        expires = now + timedelta(seconds=3600)

        # Contract: Token payload must match AUTH_TOKEN_PAYLOAD_SCHEMA
        payload = {
            "sub": str(user.id),      # Subject (user ID)
            "email": user.email,       # User email
            "role": user.role,         # User role
            "iat": now,                # Issued at
            "exp": expires             # Expiration
        }

        token = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._token_algorithm
        )

        return AuthToken(
            access_token=token,
            token_type="bearer",
            expires_in=3600
        )


# =============================================================================
# Mock Event Consumer
# =============================================================================

class MockAuthEventHandler:
    """
    Mock event handler for UserService events.

    AuthService subscribes to UserService events to:
    - Warm caches when users are created
    - Invalidate sessions when users are deleted
    - Update permissions when roles change
    """

    def __init__(self):
        self._user_cache: Dict[UUID, Any] = {}
        self._events_received: list = []

    def handle_user_created(self, event: Dict[str, Any]) -> None:
        """
        Handle USER_CREATED event from UserService.

        Contract Tested:
            - Event contains user ID
            - Event contains email
            - Event contains role
        """
        self._events_received.append(event)

        user_id = UUID(event["user_id"])

        # Cache user data for faster auth lookups
        self._user_cache[user_id] = {
            "id": user_id,
            "email": event["email"],
            "role": event["role"],
            "is_active": True
        }

    def handle_user_updated(self, event: Dict[str, Any]) -> None:
        """
        Handle USER_UPDATED event from UserService.

        Contract Tested:
            - Event contains updated fields
            - Cache invalidation works correctly
        """
        self._events_received.append(event)

        user_id = UUID(event["user_id"])

        # Update cache or invalidate
        if user_id in self._user_cache:
            if "role" in event:
                self._user_cache[user_id]["role"] = event["role"]
            if "email" in event:
                self._user_cache[user_id]["email"] = event["email"]
            if "is_active" in event:
                self._user_cache[user_id]["is_active"] = event["is_active"]

    def handle_user_deleted(self, event: Dict[str, Any]) -> None:
        """
        Handle USER_DELETED event from UserService.

        Contract Tested:
            - Event contains user ID
            - Cache entry is removed
        """
        self._events_received.append(event)

        user_id = UUID(event["user_id"])

        # Remove from cache and invalidate any active sessions
        if user_id in self._user_cache:
            del self._user_cache[user_id]

    def get_cached_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user from cache (for testing cache warming)."""
        return self._user_cache.get(user_id)


# =============================================================================
# Mock API Client Consumer
# =============================================================================

class MockAuthAPIConsumer:
    """
    Mock API client showing how AuthService calls UserService API.

    This demonstrates the HTTP contract between services.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self._base_url = base_url
        self._last_request: Optional[Dict[str, Any]] = None
        self._last_response: Optional[Dict[str, Any]] = None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Call UserService API to get user by email.

        Contract Tested:
            - Endpoint: GET /api/v1/users/by-email/{email}
            - Response: UserResponse schema
            - 404 returned for non-existent users
        """
        # Contract: API endpoint path
        endpoint = f"/api/v1/users/by-email/{email}"

        self._last_request = {
            "method": "GET",
            "endpoint": endpoint,
            "headers": {
                "Accept": "application/json",
                "Authorization": "Bearer <token>"
            }
        }

        # Mock response - in real tests this would be mocked HTTP
        mock_response = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": email,
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z"
        }

        self._last_response = {
            "status": 200,
            "body": mock_response
        }

        return mock_response

    def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Call UserService API to get user by ID.

        Contract Tested:
            - Endpoint: GET /api/v1/users/{id}
            - Response: UserResponse schema
        """
        endpoint = f"/api/v1/users/{user_id}"

        self._last_request = {
            "method": "GET",
            "endpoint": endpoint,
            "headers": {
                "Accept": "application/json"
            }
        }

        mock_response = {
            "id": str(user_id),
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z"
        }

        self._last_response = {
            "status": 200,
            "body": mock_response
        }

        return mock_response

    def get_last_request(self) -> Optional[Dict[str, Any]]:
        """Get last request made (for test verification)."""
        return self._last_request

    def get_last_response(self) -> Optional[Dict[str, Any]]:
        """Get last response received (for test verification)."""
        return self._last_response


# =============================================================================
# Mock Factory
# =============================================================================

def create_mock_auth_service(user_service: Any) -> MockAuthService:
    """
    Factory function to create a mock AuthService.

    Args:
        user_service: UserService implementation or mock

    Returns:
        Configured MockAuthService
    """
    return MockAuthService(user_service)


def create_mock_event_handler() -> MockAuthEventHandler:
    """Factory function to create a mock event handler."""
    return MockAuthEventHandler()


def create_mock_api_consumer(base_url: str = "http://localhost:8000") -> MockAuthAPIConsumer:
    """Factory function to create a mock API consumer."""
    return MockAuthAPIConsumer(base_url)


# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    # Example usage showing how mocks are used in contract tests

    # 1. Create mock UserService (would be provided by Phase N)
    class MockUserService:
        def get_user_by_email(self, email: str):
            from uuid import uuid4
            from dataclasses import dataclass

            @dataclass
            class User:
                id: UUID
                email: str
                name: str
                role: str
                is_active: bool

            return User(
                id=uuid4(),
                email=email,
                name="Test User",
                role="user",
                is_active=True
            )

        def get_user_by_id(self, user_id: UUID):
            # Similar implementation
            pass

    # 2. Create mock AuthService consumer
    user_service = MockUserService()
    auth_service = create_mock_auth_service(user_service)

    # 3. Test authentication flow
    token = auth_service.authenticate_user("test@example.com", "password")

    if token:
        print(f"Authentication successful! Token: {token.access_token[:20]}...")

        # 4. Test token validation
        user = auth_service.get_user_from_token(token.access_token)
        print(f"User from token: {user.email}, role: {user.role}")

        # 5. Test permission check
        has_admin = auth_service.check_permission(user, "admin")
        print(f"Has admin permission: {has_admin}")
    else:
        print("Authentication failed")
