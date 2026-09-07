"""Focused acceptance gaps at genuine PostgreSQL/API boundaries.

Uses the explicit setup and helpers from test_api. No n8n/cloud execution is
claimed, no provider is dispatched, and each case changes only its own isolated
synthetic integration scope. Authored tests are not passes until executed.
"""
from copy import deepcopy

import pytest

from test_api import (action_context, env, envelope, pipeline, post, setup)
from backend.db import js, transaction


def read_fixture_data(t, kind):
    with transaction() as conn:
        return deepcopy(conn.execute(
            "SELECT body FROM erp.fixture_data WHERE scope_id=%s AND incident_type=%s",
            (t["sid"], kind),
        ).fetchone()["body"])


def write_fixture_data(t, kind, data):
    with transaction() as conn:
        conn.execute("UPDATE erp.fixture_data SET body=%s WHERE scope_id=%s AND incident_type=%s",
                     (js(data), t["sid"], kind))
        conn.execute("UPDATE ops.scopes SET erp_revision=erp_revision+1 WHERE id=%s", (t["sid"],))


def assert_no_actions_or_approvals(t):
    client = t["clients"]["viewer"]
    for route in ("/api/actions", "/api/approvals"):
        response = client.get(route, params={"scope_id": t["sid"]})
        assert response.status_code == 200, response.text
        assert response.json()["items"] == []
    with transaction() as conn:
        assert conn.execute("SELECT count(*) AS n FROM ops.provider_receipts WHERE scope_id=%s",
                            (t["sid"],)).fetchone()["n"] == 0


@pytest.mark.parametrize("ambiguity", ["multiple_positions", "missing_year"])
def test_ambiguous_po_position_or_missing_year_enters_persisted_review(setup, ambiguity):
    """AC09: no inferred PO item or year can create downstream actions."""
    t = setup
    data = read_fixture_data(t, "SUPPLIER_DELAY")
    body = envelope(t, "supplier-split")
    if ambiguity == "multiple_positions":
        with transaction() as conn:
            conn.execute("""INSERT INTO erp.purchase_order_items
                (scope_id,id,purchase_order_id,material_id,ordered_quantity,open_quantity)
                VALUES (%s,'4500192/20','4500192','SHAFT-DN300',40,40)""", (t["sid"],))
        data["purchase_order_items"] = [
            {"purchase_order": "4500192", "purchase_order_item": "10", "material": "SHAFT-DN300"},
            {"purchase_order": "4500192", "purchase_order_item": "20", "material": "SHAFT-DN300"},
        ]
        write_fixture_data(t, "SUPPLIER_DELAY", data)
        body["payload"].pop("purchase_order_item")
        expected_reason = "purchase_order_item"
    else:
        body["payload"]["confirmed_supply_schedule"][0]["available_at"] = "13 October 08:00 Bangkok"
        expected_reason = "full date with year"
    result = pipeline(t, body)
    assert result["status"] == "MANUAL_REVIEW" and result["skip_analysis"]
    assert expected_reason in " ".join(result["review_reasons"])
    status = t["clients"]["viewer"].get(f"/api/source-events/{result['source_event_id']}",
                                       params={"scope_id": t["sid"]})
    assert status.status_code == 200, status.text
    assert status.json()["status"] == "MANUAL_REVIEW"
    assert_no_actions_or_approvals(t)


def assessed_stage(t, source):
    """Stop before plan persistence so the actual service gate sees the draft."""
    accepted = post(t, "/internal/source-events", source)
    claim = post(t, "/internal/jobs/claim", {"job_id": accepted["job_id"], "owner": "acceptance-edge",
                                            "execution_id": "api-edge-assessment", "workflow_id": "WF03-test"})
    stage = post(t, "/internal/jobs/context", claim["items"][0])
    extraction = post(t, "/internal/extract", {"envelope": stage["envelope"], "snapshot": stage["snapshot"]})
    assert extraction["status"] == "VERIFIED", extraction
    stage = post(t, "/internal/incidents/correlate", {**stage, "extraction": extraction})
    assessment = post(t, "/internal/impact/evaluate", {"snapshot": stage["snapshot"], "facts": stage["facts"]})
    stage = post(t, "/internal/impact/save", {**stage, "impact": assessment})
    risk = post(t, "/internal/risk/evaluate", {"impact": assessment})
    draft = post(t, "/internal/plans/draft", {"impact": assessment, "risk": risk,
                                              "incident_id": stage["incident_id"], "revision": stage["revision"]})
    return stage, risk, draft


