# Tests — deepthink-loop-reasoning

Manual checklist. Each item has a concrete pass condition. Run each prompt against the installed agent and inspect the raw response.

1. **Install/backup:** With a dummy file already at `<SKILL_DIR>/SKILL.md`, run the install block from commands.md. Pass: `ls <SKILL_DIR>/SKILL.md.bak.*` shows exactly one backup file, and `head -5 <SKILL_DIR>/SKILL.md` shows `name: deepthink-loop-reasoning` in frontmatter.

2. **Output format:** Send: "Use deepthink to reason through whether to choose Next.js API routes or a separate backend for a small SaaS." Pass: the response contains, verbatim and in order, the headings `# DeepThink Analysis`, `## Problem`, `## Depth Applied`, `## Reasoning Journey`, `## Conclusion`, `## Key Insights`, `## Remaining Uncertainties`, `## Recommendations`. Fail if any heading is missing or out of order.

3. **Per-loop restatement:** Same response as test 2. Pass: the `## Reasoning Journey` section contains at least 3 subsections matching `### Loop`, and each loop subsection contains the string `Problem restated:`. Fail if any loop lacks it.

4. **Cross-loop integration:** Same response as test 2. Pass: at least one loop after Loop 1 contains one of the words "confirm", "contradict", or "refine" referring to an earlier loop, plus a statement of convergence or divergence.

5. **Remaining Uncertainties always present:** Same response as test 2. Pass: the `## Remaining Uncertainties` heading exists in every run. If convergence was clean it may say "None — convergence reached at loop N"; if unresolved it must list at least one specific gap. Fail if the section is absent.

6. **Trivial-task bypass:** Send: "What time is it in UTC right now?" Pass: the response does NOT contain `# DeepThink Analysis` — the skill correctly declines simple lookups.

7. **Depth default:** Same response as test 2. Pass: `## Depth Applied` reports between 3 and 4 loops at Standard depth. (Note: this is a convention check on the reported value, not an enforced ceiling; a report of 5+ loops at Standard depth is a fail, escalation to Deep requires reported divergence in the loop trace.)