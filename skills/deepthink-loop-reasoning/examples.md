# Examples — deepthink-loop-reasoning

## Example 1: Architecture choice (Standard depth, 4 loops)

**Input:**
> Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS.

**Expected behavior:** 4 loops. Loop 1 restates the problem and gives the fast answer ("API routes, it's simpler"). Loop 2 surfaces alternatives (separate Fastify service, serverless functions) and edge cases (long-running jobs, non-Node dependencies). Loop 3 challenges the "small SaaS stays small" assumption. Loop 4 synthesizes. Output contains all seven sections from Step 9, with Depth Applied: "4 loops / Standard".

## Example 2: Devil's advocate trigger

**Input:**
> Devil's advocate this: we're planning to store all session state in Redis with no TTL eviction.

**Expected behavior:** Loops run as usual, but Loop 3 (Challenge) is expanded — the strongest version of the opposing argument (unbounded memory growth, eviction storms, cost) is stated before any conclusion. Evidence weighting names the weakest assumption (e.g., "session sizes stay under 1 KB").

## Example 3: Skill correctly does NOT trigger

**Input:**
> What's the syntax for grep case-insensitive search?

**Expected behavior:** No DeepThink loops. The agent answers directly (`grep -i pattern file`). Applying the loop structure here would be a failure mode (excessive looping on a simple lookup).