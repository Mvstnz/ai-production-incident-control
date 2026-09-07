"""Verify handoff arithmetic and document structure, NOT the future application.

Usage: python verify_handoff.py
Only Python's standard library is required. No network or external side effects.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def when(value: str) -> datetime:
    return datetime.fromisoformat(value)


def evaluate(fixture: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    demands = fixture['production_requirements']
    supply = scenario['confirmed_supply_schedule']
    require(sum(s['quantity'] for s in supply) == fixture['open_purchase_quantity'], 'Supply double counting')
    inv = fixture['inventory']
    stock = inv['physical'] - inv['reserved_for_other_demands'] - inv['quarantined']
    require(stock == inv['available_to_this_scope'], 'Inventory inconsistent')
    # This compact fixture oracle covers these specific dated requirements,
    # not a complete production implementation or general ERP/APS engine.
    events: list[tuple[datetime, int, int, int]] = []
    for idx, row in enumerate(supply):
        events.append((when(row['available_at']), 0, idx, row['quantity']))
    for idx, row in enumerate(demands):
        events.append((when(row['need_at']), 1, idx, row['required_quantity']))
    allocated = [0] * len(demands)
    shortage = [0] * len(demands)
    completed: dict[int, datetime] = {}
    backlog: list[list[int]] = []
    for timestamp, kind, idx, quantity in sorted(events):
        if kind == 0:
            stock += quantity
            for pending in backlog:
                take = min(stock, pending[1])
                stock -= take
                pending[1] -= take
                if pending[1] == 0 and pending[0] not in completed:
                    completed[pending[0]] = timestamp
            backlog = [b for b in backlog if b[1] > 0]
        else:
            allocated[idx] = min(stock, quantity)
            stock -= allocated[idx]
            shortage[idx] = quantity - allocated[idx]
            if shortage[idx]:
                backlog.append([idx, shortage[idx]])
            else:
                completed[idx] = timestamp
    impacted = [i for i, q in enumerate(shortage) if q]
    # Verify the impacted lines are actually late under the fixture's stated convention.
    at_risk = [i for i in impacted if completed[i] + timedelta(days=demands[i]['remaining_lead_time_calendar_days']) > when(demands[i]['customer_due_at'])]
    require(impacted == at_risk, 'Shortage does not match at-risk line assumption')
    unique_lines = {demands[i]['sales_line']: demands[i]['open_net_line_value_cents'] for i in at_risk}
    value_cents = sum(unique_lines.values())
    euros = Decimal(value_cents) / 100
    gap = Decimal(sum(shortage)) / sum(d['required_quantity'] for d in demands)
    hours = (min(when(d['need_at']) for d in demands) - when(fixture['analysis_time'])).total_seconds() / 3600
    days = (max(when(s['available_at']) for s in supply) - max(when(s['available_at']) for s in fixture['original_supply_schedule'])).total_seconds() / 86400
    factors = {
        'disruption': 0 if days == 0 else 10 if days <= 2 else 15 if days <= 5 else 20 if days <= 7 else 25,
        'value': 0 if euros == 0 else 5 if euros < 25000 else 10 if euros < 50000 else 15 if euros < 100000 else 20,
        'urgency': 0 if hours > 168 else 10 if hours > 72 else 16 if hours > 24 else 20,
        'resource_gap': 0 if gap == 0 else 5 if gap < Decimal('.25') else 8 if gap < Decimal('.50') else 12 if gap < Decimal('.75') else 15,
        'alternative': 0 if fixture['qualified_alternative_available'] else 10,
        'strategic_customer': 10 if any(demands[i]['strategic_customer'] for i in at_risk) else 0,
    }
    score = sum(factors.values())
    return {
        'allocations_at_need': allocated,
        'shortages_at_need': shortage,
        'total_shortage': sum(shortage),
        'reviewed_production_orders': len(demands),
        'affected_production_orders': [demands[i]['production_order'] for i in impacted],
        'affected_sales_lines': sorted(unique_lines),
        'affected_open_order_value_cents': value_cents,
        'risk_factors': factors,
        'risk_score': score,
        'severity': 'LOW' if score < 25 else 'MEDIUM' if score < 50 else 'HIGH' if score < 75 else 'CRITICAL',
    }


def main() -> None:
    fixture = json.loads((ROOT / 'fixtures/hero_supplier_delay.json').read_text(encoding='utf-8'))
    results: list[dict[str, Any]] = []
    for scenario in fixture['scenarios']:
        actual = evaluate(fixture, scenario)
        require(actual == scenario['expected'], f"Fixture mismatch: {scenario['id']}\n{actual}")
        results.append({'scenario': scenario['id'], 'status': 'PASS', 'computed': actual})
    spec = (ROOT / 'CODEX_BUILD_SPEC.md').read_text(encoding='utf-8')
    required_files = [
        'START_HERE.md', 'AGENTS.md', 'CODEX_BUILD_SPEC.md',
        'RESUME_AFTER_HANDOFF_FIX.md', 'CONTEXT.md',
        'fixtures/hero_supplier_delay.json', 'acceptance/acceptance-matrix.json',
        'docs/adr/0001-orchestration-and-state.md',
        'docs/adr/0002-approval-and-delivery.md',
        'docs/adr/0003-impact-and-risk.md',
        'docs/adr/0004-demo-and-connected-profiles.md',
    ]
    for name in required_files:
        require((ROOT / name).is_file(), f'Missing required file: {name}')
    require('**Version:** 1.1' in spec, 'Expected canonical specification v1.1')
    milestones = re.findall(r'^\| \*\*(M\d+) —', spec, flags=re.M)
    require(milestones == [f'M{i}' for i in range(8)], 'Expected milestones M0 through M7')
    spec_ids = re.findall(r'^\| (AC\d{2}) \|', spec, flags=re.M)
    require(spec_ids == [f'AC{i:02d}' for i in range(1, 37)], 'Expected spec AC01 through AC36')
    heading_count = len(re.findall(r'^## \d+\.', spec, flags=re.M))
    require(heading_count == 23, 'Expected 23 specification sections')
    ac = json.loads((ROOT / 'acceptance/acceptance-matrix.json').read_text(encoding='utf-8'))
    require(len(ac['criteria']) == 36, 'Expected 36 acceptance criteria')
    require(all(c['status'] == 'NOT_RUN' for c in ac['criteria']), 'Application tests have not been run')
    require(len({c['id'] for c in ac['criteria']}) == 36, 'Duplicate acceptance ID')
    require({c['id'] for c in ac['criteria']} == set(spec_ids), 'Matrix and specification IDs differ')
    for file in ROOT.rglob('*.md'):
        text = file.read_text(encoding='utf-8')
        require(len(re.findall(r'^```', text, re.M)) % 2 == 0, f'Unbalanced fenced code blocks: {file.name}')
        require('20+15+16+8+10+0 = 75' not in text, 'Outdated illustrative score')
    report = {
        'check_type': 'HANDOFF_DOCUMENT_AND_FIXTURE_CONSISTENCY_ONLY',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS',
        'package_version': '1.1',
        'canonical_spec': 'CODEX_BUILD_SPEC.md',
        'required_files_checked': len(required_files),
        'milestones': milestones,
        'spec_sections': heading_count,
        'acceptance_criteria': len(ac['criteria']),
        'scenario_results': results,
        'application_implemented': False,
        'n8n_deployed': False,
        'application_acceptance_tests_executed': False,
    }
    (ROOT / 'HANDOFF_VALIDATION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
