# Commands — deepthink-loop-reasoning

This skill is a pure reasoning workflow. It uses no shell commands to produce the analysis itself. The commands below are for installing/verifying the skill on a Hermes agent, per the source handoff.

Placeholder conventions:
- `SKILL.md` — the skill file in the current directory.
- `<profile-name>` — a named Hermes profile, if used.

## Install (default location)

```bash
mkdir -p ~/.hermes/skills/deepthink
cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md
```

## Install (named profile)

```bash
mkdir -p ~/.hermes/profiles/<profile-name>/skills/deepthink
cp SKILL.md ~/.hermes/profiles/<profile-name>/skills/deepthink/SKILL.md
```

## Reload and verify

```text
/reload-skills
/reset
```

```bash
hermes skills list | grep -i deepthink
```

## Smoke test

```bash
hermes chat -q "Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS."
```

Expected: a looped DeepThink-style analysis, not a single shallow answer.

If using gateway/Telegram/Discord and the skill does not appear:

```bash
hermes gateway restart