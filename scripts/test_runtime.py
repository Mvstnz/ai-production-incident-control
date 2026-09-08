"""Real loopback HTTP -> published n8n -> APIs/Postgres/Mailpit acceptance checks.

Does not use mock HTTP, direct SQL or remote resources. Each scenario owns a new
synthetic scope. Every check records its actual result and observed execution IDs.
"""
from runtime_client import Client,ROOT,hook
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import json,time,uuid,traceback,subprocess

report={'profile':'DEMO_LOCAL','started_at':datetime.now(timezone.utc).isoformat(),'tests':[],'scopes':[],'target_tests':'NOT_RUN'}
clients={r:Client(r) for r in ('admin','purchasing','production_manager','quality_manager','operator','viewer')}
c=clients['admin']
def save():
    out=ROOT/'evidence/workflow-runs/local-e2e.json';out.parent.mkdir(parents=True,exist_ok=True)
    def sanitize(value):
        if isinstance(value,dict):return {k:sanitize(v) for k,v in value.items() if k not in ('claim_token','resume_url','password','csrf_token')}
        if isinstance(value,list):return [sanitize(v) for v in value]
        return value
    out.write_text(json.dumps(sanitize(report),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def case(name,acs,fn):
    start=time.monotonic()
    try: evidence=fn();item={'name':name,'criteria':acs,'status':'PASS','evidence':evidence}
    except Exception as e:item={'name':name,'criteria':acs,'status':'FAIL','error':str(e)};traceback.print_exc()
    item['duration_seconds']=round(time.monotonic()-start,3);report['tests'].append(item);save()
    print(name,item['status'],flush=True)
def source(scenario,scope=None):
    result=c.ok('/api/demo/runs',{'scenario':scenario,**({'scope_id':scope} if scope else {})})
    if result['scope_id'] not in report['scopes']:report['scopes'].append(result['scope_id'])
    event=c.poll(result);assert event['job_status']=='SUCCEEDED',event
    return result,event,detail(result['scope_id'],event['incident_id']) if event.get('incident_id') else None
def detail(sid,iid):return c.ok(f'/api/incidents/{iid}?scope_id={sid}')
def system(sid):return c.ok('/api/system?scope_id='+sid)
def approve(sid):
    approvals=c.ok('/api/approvals?scope_id='+sid)['items'];decisions=[]
    for a in approvals:
        if a['status']!='PENDING':continue
        body={'scope_id':sid,'decision':'APPROVE','expected_version':a['plan_version'],'plan_hash':a['plan_hash'],'comment':'Approved exact synthetic demo payload for local acceptance test.'}
        actor=clients[a['required_role']]
        result=actor.ok(f"/api/approvals/{a['id']}/decision",body)
        replay=actor.request(f"/api/approvals/{a['id']}/decision",body)[0]
        assert replay in (200,409),replay
        decisions.append({'approval_id':a['id'],'result':result,'replay_status':replay})
    return decisions
def dispatch():
    code,data=hook('apic-recovery');assert 200<=code<300,(code,data)
    return data
def wait_actions(sid,allowed=('SUCCEEDED',),seconds=75):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        actions=c.ok('/api/actions?scope_id='+sid)['items']
        current=[a for a in actions if a['status']!='CANCELLED']
        if current and all(a['status'] in allowed for a in current):return current
        time.sleep(1)
    raise AssertionError([(a['action_type'],a['status']) for a in actions])
def summary(sid,i):
    return {'scope_id':sid,'incident_id':i['id'],'revision':i['revision'],'status':i['status'],'risk_score':i['risk_score'],'severity':i['severity'],'shortage':i['impact']['total_shortage'],'affected_value_cents':i['affected_open_order_value_cents'],'jobs':system(sid)['jobs']}

hero={}
def baseline():
    s,e,i=source('supplier-delay');hero.update(source=s,event=e,incident=i)
    x=i['impact'];assert (x['total_required'],x['total_available'],x['total_shortage'])==(76,36,40)
    assert x['initial_available_inventory']==24
    assert len(x['reviewed_production_orders'])==4 and len(x['affected_production_orders'])==2
    assert i['risk_score']==83 and i['severity']=='CRITICAL' and i['affected_open_order_value_cents']==5540000
    assert x['proposals'] and x['what_if'];assert i['status']=='WAITING_APPROVAL'
    return summary(s['scope_id'],i)
case('hero_baseline_and_proposed_partial',['AC03','AC04'],baseline)

def delivery():
    sid=hero['source']['scope_id'];decisions=approve(sid);dispatch();actions=wait_actions(sid)
    i=detail(sid,hero['incident']['id']);assert i['status']=='MONITORING'
    before=[(a['id'],a['attempts'],a['provider_id']) for a in actions]
    dispatch();time.sleep(2)
    after=[(a['id'],a['attempts'],a['provider_id']) for a in wait_actions(sid)]
    assert sorted(before)==sorted(after)
    return {'scope_id':sid,'decisions':decisions,'actions':actions,'incident_status':i['status']}
case('approval_replay_early_decision_and_delivery',['AC14','AC15','AC27'],delivery)

def split():
    sid=hero['source']['scope_id'];s,e,i=source('supplier-split',sid)
    assert i['id']==hero['incident']['id'] and i['revision']==2 and len(i['revisions'])==2
    assert i['impact']['total_shortage']==10 and len(i['impact']['affected_production_orders'])==1
    assert i['risk_score']==56 and i['severity']=='HIGH' and i['affected_open_order_value_cents']==2160000
    return summary(sid,i)
case('confirmed_split_replaces_supply_and_revises',['AC05','AC08'],split)

def duplicate():
    s,e,i=source('supplier-delay');sid=s['scope_id'];envelope=e['envelope']
    envelope['source_id']=str(uuid.uuid4());envelope['correlation_id']=str(uuid.uuid4())
    with ThreadPoolExecutor(max_workers=10) as pool:results=list(pool.map(lambda _:hook('apic-email',envelope),range(10)))
    assert all(code==202 for code,_ in results),results
    events={d['source_event_id'] for _,d in results};jobs={d['job_id'] for _,d in results}
    assert len(events)==1 and len(jobs)==1
    c.poll(results[0][1]);current=detail(sid,i['id']);assert current['revision']==1 and len(current['sources'])==2
    facts=current['revisions'][0]['facts']
    other={**envelope,'source':'FORM','source_id':str(uuid.uuid4()),'payload':facts,'content_text':'Verified structured report of identical facts.'}
    code,data=hook('apic-intake',other);assert code==202;c.poll(data)
    current=detail(sid,i['id']);assert current['revision']==1 and len(current['sources'])==3
    return {'scope_id':sid,'parallel_requests':10,'unique_source_events':len(events),'unique_jobs':len(jobs),'linked_sources':len(current['sources']),'revision':current['revision'],'jobs':system(sid)['jobs']}
case('parallel_deduplication_and_cross_channel_correlation',['AC06','AC07'],duplicate)

def machine():
    s,e,i=source('machine-breakdown');sid=s['scope_id'];assert i['risk_score']==62 and i['severity']=='HIGH'
    assert i['impact']['qualified_alternative_available'] is False
    approve(sid);dispatch();actions=wait_actions(sid)
    return {**summary(sid,detail(sid,i['id'])),'actions':actions}
case('machine_approved_mock_erp_reschedule',['AC24'],machine)

def quality():
    s,e,i=source('quality-issue');sid=s['scope_id']
    assert i['severity']=='CRITICAL' and i['risk']['override_reason']=='VERIFIED_DEFECTIVE_LOT_PENDING_SHIPMENT'
    blocks=[a for a in i['actions'] if a['action_type']=='QUALITY_BLOCK'];assert blocks and all(a['status']=='WAITING_APPROVAL' for a in blocks)
    assert any(a['required_role']=='quality_manager' for a in i['approvals'])
    approve(sid);dispatch();actions=wait_actions(sid)
    return {**summary(sid,detail(sid,i['id'])),'actions':actions}
case('quality_trace_and_quality_manager_approval',['AC25'],quality)

def unknown():
    s,e,i=source('unknown-input');assert e['status']=='MANUAL_REVIEW';assert e['review_reasons']
    return {'scope_id':s['scope_id'],'source_status':e['status'],'review_reasons':e['review_reasons'],'jobs':system(s['scope_id'])['jobs']}
case('ambiguous_input_requires_clarification',['AC09'],unknown)

def timeout():
    s,e,i=source('supplier-delay');sid=s['scope_id']
    c.ok('/api/demo/failures',{'scope_id':sid,'kind':'write-timeout','enabled':True});approve(sid);dispatch()
    actions=wait_actions(sid,('SUCCEEDED','UNKNOWN_OUTCOME'));assert any(a['status']=='UNKNOWN_OUTCOME' for a in actions)
    before=[(a['id'],a['attempts'],a['provider_id']) for a in actions]
    dispatch();time.sleep(2);after=[(a['id'],a['attempts'],a['provider_id']) for a in wait_actions(sid,('SUCCEEDED','UNKNOWN_OUTCOME'))]
    assert sorted(before)==sorted(after)
    return {'scope_id':sid,'actions':actions,'blind_retry':False}
case('accepted_write_timeout_does_not_resend',['AC19'],timeout)

def digest():
    sid=hero['source']['scope_id'];one=hook('apic-digest',{'scope_id':sid});two=hook('apic-digest',{'scope_id':sid})
    assert one[0]==two[0]==200,(one,two)
    a=one[1]['items'][0];b=two[1]['items'][0];assert a['id']==b['id'] and a['body']==b['body']
    kpi=c.ok('/api/dashboard?scope_id='+sid)
    assert a['body']['affected_open_order_value_cents']==kpi['affected_open_order_value_cents']
    return {'scope_id':sid,'digest_id':a['id'],'digest':a['body'],'kpi':kpi}
case('daily_digest_is_idempotent',['AC28'],digest)

def access():
    sid=hero['source']['scope_id'];a=c.ok('/api/approvals?scope_id='+sid)['items'][-1]
    body={'scope_id':sid,'decision':'APPROVE','expected_version':a['plan_version'],'plan_hash':a['plan_hash'],'comment':'Must be denied.'}
    status=clients['viewer'].request(f"/api/approvals/{a['id']}/decision",body)[0];assert status==403
    no_csrf=c.request('/api/demo/runs',{'scenario':'supplier-delay'},{'X-CSRF-Token':''})[0];assert no_csrf==403
    foreign=clients['operator'].request('/api/incidents?scope_id='+sid)[0];assert foreign==403
    return {'viewer_denied':status,'missing_csrf_denied':no_csrf,'nonmember_scope_denied':foreign}
case('runtime_auth_csrf_scope_boundaries',['AC18','AC34'],access)

report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'passed':sum(t['status']=='PASS' for t in report['tests']),'failed':sum(t['status']=='FAIL' for t in report['tests'])}),flush=True)
raise SystemExit(any(t['status']=='FAIL' for t in report['tests']))
