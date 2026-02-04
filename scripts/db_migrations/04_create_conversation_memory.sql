-- Create conversation memory tables for long-term memory support
-- This enables persistent conversation history across Slack, Email, and Web interfaces

-- Table: conversations
-- Tracks unique conversation sessions between users and the bot
create table if not exists conversations (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  user_id text not null,           -- Slack user ID, email address, or web session ID
  channel_id text not null,         -- Slack channel/DM ID, email thread, or web session
  interface text default 'slack' check (interface in ('slack', 'email', 'web')) not null,
  metadata jsonb                    -- Additional context (thread_ts, subject line, etc.)
);

-- Table: conversation_messages
-- Stores individual messages within conversations
create table if not exists conversation_messages (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  conversation_id uuid references conversations(id) on delete cascade not null,
  role text check (role in ('user', 'assistant')) not null,
  content text not null,
  metadata jsonb                    -- Attachments, file URLs, tokens used, etc.
);

-- Indexes for efficient conversation lookup
create index if not exists idx_conversations_lookup on conversations(user_id, channel_id, interface);
create index if not exists idx_conversations_updated on conversations(updated_at desc);

-- Indexes for efficient message retrieval
create index if not exists idx_messages_conversation on conversation_messages(conversation_id, created_at);
create index if not exists idx_messages_created on conversation_messages(created_at desc);
