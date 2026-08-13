# Field notes — lessons about the method

Read at the start of Phase 2. Lessons about a specific platform belong in that platform's
dossier; this file is only for things that transfer across targets.

Seeded from the parse-prospect run on 2026-08-11 (a developer-tool target). Add one entry
per run that taught something general — and only then.

---

## Run the literal first instruction

Whatever the hero or quickstart tells a stranger to run or click, do exactly that, first,
unedited. Marketing copy drifts ahead of what ships. A 404 on the first instruction is the
highest-impact finding available, and it is the prospect's real experience — not an edge
case.

## The negative case decides the run

Products are demoed on the case they handle. The prospect's real question is what happens
on the case next to it: the benign input that looks adversarial, the record that doesn't
fit the schema, the search with no good results, the edge of the plan. Probe the negative
case early, run a few, and re-run any hit to confirm it's deterministic rather than noise.

## State which layer produced the result

Free tiers, default models, and pattern-only fast paths are not the product. Read the
response envelope or the plan page for what actually served the request, and say so
inline. A free-tier miss is not proof of a product-wide gap, and reporting it as one gets
the whole report dismissed.

## Separate "limit of the tier" from "gap in the product"

Every negative finding needs its caveat stated in the same sentence: free tier only? one
sample or a rate? a mention of the thing or a real use of it? Adversarially re-verify
anything load-bearing before it ships in the report.

## Weigh delights as heavily as friction

Honest limitations in the copy, keyless onboarding, fast responses, a good error message
— name them with the same evidence discipline. They tell marketing what to amplify, and
they're the reason the team trusts the negative findings.

## Cheap probes that pay

- The surface probe finds 404s and orphan pages in one pass, before any browsing.
- Look for a query param or setting that freezes animation before screenshotting a hero.
- JPEG data URIs at q85–90: three screenshots land near 600KB and the file stays
  self-contained.
- A budget of ~8 API calls was plenty for a full developer-tool evaluation.

## Products pitch low and get bought high

Copy concentrates on specs, speed and price. Verdicts turn on whether the buyer stops
being afraid, and on whether they can defend the purchase to someone else. Eight
parse-prospect runs scored engines, latencies and tiers; every single exit was decided by
an incident the persona feared or a hassle they wouldn't take on. Score the pyramid and
say the gap out loud — "pitched at Functional, decided at Individual" is a headline no
feature ticket can fix.

## Separate what's missing from what's unsaid

A finding of "it doesn't do X" is worth a quarter of engineering. A finding of "it does X
and the only mention is a list item on the pricing card" is worth an afternoon of copy.
Reports that don't split those two send the team to build what it already has. Score
delivered and communicated in separate columns and the split writes itself.

## Record confidence live or not at all

A confidence curve drawn at write-up is a story about the verdict. Written at each step,
before the next one, it shows where to put the call to action and where the run really
ended — often several steps before the persona admitted it.

## Ask who they'd have to tell

Even a solo buyer on their own card has an audience: a co-founder, a reviewer, the
customer owed an apology. The sentence they'd use to justify the purchase is where the
individual-level value sits, and it usually comes back as site copy that can be pasted
in unchanged.

## Price do-nothing

Most walkthroughs end at do-nothing, not at a competitor. Its price is zero and its cost
is the full exposure, and a report that hasn't put both on the page hasn't explained the
loss it's reporting.

## Time the activation, don't estimate it

Time-to-first-value is the number the team will act on. Start the clock at "decided to
try" and stop it when value actually lands — not when the page finishes loading.
