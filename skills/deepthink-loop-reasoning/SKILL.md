---
name: deepthink-loop-reasoning
description: Run a multi-loop structured reasoning process (surface, explore, challenge, synthesize, converge) on complex decisions before giving a final answer. Triggers on "think deeper", "reason through this", "what am I missing?", "devil's advocate this", and automatically on architecture decisions, security analysis, tradeoff comparisons, and multi-step reasoning chains.
category: content
---

# DeepThink — Loop-Based Reasoning

## Goal

Replace single-pass answers with a repeatable loop structure (Surface → Explore → Challenge → Synthesize → Converge) so the final answer is better grounded. The original problem is restated at the start of every loop to prevent drift.

## Inputs

- A problem statement or decision question (required)
- Optional depth level: quick (1–2 loops), standard (3–4), deep (5–6), maximum (7+). Default to standard. Never start at maximum without explicit user direction.

## Steps

1. Restate the original problem in one sentence at the start of every loop: `[LOOP N] Problem restated: <one sentence>`. This is mandatory for every loop.
2. Loop 1 (Surface): state where reasoning stands (nothing yet), then generate a fast initial hypothesis — what seems true at first glance.
3. Loop 2 (Explore): generate counterevidence, alternatives, edge cases, and missing paths not considered in Loop 1.
4. Loop 3 (Challenge): question assumptions, risks, failure modes, and weak points of the current hypothesis.
5. Loop 4 (Synthesize): integrate the strongest points from all loops into a refined conclusion.
6. After each loop, run a convergence check. Converged = same conclusion reached from different angles, no new contradictions, edge cases accounted for, remaining questions are clarifications not fundamentals. Diverged = new contradictions, challenged assumptions, uncertainty increased. If converged, stop; otherwise continue to the next loop.
7. Optionally apply special patterns: devil's advocate mode (bias toward Challenge, state the strongest opposing argument before concluding), first-principles breakout (question what is assumed; what would this look like if never solved before; simplest solution ignoring fake constraints), evidence weighting (state the strongest evidence, the weakest assumption, and what would make the conclusion lose a bet).
8. Format the final output with sections: Problem, Depth Applied, Reasoning Journey (one subsection per loop), Conclusion, Key Insights, Remaining Uncertainties, Recommendations.

## Outputs

- A structured DeepThink analysis document (markdown) with conclusion, key insights, uncertainties, and recommendations.

## Failure modes

- Agent drifts from the original question if the problem is not restated each loop — enforce Step 1 strictly.
- Over-looping on simple tasks that need only 1–2 loops — run the convergence check honestly after every loop.
- Starting at maximum depth without user direction, wasting tokens — default to standard.
- Convergence declared prematurely while contradictions remain — check for unresolved contradictions explicitly before stopping.

## Source

Jon Komet, DeepThink skill handoff (discord / 1485392832154832906 / 1519931768612847647, 2026-08-30). Install target: `~/.hermes/skills/deepthink/SKILL.md`.