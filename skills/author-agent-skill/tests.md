# Tests — author-agent-skill

Reviewer checklist. Each assertion is runnable on macOS with the commands from commands.md.

1. **Folder structure.** `ls ./<skill-name>/SKILL.md` succeeds and every relative path mentioned in SKILL.md resolves: `grep -oE '\b(scripts|resources)/[A-Za-z0-9._/-]+' ./<skill-name>/SKILL.md` outputs only paths that exist under `./<skill-name>/`.

2. **Frontmatter fields.** Run the step 6 validation block; it prints `FRONTMATTER_OK` (PyYAML path) or the sed fallback prints both a `name:` and a `description:` line, and `name` matches `^[a-z0-9-]+$`.

3. **Template fallback.** Temporarily `mv /tmp/skills-repo/template /tmp/skills-repo/template.bak`, re-run step 1 in a fresh directory; it prints `TEMPLATE_MISSING` and still creates `./<skill-name>/SKILL.md` instead of failing.

4. **Required body sections.** `grep -c '^## Examples'` and `grep -c '^## Guidelines'` on SKILL.md each return ≥ 1.

5. **Local load test.** After copying into `<project-dir>/.claude/skills/`, launch `claude` in `<project-dir>` and prompt "Use the <skill-name> skill…"; the skill's instructions visibly drive the response (e.g., its named script runs or its guidelines are followed). This tests the author's local skill, not a marketplace example plugin.

6. **Description quality.** The `description` states at least one activation trigger condition ("use when…") and names the skill's output — not just a label like "A PDF skill".