from __future__ import annotations
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tsis_backtest.market_state.contracts import MarketStateContractError
from tsis_backtest.market_state.physical_authorization_v0_2 import AUTHORIZATION_ID,AuthorizationV02
from tsis_backtest.market_state.physical_runner_v0_2 import NAMES,PhysicalRunnerV02

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"tests/fixtures/bt_gate_014_synthetic_market_state"
def put(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
class PhysicalV02Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.engine=self.root/"02_TSIS_BACKTEST_ENGINE";self.engine.mkdir()
  self.rows=json.loads((FIX/"synthetic_raw_rows.json").read_text())["records"];self.sides=json.loads((FIX/"synthetic_sidecar.json").read_text())["records"];self.ids=tuple(x["materialized_state_candidate_id"] for x in self.rows)
  self.paths={};self.hashes={}
  for n in NAMES:
   p=self.root/"provider"/f"{n}.json";put(p,{"records":self.sides,"candidate_dataset_id":self.sides[0]["candidate_dataset_id"],"candidate_dataset_fingerprint":self.sides[0]["candidate_dataset_fingerprint"],"sidecar_id":self.sides[0]["sidecar_id"],"sidecar_schema_id":self.sides[0]["sidecar_schema_id"]} if n=="sidecar_manifest" else {"columns":[]});self.paths[n]=str(p.relative_to(self.root)).replace("\\","/");self.hashes[n]=hashlib.sha256(p.read_bytes()).hexdigest()
  self.cfg={"run_id":"bt_gate_014_single_use_physical_market_state_consumer_v0_2","run_directory":"runs/v02","provider_relative_paths":self.paths,"physical_input_sha256":self.hashes}
  binding=self.engine/"binding.py";binding.write_text("binding",encoding="utf-8");self.bind={"binding.py":hashlib.sha256(binding.read_bytes()).hexdigest()}
  doc=self.engine/"docs/00_system/18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_2.md";doc.parent.mkdir(parents=True);doc.write_text("doc",encoding="utf-8")
  cfgfile=self.engine/"configs/runs/bt_gate_014_single_use_physical_market_state_consumer_v0_2.json";cfgfile.parent.mkdir(parents=True);cfgfile.write_text("config",encoding="utf-8")
  self.state=self.engine/"configs/authorizations/auth.json";put(self.state,{"authorization_id":AUTHORIZATION_ID,"consumer_id":"BT_GATE_014_BOUNDED_MARKET_STATE_CONSUMER","contract_consumer_id":"BT_GATE_014_bounded_market_state_consumer_v0_1","status":"AUTHORIZED_NOT_CONSUMED","binding_sha256":self.bind,"authorization_document_sha256":hashlib.sha256(doc.read_bytes()).hexdigest(),"configuration_sha256":hashlib.sha256(cfgfile.read_bytes()).hexdigest()})
  barrier=self.root/"02_TSIS_BACKTEST_ENGINE/configs/fixtures/BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_2.json"
  put(barrier,{"records":[{"ticker":r["ticker"],"ts_start":s["state_available_at_utc"],"ts_end":s["state_available_at_utc"],"available_at":s["state_available_at_utc"],"session_label":"REGULAR","open":1.0,"high":1.0,"low":1.0,"close":1.0,"volume":0} for r,s in zip(self.rows,self.sides)]})
 def tearDown(self): self.tmp.cleanup()
 def runner(self,rows=None):
  r=PhysicalRunnerV02(lambda p,s:copy.deepcopy(rows if rows is not None else self.rows));r.c.validate_schema_contract=lambda s:None;return r
 def execute(self,rows=None):
  with patch("tsis_backtest.market_state.physical_runner_v0_2.IDS",self.ids): return self.runner(rows).execute(self.root,self.cfg,AuthorizationV02(self.state),self.bind)
 def test_full_pipeline_writes_complete_evidence(self):
  out=self.execute();self.assertEqual((out["market_state_events_emitted"],out["market_state_store_inserts"],out["bounded_consumer_observations"]),(2,2,2))
  run=self.root/"02_TSIS_BACKTEST_ENGINE/runs/v02"
  required={"authorization_consumption_receipt.json","pre_run_manifest.json","resolved_physical_input_manifest.json","physical_schema_validation_report.json","physical_row_identity_report.json","bounded_market_state_events.json","state_aware_event_sequence.json","market_state_store_trace.json","bounded_consumer_probe_observations.json","boundary_preservation_report.json","deterministic_reproduction_source.json","physical_consumer_validation_report.json","final_manifest.json"}
  self.assertEqual({p.name for p in run.iterdir()},required)
 def test_incomplete_rows_fail_and_write_failure_manifest(self):
  rows=[{"materialized_state_candidate_id":x["materialized_state_candidate_id"],"state_output_fingerprint":x["state_output_fingerprint"]} for x in self.rows]
  with self.assertRaises(MarketStateContractError): self.execute(rows)
  self.assertTrue((self.root/"02_TSIS_BACKTEST_ENGINE/runs/v02/failure_manifest.json").is_file())
 def test_nine_input_inventory_is_closed(self):
  del self.cfg["provider_relative_paths"]["binding"]
  with self.assertRaisesRegex(MarketStateContractError,"INPUT_INVENTORY"): self.execute()
  self.assertTrue((self.root/"02_TSIS_BACKTEST_ENGINE/runs/v02/failure_manifest.json").is_file())
 def test_wrong_input_hash_consumes_and_records_failure(self):
  self.cfg["physical_input_sha256"]["binding"]="0"*64
  with self.assertRaisesRegex(MarketStateContractError,"PHYSICAL_INPUT_HASH_MISMATCH"): self.execute()
  self.assertTrue(json.loads(self.state.read_text())["status"].startswith("CONSUMED_BY_RUN_"))
  self.assertTrue((self.root/"02_TSIS_BACKTEST_ENGINE/runs/v02/failure_manifest.json").is_file())
 def test_v01_is_superseded_unconsumed(self):
  p=ROOT/"configs/authorizations/bt_gate_014_single_use_physical_consumer_authorization_v0_1.json"
  self.assertEqual(json.loads(p.read_text())["status"],"SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL")
if __name__=="__main__": unittest.main()
