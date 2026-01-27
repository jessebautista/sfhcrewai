# Slack App Setup Guide

Follow these steps to create and configure your Slack app for the CrewAI News Manager.

## Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Fill in:
   - **App Name:** `CrewAI News Manager` (or your preferred name)
   - **Pick a workspace:** Select your Slack workspace
5. Click **"Create App"**

---

## Step 2: Enable Socket Mode

1. In your app's settings (left sidebar), click **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to **ON**
3. You'll be prompted to generate an app-level token:
   - **Token Name:** `socket_token`
   - **Scopes:** Select `connections:write`
   - Click **"Generate"**
4. **📋 COPY THE TOKEN** - It starts with `xapp-`
   - Save it somewhere safe, you'll need it for `.env`

---

## Step 3: Configure User Token Permissions

1. Click **"OAuth & Permissions"** in the left sidebar
2. Scroll down to **"Scopes"**
3. Under **"User Token Scopes"** (NOT Bot Token Scopes), click **"Add an OAuth Scope"**
4. Add these scopes one by one:
   - `chat:write`
   - `users:read`
   - `channels:history`
   - `groups:history`
   - `im:history`
   - `mpim:history`

5. Scroll to the top and click **"Install to Workspace"**
6. Review the permissions and click **"Allow"**
7. **📋 COPY THE USER OAUTH TOKEN** - It starts with `xoxp-`
   - This is the token that allows posting as your user account
   - Save it securely

---

## Step 4: Subscribe to Events

1. Click **"Event Subscriptions"** in the left sidebar
2. Toggle **"Enable Events"** to **ON**
3. Under **"Subscribe to bot events"**, click **"Add Bot User Event"**
4. Add these events:
   - `app_mention`
   - `message.im`
5. Click **"Save Changes"** at the bottom

---

## Step 5: Add Tokens to .env

Add these tokens to your `.env` file:

```env
SLACK_APP_TOKEN=xapp-...    # Your app token from Step 2
SLACK_USER_TOKEN=xoxp-...   # Your user token from Step 3
```

Replace the `...` with your actual token values.

---

## ✅ Verification Checklist

Before proceeding, verify you have:

- [ ] Created a Slack app
- [ ] Enabled Socket Mode
- [ ] Generated app-level token (xapp-...)
- [ ] Configured User Token Scopes (6 scopes)
- [ ] Installed app to workspace
- [ ] Generated user OAuth token (xoxp-...)
- [ ] Subscribed to bot events
- [ ] Added both tokens to `.env`

---

## ⚠️ Important Notes

- **User Token**: Messages will appear as if posted by the user who installed the app
- **Security**: The user token has full permissions - keep it secure
- **Token Storage**: Never commit `.env` to git (it should be in `.gitignore`)

---

## Next Steps

Once you've completed all steps and added tokens to `.env`, let me know and I'll:
1. Install the required dependencies
2. Implement the Slack bot code
3. Test the integration