def test_tampered_draft_is_replaced_before_plan_persistence_and_dispatch(setup):
    """AC13: false quantities and a foreign recipient cannot bypass grounding."""
    t = setup
    stage, risk, grounded = assessed_stage(t, envelope(t))
    tampered = deepcopy(grounded)
    tampered["summary"] = "9999 units available; no shortage; score 0 LOW."
    mail = next(a for a in tampered["actions"] if a["action_type"] == "SUPPLIER_EMAIL")
    mail["payload"].update(recipient="attacker@example.test", body="9999 units available; score 0 LOW.")
    saved = post(t, "/internal/plans", {**stage, "risk": risk, "plan": tampered})
    with transaction() as conn:
        stored = conn.execute("SELECT body FROM ops.action_plans WHERE scope_id=%s AND id=%s",
                              (t["sid"], saved["plan_id"])).fetchone()["body"]
    assert stored == grounded
    assert saved["plan"] == grounded
    actions = t["clients"]["viewer"].get("/api/actions", params={"scope_id": t["sid"]}).json()["items"]
    actual_mail = next(a for a in actions if a["action_type"] == "SUPPLIER_EMAIL")
    expected_mail = next(a for a in grounded["actions"] if a["action_type"] == "SUPPLIER_EMAIL")
    assert actual_mail["payload"] == expected_mail["payload"]
    assert actual_mail["payload"]["recipient"] == "supplier@example.test"
    assert "9999" not in actual_mail["payload"]["body"]
    assert post(t, "/internal/actions/claim", action_context(t, actual_mail["id"]))["can_execute"] is False
    with transaction() as conn:
        assert conn.execute("SELECT count(*) AS n FROM ops.provider_receipts WHERE scope_id=%s",
                            (t["sid"],)).fetchone()["n"] == 0
    post(t, "/internal/jobs/complete", saved)


def test_unverified_quality_has_no_incident_action_or_approval(setup):
    """AC26: urgent persisted review does not invent failed-inspection evidence."""
    t = setup
    data = read_fixture_data(t, "QUALITY_ISSUE")
    data["quality_inspections"][0]["verified"] = False
    with transaction() as conn:
        conn.execute("UPDATE erp.quality_inspections SET verified=false WHERE scope_id=%s AND id='QI-100'",
                     (t["sid"],))
    write_fixture_data(t, "QUALITY_ISSUE", data)
    result = pipeline(t, envelope(t, "quality"))
    assert result["status"] == "MANUAL_REVIEW" and result["skip_analysis"]
    assert "Urgent review: no verified failed ERP quality inspection" in " ".join(result["review_reasons"])
    response = t["clients"]["viewer"].get("/api/incidents", params={"scope_id": t["sid"]})
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert_no_actions_or_approvals(t)


