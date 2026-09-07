# Current implementation contracts

CODEX_BUILD_SPEC.md is authoritative. Python Domain, 88/69 supplier, 52 machine, UNKNOWN_OUTCOME, four attempts, scope isolation, Quality approval. Scope/API contracts fixed before independent work.

## Files and runtime

`backend/domain.py` pure functions; `backend/main.py` ops; `backend/erp.py` ERP; `backend/db.py` persistence; `dashboard/` React/Vite. Compose project apic-portfolio. Services postgres, ops-api:8000, mock-erp:8001, n8n:5678, runners if required, dashboard:5173, mailpit:8025/SMTP1025. Loopback public ports. DB apic_demo + apic_n8n, separate roles. No external writes.

## Domain

Pure JSON dictionary signatures: `evaluate_impact(snapshot,facts)`, `evaluate_risk(impact)`, `extract_fixture(envelope,snapshot)`, `build_plan(impact,risk,incident_id,revision)`, `aggregate_values(impacts)`. Decimal inside; offset datetime validation; no IO except local configuration load. Domain owns fixtures for machine/quality and immediately communicates their schema.

Snapshot `{schema_version:'1.0',snapshot_id,scope_id,erp_revision:1,incident_type,analysis_time,data}`; supplier data = hero_supplier_delay.json excluding expected outputs/scenarios. Facts `{incident_type:'SUPPLIER_DELAY',purchase_order,purchase_order_item,material,confirmed_supply_schedule,proposed_partial?,reason}`. Other types MACHINE_BREAKDOWN / QUALITY_ISSUE. Structured source envelope.payload contains typed facts; EMAIL exact known fixture content only in fixture mode. Unknown/injection review. All quantities/times/evidence checked, not scenario name alone.

Impact `{schema_version,method_version,snapshot_id,scope_id,erp_revision,incident_type,analysis_time,data_complete,review_reasons,reviewed_production_orders,affected_production_orders,affected_sales_lines,total_required,total_available,total_shortage,allocations_at_need,shortages_at_need,baseline,projected,affected_open_order_value_cents,currency,sales_line_values,disruption_days,hours_to_first_relevant_demand,uncovered_resource_ratio,qualified_alternative_available,strategic_customer_affected,has_operational_impact,hard_override,source_refs,proposals,what_if}`. `sales_line_values` maps IDs to cents; baseline/projected per-demand full-cover/completion; what_if separate. Quality extras blockable_quantity/shipped_quantity/trace. Unknown null, no output expected values consumed.

Risk `{policy_version,data_complete,risk_score,severity,factors:{key:points},factor_details:{key:{value,points,source}},missing_factors,override_reason,explanation}`.

Extraction `{status:'VERIFIED'|'MANUAL_REVIEW',incident_type,business_key,facts,evidence,review_reasons,provider:'fixture',model:'fixture-v1',prompt_version}`.

Plan `{policy_version:'1.0',summary,summary_mode:'deterministic-template',sop_ids,actions:[{action_type,required_role,payload}]}`. INTERNAL_TICKET auto, SUPPLIER_EMAIL purchasing/production_manager, RESCHEDULE production_manager, QUALITY_BLOCK/QUALITY_RELEASE quality_manager. Email allowed `supplier@example.test`; internal `operations@example.test`. No automatic quality block. Critical plan manager review. Exact hash/version immutable post approval.

## n8n/internal endpoints

X-Service-Token distinct from user/ERP credentials. Stage context `schema_version,scope_id,correlation_id,source_event_id,job_id,claim_token,execution_id,workflow_id`, then incident_id/revision/snapshot_id. Enforce claims at writes, actual n8n IDs persisted.

* POST /internal/source-events: canonical envelope per spec -> 202 `{source_event_id,job_id,scope_id,correlation_id,status_url,duplicate}` durable event+job.
* POST /internal/jobs/claim `{job_id?,owner,limit}` -> `{items:[stage]}`.
* POST /internal/jobs/context stage -> stage + `{envelope,snapshot}`.
* POST /internal/extract `{envelope,snapshot}` -> extraction.
* POST /internal/incidents/correlate `{...stage,extraction}` -> stage + `{incident_id,revision,snapshot_id,status,skip_analysis}`; same facts link sources, changed facts revise/supersede.
* POST /internal/impact/evaluate `{snapshot,facts}` -> pure impact.
* POST /internal/impact/save `{...stage,impact}` -> stage + `{impact,impact_assessment_id}`.
* POST /internal/risk/evaluate `{impact}` -> risk.
* POST /internal/plans/draft `{impact,risk,incident_id,revision}` -> plan.
* POST /internal/plans `{...stage,impact_assessment_id,risk,plan}` -> stage + `{plan_id,plan_version,plan_hash,approval_ids,action_ids}`; atomic outbox.
* POST /internal/jobs/complete `{...stage,result}` idempotent same claim; /fail adds `{error_class,message,retry_after?}` classes TRANSIENT/PERMANENT/UNKNOWN_OUTCOME, max four total attempts.
* POST /internal/approvals/context `{scope_id,plan_id,execution_id,workflow_id}` -> `{status,approval_ids,action_ids,scope_id,plan_id}`.
* POST /internal/approvals/register-wait same + `{resume_url}` exact allowed origin and execution-bound path; exactly one n8n `signature` query is strictly validated and internally retained. Resume URLs never enter public evidence. Early decision is preserved.
* POST /internal/approvals/revalidate same -> `{ready_action_ids,status}`.
* POST /internal/actions/claim `{scope_id,action_id,execution_id,workflow_id}` -> `{action_id,claim_token,action_type,payload,can_execute,status}` exact current approval check.
* POST /internal/actions/execute `{scope_id,action_id,claim_token,execution_id,workflow_id}` -> persisted sandbox adapter outcome. Local Mailpit/tickets/privileged mock ERP only; provider accepts then timeout = UNKNOWN_OUTCOME, no blind retry.
* POST /internal/recovery `{execution_id,workflow_id}` -> `{jobs:[stage],plans:[{scope_id,plan_id}],actions:[{scope_id,action_id}],wakeups:[],counts}` bounded due jobs/outbox/SLA/leases. Wakeup URLs internal only.
* POST /internal/errors `{execution_id,workflow_id,job_id?,scope_id?,message,error_class}` safe metadata.
* POST /internal/digest `{scope_id?,execution_id,workflow_id}` unique scope/date/channel; dedup values.

