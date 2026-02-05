# Getting Started with Kurultai

Welcome to Kurultai! This guide will help you get up and running with the skills marketplace for Claude Code.

## What You'll Learn

- How to install Kurultai
- How to discover and install skills
- How to use skills in Claude Code
- How to compose skills into workflows

## Prerequisites

Before you begin, you'll need:

1. **Git** - For cloning skills
2. **Python 3.10+** - For the Kurultai CLI
3. **Claude Code** - The AI assistant that runs the skills

## Installation

### Step 1: Install Kurultai

Run the installation script:

```bash
curl -fsSL https://raw.githubusercontent.com/kurultai/kurultai/main/install.sh | bash
```

Or install manually:

```bash
# Clone the repository
git clone https://github.com/kurultai/kurultai.git
cd kurultai

# Run the installer
./install.sh
```

### Step 2: Reload Your Shell

After installation, reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc
```

### Step 3: Verify Installation

Check that Kurultai is installed correctly:

```bash
kurultai --version
```

You should see output like:
```
kurultai version 0.1.0
```

## Your First Skill

### Discover Available Skills

Browse the available skills:

```bash
# List all skills
kurultai list

# Search for specific skills
kurultai search "security"

# Show details about a skill
kurultai info horde-swarm
```

### Install a Skill

Install the core `horde-swarm` engine:

```bash
kurultai install horde-swarm
```

This will:
1. Clone the skill repository
2. Install dependencies
3. Register the skill with Claude Code

### Use the Skill

Now you can use the skill in Claude Code:

```bash
# Start Claude Code
claude

# In Claude Code, use the skill
/claude use horde-swarm "Analyze this codebase for security issues"
```

## Understanding the Horde Ecosystem

The horde skills work together as an ecosystem. Here's how they relate:

```
horde-swarm (core engine)
    │
    ├── horde-brainstorming - Multi-phase design process
    ├── horde-plan - Create implementation plans
    ├── horde-implement - Execute plans
    ├── horde-learn - Extract insights from sources
    └── horde-gate-testing - Validate implementations
```

### Installing the Full Ecosystem

Install all core horde skills:

```bash
kurultai install horde-brainstorming
kurultai install horde-plan
kurultai install horde-implement
kurultai install horde-learn
kurultai install horde-gate-testing
```

Or install them all at once:

```bash
kurultai install horde-swarm horde-brainstorming horde-plan horde-implement horde-learn horde-gate-testing
```

## Basic Usage Patterns

### Pattern 1: Single Skill

Use a single skill for a specific task:

```bash
/claude use horde-learn "https://docs.example.com/api"
```

### Pattern 2: Sequential Skills

Chain skills together:

```bash
# First, brainstorm a design
/claude use horde-brainstorming "Design a notification system"

# Then create a plan
/claude use horde-plan "Implement the notification system design"

# Finally, implement it
/claude use horde-implement "Build according to the plan"
```

### Pattern 3: Parallel Analysis

Use horde-swarm for multi-perspective analysis:

```bash
/claude use horde-swarm \
  --pattern multi-perspective \
  --agents "security,performance,architecture" \
  "Review this system design"
```

## Creating a Workflow

Workflows let you define multi-step processes:

### Step 1: Create a Workflow File

Create `my-workflow.yaml`:

```yaml
workflow:
  name: "Feature Development"
  description: "Complete workflow from design to implementation"

  steps:
    - name: "Design"
      skill: horde-brainstorming
      input: "{{prompt}}"

    - name: "Plan"
      skill: horde-plan
      input: "Create implementation plan from the design"

    - name: "Implement"
      skill: horde-implement
      input: "Implement according to the plan"

    - name: "Test"
      skill: horde-gate-testing
      input: "Validate the implementation"
```

### Step 2: Run the Workflow

```bash
kurultai workflow run my-workflow.yaml --var prompt="Build a user authentication system"
```

## Managing Skills

### List Installed Skills

```bash
kurultai list --installed
```

### Update Skills

```bash
# Update a specific skill
kurultai update horde-swarm

# Update all skills
kurultai update --all
```

### Remove Skills

```bash
kurultai remove horde-swarm
```

### Configure Skills

```bash
# View skill configuration
kurultai config horde-swarm

# Edit configuration
kurultai config horde-swarm --edit
```

## Next Steps

Now that you have the basics, you can:

1. **Explore More Skills** - Browse the marketplace for skills that fit your needs
2. **Create Your Own Skills** - Follow the [skill creation guide](creating-skills.md)
3. **Learn About the Horde Ecosystem** - Read the [detailed documentation](horde-ecosystem.md)
4. **Join the Community** - Get help and share your skills on [Discord](https://discord.gg/kurultai)

## Common Issues

### Issue: "kurultai: command not found"

**Solution**: Make sure `~/.kurultai` is in your PATH:

```bash
export PATH="$HOME/.kurultai:$PATH"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Issue: "Skill not found"

**Solution**: Check that the skill is installed:

```bash
kurultai list --installed
```

If not, install it:

```bash
kurultai install skill-name
```

### Issue: "Permission denied"

**Solution**: Skills declare required permissions. Review them with:

```bash
kurultai info skill-name
```

If you trust the skill, you can grant permissions during installation:

```bash
kurultai install skill-name --grant-permissions
```

## Getting Help

- **Documentation**: https://github.com/kurultai/kurultai/tree/main/docs
- **Issues**: https://github.com/kurultai/kurultai/issues
- **Discord**: https://discord.gg/kurultai

Happy skill building!
