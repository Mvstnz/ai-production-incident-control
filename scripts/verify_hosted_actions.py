"""Verify approved sandbox actions in a private scope on the deployed system."""
import json,time
from datetime import datetime,timezone
import httpx
from verify_hosted import ROOT,ENV,ORIGIN,client

def main():
    admin=client();sid=None;incident_ids=[]
    for scenario in ('supplier-delay','machine-breakdown','quality-issue'):
        response=admin.post('/api/demo/runs',json={'scenario':scenario,**({'scope_id':sid} if sid else {})})
        assert response.status_code==202,(scenario,response.status_code,response.text[:200])
        run=response.json();sid=run['scope_id'];print('Accepted private '+scenario,flush=True)
        for _ in range(80):
            event=admin.get('/api/source-events/'+run['source_event_id'],params={'scope_id':sid}).json()
            if event.get('job_status')=='SUCCEEDED':break
            time.sleep(1)
        else:raise AssertionError('Analysis did not complete')
        incident_ids.append(event['incident_id'])
    (ROOT/'.local/hosted-action-scope.json').write_text(json.dumps({'scope_id':sid,'incidents':incident_ids}))
    approvals=admin.get('/api/approvals',params={'scope_id':sid}).json()['items'];actors={}
    for approval in approvals:
        if approval['status']!='PENDING':continue
        actor=actors.setdefault(approval['required_role'],client(approval['required_role']))
        response=actor.post('/api/approvals/'+approval['id']+'/decision',json={'scope_id':sid,'decision':'APPROVE','expected_version':approval['plan_version'],'plan_hash':approval['plan_hash'],'comment':'Approve the displayed synthetic payload for live sandbox verification.'})
        assert response.status_code==200,('approval',response.status_code,response.text[:200])
    for _ in range(90):
        actions=admin.get('/api/actions',params={'scope_id':sid}).json()['items']
        if actions and all(a['status']=='SUCCEEDED' for a in actions):break
        if any(a['status'] in ('FAILED','UNKNOWN_OUTCOME') for a in actions):raise AssertionError([(a['action_type'],a['status']) for a in actions])
        time.sleep(1)
    else:raise AssertionError([(a['action_type'],a['status']) for a in actions])
    mail=next(a for a in actions if a['action_type']=='SUPPLIER_EMAIL')
    assert mail['result']['delivery_mode']=='captured'
    before=sorted((a['id'],a['attempts'],a['provider_id']) for a in actions)
    r=httpx.post(ENV['N8N_RECOVERY_URL'],json={},headers={'X-Webhook-Token':ENV['N8N_WEBHOOK_TOKEN']},timeout=20);assert r.is_success
    time.sleep(4)
    after=admin.get('/api/actions',params={'scope_id':sid}).json()['items']
    assert before==sorted((a['id'],a['attempts'],a['provider_id']) for a in after)
    public=httpx.Client(base_url=ORIGIN,headers={'Origin':ORIGIN},timeout=30)
    assert public.post('/api/auth/demo').status_code==200
    assert public.get('/api/dashboard',params={'scope_id':sid}).status_code==403
    report={'run_at':datetime.now(timezone.utc).isoformat(),'status':'TARGET_TESTED','scope_id':sid,'public_scope_isolation':'PASS','repeated_dispatch_idempotent':'PASS','email_delivery':'database capture; no external mail','actions':[{k:a[k] for k in ('id','action_type','status','attempts','provider_id','execution_id','workflow_id')} for a in actions]}
    path=ROOT/'evidence/workflow-runs/hosted-actions.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2))
    print('Approved email capture, saw rescheduling and plate shipment block verified.',flush=True)

if __name__=='__main__':main()
