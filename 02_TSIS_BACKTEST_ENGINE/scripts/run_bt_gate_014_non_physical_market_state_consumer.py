from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from tsis_backtest.market_state.acceptance import AcceptanceMatrix
from tsis_backtest.market_state.runner import SyntheticMarketStateRunRequest,SyntheticMarketStateRunner

def resolve(v): p=Path(v); return p if p.is_absolute() else ROOT/p
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--config',default=str(ROOT/'configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json')); ap.add_argument('--output-root',default=None); ns=ap.parse_args()
 c=json.loads(resolve(ns.config).read_text(encoding='utf-8')); output=resolve(ns.output_root or c['output_root'])
 req=SyntheticMarketStateRunRequest(c['run_id'],output,resolve(c['fixture_root']),resolve(c['adoption_record']),resolve(c['outer_handoff']),resolve(c['nested_evidence']),c['authority'],False,resolve(ns.config))
 runner=SyntheticMarketStateRunner(); first=runner.run(req); second=runner.run(req); matrix=AcceptanceMatrix(req).execute()
 det={'status':'PASS' if first['deterministic_output_hash']==second['deterministic_output_hash'] else 'FAIL','repeat_count':2,'root_independence_case':'NEGATIVE_33','first_hash':first['deterministic_output_hash'],'second_hash':second['deterministic_output_hash'],'scientific_hashes_match':first['deterministic_output_hash']==second['deterministic_output_hash']}
 run_dir=runner.write_result(req,first,matrix,det)
 result={'run_dir':str(run_dir),'validation_status':first['validation_status'],'acceptance_matrix_status':matrix['status'],'positive_case_count':matrix['positive_case_count'],'negative_case_count':matrix['negative_case_count'],'failed_case_count':matrix['failed_case_count'],'determinism_status':det['status'],'deterministic_output_hash':first['deterministic_output_hash'],'physical_state_rows_read':0,'orders_emitted':0,'fills_emitted':0,'PnL_calculated':False,'phase_b_external_review':'PENDING_RE_REVIEW','new_single_use_physical_authorization':'NOT_AUTHORIZED','next_required_action':'PHASE_B_EXTERNAL_RE_REVIEW'}
 print(json.dumps(result,indent=2,sort_keys=True)); return 0 if all(x=='PASS' for x in (matrix['status'],det['status'],first['validation_status'])) else 1
if __name__=='__main__': raise SystemExit(main())
