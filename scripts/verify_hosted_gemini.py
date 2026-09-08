"""One explicitly authorized hosted synthetic mail run; no external mail delivery.

This invokes the existing n8n Gemini node through the same authenticated endpoint
as the dashboard. It is a smoke test, not a statistical model evaluation.
"""
from datetime import datetime, timezone
import json
import time

from verify_hosted import ROOT, ORIGIN, client


def main():
    c = client()
    catalog = c.get('/api/demo/catalog').json()
    assert catalog['live_ai_enabled'], 'Hosted Gemini is not enabled'
    mail = catalog['source_email']
    response = c.post('/api/demo/custom-email', json={
        'subject': mail['subject'], 'content_text': mail['content_text']})
    assert response.status_code == 202, ('intake', response.status_code)
    run = response.json()
    print('Hosted synthetic mail accepted for actual Gemini extraction.', flush=True)
    event = {}
    for i in range(60):
        response = c.get('/api/source-events/' + run['source_event_id'],
                         params={'scope_id': run['scope_id']})
        response.raise_for_status()
        event = response.json()
        if event.get('job_status') in ('SUCCEEDED', 'DEAD_LETTER', 'MANUAL_REVIEW'):
            break
        if i % 10 == 0:
            print('Analysis state: ' + str(event.get('job_status')), flush=True)
        time.sleep(2)
    report = {
        'tested_at': datetime.now(timezone.utc).isoformat(),
        'origin': ORIGIN, 'scope_id': run['scope_id'],
        'source_event_id': run['source_event_id'], 'job_id': run['job_id'],
        'job_status': event.get('job_status'), 'source_status': event.get('status'),
        'boundary': 'One actual hosted synthetic mail extraction; no external email sent; not a statistical accuracy evaluation.',
    }
    system = c.get('/api/system', params={'scope_id': run['scope_id']}).json()
    job = next((j for j in system.get('jobs', []) if j['id'] == run['job_id']), {})
    report.update(workflow_id=job.get('workflow_id'), execution_id=job.get('execution_id'),
                  live_ai=system.get('live_ai'))
    if event.get('incident_id'):
        d = c.get('/api/incidents/' + event['incident_id'], params={'scope_id': run['scope_id']}).json()
        rev = next(r for r in d['revisions'] if r['revision'] == d['revision'])
        report.update(incident_id=d['id'], extraction_metadata=rev['extraction_metadata'],
                      result={'risk_score': d['risk_score'], 'severity': d['severity'],
                              'shortage': d['impact']['total_shortage'],
                              'affected_orders': len(d['impact']['affected_production_orders']),
                              'affected_value_cents': d['affected_open_order_value_cents'],
                              'partial_status': rev['facts']['proposed_partial']['status']})
    report['status'] = 'PASS' if (
        event.get('job_status') == 'SUCCEEDED' and event.get('status') == 'VERIFIED'
        and report.get('extraction_metadata', {}).get('provider') == 'google-gemini'
        and report.get('result') == {'risk_score': 83, 'severity': 'CRITICAL', 'shortage': 40,
            'affected_orders': 2, 'affected_value_cents': 5540000, 'partial_status': 'PROPOSED'}
    ) else 'FAIL'
    dest = ROOT / 'evidence/workflow-runs/hosted-gemini.json'
    dest.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps(report, default=str), flush=True)
    assert report['status'] == 'PASS', 'Inspect persisted evidence and the referenced n8n execution'


if __name__ == '__main__':
    main()
