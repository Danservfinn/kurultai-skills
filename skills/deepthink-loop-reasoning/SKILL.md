---
name: deepthink-loop-reasoning
description: Apply a multi-loop structured reasoning process (surface, explore, challenge, synthesize, converge) to complex decisions before giving a final answer. Triggers on explicit phrases like "think deeper" or "devil's advocate this", and automatically on architecture choices, tradeoff comparisons, and multi-step reasoning chains.
category: reasoning
---

# DeepThink — Loop-Based Reasoning

## Goal

Replace a single-pass answer with a repeatable multi-loop reasoning process for non-trivial problems. Each loop re-injects the original problem, adds new evidence or challenges, and checks whether reasoning has converged. The goal is better-grounded answers, not longer ones.

## Inputs

- A non-trivial problem statement or decision (architecture choice, security analysis, tradeoff comparison, strategy decision).
- Optional explicit trigger phrase: "think deeper", "deep think", "reason through this", "analyze this thoroughly", "what am I missing?", "devil's advocate this".

Do NOT trigger on: simple factual lookups, single-step tasks, or tasks already handled by a more specialized skill.

## Steps

1. Restate the original problem in one sentence. This restatement is re-emitted at the start of every loop to anchor reasoning and prevent drift.
2. Loop 1 (Surface): write a fast initial hypothesis of what seems true at first glance. Do not research or challenge yet.
3. Loop 2 (Explore): generate counterevidence, alternative approaches, edge cases, and missing paths not considered in Loop 1.
4. Loop 3 (Challenge): question assumptions, identify risks, failure modes, and weak points of the current hypothesis. In devil's-advocate mode, bias heavily toward this loop and state the strongest opposing argument before concluding.
5. Loop 4 (Synthesize): integrate the strongest points from all prior loops into a refined conclusion.
6. Run a convergence check: if the same conclusion is reached from different angles with no new contradictions, stop. If new contradictions or challenged assumptions appear, run another loop.
7. For any Loop 5+ (escalation): repeat the full loop procedure with a defined focus — Loop 5 (Breakout): question first principles ("what are we assuming that isn't true?", "what would this look like if we'd never solved a similar problem?"); Loop 6 (Re-Challenge): run a second Challenge pass against the Loop 4/5 conclusion; Loop 7 (Final Synthesize): re-integrate. Do not exceed 7 loops without explicit user direction. Each escalation loop still begins with the problem restatement and ends with the convergence check.
8. Weight the evidence: state the strongest single piece of evidence for the conclusion, the weakest assumption it rests on, and what would make the conclusion wrong.
9. Format the output as: Problem, Depth Applied (loop count and level), Reasoning Journey (per loop, each beginning with the problem restatement), Conclusion, Key Insights, Remaining Uncertainties, Recommendations.

Depth guidance: start at Standard (3-4 loops). Escalate to Deep (5-6) only if divergence persists after Loop 4. Maximum (7+) requires explicit user direction.

## Outputs

A structured DeepThink analysis document with per-loop reasoning trace, refined conclusion, key insights, and remaining uncertainties, in the format defined in Step 9.

## Failure modes

- Agent drifts from the original question because the problem is not re-injected each loop.
- Premature convergence: stopping after Loop 1 on a problem that warranted Standard depth.
- Excessive looping on simple factual lookups or single-step tasks where the skill should not trigger.
- Longer but not better-grounded answers if loops add volume without new evidence — if a loop produces nothing new, that is a convergence signal, not a reason to continue.

## Source

Jon Komet, "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" (Discord thread 1485392832154832906/1519931768612847647, 2026-08-21), attachment `deepthink-skill-handoff-clean.md`.