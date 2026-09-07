from pathlib import Path
import json,time,urllib.request,urllib.error
root=Path(__file__).resolve().parents[1]
env=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if line and not line.startswith('#'))
for n in range(30):
    try:
        urllib.request.urlopen('http://127.0.0.1:5678/healthz',timeout=2);break
    except (urllib.error.URLError,TimeoutError):time.sleep(1)
req=urllib.request.Request('http://127.0.0.1:5678/webhook/apic-probe',data=b'{}',headers={'Content-Type':'application/json','X-Webhook-Token':env['N8N_WEBHOOK_TOKEN']})
with urllib.request.urlopen(req,timeout=45) as response:
    result=json.load(response)
assert result['probe']==42 and result['execution_id']
req=urllib.request.Request('http://127.0.0.1:5678/webhook/apic-probe',data=b'{}',headers={'Content-Type':'application/json'})
try:urllib.request.urlopen(req,timeout=5);raise AssertionError('Unauthenticated probe accepted')
except urllib.error.HTTPError as exc:assert exc.code in (401,403)
dest=root/'evidence/workflow-runs';dest.mkdir(parents=True,exist_ok=True)
history=dest/'m0-local.json'
data=json.loads(history.read_text()) if history.exists() else {'profile':'DEMO_LOCAL','workflow_id':'APICPROBE0000001','runs':[]}
data['runs'].append({'status':'PASS','result':result,'unauthenticated_status':'REJECTED','tested_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
history.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(result));print('PASS: authenticated production webhook and real code runner; unauthenticated request rejected.')
