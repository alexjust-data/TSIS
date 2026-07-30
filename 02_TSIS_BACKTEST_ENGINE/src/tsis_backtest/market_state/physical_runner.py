"""Bounded physical Market State runner. Importing this module never opens Parquet."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any,Callable
from .consumer import FROZEN_PROVIDER_AUTHORITY,MarketStateConsumerV0_1
from .contracts import MarketStateContractError
from .physical_authorization import SingleUseAuthorization,sha256

AUTHORIZED_IDS=("f09492ac417d05161f70ee75f81e345a9cc315cef9beb9939d2df6ff3eb58dd3","26d923a282355ad242a5d91ad7d6183bed6a94842041ecf966ac70c366308c0e")
EXPECTED_FINGERPRINTS=("f7c926be8e8bb6e84433061213bc554d54de2e03d0910a799e974ff5aea04617","2420034cb851629b48ee3216713b6bc1a337ce0a4356096575a3db1a91edb7bd")
ALLOWED_RELATIVE_PATHS={
"candidate_parquet":"00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/market_state_on_demand_scale_validation_v0_1_20260727T133641Z/market_state_scale_validation_candidate_v0_1.parquet",
"physical_schema_contract":"00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1/PHYSICAL_SCHEMA_CONTRACT.json",
"sidecar_manifest":"00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/09_STATE_CONSUMPTION_BOUNDARY/market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"}

def _stable_bytes(path:Path)->tuple[bytes,str]:
    before=path.read_bytes(); h=hashlib.sha256(before).hexdigest()
    if hashlib.sha256(path.read_bytes()).hexdigest()!=h: raise MarketStateContractError("FAIL_SOURCE_MUTATION",str(path))
    return before,h
def resolve_inputs(tsis_root:Path,config:dict[str,Any])->dict[str,Path]:
    if set(config["provider_relative_paths"])!=set(ALLOWED_RELATIVE_PATHS): raise MarketStateContractError("FAIL_BT_GATE_014_SCOPE_LEAKAGE","paths")
    out={}
    for key,expected in ALLOWED_RELATIVE_PATHS.items():
        if config["provider_relative_paths"][key]!=expected: raise MarketStateContractError("FAIL_BT_GATE_014_SCOPE_LEAKAGE",key)
        p=(tsis_root/expected).resolve()
        if tsis_root.resolve() not in p.parents: raise MarketStateContractError("FAIL_BT_GATE_014_SCOPE_LEAKAGE",key)
        out[key]=p
    return out
def default_reader(path:Path)->list[dict[str,Any]]:
    import pyarrow.parquet as pq
    table=pq.read_table(path,filters=[("materialized_state_candidate_id","in",list(AUTHORIZED_IDS))])
    return table.to_pylist()
def validate_selected_rows(rows:list[dict[str,Any]])->None:
    if len(rows)!=2: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_ROW_CARDINALITY",str(len(rows)))
    ids=tuple(row.get("materialized_state_candidate_id") for row in rows)
    if set(ids)!=set(AUTHORIZED_IDS) or len(set(ids))!=2: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY","ids")
    got={row.get("state_output_fingerprint") for row in rows}
    if got!=set(EXPECTED_FINGERPRINTS): raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY","fingerprints")

class PhysicalMarketStateRunner:
    def __init__(self,reader:Callable[[Path],list[dict[str,Any]]]=default_reader): self.reader=reader
    def execute(self,root:Path,config:dict[str,Any],authorization:SingleUseAuthorization,bindings:dict[str,str])->dict[str,Any]:
        paths=resolve_inputs(root,config); run_dir=root/"02_TSIS_BACKTEST_ENGINE"/config["run_directory"]
        authorization.acquire_and_consume(bindings,run_dir)
        expected=config["physical_input_sha256"]; identities={}
        for key,path in paths.items():
            _,actual=_stable_bytes(path)
            if actual!=expected[key]: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_INPUT_HASH_MISMATCH",key)
            identities[key]={"relative_path":config["provider_relative_paths"][key],"sha256_before":actual}
        rows=self.reader(paths["candidate_parquet"]); validate_selected_rows(rows)
        for key,path in paths.items():
            after=sha256(path); identities[key]["sha256_after"]=after
            if after!=identities[key]["sha256_before"]: raise MarketStateContractError("FAIL_SOURCE_MUTATION",key)
        return {"validation_status":"PASS","physical_data_files_opened":1,"physical_state_rows_read":2,
                "authorized_rows_materialized":2,"unlisted_rows_delivered_to_consumer":0,
                "unlisted_rows_persisted_in_evidence":0,"strategy_decisions":0,"orders":0,"fills":0,"PnL_calculated":False,
                "input_identities":identities}
