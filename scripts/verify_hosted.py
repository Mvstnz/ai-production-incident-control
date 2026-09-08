"""Exercise the deployed application via real HTTPS; never print credentials."""
import json,time
from pathlib import Path
from datetime import datetime,timezone
import httpx

ROOT=Path(__file__).resolve().parents[1]
ENV=json.loads((ROOT/'.local/hosted-env.json').read_text())
ORIGIN=ENV['DASHBOARD_ORIGIN']
SID='df7540ff-dfa1-5883-9ea7-fdf4a4dd5e10'

def client(role='admin'):
    account=next(u for u in json.loads((ROOT/'.local/hosted-credentials.json').read_text())['users'] if u['role']==role)
    c=httpx.Client(base_url=ORIGIN,timeout=60,headers={'Origin':ORIGIN})
    response=c.post('/api/auth/login',json={k:account[k] for k in ('username','password')})
    assert response.status_code==200,('login',response.status_code)
    c.headers['X-CSRF-Token']=response.json()['csrf_token']
    return c

def main():
    c=client()
    report={'run_at':datetime.now(timezone.utc).isoformat(),'origin':ORIGIN,'dataset':'fictional-v2','checks':[],'incidents':[]}
    for path in ('/','/health/live','/health/ready','/api/demo/catalog'):
        r=c.get(path);assert r.status_code==200,(path,r.status_code)
        report['checks'].append({'path':path,'status':r.status_code})
    for scenario,kind,score in [('supplier-delay','SUPPLIER_DELAY',83),('machine-breakdown','MACHINE_BREAKDOWN',62),('quality-issue','QUALITY_ISSUE',70)]:
        existing=c.get('/api/incidents',params={'scope_id':SID}).json()['items']
        matching=next((i for i in existing if i['incident_type']==kind and i.get('risk_score')==score),None)
        if not matching:
            r=c.post('/api/demo/runs',json={'scenario':scenario,'scope_id':SID})
            assert r.status_code==202,('intake',scenario,r.status_code,r.text[:300])
            run=r.json();print('Accepted '+scenario+' '+run['source_event_id'],flush=True)
            for _ in range(60):
                event=c.get('/api/source-events/'+run['source_event_id'],params={'scope_id':SID})
                assert event.status_code==200,event.text[:300]
                body=event.json()
                if body.get('job_status')=='SUCCEEDED':break
                if body.get('job_status') in ('DEAD_LETTER','MANUAL_REVIEW'):raise AssertionError((scenario,body['job_status']))
                time.sleep(1)
            else:raise AssertionError((scenario,'analysis timeout',body.get('job_status')))
            matching=c.get('/api/incidents/'+body['incident_id'],params={'scope_id':SID}).json()
        assert matching['risk_score']==score,(scenario,matching.get('risk_score'))
        report['incidents'].append({k:matching[k] for k in ('id','incident_type','risk_score','severity','status')})
        print(scenario+' verified: '+str(score),flush=True)
    visitor=httpx.Client(base_url=ORIGIN,headers={'Origin':ORIGIN},timeout=30)
    r=visitor.post('/api/auth/demo');assert r.status_code==200,('public login',r.status_code,r.text[:200])
    session=r.json();assert session['user']['role']=='viewer' and [s['id'] for s in session['scopes']]==[SID]
    visitor.headers['X-CSRF-Token']=session['csrf_token']
    assert visitor.post('/api/demo/runs',json={'scenario':'supplier-delay','scope_id':SID}).status_code==403
    assert visitor.get('/api/dashboard',params={'scope_id':SID}).status_code==200
    report['checks'].append({'public_read_only_scope':'PASS','public_mutation_denied':'PASS'})
    report['status']='TARGET_TESTED'
    path=ROOT/'evidence/workflow-runs/hosted-demo.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2))
    print('Hosted scenarios and public read-only access verified.',flush=True)

if __name__=='__main__':main()
