"""
Simple script to create the agent_logs table using Supabase HTTP API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Try to create the table using RPC if available
# Note: This requires setting up a stored procedure in Supabase first.
# Easier method: Use the Supabase Dashboard SQL Editor

print("=" * 70)
print("📊 Agent Logs Table Creation")
print("=" * 70)
print("\nThe Supabase Python client doesn't support executing raw DDL SQL.")
print("You need to create the table manually via the Supabase Dashboard.")
print("\n" + "=" * 70)
print("STEP-BY-STEP INSTRUCTIONS:")
print("=" * 70)
print("\n1. Open your browser and go to:")
print(f"   {url.replace('https://', 'https://app.supabase.com/project/')}")
print("\n2. Click 'SQL Editor' in the left sidebar")
print("\n3. Click 'New Query' or the '+' button")
print("\n4. Copy and paste this SQL:")
print("\n" + "-" * 70)

sql = """create table if not exists agent_logs (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  agent_name text not null,
  event_type text not null,
  message text,
  metadata jsonb,
  status text
);

create index if not exists idx_logs_created_at on agent_logs(created_at desc);"""

print(sql)
print("-" * 70)

print("\n5. Click 'Run' (or press Ctrl+Enter)")
print("\n6. Verify success message appears")
print("\n7. Go to 'Table Editor' and confirm 'agent_logs' table exists")
print("\n" + "=" * 70)
print("✅ After completing these steps, the Observability feature will be ready!")
print("=" * 70)
