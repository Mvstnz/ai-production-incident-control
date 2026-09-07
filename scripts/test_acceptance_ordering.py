"""Observe AC06/AC15 ordering through real local n8n and sandbox SMTP.

No workflow mutation, container interruption, direct SQL or remote provider.
Only newly created synthetic scopes are reset; shared showcase data is retained.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import time
from urllib.request import urlopen
from uuid import uuid4

from runtime_client import Client, ROOT, hook

c = Client('admin')
actors = {role: Client(role) for role in ('purchasing', 'production_manager')}
OUTPUT = ROOT / 'evidence/workflow-runs/acceptance-ordering.json'
report = {'profile': 'DEMO_LOCAL', 'started_at': datetime.now(timezone.utc).isoformat(), 'tests': []}


def system(sid):
    return c.ok('/api/system?scope_id=' + sid)


def actions(sid):
    return c.ok('/api/actions?scope_id=' + sid)['items']


def wait_for(fn, predicate, timeout=90):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        result = fn()
        if predicate(result):
            return result
        time.sleep(0.5)
    raise AssertionError('Observed condition did not become true')


def approve(sid):
    decisions = []
    for approval in c.ok('/api/approvals?scope_id=' + sid)['items']:
        assert approval['status'] == 'PENDING'
        body = {'scope_id': sid, 'decision': 'APPROVE',
                'expected_version': approval['plan_version'], 'plan_hash': approval['plan_hash'],
                'comment': 'Exact synthetic payload reviewed for the local ordering acceptance test.'}
        result = actors[approval['required_role']].ok('/api/approvals/' + approval['id'] + '/decision', body)
        assert result['decision_status'] == 'APPROVED'
        decisions.append({'approval_id': approval['id'], 'status': result['decision_status']})
    assert decisions
    return decisions


def recover():
    status, _ = hook('apic-recovery')
    assert 200 <= status < 300


def smtp_count(action_id):
    start = 0
    found = []
    while True:
        with urlopen(f'http://127.0.0.1:8025/api/v1/messages?start={start}&limit=100', timeout=10) as response:
            page = json.load(response)
        rows = page['messages']
        found.extend(row['ID'] for row in rows if row['MessageID'].strip('<>') == f'apic-{action_id}@example.test')
        start += len(rows)
        if not rows or start >= page['total']:
            return found


def delivered_once(sid):
    recover()
    completed = wait_for(lambda: actions(sid), lambda rows: bool(rows) and all(a['status'] == 'SUCCEEDED' for a in rows))
    mails = [a for a in completed if a['action_type'] == 'SUPPLIER_EMAIL']
    assert len(mails) == 1 and mails[0]['attempts'] == 1
    before = sorted((a['id'], a['attempts'], a['provider_id']) for a in completed)
    captured = smtp_count(mails[0]['id'])
    assert len(captured) == 1
    for _ in range(3):
        recover()
    time.sleep(3)
    after = sorted((a['id'], a['attempts'], a['provider_id']) for a in actions(sid))
    assert before == after and smtp_count(mails[0]['id']) == captured
    return {'actions': [{k: a[k] for k in ('id', 'action_type', 'status', 'attempts', 'execution_id', 'workflow_id', 'provider_id')} for a in completed],
            'mailpit_capture_ids': captured, 'smtp_message_count': 1, 'effects_stable_after_three_recoveries': True}


def parallel_then_delivery():
    seed = c.ok('/api/demo/runs', {'scenario': 'supplier-delay'})
    event = c.poll(seed)
    assert event['job_status'] == 'SUCCEEDED'
    sid = seed['scope_id']
    wait_for(lambda: actions(sid), lambda rows: all(a['status'] != 'IN_PROGRESS' for a in rows))
    c.ok(f'/api/demo/runs/{sid}/reset', {})
    assert c.ok('/api/incidents?scope_id=' + sid)['total'] == 0
    assert system(sid)['jobs'] == []
    envelope = {**event['envelope'], 'source_id': str(uuid4()), 'correlation_id': str(uuid4())}
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda _: hook('apic-email', envelope), range(10)))
    assert all(status == 202 for status, _ in results)
    source_ids = {data['source_event_id'] for _, data in results}
    job_ids = {data['job_id'] for _, data in results}
    assert len(source_ids) == len(job_ids) == 1
    accepted = c.poll(results[0][1])
    assert accepted['job_status'] == 'SUCCEEDED'
    incidents = c.ok('/api/incidents?scope_id=' + sid)
    assert incidents['total'] == 1
    detail = c.ok(f"/api/incidents/{accepted['incident_id']}?scope_id={sid}")
    assert len(detail['sources']) == 1 and detail['revision'] == 1
    assert len(system(sid)['jobs']) == 1
    decisions = approve(sid)
    return {'scope_id': sid, 'incident_id': accepted['incident_id'], 'concurrent_requests': 10,
            'initial_incident_count': 0, 'unique_source_event_ids': sorted(source_ids), 'unique_job_ids': sorted(job_ids),
            'incident_count': 1, 'linked_source_count': 1, 'decisions': decisions, **delivered_once(sid)}


def early_approval():
    seed = c.ok('/api/demo/runs', {'scenario': 'supplier-delay'})
    event = c.poll(seed)
    assert event['job_status'] == 'SUCCEEDED'
    sid = seed['scope_id']
    before = system(sid)['wait_registrations']
    assert before == [], 'Wait was already registered; this run cannot prove early approval'
    decisions = approve(sid)
    after = system(sid)['wait_registrations']
    assert after == [], 'Wait registration raced the decision; early ordering not proved'
    observed_at = datetime.now(timezone.utc).isoformat()
    persisted = c.ok('/api/approvals?scope_id=' + sid)['items']
    assert all(a['status'] == 'APPROVED' for a in persisted)
    delivery = delivered_once(sid)
    return {'scope_id': sid, 'incident_id': event['incident_id'], 'decisions': decisions,
            'wait_registrations_before_decision': before, 'wait_registrations_after_committed_decision': after,
            'early_decision_observed_at': observed_at, 'decision_persisted_before_recovery': True,
            'continuation': 'Recovery executes persisted approved actions even when no Wait was registered.', **delivery}


for name, criterion, fn in [('ten_concurrent_first_deliveries_then_one_sandbox_effect', 'AC06', parallel_then_delivery),
                            ('committed_approval_observed_before_any_wait_then_n8n_delivery', 'AC15', early_approval)]:
    started = time.monotonic()
    try:
        result = {'name': name, 'criteria': [criterion], 'status': 'PASS', 'evidence': fn()}
    except Exception as error:
        result = {'name': name, 'criteria': [criterion], 'status': 'FAIL', 'error': str(error)[:1000]}
    result['duration_seconds'] = round(time.monotonic() - started, 3)
    report['tests'].append(result)
    OUTPUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(name, result['status'], flush=True)
raise SystemExit(any(case['status'] != 'PASS' for case in report['tests']))
