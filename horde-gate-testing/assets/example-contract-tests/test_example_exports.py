"""
Example contract tests for UserService exports.

These tests verify that UserService (Phase N) exports the expected
interfaces that AuthService (Phase N+1) depends on.

Usage:
    pytest test_example_exports.py -v
"""

import pytest
from typing import Optional
from dataclasses import dataclass
from uuid import UUID, uuid4


# =============================================================================
# Test Data and Fixtures
# =============================================================================

@dataclass
class User:
    """Expected User dataclass from UserService."""
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool


@dataclass
class UserProfile:
    """Expected UserProfile dataclass from UserService."""
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        role="user",
        is_active=True
    )


@pytest.fixture
def mock_user_service():
    """
    Mock UserService for testing exports.

    In real tests, this would import from the actual implementation:
        from user_service import UserService
    """
    class MockUserService:
        def __init__(self):
            self._users = {}

        def create_user(self, email: str, name: str, role: str = "user") -> User:
            """Create a new user."""
            user = User(
                id=uuid4(),
                email=email,
                name=name,
                role=role,
                is_active=True
            )
            self._users[user.id] = user
            return user

        def get_user_by_id(self, user_id: UUID) -> Optional[User]:
            """Get user by ID. Returns None if not found."""
            return self._users.get(user_id)

        def update_user_profile(self, user_id: UUID, profile: UserProfile) -> Optional[User]:
            """Update user profile. Returns updated user or None."""
            user = self._users.get(user_id)
            if user:
                updated = User(
                    id=user.id,
                    email=profile.email or user.email,
                    name=profile.name or user.name,
                    role=profile.role or user.role,
                    is_active=user.is_active
                )
                self._users[user_id] = updated
                return updated
            return None

        def delete_user(self, user_id: UUID) -> bool:
            """Soft-delete user. Returns True if deleted."""
            user = self._users.get(user_id)
            if user:
                self._users[user_id] = User(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    role=user.role,
                    is_active=False
                )
                return True
            return False

    return MockUserService()


# =============================================================================
# Contract Tests: Interface Verification
# =============================================================================

class TestUserServiceExports:
    """Verify UserService exports expected interfaces."""

    def test_user_service_class_exported(self, mock_user_service):
        """Contract: UserService class is available and instantiable."""
        assert mock_user_service is not None
        assert hasattr(mock_user_service, 'create_user')
        assert hasattr(mock_user_service, 'get_user_by_id')
        assert hasattr(mock_user_service, 'update_user_profile')
        assert hasattr(mock_user_service, 'delete_user')

    def test_create_user_signature(self, mock_user_service):
        """Contract: create_user accepts email, name, and optional role."""
        import inspect
        sig = inspect.signature(mock_user_service.create_user)
        params = list(sig.parameters.keys())

        assert 'email' in params
        assert 'name' in params
        assert 'role' in params

        # Check defaults
        assert sig.parameters['role'].default == "user"

    def test_get_user_by_id_signature(self, mock_user_service):
        """Contract: get_user_by_id accepts UUID and returns Optional[User]."""
        import inspect
        sig = inspect.signature(mock_user_service.get_user_by_id)
        params = list(sig.parameters.keys())

        assert 'user_id' in params

    def test_update_user_profile_signature(self, mock_user_service):
        """Contract: update_user_profile accepts user_id and profile."""
        import inspect
        sig = inspect.signature(mock_user_service.update_user_profile)
        params = list(sig.parameters.keys())

        assert 'user_id' in params
        assert 'profile' in params

    def test_delete_user_signature(self, mock_user_service):
        """Contract: delete_user accepts user_id and returns bool."""
        import inspect
        sig = inspect.signature(mock_user_service.delete_user)
        params = list(sig.parameters.keys())

        assert 'user_id' in params


class TestUserDataclass:
    """Verify User dataclass structure."""

    def test_user_dataclass_fields(self, sample_user):
        """Contract: User has all expected fields."""
        assert hasattr(sample_user, 'id')
        assert hasattr(sample_user, 'email')
        assert hasattr(sample_user, 'name')
        assert hasattr(sample_user, 'role')
        assert hasattr(sample_user, 'is_active')

    def test_user_id_is_uuid(self, sample_user):
        """Contract: User.id is a UUID."""
        assert isinstance(sample_user.id, UUID)

    def test_user_email_is_string(self, sample_user):
        """Contract: User.email is a string."""
        assert isinstance(sample_user.email, str)
        assert '@' in sample_user.email  # Basic email format check


class TestUserProfileDataclass:
    """Verify UserProfile dataclass structure."""

    def test_user_profile_fields(self):
        """Contract: UserProfile has all expected fields."""
        profile = UserProfile(email="test@example.com", name="Test")

        assert hasattr(profile, 'email')
        assert hasattr(profile, 'name')
        assert hasattr(profile, 'role')
        assert hasattr(profile, 'avatar_url')

    def test_user_profile_optional_avatar(self):
        """Contract: UserProfile avatar_url is optional."""
        profile_without_avatar = UserProfile(email="test@example.com", name="Test")
        profile_with_avatar = UserProfile(
            email="test@example.com",
            name="Test",
            avatar_url="https://example.com/avatar.png"
        )

        assert profile_without_avatar.avatar_url is None
        assert profile_with_avatar.avatar_url is not None


