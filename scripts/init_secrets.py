"""Create local random credentials once; never print values."""
from pathlib import Path
import secrets
import json
ROOT = Path(__file__).resolve().parents[1]
def main():
    local = ROOT / '.local'
    local.mkdir(exist_ok=True)
    env_path = ROOT / '.env'
    if not env_path.exists():
        names = ['DB_OWNER_PASSWORD','DB_APP_PASSWORD','DB_ERP_PASSWORD','DB_N8N_PASSWORD','SERVICE_TOKEN','ERP_READ_TOKEN','ERP_WRITE_TOKEN','SESSION_SECRET','N8N_WEBHOOK_TOKEN','N8N_ENCRYPTION_KEY','RUNNER_TOKEN']
        env = {name:secrets.token_hex(32) for name in names}
        env.update(PROFILE='DEMO_LOCAL',EXTERNAL_ACTIONS_ENABLED='false',AI_MODE='fixture')
        env_path.write_text('\n'.join(f'{k}={v}' for k,v in env.items())+'\n',encoding='utf-8')
    env = dict(line.split('=',1) for line in env_path.read_text().splitlines() if line and not line.startswith('#'))
    credentials_path = local/'credentials.json'
    if not credentials_path.exists():
        users = [{'username':role,'role':role,'password':secrets.token_urlsafe(24)} for role in ['viewer','operator','purchasing','production_manager','quality_manager','admin']]
        credentials_path.write_text(json.dumps({'users':users},indent=2)+'\n',encoding='utf-8')
    headers = [('apicOpsService01','APIC Operations Service','X-Service-Token','SERVICE_TOKEN'),('apicErpRead0001','APIC ERP Read','X-ERP-Token','ERP_READ_TOKEN'),('apicWebhook001','APIC Webhook Intake','X-Webhook-Token','N8N_WEBHOOK_TOKEN')]
    n8n = [{'id':cid,'name':name,'type':'httpHeaderAuth','data':{'name':header,'value':env[key]}} for cid,name,header,key in headers]
    n8n.append({'id':'apicForm000001','name':'APIC Demo Form','type':'httpBasicAuth','data':{'user':'apic-form','password':env['N8N_WEBHOOK_TOKEN']}})
    (local/'n8n-credentials.json').write_text(json.dumps(n8n),encoding='utf-8')
    print('Local secrets ready; existing secrets preserved. Credentials: .local/credentials.json (do not commit).')
if __name__ == '__main__': main()
