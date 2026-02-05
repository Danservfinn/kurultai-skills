---
name: ship-it
description: "Automated workflow to test, update documentation, commit, and deploy changes. Updates project knowledge base. Use /ship-it after completing features or fixes to safely ship code."
---

# Ship It - Test, Document, Commit & Deploy

Automated workflow for shipping code changes safely and consistently, including knowledge base updates.

## Workflow

When invoked, execute these steps in order:

### Step 1: Audit Implementation Completeness

Before shipping, verify the recent work is actually complete:

#### 1a. Check for Active Plan

Look for an active plan file in `.claude/plans/`:
```bash
ls -la .claude/plans/*.md 2>/dev/null | head -5
```

If a plan exists, read it and verify:
- All planned tasks are implemented
- No TODO items remain unaddressed
- Edge cases mentioned in plan are handled

#### 1b. Review Recent Implementation

Examine the most recent changes for completeness:
```bash
git log --oneline -10
git diff --name-only HEAD~3..HEAD
```

For each modified file, check:
- No incomplete implementations (search for `TODO`, `FIXME`, `XXX`)
- No placeholder code or stub functions
- No commented-out incomplete code

```bash
git diff HEAD~3..HEAD | grep -E "(TODO|FIXME|XXX|HACK|PLACEHOLDER)" || echo "No incomplete markers found"
```

#### 1c. Verify Feature Completeness

If implementing a feature:
- Does it handle error cases?
- Are there missing validation checks?
- Is the happy path AND unhappy path working?

**CRITICAL:** If the audit reveals incomplete work, STOP and report what's missing. Complete the implementation before shipping.

### Step 2: Analyze Changes

```bash
git status
git diff --stat HEAD~1..HEAD 2>/dev/null || git diff --stat
```

Identify what files changed and categorize:
- New files/modules added?
- Existing modules modified?
- Configuration changes?
- New features or APIs?

### Step 3: Run Tests

Run the project's test suite:

```bash
# For BYRD project
pytest -v --tb=short

# Alternative for JS projects
# npm test
```

**CRITICAL:** If tests fail, STOP and report the failures. Do NOT proceed to commit.

### Step 4: Update Project Documentation

Based on what changed, update **ALL** relevant documentation:

#### 4a. Update CLAUDE.md Files

**CRITICAL:** CLAUDE.md files are the project's institutional memory. Update them when:

| Changed | CLAUDE.md Section to Update |
|---------|----------------------------|
| New patterns discovered | Add to patterns/conventions section |
| New commands/workflows | Add to commands/workflows section |
| Environment changes | Update environment/setup instructions |
| Architecture changes | Update architecture overview |
| New dependencies | Update dependencies section |
| Bug fixes with learnings | Add to known issues/gotchas section |
| Performance optimizations | Document the approach taken |

Check ALL CLAUDE.md files in the project hierarchy:
- `./CLAUDE.md` (project root)
- `./.claude/CLAUDE.md` (claude-specific instructions)
- Parent directories if relevant

#### 4b. Update ARCHITECTURE.md

**CRITICAL:** ARCHITECTURE.md documents system design and technical decisions. Update when:

| Changed | ARCHITECTURE.md Section to Update |
|---------|----------------------------------|
| New API endpoints | API Routes / Endpoints section |
| New components/modules | Component Architecture section |
| Database schema changes | Data Model / Schema section |
| New services/agents | Service Architecture section |
| Integration changes | External Integrations section |
| Performance changes | Performance Considerations section |
| Security changes | Security Architecture section |

If ARCHITECTURE.md doesn't exist, create it with sections for:
- System Overview
- Component Architecture
- Data Flow
- API Routes
- Database Schema
- External Integrations

#### 4c. Update Other Documentation

| Changed | Update |
|---------|--------|
| User-facing features | README.md |
| Environment variables | .env.example |
| Build/deploy process | DEPLOYMENT.md or README |
| API contracts | API docs, OpenAPI spec |
| Configuration options | Config docs |

### Step 5: Update Knowledge Base

Update the `.claude/` knowledge base based on changes:

#### 5a. Record Deployment Observation

Use the `mem-record` skill to record what was shipped:

```
Type: ✅ change
Title: <descriptive title of what shipped>
Content: <summary of changes, files modified, features added>
Files: <list of key files changed>
```

#### 5b. Update Metadata (if modules changed)

If a core module was significantly modified, update its metadata file:

