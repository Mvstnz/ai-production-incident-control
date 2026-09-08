"""Observed local n8n resilience checks; shared-service interruption is opt-in.

python scripts/test_resilience.py --phase normal
python scripts/test_resilience.py --phase restart --allow-interruption
python scripts/test_resilience.py --phase database --allow-interruption

Coordinate restart/database phases with other test/browser sessions first.
Only new synthetic scopes are created; n8n internal tables are never queried.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen
from urllib.error import HTTPError,URLError
import uuid

from runtime_client import Client,ROOT,hook

args=argparse.ArgumentParser()
args.add_argument('--phase',choices=('normal','restart','database'),required=True)
args.add_argument('--allow-interruption',action='store_true')
args.add_argument('--case',action='append',default=[],help='Run only the named case; retain previous attempts in evidence history.')
options=args.parse_args()
if options.phase!='normal' and not options.allow_interruption:
    raise SystemExit('Shared-service restart requires prior coordination and --allow-interruption.')

OUTPUT=ROOT/'evidence/workflow-runs/resilience.json'
report=json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else {'profile':'DEMO_LOCAL','started_at':datetime.now(timezone.utc).isoformat(),'tests':[],'scopes':[],'target_tests':'NOT_RUN','boundary':'Real loopback HTTP -> published local n8n -> APIs -> PostgreSQL and sandbox providers'}
clients={r:Client(r) for r in ('admin','production_manager','purchasing')}
c=clients['admin']


def save():
    report['updated_at']=datetime.now(timezone.utc).isoformat()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def case(name,criteria,fn):
    if options.case and name not in options.case:return
    start=time.monotonic()
    try:
        data=fn();result={'name':name,'phase':options.phase,'criteria':criteria,'status':'PASS','evidence':data}
    except Exception as error:
        result={'name':name,'phase':options.phase,'criteria':criteria,'status':'FAIL','error':str(error)[:5000]}
    result['duration_seconds']=round(time.monotonic()-start,3)
    previous=[test for test in report['tests'] if test['name']==name]
    if previous:report.setdefault('history',[]).extend(previous)
    report['tests']=[test for test in report['tests'] if test['name']!=name]+[result]
    save();print(name,result['status'],flush=True)


def recover():
    code,data=hook('apic-recovery')
    assert 200<=code<300,('Recovery trigger failed',code,data)
    return data


def system(sid):return c.ok('/api/system?scope_id='+sid)
def approvals(sid):return c.ok('/api/approvals?scope_id='+sid)['items']
def actions(sid):return c.ok('/api/actions?scope_id='+sid)['items']
def detail(sid,iid):return c.ok(f'/api/incidents/{iid}?scope_id={sid}')


def wait_for(fn,condition,timeout=90,label='condition'):
    end=time.monotonic()+timeout;last=None
    while time.monotonic()<end:
        last=fn()
        if condition(last):return last
        time.sleep(1)
    raise AssertionError((label,'deadline exceeded',last))


def source(scenario='supplier-delay',sid=None):
    accepted=c.ok('/api/demo/runs',{'scenario':scenario,**({'scope_id':sid} if sid else {})})
    if accepted['scope_id'] not in report['scopes']:
        report['scopes'].append(accepted['scope_id']);save()
    event=c.poll(accepted,seconds=110)
    assert event['job_status']=='SUCCEEDED',event
    return accepted,event,detail(accepted['scope_id'],event['incident_id'])


def decision(sid,approval,choice='APPROVE',payload=None):
    body={'scope_id':sid,'decision':choice,'expected_version':approval['plan_version'],'plan_hash':approval['plan_hash'],'comment':'Exact synthetic plan reviewed in local resilience acceptance test.'}
    if payload is not None:body['payload']=payload
    return clients[approval['required_role']].request(f"/api/approvals/{approval['id']}/decision",body)


def approve_all(sid):
    results=[]
    for approval in approvals(sid):
        if approval['status']=='PENDING':
            status,data=decision(sid,approval);assert status==200,(status,data)
            results.append({'approval_id':approval['id'],'result':data})
    return results


def current_actions_done(sid,timeout=100):
    return wait_for(lambda:actions(sid),lambda rows:bool(rows) and all(r['status'] in ('SUCCEEDED','CANCELLED') for r in rows),timeout,'actions succeeded')


def summary(sid,iid):
    return {'scope_id':sid,'incident_id':iid,'incident_status':detail(sid,iid)['status'],'jobs':system(sid)['jobs'],'wait_registrations':system(sid).get('wait_registrations',[]),'actions':actions(sid)}


def rejected():
    src,event,incident=source();sid=src['scope_id']
    approval=next(a for a in approvals(sid) if a['status']=='PENDING')
    status,data=decision(sid,approval,'REJECT');assert status==200,(status,data)
    recover();time.sleep(4)
    state=detail(sid,incident['id'])
    assert state['status'] not in ('RESOLVED','CLOSED')
    assert next(a for a in approvals(sid) if a['id']==approval['id'])['status']=='REJECTED'
    assert all(a['status'] not in ('READY','IN_PROGRESS','SUCCEEDED') for a in actions(sid) if a['action_type']=='SUPPLIER_EMAIL')
    return {**summary(sid,incident['id']),'approval_id':approval['id'],'decision_result':data}


def modified():
    src,event,incident=source();sid=src['scope_id']
    approval=next(a for a in approvals(sid) if a['status']=='PENDING')
    old=next(p for p in incident['plans'] if p['id']==approval['plan_id'])
    payload=deepcopy(old['body'])
    mail=next(a for a in payload['actions'] if a['action_type']=='SUPPLIER_EMAIL')
    mail['payload']['body']+='\nPlease reply with the verified availability confirmation.'
    code,data=decision(sid,approval,'MODIFY',payload);assert code==200,(code,data)
    assert data['plan_version']==old['plan_version']+1 and data['plan_hash']!=old['plan_hash']
    current=detail(sid,incident['id'])
    assert next(a for a in current['approvals'] if a['id']==approval['id'])['status']=='SUPERSEDED'
    assert all(a['status']=='CANCELLED' for a in current['actions'] if a['plan_id']==old['id'] and a['action_type']=='SUPPLIER_EMAIL')
    assert any(a['status']=='PENDING' and a['plan_id']==data['plan_id'] for a in current['approvals'])
    approved=approve_all(sid);recover();executed=current_actions_done(sid)
    sent=next(a for a in executed if a['plan_id']==data['plan_id'] and a['action_type']=='SUPPLIER_EMAIL')
    assert sent['payload']['body']==mail['payload']['body']
    return {**summary(sid,incident['id']),'old_plan_id':old['id'],'new_plan':data,'approval_decisions':approved,'sent_exact_modified_body':True}


def expired():
    src,event,incident=source();sid=src['scope_id']
    approval=next(a for a in approvals(sid) if a['status']=='PENDING')
    advanced=c.ok(f'/api/demo/runs/{sid}/advance',{'seconds':86401})
    recover()
    state=wait_for(lambda:approvals(sid),lambda rows:any(a['id']==approval['id'] and a['status']=='EXPIRED' for a in rows),30,'approval expiry')
    code,data=decision(sid,approval);assert code==409,(code,data)
    assert all(a['status'] not in ('READY','IN_PROGRESS','SUCCEEDED') for a in actions(sid) if a['action_type']=='SUPPLIER_EMAIL')
    return {**summary(sid,incident['id']),'clock':advanced,'approvals':state,'late_approval_http_status':code}


def stale():
    src,event,incident=source();sid=src['scope_id']
    old=next(a for a in approvals(sid) if a['status']=='PENDING')
    split,_,new=source('supplier-split',sid)
    assert new['revision']==2
    code,result=decision(sid,old);assert code==409,(code,result)
    assert next(a for a in approvals(sid) if a['id']==old['id'])['status']=='SUPERSEDED'
    assert all(a['status']=='CANCELLED' for a in actions(sid) if a['plan_id']==old['plan_id'] and a['action_type']=='SUPPLIER_EMAIL')
    return {**summary(sid,incident['id']),'old_approval_id':old['id'],'revision':new['revision'],'old_approval_http_status':code}


def retry_read(kind,persist):
    src,event,incident=source();sid=src['scope_id']
    c.ok('/api/demo/failures',{'scope_id':sid,'kind':kind,'enabled':True})
    try:
        accepted=c.ok('/api/demo/runs',{'scenario':'supplier-split','scope_id':sid})
        jid=accepted['job_id'];history=[];lastkey=None;start=time.monotonic();next_recovery=0
        while time.monotonic()-start<400:
            job=next(j for j in system(sid)['jobs'] if j['id']==jid)
            key=(job['status'],job['attempts'],job['execution_id'],job.get('next_attempt_at'))
            if key!=lastkey:
                history.append({'observed_at':datetime.now(timezone.utc).isoformat(),**job});lastkey=key
                print(kind,job['status'],'attempt',job['attempts'],flush=True)
            assert job['attempts']<=4,job
            if not persist and job['status']=='RETRY_SCHEDULED':
                c.ok('/api/demo/failures',{'scope_id':sid,'kind':kind,'enabled':False})
            if job['status'] in ('DEAD_LETTER','SUCCEEDED'):break
            if time.monotonic()>=next_recovery:recover();next_recovery=time.monotonic()+8
            time.sleep(2)
        if persist:assert job['status']=='DEAD_LETTER' and job['attempts']==4,job
        else:assert job['status']=='SUCCEEDED' and 2<=job['attempts']<=4,job
        errors=c.ok('/api/errors?scope_id='+sid)['items']
        errors=[e for e in errors if e.get('job_id')==jid]
        assert errors and all(e['error_class']=='TRANSIENT' for e in errors),errors
        if kind=='read-429':
            scheduled=next(x for x in history if x['status']=='RETRY_SCHEDULED')
            delay=(datetime.fromisoformat(scheduled['next_attempt_at'])-datetime.fromisoformat(scheduled['observed_at'])).total_seconds()
            assert delay>=25,('Retry-After was not preserved',delay,scheduled)
        return {'scope_id':sid,'job_id':jid,'kind':kind,'history':history,'workflow_errors':errors,'final_status':job['status'],'total_attempts':job['attempts'],'max_total_attempts':4}
    finally:
        c.ok('/api/demo/failures',{'scope_id':sid,'kind':kind,'enabled':False})


def sla():
    src,event,incident=source();sid=src['scope_id']
    c.ok(f'/api/demo/runs/{sid}/advance',{'seconds':1801})
    recover()
    state=wait_for(lambda:system(sid),lambda x:len([n for n in x.get('notifications',[]) if n['body']['kind']=='SLA'])==2,30,'two SLA stages')
    before=[n['id'] for n in state['notifications'] if n['body']['kind']=='SLA']
    recover();time.sleep(3)
    after=[n['id'] for n in system(sid)['notifications'] if n['body']['kind']=='SLA']
    assert sorted(before)==sorted(after)
    assert all(a['status']=='PENDING' for a in approvals(sid))
    assert all(a['status']!='SUCCEEDED' for a in actions(sid) if a['action_type']=='SUPPLIER_EMAIL')
    return {**summary(sid,incident['id']),'notification_ids_before':before,'notification_ids_after':after,'automatic_approval':False}


def scoped_reset():
    src,event,incident=source();sid=src['scope_id']
    other,_,other_incident=source();foreign=other['scope_id']
    before=detail(foreign,other_incident['id'])
    # Let the already-allowed internal sandbox ticket finish before reset.
    wait_for(lambda:actions(sid),lambda rows:all(a['status']!='IN_PROGRESS' for a in rows),30,'no in-flight action')
    result=c.ok(f'/api/demo/runs/{sid}/reset',{})
    assert c.ok('/api/incidents?scope_id='+sid)['total']==0
    after=detail(foreign,other_incident['id'])
    assert before['id']==after['id'] and before['revision']==after['revision'] and before['impact']==after['impact']
    assert {x['id'] for x in before['sources']}=={x['id'] for x in after['sources']}
    return {'reset_scope':sid,'reset_result':result,'other_scope':foreign,'other_incident_id':after['id'],'other_revision':after['revision'],'other_impact_unchanged':True}


def compose(*command):
    result=subprocess.run(['docker','compose',*command],cwd=ROOT,capture_output=True,text=True,timeout=120)
    assert result.returncode==0,(command,result.stderr[-1000:])
    return {'command':['docker','compose',*command],'returncode':result.returncode,'observed_at':datetime.now(timezone.utc).isoformat()}


def health(url,timeout=120):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        try:
            with urlopen(url,timeout=4) as response:
                if response.status==200:return {'url':url,'http_status':200,'observed_at':datetime.now(timezone.utc).isoformat()}
        except (HTTPError,URLError,TimeoutError,OSError):pass
        time.sleep(2)
    raise AssertionError(('Health did not recover',url))


def webhook_ready(timeout=75):
    """n8n liveness precedes webhook activation after restart; observe both."""
    observed=[];end=time.monotonic()+timeout
    while time.monotonic()<end:
        try:
            code,data=hook('apic-recovery')
            observed.append({'http_status':code,'observed_at':datetime.now(timezone.utc).isoformat()})
            if 200<=code<300:return observed
            assert code in (404,503),('Unexpected recovery activation error',code,str(data)[:300])
        except (URLError,TimeoutError,OSError) as error:
            observed.append({'transport_error':type(error).__name__,'observed_at':datetime.now(timezone.utc).isoformat()})
        time.sleep(2)
    raise AssertionError(('Published webhook readiness deadline',observed))


def restart_wait_and_outbox():
    src,event,incident=source();sid=src['scope_id']
    registered=wait_for(lambda:system(sid).get('wait_registrations',[]),bool,90,'real Wait registration')
    operations=[]
    try:
        operations.append(compose('stop','n8n'))
        decisions=approve_all(sid)
        waiting_actions=actions(sid)
        assert any(a['action_type']=='SUPPLIER_EMAIL' and a['status']=='READY' for a in waiting_actions)
        durable=system(sid)
        assert durable['wait_registrations']==registered
        assert any(x['kind']=='WAKEUP' and x['count']>=1 for x in durable['outbox'])
    finally:
        operations.append(compose('start','n8n'))
        recovered=health('http://127.0.0.1:5678/healthz')
    retained=system(sid).get('wait_registrations',[])
    assert retained==registered
    readiness=webhook_ready();finished=current_actions_done(sid,120)
    before=sorted((a['id'],a['attempts'],a['provider_id']) for a in finished)
    recover();time.sleep(3)
    after=sorted((a['id'],a['attempts'],a['provider_id']) for a in current_actions_done(sid))
    assert before==after
    return {**summary(sid,incident['id']),'container_operations':operations,'health_after_restart':recovered,'published_webhook_readiness':readiness,'wait_registration_before':registered,'wait_registration_after':retained,'decision_committed_while_n8n_stopped':decisions,'outbox_while_stopped':durable['outbox'],'action_effects_after_first_and_second_recovery_equal':True}


def database_outage():
    src,event,incident=source();sid=src['scope_id']
    envelope=deepcopy(event['envelope']);envelope['source_id']=str(uuid.uuid4());envelope['correlation_id']=str(uuid.uuid4())
    operations=[];failure=None
    try:
        operations.append(compose('stop','postgres'))
        try:
            code,data=hook('apic-email',envelope)
            failure={'http_status':code,'response':str(data)[:1000]}
            assert code!=202,('False acceptance during database outage',code,data)
        except (URLError,TimeoutError,OSError) as error:
            failure={'http_status':None,'transport_error':type(error).__name__,'accepted':False}
    finally:
        operations.append(compose('start','postgres'))
        ready_ops=health('http://127.0.0.1:8000/health/ready',120)
        ready_n8n=health('http://127.0.0.1:5678/healthz',150)
    readiness=webhook_ready()
    code,accepted=hook('apic-email',envelope);assert code==202,(code,accepted)
    final=c.poll(accepted,seconds=110);assert final['job_status']=='SUCCEEDED',final
    replay_code,replayed=hook('apic-email',envelope);assert replay_code==202
    assert replayed['source_event_id']==accepted['source_event_id'] and replayed['job_id']==accepted['job_id']
    return {**summary(sid,incident['id']),'container_operations':operations,'outage_ingress':failure,'health_after_recovery':[ready_ops,ready_n8n],'published_webhook_readiness':readiness,'redelivery_source_event_id':accepted['source_event_id'],'redelivery_job_id':accepted['job_id'],'same_source_retry_deduplicated':True}


if options.phase=='normal':
    case('rejected_plan_never_dispatches_supplier_email',['AC16'],rejected)
    case('modified_plan_requires_new_exact_approval',['AC16'],modified)
    case('expired_plan_prevents_late_approval',['AC16'],expired)
    case('superseded_approval_rejected_after_new_revision',['AC17'],stale)
    case('ERP_429_respects_retry_after_then_recovers',['AC20'],lambda:retry_read('read-429',False))
    case('ERP_503_stops_after_four_attempts_in_DLQ',['AC20'],lambda:retry_read('read-503',True))
    case('SLA_stages_are_unique_and_never_auto_approve',['AC23'],sla)
    case('reset_only_changes_owned_synthetic_scope',['AC29'],scoped_reset)
elif options.phase=='restart':
    case('registered_wait_and_committed_approval_outbox_survive_n8n_restart',['AC22'],restart_wait_and_outbox)
else:
    case('database_outage_no_false_202_and_safe_redelivery',['AC21'],database_outage)

failed=[t['name'] for t in report['tests'] if t['phase']==options.phase and t['status']=='FAIL']
print(json.dumps({'phase':options.phase,'failed':failed,'evidence':str(OUTPUT.relative_to(ROOT))}),flush=True)
raise SystemExit(bool(failed))
