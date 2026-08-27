# Commands — deepthink-loop-reasoning

## Placeholder conventions

- `<SKILL_DIR>` — the directory containing this skill package on the host agent. Adapt to the host's actual skill layout; the source handoff used `~/.hermes/skills/deepthink/` for Hermes, but other agent stacks use different paths. Check your agent's documentation for where skill markdown files are loaded from before installing.
- `<PACKAGE_DIR>` — the directory containing this SKILL.md/examples.md/commands.md/tests.md bundle.

This skill is a reasoning workflow; it requires no commands at runtime. The only commands are for installation and verification of the install.

## Step: Install the skill file

Back up any existing skill at the target path before overwriting:

```bash
mkdir -p <SKILL_DIR>
if [ -f <SKILL_DIR>/SKILL.md ]; then
  cp <SKILL_DIR>/SKILL.md "<SKILL_DIR>/SKILL.md.bak.$(date +%Y%m%d%H%M%S)"
fi
cp <PACKAGE_DIR>/SKILL.md <SKILL_DIR>/SKILL.md
```

## Step: Verify the file landed

```bash
ls -l <SKILL_DIR>/SKILL.md
head -5 <SKILL_DIR>/SKILL.md
```

`head -5` should show the YAML frontmatter with `name: deepthink-loop-reasoning`.

## Step: Reload skills (agent-dependent)

The source handoff lists `/reload-skills` and `/reset` — these are typed into the agent's **chat interface**, not a shell. Whether they exist depends on the host agent; consult its documentation. If no reload command exists, restart the agent process the way your deployment normally does.

## Step: Verify the skill triggers

Ask the agent (through whatever chat interface it exposes):

```
Use deepthink to reason through whether I should choose Next.js API routes
or a separate backend service for a small SaaS.
```

The response should follow the output format in SKILL.md step 11 (starts with `# DeepThink Analysis`, contains `## Reasoning Journey` with per-loop subsections).