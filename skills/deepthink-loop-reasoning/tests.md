# Tests — Manual Checklist

All assertions are mechanically checkable against the output document (`<OUTPUT_FILE>`).

## Setup

Run the skill on a non-trivial problem, e.g. "Should we use Postgres or SQLite for a single-server internal tool with 5 users?" Save output to `deepthink-analysis.md`.

## Assertions

1. **Gate check works.** Ask a trivial question ("what is the exit code of `grep foo missing.txt`?"). Assert the response does NOT contain the string `DeepThink Analysis`:
   ```bash
   # run the trivial question, capture output to trivial.md, then:
   ! grep -q "DeepThink Analysis" trivial.md
   ```

2. **Output structure present.** All required section headers exist:
   ```bash
   for h in "## Problem" "## Depth Applied" "## Reasoning Journey" "## Conclusion" "## Key Insights"; do
     grep -q "^$h$" deepthink-analysis.md || echo "MISSING: $h"
   done
   ```

3. **Every loop restates the problem.** Each loop heading is followed by a restatement line:
   ```bash
   grep -c "^\[LOOP [0-9]\+\] Problem restated:" deepthink-analysis.md
   # must equal the loop count reported under "## Depth Applied"
   ```

4. **Depth cap respected without user direction.** With no depth specified, the Depth Applied line reports ≤ 6 loops:
   ```bash
   grep -E "^[0-9]+ loops" deepthink-analysis.md | awk '$1 <= 6 {found=1} END {exit !found}'
   ```

5. **Devil's Advocate emits the opposing argument.** Run with input "Devil's advocate this: <claim>". Assert the literal marker appears:
   ```bash
   grep -qi "strongest version of the opposing argument\|opposing argument" deepthink-analysis.md
   ```

6. **Install verification is honest.** If the install step was used, confirm the backup logic and that no unverified CLI was required:
   ```bash
   ls -l <SKILL_DIR>/SKILL.md
   # and confirm the skill was verified via file inspection (head -5), not via an unconfirmed `hermes` subcommand