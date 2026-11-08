---
name: author-agent-skill
description: Create a reusable Agent Skill as a self-contained folder with a SKILL.md (YAML frontmatter plus instructions, examples, and guidelines), optionally add scripts/resources, and install it for local testing in Claude Code via .claude/skills directories or a plugin marketplace.
category: agent-security
---
```

# Author an Agent Skill

## Goal

Produce a self-contained skill folder containing a `SKILL.md` file with valid YAML frontmatter (`name`, `description`) and a markdown body (instructions, `## Examples`, `## Guidelines`), then load and test it in Claude Code.

## Inputs

- A task description for the skill (what the skill does and when to use it).
- Optional supporting scripts and resources to bundle in the skill folder.
- Network access to clone `https://github.com/anthropics/skills` (for the template and as a marketplace source).
- Claude Code installed locally for the testing step (the `/plugin` and skills-loading features are Claude Code features; without them, stop after step 6 and note the skill is untested).

## Steps

1. Clone the `anthropics/skills` repository to `/tmp/skills-repo`. Check whether `/tmp/skills-repo/template/SKILL.md` exists; if it does, copy the template folder into your working directory as `./<skill-name>`. If it does not, create `./<skill-name>/` manually and note that you will write SKILL.md from the template pattern in the README instead of copying files. Also check `/tmp/skills-repo/skills/skill-creator` — the repo ships a `skill-creator` example skill that documents best practices; read it if present.
2. If the template was copied, open `./<skill-name>/SKILL.md` and strip all template placeholder text; the file will be rewritten in steps 3–4. If not, create `./<skill-name>/SKILL.md` as an empty file.
3. Write the YAML frontmatter delimited by `---` lines with exactly the two required fields: `name` — a unique identifier, lowercase, hyphens for spaces — and `description` — a complete description of what the skill does and when to use it. Write the description so an agent reading only frontmatter can decide when to activate the skill; include trigger conditions, not just a label.
4. Write the markdown body: a title, imperative instructions the agent will follow when the skill is active, an `## Examples` section with at least two concrete usage examples, and a `## Guidelines` section with constraints and cautions.
5. Copy any supporting scripts or resources into `./<skill-name>/` so the folder is fully self-contained; reference them from SKILL.md by relative path. Make scripts executable.
6. Validate the file: parse the frontmatter with `python3` (checking PyYAML availability first, with a sed-based field-existence fallback), and assert that both `name` and `description` keys exist and `name` matches `^[a-z0-9-]+$`.
7. Test locally without a marketplace: copy (or symlink) `./<skill-name>/` into the project-local skills directory `.claude/skills/` (or the user-level `~/.claude/skills/`) of a scratch project, launch Claude Code there, and invoke the skill by name to confirm it loads and executes. Optionally, to test via the marketplace path, register a plugin marketplace pointing at a local clone containing your skill inside a plugin structure, then install and invoke it — but the `.claude/skills/` directory is the direct local-test mechanism and requires no packaging.

## Outputs

- `./<skill-name>/` — a self-contained skill folder with `SKILL.md` and any bundled scripts/resources.
- A verified load of the skill in Claude Code via `.claude/skills/` (and optionally an installable plugin/marketplace setup).

## Failure modes

- Frontmatter missing `name` or `description` — caught by the step 6 validation; fix before testing.
- Description too vague so the agent does not know when to activate the skill — rewrite to state trigger conditions and scope.
- Skill folder not self-contained (missing scripts/resources referenced in SKILL.md) — check every relative path in SKILL.md resolves inside the folder.
- Template directory absent from the repo (it has moved in the past) — use the manual-creation fallback in step 1.
- PyYAML not installed — the validation falls back to `sed`/`grep` field checks; install PyYAML (`python3 -m pip install pyyaml`) for full YAML parsing.
- Claude Code unavailable — steps 1–6 still complete; the skill ships untested, which must be stated in the output.

## Source

- https://github.com/anthropics/skills (README: "Creating a Basic Skill", `/template`, `/skills/skill-creator`, `/plugin marketplace add anthropics/skills`), accessed 2026-11-08.