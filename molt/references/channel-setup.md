# Channel Setup Guide

This document provides detailed setup instructions for each messaging channel supported by Moltbot.

**Related documentation:**
- [Configuration Reference](configuration.md) - Full moltbot.json schema
- [Environment Variables](environment-variables.md) - All supported environment variables
- [Security Checklist](security-checklist.md) - Security audit and hardening

## Signal

Signal provides end-to-end encrypted messaging and is configured via device linking.

### Prerequisites

- Signal installed on your phone
- Phone number registered with Signal

### Setup Steps

1. **Access Control UI**
   - Navigate to `https://<your-railway-domain>/`
   - Login with your setup credentials

2. **Link Signal Device**
   - Go to Channels > Signal
   - Click "Link Device" to generate QR code
   - On your phone: Signal > Settings > Linked Devices > Link New Device
   - Scan the QR code with your phone

3. **Configure Access Controls**

   Edit `/data/.clawdbot/moltbot.json`:
   ```json5
   {
     "channels": {
       "signal": {
         "enabled": true,
         // Allow specific phone numbers
         "allowFrom": ["+15555550123", "+15555550456"],
         // Group settings
         "groups": {
           // Require @mention in all groups
           "*": { "requireMention": true },
           // Allow specific group without mention
           "group-id-here": { "requireMention": false }
         }
       }
     }
   }
   ```

4. **Test Connection**
   - Send a message from your allowed phone number
   - Verify Moltbot responds

### Troubleshooting

- **Device not linking**: Ensure your phone has internet connectivity
- **Messages not received**: Check `allowFrom` list includes your number
- **Group messages ignored**: Verify group settings and mention requirements

---

## Discord

Discord requires creating a bot application in the Discord Developer Portal.

### Prerequisites

- Discord account
- Server where you have admin permissions (to invite the bot)

### Setup Steps

1. **Create Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Name your application and create it

2. **Configure Bot**
   - Navigate to "Bot" section
   - Click "Add Bot"
   - Under "Privileged Gateway Intents", enable:
     - **MESSAGE CONTENT INTENT** (required)
     - SERVER MEMBERS INTENT (optional)
     - PRESENCE INTENT (optional)

3. **Get Bot Token**
   - In Bot section, click "Reset Token"
   - Copy the token (store securely, shown only once)

4. **Set Environment Variable**

   In Railway dashboard, add:
   ```
   DISCORD_BOT_TOKEN=your-bot-token-here
   ```

5. **Invite Bot to Server**
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Read Message History`, `Add Reactions`
   - Copy generated URL and open it
   - Select your server and authorize

6. **Configure in moltbot.json** (optional)
   ```json5
   {
     "channels": {
       "discord": {
         "enabled": true,
         "token": "${DISCORD_BOT_TOKEN}",
         // Allow specific users
         "allowFrom": ["discord:user-id-here"],
         // Guild (server) settings
         "guilds": {
           "*": { "requireMention": true }
         }
       }
     }
   }
   ```

### Troubleshooting

- **Error 4014**: MESSAGE CONTENT INTENT not enabled in Developer Portal
- **Bot not responding**: Verify token is correct and bot is in the server
- **Permission errors**: Check bot role has necessary permissions

---

## Telegram

Telegram bots are created through BotFather and configured via bot token.

### Prerequisites

- Telegram account
- Telegram app installed

### Setup Steps

1. **Create Bot with BotFather**
   - Open Telegram and search for @BotFather
   - Send `/newbot`
   - Follow prompts to name your bot
   - Copy the bot token provided

2. **Set Environment Variable**

   In Railway dashboard, add:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

3. **Configure in moltbot.json**
   ```json5
   {
     "channels": {
       "telegram": {
         "enabled": true,
         "botToken": "${TELEGRAM_BOT_TOKEN}",
         // Allow specific Telegram user IDs
         "allowFrom": ["tg:123456789"],
         // Group settings
         "groups": {
           "*": { "requireMention": true }
         },
         // Optional: webhook for better reliability
         "webhookUrl": "https://your-domain.railway.app/telegram/webhook"
       }
     }
   }
   ```

4. **Find Your Telegram User ID**
   - Message @userinfobot on Telegram
   - Use the ID in `allowFrom` with `tg:` prefix

5. **Start Conversation**
   - Search for your bot by username
   - Send `/start` to initiate

### Troubleshooting

- **Bot not responding**: Verify token is valid with BotFather
- **Webhook errors**: Ensure Railway domain has valid HTTPS certificate
- **Group messages missed**: Check group permissions and mention settings

---

## WhatsApp

WhatsApp uses the WhatsApp Web protocol and requires QR code linking.

### Prerequisites

- WhatsApp installed on your phone
- Active WhatsApp account
- Recommended: Dedicated phone number for the bot

### Setup Steps

1. **Access Control UI**
   - Navigate to `https://<your-railway-domain>/`
   - Login with your setup credentials

