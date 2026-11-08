---
name: minimal-code-solution-ladder
description: Solve a coding task by reading the affected code first, then choosing the minimal solution via a reuse ladder (need/exists/stdlib/platform/installed dep/one line/minimum), leaving one small test for risky logic, and reporting what was skipped.
category: product-building
---
```

# Minimal Code Solution Ladder

## Goal

Write the minimum code a coding task actually needs. Read the affected code first, climb a reuse ladder stopping at the first rung that holds, never cut validation, error handling, security, or accessibility, leave one small test behind for risky logic, and end with an explicit report of what was skipped and what risk remains.

## Inputs

- A coding task or change request (issue text, message, or spec).
- The target repository on disk, with read access to its source files, dependency manifests, and test runner.
- No API keys or external services required. Web access only if the task itself demands it.

## Steps

1. Read the code the change touches before writing anything. Use `grep`/`rg` to locate relevant functions, components, and entry points; open the affected files; trace the real data flow from entry point to storage/response. Write down the flow in one or two sentences so the rung choice is grounded, not guessed.
2. Climb the ladder, stopping at the first rung that holds:
   1. Does this need to exist at all?
   2. Is it already in this codebase (search for existing utils, components, helpers)?
   3. Does the standard library do it?
   4. Does a native platform feature do it (e.g. browser-native `<input type="date">` instead of a hand-built calendar)?
   5. Does an already-installed dependency do it (check `package.json` / `requirements.txt` / `go.mod` etc., not new installs)?
   6. Can it be one line?
   7. Only then write the minimum that works.
3. Implement the chosen solution. Never cut trust-boundary validation, data-loss handling, security, or accessibility, regardless of pressure to minimize code. Prefer composing existing pieces (e.g. the repo's `Input` component plus a browser-native date input) over new abstractions.
4. If the logic contains a branch, loop, parser, money handling, or security, write one small test for it and run the project's test command to confirm it passes.
5. End the reply with what was skipped or not checked and any known risk. Mark deliberate deferrals inline as `shortcut:` comments (with when to revisit) so they can later be harvested into a debt ledger.

## Outputs

- A minimal working code change in the repository.
- One small test for risky logic, run and passing (if applicable).
- A closing report: rung chosen, what was skipped or not checked, and known risks.

## Failure modes

- Cutting validation, security, or accessibility under pressure to minimize code. The rule is "write only what the task needs," never "fewest tokens."
- Skipping the code-reading step and picking a ladder rung blind; the ladder runs after understanding the problem, not instead of it.
- `shortcut:` comments accumulating into untracked debt — harvest them into a ledger periodically.
- Adding a new dependency when rungs 2–6 (codebase, stdlib, platform, installed dep, one line) had not been exhausted first.

## Source

Ponytail (DietrichGebert/ponytail), https://github.com/DietrichGebert/ponytail — README "How it works" ladder and FAQ; `examples/debounce.md`, `examples/csv-sum.md`. Referenced 2026-11-08.