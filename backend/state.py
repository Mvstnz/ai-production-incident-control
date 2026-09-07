"""Atomic commands called separately by n8n; no hidden workflow execution."""
from datetime import timedelta
from fastapi import HTTPException

from backend.db import audit, digest, js, now, outbox, uid, utcnow
from backend.clock import SLA


def require_job(conn, stage):
    row=conn.execute("SELECT * FROM ops.analysis_jobs WHERE id=%s AND scope_id=%s FOR UPDATE",(stage["job_id"],stage["scope_id"])).fetchone()
    if not row or str(row["claim_token"]) != str(stage["claim_token"]) or row["status"] != "RUNNING" or row["lease_until"] < utcnow():
        raise HTTPException(409,"Analysis lease is stale or not owned")
    if str(row["source_event_id"]) != str(stage["source_event_id"]):
        raise HTTPException(409,"Source does not belong to claimed job")
    conn.execute("UPDATE ops.analysis_jobs SET execution_id=%s,workflow_id=%s,lease_until=%s WHERE id=%s",(stage["execution_id"],stage["workflow_id"],utcnow()+timedelta(minutes=5),row["id"]))
    return row


def stage_for(row):
    return {"schema_version":"1.0", **{k:str(row[k]) for k in ("scope_id","source_event_id","id","correlation_id","claim_token") if row.get(k)},"job_id":str(row["id"]),"execution_id":row.get("execution_id") or row.get("owner"),"workflow_id":row.get("workflow_id") or "WF03"}


def supersede(conn,sid,incident_id):
    conn.execute("""UPDATE ops.approvals SET status='SUPERSEDED' WHERE scope_id=%s AND status IN ('PENDING','APPROVED') AND plan_id IN (SELECT id FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s)""",(sid,sid,incident_id))
    conn.execute("""UPDATE ops.incident_actions SET status='CANCELLED' WHERE scope_id=%s AND status IN ('PLANNED','READY','WAITING_APPROVAL','RETRY_SCHEDULED') AND plan_id IN (SELECT id FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s)""",(sid,sid,incident_id))
    conn.execute("UPDATE ops.action_plans SET status='SUPERSEDED' WHERE scope_id=%s AND incident_id=%s AND status='CURRENT'",(sid,incident_id))


def correlate(conn,s,extraction):
    require_job(conn,s)
    sid=s["scope_id"]
    if extraction.get("status") != "VERIFIED":
        reasons=extraction.get("review_reasons") or ["Unable to verify source facts"]
        conn.execute("UPDATE ops.source_events SET status='MANUAL_REVIEW',review_reasons=%s WHERE scope_id=%s AND id=%s",(js(reasons),sid,s["source_event_id"]))
        audit(conn,sid,"SOURCE_MANUAL_REVIEW",s["source_event_id"],data={"reasons":reasons})
        return {**s,"status":"MANUAL_REVIEW","skip_analysis":True,"review_reasons":reasons}
    facts=extraction["facts"]
    key=extraction["business_key"]
    if not isinstance(key,str): key=digest(key)
    kind=extraction["incident_type"]
    conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",(f"{sid}:{kind}:{key}",))
    incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND incident_type=%s AND business_key=%s AND status NOT IN ('RESOLVED','CLOSED') FOR UPDATE",(sid,kind,key)).fetchone()
    source=conn.execute("SELECT envelope FROM ops.source_events WHERE scope_id=%s AND id=%s",(sid,s["source_event_id"])).fetchone()["envelope"]
    correction=source.get("correction_context")
    if correction and (not incident or str(incident["id"])!=correction.get("incident_id") or incident["revision"]!=correction.get("expected_revision")):
        raise HTTPException(409,"Factual correction refers to a stale incident revision")
    fingerprint=digest(facts)
    skip=False
    if incident:
        iid=incident["id"]
        old=conn.execute("SELECT fingerprint FROM ops.incident_revisions WHERE scope_id=%s AND incident_id=%s AND revision=%s",(sid,iid,incident["revision"])).fetchone()
        revision=incident["revision"]
        if old["fingerprint"] == fingerprint:
            skip=bool(conn.execute("SELECT 1 FROM ops.impact_assessments WHERE scope_id=%s AND incident_id=%s AND revision=%s",(sid,iid,revision)).fetchone())
        else:
            revision+=1
            supersede(conn,sid,iid)
            conn.execute("UPDATE ops.incidents SET revision=%s,status='ANALYZING',updated_at=%s WHERE scope_id=%s AND id=%s",(revision,now(conn,sid),sid,iid))
    else:
        iid=uid(); revision=1
        previous=conn.execute("SELECT id FROM ops.incidents WHERE scope_id=%s AND incident_type=%s AND business_key=%s ORDER BY updated_at DESC LIMIT 1",(sid,kind,key)).fetchone()
        conn.execute("""INSERT INTO ops.incidents(id,scope_id,number,incident_type,business_key,title,status,updated_at,prior_incident_id)
            VALUES (%s,%s,%s,%s,%s,%s,'ANALYZING',%s,%s)""",(iid,sid,"INC-"+str(iid)[:8].upper(),kind,key,kind.replace("_"," ").title()+" · "+key,now(conn,sid),previous["id"] if previous else None))
    conn.execute("""INSERT INTO ops.incident_revisions(id,scope_id,incident_id,revision,fingerprint,facts,evidence)
        VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(scope_id,incident_id,revision) DO NOTHING""",(uid(),sid,iid,revision,fingerprint,js(facts),js(extraction.get("evidence",[]))))
    conn.execute("INSERT INTO ops.incident_sources VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",(sid,iid,s["source_event_id"],revision))
    conn.execute("UPDATE ops.source_events SET status='VERIFIED' WHERE scope_id=%s AND id=%s",(sid,s["source_event_id"]))
    audit(conn,sid,"SOURCE_CORRELATED",iid,data={"revision":revision,"skip_analysis":skip,"source_event_id":str(s["source_event_id"])},correlation_id=s["correlation_id"])
    return {**s,"incident_id":str(iid),"revision":revision,"facts":facts,"status":"ANALYZING","skip_analysis":skip}


