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

# Store the Slack client globally for sending notifications
slack_client = None


def download_slack_files(files, token):
    """Download files from Slack."""
    import requests
    from src.core.file_handler import FileAdapter
    
    downloaded = []
    for file in files[:3]:
        try:
            if file.get('size', 0) > 10 * 1024 * 1024:
                print(f"⚠️ Skip {file['name']}: Too large")
                continue
            
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(file['url_private'], headers=headers)
            
            if response.status_code == 200:
                file_obj = FileAdapter.from_slack_file(
                    file['name'], response.content, file.get('mimetype', 'application/octet-stream')
                )
                downloaded.append(file_obj)
                print(f"✅ Downloaded {file['name']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    return downloaded


def format_attachment_context(result):
    """Format attachment results."""
    context = ""
    if result['images']:
        context += "\n\n📸 Attached Images:\n"
        for idx, url in enumerate(result['images'], 1):
            context += f"{idx}. {url}\n"
    if result['pdf_text']:
        context += f"\n\n📄 Content:\n{result['pdf_text'][:1500]}...\n"
    return context


@app.event("message")
def handle_message(event, say, logger):
    """
    Handle direct messages to the bot AND thread replies in channels.
    """
    # Ignore messages from bots
    if event.get("bot_id"):
        return
    
    user_text = event.get("text", "")
    channel = event.get("channel")
    user = event.get("user")
    files = event.get("files", [])
    thread_ts = event.get("thread_ts")  # Parent thread timestamp if in thread
    
    # Only handle:
    # 1. Direct messages (channel starts with 'D')
    # 2. Thread replies where bot is participating
    is_dm = channel.startswith('D')
    is_thread_reply = thread_ts is not None
    
    if not is_dm and not is_thread_reply:
        # Not a DM and not in a thread - ignore (will be handled by app_mention if @mentioned)
        return
    
    logger.info(f"Received {'DM' if is_dm else 'thread message'} from {user}: {user_text}")
    
    # Initialize memory manager and get conversation context
    conversation_id = None
    conversation_context = ""
    try:
        from src.core.memory_manager import MemoryManager
        memory = MemoryManager()
        # For threads, use thread_ts to maintain separate conversation per thread
        conv_channel = f"{channel}_{thread_ts}" if is_thread_reply else channel
        metadata = {'thread_ts': thread_ts} if is_thread_reply else None
        conversation_id = memory.get_or_create_conversation(
            user, conv_channel, interface='slack', metadata=metadata
        )
        history = memory.get_conversation_history(conversation_id, limit=20)
        conversation_context = memory.format_history_for_prompt(history)
        logger.info(f"Retrieved {len(history)} messages from conversation history")
    except Exception as e:
        logger.warning(f"Memory not available: {e}. Proceeding without context.")
    
    # Process attachments if present
    attachment_context = ""
    if files:
        say(f"📎 Processing {len(files)} attachment(s)...", channel=channel)
        
        try:
            downloaded_files = download_slack_files(files, os.environ.get("SLACK_USER_TOKEN"))
            
            if downloaded_files:
                from src.core.file_handler import process_files
                result = process_files(downloaded_files)
                
                attachment_context = format_attachment_context(result)
                
                if result['images']:
                    say(f"✅ Uploaded {len(result['images'])} image(s)", channel=channel)
                if result['pdf_text']:
                    say(f"✅ Extracted content from files", channel=channel)
                if result['errors']:
                    for error in result['errors']:
                        say(f"⚠️ {error}", channel=channel)
        except Exception as e:
            logger.error(f"Attachment error: {e}")
            say(f"⚠️ Error processing attachments: {str(e)}", channel=channel)
    
    
    # Check if this is a conversational message (greeting, introduction, etc)
    from src.core.behavioral_config import BehavioralConfig
    is_conversational = BehavioralConfig.is_conversational(user_text)
    
    # Acknowledge receipt with professional, concise message
    if is_conversational:
        ack_message = f"{BehavioralConfig.INITIAL_RESPONSE_TEMPLATE} ⏳"
    else:
        ack_message = f"Processing your request... ⏳"
    
    say(
        text=ack_message,
        channel=channel,
        thread_ts=thread_ts  # Reply in thread if applicable
    )
    
    try:
        # Store user message in memory
        if conversation_id:
            try:
                memory.store_message(conversation_id, role='user', content=user_text)
            except Exception as e:
                logger.warning(f"Failed to store user message: {e}")
        
        # Combine conversation context, current message, and attachments
        full_command = f"{conversation_context}\n\nCurrent request: {user_text}{attachment_context}"
        
        # Run the agent
        orchestrator = OrchestratorAgent()
        result = orchestrator.run_mission(full_command)
        
        # Store assistant response in memory
        if conversation_id:
            try:
                memory.store_message(conversation_id, role='assistant', content=str(result))
            except Exception as e:
                logger.warning(f"Failed to store assistant response: {e}")
        
        # Reply with result (in thread if applicable)
        say(
            text=f"✅ Mission Complete:\n\n{result}",
            channel=channel,
            thread_ts=thread_ts
        )
        logger.info(f"Mission completed successfully for {user}")
        
    except Exception as e:
        logger.error(f"Mission failed: {e}")
        say(
            text=f"❌ Error: {str(e)}",
            channel=channel,
            thread_ts=thread_ts
        )


@app.event("app_mention")
def handle_mention(event, say, logger):
    """
    Handle @mentions of the bot in channels.
    """
    user_text = event.get("text", "")
    channel = event.get("channel")
    # For thread replies, thread_ts is the parent. For first mention, ts becomes the parent.
    thread_ts = event.get("thread_ts") or event.get("ts")  # Use parent thread or current message
    user = event.get("user")
    
    # Remove the bot mention from the text
    # User mentions look like <@U12345678>
    import re
    user_text = re.sub(r'<@[A-Z0-9]+>', '', user_text).strip()
    
    logger.info(f"Received mention from {user} in {channel}: {user_text}")
    
    # Initialize memory manager and get conversation context
    # For mentions, we use channel+thread_ts as unique conversation ID
    conversation_id = None
    conversation_context = ""
    try:
        from src.core.memory_manager import MemoryManager
        memory = MemoryManager()
        # Use thread_ts if available, otherwise channel as conversation identifier
        conv_channel = f"{channel}_{thread_ts}" if thread_ts else channel
        metadata = {'thread_ts': thread_ts} if thread_ts else None
        conversation_id = memory.get_or_create_conversation(
            user, conv_channel, interface='slack', metadata=metadata
        )
        history = memory.get_conversation_history(conversation_id, limit=20)
        conversation_context = memory.format_history_for_prompt(history)
        logger.info(f"Retrieved {len(history)} messages from thread history")
    except Exception as e:
        logger.warning(f"Memory not available: {e}. Proceeding without context.")
    
    
    # Check if this is a conversational message
    from src.core.behavioral_config import BehavioralConfig
    is_conversational = BehavioralConfig.is_conversational(user_text)
    
    # Acknowledge in thread with professional message
    if is_conversational:
        ack_message = f"{BehavioralConfig.INITIAL_RESPONSE_TEMPLATE} ⏳"
    else:
        ack_message = f"Processing your request... ⏳"
    
    say(
        text=ack_message,
        channel=channel,
        thread_ts=thread_ts
    )
    
    try:
        # Store user message in memory
        if conversation_id:
            try:
                memory.store_message(conversation_id, role='user', content=user_text)
            except Exception as e:
                logger.warning(f"Failed to store user message: {e}")
        
        # Combine conversation context with current request
        full_command = f"{conversation_context}\n\nCurrent request: {user_text}"
        
        # Run the agent
        orchestrator = OrchestratorAgent()
        result = orchestrator.run_mission(full_command)
        
        # Store assistant response in memory
        if conversation_id:
            try:
                memory.store_message(conversation_id, role='assistant', content=str(result))
            except Exception as e:
                logger.warning(f"Failed to store assistant response: {e}")
        
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


@app.action("approve_proposal")
def handle_approve_proposal(ack, body, logger):
    """
    Handle approval button click.
    """
    ack()  # Acknowledge the action
    
    proposal_id = body["actions"][0]["value"]
    user = body["user"]["id"]
    
    logger.info(f"User {user} approving proposal {proposal_id}")
    
    try:
        from src.core.proposal import ProposalManager
        manager = ProposalManager()
        manager.approve_proposal(proposal_id)
        
        # Update the message to show it's been approved
        app.client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            text=f"✅ Proposal approved by <@{user}>!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Proposal Approved*\n\nApproved by <@{user}> and executed successfully!"
                    }
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to approve proposal: {e}")
        app.client.chat_postMessage(
            channel=body["container"]["channel_id"],
            thread_ts=body["container"]["message_ts"],
            text=f"❌ Error approving proposal: {str(e)}"
        )


