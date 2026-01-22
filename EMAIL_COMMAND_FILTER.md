# Email Subject Keyword Filter - Usage Guide

The email bot now only processes emails with **"COMMAND:"** prefix in the subject line.

## How to Use

### ✅ **Emails That Will Be Processed:**

```
Subject: COMMAND: Create article about Python
Subject: command: Fetch latest news
Subject: COMMAND: Update article 12345
```

**Notes:**
- Case-insensitive (COMMAND, Command, command all work)
- The "COMMAND:" prefix is removed before sending to AI
- AI receives: "Create article about Python" (clean command)

### ❌ **Emails That Will Be Ignored:**

```
Subject: iPhone 15 Sale - 50% Off!
Subject: Your package has shipped
Subject: Create article about Python (missing COMMAND:)
Subject: COMMAND (no command after prefix)
```

**What happens:**
- Email is marked as read
- No agent processing
- No reply sent
- Logged as "skipped"

---

## Examples

### Example 1: Create Article
```
To: neick.sup22@gmail.com
Subject: COMMAND: Create news article about AI advances
Body: (optional additional context)
```

**Bot receives:** "Create news article about AI advances"

### Example 2: Fetch News
```
To: neick.sup22@gmail.com
Subject: COMMAND: Fetch latest news
```

**Bot receives:** "Fetch latest news"

### Example 3: Update Article
```
To: neick.sup22@gmail.com
Subject: COMMAND: Update article 575412 with new content
```

**Bot receives:** "Update article 575412 with new content"

---

## Benefits

✅ **Prevents spam processing:** Promotional emails ignored  
✅ **Clear intent:** Users know how to trigger bot  
✅ **Saves resources:** Only processes legitimate commands  
✅ **Easy to remember:** Simple "COMMAND:" prefix  
✅ **Flexible:** Case-insensitive matching  

---

## Configuration

No configuration needed - the filter is active by default.

**Current Settings:**
- Keyword: `COMMAND:`
- Case-sensitive: NO (works with any case)
- Position: Must be at START of subject
- Automatic: Filtered emails are auto-marked as read

---

## Testing

Send a test email:
```
To: neick.sup22@gmail.com
Subject: COMMAND: Hello
```

Expected response: Bot replies with greeting from agent.

Send spam email:
```
To: neick.sup22@gmail.com  
Subject: Buy cheap iPhones now!
```

Expected: Ignored, marked as read, no processing.
