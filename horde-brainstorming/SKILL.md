---
name: supercharged-brainstorming
description: "Use for complex feature design, system architecture, or when exploring multiple technical approaches. Combines collaborative discovery with parallel domain expert analysis to produce validated, implementable designs."
---

# Supercharged Brainstorming

Transform ideas into production-ready designs through collaborative discovery amplified by parallel domain expert analysis.

## When to Use This Skill

Invoke this skill when:
- Designing complex features with multiple technical components
- Exploring architectural decisions with significant trade-offs
- Building systems that span multiple domains (frontend, backend, infrastructure)
- Need validated designs before implementation
- Want to catch failure modes and edge cases early
- Previous simple brainstorming revealed hidden complexity

**vs. Simple Brainstorming:**
- Simple brainstorming: Linear Q&A, single-threaded exploration
- Supercharged brainstorming: Parallel domain analysis, adversarial review, validated options

## The Process

### Phase 1: Intent Gathering (Sequential)

Establish foundational understanding through collaborative dialogue:

1. **Analyze current context**
   - Review existing codebase, architecture, and constraints
   - Check for related designs in `docs/plans/`
   - Understand technical debt and existing patterns

2. **Ask targeted questions** (one at a time)
   - What problem are we solving?
   - Who are the users and what do they need?
   - What are the hard constraints (time, budget, technology)?
   - What does success look like?
   - What are the known unknowns?

3. **Stop when:** Have enough context to route to domain specialists

### Phase 2: Parallel Domain Exploration

Dispatch domain specialists in parallel based on problem characteristics:

**Domain Routing Table (using Skills):**

| Problem Keywords | Skills to Invoke via `Skill()` |
|------------------|-------------------------------|
| "user interface", "dashboard", "component" | `ux-researcher-designer`, `senior-frontend` |
| "API", "endpoint", "database", "backend" | `senior-backend`, `senior-architect` |
| "infrastructure", "deploy", "scale" | `senior-devops`, `senior-architect` |
| "data pipeline", "ETL", "analytics" | `senior-data-engineer`, `senior-data-scientist` |
| "ML", "model", "prediction" | `senior-ml-engineer`, `senior-data-scientist` |
| "authentication", "security", "privacy" | `senior-backend`, `senior-architect` |
| "real-time", "websocket", "queue" | `senior-backend`, `senior-devops` |

**Domain Routing Table (using Task subagent dispatch):**

| Problem Keywords | Subagent Type for `Task()` |
|------------------|---------------------------|
| "user interface", "dashboard", "component" | `frontend-mobile-development:frontend-developer` |
| "API", "endpoint", "database", "backend" | `backend-development:backend-architect` |
| "infrastructure", "deploy", "scale" | `senior-devops` (as skill) or `senior-architect` |
| "data pipeline", "ETL", "analytics" | `senior-data-engineer` (as skill) |
| "ML", "model", "prediction" | `senior-ml-engineer` (as skill) |
| "authentication", "security", "privacy" | `backend-development:backend-architect` |
| "real-time", "websocket", "queue" | `backend-development:backend-architect` |

**Each specialist explores:**
- Technical approaches and trade-offs
- Integration patterns with existing systems
- Scalability and performance considerations
- Risk areas and mitigation strategies

**Dispatch pattern using Skills:**
```
Skill("ux-researcher-designer", "Explore UX approach for [feature] from user research perspective...")
Skill("senior-backend", "Explore backend approach for [feature] considering API design...")
```

**Dispatch pattern using Task subagent:**
```
Task(
  subagent_type: "backend-development:backend-architect",
  prompt: |
    ## Context
    [Problem statement from Phase 1]
    [Relevant constraints]

    ## Your Task
    Explore technical approaches for this feature from your domain perspective:

    1. **Approaches:** Identify 2-3 viable technical approaches
    2. **Trade-offs:** For each, list pros/cons specific to your domain
    3. **Integration:** How would this integrate with existing systems?
    4. **Risks:** What could go wrong? How to mitigate?
    5. **Recommendation:** What's your recommended approach and why?

    ## Output Format
    Return structured findings with specific technology recommendations,
    architecture patterns, and concrete implementation guidance.
)
```

### Phase 3: Adversarial Review

Stress-test the emerging design by dispatching critics:

