# Examples

## Example 1 — Architecture choice (Standard depth)

**Input:**

> Use deepthink to reason through whether I should choose Next.js API routes or a separate Fastify backend service for a small SaaS with 3 devs.

**Expected behavior:** 4 loops. Loop 1 surfaces "API routes, fewer moving parts." Loop 2 explores alternatives (separate service, serverless functions, monorepo split) and edge cases (long-running jobs, websockets). Loop 3 challenges the "small team = less infra" assumption (coupling deploy cycles, vendor lock-in). Loop 4 synthesizes: API routes now, extract a service only when a long-running-job requirement lands. Convergence check passes (same conclusion from team-size and risk angles). Output uses the full DeepThink Analysis format with `4 loops / Standard`.

## Example 2 — Security analysis (Devil's Advocate)

**Input:**

> Devil's advocate this: we store session tokens in localStorage because it's simpler than cookies for our SPA.

**Expected behavior:** Loops biased toward Challenge. Loop 1 surface: "works, common pattern." Loop 2: XSS exfiltration path, `HttpOnly` cookie alternative, token rotation. Loop 3 (dominant): strongest version of the opposing argument stated explicitly — "any single XSS bug becomes full account takeover, and XSS is the most common web vuln class." Loop 4 synthesizes: move to HttpOnly cookies with CSRF protection. Output includes the opposing argument verbatim under Key Insights.

## Example 3 — Trivial task (gate check, skill NOT applied)

**Input:**

> Think through this: what's the exit code of `grep foo missing.txt`?

**Expected behavior:** Step 1 gate check fires — this is a single factual answer (exit code 2, file not found). Answer directly in one or two sentences. Do not emit a DeepThink Analysis document. If the user pushes back with "no, really think deeper," then apply Quick depth (1–2 loops).