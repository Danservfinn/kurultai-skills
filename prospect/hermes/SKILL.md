---
name: prospect
description: "Walk any platform as a realistic prospect and deliver an HTML feedback report."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [ProspectWalkthrough, ProductFeedback, Conversion, CompetitorTeardown, GTM]
---

# Prospect Walkthrough (any platform)

Pick a platform, learn it cold, then send one believable buyer through it and
write down what happened. The value of this skill is honesty: the persona's
patience, budget, and skepticism decide every judgment — not what you know
about how the product works.

Works on any target — a developer tool, a SaaS app, a consumer subscription, a
marketplace, a shop, an open-source project, a competitor. `parse-prospect` is
the fixed-target version of this for parsethis.ai; **this is the general form,
and Phase 0 is what makes it general: you learn the platform before you judge
it.**

Uses native Hermes tools: `browser_navigate` + `browser_vision` for the
walkthrough, `terminal` for probes and API calls, `web_search` for the outside
view, `delegate_task` for parallel research, `write_file` for the report.
Model-agnostic — no external CLI dependency beyond the active Hermes provider.

## Invocation

The prompt names a target: a URL, a product name, or "our competitor X". If
nothing is named, ask for one. Everything else is optional and inferred in
Phase 0 — persona angle, time budget, depth, whether we own the product. Honor
anything the user does supply; a named persona angle overrides rotation.

## Ground Rules (bind every phase)

1. **Learn before you judge.** Phase 0 is a gate, not a warm-up. A walkthrough
   of a product you misread produces confident nonsense. No persona may be
   written until the dossier answers Phase 0's questions.
2. **Evidence before empathy.** Every persona trait traces to a source: site
   copy, market research, review sites, or internal docs when we own the
   product. Where sources conflict the outside view wins — prospects are who
   they are, not who the site wishes they were.
3. **Enter through the front door.** Start where a stranger starts: the landing
   URL or a search result. No insider URLs, no repo knowledge. If the persona
   cannot find it, that IS the finding.
4. **Judge with the persona's brain.** Banned: excusing a bug because you know
   its cause, reading a docs page the persona would have bounced from, retrying
   a failed call more than an impatient stranger would. When the persona would
   leave, record the exit moment and what would have kept them — then continue
   if useful, labelled "post-exit exploration," and keep it out of the scorecard.
5. **Do the things, don't imagine them.** Load the real pages, click the real
   buttons, run the real quickstart, make real calls with realistic payloads.
   Screenshot via `browser_vision`. Paste real response bodies, error text and
   latencies into the report. A walkthrough without artifacts is fiction, and
   fiction gets the report dismissed.
6. **Light touch, and stay inside what's allowed.** Public pages, documented
   free tiers, published APIs. No paywall or auth bypass, no credential
   guessing, no load testing, no bulk scraping; honor robots.txt and the terms.
   Under ~10 API calls at human pace. **Never invent an identity to get past a
   signup** — no made-up names on forms that ask for real ones, no fake payment
   details. If the walkthrough needs an account, stop and ask the operator
   whether to create one and with which identity. A wall you will not climb is
   a finding, not a failure. On **our own** product there is a legitimate way
   through a paywall that fakes nothing — see "Getting Past the Card Field". On
   someone else's there is not, and the wall is where the walkthrough ends.
7. **Ours or theirs changes the job.** For our own product, internal sources are
   fair game for the **dossier** — never for the walkthrough — and the report is
   blunt and fix-oriented. For a third party: public sources only, the report is
   a teardown, and every claim about their internals is marked as inference.

## Sandbox Boundary

The walkthrough agent must hold the same context as a stranger. Internal
knowledge — which features are shipped versus planned, which claims the team
considers safe — contaminates every judgment, because the persona can no longer
honestly "discover" a broken feature or "notice" an overclaim.