def test_genuinely_computed_low_supplier_mail_still_cannot_dispatch_unapproved(setup):
    """AC35: the deterministic policy computes LOW from actual fixture facts."""
    t = setup
    data = read_fixture_data(t, "SUPPLIER_DELAY")
    requirement = deepcopy(data["production_requirements"][0])
    requirement.update(required_quantity=15, need_at="2026-10-20T08:00:00+07:00",
                       customer_due_at="2026-10-22T08:00:00+07:00", open_net_line_value_cents=10000,
                       strategic_customer=False)
    data["production_requirements"] = [requirement]
    data["qualified_alternative_available"] = True
    with transaction() as conn:
        conn.execute("UPDATE erp.supply_schedules SET available_at='2026-10-20T01:00:00Z' WHERE scope_id=%s",
                     (t["sid"],))
        conn.execute("DELETE FROM erp.production_requirements WHERE scope_id=%s AND id!='REQ-MO-1001'", (t["sid"],))
        conn.execute("UPDATE erp.production_requirements SET quantity=15,need_at='2026-10-20T01:00:00Z' WHERE scope_id=%s AND id='REQ-MO-1001'", (t["sid"],))
        conn.execute("UPDATE erp.production_orders SET quantity=15 WHERE scope_id=%s AND id='MO-1001'", (t["sid"],))
        conn.execute("UPDATE erp.production_sales_allocations SET quantity=15 WHERE scope_id=%s AND production_order_id='MO-1001'", (t["sid"],))
        conn.execute("UPDATE erp.sales_order_items SET open_quantity=15,open_net_line_value_cents=10000,customer_due_at='2026-10-22T01:00:00Z' WHERE scope_id=%s AND id='SO-2000/10'", (t["sid"],))
    write_fixture_data(t, "SUPPLIER_DELAY", data)
    body = envelope(t, "supplier-split")
    body["payload"]["confirmed_supply_schedule"] = [{"quantity": 40, "available_at": "2026-10-21T08:00:00+07:00", "status": "CONFIRMED"}]
    result = pipeline(t, body)
    assert result["impact"]["has_operational_impact"] is True
    assert result["impact"]["total_shortage"] == 1
    assert 0 < result["risk"]["risk_score"] < 25
    assert result["risk"]["severity"] == "LOW"
    assert result["risk"]["risk_score"] == sum(result["risk"]["factors"].values())
    approvals = t["clients"]["viewer"].get("/api/approvals", params={"scope_id": t["sid"]}).json()["items"]
    assert len(approvals) == 1 and approvals[0]["required_role"] == "purchasing" and approvals[0]["status"] == "PENDING"
    actions = t["clients"]["viewer"].get("/api/actions", params={"scope_id": t["sid"]}).json()["items"]
    mail = next(a for a in actions if a["action_type"] == "SUPPLIER_EMAIL")
    assert mail["status"] == "WAITING_APPROVAL"
    assert post(t, "/internal/actions/claim", action_context(t, mail["id"]))["can_execute"] is False
    with transaction() as conn:
        assert conn.execute("SELECT count(*) AS n FROM ops.provider_receipts WHERE scope_id=%s",
                            (t["sid"],)).fetchone()["n"] == 0


def test_dashboard_unions_same_sales_position_across_two_current_incidents(setup):
    """AC11: two real persisted assessments share one scoped sales position."""
    t = setup
    supplier_data = read_fixture_data(t, "SUPPLIER_DELAY")
    machine_data = read_fixture_data(t, "MACHINE_BREAKDOWN")
    shared = supplier_data["production_requirements"][1]
    due = "2026-10-12T16:00:00+07:00"
    shared["customer_due_at"] = due
    operation = machine_data["production_operations"][0]
    operation.update(sales_line=shared["sales_line"], open_net_line_value_cents=shared["open_net_line_value_cents"],
                     customer_due_at=due, strategic_customer=shared["strategic_customer"])
    with transaction() as conn:
        conn.execute("UPDATE erp.sales_order_items SET customer_due_at=%s WHERE scope_id=%s AND id=%s",
                     (due, t["sid"], shared["sales_line"]))
        conn.execute("UPDATE erp.production_sales_allocations SET sales_line_id=%s WHERE scope_id=%s AND production_order_id=%s",
                     (shared["sales_line"], t["sid"], operation["production_order"]))
    write_fixture_data(t, "SUPPLIER_DELAY", supplier_data)
    write_fixture_data(t, "MACHINE_BREAKDOWN", machine_data)
    supplier = pipeline(t)
    machine = pipeline(t, envelope(t, "machine"))
    assert supplier["incident_id"] != machine["incident_id"]
    assert shared["sales_line"] in supplier["impact"]["affected_sales_lines"]
    assert shared["sales_line"] in machine["impact"]["affected_sales_lines"]
    union = {**supplier["impact"]["sales_line_values"], **machine["impact"]["sales_line_values"]}
    expected = sum(union.values())
    naive_sum = supplier["impact"]["affected_open_order_value_cents"] + machine["impact"]["affected_open_order_value_cents"]
    assert naive_sum > expected
    response = t["clients"]["viewer"].get("/api/dashboard", params={"scope_id": t["sid"]})
    assert response.status_code == 200, response.text
    kpi = response.json()
    assert kpi["open_incidents"] == 2
    assert kpi["affected_open_order_value_cents"] == expected
    assert kpi["aggregation"] == "union of unique open sales positions"
