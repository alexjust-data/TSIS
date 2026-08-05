from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TSIS_ROOT=ROOT.parents[1]; ENGINE=TSIS_ROOT/'02_TSIS_BACKTEST_ENGINE'
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 regs={
  'decisions':load(ROOT/'04_DECISIONS/DECISION_LEDGER.json'),'policies':load(ROOT/'05_POLICIES/POLICY_REGISTER.json'),
  'traceability':load(ROOT/'06_TRACEABILITY/TRACEABILITY_MATRIX.json'),'exceptions':load(ROOT/'07_EXCEPTIONS/EXCEPTION_AND_WAIVER_REGISTER.json'),'gates':load(ROOT/'08_GATES_AND_REVIEWS/GATE_REGISTER.json')}
 decisions={x['decision_id'] for x in regs['decisions']['entries']}; policies={x['policy_id']:x for x in regs['policies']['entries']}; gates={x['gate_id']:x for x in regs['gates']['gates']}; exceptions={x['exception_id']:x for x in regs['exceptions']['entries']}
 assert len(decisions)==len(regs['decisions']['entries']);assert len(policies)==len(regs['policies']['entries']);assert len(gates)==len(regs['gates']['gates']);assert len(exceptions)==len(regs['exceptions']['entries'])
 for x in regs['decisions']['entries']: assert set(x['policy_ids'])<=set(policies) and x['authorized_by_gate'] in gates
 for x in policies.values(): assert x['decision_id'] in decisions
 for x in regs['traceability']['entries']: assert set(x['decision_ids'])<=decisions and set(x['policy_ids'])<=set(policies) and x['gate_id'] in gates
 status='CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS'
 rows={
  next(x for x in regs['decisions']['entries'] if x['decision_id']=='BT-STATE-002')['status'],policies['BT-POL-STATE-002']['status'],
  next(x for x in regs['traceability']['entries'] if x['capability_id']=='BT-CAP-PIT-MARKET-STATE-CONSUMER-V0-1')['status'],
  next(x for x in regs['exceptions']['entries'] if x['exception_id']=='BT-EXC-010')['status'],gates['BT-GATE-014']['status']}
 assert rows=={status},rows
 v3=load(ENGINE/'configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_3.json');run3=ENGINE/'runs/bt_gate_014_single_use_physical_market_state_consumer_v0_3'
 assert v3['status']=='CONSUMED_BY_RUN_bt_gate_014_single_use_physical_market_state_consumer_v0_3';assert v3['consumed_by_run_id']=='bt_gate_014_single_use_physical_market_state_consumer_v0_3'
 for n in ('authorization_consumption_receipt.json','pre_run_manifest.json','failure_manifest.json'): assert (run3/n).is_file()
 failure=load(run3/'failure_manifest.json');assert failure['error_code']=='FAIL_MARKET_STATE_RESTRICTION_PROPAGATION';assert failure['market_state_events_emitted']==0 and failure['orders']==0 and failure['fills']==0
 v4=load(ENGINE/'configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_4.json');run4=ENGINE/'runs/bt_gate_014_single_use_physical_market_state_consumer_v0_4'
 assert v4['status']=='CONSUMED_BY_RUN_bt_gate_014_single_use_physical_market_state_consumer_v0_4'
 failure4=load(run4/'failure_manifest.json');assert failure4['physical_data_files_opened']==1 and failure4['physical_state_rows_read']==2
 v5=load(ENGINE/'configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_5.json')
 assert v5['status']=='CONSUMED_BY_RUN_bt_gate_014_single_use_physical_market_state_consumer_v0_5' and v5['consumed_by_run_id']=='bt_gate_014_single_use_physical_market_state_consumer_v0_5'
 run5=ENGINE/'runs/bt_gate_014_single_use_physical_market_state_consumer_v0_5';assert (run5/'final_manifest.json').is_file();final5=load(run5/'final_manifest.json');assert final5['validation_status']=='PASS' and final5['physical_state_rows_read']==2
 pm=load(ROOT/'PACKAGE_MANIFEST.json')
 bt15_status='NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PENDING_SINGLE_USE_PHYSICAL_AUTHORIZATION'
 bt15_decision=next(x for x in regs['decisions']['entries'] if x['decision_id']=='BT-STATE-003')
 bt15_policy=policies['BT-POL-STATE-003']
 bt15_trace=next(x for x in regs['traceability']['entries'] if x['capability_id']=='BT-CAP-PIT-EVENT-STATE-CONSUMER-V0-1')
 bt15_gate=gates['BT-GATE-015']
 assert {bt15_decision['status'],bt15_policy['status'],bt15_trace['status'],bt15_gate['status']}=={bt15_status}
 assert bt15_gate['implementation_acceptance']=='ACCEPTED_NON_PHYSICAL_ONLY'
 assert bt15_gate['physical_execution']=='NOT_AUTHORIZED' and bt15_gate['physical_state_rows_read']==0
 acceptance=ROOT/'08_GATES_AND_REVIEWS/BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md'
 assert acceptance.is_file() and 'BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS' in acceptance.read_text(encoding='utf-8')
 handoff=ENGINE/'docs/00_system/CURRENT_PROJECT_HANDOFF.md'
 handoff_text=handoff.read_text(encoding='utf-8')
 assert 'Status: `LIVE_RESTART_AUTHORITY`' in handoff_text and bt15_status in handoff_text
 auth1=load(ENGINE/'configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_1.json')
 auth2=load(ENGINE/'configs/authorizations/bt_gate_015_single_use_physical_event_state_consumer_v0_2.json')
 assert auth1['status']=='DRAFT_SUPERSEDED_NEVER_AUTHORIZED' and auth1['execution_authorized'] is False
 assert auth2['status']=='DRAFT_NOT_AUTHORIZED_PENDING_PREEXECUTION_REVIEW' and auth2['execution_authorized'] is False
 assert pm['current_gate']['gate_id']=='BT-GATE-015'
 assert pm['current_gate']['status']==bt15_status
 assert pm['current_gate']['implementation_acceptance']=='ACCEPTED_NON_PHYSICAL_ONLY'
 assert pm['current_gate']['physical_consumer_read']=='NOT_AUTHORIZED'
 assert pm['current_gate']['physical_state_rows_read']==0
 assert pm['current_gate']['new_single_use_physical_authorization']=='NOT_AUTHORIZED'
 assert pm['status']=='BT_GATE_015_NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PHYSICAL_READ_NOT_AUTHORIZED'
 assert pm['manifest_regenerated_reason']=='bt_gate_015_non_physical_external_review_accepted_documentation_synchronized'
 candidate=pm['next_candidate_gate']
 assert candidate['gate_id']=='BT-GATE-015' and candidate['status']==bt15_status
 assert candidate['implementation']=='ACCEPTED_NON_PHYSICAL_ONLY' and candidate['physical_read']=='NOT_AUTHORIZED'
 assert pm['file_count']==len(pm['files'])
 for rel,h in pm['files'].items(): assert sha(TSIS_ROOT/Path(rel))==h,rel
 print(json.dumps({
  'status':'PASS',
  'decision_count':len(decisions),
  'policy_count':len(policies),
  'traceability_capability_count':len(regs['traceability']['entries']),
  'exception_count':len(exceptions),
  'gate_count':len(gates),
  'v0_3_state':v3['status'],
  'v0_4_state':v4['status'],
  'v0_4_physical_files_opened':failure4['physical_data_files_opened'],
  'v0_4_physical_rows_read':failure4['physical_state_rows_read'],
  'v0_5_state':v5['status'],
  'v0_5_physical_rows_read':final5['physical_state_rows_read'],
  'bt_gate_015_status':bt15_status,
  'bt_gate_015_non_physical_external_review':'PASS',
  'bt_gate_015_physical_rows_read':bt15_gate['physical_state_rows_read'],
  'governance_package_hashes_verified':len(pm['files'])
 },indent=2,sort_keys=True))
if __name__=='__main__':main()
