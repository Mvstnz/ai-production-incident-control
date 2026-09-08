"""One authorized synthetic Gemini mail run through dashboard API and published n8n.

The provider key stays in local ignored configuration/n8n credentials. Evidence
contains only model metadata, persisted outcome and n8n execution provenance.
"""
from datetime import datetime, timezone
import json

from runtime_client import Client, ROOT


SUBJECT = "Delivery update for PO DEMO-PO-8264 item 10"
CONTENT = """Hello Purchasing Team,

Material: DEMO-ROD-20
Purchase order PO DEMO-PO-8264, item 10.

Because of A broken delivery truck has delayed the steel rods needed for four mounting-frame orders., the new confirmed availability at your plant is 19 October 2026, 08:00 Berlin time, for the full quantity of 40 pcs.

We may be able to make 10 of these 40 pcs available at your plant on 13 October 2026, 08:00 Berlin time. This early partial delivery is not confirmed yet.

Best regards,
Synthetic Supplier"""


def main():
    client = Client("admin")
    source = client.ok("/api/demo/custom-email", {"subject": SUBJECT, "content_text": CONTENT})
    event = client.poll(source, seconds=120)
    assert event["job_status"] == "SUCCEEDED", event
    assert event["status"] == "VERIFIED", event
    detail = client.ok(f"/api/incidents/{event['incident_id']}?scope_id={source['scope_id']}")
    revision = detail["revisions"][-1]
    metadata = revision["extraction_metadata"]
    assert metadata["provider"] == "google-gemini"
    assert metadata["model"] == "models/gemini-3.1-flash-lite"
    assert metadata["prompt_version"] == "extraction-v2.0"
    response_metadata = metadata["response_metadata"]
    assert set(response_metadata) == {
        "request_id", "finish_reason", "prompt_tokens", "completion_tokens",
        "total_tokens", "latency_ms",
    }
    assert revision["facts"]["purchase_order"] == "DEMO-PO-8264"
    assert revision["facts"]["confirmed_supply_schedule"][0]["quantity"] == 40
    assert revision["facts"]["proposed_partial"]["status"] == "PROPOSED"
    assert detail["risk_score"] == 83 and detail["severity"] == "CRITICAL"
    system = client.ok("/api/system?scope_id=" + source["scope_id"])
    job = next(item for item in system["jobs"] if str(item["id"]) == source["job_id"])
    evidence = {
        "status": "PASS",
        "profile": "DEMO_LOCAL",
        "provider": metadata["provider"],
        "model": metadata["model"],
        "prompt_version": metadata["prompt_version"],
        "response_metadata_fields": sorted(response_metadata),
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "scope_id": source["scope_id"],
        "source_event_id": source["source_event_id"],
        "job_id": source["job_id"],
        "incident_id": event["incident_id"],
        "workflow_id": job["workflow_id"],
        "execution_id": job["execution_id"],
        "result": {"status": detail["status"], "risk_score": detail["risk_score"],
                   "severity": detail["severity"], "confirmed_quantity": 40,
                   "proposed_partial_status": "PROPOSED"},
        "boundary": "One synthetic live-provider smoke run; not a statistical model evaluation.",
    }
    path = ROOT / "evidence" / "workflow-runs" / "live-gemini-mail-smoke.json"
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "scope_id": source["scope_id"],
                      "incident_id": event["incident_id"], "execution_id": job["execution_id"]}))


if __name__ == "__main__":
    main()