**Dispatch in parallel:**
- **Security reviewer:** "How could this be attacked? What are the vulnerabilities?"
- **Edge case reviewer:** "Where does this break? What are the failure modes?"
- **Maintenance reviewer:** "What will be hard to change? Where is technical debt introduced?"
- **Cost/performance reviewer:** "What will be expensive to run? Where are the bottlenecks?"

**Each critic returns:**
- Identified risks and failure modes
- Severity assessment (Critical/High/Medium/Low)
- Mitigation strategies

### Phase 4: Synthesis and Options Presentation

Consolidate findings into 2-3 validated design options:

**Structure each option:**
```markdown
## Option [A/B/C]: [Name]

### Overview
[2-3 sentence description]

### Architecture
[High-level diagram or description]

### Key Components
- Component 1: [Description]
- Component 2: [Description]

### Trade-offs
**Pros:**
- [From domain specialists]

**Cons:**
- [From domain specialists]

### Risk Assessment
| Risk | Severity | Mitigation |
|------|----------|------------|
| [Risk] | [Level] | [Strategy] |

### Effort Estimate
- Implementation: [S/M/L]
- Complexity: [Low/Medium/High]
- Maintenance: [Easy/Moderate/Hard]
```

**Present to user:**
- Lead with recommended option and reasoning
- Highlight key trade-offs between options
- Note which option addresses each major risk

### Phase 5: Detailed Design Documentation

Once user selects an option, dispatch parallel documentation tasks:

**Create tasks for:**
1. **Technical writer:** Core design document
2. **Architect:** System diagrams and data flows
3. **API designer:** Interface specifications (if applicable)
4. **DevOps planner:** Infrastructure and deployment guide

**Output:**
- `docs/plans/YYYY-MM-DD-<feature>-design.md`
- Architecture diagrams (Mermaid)
- API specifications
- Deployment considerations

### Phase 6: Implementation Planning (Optional)

If ready to proceed:
- Use `superpowers:writing-plans` to create implementation plan
- Use `superpowers:using-git-worktrees` for isolated workspace
- Or hand off to `superpowers:subagent-driven-development` for execution

## Key Principles

- **Parallel exploration beats sequential questioning** - Domain experts investigate simultaneously
- **Adversarial review catches blind spots** - Critics find what optimists miss
- **Validated options reduce decision fatigue** - Present trade-offs clearly, recommend decisively
- **YAGNI still applies** - Remove unnecessary features from all designs
- **Incremental validation** - Check with user after Phase 1, after Phase 4

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `critical-review` | Phase 3 adversarial review |
| `subagent-driven-development` | Phase 6 implementation |
| `writing-plans` | Phase 6 plan creation |
| `using-git-worktrees` | Phase 6 workspace setup |
| `senior-architect` | Phase 2 domain exploration |
| `senior-backend` | Phase 2 domain exploration |
| `senior-frontend` | Phase 2 domain exploration |
| `senior-devops` | Phase 2 domain exploration |

## Example Workflow

**User:** "I want to add a real-time notification system"

**Phase 1:**
- "Who receives notifications?" → Users
- "What triggers them?" → System events
- "Real-time means <1s or <5s?" → <3s acceptable
- "Scale?" → 10K concurrent users

**Phase 2 (Parallel):**
- Backend architect → WebSockets vs SSE vs polling analysis
- DevOps engineer → Redis, load balancer requirements
- Frontend developer → Connection management, reconnection logic
- Security reviewer → WebSocket authentication patterns

**Phase 3 (Parallel):**
- Scalability critic → Redis single point of failure
- Security critic → Token expiration in persistent connections
- Cost critic → Connection overhead at 10K users

**Phase 4:**
- Option A: WebSockets + Redis (real-time, complex)
- Option B: SSE + PostgreSQL LISTEN (simpler, slightly slower)
- Option C: Polling + caching (simplest, not truly real-time)

**Phase 5:**
- Design document with architecture
- API specification
- Deployment guide

**Phase 6:**
- Implementation plan
- Or direct handoff to subagent-driven-development

## Red Flags

**Never:**
- Skip Phase 1 context gathering (domain experts need context)
- Skip adversarial review (blind spots are expensive)
- Present more than 3 options (decision paralysis)
- Proceed to Phase 5 without user selection
- Let domain specialists work without constraints from Phase 1

**Watch for:**
- Domain specialists suggesting incompatible approaches
- Critics identifying show-stopper risks
- User uncertainty between options (need more clarification)
- Scope creep during documentation phase
