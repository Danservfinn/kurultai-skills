# Kurultai Skills

> A collection of 64 skills for Claude Code. Multi-agent orchestration, specialized workflows, and domain expertise for complex software engineering tasks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

Copy and paste this into Claude Code:

```
Clone https://github.com/Danservfinn/kurultai-skills into ~/.claude/skills/. Each subdirectory containing a SKILL.md file is a separate skill. Do not overwrite any existing skills. Exclude .git and __pycache__. After copying, list how many skills were installed.
```

Or run in your terminal:

```bash
git clone https://github.com/Danservfinn/kurultai-skills.git ~/.claude/skills
```

Skills are immediately available as slash commands in Claude Code (e.g., `/horde-swarm`, `/brainstorming`, `/senior-backend`).

## Skills (64)

| Category | Skills |
|---|---|
| **Horde Ecosystem** | golden-horde (v2.0), horde-swarm, horde-plan (v1.2), horde-implement (v2.0), horde-test (v1.0), horde-review, horde-brainstorming, horde-learn, horde-gate-testing, horde-skill-creator |
| **Senior Specialists** | senior-architect, senior-backend, senior-frontend, senior-fullstack, senior-devops, senior-data-engineer, senior-data-scientist, senior-ml-engineer, senior-computer-vision, senior-prompt-engineer |
| **Dev Workflow** | brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, code-reviewer, requesting-code-review, receiving-code-review, verification-before-completion, systematic-debugging, implementation-status, ship-it |
| **Specialized** | agent-collaboration, agent-development, command-development, skill-creator, skill-development, changelog-generator, claude-cleanup, file-organizer, video-downloader, webapp-testing, oauth-setup, theme-factory, web-artifacts-builder, frontend-design, writing-rules |
| **Analysis & Content** | accessibility-auditor, critical-reviewer, content-research-writer, seo-optimizer, lead-research-assistant, ui-design-system, ux-researcher-designer, product-strategist |
| **Leadership** | cto-advisor, ceo-advisor, parse-cfo |
| **Project-Specific** | molt, kurultai-model-switcher, last30days, dev-deploy, review, using-superpowers |

---

## The Horde Ecosystem

The horde skills are the core of Kurultai. They compose together into multi-agent workflows where each skill handles a distinct phase of work.

```
                    golden-horde (v2.0)
                    Meta-orchestrator: 9 patterns, 60+ agents,
                    embeds all horde skill methodologies
                              |
                              | delegates to
                              v
                        horde-swarm
                        Parallel dispatch engine
                        (fire-and-forget, 35+ agent types)
                              |
          +-------------------+-------------------+
          |                   |                   |
    horde-brainstorming  horde-plan (v1.2)   horde-learn
    (6-phase design)     (Plan Output         (insight
                          Contract)            extraction)
                              |
                              v
                      horde-implement (v2.0)
                      Two-Layer Conductor
                      (parse or generate plans,
                       phase gating, checkpoint/resume)
                              |
          +-------------------+-------------------+
          |                   |                   |
    horde-gate-testing   horde-test          horde-review
    (phase gates)        (test suites)       (multi-domain
                                              validation)
```

### Quick Reference

| Skill | Version | Purpose | Invoke |
|-------|---------|---------|--------|
| **golden-horde** | v2.0 | Meta-orchestrator with 9 coordination patterns, 60+ agent types, 8 embedded skill methodologies | `/golden-horde <task>` |
| **horde-swarm** | -- | Fire-and-forget parallel dispatch of 35+ specialized agent types | `/horde-swarm <task>` |
| **horde-plan** | v1.2 | Structured plans with Plan Output Contract for zero-friction horde-implement parsing | `/horde-plan <task>` |
| **horde-implement** | v2.0 | Two-Layer Conductor plan executor. Path A: generate + execute. Path B: parse existing plan | `/horde-implement <task>` |
| **horde-test** | v1.0 | Parallel test suite execution (unit, integration, e2e, edge cases) | `/horde-test <task>` |
| **horde-review** | -- | Multi-disciplinary review (backend, security, performance, architecture) | `/horde-review <task>` |
| **horde-brainstorming** | -- | 6-phase collaborative design: intent, exploration, adversarial review, synthesis, design docs, implementation plan | `/horde-brainstorming <task>` |
| **horde-learn** | -- | Extract insights and patterns from text sources (docs, articles, code) | `/horde-learn <task>` |
| **horde-gate-testing** | -- | Integration tests between implementation phases | `/horde-gate-testing <task>` |
| **horde-skill-creator** | -- | 7-phase workflow for creating new skills with validation | `/horde-skill-creator <task>` |

---

### golden-horde (v2.0)

The master orchestration skill. Unlike horde-swarm (fire-and-forget parallel dispatch), golden-horde enables **inter-agent communication** through 9 coordination patterns.

#### 9 Orchestration Patterns

