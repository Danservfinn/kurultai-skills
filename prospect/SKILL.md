---
name: prospect
description: Walk any platform as a realistic prospect — learn the product cold first, build an evidence-grounded persona, evaluate the live site and API as that user with a browser and real calls, then deliver an HTML feedback report with a scorecard and prioritized fixes. Use for a prospect walkthrough, persona-based product feedback, a conversion or funnel audit, a competitor teardown, onboarding review, or "evaluate <product> as a customer."
---

# Prospect

Pick a platform, learn it cold, then send one believable buyer through it and write down
what happened. The value of this skill is honesty: the persona's patience, budget, and
skepticism decide every judgment — not what you know about how the product works.

Works on any target — a developer tool, a SaaS app, a consumer subscription, a
marketplace, a shop, an open-source project, a competitor. `parse-prospect` is the
fixed-target version of this for parsethis.ai. This is the general form, and **Phase 0
is what makes it general: you learn the platform before you judge it.**

## Invocation

The prompt names a target: a URL, a product name, or "our competitor X". If nothing is
named, ask for one. Everything else is optional and inferred from Phase 0: persona
angle, time budget, depth, whether we own the product. Honor any of those the user does
supply — a named persona angle overrides rotation.

## Ground rules (they bind every phase)

1. **Learn before you judge.** Phase 0 is a gate, not a warm-up. A walkthrough of a
   product you misread produces confident nonsense. You may not write a persona until
   the dossier answers the five questions in Phase 0.
2. **Evidence before empathy.** The persona comes from research, not from stereotype.
   Every trait traces to a source: site copy, market research, review sites, or internal
   docs when we own the product. Where sources conflict, the outside view wins —
   prospects are who they are, not who the site wishes they were.
3. **Enter through the front door.** Start where a stranger starts: the landing URL or a
   search result. No insider URLs, no repo knowledge, no "we know the endpoint is X." If
   the persona can't find it, that IS the finding.
4. **Judge with the persona's brain.** Banned: excusing a bug because you know its cause;
   reading a docs page the persona would have bounced from; retrying a failed call more
   times than an impatient stranger would. When the persona would leave, record the exit
   moment and what would have kept them — then continue if useful, labeled "post-exit
   exploration," and keep it out of the scorecard.
5. **Do the things, don't imagine them.** Load the real pages, click the real buttons,
   run the real quickstart, make real calls with a realistic payload. Screenshot what the
   persona sees. Paste real response bodies, error text, and latencies into the report. A
   walkthrough without artifacts is fiction, and fiction gets the report dismissed.
6. **Light touch, and stay inside what's allowed.** Public pages, documented free tiers,
   published APIs. No paywall or auth bypass, no credential guessing, no load testing, no
   bulk scraping; honor robots.txt and the terms. Keep it under ~10 API calls at human
   pace. **Never invent an identity to get past a signup** — no made-up names on forms
   that ask for real ones, no fake payment details, no disposable-identity tricks. If the
   walkthrough needs an account, stop and ask the operator whether to create one and with
   which identity. A wall you won't climb is a finding, not a failure: record where it
   stopped the persona and what was on the other side. On **our own** product there is a
   legitimate way through a paywall that fakes nothing — see "Getting past the card
   field" below. On someone else's, there isn't; the wall is where the walkthrough ends.
7. **Ours or theirs changes the job.** For our own product (Phase 0.2), internal sources
   are fair game for the dossier — never for the walkthrough — and the report is blunt
   and fix-oriented. For a third party, public sources only, the report is a teardown,
   and every claim about their internals is marked as inference.
8. **The competitive frame is part of the persona.** Real evaluators arrive comparing.
   Name the persona's alternative — a named rival, the incumbent tool, or "a weekend of
   building it myself" — and score the target against that alternative, not against
   perfection.