# =============================================================================
# Contract Tests: Behavior Verification
# =============================================================================

class TestUserServiceBehavior:
    """Verify UserService behaves as expected."""

    def test_create_user_returns_user(self, mock_user_service):
        """Contract: create_user returns a User object."""
        user = mock_user_service.create_user("new@example.com", "New User")

        assert isinstance(user, User)
        assert user.email == "new@example.com"
        assert user.name == "New User"
        assert user.role == "user"
        assert user.is_active is True

    def test_get_user_by_id_returns_user(self, mock_user_service):
        """Contract: get_user_by_id returns User for existing user."""
        created = mock_user_service.create_user("test@example.com", "Test User")
        retrieved = mock_user_service.get_user_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.email == created.email

    def test_get_user_by_id_returns_none_for_missing(self, mock_user_service):
        """Contract: get_user_by_id returns None for non-existent user."""
        non_existent_id = uuid4()
        result = mock_user_service.get_user_by_id(non_existent_id)

        assert result is None

    def test_update_user_profile_updates_fields(self, mock_user_service):
        """Contract: update_user_profile updates specified fields."""
        user = mock_user_service.create_user("original@example.com", "Original Name")
        profile = UserProfile(email="updated@example.com", name="Updated Name", role="admin")

        updated = mock_user_service.update_user_profile(user.id, profile)

        assert updated is not None
        assert updated.email == "updated@example.com"
        assert updated.name == "Updated Name"
        assert updated.role == "admin"

    def test_delete_user_soft_delete(self, mock_user_service):
        """Contract: delete_user performs soft delete (is_active=False)."""
        user = mock_user_service.create_user("delete@example.com", "To Delete")

        deleted = mock_user_service.delete_user(user.id)
        retrieved = mock_user_service.get_user_by_id(user.id)

        assert deleted is True
        assert retrieved is not None
        assert retrieved.is_active is False

    def test_delete_user_returns_false_for_missing(self, mock_user_service):
        """Contract: delete_user returns False for non-existent user."""
        non_existent_id = uuid4()
        result = mock_user_service.delete_user(non_existent_id)

        assert result is False


# =============================================================================
# Contract Tests: AuthService Integration Points
# =============================================================================

class TestAuthServiceIntegration:
    """
    Verify integration points specific to AuthService needs.

    These tests ensure UserService meets AuthService's requirements.
    """

    def test_email_field_accessible_for_auth(self, mock_user_service):
        """Contract: AuthService can access email for authentication."""
        user = mock_user_service.create_user("auth@example.com", "Auth User")

        # AuthService needs to lookup by email
        assert isinstance(user.email, str)
        assert len(user.email) > 0

    def test_role_field_accessible_for_auth(self, mock_user_service):
        """Contract: AuthService can access role for authorization."""
        user = mock_user_service.create_user("role@example.com", "Role User", role="admin")

        # AuthService needs role for permission checks
        assert isinstance(user.role, str)
        assert user.role == "admin"

    def test_is_active_checked_by_auth(self, mock_user_service):
        """Contract: AuthService can check is_active status."""
        user = mock_user_service.create_user("active@example.com", "Active User")

        # AuthService should reject inactive users
        assert hasattr(user, 'is_active')
        assert isinstance(user.is_active, bool)

    def test_user_lookup_by_id_for_token_validation(self, mock_user_service):
        """Contract: AuthService can validate tokens by looking up user ID."""
        user = mock_user_service.create_user("token@example.com", "Token User")

        # Simulate token containing user_id
        token_user_id = user.id
        retrieved = mock_user_service.get_user_by_id(token_user_id)

        assert retrieved is not None
        assert retrieved.id == token_user_id


# =============================================================================
# Edge Case Contract Tests
# =============================================================================

class TestEdgeCases:
    """Verify edge case handling."""

    def test_create_user_with_empty_name(self, mock_user_service):
        """Contract: Empty name handling is defined."""
        # Behavior may vary - test documents actual behavior
        user = mock_user_service.create_user("empty@example.com", "")
        assert user.name == ""

    def test_create_user_with_special_characters_in_name(self, mock_user_service):
        """Contract: Special characters in name are handled."""
        user = mock_user_service.create_user(
            "special@example.com",
            "User with ñ and émojis"
        )
        assert "ñ" in user.name
        assert "émojis" in user.name

    def test_update_user_with_partial_profile(self, mock_user_service):
        """Contract: Partial profile updates work correctly."""
        user = mock_user_service.create_user("partial@example.com", "Original Name")

        # Update only name
        partial_profile = UserProfile(email=None, name="New Name", role=None)
        updated = mock_user_service.update_user_profile(user.id, partial_profile)

        assert updated.name == "New Name"
        # Other fields should retain original values
        assert updated.email == "partial@example.com"


# =============================================================================
# Run Configuration
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
