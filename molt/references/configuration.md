# Moltbot Configuration Reference

This document provides a complete reference for the `moltbot.json` configuration file.

**Related documentation:**
- [Environment Variables](environment-variables.md) - All supported environment variables
- [Channel Setup Guide](channel-setup.md) - Per-channel setup instructions
- [Security Checklist](security-checklist.md) - Security audit and hardening

## File Location

On Railway deployments: `/data/.clawdbot/moltbot.json`

The file uses JSON5 format, which allows:
- Comments (`//` and `/* */`)
- Trailing commas
- Unquoted keys
- Single-quoted strings

## Configuration Schema

### Gateway Settings

```json5
{
  "gateway": {
    // Server mode: "local" for development, "remote" for Railway/production
    "mode": "remote",

    // Port configuration (Railway manages external port)
    "port": 18789,

    // Binding mode: "loopback", "lan", "tailnet", or custom
    "bind": "loopback",

    // Authentication (required for non-loopback binds)
    "auth": {
      "mode": "token",  // "token" or "password"
      "token": "${CLAWDBOT_GATEWAY_TOKEN}"
    },

    // Control UI settings
    "controlUi": {
      "enabled": true,
      "allowInsecureAuth": false  // Set true if not using HTTPS
    },

    // Tailscale integration (optional)
    "tailscale": {
      "serve": false,
      "funnel": false
    }
  }
}
```

### Agent Configuration

```json5
{
  "agents": {
    "defaults": {
      // Workspace directory for file operations
      "workspace": "/data/workspace",

      // Model configuration
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": [
          "openai/gpt-4o",
          "openrouter/anthropic/claude-3.5-sonnet"
        ]
      },

      // Sandbox settings for non-main sessions
      "sandbox": {
        "enabled": false,
        "docker": {
          "image": "node:22-slim",
          "setupCommand": "apt-get update && apt-get install -y python3"
        }
      }
    },

    // Multiple isolated agents (optional)
    "list": [
      {
        "id": "main",
        "name": "Main Agent",
        "workspace": "/data/workspace"
      },
      {
        "id": "sandbox",
        "name": "Sandbox Agent",
        "workspace": "/data/sandbox-workspace",
        "sandbox": { "enabled": true }
      }
    ]
  }
}
```

### Channel Configuration

```json5
{
  "channels": {
    // WhatsApp
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+15555550123", "+15555550456"],
      "groups": {
        "*": { "requireMention": true },
        "specific-group-id": { "requireMention": false }
      }
    },

    // Telegram
    "telegram": {
      "enabled": true,
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "allowFrom": ["tg:123456789"],
      "groups": {
        "*": { "requireMention": true }
      },
      "webhookUrl": "https://your-domain.railway.app/telegram/webhook"
    },

    // Discord
    "discord": {
      "enabled": true,
      "token": "${DISCORD_BOT_TOKEN}",
      "allowFrom": ["discord:123456789"],
      "guilds": {
        "*": { "requireMention": true }
      }
    },

    // Slack
    "slack": {
      "enabled": true,
      "botToken": "${SLACK_BOT_TOKEN}",
      "appToken": "${SLACK_APP_TOKEN}",
      "allowFrom": ["slack:U123456789"]
    },

    // Signal
    "signal": {
      "enabled": true,
      "allowFrom": ["+15555550123"],
      "groups": {
        "*": { "requireMention": true }
      }
    },

    // Note: For multiple accounts per channel, see Channel Setup Guide
  }
}
```

### Session Configuration

```json5
{
  "session": {
    // Session scope: "per-sender" groups by user
    "scope": "per-sender",

    // Session reset behavior
    "reset": {
      "mode": "daily",  // "daily" or "idle"
      "idleMinutes": 60  // For "idle" mode
    },

    // DM session grouping
    "dmScope": "per-sender"
  }
}
```

### Skills Configuration

```json5
{
  "skills": {
    // Skill loading settings
    "load": {
      "watch": true,  // Auto-refresh on changes
      "watchDebounceMs": 250,
      "extraDirs": ["/custom/skills"]  // Additional skill directories
    },

    // Per-skill configuration
    "entries": {
      "weather": {
        "enabled": true,
        "apiKey": "your-weather-api-key"
      },
      "github": {
        "enabled": true,
        "env": {
          "GITHUB_TOKEN": "ghp_..."
        }
      },
      "disabled-skill": {
        "enabled": false
      }
    },

    // Allowlist for bundled skills only
    "allowBundled": ["weather", "github", "notion"]
  }
}
```

### Environment Variables in Config

```json5
{
  "env": {
    // Variables set only if not already defined
    "CUSTOM_VAR": "value",
    "ANOTHER_VAR": "another-value"
  },

  // Shell environment import
  "shellEnv": {
    "enabled": false,
    "timeoutMs": 15000
  }
}
```

### Tool Policies

```json5
{
  "tools": {
    // Allow/deny specific tools
    "allow": ["shell", "browser", "file"],
    "deny": ["dangerous-tool"],

    // Tool groups
    "groups": {
      "filesystem": ["file_read", "file_write", "file_delete"],
      "network": ["http_request", "browser"]
    }
  }
}
```

### Cron Jobs

```json5
{
  "cron": {
    "jobs": [
      {
        "name": "daily-summary",
        "schedule": "0 9 * * *",  // 9 AM daily
        "agent": "main",
        "prompt": "Send me a daily summary"
      }
    ]
  }
}
```

### Webhooks

```json5
{
  "webhooks": {
    "gmail": {
      "enabled": true,
      "endpoint": "/webhooks/gmail"
    },
    "custom": {
      "enabled": true,
      "endpoint": "/webhooks/custom",
      "secret": "${WEBHOOK_SECRET}"
    }
  }
}
```

## Complete Example Configuration

```json5
{
  // Gateway settings for Railway
  "gateway": {
    "mode": "remote",
    "auth": {
      "mode": "token",
      "token": "${CLAWDBOT_GATEWAY_TOKEN}"
    }
  },

  // Agent configuration
  "agents": {
    "defaults": {
      "workspace": "/data/workspace",
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": ["openai/gpt-4o"]
      }
    }
  },

  // Channel configuration
  "channels": {
    "signal": {
      "enabled": true,
      "allowFrom": ["+15555550123"],
      "groups": {
        "*": { "requireMention": true }
      }
    },
    "telegram": {
      "enabled": true,
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "allowFrom": ["tg:123456789"]
    }
  },

  // Session settings
  "session": {
    "scope": "per-sender",
    "reset": { "mode": "daily" }
  },

  // Skills
  "skills": {
    "load": { "watch": true },
    "entries": {
      "weather": { "enabled": true },
      "github": {
        "enabled": true,
        "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
      }
    }
  }
}
```

## Configuration Validation

Run `moltbot doctor` to validate configuration:

```bash
moltbot doctor
```

Common validation errors:
- Unknown keys (typos in config)
- Invalid types (string where number expected)
- Missing required fields
- Invalid model names

## Hot Reloading

Some configuration changes take effect immediately:
- Skill enable/disable
- Channel allowlists
- Session settings

Others require gateway restart:
- Gateway mode/port/auth changes
- Agent model changes
- Sandbox configuration
