# Examples — deepthink-loop-reasoning

## Example 1: Architecture decision (Standard depth)

**Input:**

```
Use deepthink to reason through whether I should choose Next.js API routes
or a separate backend service for a small SaaS with ~500 users, 3 devs,
and a billing integration via Stripe.
```

**Expected behavior:** 3–4 loops. Loop 1 restates the problem and gives the fast hypothesis (Next.js API routes — smaller team, less ops). Loop 2 surfaces alternatives (separate Fastify service, serverless functions outside Next) and edge cases (long-running Stripe webhooks, background jobs). Loop 3 challenges the assumption that the team stays at 3 devs and that API routes handle webhook retry semantics. Loop 4 synthesizes. Output contains all seven sections from SKILL.md step 11, with `## Depth Applied` reading `4 loops / Standard` and `## Remaining Uncertainties` present (e.g., "None — convergence reached at loop 4" or listed gaps such as expected job volume).

## Example 2: Security analysis with Devil's Advocate

**Input:**

```
Devil's advocate this: we're considering storing session tokens in
localStorage for our internal admin panel because it's simpler than
httpOnly cookies. What am I missing?
```

**Expected behavior:** Standard depth with Devil's Advocate pattern — Loop 3 (Challenge) is expanded: XSS exfiltration of localStorage, missing cookie flags (SameSite, Secure), CSRF tradeoff reversal. The strongest version of the opposing argument (httpOnly cookies with a CSRF token) is stated before the Conclusion. Conclusion recommends against localStorage; Recommendations section included because the user is deciding an implementation.

## Example 3: Escalation to Deep depth

**Input:**

```
Reason through this thoroughly: we're choosing between Postgres, DynamoDB,
and CockroachDB for a multi-region SaaS that must survive a regional
outage. Standard depth isn't settling it — keep going.
```

**Expected behavior:** Loops 1–4 run; suppose loop 3's cross-loop integration reports divergence (consistency-model tradeoffs contradict the loop 1 hypothesis). Per step 10, additional loops run (5–6 total, Deep depth). `## Depth Applied` reads e.g. `6 loops / Deep`. Remaining Uncertainties lists unresolved items such as untested failover behavior under the user's actual write pattern.