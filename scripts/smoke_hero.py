from runtime_client import Client,ROOT
import json
c=Client()
source=c.ok('/api/demo/runs',{'scenario':'supplier-delay'})
(ROOT/'.local/hero-source.json').write_text(json.dumps(source))
print('Durably accepted:',json.dumps(source),flush=True)
result=c.poll(source)
print('Analysis result:',json.dumps(result),flush=True)
items=c.ok('/api/incidents?scope_id='+source['scope_id'])
print('Incidents:',json.dumps(items),flush=True)
(ROOT/'.local/hero-result.json').write_text(json.dumps({'source':source,'result':result,'incidents':items},indent=2))
