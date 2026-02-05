# Moltbot Security Checklist & Hardening Guide

This document provides comprehensive security audit checklists and hardening procedures for Moltbot deployments.

**Related documentation:**
- [Configuration Reference](configuration.md) - Full moltbot.json schema
- [Environment Variables](environment-variables.md) - All supported environment variables
- [Channel Setup Guide](channel-setup.md) - Per-channel setup instructions

## Pre-Deployment Security Checklist

Complete before making Moltbot accessible:

### Credential Security
- [ ] All API keys generated with sufficient entropy (min 32 chars)
- [ ] `SETUP_PASSWORD` is unique, not reused from other services
- [ ] `CLAWDBOT_GATEWAY_TOKEN` generated using `openssl rand -base64 48`
- [ ] No credentials committed to any git repository
- [ ] No credentials visible in deployment logs
- [ ] All credentials stored only in Railway environment variables

### Network Security
- [ ] HTTPS enforced (Railway provides automatically)
- [ ] No HTTP fallback configured
- [ ] Gateway authentication mode set to `token`
- [ ] `allowInsecureAuth` set to `false`
- [ ] No unnecessary ports exposed

### Access Control
- [ ] All channel `allowFrom` lists are explicit (no wildcards)
- [ ] Group messages require mention (`requireMention: true`)
- [ ] Railway project access limited to necessary team members
- [ ] 2FA enabled on Railway account
- [ ] 2FA enabled on all AI provider accounts

## Post-Deployment Security Audit

Run after initial setup and periodically (weekly recommended):

### Gateway Security
```bash
# Check gateway authentication status
moltbot gateway status

# Verify auth is required
# Output should show: auth.mode = "token"
```

- [ ] Gateway requires authentication
- [ ] No anonymous access possible
- [ ] Control UI protected by auth token
- [ ] WebSocket connections require auth

### Configuration Audit
```bash
# Run full security audit
moltbot security audit --deep

# Check for config issues
moltbot doctor
```

- [ ] No plaintext credentials in `moltbot.json`
- [ ] All secrets use `${VAR_NAME}` substitution
- [ ] No overly permissive allowlists
- [ ] Sandboxing enabled for non-main sessions

### Session Security
```bash
# List active sessions
moltbot status --all
```

- [ ] No unexpected active sessions
- [ ] Session reset configured (daily or idle-based)
- [ ] Session files not world-readable

### Log Audit
```bash
# Review recent logs for anomalies
railway logs --deployment | grep -i "error\|warn\|auth\|denied"
```

- [ ] No failed authentication attempts from unknown sources
- [ ] No unusual error patterns
- [ ] No credential leaks in logs
- [ ] No unexpected IP addresses

## Channel-Specific Security

### Signal Security
- [ ] Using dedicated Signal account (not personal)
- [ ] Linked device list reviewed (remove unknown devices)
- [ ] `allowFrom` contains only trusted numbers
- [ ] Groups require mention

### Discord Security
- [ ] Bot token stored only in environment variables
- [ ] Bot invited with minimal permissions (no Administrator)
- [ ] MESSAGE CONTENT INTENT justified and reviewed
- [ ] Guild/channel restrictions configured
- [ ] Bot not in untrusted servers

### Telegram Security
- [ ] Privacy mode enabled via BotFather (`/setprivacy`)
- [ ] Bot token never shared or committed
- [ ] `allowFrom` contains only trusted user IDs
- [ ] Webhook URL uses HTTPS only

### WhatsApp Security
- [ ] Using dedicated phone number (not personal)
- [ ] QR code scanning done on trusted network
- [ ] Linked devices list reviewed periodically
- [ ] `allowFrom` contains only trusted numbers

### Slack Security
- [ ] App uses minimal OAuth scopes
- [ ] Socket Mode preferred over webhooks
- [ ] Bot limited to specific channels
- [ ] Signing secret configured

## Credential Rotation Procedures

### Rotating SETUP_PASSWORD

1. Generate new password:
   ```bash
   openssl rand -base64 24
   ```

2. Update in Railway dashboard:
   - Navigate to your service
   - Go to Variables
   - Update `SETUP_PASSWORD`

3. Redeploy:
   ```bash
   railway redeploy
   ```

4. Verify new password works at `/setup`

### Rotating GATEWAY_TOKEN

1. Generate new token:
   ```bash
   openssl rand -base64 48
   ```

2. Update in Railway dashboard:
   - Update `CLAWDBOT_GATEWAY_TOKEN`

3. Update local CLI config if using remote gateway

4. Redeploy:
   ```bash
   railway redeploy
   ```

5. Verify gateway accepts new token

### Rotating AI Provider API Keys

1. **Anthropic**:
   - Go to https://console.anthropic.com/settings/keys
   - Create new key
   - Update `ANTHROPIC_API_KEY` in Railway
   - Verify Moltbot works
   - Delete old key at Anthropic

