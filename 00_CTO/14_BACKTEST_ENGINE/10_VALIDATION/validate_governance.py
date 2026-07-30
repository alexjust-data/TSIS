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
 assert pm['current_gate']['physical_consumer_read']=='EXECUTED_PASS_PENDING_EXTERNAL_REVIEW'
 assert pm['current_gate']['physical_state_rows_read']==2
 assert pm['current_gate']['new_single_use_physical_authorization']=='V0_5_CONSUMED_FINAL_SECOND_EXECUTION_PROHIBITED'
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
  'governance_package_hashes_verified':len(pm['files'])
 },indent=2,sort_keys=True))
if __name__=='__main__':main()
