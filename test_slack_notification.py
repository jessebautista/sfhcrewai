"""
Test script to verify Slack notification works
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from slack_sdk import WebClient

# Test sending a message to the notification channel
token = os.environ.get("SLACK_USER_TOKEN")
channel = os.environ.get("SLACK_NOTIFICATION_CHANNEL", "#news-approval")

print(f"Token: {token[:20]}...")
print(f"Channel: {channel}")

client = WebClient(token=token)

# Test 1: Get user info
print("\n1. Testing auth...")
auth = client.auth_test()
print(f"✅ Authenticated as: {auth['user']}")

# Test 2: Send simple message
print(f"\n2. Sending test message to {channel}...")
try:
    result = client.chat_postMessage(
        channel=channel,
        text="Test message from proposal notification system"
    )
    print(f"✅ Message sent! ts: {result['ts']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Send message with buttons
print(f"\n3. Sending message with buttons...")
try:
    result = client.chat_postMessage(
        channel=channel,
        text="Test proposal notification",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 Test Proposal"
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
                        "value": "test-123"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "action_id": "reject_proposal",
                        "value": "test-123"
                    }
                ]
            }
        ]
    )
    print(f"✅ Message with buttons sent! ts: {result['ts']}")
    print(f"\nCheck {channel} for the test message!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
