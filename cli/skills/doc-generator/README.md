# Documentation Generator Skill

A comprehensive documentation generation skill for Kurultai that creates API docs, usage guides, README files, and more from source code analysis.

## Overview

The doc-generator skill analyzes source code and generates high-quality documentation including:
- API reference documentation
- Usage guides with examples
- README files
- Changelogs
- Developer guides

## Installation

```bash
kurultai install doc-generator
```

## Usage

### Basic Usage

Generate documentation for a single file:
```bash
kurultai run doc-generator --file src/api.py
```

Generate documentation for an entire project:
```bash
kurultai run doc-generator --dir src/ --output docs/
```

### Documentation Types

Generate only API documentation:
```bash
kurultai run doc-generator --file src/api.py --type api
```

Generate usage guide:
```bash
kurultai run doc-generator --file src/api.py --type usage
```

Generate README:
```bash
kurultai run doc-generator --dir . --type readme
```

### Output Formats

Generate HTML documentation:
```bash
kurultai run doc-generator --file src/api.py --format html
```

Generate JSON for programmatic use:
```bash
kurultai run doc-generator --file src/api.py --format json
```

### Advanced Options

Include private/internal members:
```bash
kurultai run doc-generator --file src/api.py --include-private
```

Comprehensive documentation with all details:
```bash
kurultai run doc-generator --file src/api.py --depth comprehensive
```

Watch mode for continuous regeneration:
```bash
kurultai run doc-generator --dir src/ --watch
```

## Features

### 1. Automatic Extraction
- Parses docstrings and comments
- Extracts type information
- Identifies public APIs
- Finds usage examples in tests

### 2. Multiple Output Formats
- **Markdown**: Great for GitHub/GitLab
- **HTML**: Standalone documentation sites
- **JSON**: Programmatic consumption

### 3. Language Support
- Python (Google, NumPy, Sphinx docstrings)
- JavaScript/TypeScript (JSDoc)
- Java (Javadoc)
- Go (GoDoc)
- Rust (rustdoc)
- Ruby (RDoc/YARD)
- C# (XML documentation)

### 4. Documentation Types
- **API Reference**: Complete function/class documentation
- **Usage Guide**: Tutorials and how-to guides
- **README**: Project overview and quick start
- **Changelog**: Version history and changes

## Output Examples

### API Documentation Example

Input file `calculator.py`:
```python
def calculate(expression: str, precision: int = 2) -> float:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: Mathematical expression to evaluate
        precision: Number of decimal places (default: 2)

    Returns:
        Calculated result as a float

    Raises:
        ValueError: If expression is invalid or unsafe
        TypeError: If precision is not an integer

    Example:
        >>> calculate("2 + 2")
        4.0
        >>> calculate("10 / 3", precision=4)
        3.3333
    """
    ...
```

Generated documentation:
```markdown
### calculate()

Evaluate a mathematical expression safely.

```python
calculate(expression: str, precision: int = 2) -> float
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| expression | str | Yes | Mathematical expression to evaluate |
| precision | int | No | Number of decimal places (default: 2) |

**Returns:**
| Type | Description |
|------|-------------|
| float | Calculated result |

**Raises:**
| Exception | Condition |
|-----------|-----------|
| ValueError | If expression is invalid or unsafe |
| TypeError | If precision is not an integer |

**Example:**
```python
>>> calculate("2 + 2")
4.0
>>> calculate("10 / 3", precision=4)
3.3333
```
```

### README Generation Example

```bash
kurultai run doc-generator --dir . --type readme --output README.md
```

Generates a complete README with:
- Project title and description
- Feature list
- Installation instructions
- Quick start example
- Links to full documentation
- Contributing guidelines
- License information

## Configuration

Create a `doc-config.yaml` to customize generation:

```yaml
# Output settings
output:
  format: markdown
  directory: docs/
  single_file: false

# Documentation types to generate
types:
  - api
  - usage
  - readme

# Language-specific settings
languages:
  python:
    docstring_style: google  # google, numpy, sphinx
    include_type_hints: true
  javascript:
    include_jsdoc: true
    extract_prop_types: true

# Content options
include:
  private: false
  examples: true
  tests_as_examples: true
  source_links: true

# Template customization
templates:
  api_template: custom/api.md
  readme_template: custom/readme.md
```

## Integration

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: generate-docs
        name: Generate Documentation
        entry: kurultai run doc-generator --dir src/ --check
        language: system
```

### CI/CD Pipeline

```yaml
# .github/workflows/docs.yml
name: Documentation
on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Documentation
        run: kurultai run doc-generator --dir src/ --output docs/
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### VS Code Extension

Configure VS Code to use doc-generator:

```json
{
  "kurultai.doc-generator.onSave": true,
  "kurultai.doc-generator.format": "markdown"
}
```

## Best Practices

1. **Write Good Docstrings**: The quality of generated docs depends on source comments
2. **Use Type Hints**: Types improve documentation accuracy
3. **Include Examples**: Real code examples help users understand usage
4. **Document Exceptions**: Always document what errors can be raised
5. **Keep Docs Updated**: Regenerate docs when code changes
6. **Review Generated Docs**: Always review and refine generated output

## Tips for Better Documentation

### For Python
- Use Google-style docstrings for best results
- Add type hints to all function signatures
- Include doctest examples

### For JavaScript/TypeScript
- Use JSDoc comments consistently
- Define interfaces for complex objects
- Document component props

### For Java
- Write comprehensive Javadoc
- Use @param, @return, @throws tags
- Include @since for API versioning

## Troubleshooting

### Missing Documentation
If documentation is missing:
1. Check that source files have docstrings/comments
2. Verify file is in supported language
3. Check include patterns in configuration

### Incorrect Types
If types are incorrect:
1. Add explicit type hints/annotations
2. Check language-specific type syntax
3. Verify imports are resolvable

### Formatting Issues
If output formatting is wrong:
1. Check output format setting
2. Verify template files exist
3. Try different format option

## Contributing

To contribute improvements:

1. Fork the repository
2. Add support for new language features
3. Improve extraction accuracy
4. Add new output formats
5. Submit a pull request

## License

MIT License - See LICENSE file for details
