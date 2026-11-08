# Tests

Manual checklist for a reviewer.

1. **Reading happened first.** Ask the agent for a one-sentence description of the data flow it traced before implementing. If it cannot name the entry point and where data lands, the rung choice is invalid.
2. **Rung discipline.** Review the reply: the chosen rung is stated, and the rungs below it (need / codebase / stdlib / platform / installed dep / one line) were each explicitly considered or searched. Verify rung 2 with `rg -ni "<solution-name>" .` returning nothing that was ignored.
3. **No new dependencies.** Run `git diff package.json requirements.txt go.mod` (as applicable). A new dependency must be justified by exhausting rungs 2–6; flag any unjustified addition.
4. **Non-negotiables intact.** In the diff, confirm input validation at trust boundaries, error handling for data loss, security checks, and accessibility attributes (labels/ARIA on new UI) are present, not stripped.
5. **Test for risky logic.** If the change touches a branch, loop, parser, money, or security, a test exists in the diff and `<TESTCMD>` passes on a clean run.
6. **Closing report present.** The reply ends with "Skipped:" / risk lines; every deliberate deferral appears as a `shortcut:` comment in code, findable with `rg -n "shortcut:" .`.