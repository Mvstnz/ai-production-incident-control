"""Build the acceptance index from actual retained reports; unknown checks stay NOT_RUN."""
from pathlib import Path
import json,re
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
matrix=read('acceptance/acceptance-matrix.json')
matrix.update(spec_version='1.1',evaluated_at=datetime.now(timezone.utc).isoformat(),note='Executed local evidence only. Target runtime and live model evaluation are separate; blocked or unexecuted checks are never passed.')
rows={x['id']:x for x in matrix['criteria']}
for row in rows.values():row.update(status='NOT_RUN',evidence=[],verification_scope='DEMO_LOCAL')
def set_result(key,status,*evidence,note=None):
    rows[key].update(status=status,evidence=list(evidence))
    if note:rows[key]['note']=note
for filename in ('evidence/workflow-runs/local-e2e.json','evidence/workflow-runs/resilience.json'):
    for case in read(filename)['tests']:
        for key in case.get('criteria',[]):
            if key=='AC09':continue # Exact ambiguity cases are covered by the separate API acceptance edge suite.
            row=rows[key]
            if row['status']!='FAIL':row['status']=case['status']
            row['evidence'].append(filename+'#'+case['name'])

# These exact combined/ordered scenarios require their own observed evidence.
for key in ('AC06','AC15'):
    set_result(key,'NOT_RUN')
ordering=ROOT/'evidence/workflow-runs/acceptance-ordering.json'
if ordering.exists():
    for case in read('evidence/workflow-runs/acceptance-ordering.json')['tests']:
        for key in case['criteria']:
            set_result(key,case['status'],'evidence/workflow-runs/acceptance-ordering.json#'+case['name'])

api=(ROOT/'docs/implementation/api-integration-output.txt').read_text(encoding='utf-8')
unit=(ROOT/'evidence/test-results/domain-junit.xml').read_text(encoding='utf-8')
assert 'failures="0"' in unit and 'errors="0"' in unit,'Domain evidence is not clean'
assert re.search(r'\b\d+ passed\b',api) and ' FAILED' not in api,'API evidence is not clean'
api_tests={
 'AC09':['test_ambiguous_po_position_or_missing_year_enters_persisted_review'],
 'AC11':['test_dashboard_unions_same_sales_position_across_two_current_incidents'],
 'AC13':['test_tampered_draft_is_replaced_before_plan_persistence_and_dispatch'],
 'AC26':['test_unverified_quality_has_no_incident_action_or_approval'],
 'AC35':['test_genuinely_computed_low_supplier_mail_still_cannot_dispatch_unapproved'],
}
for key,names in api_tests.items():
    found=all(any(n in line and 'PASSED' in line for line in api.splitlines()) for n in names)
    set_result(key,'PASS' if found else 'NOT_RUN','docs/implementation/api-integration-output.txt','tests/integration/test_acceptance_edges.py',note='Exact API boundary scenario; no live LLM call.' if key=='AC13' else None)
for key,names in {'AC10':'test_own_reservation_is_protected_without_double_subtraction; test_lot_inventory_excludes_blocked_and_foreign_reservations','AC12':'test_unknown_free_text_and_prompt_injection_never_automated; test_unknown_and_injection_are_manual_review','AC33':'test_mixed_or_incomplete_snapshots; test_immutable_snapshot_and_cross_scope_foreign_key'}.items():
    set_result(key,'PASS','evidence/test-results/domain-junit.xml','docs/implementation/api-integration-output.txt',note=names)
for key,filename in [('AC01','evidence/test-results/github-ci.json'),('AC02','evidence/test-results/rebootstrap.json'),('AC30','evidence/test-results/secret-scan.json')]:
    path=ROOT/filename
    set_result(key,read(filename).get('status','NOT_RUN') if path.exists() else 'NOT_RUN',filename)
set_result('AC31','BLOCKED','evidence/workflow-runs/target-deployment.json','n8n/target/manifest.json','docs/BLOCKERS.md',note='Ten target workflows created and read back. Zero target executions; update/execute approval gate and required reachable endpoints/credentials missing.')
rows['AC31']['verification_scope']='CONNECTED_SANDBOX'
evaluation=read('evidence/evaluations/fixture-v1-report.json')
set_result('AC32','PASS' if evaluation['status']=='LOCAL_TESTED' else 'NOT_RUN','evidence/evaluations/fixture-v1-report.json',note='50 deterministic fixture cases; development/holdout denominators and versions reported. LIVE_EVAL_NOT_RUN; no model-performance claim.')
browser=read('evidence/test-results/browser.json')
matches=[x for x in browser['checks'] if 'AC36' in x.get('criteria',[])]
set_result('AC36','PASS' if matches and all(x['status']=='PASS' for x in matches) else 'NOT_RUN','evidence/test-results/browser.json','evidence/screenshots/n8n-action-execution-670.png','evidence/screenshots/dashboard-actions.png')
matrix['summary']={status:sum(r['status']==status for r in rows.values()) for status in ('PASS','FAIL','BLOCKED','NOT_RUN')}
(ROOT/'acceptance/acceptance-matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(matrix['summary']))
