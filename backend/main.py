"""Operations API: authenticated boundaries and atomic state commands for n8n."""
import json
import logging
import os
import random
import re
import secrets
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, urlparse
from uuid import UUID
from zoneinfo import ZoneInfo

import httpx
import psycopg
from argon2.exceptions import VerificationError
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import AwareDatetime

from backend.db import audit, canonical, digest, js, now, outbox, transaction, uid, utcnow
from backend.domain import aggregate_values, build_plan, evaluate_impact, evaluate_risk, extract_fixture, verify_live_extraction
from backend.models import ActionCommand, Claim, CustomEmail, Decision, Demo, DraftInput, Envelope, ExtractInput, ImpactInput, LiveExtractionInput, Login, PlanContext, RiskInput, Stage
from backend.security import BodyLimitMiddleware, hashed, origin, passwords, rate_limit, role, safe_message, scope, service, user
from backend.seed import fixture
from backend.datasets import dataset_name, demo_clock, demo_timezone
from backend.clock import SLA, add_business_hours
from backend.state import correlate, create_plan, plan_result, require_job, revalidate, stage_for, supersede

app=FastAPI(title="AI Production Incident Control",version="1.0.0",description="Synthetic demo. n8n orchestrates; API commands persist atomic state.")
app.add_middleware(BodyLimitMiddleware)
log=logging.getLogger("apic")


def notify_recovery():
    """Wake n8n after committed work; the scheduled recovery remains the fallback."""
    url=os.getenv("N8N_RECOVERY_URL")
    if not url: return
    try:
        response=httpx.post(url,json={},headers={"X-Webhook-Token":os.getenv("N8N_WEBHOOK_TOKEN","")},timeout=10)
        response.raise_for_status()
    except httpx.HTTPError:
        log.warning("n8n recovery wakeup deferred to scheduled recovery")


@app.exception_handler(HTTPException)
async def http_error(request,error):
    return JSONResponse({"error_code":f"HTTP_{error.status_code}","message":safe_message(error.detail),"retryable":error.status_code in (429,503),"correlation_id":request.headers.get("x-correlation-id")},status_code=error.status_code,headers=error.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request,error):
    return JSONResponse({"error_code":"VALIDATION_ERROR","message":"Invalid request fields","retryable":False,"field_errors":[{"loc":x["loc"],"type":x["type"]} for x in error.errors()]},422)


@app.exception_handler(psycopg.OperationalError)
async def database_unavailable(request,error):
    log.error(json.dumps({"event":"database_unavailable","path":request.url.path,"retryable":True}))
    return JSONResponse({"error_code":"DATABASE_UNAVAILABLE","message":"Database unavailable; no acceptance was committed","retryable":True},503)


@app.get("/health/live")
def live(): return {"status":"alive","version":"1.0.0"}


@app.get("/health/ready")
def ready():
    with transaction() as conn:
        migration=conn.execute("SELECT version FROM ops.schema_migrations ORDER BY version DESC LIMIT 1").fetchone()
        if not migration: raise HTTPException(503,"Migration missing")
    return {"status":"ready","schema":migration["version"]}


@app.post("/api/auth/login")
def login(body:Login,request:Request,response:Response):
    origin(request); rate_limit(request)
    with transaction() as conn:
        found=conn.execute("SELECT * FROM ops.users WHERE username=%s",(body.username,)).fetchone()
        try: valid=found and passwords.verify(found["password_hash"],body.password)
        except VerificationError: valid=False
        if not valid: raise HTTPException(401,"Invalid username or password")
        raw,csrf=secrets.token_urlsafe(48),secrets.token_urlsafe(32)
        conn.execute("INSERT INTO ops.sessions VALUES (%s,%s,%s,%s)",(hashed(raw),found["id"],hashed(csrf),utcnow()+timedelta(hours=8)))
        scopes=conn.execute("SELECT s.id,s.name FROM ops.scopes s JOIN ops.memberships m ON m.scope_id=s.id WHERE m.user_id=%s ORDER BY s.created_at",(found["id"],)).fetchall()
    response.set_cookie("apic_session",raw,max_age=8*3600,httponly=True,samesite="strict",secure=os.getenv("COOKIE_SECURE","false")=="true",path="/api")
    return {"user":{k:found[k] for k in ("id","username","role")},"csrf_token":csrf,"scopes":scopes}


@app.post("/api/auth/demo")
def public_demo(request:Request,response:Response):
    """A public visitor can only read the explicitly published synthetic scope."""
    if os.getenv("PUBLIC_DEMO_ENABLED","false") != "true":
        raise HTTPException(404,"Public demo is not enabled")
    origin(request); rate_limit(request,"public-demo",20)
    from backend.bootstrap import DEFAULT_SCOPE
    with transaction() as conn:
        found=conn.execute("SELECT id,username,role FROM ops.users WHERE username='public_viewer' AND role='viewer'").fetchone()
        if not found: raise HTTPException(503,"Public demo is being prepared")
        raw,csrf=secrets.token_urlsafe(48),secrets.token_urlsafe(32)
        conn.execute("DELETE FROM ops.sessions WHERE user_id=%s AND expires_at<%s",(found["id"],utcnow()))
        conn.execute("INSERT INTO ops.sessions VALUES (%s,%s,%s,%s)",(hashed(raw),found["id"],hashed(csrf),utcnow()+timedelta(hours=2)))
        available=conn.execute("SELECT s.id,s.name FROM ops.scopes s JOIN ops.memberships m ON m.scope_id=s.id WHERE m.user_id=%s AND s.id=%s",(found["id"],DEFAULT_SCOPE)).fetchall()
    response.set_cookie("apic_session",raw,max_age=7200,httponly=True,samesite="strict",secure=os.getenv("COOKIE_SECURE","false")=="true",path="/api")
    return {"user":found,"csrf_token":csrf,"scopes":available}


@app.get("/api/demo/catalog")
def demo_catalog():
    data=fixture("SUPPLIER_DELAY")
    return {"dataset":dataset_name(),"timezone":demo_timezone(),"public_demo_enabled":os.getenv("PUBLIC_DEMO_ENABLED","false")=="true","live_ai_enabled":live_ai_config()[0],"source_email":data["source_email"]}


@app.get("/api/auth/me")
def me(request:Request,actor=Depends(user)):
    csrf=secrets.token_urlsafe(32)
    with transaction() as conn:
        conn.execute("UPDATE ops.sessions SET csrf_hash=%s WHERE token_hash=%s",(hashed(csrf),hashed(request.cookies["apic_session"])))
        available=conn.execute("SELECT s.id,s.name FROM ops.scopes s JOIN ops.memberships m ON m.scope_id=s.id WHERE m.user_id=%s ORDER BY s.created_at DESC",(actor["id"],)).fetchall()
    return {"user":{k:actor[k] for k in ("id","username","role")},"csrf_token":csrf,"scopes":available}


@app.post("/api/auth/logout")
def logout(request:Request,response:Response,actor=Depends(user)):
    with transaction() as conn: conn.execute("DELETE FROM ops.sessions WHERE token_hash=%s",(hashed(request.cookies.get("apic_session","")),))
    response.delete_cookie("apic_session",path="/api")
    return {"status":"logged_out"}


@app.get("/api/scopes")
def scopes(actor=Depends(user)):
    with transaction() as conn:
        return {"items":conn.execute("SELECT s.id,s.name,s.clock_at AS clock,s.synthetic FROM ops.scopes s JOIN ops.memberships m ON m.scope_id=s.id WHERE m.user_id=%s ORDER BY s.created_at DESC",(actor["id"],)).fetchall()}


