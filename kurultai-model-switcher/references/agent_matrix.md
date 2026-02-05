# Kurultai Agent Configuration Matrix

Reference guide for the 6-agent Kurultai system with model assignments and use cases.

## Agent Overview

| ID | Name | Role | Default Model | Failover |
|----|------|------|---------------|----------|
| main | Kublai | Squad Lead / Router | moonshot/kimi-k2.5 | Ögedei |
| researcher | Möngke | Researcher | zai/glm-4.5 | - |
| writer | Chagatai | Content Writer | moonshot/kimi-k2.5 | - |
| developer | Temüjin | Developer / Security | zai/glm-4.7 | - |
| analyst | Jochi | Analyst | zai/glm-4.5 | - |
| ops | Ögedei | Operations / Emergency | zai/glm-4.5 | - |

## Agent Details

### Kublai (main)
- **Responsibilities**: Task routing, delegation, inter-agent coordination, final approval
- **Current Model**: moonshot/kimi-k2.5
- **Failover**: Ögedei handles routing when Kublai unavailable
- **Use Cases for Model Switching**:
  - Switch to lighter model for simple routing tasks
  - Switch to stronger model for complex synthesis tasks
  - Failover to backup provider during outages

### Möngke (researcher)
- **Responsibilities**: Deep research, information gathering, fact verification
- **Current Model**: zai/glm-4.5
- **Use Cases for Model Switching**:
  - Switch to larger context window model for large research tasks
  - Switch to faster model for quick lookups
  - Use reasoning-capable model for complex analysis

### Chagatai (writer)
- **Responsibilities**: Content creation, documentation, communication
- **Current Model**: moonshot/kimi-k2.5
- **Use Cases for Model Switching**:
  - Switch to creative-focused model for marketing content
  - Switch to technical model for documentation
  - Use multilingual model for non-English content

### Temüjin (developer)
- **Responsibilities**: Code review, security audits, implementation
- **Current Model**: zai/glm-4.7 (strongest coding model)
- **Use Cases for Model Switching**:
  - Keep on strongest available model for security audits
  - Switch to specialized model for specific languages (e.g., Rust, Haskell)
  - Use reasoning model for architecture decisions

### Jochi (analyst)
- **Responsibilities**: Performance analysis, metrics, optimization
- **Current Model**: zai/glm-4.5
- **Use Cases for Model Switching**:
  - Switch to model with tool use for data processing
  - Use reasoning model for root cause analysis
  - Switch to cost-effective model for bulk processing

### Ögedei (ops)
- **Responsibilities**: Operations, monitoring, emergency response
- **Current Model**: zai/glm-4.5
- **Failover Role**: Takes over for Kublai when unavailable
- **Use Cases for Model Switching**:
  - Switch to fastest available model for emergency response
  - Use reliable model during incident management
  - Failover configuration requires compatible capability with Kublai

## Model Provider Mapping

### Anthropic Models
| Model | Provider ID | Best For |
|-------|-------------|----------|
| claude-opus-4 | anthropic | Complex reasoning, analysis |
| claude-sonnet-4 | anthropic | Balanced performance |
| claude-haiku-4 | anthropic | Fast responses, cost efficiency |

### Z.AI Models (via Proxy)
| Model | Provider ID | Best For |
|-------|-------------|----------|
| zai/glm-4.7 | zai | Coding, technical tasks |
| zai/glm-4.5 | zai | General purpose |
| zai/glm-4-flash | zai | Fast, cost-effective |

### Moonshot Models
| Model | Provider ID | Best For |
|-------|-------------|----------|
| moonshot/kimi-k2.5 | moonshot | Long context, writing |

### OpenRouter Models
| Model | Provider ID | Best For |
|-------|-------------|----------|
| openrouter/anthropic/claude-sonnet-4 | openrouter | Backup provider access |

## Environment Variables

Required for model switching:
- `ANTHROPIC_API_KEY` - For Anthropic models
- `OPENROUTER_API_KEY` - For OpenRouter models
- `ANTHROPIC_BASE_URL` - For Z.AI proxy (set to Z.AI endpoint)
- `OPENCLAW_GATEWAY_TOKEN` - For agent communication

## Configuration Files

### moltbot.json
Path: `/data/.clawdbot/moltbot.json` (production) or `moltbot.json` (local)

Contains agent definitions with model assignments:
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
Path: `/data/.clawdbot/openclaw.json` (production) or `~/.openclaw/openclaw.json` (local)

Contains provider and model definitions with API configuration.

## Switching Guidelines

### Emergency Failover
1. Check provider status
2. Switch all agents to backup provider
3. Verify API keys for backup provider
4. Deploy and monitor

### A/B Testing
1. Switch one agent to test model
2. Run representative tasks
3. Evaluate performance
4. Rollback or promote based on results

### Cost Optimization
1. Identify low-priority agents
2. Switch to cost-effective models during off-peak
3. Monitor quality metrics
4. Adjust as needed

### Security Audit Mode
1. Switch Temüjin to strongest available model
2. Enable additional logging
3. Run security audit
4. Return to normal model after completion
