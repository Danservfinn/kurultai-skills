# Commands

## Placeholders

- `<PROBLEM>` — the problem statement text.
- `<OUTPUT_FILE>` — path to write the DeepThink Analysis document, e.g. `deepthink-analysis.md`.
- `<SKILL_DIR>` — your agent's skill directory. The source states `~/.hermes/skills/deepthink/` for Hermes; **verify this applies to your installation before use** (check your agent's documentation for how it discovers skills). If a profile layout exists at `~/.hermes/profiles/<profile-name>/skills/`, prefer the profile path when running under that profile.

This skill is primarily a reasoning workflow; the only shell commands involved are optional install and output-writing steps.

## Step: Install the skill (optional, one-time)

```bash
# From the directory containing this SKILL.md. Back up any existing copy first.
mkdir -p <SKILL_DIR>
[ -f <SKILL_DIR>/SKILL.md ] && cp <SKILL_DIR>/SKILL.md <SKILL_DIR>/SKILL.md.bak
cp ./SKILL.md <SKILL_DIR>/SKILL.md
```

## Step: Verify install (mechanical, no invented CLI assumed)

```bash
# Confirm the file landed and frontmatter parses.
ls -l <SKILL_DIR>/SKILL.md
head -5 <SKILL_DIR>/SKILL.md
```

Note: the source handoff suggests `hermes skills list | grep -i deepthink` and `hermes chat -q "..."` for verification. These commands are **unverified** — run `hermes --help` (or your agent's equivalent) first to confirm they exist in your build before relying on them. Similarly, the in-session `/reload-skills` and `/reset` commands are only valid in whatever interactive interface your agent provides (CLI REPL, Discord, Telegram); they are not shell commands.

## Step: Write the output document

```bash
cat > <OUTPUT_FILE> <<'EOF'
# DeepThink Analysis

## Problem
<PROBLEM>

## Depth Applied
...

EOF
# Then fill in the remaining sections per SKILL.md Step 9.