@app.post("/internal/source-events",status_code=202,dependencies=[Depends(service)])
def ingest(body:Envelope):
    envelope=body.model_dump(mode="json")
    # Correlation/receipt time are transport metadata, not source content identity.
    payload_hash=digest({k:v for k,v in envelope.items() if k not in ("correlation_id","received_at")})
    with transaction() as conn:
        now(conn,body.scope_id)
        eid=uid()
        found=conn.execute("""INSERT INTO ops.source_events(id,scope_id,source,source_account_id,source_id,payload_hash,envelope,received_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(scope_id,source,source_account_id,source_id) DO NOTHING RETURNING *""",
            (eid,body.scope_id,body.source,body.source_account_id,body.source_id,payload_hash,js(envelope),body.received_at)).fetchone()
        duplicate=not found
        if not found:
            found=conn.execute("SELECT * FROM ops.source_events WHERE scope_id=%s AND source=%s AND source_account_id=%s AND source_id=%s FOR UPDATE",(body.scope_id,body.source,body.source_account_id,body.source_id)).fetchone()
            if found["payload_hash"]!=payload_hash: raise HTTPException(409,"Source ID already exists with different content")
        conn.execute("""INSERT INTO ops.analysis_jobs(id,scope_id,source_event_id,correlation_id) VALUES (%s,%s,%s,%s) ON CONFLICT(scope_id,source_event_id) DO NOTHING""",(uid(),body.scope_id,found["id"],body.correlation_id))
        job=conn.execute("SELECT * FROM ops.analysis_jobs WHERE scope_id=%s AND source_event_id=%s",(body.scope_id,found["id"])).fetchone()
        if not duplicate: audit(conn,body.scope_id,"SOURCE_ACCEPTED",found["id"],data={"source":body.source},correlation_id=body.correlation_id)
        return {"source_event_id":str(found["id"]),"job_id":str(job["id"]),"scope_id":str(body.scope_id),"correlation_id":str(job["correlation_id"]),"status_url":f"/api/source-events/{found['id']}?scope_id={body.scope_id}","duplicate":duplicate}


@app.post("/internal/jobs/claim",dependencies=[Depends(service)])
def claim_jobs(body:Claim):
    with transaction() as conn:
        rows=conn.execute("""SELECT * FROM ops.analysis_jobs WHERE status IN ('PENDING','RETRY_SCHEDULED') AND next_attempt_at<=%s AND attempts<4 AND (%s::uuid IS NULL OR id=%s) ORDER BY next_attempt_at LIMIT %s FOR UPDATE SKIP LOCKED""",(utcnow(),body.job_id,body.job_id,body.limit)).fetchall()
        result=[]
        for row in rows:
            row=conn.execute("""UPDATE ops.analysis_jobs SET status='RUNNING',attempts=attempts+1,claim_token=%s,lease_until=%s,owner=%s,execution_id=%s,workflow_id=%s WHERE id=%s RETURNING *""",(uid(),utcnow()+timedelta(minutes=5),body.owner,body.execution_id,body.workflow_id,row["id"])).fetchone()
            result.append(stage_for(row))
        return {"items":result}


def erp_call(path,payload=None,write=False):
    headers={"X-ERP-Token":os.getenv("ERP_WRITE_TOKEN" if write else "ERP_READ_TOKEN","")}
    url=os.getenv("ERP_BASE_URL","http://mock-erp:8001")+path
    try:
        response=httpx.post(url,headers=headers,json=payload,timeout=15) if payload is not None else httpx.get(url,headers=headers,timeout=15)
    except httpx.RequestError: raise HTTPException(503,"Mock ERP is unreachable")
    if response.status_code>=400:
        raise HTTPException(response.status_code,"Mock ERP rejected request",headers={"Retry-After":response.headers.get("Retry-After","5")})
    return response.json()


@app.post("/internal/jobs/context",dependencies=[Depends(service)])
def context(body:Stage):
    s=body.model_dump(mode="json",exclude_none=True)
    with transaction() as conn:
        require_job(conn,s)
        envelope=conn.execute("SELECT envelope FROM ops.source_events WHERE scope_id=%s AND id=%s",(body.scope_id,body.source_event_id)).fetchone()["envelope"]
    kind=(envelope.get("payload") or {}).get("incident_type","SUPPLIER_DELAY")
    if kind not in ("SUPPLIER_DELAY","MACHINE_BREAKDOWN","QUALITY_ISSUE"): kind="SUPPLIER_DELAY"
    try:
        snapshot=erp_call("/erp/v1/snapshots",{"scope_id":str(body.scope_id),"incident_type":kind,"revision":1})
    except HTTPException as error:
        # Persist provider retry metadata before n8n's generic Error Trigger can
        # discard response headers. The API owns this atomic lease transition;
        # the n8n monitor still orchestrates the later retry.
        retry_after=(error.headers or {}).get("Retry-After")
        try: retry_after=max(0,int(retry_after)) if retry_after is not None else None
        except (TypeError,ValueError): retry_after=None
        failure={**s,"error_class":"TRANSIENT" if error.status_code==429 or error.status_code>=500 else "PERMANENT","message":f"Mock ERP snapshot request returned HTTP {error.status_code}","retry_after":retry_after}
        with transaction() as conn: fail_job(conn,failure)
        raise
    return {**s,"envelope":envelope,"snapshot":snapshot,"snapshot_id":snapshot["snapshot_id"]}


@app.post("/internal/extract",dependencies=[Depends(service)])
def extract(body:ExtractInput): return extract_fixture(body.envelope,body.snapshot)


def live_ai_config():
    try: limit=int(os.getenv("LLM_MAX_CALLS","0"))
    except ValueError: limit=0
    model=os.getenv("LLM_MODEL","").strip()
    enabled=os.getenv("AI_MODE","fixture")=="live" and bool(model) and limit>0
    return enabled,model,max(0,limit)


@app.post("/internal/extract/live/prepare",dependencies=[Depends(service)])
def prepare_live_extract(body:Stage):
    enabled,model,limit=live_ai_config()
    if not enabled: raise HTTPException(503,"Live AI is disabled or missing a bounded model configuration")
    data=body.model_dump(mode="json",exclude_none=True)
    envelope=data.get("envelope")
    if not isinstance(envelope,dict) or envelope.get("source")!="EMAIL" or envelope.get("ai_mode")!="live":
        raise HTTPException(422,"Live AI requires an EMAIL envelope explicitly marked ai_mode=live")
    with transaction() as conn:
        require_job(conn,data)
        conn.execute("SELECT pg_advisory_xact_lock(hashtext('apic:live-ai-budget'))")
        existing=conn.execute("SELECT model FROM ops.live_ai_calls WHERE job_id=%s AND execution_id=%s",(body.job_id,body.execution_id)).fetchone()
        used=conn.execute("SELECT count(*) AS count FROM ops.live_ai_calls").fetchone()["count"]
        if not existing:
            if used>=limit: raise HTTPException(429,"The configured live AI call budget is exhausted")
            conn.execute("INSERT INTO ops.live_ai_calls(job_id,execution_id,scope_id,model) VALUES (%s,%s,%s,%s)",(body.job_id,body.execution_id,body.scope_id,model))
            used+=1
    return {**data,"llm_model":existing["model"] if existing else model,"llm_calls_used":used,"llm_calls_limit":limit}


@app.post("/internal/extract/live/verify",dependencies=[Depends(service)])
def verify_live_extract(body:LiveExtractionInput):
    configured,model,_=live_ai_config()
    if not configured or body.model!=model: raise HTTPException(409,"Live AI model does not match the bounded runtime configuration")
    return verify_live_extraction(body.envelope,body.snapshot,body.candidate,body.model,
        body.response_metadata.model_dump(mode="json",exclude_none=False))


@app.post("/internal/incidents/correlate",dependencies=[Depends(service)])
def correlate_source(body:Stage):
    s=body.model_dump(mode="json",exclude_none=True)
    with transaction() as conn: return correlate(conn,s,s["extraction"])


@app.post("/internal/impact/evaluate",dependencies=[Depends(service)])
def impact(body:ImpactInput): return evaluate_impact(body.snapshot,body.facts)


