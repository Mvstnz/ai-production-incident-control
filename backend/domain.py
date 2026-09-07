"""Deterministic, side-effect-free business rules for synthetic APIC data.

The algorithms consume facts and a single ERP snapshot. Expected fixture outputs
are never input to the calculations. Times retain offsets; money uses cents and
resource arithmetic uses Decimal until JSON serialization.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/risk-policy.v1.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "config/action-catalog.v1.json").read_text(encoding="utf-8"))
HERO = json.loads((ROOT / "fixtures/hero_supplier_delay.json").read_text(encoding="utf-8"))
METHOD_VERSION = "impact-v1.0"
Json = dict[str, Any]


class DomainValidationError(ValueError):
    """A missing or inconsistent business fact; callers route this to review."""


def number(value: Any, name: str, *, negative: bool = False) -> Decimal:
    if value is None or isinstance(value, bool):
        raise DomainValidationError(f"{name}: a verified numeric value is required")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise DomainValidationError(f"{name}: invalid decimal") from None
    if not result.is_finite() or (not negative and result < 0):
        raise DomainValidationError(f"{name}: finite nonnegative value required")
    return result


def timestamp(value: Any, name: str = "timestamp") -> datetime:
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", value):
        raise DomainValidationError(f"{name}: full date with year, time and UTC offset required")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise DomainValidationError(f"{name}: invalid date/time") from None
    if result.tzinfo is None or result.utcoffset() is None:
        raise DomainValidationError(f"{name}: UTC offset required")
    return result.astimezone(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def _json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, datetime):
        return _iso(value)
    if isinstance(value, dict):
        return {key: _json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(item) for item in value]
    return value


def _required(value: Json, key: str) -> Any:
    if key not in value or value[key] is None or value[key] == "":
        raise DomainValidationError(f"{key}: verified value is missing")
    return value[key]


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise DomainValidationError(f"{name}: verified true/false value required")
    return value


def _unique(rows: list[Json], key: str) -> dict[str, Json]:
    out = {}
    for row in rows:
        ident = str(_required(row, key))
        if ident in out:
            raise DomainValidationError(f"{key}: duplicate {ident}")
        out[ident] = row
    return out


def _snapshot(snapshot: Json, facts: Json) -> tuple[Json, datetime]:
    for key in ("snapshot_id", "scope_id", "erp_revision", "analysis_time", "data", "incident_type"):
        _required(snapshot, key)
    if snapshot.get("schema_version") != "1.0":
        raise DomainValidationError("snapshot schema_version must be 1.0")
    if snapshot["incident_type"] != facts.get("incident_type"):
        raise DomainValidationError("incident_type does not match ERP snapshot")
    if not isinstance(snapshot["erp_revision"], int) or snapshot["erp_revision"] < 1:
        raise DomainValidationError("erp_revision must be a positive integer")
    if snapshot.get("data_complete") is False or snapshot["data"].get("data_complete") is False:
        raise DomainValidationError("ERP snapshot is explicitly incomplete")

    def check(value: Any) -> None:
        if isinstance(value, dict):
            for key in ("snapshot_id", "scope_id", "erp_revision"):
                if key in value and value[key] != snapshot[key]:
                    raise DomainValidationError(f"Mixed ERP snapshot: inconsistent {key}")
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)

    check(snapshot["data"])
    check(facts)
    if snapshot["data"].get("currency") != "EUR":
        raise DomainValidationError("Only verified EUR snapshot values are supported")
    return snapshot["data"], timestamp(snapshot["analysis_time"], "analysis_time")


def _empty(snapshot: Json, facts: Json) -> Json:
    return {"schema_version": "1.0", "method_version": METHOD_VERSION,
            **{k: snapshot.get(k) for k in ("snapshot_id", "scope_id", "erp_revision", "analysis_time")},
            "incident_type": facts.get("incident_type"), "data_complete": False,
            "review_reasons": [], "reviewed_production_orders": [], "affected_production_orders": [],
            "affected_sales_lines": [], "total_required": None, "total_available": None,
            "total_shortage": None, "allocations_at_need": [], "shortages_at_need": [],
            "baseline": [], "projected": [], "affected_open_order_value_cents": None,
            "currency": "EUR", "sales_line_values": {}, "disruption_days": None,
            "hours_to_first_relevant_demand": None, "uncovered_resource_ratio": None,
            "qualified_alternative_available": None, "strategic_customer_affected": None,
            "has_operational_impact": None, "hard_override": None, "source_refs": [],
            "proposals": [], "what_if": None}


def _schedule(rows: Any, maximum: Decimal, label: str) -> list[Json]:
    if not isinstance(rows, list) or not rows:
        raise DomainValidationError(f"{label}: confirmed supply schedule required")
    result = []
    for index, row in enumerate(rows):
        if set(row) - {"quantity", "available_at", "status"}:
            raise DomainValidationError(f"{label}: unsupported supply fields")
        if row.get("status") != "CONFIRMED":
            raise DomainValidationError(f"{label}: a proposed arrival cannot enter confirmed supply")
        result.append({"quantity": number(row.get("quantity"), f"{label}[{index}].quantity"),
                       "available_at": timestamp(row.get("available_at"), f"{label}[{index}].available_at")})
    if sum((x["quantity"] for x in result), Decimal(0)) > maximum:
        raise DomainValidationError("Supply schedule exceeds open PO quantity; split must replace final arrival")
    return sorted(result, key=lambda row: row["available_at"])


def _inventory(data: Json, requirements: list[Json]) -> tuple[Decimal, dict[str, Decimal]]:
    own_ids = {r["production_order"] for r in requirements}
    own: dict[str, Decimal] = {}
    if "inventory_lots" not in data:
        inv = _required(data, "inventory")
        physical = number(inv.get("physical"), "inventory.physical")
        foreign = number(inv.get("reserved_for_other_demands"), "inventory.reserved_for_other_demands")
        blocked = number(inv.get("quarantined"), "inventory.quarantined")
        for key, val in inv.get("reserved_for_own_demands", {}).items():
            if key not in own_ids:
                raise DomainValidationError("Own reservation refers to an unreviewed production order")
            own[key] = number(val, "own reservation")
        usable = physical - foreign - blocked
        if usable < 0 or sum(own.values(), Decimal(0)) > usable:
            raise DomainValidationError("Inventory reservations/quarantine exceed physical stock")
        if "available_to_this_scope" in inv and number(inv["available_to_this_scope"], "available_to_this_scope") != usable:
            raise DomainValidationError("Inventory declared availability is inconsistent")
        return usable - sum(own.values(), Decimal(0)), own
    lots = _unique(data["inventory_lots"], "lot_id")
    reservations = data.get("inventory_reservations", [])
    free = Decimal(0)
    for lot_id, lot in lots.items():
        if lot.get("material") != data.get("material"):
            continue
        physical = number(lot.get("physical_quantity"), "lot.physical_quantity")
        if lot.get("quality_status") not in ("RELEASED", "QUARANTINED", "BLOCKED"):
            raise DomainValidationError("Lot quality status is unknown")
        lot_reservations = [r for r in reservations if r.get("lot_id") == lot_id]
        reserved = sum((number(r.get("quantity"), "reservation.quantity") for r in lot_reservations), Decimal(0))
        if reserved > physical:
            raise DomainValidationError("Lot reservations exceed physical stock")
        if lot["quality_status"] != "RELEASED":
            continue
        free += physical - reserved
        for reservation in lot_reservations:
            target = reservation.get("production_order")
            if target in own_ids:
                own[target] = own.get(target, Decimal(0)) + number(reservation["quantity"], "reservation.quantity")
    if any(r.get("lot_id") not in lots for r in reservations):
        raise DomainValidationError("Reservation refers to an unknown lot")
    return free, own


def _allocate(requirements: list[Json], schedule: list[Json], free: Decimal, own: dict[str, Decimal]) -> list[Json]:
    # Initial lots exist at the snapshot; receipts before/at a need are usable.
    pools = deepcopy(own)
    results: dict[str, Json] = {}
    backlog: list[Json] = []
    events = []
    for index, arrival in enumerate(schedule):
        events.append((arrival["available_at"], 0, 0, str(index), arrival))
    for req in requirements:
        events.append((req["_need"], 1, req.get("priority", 100), req["_id"], req))

    def cover(row: Json, moment: datetime) -> None:
        nonlocal free
        remaining = row["required_quantity"] - row["covered_quantity"]
        reserved = min(pools.get(row["production_order"], Decimal(0)), remaining)
        pools[row["production_order"]] = pools.get(row["production_order"], Decimal(0)) - reserved
        remaining -= reserved
        assigned = min(free, remaining)
        free -= assigned
        row["covered_quantity"] += reserved + assigned
        if row["covered_quantity"] == row["required_quantity"] and row["full_cover_at"] is None:
            row["full_cover_at"] = moment
            row["completion_at"] = moment + timedelta(days=float(row["_lead"]))

    for moment, kind, _, _, event in sorted(events, key=lambda item: item[:4]):
        if kind == 0:
            free += event["quantity"]
            for row in backlog:
                cover(row, moment)
            backlog = [row for row in backlog if row["full_cover_at"] is None]
            continue
        row = {"requirement_id": event["_id"], "production_order": event["production_order"],
               "need_at": moment, "required_quantity": event["_quantity"],
               "covered_quantity": Decimal(0), "covered_at_need": Decimal(0), "shortage_at_need": Decimal(0),
               "full_cover_at": None, "completion_at": None, "_lead": event["_lead"]}
        cover(row, moment)
        row["covered_at_need"] = row["covered_quantity"]
        row["shortage_at_need"] = row["required_quantity"] - row["covered_at_need"]
        results[event["_id"]] = row
        if row["full_cover_at"] is None:
            backlog.append(row)
    return [{k: v for k, v in results[req["_id"]].items() if not k.startswith("_")} for req in requirements]


def _sales_for(data: Json, record: Json) -> list[Json]:
    if "production_sales_allocations" in data:
        sales = _unique(data.get("sales_order_items", []), "sales_line")
        links = [link for link in data["production_sales_allocations"] if link.get("production_order") == record["production_order"]]
        result = []
        for link in links:
            quantity = number(link.get("quantity"), "production_sales_allocations.quantity")
            if link.get("sales_line") not in sales:
                raise DomainValidationError("Production allocation has an unknown sales line")
            if quantity:
                if "open_quantity" in sales[link["sales_line"]] and quantity > number(sales[link["sales_line"]]["open_quantity"], "sales.open_quantity"):
                    raise DomainValidationError("Production-to-sales allocation exceeds the open sales quantity")
                result.append(sales[link["sales_line"]])
        return result
    if "sales_lines" in record:
        return record["sales_lines"]
    return [record] if record.get("sales_line") else []


def _register_sales(result: Json, sales: Json) -> None:
    line = str(_required(sales, "sales_line"))
    amount = number(sales.get("open_net_line_value_cents"), "open_net_line_value_cents")
    if amount != amount.to_integral_value():
        raise DomainValidationError("Money must contain whole integer cents")
    if line in result["sales_line_values"] and result["sales_line_values"][line] != int(amount):
        raise DomainValidationError("Conflicting values for the same sales line")
    result["sales_line_values"][line] = int(amount)
    result["strategic_customer_affected"] |= _bool(sales.get("strategic_customer"), "strategic_customer")


def _supplier(result: Json, data: Json, facts: Json, now: datetime) -> None:
    for key in ("purchase_order", "purchase_order_item", "material"):
        if str(_required(facts, key)) != str(_required(data, key)):
            raise DomainValidationError(f"{key}: no unique matching ERP purchase-order item")
    if "purchase_order_items" in data:
        matches = [p for p in data["purchase_order_items"] if all(str(p.get(k)) == str(facts[k]) for k in ("purchase_order", "purchase_order_item", "material"))]
        if len(matches) != 1:
            raise DomainValidationError("Purchase-order item is ambiguous in ERP")
    maximum = number(data.get("open_purchase_quantity"), "open_purchase_quantity")
    original = _schedule(_required(data, "original_supply_schedule"), maximum, "original_supply_schedule")
    confirmed = _schedule(_required(facts, "confirmed_supply_schedule"), maximum, "confirmed_supply_schedule")
    requirements = deepcopy(_required(data, "production_requirements"))
    identifiers = set()
    for index, req in enumerate(requirements):
        req["_id"] = str(req.get("requirement_id", _required(req, "production_order")))
        if req["_id"] in identifiers:
            raise DomainValidationError("Multiple material requirements need distinct requirement_id values")
        identifiers.add(req["_id"])
        req["_need"] = timestamp(req.get("need_at"), "need_at")
        req["_quantity"] = number(req.get("required_quantity"), "required_quantity")
        req["_lead"] = number(req.get("remaining_lead_time_calendar_days"), "remaining_lead_time_calendar_days")
        number(req.get("priority", 100), "priority")
    requirements.sort(key=lambda r: (r["_need"], r.get("priority", 100), r["_id"]))
    free, own = _inventory(data, requirements)
    baseline = _allocate(requirements, original, free, own)
    projected = _allocate(requirements, confirmed, free, own)
    result.update(baseline=baseline, projected=projected, strategic_customer_affected=False)
    affected = set()
    for req, before, after in zip(requirements, baseline, projected):
        worse = ((after["completion_at"] is None and before["completion_at"] is not None)
                 or (after["completion_at"] is not None and before["completion_at"] is not None and after["completion_at"] > before["completion_at"])
                 or after["shortage_at_need"] > before["shortage_at_need"])
        after["affected"] = worse
        after["already_late_in_baseline"] = before["shortage_at_need"] > 0
        after["sales_lines"] = [str(s["sales_line"]) for s in _sales_for(data, req)]
        if worse:
            affected.add(req["production_order"])
            for sales in _sales_for(data, req):
                due = timestamp(sales.get("customer_due_at"), "customer_due_at")
                if after["completion_at"] is None or after["completion_at"] > due:
                    _register_sales(result, sales)
    total = sum((req["_quantity"] for req in requirements), Decimal(0))
    shortage = sum((row["shortage_at_need"] for row in projected), Decimal(0))
    active = [req for req in requirements if req["_quantity"] > 0]
    result.update(reviewed_production_orders=sorted({r["production_order"] for r in requirements}),
                  affected_production_orders=sorted(affected), total_required=total,
                  total_available=sum((row["covered_at_need"] for row in projected), Decimal(0)),
                  initial_available_inventory=free + sum(own.values(), Decimal(0)), total_shortage=shortage,
                  allocations_at_need=[row["covered_at_need"] for row in projected],
                  shortages_at_need=[row["shortage_at_need"] for row in projected],
                  confirmed_supply_quantity=sum((row["quantity"] for row in confirmed), Decimal(0)),
                  disruption_days=max(Decimal(0), Decimal(str((max(r["available_at"] for r in confirmed) - max(r["available_at"] for r in original)).total_seconds())) / Decimal(86400)),
                  hours_to_first_relevant_demand=Decimal(str((active[0]["_need"] - now).total_seconds())) / 3600 if active else None,
                  uncovered_resource_ratio=shortage / total if total else Decimal(0),
                  qualified_alternative_available=data.get("qualified_alternative_available"),
                  has_operational_impact=bool(affected),
                  source_refs=[f"erp:{result['snapshot_id']}/purchase-orders/{facts['purchase_order']}/{facts['purchase_order_item']}"])
    proposal = facts.get("proposed_partial")
    if proposal:
        if proposal.get("status") != "PROPOSED" or proposal.get("replaces_quantity_from_final_delivery") is not True:
            raise DomainValidationError("Partial offer must explicitly be proposed and replace final-delivery quantity")
        quantity = number(proposal.get("quantity"), "proposed_partial.quantity")
        proposed_at = timestamp(proposal.get("available_at"), "proposed_partial.available_at")
        revised = deepcopy(confirmed)
        if quantity > revised[-1]["quantity"] or proposed_at >= revised[-1]["available_at"]:
            raise DomainValidationError("Proposed split exceeds or does not precede final confirmed delivery")
        revised[-1]["quantity"] -= quantity
        revised.append({"quantity": quantity, "available_at": proposed_at})
        result["proposals"] = [deepcopy(proposal)]
        hypothetical_facts = {**facts, "confirmed_supply_schedule": [{"quantity": r["quantity"], "available_at": _iso(r["available_at"]), "status": "CONFIRMED"} for r in revised]}
        hypothetical_facts.pop("proposed_partial", None)
        hypothetical = _empty(result, facts)
        _supplier(hypothetical, data, hypothetical_facts, now)
        _finish(hypothetical)
        result["what_if"] = {"label": "Unconfirmed split: hypothetical only", "impact": _json(hypothetical), "risk": evaluate_risk(_json(hypothetical))}


def _overlap(start: datetime, end: datetime, other_start: datetime, other_end: datetime) -> Decimal:
    return Decimal(str(max(0, (min(end, other_end) - max(start, other_start)).total_seconds()))) / 3600


def _machine(result: Json, data: Json, facts: Json, now: datetime) -> None:
    machines = _unique(_required(data, "machines"), "machine_id")
    machine_id = str(_required(facts, "machine_id"))
    if machine_id not in machines:
        raise DomainValidationError("Machine is not present in ERP")
    outage_start = timestamp(facts.get("outage_start_at"), "outage_start_at")
    outage_end = timestamp(facts.get("outage_end_at"), "outage_end_at")
    if outage_end <= outage_start:
        raise DomainValidationError("outage_end_at must follow outage_start_at")
    all_operations = deepcopy(_required(data, "production_operations"))
    _unique(all_operations, "operation_id")
    operations = [op for op in all_operations if op.get("machine_id") == machine_id]
    calendar = deepcopy(_required(data, "capacity_calendar"))
    for slot in calendar:
        slot["_start"] = timestamp(slot.get("start_at"), "capacity.start_at")
        slot["_end"] = timestamp(slot.get("end_at"), "capacity.end_at")
        slot["_free"] = number(slot.get("available_hours"), "capacity.available_hours")
        slot["_busy"] = []
        if slot["_end"] <= slot["_start"] or slot["_free"] > _overlap(slot["_start"], slot["_end"], slot["_start"], slot["_end"]):
            raise DomainValidationError("Invalid capacity calendar interval")
        if slot.get("machine_id") not in machines:
            raise DomainValidationError("Capacity calendar references an unknown machine")
    for machine in machines:
        slots = sorted((s for s in calendar if s["machine_id"] == machine), key=lambda s: s["_start"])
        if any(a["_end"] > b["_start"] for a, b in zip(slots, slots[1:])):
            raise DomainValidationError("Overlapping capacity calendar would double-count capacity")
    total, missing = Decimal(0), Decimal(0)
    result["strategic_customer_affected"] = False
    affected = set()
    alternatives = []
    baseline_calendar = deepcopy(calendar)

    def fits(slot: Json, start: datetime, end: datetime, hours: Decimal) -> bool:
        return (slot["_start"] <= start and slot["_end"] >= end and slot["_free"] >= hours
                and all(_overlap(start, end, a, b) == 0 for a, b in slot["_busy"]))

    def reserve(slot: Json, start: datetime, end: datetime, hours: Decimal) -> None:
        slot["_free"] -= hours
        slot["_busy"].append((start, end))

    # Validate all baseline bookings, including alternative-machine commitments.
    for op in all_operations:
        if op.get("machine_id") not in machines:
            raise DomainValidationError("Operation refers to an unknown machine")
        assigned_machine = machines[op["machine_id"]]
        if assigned_machine.get("site") != op.get("site") or op.get("required_capability") not in assigned_machine.get("capabilities", []):
            raise DomainValidationError("Baseline operation has no qualified assigned machine")
        op["_start"] = timestamp(op.get("start_at"), "operation.start_at")
        op["_end"] = timestamp(op.get("end_at"), "operation.end_at")
        op["_hours"] = number(op.get("required_hours"), "operation.required_hours")
        duration = _overlap(op["_start"], op["_end"], op["_start"], op["_end"])
        if duration <= 0 or op["_hours"] > duration:
            raise DomainValidationError("Operation hours exceed the scheduled interval")
        baseline_slots = [s for s in baseline_calendar if s["machine_id"] == op["machine_id"] and fits(s, op["_start"], op["_end"], op["_hours"])]
        if not baseline_slots:
            raise DomainValidationError("Planned operation has no verified non-overlapping baseline capacity")
        reserve(baseline_slots[0], op["_start"], op["_end"], op["_hours"])
        overlap = _overlap(op["_start"], op["_end"], outage_start, outage_end) if op["machine_id"] == machine_id else Decimal(0)
        op["_gap"] = op["_hours"] * overlap / duration
        if not op["_gap"]:
            matching = [s for s in calendar if s["machine_id"] == op["machine_id"] and fits(s, op["_start"], op["_end"], op["_hours"])]
            if not matching:
                raise DomainValidationError("Planned operation has no verified baseline capacity")
            reserve(matching[0], op["_start"], op["_end"], op["_hours"])
    for op in sorted(operations, key=lambda o: (o["_start"], o["operation_id"])):
        total += op["_hours"]
        missing += op["_gap"]
        completion = op["_end"]
        candidate = None
        if op["_gap"]:
            affected.add(op["production_order"])
            available = []
            for slot in calendar:
                if slot["machine_id"] != machine_id:
                    continue
                starts = sorted({max(slot["_start"], outage_end)} | {end for _, end in slot["_busy"] if end >= outage_end})
                for start in starts:
                    end = start + timedelta(hours=float(op["_hours"]))
                    if fits(slot, start, end, op["_hours"]):
                        available.append((start, end, slot))
                        break
            available.sort(key=lambda value: value[0])
            # First scope does not split an operation: allocate the full operation.
            if available:
                start, completion, slot = available[0]
                reserve(slot, start, completion, op["_hours"])
            else:
                completion = None
            for slot in sorted(calendar, key=lambda s: s["_start"]):
                machine = machines[slot["machine_id"]]
                if (slot["machine_id"] != machine_id and machine.get("site") == op.get("site")
                        and op.get("required_capability") in machine.get("capabilities", [])
                        and fits(slot, op["_start"], op["_end"], op["_hours"])):
                    candidate = {"operation_id": op["operation_id"], "production_order": op["production_order"],
                                 "machine_id": slot["machine_id"], "start_at": _iso(op["_start"]), "end_at": _iso(op["_end"]),
                                 "required_hours": op["_hours"], "capability": op["required_capability"], "site": op["site"],
                                 "status": "PROPOSED", "capacity_reserved": False}
                    reserve(slot, op["_start"], op["_end"], op["_hours"])  # Only within the hypothetical proposal, never persisted.
                    alternatives.append(candidate)
                    break
            for sales in _sales_for(data, op):
                if completion is None or completion > timestamp(sales.get("customer_due_at"), "customer_due_at"):
                    _register_sales(result, sales)
        result["baseline"].append({"operation_id": op["operation_id"], "production_order": op["production_order"], "completion_at": op["_end"], "required_hours": op["_hours"]})
        result["projected"].append({"operation_id": op["operation_id"], "production_order": op["production_order"], "completion_at": completion, "capacity_gap_hours": op["_gap"], "affected": bool(op["_gap"]), "alternative": candidate})
    result.update(reviewed_production_orders=sorted({op["production_order"] for op in operations}),
                  affected_production_orders=sorted(affected), total_required=total, total_available=total-missing,
                  total_shortage=missing, required_hours=total, uncovered_hours=missing,
                  disruption_days=Decimal(str((outage_end-outage_start).total_seconds())) / 86400,
                  hours_to_first_relevant_demand=Decimal(str((min(op["_start"] for op in operations)-now).total_seconds())) / 3600 if operations else None,
                  uncovered_resource_ratio=missing/total if total else Decimal(0),
                  qualified_alternative_available=len(alternatives) == len([op for op in operations if op["_gap"] > 0]),
                  has_operational_impact=bool(affected), proposals=alternatives,
                  source_refs=[f"erp:{result['snapshot_id']}/machines/{machine_id}/capacity-calendar"])


def _quality(result: Json, data: Json, facts: Json, now: datetime) -> None:
    lot_id = str(_required(facts, "lot_id"))
    lots = _unique(_required(data, "inventory_lots"), "lot_id")
    inspections = _unique(_required(data, "quality_inspections"), "inspection_id")
    inspection = inspections.get(str(_required(facts, "inspection_id")))
    if lot_id not in lots or facts.get("material") != lots[lot_id].get("material"):
        raise DomainValidationError("Quality lot/material cannot be uniquely verified")
    quantity = number(facts.get("reported_quantity"), "reported_quantity")
    physical = number(lots[lot_id].get("physical_quantity"), "physical_quantity")
    if (not inspection or inspection.get("lot_id") != lot_id or inspection.get("material") != facts.get("material")
            or inspection.get("verified") is not True or inspection.get("result") != "FAILED"):
        raise DomainValidationError("Urgent review: no verified failed ERP quality inspection")
    inspected_at = timestamp(inspection.get("inspected_at"), "inspected_at")
    if inspected_at > now:
        raise DomainValidationError("Quality inspection occurs after the analysis snapshot")
    inspected = number(inspection.get("inspected_quantity"), "inspected_quantity")
    if quantity > inspected or quantity > physical or facts.get("defect_type") != inspection.get("defect_type"):
        raise DomainValidationError("Reported defect quantity/type disagrees with the verified inspection")
    dispositions = _unique(data.get("quality_dispositions", []), "disposition_id")
    released_disposition = None
    for disposition in dispositions.values():
        if (disposition.get("lot_id") != lot_id or disposition.get("inspection_id") != inspection["inspection_id"]
                or disposition.get("verified") is not True or disposition.get("result") != "RELEASED"):
            continue
        evidence = disposition.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            raise DomainValidationError("Verified quality disposition requires nonempty evidence")
        decided_at = timestamp(disposition.get("decided_at"), "quality_disposition.decided_at")
        if decided_at < inspected_at or decided_at > now:
            raise DomainValidationError("Quality disposition must follow the failed inspection and precede the analysis snapshot")
        if lots[lot_id].get("quality_status") == "RELEASED":
            if released_disposition is None or decided_at > timestamp(released_disposition["decided_at"]):
                released_disposition = disposition
    shipments = _unique(_required(data, "shipments"), "shipment_id")
    items = _unique(_required(data, "shipment_items"), "shipment_item_id")
    allocations = [x for x in _required(data, "lot_allocations") if x.get("lot_id") == lot_id]
    allocated = sum((number(x.get("quantity"), "lot_allocation.quantity") for x in allocations), Decimal(0))
    if allocated > physical or allocated > inspected:
        raise DomainValidationError("Lot allocations exceed physical/verified inspected quantity")
    blocked, shipped = Decimal(0), Decimal(0)
    result["strategic_customer_affected"] = False
    result["trace"] = []
    demand_times = []
    for allocation in allocations:
        item = items.get(allocation.get("shipment_item_id"))
        if not item or item.get("shipment_id") not in shipments:
            raise DomainValidationError("Incomplete lot-to-shipment trace")
        shipment = shipments[item["shipment_id"]]
        qty = number(allocation["quantity"], "lot_allocation.quantity")
        if shipment.get("status") not in ("PENDING", "BLOCKED", "SHIPPED"):
            raise DomainValidationError("Unknown shipment status")
        is_shipped = shipment["status"] == "SHIPPED"
        shipped += qty if is_shipped else 0
        blocked += 0 if is_shipped or released_disposition else qty
        demand_times.append(timestamp(shipment.get("scheduled_at"), "scheduled_at"))
        result["trace"].append({"lot_id": lot_id, "inspection_id": inspection["inspection_id"],
                                "shipment_id": shipment["shipment_id"], "shipment_item_id": item["shipment_item_id"],
                                "sales_line": item["sales_line"], "quantity": qty, "shipment_status": shipment["status"],
                                "disposition_id": released_disposition["disposition_id"] if released_disposition else None})
        if not is_shipped and qty and not released_disposition:
            _register_sales(result, item)
    replacement = data.get("replacement_available_at")
    disruption = max(Decimal(0), Decimal(str((timestamp(replacement, "replacement_available_at") - now).total_seconds()))/86400) if replacement else None
    covered = allocated - shipped if released_disposition else Decimal(0)
    result.update(blockable_quantity=blocked, shipped_quantity=shipped, unusable_inventory_quantity=0 if released_disposition else physical,
                  usable_inventory_quantity=physical if released_disposition else 0, total_required=allocated,
                  total_shortage=allocated-covered, total_available=covered,
                  disruption_days=0 if released_disposition and not shipped else disruption,
                  hours_to_first_relevant_demand=Decimal(str((min(demand_times)-now).total_seconds()))/3600 if demand_times else None,
                  uncovered_resource_ratio=(allocated-covered)/allocated if allocated else Decimal(0),
                  qualified_alternative_available=data.get("qualified_alternative_available"),
                  has_operational_impact=bool(allocated-covered),
                  hard_override="VERIFIED_DEFECTIVE_LOT_PENDING_SHIPMENT" if blocked else None,
                  source_refs=[f"erp:{result['snapshot_id']}/quality-inspections/{inspection['inspection_id']}"])
    result["verified_disposition"] = deepcopy(released_disposition)
    if released_disposition:
        result["source_refs"].append(f"erp:{result['snapshot_id']}/quality-dispositions/{released_disposition['disposition_id']}")
    if shipped:
        result["review_reasons"].append("Verified defective lot already shipped: manager escalation and disposition review; no recall executed")
    if blocked:
        result["proposals"] = [{"lot_id": lot_id, "inspection_id": inspection["inspection_id"], "quantity": blocked,
                                "shipment_item_ids": sorted({t["shipment_item_id"] for t in result["trace"] if t["shipment_status"] != "SHIPPED"}),
                                "status": "PROPOSED", "requires_quality_approval": True}]


def _finish(result: Json) -> None:
    result["affected_sales_lines"] = sorted(result["sales_line_values"])
    result["affected_open_order_value_cents"] = sum(result["sales_line_values"].values())
    result["data_complete"] = not result["review_reasons"]
    result["impact_status"] = "MANUAL_REVIEW" if result["review_reasons"] else ("OPERATIONAL_IMPACT" if result["has_operational_impact"] else "NO_OPERATIONAL_IMPACT")


def evaluate_impact(snapshot: Json, facts: Json) -> Json:
    result = _empty(snapshot, facts)
    try:
        data, now = _snapshot(snapshot, facts)
        handler = {"SUPPLIER_DELAY": _supplier, "MACHINE_BREAKDOWN": _machine, "QUALITY_ISSUE": _quality}.get(facts.get("incident_type"))
        if not handler:
            raise DomainValidationError("Unsupported incident_type")
        handler(result, data, facts, now)
        _finish(result)
    except (DomainValidationError, KeyError, TypeError, AttributeError) as error:
        # Partial arithmetic is not a reliable assessment after a validation error.
        result = _empty(snapshot, facts)
        result["review_reasons"] = [str(error)]
        result["impact_status"] = "MANUAL_REVIEW"
    return _json(result)


def evaluate_risk(impact: Json) -> Json:
    factors, details, missing = {}, {}, []
    override = impact.get("hard_override")
    result = {"policy_version": POLICY["version"], "data_complete": False, "risk_score": None,
              "severity": POLICY["hard_overrides"].get(override, "MANUAL_REVIEW"), "factors": factors,
              "factor_details": details, "missing_factors": missing, "override_reason": override,
              "explanation": ""}
    if impact.get("data_complete") is True and impact.get("has_operational_impact") is False and not override:
        result.update(data_complete=True, risk_score=0, severity="LOW", explanation="NO_OPERATIONAL_IMPACT: no additional impairment against the verified baseline.")
        return result
    for key, rule in POLICY["factors"].items():
        field = rule["field"]
        value = impact.get(field)
        try:
            if "boolean_points" in rule:
                points = rule["boolean_points"][str(_bool(value, field)).lower()]
            else:
                numeric = number(value, field, negative=key == "urgency")
                if key == "resource_gap" and numeric > 1:
                    raise DomainValidationError("resource gap exceeds 1")
                if key == "value" and numeric != numeric.to_integral_value():
                    raise DomainValidationError("value must contain whole cents")
                points = next(band["points"] for band in rule["bands"] if ("lte" not in band or numeric <= Decimal(str(band["lte"]))) and ("lt" not in band or numeric < Decimal(str(band["lt"]))))
            factors[key] = points
            details[key] = {"value": value, "points": points, "source": f"impact.{field}"}
        except (DomainValidationError, KeyError, StopIteration):
            missing.append(field)
    if impact.get("data_complete") is not True:
        missing.append("complete_consistent_erp_snapshot")
    if not missing:
        score = sum(factors.values())
        result.update(data_complete=True, risk_score=score, severity=POLICY["hard_overrides"].get(override) or next(b["name"] for b in POLICY["severity"] if score <= b["lte"]), explanation="Demo policy v1: " + " + ".join(str(p) for p in factors.values()) + f" = {score}. This is a prioritization score, not a loss probability.")
    else:
        result["explanation"] = "MANUAL_REVIEW: missing or inconsistent evidence for " + ", ".join(missing) + "."
    if override:
        result["explanation"] += f" Verified hard override: {override}."
    return result


_INJECTION = re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|system)|system\s*prompt|(?:run|execute)\s+(?:sql|shell|code|command)|(?:fetch|visit|open)\s+https?://|send\s+(?:secrets|credentials)|(?:recipient|webhook)\s*[:=]\s*https?://", re.I)


def extract_fixture(envelope: Json, snapshot: Json) -> Json:
    result = {"status": "MANUAL_REVIEW", "incident_type": None, "business_key": None,
              "facts": {}, "evidence": {}, "review_reasons": [], "provider": "fixture",
              "model": "fixture-v1", "prompt_version": "extraction-v1.0"}
    try:
        text = envelope.get("content_text", "")
        if not isinstance(text, str) or len(text.encode("utf-8")) > 65536:
            raise DomainValidationError("content_text exceeds 64 KiB or has invalid type")
        if envelope.get("attachments"):
            raise DomainValidationError("Attachments are unsupported; required attachment facts need manual review")
        if _INJECTION.search(text) or _INJECTION.search(json.dumps(envelope.get("payload", {}))):
            raise DomainValidationError("Instruction-like untrusted content: prompt-injection review")
        if envelope.get("source") == "EMAIL":
            if envelope.get("sender") != HERO["source_email"]["sender"]:
                raise DomainValidationError("Unknown supplier sender: no verified fixture supplier association")
            if text.replace("\r\n", "\n") != HERO["source_email"]["content_text"]:
                raise DomainValidationError("Unknown free text: fixture mode supports the exact supplied synthetic email only; live AI or structured input required")
            facts = {"incident_type": "SUPPLIER_DELAY", **{k: HERO[k] for k in ("purchase_order", "purchase_order_item", "material")},
                     "confirmed_supply_schedule": deepcopy(HERO["scenarios"][0]["confirmed_supply_schedule"]),
                     "proposed_partial": deepcopy(HERO["scenarios"][0]["proposed_partial"]), "reason": "Heat treatment capacity problems"}
            result["evidence"] = {key: {"value": deepcopy(value), "evidence": {"source": "content_text", "start": 0, "end": len(text), "quote": text}} for key, value in facts.items()}
        elif envelope.get("source") in ("API", "FORM"):
            facts = deepcopy(_required(envelope, "payload"))
            if not isinstance(facts, dict):
                raise DomainValidationError("payload must be typed incident facts")
            fields = {"SUPPLIER_DELAY": {"incident_type", "purchase_order", "purchase_order_item", "material", "confirmed_supply_schedule", "proposed_partial", "reason"},
                      "MACHINE_BREAKDOWN": {"incident_type", "machine_id", "outage_start_at", "outage_end_at", "reason"},
                      "QUALITY_ISSUE": {"incident_type", "lot_id", "inspection_id", "material", "reported_quantity", "defect_type", "reason"}}
            if facts.get("incident_type") not in fields or set(facts) - fields[facts["incident_type"]]:
                raise DomainValidationError("Unknown incident type or unsupported fact/action fields")
            result["evidence"] = {key: {"value": deepcopy(value), "evidence": {"source": "structured_payload", "pointer": f"/payload/{key}"}} for key, value in facts.items()}
        else:
            raise DomainValidationError("Unsupported source; use authenticated EMAIL, API or FORM")
        result["incident_type"] = facts.get("incident_type")
        verified = evaluate_impact(snapshot, facts)
        if verified["review_reasons"]:
            raise DomainValidationError("; ".join(verified["review_reasons"]))
        if facts["incident_type"] == "SUPPLIER_DELAY":
            key = f"SUPPLIER_DELAY:{facts['purchase_order']}:{facts['purchase_order_item']}"
        elif facts["incident_type"] == "MACHINE_BREAKDOWN":
            key = f"MACHINE_BREAKDOWN:{facts['machine_id']}"
        else:
            key = f"QUALITY_ISSUE:{facts['lot_id']}:{facts['inspection_id']}"
        result.update(status="VERIFIED", facts=_json(facts), business_key=key)
    except (DomainValidationError, TypeError, KeyError, ValueError) as error:
        result["review_reasons"] = [str(error)]
    return result


_ENGLISH_MONTHS = {name: index for index, name in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"), 1)}


def _evidence_span(envelope: Json, quote: Any, field: str) -> Json:
    if not isinstance(quote, str) or not quote.strip():
        raise DomainValidationError(f"{field}: an exact evidence quote is required")
    for source in ("content_text", "subject"):
        value = envelope.get(source, "")
        if isinstance(value, str):
            start = value.find(quote)
            if start >= 0:
                return {"source": source, "start": start, "end": start + len(quote), "quote": quote}
    raise DomainValidationError(f"{field}: evidence quote is not present in subject or content_text")


def _date_in_quote(value: Any, quote: str, field: str) -> None:
    expected = timestamp(value, field)
    candidates = []
    for match in re.finditer(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})\b", quote):
        candidates.append(timestamp(match.group(0), field + " evidence"))
    pattern = r"\b(\d{1,2}) (" + "|".join(_ENGLISH_MONTHS) + r") (\d{4}),? (\d{1,2}):(\d{2}) Bangkok time\b"
    for match in re.finditer(pattern, quote, re.I):
        month = next(number for name, number in _ENGLISH_MONTHS.items() if name.lower() == match.group(2).lower())
        try:
            local = datetime(int(match.group(3)), month, int(match.group(1)), int(match.group(4)),
                             int(match.group(5)), tzinfo=ZoneInfo("Asia/Bangkok"))
        except ValueError:
            raise DomainValidationError(f"{field}: invalid date in evidence quote") from None
        candidates.append(local.astimezone(timezone.utc))
    if expected not in candidates:
        raise DomainValidationError(f"{field}: extracted date is not mechanically supported by its evidence quote")


def _live_schedule(rows: Any, envelope: Json, field: str, status: str) -> tuple[Any, list[Json]]:
    if field == "confirmed_supply_schedule":
        if not isinstance(rows, list) or not rows:
            raise DomainValidationError("confirmed_supply_schedule: at least one confirmed entry is required")
        source_rows = rows
    else:
        if rows in (None, [], {}):
            return None, []
        if not isinstance(rows, dict):
            raise DomainValidationError("proposed_partial: one object or null is required")
        source_rows = [rows]
    clean, spans = [], []
    for index, row in enumerate(source_rows):
        if not isinstance(row, dict) or set(row) - {"quantity", "available_at", "status", "replaces_quantity_from_final_delivery", "evidence_quote"}:
            raise DomainValidationError(f"{field}[{index}]: unsupported model fields")
        if row.get("status") != status:
            raise DomainValidationError(f"{field}[{index}]: status must be {status}")
        quantity = number(_required(row, "quantity"), f"{field}[{index}].quantity")
        quote = _required(row, "evidence_quote")
        span = _evidence_span(envelope, quote, f"{field}[{index}]")
        if not re.search(rf"(?<!\d){re.escape(str(_json(quantity)))}(?!\d)", quote):
            raise DomainValidationError(f"{field}[{index}].quantity: value is not present in evidence quote")
        _date_in_quote(_required(row, "available_at"), quote, f"{field}[{index}].available_at")
        lowered = quote.lower()
        if status == "CONFIRMED" and ("confirm" not in lowered or "not confirmed" in lowered):
            raise DomainValidationError(f"{field}[{index}]: evidence does not establish confirmed availability")
        if status == "PROPOSED" and not any(term in lowered for term in ("may", "might", "could", "propos", "not confirmed")):
            raise DomainValidationError(f"{field}[{index}]: evidence does not establish a proposal")
        item = {"quantity": _json(quantity), "available_at": row["available_at"], "status": status}
        if status == "PROPOSED":
            item["replaces_quantity_from_final_delivery"] = _bool(
                row.get("replaces_quantity_from_final_delivery"),
                "proposed_partial.replaces_quantity_from_final_delivery")
        clean.append(item)
        spans.append({"value": deepcopy(item), "evidence": span})
    return (clean if field == "confirmed_supply_schedule" else clean[0]), spans


def verify_live_extraction(envelope: Json, snapshot: Json, candidate: Any, model: str,
                           response_metadata: Json | None = None) -> Json:
    """Turn an untrusted Gemini candidate into verified facts or manual review.

    Model output never supplies status, business identity, recipients or actions. Every
    accepted critical fact needs an exact source quote and must pass the deterministic
    ERP impact validator before it can enter the incident pipeline.
    """
    result = {"status": "MANUAL_REVIEW", "incident_type": None, "business_key": None,
              "facts": {}, "evidence": {}, "review_reasons": [], "provider": "google-gemini",
              "model": model, "prompt_version": "extraction-v2.0",
              "response_metadata": response_metadata or {}}
    try:
        text = envelope.get("content_text", "")
        subject = envelope.get("subject", "")
        if envelope.get("source") != "EMAIL" or envelope.get("ai_mode") != "live":
            raise DomainValidationError("Live extraction requires an EMAIL envelope explicitly marked ai_mode=live")
        if not isinstance(text, str) or not text.strip() or len(text.encode("utf-8")) > 65536:
            raise DomainValidationError("content_text exceeds 64 KiB, is empty or has invalid type")
        if not isinstance(subject, str) or len(subject) > 500:
            raise DomainValidationError("subject exceeds 500 characters or has invalid type")
        if envelope.get("attachments"):
            raise DomainValidationError("Attachments are unsupported; required attachment facts need manual review")
        if _INJECTION.search(text) or _INJECTION.search(subject):
            raise DomainValidationError("Instruction-like untrusted content: prompt-injection review")
        if not isinstance(candidate, dict):
            raise DomainValidationError("Gemini output must be one JSON object")
        allowed = {"incident_type", "purchase_order", "purchase_order_item", "material",
                   "confirmed_supply_schedule", "proposed_partial", "reason", "evidence", "ambiguities"}
        if set(candidate) - allowed:
            raise DomainValidationError("Gemini output contains unsupported fields")
        ambiguities = candidate.get("ambiguities", [])
        if ambiguities is None:
            ambiguities = []
        if not isinstance(ambiguities, list) or any(not isinstance(item, str) for item in ambiguities):
            raise DomainValidationError("ambiguities must be a list of strings")
        if ambiguities:
            raise DomainValidationError("Gemini reported ambiguity: " + "; ".join(ambiguities[:5]))
        if candidate.get("incident_type") != "SUPPLIER_DELAY":
            raise DomainValidationError("Email live extraction currently supports SUPPLIER_DELAY only")
        evidence_quotes = _required(candidate, "evidence")
        if not isinstance(evidence_quotes, dict) or set(evidence_quotes) != {"purchase_order", "purchase_order_item", "material", "reason"}:
            raise DomainValidationError("evidence must contain exactly purchase_order, purchase_order_item, material and reason quotes")
        facts = {"incident_type": "SUPPLIER_DELAY"}
        evidence = {"incident_type": {"value": "SUPPLIER_DELAY", "evidence": {"source": "workflow_contract"}}}
        for field in ("purchase_order", "purchase_order_item", "material", "reason"):
            value = _required(candidate, field)
            if not isinstance(value, str) or len(value) > 500:
                raise DomainValidationError(f"{field}: a bounded string is required")
            span = _evidence_span(envelope, evidence_quotes.get(field), field)
            if value.lower() not in span["quote"].lower():
                raise DomainValidationError(f"{field}: value is not present in evidence quote")
            facts[field] = value
            evidence[field] = {"value": value, "evidence": span}
        confirmed, confirmed_spans = _live_schedule(candidate.get("confirmed_supply_schedule"), envelope, "confirmed_supply_schedule", "CONFIRMED")
        proposed, proposed_spans = _live_schedule(candidate.get("proposed_partial"), envelope, "proposed_partial", "PROPOSED")
        facts["confirmed_supply_schedule"] = confirmed
        facts["proposed_partial"] = proposed
        evidence["confirmed_supply_schedule"] = {"value": confirmed, "evidence": confirmed_spans[0]["evidence"]}
        if proposed is not None:
            evidence["proposed_partial"] = {"value": proposed, "evidence": proposed_spans[0]["evidence"]}
        verified = evaluate_impact(snapshot, facts)
        if verified["review_reasons"]:
            raise DomainValidationError("; ".join(verified["review_reasons"]))
        result.update(status="VERIFIED", incident_type="SUPPLIER_DELAY", facts=_json(facts),
                      business_key=f"SUPPLIER_DELAY:{facts['purchase_order']}:{facts['purchase_order_item']}",
                      evidence=evidence)
    except (DomainValidationError, TypeError, KeyError, ValueError) as error:
        result["review_reasons"] = [str(error)]
    return result


def _summary(impact: Json, risk: Json) -> str:
    if not impact.get("data_complete") or not risk.get("data_complete"):
        return "Manual review required. " + " ".join(impact.get("review_reasons", [])) + " " + risk.get("explanation", "")
    amount = Decimal(impact["affected_open_order_value_cents"]) / 100
    return (f"{impact['incident_type']}: {len(impact['reviewed_production_orders'])} production orders reviewed; "
            f"{len(impact['affected_production_orders'])} affected. Resource shortage: {impact['total_shortage']}. "
            f"Affected open-order value: EUR {amount:,.2f}. Risk: {risk['risk_score']} / {risk['severity']}. "
            "Synthetic ERP assessment; affected value is not a forecast revenue loss.")


def validate_draft(candidate: str, impact: Json, risk: Json) -> Json:
    """Conservative fallback: only exact grounded template text is accepted.

    A future live adapter can supply a typed claims list. Until then unverified
    prose, including any changed number, ID, recipient or severity, is discarded.
    """
    template = _summary(impact, risk)
    return {"text": template, "mode": "deterministic-template", "candidate_accepted": candidate == template,
            "reason": None if candidate == template else "Unverified generated draft replaced with grounded template"}


def build_plan(impact: Json, risk: Json, incident_id: str, revision: int) -> Json:
    summary = _summary(impact, risk)
    plan = {"policy_version": CATALOG["version"], "summary": summary, "summary_mode": "deterministic-template",
            "sop_ids": [], "actions": [], "manager_review_required": risk.get("severity") == "CRITICAL"}
    if impact.get("has_operational_impact") is False and impact.get("data_complete"):
        return plan
    base = {"incident_id": incident_id, "incident_revision": revision}
    plan["actions"].append({"action_type": "INTERNAL_TICKET", "required_role": None,
                            "payload": {**base, "recipient": "operations@example.test", "title": f"{risk.get('severity')} incident {incident_id}", "body": summary}})
    if not impact.get("data_complete") or not risk.get("data_complete"):
        plan["sop_ids"] = ["SOP-MANUAL-REVIEW-v1"]
        return plan
    incident_type = impact.get("incident_type")
    if incident_type == "SUPPLIER_DELAY":
        plan["sop_ids"] = ["SOP-SUPPLIER-DELAY-v1"]
        role = "production_manager" if plan["manager_review_required"] else "purchasing"
        plan["actions"].append({"action_type": "SUPPLIER_EMAIL", "required_role": role,
                                "payload": {**base, "recipient": "supplier@example.test", "subject": f"Availability confirmation requested — {incident_id} revision {revision}",
                                            "body": "Dear Supplier,\n\n" + summary + "\n\nPlease confirm feasible material availability and any proposed split. An unconfirmed offer does not change our confirmed plan.\n\nSynthetic APIC purchasing team"}})
    elif incident_type == "MACHINE_BREAKDOWN":
        plan["sop_ids"] = ["SOP-MACHINE-BREAKDOWN-v1"]
        for proposal in impact.get("proposals", []):
            plan["actions"].append({"action_type": "RESCHEDULE", "required_role": "production_manager",
                                    "payload": {**base, **{key: proposal[key] for key in ("operation_id", "production_order", "machine_id", "start_at", "end_at", "required_hours", "capability", "site")}}})
    elif incident_type == "QUALITY_ISSUE":
        plan["sop_ids"] = ["SOP-QUALITY-ISSUE-v1"]
        for proposal in impact.get("proposals", []):
            plan["actions"].append({"action_type": "QUALITY_BLOCK", "required_role": "quality_manager",
                                    "payload": {**base, **{key: proposal[key] for key in ("lot_id", "inspection_id", "quantity", "shipment_item_ids")}}})
    return plan


def aggregate_values(impacts: list[Json]) -> Json:
    """Union current open assessments; conflicting line values are never hidden."""
    lines: dict[str, int] = {}
    scopes = {impact.get("scope_id") for impact in impacts if impact.get("scope_id")}
    reasons = []
    if len(scopes) > 1:
        return {"data_complete": False, "affected_open_order_value_cents": None, "currency": "EUR", "sales_line_values": {}, "affected_sales_lines": [], "review_reasons": ["Aggregation cannot mix demo scopes"]}
    for impact in impacts:
        if impact.get("is_current") is False or impact.get("status") in ("RESOLVED", "CLOSED") or impact.get("is_hypothetical"):
            continue
        for line in impact.get("affected_sales_lines", []):
            try:
                value = number(impact.get("sales_line_values", {}).get(line), "sales line value")
                if value != value.to_integral_value():
                    raise DomainValidationError("Non-integer cents")
                if line in lines and lines[line] != int(value):
                    raise DomainValidationError(f"Conflicting current values for sales line {line}")
                lines[line] = int(value)
            except DomainValidationError as error:
                reasons.append(str(error))
    return {"data_complete": not reasons, "affected_open_order_value_cents": sum(lines.values()) if not reasons else None,
            "currency": "EUR", "sales_line_values": lines, "affected_sales_lines": sorted(lines), "review_reasons": reasons,
            "aggregation": "union of unique open sales positions"}
