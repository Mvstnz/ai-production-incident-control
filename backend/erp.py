"""Synthetic ERP boundary. Snapshots are immutable and commands require DB receipts."""
import json
from typing import Literal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from backend.db import canonical, digest, js, transaction, uid
from backend.models import Strict
from backend.security import BodyLimitMiddleware, token
from backend.seed import seed_scope

app=FastAPI(title="APIC Synthetic ERP API",version="1.0.0")
app.add_middleware(BodyLimitMiddleware)


def reader(request: Request): token(request,"x-erp-token","ERP_READ_TOKEN")
def writer(request: Request): token(request,"x-erp-token","ERP_WRITE_TOKEN")


class SnapshotRequest(Strict):
    scope_id: UUID
    incident_type: Literal["SUPPLIER_DELAY","MACHINE_BREAKDOWN","QUALITY_ISSUE"]
    revision: int | None = None


class SeedRequest(Strict):
    scope_id: UUID
    shipped: bool = False


class ERPCommand(Strict):
    scope_id: UUID
    action_id: UUID
    claim_token: UUID
    payload: dict


@app.get("/health/live")
def live(): return {"status":"alive","synthetic":True}


@app.get("/health/ready")
def ready():
    try:
        with transaction(erp=True) as conn: conn.execute("SELECT 1 FROM erp.fixture_data LIMIT 1")
    except Exception: raise HTTPException(503,"ERP database unavailable")
    return {"status":"ready"}


@app.post("/erp/v1/demo/seed",dependencies=[Depends(writer)])
def seed(body: SeedRequest):
    with transaction(erp=True) as conn:
        conn.execute("SELECT id FROM ops.scopes WHERE id=%s FOR UPDATE",(body.scope_id,))
        seed_scope(conn,body.scope_id)
        if body.shipped:
            conn.execute("UPDATE erp.shipments SET status='SHIPPED' WHERE scope_id=%s",(body.scope_id,))
            conn.execute("UPDATE ops.scopes SET erp_revision=erp_revision+1 WHERE id=%s",(body.scope_id,))
    return {"scope_id":str(body.scope_id),"synthetic":True}


@app.post("/erp/v1/demo/reset",dependencies=[Depends(writer)])
def reset_seed(body:SeedRequest):
    with transaction(erp=True) as conn:
        conn.execute("SELECT id FROM ops.scopes WHERE id=%s FOR UPDATE",(body.scope_id,))
        if conn.execute("SELECT 1 FROM ops.incident_actions WHERE scope_id=%s",(body.scope_id,)).fetchone(): raise HTTPException(409,"Operations must finish scoped reset before ERP reset")
        # Fixed dependency order, one explicitly authenticated synthetic scope.
        for table in ("command_receipts","quality_dispositions","lot_allocations","quality_inspections","shipment_items","shipments","production_sales_allocations","production_operations","production_requirements","inventory_reservations","inventory_lots","supply_schedules","purchase_order_items","purchase_orders","supplier_materials","materials","suppliers","production_orders","capacity_calendar","machine_capabilities","machines","sales_order_items","sales_orders","customers","fixture_data"):
            conn.execute(f"DELETE FROM erp.{table} WHERE scope_id=%s",(body.scope_id,))
        seed_scope(conn,body.scope_id)
        conn.execute("UPDATE ops.scopes SET erp_revision=erp_revision+1 WHERE id=%s",(body.scope_id,))
    return {"status":"reset","scope_id":str(body.scope_id),"snapshots_retained":True}


