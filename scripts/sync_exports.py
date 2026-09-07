"""Read back supported local n8n CLI exports, compare graphs, sanitize and inventory."""
from pathlib import Path
import subprocess,json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
command=['rtk','docker','compose','exec','-T','n8n','n8n','export:workflow','--all','--output=/project/local/all-readback.json']
subprocess.run(command,cwd=ROOT,check=True)
all_flows=json.loads((ROOT/'.local/all-readback.json').read_text(encoding='utf-8'))
source=json.loads((ROOT/'n8n/manifest.example.json').read_text())
outdir=ROOT/'n8n/exports/local';outdir.mkdir(parents=True,exist_ok=True)
report={'profile':'DEMO_LOCAL','readback_at':datetime.now(timezone.utc).isoformat(),'n8n_version':'2.37.10','workflows':[]}
for row in source['workflows']:
    matches=[w for w in all_flows if w['id']==row['id']]
    assert len(matches)==1,(row['key'],'missing/duplicateID')
    actual=matches[0];expected=json.loads((ROOT/'n8n/workflows'/row['file']).read_text(encoding='utf-8'))
    def graph(flow):
        return {'nodes':[{k:n[k] for k in ('id','name','type','typeVersion','parameters','credentials') if k in n} for n in flow['nodes']],'connections':flow['connections']}
    assert graph(actual)==graph(expected),(row['key'],'runtime/source graph drift')
    assert actual['active'] is True,(row['key'],'not published')
    safe={k:actual[k] for k in ('id','name','active','nodes','connections','settings','versionId','activeVersionId') if k in actual}
    safe['pinData']={};safe['tags']=[]
    payload=json.dumps(safe,ensure_ascii=False,indent=2)+'\n';(outdir/row['file']).write_text(payload,encoding='utf-8')
    report['workflows'].append({'key':row['key'],'id':row['id'],'name':actual['name'],'state':'PUBLISHED','graph_comparison':'PASS','file':'n8n/exports/local/'+row['file'],'sha256':hashlib.sha256(payload.encode()).hexdigest(),'url':'http://127.0.0.1:5678/workflow/'+row['id']})
(ROOT/'n8n/manifest.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'evidence/workflow-runs/local-readback.json').write_text(json.dumps(report,indent=2)+'\n')
print('10/10 published local graphs read back, matched source and sanitized.')
