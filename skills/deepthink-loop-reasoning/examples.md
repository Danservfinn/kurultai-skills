## Example 1 — Architecture decision (automatic trigger)

**Input:** "Should we use Next.js API routes or a separate backend service for a small SaaS?"

**Behavior:** No trigger phrase, but this is an architecture decision comparing competing approaches, so DeepThink applies automatically at Standard depth.

**Output shape:**

```
# DeepThink Analysis

## Problem
Next.js API routes vs. a separate backend service for a small SaaS.

## Depth Applied
4 loops / Standard

## Reasoning Journey

### Loop 1 — Surface
[LOOP 1] Problem restated: choose between Next.js API routes and a separate backend for a small SaaS.
Initial hypothesis: API routes are fine for a small SaaS; fewer moving parts, faster to ship.

### Loop 2 — Explore
[LOOP 2] Problem restated: ...
Counterevidence: separate backend enables independent scaling, non-JS services, cleaner boundaries if the product grows. Edge case: long-running requests hit serverless timeouts on API routes.

### Loop 3 — Challenge
[LOOP 3] Problem restated: ...
Weak point of hypothesis: "small SaaS stays small" is an assumption, not a fact. Failure mode: vendor lock-in to one deployment model.

### Loop 4 — Synthesize
[LOOP 4] Problem restated: ...
Refined conclusion: start with API routes; define the service boundary so extraction to a separate backend later is cheap.

## Conclusion
Use Next.js API routes now, with an explicit interface layer so a backend service can be split out without a rewrite.

## Key Insights
- Serverless timeout limits are the hardest constraint to reverse later.
- The decision is really about reversibility, not feature sets.

## Remaining Uncertainties
- Expected request durations under real load are unknown.

## Recommendations
Prototype the slowest planned endpoint first to test timeout behavior before committing.
```

## Example 2 — Devil's advocate trigger

**Input:** "devil's advocate this: we're moving our whole infra to Kubernetes"

**Behavior:** Explicit trigger plus devil's-advocate mode. Bias hard toward Loop 3; state the strongest opposing argument before concluding.

**Output shape:** Standard depth, but Loop 3 is expanded: strongest opposing argument stated first ("Kubernetes is a platform for running many services with complex scheduling needs; a team of 5 with 6 services is paying operational tax for capabilities it does not use"), followed by assumption challenges (who is on-call, what breaks at 3am, what the actual scaling problem is), then Synthesize and converge.

## Example 3 — When NOT to use it

**Input:** "what time is it in Berlin?"

**Behavior:** Simple factual lookup. Do not run loops. Answer directly. Running DeepThink here is a failure mode (overuse), not thoroughness.

## Example 4 — Install and verify

**Input:** "Install this DeepThink skill on my Hermes setup."

```bash
mkdir -p ~/.hermes/skills/deepthink
cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md
hermes skills list | grep -i deepthink
hermes chat -q "Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS."
```

Expected: `hermes skills list` shows the deepthink skill; the chat query returns a looped analysis rather than a single shallow answer.