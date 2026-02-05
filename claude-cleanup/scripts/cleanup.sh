#!/bin/bash
# Claude Code Memory Cleanup Script
# Kills orphaned subagent processes that accumulate over time

set -e

echo "=== Claude Code Memory Cleanup ==="
echo ""

# Count processes before
BEFORE_COUNT=$(ps aux | grep -c "claude.*--disallowedTools" 2>/dev/null || echo "0")
BEFORE_MEM=$(ps aux | grep "claude" | grep -v grep | awk '{sum += $6} END {printf "%.0f", sum/1024}' 2>/dev/null || echo "0")

echo "Before cleanup:"
echo "  Subagent processes: $BEFORE_COUNT"
echo "  Total Claude memory: ${BEFORE_MEM}MB"
echo ""

# Kill orphaned haiku subagents (identified by --disallowedTools flag)
if pgrep -f "claude.*--model claude-haiku.*--disallowedTools" > /dev/null 2>&1; then
    echo "Killing orphaned haiku subagents..."
    pkill -f "claude.*--model claude-haiku.*--disallowedTools" 2>/dev/null || true
    sleep 1
else
    echo "No orphaned haiku subagents found."
fi

# Kill any other orphaned subagents (sonnet, opus)
if pgrep -f "claude.*--model claude-sonnet.*--disallowedTools" > /dev/null 2>&1; then
    echo "Killing orphaned sonnet subagents..."
    pkill -f "claude.*--model claude-sonnet.*--disallowedTools" 2>/dev/null || true
    sleep 1
fi

if pgrep -f "claude.*--model claude-opus.*--disallowedTools" > /dev/null 2>&1; then
    echo "Killing orphaned opus subagents..."
    pkill -f "claude.*--model claude-opus.*--disallowedTools" 2>/dev/null || true
    sleep 1
fi

# Count processes after
AFTER_COUNT=$(ps aux | grep -c "claude.*--disallowedTools" 2>/dev/null || echo "0")
AFTER_MEM=$(ps aux | grep "claude" | grep -v grep | awk '{sum += $6} END {printf "%.0f", sum/1024}' 2>/dev/null || echo "0")

echo ""
echo "After cleanup:"
echo "  Subagent processes: $AFTER_COUNT"
echo "  Total Claude memory: ${AFTER_MEM}MB"
echo ""

# Calculate savings
FREED=$((BEFORE_MEM - AFTER_MEM))
KILLED=$((BEFORE_COUNT - AFTER_COUNT))

if [ "$KILLED" -gt 0 ]; then
    echo "Cleanup complete!"
    echo "  Processes killed: $KILLED"
    echo "  Memory freed: ~${FREED}MB"
else
    echo "No orphaned processes found. System is clean."
fi
