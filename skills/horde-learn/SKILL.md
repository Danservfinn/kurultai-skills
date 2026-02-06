---
name: horde-learn
description: Extract insights and actionable learnings from text sources (X posts, moltbook entries, websites, documents, articles) and apply them to the current project context. Use when the user asks to "learn from this", "extract insights from", "what can we learn from", "analyze this content", "apply this to our project", or provides content for analysis and application.
integrations:
  - horde-swarm
---

# Horde Learn

## Overview

Enable continuous learning and knowledge application by analyzing text from diverse sources, extracting relevant insights, and translating them into actionable recommendations for the current project context.

## When to Use

Invoke this skill when:
- User provides text content and asks to learn from it or extract insights
- User shares an article, post, or document asking "what should we take from this?"
- User wants to apply external knowledge to current project challenges
- User asks to analyze content for best practices, patterns, or principles
- User provides moltbook entries, X posts, or web content for contextual learning

## Content Type Handling

### Short-Form Content (Social Media, X Posts)

**Characteristics:** < 280 characters, dense, often opinionated or linked

**Analysis Approach:**
1. Extract core claim or insight
2. Identify context (who, what domain, why it matters)
3. Evaluate relevance to current project
4. If links present, note for follow-up but don't fetch automatically

**Example Patterns:**
- "Best practice: X" → Extract as principle
- "Avoid Y" → Extract as anti-pattern
- "Just learned Z" → Extract as discovery
- Hot takes → Evaluate credibility before applying

### Long-Form Content (Articles, Documentation, Moltbook Entries)

**Characteristics:** Structured, multi-paragraph, contains examples

**Analysis Approach:**
1. Skim for structure (headings, lists, code blocks)
2. Extract key concepts (nouns, technologies, patterns)
3. Identify principles and best practices
4. Note code examples or configurations
5. Extract quotes worth preserving
6. Map insights to project areas

**Output Structure:**
```markdown
## Key Insights
- Insight 1
- Insight 2

## Applicable Principles
1. **Principle Name**: Description
   - Relevance: Why it matters for this project

## Action Items
- [ ] Specific action based on insight
- [ ] Another action
```

### Structured Content (Moltbook, Documentation)

**Characteristics:** Has metadata, categories, explicit knowledge encoding

**Analysis Approach:**
1. Respect existing structure
2. Cross-reference with existing project knowledge
3. Identify gaps between current state and described state
4. Generate migration or adoption plan

### Unstructured Content (Raw Text, Notes)

**Characteristics:** Free-form, may contain fragments, incomplete thoughts

**Analysis Approach:**
1. Identify themes and patterns
2. Cluster related concepts
3. Fill in implied context
4. Ask clarifying questions if critical information missing

## Learning Workflow

### Step 1: Content Ingestion