| Module Changed | Update File |
|----------------|-------------|
| agi_runner.py | .claude/metadata/agi-runner.md (create if missing) |
| server.py | .claude/metadata/server-api.md |
| dreamer.py | .claude/metadata/dreamer-module.md |
| seeker.py | .claude/metadata/seeker-module.md |
| memory.py | .claude/metadata/memory-schema.md |
| omega.py | .claude/metadata/omega-system.md |

#### 5c. Update Manifest (if new knowledge added)

If you created new metadata/pattern files, add them to `.claude/manifest.md`:

```markdown
| Title | Type | Path | Tags | Relations | Updated |
|-------|------|------|------|-----------|---------|
| New Entry | metadata | ./.claude/metadata/new-file.md | tags, here | — | YYYY-MM-DD |
```

#### 5d. Update Code Index (if structure changed)

If new Python files were added, update `.claude/code_index/module-index.md`.

### Step 6: Commit

Stage and commit with conventional format:

```bash
git add -A
git commit -m "$(cat <<'EOF'
<type>: <description>

<body if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

Types: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

### Step 7: Deploy

#### 7a. Push to Git Remotes

```bash
git push origin main
git push hf main 2>/dev/null || echo "No HuggingFace remote"
```

#### 7b. Deploy to Hosting Platform

Detect and deploy to the project's hosting platform:

**Vercel Projects** (detected by `vercel.json` or `.vercel/`):
```bash
vercel --prod
```

**Railway Projects** (detected by `railway.json` or Procfile):
```bash
railway up
```

**Next.js on Vercel** (auto-deploy on push to main):
- Verify deployment status at Vercel dashboard
- Check build logs if deployment fails

**Python/Flask on Railway**:
```bash
railway up --detach
```

**Manual Deployment Required**:
- If no auto-deploy configured, prompt user for deployment command
- Document the deployment process in CLAUDE.md for future runs

#### 7c. Verify Deployment

After deployment:
1. Check the production URL is accessible
2. Verify key functionality works
3. Monitor for errors in logs (first 2 minutes)

## Output Format

Report progress like this:

```
🚀 Ship-It Workflow
━━━━━━━━━━━━━━━━━━━

📋 Changes detected:
   - server.py (modified)
   - agi_runner.py (modified)
   - src/components/Dashboard.tsx (new)

🧪 Running tests...
   ✅ 94 passed, 0 failed

📝 Documentation Updated:
   CLAUDE.md:
   - ✅ Added new Dashboard component pattern
   - ✅ Documented performance optimization approach
   ARCHITECTURE.md:
   - ✅ Added Dashboard to Component Architecture
   - ✅ Documented new /api/metrics endpoint
   - ✅ Updated Data Flow diagram
   README.md:
   - ✅ Added Dashboard feature description

🧠 Knowledge Base:
   - Recorded observation: "AGI metrics endpoint added"
   - Updated .claude/metadata/agi-runner.md
   - Updated manifest.md

📦 Committed:
   feat: add comprehensive AGI metrics endpoint

🚀 Deployed:
   Git:
   - ✅ origin/main
   - ✅ hf/main
   Hosting:
   - ✅ Vercel production deployment
   - 🔗 https://myapp.vercel.app
   Verification:
   - ✅ Production URL accessible
   - ✅ New endpoint responding

✅ Ship complete!
```

## Knowledge Base Structure

```
.claude/
├── manifest.md           # Index of all knowledge entries
├── metadata/             # Module documentation
│   ├── dreamer-module.md
│   ├── seeker-module.md
│   └── ...
├── patterns/             # Architectural patterns
├── cheatsheets/          # Quick reference guides
├── memory_anchors/       # Key concepts and protocols
└── code_index/           # Code structure index
```

## Arguments

- `/ship-it` - Full workflow (tests, docs, KB, commit, deploy)
- `/ship-it --skip-tests` - Skip tests (dangerous!)
- `/ship-it --no-deploy` - Commit and push to git only, no hosting deployment
- `/ship-it --no-kb` - Skip knowledge base updates
- `/ship-it --no-docs` - Skip documentation updates (not recommended)
- `/ship-it --dry-run` - Show what would happen without making changes
- `/ship-it --verify-only` - Only verify current deployment status

## Safety Rules

1. Never force push
2. Never skip failing tests without explicit user override
3. Verify test output before proceeding
4. Ask before large documentation rewrites
5. Keep knowledge base updates focused and minimal
6. Always update CLAUDE.md and ARCHITECTURE.md when patterns, architecture, or workflows change
7. Verify deployment succeeded before marking ship complete
8. If deployment fails, rollback git push is NOT automatic - alert user
