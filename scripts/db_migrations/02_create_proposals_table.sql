-- Create proposal_status enum type
create type proposal_status as enum ('pending', 'approved', 'rejected', 'failed');

-- Create proposals table
create table if not exists proposals (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  proposal_type text check (proposal_type in ('create', 'update')) not null,
  status proposal_status default 'pending' not null,
  target_record_id text,           -- Null for 'create' actions, ID for 'update' actions
  payload jsonb not null,          -- The content to write/update
  reason text,                     -- Agent's reasoning for the proposal
  feedback text                    -- Admin's rejection reason (if rejected)
);

-- Create index on status for efficient pending proposal queries
create index if not exists idx_proposals_status on proposals(status);

-- Create index on created_at for sorting
create index if not exists idx_proposals_created_at on proposals(created_at desc);
