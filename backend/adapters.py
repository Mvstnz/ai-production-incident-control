"""Local effects only. Uncertain writes never enter the automatic retry queue."""
import os
import smtplib
from datetime import timedelta
from email.message import EmailMessage

import httpx
from fastapi import HTTPException

from backend.db import audit, js, now, transaction, uid, utcnow
from backend.state import revalidate


def execute_action(body):
    with transaction() as conn:
        action=conn.execute("SELECT * FROM ops.incident_actions WHERE scope_id=%s AND id=%s FOR NO KEY UPDATE",(body.scope_id,body.action_id)).fetchone()
        if not action or str(action["claim_token"])!=str(body.claim_token): raise HTTPException(409,"Action claim is not owned")
        if action["status"] in ("SUCCEEDED","UNKNOWN_OUTCOME"): return {"action_id":str(body.action_id),"status":action["status"],"provider_id":action["provider_id"],**action["result"]}
        if action["status"]!="IN_PROGRESS" or action["lease_until"]<utcnow(): raise HTTPException(409,"Action claim expired")
        state=revalidate(conn,body.scope_id,action["plan_id"])
        if state["status"]=="SUPERSEDED" or (action["required_role"] and state["status"]!="APPROVED"):
            conn.execute("UPDATE ops.incident_actions SET status='CANCELLED' WHERE scope_id=%s AND id=%s",(body.scope_id,body.action_id))
            return {"action_id":str(body.action_id),"status":"CANCELLED"}
        failure={x["kind"] for x in conn.execute("SELECT kind FROM ops.failures WHERE scope_id=%s AND enabled",(body.scope_id,))}
        if "permanent" in failure:
            conn.execute("UPDATE ops.incident_actions SET status='FAILED',result=%s WHERE scope_id=%s AND id=%s",(js({"error_class":"PERMANENT","message":"Synthetic permanent adapter failure"}),body.scope_id,body.action_id))
            return {"action_id":str(body.action_id),"status":"FAILED"}
        payload=action["payload"]; provider_id=None; outcome="SUCCEEDED"
        previous=conn.execute("SELECT * FROM ops.provider_receipts WHERE scope_id=%s AND action_id=%s",(body.scope_id,body.action_id)).fetchone()
        if previous:
            provider_id=str(previous["id"])
        elif action["action_type"]=="INTERNAL_TICKET":
            provider_id="ticket-"+str(body.action_id)
        elif action["action_type"]=="SUPPLIER_EMAIL":
            recipient=payload.get("recipient",payload.get("to"))
            if recipient!="supplier@example.test": raise HTTPException(422,"Recipient is not in sandbox allowlist")
            host=os.getenv("MAILPIT_HOST","mailpit")
            if host not in ("mailpit","localhost","127.0.0.1","::1"): raise HTTPException(503,"Only local Mailpit transport is implemented")
            message=EmailMessage(); message["From"]="operations@example.test"; message["To"]=recipient
            message["Subject"]=payload["subject"]; message["Message-ID"]=f"<apic-{body.action_id}@example.test>"
            message.set_content(payload.get("body",payload.get("content_text","")))
            try:
                with smtplib.SMTP(host,int(os.getenv("SMTP_PORT","1025")),timeout=8) as smtp: smtp.send_message(message)
                provider_id=str(message["Message-ID"])
            except (TimeoutError,OSError,smtplib.SMTPException):
                # The SMTP response may have been lost after acceptance. No blind retry.
                outcome="UNKNOWN_OUTCOME"
        elif action["action_type"] in ("RESCHEDULE","QUALITY_BLOCK","QUALITY_RELEASE"):
            command={"RESCHEDULE":"reschedule","QUALITY_BLOCK":"quality-block","QUALITY_RELEASE":"quality-release"}[action["action_type"]]
            try:
                response=httpx.post(os.getenv("ERP_BASE_URL","http://mock-erp:8001")+"/erp/v1/commands/"+command,headers={"X-ERP-Token":os.getenv("ERP_WRITE_TOKEN","")},json={"scope_id":str(body.scope_id),"action_id":str(body.action_id),"claim_token":str(body.claim_token),"payload":payload},timeout=15)
                if response.status_code==200: provider_id=response.json()["provider_id"]
                else: outcome="FAILED" if response.status_code<500 else "UNKNOWN_OUTCOME"
            except httpx.RequestError: outcome="UNKNOWN_OUTCOME"
        else: raise HTTPException(422,"Unsupported action adapter")
        if provider_id and not previous:
            conn.execute("INSERT INTO ops.provider_receipts(id,scope_id,action_id,provider,payload) VALUES (%s,%s,%s,%s,%s) ON CONFLICT(scope_id,action_id) DO NOTHING",(uid(),body.scope_id,body.action_id,action["action_type"],js({"provider_id":provider_id,"synthetic":True})))
        if "write-timeout" in failure and provider_id:
            outcome="UNKNOWN_OUTCOME"
        result={"synthetic":True,"provider_id":provider_id,"reconciliation_required":outcome=="UNKNOWN_OUTCOME"}
        conn.execute("UPDATE ops.incident_actions SET status=%s,provider_id=%s,result=%s,lease_until=NULL,completed_at=%s WHERE scope_id=%s AND id=%s",(outcome,provider_id,js(result),now(conn,body.scope_id),body.scope_id,body.action_id))
        audit(conn,body.scope_id,"ACTION_"+outcome,body.action_id,data={"provider_id":provider_id,"execution_id":body.execution_id,"workflow_id":body.workflow_id})
        plan=conn.execute("SELECT incident_id FROM ops.action_plans WHERE scope_id=%s AND id=%s",(body.scope_id,action["plan_id"])).fetchone()
        remaining=conn.execute("SELECT 1 FROM ops.incident_actions WHERE scope_id=%s AND plan_id=%s AND status NOT IN ('SUCCEEDED','CANCELLED')",(body.scope_id,action["plan_id"])).fetchone()
        if not remaining:
            conn.execute("UPDATE ops.incidents SET status='MONITORING',updated_at=%s WHERE scope_id=%s AND id=%s AND status NOT IN ('MANUAL_REVIEW','RESOLVED','CLOSED')",(now(conn,body.scope_id),body.scope_id,plan["incident_id"]))
        return {"action_id":str(body.action_id),"status":outcome,**result}
