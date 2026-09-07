# AI Production Incident Control

Turn a manufacturing disruption into verified operational impact, an exact human-reviewed response and an auditable action trail. Ten visible n8n workflows coordinate a FastAPI Operations service, a separate synthetic ERP service, PostgreSQL and a React dashboard.

**This is a synthetic portfolio demo.** Guided scenarios use a conservative fixture provider. An optional, explicitly enabled Gemini path can extract a freely edited synthetic supplier email; the backend still requires exact source quotes and an ERP-consistent result before accepting facts. Messages go to local Mailpit, tickets remain in the sandbox, and ERP changes affect synthetic data only. A completed notification leaves an incident in monitoring; resolution requires current operational evidence.

The local application has executed real n8n workflows, including one authorized synthetic Gemini mail smoke run. That run proves connectivity and the guarded path, not statistical model quality. Cloud workflows have also been created and read back, but **connected core-workflow execution remains blocked** by non-routable Operations/ERP placeholders. The isolated cloud credential probe succeeded without publishing a workflow. See [acceptance evidence](acceptance/acceptance-matrix.json), [workflow IDs](docs/implementation/workflow-inventory.md) and [remaining blockers](docs/BLOCKERS.md).

![Actual local operations overview](evidence/screenshots/dashboard-overview.png)

## Start locally

Prerequisites: Docker Engine with Compose, Python 3.12, Git and [RTK](https://github.com/rtk-ai/rtk). A source frontend build additionally uses Node 24.12.0 and npm; the Compose build supplies Node itself. The verified versions and image digests are in [versions.lock](versions.lock).

From this repository directory:

```powershell
rtk proxy python scripts/bootstrap.py
```

Bootstrap generates random local credentials once, starts persistent infrastructure, applies migrations, seeds the synthetic ERP, imports and publishes the ten local workflows, and builds the dashboard. Three shared showcase incidents enter the actual n8n intake so the viewer account has real supplier, machine and quality results to inspect. Consequential actions still await human approval. Existing showcase types, secrets and deterministic workflow IDs are preserved on subsequent runs. Initial image download/build takes several minutes.

| Service | Local address |
|---|---|
| Dashboard | http://127.0.0.1:5173 |
| n8n editor | http://127.0.0.1:5678 |
| Operations OpenAPI | http://127.0.0.1:8000/docs |
| Mailpit inbox | http://127.0.0.1:8025 |

Sign in using one of the accounts in **`.local/credentials.json`**: viewer, operator, purchasing, production_manager, quality_manager or admin. Keep that file and `.env` private. An n8n owner account is only needed for its editor; workflows execute after CLI deployment. On this delivered workspace the local editor was configured and its generated login is in `.local/n8n-owner.json`.

Choose **Run demo → Supplier delay**. The persisted assessment computes 38 required, 14 covered at need, 24 shortage, two affected production orders, €126,400 and **88 CRITICAL**. The offered partial delivery appears separately. A confirmed 10 + 30 split replaces the supply schedule, producing 14 shortage, €54,400 and **69 HIGH**.

Choose **Run demo → Analyze with Gemini** to edit and check your own synthetic supplier mail. The sender is fixed to `supplier@example.test`; the form does not send mail. Gemini can propose only typed extraction fields. Unsupported attachments, prompt-like instructions, missing evidence, invented values, ambiguous confirmation and ERP mismatches become `MANUAL_REVIEW`. Actions and recipients remain deterministic and still require their configured human approval.

Live mode is opt-in and bounded. In the private, ignored `.env`, set `AI_MODE=live`, `LLM_MODEL=models/gemini-3.1-flash-lite`, `LLM_API_KEY=<your-key>` and a positive `LLM_MAX_CALLS`, then rerun bootstrap. The model node resolves `LLM_MODEL` at runtime, and every real provider invocation (including a retry under a new n8n execution ID) consumes one durable budget slot. The key is imported into the local n8n credential store and is never part of workflow JSON, evidence or Git. Without these settings, all guided scenarios and CI continue in free fixture mode and the custom-mail endpoint stays disabled.

The machine fixture calculates **52 HIGH** and requires approval before rescheduling. The quality fixture traces a verified failed inspection to pending shipment and requires a Quality manager before blocking. Quality release is a separate proposal and approval.

## Verify

```powershell
rtk proxy python -m pip install -r backend/requirements.lock.txt
rtk proxy python -m pytest tests/unit -q
rtk proxy python -m backend.run_integration
rtk proxy python -X utf8 scripts/test_runtime.py
rtk proxy python -X utf8 scripts/test_acceptance_ordering.py
rtk proxy python -X utf8 scripts/test_resilience.py --phase normal
rtk proxy python -X utf8 scripts/smoke_live_mail.py  # only with authorized live mode
rtk npm ci
rtk npm run build
rtk proxy python scripts/scan_repository.py
```

The API suite uses a separate real PostgreSQL database, `apic_integration`. Runtime tests call the published local n8n webhooks and observe persisted results; they create new synthetic scopes. The resilience runner also has explicit restart/database phases documented in its help. Run disruption tests when other local demo users are idle.

`verify_handoff.py` is the original **handoff-package checker**, not an application test. It expects untouched NOT_RUN acceptance entries and should be run against the separately extracted v1.1 handoff, as recorded in [handoff validation](evidence/test-results/handoff-v1.1.json).

The [public repository](https://github.com/Mvstnz/ai-production-incident-control) includes a [successful fresh GitHub CI run](https://github.com/Mvstnz/ai-production-incident-control/actions/runs/34124335738) for application revision `8fb00eb813c618e3588134e5c44997f53cc3a451`. Build, 100 domain tests, 30 API tests, ten local n8n E2E cases, shared viewer examples, repeated bootstrap and the repository scan passed. Later changes only add verification scripts, evidence and documentation. Dependency versions and Action commits are pinned; the exact hosted result is retained in [CI evidence](evidence/test-results/github-ci.json).

## Architecture and evidence

- [Architecture](docs/architecture.md), [data model](docs/data-model.md), [security](docs/security.md), [limitations](docs/limitations.md)
- [Demo walkthrough](docs/demo-guide.md), [portfolio narrative](docs/portfolio.md), [handover and rollback](docs/implementation/handover.md)
- [Milestone progress](docs/implementation/progress.md), [executed test report](docs/implementation/test-report.md), [API verification](docs/implementation/backend-verification.md)
- [Real local workflow runs](evidence/workflow-runs/local-e2e.json), [Gemini mail smoke](evidence/workflow-runs/live-gemini-mail-smoke.json), [resilience](evidence/workflow-runs/resilience.json), [fixture evaluation](evidence/evaluations/fixture-v1-report.json)
- [Cloud deployment readback](evidence/workflow-runs/target-deployment.json), [screenshots](evidence/screenshots)

The source specification is [CODEX_BUILD_SPEC.md v1.1](CODEX_BUILD_SPEC.md). Archived earlier plans are retained only for provenance and must not be combined with it.

## Stop and rollback

```powershell
rtk docker compose stop
rtk docker compose up -d
```

Volumes preserve application data, n8n state and Mailpit messages. Before each local workflow update, the deploy script saves the prior owned workflow under `.local/rollback-WFxx.json`. Restore only an identified APIC workflow using the instructions in [handover](docs/implementation/handover.md). There is no automatic destructive volume reset or remote publication step.
