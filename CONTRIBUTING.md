# Contributing to Kurultai

Thank you for your interest in contributing to Kurultai! This document provides guidelines for contributing to the skills marketplace.

## Ways to Contribute

1. **Create Skills** - Build and publish new skills
2. **Improve Documentation** - Help make docs clearer and more complete
3. **Report Bugs** - Submit issues for bugs you find
4. **Suggest Features** - Propose new features or improvements
5. **Review Skills** - Help review community-submitted skills

## Creating Skills

### Before You Start

- Check if a similar skill already exists
- Consider if your skill should be part of an existing skill instead
- Review the [skill creation guide](docs/creating-skills.md)

### Skill Guidelines

1. **Single Responsibility** - Each skill should do one thing well
2. **Clear Documentation** - Include README with usage examples
3. **Test Coverage** - Write tests for your skill
4. **Security First** - Request minimal permissions
5. **Semantic Versioning** - Use semver for versions

### Submission Process

1. Create your skill following the [creation guide](docs/creating-skills.md)
2. Test thoroughly with `kurultai test`
3. Publish to your own GitHub repo
4. Submit to the registry via PR to `kurultai/registry`

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

## Development Setup

```bash
# Clone the repository
git clone https://github.com/kurultai/kurultai.git
cd kurultai

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

## Commit Guidelines

We use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example: `feat: add support for custom agent types`

## Questions?

Join our [Discord community](https://discord.gg/kurultai) or open an issue.

Thank you for contributing!
