---
name: deepthink-loop-reasoning
description: Apply a structured multi-loop reasoning process (surface, explore, challenge, synthesize, converge) to complex decisions before giving a final answer. Triggers on "think deeper", "devil's advocate this", "what am I missing?", and automatically on architecture decisions, security analysis, and tradeoff comparisons.
category: content
---

# DeepThink — Loop-Based Reasoning

## Goal

Replace single-pass answers to non-trivial problems with a repeatable loop structure: surface, explore, challenge, synthesize, converge. The goal is better-grounded answers, not longer ones.

## Inputs

- A non-trivial problem statement or decision: architecture choice, security analysis, tradeoff comparison, strategy decision, multi-step reasoning chain.
- Optional explicit trigger phrase from the user: "think deeper", "deep think", "reason through this", "analyze this thoroughly", "what am I missing?", "devil's advocate this".
- No API keys or external services required. This is a pure reasoning workflow.

## Steps

1. **Decide whether to apply the skill.** Skip for simple factual lookups ("what time is it?", "grep for this string") and single-step tasks. Apply automatically for architecture decisions, security/threat modeling, comparing competing approaches, risk/tradeoff analysis, and multi-step reasoning chains.
2. **Set depth level.** Always start at Standard (3–4 loops). Escalate to Deep (5–6) only if divergence persists. Never start at Maximum (7+) without explicit user direction.
3. **Start every loop by restating the original problem in one sentence.** Format: `[LOOP N] Problem restated: <one sentence>`. This prevents drift.
4. **Loop 1 (Surface):** write a fast initial hypothesis answering the problem. What seems true at first glance?
5. **Loop 2 (Explore):** generate counterevidence, alternative approaches, edge cases, and missing paths not considered in Loop 1.
6. **Loop 3 (Challenge):** question assumptions, identify risks, failure modes, and weak points of the current hypothesis. In devil's-advocate mode, bias hard toward this loop and state the strongest version of the opposing argument before concluding.
7. **Loop 4 (Synthesize):** integrate the strongest points from all loops into a refined conclusion.
8. **Run a convergence check.** Convergence signals: same conclusion reached from different angles, no new contradictions, edge cases accounted for, remaining questions are clarifications not fundamental uncertainties. Divergence signals: new contradictions, key assumptions challenged, uncertainty increased. If converged, stop. If diverged, run another loop.
9. **Weight the evidence.** State: the strongest single piece of evidence for the conclusion; the weakest assumption the conclusion rests on; what would make the conclusion wrong (what would lose the bet).
10. **Format the final output** with these sections: Problem, Depth Applied, Reasoning Journey (one subsection per loop), Conclusion, Key Insights, Remaining Uncertainties (only if divergence unresolved), Recommendations (if the user asked for action).

## Outputs

- A structured DeepThink analysis document (markdown) with per-loop reasoning trace, depth level, conclusion, key insights, evidence weighting, uncertainties, and recommendations.

## Failure Modes

- Agent drifts from the original question if the problem is not restated at the start of every loop.
- Over-looping on simple tasks — the skill must be skipped for simple factual lookups.
- Starting at Maximum depth without user direction instead of Standard 3–4 loops.
- Loops producing longer but not better-grounded answers — each loop must add new evidence, alternatives, or challenges, not restate prior loops.

## Source

Discord thread `1485392832154832906/1519931768612847647` — "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" by Jon Komet, 2026-08-30. Attachment: `deepthink-skill-handoff-clean.md` (DeepThink SKILL.md handoff, generated 6/26/2026).