2. **Link WhatsApp Device**
   - Go to Channels > WhatsApp
   - Click "Connect" to display QR code
   - On your phone: WhatsApp > Settings > Linked Devices > Link a Device
   - Scan the QR code

3. **Configure Access Controls**
   ```json5
   {
     "channels": {
       "whatsapp": {
         "enabled": true,
         // Allow specific phone numbers (include country code)
         "allowFrom": ["+15555550123", "+15555550456"],
         // Group settings
         "groups": {
           "*": { "requireMention": true }
         }
       }
     }
   }
   ```

4. **Test Connection**
   - Send a message from an allowed number
   - Verify response

### Important Notes

- WhatsApp Web sessions may disconnect periodically
- Re-scan QR code if connection is lost
- Using a dedicated number prevents conflicts with personal WhatsApp

### Troubleshooting

- **QR code not loading**: Check gateway is running
- **Frequent disconnects**: WhatsApp may flag unusual activity; use dedicated number
- **Messages not received**: Verify phone number format includes country code

---

## Slack

Slack requires creating a Slack App with bot and app tokens.

### Prerequisites

- Slack workspace where you have admin permissions
- Permission to create Slack apps

### Setup Steps

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Click "Create New App" > "From scratch"
   - Name your app and select workspace

2. **Configure Bot Token Scopes**
   - Go to OAuth & Permissions
   - Add these Bot Token Scopes:
     - `chat:write`
     - `channels:history`
     - `groups:history`
     - `im:history`
     - `mpim:history`
     - `users:read`

3. **Enable Socket Mode**
   - Go to Socket Mode
   - Enable Socket Mode
   - Create an App-Level Token with `connections:write` scope
   - Copy this token (starts with `xapp-`)

4. **Install to Workspace**
   - Go to Install App
   - Click "Install to Workspace"
   - Authorize the permissions
   - Copy Bot User OAuth Token (starts with `xoxb-`)

5. **Set Environment Variables**

   In Railway dashboard, add:
   ```
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_APP_TOKEN=xapp-...
   ```

6. **Configure in moltbot.json**
   ```json5
   {
     "channels": {
       "slack": {
         "enabled": true,
         "botToken": "${SLACK_BOT_TOKEN}",
         "appToken": "${SLACK_APP_TOKEN}",
         // Allow specific Slack user IDs
         "allowFrom": ["slack:U123456789"]
       }
     }
   }
   ```

### Troubleshooting

- **App not connecting**: Verify Socket Mode is enabled
- **Permission errors**: Check all required scopes are added
- **Messages not received**: Ensure app is installed to workspace

---

## Multiple Accounts

Moltbot supports multiple accounts per channel for different use cases.

### Configuration Example

```json5
{
  "channels": {
    "telegram": {
      "accounts": {
        "default": {
          "name": "Primary Bot",
          "botToken": "${TELEGRAM_BOT_TOKEN_PRIMARY}"
        },
        "alerts": {
          "name": "Alerts Bot",
          "botToken": "${TELEGRAM_BOT_TOKEN_ALERTS}"
        },
        "team": {
          "name": "Team Bot",
          "botToken": "${TELEGRAM_BOT_TOKEN_TEAM}"
        }
      }
    }
  }
}
```

Each account operates independently with its own:
- Authentication credentials
- Allowlists
- Session handling

---

## Access Control Patterns

### Allow Specific Users Only

```json5
{
  "channels": {
    "telegram": {
      "allowFrom": ["tg:123", "tg:456"]
    }
  }
}
```

### Allow All DMs, Restrict Groups

```json5
{
  "channels": {
    "telegram": {
      "allowFrom": ["*"],
      "groups": {
        "*": { "requireMention": true }
      }
    }
  }
}
```

### Require Mention in All Contexts

```json5
{
  "channels": {
    "telegram": {
      "allowFrom": ["*"],
      "groups": {
        "*": { "requireMention": true }
      },
      "dms": {
        "requireMention": true
      }
    }
  }
}
```

### Open Access (Not Recommended)

```json5
{
  "channels": {
    "telegram": {
      "allowFrom": ["*"],
      "groups": {
        "*": { "requireMention": false }
      }
    }
  }
}
```

**Warning**: Open access exposes your bot to anyone. Use with caution and monitor usage.
