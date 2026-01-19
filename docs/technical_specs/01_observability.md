# Technical Spec: Observability & Monitoring

**Status**: Draft
**Priority**: High (Foundation)

## 1. Overview
The goal is to provide visibility into the AI agents' activities, performance, and health. This involves centralized logging to Supabase and a visualization dashboard in Streamlit.

## 2. Infrastructure Changes

### 2.1 Database Schema (Supabase)
Create a new table `agent_logs` to store structured event data.

```sql
create table agent_logs (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  agent_name text not null,        -- e.g., "Orchestrator", "Fetcher"
  event_type text not null,        -- e.g., "mission_start", "step", "error", "mission_end"
  message text,                    -- Human readable summary
  metadata jsonb,                  -- Full prompt, tools used, token usage stats
  status text                      -- "success", "failure", "running"
);

-- Index for faster querying by time
create index idx_logs_created_at on agent_logs(created_at desc);
```

## 3. Implementation Details

### 3.1 Logger Module (`src/core/logger.py`)
A non-blocking logger class that pushes data to Supabase.

```python
import threading
from src.tools.supabase_ops import SupabaseManager

class AgentLogger:
    def log(self, agent_name, event_type, message, metadata=None, status="info"):
        # Run in thread to not block the agent execution
        threading.Thread(target=self._push_to_db, args=(...)).start()

    def _push_to_db(self, ...):
         # Supabase insert
         pass
```

### 3.2 Agent Instrumentation
Modify `src/agents/orchestrator.py` to inject the logger.

-   **Start**: `logger.log("Orchestrator", "mission_start", "Processing user request", {"prompt": prompt})`
-   **End**: `logger.log("Orchestrator", "mission_end", "Finished", {"result": result})`

### 3.3 Dashboard UI (`src/ui/dashboard.py`)
A new Streamlit page showing:

1.  **KPIs**: Total runs (24h), Success Rate, Avg Duration.
2.  **Activity Feed**: Table of `agent_logs` sorted by `created_at desc`.
3.  **Details View**: Click on a row to see full JSON metadata (prompts/responses).

## 4. Verification
1.  Run a mission.
2.  Check `agent_logs` table for new rows.
3.  Open Dashboard and confirm the mission appears.
