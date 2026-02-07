# horde-prompt Tests

Test suite for the horde-prompt skill.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_generation.py -v
```

## Test Categories

- `test_generation.py`: Prompt generation functionality
- `test_compression.py`: Token compression utilities
- `test_validation.py`: Prompt validation

## Adding Tests

When adding new agent types or optimization strategies,
add corresponding tests to verify functionality.