9. **Price it, don't just rate it.** A rung and a score record the verdict; they don't
   explain it. Every run scores the value pyramid and does the value math in the persona's
   own numbers — `references/value-pyramid.md`, read in Phase 1 and again in Phase 3. Two
   things follow from it and bind the whole run: element weights are set **before** the
   walkthrough, and a number the persona card can't source is left empty rather than
   invented.

## Phase 0 — Learn the platform

Fan out where you can (parallel agents or a Workflow if the user asked for one;
sequential otherwise). Produce a **dossier** — see `references/dossier-template.md`.

**0.1 Resolve the target.** Turn a name into a canonical URL and confirm it's the right
product (name collisions are common). Note the company behind it, age, size, funding or
backing if public.

**0.2 Establish ownership.** Ours or a third party? Check `~/brain/projects/`
and local repos for a matching project page; ask the user if it's still unclear. This
decides rule 7 and which sources Phase 0 may use.

**0.3 Map the surface.** Run `scripts/surface-probe.sh <url>` for status, redirect, type,
and title across the standard route set plus anything in `sitemap.xml`. Then walk the nav
and footer in a browser for what the probe can't guess. Note every machine-readable
surface: `/llms.txt`, `/openapi.json`, `/.well-known/*`, `/mcp`, `/status`, RSS, a public
changelog. Record 404s and orphan pages now — they're findings later.

**0.4 Read the product.** What it does in one sentence a stranger would accept. Category
and archetype (`references/archetypes.md`). The job it claims to do. Feature list, and
which features are shipped versus announced. The headline claims and proof offered.

**0.5 Find the access model.** The most consequential fact in the dossier — it decides
how far the walkthrough can go. Which is it: open and keyless / free tier behind signup /
trial behind a card / freemium app / waitlist / demo-request only / paid-only /
open-source self-host? **Locate the wall precisely** and note what the site tells a
stranger about what's past it.

**0.6 Do the money.** Pricing shape, the billing unit, what's metered, what the persona's
real usage would cost per month, and what's hidden until contact-sales.

**0.7 Get the outside view.** Web search: who actually buys this, how they evaluate,
session length and evaluation style, standing objections, and the competitor set —
including the do-nothing and build-it-myself options. Review sites, forum threads, and
comparison posts beat the vendor's own copy every time. Reviews are also the cheapest
source of the *individual*-level value elements — what buyers say it did for their week,
their nerves, or their standing with their boss, which no vendor page ever states.

**0.8 Build the claim ledger.** Every checkable number or promise on the site — latency,
accuracy, uptime, "works with X", "set up in 5 minutes", a compliance badge — paired with
the probe that would check it. This becomes the walkthrough's test list.

**0.9 Read the pitch altitude.** Against `references/value-pyramid.md`, mark which value
elements the site actually sells, and how loudly: led with (hero, nav, pricing card),
stated on a page, or buried in one list item. This fills the *communicated* column before
the walkthrough starts, so Phase 3 only has to add what was *delivered*. Note the level
the copy concentrates on — it is half of the run's headline finding.

**Gate — do not start Phase 1 until the dossier answers:** What is this? Who is it for?
How does a stranger get their first real value, and how long should that take? Where is
the wall? What would this persona use instead? Which level of the pyramid does the copy
pitch at? Write the dossier to disk before moving on.

## Phase 1 — Research → persona

