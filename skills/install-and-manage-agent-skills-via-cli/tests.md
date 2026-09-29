Run in a throwaway directory to avoid touching real global skill dirs:
  mkdir /tmp/skills-test && cd /tmp/skills-test
Tests 1–4 use project scope only; no global (-g) flags are used,
so ~/.claude/skills/ and other home dirs are never modified.
```

1. **Flag surface check:** `npx skills add --help` lists `-s, --skill`, `-a, --agent`, `-g`, `-y`, `--list`, and `--copy`. If any is missing, stop and note the version before running later tests.
2. **Discovery works:** `npx skills add vercel-labs/agent-skills --list` exits 0 and prints a list of skill names including `web-design-guidelines`.
3. **Install and verify:** `npx skills add vercel-labs/agent-skills --skill web-design-guidelines -a claude-code -y` then `ls .claude/skills/` shows `web-design-guidelines/` containing a `SKILL.md` whose frontmatter has `name:` and `description:`.
4. **Use-without-install adds nothing:** `npx skills use vercel-labs/agent-skills@frontend-design > /tmp/prompt.txt` exits 0, `/tmp/prompt.txt` is non-empty, and `ls .claude/skills/` still shows only `web-design-guidelines` (no `frontend-design`).
5. **Update and targeted remove:** `npx skills update web-design-guidelines` exits 0; `npx skills remove web-design-guidelines` then `ls .claude/skills/` shows it is gone. Do NOT run `remove --all` here.
6. **Cleanup:** `rm -rf /tmp/skills-test /tmp/prompt.txt`. Confirm no changes under `$HOME` were made at any point (no `-g` was used).