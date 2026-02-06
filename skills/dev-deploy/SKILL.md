---
name: dev-deploy
description: Parse deployment workflow for merging dev branch to main and triggering Railway production deployment. Use this skill when the user asks to deploy to production, promote changes from dev, merge dev to main, or trigger a production release. This skill handles the complete workflow: checking branch status, merging dev to main, pushing to origin, and monitoring Railway deployment.
tags: [Parse, Deployment, DevOps, Railway, Release, Git]
dependencies: [railway-cli, railway-mcp]
allowed-tools: Bash, mcp__Railway__*
related-skills: [ship-it, parse-cto, senior-devops]
---

# Parse Dev-to-Production Deployment

## Overview

Handle the complete workflow of deploying Parse code changes from the `dev` branch to production (`main` branch). This includes merging dev to main, pushing to origin, and monitoring Railway auto-deployment.

## When to Use

Invoke this skill when:
- User asks to "deploy to production"
- User asks to "merge dev to main"
- User asks to "promote changes from dev"
- User asks to "release to production"
- After completing feature work that needs production deployment

## Deployment Workflow

### Step 1: Pre-Deployment Checks

Before merging, verify the current state:

```bash
# Check current branch
git branch --show-current

# Check for uncommitted changes
git status

# Check recent commits on dev
git log dev --oneline -5

# Check recent commits on main
git log main --oneline -5
```

**Abort deployment if:**
- There are uncommitted changes on dev
- There are merge conflicts expected
- Recent commits on dev are not intended for production

### Step 2: Merge Dev to Main

```bash
# Switch to main branch
git checkout main

# Pull latest main (to avoid conflicts)
git pull origin main

# Merge dev into main
git merge dev

# Push to origin (triggers Railway deployment)
git push origin main
```

### Step 3: Monitor Railway Deployment

Use Railway MCP tools to monitor deployment:

```bash
# List recent deployments
railway list-deployments --json

# Check deployment status
railway status

# Get deployment logs if needed
railway logs --build
```

**Success indicators:**
- Build completes without errors
- Healthcheck passes (`/api/health` returns 200)
- Deployment status shows "SUCCESS"

### Step 4: Post-Deployment Verification

After deployment succeeds:

```bash
# Check production URL
curl -I https://parse-dev.up.railway.app/api/health

# Verify key endpoints work
curl https://parse-dev.up.railway.app/api/stats
```

### Step 5: Return to Dev Branch

```bash
git checkout dev
```

## Error Handling

### Merge Conflicts

If merge fails with conflicts:

```bash
# Abort the merge
git merge --abort

# Notify user of conflict
echo "Merge conflict detected. Please resolve conflicts manually."
```

### Railway Deployment Failures

If Railway deployment fails:

1. Get deployment logs: `railway logs --build`
2. Check for common issues:
   - Failed Prisma migrations
   - Build errors
   - Healthcheck failures
3. Use Railway MCP tools to investigate
4. Consider rollback if critical: `git revert HEAD`

### Rollback Procedure

If production deployment breaks something critical:

```bash
# Revert the merge on main
git checkout main
git revert HEAD
git push origin main
```

## Railway Environment

**Current Configuration:**
- Production URL: https://parse-dev.up.railway.app
- Deployment branch: `main`
- Auto-deploy: Enabled on push to main
- Builder: Nixpacks
- Healthcheck: `/api/health`

## Safety Rules

1. **Never force push** to main branch
2. **Always verify** git status before merging
3. **Always monitor** Railway deployment after push
4. **Never merge** uncommitted or untested code
5. **Keep user informed** of each step in the process

## Quick Reference

| Action | Command |
|--------|---------|
| Check branch | `git branch --show-current` |
| Merge dev to main | `git checkout main && git merge dev && push` |
| Check deployment | `railway list-deployments --json` |
| Check health | `curl https://parse-dev.up.railway.app/api/health` |
| Rollback | `git revert HEAD && push` |