ACTION_ROLES={"INTERNAL_TICKET":None,"SUPPLIER_EMAIL":"purchasing","RESCHEDULE":"production_manager","QUALITY_BLOCK":"quality_manager","QUALITY_RELEASE":"quality_manager"}


def validate_actions(plan):
    actions=plan.get("actions",[])
    if len(actions)>12:
        raise HTTPException(422,"Too many actions")
    for action in actions:
        kind=action.get("action_type")
        if kind not in ACTION_ROLES:
            raise HTTPException(422,"Action type is not allowed")
        payload=action.get("payload",{})
        if not isinstance(payload,dict): raise HTTPException(422,"Invalid action payload")
        if kind=="SUPPLIER_EMAIL":
            target=payload.get("to",payload.get("recipient"))
            if target!="supplier@example.test" or not payload.get("subject") or not (payload.get("body") or payload.get("content_text")):
                raise HTTPException(422,"Email must contain an approved sandbox recipient, subject and complete text")
        action["required_role"]=(action.get("required_role") if kind=="SUPPLIER_EMAIL" and action.get("required_role") in ("purchasing","production_manager") else ACTION_ROLES[kind])
    return plan


def plan_hash(plan,revision,impact_id,version):
    return digest({"incident_revision":revision,"impact_assessment_id":str(impact_id),"plan_version":version,"policy_version":plan["policy_version"],"plan":plan})


