"""HTTP test client for the loopback demo; credentials never enter evidence."""
from pathlib import Path
from urllib.request import Request,build_opener,HTTPCookieProcessor
from urllib.error import HTTPError
import http.cookiejar,json,time
ROOT=Path(__file__).resolve().parents[1]
ENV=dict(x.split('=',1) for x in (ROOT/'.env').read_text().splitlines() if x and not x.startswith('#'))
class Client:
    def __init__(self,role='admin'):
        self.opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.csrf=''
        account=next(u for u in json.loads((ROOT/'.local/credentials.json').read_text())['users'] if u['role']==role)
        status,data=self.request('/api/auth/login',{'username':account['username'],'password':account['password']})
        assert status==200,(status,data)
        self.csrf=data['csrf_token'];self.scopes=data['scopes']
    def request(self,path,body=None,headers=None):
        h={'Origin':'http://127.0.0.1:5173','X-CSRF-Token':self.csrf,**(headers or {})}
        if body is not None:h['Content-Type']='application/json'
        req=Request('http://127.0.0.1:8000'+path,data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:
            with self.opener.open(req,timeout=40) as r:return r.status,json.loads(r.read())
        except HTTPError as e:
            raw=e.read().decode()
            try:raw=json.loads(raw)
            except ValueError:pass
            return e.code,raw
    def ok(self,path,body=None):
        code,data=self.request(path,body)
        assert 200<=code<300,(path,code,data)
        return data
    def poll(self,source,seconds=80):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            data=self.ok(source['status_url'])
            if data.get('job_status') in ('SUCCEEDED','MANUAL_REVIEW','DEAD_LETTER','FAILED'):
                return data
            time.sleep(1)
        raise AssertionError(('Analysis deadline',data))
def hook(path,body=None):
    req=Request('http://127.0.0.1:5678/webhook/'+path,data=json.dumps(body or {}).encode(),headers={'Content-Type':'application/json','X-Webhook-Token':ENV['N8N_WEBHOOK_TOKEN']})
    try:
        with build_opener().open(req,timeout=45) as r:
            raw=r.read();return r.status,json.loads(raw) if raw else {}
    except HTTPError as e:return e.code,e.read().decode()
