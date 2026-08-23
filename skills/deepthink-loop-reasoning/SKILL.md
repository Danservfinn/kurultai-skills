---
name: deepthink-loop-reasoning
description: Run a multi-loop structured reasoning process (surface, explore, challenge, synthesize, converge) on complex decisions before giving a final answer. Use when the user says "think deeper", "reason through this", "devil's advocate this", or when a task involves architecture decisions, security analysis, tradeoffs, or comparing approaches. Do not use for simple lookups or single-step tasks.
category: content
---

# DeepThink Loop-Based Reasoning

## Goal

Replace a single-pass answer with a repeatable loop-based reasoning process on non-trivial problems, producing a structured analysis document with a per-loop reasoning trace and an evidence-weighted conclusion.

## Inputs

- A non-trivial problem statement or decision question (required).
- Optional depth level: `quick` (1-2 loops), `standard` (3-4), `deep` (5-6), `maximum` (7+). Default is `standard`. Never use `maximum` unless the user explicitly requests it.

No API keys or external services are required. This skill is pure reasoning over the provided input.

## Steps

1. **Gate on complexity.** If the task is a simple factual lookup, a single-step task, or already covered by a more specific skill, do not use this skill — answer directly.
2. **Select depth.** Start at `standard` (3-4 loops). Escalate to `deep` (5-6) only if divergence persists after loop 4. Never start at `maximum` without explicit user direction.
3. **Run Loop 1 (Surface).** Begin by restating the original problem in one sentence in the form `[LOOP 1] Problem restated: <sentence>`. Then write a fast initial hypothesis of what seems true at first glance.
4. **Run Loop 2 (Explore).** Restate the problem again first. Generate counterevidence, alternatives, edge cases, and missing paths not yet considered.
5. **Run Loop 3 (Challenge).** Restate the problem again first. Question assumptions, risks, failure modes, and weak points of the current hypothesis. For devil's-advocate requests, state the strongest version of the opposing argument before concluding.
6. **Run Loop 4 (Synthesize).** Restate the problem again first. Integrate the strongest points from all loops into a refined conclusion, explicitly noting for each prior loop whether it confirms, contradicts, or refines the current view.
7. **Convergence check.** Stop if the same conclusion is reached from different angles with no new contradictions and remaining questions are clarifications rather than fundamental uncertainties. If new contradictions or challenged assumptions appeared, run another loop (up to the depth limit) and re-check.
8. **Apply evidence weighting.** After convergence, state: the strongest single piece of evidence for the conclusion, the weakest assumption the conclusion rests on, and what would make the conclusion wrong.
9. **Format the final output** with these sections: `Problem`, `Depth Applied`, `Reasoning Journey` (one subsection per loop, each opening with the problem restatement), `Conclusion`, `Key Insights`, `Remaining Uncertainties`, `Recommendations`, and the evidence-weighting statements from step 8.

## Outputs

- A structured DeepThink analysis document with a per-loop reasoning trace (markdown, sections as in step 9).
- A refined, evidence-weighted conclusion with key insights and remaining uncertainties.

## Failure modes

- **Drift:** the agent wanders from the original question. Mitigated by restating the problem at the start of every loop (steps 3-6).
- **Overuse:** running loops on trivial lookups wastes time. Mitigated by the step 1 gate.
- **False convergence:** stopping early while contradictions remain unexamined. Mitigated by the explicit convergence signals in step 7.
- **Length without grounding:** output grows but adds no evidence. Each loop must add new evidence, alternatives, or challenges — not restate prior loops.

## Source

Jon Komet, "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" (Discord thread `1485392832154832906/1519931768612847647`, 2026-08-23), attachment `deepthink-skill-handoff-clean.md`.