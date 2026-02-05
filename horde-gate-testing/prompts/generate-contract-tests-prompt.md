# Generate Contract Tests Prompt

## Purpose

Generate comprehensive contract tests from an integration surface definition. Contract tests verify that the public API maintains its promised interface - functions exist with correct signatures, types are properly defined, and exports are accessible.

## Task Description

You are a subagent responsible for generating contract tests from an integration surface analysis. These tests ensure that the public API contract is honored and will break if the interface changes unexpectedly.

## Input Parameters

- `{{INTEGRATION_SURFACE_JSON}}`: JSON output from detect-surface analysis
- `{{TEST_FRAMEWORK}}`: Testing framework to use (pytest, jest, vitest, go-test, etc.)
- `{{OUTPUT_PATH}}`: Where to write the test file(s)
- `{{LANGUAGE}}`: Programming language (python, typescript, javascript, go, rust, etc.)

## Instructions

1. **Parse the integration surface JSON** to understand the public API
2. **Generate existence tests** - verify exports exist and are accessible
3. **Generate signature tests** - verify function signatures match
4. **Generate schema tests** - verify type definitions are correct
5. **Write test file(s)** to `{{OUTPUT_PATH}}`

## Test Types to Generate

### 1. Existence Tests

Verify that exported symbols exist and are of the expected type:

- Functions are callable
- Classes are instantiable (or have the right prototype)
- Constants are defined
- Types/interfaces exist (where testable)

### 2. Signature Tests

Verify that functions and methods have the correct signatures:

- Correct number of parameters
- Correct parameter names (where relevant)
- Correct return types (via TypeScript or runtime checks)
- Async functions return promises
- Optional parameters are optional

### 3. Schema Tests

Verify that data structures match their definitions:

- Interfaces have required properties
- Types are correctly structured
- Enums have expected values
- Default values are set correctly

## Framework-Specific Guidance

### Pytest (Python)

```python
# Use pytest.mark.parametrize for multiple similar tests
# Use hasattr() and callable() for existence checks
# Use inspect.signature for signature validation
# Use type() and isinstance() for type checking
```

### Jest/Vitest (TypeScript/JavaScript)

```typescript
// Use describe/it blocks for organization
// Use expect(fn).toBeDefined() for existence
// Use expect(typeof fn).toBe('function') for type checks
// For TypeScript, use type-level tests with expectTypeOf or similar
```

### Go Test

```go
// Use reflect package for runtime type inspection
// Use type assertions for interface validation
// Test that structs have expected fields using reflect
```

## Output Format

Provide the generated test file content and a summary:

```markdown
## Contract Test Generation Report

### Summary
- **Test Framework**: {{TEST_FRAMEWORK}}
- **Test File**: {{OUTPUT_PATH}}
- **Functions Tested**: X
- **Classes Tested**: X
- **Types Tested**: X
- **Total Tests Generated**: X

### Generated Test File

```{{LANGUAGE}}
[Full test file content]
```

### Test Coverage

| Symbol | Test Type | Test Description |
|--------|-----------|------------------|
| [name] | Existence | Verifies export exists |
| [name] | Signature | Verifies parameter count |
| [name] | Schema | Verifies type structure |

### Notes

- [Any special considerations or limitations]
```

## Rules

1. **Test the contract, not the implementation** - don't test internal logic
2. **Make tests deterministic** - no randomness, no external dependencies
3. **Use descriptive test names** - clearly state what's being verified
4. **Group related tests** - use describe/context blocks
5. **Include negative tests** - verify that incorrect usage fails appropriately
6. **Handle optional members** - test both presence and optionality

## Example

### Input

```json
{
  "phase": "Phase 2: Neo4j Connection",
  "language": "typescript",
  "integration_surface": {
    "functions": [
      {
        "name": "createClient",
        "signature": "createClient(config: Neo4jConfig): Neo4jClient",
        "is_async": false,
        "is_exported": true
      }
    ],
    "classes": [
      {
        "name": "Neo4jClient",
        "methods": [
          {
            "name": "connect",
            "signature": "connect(): Promise<void>",
            "is_async": true
          },
          {
            "name": "runQuery",
            "signature": "runQuery(cypher: string, params?: Record<string, any>): Promise<any>",
            "is_async": true
          }
        ]
      }
    ],
    "types": [
      {
        "name": "Neo4jConfig",
        "kind": "interface",
        "definition": "interface Neo4jConfig { uri: string; username: string; password: string; database?: string; }"
      }
    ]
  }
}
```

