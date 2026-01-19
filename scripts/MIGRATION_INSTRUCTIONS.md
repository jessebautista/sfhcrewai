# Database Migration Instructions

## Create the agent_logs Table

Since we're using Supabase's service role key, we need to run the SQL migration through the Supabase Dashboard.

### Steps:

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Navigate to your project: seaoujebnhmuaeolhswo

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Run the Migration SQL**
   - Copy the contents of `scripts/db_migrations/01_create_agent_logs.sql`
   - Paste into the SQL editor
   - Click "Run" or press Ctrl+Enter

4. **Verify Creation**
   - Go to "Table Editor" in the left sidebar
   - You should see a new table called `agent_logs`
   - The table should have the following columns:
     - `id` (uuid, primary key)
     - `created_at` (timestamp with time zone)
     - `agent_name` (text)
     - `event_type` (text)
     - `message` (text)
     - `metadata` (jsonb)
     - `status` (text)

## Alternative: Direct PostgreSQL Access

If you have the PostgreSQL connection string, you can use `psql`:

```bash
psql "postgresql://postgres:[password]@db.seaoujebnhmuaeolhswo.supabase.co:5432/postgres" -f scripts/db_migrations/01_create_agent_logs.sql
```

Replace `[password]` with your database password from the Supabase dashboard.