Synthesize **one primary persona** from the dossier's ICP signals and outside view. A
card with: name, role, company size and stage, what they're shipping or trying to do,
their stack or context, the incident or fear that brought them here, evaluation style
(docs-first / demo-first / pricing-first / trial-first / reviews-first), a specific time
budget ("25 minutes tonight, after the kids are down"), budget authority, their
alternative if this fails, and 3–5 personal heuristics stated as tripwires ("if the
quickstart doesn't work first try, I'm out").

Every trait carries its source. Rotate the lens across runs — check the platform's
`runs.md` and pick a persona that stresses a different path than last time (a skeptic
after a champion; a buyer after a builder; a mobile-only user after a desktop one).

**The card also carries economics**, because the value math in Phase 3 is arithmetic on
these fields and nothing else: monthly volume of the relevant unit; the cost of one bad
outcome of the type they fear; how often they'd expect it without the product; the cost of
one false alarm or wrong call by the product; hours to integrate; what an hour of theirs
is worth; and the price of the tier they'd actually buy. Same evidence trail as every
other trait. A field with no defensible source is left empty and the math says so — a
plausible invented number is the one failure mode that discredits a whole report.

**Then set the value weights, before walking.** Pick the 8–10 pyramid elements this
persona prices and weight each 0–3 from their heuristics and their trigger incident.
Write them down now. Weights chosen after the walkthrough only rationalize what it found.

## Phase 2 — The walkthrough

Time-boxed to the persona's budget, in a browser, with a running log. For each step
record: **stage → what I did → what I expected → what actually happened → verdict**
(delight / fine / friction / exit-risk) → **confidence (0–100) → the unedited inner
thought**. Screenshot at the three moments that matter: first impression, first confusion,
first success.

The last two columns are the confidence trace, and they are only worth anything if written
**at the moment**, before the next step is taken. A curve reconstructed at write-up is a
story about the verdict rather than evidence for it. Where the curve peaks is where the
call to action belongs; where it falls off a cliff is the fix.

The spine below is universal; `references/archetypes.md` supplies the decisive probes for
this platform's type. Follow the persona's instincts over both.

1. **Arrival** — a 10-second read. What do they think this does? Would they scroll?
2. **Their path** — wherever their evaluation style sends them next, not where the site
   wants them to go.
3. **Activation** — the attempt at first real value. Time it: from "decided to try" to
   the moment value lands. That number, **time-to-first-value**, is the walkthrough's
   headline metric. The archetype defines what counts as value.
4. **Depth check** — the one page or feature their decision actually hinges on.
5. **Money math** — their real volume against the tiers; catch the moment of sticker
   interpretation. Then price the ladder while the sticker is in front of them: what
   would feel suspiciously cheap, what feels fair, what makes them hesitate, what is out
   of the question — and what would have justified the next tier up. Cards state the
   floor ("under my coffee budget") and almost never test the ceiling.
6. **Trust check** — whatever their org requires: data handling, retention, security
   page, compliance claims, who else uses it, does the company look alive.
7. **The wall** — where the access model stops them. Does the page explain what's past
   it? Is the ask proportionate to what they've seen so far?
8. **The audience** — who they'd have to explain this purchase to, and the exact sentence
   they'd use. Ask it as a question the persona answers, not as analysis about them.
9. **Exit decision** — place them on the rung ladder and name the single change that
   moves them up one:
   **1** bounced · **2** left unconvinced · **3** bookmarked · **4** signed up or
   started a trial · **5** would pay or adopt.
   Price the option they actually took, including do-nothing, whose price is zero and
   whose cost is the full exposure. A run that hasn't priced do-nothing hasn't explained
   the loss — and do-nothing wins most walkthroughs.

Capture along the way: every 404, every broken snippet, every claim from the ledger that
came back unverifiable, every dark pattern, and every moment of real delight — those
matter as much, because they tell marketing what to amplify.

Four extra things to log as they happen, because none of them can be recovered afterwards:

- **Beliefs.** When the persona changes their mind about the category, the product, or
  their own risk, write down the old belief and the artifact that moved it. At the end,
  list the beliefs that were never tested — usually the report's most useful column.
- **Objections.** Resolve each standing objection from the dossier to one of three states:
  answered · **answered but not found** · absent. The middle state is a navigation bug and
  gets confused for the third one constantly; only a live log can tell them apart.
- **Value evidence.** When a step proves or disproves one of the weighted pyramid
  elements, tag the log line with that element. Phase 3 fills the *delivered* column from
  these tags, so an untagged run has to score from memory.
- **Rates, with n.** Every probe of the thing the product promises goes in the tally, hits
  and misses both. Report them as "3 of 4", never as a percentage — four probes is not a
  rate, and the report has to say so in the same sentence.

Verify before you accuse. Re-run anything load-bearing to confirm it's deterministic, and
separate "limit of the free tier" from "gap in the product" in every negative finding. An
overclaimed report gets dismissed; one that states the caveat inline gets acted on.

## Getting past the card field (our own product only)

Most walkthroughs die at the payment form, so everything behind it goes unexamined —
the success page, the entitlement grant, the billing dashboard, the portal, cancelling,
downgrading. That is often where the worst defects live, precisely because nobody walks
it. On a product we own, two mechanisms open it without faking anything. On a third
party's, neither exists: the paywall is the end of the walkthrough, full stop.

**A test-mode replica (default).** Run the product against the payment provider's test
mode, on its own database and its own port, with webhooks forwarded to it. Purchases
cost nothing and touch no production state, so a run can buy repeatedly and reset
between actors. Prefer this whenever the question is "what happens after payment."

**An owner-issued full-discount code (when the evaluation must happen on the live
site).** Mint a single-use 100%-off code, scoped to the products being evaluated, with a
short expiry. The persona walks the real funnel and pastes it like any customer with a
promo in their inbox.

Whichever you use, these hold:

- **Never fake payment details, and never charge a real card without the operator
  saying so.** A test card belongs only in test mode. If the only way through is real
  money, stop and ask.
- **A full discount usually removes the card form entirely**, because a provider that
  expects no future charge stops asking for a payment method. That is what makes this
  work without a card — and it also means the card form itself goes unwalked, so say so
  when it could matter to a finding.
- **Tear down what the run created.** A fully-discounted subscription is still an active
  subscription in the owner's revenue reporting, and a test organization with no delete
  endpoint is permanent. Know before you start which artifacts you can remove and which
  you cannot; the ones you cannot are a reason to prefer the replica.
- **Say which host produced each finding.** Latency from a local replica is not
  comparable to production, and a defect seen only there needs re-checking against the
  live site before it becomes a ticket.
- **Environment setup is an operator step, not a persona step.** Starting the replica or
  minting a code means touching the repo, which would contaminate the persona. Prepare it
  first, then hand the walkthrough nothing but a base URL and a code.

Worked example: `parse-prospect`, which carries the concrete scripts for both paths.

## Phase 3 — The report (HTML)

**Voice: write the whole report in first person, as the persona.** Not a study of a
prospect — the prospect's own account. "I ran the quickstart curl and it 404'd," never
"she ran the quickstart and it 404'd." First person singular, past tense, throughout.

This is a discipline, not a style preference. Third person lets the writer drift back
into the builder's head and start explaining why a thing is the way it is; first person
makes that drift audible, because the persona has no idea why. If a sentence can't be
said by someone who has never seen the codebase, it doesn't belong in the report.

How it lands per section:

- **Persona card** — a self-introduction. "I run platform at a 40-person fintech. I
  have twenty minutes and I've already rejected two vendors this quarter." Keep the
  evidence trail for each trait, but as a separate annotation, not in the voice.
- **Journey map, likes and dislikes, claim ledger, verdict** — all the persona speaking.
  Verdicts stay blunt: "this is where I would have left."
- **Recommendations** — the one place to shift register, because the audience changes.
  Frame each as what would have changed the persona's mind ("what would have kept me"),
  then state the fix plainly and directively so it can become a ticket. Keep the
  imperative — "Correct the retention sentence on /trust" — inside a first-person frame.
- **Scorecard and tables** — data, not voice. Leave them neutral.

Two guardrails. Never invent biography to fill the voice — everything the persona says
about their world traces to the persona card, which traces to research. And when the
persona is an archetype composite rather than a real named person, say so plainly on the
card; first person makes a report read as testimony, so who is testifying must be honest.

Sections:

- **Persona card** — who walked, with the evidence trail per trait, economics included.
- **Journey map** — the stage/did/expected/actual/verdict table plus the confidence trace
  and inner thoughts, screenshots inline as data URIs, real payloads and latencies.
- **Platform map** — every surface touched, its job, its state (works / friction /
  broken).
- **What I believed, and what changed it** — the belief ledger, ending with the beliefs
  nothing tested.
- **Value ladder** — the weighted pyramid rows: weight, delivered (with a walkthrough
  receipt), communicated (scored from where the persona actually went), the alternative,
  and the one-word diagnosis per row. Close with the two summary reads: pitch altitude vs
  decision altitude, and the unsold asset. Rules in `references/value-pyramid.md`.
- **Does it pay for me** — the value math table, the break-even sentence in the persona's
  voice, and the same math for the alternative and for doing nothing. Every observed rate
  carries its n in the same sentence.
- **My objections** — each resolved to answered / answered but not found / absent.
- **Who I'd have to explain this to** — the audience and the sentence they'd use.
- **Claim ledger results** — claim, probe, verdict (held / unverifiable / contradicted).
- **Likes and dislikes** — each with a receipt. No vibes without evidence.
- **Scorecard** — 1–5 on first impression, time-to-first-value, docs or help quality,
  pricing clarity, trust signals, and competitive standing, plus any archetype extras.
  Score the persona's alternative in a parallel column.
- **Recommendations** — ranked by conversion impact against build effort, each concrete
  enough to become a ticket, tagged with the journey moment it fixes **and the value
  ladder row it moves**. Copy-debt rows are a day's work and belong at the top; product
  gaps are a quarter and belong further down however loudly they were felt.
- **The verdict** — which rung, the one change that moves them up, the price ladder if the
  run was revenue-aimed, and what I'd tell a peer in one paragraph.

Style: sample the platform's own palette and fonts so the team reads it as a native
document (the template is CSS-variable driven for exactly this). Self-contained — inline
CSS, no CDNs. Head it with a line stating it's an independent prospect walkthrough, and
don't reproduce a third party's logo in a way that reads as their own document.

Save to `~/reports/prospect/<platform-slug>/<date>-<persona-slug>.html` and offer to
publish it as an artifact for sharing.

## Phase 4 — Persist

1. Update `~/reports/prospect/<platform-slug>/dossier.md` with what the walkthrough
   corrected. The dossier is the reason run 2 costs a fraction of run 1.
2. Append one line to that folder's `runs.md`: date — persona — report path — rung —
   headline finding.
3. Append this run's column to `~/reports/prospect/<platform-slug>/value-pyramid.md`,
   cells as `weight/delivered/communicated`. One report is an anecdote; the same elements
   scored across personas is an instrument. Read the rollup before writing the
   recommendations — an element delivered and unsold in *every* run is the cheapest
   revenue in the product, and a weight-3 row that stays red across different personas is
   a roadmap item rather than a persona quirk.
4. Lessons about **this platform** go in the dossier. Lessons about **the method** go in
   `references/field-notes.md` — read it at the start of Phase 2.
5. If we own the platform, update the brain project page and append to
   `~/brain/log.md`.

## Working files

```
~/reports/prospect/<platform-slug>/
  dossier.md                      # Phase 0, updated each run
  runs.md                         # one line per run, drives persona rotation
  value-pyramid.md                # cross-run element scores, one column per run
  <date>-<persona-slug>.html      # the report
  screens/                        # raw screenshots before they're inlined
```

Check for an existing dossier before starting: if one exists, Phase 0 becomes a refresh —
re-probe the surface, re-check pricing and the access model, diff against what's recorded.

## Tooling

- Browser: Playwright MCP or Claude-in-Chrome. Screenshot at the persona's viewport —
  use a phone viewport when the persona is mobile-first.
- `scripts/surface-probe.sh <url>` — status, redirect, content type, size, and title
  across the standard route set; also lists `sitemap.xml` entries. Fast way to find 404s,
  orphan pages, and machine surfaces.
- `curl -w` for API timings; `jq` for response bodies.
- Embed screenshots as JPEG data URIs at q85–90 — a three-shot report lands near 600KB
  and stays self-contained.