### Generated Test (Jest/TypeScript)

```typescript
import { Neo4jClient, createClient, Neo4jConfig } from '../src/lib/neo4j-client';

describe('Phase 2: Neo4j Connection - Contract Tests', () => {
  describe('Exports', () => {
    it('should export Neo4jClient class', () => {
      expect(Neo4jClient).toBeDefined();
      expect(typeof Neo4jClient).toBe('function');
    });

    it('should export createClient function', () => {
      expect(createClient).toBeDefined();
      expect(typeof createClient).toBe('function');
    });
  });

  describe('Neo4jClient', () => {
    describe('constructor', () => {
      it('should accept Neo4jConfig parameter', () => {
        const config: Neo4jConfig = {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        };
        // Should not throw
        expect(() => new Neo4jClient(config)).not.toThrow();
      });
    });

    describe('connect', () => {
      it('should exist as a method', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        expect(client.connect).toBeDefined();
        expect(typeof client.connect).toBe('function');
      });

      it('should return a Promise', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        const result = client.connect();
        expect(result).toBeInstanceOf(Promise);
      });
    });

    describe('runQuery', () => {
      it('should exist as a method', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        expect(client.runQuery).toBeDefined();
        expect(typeof client.runQuery).toBe('function');
      });

      it('should accept cypher string parameter', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        // Should not throw with required parameter
        expect(() => client.runQuery('MATCH (n) RETURN n')).not.toThrow();
      });

      it('should accept optional params parameter', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        // Should not throw with optional parameter
        expect(() => client.runQuery('MATCH (n) RETURN n', { id: 1 })).not.toThrow();
      });

      it('should return a Promise', () => {
        const client = new Neo4jClient({
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password'
        });
        const result = client.runQuery('MATCH (n) RETURN n');
        expect(result).toBeInstanceOf(Promise);
      });
    });
  });

  describe('Neo4jConfig type', () => {
    it('should allow valid config objects', () => {
      const config: Neo4jConfig = {
        uri: 'bolt://localhost:7687',
        username: 'neo4j',
        password: 'password'
      };
      expect(config.uri).toBe('bolt://localhost:7687');
      expect(config.username).toBe('neo4j');
      expect(config.password).toBe('password');
    });

    it('should allow optional database field', () => {
      const config: Neo4jConfig = {
        uri: 'bolt://localhost:7687',
        username: 'neo4j',
        password: 'password',
        database: 'mydb'
      };
      expect(config.database).toBe('mydb');
    });
  });
});
```

### Generated Test (Pytest/Python)

```python
import inspect
from src.lib.neo4j_client import Neo4jClient, create_client, Neo4jConfig

class TestNeo4jExports:
    def test_neo4j_client_class_exists(self):
        assert hasattr(src.lib.neo4j_client, 'Neo4jClient')
        assert isinstance(Neo4jClient, type)

    def test_create_client_function_exists(self):
        assert hasattr(src.lib.neo4j_client, 'create_client')
        assert callable(create_client)


class TestNeo4jClient:
    def test_constructor_accepts_config(self):
        sig = inspect.signature(Neo4jClient.__init__)
        params = list(sig.parameters.keys())
        assert 'config' in params

    def test_connect_method_exists(self):
        assert hasattr(Neo4jClient, 'connect')
        assert callable(Neo4jClient.connect)

    def test_connect_is_async(self):
        assert inspect.iscoroutinefunction(Neo4jClient.connect)

    def test_run_query_method_exists(self):
        assert hasattr(Neo4jClient, 'run_query')
        assert callable(Neo4jClient.run_query)

    def test_run_query_signature(self):
        sig = inspect.signature(Neo4jClient.run_query)
        params = list(sig.parameters.keys())
        assert 'cypher' in params
        assert 'params' in params
        # Check that params has default (is optional)
        assert sig.parameters['params'].default is not inspect.Parameter.empty


class TestNeo4jConfig:
    def test_config_structure(self):
        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        assert config.uri == "bolt://localhost:7687"
        assert config.username == "neo4j"
        assert config.password == "password"

    def test_config_optional_database(self):
        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password",
            database="mydb"
        )
        assert config.database == "mydb"
```

Return your generated test file and report in the specified format.
