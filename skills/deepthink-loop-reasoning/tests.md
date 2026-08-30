Manual checklist for `deepthink-loop-reasoning`:

1. **Loop restatement present.** Give the agent a non-trivial architecture question. Confirm the output's Reasoning Journey begins each loop subsection with a one-sentence restatement of the original problem (`[LOOP N] Problem restated: ...` or equivalent).
2. **Output format matches spec.** Confirm the output contains exactly these sections: Problem, Depth Applied, Reasoning Journey, Conclusion, Key Insights, Remaining Uncertainties, Recommendations.
3. **Default depth is Standard.** Ask a normal architecture question with no depth directive. Confirm the agent runs 3–4 loops, not 7+, and states the depth level in "Depth Applied".
4. **Skip case works.** Ask a simple factual lookup ("default Postgres port?"). Confirm the agent answers directly without loop structure.
5. **Evidence weighting present.** Confirm the conclusion includes the strongest evidence, the weakest assumption, and what would make the conclusion wrong.
6. **Devil's advocate bias.** Say "devil's advocate this: <plan>". Confirm the reasoning is weighted toward challenge/contradiction and states the strongest opposing argument before concluding.