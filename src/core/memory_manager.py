"""
Memory Manager for tracking conversation history across interfaces.
Supports Slack, Email, and Web UI with persistent storage in Supabase.
"""
import os
from typing import List, Dict, Optional, Any
from datetime import datetime


class MemoryManager:
    """
    Manages conversation memory for multi-turn interactions.
    Stores and retrieves conversation history from the database.
    """
    
    def __init__(self):
        """Initialize Memory Manager with Supabase connection."""
        from src.tools.supabase_ops import SupabaseManager
        self.supabase = SupabaseManager()
        
    def get_or_create_conversation(
        self, 
        user_id: str, 
        channel_id: str, 
        interface: str = 'slack',
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get existing conversation or create a new one.
        
        Args:
            user_id: Unique user identifier (Slack user ID, email, etc.)
            channel_id: Channel/conversation identifier
            interface: Interface type ('slack', 'email', 'web')
            metadata: Optional metadata (thread_ts, subject, etc.)
            
        Returns:
            conversation_id: UUID of the conversation
        """
        try:
            # Try to find existing conversation
            result = self.supabase.client.table('conversations').select('id').eq(
                'user_id', user_id
            ).eq(
                'channel_id', channel_id
            ).eq(
                'interface', interface
            ).execute()
            
            if result.data and len(result.data) > 0:
                # Update the updated_at timestamp
                conversation_id = result.data[0]['id']
                self.supabase.client.table('conversations').update({
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', conversation_id).execute()
                
                return conversation_id
            
            # Create new conversation
            new_conversation = {
                'user_id': user_id,
                'channel_id': channel_id,
                'interface': interface,
                'metadata': metadata or {}
            }
            
            result = self.supabase.client.table('conversations').insert(
                new_conversation
            ).execute()
            
            return result.data[0]['id']
            
        except Exception as e:
            print(f"⚠️ Memory: Failed to get/create conversation: {e}")
            # Return a fallback ID (won't persist but allows graceful degradation)
            return f"fallback-{user_id}-{channel_id}"
    
    def store_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a message in the conversation history.
        
        Args:
            conversation_id: UUID of the conversation
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (attachments, file URLs, etc.)
            
        Returns:
            Success status
        """
        try:
            # Don't store if using fallback ID
            if conversation_id.startswith('fallback-'):
                return False
                
            message = {
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'metadata': metadata or {}
            }
            
            self.supabase.client.table('conversation_messages').insert(
                message
            ).execute()
            
            # Update conversation timestamp
            self.supabase.client.table('conversations').update({
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', conversation_id).execute()
            
            return True
            
        except Exception as e:
            print(f"⚠️ Memory: Failed to store message: {e}")
            return False
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Retrieve recent conversation history.
        
        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to retrieve (default: 20)
            
        Returns:
            List of messages in format [{"role": "user/assistant", "content": "..."}]
            Ordered chronologically (oldest first)
        """
        try:
            # Don't retrieve if using fallback ID
            if conversation_id.startswith('fallback-'):
                return []
                
            result = self.supabase.client.table('conversation_messages').select(
                'role, content, created_at'
            ).eq(
                'conversation_id', conversation_id
            ).order(
                'created_at', desc=True
            ).limit(limit).execute()
            
            if not result.data:
                return []
            
            # Reverse to get oldest first (chronological order)
            messages = result.data[::-1]
            
            return [
                {'role': msg['role'], 'content': msg['content']}
                for msg in messages
            ]
            
        except Exception as e:
            print(f"⚠️ Memory: Failed to retrieve history: {e}")
            return []
    
    def format_history_for_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format message history into a context string for the agent.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Formatted string for agent prompt
        """
        if not messages:
            return ""
        
        # Build conversation context
        formatted_lines = ["[Previous Conversation Context]"]
        
        for msg in messages:
            role_label = "User" if msg['role'] == 'user' else "Assistant"
            formatted_lines.append(f"{role_label}: {msg['content']}")
        
        formatted_lines.append("[End of Previous Context]\n")
        
        return "\n".join(formatted_lines)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Delete all messages in a conversation.
        Useful for "reset memory" functionality.
        
        Args:
            conversation_id: UUID of the conversation
            
        Returns:
            Success status
        """
        try:
            # Don't clear if using fallback ID
            if conversation_id.startswith('fallback-'):
                return False
                
            self.supabase.client.table('conversation_messages').delete().eq(
                'conversation_id', conversation_id
            ).execute()
            
            print(f"✅ Memory: Cleared conversation {conversation_id}")
            return True
            
        except Exception as e:
            print(f"⚠️ Memory: Failed to clear conversation: {e}")
            return False
    
    def get_conversation_count(self, user_id: str, interface: str = 'slack') -> int:
        """
        Get the number of messages in all conversations for a user.
        Useful for analytics.
        
        Args:
            user_id: User identifier
            interface: Interface type
            
        Returns:
            Total message count
        """
        try:
            # Get all conversations for this user
            conversations = self.supabase.client.table('conversations').select(
                'id'
            ).eq(
                'user_id', user_id
            ).eq(
                'interface', interface
            ).execute()
            
            if not conversations.data:
                return 0
            
            # Count messages across all conversations
            total = 0
            for conv in conversations.data:
                result = self.supabase.client.table('conversation_messages').select(
                    'id', count='exact'
                ).eq(
                    'conversation_id', conv['id']
                ).execute()
                total += result.count or 0
            
            return total
            
        except Exception as e:
            print(f"⚠️ Memory: Failed to get conversation count: {e}")
            return 0
