# Technical Spec: Human-in-the-Loop (HITL) Workflow

**Status**: Draft
**Priority**: Medium/Hard
**Type**: Core Logic Enhancement

## 1. Overview
The current "wait signal" is in-memory and fragile. This feature moves the approval queue to the database, allowing:
1.  Asynchronous approvals (User can approve hours after agent submits).
2.  Persistence across restarts.
3.  Multi-stage workflows (Draft -> Pending -> Approved/Rejected).

## 2. Infrastructure Changes

### 2.1 Database Schema (Supabase)
Create a `proposals` table.

```sql
create type proposal_status as enum ('pending', 'approved', 'rejected', 'failed');

create table proposals (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  proposal_type text check (proposal_type in ('create', 'update')),
  status proposal_status default 'pending',
  target_record_id uuid,           -- Null for 'create' actions
  payload jsonb not null,          -- The content to write/update
  reason text,                     -- Agent's reasoning
  feedback text                    -- Admin's rejection reason
);
```

## 3. Implementation Details

### 3.1 Proposal Manager Refactor (`src/core/proposal.py`)
Replace the threading/memory logic with Supabase calls.

-   `submit_proposal(data)` -> `INSERT INTO proposals ...`
-   `get_pending_proposals()` -> `SELECT * FROM proposals WHERE status = 'pending'`
-   `approve_proposal(id)` -> 
    1. Update status to 'approved'.
    2. Execute the actual write to the `news` table.

### 3.2 UI Updates (`src/ui/app.py`)
The "Admin Controls" sidebar must be upgraded:
-   Fetch list of ALL pending proposals.
-   Render them as a list/cards.
-   "Approve" button triggers the transaction.
-   "Reject" button opens a text input for feedback (optional).

## 4. Advanced: Agent Feedback Loop
If a proposal is rejected with feedback, we can optionally trigger the Orchestrator to "fix" it.
-   Monitor `proposals` table for `status='rejected'`.
-   Feed `payload` + `feedback` back into the Agent.

## 5. Verification
1.  Agent submits draft -> Check DB table `proposals` (should exist with status `pending`).
2.  Restart App -> Draft should still be visible in UI.
3.  Click Approve -> Check DB table `news` (record should be created/updated) AND `proposals` (status `approved`).
