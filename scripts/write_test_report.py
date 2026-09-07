"""Summarize retained execution evidence without manufacturing missing IDs."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def execution_ids(value):
    found=[]
    if isinstance(value,dict):
        if value.get('execution_id'):found.append(str(value['execution_id']))
        for item in value.values():found.extend(execution_ids(item))
    elif isinstance(value,list):
        for item in value:found.extend(execution_ids(item))
    return sorted(set(found),key=lambda v:(len(v),v))
api=(ROOT/'docs/implementation/api-integration-output.txt').read_text(encoding='utf-8')
result=re.findall(r'\d+ passed[^\n]*',api)[-1].strip('= ')
lines=['# Executed test report','','The matrix is an index of retained evidence. Fixture tests, local runtime and connected-cloud execution are separate. No unexecuted test is passed.','','| Boundary | Actual result | Command / evidence |','|---|---|---|',
'| Pure domain | 100 passed | `rtk proxy python -m pytest tests/unit -q`; domain-junit.xml |',
f'| Real PostgreSQL API integration | {result} | `rtk proxy python -m backend.run_integration`; api-integration-output.txt |',
'| Published local n8n E2E | 10/10 passed after final redeploy | `rtk proxy python -X utf8 scripts/test_runtime.py` |',
'| Actual runtime resilience | 10/10 passed, earlier failures retained | `rtk proxy python -X utf8 scripts/test_resilience.py --phase normal`; disruptive phases below |',
'| Repeat full bootstrap | Passed, identities and secrets preserved | `rtk proxy python scripts/test_rebootstrap.py` |',
'| Frontend build / typecheck | Passed | `rtk npm run build` |',
'| Real browser | Four views, exact approval, role/scope checks, responsive keyboard and same execution verified | evidence/test-results/browser.json |',
'| Fixture evaluation | 50 cases; 30 development / 20 holdout | evidence/evaluations/fixture-v1-report.json |',
'| Live LLM | NOT_RUN, zero calls/cost | Missing configured model/credential/call budget |',
'| Target cloud n8n | 10 created/read back, 0 executions | BLOCKED; target-deployment.json |']
ci=ROOT/'evidence/test-results/github-ci.json'
lines+=['',('Fresh GitHub CI: '+read('evidence/test-results/github-ci.json')['status']) if ci.exists() else 'Fresh GitHub CI: pending the first public run.','','## Recorded local execution IDs','', '| Scenario | Status | Recorded execution IDs |','|---|---|---|']
for path in ('evidence/workflow-runs/local-e2e.json','evidence/workflow-runs/resilience.json'):
    for case in read(path)['tests']:
        ids=execution_ids(case.get('evidence',{}))
        lines.append(f"| {case['name']} | {case['status']} | {', '.join(ids) or 'Not retained in this case; HTTP/persisted-result evidence only'} |")
lines+=['','Each execution is in the local n8n instance, not the cloud target. Action records and browser evidence separately prove action670 succeeded once and left the incident in monitoring.','','## Disruption commands','','Run only with other local users idle; these stop/start this project’s own containers and restore them in finally blocks.','','```sh','rtk proxy python -X utf8 scripts/test_resilience.py --phase restart --allow-interruption','rtk proxy python -X utf8 scripts/test_resilience.py --phase database --allow-interruption','```','','Normal resilience includes real 429 Retry-After, bounded503 retries, rejection/modification/expiry, stale approval, repeated SLA and isolated reset. Restart persists an actual signed Wait and commits approval/outbox while n8n is stopped. Database outage proves no false202 and safe replay after restoration. The complete raw sanitized results are in evidence/workflow-runs/.','','Two third-party deprecation warnings occurred in the API test client; the run passed. Load testing, live model accuracy and real external delivery are not covered.']
(ROOT/'docs/implementation/test-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Executed test report written.')
