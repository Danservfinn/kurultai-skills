---
name: oauth-setup
description: This skill guides through setting up OAuth authentication (Google and Facebook) for Next.js applications using NextAuth.js v5. Use when setting up social login, configuring OAuth providers, or troubleshooting authentication issues. Covers creating developer apps, configuring credentials, and setting up environment variables.
---

# OAuth Setup for Next.js with NextAuth.js

## Overview

This skill provides step-by-step guidance for configuring OAuth authentication providers (Google and Facebook) in Next.js applications using NextAuth.js v5. It covers the complete workflow from creating developer applications to testing the OAuth flow.

## Prerequisites

Before starting OAuth setup, ensure:
- Next.js application with NextAuth.js v5 installed
- Access to Google Cloud Console and Meta for Developers
- Production domain (for OAuth redirect URIs)

## Quick Reference

### OAuth Redirect URI Format
```
https://{your-domain}/api/auth/callback/{provider}
```

Examples:
- Google: `https://myapp.vercel.app/api/auth/callback/google`
- Facebook: `https://myapp.vercel.app/api/auth/callback/facebook`

### Required Environment Variables
```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Facebook OAuth
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret

# NextAuth
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=your_random_secret_string
```

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Navigate to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Google+ API (if not already enabled)

### Step 2: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select User Type:
   - **External**: For public apps (requires verification for production)
   - **Internal**: For Google Workspace users only
3. Fill in required fields:
   - App name
   - User support email
   - Developer contact email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users (required for external apps in testing)

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Web application**
4. Configure:
   - Name: Your app name
   - Authorized JavaScript origins: `https://your-domain.com`
   - Authorized redirect URIs: `https://your-domain.com/api/auth/callback/google`
5. Copy **Client ID** and **Client Secret**

### Step 4: Add to Environment Variables

Add to your `.env.local` or hosting provider:
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

### Google OAuth Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `redirect_uri_mismatch` | Callback URL doesn't match | Verify redirect URI in Google Console matches exactly |
| `access_denied` | User not in test users list | Add user email to OAuth consent screen test users |
| `invalid_client` | Wrong credentials | Double-check Client ID and Secret |

## Facebook OAuth Setup

### Step 1: Create Facebook App

1. Navigate to [Meta for Developers](https://developers.facebook.com)
2. Click **My Apps** → **Create App**
3. Select use case: **Authenticate and request data from users with Facebook Login**
4. Select app type: **Consumer** (or appropriate type)
5. Enter app name and contact email
6. Complete app creation

### Step 2: Configure Facebook Login

1. In your app dashboard, find **Use cases** in the sidebar
2. Click **Customize** next to **Facebook Login**
3. Go to **Settings** tab
4. Add **Valid OAuth Redirect URIs**:
   ```
   https://your-domain.com/api/auth/callback/facebook
   ```
5. Click **Save changes**

### Step 3: Add Email Permission

1. Go to **Use cases** → **Customize** → **Permissions and features**
2. Find **email** permission
3. Click **+ Add** to enable email permission
4. Status should show "Ready for testing"

### Step 4: Get App Credentials

1. Go to **App settings** → **Basic**
2. Copy **App ID** (this is your `FACEBOOK_CLIENT_ID`)
3. Click **Show** next to App Secret (requires password verification)
4. Copy **App Secret** (this is your `FACEBOOK_CLIENT_SECRET`)

### Step 5: Add to Environment Variables

Add to your `.env.local` or hosting provider:
```env
FACEBOOK_CLIENT_ID=your_app_id_here
FACEBOOK_CLIENT_SECRET=your_app_secret_here
```

### Facebook OAuth Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid Scopes: email` | Email permission not added | Add email permission in Use cases → Permissions |
| `App not setup` | Facebook Login not configured | Complete Facebook Login setup in Use cases |
| `URL blocked` | Redirect URI not whitelisted | Add exact callback URL in Facebook Login settings |
| `Can't load URL` | Domain not verified | Verify domain in App settings → Basic |

### Facebook Development vs Production Mode

**Development Mode** (default):
- Only app developers and testers can log in
- Add testers in **App Roles** → **Roles**
- Good for testing before launch

**Production Mode** (requires App Review):
- All users can log in
- Submit for App Review in **App Review** → **Requests**
- Required permissions: `email`, `public_profile`

## NextAuth.js Configuration

### Basic Provider Setup

```typescript
// src/lib/auth.ts
import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import FacebookProvider from "next-auth/providers/facebook"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    FacebookProvider({
      clientId: process.env.FACEBOOK_CLIENT_ID!,
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET!,
    }),
  ],
  // Add session strategy, callbacks, etc. as needed
})
```

### API Route Handler

```typescript
// src/app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/lib/auth"

export const { GET, POST } = handlers
```

## Deployment Checklist

Before deploying OAuth to production:

- [ ] All environment variables set in hosting provider
- [ ] OAuth redirect URIs updated to production domain
- [ ] Google OAuth consent screen configured
- [ ] Facebook email permission added
- [ ] Test OAuth flow on staging/preview deployment
- [ ] (Optional) Submit Facebook app for review if going public

## Vercel-Specific Setup

When deploying to Vercel:

1. Go to Project Settings → Environment Variables
2. Add all OAuth credentials
3. Redeploy to apply new environment variables
4. Update OAuth redirect URIs to use `*.vercel.app` domain

## Common Patterns

### Adding OAuth Buttons to Sign-in Page

```tsx
// Sign-in page component
import { signIn } from "next-auth/react"

export function SignInButtons() {
  return (
    <div>
      <button onClick={() => signIn("google")}>
        Continue with Google
      </button>
      <button onClick={() => signIn("facebook")}>
        Continue with Facebook
      </button>
    </div>
  )
}
```

### Handling OAuth Errors

```typescript
// In NextAuth config
pages: {
  signIn: "/auth/signin",
  error: "/auth/signin", // Redirect errors to signin page
}
```

## Resources

- [NextAuth.js Documentation](https://authjs.dev)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
