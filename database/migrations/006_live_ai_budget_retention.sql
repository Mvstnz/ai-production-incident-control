-- Budget consumption is append-only even when a synthetic demo scope is reset.
ALTER TABLE ops.live_ai_calls
    DROP CONSTRAINT IF EXISTS live_ai_calls_job_id_fkey;
