# Verification Subagent Prompt Template

Use this template when an implementer claims test results - verify independently before accepting.

**Purpose:** Independent verification of test results using evidence-before-assertions principles

**Dispatch after implementer reports test results, before proceeding to reviews.**

```
Task tool (general-purpose):
  description: "Verify test results for Task N: [task name]"
  prompt: |
    You are verifying test results claimed by an implementer.

    ## What Was Implemented

    [Summary of what implementer built]

    ## What Implementer Claims

    [Implementer's test report - e.g., "5/5 tests passing"]

    ## CRITICAL: Do Not Trust the Report

    The implementer may be mistaken, optimistic, or may have run tests incorrectly.
    You MUST verify independently.

    ## Your Job

    Run the tests yourself and provide actual evidence.

    1. **Identify the test command** - What command should be run?
    2. **Run the FULL command** - Execute it completely
    3. **Read the FULL output** - Check exit code, count failures
    4. **Verify the claim** - Does output match what implementer said?

    ## Report Format

    Report exactly what you observed:

    **Command run:**
    [The exact command you executed]

    **Full output:**
    [Paste the actual output, including exit code if available]

    **Verification result:**
    - ✅ Claim confirmed - output matches implementer's report
    - ❌ Claim incorrect - actual results differ: [describe difference]

    **If claim is incorrect:**
    - What implementer claimed vs. actual results
    - Which tests failed (if any)
    - Recommendation on how to proceed
```

**Verification subagent returns:** Command executed, full output, confirmation whether claim matches reality.
