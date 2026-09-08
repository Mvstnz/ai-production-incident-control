# Implementation contract

The executable contracts are `backend/models.py`, the FastAPI routes in `backend/main.py` and `backend/erp.py`, and the typed n8n stage envelopes. Public input uses `schema_version`, `scope_id`, source identity, offset-aware timestamps and either email text or structured facts.

ERP snapshots are immutable, scope-bound JSON with `snapshot_id`, `erp_revision`, `incident_type`, `analysis_time` and `data`. Canonical demo inputs live in the three JSON fixtures. Runtime code does not consume expected test outputs.

n8n owns orchestration; API services own atomic state transitions and deterministic calculations. Plans bind exact revisions, hashes and payloads. See the build specification for the full invariants.
