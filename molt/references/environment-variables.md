# Moltbot Environment Variables Reference

This document provides a complete reference for all environment variables used in Moltbot Railway deployments.

**Related documentation:**
- [Configuration Reference](configuration.md) - Full moltbot.json schema
- [Channel Setup Guide](channel-setup.md) - Per-channel setup instructions
- [Security Checklist](security-checklist.md) - Security audit and hardening

## Railway-Specific Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SETUP_PASSWORD` | Yes | - | Password protecting the `/setup` wizard |
| `PORT` | No | `8080` | External port exposed by Railway |
| `CLAWDBOT_STATE_DIR` | No | `/data/.clawdbot` | Configuration and credentials storage |
| `CLAWDBOT_WORKSPACE_DIR` | No | `/data/workspace` | Workspace file storage |
| `CLAWDBOT_GATEWAY_TOKEN` | **Yes** | - | Gateway authentication token (generate with `openssl rand -base64 48`) |
| `INTERNAL_GATEWAY_HOST` | No | `127.0.0.1` | Internal gateway host |
| `INTERNAL_GATEWAY_PORT` | No | `18789` | Internal gateway port |
| `CLAWDBOT_ENTRY` | No | `/clawdbot/dist/entry.js` | Node.js entry point |

## AI Provider Variables

### Anthropic (Recommended)

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key starting with `sk-ant-...` |

### OpenAI

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key starting with `sk-...` |
| `OPENAI_ORG_ID` | Optional organization ID |

### OpenRouter

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | API key starting with `sk-or-...` |

### Google (Gemini)

| Variable | Description |
|----------|-------------|
| `GOOGLE_AI_API_KEY` | Google AI API key |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID (for Vertex AI) |

### Groq

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | API key starting with `gsk-...` |

## Channel Variables

### Telegram

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather (format: `123456:ABC...`) |
| `TELEGRAM_WEBHOOK_URL` | Optional webhook URL for receiving updates |

### Discord

| Variable | Description |
|----------|-------------|
| `DISCORD_BOT_TOKEN` | Bot token from Discord Developer Portal |
| `DISCORD_CLIENT_ID` | Application client ID (for OAuth) |
| `DISCORD_CLIENT_SECRET` | Application client secret (for OAuth) |

### Slack

| Variable | Description |
|----------|-------------|
| `SLACK_BOT_TOKEN` | Bot token starting with `xoxb-...` |
| `SLACK_APP_TOKEN` | App-level token starting with `xapp-...` |
| `SLACK_SIGNING_SECRET` | Request signing secret |

### Signal

Signal does not use environment variables for authentication. Configuration is done through the Control UI via QR code linking.

### WhatsApp

WhatsApp does not use environment variables for authentication. Configuration is done through the Control UI via QR code scanning.

## Voice & Speech Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | ElevenLabs API key for text-to-speech |
| `ELEVENLABS_VOICE_ID` | Default voice ID |

## Search & Web Variables

| Variable | Description |
|----------|-------------|
| `BRAVE_SEARCH_API_KEY` | Brave Search API key for web search |
| `SERPER_API_KEY` | Serper API key (alternative search) |

## Gateway Configuration Variables

| Variable | Description |
|----------|-------------|
| `CLAWDBOT_CONFIG_PATH` | Custom path to `moltbot.json` |
| `CLAWDBOT_LOAD_SHELL_ENV` | Set to `1` to import shell environment |
| `CLAWDBOT_SHELL_ENV_TIMEOUT_MS` | Shell import timeout (default: 15000) |

## Loading Precedence

Moltbot loads environment variables in this order (later sources do not override earlier ones):

1. Process environment (from Railway dashboard)
2. `.env` in current working directory
3. Global `.env` at `~/.clawdbot/.env` (or `$CLAWDBOT_STATE_DIR/.env`)
4. Config `env` block in `moltbot.json`
5. Optional login-shell import (if `CLAWDBOT_LOAD_SHELL_ENV=1`)

## Variable Substitution

Configuration files support `${VAR_NAME}` syntax for dynamic value injection:

```json5
{
  "channels": {
    "telegram": {
      "botToken": "${TELEGRAM_BOT_TOKEN}"
    }
  }
}
```

## Security Notes

- Never commit API keys or tokens to version control
- Use Railway's secret management for sensitive values
- Rotate tokens periodically, especially after potential exposure
- Use the minimum required permissions for each API key
