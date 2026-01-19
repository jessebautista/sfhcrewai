create table if not exists agent_logs (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  agent_name text not null,
  event_type text not null,
  message text,
  metadata jsonb,
  status text
);

create index if not exists idx_logs_created_at on agent_logs(created_at desc);
