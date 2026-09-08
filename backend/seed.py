"""Idempotent synthetic ERP seeds shared by bootstrap and isolated demo scopes."""
import json
from pathlib import Path

from psycopg import sql

from backend.db import js
from backend.datasets import FILES, load_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILES = FILES


def fixture(kind):
    return load_fixture(kind)


def insert(conn, table, scope_id, **values):
    values = {"scope_id":scope_id, **values}
    statement = sql.SQL("INSERT INTO erp.{} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
        sql.Identifier(table),sql.SQL(",").join(map(sql.Identifier,values)),sql.SQL(",").join(sql.Placeholder() for _ in values))
    conn.execute(statement, list(values.values()))


def sales(conn, sid, line, quantity, value, due, strategic):
    order = line.split("/")[0]
    customer = "CUSTOMER-" + order
    insert(conn,"customers",sid,id=customer,strategic=strategic)
    insert(conn,"sales_orders",sid,id=order,customer_id=customer)
    insert(conn,"sales_order_items",sid,id=line,sales_order_id=order,open_quantity=quantity,open_net_line_value_cents=value,customer_due_at=due)


def seed_scope(conn, sid):
    for kind in FIXTURE_FILES:
        raw = fixture(kind)
        data = {k:v for k,v in raw.items() if k not in ("expected","scenarios","facts","source_email")}
        insert(conn,"fixture_data",sid,incident_type=kind,body=js(data))
        if kind == "SUPPLIER_DELAY":
            supplier_id=data["supplier_id"]
            insert(conn,"suppliers",sid,id=supplier_id,name=data["supplier"])
            insert(conn,"materials",sid,id=data["material"],description=data.get("material_description","Invented demo component"),unit=data["unit"],material_type="COMPONENT")
            insert(conn,"supplier_materials",sid,supplier_id=supplier_id,material_id=data["material"],qualified=True,available_at=None)
            insert(conn,"purchase_orders",sid,id=data["purchase_order"],supplier_id=supplier_id)
            poi=f'{data["purchase_order"]}/{data["purchase_order_item"]}'
            insert(conn,"purchase_order_items",sid,id=poi,purchase_order_id=data["purchase_order"],material_id=data["material"],ordered_quantity=data["open_purchase_quantity"],open_quantity=data["open_purchase_quantity"])
            for i,row in enumerate(data["original_supply_schedule"]):
                insert(conn,"supply_schedules",sid,id=f"{poi}/{i}",purchase_order_item_id=poi,quantity=row["quantity"],available_at=row["available_at"],status=row["status"],revision=1)
            inv=data["inventory"]
            lot_id=data["inventory_lot_id"]
            insert(conn,"inventory_lots",sid,id=lot_id,material_id=data["material"],site=data["site"],quantity=inv["physical"]-inv["quarantined"],quality_status="RELEASED")
            if inv["quarantined"]:
                insert(conn,"inventory_lots",sid,id=lot_id+"-HOLD",material_id=data["material"],site=data["site"],quantity=inv["quarantined"],quality_status="QUARANTINED")
            insert(conn,"production_orders",sid,id="MO-OTHER",quantity=inv["reserved_for_other_demands"],priority=0)
            insert(conn,"inventory_reservations",sid,id="RES-OTHER",lot_id=lot_id,production_order_id="MO-OTHER",quantity=inv["reserved_for_other_demands"])
            for index,row in enumerate(data["production_requirements"]):
                mo=row["production_order"]
                insert(conn,"production_orders",sid,id=mo,quantity=row["required_quantity"],priority=index+1)
                insert(conn,"production_requirements",sid,id=f"REQ-{mo}",production_order_id=mo,material_id=data["material"],quantity=row["required_quantity"],need_at=row["need_at"],remaining_days=row["remaining_lead_time_calendar_days"])
                sales(conn,sid,row["sales_line"],row["required_quantity"],row["open_net_line_value_cents"],row["customer_due_at"],row["strategic_customer"])
                insert(conn,"production_sales_allocations",sid,production_order_id=mo,sales_line_id=row["sales_line"],quantity=row["required_quantity"])
        elif kind == "MACHINE_BREAKDOWN":
            for row in data["machines"]:
                insert(conn,"machines",sid,id=row["machine_id"],site=row["site"])
                for capability in row["capabilities"]:
                    insert(conn,"machine_capabilities",sid,machine_id=row["machine_id"],capability=capability)
            for index,row in enumerate(data["capacity_calendar"]):
                insert(conn,"capacity_calendar",sid,id=f"CAP-{index}",**row)
            for row in data["production_operations"]:
                insert(conn,"production_orders",sid,id=row["production_order"],quantity=1,priority=1)
                insert(conn,"production_operations",sid,id=row["operation_id"],production_order_id=row["production_order"],**{k:row[k] for k in ("machine_id","site","required_capability","start_at","end_at","required_hours")})
                sales(conn,sid,row["sales_line"],1,row["open_net_line_value_cents"],row["customer_due_at"],row["strategic_customer"])
                insert(conn,"production_sales_allocations",sid,production_order_id=row["production_order"],sales_line_id=row["sales_line"],quantity=1)
        else:
            seed_quality(conn,sid,data)


def seed_quality(conn,sid,data):
    for row in data["inventory_lots"]:
        material=row.get("material",row.get("material_id"))
        insert(conn,"materials",sid,id=material,description="Synthetic quality demo material",unit="pcs",material_type="COMPONENT")
        insert(conn,"inventory_lots",sid,id=row["lot_id"],material_id=material,site=row["site"],quantity=row["physical_quantity"],quality_status=row.get("quality_status","QUARANTINED"))
    for row in data["shipments"]:
        insert(conn,"shipments",sid,id=row["shipment_id"],status=row["status"],planned_at=row.get("scheduled_at",data["analysis_time"]))
    for row in data["shipment_items"]:
        sales(conn,sid,row["sales_line"],row["open_quantity"],row["open_net_line_value_cents"],row.get("customer_due_at",data["analysis_time"]),row.get("strategic_customer",False))
        insert(conn,"shipment_items",sid,id=row["shipment_item_id"],shipment_id=row["shipment_id"],sales_line_id=row["sales_line"],quantity=row["open_quantity"],status=row.get("status","OPEN"))
    for row in data["lot_allocations"]:
        insert(conn,"lot_allocations",sid,**{k:row[k] for k in ("lot_id","shipment_item_id","quantity")})
    for row in data["quality_inspections"]:
        insert(conn,"quality_inspections",sid,id=row["inspection_id"],lot_id=row["lot_id"],result=row["result"],verified=row["verified"],evidence=str(row.get("evidence",row.get("evidence_ref","synthetic inspection"))))