ERP X-ERP-Token: POST /erp/v1/snapshots `{scope_id,incident_type,revision}` -> snapshot; GET /erp/v1/snapshots/{id}, detailed reads require snapshot_id. Separate privileged token for commands reschedule/quality-block/quality-release, exact DB-authorized action receipt, no boolean approval bypass.

WF01/02 authenticated Webhook persist then Respond 202 and asynchronously WF03. WF03 claims/extract/correlate -> WF04 snapshot/impact -> WF05 risk/draft/plan -> complete. WF06 async request/Wait/revalidate -> WF07, never blocks calculation parent. WF08 every 60s + protected test Webhook dispatch/recover. WF09 Error Trigger + subworkflow harness. WF10 daily08:00 Bangkok + subworkflow. All APIC | names; no foreign flow writes.

## Browser API

Cookie session with server record/Argon2, Origin + X-CSRF-Token for POST (login Origin only). Public proxy /api only. Scope membership checked for every request. Standard users viewer/operator/purchasing/production_manager/quality_manager/admin with generated passwords saved only ignored .local/credentials.json.

* POST /api/auth/login `{username,password}` -> `{user:{id,username,role},csrf_token,scopes:[{id,name}]}`; GET /api/auth/me; POST /api/auth/logout.
* GET /api/scopes -> `{items:[{id,name,clock,synthetic:true}]}`. Reads use scope_id query, writes body (unless scope path).
* POST /api/demo/runs `{scenario:'supplier-delay'|'supplier-split'|'machine-breakdown'|'quality-issue'|'quality-shipped'|'unknown-input',scope_id?}` creates scope if absent, then through true WF01/02 intake. Split same scope. Return `{scope_id,source_event_id,job_id,status_url}`. POST /api/intake canonical envelope forward protected WF02; fail503 if no commit.
* POST /api/demo/runs/{scope_id}/advance `{seconds}` admin nonnegative clock; /reset own synthetic scope only.
* GET /api/source-events/{id}?scope_id status/review/incident.
* GET /api/incidents?scope_id=&type=&severity=&status=&offset=&limit= -> `{items:[{id,number,title,incident_type,status,revision,risk_score,severity,affected_open_order_value_cents,updated_at}],total}`.
* GET /api/incidents/{id}?scope_id -> same + `{sources,revisions,impact,risk,plans,actions,approvals,timeline}`.
* GET /api/approvals?scope_id -> `{items:[{id,incident_id,revision,plan_id,plan_version,plan_hash,status,required_role,expires_at,actions:[{action_type,payload}]}]}`.
* POST /api/approvals/{id}/decision `{scope_id,decision:'APPROVE'|'REJECT'|'MODIFY',expected_version,plan_hash,comment,payload?}`. Stale/expired409, roles403. Modify new plan+approval. Approve outbox wakes WF06, consumes once. No GET writes.
* POST /api/incidents/{id}/corrections `{scope_id,expected_revision,facts,reason}`; /resolve `{scope_id,expected_revision,evidence,reason}` proper manager and evidence; /close only after RESOLVED.
* GET /api/dashboard?scope_id -> `{open_incidents,critical_incidents,affected_open_order_value_cents,pending_approvals,sla_breaches,currency,clock,timezone,ai_mode:'simulated AI',profile:'DEMO_LOCAL',aggregation:'union of unique open sales positions'}`.
* GET /api/actions?scope_id, /api/errors?scope_id -> `{items}`; GET /api/system?scope_id safe health/config and jobs.
* POST /api/errors/{id}/retry `{scope_id,reason}` admin preserves IDs.
* POST /api/demo/failures `{scope_id,kind:'read-503'|'read-429'|'write-timeout'|'permanent',enabled}` admin, scope-specific.

Health live/ready separate. OpenAPI schemas generated. Tests mark LOCAL_TESTED separate from TARGET_TESTED. Concrete integration contract adjustments coordinated with parent, never silently divergent.
