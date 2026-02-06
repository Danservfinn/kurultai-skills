# Contract Testing Guide

Guide to writing effective contract tests for phase gate testing.

---

## What is Contract Testing

Contract testing verifies that two software components (phases) can communicate with each other by checking that the producer (Phase N) meets the expectations of the consumer (Phase N+1).

### Definition

A **contract** is the agreed-upon interface between two components:
- **Function signatures**: Names, parameters, return types
- **Data schemas**: Structure, types, constraints
- **Behavior**: Side effects, error handling, timing
- **Protocols**: HTTP methods, event formats, database constraints

### Purpose

Contract tests answer these questions:
1. Does the producer export what the consumer needs?
2. Does the data format match expectations?
3. Does the behavior match the specification?
4. Can the consumer use the producer without modification?

### Contract Testing vs Unit Testing

| Aspect | Unit Testing | Contract Testing |
|--------|-------------|------------------|
| Focus | Internal implementation | External interface |
| Scope | Single component | Component interaction |
| Stability | Changes frequently | Stable across versions |
| Consumer | Same team | Different team/phase |
| Mocking | Dependencies mocked | Consumer mocked |

---

## Contract Test Types

### Existence Tests

Verify that expected items exist and are accessible.

#### Purpose
Confirm that functions, classes, modules, and endpoints are available to the consumer.

#### Examples

```python
# Function existence
def test_create_user_function_exists():
    """Verify create_user function is exported."""
    assert hasattr(module, 'create_user'), "create_user not found"
    assert callable(getattr(module, 'create_user')), "create_user is not callable"

# Class existence
def test_database_connection_class_exists():
    """Verify DatabaseConnection class is exported."""
    assert hasattr(module, 'DatabaseConnection'), "DatabaseConnection not found"
    assert isinstance(getattr(module, 'DatabaseConnection'), type), "DatabaseConnection is not a class"

# Endpoint existence
def test_users_endpoint_exists(client):
    """Verify /api/v1/users endpoint exists."""
    response = client.get('/api/v1/users')
    assert response.status_code != 404, "Endpoint not found"

# Table existence
def test_users_table_exists(db):
    """Verify users table exists in database."""
    result = db.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'users'")
    assert result.fetchone() is not None, "users table not found"
```

#### Checklist

- [ ] All expected functions exist and are callable
- [ ] All expected classes exist and are instantiable
- [ ] All expected modules can be imported
- [ ] All expected endpoints return non-404
- [ ] All expected database tables exist
- [ ] All expected configuration keys exist

---

### Signature Tests

Verify that functions, methods, and classes have the correct signatures.

#### Purpose
Confirm that parameters, types, and return values match the contract.

#### Examples

```python
import inspect
from typing import get_type_hints

# Function signature
def test_create_user_signature():
    """Verify create_user has correct signature."""
    sig = inspect.signature(create_user)
    params = list(sig.parameters.keys())

    assert 'username' in params, "Missing required parameter: username"
    assert 'email' in params, "Missing required parameter: email"

    # Check default values
    email_param = sig.parameters['email']
    assert email_param.default is inspect.Parameter.empty, "email should be required"

    role_param = sig.parameters.get('role')
    if role_param:
        assert role_param.default == "user", "role should default to 'user'"

# Type hints
def test_create_user_type_hints():
    """Verify create_user has correct type hints."""
    hints = get_type_hints(create_user)

    assert 'username' in hints, "Missing type hint for username"
    assert hints['username'] == str, "username should be str"

    assert 'return' in hints, "Missing return type hint"
    assert hints['return'] == User, "Return type should be User"

# Class constructor
def test_database_connection_constructor():
    """Verify DatabaseConnection constructor signature."""
    sig = inspect.signature(DatabaseConnection.__init__)
    params = list(sig.parameters.keys())

    assert 'connection_string' in params, "Missing connection_string parameter"
    assert 'pool_size' in params, "Missing pool_size parameter"

    pool_size_param = sig.parameters['pool_size']
    assert pool_size_param.default == 10, "pool_size should default to 10"

# HTTP endpoint signature
def test_create_user_endpoint_signature(client):
    """Verify POST /api/v1/users accepts correct body."""
    # Test with valid body
    response = client.post('/api/v1/users', json={
        'username': 'test',
        'email': 'test@example.com'
    })
    assert response.status_code in [201, 422], "Should accept valid body or validate it"

    # Test with missing required field
    response = client.post('/api/v1/users', json={
        'username': 'test'
        # missing email
    })
    assert response.status_code == 422, "Should reject missing required field"
```

