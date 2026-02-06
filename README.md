# Kurultai

> A skills marketplace for Claude Code. Discover, install, and compose agent workflows for complex multi-agent orchestration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## For Machines

Copy and paste this prompt into Claude Code to install all 65 skills:

```
Clone https://github.com/Danservfinn/kurultai-skills and copy every subdirectory from the skills/ folder into ~/.claude/skills/. Each subdirectory is a separate skill containing a SKILL.md file and optional supporting files. Do not overwrite any existing skills that are already installed. Exclude .git, __pycache__, and .zip files. After copying, list how many skills were installed.
```

Or run this in your terminal:

```bash
git clone https://github.com/Danservfinn/kurultai-skills.git /tmp/kurultai-skills-install && \
rsync -av --ignore-existing --exclude='.git' --exclude='__pycache__' --exclude='*.zip' \
  /tmp/kurultai-skills-install/skills/ ~/.claude/skills/ && \
rm -rf /tmp/kurultai-skills-install && \
echo "Installed. Total skills: $(ls -d ~/.claude/skills/*/ 2>/dev/null | wc -l)"
```

### What's Included (65 skills)

| Category | Skills |
|---|---|
| **Horde Ecosystem** | golden-horde, horde-swarm, horde-plan, horde-implement, horde-test, horde-review, horde-brainstorming, horde-learn, horde-gate-testing, horde-skill-creator |
| **Senior Specialists** | senior-architect, senior-backend, senior-frontend, senior-fullstack, senior-devops, senior-data-engineer, senior-data-scientist, senior-ml-engineer, senior-computer-vision, senior-prompt-engineer |
| **Dev Workflow** | brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, code-reviewer, requesting-code-review, receiving-code-review, verification-before-completion, systematic-debugging, implementation-status, ship-it, generate-tests |
| **Specialized** | agent-collaboration, agent-development, command-development, skill-creator, skill-development, changelog-generator, claude-cleanup, file-organizer, video-downloader, webapp-testing, oauth-setup, theme-factory, web-artifacts-builder, frontend-design |
| **Analysis & Content** | accessibility-auditor, critical-reviewer, content-research-writer, seo-optimizer, lead-research-assistant, ui-design-system, ux-researcher-designer, product-strategist |
| **Leadership** | cto-advisor, ceo-advisor, parse-cfo |
| **Project-Specific** | molt, kurultai-model-switcher, data-ingestion, last30days, dev-deploy, review, using-superpowers, writing-rules |

---

## What is Kurultai?

Kurultai is a **skills marketplace for Claude Code** that enables users to discover, install, and compose custom agent configurations and workflows. It transforms Claude Code from a single assistant into a **multi-agent orchestration platform**.

### Key Capabilities

- **Skill Discovery**: Browse a curated marketplace of pre-built agent skills
- **One-Line Installation**: Install skills directly into Claude Code with a single command
- **Workflow Composition**: Chain multiple skills into complex multi-agent workflows
- **Horde Ecosystem**: Use the `horde-*` family of skills for sophisticated AI workflows
- **Custom Skills**: Create and publish your own agent configurations

---

## The Horde Skills Ecosystem

The "horde" skills are the centerpiece of Kurultai. They work together as an **ecosystem** where users compose complex workflows through skill composition.

### Core Principle: horde-swarm as Engine

**`horde-swarm`** is the foundational engine that powers all other horde skills. It provides the parallel execution layer that enables multi-agent workflows.

