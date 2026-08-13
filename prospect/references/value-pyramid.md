# Value pyramid — pricing the product in the persona's head

The journey table records **what happened**. This file records **how the persona priced
it**. Without it a report ends in a rung and a score with no economic reasoning behind
them, and the team cannot tell a copy bug from a product gap.

Adapted from Bain's *Elements of Value* (B2C, 2016) and *B2B Elements of Value* (2018).
Trimmed to what a self-serve walkthrough can actually observe, with a few elements added
that the originals don't name. Not a faithful reproduction — don't cite element counts.

Used by the `prospect` and `parse-prospect` skills. Read it in Phase 1 (to set weights)
and again in Phase 3 (to score).

---

## 1. The levels

Higher is harder to copy and harder to say out loud. Most products pitch low and get
bought high — finding that gap is the point of the instrument.

### B2B ladder (default for tools, APIs, platforms, anything expensed)

| Level | Elements |
|---|---|
| **Table stakes** | meets the spec · acceptable price · regulatory compliance · ethical standards |
| **Functional** | improved top line · cost reduction · product quality · scalability · innovation |
| **Ease of doing business** | *Productivity:* time savings · reduced effort · decreased hassles · information · transparency<br>*Operational:* organization · simplification · connection · integration<br>*Access:* availability · variety · configurability<br>*Relationship:* responsiveness · expertise · commitment · stability · cultural fit<br>*Strategic:* risk reduction · reach · flexibility · component quality<br>*Added:* reversibility (can I leave in two clicks?) · legibility (can I tell what it did and why?) |
| **Individual** | network expansion · marketability · **reputational assurance** · design and aesthetics · growth and development · **reduced anxiety** · fun and perks<br>*Added:* blame transfer (if it goes wrong, is it now someone else's fault?) |
| **Inspirational** | purpose · vision · hope · social responsibility |

The two bolded elements decide more self-serve B2B purchases than any functional one.
They are also the two that almost no vendor writes down.

### B2C ladder (consumer subscriptions, shops, apps)

| Level | Elements |
|---|---|
| **Functional** | saves time · simplifies · makes money · reduces risk · organizes · integrates · connects · reduces effort · avoids hassles · reduces cost · quality · variety · sensory appeal · informs |
| **Emotional** | reduces anxiety · rewards me · nostalgia · design and aesthetics · badge value · wellness · therapeutic value · fun and entertainment · attractiveness · provides access |
| **Life changing** | provides hope · self-actualization · motivation · heirloom · affiliation and belonging |
| **Social impact** | self-transcendence |

Pick one ladder. Mixed targets (a developer tool sold to a solo founder's own card) use
B2B and note the personal-money distortion on the card.

---

## 2. The scoring rules

**Score 8–10 elements, never all of them.** The ones this persona actually priced. An
element nobody weighed is noise, and a 40-row table gets skimmed.

Four columns per element, three of them 0–3:

| Column | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Weight** — how much it decided this persona's verdict | irrelevant | nice to have | would argue about it | deal-maker or deal-breaker |
| **Delivered** — what the walkthrough proved | absent or broken | partial, or only under conditions | works as needed | better than the alternative, provably |
| **Communicated** — could the persona find out? | nowhere on the site | buried: one list item, or a page they'd never reach | stated on a page they visited | led with — hero, nav, or pricing card |
| **Alternative** — what their fallback gives them | absent | partial | works | better |

**Set the weights in Phase 1, before the walkthrough.** They come from the persona card's
heuristics and the incident that brought them, and they get written down before anything
is measured. Weights assigned after the fact just rationalize whatever the run found.

**Delivered scores cite the walkthrough, not the marketing.** A receipt is a response
body, a screenshot, a latency, a click that worked. "The page says it does" is a
*communicated* score of 2 and a *delivered* score of unknown — write `?`, not a guess.

**Communicated is scored from where the persona actually went.** A brilliant page they
never reached scores 1, and that is the finding. Cross-check against the journey table:
if they never loaded the URL, it cannot score above 1.

---

## 3. Reading the table

Each row's three scores produce one diagnosis. This is the column that turns the report
into tickets.

| Pattern | Diagnosis | What it costs to fix |
|---|---|---|
| delivered ≥2, communicated ≤1 | **Copy debt** — you built it and nobody knows | a day |
| delivered ≤1, weight ≥2 | **Product gap** — the real kind | a quarter |
| communicated ≥2, delivered ≤1 | **Overclaim** — the trust hit; cross-file it in the claim ledger | a day, plus the credibility already spent |
| all three ≥2 | **Parity** — true and useless; no reason to switch lives here | find the differentiator elsewhere |
| alternative > delivered, weight 3 | **The loss** — this row is why they didn't buy | this is the roadmap |
| weight 3, communicated 3, delivered 3 | **The pitch** — lead with this everywhere | protect it |

Then two summary reads:

**Pitch altitude vs decision altitude.** Which level does the site's copy concentrate on
(weight the hero, nav and pricing cards heavily — that's what a stranger meets), and which
level holds the persona's weight-3 rows? State it in one sentence: *"Pitched at
Functional, decided at Individual."* When those differ, the gap is the report's headline
and no feature work fixes it.

**The unsold asset.** The highest-delivered row with the lowest communicated score. Name
it, quote where it currently appears, and say where it should appear instead.

---

## 4. The value math

The pyramid says *which* value. This says *how much*, in the persona's own numbers. It
is the direct answer to "are we worth it to this person."

**It requires the persona card to carry economics.** No number, no math — an empty cell
beats an invented one, and inventing here destroys the report's credibility faster than
any wrong verdict. Required fields, each with the same evidence trail as every other
persona trait:

| Field | Symbol | Notes |
|---|---|---|
| Volume of the relevant unit per month | V | requests, orders, tickets, sessions |
| Cost of one bad outcome of the type they fear | C_bad | money + their time + the relationship |
| How often they'd expect it without the product | P_bad | as they'd say it: "one every N months" |
| Cost of one false alarm / wrong call by the product | C_fp | often higher than C_bad — ask, don't assume |
| Hours to integrate | H | their estimate after reading the docs |
| What an hour of theirs is worth | R | salary-derived, or founder opportunity cost |
| Price of the tier they'd actually buy | Price | per month |

Then, from the walkthrough's own probes:

| Field | Symbol | Guardrail |
|---|---|---|
| Hit rate — how often it did the thing it promises | D | **state n.** 4 probes is not a rate. Write "3 of 4" and say so in the report |
| False-alarm rate | FP | same guardrail, same sentence |

The arithmetic, shown in the report as a table so a reader can dispute any line:

```
Annual exposure       = P_bad × C_bad
Annual benefit        = D × annual exposure
Year-one cost         = 12 × Price  +  H × R  +  (12 × V × FP × C_fp)
Break-even            = the P_bad at which benefit = cost
```

Ship it as one sentence in the persona's voice: *"This pays for itself if it stops one
incident every N months. At the false-alarm rate I saw, it costs me more than that in
lost customers."* If the false-alarm term dominates the price term, say so loudly — that
is a product decision disguised as a pricing page.

**Do the same math for the alternative,** including the do-nothing option, whose price is
zero and whose cost is the full exposure. Most walkthroughs end at do-nothing, and a
report that hasn't priced do-nothing hasn't explained the loss.

---

## 5. The other four instruments

Small, cheap, and they carry most of the "what were they thinking" signal.

**Confidence trace.** Two extra columns on the journey table — a 0–100 reading of how
likely the persona is to buy at that moment, and their unedited inner thought. **Recorded
live, never reconstructed at write-up**: a curve drawn from memory is a story about the
verdict, not evidence for it. The shape is the deliverable — where it peaked is where the
CTA belongs; where it fell off a cliff is the fix.

**Belief ledger.** Three columns: what I believed walking in (about the category, the
product, and my own risk), what changed it, and what never got tested. The untested rows
are usually the most useful thing in the report — they are the beliefs the site left to
chance.

**Objection ledger.** The category's standing objections from the dossier, each resolved
to one of three states, not two: **answered** (found it, believed it) · **answered but not
found** (it exists, the persona never reached it — a navigation bug) · **absent**. Blurring
the middle state into the third sends the team to build something they already have.

**The audience.** Who the persona would have to explain this purchase to — a co-founder,
a security reviewer, the boss who asked "are we covered?", the customer owed an apology —
and the exact sentence they'd use. That sentence is where reputational assurance lives,
and it usually comes back as pasteable site copy.

Optional, worth it when the run is about revenue rather than product feedback:

**Price ladder.** Four points in the persona's voice: what price would feel suspiciously
cheap, what feels fair, what makes them hesitate, and what is out of the question. Then:
what would have justified the next tier up? Persona cards routinely assert the floor
("$12 is below my think-about-it line") and never test the ceiling.

**Switching and staying costs.** What they'd rip out, who they'd have to tell, what it
costs to leave, and what the status quo genuinely gives them. Most losses go to
no-decision, not to a competitor.

**What I'd tell a peer.** One paragraph they'd post in a team channel. It's the honest
compression of perceived value, and it's a free word-of-mouth test.

---

## 6. The cross-run rollup

One report is an anecdote. The same elements scored the same way across personas is an
instrument — and it is the reason to standardize the scoring at all.

After each run, append to `~/reports/prospect/<platform-slug>/value-pyramid.md`
(`~/reports/parse-prospect/value-pyramid.md` for the fixed-target skill): one column per
run, one row per element, cells as `weight/delivered/communicated`.

Read it for elements that are **delivered and unsold in every run** — those are the
cheapest revenue in the product — and for weight-3 rows that stay red across different
personas, which is a roadmap item rather than a persona quirk. Note in the rollup which
runs predate the instrument; do not back-fill scores for runs that didn't measure them.

Skeleton for run 1 — add rows as personas price elements the list doesn't carry yet:

```markdown
# <Platform> — value pyramid rollup

Cells are `weight/delivered/communicated`, each 0–3. Rules:
~/.claude/skills/prospect/references/value-pyramid.md

| Element | Level | <persona 1> | <persona 2> |
|---|---|---|---|
| Product quality — it does the thing | Functional | 3/2/3 | |
| Acceptable price | Table stakes | | |
| Risk reduction | Strategic | | |
| Decreased hassles — getting started | Productivity | | |
| Stability — still working next month | Relationship | | |
| Reversibility — I can leave | Added | | |
| Reduced anxiety | Individual | | |
| Reputational assurance | Individual | | |

Per run, one line: pitch altitude vs decision altitude · the unsold asset ·
the break-even sentence · rung.
```

`~/reports/parse-prospect/value-pyramid.md` is the worked example, including how to
handle runs that predate the instrument.