| # | Pattern | Agents | Description |
|---|---------|--------|-------------|
| 1 | **Review Loop** | Producer + Reviewer(s) | Iterative refinement. Producer creates output, reviewers critique with specific feedback, producer revises. Repeats until approved or max 5 rounds. |
| 2 | **Adversarial Debate** | 2 Advocates + Judge | Structured argument between opposing positions. Each side makes the strongest case. Judge rules on contested points. |
| 3 | **Assembly Line** | 3-6 Stage Agents | Pipeline where each stage's output feeds the next. Backward messages allow clarification and correction without halting. |
| 4 | **Swarm Discovery** | 2-4 Scouts + Specialists | Scouts explore unknown problem space, dynamically spawn specialists as sub-problems are discovered. Team grows organically. |
| 5 | **Consensus Deliberation** | 3-5 Experts + Facilitator | Independent blind analysis, then challenge phase, then convergence. Ensures genuine expert integration, not averaging. |
| 6 | **Contract-First Negotiation** | 2+ Negotiators | Agents agree on a shared contract (API, schema, protocol) before independent implementation. Proposal/counter-proposal until convergence. |
| 7 | **Expertise Routing** | Generalist + Specialists | Primary agent works on task, routes sub-problems to specialist agents for consultation. Specialists stay on standby between consultations. |
| 8 | **Watchdog** | Implementers + Watchdog | Watchdog monitors implementers at checkpoints, sends corrections in real-time. Catches constraint violations before they propagate. |
| 9 | **Nested Swarm** | Golden-horde + Sub-swarms | Golden-horde agent spawns horde-swarm sub-agents for parallelizable sub-tasks. Results synthesized before continuing team communication. Max depth: 2. |

#### 60+ Agent Types (3 Tiers)

- **Tier 1 (Implementation):** 35+ specialized agents from horde-swarm (backend, frontend, Python, data/ML, DevOps, security, architecture, etc.)
- **Tier 2 (System):** Plan, Explore, Bash, general-purpose, docs-architect, tutorial-engineer, payment-integration, agent-expert, code-reviewer
- **Tier 3 (Judgment):** cost-analyst, chaos-engineer, compliance-auditor, migration-strategist, api-contract-designer, performance-profiler, tech-debt-assessor, integration-tester, prompt-engineer -- spawned as `general-purpose` with specialized prompts

#### 8 Embedded Skill Methodologies

Since subagents cannot invoke the `Skill()` tool, golden-horde injects each horde skill's workflow as a prompt template. The orchestrator reads the skill's SKILL.md and distills the methodology into the agent's instructions.

Embedded: horde-plan v1.2, horde-implement, horde-test, horde-review, horde-brainstorming, horde-learn, horde-gate-testing, horde-skill-creator

#### Pattern Selection (Decision Matrix)

| Signal in Request | Pattern |
|---|---|
| "review", "iterate", "refine", "validate" | Review Loop |
| "choose between", "debate", "tradeoffs", "compare" | Adversarial Debate |
| "then", "based on", "after", "pipeline" | Assembly Line |
| "audit", "investigate", "explore", "unknown scope" | Swarm Discovery |
| "agree on", "decide", "recommend", "evaluate together" | Consensus Deliberation |
| "agree on API", "contract", "schema first" | Contract-First Negotiation |
| "build + consult specialist", "multi-domain" | Expertise Routing |
| "enforce standards", "catch violations", "monitor" | Watchdog |
| "research deeply then iterate", "parallel + review" | Nested Swarm |
| "plan then build", "full lifecycle" | Assembly Line (horde-plan + horde-implement) |

#### Examples

```
/golden-horde Design a database migration strategy, then have a DBA review it for safety
/golden-horde Debate PostgreSQL vs DynamoDB for our event store, then have a judge decide
/golden-horde Audit this codebase for security vulnerabilities -- discover and remediate as you go
/golden-horde Have backend and frontend agents agree on the API contract before implementing
/golden-horde Plan, implement, test, and review a notification service (full lifecycle)
```

---

### horde-swarm

The parallel dispatch engine. Analyzes a task, selects optimal agent types from its registry of 35+, dispatches them simultaneously, and synthesizes results.

**Key property:** Fire-and-forget. No inter-agent communication. Each agent works independently. The orchestrator synthesizes all outputs into a unified result.

```
/horde-swarm Review this API design from backend, frontend, and security perspectives
/horde-swarm Analyze this codebase for performance bottlenecks
```

---

### horde-plan (v1.2)

Creates structured implementation plans with a **Plan Output Contract** optimized for zero-friction parsing by horde-implement.

**v1.2 features:**
- Strict heading contract: `## Phase {id}: {name}`, `### Task {id}.{n}: {name}`, `### Exit Criteria Phase {id}`
- Task type hints in code blocks for automatic classification (bash/code_write/config/browser/verify/human_required)
- Gate depth signals: DEEP (code-to-deploy), STANDARD (schema-to-consumer), LIGHT (independent), NONE (verify-only)
- YAML frontmatter plan manifest with phase index and task transfer IDs
- Complexity scoring with golden-horde deliberation threshold (score >= 15)
- Structured handoff to horde-implement Path B