@app.post("/internal/impact/save",dependencies=[Depends(service)])
def save_impact(body:Stage):
    s=body.model_dump(mode="json",exclude_none=True); assessment=s["impact"]
    with transaction() as conn:
        require_job(conn,s)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s FOR UPDATE",(body.scope_id,body.incident_id)).fetchone()
        snapshot=conn.execute("SELECT * FROM erp.snapshots WHERE scope_id=%s AND id=%s",(body.scope_id,body.snapshot_id)).fetchone()
        if not incident or incident["revision"]!=body.revision or not snapshot or str(assessment.get("snapshot_id"))!=str(body.snapshot_id) or str(assessment.get("scope_id"))!=str(body.scope_id) or assessment.get("erp_revision")!=snapshot["erp_revision"]:
            raise HTTPException(409,"Stale revision or mismatched ERP snapshot")
        facts=conn.execute("SELECT facts FROM ops.incident_revisions WHERE scope_id=%s AND incident_id=%s AND revision=%s",(body.scope_id,body.incident_id,body.revision)).fetchone()["facts"]
        verified=evaluate_impact(snapshot["body"],facts)
        if verified!=assessment: raise HTTPException(409,"Assessment differs from authoritative pure calculation")
        existing=conn.execute("SELECT * FROM ops.impact_assessments WHERE scope_id=%s AND incident_id=%s AND revision=%s",(body.scope_id,body.incident_id,body.revision)).fetchone()
        if existing:
            if existing["body"]!=assessment: raise HTTPException(409,"Revision already has an immutable assessment from another snapshot; create a new revision for reassessment")
            return {**s,"impact_assessment_id":str(existing["id"])}
        result=conn.execute("""INSERT INTO ops.impact_assessments(id,scope_id,incident_id,revision,snapshot_id,method_version,body) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(scope_id,incident_id,revision) DO NOTHING RETURNING id""",(uid(),body.scope_id,body.incident_id,body.revision,body.snapshot_id,assessment["method_version"],js(assessment))).fetchone()
        if not result: result=conn.execute("SELECT id FROM ops.impact_assessments WHERE scope_id=%s AND incident_id=%s AND revision=%s",(body.scope_id,body.incident_id,body.revision)).fetchone()
        for line,value in assessment.get("sales_line_values",{}).items():
            if line in assessment.get("affected_sales_lines",[]): conn.execute("INSERT INTO ops.incident_impacts VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",(body.scope_id,result["id"],line,value))
        conn.execute("UPDATE ops.incidents SET current_impact_id=%s,affected_open_order_value_cents=%s,status=%s,updated_at=%s WHERE scope_id=%s AND id=%s",(result["id"],assessment.get("affected_open_order_value_cents") or 0,"ASSESSED" if assessment["data_complete"] else "MANUAL_REVIEW",now(conn,body.scope_id),body.scope_id,body.incident_id))
        audit(conn,body.scope_id,"IMPACT_SAVED",body.incident_id,data={"revision":body.revision,"snapshot_id":str(body.snapshot_id),"impact_assessment_id":str(result["id"])},correlation_id=body.correlation_id)
        return {**s,"impact_assessment_id":str(result["id"])}


@app.post("/internal/risk/evaluate",dependencies=[Depends(service)])
def risk(body:RiskInput): return evaluate_risk(body.impact)


@app.post("/internal/plans/draft",dependencies=[Depends(service)])
def draft(body:DraftInput): return build_plan(body.impact,body.risk,body.incident_id,body.revision)


@app.post("/internal/plans",dependencies=[Depends(service)])
def plan(body:Stage):
    s=body.model_dump(mode="json",exclude_none=True)
    with transaction() as conn:
        require_job(conn,s)
        assessment=conn.execute("SELECT * FROM ops.impact_assessments WHERE scope_id=%s AND id=%s AND incident_id=%s AND revision=%s",(body.scope_id,s["impact_assessment_id"],body.incident_id,body.revision)).fetchone()
        if not assessment: raise HTTPException(409,"Impact is not part of this revision")
        computed=evaluate_risk(assessment["body"])
        if computed!=s["risk"]: raise HTTPException(409,"Risk differs from the versioned policy")
        grounded=build_plan(assessment["body"],computed,str(body.incident_id),body.revision)
        # AI prose/parameters cannot bypass the deterministic fact/recipient gate.
        if grounded!=s["plan"]: s["plan"]=grounded
        conn.execute("INSERT INTO ops.risk_assessments VALUES (%s,%s,%s,%s,%s) ON CONFLICT(scope_id,impact_id) DO NOTHING",(uid(),body.scope_id,assessment["id"],computed["policy_version"],js(computed)))
        return {**s,**create_plan(conn,body.scope_id,body.incident_id,body.revision,assessment["id"],computed,s["plan"])}


@app.post("/internal/jobs/complete",dependencies=[Depends(service)])
def complete(body:Stage,background_tasks:BackgroundTasks):
    background_tasks.add_task(notify_recovery)
    s=body.model_dump(mode="json",exclude_none=True)
    with transaction() as conn:
        row=conn.execute("SELECT * FROM ops.analysis_jobs WHERE scope_id=%s AND id=%s FOR UPDATE",(body.scope_id,body.job_id)).fetchone()
        if row and row["status"]=="SUCCEEDED" and str(row["claim_token"])==str(body.claim_token): return {**s,"status":"SUCCEEDED"}
        require_job(conn,s)
        conn.execute("UPDATE ops.analysis_jobs SET status='SUCCEEDED',result=%s,lease_until=NULL WHERE scope_id=%s AND id=%s",(js(s.get("result",{"incident_id":s.get("incident_id"),"revision":s.get("revision")})),body.scope_id,body.job_id))
        return {**s,"status":"SUCCEEDED"}


