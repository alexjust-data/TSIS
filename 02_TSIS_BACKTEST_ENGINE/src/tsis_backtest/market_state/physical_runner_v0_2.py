from __future__ import annotations
import datetime,hashlib,json
from pathlib import Path
from typing import Any
from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent
from .consumer import FROZEN_PROVIDER_AUTHORITY,MarketStateConsumerV0_1,_utc,state_aware_order_key
from .contracts import BoundedConsumerProbeObservation,MarketStateContractError,to_market_state_jsonable
from .store import MarketStateStore
from .physical_authorization_v0_2 import AuthorizationV02,atomic
IDS=("f09492ac417d05161f70ee75f81e345a9cc315cef9beb9939d2df6ff3eb58dd3","26d923a282355ad242a5d91ad7d6183bed6a94842041ecf966ac70c366308c0e")
NAMES=("candidate_parquet","physical_schema_contract","binding","sidecar_manifest","sidecar_contract","timestamp_contract","lineage_manifest","temporal_legality_report","state_bundle_manifest")
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,data): atomic(path,to_market_state_jsonable(data))
class PhysicalRunnerV02:
 def __init__(self,row_reader=None): self.c=MarketStateConsumerV0_1();self.row_reader=row_reader or self._read_parquet
 def _read_parquet(self,path,schema):
  import pyarrow.parquet as pq
  pf=pq.ParquetFile(path); observed=[{"name":f.name,"type":str(f.type),"nullable":f.nullable} for f in pf.schema_arrow]
  if observed!=schema["columns"]: raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH","40 columns")
  return pq.read_table(path,filters=[("materialized_state_candidate_id","in",list(IDS))]).to_pylist()

 @staticmethod
 def _normalize_row(row):
  out=dict(row)
  for key,value in tuple(out.items()):
   if isinstance(value,datetime.datetime): out[key]=value.astimezone(datetime.timezone.utc).isoformat().replace("+00:00","Z")
   elif isinstance(value,datetime.date): out[key]=value.isoformat()
  return out
 def execute(self,root,config,auth,bindings):
  root=Path(root); run_dir=root/"02_TSIS_BACKTEST_ENGINE"/config["run_directory"]; auth.consume(bindings,run_dir)
  try: return self._after_consumption(root,config,run_dir)
  except Exception as e:
   write(run_dir/"failure_manifest.json",{"status":"FAIL","error_code":getattr(e,"code",type(e).__name__),"error":str(e),"authorization_consumed":True,"strategy_decisions":0,"orders":0,"fills":0,"PnL_calculated":False})
   raise
 def _after_consumption(self,root,config,run_dir):
  if set(config["provider_relative_paths"])!=set(NAMES) or set(config["physical_input_sha256"])!=set(NAMES): raise MarketStateContractError("FAIL_BT_GATE_014_INPUT_INVENTORY","nine inputs")
  paths={}; identities={}
  for name in NAMES:
   rel=config["provider_relative_paths"][name]
   if Path(rel).is_absolute() or ".." in Path(rel).parts: raise MarketStateContractError("FAIL_BT_GATE_014_SCOPE_LEAKAGE",name)
   p=(root/rel).resolve()
   if root.resolve() not in p.parents: raise MarketStateContractError("FAIL_BT_GATE_014_SCOPE_LEAKAGE",name)
   before=h(p)
   if before!=config["physical_input_sha256"][name]: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_INPUT_HASH_MISMATCH",name)
   paths[name]=p;identities[name]={"relative_path":rel,"sha256_before":before,"size_bytes":p.stat().st_size}
  schema=json.loads(paths["physical_schema_contract"].read_text(encoding="utf-8"));self.c.validate_schema_contract(schema)
  side=json.loads(paths["sidecar_manifest"].read_text(encoding="utf-8"))
  sides=[{**x,"sidecar_id":side["sidecar_id"],"sidecar_schema_id":side["sidecar_schema_id"]} for x in side["records"] if x["materialized_state_candidate_id"] in IDS]
  rows=[self._normalize_row(x) for x in self.row_reader(paths["candidate_parquet"],schema)]
  if len(rows)!=2: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_ROW_CARDINALITY",str(len(rows)))
  authority={**FROZEN_PROVIDER_AUTHORITY,"candidate_dataset_id":side["candidate_dataset_id"],"candidate_dataset_fingerprint":side["candidate_dataset_fingerprint"]}
  validated=self.c.validate_join_and_seal(rows,sides,authority,identities["sidecar_manifest"]["sha256_before"])
  if {v.event.materialized_state_candidate_id for v in validated}!=set(IDS): raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_ROW_IDENTITY","ids")
  barriers=json.loads((root/"02_TSIS_BACKTEST_ENGINE/configs/fixtures/BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_2.json").read_text())
  bars=[]
  for x in barriers["records"]:
   b=MarketDataBar1m(x["ticker"],_utc(x["ts_start"]),_utc(x["ts_end"]),_utc(x["available_at"]),x["session_label"],x["open"],x["high"],x["low"],x["close"],x["volume"],"synthetic_barrier")
   bars.append(ReplayBarEvent("BAR",b.ticker,b.available_at,b,{"synthetic":True,"execution_input":False}))
  events=[v.event for v in validated]; ordered=sorted([*bars,*events],key=state_aware_order_key); store=MarketStateStore();seq=[];obs=[];byid={v.event.materialized_state_candidate_id:v for v in validated}
  for i,e in enumerate(ordered):
   if isinstance(e,ReplayBarEvent): seq.append({"event_index":i,"event_type":"BAR","priority":1,"available_at_utc":e.available_at});continue
   n=store.insert(byid[e.materialized_state_candidate_id],e.state_available_at_utc); visible=self.c.require_probe_visibility(store,e.materialized_state_candidate_id,e.state_available_at_utc)
   obs.append(BoundedConsumerProbeObservation(f"physical-probe-{i}",i,e.state_available_at_utc,e.materialized_state_candidate_id,e.state_output_fingerprint,17,e.restriction_codes,n,"VISIBLE").to_dict());seq.append({"event_index":i,"event_type":e.event_type,"priority":2,"available_at_utc":e.state_available_at_utc})
  self.c.validate_ordered_sequence(ordered)
  for n,p in paths.items():
   after=h(p);identities[n]["sha256_after"]=after
   if after!=identities[n]["sha256_before"]: raise MarketStateContractError("FAIL_SOURCE_MUTATION",n)
  artifacts={"pre_run_manifest.json":{"run_id":config["run_id"],"authorization_consumed":True},"resolved_physical_input_manifest.json":identities,"physical_schema_validation_report.json":{"status":"PASS","column_count":40},"physical_row_identity_report.json":{"status":"PASS","authorized_ids":list(IDS)},"bounded_market_state_events.json":[e.to_dict() for e in events],"state_aware_event_sequence.json":seq,"market_state_store_trace.json":to_market_state_jsonable(store.trace),"bounded_consumer_probe_observations.json":obs,"boundary_preservation_report.json":{"status":"PASS","strategy":False,"orders":0,"fills":0,"PnL":False},"deterministic_reproduction_source.json":{"events":[e.to_dict() for e in events],"sequence":seq},"physical_consumer_validation_report.json":{"status":"PASS","physical_data_files_opened":1,"physical_state_rows_read":2,"events":2,"store_inserts":2,"observations":2,"early_deliveries":0}}
  hashes={"authorization_consumption_receipt.json":h(run_dir/"authorization_consumption_receipt.json")}
  for name,data in artifacts.items(): write(run_dir/name,data);hashes[name]=h(run_dir/name)
  final={"gate_id":"BT-GATE-014","authorization_version":"V0.2","validation_status":"PASS","physical_data_files_opened":1,"physical_state_rows_read":2,"market_state_events_emitted":2,"typed_scientific_values_per_event":17,"market_state_store_inserts":2,"bounded_consumer_observations":2,"delivery_before_available_at":0,"strategy_decisions":0,"orders":0,"fills":0,"PnL_calculated":False,"output_artifact_hashes":hashes,"external_acceptance_review":"PENDING","BT_GATE_014_CLOSED_PASS":"NOT_AUTHORIZED"}
  write(run_dir/"final_manifest.json",final);return final
