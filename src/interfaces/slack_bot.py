"""
Slack bot interface for CrewAI News Manager.
Uses Socket Mode with user token to post messages as a real user account.
"""
import os
import sys
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator import OrchestratorAgent

load_dotenv()

# Initialize Slack app with user token (posts as user account)
app = App(token=os.environ.get("SLACK_USER_TOKEN"))


@app.event("message")
def handle_message(event, say, logger):
    """
    Handle direct messages to the bot.
    """
    # Ignore messages from bots and threaded messages
    if event.get("bot_id") or event.get("thread_ts"):
        return
    
    user_text = event.get("text", "")
    channel = event.get("channel")
    user = event.get("user")
    
    logger.info(f"Received DM from {user}: {user_text}")
    
    # Acknowledge receipt
    say(
        text=f"Processing your request: '{user_text}'... ⏳",
        channel=channel
    )
    
    try:
        # Run the agent
        orchestrator = OrchestratorAgent()
        result = orchestrator.run_mission(user_text)
        
        # Reply with result
        say(
            text=f"✅ Mission Complete:\n\n{result}",
            channel=channel
        )
        logger.info(f"Mission completed successfully for {user}")
        
    except Exception as e:
        logger.error(f"Mission failed: {e}")
        say(
            text=f"❌ Error: {str(e)}",
            channel=channel
        )


@app.event("app_mention")
def handle_mention(event, say, logger):
    """
    Handle @mentions of the bot in channels.
    """
    user_text = event.get("text", "")
    channel = event.get("channel")
    thread_ts = event.get("ts")  # Reply in thread
    user = event.get("user")
    
    # Remove the bot mention from the text
    # User mentions look like <@U12345678>
    import re
    user_text = re.sub(r'<@[A-Z0-9]+>', '', user_text).strip()
    
    logger.info(f"Received mention from {user} in {channel}: {user_text}")
    
    # Acknowledge in thread
    say(
        text=f"Processing your request: '{user_text}'... ⏳",
        channel=channel,
        thread_ts=thread_ts
    )
    
    try:
        # Run the agent
        orchestrator = OrchestratorAgent()
        result = orchestrator.run_mission(user_text)
        
        # Reply in thread
        say(
            text=f"✅ Mission Complete:\n\n{result}",
            channel=channel,
            thread_ts=thread_ts
        )
        logger.info(f"Mission completed successfully for mention in {channel}")
        
    except Exception as e:
        logger.error(f"Mission failed: {e}")
        say(
            text=f"❌ Error: {str(e)}",
            channel=channel,
            thread_ts=thread_ts
        )


def main():
    """Start the Slack bot with Socket Mode."""
    app_token = os.environ.get("SLACK_APP_TOKEN")
    user_token = os.environ.get("SLACK_USER_TOKEN")
    
    if not app_token or not user_token:
        print("❌ Error: SLACK_APP_TOKEN and SLACK_USER_TOKEN must be set in .env")
        sys.exit(1)
    
    print("🤖 Starting Slack bot...")
    print("📝 Using user token - messages will post as your user account")
    print("✅ Bot is running! Send a DM or @mention to interact.")
    print("Press Ctrl+C to stop.")
    
    # Start Socket Mode handler
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()
