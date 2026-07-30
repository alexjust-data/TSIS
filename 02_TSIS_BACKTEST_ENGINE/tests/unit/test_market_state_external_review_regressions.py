from __future__ import annotations
import copy,hashlib,json,shutil,tempfile,unittest,zipfile
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from tsis_backtest.market_state.consumer import FINGERPRINT_FIELDS,ID_FIELDS,MarketStateConsumerV0_1,canonical_hash
from tsis_backtest.market_state.contracts import MarketStateContractError
from tsis_backtest.market_state.runner import SyntheticMarketStateRunRequest,SyntheticMarketStateRunner
from tsis_backtest.market_state.store import MarketStateStore
ROOT=Path(__file__).resolve().parents[2]; CONFIG=ROOT/'configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json'
def load():
 c=json.loads(CONFIG.read_text(encoding='utf-8')); f=ROOT/c['fixture_root']; return c,json.loads((f/'synthetic_raw_rows.json').read_text())['records'],json.loads((f/'synthetic_sidecar.json').read_text())['records']
def request(c,**kw):
 d=dict(run_id=c['run_id'],output_root=ROOT/'runs',fixture_root=ROOT/c['fixture_root'],adoption_record=ROOT/c['adoption_record'],outer_handoff=ROOT/c['outer_handoff'],nested_evidence=ROOT/c['nested_evidence'],authority=c['authority'],physical_execution_authorized=False,config_path=CONFIG); d.update(kw); return SyntheticMarketStateRunRequest(**d)
