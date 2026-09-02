# Tests — deepthink-loop-reasoning

Manual checklist for a reviewer:

1. **Restatement invariant:** feed the skill an architecture question and inspect the output. Every `### Loop N` section must begin with `[LOOP N] Problem restated: ...` containing a faithful one-sentence restatement of the original question. Fail if any loop omits it.
2. **Section completeness:** the output contains exactly these headings: `# DeepThink Analysis`, `## Problem`, `## Depth Applied`, `## Reasoning Journey`, `## Conclusion`, `## Key Insights`, `## Remaining Uncertainties`, `## Recommendations` (last two contextually optional per the spec, others mandatory).
3. **Gate rejection:** ask "what time is it?" — verify the skill does NOT produce a DeepThink Analysis.
4. **Depth default:** run a standard architecture question; `## Depth Applied` should report 3-4 loops / Standard, not 7+.
5. **Convergence check is substantive:** in a 4-loop output, at least one loop's convergence statement references a concrete signal (e.g., "conclusion reinforced from X and Y angles, no new contradictions"), not a bare "done".
6. **Install verification:** after running the install commands, `hermes skills list | grep -i deepthink` returns a match, and the smoke-test chat prompt returns a looped analysis.