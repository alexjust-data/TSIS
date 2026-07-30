"""Atomic single-use authorization state for BT-GATE-014."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any
from .contracts import MarketStateContractError

AUTHORIZATION_ID="BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-1"
RUN_ID="bt_gate_014_single_use_physical_market_state_consumer_v0_1"

def _strict(path:Path)->dict[str,Any]:
    def reject(value): raise ValueError(f"non-finite JSON constant: {value}")
    return json.loads(path.read_text(encoding="utf-8"),parse_constant=reject)
def _write_atomic(path:Path,data:dict[str,Any])->None:
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    os.replace(tmp,path)
def sha256(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()

class SingleUseAuthorization:
    def __init__(self,state_path:Path): self.state_path=state_path; self.lock_path=state_path.with_suffix(".lock")
    def inspect(self)->dict[str,Any]:
        data=_strict(self.state_path)
        if data.get("authorization_id")!=AUTHORIZATION_ID: raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_ID_MISMATCH",str(self.state_path))
        return data
    def acquire_and_consume(self,expected_bindings:dict[str,str],run_dir:Path)->dict[str,Any]:
        try:
            fd=os.open(self.lock_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        except FileExistsError as exc:
            raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_LOCKED",str(self.lock_path)) from exc
        try:
            os.close(fd)
            state=self.inspect()
            status=state.get("status")
            if isinstance(status,str) and status.startswith("CONSUMED_BY_RUN_"):
                raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_ALREADY_CONSUMED",status)
            if status!="AUTHORIZED_NOT_CONSUMED":
                raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZATION_NOT_ISSUED",str(status))
            if state.get("binding_sha256")!=expected_bindings:
                raise MarketStateContractError("FAIL_BT_GATE_014_AUTHORIZED_RUNNER_HASH_MISMATCH","binding_sha256")
            if run_dir.exists():
                raise MarketStateContractError("FAIL_NONEMPTY_RUN_DIRECTORY",str(run_dir))
            run_dir.mkdir(parents=True)
            state["status"]=f"CONSUMED_BY_RUN_{RUN_ID}"
            state["consumed_by_run_id"]=RUN_ID
            _write_atomic(self.state_path,state)
            receipt={"authorization_id":AUTHORIZATION_ID,"status":state["status"],"binding_sha256":expected_bindings}
            _write_atomic(run_dir/"authorization_consumption_receipt.json",receipt)
            return receipt
        finally:
            self.lock_path.unlink(missing_ok=True)
