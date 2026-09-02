---
name: deepthink-loop-reasoning
description: Run structured multi-loop reasoning (surface, explore, challenge, synthesize, converge) on complex decisions before giving a final answer. Triggers on "think deeper", "what am I missing?", "devil's advocate this", or automatically on architecture decisions, security analysis, and tradeoff comparisons. Skip for factual lookups and single-step tasks.
category: content
---

# DeepThink — Loop-Based Reasoning

## Goal

Produce a better-grounded answer to a non-trivial problem by running 3-4 structured reasoning loops instead of trusting the first plausible answer. Output a DeepThink Analysis document.

## Inputs

- A non-trivial problem statement (architecture decision, security analysis, tradeoff comparison).
- Optional explicit trigger: "think deeper", "deep think", "reason through this", "what am I missing?", "devil's advocate this".

No API keys or external services are required. This skill is pure reasoning over the provided problem statement; any web/shell evidence gathering is optional supplement.

## Steps

1. **Gate: decide whether to run.** Use this skill for architecture decisions, security/threat analysis, risk and tradeoff analysis, comparing competing approaches, strategy decisions, or multi-step reasoning chains. Do NOT use it for simple factual lookups ("what time is it?", "grep for this string") or single-step tasks.
2. **Set depth to Standard (3-4 loops).** Never start at Maximum without explicit user direction. Escalate to Deep (5-6 loops) only if divergence persists after loop 4.
3. **For each loop, restate the original problem first**, in one sentence, in the exact form: `[LOOP N] Problem restated: <one sentence>`. This prevents drift. Never skip this.
4. **Loop 1 (Surface):** state where reasoning stands (nothing yet), then write the fast initial hypothesis — what seems true at first glance.
5. **Loop 2 (Explore):** state current state after loop 1, then generate counterevidence, alternative approaches, edge cases, and missing paths not yet considered.
6. **Loop 3 (Challenge):** state current state after loop 2, then question assumptions, identify risks, failure modes, and weak points of the current hypothesis.
7. **Loop 4 (Synthesize):** state current state after loop 3, then integrate the strongest points from all loops into a refined conclusion.
8. **After each loop, run a convergence check.** Convergence signals: same conclusion reached from different angles; no new contradictions; edge cases accounted for; remaining questions are clarifications, not fundamental uncertainties. Divergence signals: new contradictions, challenged key assumptions, uncertainty increased. If converged, stop early; if divergent after loop 4, continue to loop 5-6 (Deep).
9. **In every loop, cross-integrate:** explicitly state whether this loop confirms, contradicts, or refines loops 1..N-1, and what would change if the new evidence were not true.
10. **Format the final output** with these sections exactly: `# DeepThink Analysis`, `## Problem`, `## Depth Applied` (N loops / depth level), `## Reasoning Journey` (one subsection per loop, titled `### Loop N -- Surface/Explore/Challenge/Synthesize/Converge`), `## Conclusion`, `## Key Insights` (bulleted), `## Remaining Uncertainties` (only if divergence not resolved), `## Recommendations` (if the user asked for action).
11. **Optionally apply special patterns when appropriate:**
    - **Devil's Advocate Mode:** when asked to challenge an idea, bias hard toward Loop 3 patterns; state the strongest version of the opposing argument before concluding.
    - **First Principles Breakout:** when stuck in local maxima, add a breakout loop asking: what are we assuming that isn't true? What would this look like with no prior solution? What's the simplest solution ignoring all but real constraints?
    - **Evidence Weighting:** after loops stabilize, state the strongest single piece of evidence for the conclusion, the weakest assumption it rests on, and what would make the conclusion wrong if you had to bet on it.

## Outputs

- A DeepThink Analysis document (markdown) with: Problem, Depth Applied, Reasoning Journey (per loop, each starting with the restated problem), Conclusion, Key Insights, Remaining Uncertainties, Recommendations.

## Failure Modes

- **Reasoning drift**: the original problem is not restated at the start of every loop. Mitigation: step 3 is mandatory.
- **Over-looping on simple tasks**: applying this to factual lookups or single-step tasks adds latency with no benefit. Mitigation: step 1 gate.
- **Length without convergence**: loops that restate prior content instead of adding new evidence. Mitigation: the convergence check (step 8) must cite a concrete signal, not just "looks done".

## Source

- Discord thread "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" (2026-09-02), attachment `deepthink-skill-handoff-clean.md` by Jon Komet. Install target on Hermes: `~/.hermes/skills/deepthink/SKILL.md`.