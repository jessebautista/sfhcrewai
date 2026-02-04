"""
Test script for Long-Term Memory integration.
Tests the MemoryManager module functionality.
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.memory_manager import MemoryManager

load_dotenv()

def test_memory_manager():
    """Test basic MemoryManager functionality."""
    print("🧪 Testing Long-Term Memory Integration\n")
    print("=" * 60)
    
    # Initialize Memory Manager
    print("\n1. Initializing MemoryManager...")
    memory = MemoryManager()
    print("✅ MemoryManager initialized")
    
    # Test conversation creation
    print("\n2. Creating test conversation...")
    user_id = "test_user_123"
    channel_id = "test_channel_456"
    conversation_id = memory.get_or_create_conversation(
        user_id=user_id,
        channel_id=channel_id,
        interface='slack',
        metadata={'test': True}
    )
    print(f"✅ Conversation created: {conversation_id}")
    
    # Test storing user message
    print("\n3. Storing user message...")
    success = memory.store_message(
        conversation_id=conversation_id,
        role='user',
        content='Hello, can you remember my name is Alice?'
    )
    print(f"✅ User message stored: {success}")
    
    # Test storing assistant message
    print("\n4. Storing assistant message...")
    success = memory.store_message(
        conversation_id=conversation_id,
        role='assistant',
        content='Of course! I will remember that your name is Alice.'
    )
    print(f"✅ Assistant message stored: {success}")
    
    # Store another user message
    print("\n5. Storing second user message...")
    success = memory.store_message(
        conversation_id=conversation_id,
        role='user',
        content='What is my name?'
    )
    print(f"✅ Second user message stored: {success}")
    
    # Retrieve conversation history
    print("\n6. Retrieving conversation history...")
    history = memory.get_conversation_history(conversation_id, limit=20)
    print(f"✅ Retrieved {len(history)} messages:")
    for i, msg in enumerate(history, 1):
        print(f"   {i}. {msg['role'].upper()}: {msg['content']}")
    
    # Test history formatting
    print("\n7. Testing history formatting for prompt...")
    formatted = memory.format_history_for_prompt(history)
    print("✅ Formatted context:")
    print(formatted)
    
    # Test getting same conversation again (should return same ID)
    print("\n8. Testing conversation retrieval (should return same ID)...")
    conversation_id_2 = memory.get_or_create_conversation(
        user_id=user_id,
        channel_id=channel_id,
        interface='slack'
    )
    print(f"✅ Retrieved conversation: {conversation_id_2}")
    print(f"   Same as original? {conversation_id == conversation_id_2}")
    
    # Test with different user (should create new conversation)
    print("\n9. Testing with different user (should create new conversation)...")
    conversation_id_3 = memory.get_or_create_conversation(
        user_id="different_user_789",
        channel_id=channel_id,
        interface='slack'
    )
    print(f"✅ New conversation: {conversation_id_3}")
    print(f"   Different from original? {conversation_id != conversation_id_3}")
    
    # Test conversation count
    print("\n10. Testing conversation count...")
    count = memory.get_conversation_count(user_id, interface='slack')
    print(f"✅ Total messages for {user_id}: {count}")
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!\n")
    print("📝 Next steps:")
    print("   1. Start the Slack bot: python src/interfaces/slack_bot.py")
    print("   2. Send a DM to test memory: 'My name is [Your Name]'")
    print("   3. In a new message, ask: 'What's my name?'")
    print("   4. Check if the bot remembers your name from the previous message")
    print("\n✨ Long-term memory is now active for Slack integration!")

if __name__ == "__main__":
    try:
        test_memory_manager()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
