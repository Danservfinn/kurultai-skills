Placeholders:
  <SOURCE>    skill source: owner/repo, git URL, tree URL, local path, or download URL
  <AGENT>     agent name, e.g. claude-code, codex, opencode, cursor
  <SKILL>     skill name as shown by --list or find (quote if it contains spaces)
  <QUERY>     search keyword
  <OWNER>     GitHub org or user
  <NAME>      new skill name for init

All commands run via npx; Node.js required. Run `npx skills --help` and
`npx skills add --help` first and confirm every flag used below appears there
before running it.
```

### Step 1 — Verify CLI surface

```bash
npx skills --help
npx skills add --help
```

### Step 2 — Discover skills

```bash
npx skills find <QUERY>
npx skills find            # interactive
npx skills find <QUERY> --owner <OWNER>
npx skills add <SOURCE> --list
```

### Step 3 — Install

```bash
npx skills add <SOURCE> --skill <SKILL> -a <AGENT> -g -y
npx skills add <SOURCE> --skill <SKILL> -a <AGENT> -y          # project scope
npx skills add <SOURCE> --skill '*' -a <AGENT> -y
npx skills add <SOURCE> --skill <SKILL> -a '*' -y
npx skills add <SOURCE> --all
npx skills add <SOURCE> --skill "Convex Best Practices" -a <AGENT> -y
npx skills add <SOURCE> --skill <SKILL> -a <AGENT> -y --copy   # when symlinks unsupported
```

### Step 4 — Private repo auth

```bash
gh auth status                       # preferred: authenticated GitHub CLI
# or: configure git credential helper, SSH keys, or:
export GITHUB_TOKEN=<token>
```

### Step 5 — Scaffold a new skill

```bash
npx skills init <NAME>
npx skills init                      # SKILL.md in current directory
```

### Step 6 — List installed

```bash
npx skills list
npx skills list -g
npx skills list -a <AGENT> -a <AGENT>
```

### Step 7 — Use without installing

```bash
npx skills use <SOURCE>@<SKILL>              # prints prompt to stdout
npx skills use <SOURCE>@<SKILL> | claude
npx skills use <SOURCE> --skill <SKILL> --agent <AGENT>
```

### Step 8 — Update and remove

```bash
npx skills update <NAME>
npx skills update <NAME> <NAME>
npx skills update -g
npx skills update -p
npx skills update -y
npx skills remove <NAME>
npx skills remove <NAME> -g
npx skills remove --agent <AGENT> <NAME>
npx skills rm <NAME>
npx skills remove --skill '*' -a <AGENT>     # all skills from one agent
# DESTRUCTIVE — removes every skill in scope, no confirmation:
npx skills remove --all