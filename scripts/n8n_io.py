"""Supported CLI exports through container /tmp, independent of host bind ownership."""
from pathlib import Path
import json,subprocess,uuid
ROOT=Path(__file__).resolve().parents[1]

def export_all(destination,allow_empty=False):
    temporary='/tmp/apic-export-'+uuid.uuid4().hex+'.json'
    result=subprocess.run(['rtk','proxy','docker','compose','exec','-T','n8n','n8n','export:workflow','--all','--output='+temporary],cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        if allow_empty and 'No workflows found' in result.stdout+result.stderr:return []
        raise RuntimeError('n8n CLI export failed; deployment stopped before mutation')
    subprocess.run(['rtk','docker','compose','cp','n8n:'+temporary,str(destination)],cwd=ROOT,check=True)
    flows=json.loads(destination.read_text(encoding='utf-8'))
    assert isinstance(flows,list),'Unexpected supported CLI export format'
    return flows

def backup_owned(workflows):
    raw=ROOT/'.local/predeploy-readback.json'
    current={w['id']:w for w in export_all(raw,allow_empty=True)}
    for workflow in workflows:
        actual=current.get(workflow['id'])
        if actual is None:continue # First import of this exact ID.
        if not actual['name'].startswith('APIC |'):
            raise RuntimeError('Owned workflow ID collides with a foreign workflow; no mutation performed')
        destination=ROOT/'.local'/('rollback-'+workflow['key']+'.json')
        destination.write_text(json.dumps([actual],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Existing APIC workflows backed up through supported CLI; foreign workflows unchanged.')
