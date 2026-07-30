from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from .contracts import MarketStateContractError
AUTHORIZATION_ID="BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-2"
RUN_ID="bt_gate_014_single_use_physical_market_state_consumer_v0_2"
def atomic(path,data):
 tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8"); os.replace(tmp,path)
class AuthorizationV02:
 def __init__(self,path): self.path=Path(path); self.lock=self.path.with_suffix(".lock")
 def consume(self,bindings,run_dir):
  try: fd=os.open(self.lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.close(fd)
  except FileExistsError as e: raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_LOCKED",str(self.lock)) from e
  try:
   s=json.loads(self.path.read_text(encoding="utf-8"))
   if s.get("authorization_id")!=AUTHORIZATION_ID: raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH","id")
   if s.get("consumer_id")!="BT_GATE_014_BOUNDED_MARKET_STATE_CONSUMER" or s.get("contract_consumer_id")!="BT_GATE_014_bounded_market_state_consumer_v0_1": raise MarketStateContractError("FAIL_BT_GATE_014_CONSUMER_ID_MISMATCH","consumer")
   if str(s.get("status","")).startswith("CONSUMED_BY_RUN_"): raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_ALREADY_CONSUMED",s["status"])
   if s.get("status")!="AUTHORIZED_NOT_CONSUMED": raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_NOT_ISSUED",str(s.get("status")))
   if s.get("binding_sha256")!=bindings: raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH","bindings")
   engine_root=self.path.parents[2]
   for rel,want in bindings.items():
    target=engine_root/rel
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=want: raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH",rel)
   doc=engine_root/"docs/00_system/18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_2.md";cfg=engine_root/"configs/runs/bt_gate_014_single_use_physical_market_state_consumer_v0_2.json"
   if hashlib.sha256(doc.read_bytes()).hexdigest()!=s.get("authorization_document_sha256") or hashlib.sha256(cfg.read_bytes()).hexdigest()!=s.get("configuration_sha256"): raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZED_BINDING_HASH_MISMATCH","document/configuration")
   if run_dir.exists(): raise MarketStateContractError("FAIL_NONEMPTY_RUN_DIRECTORY",str(run_dir))
   run_dir.mkdir(parents=True); s["status"]="CONSUMED_BY_RUN_"+RUN_ID;s["consumed_by_run_id"]=RUN_ID;atomic(self.path,s)
   receipt={"authorization_id":AUTHORIZATION_ID,"consumer_id":s["consumer_id"],"contract_consumer_id":s["contract_consumer_id"],"status":s["status"],"binding_sha256":bindings};atomic(run_dir/"authorization_consumption_receipt.json",receipt);return receipt
  finally: self.lock.unlink(missing_ok=True)