def fail_job(conn,s):
    row=require_job(conn,s); cls=s.get("error_class","PERMANENT")
    retry=cls=="TRANSIENT" and row["attempts"]<4
    delay=max(int(s.get("retry_after") or 0),[5,30,120,120][row["attempts"]-1])+random.Random(str(row["id"])+str(row["attempts"])).uniform(0,1)
    due=utcnow()+timedelta(seconds=delay)
    conn.execute("UPDATE ops.analysis_jobs SET status=%s,next_attempt_at=%s,last_error=%s,lease_until=NULL WHERE scope_id=%s AND id=%s",("RETRY_SCHEDULED" if retry else "DEAD_LETTER",due,safe_message(s.get("message","Workflow failure")),s["scope_id"],s["job_id"]))
    eid=uid()
    conn.execute("INSERT INTO ops.workflow_errors(id,scope_id,job_id,execution_id,workflow_id,error_class,message,retryable,dead_letter,next_attempt_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(eid,s["scope_id"],s["job_id"],s["execution_id"],s["workflow_id"],cls,safe_message(s.get("message","Workflow failure")),cls=="TRANSIENT",not retry,due if retry else None))
    audit(conn,s["scope_id"],"JOB_RETRY" if retry else "JOB_DEAD_LETTER",s["job_id"],data={"attempt":row["attempts"],"error_class":cls})
    return {"status":"RETRY_SCHEDULED" if retry else "DEAD_LETTER","error_id":eid,"next_attempt_at":due if retry else None}


@app.post("/internal/jobs/fail",dependencies=[Depends(service)])
def fail(body:Stage):
    with transaction() as conn: return fail_job(conn,body.model_dump(mode="json",exclude_none=True))


@app.post("/internal/approvals/context",dependencies=[Depends(service)])
def approval_context(body:PlanContext):
    with transaction() as conn:
        state=revalidate(conn,body.scope_id,body.plan_id)
        conn.execute("UPDATE ops.outbox_events SET status='DELIVERED',lease_until=%s WHERE scope_id=%s AND event_key=%s",(utcnow()+timedelta(minutes=2),body.scope_id,"plan:"+str(body.plan_id)))
        return {**plan_result(conn,body.scope_id,{"id":body.plan_id,"plan_version":0,"plan_hash":""}),**state}


@app.post("/internal/approvals/register-wait",dependencies=[Depends(service)])
def register_wait(body:PlanContext):
    parsed=urlparse(body.resume_url or "")
    allowed=urlparse(os.getenv("N8N_ALLOWED_RESUME_ORIGIN",os.getenv("N8N_BASE_URL","http://n8n:5678")))
    query=parse_qsl(parsed.query,keep_blank_values=True)
    signed_query=(len(query)==1 and query[0][0]=="signature" and re.fullmatch(r"[A-Za-z0-9._~-]{16,2048}",query[0][1]) is not None)
    exact_path=(re.fullmatch(r"[A-Za-z0-9_-]{1,100}",body.execution_id) is not None and parsed.path==f"/webhook-waiting/{body.execution_id}")
    if (parsed.scheme,parsed.netloc)!=(allowed.scheme,allowed.netloc) or not exact_path or not signed_query or parsed.fragment or parsed.username:
        raise HTTPException(422,"Resume URL is not an allowed n8n Wait endpoint")
    with transaction() as conn:
        state=revalidate(conn,body.scope_id,body.plan_id)
        conn.execute("""INSERT INTO ops.wait_registrations(scope_id,plan_id,execution_id,workflow_id,resume_url) VALUES (%s,%s,%s,%s,%s) ON CONFLICT(scope_id,plan_id) DO UPDATE SET execution_id=EXCLUDED.execution_id,workflow_id=EXCLUDED.workflow_id,resume_url=EXCLUDED.resume_url,registered_at=now()""",(body.scope_id,body.plan_id,body.execution_id,body.workflow_id,body.resume_url))
        if state["status"]!="PENDING": outbox(conn,body.scope_id,f"wake:{body.plan_id}:{body.execution_id}","WAKEUP",{"scope_id":str(body.scope_id),"plan_id":str(body.plan_id)})
        return state


@app.post("/internal/approvals/revalidate",dependencies=[Depends(service)])
def recheck(body:PlanContext):
    with transaction() as conn: return revalidate(conn,body.scope_id,body.plan_id)


@app.post("/internal/actions/claim",dependencies=[Depends(service)])
def claim_action(body:ActionCommand):
    with transaction() as conn:
        row=conn.execute("SELECT * FROM ops.incident_actions WHERE scope_id=%s AND id=%s FOR UPDATE",(body.scope_id,body.action_id)).fetchone()
        if not row: raise HTTPException(404,"Action not found")
        state=revalidate(conn,body.scope_id,row["plan_id"])
        row=conn.execute("SELECT * FROM ops.incident_actions WHERE scope_id=%s AND id=%s",(body.scope_id,body.action_id)).fetchone()
        allowed=row["status"] in ("READY","RETRY_SCHEDULED") and row["next_attempt_at"]<=utcnow() and row["attempts"]<4 and state["status"]!="SUPERSEDED" and (not row["required_role"] or state["status"]=="APPROVED")
        if not allowed: return {"scope_id":str(body.scope_id),"action_id":str(body.action_id),"status":row["status"],"can_execute":False}
        claim=uid()
        conn.execute("UPDATE ops.incident_actions SET status='IN_PROGRESS',claim_token=%s,lease_until=%s,attempts=attempts+1,execution_id=%s,workflow_id=%s WHERE scope_id=%s AND id=%s",(claim,utcnow()+timedelta(minutes=2),body.execution_id,body.workflow_id,body.scope_id,body.action_id))
        conn.execute("UPDATE ops.outbox_events SET status='DELIVERED' WHERE scope_id=%s AND event_key=%s",(body.scope_id,"action:"+str(body.action_id)))
        audit(conn,body.scope_id,"ACTION_CLAIMED",body.action_id,data={"execution_id":body.execution_id,"workflow_id":body.workflow_id})
        return {"scope_id":str(body.scope_id),"action_id":str(body.action_id),"claim_token":claim,"action_type":row["action_type"],"payload":row["payload"],"can_execute":True,"status":"IN_PROGRESS"}


@app.post("/internal/actions/execute",dependencies=[Depends(service)])
def execute(body:ActionCommand):
    from backend.adapters import execute_action
    return execute_action(body)


def dashboard(conn,sid,updated_after=None,updated_before=None):
    bounds=" AND (%s::timestamptz IS NULL OR i.updated_at>=%s) AND (%s::timestamptz IS NULL OR i.updated_at<=%s)"
    args=(sid,updated_after,updated_after,updated_before,updated_before)
    incidents=conn.execute("SELECT i.* FROM ops.incidents i WHERE i.scope_id=%s AND i.status NOT IN ('RESOLVED','CLOSED')"+bounds,args).fetchall()
    impacts=conn.execute("SELECT a.body FROM ops.impact_assessments a JOIN ops.incidents i ON (i.scope_id,i.current_impact_id)=(a.scope_id,a.id) WHERE i.scope_id=%s AND i.status NOT IN ('RESOLVED','CLOSED')"+bounds,args).fetchall()
    value=aggregate_values([x["body"] for x in impacts])
    pending=conn.execute("SELECT count(*) AS n FROM ops.approvals WHERE scope_id=%s AND status='PENDING'",(sid,)).fetchone()["n"]
    sla=conn.execute("SELECT count(*) AS n FROM ops.outbox_events WHERE scope_id=%s AND kind='SLA'",(sid,)).fetchone()["n"]
    live,_,_=live_ai_config()
    return {"open_incidents":len(incidents),"critical_incidents":sum(i["severity"]=="CRITICAL" for i in incidents),"affected_open_order_value_cents":value["affected_open_order_value_cents"],"pending_approvals":pending,"sla_breaches":sla,"currency":"EUR","clock":now(conn,sid),"timezone":demo_timezone(),"ai_mode":"Live Gemini + verified facts" if live else "Simulated AI","profile":os.getenv("PROFILE","DEMO_LOCAL"),"aggregation":"union of unique open sales positions"}


@app.get("/api/dashboard")
def kpis(scope_id:UUID,updated_after:AwareDatetime|None=None,updated_before:AwareDatetime|None=None,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        return dashboard(conn,scope_id,updated_after,updated_before)


@app.get("/api/incidents")
def incidents(scope_id:UUID,type:str|None=None,severity:str|None=None,status:str|None=None,updated_after:AwareDatetime|None=None,updated_before:AwareDatetime|None=None,offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=200),actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        where="scope_id=%s AND (%s::text IS NULL OR incident_type=%s) AND (%s::text IS NULL OR severity=%s) AND (%s::text IS NULL OR status=%s) AND (%s::timestamptz IS NULL OR updated_at>=%s) AND (%s::timestamptz IS NULL OR updated_at<=%s)"
        args=(scope_id,type,type,severity,severity,status,status,updated_after,updated_after,updated_before,updated_before)
        total=conn.execute("SELECT count(*) AS n FROM ops.incidents WHERE "+where,args).fetchone()["n"]
        items=conn.execute("SELECT * FROM ops.incidents WHERE "+where+" ORDER BY updated_at DESC LIMIT %s OFFSET %s",(*args,limit,offset)).fetchall()
        return {"items":items,"total":total}


@app.get("/api/incidents/{incident_id}")
def detail(incident_id:UUID,scope_id:UUID,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s",(scope_id,incident_id)).fetchone()
        if not incident: raise HTTPException(404,"Incident not found")
        impact=conn.execute("SELECT body FROM ops.impact_assessments WHERE scope_id=%s AND id=%s",(scope_id,incident["current_impact_id"])).fetchone()
        risk=conn.execute("SELECT body FROM ops.risk_assessments WHERE scope_id=%s AND impact_id=%s",(scope_id,incident["current_impact_id"])).fetchone()
        plans=conn.execute("SELECT * FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s ORDER BY plan_version DESC",(scope_id,incident_id)).fetchall()
        actions=conn.execute("SELECT a.* FROM ops.incident_actions a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) WHERE p.scope_id=%s AND p.incident_id=%s ORDER BY p.plan_version",(scope_id,incident_id)).fetchall()
        for a in actions: a.pop("claim_token",None)
        approvals=conn.execute("SELECT a.* FROM ops.approvals a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) WHERE p.scope_id=%s AND p.incident_id=%s",(scope_id,incident_id)).fetchall()
        return {**incident,"sources":conn.execute("SELECT s.*,l.revision FROM ops.source_events s JOIN ops.incident_sources l ON (l.scope_id,l.source_event_id)=(s.scope_id,s.id) WHERE l.scope_id=%s AND l.incident_id=%s",(scope_id,incident_id)).fetchall(),"revisions":conn.execute("SELECT * FROM ops.incident_revisions WHERE scope_id=%s AND incident_id=%s ORDER BY revision",(scope_id,incident_id)).fetchall(),"impact":impact["body"] if impact else None,"risk":risk["body"] if risk else None,"plans":plans,"actions":actions,"approvals":approvals,"timeline":conn.execute("SELECT * FROM ops.audit_events WHERE scope_id=%s AND (object_id=%s OR object_id IN (SELECT id::text FROM ops.incident_actions WHERE scope_id=%s AND plan_id IN (SELECT id FROM ops.action_plans WHERE scope_id=%s AND incident_id=%s))) ORDER BY created_at",(scope_id,str(incident_id),scope_id,scope_id,incident_id)).fetchall()}


@app.get("/api/source-events/{event_id}")
def event(event_id:UUID,scope_id:UUID,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        row=conn.execute("SELECT s.*,l.incident_id,l.revision,j.id AS job_id,j.status AS job_status FROM ops.source_events s LEFT JOIN ops.incident_sources l ON (l.scope_id,l.source_event_id)=(s.scope_id,s.id) LEFT JOIN ops.analysis_jobs j ON (j.scope_id,j.source_event_id)=(s.scope_id,s.id) WHERE s.scope_id=%s AND s.id=%s",(scope_id,event_id)).fetchone()
        if not row: raise HTTPException(404,"Source event not found")
        return row


@app.get("/api/approvals")
def approval_list(scope_id:UUID,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        rows=conn.execute("SELECT a.*,p.incident_id,p.revision,i.title AS incident_title FROM ops.approvals a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id) WHERE a.scope_id=%s ORDER BY a.expires_at",(scope_id,)).fetchall()
        for row in rows: row["actions"]=conn.execute("SELECT action_type,payload FROM ops.incident_actions WHERE scope_id=%s AND plan_id=%s",(scope_id,row["plan_id"])).fetchall()
        return {"items":rows}


@app.post("/api/approvals/{approval_id}/decision")
def decide(approval_id:UUID,body:Decision,background_tasks:BackgroundTasks,actor=Depends(user)):
    background_tasks.add_task(notify_recovery)
    with transaction() as conn:
        scope(conn,actor,body.scope_id)
        approval=conn.execute("SELECT * FROM ops.approvals WHERE scope_id=%s AND id=%s FOR UPDATE",(body.scope_id,approval_id)).fetchone()
        if not approval: raise HTTPException(404,"Approval not found")
        role(actor,approval["required_role"])
        state=revalidate(conn,body.scope_id,approval["plan_id"])
        if approval["plan_version"]!=body.expected_version or approval["plan_hash"]!=body.plan_hash or approval["status"]!="PENDING" or state["status"] in ("SUPERSEDED","EXPIRED"):
            raise HTTPException(409,"Approval is stale, expired or already consumed")
        clock=now(conn,body.scope_id)
        if approval["expires_at"]<=clock: raise HTTPException(409,"Approval expired")
        if body.decision=="MODIFY":
            if not body.payload: raise HTTPException(422,"Modify requires a complete revised plan payload")
            old=conn.execute("SELECT * FROM ops.action_plans WHERE scope_id=%s AND id=%s",(body.scope_id,approval["plan_id"])).fetchone()
            risk=conn.execute("SELECT body FROM ops.risk_assessments WHERE scope_id=%s AND impact_id=%s",(body.scope_id,old["impact_assessment_id"])).fetchone()["body"]
            if body.payload==old["body"]: raise HTTPException(422,"Modified plan must differ")
            original_actions=old["body"].get("actions",[]); revised_actions=body.payload.get("actions",[])
            if len(original_actions)!=len(revised_actions): raise HTTPException(422,"Changing action selection requires factual reassessment")
            for original,revised in zip(original_actions,revised_actions):
                if original.get("action_type")!=revised.get("action_type"): raise HTTPException(422,"Changing action type requires factual reassessment")
                immutable=lambda p:{k:v for k,v in p.items() if k not in ("body","subject","title")}
                if immutable(original.get("payload",{}))!=immutable(revised.get("payload",{})): raise HTTPException(422,"Changing factual command parameters requires reassessment")
            result=create_plan(conn,body.scope_id,old["incident_id"],old["revision"],old["impact_assessment_id"],risk,body.payload)
            audit(conn,body.scope_id,"APPROVAL_MODIFIED",old["incident_id"],actor=str(actor["id"]),data={"old_plan_id":str(old["id"]),"new_plan_id":result["plan_id"],"comment":body.comment})
            return {**result,"status":"SUPERSEDED"}
        state="APPROVED" if body.decision=="APPROVE" else "REJECTED"
        conn.execute("UPDATE ops.approvals SET status=%s,actor_id=%s,decision=%s,comment=%s,decided_at=%s WHERE scope_id=%s AND id=%s",(state,actor["id"],body.decision,body.comment,clock,body.scope_id,approval_id))
        outbox(conn,body.scope_id,f"decision:{approval_id}","WAKEUP",{"scope_id":str(body.scope_id),"plan_id":str(approval["plan_id"])})
        result=revalidate(conn,body.scope_id,approval["plan_id"])
        audit(conn,body.scope_id,"APPROVAL_"+state,approval["plan_id"],actor=str(actor["id"]),data={"approval_id":str(approval_id),"plan_hash":body.plan_hash,"comment":body.comment})
        return {**result,"approval_id":str(approval_id),"decision_status":state}


@app.get("/api/actions")
def actions(scope_id:UUID,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        rows=conn.execute("SELECT id,scope_id,plan_id,action_type,payload,status,attempts,provider_id,execution_id,workflow_id,result FROM ops.incident_actions WHERE scope_id=%s ORDER BY id",(scope_id,)).fetchall()
        return {"items":rows}


@app.get("/api/errors")
def errors(scope_id:UUID,actor=Depends(user)):
    with transaction() as conn:
        scope(conn,actor,scope_id)
        return {"items":conn.execute("SELECT * FROM ops.workflow_errors WHERE scope_id=%s ORDER BY created_at DESC",(scope_id,)).fetchall()}


@app.get("/api/system")
def system(scope_id:UUID,actor=Depends(user)):
    live,model,limit=live_ai_config()
    with transaction() as conn:
        scope(conn,actor,scope_id)
        calls=conn.execute("SELECT count(*) AS count FROM ops.live_ai_calls").fetchone()["count"]
        jobs=conn.execute("""SELECT j.id,j.source_event_id,j.status,j.step,j.attempts,j.next_attempt_at,
            j.execution_id,j.workflow_id,j.last_error,i.id AS incident_id,i.title AS incident_title
            FROM ops.analysis_jobs j LEFT JOIN ops.incident_sources s
            ON (s.scope_id,s.source_event_id)=(j.scope_id,j.source_event_id)
            LEFT JOIN ops.incidents i ON (i.scope_id,i.id)=(s.scope_id,s.incident_id)
            WHERE j.scope_id=%s""",(scope_id,)).fetchall()
        waits=conn.execute("""SELECT w.scope_id,w.plan_id,w.execution_id,w.workflow_id,w.registered_at,
            i.id AS incident_id,i.title AS incident_title,p.status AS plan_status
            FROM ops.wait_registrations w JOIN ops.action_plans p ON (p.scope_id,p.id)=(w.scope_id,w.plan_id)
            JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id)
            WHERE w.scope_id=%s""",(scope_id,)).fetchall()
        return {"profile":os.getenv("PROFILE","DEMO_LOCAL"),"ai_mode":"Live Gemini + verified facts" if live else "Simulated AI","live_ai":{"enabled":live,"model":model or None,"calls_used":calls,"calls_limit":limit},"external_actions_enabled":False,"jobs":jobs,"outbox":conn.execute("SELECT kind,status,count(*) AS count FROM ops.outbox_events WHERE scope_id=%s GROUP BY kind,status",(scope_id,)).fetchall(),"notifications":conn.execute("SELECT id,body,created_at FROM ops.sandbox_notifications WHERE scope_id=%s ORDER BY created_at DESC",(scope_id,)).fetchall(),"wait_registrations":waits,"health":{"database":"ready"}}


def forward_intake(envelope):
    name="N8N_INTAKE_EMAIL_URL" if envelope["source"]=="EMAIL" else "N8N_INTAKE_API_URL"
    url=os.getenv(name,"")
    if not url: raise HTTPException(503,"n8n intake webhook is not configured")
    try: response=httpx.post(url,json=envelope,headers={"X-Webhook-Token":os.getenv("N8N_WEBHOOK_TOKEN","")},timeout=25)
    except httpx.RequestError: raise HTTPException(503,"n8n intake unavailable; retry with the same source ID")
    if response.status_code not in (200,202): raise HTTPException(503,"n8n did not confirm durable intake")
    try: result=response.json()
    except ValueError: raise HTTPException(503,"n8n returned no durable event reference")
    if not isinstance(result,dict) or not result.get("source_event_id"): raise HTTPException(503,"n8n returned no durable event reference")
    with transaction() as conn:
        saved=conn.execute("SELECT id FROM ops.source_events WHERE scope_id=%s AND id=%s",(envelope["scope_id"],result["source_event_id"])).fetchone()
        if not saved: raise HTTPException(503,"n8n response was not backed by a committed source event")
    return result


@app.post("/api/intake",status_code=202)
def intake(body:Envelope,actor=Depends(user)):
    role(actor,"operator","purchasing","production_manager","quality_manager","admin")
    if body.correction_context: raise HTTPException(422,"Use the version-checked incident correction command")
    with transaction() as conn: scope(conn,actor,body.scope_id)
    return forward_intake(body.model_dump(mode="json"))


@app.post("/api/demo/runs",status_code=202)
def demo(body:Demo,actor=Depends(user)):
    role(actor,"operator","purchasing","production_manager","quality_manager","admin")
    sid=str(body.scope_id) if body.scope_id else uid()
    with transaction() as conn:
        if body.scope_id: scope(conn,actor,sid)
        else:
            conn.execute("INSERT INTO ops.scopes(id,name,owner_id,clock_at) VALUES (%s,%s,%s,%s)",(sid,"Demo · "+body.scenario,actor["id"],demo_clock()))
            # Explicit synthetic-team membership, never a global role-based scope bypass.
            conn.execute("INSERT INTO ops.memberships SELECT %s,id FROM ops.users WHERE id=%s OR role IN ('production_manager','quality_manager','purchasing','admin')",(sid,actor["id"]))
            audit(conn,sid,"DEMO_CREATED",sid,actor=str(actor["id"]),data={"scenario":body.scenario})
    erp_call("/erp/v1/demo/seed",{"scope_id":sid,"shipped":body.scenario=="quality-shipped"},write=True)
    base={"schema_version":"1.0","scope_id":sid,"source_account_id":"synthetic-demo","source_id":uid(),"received_at":demo_clock(),"correlation_id":uid()}
    if body.scenario in ("supplier-delay","unknown-input"):
        data=fixture("SUPPLIER_DELAY")["source_email"]
        envelope={**base,"source":"EMAIL",**data}
        if body.scenario=="unknown-input": envelope["content_text"]="Our delivery might arrive next Friday. Please advise."
    elif body.scenario=="supplier-split":
        f=fixture("SUPPLIER_DELAY")
        envelope={**base,"source":"FORM","payload":{"incident_type":"SUPPLIER_DELAY",**{k:f[k] for k in ("purchase_order","purchase_order_item","material")},"confirmed_supply_schedule":f["scenarios"][1]["confirmed_supply_schedule"],"reason":f.get("reason","A broken delivery truck has delayed the steel rods needed for four mounting-frame orders.")},"subject":"Confirmed split revision"}
    else:
        kind="MACHINE_BREAKDOWN" if body.scenario=="machine-breakdown" else "QUALITY_ISSUE"
        envelope={**base,"source":"API","payload":fixture(kind)["facts"],"subject":body.scenario}
    return {**forward_intake(Envelope(**envelope).model_dump(mode="json")),"scope_id":sid}


@app.post("/api/demo/custom-email",status_code=202)
def custom_email(body:CustomEmail,actor=Depends(user)):
    role(actor,"operator","purchasing","production_manager","quality_manager","admin")
    live,_,limit=live_ai_config()
    if not live: raise HTTPException(503,"Live Gemini mail analysis is not enabled")
    sid=uid()
    with transaction() as conn:
        calls=conn.execute("SELECT count(*) AS count FROM ops.live_ai_calls").fetchone()["count"]
        if calls>=limit: raise HTTPException(429,"The configured live AI call budget is exhausted")
        conn.execute("INSERT INTO ops.scopes(id,name,owner_id,clock_at) VALUES (%s,'Demo · Gemini mail',%s,%s)",(sid,actor["id"],demo_clock()))
        conn.execute("INSERT INTO ops.memberships SELECT %s,id FROM ops.users WHERE id=%s OR role IN ('production_manager','quality_manager','purchasing','admin')",(sid,actor["id"]))
        audit(conn,sid,"DEMO_CREATED",sid,actor=str(actor["id"]),data={"scenario":"custom-gemini-email","synthetic":True})
    erp_call("/erp/v1/demo/seed",{"scope_id":sid,"shipped":False},write=True)
    envelope=Envelope(scope_id=sid,source="EMAIL",source_account_id="synthetic-custom-mail",
        source_id=uid(),received_at=demo_clock(),correlation_id=uid(),
        sender="supplier@example.test",subject=body.subject,content_text=body.content_text,ai_mode="live")
    return {**forward_intake(envelope.model_dump(mode="json")),"scope_id":sid}


@app.post("/api/demo/runs/{scope_id}/advance")
def advance(scope_id:UUID,body:dict,actor=Depends(user)):
    role(actor,"admin")
    seconds=body.get("seconds")
    if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or seconds<0 or seconds>86400*30: raise HTTPException(422,"seconds must be between 0 and 2592000")
    with transaction() as conn:
        scope(conn,actor,scope_id)
        row=conn.execute("UPDATE ops.scopes SET clock_at=clock_at+%s*interval '1 second' WHERE id=%s RETURNING clock_at",(seconds,scope_id)).fetchone()
        audit(conn,scope_id,"DEMO_CLOCK_ADVANCED",scope_id,actor=str(actor["id"]),data={"seconds":seconds,"n8n_clock_unchanged":True})
        return {"scope_id":str(scope_id),"clock":row["clock_at"],"n8n_clock_unchanged":True}


@app.post("/api/demo/runs/{scope_id}/reset")
def reset(scope_id:UUID,actor=Depends(user)):
    role(actor,"admin","operator","purchasing","production_manager","quality_manager")
    with transaction() as conn:
        current=scope(conn,actor,scope_id)
        if str(current["owner_id"])!=str(actor["id"]): raise HTTPException(403,"Only the synthetic scope owner may reset it")
        if conn.execute("SELECT 1 FROM ops.incident_actions WHERE scope_id=%s AND status IN ('IN_PROGRESS','UNKNOWN_OUTCOME')",(scope_id,)).fetchone(): raise HTTPException(409,"Reconcile in-flight or unknown actions before reset")
        if conn.execute("SELECT 1 FROM ops.analysis_jobs WHERE scope_id=%s AND status='RUNNING'",(scope_id,)).fetchone(): raise HTTPException(409,"Wait for running analysis before reset")
        conn.execute("DELETE FROM ops.incidents WHERE scope_id=%s",(scope_id,))
        conn.execute("DELETE FROM ops.source_events WHERE scope_id=%s",(scope_id,))
        for table in ("outbox_events","digests","failures"):
            conn.execute(f"DELETE FROM ops.{table} WHERE scope_id=%s",(scope_id,))
        conn.execute("UPDATE ops.scopes SET clock_at=%s WHERE id=%s",(demo_clock(),scope_id))
        audit(conn,scope_id,"DEMO_RESET",scope_id,actor=str(actor["id"]),data={"audit_retained":True})
    erp_call("/erp/v1/demo/reset",{"scope_id":str(scope_id)},write=True)
    return {"scope_id":str(scope_id),"status":"reset","audit_retained":True}


@app.post("/api/demo/failures")
def failure(body:dict,actor=Depends(user)):
    role(actor,"admin")
    sid=body.get("scope_id"); kind=body.get("kind")
    if kind not in ("read-503","read-429","write-timeout","permanent") or not isinstance(body.get("enabled"),bool): raise HTTPException(422,"Unsupported failure injection")
    with transaction() as conn:
        scope(conn,actor,sid)
        conn.execute("INSERT INTO ops.failures VALUES (%s,%s,%s) ON CONFLICT(scope_id,kind) DO UPDATE SET enabled=EXCLUDED.enabled",(sid,kind,body["enabled"]))
        audit(conn,sid,"DEMO_FAILURE_CONFIGURED",sid,actor=str(actor["id"]),data={"kind":kind,"enabled":body["enabled"]})
    return {"status":"configured"}


@app.post("/api/incidents/{incident_id}/corrections",status_code=202)
def correction(incident_id:UUID,body:dict,actor=Depends(user)):
    role(actor,"operator","purchasing","production_manager","quality_manager")
    sid=body.get("scope_id")
    if not body.get("reason") or not isinstance(body.get("facts"),dict): raise HTTPException(422,"Correction needs facts and a reason")
    with transaction() as conn:
        scope(conn,actor,sid)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s",(sid,incident_id)).fetchone()
        if not incident or incident["revision"]!=body.get("expected_revision"): raise HTTPException(409,"Incident revision is stale")
        audit(conn,sid,"CORRECTION_REQUESTED",incident_id,actor=str(actor["id"]),data={"reason":body["reason"]})
    envelope=Envelope(scope_id=sid,source="FORM",source_account_id="verified-correction",source_id=f"{incident_id}:{body['expected_revision']}:{digest(body['facts'])}",received_at=utcnow(),correlation_id=uid(),payload=body["facts"],subject="Human factual correction",correction_context={"incident_id":str(incident_id),"expected_revision":body["expected_revision"],"actor_id":str(actor["id"])})
    return forward_intake(envelope.model_dump(mode="json"))


@app.post("/api/incidents/{incident_id}/resolve")
def resolve(incident_id:UUID,body:dict,actor=Depends(user)):
    sid=body.get("scope_id")
    with transaction() as conn:
        scope(conn,actor,sid)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,incident_id)).fetchone()
        if not incident: raise HTTPException(404,"Incident not found")
        role(actor,"quality_manager" if incident["incident_type"]=="QUALITY_ISSUE" else "production_manager")
        if incident["revision"]!=body.get("expected_revision") or incident["status"]!="MONITORING": raise HTTPException(409,"Incident cannot be resolved in this state/version")
        evidence=body.get("evidence",{})
        if not isinstance(evidence,dict) or not evidence.get("snapshot_id") or not body.get("reason"): raise HTTPException(422,"A consistent ERP reassessment snapshot and reason are required")
        snapshot=conn.execute("SELECT x.body FROM erp.snapshots x JOIN ops.scopes s ON (s.id,s.erp_revision)=(x.scope_id,x.erp_revision) WHERE x.scope_id=%s AND x.id=%s",(sid,evidence["snapshot_id"])).fetchone()
        revision=conn.execute("SELECT facts FROM ops.incident_revisions WHERE scope_id=%s AND incident_id=%s AND revision=%s",(sid,incident_id,incident["revision"])).fetchone()
        checked=evaluate_impact(snapshot["body"],revision["facts"]) if snapshot else {}
        if not checked.get("data_complete") or checked.get("has_operational_impact") is not False or float(checked.get("total_shortage") or 0)!=0 or checked.get("hard_override"):
            raise HTTPException(409,"Current ERP evidence does not demonstrate restored coverage or quality disposition")
        if incident["incident_type"]=="QUALITY_ISSUE" and not checked.get("verified_disposition"): raise HTTPException(409,"Verified quality disposition is required")
        conn.execute("UPDATE ops.incidents SET status='RESOLVED',updated_at=%s WHERE scope_id=%s AND id=%s",(now(conn,sid),sid,incident_id))
        audit(conn,sid,"INCIDENT_RESOLVED",incident_id,actor=str(actor["id"]),data={"evidence":evidence,"reason":body["reason"]})
        return {"status":"RESOLVED"}


@app.post("/api/incidents/{incident_id}/quality-release-plan")
def quality_release_plan(incident_id:UUID,body:dict,actor=Depends(user)):
    """Explicit synthetic disposition proposal; a second POST must approve it."""
    role(actor,"quality_manager")
    sid=body.get("scope_id")
    evidence=body.get("disposition_evidence")
    if not isinstance(evidence,str) or not 10<=len(evidence)<=2000: raise HTTPException(422,"Documented quality disposition evidence is required")
    with transaction() as conn:
        scope(conn,actor,sid)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,incident_id)).fetchone()
        if not incident or incident["incident_type"]!="QUALITY_ISSUE" or incident["revision"]!=body.get("expected_revision"): raise HTTPException(409,"Matching quality incident revision required")
        block=conn.execute("SELECT a.* FROM ops.incident_actions a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) WHERE a.scope_id=%s AND p.incident_id=%s AND a.action_type='QUALITY_BLOCK' AND a.status='SUCCEEDED' ORDER BY p.plan_version DESC LIMIT 1",(sid,incident_id)).fetchone()
        if not block: raise HTTPException(409,"A succeeded quality block is required before a release proposal")
        risk=conn.execute("SELECT body FROM ops.risk_assessments WHERE scope_id=%s AND impact_id=%s",(sid,incident["current_impact_id"])).fetchone()["body"]
        payload={**block["payload"],"disposition_evidence":evidence}
        proposed={"policy_version":"1.0","summary":"Separate Quality disposition: release the synthetically blocked lot after the documented review.","summary_mode":"deterministic-template","sop_ids":["SOP-QUALITY-ISSUE-v1"],"actions":[{"action_type":"QUALITY_RELEASE","required_role":"quality_manager","payload":payload}]}
        result=create_plan(conn,sid,incident_id,incident["revision"],incident["current_impact_id"],risk,proposed)
        audit(conn,sid,"QUALITY_RELEASE_PROPOSED",incident_id,actor=str(actor["id"]),data={"plan_id":result["plan_id"],"evidence":evidence})
        return result


@app.post("/api/incidents/{incident_id}/close")
def close(incident_id:UUID,body:dict,actor=Depends(user)):
    sid=body.get("scope_id")
    with transaction() as conn:
        scope(conn,actor,sid)
        incident=conn.execute("SELECT * FROM ops.incidents WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,incident_id)).fetchone()
        if not incident: raise HTTPException(404,"Incident not found")
        role(actor,"quality_manager" if incident["incident_type"]=="QUALITY_ISSUE" else "production_manager")
        if incident["status"]!="RESOLVED" or incident["revision"]!=body.get("expected_revision") or not body.get("reason"): raise HTTPException(409,"Only a resolved matching revision can close with a reason")
        conn.execute("UPDATE ops.incidents SET status='CLOSED',updated_at=%s WHERE scope_id=%s AND id=%s",(now(conn,sid),sid,incident_id))
        audit(conn,sid,"INCIDENT_CLOSED",incident_id,actor=str(actor["id"]),data={"reason":body["reason"]})
        return {"status":"CLOSED"}


@app.post("/api/errors/{error_id}/retry")
def retry(error_id:UUID,body:dict,actor=Depends(user)):
    role(actor,"admin"); sid=body.get("scope_id")
    if not body.get("reason"): raise HTTPException(422,"Controlled retry requires a reason")
    with transaction() as conn:
        scope(conn,actor,sid)
        error=conn.execute("SELECT * FROM ops.workflow_errors WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,error_id)).fetchone()
        if not error or not error["retryable"] or not error["job_id"]: raise HTTPException(409,"This error cannot be retried")
        job=conn.execute("SELECT * FROM ops.analysis_jobs WHERE scope_id=%s AND id=%s FOR UPDATE",(sid,error["job_id"])).fetchone()
        if job["status"]!="DEAD_LETTER": raise HTTPException(409,"Job is not in Dead Letter")
        conn.execute("UPDATE ops.analysis_jobs SET status='PENDING',attempts=0,next_attempt_at=%s,claim_token=NULL WHERE scope_id=%s AND id=%s",(utcnow(),sid,job["id"]))
        conn.execute("UPDATE ops.workflow_errors SET dead_letter=false WHERE id=%s",(error_id,))
        audit(conn,sid,"ADMIN_RETRY",job["id"],actor=str(actor["id"]),data={"reason":body["reason"],"previous_attempts":job["attempts"]})
        return {"job_id":str(job["id"]),"status":"PENDING"}


@app.post("/internal/errors",dependencies=[Depends(service)])
def internal_error(body:dict):
    with transaction() as conn:
        if body.get("execution_id"):
            broken=conn.execute("SELECT scope_id,plan_id FROM ops.wait_registrations WHERE execution_id=%s",(str(body["execution_id"]),)).fetchall()
            for waiting in broken:
                conn.execute("DELETE FROM ops.wait_registrations WHERE scope_id=%s AND plan_id=%s",(waiting["scope_id"],waiting["plan_id"]))
                conn.execute("UPDATE ops.outbox_events SET status='PENDING',lease_until=NULL WHERE scope_id=%s AND event_key=%s",(waiting["scope_id"],"plan:"+str(waiting["plan_id"])))
        code=body.get("status_code")
        if isinstance(code,int): body["error_class"]="TRANSIENT" if code==429 or code>=500 else "PERMANENT"
        if not body.get("job_id") and body.get("execution_id"):
            own=conn.execute("SELECT * FROM ops.analysis_jobs WHERE execution_id=%s ORDER BY lease_until DESC NULLS LAST LIMIT 1",(str(body["execution_id"]),)).fetchone()
            if own:
                body={**body,"job_id":str(own["id"]),"scope_id":str(own["scope_id"])}
        if body.get("job_id") and body.get("scope_id"):
            row=conn.execute("SELECT * FROM ops.analysis_jobs WHERE scope_id=%s AND id=%s",(body["scope_id"],body["job_id"])).fetchone()
            if row and row["status"]=="RUNNING": return fail_job(conn,{**stage_for(row),**body,"claim_token":str(row["claim_token"])})
        eid=uid(); cls=body.get("error_class","PERMANENT")
        conn.execute("INSERT INTO ops.workflow_errors(id,scope_id,job_id,execution_id,workflow_id,error_class,message,retryable,dead_letter) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(eid,body.get("scope_id"),body.get("job_id"),body.get("execution_id"),body.get("workflow_id"),cls,safe_message(body.get("message","Unclassified workflow failure")),cls=="TRANSIENT",not body.get("job_id")))
        return {"error_id":eid,"status":"RECORDED"}


@app.post("/internal/recovery",dependencies=[Depends(service)])
def recovery(body:dict):
    with transaction() as conn:
        # A decision wakeup becomes obsolete after all effects finish, or after
        # its plan is superseded. Retain its audit row without endless delivery.
        conn.execute("""UPDATE ops.outbox_events e SET status='DELIVERED',lease_until=NULL
            WHERE e.kind='WAKEUP' AND e.status!='DELIVERED' AND EXISTS (
              SELECT 1 FROM ops.action_plans p WHERE p.scope_id=e.scope_id AND p.id=(e.payload->>'plan_id')::uuid
              AND (p.status!='CURRENT' OR NOT EXISTS (
                SELECT 1 FROM ops.incident_actions a WHERE a.scope_id=p.scope_id AND a.plan_id=p.id AND a.status NOT IN ('SUCCEEDED','CANCELLED'))))""")
        conn.execute("UPDATE ops.analysis_jobs SET status=CASE WHEN attempts<4 THEN 'RETRY_SCHEDULED' ELSE 'DEAD_LETTER' END,next_attempt_at=%s,lease_until=NULL WHERE status='RUNNING' AND lease_until<%s",(utcnow(),utcnow()))
        conn.execute("UPDATE ops.incident_actions SET status='UNKNOWN_OUTCOME',result=%s,lease_until=NULL WHERE status='IN_PROGRESS' AND lease_until<%s",(js({"message":"Worker lease expired after dispatch may have started","reconciliation_required":True}),utcnow()))
        jobs=conn.execute("SELECT id AS job_id,scope_id,source_event_id,correlation_id FROM ops.analysis_jobs WHERE status IN ('PENDING','RETRY_SCHEDULED') AND next_attempt_at<=%s AND attempts<4 ORDER BY next_attempt_at LIMIT 50",(utcnow(),)).fetchall()
        plans=[]; wakeups=[]
        pending=conn.execute("SELECT p.*,i.severity FROM ops.action_plans p JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id) WHERE p.status='CURRENT' ORDER BY p.created_at LIMIT 100").fetchall()
        for plan in pending:
            sid,pid=plan["scope_id"],plan["id"]
            status=revalidate(conn,sid,pid)
            clock=now(conn,sid); interval=SLA["review_seconds"].get(plan["severity"])
            if interval and status["status"]=="PENDING":
                elapsed=(clock-plan["created_at"]).total_seconds()
                for level in range(1,min(int(elapsed//interval),SLA["escalation_stages"])+1):
                    outbox(conn,sid,f"sla:{pid}:{level}","SLA",{"scope_id":str(sid),"plan_id":str(pid),"stage":level,"recipient":"operations@example.test"})
            wait=conn.execute("SELECT * FROM ops.wait_registrations WHERE scope_id=%s AND plan_id=%s",(sid,pid)).fetchone()
            if not wait:
                event=conn.execute("SELECT * FROM ops.outbox_events WHERE scope_id=%s AND event_key=%s FOR UPDATE",(sid,"plan:"+str(pid))).fetchone()
                if event and (event["status"]=="PENDING" or event["lease_until"] and event["lease_until"]<utcnow()):
                    plans.append({"scope_id":str(sid),"plan_id":str(pid)})
                    conn.execute("UPDATE ops.outbox_events SET status='DISPATCHED',lease_until=%s WHERE id=%s",(utcnow()+timedelta(minutes=2),event["id"]))
            elif status["status"]!="PENDING":
                outbox(conn,sid,f"wake:{pid}:{wait['execution_id']}","WAKEUP",{"scope_id":str(sid),"plan_id":str(pid)})
        due=conn.execute("SELECT e.*,w.resume_url FROM ops.outbox_events e JOIN ops.wait_registrations w ON w.scope_id=e.scope_id AND w.plan_id=(e.payload->>'plan_id')::uuid WHERE e.kind='WAKEUP' AND e.status!='DELIVERED' AND e.next_attempt_at<=%s AND (e.lease_until IS NULL OR e.lease_until<%s) LIMIT 50 FOR UPDATE OF e SKIP LOCKED",(utcnow(),utcnow())).fetchall()
        for event in due:
            wakeups.append({"scope_id":str(event["scope_id"]),"event_id":str(event["id"]),"resume_url":event["resume_url"]})
            conn.execute("UPDATE ops.outbox_events SET lease_until=%s,next_attempt_at=%s,attempts=attempts+1 WHERE id=%s",(utcnow()+timedelta(seconds=30),utcnow()+timedelta(seconds=30),event["id"]))
        actions=conn.execute("SELECT id AS action_id,scope_id FROM ops.incident_actions WHERE status IN ('READY','RETRY_SCHEDULED') AND next_attempt_at<=%s AND attempts<4 LIMIT 50",(utcnow(),)).fetchall()
        followups=conn.execute("SELECT a.* FROM ops.incident_actions a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id) WHERE a.status='SUCCEEDED' AND a.action_type IN ('SUPPLIER_EMAIL','RESCHEDULE') AND a.completed_at IS NOT NULL AND p.status='CURRENT' AND i.status NOT IN ('RESOLVED','CLOSED') LIMIT 100").fetchall()
        for action in followups:
            if now(conn,action["scope_id"])>=add_business_hours(action["completed_at"],SLA["action_followup_business_hours"]):
                outbox(conn,action["scope_id"],f"followup:{action['id']}","FOLLOWUP",{"action_id":str(action["id"]),"message":"Verify the operational result; dispatch success does not resolve the incident.","policy_version":SLA["version"]})
        notifications=conn.execute("SELECT * FROM ops.outbox_events WHERE kind IN ('SLA','FOLLOWUP') AND status='PENDING' LIMIT 100 FOR UPDATE SKIP LOCKED").fetchall()
        for notification in notifications:
            conn.execute("INSERT INTO ops.sandbox_notifications VALUES (%s,%s,%s,'operations@example.test',%s,now()) ON CONFLICT(event_id) DO NOTHING",(uid(),notification["scope_id"],notification["id"],js({"kind":notification["kind"],**notification["payload"]})))
            conn.execute("UPDATE ops.outbox_events SET status='DELIVERED' WHERE id=%s",(notification["id"],))
        return {"jobs":jobs,"plans":plans,"actions":actions,"wakeups":wakeups,"counts":{"jobs":len(jobs),"plans":len(plans),"actions":len(actions),"wakeups":len(wakeups)}}


@app.post("/internal/outbox/ack",dependencies=[Depends(service)])
def ack(body:dict):
    with transaction() as conn:
        conn.execute("UPDATE ops.outbox_events SET status='DELIVERED',lease_until=NULL WHERE scope_id=%s AND id=%s AND kind='WAKEUP'",(body.get("scope_id"),body.get("event_id")))
    return {"status":"ACKNOWLEDGED"}


@app.post("/internal/digest",dependencies=[Depends(service)])
def daily_digest(body:dict):
    with transaction() as conn:
        scopes=conn.execute("SELECT s.id FROM ops.scopes s WHERE (%s::uuid IS NULL OR s.id=%s) AND EXISTS (SELECT 1 FROM ops.memberships m WHERE m.scope_id=s.id)",(body.get("scope_id"),body.get("scope_id"))).fetchall()
        reports=[]
        for s in scopes:
            sid=s["id"]; date=now(conn,sid).astimezone(ZoneInfo(demo_timezone())).date()
            data=dashboard(conn,sid)
            report=conn.execute("INSERT INTO ops.digests VALUES (%s,%s,%s,'sandbox',%s) ON CONFLICT(scope_id,business_date,channel) DO NOTHING RETURNING *",(uid(),sid,date,js(data))).fetchone()
            if not report: report=conn.execute("SELECT * FROM ops.digests WHERE scope_id=%s AND business_date=%s AND channel='sandbox'",(sid,date)).fetchone()
            reports.append(report)
        return {"items":reports}