```
┌─────────────────────────────────────────────────────────────────┐
│                      HORDE ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐                                            │
│  │  golden-horde    │  ◄── META-ORCHESTRATOR                    │
│  │  (9 patterns,    │      Embeds all skill methodologies        │
│  │   60+ agents)    │      Coordinates inter-agent communication │
│  └────────┬─────────┘                                            │
│           │ delegates to                                         │
│           ▼                                                      │
│  ┌──────────────┐                                                │
│  │ horde-swarm  │  ◄── ENGINE (fire-and-forget parallel)        │
│  │   (Core)     │                                                │
│  └──────┬───────┘                                                │
│         │                                                        │
│    ┌────┼────────────────┬────────────────┐                      │
│    │    │                │                │                      │
│    ▼    ▼                ▼                ▼                      │
│  ┌────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │horde-      │  │horde-plan   │  │horde-learn  │               │
│  │brainstorm  │  │             │  │             │               │
│  └─────┬──────┘  └──────┬──────┘  └─────────────┘               │
│        │                │                                        │
│        │                ▼                                        │
│        │       ┌─────────────────┐                               │
│        │       │ horde-implement │  ◄── TWO-LAYER CONDUCTOR     │
│        │       │  (v2.0: plan    │      Parse or generate plans  │
│        │       │   executor)     │      Phase gating + checkpoint│
│        │       └────────┬────────┘                               │
│        │                │                                        │
│        └────────────────┤                                        │
│                         ▼                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │horde-gate-  │  │ horde-test  │  │horde-review │              │
│  │testing      │  │             │  │             │              │
│  │(phase gates)│  │(test suites)│  │(multi-domain│              │
│  └─────────────┘  └─────────────┘  │ validation) │              │
│                                    └─────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Horde Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [**golden-horde**](#golden-horde) | Master orchestrator - 9 patterns, 60+ agents, all skill methodologies embedded | Tasks requiring inter-agent communication, review loops, debates, consensus |
| [**horde-swarm**](#horde-swarm) | Core execution engine - dispatch parallel subagents | Any multi-perspective task |
| [**horde-brainstorming**](#horde-brainstorming) | 6-phase collaborative design process | Complex feature design, architecture decisions |
| [**horde-plan**](#horde-plan) | Create comprehensive implementation plans | Breaking down large tasks |
| [**horde-implement**](#horde-implement-v20--two-layer-conductor) | Two-Layer Conductor plan executor with dual entry paths | Execute existing plans or generate-then-execute |
| [**horde-test**](#horde-test) | Comprehensive test suite execution | Unit, integration, e2e, edge case testing |
| [**horde-review**](#horde-review) | Multi-disciplinary critical review | Backend, security, performance, architecture review |
| [**horde-learn**](#horde-learn) | Extract insights from text sources | Research, analysis, competitive intelligence |
| [**horde-gate-testing**](#horde-gate-testing) | Integration testing between phases | Validating implementations |
| [**horde-skill-creator**](#horde-skill-creator) | 7-phase skill creation workflow | Building new skills with validation |

### golden-horde (Meta-Orchestrator)

**golden-horde** is the master orchestration skill — a meta-orchestrator that coordinates all other horde skills. Unlike horde-swarm (fire-and-forget parallel dispatch), golden-horde enables **inter-agent communication** through 9 coordination patterns.

#### 9 Orchestration Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Review Loop** | Producer + Reviewer iterate until quality bar met | Code review, document refinement |
| **Adversarial Debate** | Agents argue opposing positions, judge synthesizes | Architecture decisions, risk assessment |
| **Assembly Line** | Sequential handoff between specialists | Multi-step transformations |
| **Swarm Discovery** | Parallel exploration, results merged | Research, codebase analysis |
| **Consensus Deliberation** | Multiple agents vote on proposals | Design decisions, prioritization |
| **Contract-First Negotiation** | Agents agree on interfaces before building | API design, service boundaries |
| **Expertise Routing** | Route to specialist based on task classification | Mixed-domain workflows |
| **Watchdog** | Monitor agent oversees worker agents | Long-running tasks, quality gates |
| **Nested Swarm** | Orchestrator spawns sub-orchestrators | Complex multi-phase projects |

#### 60+ Agent Types (3 Tiers)

- **Tier 1 (Implementation)**: 35+ specialized agents from horde-swarm
- **Tier 2 (System)**: Plan, Explore, Bash, docs, payment, agent-expert, etc.
- **Tier 3 (Judgment)**: cost-analyst, chaos-engineer, compliance-auditor — spawned as `general-purpose` with specialized prompts

#### 8 Embedded Skill Methodologies

golden-horde embeds the methodologies of all horde skills (horde-plan, horde-implement, horde-test, horde-review, horde-brainstorming, horde-learn, horde-gate-testing, horde-skill-creator) as prompt templates, since subagents cannot invoke the Skill() tool directly.

---

### How Skills Compose

Skills compose through **output chaining** - the output of one skill becomes the input to another:

```yaml
# Example: Feature Development Workflow
workflow:
  name: "Build Authentication System"
  steps:
    - skill: horde-brainstorming
      input: "Design a secure authentication system"
      output: design_spec

    - skill: horde-plan
      input: "{{design_spec}}"
      output: implementation_plan

    - skill: horde-implement
      input: "{{implementation_plan}}"
      output: codebase

    - skill: horde-gate-testing
      input: "{{codebase}}"
      output: validated_code