def build_snapshot(conn,sid,kind):
    state=conn.execute("SELECT * FROM ops.scopes WHERE id=%s FOR SHARE",(sid,)).fetchone()
    if not state: raise HTTPException(404,"Scope not found")
    failures={row["kind"] for row in conn.execute("SELECT kind FROM ops.failures WHERE scope_id=%s AND enabled",(sid,))}
    if "read-503" in failures: raise HTTPException(503,"Synthetic ERP read failure")
    if "read-429" in failures: raise HTTPException(429,"Synthetic ERP rate limit",headers={"Retry-After":"30"})
    row=conn.execute("SELECT body FROM erp.fixture_data WHERE scope_id=%s AND incident_type=%s",(sid,kind)).fetchone()
    if not row: raise HTTPException(404,"ERP seed is missing")
    data=row["body"]
    if kind=="SUPPLIER_DELAY":
        lots=conn.execute("SELECT * FROM erp.inventory_lots WHERE scope_id=%s AND material_id=%s",(sid,data["material"])).fetchall()
        reservations=conn.execute("SELECT r.* FROM erp.inventory_reservations r JOIN erp.inventory_lots l ON (l.scope_id,l.id)=(r.scope_id,r.lot_id) WHERE r.scope_id=%s AND l.material_id=%s",(sid,data["material"])).fetchall()
        data["inventory"]={"physical":sum(x["quantity"] for x in lots),"quarantined":sum(x["quantity"] for x in lots if x["quality_status"]!="RELEASED"),"reserved_for_other_demands":sum(x["quantity"] for x in reservations if x["production_order_id"] not in {r["production_order"] for r in data["production_requirements"]})}
        data["inventory"]["available_to_this_scope"]=data["inventory"]["physical"]-data["inventory"]["quarantined"]-data["inventory"]["reserved_for_other_demands"]
        own={}
        for reservation in reservations:
            mo=reservation["production_order_id"]
            if mo in {r["production_order"] for r in data["production_requirements"]}: own[mo]=own.get(mo,0)+reservation["quantity"]
        if own: data["inventory"]["reserved_for_own_demands"]=own
        data["original_supply_schedule"]=[{"quantity":r["quantity"],"available_at":r["available_at"].isoformat(),"status":r["status"]} for r in conn.execute("SELECT * FROM erp.supply_schedules WHERE scope_id=%s AND purchase_order_item_id=%s AND revision=(SELECT max(revision) FROM erp.supply_schedules WHERE scope_id=%s AND purchase_order_item_id=%s) ORDER BY available_at",(sid,data["purchase_order"]+"/"+data["purchase_order_item"],sid,data["purchase_order"]+"/"+data["purchase_order_item"]))]
    elif kind=="MACHINE_BREAKDOWN":
        operations={r["id"]:r for r in conn.execute("SELECT * FROM erp.production_operations WHERE scope_id=%s",(sid,))}
        for operation in data["production_operations"]:
            current=operations[operation["operation_id"]]
            for key in ("machine_id","start_at","end_at"):
                operation[key]=current[key].isoformat() if hasattr(current[key],"isoformat") else current[key]
    else:
        shipments={r["id"]:r for r in conn.execute("SELECT * FROM erp.shipments WHERE scope_id=%s",(sid,))}
        for shipment in data["shipments"]: shipment["status"]=shipments[shipment["shipment_id"]]["status"]
        lots={r["id"]:r for r in conn.execute("SELECT * FROM erp.inventory_lots WHERE scope_id=%s",(sid,))}
        for lot in data["inventory_lots"]: lot["quality_status"]=lots[lot["lot_id"]]["quality_status"]
        data["quality_dispositions"]=[dict(r) for r in conn.execute("SELECT disposition_id,lot_id,inspection_id,verified,result,evidence,decided_at FROM erp.quality_dispositions WHERE scope_id=%s",(sid,))]
    snapshot={"schema_version":"1.0","snapshot_id":uid(),"scope_id":str(sid),"erp_revision":state["erp_revision"],"incident_type":kind,"analysis_time":state["clock_at"].isoformat(),"data":json.loads(canonical(data))}
    return snapshot


@app.post("/erp/v1/snapshots",dependencies=[Depends(reader)])
def snapshot(body: SnapshotRequest):
    with transaction(erp=True) as conn:
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        result=build_snapshot(conn,body.scope_id,body.incident_type)
        conn.execute("INSERT INTO erp.snapshots(id,scope_id,erp_revision,incident_type,body,content_hash) VALUES (%s,%s,%s,%s,%s,%s)",(result["snapshot_id"],body.scope_id,result["erp_revision"],body.incident_type,js(result),digest(result)))
    return result


@app.get("/erp/v1/snapshots/{snapshot_id}",dependencies=[Depends(reader)])
def get_snapshot(snapshot_id: UUID,scope_id: UUID):
    with transaction(erp=True) as conn:
        row=conn.execute("SELECT body FROM erp.snapshots WHERE scope_id=%s AND id=%s",(scope_id,snapshot_id)).fetchone()
        if not row: raise HTTPException(404,"Snapshot not found in scope")
        return row["body"]


@app.get("/erp/v1/{resource}",dependencies=[Depends(reader)])
def detailed(resource: str,snapshot_id: UUID,scope_id: UUID):
    allowed={"purchase-orders":["purchase_order","purchase_order_item","material","open_purchase_quantity","original_supply_schedule"],"inventory":["inventory","inventory_lots"],"requirements":["production_requirements"],"capacity":["machines","capacity_calendar","production_operations"],"lot-trace":["inventory_lots","quality_inspections","shipments","shipment_items","lot_allocations"]}
    if resource not in allowed: raise HTTPException(404,"ERP resource not found")
    value=get_snapshot(snapshot_id,scope_id)
    return {"snapshot_id":str(snapshot_id),"scope_id":str(scope_id),"erp_revision":value["erp_revision"],"data":{k:value["data"][k] for k in allowed[resource] if k in value["data"]}}


