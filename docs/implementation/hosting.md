# Hosted release — 2026-09-08

[Open the application](https://ai-production-incident-control-dash.vercel.app) and select **Explore the workspace**. The earlier dashboard layout has been restored at the user's request, retaining ordinary manufacturing examples and readable supplier emails. See the [restoration and verification](dashboard-restoration.md). The guided redesign below is historical verification, not the current layout.

The ordinary manufacturing examples are delayed steel rods, a stopped band saw and mounting plates with oversized holes. The current project, local database and hosted database no longer use the previous reference-product or invented-brand fixtures. Earlier fixture archives and screenshots were removed. The UI uses ordinary names and formatted dates; identifiers and exact technical references remain available in expandable details.

## Deployed services

| Service | Deployment |
| --- | --- |
| Vercel | ai-production-incident-control-dashboard in pattaya-pimps; production alias linked above |
| Supabase | apic-portfolio; project kgymsfryvfhfwackheet, Frankfurt; private ops and erp schemas |
| n8n cloud | mvstnz1.app.n8n.cloud; all ten APIC workflows published and credentialed |
| Last verified production deployment | dpl_H9ctmCkWmhSsp6atNLmtyMV9gVYM; production alias confirmed after Git push |

Application revision: `8520a591373f043d23a7a7a1edd68118b1c1d5f4` on `main`. The [GitHub acceptance run for this revision](https://github.com/Mvstnz/ai-production-incident-control/actions/runs/34223684112) passed. The previous full acceptance baseline recorded 36 PASS within its defined scope. This dashboard update reran the production build, 112 unit tests and all 34 API integration tests, followed by local responsive and hosted browser checks. Later documentation/evidence commits do not change the tested application.

The [workflow inventory](workflow-inventory.md) lists every actual workflow ID, and the [manifest](../../n8n/target/manifest.json) records the published graph readback.

Supabase's Data API is disabled. Application, ERP and deployment roles have separate grants. Runtime pooler connections use TLS and disabled prepared statements. Migration credentials remain local; Vercel holds only runtime connections and service/session tokens. The n8n credential store holds its purpose-specific header and form credentials.

## Observed verification

- 112 unit tests passed against the current fixtures.
- 34 PostgreSQL API integration tests passed, including exact approvals, immutable facts, role checks, scope isolation and bounded retries.
- Ten local n8n runtime scenarios passed; the supplier baseline was retested after correcting the harness to distinguish 24 initial rods from 36 rods covered across all required dates.
- Ten resilience scenarios and two concurrent-delivery / early-approval cases passed. These include an actual n8n restart and a database interruption.
- Repeated local bootstrap preserved scopes, jobs, actions, credentials and workflow IDs.
- Three hosted HTTPS assessments passed: supplier 83 / CRITICAL, saw 62 / HIGH and quality 70 / CRITICAL.
- Six approved hosted actions succeeded once; repeated recovery preserved attempts and provider references. The supplier message was captured, the saw job rescheduled, and the plate shipment blocked in the synthetic ERP.
- Public visitor access is read-only, confined to the shared workspace; private workspace reads and visitor mutations returned 403.
- Browser checks cover readable overview, approvals, dates, machine names, expandable references and processing history. Screenshots were inspected in the task.
- The 50-case deterministic fixture evaluation ran with zero live-model calls.
- A separate actual hosted Gemini mail run passed. Cloud workflow WF03 `6tHziLEHudpdk5hk`, execution `120`, ran the Gemini node successfully and verified the extracted facts. The resulting incident correctly records 40 missing rods, two affected orders, €55,400 and 83 / CRITICAL. The proposed partial delivery remains unconfirmed. This consumed one of the configured 20 total provider reservations. See [persisted result](../../evidence/workflow-runs/hosted-gemini.json) and [sanitized node execution](../../evidence/workflow-runs/hosted-gemini-n8n.json).

Exact results and execution IDs: [hosted analyses](../../evidence/workflow-runs/hosted-demo.json), [hosted actions](../../evidence/workflow-runs/hosted-actions.json), [local runtime](../../evidence/workflow-runs/local-e2e.json), [resilience](../../evidence/workflow-runs/resilience.json), [ordering](../../evidence/workflow-runs/acceptance-ordering.json), [API output](api-integration-output.txt), [unit JUnit](../../evidence/test-results/domain-junit.xml), [fresh GitHub CI](../../evidence/test-results/github-ci.json).

## Access and operations

The public entry creates a viewer session for the shared workspace. Authorized operational accounts are listed in the ignored local file .local/hosted-credentials.json. Their passwords are not published in the repository.

Supplier emails are stored in PostgreSQL and never delivered externally. The three shared example cases use stored fixture assessments; browsing them does not invoke a model. Authorized team members can submit a new synthetic supplier mail through **Start an example → Analyze with Gemini** for actual extraction. The configured model is `models/gemini-3.1-flash-lite`, the total call budget is 20, and the provider credential remains in n8n. Public visitors cannot submit new mail or approve actions. Database writes affect only the synthetic ERP.

Immediate recovery wakeups follow completed analyses and approval decisions. An hourly fallback avoids exhausting the n8n trial's execution allowance. Digests run daily in Europe/Berlin. The account showed eight trial days remaining on 2026-09-08; continued orchestration depends on the account remaining available. No paid plan was purchased.

## Reproduce and recover

Run locally with `python scripts/bootstrap.py` (Docker and Python required). Generated local credentials are in ignored .local/credentials.json.

Checks: `python -m pytest tests/unit -q`, `python -m backend.run_integration`, `python -X utf8 scripts/test_runtime.py`, `python scripts/test_showcase.py` and `python scripts/test_rebootstrap.py`. Hosted checks are scripts/verify_hosted.py and scripts/verify_hosted_actions.py and require the ignored hosting configuration.

Keep this release's Git commit and the current ten sanitized workflow exports as the recovery baseline. A later frontend/API regression can be recovered by redeploying this release to the existing Vercel project or promoting its verified deployment. Restore workflow graphs from this release's n8n/target files, retaining the saved credential references. Database migration rollback and backup restoration were not exercised; do not claim them as tested.

Implemented, locally tested and target-tested boundaries are recorded separately in the [acceptance matrix](../../acceptance/acceptance-matrix.json). One live-provider smoke test has passed; statistical live-model accuracy, real supplier delivery, load testing and disaster recovery remain NOT_RUN.