#### Checklist

- [ ] All required parameters are present
- [ ] Parameter types match contract
- [ ] Return types match contract
- [ ] Default values are correct
- [ ] Optional parameters are marked as such
- [ ] HTTP endpoints accept expected body/params
- [ ] HTTP endpoints return expected status codes

---

### Behavior Tests

Verify that functions behave as expected.

#### Purpose
Confirm that the producer produces correct outputs and side effects for given inputs.

#### Examples

```python
# Function behavior
def test_create_user_creates_user():
    """Verify create_user actually creates a user."""
    result = create_user("test_user", "test@example.com")

    assert result.username == "test_user", "Username not set correctly"
    assert result.email == "test@example.com", "Email not set correctly"
    assert result.id is not None, "ID not generated"
    assert result.created_at is not None, "Created timestamp not set"

# Side effects
def test_create_user_persists_to_database(db):
    """Verify create_user persists to database."""
    create_user("test_user", "test@example.com")

    result = db.execute("SELECT * FROM users WHERE username = %s", ("test_user",))
    row = result.fetchone()

    assert row is not None, "User not found in database"
    assert row['email'] == "test@example.com", "Email not persisted correctly"

# Error behavior
def test_create_user_duplicate_username_raises_error():
    """Verify create_user raises error for duplicate username."""
    create_user("test_user", "test1@example.com")

    with pytest.raises(DuplicateUserError) as exc_info:
        create_user("test_user", "test2@example.com")

    assert "already exists" in str(exc_info.value), "Error message should indicate duplicate"

# Event emission
def test_create_user_emits_event(event_bus):
    """Verify create_user emits user.created event."""
    events = []
    event_bus.subscribe("user.created", events.append)

    user = create_user("test_user", "test@example.com")

    assert len(events) == 1, "Event not emitted"
    assert events[0]['type'] == 'user.created', "Wrong event type"
    assert events[0]['payload']['user_id'] == user.id, "Wrong user ID in event"

# API behavior
def test_create_user_endpoint_behavior(client):
    """Verify POST /api/v1/users creates user and returns correct response."""
    response = client.post('/api/v1/users', json={
        'username': 'test',
        'email': 'test@example.com'
    })

    assert response.status_code == 201, "Should return 201 Created"

    data = response.json()
    assert data['username'] == 'test', "Username not in response"
    assert data['email'] == 'test@example.com', "Email not in response"
    assert 'id' in data, "ID not in response"
    assert 'created_at' in data, "Created timestamp not in response"
```

#### Checklist

- [ ] Functions return correct values for valid inputs
- [ ] Functions produce expected side effects
- [ ] Functions handle errors correctly
- [ ] Events are emitted at correct times
- [ ] API responses match expected format
- [ ] State changes are persisted correctly
- [ ] Idempotent operations can be repeated safely

---

### Schema Tests

Verify that data structures match expected schemas.

#### Purpose
Confirm that data passed between phases conforms to the agreed-upon structure.

#### Examples

```python
# JSON schema validation
def test_user_response_schema(client):
    """Verify user API response matches schema."""
    response = client.get('/api/v1/users/123')
    data = response.json()

    schema = {
        "type": "object",
        "required": ["id", "username", "email", "created_at"],
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "username": {"type": "string", "minLength": 3, "maxLength": 50},
            "email": {"type": "string", "format": "email"},
            "created_at": {"type": "string", "format": "date-time"},
            "metadata": {"type": "object"}
        }
    }

    validate(instance=data, schema=schema)

# Data class validation
def test_user_dataclass_schema():
    """Verify User dataclass has expected fields."""
    user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        username="test_user",
        email="test@example.com",
        created_at=datetime.now()
    )

    assert hasattr(user, 'id'), "Missing id field"
    assert hasattr(user, 'username'), "Missing username field"
    assert hasattr(user, 'email'), "Missing email field"
    assert hasattr(user, 'created_at'), "Missing created_at field"

    assert isinstance(user.id, str), "id should be string"
    assert isinstance(user.username, str), "username should be string"
    assert isinstance(user.email, str), "email should be string"

# Database schema validation
def test_users_table_schema(db):
    """Verify users table has correct schema."""
    result = db.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users'
    """)
    columns = {row['column_name']: row for row in result}

    assert 'id' in columns, "Missing id column"
    assert columns['id']['data_type'] == 'uuid', "id should be uuid"
    assert columns['id']['is_nullable'] == 'NO', "id should be non-nullable"

    assert 'username' in columns, "Missing username column"
    assert columns['username']['data_type'] == 'character varying', "username should be varchar"

    assert 'email' in columns, "Missing email column"
    assert columns['email']['is_nullable'] == 'NO', "email should be non-nullable"

# Event schema validation
def test_user_created_event_schema():
    """Verify user.created event matches schema."""
    event = {
        "type": "user.created",
        "timestamp": "2024-01-15T10:30:00Z",
        "payload": {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "test_user",
            "email": "test@example.com"
        }
    }

    # Required fields
    assert 'type' in event, "Missing type field"
    assert 'timestamp' in event, "Missing timestamp field"
    assert 'payload' in event, "Missing payload field"

    # Type validation
    assert event['type'] == 'user.created', "Wrong event type"
    assert isinstance(event['timestamp'], str), "timestamp should be string"
    assert isinstance(event['payload'], dict), "payload should be object"

    # Payload validation
    payload = event['payload']
    assert 'user_id' in payload, "Missing user_id in payload"
    assert 'username' in payload, "Missing username in payload"
    assert 'email' in payload, "Missing email in payload"
```