@app.post("/erp/v1/commands/{command}",dependencies=[Depends(writer)])
def command(command: str,body: ERPCommand):
    expected={"reschedule":"RESCHEDULE","quality-block":"QUALITY_BLOCK","quality-release":"QUALITY_RELEASE"}
    if command not in expected: raise HTTPException(404,"Command not allowed")
    with transaction(erp=True) as conn:
        action=conn.execute("""SELECT a.*,p.revision,p.status AS plan_status,p.incident_id,i.revision AS current_revision FROM ops.incident_actions a JOIN ops.action_plans p ON (p.scope_id,p.id)=(a.scope_id,a.plan_id) JOIN ops.incidents i ON (i.scope_id,i.id)=(p.scope_id,p.incident_id) WHERE a.scope_id=%s AND a.id=%s""",(body.scope_id,body.action_id)).fetchone()
        if not action or action["action_type"]!=expected[command] or action["payload"]!=body.payload or str(action["claim_token"])!=str(body.claim_token) or action["status"]!="IN_PROGRESS" or action["plan_status"]!="CURRENT" or action["revision"]!=action["current_revision"]:
            raise HTTPException(403,"No matching current authorized action claim")
        if conn.execute("SELECT 1 FROM ops.approvals WHERE scope_id=%s AND plan_id=%s AND status!='APPROVED'",(body.scope_id,action["plan_id"])).fetchone(): raise HTTPException(403,"Required approval is missing")
        conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",(str(body.scope_id)+":"+str(body.action_id),))
        previous=conn.execute("SELECT * FROM erp.command_receipts WHERE scope_id=%s AND action_id=%s",(body.scope_id,body.action_id)).fetchone()
        if previous:
            if previous["payload_hash"]!=digest(body.payload): raise HTTPException(409,"Command receipt payload conflict")
            return previous["result"]
        p=body.payload
        if command=="reschedule":
            operation=conn.execute("SELECT * FROM erp.production_operations WHERE scope_id=%s AND id=%s FOR UPDATE",(body.scope_id,p["operation_id"])).fetchone()
            capacity=conn.execute("SELECT * FROM erp.capacity_calendar WHERE scope_id=%s AND machine_id=%s AND start_at<=%s AND end_at>=%s AND available_hours>=%s FOR UPDATE",(body.scope_id,p["machine_id"],p["start_at"],p["end_at"],p["required_hours"])).fetchone()
            capability=conn.execute("SELECT 1 FROM erp.machine_capabilities c JOIN erp.machines m ON (m.scope_id,m.id)=(c.scope_id,c.machine_id) WHERE c.scope_id=%s AND c.machine_id=%s AND c.capability=%s AND m.site=%s",(body.scope_id,p["machine_id"],p["capability"],p["site"])).fetchone()
            if not operation or not capacity or not capability: raise HTTPException(409,"Qualified free capacity is no longer available")
            conn.execute("UPDATE erp.capacity_calendar SET available_hours=available_hours-%s WHERE scope_id=%s AND id=%s",(p["required_hours"],body.scope_id,capacity["id"]))
            conn.execute("UPDATE erp.production_operations SET machine_id=%s,start_at=%s,end_at=%s WHERE scope_id=%s AND id=%s",(p["machine_id"],p["start_at"],p["end_at"],body.scope_id,p["operation_id"]))
        else:
            if command=="quality-release" and not p.get("disposition_evidence"): raise HTTPException(422,"Separate verified disposition evidence is required")
            inspections=conn.execute("SELECT * FROM erp.quality_inspections WHERE scope_id=%s AND id=%s AND lot_id=%s",(body.scope_id,p["inspection_id"],p["lot_id"])).fetchone()
            if command=="quality-block" and (not inspections or not inspections["verified"] or inspections["result"]!="FAILED"): raise HTTPException(409,"Verified failed inspection required")
            for item in p["shipment_item_ids"]:
                target=conn.execute("SELECT i.*,s.status AS shipment_status FROM erp.shipment_items i JOIN erp.shipments s ON (s.scope_id,s.id)=(i.scope_id,i.shipment_id) JOIN erp.lot_allocations a ON (a.scope_id,a.shipment_item_id)=(i.scope_id,i.id) WHERE i.scope_id=%s AND i.id=%s AND a.lot_id=%s FOR UPDATE OF i",(body.scope_id,item,p["lot_id"])).fetchone()
                if not target or target["shipment_status"]=="SHIPPED": raise HTTPException(409,"Cannot block or release shipped/unlinked material")
                conn.execute("UPDATE erp.shipment_items SET status=%s WHERE scope_id=%s AND id=%s",("BLOCKED" if command=="quality-block" else "OPEN",body.scope_id,item))
            conn.execute("UPDATE erp.inventory_lots SET quality_status=%s WHERE scope_id=%s AND id=%s",("BLOCKED" if command=="quality-block" else "RELEASED",body.scope_id,p["lot_id"]))
            if command=="quality-release":
                conn.execute("INSERT INTO erp.quality_dispositions SELECT %s,%s,%s,%s,true,'RELEASED',%s,clock_at FROM ops.scopes WHERE id=%s",(body.scope_id,uid(),p["lot_id"],p["inspection_id"],str(p["disposition_evidence"]),body.scope_id))
        result={"status":"SUCCEEDED","provider_id":"erp-"+str(body.action_id),"synthetic":True,"command":command}
        conn.execute("INSERT INTO erp.command_receipts VALUES (%s,%s,%s,%s,%s)",(body.scope_id,body.action_id,command,digest(body.payload),js(result)))
        conn.execute("UPDATE ops.scopes SET erp_revision=erp_revision+1 WHERE id=%s",(body.scope_id,))
        return result
