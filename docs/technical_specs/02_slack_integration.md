# Technical Spec: Slack Integration (Chat Bot)

**Status**: Draft
**Priority**: Medium
**Type**: Chat Interface

## 1. Overview
Enable users to interact with the CrewAI news manager directly via Slack. The bot will accept natural language commands in a Direct Message (DM) or Mention, run the agent, and reply in a thread.

## 2. Prerequisites
-   **Slack App** configured in [api.slack.com/apps](https://api.slack.com/apps).
-   **Socket Mode** enabled (bypasses need for public HTTP webhook).
-   **Scopes**: `app_mentions:read`, `chat:write`, `im:history`, `im:read`.

## 3. Configuration (`.env`)
```env
SLACK_APP_TOKEN=xapp-...  # App-level token for Socket Mode
SLACK_BOT_TOKEN=xoxb-...  # Bot User OAuth Token
```

## 4. Implementation Details

### 4.1 Dependencies
`requirements.txt` update:
```text
slack_bolt>=1.18.0
slack_sdk>=3.27.0
aiohttp
```

### 4.2 Bot Service (`src/interfaces/slack_bot.py`)
We will use the `slack_bolt` framework with `SocketModeHandler`.

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.agents.orchestrator import OrchestratorAgent

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("message")
def handle_message(message, say):
    user_text = message.get("text")
    
    # 1. Acknowledge
    say(f"Processing your request: '{user_text}'... ⏳")
    
    # 2. Run Agent
    # Note: detailed error handling needed here
    orchestrator = OrchestratorAgent()
    result = orchestrator.run_mission(user_text)
    
    # 3. Reply
    say(f"✅ Mission Complete:\n\n{result}")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

### 4.3 Concurrency
Since CrewAI agents can be slow, the bot should handle requests asynchronously or offload them to a background worker to prevent the specific Slack event handler from timing out (though Socket Mode is lenient).

## 5. Verification
1.  Run `python src/interfaces/slack_bot.py`.
2.  Open Slack.
3.  Send "Hello" to the bot.
4.  Verify response.