#### Checklist

- [ ] All required fields are present
- [ ] Field types match specification
- [ ] String formats are valid (UUID, email, datetime)
- [ ] Numeric ranges are valid
- [ ] Enum values are valid
- [ ] Nested objects match sub-schemas
- [ ] Arrays have correct item types
- [ ] Nullable fields are marked correctly

---

## Best Practices

### 1. Test from Consumer Perspective

Write tests that reflect how the consumer will actually use the producer.

```python
# Good: Tests actual consumer usage pattern
def test_consumer_can_create_and_fetch_user():
    """Simulate how Phase 2 will use Phase 1's API."""
    # Create user
    create_response = client.post('/api/v1/users', json={
        'username': 'test',
        'email': 'test@example.com'
    })
    user_id = create_response.json()['id']

    # Fetch user
    get_response = client.get(f'/api/v1/users/{user_id}')
    assert get_response.json()['username'] == 'test'

# Bad: Tests internal implementation details
def test_internal_user_service_calls_database():
    """This tests internals, not the contract."""
    with mock.patch('database.execute') as mock_db:
        user_service.create_user("test", "test@example.com")
        mock_db.assert_called_once()  # Too implementation-specific
```

### 2. Make Tests Deterministic

Contract tests should produce the same results every time.

```python
# Good: Deterministic test
def test_create_user_returns_consistent_format():
    """Test always passes or always fails."""
    user = create_user("test", "test@example.com")
    assert isinstance(user.id, str)
    assert len(user.id) == 36  # UUID length

# Bad: Non-deterministic test
def test_create_user_random_behavior():
    """Test may pass or fail randomly."""
    user = create_user("test", "test@example.com")
    # Don't test random values without controlling the randomness
    assert user.id != "123"  # May fail by chance
```

### 3. Isolate the Contract

Test the contract in isolation, not the entire system.

```python
# Good: Isolated contract test
def test_api_contract(client):
    """Test only the API contract, not business logic."""
    response = client.get('/api/v1/users/123')
    assert response.status_code in [200, 404]  # Contract: must return 200 or 404
    if response.status_code == 200:
        assert 'id' in response.json()  # Contract: must have id field

# Bad: Testing business logic
def test_user_business_rules(db):
    """This belongs in unit tests, not contract tests."""
    user = create_user("test", "test@example.com")
    assert user.is_active == True  # Business rule, not contract
```

### 4. Document Assumptions

Document what the consumer assumes about the producer.

```python
def test_user_list_pagination():
    """
    Contract: GET /api/v1/users returns paginated results.

    Consumer Assumptions:
    - Default page size is 20
    - Response includes total_count field
    - Response includes has_next field
    - Page parameter starts at 1 (not 0)
    """
    response = client.get('/api/v1/users')
    data = response.json()

    assert 'items' in data, "Consumer expects items array"
    assert 'total_count' in data, "Consumer expects total_count for pagination UI"
    assert 'has_next' in data, "Consumer expects has_next for next page button"
    assert len(data['items']) <= 20, "Consumer assumes default page size of 20"
```

### 5. Version Contracts

When contracts change, version them to maintain backward compatibility.

