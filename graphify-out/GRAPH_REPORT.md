# Graph Report - ai-production-incident-control  (2026-09-07)

## Corpus Check
- 195 files · ~158,436 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 903 nodes · 2189 edges · 49 communities (30 shown, 15 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 78 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Backend APIs and Security
- Dashboard Application
- Domain Evaluation Engine
- Core Database Schema
- Seeds and Integration Tests
- Runtime Test Client
- Contracts and Verification
- Specification and Acceptance
- Deployment and CI Config
- Frontend Dependencies
- Evaluation Builders
- Runtime Acceptance Helpers
- Incident Detail Evidence
- Dashboard TypeScript Config
- Workflow Deployment Tools
- Data Integrity Constraints
- Workflow Builder DSL
- Root JavaScript Tooling
- Action Execution Evidence
- Approval Modal Evidence
- Reliability Dashboard Evidence
- Guided Demo Evidence
- Mobile Reliability View
- Mobile Navigation Evidence
- Overview Dashboard Evidence
- Hero Workflow Evidence
- Local Workflow Manifest
- Integration Test Runner
- Scope Notification Schema
- n8n Action Evidence
- Acceptance Finalizer
- Public Release Preparation
- Evidence Report Writer
- Secret Initialization
- Root TypeScript Config
- Backend Package
- Incident Impact Link
- Bash Bootstrap
- CI RTK Installer
- PostgreSQL Initialization
- GitHub CI Recorder
- Repository Secret Scanner
- Workflow Inventory Writer
- Daily Management Digest
- Incident Actions Table

## God Nodes (most connected - your core abstractions)
1. `transaction()` - 78 edges
2. `post()` - 55 edges
3. `evaluate_impact()` - 41 edges
4. `uid()` - 31 edges
5. `fixture()` - 28 edges
6. `js()` - 24 edges
7. `evaluate_risk()` - 24 edges
8. `audit()` - 23 edges
9. `_json()` - 23 edges
10. `envelope()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Deterministic Grounded Summary` --semantically_similar_to--> `Exact Plan Approval`  [INFERRED] [semantically similar]
  prompts/summary.v1.md → docs/implementation/contracts.md
- `Live LLM Evaluation Not Run` --semantically_similar_to--> `Live Evaluation Not Run`  [INFERRED] [semantically similar]
  docs/implementation/test-report.md → evidence/evaluations/README.md
- `Evidence-Grounded Incident Extraction` --semantically_similar_to--> `Manual Review SOP v1`  [INFERRED] [semantically similar]
  prompts/extraction.v1.md → sops/manual-review.v1.md
- `test_auth_csrf_scope_and_mutated_roles()` --calls--> `uid()`  [EXTRACTED]
  tests/integration/test_api.py → backend/db.py
- `setup()` --indirect_call--> `erp_call()`  [INFERRED]
  tests/integration/test_api.py → backend/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Durable Incident Processing Pipeline** — codex_build_spec_intake_workflows, codex_build_spec_normalize_verify_dedupe, codex_build_spec_erp_impact_analysis, codex_build_spec_risk_ai_action_plan, codex_build_spec_human_approval_workflow, codex_build_spec_action_execution [EXTRACTED 1.00]
- **Recovery Error and Outbox Control Loop** — codex_build_spec_recovery_monitor, codex_build_spec_error_dead_letter_handler, codex_build_spec_transactional_outbox [EXTRACTED 1.00]
- **Controlled Incident Lifecycle** — ai_production_incident_control_docs_portfolio_controlled_incident_process, ai_production_incident_control_docs_archive_handoff_v1_0_codex_build_spec_product_promise, ai_production_incident_control_docs_portfolio_traceability [EXTRACTED 1.00]
- **Orchestration and State Architecture** — ai_production_incident_control_docs_adr_0001_n8n_as_orchestrator_orchestration_api_split, ai_production_incident_control_docs_adr_0001_orchestration_and_state_postgresql_state_boundary, ai_production_incident_control_docs_archive_handoff_v1_0_codex_build_spec_ten_workflows [INFERRED 0.95]
- **Approval and Delivery Safety** — ai_production_incident_control_docs_security_exact_approval_safety, ai_production_incident_control_docs_adr_0002_approval_and_delivery_versioned_approval_delivery, ai_production_incident_control_docs_adr_0003_versioned_approvals_and_outbox_transactional_work_queue, ai_production_incident_control_docs_limitations_delivery_guarantee_boundary [EXTRACTED 1.00]
- **Local Verification Stack** — evidence_test_results_domain_domain_unit_tests, docs_implementation_api_integration_output_api_integration_suite, docs_implementation_test_report_local_n8n_e2e [EXTRACTED 1.00]
- **Intake and Assessment Pipeline** — docs_implementation_workflow_inventory_wf01_email_intake, docs_implementation_workflow_inventory_wf03_normalize_verify_correlate, docs_implementation_workflow_inventory_wf04_erp_impact_analysis [EXTRACTED 1.00]
- **Approval Action and Recovery Pipeline** — docs_implementation_workflow_inventory_wf06_human_approval, docs_implementation_workflow_inventory_wf07_action_execution, docs_implementation_workflow_inventory_wf08_sla_dispatch_recovery [EXTRACTED 1.00]
- **Response Plan Actions** — evidence_screenshots_dashboard_actions_versioned_response_plan, evidence_screenshots_dashboard_actions_internal_ticket_action, evidence_screenshots_dashboard_actions_supplier_email_action [EXTRACTED 1.00]
- **Persisted Action Evidence** — evidence_screenshots_dashboard_actions_internal_ticket_outcome, evidence_screenshots_dashboard_actions_supplier_email_outcome, evidence_screenshots_dashboard_actions_action_execution_workflow [EXTRACTED 1.00]
- **Exact Approval Inputs** — evidence_screenshots_dashboard_approval_plan_version_1, evidence_screenshots_dashboard_approval_decision_rationale, evidence_screenshots_dashboard_approval_review_attestation [EXTRACTED 1.00]
- **Operational Impact Metrics** — evidence_screenshots_dashboard_incident_required_quantity_38, evidence_screenshots_dashboard_incident_covered_at_need_14, evidence_screenshots_dashboard_incident_shortage_at_need_24 [EXTRACTED 1.00]
- **Confirmed and Hypothetical Scenario Comparison** — evidence_screenshots_dashboard_incident_unconfirmed_split_scenario, evidence_screenshots_dashboard_incident_current_confirmed_plan, evidence_screenshots_dashboard_incident_hypothetical_split_outcome [EXTRACTED 1.00]
- **Verified Assessment Outputs** — evidence_screenshots_dashboard_incident_verified_assessment, evidence_screenshots_dashboard_incident_operational_impact, evidence_screenshots_dashboard_incident_risk_assessment_88_critical [EXTRACTED 1.00]

## Communities (49 total, 15 thin omitted)

### Community 0 - "Backend APIs and Security"
Cohesion: 0.05
Nodes (134): AwareDatetime, execute_action(), Local effects only. Uncertain writes never enter the automatic retry queue., main(), python -m backend.bootstrap: migrations and idempotent synthetic seed., main(), Remove work from historical API test scopes only; preserve append-only history., add_business_hours() (+126 more)

### Community 1 - "Dashboard Application"
Cohesion: 0.09
Nodes (66): Action, api(), ApiError, Approval, canDecide(), date(), Detail, Incident (+58 more)

### Community 2 - "Domain Evaluation Engine"
Cohesion: 0.10
Nodes (75): aggregate_values(), _allocate(), _bool(), build_plan(), DomainValidationError, _empty(), evaluate_impact(), evaluate_risk() (+67 more)

### Community 3 - "Core Database Schema"
Cohesion: 0.07
Nodes (60): append_only_audit, erp.capacity_calendar, erp.check_schedule(), erp.command_receipts, erp.customers, erp.fixture_data, erp.inventory_lots, erp.inventory_reservations (+52 more)

### Community 4 - "Seeds and Integration Tests"
Cohesion: 0.08
Nodes (55): fixture(), insert(), Idempotent synthetic ERP seeds shared by bootstrap and isolated demo scopes., sales(), seed_quality(), seed_scope(), fixture, assert_no_actions_or_approvals() (+47 more)

### Community 5 - "Runtime Test Client"
Cohesion: 0.09
Nodes (46): Client, hook(), HTTP test client for the loopback demo; credentials never enter evidence., main(), Populate the shared read-only viewer scope through real local n8n intake., actions(), approve(), delivered_once() (+38 more)

### Community 6 - "Contracts and Verification"
Cohesion: 0.06
Nodes (57): API Integration Suite, apic_integration PostgreSQL Database, Backend and PostgreSQL Verification, Quality Release Approval Flow, Retry-After Job Context Persistence, Signed Wait URL Validation, Unknown Outcome Reconciliation, Browser API Contract (+49 more)

### Community 7 - "Specification and Acceptance"
Cohesion: 0.06
Nodes (45): ADR 0001: n8n as Orchestrator, Visible Orchestration and Atomic API Split, ADR 0001: Orchestration and State, PostgreSQL Domain State Boundary, ADR 0002: Approval and Delivery, Versioned Approval and Honest Delivery, ADR 0002: Offline-Safe Demo First, Offline-Safe Demonstration (+37 more)

### Community 8 - "Deployment and CI Config"
Cohesion: 0.07
Nodes (44): APIC Project Work Rules, Pinned Python Runtime Dependencies, WF07 Action Execution, Synthetic AI Evaluation, Versioned API Contracts, Versioned Human Approval Protocol, Authoritative Build Plan v1.1, Canonical Intake Envelope (+36 more)

### Community 9 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (21): dependencies, lucide-react, react, react-dom, devDependencies, @types/react, @types/react-dom, vite (+13 more)

### Community 10 - "Evaluation Builders"
Cohesion: 0.15
Nodes (18): evaluate(), main(), Any, datetime, Verify handoff arithmetic and document structure, NOT the future application.…, require(), when(), build_case() (+10 more)

### Community 11 - "Runtime Acceptance Helpers"
Cohesion: 0.27
Nodes (18): approve(), baseline(), case(), delivery(), detail(), dispatch(), duplicate(), machine() (+10 more)

### Community 12 - "Incident Detail Evidence"
Cohesion: 0.13
Nodes (19): Before and After Incident Schedule, Consistent ERP Snapshot, Covered at Need 14, Current Confirmed Plan, APIC Incident Assessment View, Deterministic Response Summary, Hypothetical Split Outcome 14 Shortage Risk 69 High, Incident Monitoring Status (+11 more)

### Community 13 - "Dashboard TypeScript Config"
Cohesion: 0.12
Nodes (16): compilerOptions, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib, module, moduleResolution (+8 more)

### Community 14 - "Workflow Deployment Tools"
Cohesion: 0.25
Nodes (12): compose(), deploy(), main(), Local-only reproducible bootstrap; never targets the connected cloud instance., run(), wait(), wait_published_webhook(), Redeploy only named owned local workflows, with a prior supported-CLI export. (+4 more)

### Community 15 - "Data Integrity Constraints"
Cohesion: 0.13
Nodes (13): erp.check_reservations(), erp.quality_dispositions, immutable_action_content, immutable_disposition, immutable_plan_content, reservation_total, ops.reject_mutation, erp.check_reservations (+5 more)

### Community 16 - "Workflow Builder DSL"
Cohesion: 0.22
Nodes (4): Flow, main(), provenance(), Build auditable n8n graphs. Runtime import/readback tests are separate.

### Community 17 - "Root JavaScript Tooling"
Cohesion: 0.13
Nodes (14): devDependencies, prettier, typescript, name, private, scripts, build, dev (+6 more)

### Community 18 - "Action Execution Evidence"
Cohesion: 0.20
Nodes (12): APIC WF07 Action Execution, Critical Risk Assessment 88, APIC Dashboard Actions View, Internal Ticket Action, Succeeded Internal Ticket Outcome, Incident Monitoring Status, Production Manager Approval Requirement, Supplier Delay Incident 213a1ccf (+4 more)

### Community 19 - "Approval Modal Evidence"
Cohesion: 0.24
Nodes (11): Critical Supplier Delay Assessment, APIC Dashboard Approval View, Required Decision Rationale, Approve Exact Response v1 Modal, Approve This Exact Version Control, Incident 213a1ccf Revision 1, Response Plan Version 1, Production Manager Session (+3 more)

### Community 20 - "Reliability Dashboard Evidence"
Cohesion: 0.60
Nodes (5): APIC Reliability Dashboard Screenshot, Succeeded Sandbox Action Receipts, Succeeded Analysis Job with n8n Reference, Reliability Dashboard, Transactional Outbox Status

### Community 21 - "Guided Demo Evidence"
Cohesion: 0.60
Nodes (5): APIC Viewer Guided Demo Screenshot, Start a Guided Demo Modal, Read-Only Viewer Access, Synthetic Data and Local-Effects Boundary, Supplier, Machine, and Quality Demo Scenarios

### Community 22 - "Mobile Reliability View"
Cohesion: 0.40
Nodes (5): APIC Mobile Reliability View, No Analysis Jobs, Database Ready Simulated AI External Actions Disabled, Mobile Reliability Dashboard, Waiting Workflows Evidence

### Community 23 - "Mobile Navigation Evidence"
Cohesion: 0.40
Nodes (5): APIC Mobile Menu View, Demo Local Isolated Synthetic Operations, Selected Reliability Section, Viewer Role Session, Mobile Workspace Navigation Drawer

### Community 24 - "Overview Dashboard Evidence"
Cohesion: 0.60
Nodes (5): APIC Operations Overview, Persisted Incident Register, One Open Critical Incident EUR 126400, Critical Supplier Delay Monitoring Incident, Facts First People in Control

### Community 25 - "Hero Workflow Evidence"
Cohesion: 0.70
Nodes (5): Normalize Verify and Correlate Processing Graph, Published Workflow State, n8n Hero Execution Screenshot, Successful n8n Execution 11, APIC WF03 Normalize Verify and Correlate

### Community 26 - "Local Workflow Manifest"
Cohesion: 0.40
Nodes (4): n8n_version, profile, readback_at, workflows

### Community 27 - "Integration Test Runner"
Cohesion: 0.67
Nodes (3): main(), Host runner: real PostgreSQL, separate apic_integration DB, no n8n test jobs.…, run()

### Community 28 - "Scope Notification Schema"
Cohesion: 0.50
Nodes (3): ops.sandbox_notifications, ops.outbox_events, ops.scopes

### Community 29 - "n8n Action Evidence"
Cohesion: 0.83
Nodes (4): APIC Action Execution Workflow, Linear Action Execution Graph, n8n Action Execution Screenshot, Successful n8n Execution 670

## Ambiguous Edges - Review These
- `n8n Action Execution Screenshot` → `APIC Action Execution Workflow`  [AMBIGUOUS]
  evidence/screenshots/n8n-action-execution-670.png · relation: references

## Knowledge Gaps
- **108 isolated node(s):** `name`, `version`, `private`, `type`, `dev` (+103 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 208 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `n8n Action Execution Screenshot` and `APIC Action Execution Workflow`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `transaction()` connect `Backend APIs and Security` to `Seeds and Integration Tests`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `evaluate_impact()` connect `Domain Evaluation Engine` to `Backend APIs and Security`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `evaluate_risk()` connect `Domain Evaluation Engine` to `Backend APIs and Security`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `evaluate_impact()` (e.g. with `_machine()` and `_quality()`) actually correct?**
  _`evaluate_impact()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _108 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Backend APIs and Security` be split into smaller, more focused modules?**
  _Cohesion score 0.05271610769957487 - nodes in this community are weakly interconnected._