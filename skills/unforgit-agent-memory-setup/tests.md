# Tests

Manual checklist for a reviewer:

1. **Package verification gate:** run `npm view unforgit repository`. Assert the output references `miguelmedeiros/unforgit`; if not, the skill correctly stops before install.
2. **Init creates local storage:** after `unforgit init` in a scratch folder, assert a `.unforgit` directory (or equivalent SQLite store/config) exists: `ls -la` the project folder.
3. **Dry-run is non-destructive:** create a CLAUDE.md with one convention line and one secret-looking line (`API_KEY=sk-...`); run `unforgit md import CLAUDE.md --dry-run`; assert the file is unchanged afterward and the preview flags/skips the secret line.
4. **Export backup exists:** after step 7, assert a file matching `CLAUDE.md.bak.*` exists and `diff` between it and the new CLAUDE.md is explainable (only unforgit-ID-annotated regenerated content differs).
5. **Recall works without an OpenAI key:** `unforgit remember "test memory alpha"` then `unforgit recall "test memory alpha"` returns the memory via local FTS.
6. **Push/pull blocked without remote:** `unforgit push` in a fresh init fails or reports no remote; assert the skill documents this as expected and does not claim team sync works unconfigured.