```

---

## Quick Start

### Installation

```bash
# Install the Kurultai CLI
pip install kurultai

# Or install directly in Claude Code
/claude install skill kurultai
```

### Discover Skills

```bash
# Search available skills
kurultai search "security audit"

# Browse by category
kurultai list --category orchestration

# Show skill details
kurultai info horde-swarm
```

### Install a Skill

```bash
# Install the core horde-swarm engine
kurultai install horde-swarm

# Install a specific version
kurultai install horde-swarm@1.2.0

# Install from a GitHub repo
kurultai install github.com/kurultai/skills/horde-swarm
```

### Use a Skill

```bash
# Use horde-swarm for parallel analysis
/claude use horde-swarm "Analyze this codebase for security issues"

# Use horde-brainstorming for design
/claude use horde-brainstorming "Design a real-time notification system"

# Compose skills in a workflow
/claude workflow --file feature-development.yaml
```

---

## How Horde Skills Work

### horde-swarm

**horde-swarm** is the execution engine at the heart of the Kurultai ecosystem. It enables parallel agent dispatch for any task.

#### Core Concept: Parallel Subagent Dispatch

Instead of a single agent working on a task, horde-swarm dispatches multiple specialized agents in parallel, then synthesizes their outputs.

```
User Request
     │
     ▼
┌─────────────┐    ┌─────────────────────────────────────┐
│ Task        │───▶│ horde-swarm analyzes task and       │
│ Analyzer    │    │ determines optimal agent composition  │
└─────────────┘    └─────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ Agent 1  │       │ Agent 2  │       │ Agent N  │
    │ (Backend │       │ (Frontend│       │ (Security│
    │  Expert) │       │  Expert) │       │  Expert) │
    └────┬─────┘       └────┬─────┘       └────┬─────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Synthesizer    │
                   │  (swarm:synth)  │
                   │                 │
                   │  Combines N     │
                   │  perspectives   │
                   │  into unified   │
                   │  output         │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Final Output   │
                   │  to User        │
                   └─────────────────┘
```

#### Usage Patterns

**Pattern 1: Multi-Perspective Analysis**
```bash
/claude use horde-swarm \
  --pattern multi-perspective \
  --agents "backend,frontend,security" \
  "Review this API design"
```

**Pattern 2: Divide and Conquer**
```bash
/claude use horde-swarm \
  --pattern divide-conquer \
  --chunks 5 \
  "Refactor this 10,000 line codebase"
```

**Pattern 3: Expert Review Panel**
```bash
/claude use horde-swarm \
  --pattern expert-panel \
  --agents "architect,security-reviewer,performance-expert" \
  "Review this system design"
