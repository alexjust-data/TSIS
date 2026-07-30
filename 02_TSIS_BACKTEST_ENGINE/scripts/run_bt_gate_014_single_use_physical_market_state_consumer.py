from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from tsis_backtest.market_state.physical_authorization import AUTHORIZATION_ID,SingleUseAuthorization
from tsis_backtest.market_state.physical_runner import PhysicalMarketStateRunner
def main():
 p=argparse.ArgumentParser(); p.add_argument("--confirm-authorization-id",required=True); a=p.parse_args()
 if a.confirm_authorization_id!=AUTHORIZATION_ID: raise SystemExit("FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH")
 config_path=ROOT/"configs/runs/bt_gate_014_single_use_physical_market_state_consumer_v0_1.json"
 state_path=ROOT/"configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_1.json"
 state=json.loads(state_path.read_text(encoding="utf-8"))
 if state.get("authorization_document_sha256")!=hashlib.sha256((ROOT/"docs/00_system/18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_1.md").read_bytes()).hexdigest(): raise SystemExit("FAIL_BT_GATE_014_AUTHORIZED_DOCUMENT_HASH_MISMATCH")
 if state.get("configuration_sha256")!=hashlib.sha256(config_path.read_bytes()).hexdigest(): raise SystemExit("FAIL_BT_GATE_014_AUTHORIZED_CONFIGURATION_HASH_MISMATCH")
 config=json.loads(config_path.read_text(encoding="utf-8")); bindings=config["binding_sha256"]
 result=PhysicalMarketStateRunner().execute(ROOT.parent,config,SingleUseAuthorization(state_path),bindings)
 print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
