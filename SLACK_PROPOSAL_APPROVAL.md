# Slack Interactive Proposal Approval - Feature Documentation

## Overview

Enhanced the Slack bot to support interactive proposal approval directly from Slack messages using Block Kit interactive buttons.

## How It Works

### 1. **Proposal Creation**
When an agent creates a proposal (via "Submit Draft Creation" or "Submit Draft Update" tools):
1. Proposal is saved to database
2. **Slack notification is automatically sent** to the user
3. Notification includes interactive [Approve] and [Reject] buttons

### 2. **Notification Message Format**

```
📋 New Proposal Awaiting Approval

Type: CREATE
Proposal ID: abc123...

Reason: New article about upcoming event

Payload Preview:
{ "title": "Event Title", "content": "..." }

[✅ Approve]  [❌ Reject]
```

### 3. **Button Actions**

**Approve Button:**
- Clicks execute the proposal immediately
- Creates/updates record in database
- Updates message to show approval confirmation
- Shows who approved it

**Reject Button:**
- Marks proposal as rejected
- Updates message to show rejection
- Records rejection in database

---

## Configuration

### Optional: Set Notification Channel

By default, notifications go to the user who installed the app. You can specify a channel:

**Add to `.env`:**
```env
SLACK_NOTIFICATION_CHANNEL=#proposals
```

Or use a user DM:
```env
SLACK_NOTIFICATION_CHANNEL=@yourusername
```

---

## Usage Example

### Step 1: Create Proposal via Slack
```
@CrewAI News Manager create a news article about spring concert
```

### Step 2: Receive Notification
Within seconds, you'll receive a Slack message with proposal details and buttons.

### Step 3: Approve or Reject
Click the button directly in the message - no need to open Streamlit!

### Step 4: Confirmation
Message updates to show your action was completed.

---

## Technical Implementation

### Files Modified

1. **`src/interfaces/slack_bot.py`**
   - Added `@app.action("approve_proposal")` handler
   - Added `@app.action("reject_proposal")` handler
   - Added `send_proposal_notification()` function
   - Uses Slack Block Kit for rich message formatting

2. **`src/core/proposal.py`**
   - `submit_proposal()` now triggers Slack notification
   - Silent fail if notification can't be sent (doesn't break proposal flow)

### Dependencies
- Uses existing `slack_bolt` package
- No additional installations needed

---

## Benefits

✅ **Faster approval workflow** - No need to open Streamlit UI  
✅ **Mobile-friendly** - Approve from Slack mobile app  
✅ **Real-time notifications** - Get notified immediately  
✅ **Audit trail** - See who approved/rejected in message  
✅ **Dual interface** - Can still use Streamlit Admin Controls if preferred

---

## Testing

**Test the feature:**
1. Restart Slack bot (already done)
2. Send command: `@CrewAI News Manager create a news article`
3. Agent will create a proposal
4. You should receive a Slack message with buttons
5. Click [✅ Approve] or [❌ Reject]
6. Message updates to confirm action

**Troubleshooting:**
- If no notification appears, check:
  - Bot is running
  - `SLACK_NOTIFICATION_CHANNEL` is set correctly (or use default "@me")
  - Proposal was created (check database or Streamlit)

---

## Next Steps

The Slack integration is now **feature-complete** with:
- ✅ DM and @mention handling
- ✅ Agent mission execution
- ✅ Interactive proposal approval
- ✅ Real-time notifications

Ready for production use!