def create_plan(conn,sid,iid,revision,impact_id,risk,plan):
    incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,iid)).fetchone()
    if not incident or incident["revision"]!=revision:
        raise HTTPException(409,"Incident revision is stale")
    plan=validate_actions(plan)
    version=conn.execute("SELECT COALESCE(max(plan_version),0)+1 AS n FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s",(sid,iid)).fetchone()["n"]
    prior=conn.execute("SELECT * FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s AND revision=%s AND status='CURRENT'",(sid,iid,revision)).fetchone()
    if prior and prior["body"]==plan:
        return plan_result(conn,sid,prior)
    if prior: supersede(conn,sid,iid)
    pid=uid(); ph=plan_hash(plan,revision,impact_id,version); clock=now(conn,sid)
    conn.execute("INSERT INTO ops.action_plans(id,scope_id,incident_id,revision,impact_assessment_id,plan_version,plan_hash,policy_version,body,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(pid,sid,iid,revision,impact_id,version,ph,plan["policy_version"],js(plan),clock))
    roles={a["required_role"] for a in plan["actions"] if a.get("required_role")}
    if risk.get("severity")=="CRITICAL":
        roles.add("quality_manager" if incident["incident_type"]=="QUALITY_ISSUE" else "production_manager")
    for required in sorted(roles):
        conn.execute("INSERT INTO ops.approvals(id,scope_id,plan_id,plan_version,plan_hash,required_role,expires_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",(uid(),sid,pid,version,ph,required,clock+timedelta(hours=SLA["approval_expiry_hours"])))
    for index,action in enumerate(plan["actions"]):
        aid=uid(); state="WAITING_APPROVAL" if action["required_role"] else "READY"
        conn.execute("""INSERT INTO ops.incident_actions(id,scope_id,plan_id,action_key,action_type,payload,required_role,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(aid,sid,pid,f"{iid}:{version}:{index}:{action['action_type']}",action["action_type"],js(action["payload"]),action["required_role"],state))
        outbox(conn,sid,f"action:{aid}","ACTION",{"scope_id":str(sid),"action_id":aid})
    if roles: outbox(conn,sid,f"plan:{pid}","PLAN",{"scope_id":str(sid),"plan_id":pid})
    state="MANUAL_REVIEW" if not risk.get("data_complete",False) else "WAITING_APPROVAL" if roles else "ACTION_IN_PROGRESS" if plan["actions"] else "MONITORING"
    conn.execute("UPDATE ops.incidents SET status=%s,risk_score=%s,severity=%s,updated_at=%s WHERE scope_id=%s AND id=%s",(state,risk.get("risk_score"),risk.get("severity"),clock,sid,iid))
    audit(conn,sid,"PLAN_CREATED",iid,data={"plan_id":pid,"plan_version":version,"plan_hash":ph})
    return plan_result(conn,sid,{"id":pid,"plan_version":version,"plan_hash":ph})


def plan_result(conn,sid,plan):
    return {"scope_id":str(sid),"plan_id":str(plan["id"]),"plan_version":plan["plan_version"],"plan_hash":plan["plan_hash"],"approval_ids":[str(r["id"]) for r in conn.execute("SELECT id FROM ops.approvals WHERE scope_id=%s AND plan_id=%s",(sid,plan["id"]))],"action_ids":[str(r["id"]) for r in conn.execute("SELECT id FROM ops.incident_actions WHERE scope_id=%s AND plan_id=%s",(sid,plan["id"]))]}


def revalidate(conn,sid,pid):
    plan=conn.execute("""SELECT p.*,i.revision AS current_revision FROM ops.action_plans p JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id) WHERE p.scope_id=%s AND p.id=%s FOR UPDATE OF p,i""",(sid,pid)).fetchone()
    if not plan: raise HTTPException(404,"Plan not found")
    if plan["status"]!="CURRENT" or plan["revision"]!=plan["current_revision"] or plan["plan_hash"]!=plan_hash(plan["body"],plan["revision"],plan["impact_assessment_id"],plan["plan_version"]):
        return {"status":"SUPERSEDED","ready_action_ids":[],"scope_id":str(sid),"plan_id":str(pid)}
    conn.execute("UPDATE ops.approvals SET status='EXPIRED' WHERE scope_id=%s AND plan_id=%s AND status='PENDING' AND expires_at<=%s",(sid,pid,now(conn,sid)))
    approvals=conn.execute("SELECT * FROM ops.approvals WHERE scope_id=%s AND plan_id=%s",(sid,pid)).fetchall()
    all_approved=all(a["status"]=="APPROVED" for a in approvals)
    if all_approved:
        conn.execute("UPDATE ops.incident_actions SET status='READY' WHERE scope_id=%s AND plan_id=%s AND status='WAITING_APPROVAL'",(sid,pid))
    ready=conn.execute("SELECT id FROM ops.incident_actions WHERE scope_id=%s AND plan_id=%s AND status='READY'",(sid,pid)).fetchall()
    failed=next((a["status"] for a in approvals if a["status"] in ("REJECTED","EXPIRED","SUPERSEDED")),None)
    return {"status":failed or ("APPROVED" if all_approved else "PENDING"),"ready_action_ids":[str(a["id"]) for a in ready],"scope_id":str(sid),"plan_id":str(pid)}
