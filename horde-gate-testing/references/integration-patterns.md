# Integration Patterns for Phase Gate Testing

Common integration patterns between phases and how to test them effectively.

---

## Function-to-Function

Testing function exports and signatures between phases.

### Description
Phase N exports functions that Phase N+1 imports and calls. The contract includes function name, parameters, return type, and behavior.

### Example Scenario
Phase 1 implements a `create_user()` function. Phase 2 needs to call this function to create users during onboarding.

```python
# Phase 1 exports
def create_user(username: str, email: str, role: str = "user") -> User:
    """Create a new user account."""
    pass

# Phase 2 expects
def create_user(username: str, email: str, role: str = "user") -> User:
    """Must accept username, email, optional role. Must return User object."""
    pass
```

### Testing Approach
1. **Existence Test**: Verify function exists with correct name
2. **Signature Test**: Verify parameters and types match
3. **Return Type Test**: Verify return type matches contract
4. **Behavior Test**: Verify function behaves as documented

### Mock Strategy
```python
# Mock Phase N+1 consumer
class MockPhaseNPlus1:
    def onboard_user(self, username: str, email: str):
        # Test that Phase N function can be called as expected
        user = create_user(username, email)
        assert user.username == username
        assert user.email == email
```

---

## Class-to-Class

Testing class interfaces and inheritance between phases.

### Description
Phase N exports classes that Phase N+1 instantiates or extends. The contract includes constructor signature, methods, properties, and inheritance hierarchy.

### Example Scenario
Phase 1 implements a `DatabaseConnection` class. Phase 2 extends it with `CachedDatabaseConnection`.

```python
# Phase 1 exports
class DatabaseConnection:
    def __init__(self, connection_string: str, pool_size: int = 10):
        self.connection_string = connection_string
        self.pool_size = pool_size

    def query(self, sql: str, params: dict = None) -> List[dict]:
        pass

    def close(self) -> None:
        pass

# Phase 2 expects
class CachedDatabaseConnection(DatabaseConnection):
    def __init__(self, connection_string: str, pool_size: int = 10, cache_ttl: int = 300):
        super().__init__(connection_string, pool_size)
        self.cache_ttl = cache_ttl
```

### Testing Approach
1. **Constructor Test**: Verify constructor accepts expected parameters
2. **Method Signature Test**: Verify all expected methods exist with correct signatures
3. **Inheritance Test**: Verify class can be extended as expected
4. **Property Test**: Verify properties are accessible and mutable as expected

### Mock Strategy
```python
# Mock Phase N+1 extending class
class MockExtendedConnection(DatabaseConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_flag = True

# Test that extension works
def test_class_extensibility():
    conn = MockExtendedConnection("postgres://localhost", pool_size=5)
    assert hasattr(conn, 'connection_string')
    assert hasattr(conn, 'pool_size')
    assert hasattr(conn, 'custom_flag')
    assert callable(getattr(conn, 'query'))
    assert callable(getattr(conn, 'close'))
```

---

## Data Flow

Testing data structure contracts between phases.

### Description
Phase N produces data structures that Phase N+1 consumes. The contract includes field names, types, constraints, and serialization format.

### Example Scenario
Phase 1 produces `User` records. Phase 2 consumes them for analytics.

```python
# Phase 1 produces
user_data = {
    "id": "uuid-string",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "metadata": {
        "source": "web_signup",
        "referrer": "google"
    }
}

# Phase 2 expects
expected_schema = {
    "id": str,  # UUID format
    "username": str,  # 3-50 characters
    "email": str,  # Valid email format
    "created_at": str,  # ISO 8601 datetime
    "metadata": dict  # Optional nested object
}
```

### Testing Approach
1. **Schema Validation**: Verify data matches expected schema
2. **Type Checking**: Verify all fields have correct types
3. **Constraint Validation**: Verify data meets constraints (length, format, range)
4. **Serialization Test**: Verify data serializes/deserializes correctly

### Mock Strategy
```python
# Mock data producer
def mock_produce_user():
    return {
        "id": str(uuid.uuid4()),
        "username": "test_user",
        "email": "test@example.com",
        "created_at": datetime.now().isoformat(),
        "metadata": {}
    }

# Mock data consumer
def mock_consume_user(user_data: dict) -> bool:
    # Verify all required fields present
    required = ["id", "username", "email", "created_at"]
    for field in required:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")
    return True
```

