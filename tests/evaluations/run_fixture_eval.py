"""Run the frozen fixture evaluation. Makes zero network/provider calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.domain import extract_fixture


def metric(numerator, denominator):
    return {"numerator":numerator,"denominator":denominator,"ratio":round(numerator/denominator,6) if denominator else None}


def critical_fields(facts):
    if facts is None:
        return {}
    values = {key:facts[key] for key in ("purchase_order","purchase_order_item","material") if key in facts}
    if "confirmed_supply_schedule" in facts:
        values["dates"]=[r.get("available_at") for r in facts["confirmed_supply_schedule"]]
        values["quantities"]=[r.get("quantity") for r in facts["confirmed_supply_schedule"]]
    elif "outage_start_at" in facts:
        values["dates"]=[facts.get("outage_start_at"),facts.get("outage_end_at")]
    elif "reported_quantity" in facts:
        values["quantities"]=[facts["reported_quantity"]]
    return values


def main():
    source = ROOT / "fixtures/evaluation-v1.json"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == source.with_suffix(".sha256").read_text(encoding="utf-8").strip(), "Frozen dataset changed"
    dataset = json.loads(source.read_text(encoding="utf-8"))
    results=[]
    for case in dataset["cases"]:
        start=time.perf_counter()
        output=extract_fixture(case["envelope"],case["snapshot"])
        latency=(time.perf_counter()-start)*1000
        truth=case["ground_truth"]
        expected_fields=critical_fields(truth["facts"])
        actual_fields=critical_fields(output["facts"])
        schema_valid=(output.get("status") in ("VERIFIED","MANUAL_REVIEW") and isinstance(output.get("facts"),dict)
                      and isinstance(output.get("review_reasons"),list) and output.get("provider")=="fixture")
        results.append({"id":case["id"],"split":case["split"],"scenario":case["scenario"],"status":output["status"],
                        "expected_status":truth["status"],"decision_correct":output["status"]==truth["status"],
                        "incident_type_correct":output["incident_type"]==truth["incident_type"],
                        "facts_exact_match":output["facts"]==truth["facts"] if truth["facts"] is not None else None,
                        "field_exact_matches":{key:actual_fields.get(key)==value for key,value in expected_fields.items()},
                        "mandatory_review":truth["mandatory_review"],"schema_valid":schema_valid,
                        "latency_ms":round(latency,4),"review_reasons":output["review_reasons"],
                        "unsubstantiated_automatic_facts":output["status"]=="VERIFIED" and output["facts"]!=truth["facts"]})
    splits={}
    for split in ("development","holdout"):
        rows=[r for r in results if r["split"]==split]
        auto=[r for r in rows if r["status"]=="VERIFIED"]
        exact=[r for r in rows if r["facts_exact_match"] is not None]
        review=[r for r in rows if r["mandatory_review"]]
        latencies=sorted(r["latency_ms"] for r in rows)
        splits[split]={"cases":len(rows),"decision_accuracy":metric(sum(r["decision_correct"] for r in rows),len(rows)),
                       "incident_type_accuracy":metric(sum(r["incident_type_correct"] for r in rows),len(rows)),
                       "critical_facts_exact_match":metric(sum(r["facts_exact_match"] for r in exact),len(exact)),
                       "schema_valid_or_review":metric(sum(r["schema_valid"] for r in rows),len(rows)),
                       "mandatory_review_recall":metric(sum(r["status"]=="MANUAL_REVIEW" for r in review),len(review)),
                       "automatic_processing_rate":metric(len(auto),len(rows)),
                       "unsubstantiated_critical_facts_rate":metric(sum(r["unsubstantiated_automatic_facts"] for r in auto),len(auto)),
                       "latency_ms":{"p50":statistics.median(latencies),"p95":latencies[max(0,int(len(latencies)*.95)-1)]}}
        splits[split]["critical_field_metrics"]={key:metric(sum(r["field_exact_matches"].get(key,False) for r in rows),sum(key in r["field_exact_matches"] for r in rows)) for key in ("purchase_order","purchase_order_item","material","dates","quantities")}
    report={"run_at":datetime.now(timezone.utc).isoformat(),"status":"LOCAL_TESTED","evaluation_mode":"deterministic fixture and structured-input validation; not model evaluation",
            "dataset_version":dataset["dataset_version"],"dataset_sha256":digest,"provider":"fixture","model":"fixture-v1","prompt_version":"extraction-v1.0",
            "live_evaluation":"LIVE_EVAL_NOT_RUN","live_blocker":"No authorized configured live-model credential, model and call/cost budget available for this run",
            "provider_calls":0,"measured_provider_cost_eur":0,"splits":splits,"results":results,
            "limitations":["Structured API/form validation and exact known-email mapping do not establish free-text LLM accuracy.",
                            "Unsupported free text is intentionally reviewed, so incident-type accuracy can be below the live-model target.",
                            "Transport deduplication belongs to integration tests; duplicate inputs here test deterministic normalization only."]}
    destination=ROOT / "evidence/evaluations/fixture-v1-report.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(destination),"splits":splits,"live_evaluation":"LIVE_EVAL_NOT_RUN"},indent=2))
    if any(not r["decision_correct"] or not r["schema_valid"] or r["unsubstantiated_automatic_facts"] for r in results):
        raise SystemExit(1)


if __name__=="__main__": main()
