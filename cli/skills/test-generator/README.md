# Test Generator Skill

A comprehensive test generation skill for Kurultai that creates unit tests, integration tests, edge case tests, and property-based tests from code analysis.

## Overview

The test-generator skill analyzes source code and generates thorough test suites that validate functionality, catch edge cases, and ensure code reliability.

## Installation

```bash
kurultai install test-generator
```

## Usage

### Basic Usage

Generate tests for a single file:
```bash
kurultai run test-generator --file src/calculator.py
```

Generate tests for an entire project:
```bash
kurultai run test-generator --dir src/ --output tests/
```

### Test Types

Generate only unit tests:
```bash
kurultai run test-generator --file src/calculator.py --type unit
```

Generate edge case tests:
```bash
kurultai run test-generator --file src/calculator.py --type edge_cases
```

Generate integration test scaffolding:
```bash
kurultai run test-generator --file src/api.py --type integration
```

### Framework Selection

Generate tests with specific framework:
```bash
kurultai run test-generator --file src/utils.js --framework jest
```

Auto-detect framework from project:
```bash
kurultai run test-generator --file src/utils.py --framework auto
```

### Advanced Options

Generate tests with mocks for dependencies:
```bash
kurultai run test-generator --file src/api.py --with-mocks
```

Generate property-based tests:
```bash
kurultai run test-generator --file src/sorting.py --property-based
```

Update existing test file:
```bash
kurultai run test-generator --file src/calculator.py --update tests/test_calculator.py
```

## Features

### 1. Comprehensive Test Coverage
- **Happy Path Tests**: Normal operation scenarios
- **Edge Case Tests**: Boundary values and corner cases
- **Error Case Tests**: Exception and error handling
- **State-Based Tests**: State transitions and side effects
- **Integration Tests**: External dependency interactions

### 2. Multi-Language Support
- Python (pytest, unittest)
- JavaScript/TypeScript (Jest, Mocha, Vitest)
- Java (JUnit 4/5, TestNG)
- Go (testing, testify)
- Rust (built-in test framework)
- Ruby (RSpec, Minitest)
- C# (NUnit, xUnit, MSTest)

### 3. Testing Patterns
- Arrange-Act-Assert structure
- Table-driven tests
- Parameterized tests
- Property-based testing
- Snapshot testing
- Mock/stub generation

### 4. Smart Analysis
- Identifies all code paths
- Detects boundary conditions
- Recognizes error scenarios
- Suggests mock points
- Estimates coverage

## Output Examples

### Python Test Generation

Input file `calculator.py`:
```python
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

Generated tests:
```python
import pytest
from calculator import divide