Receive text from any source. Do NOT make assumptions about:
- Source credibility (evaluate, don't assume)
- Completeness (check if more context needed)
- Urgency (prioritize based on relevance, not novelty)

### Step 2: Insight Extraction

Extract insights by asking:
1. **What** is being said? (Core claims, facts, opinions)
2. **Why** does it matter? (Context, motivation, impact)
3. **How** does it apply? (Direct application, inspiration, warning)

Classify each insight as one primary type:
- **Principle**: Fundamental truth or guideline (e.g., "Never trust user input")
- **Pattern**: Reusable solution approach (e.g., "Repository pattern for data access")
- **Anti-pattern**: Common mistake to avoid (e.g., "God classes")
- **Tool**: Specific technology recommendation (e.g., "Use Redis for caching")
- **Process**: Workflow or methodology (e.g., "Code review before merge")

**Multi-category handling:** An insight can be tagged with secondary types if relevant. For example: "Microservices pattern" can be primary: Pattern, secondary: Architecture.

**Always capture metadata separately:**
- Source URL/document
- Author (if known)
- Date encountered
- Project context

### Step 3: Relevance Filtering

For each extracted insight, evaluate:

**Relevance Criteria:**
- Does it address a current project challenge?
- Does it improve an existing approach?
- Does it prevent a known risk?
- Does it enable a new capability?

**Scoring:**
- **High**: Directly applicable to active work
- **Medium**: Relevant but not urgent
- **Low**: Interesting but not immediately useful
- **None**: Store for potential future reference

Only present High and Medium relevance insights by default. Low and None can be mentioned in summary but not elaborated.

### Step 4: Application Generation

For relevant insights, generate specific actions:

**Action Types:**
1. **Immediate**: Can be done now, quick win
2. **Planned**: Should be scheduled (add to tasks, plans)
3. **Consider**: Worth exploring but not committed
4. **Research**: Needs more information

**Action Format:**
```markdown
### [Action Type]: [Brief Title]

**Insight:** What triggered this action
**Impact:** Expected benefit
**Effort:** Low/Medium/High
**Proposed:**
- Step 1
- Step 2

**Questions:**
- Any clarifications needed before proceeding
```

### Step 5: Synthesis Output

Present findings in this order:

1. **Executive Summary** (3-5 bullet points)
   - Most important insights
   - Top recommended actions

2. **Detailed Insights** (grouped by theme)
   - Each insight with relevance score
   - Source context

3. **Action Plan** (prioritized)
   - Immediate actions (do now)
   - Planned actions (schedule)
   - Consider items (optional)

4. **Related Knowledge** (if available)
   - Links to existing project knowledge
   - Related areas to explore

5. **Questions for User** (if any)
   - Clarifications needed
   - Preferences for how to proceed

## Integration with Memory

When using this skill with the Molt memory system:

1. **Before learning:** Search existing memory for related topics
2. **During learning:** Note connections to existing knowledge
3. **After learning:** Offer to store insights in memory system

**Storage Categories:**
- `principle`: Fundamental truths and best practices
- `pattern`: Reusable solutions
- `antipattern`: Things to avoid
- `discovery`: New findings worth remembering
- `source`: Where the knowledge came from

## Example Usage

### Input (X Post):
```
"Hot take: most microservices architectures fail because teams
skip the proper bounded context design phase. DDD is not optional."
```

### Output:
```markdown
## Executive Summary
- Key insight: Bounded context design is critical for microservices success
- Recommendation: Review current service boundaries using DDD

## Key Insights
**Pattern:** Domain-Driven Design (DDD) Prerequisite
- **Source:** X post (hot take)
- **Insight:** Skipping bounded context design leads to microservices failure
- **Relevance:** High - applies to our current service architecture

## Action Plan
### Immediate: Review Service Boundaries
- **Insight:** Current microservices may lack proper bounded contexts
- **Effort:** Medium
- **Proposed:**
  1. Map current service boundaries
  2. Evaluate against DDD principles
  3. Identify mismatched domains

### Consider: DDD Workshop
- **Insight:** Team may need DDD training
- **Effort:** High
- **Proposed:** Schedule if gaps identified in review

## Questions
- Has the team done formal DDD boundary design?
- Are there pain points in current service communication?
```

## Tips for Effective Learning

1. **Be skeptical but open**: Evaluate credibility, don't dismiss entirely
2. **Context matters**: A principle valid in one context may not apply elsewhere
3. **Connect dots**: Link new insights to existing knowledge
4. **Prioritize action**: Learning without application is just entertainment
5. **Stay focused**: Don't try to apply everything at once

## Handling Long Content

When content exceeds readable chunks (~3000 words or complex structure):

### Chunking Strategy

1. **Identify natural breakpoints:**
   - Section headers
   - Code block boundaries
   - Paragraph breaks between topics

2. **Process chunks sequentially:**
   ```
   Chunk 1 → Extract insights → Store intermediate
   Chunk 2 → Extract insights → Merge with previous
   Chunk 3 → Extract insights → Final synthesis
   ```

3. **Maintain context between chunks:**
   - Pass accumulated insights to next chunk processing
   - Note cross-chunk references
   - Flag insights that need full-context evaluation

4. **Deduplicate across chunks:**
   - Same principle mentioned in multiple chunks = single insight
   - Merge similar findings with "Appears in sections: X, Y, Z"

### Size Guidelines

| Content Size | Approach |
|--------------|----------|
| < 1000 words | Single-pass analysis |
| 1000-3000 words | Single-pass with section tracking |
| 3000-10000 words | Chunk by major sections |
| > 10000 words | Chunk + iterative refinement |

## Error Handling

### Content Parsing Failures

**Unreadable/malformed content:**
1. Attempt to extract any readable text
2. If < 50% readable: Inform user, request better source
3. If partially readable: Process what can be extracted, note limitations

**Encoding issues:**
1. Try UTF-8 decoding first
2. Fall back to common encodings (latin-1, cp1252)
3. If all fail: Request user provide text in plain format

### Empty or Low-Value Content

**No insights extracted:**
```markdown
## Analysis Results

**Content processed:** [source]
**Finding:** No actionable insights identified for current project context.

**Reasons:**
- Content is introductory/tutorial material
- Focus area doesn't overlap with active work
- Recommendations are too generic

**Suggested action:** Archive for future reference or skip.
```

### Relevance Assessment Failure

**Unable to determine relevance:**
1. Ask user clarifying questions:
   - "What area of the project should I focus on?"
   - "Is [topic X] relevant to current work?"
2. Default to "Medium" relevance if no context available
3. Present insights with disclaimer: "Relevance uncertain - please review"

### Contradictory Insights

When the same source contains conflicting advice:

1. **Extract both perspectives:**
   - "Approach A: [description] - Context: [when applicable]"
   - "Approach B: [description] - Context: [when applicable]"

2. **Note the contradiction:**
   - "Conflict: Source recommends both X and not-X in different sections"

3. **Provide decision framework:**
   ```markdown
   ## Contradictory Guidance Detected

   **Option A:** [First approach]
   - Best when: [conditions]

   **Option B:** [Second approach]
   - Best when: [conditions]

   **Recommendation:** Choose based on [specific project factor]
   ```

## Limitations

- Cannot verify factual accuracy of source content
- Source credibility evaluation is heuristic, not definitive
- Relevance scoring depends on available project context
- May miss implicit insights that require deep domain knowledge
- Long content may lose nuanced connections between distant sections

## Integration with horde-swarm

Use `horde-swarm` when learning from multiple sources simultaneously:

```python
# Example: Learn from 3 different architecture articles in parallel
Task(subagent_type="backend-development:backend-architect",
     prompt="Extract architectural principles from: [article 1]")

Task(subagent_type="backend-development:backend-architect",
     prompt="Extract architectural principles from: [article 2]")

Task(subagent_type="backend-development:backend-architect",
     prompt="Extract architectural principles from: [article 3]")

# Synthesize: Compare principles across sources, identify consensus vs debate
```
