---
name: claude-cleanup
description: Clean up orphaned Claude Code subagent processes that accumulate over time and consume RAM/swap. This skill should be used when the user mentions memory issues, slow system, high RAM usage, swap usage, or wants to clean up Claude processes. Also use when system feels sluggish or unresponsive.
---

# Claude Code Memory Cleanup

Clean up orphaned Claude Code subagent processes that accumulate and consume system memory.

## Problem

Claude Code's Task tool spawns subagent processes (haiku/sonnet/opus workers) that sometimes aren't properly terminated after completing their work. Over days of use, hundreds of orphaned processes can accumulate, consuming gigabytes of RAM and causing system slowdown.

## When to Use

- System feels slow or unresponsive
- High RAM or swap usage
- User mentions memory issues
- User asks to clean up Claude processes
- Before starting intensive work sessions
- Periodically as maintenance (weekly recommended)

## Quick Cleanup

To run the cleanup script:

```bash
bash ~/.claude/skills/claude-cleanup/scripts/cleanup.sh
```

## Manual Cleanup Commands

To check for orphaned processes:

```bash
ps aux | grep "claude.*--disallowedTools" | wc -l
```

To see total Claude memory usage:

```bash
ps aux | grep claude | awk '{sum += $6} END {print "Claude memory: " sum/1024 " MB"}'
```

To kill orphaned haiku subagents:

```bash
pkill -f "claude.*--model claude-haiku.*--disallowedTools"
```

To kill all orphaned subagents (haiku, sonnet, opus):

```bash
pkill -f "claude.*--disallowedTools"
```

## What Gets Cleaned

The cleanup targets processes with these characteristics:
- Command contains `claude`
- Has `--disallowedTools` flag (identifies subagent workers)
- Model flag like `--model claude-haiku-4-5`

## What Is Preserved

The cleanup preserves:
- Main Claude Code sessions (no `--disallowedTools` flag)
- MCP server processes (claude-mem, chroma-mcp, etc.)
- Chrome DevTools MCP servers

## Workflow

1. Run the cleanup script or manual commands above
2. Verify remaining processes are legitimate main sessions
3. Check memory usage has decreased

## Automatic Cleanup (PostToolUse Hook)

A PostToolUse hook automatically monitors subagent count after every `Task` tool call:

- **Script:** `~/.claude/hooks/post-task-cleanup.sh`
- **Trigger:** Fires after each `Task` tool dispatch
- **Threshold:** If orphaned subagent count > 50, kills all orphans
- **Config:** Registered in `~/.claude/settings.json` under `hooks.PostToolUse`

This is the primary defense against ENFILE (file table overflow). All 11 horde skills also include a "Process Guard" preamble as secondary defense-in-depth.

## Preventive Measures

To avoid accumulation:
- The PostToolUse hook handles cleanup automatically during horde dispatches
- Restart Claude Code sessions weekly
- Run cleanup before starting intensive work
- Monitor memory usage periodically