@app.action("reject_proposal")
def handle_reject_proposal(ack, body, logger):
    """
    Handle rejection button click.
    """
    ack()  # Acknowledge the action
    
    proposal_id = body["actions"][0]["value"]
    user = body["user"]["id"]
    
    logger.info(f"User {user} rejecting proposal {proposal_id}")
    
    try:
        from src.core.proposal import ProposalManager
        manager = ProposalManager()
        manager.reject_proposal(proposal_id, f"Rejected by user via Slack")
        
        # Update the message to show it's been rejected
        app.client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            text=f"❌ Proposal rejected by <@{user}>.",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *Proposal Rejected*\n\nRejected by <@{user}>."
                    }
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to reject proposal: {e}")
        app.client.chat_postMessage(
            channel=body["container"]["channel_id"],
            thread_ts=body["container"]["message_ts"],
            text=f"❌ Error rejecting proposal: {str(e)}"
        )


def send_proposal_notification(proposal):
    """Send an interactive message to Slack when a proposal is created."""
    global slack_client
    if not slack_client:
        from slack_sdk import WebClient
        slack_client = WebClient(token=os.environ.get("SLACK_USER_TOKEN"))
    
    try:
        # Get the user who installed the app (the user token owner)
        # For simplicity, we'll post to a specific channel or DM
        # You can configure this via environment variable
        notification_channel = os.environ.get("SLACK_NOTIFICATION_CHANNEL", "@me")
        
        proposal_type = proposal.get("proposal_type", "unknown")
        reason = proposal.get("reason", "No reason provided")
        proposal_id = proposal.get("id")
        payload = proposal.get("payload", {})
        
        # Build a nice formatted message
        payload_preview = str(payload)[:200] + "..." if len(str(payload)) > 200 else str(payload)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 New Proposal Awaiting Approval"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:*\n{proposal_type.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Proposal ID:*\n`{proposal_id}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reason:*\n{reason}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Payload Preview:*\n```{payload_preview}```"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "action_id": "approve_proposal",
                        "value": proposal_id
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "action_id": "reject_proposal",
                        "value": proposal_id
                    }
                ]
            }
        ]
        
        slack_client.chat_postMessage(
            channel=notification_channel,
            text=f"New proposal: {proposal_type}",
            blocks=blocks
        )
        
    except Exception as e:
        print(f"Failed to send proposal notification: {e}")


def main():
    """Start the Slack bot with Socket Mode."""
    app_token = os.environ.get("SLACK_APP_TOKEN")
    user_token = os.environ.get("SLACK_USER_TOKEN")
    
    if not app_token or not user_token:
        print("❌ Error: SLACK_APP_TOKEN and SLACK_USER_TOKEN must be set in .env")
        sys.exit(1)
    
    # Store client globally for notifications
    global slack_client
    slack_client = app.client
    
    print("🤖 Starting Slack bot...")
    print("📝 Using user token - messages will post as your user account")
    print("✅ Bot is running! Send a DM or @mention to interact.")
    print("💡 Interactive proposal buttons enabled!")
    print("Press Ctrl+C to stop.")
    
    # Start Socket Mode handler
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()
