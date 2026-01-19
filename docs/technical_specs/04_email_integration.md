# Technical Spec: Email Integration (Chat Interface)

**Status**: Draft
**Priority**: Hard
**Type**: Chat Interface

## 1. Overview
Allow users to task the agent via email. The system will poll an inbox for new messages, interpret the body as a prompt, and reply with the results.

## 2. Prerequisites
-   Dedicated Email Account (e.g., Gmail).
-   **App Password** generated (for IMAP/SMTP access).
-   IMAP/SMTP enabled on the account.

## 3. Configuration (`.env`)
```env
EMAIL_USER=your_bot@gmail.com
EMAIL_PASSWORD=app_password_here
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_SMTP_SERVER=smtp.gmail.com
```

## 4. Implementation Details

### 4.1 Dependencies
Built-in `imaplib`, `smtplib`, `email`. No external pip packages strictly required, though `beautifulsoup4` is helpful for parsing HTML email bodies.

### 4.2 Email Bot Service (`src/interfaces/email_bot.py`)
A daemon process running a `while True` loop.

#### Polling Logic
1.  Connect via `imaplib.IMAP4_SSL`.
2.  Login and Select `INBOX`.
3.  Search: `type, data = mail.search(None, 'UNSEEN')`.
4.  For each ID:
    -   Fetch RFC822 content.
    -   Parse using `email.message_from_bytes`.
    -   Extract body (prefer `text/plain`, fallback to stripping HTML from `text/html`).
    -   **Important**: Filter out signatures/replies to avoid loops.

#### Agent Execution
-   Instantiate `OrchestratorAgent`.
-   `result = agent.run_mission(email_body_text)`.

#### Reply Logic
1.  Connect via `smtplib.SMTP_SSL`.
2.  Compose `MIMEMultipart` message.
3.  Subject: `Re: {original_subject}`.
4.  Body: The Agent's result.
5.  Send.

### 4.3 Challenges & Mitigations
-   **Spam/Loops**: Only reply to allowed senders (allowlist in `.env` recommended).
-   **Timeouts**: IMAP connections time out. The script must handle re-connection logic in the loop.
-   **Formatting**: Agents output Markdown. Email clients prefer HTML. We should convert Markdown -> HTML for the email body.

## 5. Verification
1.  Send email with subject "Task" and body "Fetch latest news".
2.  Monitor logs for "New email received".
3.  Wait for reply in your personal inbox.