---

## API-to-Consumer

Testing API endpoints before the consumer exists.

### Description
Phase N implements API endpoints. Phase N+1 will consume these endpoints. Test the API contract without the actual consumer.

### Example Scenario
Phase 1 implements REST API. Phase 2 will build a frontend that calls these endpoints.

```python
# Phase 1 exports (FastAPI example)
@app.get("/api/v1/users/{user_id}")
def get_user(user_id: str) -> UserResponse:
    pass

@app.post("/api/v1/users")
def create_user(request: CreateUserRequest) -> UserResponse:
    pass

# Phase 2 expects
# GET /api/v1/users/{id} -> 200 OK with user JSON
# POST /api/v1/users -> 201 Created with user JSON
# Error cases -> 4xx/5xx with error JSON
```

### Testing Approach
1. **Endpoint Existence**: Verify endpoints exist at expected paths
2. **Method Validation**: Verify HTTP methods are correct
3. **Request Schema**: Verify request body/params match expected format
4. **Response Schema**: Verify response format matches contract
5. **Status Codes**: Verify correct status codes for success/error cases
6. **Header Validation**: Verify required headers (auth, content-type)

### Mock Strategy
```python
# Mock API consumer
class MockAPIConsumer:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_user(self, user_id: str) -> dict:
        response = requests.get(f"{self.base_url}/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        return data

    def create_user(self, username: str, email: str) -> dict:
        response = requests.post(
            f"{self.base_url}/api/v1/users",
            json={"username": username, "email": email}
        )
        assert response.status_code == 201
        return response.json()
```

---

## Event-Driven

Testing event producers before subscribers exist.

### Description
Phase N emits events that Phase N+1 will subscribe to. Test the event schema and emission without the actual subscriber.

### Example Scenario
Phase 1 emits `user.created` events. Phase 2 will subscribe to these events to send welcome emails.

```python
# Phase 1 emits
event = {
    "type": "user.created",
    "timestamp": "2024-01-15T10:30:00Z",
    "payload": {
        "user_id": "uuid-string",
        "username": "john_doe",
        "email": "john@example.com"
    }
}

# Phase 2 expects
def handle_user_created(event: dict):
    user_id = event["payload"]["user_id"]
    email = event["payload"]["email"]
    send_welcome_email(email, user_id)
```

### Testing Approach
1. **Event Schema**: Verify event structure matches expected format
2. **Event Types**: Verify all expected event types are emitted
3. **Payload Validation**: Verify payload contains required fields
4. **Timing Test**: Verify events are emitted at correct times
5. **Ordering Test**: Verify events are emitted in correct order when sequence matters

### Mock Strategy
```python
# Mock event subscriber
class MockEventSubscriber:
    def __init__(self):
        self.received_events = []

    def handle_event(self, event: dict):
        self.received_events.append(event)

    def assert_event_received(self, event_type: str, payload_matcher: callable = None):
        matching = [e for e in self.received_events if e["type"] == event_type]
        assert len(matching) > 0, f"No events of type {event_type} received"
        if payload_matcher:
            assert any(payload_matcher(e["payload"]) for e in matching)

# Test usage
def test_user_created_event():
    subscriber = MockEventSubscriber()
    # Trigger event emission
    create_user("test_user", "test@example.com")
    # Verify event was emitted correctly
    subscriber.assert_event_received("user.created", lambda p: p["username"] == "test_user")
```

---

## Database Schema

Testing schema migrations and data contracts.

### Description
Phase N creates or modifies database schema. Phase N+1 depends on specific tables, columns, and constraints.

### Example Scenario
Phase 1 creates the users table. Phase 2 will add profile data that references users.

```sql
-- Phase 1 creates
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Phase 2 expects
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    bio TEXT
);
```

### Testing Approach
1. **Table Existence**: Verify expected tables exist
2. **Column Validation**: Verify columns exist with correct types
3. **Constraint Validation**: Verify constraints (PK, FK, unique, check) are in place
4. **Index Validation**: Verify expected indexes exist
5. **Migration Test**: Verify migrations run successfully and are idempotent
6. **Data Integrity**: Verify existing data remains valid after migration