When we own the product, the split is: **the dossier may read internal sources;
the walkthrough may not.** Build the dossier first, then walk with nothing but
the live site in hand. When `delegate_task` fans out research, carry this
boundary in the `context` field of every dispatch — contamination propagates
through subagent summaries.

## Prerequisites

- **Target reachable**: `curl -s -o /dev/null -w "%{http_code}" <url>` returns 200
- **Report dir**: `~/reports/prospect/<target-slug>/` (created on first run)
- **Dossier**: `~/reports/prospect/<target-slug>/dossier.md`, refreshed per run
  so run N+1 costs a fraction of run 1

## How to Run

```
Phase 0: learn the platform (terminal probe + web_search + delegate_task)
Phase 1: persona synthesis
Phase 2: live walkthrough (browser_navigate + terminal)
Phase 3: HTML report (write_file)
```

## Procedure

### Phase 0 — Learn the platform

Produce a dossier answering all six:

1. **Resolve the target.** Name → canonical URL; confirm it is the right product
   (name collisions are common). Company behind it, age, size, backing.
2. **Establish ownership.** Ours or a third party? Check the brain wiki's
   project pages and local repos; ask if unclear. This decides rule 7 and which
   sources Phase 0 may use.
3. **Map the surface.** Probe the standard route set plus `sitemap.xml` for
   status, redirect, type and title, then walk nav and footer in a browser for
   what a probe cannot guess. Note machine surfaces: `/llms.txt`,
   `/openapi.json`, `/.well-known/*`, `/mcp`, `/status`, RSS, changelog. Record
   404s and orphan pages now — they are findings later.
4. **Read the product.** What it does in one sentence a stranger would accept.
   Category and archetype. The job it claims to do. Which features are shipped
   versus announced. Headline claims and the proof offered.
5. **Find the access model.** The most consequential fact in the dossier, because
   it decides how far the walkthrough can go: open and keyless / free tier behind
   signup / trial behind a card / freemium / waitlist / demo-request only /
   paid-only / self-host. **Locate the wall precisely** and note what the site
   tells a stranger about what is past it.
6. **Do the money.** Pricing shape, billing unit, what is metered, what the
   persona's real usage would cost per month, what is hidden until contact-sales.

### Phase 1 — Persona synthesis

