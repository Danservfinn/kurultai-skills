# Creating Skills for Kurultai

This guide walks you through creating, testing, and publishing skills for the Kurultai marketplace.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Skill Structure](#skill-structure)
3. [The skill.yaml Manifest](#the-skillyaml-manifest)
4. [Creating Prompts](#creating-prompts)
5. [Testing Your Skill](#testing-your-skill)
6. [Publishing](#publishing)
7. [Best Practices](#best-practices)
8. [Integrating with horde-swarm](#integrating-with-horde-swarm)

---

## Quick Start

```bash
# Install Kurultai CLI
pip install kurultai

# Create a new skill from template
kurultai create my-first-skill --template basic

# Test it locally
kurultai test my-first-skill

# Publish to GitHub
kurultai publish my-first-skill --repo github.com/yourname/my-first-skill
```

---

## Skill Structure

A minimal skill has this structure:

```
my-skill/
├── skill.yaml          # Required: Skill manifest
├── README.md           # Required: Documentation
└── prompts/
    └── main.md         # Required: Main prompt
```

A complete skill includes:

```
my-skill/
├── skill.yaml          # Skill manifest
├── README.md           # User documentation
├── CHANGELOG.md        # Version history
├── prompts/
│   ├── main.md         # Main prompt template
│   ├── system.md       # System prompt additions
│   └── examples.md     # Few-shot examples
├── config/
│   ├── schema.json     # Configuration JSON schema
│   └── defaults.yaml   # Default configuration values
├── resources/
│   └── assets/         # Images, icons, etc.
└── tests/
    └── test_skill.py   # Validation tests
```

---

## The skill.yaml Manifest

The `skill.yaml` file is the heart of your skill. It declares metadata, dependencies, permissions, and entry points.

### Minimal Example

```yaml
skill:
  id: my-skill
  version: 1.0.0
  name: My First Skill
  description: A brief description of what this skill does
  author: Your Name
  license: MIT

  entry_points:
    default: prompts/main.md
```

### Complete Example

```yaml
skill:
  # Core metadata
  id: my-skill
  version: 1.0.0
  name: My Advanced Skill
  description: |
    A multi-line description that explains
    what this skill does and when to use it.
  author: Your Name <you@example.com>
  license: MIT
  homepage: https://github.com/yourname/my-skill
  repository: https://github.com/yourname/my-skill.git

  # Categorization
  categories:
    - automation
    - analysis
  keywords:
    - keyword1
    - keyword2

  # Horde integration
  horde:
    compatible: true
    requires: horde-swarm>=1.0.0
    swarm_patterns:
      - multi-perspective
      - divide-conquer
    agent_types:
      - researcher
      - developer

  # Dependencies on other skills
  dependencies:
    skills:
      - id: horde-swarm
        version: ^1.0.0
        optional: false
      - id: helper-skill
        version: ~2.1.0
        optional: true

  # System requirements
  system:
    min_claude_version: "1.0.0"
    required_tools:
      - Read
      - Write
      - Task
    optional_tools:
      - Bash

  # Permission declarations
  permissions:
    filesystem:
      read:
        - "{{workspace}}/**"
      write:
        - "{{workspace}}/output/**"
    network:
      allowed_hosts:
        - "api.example.com"
    tools:
      allowed:
        - Read
        - Write
        - Task
      blocked:
        - Bash
    delegation:
      max_subagents: 5
      allowed_agents:
        - researcher
        - developer

  # Configuration schema
  configuration:
    schema: config/schema.json
    defaults: config/defaults.yaml

  # Entry points
  entry_points:
    default: prompts/main.md
    commands:
      analyze:
        description: "Run analysis mode"
        prompt: prompts/analyze.md
      report:
        description: "Generate report"
        prompt: prompts/report.md

  # Resource limits
  resources:
    max_execution_time: 300
    max_memory_mb: 512
    max_context_tokens: 10000

  # Provenance
  provenance:
    source_commit: "abc123..."
    signatures:
      - key_id: your-signing-key
        signature: "base64..."
```

### Field Reference

#### Core Metadata

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (lowercase, hyphens) |
| `version` | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| `name` | Yes | Human-readable name |
| `description` | Yes | What the skill does |
| `author` | No | Author name/email |
| `license` | No | SPDX license identifier |
| `homepage` | No | URL to project page |
| `repository` | No | URL to source code |

#### Horde Integration

| Field | Description |
|-------|-------------|
| `horde.compatible` | Whether skill works with horde-swarm |
| `horde.requires` | Minimum horde-swarm version |
| `horde.swarm_patterns` | Which patterns this skill uses |
| `horde.agent_types` | Agent types this skill dispatches |

#### Dependencies

```yaml
dependencies:
  skills:
    - id: other-skill
      version: ^1.0.0      # semver range
      optional: false      # true if not required
```

Version constraints:
- `^1.0.0` - Compatible with 1.x.x (recommended)
- `~1.0.0` - Compatible with 1.0.x
- `>=1.0.0` - 1.0.0 or higher
- `1.0.0` - Exact version

#### Permissions

Permissions are declarative - they document what your skill needs, and the system enforces them.

```yaml
permissions:
  filesystem:
    read: ["{{workspace}}/**"]      # Glob patterns
    write: ["{{workspace}}/out/**"]
    delete: []                       # No delete permission

  network:
    allowed_hosts: ["api.github.com"]
    blocked_hosts: ["internal.network"]

  tools:
    allowed: [Read, Write, Task]
    blocked: [Bash]                  # Explicitly blocked
    require_confirmation: [Edit]     # Ask before using

  delegation:
    max_subagents: 5
    allowed_agents: [researcher, developer]
    blocked_agents: [admin]
```

---

## Creating Prompts

Prompts are the instructions that guide Claude when executing your skill.

### Main Prompt (prompts/main.md)

```markdown
# My Skill

You are an expert at [domain]. Your task is to [objective].

## Instructions

1. First, [step one]
2. Then, [step two]
3. Finally, [step three]

## Output Format

Provide your response in the following format:

```yaml
result:
  summary: "Brief summary"
  details: "Detailed explanation"
  recommendations:
    - "Recommendation 1"
    - "Recommendation 2"
```

## Constraints

- [Constraint 1]
- [Constraint 2]
```

### System Prompt (prompts/system.md)

System prompts add context to every interaction:

```markdown
You are an expert [role] with 10+ years of experience.

Your expertise includes:
- Area 1
- Area 2
- Area 3

Always follow these principles:
1. Be thorough and detailed
2. Provide concrete examples
3. Consider edge cases
```

### Few-Shot Examples (prompts/examples.md)

Examples help Claude understand the expected input/output format:

```markdown
## Example 1: Simple Case

Input: [simple input]

Output:
```yaml
result:
  summary: "Simple result"
  details: "Explanation"
```

## Example 2: Complex Case

Input: [complex input]

Output:
```yaml
result:
  summary: "Complex result"
  details: "Detailed explanation"
  recommendations:
    - "Do this"
    - "Then do that"
```
```

---

## Testing Your Skill

### Local Testing

```bash
# Test skill loading
kurultai validate my-skill

# Test skill execution
kurultai test my-skill --input "test input"

# Test with specific configuration
kurultai test my-skill --config test-config.yaml

# Run all tests
kurultai test my-skill --full
```

### Writing Tests

Create `tests/test_skill.py`:

```python
import pytest
from kurultai.testing import SkillTestCase

class TestMySkill(SkillTestCase):
    skill_id = "my-skill"

    def test_basic_execution(self):
        result = self.run_skill("test input")
        assert result.status == "success"
        assert "expected" in result.output

    def test_with_config(self):
        result = self.run_skill(
            "test input",
            config={"option": "value"}
        )
        assert result.output["config_applied"] == True

    def test_error_handling(self):
        result = self.run_skill("invalid input")
        assert result.status == "error"
        assert "error_message" in result.output
```

### Integration Testing

Test your skill with other skills:

```bash
# Test in a workflow
kurultai workflow test --file test-workflow.yaml
```

---

## Publishing

### Pre-Publication Checklist

- [ ] `skill.yaml` is valid
- [ ] `README.md` is complete
- [ ] Tests pass
- [ ] Version is updated
- [ ] No secrets in code
- [ ] License is specified

### Publishing to GitHub

```bash
# Create GitHub repo first
gh repo create yourname/my-skill --public

# Publish
kurultai publish my-skill --repo github.com/yourname/my-skill
```

This will:
1. Validate the skill
2. Create a git commit
3. Push to GitHub
4. Create a tag for the version
5. Update the registry index

### Version Updates

```bash
# Update version in skill.yaml
# Then publish
kurultai publish my-skill --bump patch  # or minor, major
```

---

## Best Practices

### 1. Single Responsibility

Each skill should do one thing well:

```yaml
# Good: Focused skill
id: code-reviewer
name: Code Reviewer
description: Reviews code for bugs and style issues

# Bad: Too broad
id: dev-toolkit
name: Developer Toolkit
description: Does code review, testing, deployment, documentation...
```

### 2. Clear Input/Output Contracts

Document what your skill expects and produces:

```markdown
## Input

- `code`: String containing code to review
- `language`: Programming language (optional, auto-detected)

## Output

```yaml
review:
  summary: "Brief overview"
  issues:
    - severity: "error|warning|info"
      line: 42
      message: "Description of issue"
      suggestion: "How to fix"
```
```

### 3. Graceful Error Handling

```python
# In your skill logic
try:
    result = process(input_data)
except ValidationError as e:
    return {
        "status": "error",
        "error_type": "validation",
        "message": str(e),
        "suggestion": "Check your input format"
    }
except ExternalAPIError as e:
    return {
        "status": "error",
        "error_type": "external",
        "message": "External service unavailable",
        "retryable": True
    }
```

### 4. Minimal Permissions

Request only the permissions you need:

```yaml
# Good: Minimal permissions
permissions:
  filesystem:
    read: ["{{workspace}}/src/**"]
    write: ["{{workspace}}/reports/**"]

# Bad: Overly broad
permissions:
  filesystem:
    read: ["/**"]
    write: ["/**"]
```

### 5. Configuration Over Code

Make your skill configurable:

```yaml
# config/schema.json
{
  "type": "object",
  "properties": {
    "strictness": {
      "type": "string",
      "enum": ["lenient", "normal", "strict"],
      "default": "normal"
    },
    "max_issues": {
      "type": "integer",
      "default": 50
    }
  }
}
```

### 6. Documentation

Your README should include:

```markdown
# My Skill

## Description
What this skill does and why it's useful.

## Installation
```bash
kurultai install my-skill
```

## Usage
```bash
/claude use my-skill "your input here"
```

## Configuration
Options and how to set them.

## Examples
Specific examples of inputs and outputs.

## Integration
How this skill composes with other skills.
```

---

## Integrating with horde-swarm

To make your skill part of the horde ecosystem:

### 1. Declare Compatibility

```yaml
skill:
  horde:
    compatible: true
    requires: horde-swarm>=1.0.0
```

### 2. Accept Swarm Context

```python
class MySkill:
    def __init__(self, context):
        self.context = context
        # Access the swarm engine
        self.swarm = context.get_engine("horde-swarm")

    def execute(self, task: str):
        # Use swarm for parallel execution
        results = self.swarm.dispatch(
            task=task,
            agents=self.get_specialists()
        )
        return self.synthesize(results)
```

### 3. Implement Synthesis

```python
def synthesize(self, results: List[AgentOutput]) -> UnifiedOutput:
    """Combine multiple agent outputs."""
    # Deduplicate
    unique = self.deduplicate(results)

    # Resolve conflicts
    resolved = self.resolve_conflicts(unique)

    # Build consensus
    consensus = self.build_consensus(resolved)

    return UnifiedOutput(consensus)
```

### 4. Declare Agent Types

```yaml
skill:
  horde:
    agent_types:
      - researcher      # This skill dispatches researchers
      - analyst         # and analysts
```

---

## Example: Complete Skill

Here's a complete example of a code review skill:

### skill.yaml

```yaml
skill:
  id: python-code-reviewer
  version: 1.0.0
  name: Python Code Reviewer
  description: Reviews Python code for bugs, style, and best practices
  author: Your Name
  license: MIT

  categories:
    - code-review
    - python

  horde:
    compatible: true
    requires: horde-swarm>=1.0.0
    swarm_patterns:
      - multi-perspective
    agent_types:
      - code-reviewer

  permissions:
    filesystem:
      read: ["{{workspace}}/**/*.py"]
    tools:
      allowed: [Read, Grep]

  configuration:
    schema: config/schema.json

  entry_points:
    default: prompts/main.md
```

### prompts/main.md

```markdown
# Python Code Reviewer

Review the provided Python code for:
1. Bugs and logic errors
2. Style violations (PEP 8)
3. Performance issues
4. Security vulnerabilities

## Input

```python
{{code}}
```

## Output Format

```yaml
review:
  summary: "Brief overview of findings"
  score: 85  # 0-100
  issues:
    - severity: "error|warning|info"
      category: "bug|style|performance|security"
      line: 42
      message: "Description"
      suggestion: "How to fix"
  recommendations:
    - "General improvement 1"
    - "General improvement 2"
```
```

### config/schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "strictness": {
      "type": "string",
      "enum": ["lenient", "normal", "strict"],
      "default": "normal"
    },
    "check_types": {
      "type": "boolean",
      "default": true
    }
  }
}
```

---

## Next Steps

- Read the [Horde Ecosystem Guide](horde-ecosystem.md) to understand how skills compose
- Check out [example skills](https://github.com/kurultai/skills) for inspiration
- Join the [Discord community](https://discord.gg/kurultai) for help
