# Email Bot Setup Guide

Complete guide to setting up email integration for the CrewAI News Manager.

## Overview

The email bot allows users to interact with the AI agent by sending emails. The bot polls an inbox, processes commands, runs the agent, and replies with results.

---

## Prerequisites

- An email account (Gmail recommended for testing)
- IMAP/SMTP access enabled
- Python environment with project dependencies

---

## Step 1: Choose Email Provider

### Recommended: Gmail

**Pros:**
- Easy to set up
- Reliable IMAP/SMTP
- Good for testing

**Cons:**
- Requires app password setup
- Rate limits on polling

### Alternative: Outlook/Office 365

**Pros:**
- No app password needed for personal accounts
- Good reliability

**Configuration:**
```
IMAP: outlook.office365.com:993
SMTP: smtp.office365.com:587
```

### Alternative: Custom Provider

Any IMAP-compatible email works. Check your provider's documentation for:
- IMAP server address and port
- SMTP server address and port
- SSL/TLS requirements

---

## Step 2: Gmail Setup (Detailed)

### 2.1 Create or Use Existing Account

1. Go to https://accounts.google.com/signup
2. Create account or use existing
3. **Recommended:** Create dedicated account like `crewai-bot@gmail.com`

### 2.2 Enable 2-Factor Authentication

> **Required for App Passwords**

1. Go to https://myaccount.google.com/security
2. Click **"2-Step Verification"**
3. Follow prompts to enable (use phone verification)
4. Complete setup

### 2.3 Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. **App:** Select "Mail"
3. **Device:** Select "Other (Custom name)"
4. **Name:** Enter "CrewAI News Bot"
5. Click **"Generate"**
6. **📋 COPY THE 16-CHARACTER PASSWORD**
   - Example: `abcd efgh ijkl mnop`
   - Remove spaces: `abcdefghijklmnop`
   - This is what goes in `.env`

### 2.4 Enable IMAP

1. Open Gmail
2. Click Settings (⚙️) → "See all settings"
3. Go to **"Forwarding and POP/IMAP"** tab
4. Under "IMAP access", select **"Enable IMAP"**
5. Click **"Save Changes"**

---

## Step 3: Add Credentials to .env

Open your `.env` file and add:

```env
# Email Bot Configuration
EMAIL_ADDRESS=your-bot-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_POLL_INTERVAL=60
```

**For Gmail:**
- `EMAIL_ADDRESS`: Your Gmail address
- `EMAIL_PASSWORD`: The 16-character app password (no spaces)
- IMAP/SMTP servers: Use values above

**For Outlook:**
```env
EMAIL_ADDRESS=your-email@outlook.com
EMAIL_PASSWORD=your-account-password
EMAIL_IMAP_SERVER=outlook.office365.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.office365.com
EMAIL_SMTP_PORT=587
EMAIL_POLL_INTERVAL=60
```

---

## Step 4: Test Email Access

Before running the bot, verify credentials work:

### Quick Test (Python)

```python
import imaplib

# Test IMAP connection
mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login('your-email@gmail.com', 'your-app-password')
print("✅ IMAP connection successful!")
mail.logout()
```

If this works, your credentials are correct!

---

## Step 5: Security Best Practices

### ✅ DO:
- Use app-specific passwords
- Keep `.env` in `.gitignore`
- Use dedicated bot email account
- Enable 2FA on email account

### ❌ DON'T:
- Use your main email password
- Commit `.env` to git
- Share app passwords publicly
- Disable account security features

---

## Configuration Reference

### Gmail Settings
```env
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

### Outlook Settings
```env
EMAIL_IMAP_SERVER=outlook.office365.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.office365.com
EMAIL_SMTP_PORT=587
```

### Common Providers

| Provider | IMAP Server | SMTP Server |
|----------|-------------|-------------|
| Gmail | imap.gmail.com:993 | smtp.gmail.com:587 |
| Outlook | outlook.office365.com:993 | smtp.office365.com:587 |
| Yahoo | imap.mail.yahoo.com:993 | smtp.mail.yahoo.com:587 |
| ProtonMail | 127.0.0.1:1143 (Bridge) | 127.0.0.1:1025 (Bridge) |

---

## Troubleshooting

### "Authentication failed"
- Double-check email address
- Verify app password is correct (no spaces)
- Ensure 2FA is enabled (for Gmail)
- Check IMAP is enabled in email settings

### "Connection refused"
- Verify IMAP server address
- Check port number (993 for SSL)
- Ensure firewall allows outbound connections

### "Too many login attempts"
- Wait 15 minutes
- Reduce `EMAIL_POLL_INTERVAL` to avoid rate limits
- Check for multiple bot instances running

---

## Next Steps

Once setup is complete:
1. ✅ Email account created/configured
2. ✅ App password generated
3. ✅ IMAP/SMTP enabled
4. ✅ Credentials added to `.env`
5. ✅ Test connection successful

**You're ready!** Let me know and I'll implement the email bot code.

---

## Usage After Implementation

### Sending Commands

**Email Format:**
- **To:** `your-bot-email@gmail.com`
- **Subject:** Your command (e.g., "Fetch latest news")
- **Body:** Optional additional context

**Examples:**
- Subject: `Hello` → Bot responds with greeting
- Subject: `Fetch latest news` → Agent returns news articles
- Subject: `Create article about AI` → Agent creates draft proposal

### Expected Response Time

- Bot polls every 60 seconds (configurable)
- Processing time: 5-30 seconds (depends on agent)
- Total: ~1-2 minutes from send to reply

---

## Ready to Implement?

Once you've completed the setup, let me know and I'll:
1. Install dependencies
2. Create `email_bot.py` with full implementation
3. Test the bot with your email account
4. Verify proposal workflow via email