class ExternalReviewRegressionTests(unittest.TestCase):
 def setUp(self):
  self.c,self.rows,self.sides=load(); self.consumer=MarketStateConsumerV0_1(); self.temp=Path(tempfile.mkdtemp(prefix='bt014_review_'))
  self.side_hash=hashlib.sha256((ROOT/self.c['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest()
 def tearDown(self): shutil.rmtree(self.temp,ignore_errors=True)
 def code(self,code,fn):
  with self.assertRaises(MarketStateContractError) as x: fn()
  self.assertEqual(x.exception.code,code)
 def resign(self,row,side):
  fingerprint=canonical_hash({field:row[field] for field in FINGERPRINT_FIELDS}); row['state_output_fingerprint']=fingerprint; side['state_output_fingerprint']=fingerprint
  candidate=canonical_hash({field:(fingerprint if field=='state_output_fingerprint' else row[field]) for field in ID_FIELDS}); row['materialized_state_candidate_id']=candidate; side['materialized_state_candidate_id']=candidate
 def mutated_request(self,mutator):
  case_root=Path(tempfile.mkdtemp(prefix='case_',dir=self.temp)); fixture=case_root/'fixture'; shutil.copytree(ROOT/self.c['fixture_root'],fixture); mutator(fixture)
  manifest_path=fixture/'synthetic_fixture_manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
  for name,identity in manifest['files'].items():
   path=fixture/name; identity['sha256']=hashlib.sha256(path.read_bytes()).hexdigest(); identity['size_bytes']=path.stat().st_size
  manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
  config=copy.deepcopy(self.c); config['synthetic_fixture_manifest_sha256']=hashlib.sha256(manifest_path.read_bytes()).hexdigest(); config['synthetic_fixture_manifest_size_bytes']=manifest_path.stat().st_size
  config_path=case_root/'config.json'; config_path.write_text(json.dumps(config,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
  return request(self.c,fixture_root=fixture,config_path=config_path)
 def test_component_cannot_exceed_decision_or_state_availability(self):
  side=copy.deepcopy(self.sides[0]); side['component_availability_evidence'][0]['component_as_of_utc']='2026-01-05T14:31:01Z'; side['component_availability_evidence'][0]['component_available_at_utc']='2026-01-05T14:31:02Z'
  self.code('FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
 def test_row_temporal_values_must_equal_component_derivations(self):
  side=copy.deepcopy(self.sides[0]); side['state_as_of_utc']='2026-01-05T14:30:59Z'; self.code('FAIL_MARKET_STATE_AS_OF_DERIVATION_MISMATCH',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
  side=copy.deepcopy(self.sides[0]); side['state_available_at_utc']='2026-01-05T14:31:01Z'; self.code('FAIL_MARKET_STATE_AVAILABILITY_DERIVATION_MISMATCH',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
 def test_store_visibility_includes_actual_insert_time(self):
  side_hash=hashlib.sha256((ROOT/self.c['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest(); validated=self.consumer.validate_and_seal(self.rows[0],self.sides[0],self.c['authority'],side_hash); e=validated.event; store=MarketStateStore(); inserted=e.state_available_at_utc+timedelta(minutes=5); store.insert(validated,inserted)
  self.assertIsNone(store.get_exact(e.materialized_state_candidate_id,inserted-timedelta(seconds=1))); self.assertIsNone(store.latest_visible(e.profile_id,e.instrument_id,e.decision_timestamp_utc,inserted-timedelta(seconds=1))); self.assertEqual(store.get_exact(e.materialized_state_candidate_id,inserted),e)
 def test_join_rejects_orphan_sidecar_and_reuse(self):
  self.code('FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',lambda:self.consumer.join_rows([self.rows[0]],self.sides,self.c['authority'],self.side_hash))
  self.code('FAIL_MARKET_STATE_SIDECAR_DUPLICATE',lambda:self.consumer.join_rows([self.rows[0],self.rows[0]],[self.sides[0]],self.c['authority'],self.side_hash))
 def test_runner_requires_exact_frozen_runtime_authority(self):
  authority=dict(self.c['authority']); authority['current_runtime_content_sha256']='0'*64
  self.code('FAIL_MARKET_STATE_AUTHORITY_MISMATCH',lambda:SyntheticMarketStateRunner().run(request(self.c,authority=authority)))
 def test_fixture_manifest_hash_and_size_are_enforced(self):
  fixture=self.temp/'fixture'; shutil.copytree(ROOT/self.c['fixture_root'],fixture); raw=fixture/'synthetic_raw_rows.json'; raw.write_bytes(raw.read_bytes()+b' ')
  self.code('FAIL_SYNTHETIC_INPUT_HASH_MISMATCH',lambda:SyntheticMarketStateRunner().run(request(self.c,fixture_root=fixture)))
 def test_missing_required_sidecar_identity_is_rejected(self):
  side=copy.deepcopy(self.sides[0]); del side['source_candidate_record_id']
  self.code('FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
 def test_store_rejects_forged_unvalidated_event(self):
  from dataclasses import replace
  event=self.consumer.build_event(self.rows[0],self.sides[0],self.c['authority'],self.side_hash); forged=replace(event,state_replay_consumption_legality='research_only')
  self.code('FAIL_MARKET_STATE_STORE_VALIDATION_RECEIPT_REQUIRED',lambda:MarketStateStore().insert(forged,event.state_available_at_utc))
 def test_unmanifested_sidecar_mutation_is_rejected(self):
  fixture=self.temp/'fixture'; shutil.copytree(ROOT/self.c['fixture_root'],fixture); side=fixture/'synthetic_sidecar.json'; side.write_text(side.read_text(encoding='utf-8')+' ',encoding='utf-8')
  manifest_path=fixture/'synthetic_fixture_manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8')); del manifest['files']['synthetic_sidecar.json']; manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
  config_path=self.temp/'config.json'; config=copy.deepcopy(self.c); import hashlib; config['synthetic_fixture_manifest_sha256']=hashlib.sha256(manifest_path.read_bytes()).hexdigest(); config['synthetic_fixture_manifest_size_bytes']=manifest_path.stat().st_size; config_path.write_text(json.dumps(config,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
  self.code('FAIL_SYNTHETIC_INPUT_MANIFEST_COVERAGE',lambda:SyntheticMarketStateRunner().run(request(self.c,fixture_root=fixture,config_path=config_path)))
 def test_config_path_is_mandatory(self):
  self.code('FAIL_BT_GATE_014_CONFIG_REQUIRED',lambda:SyntheticMarketStateRunner().run(request(self.c,config_path=None)))
 def test_request_authority_must_equal_config_authority(self):
  authority=dict(self.c['authority']); authority['candidate_dataset_id']='other_synthetic_dataset'
  self.code('FAIL_MARKET_STATE_AUTHORITY_MISMATCH',lambda:SyntheticMarketStateRunner().run(request(self.c,authority=authority)))
 def test_store_rejects_post_validation_event_mutations(self):
  from dataclasses import replace
  side_hash=hashlib.sha256((ROOT/self.c['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest(); validated=self.consumer.validate_and_seal(self.rows[0],self.sides[0],self.c['authority'],side_hash); event=validated.event
  mutations=(
   replace(event,state_kind='event_state'),replace(event,event_type='Other'),replace(event,state_output_fingerprint='0'*64),
   replace(event,audit_lineage=replace(event.audit_lineage,current_runtime_content_sha256='0'*64)),
   replace(event,state_publication_latency_policy_id='other'),replace(event,state_publication_latency='PT5M'))
  for forged in mutations:
   with self.subTest(forged=forged): self.code('FAIL_MARKET_STATE_STORE_INVALID_VALIDATION_RECEIPT',lambda f=forged:MarketStateStore().insert(replace(validated,event=f),event.state_available_at_utc))
 def test_sidecar_frozen_profile_policy_and_identity_are_enforced(self):
  cases=(('physical_profile_id','wrong_profile','FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH'),('state_availability_policy_id','wrong_policy','FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH'),('sidecar_id','','FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH'),('sidecar_schema_id','','FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH'))
  for field,value,code in cases:
   side=copy.deepcopy(self.sides[0]); side[field]=value
   with self.subTest(field=field): self.code(code,lambda s=side:self.consumer.build_event(self.rows[0],s,self.c['authority'],self.side_hash))
 def test_provider_authority_cannot_be_locally_resigned(self):
  evidence=self.temp/'evidence'; evidence.mkdir(); nested=evidence/'nested.zip'
  with zipfile.ZipFile(nested,'w') as z: z.writestr('tampered.txt','tampered')
  outer=evidence/'outer.zip'
  with zipfile.ZipFile(ROOT/self.c['outer_handoff']) as source, zipfile.ZipFile(outer,'w') as target:
   for info in source.infolist():
    payload=source.read(info.filename)
    if info.filename.endswith(Path(self.c['nested_evidence']).name): payload=nested.read_bytes()
    target.writestr(info,payload)
  adoption=json.loads((ROOT/self.c['adoption_record']).read_text()); outer_hash=hashlib.sha256(outer.read_bytes()).hexdigest(); nested_hash=hashlib.sha256(nested.read_bytes()).hexdigest()
  for key in ('sha256_before_adoption','sha256_after_adoption'): adoption['outer_handoff'][key]=outer_hash; adoption['nested_provider_evidence'][key]=nested_hash
  adoption['outer_handoff']['size_bytes']=outer.stat().st_size; adoption['nested_provider_evidence']['size_bytes']=nested.stat().st_size; adoption['nested_provider_evidence']['nested_inside_outer_sha256']=nested_hash
  adoption_path=evidence/'adoption.json'; adoption_path.write_text(json.dumps(adoption,sort_keys=True)+'\n',encoding='utf-8')
  config=copy.deepcopy(self.c); config['outer_handoff_sha256']=outer_hash; config['outer_handoff_size_bytes']=outer.stat().st_size; config['nested_evidence_sha256']=nested_hash; config['nested_evidence_size_bytes']=nested.stat().st_size
  config['adoption_record_sha256']=hashlib.sha256(adoption_path.read_bytes()).hexdigest(); config['adoption_record_size_bytes']=adoption_path.stat().st_size
  config_path=evidence/'config.json'; config_path.write_text(json.dumps(config,sort_keys=True)+'\n',encoding='utf-8')
  self.code('FAIL_PROVIDER_HANDOFF_HASH_MISMATCH',lambda:SyntheticMarketStateRunner().run(request(self.c,outer_handoff=outer,nested_evidence=nested,adoption_record=adoption_path,config_path=config_path)))
 def test_validate_and_seal_revalidates_raw_inputs_atomically(self):
  side_hash=hashlib.sha256((ROOT/self.c['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest()
  mutations=(('ticker','FORGED'),('state_output_fingerprint','0'*64),('restriction_codes_json','[]'))
  for field,value in mutations:
   row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row[field]=value
   if field in side: side[field]=value
   with self.subTest(field=field): self.code('FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH' if field!='restriction_codes_json' else 'FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH',lambda r=row,s=side:self.consumer.validate_and_seal(r,s,self.c['authority'],side_hash))
  self.assertFalse(hasattr(self.consumer,'seal_validated_event'))
 def test_provider_component_status_and_identity_rules(self):
  side=copy.deepcopy(self.sides[0]); self.assertTrue(all(x['availability_status']=='available' for x in side['component_availability_evidence'])); self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash)
  side=copy.deepcopy(self.sides[0]); side['component_availability_evidence'][1]['component_id']=side['component_availability_evidence'][0]['component_id']; self.code('FAIL_MARKET_STATE_COMPONENT_SET',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
  side=copy.deepcopy(self.sides[0]); side['component_availability_evidence'][0]['availability_rule_id']=''; self.code('FAIL_MARKET_STATE_COMPONENT_IDENTITY',lambda:self.consumer.build_event(self.rows[0],side,self.c['authority'],self.side_hash))
 def test_lineage_separates_consumed_and_provider_sidecar_hashes(self):
  side_hash=hashlib.sha256((ROOT/self.c['fixture_root']/'synthetic_sidecar.json').read_bytes()).hexdigest(); event=self.consumer.build_event(self.rows[0],self.sides[0],self.c['authority'],side_hash)
  self.assertEqual(event.audit_lineage.consumed_sidecar_sha256,side_hash); self.assertEqual(event.audit_lineage.provider_sidecar_authority_sha256,self.c['authority']['sidecar_sha256']); self.assertNotEqual(side_hash,self.c['authority']['sidecar_sha256'])
 def test_parquet_config_path_rejected_before_read(self):
  path=self.temp/'must_not_open.parquet'; path.write_bytes(b'invalid')
  self.code('FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED',lambda:SyntheticMarketStateRunner().run(request(self.c,config_path=path)))
 def test_runner_rejects_duplicate_sidecars_before_indexing(self):
  def mutate(fixture):
   path=fixture/'synthetic_sidecar.json'; document=json.loads(path.read_text(encoding='utf-8')); document['records'].append(copy.deepcopy(document['records'][0])); path.write_text(json.dumps(document,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
  req=self.mutated_request(mutate)
  self.code('FAIL_MARKET_STATE_SIDECAR_DUPLICATE',lambda:SyntheticMarketStateRunner().run(req))
 def test_store_lineage_is_recursively_immutable(self):
  row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row['source_lineage_json']='{"nested":{"values":[1,2]},"synthetic":true}'; self.resign(row,side)
  validated=self.consumer.validate_and_seal(row,side,self.c['authority'],self.side_hash); event=validated.event; store=MarketStateStore(); store.insert(validated,event.state_available_at_utc); stored=store.get_exact(event.materialized_state_candidate_id,event.state_available_at_utc); before=canonical_hash(stored.to_dict())
  with self.assertRaises(TypeError): stored.audit_lineage.source_lineage['nested']['values'][0]=99
  self.assertEqual(canonical_hash(stored.to_dict()),before); self.assertEqual(json.loads(stored.audit_lineage.source_lineage_raw_json),stored.to_dict()['audit_lineage']['source_lineage'])
 def test_validate_and_seal_rejects_wrong_schema_and_empty_sidecar_hash(self):
  row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row['state_schema_version']='wrong_schema'; self.resign(row,side)
  self.code('FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH',lambda:self.consumer.validate_and_seal(row,side,self.c['authority'],self.side_hash))
  self.code('FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',lambda:self.consumer.validate_and_seal(self.rows[0],self.sides[0],self.c['authority'],''))
 def test_strict_embedded_json_rejects_non_finite_constants(self):
  row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row['source_lineage_json']='{"x":NaN}'; self.resign(row,side)
  self.code('FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON',lambda:self.consumer.validate_and_seal(row,side,self.c['authority'],self.side_hash))
 def test_empty_row_and_sidecar_identities_are_rejected(self):
  for field in ('ticker','instrument_id','context_id'):
   row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row[field]=side[field]=''; self.resign(row,side)
   with self.subTest(field=field): self.code('FAIL_MARKET_STATE_IDENTITY_INVALID',lambda r=row,s=side:self.consumer.validate_and_seal(r,s,self.c['authority'],self.side_hash))
 def test_sidecar_and_component_schemas_are_closed(self):
  side=copy.deepcopy(self.sides[0]); side['unexpected']='forbidden'
  self.code('FAIL_MARKET_STATE_SIDECAR_SCHEMA_MISMATCH',lambda:self.consumer.validate_and_seal(self.rows[0],side,self.c['authority'],self.side_hash))
  side=copy.deepcopy(self.sides[0]); side['component_availability_evidence'][0]['unexpected']='forbidden'
  self.code('FAIL_MARKET_STATE_COMPONENT_SCHEMA_MISMATCH',lambda:self.consumer.validate_and_seal(self.rows[0],side,self.c['authority'],self.side_hash))
 def test_runner_rejects_falsified_fixture_boundary_flags(self):
  for field,value in (('not_provider_evidence',False),('not_scientific_observation',False),('provider_parquet_opened',True)):
   def mutate(fixture,f=field,v=value):
    path=fixture/'synthetic_raw_rows.json'; document=json.loads(path.read_text(encoding='utf-8')); document[f]=v; path.write_text(json.dumps(document,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
   req=self.mutated_request(mutate)
   with self.subTest(field=field): self.code('FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED',lambda r=req:SyntheticMarketStateRunner().run(r))
 def test_market_state_artifacts_use_canonical_z_timestamps(self):
  req=request(self.c,run_id='utc_serialization',output_root=self.temp/'runs'); runner=SyntheticMarketStateRunner(); result=runner.run(req); report={'status':'PASS','positive_case_count':15,'negative_case_count':33,'failed_case_count':0}; det={'status':'PASS','first_hash':result['deterministic_output_hash'],'second_hash':result['deterministic_output_hash']}; run_dir=runner.write_result(req,result,report,det)
  for name in ('state_aware_event_sequence.json','market_state_store_trace.json','bounded_consumer_probe_observations.json'):
   text=(run_dir/name).read_text(encoding='utf-8'); self.assertNotIn('+00:00',text,name); self.assertIn('Z',text,name)
 def test_governance_deterministic_hash_is_cross_surface_consistent(self):
  final=json.loads((ROOT/'runs/bt_gate_014_single_use_physical_market_state_consumer_v0_5/final_manifest.json').read_text(encoding='utf-8')); governance=ROOT.parent/'00_CTO/14_BACKTEST_ENGINE'
  policy=json.loads((governance/'05_POLICIES/POLICY_REGISTER.json').read_text(encoding='utf-8')); gate=json.loads((governance/'08_GATES_AND_REVIEWS/GATE_REGISTER.json').read_text(encoding='utf-8')); trace=json.loads((governance/'06_TRACEABILITY/TRACEABILITY_MATRIX.json').read_text(encoding='utf-8')); package=json.loads((governance/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
  policy_hash=next(item['deterministic_output_hash'] for item in policy['entries'] if item['policy_id']=='BT-POL-STATE-002'); gate_hash=next(item['deterministic_output_hash'] for item in gate['gates'] if item['gate_id']=='BT-GATE-014'); trace_entry=next(item for item in trace['entries'] if item['capability_id']=='BT-CAP-PIT-MARKET-STATE-CONSUMER-V0-1'); trace_hash=trace_entry['deterministic_output_hash']
  self.assertEqual({final['deterministic_output_hash'],policy_hash,gate_hash,trace_hash,package['current_gate']['deterministic_output_hash']},{final['deterministic_output_hash']})
 def test_living_documents_have_exactly_one_current_authoritative_state(self):
  governance=ROOT.parent/'00_CTO/14_BACKTEST_ENGINE'
  paths=(ROOT/'AGENTS.md',ROOT/'README.md',ROOT/'CHANGELOG.md',ROOT/'docs/00_system/BACKTEST_ENGINE_ROADMAP.md',governance/'AGENTS.md',governance/'README.md',governance/'CHANGELOG.md')
  for path in paths:
   text=path.read_text(encoding='utf-8')
   headings=[line for line in text.splitlines() if line.startswith('## Current Authoritative State')]
   self.assertEqual(len(headings),1,path)
   self.assertIn('BT-GATE-014 final closure',headings[0],path)
 def test_current_project_handoff_is_complete_and_markdown_is_clean(self):
  handoff=ROOT/'docs/00_system/CURRENT_PROJECT_HANDOFF.md'
  text=handoff.read_text(encoding='utf-8')
  for required in (
   'Status: LIVE_RESTART_AUTHORITY',
   'BT-GATE-014 /',
   'CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS',
   'V0.5 = CONSUMED_FINAL',
   'SECOND_EXECUTION_V0.5 = PROHIBITED',
   'BT-GATE-015 = NOT_OPEN',
   'BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED',
   'BT-GATE-015_PHYSICAL_READ = NOT_AUTHORIZED',
  ):
   self.assertIn(required,text)
  self.assertEqual(text.count('```') % 2,0)
  for path in (ROOT/'AGENTS.md',ROOT/'docs/00_system/19_BT_GATE_014_FINAL_POSTEXECUTION_ACCEPTANCE_V0_1.md',handoff):
   document=path.read_text(encoding='utf-8')
   self.assertNotIn('`\text',document,path)
   self.assertEqual(document.count('```') % 2,0,path)
if __name__=='__main__': unittest.main()