```

#### How Other Skills Use horde-swarm

| Skill | How It Uses horde-swarm |
|-------|------------------------|
| horde-brainstorming | Dispatches domain specialists in Phase 2 (Parallel Domain Exploration) |
| horde-plan | Dispatches implementation planners for different components |
| horde-implement | Dispatches phase executor subagents and uses swarm for parallel task execution |
| horde-learn | Dispatches researchers to extract information from multiple sources |
| horde-gate-testing | Dispatches test runners and validators in parallel |

---

### horde-brainstorming

**horde-brainstorming** implements a 6-phase collaborative design process inspired by the [horde-brainstorming skill](https://github.com/kurultai/skills/horde-brainstorming).

#### The 6 Phases

```
┌─────────────────────────────────────────────────────────────────┐
│                  HORDE-BRAINSTORMING PHASES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: Intent Gathering                                       │
│  ├── Analyze current context                                     │
│  ├── Ask targeted questions                                      │
│  └── Establish problem statement                                 │
│                           │                                      │
│                           ▼                                      │
│  Phase 2: Parallel Domain Exploration                            │
│  ├── Dispatch domain specialists (via horde-swarm)               │
│  ├── Each explores from their expertise                          │
│  └── Gather technical approaches                                 │
│                           │                                      │
│                           ▼                                      │
│  Phase 3: Adversarial Review                                     │
│  ├── Security reviewer: "How could this be attacked?"            │
│  ├── Edge case reviewer: "Where does this break?"                │
│  └── Maintenance reviewer: "What will be hard to change?"        │
│                           │                                      │
│                           ▼                                      │
│  Phase 4: Synthesis                                              │
│  ├── Consolidate findings                                        │
│  ├── Present 2-3 validated options                               │
│  └── Highlight trade-offs                                        │
│                           │                                      │
│                           ▼                                      │
│  Phase 5: Detailed Design Documentation                          │
│  ├── Create design documents                                     │
│  ├── Generate architecture diagrams                              │
│  └── Document API specifications                                 │
│                           │                                      │
│                           ▼                                      │
│  Phase 6: Implementation Planning                                │
│  ├── Create implementation roadmap                               │
│  ├── Identify dependencies                                       │
│  └── Estimate effort                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Usage

```bash
# Start a brainstorming session
/claude use horde-brainstorming "Design a payment processing system"

# The skill will:
# 1. Ask clarifying questions
# 2. Dispatch domain specialists in parallel
# 3. Conduct adversarial review
# 4. Present 2-3 design options
# 5. Generate design documentation
# 6. Create implementation plan
```

---

### horde-plan

**horde-plan** creates comprehensive implementation plans from requirements or design documents.

#### How It Works

```
Input: Design Document or Requirements
              │
              ▼
    ┌─────────────────┐
    │  Plan Generator │
    │                 │
    │  1. Decompose   │
    │     into tasks  │
    │                 │
    │  2. Identify    │
    │     dependencies│
    │                 │
    │  3. Estimate    │
    │     effort      │
    │                 │
    │  4. Create      │
    │     timeline    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Output: DAG    │
    │                 │
    │  Task Graph     │
    │  with deps,     │
    │  estimates,     │
    │  assignments    │
    └─────────────────┘
```

#### Output Format

```yaml
plan:
  name: "Implement Authentication System"
  version: "1.0.0"

  tasks:
    - id: "auth-001"
      name: "Design database schema"
      estimated_hours: 4
      assignee: "database-expert"
      dependencies: []

    - id: "auth-002"
      name: "Implement user model"
      estimated_hours: 6
      assignee: "backend-developer"
      dependencies: ["auth-001"]

    - id: "auth-003"
      name: "Create login endpoint"
      estimated_hours: 4
      assignee: "backend-developer"
      dependencies: ["auth-002"]

  critical_path: ["auth-001", "auth-002", "auth-003"]
  total_estimate: "14 hours"
```

---

### horde-implement (v2.0 — Two-Layer Conductor)

**horde-implement** is a general-purpose plan executor with two entry paths: generate plans from scratch, or execute existing structured markdown plans.

#### Architecture: Two-Layer Conductor

```
                    ┌─────────────────┐
                    │   Entry Router  │
                    └────────┬────────┘
                  ┌──────────┴──────────┐
                  │                     │
        ┌─────────▼─────┐     ┌────────▼────────┐
        │  Path A:      │     │  Path B:        │
        │  Generate     │     │  Execute        │
        │  (new request │     │  (existing plan │
        │   → plan)     │     │   → parse)      │
        └───────┬───────┘     └────────┬────────┘
                └──────────┬───────────┘
                           ▼
              ┌─────────────────────────┐
              │   Orchestrator (Light)  │
              │   Holds: plan index     │
              │   (~500 tokens)         │
              └────────────┬────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Phase    │    │ Phase    │    │ Phase    │
    │ Executor │    │ Executor │    │ Executor │
    │ (Task    │    │ (Task    │    │ (Task    │
    │  Agent)  │    │  Agent)  │    │  Agent)  │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Gate     │    │ Gate     │    │ Gate     │
    │ Test     │    │ Test     │    │ Test     │
    │(horde-   │    │(selective│    │(horde-   │
    │gate-test)│    │ depth)   │    │gate-test)│
    └──────────┘    └──────────┘    └──────────┘
```

