---
name: deepthink-loop-reasoning
description: Loop-based deep reasoning for complex decisions. Triggers on "think deeper", "reason through this", "what am I missing?", "devil's advocate this", and automatically on architecture choices, security/threat analysis, tradeoff comparisons, and multi-step reasoning chains. Use before giving a final answer on any non-trivial problem.
category: reasoning
---

# DeepThink — Loop-Based Reasoning

## Goal

Replace a single-pass answer with a structured multi-loop reasoning process (Surface, Explore, Challenge, Synthesize, Converge) so the final answer is better grounded, not merely longer.

## Inputs

- A non-trivial problem statement or decision: architecture choice, security analysis, tradeoff comparison, strategy decision.
- Optional depth level from the user: `quick` (1–2 loops), `standard` (3–4), `deep` (5–6), `maximum` (7+). If absent, start at `standard`.

No API keys or external services are required. This skill is pure reasoning over the given problem; it may be combined with web/file access when the problem needs evidence.

## Steps

1. **Gate check.** If the task is a simple lookup or single-step answer ("what time is it?", "grep for this string"), do not use this skill — answer directly.
2. **Restate the problem.** Write the original problem in one sentence. Re-inject this restatement at the start of every loop, prefixed `[LOOP N] Problem restated:`. This prevents drift.
3. **Loop 1 — Surface.** State the fast initial hypothesis: what seems true at first glance? Note the current state of reasoning (nothing established yet).
4. **Loop 2 — Explore.** Generate counterevidence, alternatives, edge cases, and paths not considered in Loop 1. Explicitly note whether each item confirms, contradicts, or refines Loop 1.
5. **Loop 3 — Challenge.** Question assumptions, identify risks, failure modes, and weak points of the current hypothesis. Ask "what did I assume?" and "what would make this wrong?"
6. **Loop 4 — Synthesize.** Integrate the strongest points from all loops into a refined conclusion.
7. **Convergence check after every loop.** Ask: has reasoning stabilized?
   - Converged (stop): same conclusion reached from different angles, no new contradictions, edge cases accounted for, remaining questions are clarifications not fundamental uncertainties.
   - Diverged (continue): new contradictions, key assumptions challenged, uncertainty increased. Run another loop.
8. **Depth control.** Start at Standard (3–4 loops). Escalate to Deep (5–6) only if divergence persists after Loop 4. Never run Maximum (7+) without explicit user direction. Hard cap: if divergence persists after Loop 6 without user escalation, stop and report the unresolved contradictions under Remaining Uncertainties — do not loop indefinitely.
9. **Format the output** exactly as:

   ```markdown
   # DeepThink Analysis

   ## Problem
   <original problem statement>

   ## Depth Applied
   <N> loops / <depth level>

   ## Reasoning Journey

   ### Loop 1 — Surface
   <what we found>

   ### Loop 2 — Explore
   <new evidence, alternatives>

   ### Loop N — <loop type>
   <final loop>

   ## Conclusion
   <refined answer integrating all loops>

   ## Key Insights
   - <insight 1>
   - <insight N>

   ## Remaining Uncertainties
   - <only if divergence was not resolved>

   ## Recommendations
   <if the user asked for action — next steps>
   ```

10. **Optional special patterns** (apply only when requested or clearly apt):
    - **Devil's Advocate**: bias toward Challenge patterns; state the strongest version of the opposing argument before concluding.
    - **First Principles breakout**: when stuck, run a loop asking what is assumed that isn't true, and what the simplest solution ignoring artificial constraints looks like.
    - **Evidence Weighting**: after loops stabilize, state the strongest single piece of evidence for the conclusion, the weakest assumption it rests on, and what would make the bet lose.

## Outputs

A single DeepThink Analysis document (markdown) containing: Problem, Depth Applied, per-loop Reasoning Journey with restated problem at each loop head, Conclusion, Key Insights, Remaining Uncertainties (if any), and Recommendations (if action was requested).

## Failure modes

- **Drift**: the agent wanders from the original question. Mitigation: mandatory one-sentence restatement at the top of every loop.
- **Padding**: loops generate length rather than new insight. Mitigation: each loop must add new evidence, alternatives, or challenges; if a loop adds nothing, declare convergence and stop.
- **Misapplication to trivial tasks**: a single answer suffices for lookups. Mitigation: Step 1 gate check.
- **Non-convergence**: loops keep finding contradictions forever. Mitigation: hard cap at Loop 6 without user escalation; report unresolved contradictions honestly.

## Source

Jon Komet, "DeepThink Skill Handoff" (`deepthink-skill-handoff-clean.md`), shared in Discord thread "The DeepThink Skill: Making Hermes Slow Down Before Expensive Decisions", 2026-08-24 (attachment dated 2026-06-26). Install target per source: `~/.hermes/skills/deepthink/SKILL.md` — treat as the author's stated convention, not a verified path; confirm your agent's actual skill directory before installing.