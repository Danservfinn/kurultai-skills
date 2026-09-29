---
name: install-and-manage-agent-skills-via-cli
description: Use when you need to discover, install, update, or remove reusable SKILL.md agent-skill packages across coding agents (Claude Code, Codex, OpenCode, Cursor, and ~75 others) with the `npx skills` CLI; also use to scaffold new SKILL.md files or run a skill once without installing it.
category: ops-automation
---

# Install and Manage Agent Skills via CLI

## Goal

Discover, install, update, and remove reusable SKILL.md skill packages across coding agents using the `npx skills` CLI, and scaffold new skills from a template. All commands run via `npx`, so no global install is required; Node.js must be present.

## Inputs

- **Skill source**: `owner/repo` GitHub shorthand, full GitHub/GitLab/Azure DevOps/git URL, a tree URL pointing at one skill directory, a local path, or a direct SKILL.md/archive download URL (`.zip`, `.tar`, `.tar.gz`, `.tgz`, or no extension).
- **Target agent names**: e.g. `claude-code`, `codex`, `opencode`, `cursor`. The CLI auto-detects installed agents if none is given.
- **Scope**: project (default, installs under `./<agent>/skills/`, e.g. `.claude/skills/` for claude-code) or global (`-g`, installs under `~/<agent>/skills/`, e.g. `~/.claude/skills/`).
- **Auth for private repos** (optional): existing git credential helper, authenticated GitHub CLI (`gh`), SSH keys, or `GITHUB_TOKEN`/`GH_TOKEN` in the environment.

## Steps

1. Verify the CLI surface before relying on any flag: run `npx skills --help` and `npx skills add --help`. Confirm the flags you intend to use appear in the help output. If a flag listed below is missing from help, do not use it; fall back to interactive selection (omit the flag). All flags in this skill are documented in the vercel-labs/skills README (see Source), but help output is authoritative for the installed version.
2. Discover skills: search by keyword with `npx skills find <query>` (interactive with no query), search all repos of an org with `npx skills find <query> --owner <org>`, or list skills inside a specific repo without installing: `npx skills add <owner/repo> --list`.
3. Install non-interactively: `npx skills add <source> --skill <name> -a <agent> -g -y`. Use `-s '*'` for all skills in the repo, `-a '*'` for all detected agents, or `--all` for all skills to all agents with no prompts. Quote skill names containing spaces: `--skill "Convex Best Practices"`. Add `--copy` when the target filesystem does not support symlinks. By default installs symlink the skill into the agent's skill directory; `--copy` makes independent copies.
4. For private repos, use the same `add` command; the CLI tries git credentials, then `gh repo clone` if GitHub CLI is authenticated, then SSH. For GitHub API-based tree lookups and update checks, set `GITHUB_TOKEN` or `GH_TOKEN` if anonymous access fails.
5. Scaffold a new skill: `npx skills init [name]` creates a `SKILL.md` with YAML frontmatter (`name`, `description`) and an instruction body, in the current directory or `<name>/`.
6. List installed skills: `npx skills list` (alias `ls`); add `-g` for global only, or filter by agent with `-a claude-code -a cursor`.
7. Run a skill once without installing: `npx skills use <source>@<skill>` writes the skill files to a temp directory and prints the generated prompt to stdout (pipe it into an agent, e.g. `| claude`), or pass `--agent claude-code` to launch the agent with that prompt. No files land in agent skill directories.
8. Update installed skills: `npx skills update [names]` with `-g`/`-p` to constrain scope and `-y` to skip the scope prompt. Remove skills with `npx skills remove [names]` (alias `rm`); `remove --all` is shorthand for `--skill '*' --agent '*' -y` and removes **every** installed skill in the active scope — confirm intent before running it, and prefer targeted removal (`remove <name> -a <agent>`) in shared environments.

## Outputs

- `SKILL.md` files symlinked (default) or copied (with `--copy`) into agent skill directories: project scope `./<agent>/skills/` (e.g. `.claude/skills/`), global scope `~/<agent>/skills/` (e.g. `~/.claude/skills/`).
- Generated prompt text on stdout from `skills use` (no persistent install).
- Listings of installed (`skills list`) and available (`skills find`, `add --list`) skills.

## Failure modes

- Symlinks unsupported on the target filesystem: rerun `add` with `--copy`.
- Private repo clone fails: no git credential helper, `gh` not authenticated, no SSH key, and no `GITHUB_TOKEN`/`GH_TOKEN` set. Configure one of these and retry.
- Interactive prompts hang in CI: always pass `-y` (and explicit `-a`/`-s`) in non-interactive contexts.
- Skill names with spaces must be quoted: `--skill "Convex Best Practices"`.
- Direct download URLs capped at 10 MiB download, 25 MiB extracted, 1000 files. If needed and the source is trusted, override via `SKILLS_DOWNLOAD_MAX_BYTES`, `SKILLS_EXTRACT_MAX_BYTES`, `SKILLS_EXTRACT_MAX_FILES` (confirm the env names in `--help`/README for your version).
- Nested `SKILL.md` discovery stops three levels deep within skill container directories; a shallow `SKILL.md` shadows nested ones. Use `--full-depth` to also discover files outside container directories (verify the flag exists in `add --help` first).
- A documented flag is absent from `--help` in the installed CLI version: pin a known-good version (e.g. `npx skills@latest`) or use interactive mode instead.

## Source

- https://github.com/vercel-labs/skills (README), retrieved 2026-09-29. All commands and flags above are taken from that README; `--help` output of the installed CLI is the final authority.