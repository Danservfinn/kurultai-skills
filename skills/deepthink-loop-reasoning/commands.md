This skill is a pure reasoning workflow — it uses no shell commands, external services, or API keys. All steps are executed by the agent's own reasoning.

The only shell usage is optional installation/verification of the skill itself:

```bash
# Install the skill file (Step 0, optional)
mkdir -p ~/.hermes/skills/deepthink
cp SKILL.md ~/.hermes/skills/deepthink/SKILL.md

# Verify
hermes skills list | grep -i deepthink
```

Placeholder conventions: `SKILL.md` refers to the skill file in the current directory; `~` is the user's home directory.