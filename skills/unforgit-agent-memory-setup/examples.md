# Examples

## Example 1: Solo project with existing CLAUDE.md

Kurultai input:
> Set up unforgit memory for my project at ~/work/api-gateway. I already have a CLAUDE.md with project conventions I want imported.

Actions:
1. `npm view unforgit name version repository` — confirm repository is `miguelmedeiros/unforgit`.
2. `npm install -g unforgit && unforgit --version`
3. `cd ~/work/api-gateway && unforgit init`
4. `unforgit md import CLAUDE.md --dry-run` — review preview; note skipped lines (e.g., a line containing what looks like a token).
5. `unforgit md import CLAUDE.md`
6. Later, after fixing a bug: `unforgit remember "Auth middleware rejects tokens >2KB; fixed by truncating before signature check in src/auth/verify.ts"`
7. `unforgit recall "auth token bug"` returns the memory via local FTS (no OpenAI key configured).

## Example 2: Export back to CLAUDE.md after curation

Kurultai input:
> I've cleaned up my unforgit memories in the dashboard. Regenerate CLAUDE.md from them.

Actions:
1. `cp CLAUDE.md CLAUDE.md.bak.$(date +%Y%m%d%H%M%S)`
2. `unforgit md export --format claude --out CLAUDE.md`
3. `diff CLAUDE.md.bak.* CLAUDE.md` — verify hand-written "Coding style" section survived (it was imported earlier); restore from backup if missing.

## Example 3: Team sync attempt without a remote

Kurultai input:
> Alice and Bob both use unforgit on the shared repo; sync their memories.

Actions:
1. Both run steps 1–3 from the skill (verify, install, `unforgit init`).
2. Alice runs `unforgit push` → fails: no remote configured.
3. Correct handling: report that remote setup is required and not covered by this skill's source; direct both users to unforgit.com/docs for remote configuration, then retry `unforgit push` / `unforgit pull`.