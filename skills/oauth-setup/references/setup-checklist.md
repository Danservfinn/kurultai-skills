# OAuth Setup Detailed Checklists

## Google OAuth Complete Checklist

### Google Cloud Console Setup
- [ ] Log into Google Cloud Console (console.cloud.google.com)
- [ ] Create new project or select existing project
- [ ] Note the Project ID for reference

### OAuth Consent Screen Configuration
- [ ] Navigate to APIs & Services → OAuth consent screen
- [ ] Select user type (External or Internal)
- [ ] Fill in App information:
  - [ ] App name (shown to users during consent)
  - [ ] User support email (must be yours or a Google Group you own)
  - [ ] App logo (optional, 120x120px recommended)
- [ ] Add authorized domains if applicable
- [ ] Fill in Developer contact information
- [ ] Save and continue to Scopes

### Scopes Configuration
- [ ] Click "Add or Remove Scopes"
- [ ] Select required scopes:
  - [ ] `.../auth/userinfo.email`
  - [ ] `.../auth/userinfo.profile`
  - [ ] `openid`
- [ ] Save and continue

### Test Users (for External apps)
- [ ] Add email addresses of users who can test the app
- [ ] Users must have Google accounts
- [ ] Save and continue

### Create OAuth Credentials
- [ ] Go to APIs & Services → Credentials
- [ ] Click "Create Credentials" → "OAuth client ID"
- [ ] Select "Web application" as application type
- [ ] Enter name for the OAuth client
- [ ] Add Authorized JavaScript origins:
  - [ ] `https://your-production-domain.com`
  - [ ] `http://localhost:3000` (for development)
- [ ] Add Authorized redirect URIs:
  - [ ] `https://your-production-domain.com/api/auth/callback/google`
  - [ ] `http://localhost:3000/api/auth/callback/google` (for development)
- [ ] Click "Create"
- [ ] Copy and securely store Client ID
- [ ] Copy and securely store Client Secret

## Facebook OAuth Complete Checklist

### Meta for Developers Setup
- [ ] Log into Meta for Developers (developers.facebook.com)
- [ ] Click "My Apps" in top navigation
- [ ] Click "Create App"
- [ ] Select use case: "Authenticate and request data from users with Facebook Login"
- [ ] Select app type: "Consumer" (most common for web apps)
- [ ] Enter App display name
- [ ] Enter App contact email
- [ ] Complete creation

### Facebook Login Configuration
- [ ] In app dashboard, click "Use cases" in left sidebar
- [ ] Find "Facebook Login" section
- [ ] Click "Customize" button
- [ ] Navigate to "Settings" tab
- [ ] Enter Valid OAuth Redirect URIs:
  - [ ] `https://your-production-domain.com/api/auth/callback/facebook`
- [ ] Click "Save changes"

### Permissions Setup
- [ ] Go to Use cases → Customize → Permissions and features tab
- [ ] Locate "email" permission in the list
- [ ] Click "+ Add" button next to email
- [ ] Verify status shows "Ready for testing"
- [ ] Verify "public_profile" shows "Ready for testing"

### Get App Credentials
- [ ] Go to App settings → Basic in left sidebar
- [ ] Copy App ID (displayed at top)
- [ ] Click "Show" next to App Secret
- [ ] Enter Facebook account password to verify
- [ ] Copy App Secret

### Add Test Users (Development Mode)
- [ ] Go to App Roles → Roles in left sidebar
- [ ] Click "Add People" under Testers section
- [ ] Enter Facebook usernames or IDs
- [ ] Testers must accept the invitation from their Facebook account

### Optional: Business Verification (for Production)
- [ ] Go to App Settings → Basic
- [ ] Scroll to Business Verification section
- [ ] Complete business verification if going public
- [ ] Submit for App Review when ready

## Environment Variables Checklist

### Local Development (.env.local)
```env
# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Facebook OAuth
FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=  # Generate with: openssl rand -base64 32
```

### Production (Vercel/Hosting Provider)
- [ ] GOOGLE_CLIENT_ID added
- [ ] GOOGLE_CLIENT_SECRET added
- [ ] FACEBOOK_CLIENT_ID added
- [ ] FACEBOOK_CLIENT_SECRET added
- [ ] NEXTAUTH_URL set to production URL
- [ ] NEXTAUTH_SECRET set (unique random string)
- [ ] Redeploy after adding variables

## Testing Checklist

### Local Testing
- [ ] Start development server
- [ ] Navigate to sign-in page
- [ ] Test Google OAuth flow
- [ ] Test Facebook OAuth flow
- [ ] Verify user data is returned correctly
- [ ] Check for any console errors

### Production Testing
- [ ] Deploy to staging/preview environment
- [ ] Update redirect URIs if using different domain
- [ ] Test Google OAuth flow
- [ ] Test Facebook OAuth flow
- [ ] Verify session persists correctly
- [ ] Test sign-out functionality

## Troubleshooting Reference

### Google OAuth Issues

**Error: redirect_uri_mismatch**
- Verify redirect URI in Google Console matches exactly (including trailing slashes)
- Check for http vs https mismatch
- Ensure the domain is authorized in OAuth consent screen

**Error: access_denied**
- User not added as test user (for apps in testing mode)
- App not verified (for production apps)
- User denied consent

**Error: invalid_client**
- Client ID or Secret is incorrect
- Credentials from wrong project
- Environment variables not loaded

### Facebook OAuth Issues

**Error: Invalid Scopes: email**
- Navigate to Use cases → Permissions and features
- Add email permission
- Wait a few minutes for changes to propagate

**Error: URL blocked**
- Add exact callback URL to Facebook Login settings
- Check for trailing slashes
- Verify domain matches exactly

**Error: App not setup**
- Complete Facebook Login product setup
- Ensure app is not disabled
- Check app status in dashboard

**Error: Can't load URL**
- Domain not verified in app settings
- App is in development mode and user is not a tester
- Redirect URI not properly configured
