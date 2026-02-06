---
name: kurultai-model-switcher
description: Switch LLM models and providers for the Kurultai multi-agent OpenClaw system. Manages model assignments for 6 agents (Kublai, Möngke, Chagatai, Temüjin, Jochi, Ögedei) with validation, rollback support, and deployment guidance.
---

# Kurultai Model Switcher

Manage LLM model and provider assignments for the Kurultai 6-agent OpenClaw deployment.

## Purpose

Enable safe switching of AI models across the multi-agent system for:
- Emergency failover when providers experience outages
- A/B testing new models against existing workloads
- Cost optimization by switching to appropriate models per task
- Performance tuning based on agent-specific requirements

## When to Use

Activate this skill when the user requests:
- Switching an agent to a different model
- Emergency provider failover
- Viewing current model assignments
- Rolling back to previous model configurations
- Validating model configuration files

Common trigger phrases:
- "Switch Kublai to Claude Sonnet"
- "Failover all agents to OpenRouter"
- "What models are currently assigned?"
- "Rollback Temüjin to previous model"
- "Validate model configuration"

## Command Format

Consistent command format across Signal and Claude Code:

```
/switch-model [agent|all] to [model] [--provider provider] [--reason "reason"]
/switch-model status
/switch-model history [agent]
/switch-model rollback [agent]
/switch-model validate
```

### Parameters

- `agent`: Agent ID (`main`, `researcher`, `writer`, `developer`, `analyst`, `ops`) or `all`
- `model`: Target model identifier (e.g., `claude-sonnet-4`, `zai/glm-4.7`, `moonshot/kimi-k2.5`)
- `--provider`: Optional provider hint for validation (`anthropic`, `zai`, `moonshot`, `openrouter`)
- `--reason`: Optional reason for audit logging
- `--dry-run`: Preview changes without applying

## Agent Reference

| ID | Name | Role | Default Model |
|----|------|------|---------------|
| main | Kublai | Squad Lead / Router | moonshot/kimi-k2.5 |
| researcher | Möngke | Researcher | zai/glm-4.5 |
| writer | Chagatai | Content Writer | moonshot/kimi-k2.5 |
| developer | Temüjin | Developer / Security | zai/glm-4.7 |
| analyst | Jochi | Analyst | zai/glm-4.5 |
| ops | Ögedei | Operations / Emergency | zai/glm-4.5 |

For detailed agent information, load `references/agent_matrix.md`.

## Workflow

### 1. Parse Request

Extract from user input:
- Target agent(s) - single agent or `all`
- Target model identifier
- Optional provider hint
- Optional reason for switching

### 2. Pre-flight Validation

Before making changes:
- Verify agent ID exists or is `all`
- Validate model exists in `openclaw.json` provider configuration
- Check required API key environment variables are set
- Load current `moltbot.json` configuration

### 3. Backup Current State

Store current configuration to `.model-switch-history.json`:
- Capture current model for each affected agent
- Timestamp the backup
- Maintain last 10 states per agent

### 4. Apply Changes

Update `moltbot.json`:
- Modify `agents.list[]` entries for target agents
- Set `model` field to new model identifier
- Preserve all other agent configuration

### 5. Validate Output

After changes:
- Verify JSON is well-formed
- Confirm agents have expected model assignments
- Check no configuration corruption occurred

### 6. Log and Report

Record to `model-switch.log`:
- Timestamp
- Agent changes with old/new models
- User who initiated switch
- Reason if provided

Output to user:
- Summary of changes
- Deploy commands for Railway
- Rollback instructions if needed

## Safety Features

### Dry Run Mode

Always offer `--dry-run` first for production switches:
```
/switch-model main to claude-sonnet-4 --dry-run
```

This validates without applying changes.

### Automatic Backup

Every switch operation automatically backs up the previous state. The last 10 configurations per agent are retained in `.model-switch-history.json`.

### Rollback Capability

Revert to previous model:
```
/switch-model rollback main
```

This restores the agent to its immediately previous model assignment.

### Environment Validation

Before allowing switches to new providers, verify:
- `ANTHROPIC_API_KEY` - For Anthropic models
- `ANTHROPIC_BASE_URL` - For Z.AI proxy
- `OPENROUTER_API_KEY` - For OpenRouter models
- `OPENCLAW_GATEWAY_TOKEN` - For agent communication

## Deployment

Configuration changes require deployment to take effect:

```bash
# Commit changes
git add moltbot.json
git commit -m "switch-model: Update agent model assignments"

# Deploy to Railway
railway login
railway link --project kublai
railway up
railway logs --follow
```

The skill outputs these commands after successful configuration updates.

## Configuration Files

### moltbot.json

Production path: `/data/.clawdbot/moltbot.json`
Local path: `moltbot.json`

Contains agent definitions with model assignments in:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zai/glm-4.5"
      }
    },
    "list": [
      {
        "id": "main",
        "name": "Kublai",
        "model": "moonshot/kimi-k2.5"
      }
    ]
  }
}
```

### openclaw.json

Production path: `/data/.clawdbot/openclaw.json`
Local path: `~/.openclaw/openclaw.json`

Contains provider and model definitions. Used for validation only - never modified by this skill.

## Scripts

### model_switcher.py

Main switching logic with CLI interface.

Usage:
```bash
python scripts/model_switcher.py switch --agent main --model claude-sonnet-4
python scripts/model_switcher.py rollback --agent main
python scripts/model_switcher.py status
python scripts/model_switcher.py history --agent main
python scripts/model_switcher.py validate
```

Python API:
```python
from scripts.model_switcher import ModelSwitcher

switcher = ModelSwitcher()
result = switcher.switch_model("main", "claude-sonnet-4", reason="Testing new model")
```

## Error Handling

| Scenario | Response |
|----------|----------|
| Invalid agent ID | List valid agent IDs |
| Model not found | Suggest similar models from openclaw.json |
| Missing API key | List required environment variable |
| JSON parse error | Report corruption, suggest manual fix |
| Neo4j unavailable | Log locally, continue with warning |

## Testing

Before production switches:

1. **Validate configuration:**
   ```
   /switch-model validate
   ```

2. **Dry run the switch:**
   ```
   /switch-model developer to claude-sonnet-4 --dry-run
   ```

3. **Check current status:**
   ```
   /switch-model status
   ```

4. **Apply and monitor:**
   ```
   /switch-model developer to claude-sonnet-4 --reason "Testing coding performance"
   ```

## Integration with Neo4j

When Neo4j operational memory is available, the skill should:
- Create `ModelSwitch` nodes for each switch operation
- Link switches to the initiating user
- Track model performance metrics over time

If Neo4j is unavailable, the skill logs to local files and continues operation.

## Limitations

- Does not auto-deploy - user must run Railway commands
- Does not restart OpenClaw gateway - changes apply on next session
- Does not modify openclaw.json - only reads for validation
- Maximum 10 rollback states stored per agent