#### Key Features

- **Dual entry**: Generate from request (Path A) or parse existing plans (Path B)
- **Plan parser**: Extracts phases, tasks, exit criteria from structured markdown
- **Context windowing**: Plan index + phase slices on demand (handles 40k+ token plans)
- **Phase gate testing**: 4 depths (NONE/LIGHT/STANDARD/DEEP) via horde-gate-testing
- **Browser automation**: Orchestrator handles browser tasks inline (subagents can't access MCP)
- **Checkpoint/resume**: JSON at `.claude/plan-executor/checkpoints/`, survives session interrupts
- **Post-execution**: implementation-status audit → horde-test → horde-review

#### Usage

```bash
# Path A: Generate and execute from request
/implement Create a user authentication API with JWT tokens

# Path B: Execute existing plan
/implement execute docs/plans/kurultai_0.2.md

# Resume interrupted execution
/implement resume
```

---

### horde-learn

**horde-learn** extracts insights and actionable learnings from text sources (documentation, articles, codebases).

#### How It Works

```
Input: URLs, files, or text content
              │
              ▼
    ┌─────────────────┐
    │  horde-swarm    │
    │  dispatches     │
    │  researchers    │
    │  per source     │
    └────────┬────────┘
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Source│ │Source│ │Source│ │Source│
│  1   │ │  2   │ │  3   │ │  N   │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   │        │        │        │
   │    ┌───┴────────┴───┐    │
   │    │                │    │
   │    ▼                ▼    │
   │ ┌────────┐      ┌────────┐
   │ │Extract │      │Extract │
   │ │Facts   │      │Patterns│
   │ └────────┘      └────────┘
   │        │        │        │
   └────────┴───┬────┴────────┘
                │
                ▼
       ┌─────────────────┐
       │  Synthesizer    │
       │  creates        │
       │  unified report │
       └─────────────────┘
```

#### Usage

```bash
# Learn from documentation
/claude use horde-learn \
  --sources "https://docs.example.com/api,./local-docs" \
  --output "api-knowledge-base.yaml"

# Learn from competitor analysis
/claude use horde-learn \
  --sources "competitor1.com,competitor2.com" \
  --query "pricing strategies and feature gaps"
```

---

### horde-gate-testing

**horde-gate-testing** runs integration tests between implementation phases to catch issues early.

#### How It Works

```
Input: Codebase or Implementation
              │
              ▼
    ┌─────────────────┐
    │  horde-swarm    │
    │  dispatches     │
    │  test runners   │
    └────────┬────────┘
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Unit  │ │Integr│ │E2E   │ │Security│
│Tests │ │Tests │ │Tests │ │Audit  │
└──┬───┘ └──┬───┘ └──┬───┘ └───┬──┘
   │        │        │         │
   └────────┴───┬────┴─────────┘
                │
                ▼
       ┌─────────────────┐
       │  Test Report    │
       │                 │
       │  - Pass/Fail    │
       │  - Coverage     │
       │  - Issues       │
       │  - Recommendations│
       └─────────────────┘
```

#### Usage

```bash
# Run full test suite
/claude use horde-gate-testing --full

# Run specific test types
/claude use horde-gate-testing --types "unit,integration"

# Gate between phases
/claude use horde-implement --plan plan.yaml && \
  /claude use horde-gate-testing --gate
```

---

## Creating Custom Skills

### Skill Structure

```
my-skill/
├── skill.yaml          # Skill manifest
├── README.md           # Documentation
├── prompts/
│   ├── system.md       # System prompt
│   └── examples.md     # Few-shot examples
├── config/
│   ├── schema.json     # Config schema
│   └── defaults.yaml   # Default values
└── tests/
    └── test_skill.py   # Validation tests
```

### skill.yaml Format

```yaml
skill:
  id: my-skill
  version: 1.0.0
  name: My Custom Skill
  description: Does something useful
  author: your-name
  license: MIT

  # horde integration
  horde:
    compatible: true
    requires: horde-swarm>=1.0.0

  # dependencies on other skills
  dependencies:
    - skill: horde-swarm
      version: ^1.0.0

  # entry points
  entry_points:
    default: prompts/main.md

  # permissions
  permissions:
    filesystem:
      read: ["./**"]
      write: ["./output/**"]
    network: false
    delegation: true
```

### Publishing a Skill

```bash
# Create from template
kurultai create my-skill --template basic

# Test locally
kurultai test my-skill

# Publish to GitHub
kurultai publish my-skill --repo github.com/yourname/my-skill
```

---

## Architecture

### Distribution Model

Kurultai uses a **git-native distribution model**:

1. **Skills are Git repositories** hosted on GitHub
2. **Installation** clones the repo to `~/.kurultai/skills/`
3. **Versions** are git tags or commit hashes
4. **Dependencies** are other git repos
5. **Registry** is a JSON index for discovery

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTION FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   GitHub (kurultai/skills/*)                                    │
│        │                                                         │
│        │  git clone                                             │
│        ▼                                                         │
│   ┌──────────────┐                                              │
│   │ kurultai CLI │  install, update, remove                     │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ~/.kurultai/skills/                                            │
│   ├── horde-swarm/                                               │
│   ├── horde-brainstorming/                                       │
│   └── ...                                                        │
│                                                                  │
│          │                                                       │
│          ▼                                                       │
│   Claude Code loads skills from                                  │
│   ~/.claude/skills/                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### How horde-swarm Powers the Ecosystem

The key insight is that **horde-swarm is not just another skill** - it's the execution substrate:

```python
# Simplified architecture

class HordeSwarmEngine:
    """The execution engine that powers all horde skills."""

    def dispatch(self, task: Task, agents: List[Agent]) -> Results:
        """Dispatch multiple agents in parallel."""
        futures = []
        for agent in agents:
            future = self.executor.submit(agent.execute, task)
            futures.append(future)

        results = [f.result() for f in futures]
        return self.synthesize(results)

    def synthesize(self, results: List[Result]) -> UnifiedResult:
        """Combine multiple agent outputs into unified result."""
        # Use consensus algorithms, voting, or LLM-based synthesis
        return Synthesizer().combine(results)

# Other horde skills use the engine:

class HordeBrainstorming:
    """Uses horde-swarm for Phase 2 (Parallel Domain Exploration)."""

    def phase_2_explore(self, problem: str):
        # Dispatch domain specialists in parallel
        return self.swarm.dispatch(
            task=problem,
            agents=[
                BackendArchitect(),
                FrontendDeveloper(),
                SecurityReviewer(),
                DevOpsEngineer()
            ]
        )

class HordePlan:
    """Uses horde-swarm to generate plans from multiple perspectives."""

    def create_plan(self, design: str):
        # Dispatch planners for different aspects
        return self.swarm.dispatch(
            task=design,
            agents=[
                TaskDecomposer(),
                DependencyAnalyzer(),
                EffortEstimator()
            ]
        )
```

---

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [User Guide](docs/user-guide.md)
- [Creating Skills](docs/creating-skills.md)
- [Horde Ecosystem](docs/horde-ecosystem.md)
- [API Reference](docs/api-reference.md)
- [Architecture](docs/architecture.md)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

```bash
# Clone the repository
git clone https://github.com/kurultai/kurultai.git
cd kurultai

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Create a new skill from template
kurultai create my-skill --template basic
```

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Acknowledgments

Kurultai is inspired by:
- The OpenClaw multi-agent system
- The Claude Code ecosystem
- The npm and PyPI package managers
- The Kubernetes operator pattern

The name "Kurultai" refers to a Mongolian tribal council where leaders would gather to make decisions - reflecting the collaborative, multi-agent nature of the platform.
