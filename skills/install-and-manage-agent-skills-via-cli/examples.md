skill: install-and-manage-agent-skills-via-cli
```

## Example 1 — Discover and install a design skill to Claude Code (project scope)

**Input:**
- source: `vercel-labs/agent-skills`
- agents: `claude-code`
- scope: project

**Run:**
```bash
npx skills add vercel-labs/agent-skills --list
npx skills add vercel-labs/agent-skills --skill web-design-guidelines -a claude-code -y
ls -l .claude/skills/
```

**Result:** `web-design-guidelines` appears in `.claude/skills/` as a symlink to the canonical copy. `git status` shows the new skill directory; commit it to share with the team.

## Example 2 — Install a private skill globally for Codex and OpenCode

**Input:**
- source: `acme/private-skills` (private GitHub repo)
- agents: `codex`, `opencode`
- scope: global

**Run:**
```bash
gh auth status   # confirm GitHub CLI auth, or export GITHUB_TOKEN
npx skills add acme/private-skills --skill release-notes -a codex -a opencode -g -y
npx skills list -g -a codex -a opencode
```

**Result:** `release-notes` is installed to `~/.codex/skills/` and `~/.config/opencode/skills/` (the agents' global paths). If auth fails, the CLI errors before writing anything; fix credentials and retry.

## Example 3 — Try a skill once, then update installed skills

**Input:**
- use-without-install: `vercel-labs/agent-skills@frontend-design`
- update target: `web-design-guidelines` (previously installed)

**Run:**
```bash
npx skills use vercel-labs/agent-skills@frontend-design | claude
npx skills update web-design-guidelines
```

**Result:** The first command writes skill files to a temp dir and pipes a generated prompt to `claude`; nothing is added to `.claude/skills/` or `~/.claude/skills/` by this command. The update command refreshes the already-installed `web-design-guidelines` to the latest version from its source.