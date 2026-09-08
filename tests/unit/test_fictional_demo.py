from copy import deepcopy
import json

from backend.datasets import load_fixture
from backend.domain import build_plan, evaluate_impact, evaluate_risk, extract_fixture


def assess(kind):
    data=load_fixture(kind,'fictional-v2')
    snapshot={'schema_version':'1.0','snapshot_id':'fictional-test','scope_id':'fictional-test','erp_revision':1,'analysis_time':data['analysis_time'],'data':data,'incident_type':kind}
    envelope={'source':'EMAIL',**data['source_email']} if kind=='SUPPLIER_DELAY' else {'source':'API','payload':data['facts']}
    extracted=extract_fixture(envelope,snapshot)
    assert extracted['status']=='VERIFIED',extracted['review_reasons']
    impact=evaluate_impact(snapshot,extracted['facts'])
    assert impact['data_complete'],impact['review_reasons']
    return data,snapshot,extracted['facts'],impact,evaluate_risk(impact)


def test_steel_rod_allocation_and_recovery():
    data,snapshot,facts,impact,risk=assess('SUPPLIER_DELAY')
    assert len(impact['reviewed_production_orders'])==4
    assert impact['initial_available_inventory']==24 # 42 physical minus 10 reserved and 8 quarantined.
    assert impact['shortages_at_need']==[0,20,20,0]
    assert impact['total_shortage']==40
    assert impact['affected_open_order_value_cents']==5_540_000
    assert risk['risk_score']==83 and risk['severity']=='CRITICAL'
    revised={**facts,'confirmed_supply_schedule':data['scenarios'][1]['confirmed_supply_schedule']}
    revised.pop('proposed_partial',None)
    recovered=evaluate_impact(snapshot,revised)
    assert recovered['confirmed_supply_quantity']==75
    assert recovered['shortages_at_need']==[0,0,10,0]
    assert recovered['affected_open_order_value_cents']==2_160_000
    assert evaluate_risk(recovered)['risk_score']==56
    assert impact['what_if']['impact']['total_shortage']==10


def test_band_saw_alternative_only_covers_one_operation():
    _,_,_,impact,risk=assess('MACHINE_BREAKDOWN')
    assert impact['required_hours']==16 and impact['uncovered_hours']==10
    assert len(impact['affected_production_orders'])==2
    assert len(impact['proposals'])==1
    assert impact['proposals'][0]['machine_id']=='DEMO-SAW-02'
    assert impact['proposals'][0]['required_hours']==6
    assert impact['proposals'][0]['capacity_reserved'] is False
    assert impact['qualified_alternative_available'] is False # No complete alternative for both operations.
    assert risk['risk_score']==62


def test_mounting_plate_trace_excludes_released_comparison_lot():
    _,_,_,impact,risk=assess('QUALITY_ISSUE')
    assert impact['blockable_quantity']==48
    assert [row['quantity'] for row in impact['trace']]==[30,18]
    assert {row['lot_id'] for row in impact['trace']}=={'DEMO-LOT-PLATE-01'}
    assert impact['affected_open_order_value_cents']==2_640_000
    assert risk['risk_score']==70 and risk['severity']=='CRITICAL'
    assert risk['override_reason']=='VERIFIED_DEFECTIVE_LOT_PENDING_SHIPMENT'


def test_unrelated_supplier_mail_requires_manual_review():
    _,snapshot,_,_,_=assess('SUPPLIER_DELAY')
    result=extract_fixture({'source':'EMAIL','sender':'supplier@example.test','content_text':'An unrelated fictional order has changed.'},snapshot)
    assert result['status']=='MANUAL_REVIEW'
    for kind in ('SUPPLIER_DELAY','MACHINE_BREAKDOWN','QUALITY_ISSUE'):
        assert load_fixture(kind)['data_classification']=='SYNTHETIC_ONLY'
