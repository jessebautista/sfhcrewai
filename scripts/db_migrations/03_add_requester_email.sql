-- Add requester_email column to proposals table

ALTER TABLE proposals
ADD COLUMN IF NOT EXISTS requester_email TEXT;

-- Add index for efficient querying
CREATE INDEX IF NOT EXISTS idx_proposals_requester_email ON proposals(requester_email);
