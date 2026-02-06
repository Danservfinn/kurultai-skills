# Fix Subagent Prompt Template

Use this template when an implementer subagent has failed a task and needs systematic recovery.

**Purpose:** Fix failed implementations using root cause analysis from systematic debugging

**Only dispatch after root cause investigation using systematic-debugging.**

```
Task tool (general-purpose):
  description: "Fix failed Task N: [task name]"
  prompt: |
    You are fixing a failed implementation attempt.

    ## Original Task

    [FULL TEXT of task from plan - paste it here]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## What Implementer Tried

    [From implementer's report or commit]

    ## Root Cause Analysis

    [From systematic-debugging investigation - include specific findings]

    ## Your Job

    Fix the implementation based on the root cause analysis. Important:

    1. **Don't retry the same approach** - The previous attempt failed for a reason
    2. **Address the root cause** - Use the findings from the investigation
    3. **Learn from the failure** - Avoid making the same mistake
    4. **Follow the same workflow** - Implement, test, commit, self-review, report

    Work from: [directory]

    ## Before Reporting Back: Self-Review

    Review your fix with fresh eyes. Ask yourself:

    **Root cause addressed:**
    - Did I actually fix the identified root cause?
    - Or just treat symptoms?

    **New issues introduced:**
    - Did my fix create new problems?
    - Are edge cases handled?

    **Verification:**
    - Can I demonstrate the fix works?
    - What evidence confirms success?

    ## Report Format

    When done, report:
    - What you changed (summary)
    - How the fix addresses the root cause
    - What you tested and test results
    - Files changed
    - Any remaining concerns
```

**Fix subagent returns:** Summary of changes, how root cause was addressed, test results, files changed, any concerns.
