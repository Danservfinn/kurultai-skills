## Example 1 — Architecture decision (automatic trigger)

**Input:**

> Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS.

**Behavior:**

- Loop 1 (Surface): initial hypothesis — Next.js API routes are fine for a small SaaS; less ops overhead.
- Loop 2 (Explore): alternatives (separate Fastify service, serverless functions outside Next), edge cases (long-running jobs, websockets, team growth, vendor lock-in to Vercel).
- Loop 3 (Challenge): assumption "small SaaS stays small" is the weak point; background jobs and queue workers don't fit the request/response model well.
- Loop 4 (Synthesize): Next.js API routes for the product surface, extract a worker service only when long-running jobs appear.
- Convergence: same split conclusion reached from cost, ops, and scaling angles. Stop at 4 loops (Standard).

**Output sections:** Problem, Depth Applied (4 loops / Standard), Reasoning Journey, Conclusion, Key Insights, Remaining Uncertainties, Recommendations.

## Example 2 — Devil's advocate trigger

**Input:

> Devil's advocate this: we're moving our infra to a single-region Kubernetes cluster to cut costs.

**Behavior:**

- Bias hard toward Loop 3 (Challenge). State the strongest version of the opposing argument (multi-region or managed-PaaS reliability) before concluding.
- Loop 2 surfaces edge cases: region outage, etcd quorum loss, upgrade windows, on-call load for a small team.
- Evidence weighting: strongest evidence for single-region is the cost delta; weakest assumption is "region outages are rare enough to tolerate"; what loses the bet is a multi-hour region outage during a launch week.

## Example 3 — Skip case (over-looping guard)

**Input:

> What's the default port for Postgres?

**Behavior:** Do not run DeepThink. This is a simple factual lookup (answer: 5432). Running loops here is a failure mode, not thoroughness.