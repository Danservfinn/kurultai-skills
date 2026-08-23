# Commands — deepthink-loop-reasoning

This skill is a pure reasoning workflow. It requires no shell commands to execute. The only commands below are for installing the skill files into an agent's skills directory.

## Placeholders

- `<skills-dir>` — the skills directory of the agent stack in use. For Claude Code this is `~/.claude/skills`. For Hermes this is `~/.hermes/skills`. Substitute the actual path; do not run with the placeholder literal.
- The skill directory name is the slug: `deepthink-loop-reasoning`.

## Install (all four files, not just SKILL.md)

```bash
mkdir -p <skills-dir>/deepthink-loop-reasoning
cp SKILL.md examples.md commands.md tests.md <skills-dir>/deepthink-loop-reasoning/
```

## Verify installation (filesystem check only — no agent CLI assumed)

```bash
ls <skills-dir>/deepthink-loop-reasoning/
# Expected output: SKILL.md examples.md commands.md tests.md
```

```bash
grep -l "deepthink-loop-reasoning" <skills-dir>/deepthink-loop-reasoning/SKILL.md
# Expected: prints the file path (frontmatter name matches the directory)
```

## Reloading the agent

Reload procedure depends on the agent stack and is out of scope for this file. Consult your agent's own documentation for how it picks up new skill files. Do not run state-clearing or restart commands without knowing what they do in your specific stack.