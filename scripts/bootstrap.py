"""Local-only reproducible bootstrap; never targets the connected cloud instance."""
from pathlib import Path
import argparse,json,subprocess,sys,time,urllib.request,urllib.error,hashlib,http.client
from n8n_io import backup_owned
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    result=subprocess.run(['rtk',*args],cwd=ROOT,check=True,text=True)
    return result
def compose(*args):return run('docker','compose',*args)
def wait(url,seconds=120):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        try:
            with urllib.request.urlopen(url,timeout=2) as r:
                if r.status==200:return
        except (urllib.error.URLError,TimeoutError,ConnectionError,http.client.RemoteDisconnected):pass
        time.sleep(1)
    raise RuntimeError(f'Healthcheck timeout: {url}')

def wait_published_webhook(seconds=90):
    # n8n healthz can precede workflow activation after a restart. The owned
    # recovery hook is idempotent and only dispatches already-authorized work.
    env=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if line and not line.startswith('#'))
    deadline=time.monotonic()+seconds
    observations=[]
    while time.monotonic()<deadline:
        request=urllib.request.Request('http://127.0.0.1:5678/webhook/apic-recovery',data=b'{}',headers={'Content-Type':'application/json','X-Webhook-Token':env['N8N_WEBHOOK_TOKEN']})
        try:
            with urllib.request.urlopen(request,timeout=10) as response:
                observations.append(response.status)
                if 200<=response.status<300:
                    (ROOT/'.local/bootstrap-webhook-ready.json').write_text(json.dumps({'status':'PASS','observed_http_statuses':observations})+'\n')
                    return
        except urllib.error.HTTPError as error:
            observations.append(error.code)
            if error.code not in (404,503):raise
        except (urllib.error.URLError,TimeoutError,ConnectionError,http.client.RemoteDisconnected):
            observations.append('transport_not_ready')
        time.sleep(2)
    raise RuntimeError('Published APIC recovery webhook did not become ready')
def deploy():
    run('proxy',sys.executable,'scripts/build_workflows.py')
    compose('exec','-T','n8n','n8n','import:credentials','--input=/project/local/n8n-credentials.json')
    manifest=json.loads((ROOT/'n8n/manifest.example.json').read_text())
    backup_owned(manifest['workflows'])
    compose('exec','-T','n8n','n8n','import:workflow','--separate','--input=/project/n8n/workflows')
    for w in manifest['workflows']:
        compose('exec','-T','n8n','n8n','publish:workflow',f"--id={w['id']}")
    compose('restart','n8n','n8n-runners')
    wait('http://127.0.0.1:5678/healthz')
    wait_published_webhook()
    (ROOT/'.local/deployed-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Local workflows imported and published. Runtime acceptance tests must run separately.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--infrastructure-only',action='store_true');p.add_argument('--deploy-only',action='store_true');p.add_argument('--skip-dashboard',action='store_true');a=p.parse_args()
    run('docker','info','--format','{{.ServerVersion}}')
    run('proxy',sys.executable,'scripts/init_secrets.py')
    compose('config','--quiet')
    if a.deploy_only:deploy();return
    compose('up','-d','postgres','n8n','n8n-runners','mailpit')
    wait('http://127.0.0.1:5678/healthz')
    if a.infrastructure_only:return
    compose('build','ops-api','mock-erp','bootstrap')
    compose('run','--rm','bootstrap')
    compose('up','-d','ops-api','mock-erp')
    wait('http://127.0.0.1:8000/health/ready')
    deploy()
    if not a.skip_dashboard:
        compose('up','-d','--no-deps','--build','dashboard')
        wait('http://127.0.0.1:5173')
    wait('http://127.0.0.1:8000/health/ready')
    print('APIC local stack ready. Sign-in credentials are in .local/credentials.json; never publish this file.')
    print('An initial n8n owner setup may still be required to use the editor UI. CLI-deployed workflows do not require it to execute.')
if __name__=='__main__':main()
