-- Count each real provider invocation while keeping repeated preparation of the
-- same n8n execution idempotent.
ALTER TABLE ops.live_ai_calls ADD COLUMN execution_id text;
UPDATE ops.live_ai_calls SET execution_id='legacy:' || job_id::text;
ALTER TABLE ops.live_ai_calls ALTER COLUMN execution_id SET NOT NULL;
ALTER TABLE ops.live_ai_calls DROP CONSTRAINT live_ai_calls_pkey;
ALTER TABLE ops.live_ai_calls ADD PRIMARY KEY(job_id,execution_id);
