from __future__ import annotations
import copy, hashlib, json, tempfile, unittest
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from tsis_backtest.market_state.consumer import MarketStateConsumerV0_1, state_aware_order_key
from tsis_backtest.market_state.contracts import MarketStateContractError
from tsis_backtest.market_state.runner import SyntheticMarketStateRunRequest, SyntheticMarketStateRunner
from tsis_backtest.market_state.store import MarketStateStore

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json'
def cfg(): return json.loads(CONFIG.read_text(encoding='utf-8'))
def request(**kw):
 c=cfg(); base=dict(run_id=c['run_id'],output_root=ROOT/'runs',fixture_root=ROOT/c['fixture_root'],adoption_record=ROOT/c['adoption_record'],outer_handoff=ROOT/c['outer_handoff'],nested_evidence=ROOT/c['nested_evidence'],authority=c['authority'],physical_execution_authorized=False,config_path=CONFIG); base.update(kw); return SyntheticMarketStateRunRequest(**base)
def docs():
 c=cfg(); root=ROOT/c['fixture_root']; return json.loads((root/'synthetic_raw_rows.json').read_text()),json.loads((root/'synthetic_sidecar.json').read_text())
class MarketStateConsumerTests(unittest.TestCase):
 def setUp(self):
  self.consumer=MarketStateConsumerV0_1(); self.rows,self.side=docs(); self.auth=cfg()['authority']
  self.sidecar_sha256=hashlib.sha256((ROOT/cfg()['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest()
 def event(self,i=0): return self.consumer.build_event(copy.deepcopy(self.rows['records'][i]),copy.deepcopy(self.side['records'][i]),self.auth,self.sidecar_sha256)
 def validated(self,event):
  index=0 if event.materialized_state_candidate_id==self.rows['records'][0]['materialized_state_candidate_id'] else 1
  fixture=ROOT/cfg()['fixture_root']; side_hash=hashlib.sha256((fixture/'synthetic_sidecar.json').read_bytes()).hexdigest()
  return self.consumer.validate_and_seal(self.rows['records'][index],self.side['records'][index],self.auth,side_hash)
 def code(self, expected, fn):
  with self.assertRaises(MarketStateContractError) as ctx: fn()
  self.assertEqual(ctx.exception.code,expected)
 def test_positive_synthetic_run_is_bounded_and_deterministic(self):
  a=SyntheticMarketStateRunner().run(request()); b=SyntheticMarketStateRunner().run(request())
  self.assertEqual(a['deterministic_output_hash'],b['deterministic_output_hash']); self.assertEqual(a['market_state_events_received'],2)
  for k in ('physical_state_rows_read','strategy_callbacks','orders_emitted','fills_emitted','positions_mutated','cash_mutations','equity_mutations'): self.assertEqual(a[k],0)
 def test_positive_store_visibility_and_latest(self):
  raw=self.event(); validated=self.validated(raw); e=validated.event; s=MarketStateStore(); self.assertIsNone(s.get_exact(e.materialized_state_candidate_id,e.state_available_at_utc-timedelta(microseconds=1)))
  s.insert(validated,e.state_available_at_utc); self.assertEqual(s.get_exact(e.materialized_state_candidate_id,e.state_available_at_utc),e); self.assertEqual(s.latest_visible(e.profile_id,e.instrument_id,e.decision_timestamp_utc,e.state_available_at_utc),e)
 def test_negative_join_cardinality(self):
  self.code('FAIL_MARKET_STATE_SIDECAR_MISSING',lambda:self.consumer.join_rows(self.rows['records'],[],self.auth,self.sidecar_sha256))
  self.code('FAIL_MARKET_STATE_SIDECAR_DUPLICATE',lambda:self.consumer.join_rows([self.rows['records'][0]],[self.side['records'][0],self.side['records'][0]],self.auth,self.sidecar_sha256))
 def test_negative_identity_and_fingerprints(self):
  row=copy.deepcopy(self.rows['records'][0]); side=copy.deepcopy(self.side['records'][0]); side['ticker']='BAD'; self.code('FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',lambda:self.consumer.build_event(row,side,self.auth,self.sidecar_sha256))
  row=copy.deepcopy(self.rows['records'][0]); side=copy.deepcopy(self.side['records'][0]); row['state_output_fingerprint']=side['state_output_fingerprint']='0'*64; self.code('FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH',lambda:self.consumer.build_event(row,side,self.auth,self.sidecar_sha256))
  row=copy.deepcopy(self.rows['records'][0]); row['materialized_state_candidate_id']='0'*64; side=copy.deepcopy(self.side['records'][0]); side['materialized_state_candidate_id']='0'*64; self.code('FAIL_MARKET_STATE_CANDIDATE_ID_MISMATCH',lambda:self.consumer.build_event(row,side,self.auth,self.sidecar_sha256))
 def test_negative_payload_json_time_and_restrictions(self):
  row=copy.deepcopy(self.rows['records'][0]); row['price_movement__daily_gap_pct']=float('nan'); self.code('FAIL_MARKET_STATE_NON_FINITE_VALUE',lambda:self.consumer.build_event(row,self.side['records'][0],self.auth,self.sidecar_sha256))
  row=copy.deepcopy(self.rows['records'][0]); row['source_lineage_json']='{'; self.code('FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON',lambda:self.consumer.build_event(row,self.side['records'][0],self.auth,self.sidecar_sha256))
  side=copy.deepcopy(self.side['records'][0]); side['state_as_of_utc']='2099-01-01T00:00:00Z'; self.code('FAIL_MARKET_STATE_TEMPORAL_LEAKAGE',lambda:self.consumer.build_event(self.rows['records'][0],side,self.auth,self.sidecar_sha256))
  row=copy.deepcopy(self.rows['records'][0]); row['restriction_codes_json']='[]'; self.code('FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH',lambda:self.consumer.build_event(row,self.side['records'][0],self.auth,self.sidecar_sha256))
 def test_negative_store_and_boundaries(self):
  e=self.event(); s=MarketStateStore(); self.code('FAIL_MARKET_STATE_EARLY_STORE_INSERT',lambda:s.insert(self.validated(e),e.state_available_at_utc-timedelta(microseconds=1))); s.insert(self.validated(e),e.state_available_at_utc); self.code('FAIL_DUPLICATE_MARKET_STATE_EVENT',lambda:s.insert(self.validated(e),e.state_available_at_utc))
  self.code('FAIL_MARKET_STATE_OPERATIONAL_ROUTING_PROHIBITED',lambda:self.consumer.reject_operational_routing('execution'))
  self.code('FAIL_EVENT_STATE_NOT_AUTHORIZED',lambda:state_aware_order_key(object()))
  self.code('FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED',lambda:SyntheticMarketStateRunner().run(request(physical_execution_authorized=True)))
 def test_negative_hash_role_substitution(self):
  a=dict(self.auth); a['current_runtime_content_sha256']='b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2'; self.code('FAIL_MARKET_STATE_HASH_ROLE_SUBSTITUTION',lambda:self.consumer.build_event(self.rows['records'][0],self.side['records'][0],a,self.sidecar_sha256))
if __name__=='__main__': unittest.main()
