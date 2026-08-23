# Tests — deepthink-loop-reasoning

Manual checklist. Each item has a concrete command or input and a pass/fail criterion observable in the output text. All checks run against the skill files and a sample LLM invocation; no agent-specific CLI is assumed.

## 1. Skill files installed completely

```bash
ls <skills-dir>/deepthink-loop-reasoning/
```

**Pass:** output contains exactly `SKILL.md`, `examples.md`, `commands.md`, `tests.md`. **Fail:** any file missing.

## 2. Frontmatter matches slug

```bash
head -5 <skills-dir>/deepthink-loop-reasoning/SKILL.md | grep "name: deepthink-loop-reasoning"
```

**Pass:** prints the line. **Fail:** no output (name mismatch with directory).

## 3. Output structure on a non-trivial prompt

Give the agent this prompt with the skill active:

> Use deepthink to reason through whether we should choose Postgres or DynamoDB for a social-feed app expected to reach 10M users.

**Pass:** the response contains all of the literal section headings `Problem`, `Depth Applied`, `Reasoning Journey`, `Conclusion`, `Key Insights`, `Remaining Uncertainties`, `Recommendations`, and at least 3 loop subsections. **Fail:** any heading missing or fewer than 3 loops.

## 4. Problem restated in every loop

Using the response from test 3, count occurrences of the core problem restated at the start of each loop subsection (e.g., grep the response text for a distinctive phrase from the original question).

**Pass:** the restatement appears once per loop subsection (≥3 times). **Fail:** any loop subsection lacks a restatement.

## 5. Evidence weighting present

Using the response from test 3, check the Conclusion section (or immediately after it) for three statements: strongest single piece of evidence, weakest assumption, and what would make the conclusion wrong.

**Pass:** all three are stated. **Fail:** any of the three missing.

## 6. Depth discipline

Give the agent this prompt:

> Use deepthink at maximum depth: should we rewrite our billing system in Rust?

**Pass:** response reports 7+ loops / maximum depth. Then give the same prompt without "at maximum depth": **Pass** only if that second response reports 3-4 loops / standard. **Fail:** maximum depth used without explicit request.