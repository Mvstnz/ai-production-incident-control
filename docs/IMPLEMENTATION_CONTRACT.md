# SUPERSEDED — do not implement this contract

The later supplied CODEX_BUILD_SPEC.md overrides this provisional contract. Use `implementation/contracts.md` instead. This file is retained only as history.

This contract fixes interfaces before independent implementation. It implements the supplied BUILD_PLAN v1.0. The separately requested CODEX_BUILD_SPEC.md, M6/M7 and T33–T36 are absent from the supplied archive and remain an unresolved input blocker. No requirements are invented for them.

## Runtime

Local-only Docker project `aipc-demo`: PostgreSQL business database `aipc_demo`, n8n database `aipc_n8n`; API internal http://api:8000; browser API proxy `/v1` only; dashboard http://127.0.0.1:5173; API http://127.0.0.1:8000; n8n http://127.0.0.1:5678; Mailpit http://127.0.0.1:8025, SMTP internal mailpit:1025. No paid services or real messages. Independent implementation proceeds while the absent connector is blocked, per the user's explicit instruction. Runtime claims require executions.

## Domain module

`packages/domain-core/src/index.ts` exports `analyzeImpact(snapshot)`, `assessRisk(impact)`, `buildPlan({impact,risk,incident_id,incident_revision})`, `extractMock(event)`, and `aggregateExposure(impacts)`; all pure JSON functions. Export all input/output TypeScript types. Bundle as IIFE global `AIPC` in `n8n/build/domain.bundle.js` via esbuild. SHA256 recorded separately and in analysis metadata.

Snapshot common fields: `schema_version: '1.0'`, `id`, `type: SUPPLIER_DELAY | MACHINE_FAILURE | QUALITY_DEFECT`, `incident_revision`, `analysis_as_of` (offset timestamp). For supplier, remaining fields match `fixtures/supplier-delay-golden.json`, plus `supply` (current incident confirmed/proposed array). Do not consume `expected_initial`/`expected_revised`. API preserves snapshot as immutable JSON. Machine and quality scenario fixtures must define explicit typed inputs, documented by domain owner before API integration.

Impact common fields: `schema_version`, `erp_snapshot_id`, `incident_revision`, `analysis_as_of`, `type`, `status: COMPLETE | REVIEW_REQUIRED`, `reasons: string[]`, `shortage_quantity`, `relevant_demand_quantity`, `timely_covered_quantity`, `referenced_production_orders`, `under_supplied_production_orders`, `projections` (baseline and incident arrays), `at_risk_items` (sales_order_item, at_risk_quantity, open_quantity, unit_price_minor, currency, customer_id, strategic), `at_risk_order_value_minor`, `currency: EUR`, `additional_delay_days`, `first_disruption_at`, `confirmed_timely_alternative` (boolean or null), `disruption_quantity`, `disruption_denominator`, `disruption_unit`, `sources`, optional `quality_shipment_exposure`, `proposals`, `shipped_exposure_quantity`, `blockable_quantity`.

Risk fields: `schema_version`, `risk_policy_version: portfolio-v1`, `status`, `score` (number or null), `severity` (LOW/MEDIUM/HIGH/CRITICAL or REVIEW_REQUIRED), `factors` (objects: key, points, value, explanation), `override_reason`, `explanation`.

Plan is `{schema_version:'1.0', explanation, actions:[{type, required_role, payload}]}`. Action types `SANDBOX_TICKET`, `INTERNAL_WARNING`, `SUPPLIER_EMAIL`, `RESCHEDULE_PROPOSAL`, `QUALITY_BLOCK`, `QUALITY_RELEASE`. Allowed synthetic destinations resolved server-side. Payload email includes `recipient`, `subject`, `body`; permitted supplier `planning@asia-precision.example`, internal `operations@demo-plant.example`. Actual mail goes only to Mailpit. Workflow uses adapter route to deliver, never general arbitrary SMTP or URL from user input.

Extraction: `{status:'VALIDATED'|'REQUIRES_REVIEW', type, correlation_key, facts, evidence, uncertainties, provider:'mock', model:'fixture-v1'}`. Only exact known fixture text OR validated structured `event.facts` accepted; unknown free text and injection get review. Known demo `scenario_key`: supplier-delay, supplier-partial, machine-failure, quality-defect, quality-shipped. Event shape `{schema_version:'1.0', source_system, source_id, received_at, correlation_id, sender, subject, body_text, scenario_key?, facts?}`. Scenario key alone must never make arbitrary free text valid.

## HTTP and workflow stages

All internal routes require `X-Service-Token`; return JSON. n8n carries `{work_item_id, claim_token, kind, aggregate_id, revision, correlation_id, execution_id, workflow_id}`. Stage body always includes these. Persist workflow/execution IDs from n8n expressions. Internal routes verify live claim and expected revision and atomically persist stage result. Idempotent stage reruns return stored result; work completion accepts repeated same token after DONE but rejects old tokens after re-claim.

`POST /internal/work-items/claim` body `{owner,limit:1..20}` → `{items:[{id,claim_token,kind,aggregate_id,revision,payload,correlation_id}]}`.
`POST /internal/work-items/{id}/complete` body `{claim_token,result?,execution_id,workflow_id}` → `{status:'DONE'}`.
`POST /internal/work-items/{id}/fail` body `{claim_token,error_class,message,execution_id,workflow_id,retry_after?}`. Classes TRANSIENT, PERMANENT, DELIVERY_UNKNOWN. Max 5 attempts with lease-safe recovery.