```python
# Test both old and new contract versions
def test_api_v1_contract(client):
    """Test legacy v1 contract."""
    response = client.get('/api/v1/users/123')
    data = response.json()

    # v1 contract
    assert 'id' in data
    assert 'name' in data  # v1 used 'name', not 'username'

def test_api_v2_contract(client):
    """Test current v2 contract."""
    response = client.get('/api/v2/users/123')
    data = response.json()

    # v2 contract
    assert 'id' in data
    assert 'username' in data  # v2 uses 'username'
    assert 'email' in data  # v2 added email
```

---

## Anti-patterns

### 1. Testing Implementation Details

```python
# Anti-pattern: Testing internals
def test_internal_cache_is_used():
    with mock.patch('cache.get') as mock_cache:
        get_user(123)
        mock_cache.assert_called_once()  # Tests implementation, not contract

# Better: Test observable behavior
def test_get_user_returns_cached_data():
    # First call
    user1 = get_user(123)
    # Second call should return same data (whether cached or not)
    user2 = get_user(123)
    assert user1 == user2
```

### 2. Testing Too Much

```python
# Anti-pattern: Testing everything
def test_user_has_50_fields():
    user = get_user(123)
    # Testing every single field is fragile
    assert user.field1 == ...
    assert user.field2 == ...
    # ... 48 more assertions

# Better: Test only contract fields
def test_user_has_required_contract_fields():
    user = get_user(123)
    # Only test fields the consumer actually uses
    assert hasattr(user, 'id')
    assert hasattr(user, 'username')
    assert hasattr(user, 'email')
```

### 3. Hardcoding IDs and Timestamps

```python
# Anti-pattern: Hardcoded values
def test_get_user_returns_specific_user():
    user = get_user(123)
    assert user.id == "abc-123-def"  # May change
    assert user.created_at == "2024-01-15T10:30:00Z"  # Will change

# Better: Validate format and relationships
def test_get_user_returns_valid_user():
    user = get_user(123)
    assert len(user.id) == 36  # UUID format
    assert isinstance(user.created_at, datetime)
    assert user.created_at <= datetime.now()  # Must be in past
```

### 4. Ignoring Error Cases

```python
# Anti-pattern: Only testing happy path
def test_create_user_success():
    user = create_user("test", "test@example.com")
    assert user is not None

# Better: Test error cases too
def test_create_user_duplicate_email():
    create_user("test1", "test@example.com")

    with pytest.raises(DuplicateError):
        create_user("test2", "test@example.com")

def test_create_user_invalid_email():
    with pytest.raises(ValidationError):
        create_user("test", "not-an-email")
```

### 5. Brittle Assertions

```python
# Anti-pattern: Overly specific assertions
def test_error_message():
    with pytest.raises(Error) as exc:
        create_user("", "test@example.com")
    assert str(exc.value) == "Username cannot be empty"  # May change

# Better: Test error type and general content
def test_error_message():
    with pytest.raises(ValidationError) as exc:
        create_user("", "test@example.com")
    assert "username" in str(exc.value).lower()
    assert "empty" in str(exc.value).lower() or "required" in str(exc.value).lower()
```

---

## Test Organization

Organize contract tests by phase boundary:

```
tests/
  contract/
    phase_1_to_2/
      test_function_contracts.py
      test_data_contracts.py
      test_api_contracts.py
    phase_2_to_3/
      test_event_contracts.py
      test_schema_contracts.py
```

Each test file should focus on one type of contract:

```python
# tests/contract/phase_1_to_2/test_function_contracts.py
"""Contract tests for function interfaces between Phase 1 and Phase 2."""

import pytest
from myapp.phase1 import create_user, update_user, delete_user

class TestCreateUserContract:
    """Contract tests for create_user function."""

    def test_function_exists(self):
        """Verify create_user is exported."""
        assert callable(create_user)

    def test_signature(self):
        """Verify create_user has correct signature."""
        sig = inspect.signature(create_user)
        assert 'username' in sig.parameters
        assert 'email' in sig.parameters

    def test_behavior_creates_user(self):
        """Verify create_user creates a user."""
        user = create_user("test", "test@example.com")
        assert user.username == "test"
        assert user.email == "test@example.com"

    def test_error_on_duplicate(self):
        """Verify create_user raises error on duplicate."""
        create_user("test", "test@example.com")
        with pytest.raises(DuplicateError):
            create_user("test", "test2@example.com")
```
