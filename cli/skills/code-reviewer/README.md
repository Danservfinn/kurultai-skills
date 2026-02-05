# Code Reviewer Skill

A comprehensive code review skill for Kurultai that analyzes code for bugs, security issues, performance problems, and best practices.

## Overview

The code-reviewer skill provides structured, thorough code reviews with actionable feedback. It follows industry best practices and covers multiple dimensions of code quality.

## Installation

```bash
kurultai install code-reviewer
```

## Usage

### Basic Usage

Review a single file:
```bash
kurultai run code-reviewer --file src/main.py
```

Review an entire directory:
```bash
kurultai run code-reviewer --dir src/
```

### Advanced Options

Thorough review with detailed analysis:
```bash
kurultai run code-reviewer --file src/main.py --depth thorough
```

Quick review for rapid feedback:
```bash
kurultai run code-reviewer --file src/main.py --depth quick
```

Review specific aspects only:
```bash
kurultai run code-reviewer --file src/main.py --focus security,performance
```

Review a pull request:
```bash
kurultai run code-reviewer --pr 123
```

Review with custom configuration:
```bash
kurultai run code-reviewer --file src/main.py --config review-config.yaml
```

## Review Coverage

### 1. Bug Detection
- Logic errors and edge cases
- Null/undefined dereferences
- Off-by-one errors
- Race conditions
- Resource leaks
- Type mismatches

### 2. Security Analysis
- Injection vulnerabilities (SQL, Command, etc.)
- XSS and CSRF vulnerabilities
- Authentication/Authorization issues
- Sensitive data exposure
- Input validation gaps
- Cryptographic weaknesses

### 3. Performance Review
- Algorithmic complexity
- Database query efficiency
- Memory usage patterns
- I/O operation optimization
- Caching strategies
- Resource contention

### 4. Code Quality
- Readability and maintainability
- Test coverage adequacy
- Error handling patterns
- Documentation completeness
- Consistency with conventions

### 5. Architecture & Design
- SOLID principles adherence
- Design pattern usage
- API design quality
- Separation of concerns

## Output Format

Reviews are provided in a structured format with:

- **Critical Issues**: Must fix before merge
- **Warnings**: Should fix, may block merge
- **Suggestions**: Nice to have improvements
- **Positive Findings**: Acknowledgment of good practices
- **Action Items**: Prioritized checklist

## Supported Languages

- Python
- JavaScript / TypeScript
- Java
- Go
- Rust
- Ruby
- C#

## Configuration

Create a `review-config.yaml` to customize the review:

```yaml
# Review depth: quick, standard, thorough
depth: standard

# Focus areas (empty = all)
focus:
  - security
  - performance
  # - bugs
  # - quality
  # - architecture

# Ignore patterns
ignore:
  - "*.test.js"
  - "*_mock.go"
  - "vendor/"

# Severity thresholds
thresholds:
  max_critical: 0
  max_warnings: 10

# Language-specific settings
languages:
  python:
    max_line_length: 100
    check_type_hints: true
  javascript:
    check_async_await: true
    check_types: true
```

## Examples

### Example 1: Reviewing a Python Module

```bash
kurultai run code-reviewer --file api/auth.py
```

Sample output:
```markdown
## Code Review Summary

**File(s)**: api/auth.py
**Overall Rating**: Needs Work
**Risk Level**: High

---

## Critical Issues (Must Fix)

### 1. SQL Injection Vulnerability
- **Location**: Line 45
- **Severity**: Critical
- **Description**: User input is directly interpolated into SQL query
- **Impact**: Attackers could extract or modify database data
- **Recommendation**: Use parameterized queries

```python
# Instead of:
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Use:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
```

### Example 2: Reviewing a JavaScript PR

```bash
kurultai run code-reviewer --pr 456 --depth thorough
```

### Example 3: Focused Security Review

```bash
kurultai run code-reviewer --dir src/ --focus security
```

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Code Review
        run: kurultai run code-reviewer --pr ${{ github.event.pull_request.number }}
```

## Best Practices

1. **Review Early**: Run reviews before requesting human review
2. **Iterate**: Address critical issues first, then warnings
3. **Learn**: Use suggestions to improve your coding skills
4. **Customize**: Adjust configuration for your team's standards
5. **Combine**: Use alongside human reviewers for best results

## Contributing

To contribute improvements to this skill:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various code samples
5. Submit a pull request

## License

MIT License - See LICENSE file for details
