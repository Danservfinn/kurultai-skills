This skill is a pure reasoning workflow. It uses no shell commands, network calls, or external services. All steps are executed by the agent's own reasoning.

The only commands in the source material relate to installing the underlying DeepThink skill file on Hermes, reproduced here for reference:

## Install (reference only, not part of running the skill)

```bash
mkdir -p ~/.hermes/skills/deepthink
cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md
```

Named profile variant:

```bash
mkdir -p ~/.hermes/profiles/<profile-name>/skills/deepthink
cp SKILL.md ~/.hermes/profiles/<profile-name>/skills/deepthink/SKILL.md
```

## Verify install

```bash
hermes skills list | grep -i deepthink
hermes chat -q "Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS."
```

## Reload after install

```text
/reload-skills
/reset
```

If using gateway/Telegram/Discord and the skill does not appear:

```bash
hermes gateway restart
```

Placeholder conventions: `<profile-name>` is the Hermes profile name.