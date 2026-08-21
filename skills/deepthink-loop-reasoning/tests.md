# Tests — deepthink-loop-reasoning

Manual checklist. Run each by prompting an agent that has this skill loaded.

1. **Trigger test:** Ask "think deeper about whether to use Postgres or DynamoDB for our event log." Confirm the response contains the sections Problem, Depth Applied, Reasoning Journey, Conclusion, Key Insights, Remaining Uncertainties, Recommendations.
2. **Anti-trigger test:** Ask "what time is it in Tokyo?" Confirm the response does NOT contain a DeepThink loop structure — a direct answer is correct behavior here.
3. **Drift-prevention test:** Give a multi-part architecture question. Check that every loop in Reasoning Journey begins with a one-sentence restatement of the original problem, and that the restatement matches the original question.
4. **Evidence-weighting test:** Confirm the output states (a) the strongest piece of evidence for the conclusion, (b) the weakest assumption, and (c) what would make the conclusion wrong.
5. **Convergence test:** On a Standard-depth problem, confirm the agent stops at 3-4 loops unless it explicitly reports divergence signals (new contradictions, challenged assumptions) — and that if it escalates, Loop 5+ follows the Breakout/Re-Challenge/Final-Synthesize procedure from Step 7.
6. **Install test:** After running the install command from commands.md, run `ls <AGENT_SKILLS_DIR>/deepthink-loop-reasoning/` and confirm all four files (SKILL.md, examples.md, commands.md, tests.md) are present.