from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from tsis_backtest.market_state.physical_authorization_v0_2 import AUTHORIZATION_ID,AuthorizationV02
from tsis_backtest.market_state.physical_runner_v0_2 import PhysicalRunnerV02
def main():
 p=argparse.ArgumentParser();p.add_argument("--confirm-authorization-id",required=True);a=p.parse_args()
 if a.confirm_authorization_id!=AUTHORIZATION_ID: raise SystemExit("FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH")
 cp=ROOT/"configs/runs/bt_gate_014_single_use_physical_market_state_consumer_v0_2.json";sp=ROOT/"configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_2.json";dp=ROOT/"docs/00_system/18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_2.md"
 state=json.loads(sp.read_text()); config=json.loads(cp.read_text())
 if hashlib.sha256(cp.read_bytes()).hexdigest()!=state["configuration_sha256"] or hashlib.sha256(dp.read_bytes()).hexdigest()!=state["authorization_document_sha256"]: raise SystemExit("FAIL_BT_GATE_014_AUTHORIZED_BINDING_HASH_MISMATCH")
 for rel,want in state["binding_sha256"].items():
  if not (ROOT/rel).is_file() or hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=want: raise SystemExit("FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH")
 result=PhysicalRunnerV02().execute(ROOT.parent,config,AuthorizationV02(sp),config["binding_sha256"]);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
