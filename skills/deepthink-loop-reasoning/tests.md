# Manual Verification Checklist

1. **Install works:** run `mkdir -p ~/.hermes/skills/deepthink && cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md`, then `hermes skills list | grep -i deepthink` — output is non-empty.
2. **Functional trigger:** run `hermes chat -q "Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS."` — the response contains loop sections (Surface/Explore/Challenge/Synthesize), not a single-paragraph answer.
3. **Problem restated every loop:** inspect the output; every loop subsection begins with a one-sentence restatement of the original problem.
4. **Depth discipline:** the output reports "Depth Applied" of 3–4 loops by default; it does not jump to 7+ loops without explicit user direction.
5. **Devil's advocate mode:** ask "devil's advocate this: <idea>" — the response states the strongest opposing argument before the conclusion.
6. **No overuse:** ask a simple factual question ("what time is it in Berlin?") — the agent answers directly without loop structure.