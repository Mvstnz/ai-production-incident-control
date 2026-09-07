CREATE TABLE ops.live_ai_calls(
    job_id uuid PRIMARY KEY,
    scope_id uuid NOT NULL REFERENCES ops.scopes(id),
    model text NOT NULL,
    claimed_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX live_ai_calls_scope_claimed ON ops.live_ai_calls(scope_id,claimed_at);
