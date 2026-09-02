# Examples — deepthink-loop-reasoning

## Example 1: Architecture decision (Standard depth, 4 loops)

**Input:**
> Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS.

**Expected behavior:**
- Gate passes (architecture decision).
- `[LOOP 1] Problem restated: Should a small SaaS use Next.js API routes or a separate backend service?` → Surface: Next.js API routes seem sufficient for a small SaaS; faster to ship, one deploy.
- `[LOOP 2]` same restatement → Explore: separate backend enables non-JavaScript services, independent scaling, cleaner boundaries for future mobile clients; edge cases: long-running requests hitting serverless timeouts, vendor lock-in to Vercel request limits.
- `[LOOP 3]` same restatement → Challenge: assumption "small SaaS stays small" is the weak point; migration cost later vs. premature complexity now.
- `[LOOP 4]` same restatement → Synthesize: start with Next.js API routes; keep business logic in a separate module so extraction later is cheap.
- Convergence check after loop 4: same conclusion reinforced from ship-speed, complexity, and migration-cost angles; no new contradictions → stop.

**Output contains:** all eight required sections; Depth Applied reads `4 loops / Standard`.

## Example 2: Security analysis with Devil's Advocate Mode

**Input:**
> Devil's advocate this: we're planning to expose our internal admin API to the internet behind a single shared API key.

**Expected behavior:**
- Gate passes (security analysis) and Devil's Advocate pattern requested → bias toward Challenge-loop patterns.
- Loops run with the problem restated each time; Loop 3 carries the most weight: shared key cannot be rotated per-user, no revocation granularity, key leakage exposes full admin surface, no audit trail attribution.
- State the strongest version of the opposing argument before concluding ("a shared key is operationally simplest and fine for a team of 3").
- Conclusion: reject shared key; use short-lived per-user tokens (OIDC) with scoped roles. Evidence Weighting applied: strongest evidence is lack of per-principal revocation; weakest assumption is that the team stays small.

## Example 3: Gate rejection — do not loop

**Input:**
> What time is it in Ulaanbaatar?

**Expected behavior:**
- Gate fails (simple factual lookup). Do not run loops, do not emit a DeepThink Analysis. Answer directly, e.g. via `TZ Asia/Ulaanbaatar date`.

## Example 4: Divergence → escalate to Deep

**Input:**
> Think deeper: should we migrate our monolith to microservices, or refactor in place? Compliance requires an audit answer by Friday.

**Expected behavior:**
- Loops 1-4 run; convergence check after loop 4 finds a new contradiction (team capacity data conflicts with the migration timeline claim) → escalate to loop 5 (Deep, 5-6 loops), and the final output's `## Remaining Uncertainties` honestly lists the unresolved capacity question.