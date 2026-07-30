from __future__ import annotations
import hashlib,json,unittest
from pathlib import Path
from tsis_backtest.market_state.acceptance import AcceptanceMatrix
from tsis_backtest.market_state.runner import SyntheticMarketStateRunRequest
ROOT=Path(__file__).resolve().parents[2]; CONFIG=ROOT/'configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json'; RUN=ROOT/'runs/bt_gate_014_non_physical_market_state_consumer_v0_1'
def request():
 c=json.loads(CONFIG.read_text(encoding='utf-8')); return SyntheticMarketStateRunRequest(c['run_id'],ROOT/c['output_root'],ROOT/c['fixture_root'],ROOT/c['adoption_record'],ROOT/c['outer_handoff'],ROOT/c['nested_evidence'],c['authority'],False,CONFIG)
class MarketStateAcceptanceMatrixTests(unittest.TestCase):
 def test_all_contract_cases_are_executed(self):
  report=AcceptanceMatrix(request()).execute(); self.assertEqual(report['status'],'PASS'); self.assertEqual(report['positive_case_count'],15); self.assertEqual(report['negative_case_count'],33); self.assertEqual(report['failed_case_count'],0); self.assertTrue(report['report_generated_from_executions'])
 def test_canonical_run_manifest_resolves_all_artifacts(self):
  final=json.loads((RUN/'final_manifest.json').read_text(encoding='utf-8')); self.assertEqual(final['validation_status'],'PASS'); self.assertEqual(final['positive_case_count'],15); self.assertEqual(final['negative_case_count'],33); self.assertEqual(final['failed_case_count'],0)
  self.assertEqual(final['physical_state_rows_read'],0); self.assertEqual(final['orders_emitted'],0); self.assertEqual(final['fills_emitted'],0); self.assertFalse(final['PnL_calculated'])
  for name,expected in final['output_artifact_hashes'].items(): self.assertEqual(hashlib.sha256((RUN/name).read_bytes()).hexdigest(),expected,name)
  required={'provider_handoff_adoption_record.json','market_state_physical_column_mapping.json','bounded_market_state_event_schema.json','typed_core_four_payload_schema.json','market_state_audit_lineage_schema.json','market_state_store_contract.json','synthetic_fixture_manifest.json','synthetic_raw_rows.json','synthetic_sidecar.json','resolved_input_manifest.json','state_aware_event_sequence.json','market_state_validation_report.json','market_state_store_trace.json','bounded_consumer_probe_observations.json','negative_derivative_report.json','boundary_preservation_report.json','determinism_report.json'}
  self.assertTrue(required.issubset(final['output_artifact_hashes']))
if __name__=='__main__': unittest.main()
