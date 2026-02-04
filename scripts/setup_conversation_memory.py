"""
Helper script to display SQL migration instructions for conversation memory tables.
Since Supabase Python client doesn't support raw DDL SQL execution,
the SQL must be run manually via the Supabase Dashboard.
"""
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL", "https://your-project.supabase.co")

print("=" * 80)
print("🧠 LONG-TERM MEMORY: Database Migration Instructions")
print("=" * 80)
print("\nThe Supabase Python client doesn't support executing raw DDL SQL.")
print("You need to create the tables manually via the Supabase Dashboard.\n")
print("=" * 80)
print("STEP-BY-STEP INSTRUCTIONS:")
print("=" * 80)
print("\n1. Open your browser and go to your Supabase Dashboard:")
print(f"   {url.replace('https://', 'https://supabase.com/dashboard/project/')}")
print("\n2. Click 'SQL Editor' in the left sidebar")
print("\n3. Click '+ New Query' button")
print("\n4. Copy and paste the SQL below into the editor:")
print("\n" + "-" * 80)

sql = """-- Create conversation memory tables for long-term memory support

-- Table: conversations
-- Tracks unique conversation sessions between users and the bot
create table if not exists conversations (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  user_id text not null,
  channel_id text not null,
  interface text default 'slack' check (interface in ('slack', 'email', 'web')) not null,
  metadata jsonb
);

-- Table: conversation_messages
-- Stores individual messages within conversations
create table if not exists conversation_messages (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  conversation_id uuid references conversations(id) on delete cascade not null,
  role text check (role in ('user', 'assistant')) not null,
  content text not null,
  metadata jsonb
);

-- Indexes for efficient conversation lookup
create index if not exists idx_conversations_lookup on conversations(user_id, channel_id, interface);
create index if not exists idx_conversations_updated on conversations(updated_at desc);

-- Indexes for efficient message retrieval
create index if not exists idx_messages_conversation on conversation_messages(conversation_id, created_at);
create index if not exists idx_messages_created on conversation_messages(created_at desc);
"""

print(sql)
print("-" * 80)

print("\n5. Click 'Run' button (or press Ctrl+Enter / Cmd+Enter)")
print("\n6. Wait for success message: 'Success. No rows returned'")
print("\n7. Verify tables were created:")
print("   - Click 'Table Editor' in left sidebar")
print("   - Look for 'conversations' and 'conversation_messages' tables")
print("\n8. Test the memory manager:")
print("   python tests/test_memory_manager.py")
print("\n" + "=" * 80)
print("✅ After completing these steps, long-term memory will be ready!")
print("=" * 80)
print("\n💡 Next Steps:")
print("   1. Start Slack bot: python src/interfaces/slack_bot.py")
print("   2. Send a DM: 'My name is Alice'")
print("   3. Send another DM: 'What's my name?'")
print("   4. Bot should remember 'Alice' from previous message!\n")
