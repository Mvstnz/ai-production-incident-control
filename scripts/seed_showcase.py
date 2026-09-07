"""Populate the shared read-only viewer scope through real local n8n intake."""
from uuid import NAMESPACE_URL,uuid5
from runtime_client import Client

def main():
    client=Client('admin')
    scope_id=str(uuid5(NAMESPACE_URL,'apic-portfolio/default-demo'))
    system=client.ok('/api/system?scope_id='+scope_id)
    assert system['profile']=='DEMO_LOCAL' and system['external_actions_enabled'] is False
    existing={i['incident_type'] for i in client.ok('/api/incidents?limit=200&scope_id='+scope_id)['items']}
    for kind,scenario in [('SUPPLIER_DELAY','supplier-delay'),('MACHINE_BREAKDOWN','machine-breakdown'),('QUALITY_ISSUE','quality-issue')]:
        if kind in existing:continue
        source=client.ok('/api/demo/runs',{'scenario':scenario,'scope_id':scope_id})
        result=client.poll(source,seconds=100)
        assert result['job_status']=='SUCCEEDED',(scenario,result['job_status'])
        print('Shared synthetic showcase assessed:',scenario,'incident',result['incident_id'])
    print('Viewer showcase ready. Consequential actions still require the responsible role approval.')
if __name__=='__main__':main()