class TestDivide:
    """Test cases for divide function."""

    def test_happy_path_basic(self):
        """Test normal division operation."""
        result = divide(10, 2)
        assert result == 5.0

    def test_happy_path_negative_numbers(self):
        """Test division with negative numbers."""
        result = divide(-10, 2)
        assert result == -5.0
        result = divide(10, -2)
        assert result == -5.0
        result = divide(-10, -2)
        assert result == 5.0

    def test_happy_path_float_result(self):
        """Test division resulting in float."""
        result = divide(7, 2)
        assert result == 3.5

    def test_edge_case_zero_dividend(self):
        """Test division with zero dividend."""
        result = divide(0, 5)
        assert result == 0.0

    def test_edge_case_very_small_divisor(self):
        """Test division with very small divisor."""
        result = divide(1, 0.0001)
        assert result == 10000.0

    def test_error_case_divide_by_zero(self):
        """Test that division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

    @pytest.mark.parametrize("a,b,expected", [
        (10, 2, 5.0),
        (15, 3, 5.0),
        (100, 4, 25.0),
        (1, 4, 0.25),
    ])
    def test_multiple_cases(self, a, b, expected):
        """Test various division scenarios."""
        result = divide(a, b)
        assert result == expected
```

### JavaScript Test Generation

Input file `stringUtils.js`:
```javascript
export function truncate(str, maxLength) {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + '...';
}
```

Generated tests:
```javascript
import { truncate } from './stringUtils';

describe('truncate', () => {
  describe('happy path', () => {
    test('should truncate long strings', () => {
      expect(truncate('Hello World', 5)).toBe('Hello...');
    });

    test('should not truncate short strings', () => {
      expect(truncate('Hi', 10)).toBe('Hi');
    });

    test('should handle exact length strings', () => {
      expect(truncate('Hello', 5)).toBe('Hello');
    });
  });

  describe('edge cases', () => {
    test('should handle empty string', () => {
      expect(truncate('', 5)).toBe('');
    });

    test('should handle null input', () => {
      expect(truncate(null, 5)).toBe('');
    });

    test('should handle undefined input', () => {
      expect(truncate(undefined, 5)).toBe('');
    });

    test('should handle zero maxLength', () => {
      expect(truncate('Hello', 0)).toBe('...');
    });

    test('should handle negative maxLength', () => {
      expect(truncate('Hello', -1)).toBe('...');
    });
  });

  describe('special characters', () => {
    test('should handle unicode characters', () => {
      expect(truncate('Hello 🌍 World', 7)).toBe('Hello 🌍...');
    });

    test('should handle multibyte characters', () => {
      expect(truncate('日本語テキスト', 3)).toBe('日本語...');
    });
  });
});
```

## Configuration

Create a `test-config.yaml` to customize generation:

```yaml
# Test framework settings
framework:
  name: pytest  # auto, pytest, jest, junit, etc.
  version: "7.x"

# Test types to generate
types:
  - unit
  - edge_cases
  # - integration
  # - property_based

# Coverage targets
coverage:
  lines: 80
  branches: 70
  functions: 90

# Naming conventions
naming:
  test_prefix: "test_"
  class_suffix: "Test"
  descriptive_names: true

# Mock configuration
mocks:
  auto_mock_dependencies: true
  mock_external_apis: true
  mock_database: true

# Output settings
output:
  directory: tests/
  file_pattern: "test_{filename}"
  separate_integration: true
```

## Edge Cases Covered

The skill automatically generates tests for:

### Input Boundaries
- Empty values ("", [], {}, null, undefined)
- Zero values
- Maximum/minimum values
- Whitespace-only strings
- Unicode characters
- Very long strings
- Special characters

### Type Boundaries
- Wrong types
- Type coercion edge cases
- Null/undefined where object expected

### Numeric Boundaries
- Division by zero
- Floating point precision
- Integer overflow
- Negative numbers

### Collection Boundaries
- Empty collections
- Single element collections
- Duplicate elements
- Null elements in collections

## Integration

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: generate-tests
        name: Generate Missing Tests
        entry: kurultai run test-generator --check-coverage
        language: system
```

### CI/CD Pipeline

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  generate-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Tests
        run: kurultai run test-generator --dir src/ --output tests/
      - name: Run Tests
        run: pytest tests/
      - name: Check Coverage
        run: pytest --cov=src --cov-fail-under=80
```

## Best Practices

1. **Review Generated Tests**: Always review and refine generated tests
2. **Add Business Logic Tests**: Supplement with domain-specific test cases
3. **Maintain Test Independence**: Each test should be self-contained
4. **Use Descriptive Names**: Test names should explain the scenario
5. **Test Behavior, Not Implementation**: Focus on what, not how
6. **Keep Tests Fast**: Avoid slow operations in unit tests
7. **Update Tests with Code**: Regenerate when functionality changes

## Tips for Better Tests

### For Python
- Use pytest for rich features
- Leverage fixtures for setup
- Use parametrize for multiple cases
- Add type hints for better test generation

### For JavaScript
- Use Jest for comprehensive features
- Leverage describe blocks for organization
- Use beforeEach/afterEach for setup
- Test async code properly

### For Java
- Use JUnit 5 for modern features
- Leverage @DisplayName for readability
- Use @ParameterizedTest for multiple cases
- Consider AssertJ for fluent assertions

## Troubleshooting

### Missing Tests
If tests are missing for functions:
1. Check that functions are exported/public
2. Verify file is in supported language
3. Check include patterns in configuration

### Framework Detection Issues
If wrong framework is detected:
1. Specify framework explicitly with `--framework`
2. Check for framework configuration files
3. Verify dependencies in package.json/requirements.txt

### Coverage Gaps
If coverage is incomplete:
1. Run with `--with-mocks` for dependency coverage
2. Add property-based tests for complex logic
3. Manually add integration tests

## Contributing

To contribute improvements:

1. Fork the repository
2. Add support for new testing frameworks
3. Improve test pattern detection
4. Add new edge case categories
5. Submit a pull request

## License

MIT License - See LICENSE file for details
