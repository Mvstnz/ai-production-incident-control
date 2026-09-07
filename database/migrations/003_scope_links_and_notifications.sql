ALTER TABLE ops.incidents ADD CONSTRAINT current_impact_scope FOREIGN KEY(scope_id,current_impact_id) REFERENCES ops.impact_assessments(scope_id,id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE ops.incidents ADD CONSTRAINT prior_incident_scope FOREIGN KEY(scope_id,prior_incident_id) REFERENCES ops.incidents(scope_id,id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE ops.incidents ADD CONSTRAINT incident_type_allowed CHECK(incident_type IN ('SUPPLIER_DELAY','MACHINE_BREAKDOWN','QUALITY_ISSUE'));
CREATE TABLE ops.sandbox_notifications(id uuid PRIMARY KEY,scope_id uuid NOT NULL REFERENCES ops.scopes(id),event_id uuid NOT NULL UNIQUE REFERENCES ops.outbox_events(id) ON DELETE CASCADE,recipient text NOT NULL CHECK(recipient='operations@example.test'),body jsonb NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE ops.incident_actions ADD COLUMN completed_at timestamptz;