```
/horde-plan Create a user authentication system with JWT tokens
/horde-plan Design a real-time notification service with WebSocket support
```

---

### horde-implement (v2.0 -- Two-Layer Conductor)

General-purpose plan executor with two entry paths:

- **Path A (Generate):** Request -> senior-prompt-engineer -> plan -> execute
- **Path B (Execute):** Existing plan.md -> parse phases/tasks/exit criteria -> execute (optimized for horde-plan v1.2 output)

**Key features:**
- Context windowing: plan index (~500 tokens) + phase slices on demand
- Phase gate testing: 4 depths (NONE/LIGHT/STANDARD/DEEP) via horde-gate-testing
- Checkpoint/resume: JSON at `.claude/plan-executor/checkpoints/`
- Post-execution: implementation-status audit -> horde-test -> horde-review

```
/horde-implement Create a user authentication API with JWT tokens
/horde-implement execute docs/plans/kurultai_0.2.md
/horde-implement resume
```

---

### horde-review

Multi-disciplinary critical review using Consensus Deliberation pattern. Dispatches domain-specific reviewers (backend, security, performance, architecture, DevOps, accessibility) who independently analyze the artifact, then converge on findings.

Each finding is classified by severity: CRITICAL / HIGH / MEDIUM / LOW. Anti-sycophancy enforced -- reviewers must find at least 2 issues per domain or justify with evidence why none exist.

```
/horde-review Review the payment processing module
```

---

### horde-test (v1.0)

Comprehensive test suite execution using parallel dispatch. Categories: unit tests, integration tests, e2e tests, edge cases. Results collected and measured against coverage targets (100% pass, >80% line coverage, >70% branch coverage).

```
/horde-test Run full test suite for the authentication module
```

---

### horde-brainstorming

6-phase collaborative design process:

1. **Intent Gathering** -- Analyze context, ask targeted questions, establish problem statement
2. **Parallel Domain Exploration** -- Dispatch domain specialists via horde-swarm
3. **Adversarial Review** -- Security, edge case, and maintenance reviewers challenge proposals
4. **Synthesis** -- Consolidate into 2-3 validated options with trade-offs
5. **Detailed Design Documentation** -- Architecture diagrams, API specs
6. **Implementation Planning** -- Roadmap, dependencies, effort estimates

```
/horde-brainstorming Design a payment processing system
```

---

### horde-learn

Extracts insights from text sources (documentation, articles, codebases). Dispatches researchers per source via horde-swarm, extracts facts and patterns, synthesizes into a unified report with categorized insights (TECHNIQUE, PRINCIPLE, WARNING, OPPORTUNITY).

```
/horde-learn Extract patterns from our existing auth module
```

---

### horde-gate-testing

Integration tests between implementation phases. Verifies completed phase outputs are valid, interfaces between phases are compatible, data contracts are honored, and no regressions from previous phases. Reports PASS (proceed) or FAIL (block with details).

```
/horde-gate-testing Validate phase 2 outputs before starting phase 3
```

---

### horde-skill-creator

7-phase workflow for creating new skills: Research -> Define -> Design -> Implement -> Test -> Review -> Deploy. Produces a complete SKILL.md with YAML frontmatter and markdown body.

```
/horde-skill-creator Create a deployment automation skill
```

---

## Skill Composition

Skills compose through output chaining -- the output of one skill feeds the next:

```
/horde-brainstorming Design a caching layer
  -> produces design spec
/horde-plan Create implementation plan from that design
  -> produces structured plan (Plan Output Contract)
/horde-implement execute the-plan.md
  -> produces implementation
/horde-gate-testing Validate the implementation
  -> PASS/FAIL gate
/horde-review Review the implementation
  -> findings report
```

For full lifecycle orchestration, use golden-horde with Assembly Line pattern -- it handles the composition automatically.

---

## Skill Structure

Each skill is a directory with a `SKILL.md` file:

```
my-skill/
  SKILL.md           # Required. YAML frontmatter + markdown body.
  CLAUDE.md          # Optional. Project-specific context.
  supporting-files/  # Optional. Templates, scripts, reference docs.
```

**SKILL.md format:**

```markdown
---
name: my-skill
version: "1.0"
description: What this skill does and when to use it
integrations:
  - other-skill-it-works-with
---

# Skill Name

Description, workflow, examples, and instructions for Claude Code.
```

Skills are invoked as slash commands: `/my-skill <arguments>`

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/Danservfinn/kurultai-skills.git
cd kurultai-skills
# Create a new skill directory with SKILL.md
# Submit a pull request
```

---

## License

MIT License - see [LICENSE](LICENSE)
