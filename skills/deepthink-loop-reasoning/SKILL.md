---
name: deepthink-loop-reasoning
description: Run a multi-loop structured reasoning process (surface, explore, challenge, synthesize, converge) before answering non-trivial decisions. Re-injects the original problem each loop to prevent drift. Triggers on "think deeper", "devil's advocate this", "what am I missing?", and automatically on architecture decisions, security analysis, risk/tradeoff analysis, and competing-approach comparisons.
category: content
---

# DeepThink — Loop-Based Reasoning

## Goal

Produce a better-grounded answer to a non-trivial decision by running the question through repeated reasoning loops (Surface, Explore, Challenge, Synthesize, Converge) instead of trusting the first plausible answer. The original problem is restated at the start of every loop to prevent drift.

## Inputs

- A problem statement or decision question (required).
- Optional trigger phrase from the user: "think deeper", "deep think", "reason through this", "think this through", "analyze this thoroughly", "what am I missing?", "devil's advocate this".
- No API keys or external services required. This is a pure reasoning workflow.

## Steps

1. Decide whether DeepThink applies. Use it for architecture decisions, security/threat modeling, multi-step reasoning chains, comparing competing approaches, risk/tradeoff analysis, or any problem where a quick answer would be oversimplified. Do NOT use it for simple factual lookups ("what time is it?", "grep for this string") or single-step tasks.
2. Set depth to Standard (3–4 loops). Escalate to Deep (5–6) only if divergence persists after loop 4. Never use Maximum (7+) without explicit user direction.
3. Loop 1 (Surface): restate the original problem in one sentence (`[LOOP 1] Problem restated: <one sentence>`), then write a fast initial hypothesis — what seems true at first glance.
4. Loop 2 (Explore): restate the problem again. Generate counterevidence, alternatives, edge cases, and missing paths not yet considered. Note whether this confirms, contradicts, or refines loop 1.
5. Loop 3 (Challenge): restate the problem again. Question assumptions, risks, failure modes, and weak points of the current hypothesis. In devil's-advocate mode, bias hard toward this loop and state the strongest version of the opposing argument before concluding.
6. Loop 4 (Synthesize): restate the problem again. Integrate the strongest points from all loops into a refined conclusion.
7. After each loop, run a convergence check. Converged: same conclusion reached from different angles, no new contradictions, edge cases accounted for, remaining questions are clarifications not fundamental uncertainties. Diverged: new contradictions, key assumptions challenged, uncertainty increased. Stop if converged; run another loop if diverged.
8. If the problem feels stuck in a local maximum, insert a breakout loop asking: what are we assuming that isn't true; what would this look like if we'd never solved a similar problem; what's the simplest solution ignoring all constraints except the real ones.
9. After loops stabilize, state evidence weighting: the strongest single piece of evidence for the conclusion, the weakest assumption it rests on, and what would make the conclusion wrong.
10. Format the final output with sections: Problem, Depth Applied, Reasoning Journey (one subsection per loop), Conclusion, Key Insights, Remaining Uncertainties (only if divergence unresolved), Recommendations (if the user asked for action).
11. Optionally install as a Hermes skill:
    ```bash
    mkdir -p ~/.hermes/skills/deepthink
    cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md
    hermes skills list | grep -i deepthink
    ```
    For a named profile, use `~/.hermes/profiles/<profile-name>/skills/deepthink/` instead. If the skill does not appear via gateway/Telegram/Discord, run `hermes gateway restart`.

## Outputs

- A structured DeepThink Analysis document (markdown) with: Problem, Depth Applied, per-loop Reasoning Journey, Conclusion, Key Insights, Remaining Uncertainties, Recommendations.

## Failure modes

- Agent drifts from the original question if the problem is not restated at the start of every loop.
- Overuse on simple factual lookups or single-step tasks, wasting effort.
- Premature convergence: stopping when reasoning has not actually stabilized.
- Loops add length without new insight if the Explore loop generates no genuinely new evidence — stop instead of padding.
- Skill not appearing after install: run `hermes gateway restart` or `/reload-skills` in chat.

## Source

Discord thread "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions" (Jon Komet, 2026-08-20), attachment `deepthink-skill-handoff-clean.md`. Install target: `~/.hermes/skills/deepthink/SKILL.md`.