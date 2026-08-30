## Example 1 — Architecture decision (standard depth)

Input:
> Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS.

Expected behavior: 3–4 loops. Loop 1 restates the problem and gives a first-glance hypothesis (API routes are simpler). Loop 2 explores alternatives (separate service, serverless functions, hybrid). Loop 3 challenges assumptions (team size, expected load, coupling). Loop 4 synthesizes. Output includes all seven sections with a clear recommendation.

## Example 2 — "What am I missing?" (quick depth)

Input:
> What am I missing? I'm about to sign a 12-month contract with a single cloud vendor for a side project.

Expected behavior: 1–2 loops. Loop 1 restates and surfaces the obvious (lock-in, price). Loop 2 explores edge cases (egress fees, vendor failure, project abandonment). Convergence check passes after Loop 2; output is short but structured with Remaining Uncertainties listed honestly.

## Example 3 — Devil's advocate (deep depth)

Input:
> Devil's advocate this: we're moving our whole infra to Kubernetes because everyone else did.

Expected behavior: devil's advocate pattern — bias hard toward Challenge. Loops actively seek contradictions rather than confirmation. Before concluding, state the strongest version of the opposing argument (keep the current setup). Output includes evidence weighting: strongest evidence, weakest assumption, and what would make the conclusion wrong.