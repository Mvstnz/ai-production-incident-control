# Handover

The executable project is published at [Mvstnz/ai-production-incident-control](https://github.com/Mvstnz/ai-production-incident-control), branch `main`. Use `rtk git log -1 --oneline` for the exact checked-out revision. [Fresh GitHub CI passed](https://github.com/Mvstnz/ai-production-incident-control/actions/runs/34124335738) for application revision `8fb00eb813c618e3588134e5c44997f53cc3a451`; subsequent delivery changes add verification scripts, evidence and documentation without changing application code or workflow graphs. Hosting of the application itself is separate and has not been performed.

Run `rtk proxy python scripts/bootstrap.py` from the repository. Open http://127.0.0.1:5173 and use the randomly generated `.local/credentials.json`. Services bind only to loopback; the ERP and database have no host ports. Keep `.env`, `.local`, database volumes and private editor credentials out of Git and shared archives.

## What is demonstrated

Real local n8n execution coordinates intake, verification/correlation, immutable ERP impact, risk and action planning, human approval, action execution, recovery, error handling and digest. PostgreSQL owns domain state and concurrency. Test commands and observed results are linked from README and the acceptance matrix. Fixture evaluation is not live LLM evaluation. Target readback is not target execution.

The shared viewer scope contains supplier, machine and quality incidents assessed by actual local n8n executions `1429`, `1433` and `1437`. Their consequential actions remain waiting for the responsible human approval. Repeated bootstrap preserves those identities; independent guided demos create separate owned scopes.

The final workflow inventory maps all ten local IDs to all ten connected-cloud IDs. Local cleaned runtime exports are in `n8n/exports/local`; the actual target readbacks are in `n8n/target`. `scripts/build_workflows.py` is the reviewed local graph source, and `scripts/sync_exports.py` asserts that the persisted local graphs match it.

## Remaining connected deployment

M6/AC31 remain `BLOCKED_TARGET_CONNECTION`. Creation and read access worked through the n8n MCP connector. The automatic approval gate rejected update and execute operations under policy `never`. The session must permit the explicitly requested operations before continuing; do not bypass that gate.

Provide an authorized reachable HTTPS deployment of the Operations and Mock ERP APIs and bind the four purpose-specific n8n credentials. Configure the dashboard origin and allowed n8n continuation origin. The current cloud `.invalid` URLs are clearly marked placeholders. No public tunnel, cloud hosting, LLM spending or real delivery was initiated.

Read the current target workflow before any change, export it for rollback, apply current local graph differences (including WF04 retry metadata and WF08 recovery response), bind target workflow references, configure timezone/retention/caller policy/error routing, validate, publish only within the authorized sandbox and execute the test cases. Replace NOT_RUN only after actual execution evidence is retrieved. Target release version is currently unknown.

## Rollback and retention

- Stop all local runtime activity while retaining volumes: `rtk docker compose stop`. Resume: `rtk docker compose up -d`.
- A prior local workflow is exported to `.local/rollback-WFxx.json` before mutation. Restore one: `rtk docker compose exec -T n8n n8n import:workflow --input=/project/local/rollback-WF04.json`; publish its known APIC ID with `n8n publish:workflow --id=APICWF0400000001`, then `rtk docker compose restart n8n n8n-runners`. Restore matching application code if the API contract also changed.
- Source rollback uses a reviewed Git revision in a separate checkout and the matching database backup. Migrations are forward-only; no automatic destructive down-migration is provided.
- Use the dashboard's owner-scoped demo reset only after known/in-flight actions are reconciled. Reset keeps immutable audit history and touches only the selected synthetic scope.
- Cloud flows are inactive and produce no runtime effects. Leave them inactive or, if cleanup is desired and authorized, archive only the ten listed APIC core IDs and the optional APIC probe. Never touch unrelated flows.
- n8n execution payloads are retained for168hours. App audit retention is not automated in this portfolio demo. A production retention/export policy would need to be set before deployment.

No exactly-once claim is made for external delivery. UNKNOWN_OUTCOME is intentionally excluded from automatic retries and requires reconciliation.

## Environment repair performed

Docker Desktop initially could not start because stale Windows runtime socket directories remained. With the backend stopped, only these runtime directories were renamed as backups under AppData/Local: `Docker/run.apic-backup-20260907`, `Docker/run.apic-backup2-20260907`, `docker-secrets-engine.apic-backup-20260907`. No Docker volume or user database was deleted. The verified engine is29.2.1. These runtime-only backups are outside this repository and are not needed to run the app.
