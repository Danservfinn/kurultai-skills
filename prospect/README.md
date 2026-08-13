# prospect

Walk any platform as a realistic prospect and write down what happened.

Pick a target, learn it cold, send one believable buyer through it, and deliver
an HTML report with a scorecard, a claim ledger, value math in the persona's own
numbers, and prioritized fixes. Works on a developer tool, a SaaS app, a
consumer subscription, a marketplace, a shop, an open-source project, or a
competitor.

The value of the skill is honesty: the persona's patience, budget and skepticism
decide every judgment — not what you know about how the product works.

## Two variants

| | Path | Runtime |
|---|---|---|
| Claude Code | `SKILL.md` + `references/` + `scripts/` | Claude Code skills |
| Hermes | `hermes/SKILL.md` | Hermes agent |

Same method, different tooling. The Claude variant ships reference material the
run reads mid-flight — archetypes, a value pyramid, a dossier template, a report
template, accumulated field notes. The Hermes variant is self-contained and uses
native Hermes tools (`browser_navigate`, `browser_vision`, `terminal`,
`web_search`, `delegate_task`, `write_file`).

## Install

**Claude Code**

```bash
cp -R prospect ~/.claude/skills/prospect
```

**Hermes**

```bash
mkdir -p ~/.hermes/profiles/<profile>/skills/business/prospect
cp prospect/hermes/SKILL.md ~/.hermes/profiles/<profile>/skills/business/prospect/
```

## What makes it different from a generic audit

**Phase 0 is a gate, not a warm-up.** You may not write a persona until the
dossier answers what the product is, who owns it, what its surface looks like,
where the access wall sits, what it costs, and what the outside view says. A
walkthrough of a product you misread produces confident nonsense.

**The persona is derived, not invented.** Every trait traces to a source. Where
the vendor's copy and the market disagree, the market wins.

**It prices the product, it doesn't just rate it.** Every run scores the value
pyramid and does the arithmetic in the persona's own numbers, with element
weights fixed before the walkthrough so the result cannot be retrofitted.

**It refuses to fake its way in.** No paywall bypass, no invented identities, no
fake payment details. On a product you own there is a legitimate route past the
card field — a test-mode replica, or an owner-issued full-discount code — with
teardown discipline attached. On someone else's, the wall is where the
walkthrough ends, and that is a finding rather than a failure.

## Output

`~/reports/prospect/<target-slug>/<date>-<persona-slug>.html` — one
self-contained file, written first person as the persona, with screenshots and
real response bodies inline.
