# 🚀 CrewAI News Manager - Quick Start Guide

Complete guide for using the multi-interface AI news management system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Web UI Interface](#-web-ui-interface)
3. [Slack Bot Interface](#-slack-bot-interface)
4. [Email Bot Interface](#-email-bot-interface)
5. [File Attachments](#-file-attachments)
6. [Admin Controls & HITL](#-admin-controls--hitl)
7. [Troubleshooting](#-troubleshooting)

---

## Overview

**Three ways to interact with your AI news assistant:**

| Interface | Best For | Features |
|-----------|----------|----------|
| **Web UI** | Interactive work, testing | Real-time chat, file upload, dashboard |
| **Slack** | Team collaboration | DM commands, buttons, notifications |
| **Email** | Remote access, automation | COMMAND: prefix, attachments, replies |

**All interfaces support:**
- ✅ Create/update news articles
- ✅ File attachments (images, PDFs, CSVs)
- ✅ Human-in-the-Loop (HITL) approval workflow
- ✅ Real-time notifications

---

## 🖥️ Web UI Interface

### Starting the Web UI

```bash
cd sfhcrewai-main
streamlit run src/ui/app.py
```

**Access:** http://localhost:8501

### Using the Chat Interface

1. **Enter your command** in the chat input
2. **Upload files** (optional):
   - Click "Browse files" under "📎 File Attachments"
   - Max 3 files, 10MB each
   - Supports: JPG, PNG, WebP, PDF, CSV
3. **Press Enter** to submit

**Example Commands:**
```
Create a news article about AI advances
Update article 12345 with new content
Fetch the latest tech news
```

### File Attachments in Web UI

**Images:**
- Uploaded to Supabase Storage
- URL passed to agent
- Used as article image

**PDFs:**
- Text extracted automatically
- Content used as reference

**CSVs:**
- Data formatted as table
- Passed to agent for analysis

**Progress Bar:**
- Shows upload progress
- Real-time file processing status

### Admin Controls (Sidebar)

**Pending Proposals:**
- View all proposals awaiting approval
- Click ✅ **Approve** or ❌ **Reject**
- Proposals clear after action

---

## 💬 Slack Bot Interface

### Starting Slack Bot

```bash
$env:PYTHONPATH="."; .venv\Scripts\python.exe src/interfaces/slack_bot.py
```

**Verify running:** Should see "✅ Bot is running!"

### Sending Commands

**Direct Message (DM):**
1. Open DM with bot
2. Type your command
3. Bot replies with result

**Channel Mentions:**
```
@NewsBot Create article about blockchain
```

**With File Attachments:**
1. Click **+** (attach files)
2. Upload image/PDF/CSV
3. Add your command text
4. Send

**Bot feedback:**
```
📎 Processing 2 attachment(s)...
✅ Downloaded image.jpg
✅ Uploaded 1 image(s)
Processing your request... ⏳
✅ Mission Complete: [result]
```

### Interactive Proposals

**When agent creates proposal:**
```
📋 New Proposal: CREATE_ARTICLE

Title: "AI in Healthcare"
Content: [...preview...]

[✅ Approve] [❌ Reject]
```

Click buttons to approve/reject directly in Slack!

### Slack File Limits

- Max 3 files per message
- 10MB per file
- Types: JPG, PNG, WebP, PDF, CSV
- Downloads use Slack API

---

## 📧 Email Bot Interface

### Starting Email Bot

```bash
$env:PYTHONPATH="."; .venv\Scripts\python.exe src/interfaces/email_bot.py
```

**Verify running:** Should see "✅ Press Ctrl+C to stop"

### Email Format

**Subject Line:**
```
COMMAND: Create article about quantum computing
```

**⚠️ IMPORTANT:** Subject MUST start with `COMMAND:` (case-insensitive)

**Body:** Optional additional context

**Attachments:** 
- Attach images/PDFs/CSVs
- Max 3 files, 10MB each

### Examples

**Example 1: Simple Command**
```
To: neick.sup22@gmail.com
Subject: COMMAND: Fetch latest news
Body: Focus on technology sector
```

**Example 2: With Attachment**
```
To: neick.sup22@gmail.com
Subject: COMMAND: Create article about renewable energy
Attachments: solar-panel.jpg
```

**Example 3: Update Article**
```
To: neick.sup22@gmail.com
Subject: COMMAND: Update article 67890
Body: Add new statistics from attached PDF
Attachments: report.pdf
```

### Email Responses

**Bot replies to your email:**
```
From: neick.sup22@gmail.com
Subject: Re: COMMAND: Create article...

Command: Create article about AI

✅ Mission Complete:
[Agent's response with details]
```

### Email Notifications

**After proposal approval:**
```
From: neick.sup22@gmail.com
Subject: Proposal Approved

Your proposal has been approved!

Type: CREATE_ARTICLE
Title: "Future of AI"
Status: Approved
```

### COMMAND: Prefix Rules

✅ **Will process:**
- `COMMAND: ...`
- `command: ...`
- `Command: ...`

❌ **Will skip:**
- No "COMMAND:" prefix
- Empty subject
- Spam/promotional emails

---

## 📎 File Attachments

### Supported File Types

| Type | Extensions | Purpose | Max Size |
|------|-----------|---------|----------|
| **Images** | `.jpg`, `.jpeg`, `.png`, `.webp` | Article images | 10MB |
| **Documents** | `.pdf` | Text extraction | 10MB |
| **Data** | `.csv` | Data analysis | 10MB |

### File Processing

**Images:**
1. Uploaded to Supabase Storage
2. Public URL generated
3. URL passed to agent
4. Used in `news_image` field

**PDFs:**
1. Text extracted (first 5 pages)
2. Content provided to agent
3. Used as reference material

**CSVs:**
1. Data parsed (first 50 rows)
2. Formatted as markdown table
3. Passed to agent for analysis

### File Limits

- **Per request:** Max 3 files
- **Per file:** Max 10MB
- **Total:** 30MB max per request

### Performance

- **Parallel processing:** Multiple files processed simultaneously
- **Smart optimization:** Small images skip compression
- **Progress feedback:** Real-time status in all interfaces

---

## 🔐 Admin Controls & HITL

### Human-in-the-Loop (HITL) Workflow

**When agent needs approval:**
1. Agent creates proposal
2. Stored in Supabase `proposals` table
3. **Notifications sent:**
   - Slack: Interactive message with buttons
   - Email: Notification to requester
   - Web UI: Sidebar alert

### Approval Methods

**Method 1: Web UI**
- Check sidebar "Admin Controls"
- Click ✅ Approve or ❌ Reject

**Method 2: Slack**
- Click buttons in notification message
- Instant feedback

**Method 3: (Future) Email**
- Reply to notification
- "APPROVE" or "REJECT" in body

### Proposal Types

**CREATE_ARTICLE:**
- New article creation
- Requires: title, content, image URL

**UPDATE_ARTICLE:**
- Modify existing article
- Requires: article ID, updated fields

**DELETE_ARTICLE:**
- Remove article
- Requires: article ID, reason

---

## 🔍 Troubleshooting

### Web UI Issues

**"Connection error"**
- Check if Streamlit is running
- Restart: `streamlit run src/ui/app.py`

**File upload fails**
- Check file size (< 10MB)
- Verify Supabase Storage bucket exists
- Check `.env` for `SUPABASE_URL` and `SUPABASE_KEY`

### Slack Issues

**Bot not responding**
- Verify bot is running in terminal
- Check `.env` for `SLACK_USER_TOKEN` and `SLACK_APP_TOKEN`
- Restart bot

**Attachments not processing**
- Check file size
- Verify file type is supported
- Check terminal logs for errors

### Email Issues

**No emails being processed**
- Check if bot is running
- Verify email format: `COMMAND:` prefix
- Check Gmail IMAP settings
- Verify `.env` credentials

**Attachments ignored**
- Check file size (< 10MB)
- Verify MIME type is supported
- Check terminal for extraction errors

### General Issues

**"Agent failed"**
- Check API keys in `.env`
- Verify OpenRouter/OpenAI key is valid
- Check agent logs in Supabase

**Storage upload fails**
- Verify Supabase bucket `attachments` exists
- Check bucket is set to PUBLIC
- Verify storage policies are configured

---

## 🛠️ Configuration

### Environment Variables

Required in `.env`:

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# LLM
OPENROUTER_API_KEY=sk-or-xxx
# OR
OPENAI_API_KEY=sk-xxx

# Slack
SLACK_USER_TOKEN=xoxp-xxx
SLACK_APP_TOKEN=xapp-xxx

# Email
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
```

### File Storage

**Supabase Storage Bucket:**
- Name: `attachments`
- Public: Yes
- File size limit: 10MB
- Policies: Public read, authenticated upload

**Setup:** See `ATTACHMENT_SETUP.md`

---

## 📚 Additional Documentation

- **Slack Setup:** `SLACK_SETUP.md`
- **Email Setup:** `EMAIL_SETUP.md`
- **Attachments:** `ATTACHMENT_SETUP.md`
- **DB Migrations:** `scripts/MIGRATION_INSTRUCTIONS.md`

---

## 🎯 Quick Command Reference

### Web UI
```
Just type in chat and optionally upload files
```

### Slack
```
DM: Create article about AI
@mention: @NewsBot fetch latest news
With file: Upload file + "Create article"
```

### Email
```
Subject: COMMAND: Your command here
Attachments: Optional files
```

---

## ⚡ Best Practices

1. **Use descriptive commands**
   - ✅ "Create article about AI advances in healthcare"
   - ❌ "Create article"

2. **Attach relevant files**
   - Images for article visuals
   - PDFs for research content
   - CSVs for data-driven articles

3. **Monitor proposals**
   - Check Slack notifications
   - Review Web UI sidebar
   - Approve/reject promptly

4. **Keep files under 10MB**
   - Optimize images before upload
   - Extract relevant PDF pages
   - Filter CSV data

5. **Use COMMAND: prefix for emails**
   - Prevents spam processing
   - Clear intent signal
   - Easy to filter

---

## 🆘 Support

**Check logs:**
- Terminal output for each bot
- Supabase `agent_logs` table
- Web UI observability dashboard

**Common fixes:**
- Restart the specific bot
- Verify `.env` configuration
- Check network/API connectivity
- Review Supabase dashboard

---

**Happy news managing! 🎉**
