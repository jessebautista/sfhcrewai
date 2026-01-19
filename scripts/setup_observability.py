"""
Create the agent_logs table using Supabase client's table creation API
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

client = create_client(url, key)

print("🔧 Setting up Observability...")
print("=" * 60)

# Try to check if table exists by querying it
try:
    result = client.table("agent_logs").select("id").limit(1).execute()
    print("✅ Table 'agent_logs' already exists!")
    print(f"   Found {len(result.data)} records (showing max 1)")
    sys.exit(0)
except Exception as e:
    error_msg = str(e).lower()
    if "relation" in error_msg and "does not exist" in error_msg:
        print("ℹ️  Table 'agent_logs' does not exist yet.")
        print("\n📋 Creating table via Supabase Management API...")
        
        # Unfortunately, the standard Supabase Python client doesn't support
        # direct SQL execution or table creation via API
        # We need to use the REST API directly
        
        import requests
        
        # Use the service role key to execute SQL via REST API
        # Supabase has a postgrest endpoint for this
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Try using RPC to execute SQL (requires a stored procedure)
        # This won't work unless we have a pre-existing procedure
        
        print("\n⚠️  Direct table creation via API is not supported.")
        print("    The table needs to be created via SQL.")
        print("\n" + "=" * 60)
        print("MANUAL STEP REQUIRED:")
        print("=" * 60)
        print("\nPlease create the table by running this SQL in Supabase:")
        print("\n" + "-" * 60)
        
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
        print("\n💡 You can run this via the Supabase Dashboard > SQL Editor")
        print("=" * 60)
        sys.exit(1)
    else:
        print(f"❌ Error checking table: {e}")
        sys.exit(1)
