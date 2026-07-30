from __future__ import annotations
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock

from tsis_backtest.market_state.contracts import MarketStateContractError
from tsis_backtest.market_state.physical_authorization import AUTHORIZATION_ID,SingleUseAuthorization
from tsis_backtest.market_state.physical_runner import ALLOWED_RELATIVE_PATHS,AUTHORIZED_IDS,EXPECTED_FINGERPRINTS,PhysicalMarketStateRunner,resolve_inputs,validate_selected_rows

def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True)+"\n",encoding="utf-8")

class SingleUsePhysicalPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.engine=self.root/"02_TSIS_BACKTEST_ENGINE"; self.engine.mkdir()
        self.files={}
        for key,rel in ALLOWED_RELATIVE_PATHS.items():
            p=self.root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(key.encode())
            self.files[key]=p
        self.bindings={"runner":"a"*64}
        self.state=self.engine/"authorization.json"
        write_json(self.state,{"authorization_id":AUTHORIZATION_ID,"status":"AUTHORIZED_NOT_CONSUMED","binding_sha256":self.bindings})
        self.config={"run_directory":"runs/probe","provider_relative_paths":dict(ALLOWED_RELATIVE_PATHS),
                     "physical_input_sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in self.files.items()}}
        self.rows=[{"materialized_state_candidate_id":i,"state_output_fingerprint":f} for i,f in zip(AUTHORIZED_IDS,EXPECTED_FINGERPRINTS)]
    def tearDown(self): self.tmp.cleanup()
    def test_not_issued_never_calls_reader(self):
        write_json(self.state,{"authorization_id":AUTHORIZATION_ID,"status":"PREPARATION_AUTHORIZED_PHYSICAL_READ_NOT_ISSUED","binding_sha256":self.bindings})
        reader=Mock(return_value=self.rows)
        with self.assertRaisesRegex(MarketStateContractError,"FAIL_BT_GATE_014_AUTHORIZATION_NOT_ISSUED"):
            PhysicalMarketStateRunner(reader).execute(self.root,self.config,SingleUseAuthorization(self.state),self.bindings)
        reader.assert_not_called()
    def test_authorized_run_consumes_before_reader(self):
        observed=[]
        def reader(path):
            observed.append(json.loads(self.state.read_text())["status"]); return self.rows
        result=PhysicalMarketStateRunner(reader).execute(self.root,self.config,SingleUseAuthorization(self.state),self.bindings)
        self.assertTrue(observed[0].startswith("CONSUMED_BY_RUN_"))
        self.assertEqual(result["physical_state_rows_read"],2)
    def test_second_use_fails(self):
        runner=PhysicalMarketStateRunner(lambda p:self.rows)
        runner.execute(self.root,self.config,SingleUseAuthorization(self.state),self.bindings)
        with self.assertRaisesRegex(MarketStateContractError,"ALREADY_CONSUMED"):
            runner.execute(self.root,self.config,SingleUseAuthorization(self.state),self.bindings)
    def test_binding_mismatch_fails_before_reader(self):
        reader=Mock(return_value=self.rows)
        with self.assertRaisesRegex(MarketStateContractError,"RUNNER_HASH_MISMATCH"):
            PhysicalMarketStateRunner(reader).execute(self.root,self.config,SingleUseAuthorization(self.state),{"runner":"b"*64})
        reader.assert_not_called()
    def test_duplicate_and_unlisted_rows_fail(self):
        with self.assertRaisesRegex(MarketStateContractError,"PHYSICAL_ROW_IDENTITY"):
            validate_selected_rows([self.rows[0],self.rows[0]])
        with self.assertRaisesRegex(MarketStateContractError,"PHYSICAL_ROW_IDENTITY"):
            validate_selected_rows([self.rows[0],{"materialized_state_candidate_id":"x","state_output_fingerprint":"y"}])
    def test_paths_are_closed(self):
        bad=json.loads(json.dumps(self.config)); bad["provider_relative_paths"]["candidate_parquet"]="other.parquet"
        with self.assertRaisesRegex(MarketStateContractError,"SCOPE_LEAKAGE"): resolve_inputs(self.root,bad)
    def test_existing_run_directory_fails_before_reader(self):
        (self.engine/"runs/probe").mkdir(parents=True)
        reader=Mock(return_value=self.rows)
        with self.assertRaisesRegex(MarketStateContractError,"NONEMPTY_RUN_DIRECTORY"):
            PhysicalMarketStateRunner(reader).execute(self.root,self.config,SingleUseAuthorization(self.state),self.bindings)
        reader.assert_not_called()

if __name__=="__main__": unittest.main()
