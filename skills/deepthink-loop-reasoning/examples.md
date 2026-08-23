# Examples — deepthink-loop-reasoning

## Example 1: Architecture decision (standard depth)

**Input:**

> Use deepthink to reason through whether we should use Next.js API routes or a separate Fastify backend service for a small 3-person SaaS with ~500 users.

**Behavior:**

- Loop 1 (Surface): `[LOOP 1] Problem restated: Choose between Next.js API routes and a separate Fastify service for a small SaaS.` Initial hypothesis: API routes — fewer moving parts, one deploy target.
- Loop 2 (Explore): counterevidence — team may need background jobs and websockets API routes handle poorly; alternatives — API routes now, extract service later; edge case — Vercel function timeouts on long requests.
- Loop 3 (Challenge): assumption "500 users forever" is weak; challenge "one deploy target is simpler" against the cost of migration later.
- Loop 4 (Synthesize): API routes for CRUD, queue-based workers for long tasks; loops 2 and 3 refine rather than contradict loop 1.
- Convergence: same conclusion from cost, ops, and team-size angles. Stop at 4 loops.

**Output sections:** Problem, Depth Applied (4 loops / standard), Reasoning Journey (4 subsections), Conclusion, Key Insights, Remaining Uncertainties, Recommendations, plus evidence weighting (strongest evidence: current traffic; weakest assumption: team stays at 3; what would change it: sustained long-running request workload).

## Example 2: Devil's advocate request

**Input:**

> Devil's advocate this: we're planning to migrate our monolith to microservices next quarter.

**Behavior:** Loop 3 is weighted heaviest. Before concluding, state the strongest opposing argument (e.g., "distributed monolith failure mode: you inherit all microservice operational cost with none of the independence, and your team has no service-mesh experience"). Output uses the same section format, with the opposing argument stated verbatim before the Conclusion.

## Example 3: Trivial task (skill correctly not applied)

**Input:**

> What's the exit code grep returns when no lines match?

**Behavior:** Step 1 gate fires — this is a single-step factual lookup (answer: `1`). Answer directly; do not produce a DeepThink document. If the user follows up with "think deeper about whether we should rely on that in our CI scripts", then the skill applies.