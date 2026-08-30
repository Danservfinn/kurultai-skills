---
name: unforgit-agent-memory-setup
description: Set up persistent, shareable long-term memory for AI agents using the unforgit CLI. Use when a project needs cross-session agent memory, when importing existing CLAUDE.md/MEMORY.md files into a memory store, or when a team wants shared agent knowledge. Requires Node.js/npm; OpenAI API key optional for semantic ranking.
category: infrastructure
---

# unforgit Agent Memory Setup

## Goal

Install and configure unforgit in a project so an AI agent has persistent, recallable memory; import existing markdown memory files; and optionally export curated memory back to markdown and share it with a team.

## Inputs

- Project folder (must exist; run all commands inside it)
- Optional: existing `CLAUDE.md` or `MEMORY.md` to import
- Optional: OpenAI API key, for hybrid semantic ranking (without it, search falls back to local FTS)
- Optional: a configured unforgit remote, for team sync (setup of the remote is NOT covered by this skill's source)

## Steps

1. **Verify the package before installing.** Do not blind-install. Check that the npm package exists and matches the GitHub repo referenced in the source thread (`miguelmedeiros/unforgit`):
   - `npm view unforgit name version repository homepage`
   - Confirm `repository` points at `https://github.com/miguelmedeiros/unforgit`. If it does not, or the package does not exist, stop — see Failure modes.
2. **Install the CLI globally:** `npm install -g unforgit`. Confirm with `unforgit --version`.
3. **Initialize in the project folder:** run `unforgit init` inside the project. This sets up local storage (SQLite), config, and MCP integration.
4. **Import existing markdown memory conservatively.** Always dry-run first:
   - `unforgit md import CLAUDE.md --dry-run` — review the preview.
   - Then run without `--dry-run` to import. The importer skips likely secrets and prompt-injection-like instructions and avoids duplicates; imported memories keep source file, line, heading, and checksum.
   - Expect some ambiguous content to be skipped; review skipped items manually.
5. **Store new knowledge as it is learned** (bug fixes, decisions): use `unforgit remember` from the shell, or the `unforgit_remember` MCP tool if connected via MCP.
6. **Recall context before acting:** `unforgit recall "how to deploy"`, or the `unforgit_search` MCP tool. Local FTS works without any API key; add an OpenAI key for hybrid semantic ranking.
7. **Export curated memory back to markdown — with a backup.** `unforgit md export --format claude --out CLAUDE.md` regenerates the file from the memory store. **Warning: this overwrites the existing CLAUDE.md.** Any hand-maintained content in that file that was not imported into unforgit will be lost. Back it up first:
   - `cp CLAUDE.md CLAUDE.md.bak.$(date +%Y%m%d%H%M%S)`
   - Then run the export. Diff the result against the backup (`diff CLAUDE.md.bak.* CLAUDE.md`) and restore anything missing.
8. **Team sync (only if a remote is already configured).** `unforgit push` publishes team memories; `unforgit pull` syncs teammates' knowledge. This skill's source does not document how to configure the remote — do not attempt push/pull until remote setup is done per the official docs (unforgit.com/docs). Treat this step as blocked otherwise.
9. **Optional: web dashboard.** Run `unforgit web` and open `http://localhost:3838` to review memories, the semantic graph, and stats. Stop it with Ctrl-C when done.

## Outputs

- Persistent local memory store (SQLite) in the project
- Imported memories with provenance (source file, line, heading, checksum)
- Regenerated `CLAUDE.md` with stable Unforgit IDs (plus timestamped backup of the original)
- Optional: team-shared memory via remote sync; web dashboard at localhost:3838

## Failure modes

- `npm view unforgit` shows no package or a mismatched repository — possible typosquat/supply-chain risk; do not install. Report and stop.
- Semantic ranking unavailable without an OpenAI API key; search falls back to local FTS (still functional).
- Markdown import may skip ambiguous content due to conservative secret/injection filtering — check the dry-run output and re-add skipped items manually if needed.
- `md export --out CLAUDE.md` overwrites the existing file; without a backup, hand-maintained content not in the memory store is lost.
- `unforgit push`/`pull` fail without a configured remote; remote setup is not documented in this skill's source.
- Port 3838 already in use: `unforgit web` will fail or need a different port; check with `lsof -i :3838`.

## Source

- Discord thread "Unforgit a memory plugin for Hermes" (channel 1485392832154832906, message 1514108197651087462, 2026-08-29), linking unforgit.com and github.com/miguelmedeiros/unforgit. All command syntax taken from unforgit.com landing page content quoted in the thread.