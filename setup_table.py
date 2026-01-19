"""
Create agent_logs table using Supabase's REST API with RPC
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

print("🔧 Creating agent_logs table...")
print("=" * 60)

# We'll create a simple test record to verify the logger works
# But first, let's try to create the table using a direct SQL approach

# Supabase doesn't expose raw SQL execution via REST API for security
# We need to use the database connection string or dashboard

# Let's try an alternative: create a stored procedure first, then call it
# Actually, that also requires creating the procedure via SQL first

# BEST APPROACH: Use the PostgREST database connection
# We'll need the actual PostgreSQL connection parameters

# For now, let's just insert a test record which will show the table needs to be created
from supabase import create_client

client = create_client(url, key)

# Try to create a test log entry
test_log = {
    "agent_name": "TestAgent",
    "event_type": "test",
    "message": "Testing observability setup",
    "metadata": {"test": True},
    "status": "info"
}

try:
    result = client.table("agent_logs").insert(test_log).execute()
    print("✅ Successfully created test log entry!")
    print(f"   Entry ID: {result.data[0]['id']}")
    print("\n🎉 Table exists and logging works!")
    sys.exit(0)
except Exception as e:
    error_msg = str(e)
    if "agent_logs" in error_msg.lower() and "does not exist" in error_msg.lower():
        print("⚠️  Table 'agent_logs' does not exist.")
        print("\n📝 SQL Required:")
        print("-" * 60)
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
        print("-" * 60)
        
        # Write SQL to a temp file for easy copy-paste
        with open("create_table.sql", "w") as f:
            f.write(sql)
        
        print("\n💡 SQL saved to: create_table.sql")
        print("   Copy and paste it into Supabase Dashboard > SQL Editor")
        print("\n   OR manually create the table, then run this script again.")
        sys.exit(1)
    else:
        print(f"❌ Error: {e}")
        sys.exit(1)
