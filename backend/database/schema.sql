-- Execute this script in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    original_code TEXT NOT NULL,
    result JSONB,
    error_message TEXT
);

-- Optional: Create an index on status for faster polling
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

-- Optional: Create a function to automatically update 'updated_at'
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jobs_modtime
BEFORE UPDATE ON jobs
FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
