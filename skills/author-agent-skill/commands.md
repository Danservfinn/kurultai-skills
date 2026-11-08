# Commands — author-agent-skill

Placeholders:
- `<skill-name>` — the new skill's folder and frontmatter name (lowercase, hyphens).
- `<project-dir>` — a scratch project directory used for testing.

## Step 1 — clone repo, verify template, copy or fall back

```bash
rm -rf /tmp/skills-repo && git clone --depth 1 https://github.com/anthropics/skills /tmp/skills-repo
ls /tmp/skills-repo/template/SKILL.md 2>/dev/null && echo TEMPLATE_OK || echo TEMPLATE_MISSING
ls /tmp/skills-repo/skills/skill-creator 2>/dev/null && sed -n '1,60p' /tmp/skills-repo/skills/skill-creator/SKILL.md
# if TEMPLATE_OK:
cp -R /tmp/skills-repo/template ./<skill-name>
# if TEMPLATE_MISSING:
mkdir -p ./<skill-name> && touch ./<skill-name>/SKILL.md
```

## Step 2 — clear placeholders / confirm empty file

```bash
# if template copied:
sed -i '' '1,$d' ./<skill-name>/SKILL.md   # macOS sed; file rewritten in steps 3-4
```

## Steps 3–5 — write SKILL.md and bundle resources

```bash
cat > ./<skill-name>/SKILL.md <<'EOF'
---
name: <skill-name>
description: <what it does and when to use it, with trigger conditions>
---

# <Skill Title>

<imperative instructions>

## Examples
- <example 1>
- <example 2>

## Guidelines
- <guideline>
EOF
cp <path-to-scripts-or-resources> ./<skill-name>/ 2>/dev/null; chmod +x ./<skill-name>/*.sh ./<skill-name>/scripts/* 2>/dev/null
```

## Step 6 — validate frontmatter (PyYAML with fallback)

```bash
python3 - <<'EOF' || sed -n '/^---$/,/^---$/p' ./<skill-name>/SKILL.md | grep -E '^(name|description):' 
try:
    import yaml
except ImportError:
    raise SystemExit(1)
text = open('./<skill-name>/SKILL.md').read()
fm = text.split('---')[1]
data = yaml.safe_load(fm)
assert 'name' in data and 'description' in data, 'missing required field'
import re; assert re.fullmatch(r'[a-z0-9-]+', data['name']), 'bad name format'
print('FRONTMATTER_OK')
EOF
```

If the fallback sed/grep path is taken, verify manually that both `name:` and `description:` lines printed and the name is lowercase-hyphen.

## Step 7 — local test in Claude Code

```bash
mkdir -p <project-dir>/.claude/skills
cp -R ./<skill-name> <project-dir>/.claude/skills/
cd <project-dir> && claude
# in the Claude Code prompt, invoke the skill by name, e.g.:
#   "Use the <skill-name> skill to <example task>"
```

Optional marketplace path (requires your skill inside a plugin structure in a git repo Claude Code can reach):

```bash
# inside Claude Code:
# /plugin marketplace add <owner>/<repo-containing-your-plugin>
# /plugin install <plugin-name>@<marketplace-name>
```