2. **OpenAI**:
   - Go to https://platform.openai.com/api-keys
   - Create new key
   - Update `OPENAI_API_KEY` in Railway
   - Verify Moltbot works
   - Delete old key at OpenAI

3. **OpenRouter**:
   - Go to https://openrouter.ai/keys
   - Create new key
   - Update `OPENROUTER_API_KEY` in Railway
   - Verify Moltbot works
   - Delete old key at OpenRouter

### Rotating Channel Tokens

**Discord**:
1. Go to Discord Developer Portal
2. Navigate to your application > Bot
3. Click "Reset Token"
4. Update `DISCORD_BOT_TOKEN` in Railway
5. Redeploy

**Telegram**:
1. Message @BotFather
2. Send `/revoke`
3. Select your bot
4. Copy new token
5. Update `TELEGRAM_BOT_TOKEN` in Railway
6. Redeploy

**Slack**:
1. Go to api.slack.com/apps
2. Navigate to your app
3. Regenerate tokens in OAuth & Permissions
4. Update both `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`
5. Redeploy

## Threat Detection

### Signs of Active Compromise

**Immediate red flags:**
- Messages sent that you didn't initiate
- API usage significantly higher than expected
- Unknown sessions in `moltbot status`
- Configuration changes you didn't make
- New channels connected without your action

**Potential indicators:**
- Unusual response latency
- Unexpected errors in logs
- Memory/CPU spikes without cause
- Network traffic to unknown IPs

### Automated Monitoring

Set up alerts for:

```json5
{
  "monitoring": {
    "alertOn": {
      "failedAuth": true,
      "apiUsageSpike": true,
      "newSession": true,
      "configChange": true
    }
  }
}
```

## Incident Response Playbook

### Severity Levels

**Critical (respond within 5 minutes):**
- Confirmed credential leak
- Unauthorized messages sent
- Active session from unknown source
- API key abuse detected

**High (respond within 1 hour):**
- Suspected credential exposure
- Unusual API usage patterns
- Multiple failed auth attempts
- Configuration tampering suspected

**Medium (respond within 24 hours):**
- Minor configuration drift
- Unexpected session behavior
- Log anomalies

### Response Procedures

**Level: Critical**

1. **Isolate** (0-2 minutes):
   ```bash
   # Stop the service immediately
   railway down
   ```

2. **Revoke** (2-5 minutes):
   - Revoke ALL API keys at providers
   - Regenerate ALL bot tokens
   - Disconnect WhatsApp/Signal from phone

3. **Assess** (5-30 minutes):
   - Download all logs
   - Check API usage dashboards
   - Review message history
   - Identify scope of compromise

4. **Recover** (30+ minutes):
   - Delete Railway volume
   - Generate all new credentials
   - Redeploy with fresh config
   - Re-enable channels one by one

5. **Document**:
   - Timeline of events
   - Indicators of compromise
   - Actions taken
   - Lessons learned

## Hardening Configurations

### Maximum Security Configuration

```json5
{
  "gateway": {
    "mode": "remote",
    "auth": {
      "mode": "token",
      "token": "${CLAWDBOT_GATEWAY_TOKEN}"
    },
    "controlUi": {
      "allowInsecureAuth": false
    },
    // Rate limiting
    "rateLimit": {
      "enabled": true,
      "maxRequestsPerMinute": 30
    }
  },

  "agents": {
    "defaults": {
      // Sandbox ALL sessions
      "sandbox": {
        "enabled": true,
        "docker": {
          "networkMode": "none",
          "readOnlyRootFilesystem": true,
          "dropCapabilities": ["ALL"]
        }
      }
    }
  },

  "channels": {
    "defaults": {
      // Deny all by default
      "allowFrom": [],
      "groups": {
        "*": {
          "requireMention": true,
          "enabled": false  // Disable groups entirely
        }
      }
    }
  },

  "tools": {
    // Restrict dangerous tools
    "deny": [
      "shell_dangerous",
      "file_delete",
      "network_unrestricted"
    ]
  },

  "session": {
    "reset": {
      "mode": "idle",
      "idleMinutes": 30  // Short idle timeout
    },
    // Don't persist sensitive sessions
    "persist": false
  }
}
```

### Tool Restrictions

Limit agent capabilities based on trust level:

```json5
{
  "tools": {
    // Allow only safe tools
    "allow": [
      "file_read",
      "browser_search",
      "calculator"
    ],
    // Block dangerous operations
    "deny": [
      "shell_exec",
      "file_write",
      "network_raw",
      "process_spawn"
    ]
  }
}
```

## Security Resources

### External Resources
- Moltbot Security Advisories: Check GitHub releases
- Railway Security: https://railway.app/security
- Anthropic API Security: https://docs.anthropic.com/security

### Reporting Security Issues
- Moltbot: security@molt.bot or GitHub Security Advisories
- Railway: security@railway.app

### Security Update Notifications
- Watch Moltbot GitHub releases
- Subscribe to Railway status updates
- Monitor AI provider security blogs
