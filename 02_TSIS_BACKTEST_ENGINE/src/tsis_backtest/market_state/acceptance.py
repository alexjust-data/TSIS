"""Executed acceptance matrix for BT-GATE-014 non-physical phase."""
from __future__ import annotations
import copy, hashlib, json, shutil, tempfile, zipfile
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Mapping
from .consumer import (ENVELOPE_COLUMNS,FINGERPRINT_FIELDS,ID_FIELDS,LINEAGE_COLUMNS,PAYLOAD_COLUMNS,PHYSICAL_COLUMNS,MarketStateConsumerV0_1,canonical_hash,state_aware_order_key)
from .contracts import MarketStateContractError
from .runner import SyntheticMarketStateRunRequest,SyntheticMarketStateRunner
from .store import MarketStateStore

class AcceptanceMatrix:
 def __init__(self, request:SyntheticMarketStateRunRequest):
  self.r=request; self.c=MarketStateConsumerV0_1(); self.rows=self._load('synthetic_raw_rows.json')['records']; self.sides=self._load('synthetic_sidecar.json')['records']; self.bars=self._load('synthetic_market_bars.json')['records']; self.sidecar_sha256=hashlib.sha256((self.r.fixture_root/'synthetic_sidecar.json').read_bytes()).hexdigest()
 def _load(self,n): return json.loads((self.r.fixture_root/n).read_text(encoding='utf-8'))
 def _event(self,i=0,row=None,side=None,authority=None): return self.c.build_event(copy.deepcopy(row or self.rows[i]),copy.deepcopy(side or self.sides[i]),authority or self.r.authority,self.sidecar_sha256)
 def _validated(self,i=0,row=None,side=None,authority=None): return self.c.validate_and_seal(copy.deepcopy(row or self.rows[i]),copy.deepcopy(side or self.sides[i]),authority or self.r.authority,self.sidecar_sha256)
 def _bar(self,i=0): return SyntheticMarketStateRunner._bar_from_fixture(copy.deepcopy(self.bars[i]))
 def _resign(self,row,side):
  fp=canonical_hash({f:row[f] for f in FINGERPRINT_FIELDS}); row['state_output_fingerprint']=fp; side['state_output_fingerprint']=fp
  cid=canonical_hash({f:(fp if f=='state_output_fingerprint' else row[f]) for f in ID_FIELDS}); row['materialized_state_candidate_id']=cid; side['materialized_state_candidate_id']=cid
 def _expect(self,code,fn):
  try: fn()
  except MarketStateContractError as e:
   if e.code!=code: raise AssertionError(f'expected {code}, observed {e.code}') from e
   return code
  raise AssertionError(f'expected {code}, no failure')
 def _schema(self):
  with zipfile.ZipFile(self.r.outer_handoff) as z:
   name=next(n for n in z.namelist() if n.endswith('/PHYSICAL_SCHEMA_CONTRACT.json')); return json.loads(z.read(name).decode('utf-8-sig'))
 def _record(self,case_id,expected,fn):
  try: observed=fn(); status='PASS' if observed==expected else 'FAIL'
  except Exception as e: observed=f'{type(e).__name__}:{e}'; status='FAIL'
  evidence={'case_id':case_id,'expected_result':expected,'observed_result':observed,'status':status}
  evidence['evidence_hash']=canonical_hash(evidence); return evidence
 def execute(self):
  positives=[self._record(f'POSITIVE_{i:02d}','PASS',getattr(self,f'p{i:02d}')) for i in range(1,16)]
  negatives=[]
  expected={1:'FAIL_PROVIDER_HANDOFF_HASH_MISMATCH',2:'FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH',3:'FAIL_MARKET_STATE_HASH_ROLE_SUBSTITUTION',4:'FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH',5:'FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE',6:'FAIL_MARKET_STATE_CORE_FOUR_INCOMPLETE',7:'FAIL_MARKET_STATE_NON_FINITE_VALUE',8:'FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON',9:'FAIL_MARKET_STATE_TYPED_PAYLOAD_REQUIRED',10:'FAIL_MARKET_STATE_SIDECAR_MISSING',11:'FAIL_MARKET_STATE_SIDECAR_DUPLICATE',12:'FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',13:'FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH',14:'FAIL_MARKET_STATE_CANDIDATE_ID_MISMATCH',15:'FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC',16:'FAIL_MARKET_STATE_TEMPORAL_LEAKAGE',17:'FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER',18:'EVENT_NOT_DELIVERED_STORE_UNCHANGED',19:'FAIL_MARKET_STATE_ZERO_LATENCY_POLICY',20:'FAIL_MARKET_STATE_NOT_DECISION_SAFE',21:'FAIL_MARKET_STATE_COMPONENT_SET',22:'FAIL_MARKET_STATE_COMPONENT_LEGALITY_CONTRADICTION',23:'FAIL_MARKET_STATE_RESTRICTION_PROPAGATION',24:'FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY',25:'FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE',26:'FAIL_DUPLICATE_MARKET_STATE_EVENT',27:'FAIL_CONFLICTING_MARKET_STATE_EVENT',28:'NO_RESULT_STORE_UNCHANGED',29:'FAIL_MARKET_STATE_OPERATIONAL_ROUTING_PROHIBITED',30:'FAIL_EVENT_STATE_NOT_AUTHORIZED',31:'FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED',32:'FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED',33:'PASS_WITH_IDENTICAL_SCIENTIFIC_HASHES'}
  for i in range(1,34): negatives.append(self._record(f'NEGATIVE_{i:02d}',expected[i],getattr(self,f'n{i:02d}')))
  failed=sum(x['status']!='PASS' for x in positives+negatives)
  return {'status':'PASS' if failed==0 else 'FAIL','report_generated_from_executions':True,'positive_case_count':15,'negative_case_count':33,'failed_case_count':failed,'positive_results':positives,'negative_results':negatives}
 def p01(self): SyntheticMarketStateRunner().run(self.r); return 'PASS'
 def p02(self): self.c.validate_schema_contract(self._schema()); self.c.validate_column_mapping(ENVELOPE_COLUMNS,PAYLOAD_COLUMNS,LINEAGE_COLUMNS); return 'PASS'
 def p03(self): e=self._event(); assert len(PAYLOAD_COLUMNS)==17 and len(e.payload.to_dict())==4; return 'PASS'
 def p04(self): self._event(); return 'PASS'
 def p05(self): assert len(self.c.validate_join_and_seal([self.rows[0]],[self.sides[0]],self.r.authority,self.sidecar_sha256))==1; return 'PASS'
 def p06(self): e=self._event(); s=MarketStateStore(); assert s.get_exact(e.materialized_state_candidate_id,e.state_available_at_utc-timedelta(microseconds=1)) is None; return 'PASS'
 def p07(self): v=self._validated(); e=v.event; s=MarketStateStore(); s.insert(v,e.state_available_at_utc); assert s.get_exact(e.materialized_state_candidate_id,e.state_available_at_utc)==e; return 'PASS'
 def p08(self): e=self._event(); b=self._bar(); assert state_aware_order_key(b)<state_aware_order_key(e); return 'PASS'
 def p09(self): v=self._validated(); e=v.event; s=MarketStateStore(); seq=s.insert(v,e.state_available_at_utc); assert seq==0 and self.c.require_probe_visibility(s,e.materialized_state_candidate_id,e.state_available_at_utc)==e; return 'PASS'
 def p10(self):
  row=copy.deepcopy(self.rows[0]); side=copy.deepcopy(self.sides[0]); row['source_lineage_json']='{"nested":{"values":[1,2]},"synthetic":true}'; self._resign(row,side)
  v=self._validated(row=row,side=side); e=v.event; s=MarketStateStore(); s.insert(v,e.state_available_at_utc); fetched=s.get_exact(e.materialized_state_candidate_id,e.state_available_at_utc); assert fetched is e
  try: fetched.ticker='MUTATED'
  except FrozenInstanceError: pass
  else: raise AssertionError('top-level state was mutable')
  before=canonical_hash(fetched.to_dict())
  try: fetched.audit_lineage.source_lineage['nested']['values'][0]=99
  except TypeError: pass
  else: raise AssertionError('nested lineage was mutable')
  assert canonical_hash(fetched.to_dict())==before; return 'PASS'
 def p11(self): v1=self._validated(0); v2=self._validated(1); e1=v1.event; e2=v2.event; s=MarketStateStore(); s.insert(v1,e1.state_available_at_utc); s.insert(v2,e2.state_available_at_utc); assert s.latest_visible(e2.profile_id,e2.instrument_id,e2.decision_timestamp_utc,e2.state_available_at_utc)==e2; return 'PASS'
 def p12(self):
  e=self._event(); round_trip=json.loads(json.dumps(e.to_dict(),sort_keys=True)); assert round_trip['replay_consumption_restriction_codes']==list(e.replay_consumption_restriction_codes)
  observed=round_trip['audit_lineage']['component_availability_evidence']; expected=e.to_dict()['audit_lineage']['component_availability_evidence']; assert observed==expected; return 'PASS'
 def p13(self):
  events=self.c.join_rows(self.rows,self.sides,self.r.authority,self.sidecar_sha256); bars=tuple(self._bar(i) for i in range(len(events)))
  first=tuple(sorted((events[1],bars[0],events[0],bars[1]),key=state_aware_order_key)); second=tuple(sorted((bars[1],events[0],bars[0],events[1]),key=state_aware_order_key))
  assert [state_aware_order_key(e) for e in first]==[state_aware_order_key(e) for e in second]; return 'PASS'
 def p14(self):
  evidence=self._clean_root_manifest_evidence(); assert evidence['all_scientific_hashes_match']; return 'PASS' 
 def p15(self): x=SyntheticMarketStateRunner().run(self.r); assert all(x[k]==0 for k in ('physical_data_files_opened','physical_state_rows_read','strategy_callbacks','orders_emitted','fills_emitted','positions_mutated','cash_mutations','equity_mutations')) and not x['PnL_calculated']; return 'PASS'
 def _tamper(self,path,code):
  d=Path(tempfile.mkdtemp()); q=d/path.name; shutil.copy2(path,q); q.write_bytes(q.read_bytes()+b'x')
  try: return self._expect(code,lambda:SyntheticMarketStateRunner._verify_file(q,hashlib.sha256(path.read_bytes()).hexdigest(),code))
  finally: shutil.rmtree(d)
 def n01(self): return self._tamper(self.r.outer_handoff,'FAIL_PROVIDER_HANDOFF_HASH_MISMATCH')
 def n02(self): return self._tamper(self.r.nested_evidence,'FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH')
 def n03(self): a=dict(self.r.authority); a['current_runtime_content_sha256']='b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2'; return self._expect('FAIL_MARKET_STATE_HASH_ROLE_SUBSTITUTION',lambda:self._event(authority=a))
 def n04(self): s=self._schema(); s['columns'][0]['nullable']=True; return self._expect('FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH',lambda:self.c.validate_schema_contract(s))
 def n05(self): return self._expect('FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE',lambda:self.c.validate_column_mapping(ENVELOPE_COLUMNS,PAYLOAD_COLUMNS,LINEAGE_COLUMNS[:-1]))
 def n06(self): r=copy.deepcopy(self.rows[0]); r[PAYLOAD_COLUMNS[0]]=None; return self._expect('FAIL_MARKET_STATE_CORE_FOUR_INCOMPLETE',lambda:self._event(row=r))
 def n07(self): r=copy.deepcopy(self.rows[0]); r[PAYLOAD_COLUMNS[0]]=float('nan'); return self._expect('FAIL_MARKET_STATE_NON_FINITE_VALUE',lambda:self._event(row=r))
 def n08(self): r=copy.deepcopy(self.rows[0]); r['source_lineage_json']='{'; return self._expect('FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON',lambda:self._event(row=r))
 def n09(self): return self._expect('FAIL_MARKET_STATE_TYPED_PAYLOAD_REQUIRED',lambda:self.c.require_typed_payload({}))
 def n10(self): return self._expect('FAIL_MARKET_STATE_SIDECAR_MISSING',lambda:self.c.join_rows([self.rows[0]],[],self.r.authority,self.sidecar_sha256))
 def n11(self): return self._expect('FAIL_MARKET_STATE_SIDECAR_DUPLICATE',lambda:self.c.join_rows([self.rows[0]],[self.sides[0],self.sides[0]],self.r.authority,self.sidecar_sha256))
 def n12(self): s=copy.deepcopy(self.sides[0]); s['ticker']='BAD'; return self._expect('FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH',lambda:self._event(side=s))
 def n13(self): r=copy.deepcopy(self.rows[0]); s=copy.deepcopy(self.sides[0]); r['state_output_fingerprint']=s['state_output_fingerprint']='0'*64; return self._expect('FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH',lambda:self._event(row=r,side=s))
 def n14(self): r=copy.deepcopy(self.rows[0]); s=copy.deepcopy(self.sides[0]); r['materialized_state_candidate_id']=s['materialized_state_candidate_id']='0'*64; return self._expect('FAIL_MARKET_STATE_CANDIDATE_ID_MISMATCH',lambda:self._event(row=r,side=s))
 def n15(self): r=copy.deepcopy(self.rows[0]); s=copy.deepcopy(self.sides[0]); r['decision_timestamp_utc']=s['decision_timestamp_utc']='2026-01-05 14:31:00'; return self._expect('FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC',lambda:self._event(row=r,side=s))
 def n16(self): s=copy.deepcopy(self.sides[0]); s['state_as_of_utc']='2026-01-05T14:32:00Z'; return self._expect('FAIL_MARKET_STATE_TEMPORAL_LEAKAGE',lambda:self._event(side=s))
 def n17(self): s=copy.deepcopy(self.sides[0]); s['component_availability_evidence'][0]['source_timestamp_utc']='2026-01-05T14:32:00Z'; return self._expect('FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER',lambda:self._event(side=s))
 def n18(self):
  v=self._validated(); e=v.event; s=MarketStateStore(); observed=self._expect('FAIL_MARKET_STATE_EARLY_STORE_INSERT',lambda:s.insert(v,e.state_available_at_utc-timedelta(microseconds=1))); assert observed=='FAIL_MARKET_STATE_EARLY_STORE_INSERT' and s.count==0 and not s.trace; return 'EVENT_NOT_DELIVERED_STORE_UNCHANGED'
 def n19(self): s=copy.deepcopy(self.sides[0]); s['state_publication_latency_policy_id']='other'; return self._expect('FAIL_MARKET_STATE_ZERO_LATENCY_POLICY',lambda:self._event(side=s))
 def n20(self): s=copy.deepcopy(self.sides[0]); s['state_replay_consumption_legality']='research_only'; return self._expect('FAIL_MARKET_STATE_NOT_DECISION_SAFE',lambda:self._event(side=s))
 def n21(self): s=copy.deepcopy(self.sides[0]); s['component_availability_evidence'].pop(); return self._expect('FAIL_MARKET_STATE_COMPONENT_SET',lambda:self._event(side=s))
 def n22(self): s=copy.deepcopy(self.sides[0]); s['component_availability_evidence'][0]['availability_status']='research_only'; return self._expect('FAIL_MARKET_STATE_COMPONENT_LEGALITY_CONTRADICTION',lambda:self._event(side=s))
 def n23(self): s=copy.deepcopy(self.sides[0]); s['component_availability_evidence'][0]['restriction_codes']=[]; return self._expect('FAIL_MARKET_STATE_RESTRICTION_PROPAGATION',lambda:self._event(side=s))
 def n24(self): e=self._event(); b=self._bar(); return self._expect('FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY',lambda:self.c.validate_ordered_sequence((e,b)))
 def n25(self): e=self._event(); return self._expect('FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE',lambda:self.c.require_probe_visibility(MarketStateStore(),e.materialized_state_candidate_id,e.state_available_at_utc))
 def n26(self): v=self._validated(); e=v.event; s=MarketStateStore(); s.insert(v,e.state_available_at_utc); return self._expect('FAIL_DUPLICATE_MARKET_STATE_EVENT',lambda:s.insert(v,e.state_available_at_utc))
 def n27(self):
  v1=self._validated(0); r=copy.deepcopy(self.rows[1]); side=copy.deepcopy(self.sides[1]); r['decision_timestamp_utc']=side['decision_timestamp_utc']=self.rows[0]['decision_timestamp_utc']; side['state_as_of_utc']=side['state_available_at_utc']=self.sides[0]['state_available_at_utc']
  for component in side['component_availability_evidence']: component['source_timestamp_utc']=component['component_as_of_utc']=component['component_available_at_utc']=self.sides[0]['state_available_at_utc']
  self._resign(r,side); v2=self._validated(row=r,side=side); s=MarketStateStore(); s.insert(v1,v1.event.state_available_at_utc); return self._expect('FAIL_CONFLICTING_MARKET_STATE_EVENT',lambda:s.insert(v2,v2.event.state_available_at_utc))
 def n28(self): v=self._validated(); e=v.event; s=MarketStateStore(); s.insert(v,e.state_available_at_utc); before=s.count; assert s.latest_visible('other',e.instrument_id,e.decision_timestamp_utc,e.state_available_at_utc) is None and s.count==before; return 'NO_RESULT_STORE_UNCHANGED'
 def n29(self): return self._expect('FAIL_MARKET_STATE_OPERATIONAL_ROUTING_PROHIBITED',lambda:self.c.reject_operational_routing('execution'))
 def n30(self): return self._expect('FAIL_EVENT_STATE_NOT_AUTHORIZED',lambda:state_aware_order_key(object()))
 def n31(self):
  path=Path(tempfile.mkdtemp())/'forbidden.parquet'; path.write_bytes(b'not parquet and must never be read')
  try: return self._expect('FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED',lambda:SyntheticMarketStateRunner().run(replace(self.r,config_path=path)))
  finally: shutil.rmtree(path.parent,ignore_errors=True)
 def n32(self): f={'fixture_class':'SYNTHETIC_TYPED_MARKET_STATE','physical_source_rows':0,'synthetic':True,'uses_provider_record_identity':True}; return self._expect('FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED',lambda:self.c.validate_fixture_boundary(f))
 def n33(self):
  return 'PASS_WITH_IDENTICAL_SCIENTIFIC_HASHES' if self._clean_root_manifest_evidence()['all_scientific_hashes_match'] else 'FAIL'
 def _clean_root_manifest_evidence(self):
  roots=[Path(tempfile.mkdtemp(prefix='bt014_clean_a_')),Path(tempfile.mkdtemp(prefix='bt014_clean_b_'))]
  try:
   manifests=[]
   for root in roots:
    fixture=root/'fixture'; shutil.copytree(self.r.fixture_root,fixture); evidence=root/'evidence'; evidence.mkdir()
    outer=evidence/self.r.outer_handoff.name; nested=evidence/self.r.nested_evidence.name; adoption=evidence/'adoption.json'; config=root/'config.json'
    shutil.copy2(self.r.outer_handoff,outer); shutil.copy2(self.r.nested_evidence,nested); shutil.copy2(self.r.adoption_record,adoption)
    shutil.copy2(self.r.config_path,config) if self.r.config_path is not None else config.write_text('{}\n',encoding='utf-8',newline='\n')
    req=replace(self.r,fixture_root=fixture,outer_handoff=outer,nested_evidence=nested,adoption_record=adoption,output_root=root/'runs',config_path=config,run_id='clean')
    runner=SyntheticMarketStateRunner(); result=runner.run(req); report={'status':'PASS','positive_case_count':15,'negative_case_count':33,'failed_case_count':0}; det={'status':'PASS','hash':result['deterministic_output_hash']}
    run_dir=runner.write_result(req,result,report,det); final=json.loads((run_dir/'final_manifest.json').read_text(encoding='utf-8'))
    manifests.append({'deterministic_output_hash':result['deterministic_output_hash'],'scientific_manifest_hash':final['scientific_manifest_hash'],'artifact_hashes':final['output_artifact_hashes']})
   return {'all_scientific_hashes_match':manifests[0]==manifests[1],'root_a':manifests[0],'root_b':manifests[1]}
  finally:
   for root in roots: shutil.rmtree(root,ignore_errors=True)

