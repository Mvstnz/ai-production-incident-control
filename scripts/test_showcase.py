"""Verify the shared viewer demo and repeated population before approving its actions."""
from runtime_client import Client,ROOT
from seed_showcase import main as seed
from uuid import NAMESPACE_URL,uuid5
import json
scope_id=str(uuid5(NAMESPACE_URL,'apic-portfolio/default-demo/fictional-v2'))
viewer=Client('viewer')
def state():
    return {
        'incidents':viewer.ok('/api/incidents?limit=200&scope_id='+scope_id)['items'],
        'actions':viewer.ok('/api/actions?scope_id='+scope_id)['items'],
        'jobs':viewer.ok('/api/system?scope_id='+scope_id)['jobs']}
before=state()
assert {i['incident_type'] for i in before['incidents']}=={'SUPPLIER_DELAY','MACHINE_BREAKDOWN','QUALITY_ISSUE'}
external=[a for a in before['actions'] if a['action_type']!='INTERNAL_TICKET']
assert len(external)==3 and all(a['status']=='WAITING_APPROVAL' and a['attempts']==0 for a in external)
seed();after=state()
for key in before:assert sorted(x['id'] for x in before[key])==sorted(x['id'] for x in after[key])
code,_=viewer.request('/api/demo/runs',{'scenario':'supplier-delay','scope_id':scope_id})
assert code==403
report={'status':'PASS','scope_id':scope_id,'viewer_can_read_three_incident_types':True,'repeat_seed_preserves_incident_job_action_ids':True,'viewer_mutation_http_status':code,'consequential_actions_wait_for_approval':True,'incident_ids':[i['id'] for i in after['incidents']],'execution_ids':[j['execution_id'] for j in after['jobs']]}
(ROOT/'evidence/test-results/shared-showcase.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