### Mock Strategy
```python
# Mock schema inspector
class MockSchemaInspector:
    def __init__(self, connection):
        self.connection = connection

    def table_exists(self, table_name: str) -> bool:
        result = self.connection.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
            (table_name,)
        )
        return result.fetchone() is not None

    def column_exists(self, table_name: str, column_name: str) -> bool:
        result = self.connection.execute(
            """SELECT 1 FROM information_schema.columns
               WHERE table_name = %s AND column_name = %s""",
            (table_name, column_name)
        )
        return result.fetchone() is not None

    def foreign_key_exists(self, table_name: str, column_name: str, ref_table: str) -> bool:
        result = self.connection.execute(
            """SELECT 1 FROM information_schema.table_constraints tc
               JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
               WHERE tc.constraint_type = 'FOREIGN KEY'
               AND kcu.table_name = %s AND kcu.column_name = %s""",
            (table_name, column_name)
        )
        return result.fetchone() is not None
```

---

## Configuration

Testing configuration contracts between phases.

### Description
Phase N produces configuration that Phase N+1 consumes. The contract includes required/optional keys, value types, and validation rules.

### Example Scenario
Phase 1 sets up application configuration. Phase 2 reads specific config values to initialize services.

```yaml
# Phase 1 produces (config.yaml)
database:
  host: localhost
  port: 5432
  name: myapp
  pool_size: 10

api:
  base_url: https://api.example.com
  timeout: 30
  retries: 3

features:
  enable_caching: true
  cache_ttl: 300

# Phase 2 expects
# database.host (str, required)
# database.port (int, default 5432)
# api.base_url (str, required, must be valid URL)
# features.enable_caching (bool, default false)
```

### Testing Approach
1. **Key Existence**: Verify all required keys exist
2. **Type Validation**: Verify values have expected types
3. **Default Values**: Verify defaults are applied correctly
4. **Validation Rules**: Verify values pass validation (URL format, range, etc.)
5. **Environment Overrides**: Verify environment variables can override config
6. **Secret Handling**: Verify sensitive values are properly secured

### Mock Strategy
```python
# Mock config consumer
class MockConfigConsumer:
    def __init__(self, config: dict):
        self.config = config

    def validate(self) -> List[str]:
        errors = []

        # Required fields
        required = [
            ("database", "host"),
            ("api", "base_url")
        ]
        for path in required:
            if not self._get_nested(path):
                errors.append(f"Missing required config: {'.'.join(path)}")

        # Type validation
        if not isinstance(self._get_nested(("database", "port"), 5432), int):
            errors.append("database.port must be an integer")

        # URL validation
        base_url = self._get_nested(("api", "base_url"))
        if base_url and not base_url.startswith(("http://", "https://")):
            errors.append("api.base_url must be a valid URL")

        return errors

    def _get_nested(self, path: tuple, default=None):
        value = self.config
        for key in path:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
```

---

## Pattern Selection Guide

| Pattern | Use When | Key Tests |
|---------|----------|-----------|
| Function-to-Function | Simple utility functions shared between phases | Signature, behavior, error handling |
| Class-to-Class | Object-oriented design with inheritance | Constructor, methods, extensibility |
| Data Flow | Data structures passed between phases | Schema, types, constraints |
| API-to-Consumer | HTTP/gRPC APIs between phases | Endpoints, request/response, status codes |
| Event-Driven | Asynchronous communication | Event schema, emission timing, ordering |
| Database Schema | Schema changes between phases | Tables, columns, constraints, migrations |
| Configuration | Config-driven behavior | Keys, types, defaults, validation |

---

## Combining Patterns

Real-world phase boundaries often involve multiple patterns:

```python
# Example: Phase 1 creates API that uses database and emits events

# Patterns involved:
# 1. API-to-Consumer: REST endpoints
# 2. Database Schema: User table
# 3. Event-Driven: user.created events
# 4. Configuration: Database connection config

# Test all patterns together:
def test_phase_1_integration():
    # Setup: Load config
    config = load_config()

    # Setup: Initialize database
    db = DatabaseConnection(config["database"])

    # Setup: Mock event subscriber
    event_subscriber = MockEventSubscriber()

    # Setup: Mock API consumer (Phase 2)
    api_consumer = MockAPIConsumer("http://localhost:8000")

    # Execute: Create user via API
    response = api_consumer.create_user("test", "test@example.com")

    # Verify: Database state
    user = db.query("SELECT * FROM users WHERE username = %s", ("test",))
    assert user is not None

    # Verify: Event emitted
    event_subscriber.assert_event_received("user.created")

    # Verify: API response
    assert response["username"] == "test"
```
