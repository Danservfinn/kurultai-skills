---
name: deepthink-loop-reasoning
description: Run loop-based multi-pass reasoning (Surface, Explore, Challenge, Synthesize, Converge) on complex decisions before giving a final answer. Use on architecture choices, security analysis, tradeoff comparisons, and "what am I missing?" requests. Do not use on simple lookups or single-step tasks.
category: content
---
```

# DeepThink — Loop-Based Reasoning

## Goal

Replace a single-pass answer with a structured multi-loop reasoning trace so the final conclusion is better grounded, not merely longer. The original problem is restated at the start of every loop to prevent drift.

## Inputs

- A non-trivial problem statement or decision (architecture choice, security analysis, tradeoff comparison, strategy decision).
- Optional depth level: Quick (1–2 loops), Standard (3–4), Deep (5–6), Maximum (7+). Default is Standard.

No API keys or external services are required. This skill is pure reasoning over the provided problem statement; any research the agent does uses its normal shell/web access.

## Steps

1. Decide applicability. If the task is a simple factual lookup, a single-step task, or already covered by a more specialized skill, do not use DeepThink — answer directly.
2. Set depth. Start at Standard (3–4 loops). Escalate to Deep (5–6) only if divergence persists after loop 4. Never start at Maximum without explicit user direction.
3. At the start of every loop, restate the original problem in one sentence, formatted as `[LOOP N] Problem restated: <one sentence>`. This is mandatory for every loop, N = 1 onward.
4. Loop 1 (Surface): state the current reasoning state (nothing established yet on first loop), then generate a fast initial hypothesis — what seems true at first glance.
5. Loop 2 (Explore): generate counterevidence, alternatives, edge cases, and missing paths not considered in Loop 1.
6. Loop 3 (Challenge): question assumptions, risks, failure modes, and weak points of the current hypothesis.
7. Loop 4 (Synthesize): integrate the strongest points from all loops into a refined conclusion.
8. Before each new loop, state the current reasoning state: what is established, the current hypothesis, and what is unresolved.
9. Cross-loop integration: for each loop after the first, state whether it confirms, contradicts, or refines loops 1..N-1, and whether signals are converging (same conclusion reinforced) or diverging (conflicting signals).
10. Convergence check after every loop starting at loop 3: stop if the same conclusion is reached from different angles with no new contradictions and edge cases are accounted for; run another loop if new contradictions or challenged assumptions appeared. Convergence signals: same conclusion from different angles, no new contradictions, remaining questions are clarifications not fundamental uncertainties. Divergence signals: new contradictions, key assumptions challenged, uncertainty increased.
11. Format the final output with these exact sections, in order: `# DeepThink Analysis`, `## Problem`, `## Depth Applied` (N loops / depth level), `## Reasoning Journey` (one `### Loop N — <name>` subsection per loop, including the problem restatement and cross-loop integration), `## Conclusion`, `## Key Insights` (bulleted), `## Remaining Uncertainties` (always present; if convergence was clean, state "None — convergence reached at loop N" or list honest gaps), `## Recommendations` (only if the user asked for action).
12. Optionally apply a special pattern when requested or appropriate: Devil's Advocate (bias toward Challenge; state the strongest opposing argument before concluding), First Principles Breakout (a breakout loop questioning assumed constraints: what are we assuming that isn't true? what would this look like solved fresh? what's the simplest solution ignoring non-real constraints?), Evidence Weighting (after loops stabilize, state the strongest single piece of evidence, the weakest assumption, and what would make the conclusion wrong).

## Outputs

- A structured DeepThink analysis document (markdown) with a per-loop reasoning trace including problem restatements and cross-loop integration.
- A refined conclusion with key insights and an honest Remaining Uncertainties section.
- Actionable recommendations when the user asked for action.

## Failure modes

- Agent drifts from the original question if the problem is not restated each loop — mitigated by the mandatory step 3 restatement.
- Overuse on trivial tasks (simple lookups) wasting tokens — mitigated by step 1 applicability check.
- False convergence: stopping early because loops feel stable while key assumptions are unchallenged — apply the Challenge loop and Evidence Weighting pattern before declaring convergence.
- Output becomes longer without being better grounded — every loop must add new evidence, alternatives, or challenges, not restate prior loops.
- If the user supplies insufficient information to reason about the problem, state this in Remaining Uncertainties rather than fabricating premises.

## Source

Discord thread "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" (Jon Komet, 2026-08-26), attachment `deepthink-skill-handoff-clean.md` — Jon Komet's DeepThink skill handoff, dated 6/26/2026.