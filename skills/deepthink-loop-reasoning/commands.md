# Commands — deepthink-loop-reasoning

This skill is a pure reasoning workflow. It requires no shell commands, network access, or API keys to execute — the loops run inside the agent's own reasoning.

The only commands relevant to this skill are installation of the skill files themselves.

## Install all four skill files

Placeholder conventions:
- `<SKILL_SOURCE_DIR>` — directory containing SKILL.md, examples.md, commands.md, tests.md
- `<AGENT_SKILLS_DIR>` — the skills directory of the agent stack loading this skill (e.g., a Kurultai agent's configured skills path)

```bash
mkdir -p <AGENT_SKILLS_DIR>/deepthink-loop-reasoning
cp <SKILL_SOURCE_DIR>/SKILL.md <SKILL_SOURCE_DIR>/examples.md <SKILL_SOURCE_DIR>/commands.md <SKILL_SOURCE_DIR>/tests.md \
  <AGENT_SKILLS_DIR>/deepthink-loop-reasoning/
```

## Verify installation

```bash
ls <AGENT_SKILLS_DIR>/deepthink-loop-reasoning/
# expected: SKILL.md examples.md commands.md tests.md
grep -l "deepthink-loop-reasoning" <AGENT_SKILLS_DIR>/deepthink-loop-reasoning/SKILL.md