One primary persona, as a card: name, role, company size, what they are
shipping, stack, the incident or fear that brought them here, evaluation style,
a specific time budget ("25 minutes tonight"), budget authority, their
alternative if this fails, and 3–5 personal heuristics ("if the quickstart
curl fails first try, I'm out"). Rotate the lens across runs.

Add the **competitive frame**: real evaluators arrive comparing. Name the
alternatives from Phase 0 and score the target the way the persona would score
it against theirs, not against perfection.

### Phase 2 — The walkthrough

Time-boxed to the persona's budget. For each step record: **stage → what I did →
what I expected → what actually happened → verdict (delight / fine / friction /
exit-risk)**, with `browser_vision` screenshots at emotionally significant
moments — first impression, first confusion, first success.

Typical path, but follow the persona's instincts rather than this list: landing
read; whichever path their evaluation style dictates; the interactive surface
with a payload from their own world; first real call, timed from "decided to
try" to first success; the one docs page their integration hinges on; pricing
math against their real volume; the trust check their org requires; the exit
decision and the single change that would move them one rung.

Capture every 404, broken snippet, unverifiable claim, and moment of genuine
delight. Re-run any load-bearing negative finding to confirm it is
deterministic, and separate "tier limitation" from "product gap" every time.

### Phase 3 — The report

**Voice: first person, as the persona, throughout.** Not a study of a prospect —
the prospect's own account. Third person lets you drift back into the builder's
head and start explaining why a thing is the way it is; first person makes that
drift audible, because the persona has no idea why. If a sentence could not be
said by someone who has never seen the repo, cut it.

One self-contained HTML file to
`~/reports/prospect/<target-slug>/<date>-<persona-slug>.html`. Sections:

- **Who I am** — self-introduction, with the evidence trail per trait alongside
  as annotation rather than folded into the voice
- **What I did** — the stage/did/expected/actual/verdict table, screenshots
  inline, real response bodies and latencies
- **Platform map** — every surface touched, its job, its state
- **What worked, what didn't** — each with evidence, no vibes without receipts
- **Claim ledger** — claim, probe, verdict (held / unverifiable / contradicted)
- **Does it pay for me** — the value math and the break-even sentence
- **Scorecard** — 1–5 against first impression, time-to-first-success, docs,
  pricing clarity, trust signals, competitive standing, with the persona's
  alternative as the comparison column
- **What would have kept me** — prioritized by conversion impact × build effort,
  each concrete enough to become a ticket
- **Where I landed** — converted or not, and the single change that moves them up

Recommendations are the one place to shift register, because the audience
changes: frame each as what would have changed the persona's mind, then state
the fix plainly enough to become a ticket.

Never invent biography to fill the voice, and when the persona is an archetype
composite rather than a real named person, say so on the card — first person
makes a report read as testimony, so who is testifying must be honest.

## Getting Past the Card Field (our own product only)

Most walkthroughs die at the payment form, so everything behind it goes
unexamined — the success page, the entitlement grant, the billing dashboard, the
portal, cancelling, downgrading. That is often where the worst defects live,
precisely because nobody walks it. On a product we own, two mechanisms open it
without faking anything. On a third party's, neither exists.

**A test-mode replica (default).** Run the product against the payment
provider's test mode, on its own database and port, with webhooks forwarded to
it. Purchases cost nothing and touch no production state, so a run can buy
repeatedly and reset between actors.

**An owner-issued full-discount code (when the evaluation must happen live).**
Mint a single-use 100%-off code scoped to the products being evaluated, with a
short expiry. The persona walks the real funnel and pastes it like any customer
with a promo in their inbox.

Whichever is used:

- **Never fake payment details, and never charge a real card without the
  operator saying so.** A test card belongs only in test mode. If the only way
  through is real money, stop and ask.
- **A full discount usually removes the card form entirely**, because a provider
  expecting no future charge stops asking for a payment method. That is what
  makes this work without a card — and it means the card form goes unwalked, so
  say so wherever it could matter to a finding.
- **Tear down what the run created.** A fully-discounted subscription is still
  an active subscription in the owner's revenue reporting, and a test
  organization with no delete endpoint is permanent. Know before starting which
  artifacts you can remove and which you cannot; the ones you cannot are a
  reason to prefer the replica.
- **Say which host produced each finding.** Latency from a local replica is not
  comparable to production, and a defect seen only there needs re-checking
  against the live site before it becomes a ticket.
- **Setup is an operator step, not a persona step.** Starting the replica or
  minting a code means touching the repo, which would contaminate the persona.
  Prepare it first, then hand the walkthrough nothing but a base URL and a code.

## Pitfalls

1. **Skipping Phase 0** — the failure that produces confident nonsense. A
   persona built on a misread product misjudges everything downstream.
2. **Contaminating the walkthrough with dossier knowledge** — the dossier may
   read internal sources; the walkthrough may not. Keep the split hard.
3. **Reporting a tier limitation as a product gap** — always state which tier
   and which layer produced a verdict, and re-verify with a fresh key.
4. **Testing against a dev host** — a local instance may be a dirty state. Walk
   the real site unless the run has deliberately switched, and label the host.
5. **Weighing friction over delight** — genuine strengths tell marketing what to
   amplify and are worth as much as the bug list.
6. **Letting a run end without teardown** — the run that errors out is exactly
   the one that leaves a subscription or an org behind.

## Verification

The report exists and opens; it contains a scorecard with 1–5 ratings, at least
one real response body with timing, and a prioritized recommendation list with
impact/effort tags. The dossier has been written or refreshed for the target.

If the run bought a plan, verify the cleanup: no discount code left active, no
subscription left running, and any replica stopped.
