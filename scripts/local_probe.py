from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
probe={'id':'APICPROBE0000001','name':'APIC | M0 | Local Runtime Probe','active':False,'nodes':[
{'id':'hook','name':'Protected Probe','type':'n8n-nodes-base.webhook','typeVersion':2.1,'position':[0,0],'webhookId':'apic-m0','parameters':{'httpMethod':'POST','path':'apic-probe','authentication':'headerAuth','responseMode':'lastNode','options':{}},'credentials':{'httpHeaderAuth':{'id':'apicWebhook001','name':'APIC Webhook Intake'}}},
{'id':'code','name':'Runner Proof','type':'n8n-nodes-base.code','typeVersion':2,'position':[300,0],'parameters':{'jsCode':"return [{json:{project:'apic-portfolio',probe:6*7,execution_id:$execution.id}}];"}}], 'connections':{'Protected Probe':{'main':[[{'node':'Runner Proof','type':'main','index':0}]]}},'settings':{'executionOrder':'v1'}}
(root/'.local/probe.json').write_text(json.dumps(probe),encoding='utf-8')
print('Local authenticated runtime probe prepared.')