`POST /internal/intake/normalize` body stage IDs → `{event,work_item_id,claim_token,...}`; WF01/02 normalize already accepted event and enqueue exactly one analysis work item atomically (or use `/internal/intake/complete` with normalized event). No recursive re-intake.
`POST /internal/analysis/context` body stage IDs → `{event,...stage IDs}`.
`POST /internal/analysis/correlate` body `{...stage IDs,extraction}` → `{incident_id,incident_revision,snapshot_id,status,...stage IDs}`. REVIEW ends safely. Supplier facts changes revise same open incident. Supersede old approvals/actions.
`GET /v1/erp/snapshots/{id}` service or user auth → Snapshot.
`POST /internal/analysis/impact` body `{...stage IDs,incident_id,incident_revision,impact,bundle_hash}` persists validated impact → same references + impact.
`POST /internal/analysis/plan` body `{...stage IDs,incident_id,incident_revision,risk,plan,bundle_hash}` stores risk/plan/actions/approvals, enqueue approval.requested and auto action.ready → `{incident_id,incident_revision,risk,plan}`.
`POST /internal/approvals/dispatch` stage body handles approval.requested / approval.decided separately and enqueues approved action only after revision/hash recheck.
`POST /internal/actions/prepare` stage body → `{action_id,type,payload,state,can_execute}`; atomically checks role, approval, payload hash, plan + incident version before RUNNING. An expired RUNNING delivery cannot be retried blindly.
`POST /internal/actions/execute` body `{...stage IDs,action_id}` → persisted sandbox adapter result; timeout-after-accept injection yields DELIVERY_UNKNOWN, no retry. Adapter only Mailpit or persisted local ticket/ERP mock, never external. Network request is a workflow-visible node; API provides side-effect atomic guard and controlled transport.
`POST /internal/maintenance` `{execution_id,workflow_id}` → lease recovery/SLA/digest scheduling counts; bounded due work; demo time separate from technical lease time.
`POST /internal/errors` error-trigger payload `{execution_id,workflow_id,message,work_item_id?,claim_token?}` → error record (no raw email/credentials).
`POST /internal/digest` stage body → unique report for date + Asia/Bangkok, dedup metrics, sandbox notification reference.

WF03 invokes WF04 then WF05 synchronously. Their inputs carry work item + live claim and references. Only dispatcher completes the original work item. WF06 returns after request, never waits for human in parent execution. WF09 uses real Error Trigger and test input branch. WF08 dispatch mapping is the table in BUILD_PLAN §11.1; bounded batches and schedule trigger.

## Browser API

Session cookies via Starlette SessionMiddleware with server-side session record; POST origin + CSRF required except login (origin still required). `/v1/auth/login` `{username,password}` → `{user:{id,username,role},csrf_token}`. `/v1/auth/me` same; `/v1/auth/logout` POST. Roles viewer, operator, production_manager, quality_manager, admin; admin does not implicitly bypass quality decision. Generated local passwords in ignored `.local/credentials.json`, not committed.

`GET /v1/incidents?type=&status=&severity=` → `{items:[{id,type,lifecycle,analysis_status,revision,severity,risk_score,at_risk_order_value_minor,created_at,updated_at}]}`.
`GET /v1/incidents/{id}` → incident fields plus `source_events`, `revisions`, `impact`, `risk`, `plans`, `actions`, `approvals`, `audit` (execution IDs + times).
`GET /v1/approvals` → `{items:[{id,incident_id,incident_revision,plan_revision,status,required_role,expires_at,action_payload_hash,payload,action_type}]}`.
`POST /v1/approvals/{id}/decision` `{decision:APPROVE|REJECT|MODIFY,incident_revision,plan_revision,action_payload_hash,reason,payload?}`; MODIFY creates new approval, rejects unauthorized recipients, returns 409 for stale/expired. GET never changes state.
`POST /v1/incidents/{id}/review` `{expected_revision,facts,reason}` authorized correction preserving originals.
`POST /v1/incidents/{id}/resolve` `{expected_revision,evidence}` manager (quality manager for quality) only; require evidence and no unresolved mandatory actions or DELIVERY_UNKNOWN. Lifecycle closing/reopening explicit audited endpoint.
`GET /v1/metrics` → `{open_incidents,critical_incidents,pending_approvals,at_risk_order_value_minor,currency,analysis_as_of,aggregation:'maximum at-risk quantity per open sales position',ai_mode:'mock',timezone}`.
`GET /v1/system` → `{work_items,errors,ai_mode,demo_time,blockers}`.
`POST /v1/admin/work-items/{id}/replay` `{reason}` preserves action/business IDs.
`POST /v1/demo/scenarios/{key}/run` (operator/admin) → 202 `{event_id,status_url}`. Duplicate key repeats source; revision key submits new source. Scenario keys above plus duplicate, unknown-input. Only admin can inject technical faults via `POST /v1/demo/failures` `{kind:api-transient|delivery-unknown|permanent,enabled:boolean}`.
`POST /v1/demo/clock/advance` `{seconds}` (admin only, nonnegative). No arbitrary clock rewind.
`POST /v1/intake/events` authenticated operator/session or intake token, same event shape; Idempotency-Key required; source key + changed body 409. GET `/v1/events/{id}` reports status.

Every status in acceptance report requires concrete evidence. Connector target IDs must be listed separately from local-only IDs. Local execution never proves deployment to the user's absent connector instance.
