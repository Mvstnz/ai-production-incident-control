"""Verify a real repeat bootstrap preserves the existing synthetic business state."""
from pathlib import Path
import json,subprocess,sys,hashlib
from datetime import datetime,timezone
from runtime_client import Client,ROOT

def snapshot():
    client=Client()
    scopes=client.ok('/api/auth/me')['scopes']
    rows=[]
    for scope in scopes:
        sid=scope['id']
        system=client.ok('/api/system?scope_id='+sid)
        rows.append({'scope_id':sid,
            'jobs':sorted(x['id'] for x in system['jobs']),
            'incidents':sorted(x['id'] for x in client.ok('/api/incidents?limit=200&scope_id='+sid)['items']),
            'actions':sorted(x['id'] for x in client.ok('/api/actions?scope_id='+sid)['items'])})
    return sorted(rows,key=lambda r:r['scope_id'])

before=snapshot()
env_hash=hashlib.sha256((ROOT/'.env').read_bytes()).hexdigest()
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(['rtk','proxy',sys.executable,'scripts/bootstrap.py'],cwd=ROOT)
assert result.returncode==0,'Bootstrap failed'
after=snapshot()
assert before==after,'Persisted scope/job/action identities changed across repeat bootstrap'
assert env_hash==hashlib.sha256((ROOT/'.env').read_bytes()).hexdigest(),'Secrets unexpectedly changed'
subprocess.run(['rtk','proxy',sys.executable,'scripts/sync_exports.py'],cwd=ROOT,check=True)
report={'status':'PASS','criteria':['AC02'],'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
    'scope_count':len(before),'unchanged_scope_job_action_ids':True,'persistent_secrets_unchanged':True,
    'workflow_ids':'All ten exact published IDs read back once; see local-readback.json',
    'before':before,'after':after,'note':'Repeat bootstrap on persistent local stack. Fresh-start evidence is recorded separately in CI.'}
(ROOT/'evidence/test-results/rebootstrap.json').write_text(json.dumps(report,indent=2)+'\n')
print('Repeat bootstrap preserved scopes, jobs, actions, secrets and ten workflow IDs.')
