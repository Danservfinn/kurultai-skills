# Commands

Placeholders:
- `SKILL.md` — the DeepThink skill file in the current working directory.
- `<profile-name>` — your Hermes profile name, if you use one.

## Step 11 — Install as a Hermes skill (default location)

```bash
mkdir -p ~/.hermes/skills/deepthink
cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md
```

## Step 11 — Install into a named Hermes profile

```bash
mkdir -p ~/.hermes/profiles/<profile-name>/skills/deepthink
cp SKILL.md ~/.hermes/profiles/<profile-name>/skills/deepthink/SKILL.md
```

## Step 11 — Verify installation

```bash
hermes skills list | grep -i deepthink
```

## Step 11 — Restart gateway if skill does not appear (gateway/Telegram/Discord clients)

```bash
hermes gateway restart
```

## Step 11 — Reload inside a chat session

```text
/reload-skills
/reset
```

## Step 11 — Functional smoke test

```bash
hermes chat -q "Use deepthink to reason through whether I should choose Next.js API routes or a separate backend service for a small SaaS."
```

Note: steps 1–10 are pure reasoning steps with no shell commands. The only commands in this skill are the optional install/verify steps.