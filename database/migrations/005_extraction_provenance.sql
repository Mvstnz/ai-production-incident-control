ALTER TABLE ops.incident_revisions
    ADD COLUMN extraction_metadata jsonb NOT NULL DEFAULT '{}';
