"""Synthetic-only BT-GATE-014 runner and evidence writer."""
from __future__ import annotations
import hashlib,json,zipfile
from dataclasses import dataclass,replace
from datetime import datetime,timedelta
from pathlib import Path
from typing import Any,Mapping

from tsis_backtest.preflight.contracts import MarketDataBar1m
from tsis_backtest.replay.contracts import ReplayBarEvent
from .consumer import FROZEN_PROVIDER_AUTHORITY,MarketStateConsumerV0_1,PHYSICAL_COLUMNS,PAYLOAD_COLUMNS,ENVELOPE_COLUMNS,LINEAGE_COLUMNS,_utc,canonical_hash,state_aware_order_key,strict_json_document
from .contracts import BoundedConsumerProbeObservation,BoundedMarketStateAvailable,MarketStateContractError,to_market_state_jsonable
from .store import MarketStateStore

@dataclass(frozen=True)
class SyntheticMarketStateRunRequest:
    run_id: str; output_root: Path; fixture_root: Path; adoption_record: Path; outer_handoff: Path; nested_evidence: Path; authority: Mapping[str,str]; physical_execution_authorized: bool=False; config_path: Path|None=None

class SyntheticMarketStateRunner:
    def __init__(self) -> None: self.consumer=MarketStateConsumerV0_1()

    def run(self,request:SyntheticMarketStateRunRequest) -> dict[str,Any]:
        if request.physical_execution_authorized: raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED","Fase B")
        if request.config_path is None: raise MarketStateContractError('FAIL_BT_GATE_014_CONFIG_REQUIRED','config_path')
        for p in (request.fixture_root,request.adoption_record,request.outer_handoff,request.nested_evidence,request.config_path):
            if p.suffix.lower()=='.parquet': raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED",str(p))
        self.consumer.validate_authority_roles(request.authority)
        config_data,config_identity=self._read_stable_json_with_identity(request.config_path)
        if config_data.get('authority')!=dict(request.authority): raise MarketStateContractError('FAIL_MARKET_STATE_AUTHORITY_MISMATCH','config.authority')
        if config_data.get('physical_execution_authorized') is not False:
            raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED","config physical execution")
        adoption,adoption_identity=self._read_stable_json_with_identity(request.adoption_record)
        outer_actual=self._file_identity(request.outer_handoff)
        nested_actual=self._file_identity(request.nested_evidence)
        outer_claims=(adoption['outer_handoff'].get('sha256_before_adoption'),adoption['outer_handoff'].get('sha256_after_adoption'),config_data.get('outer_handoff_sha256'),request.authority.get('provider_handoff_sha256'),FROZEN_PROVIDER_AUTHORITY['provider_handoff_sha256'])
        if any(value!=outer_actual['sha256'] for value in outer_claims): raise MarketStateContractError('FAIL_PROVIDER_HANDOFF_HASH_MISMATCH','provider handoff trust root')
        nested_claims=(adoption['nested_provider_evidence'].get('sha256_before_adoption'),adoption['nested_provider_evidence'].get('sha256_after_adoption'),adoption['nested_provider_evidence'].get('nested_inside_outer_sha256'),config_data.get('nested_evidence_sha256'),request.authority.get('nested_provider_evidence_sha256'),FROZEN_PROVIDER_AUTHORITY['nested_provider_evidence_sha256'])
        if any(value!=nested_actual['sha256'] for value in nested_claims): raise MarketStateContractError('FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH','nested evidence trust root')
        if adoption['outer_handoff'].get('size_bytes')!=outer_actual['size_bytes'] or config_data.get('outer_handoff_size_bytes')!=outer_actual['size_bytes']: raise MarketStateContractError('FAIL_PROVIDER_HANDOFF_HASH_MISMATCH','outer size')
        if adoption['nested_provider_evidence'].get('size_bytes')!=nested_actual['size_bytes'] or config_data.get('nested_evidence_size_bytes')!=nested_actual['size_bytes']: raise MarketStateContractError('FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH','nested size')
        with zipfile.ZipFile(request.outer_handoff) as z:
            if any(n.lower().endswith('.parquet') for n in z.namelist()): raise MarketStateContractError("FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED","handoff contains parquet")
            nested_name=next(n for n in z.namelist() if n.endswith(request.nested_evidence.name))
            if hashlib.sha256(z.read(nested_name)).hexdigest()!=nested_actual['sha256']: raise MarketStateContractError("FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH",nested_name)
            schema_name=next(n for n in z.namelist() if n.endswith('/PHYSICAL_SCHEMA_CONTRACT.json'))
            schema=strict_json_document(z.read(schema_name).decode('utf-8-sig'),schema_name)
            if hashlib.sha256(z.read(schema_name)).hexdigest()!=request.authority['structural_schema_sha256']: raise MarketStateContractError("FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH","schema hash")
        self.consumer.validate_schema_contract(schema)
        fixture_manifest,fixture_manifest_identity=self._read_stable_json_with_identity(request.fixture_root/'synthetic_fixture_manifest.json')
        self.consumer.validate_fixture_manifest_boundary(fixture_manifest)
        required_fixture_files={'synthetic_raw_rows.json','synthetic_sidecar.json','synthetic_market_bars.json'}
        declared_fixture_files=set(fixture_manifest.get('files',{}))
        physical_fixture_files={path.name for path in request.fixture_root.iterdir() if path.is_file()}
        if declared_fixture_files!=required_fixture_files or physical_fixture_files!=(required_fixture_files|{'synthetic_fixture_manifest.json'}): raise MarketStateContractError('FAIL_SYNTHETIC_INPUT_MANIFEST_COVERAGE','closed fixture inventory')
        fixture_identities={}
        for name,expected in fixture_manifest['files'].items():
            path=request.fixture_root/name; raw=path.read_bytes()
            actual={'relative_path':f'tests/fixtures/bt_gate_014_synthetic_market_state/{name}','size_bytes':len(raw),'sha256_before_read':hashlib.sha256(raw).hexdigest()}
            if actual['size_bytes']!=expected.get('size_bytes') or actual['sha256_before_read']!=expected.get('sha256'): raise MarketStateContractError('FAIL_SYNTHETIC_INPUT_HASH_MISMATCH',name)
            fixture_identities[name]=actual
        rows_doc=self._read_stable_json(request.fixture_root/'synthetic_raw_rows.json')
        side_doc=self._read_stable_json(request.fixture_root/'synthetic_sidecar.json')
        bars_doc=self._read_stable_json(request.fixture_root/'synthetic_market_bars.json')
        for name,identity in fixture_identities.items():
            identity['sha256_after_read']=hashlib.sha256((request.fixture_root/name).read_bytes()).hexdigest()
            if identity['sha256_before_read']!=identity['sha256_after_read']: raise MarketStateContractError('FAIL_SOURCE_MUTATION',name)
        required_pins={'synthetic_fixture_manifest','adoption_record','outer_handoff','nested_evidence'}
        if any(f'{key}_sha256' not in config_data or f'{key}_size_bytes' not in config_data for key in required_pins): raise MarketStateContractError('FAIL_SYNTHETIC_INPUT_MANIFEST_COVERAGE','config pins')
        pinned={'synthetic_fixture_manifest':request.fixture_root/'synthetic_fixture_manifest.json','adoption_record':request.adoption_record,'outer_handoff':request.outer_handoff,'nested_evidence':request.nested_evidence}
        for key,path in pinned.items():
            if config_data.get(f'{key}_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest() or config_data.get(f'{key}_size_bytes')!=path.stat().st_size: raise MarketStateContractError('FAIL_SYNTHETIC_INPUT_HASH_MISMATCH',key)
        input_inventory={'configuration':config_identity,'fixture_manifest':fixture_manifest_identity,'fixtures':fixture_identities,'adoption_record':adoption_identity,'outer_handoff':outer_actual,'nested_provider_evidence':nested_actual}
        self.consumer.validate_fixture_boundary(rows_doc)
        self.consumer.validate_sidecar_fixture_boundary(side_doc)
        self.consumer.validate_market_bar_fixture_boundary(bars_doc)
        if (
            len(rows_doc['records'])!=fixture_manifest['record_count']
            or len(bars_doc['records'])!=fixture_manifest['market_bar_record_count']
        ):
            raise MarketStateContractError('FAIL_SYNTHETIC_INPUT_MANIFEST_COVERAGE','fixture record counts')
        consumed_sidecar_sha256=fixture_identities['synthetic_sidecar.json']['sha256_before_read']
        validated=self.consumer.validate_join_and_seal(
            rows_doc['records'],
            side_doc['records'],
            request.authority,
            consumed_sidecar_sha256,
        )
        events=tuple(item.event for item in validated)
        bars=tuple(self._bar_from_fixture(item) for item in bars_doc['records'])
        if len(bars)!=len(events): raise MarketStateContractError('FAIL_SYNTHETIC_MARKET_BAR_FIXTURE_MISMATCH','bar count')
        deliberately_unsorted=tuple(reversed((*events,*bars)))
        ordered=tuple(sorted(deliberately_unsorted,key=state_aware_order_key))
        keys=[state_aware_order_key(e) for e in ordered]
        if len(keys)!=len(set(keys)): raise MarketStateContractError("FAIL_MARKET_STATE_UNRESOLVED_ORDER_TIE","duplicate key")
        validated_by_id={item.event.materialized_state_candidate_id:item for item in validated}
        store=MarketStateStore(); observations=[]; sequence=[]; bar_count=0
        for index,event in enumerate(ordered):
            key=keys[index]
            if isinstance(event,ReplayBarEvent):
                bar_count+=1; sequence.append({'event_index':index,'event_type':'BAR','priority':1,'available_at_utc':event.available_at,'ticker':event.ticker,'order_key':key}); continue
            if not isinstance(event,BoundedMarketStateAvailable): raise MarketStateContractError("FAIL_EVENT_STATE_NOT_AUTHORIZED",type(event).__name__)
            insert_seq=store.insert(validated_by_id[event.materialized_state_candidate_id],event.state_available_at_utc)
            visible=store.get_exact(event.materialized_state_candidate_id,event.state_available_at_utc)
            if visible is None: raise MarketStateContractError("FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE",event.materialized_state_candidate_id)
            observations.append(BoundedConsumerProbeObservation(f"probe-{index:04d}",index,event.state_available_at_utc,event.materialized_state_candidate_id,event.state_output_fingerprint,17,event.restriction_codes,insert_seq,"VISIBLE"))
            sequence.append({'event_index':index,'event_type':event.event_type,'priority':2,'available_at_utc':event.state_available_at_utc,'ticker':event.ticker,'order_key':key})
        self.consumer.validate_ordered_sequence(ordered)
        semantic={'event_sequence':sequence,'events':[e.to_dict() for e in events],'store_trace':to_market_state_jsonable(store.trace),'observations':[o.to_dict() for o in observations]}
        return {'gate_id':'BT-GATE-014','gate_name':'POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1','implementation_phase':'BOUNDED_NON_PHYSICAL_IMPLEMENTATION','run_id':request.run_id,'validation_status':'PASS','provider_handoff_adoption':'PASS','physical_data_files_opened':0,'physical_state_rows_read':0,'market_data_events_processed':bar_count,'market_state_events_received':len(events),'market_state_events_validated':len(events),'market_state_store_inserts':store.count,'consumer_probe_observations':len(observations),'early_observations':0,'strategy_callbacks':0,'signals_emitted':0,'orders_emitted':0,'fills_emitted':0,'positions_mutated':0,'cash_mutations':0,'equity_mutations':0,'PnL_calculated':False,'deterministic_output_hash':canonical_hash(semantic),'semantic':semantic,'fixture_manifest':fixture_manifest,'schema':schema,'resolved_input_inventory':input_inventory}

    def write_result(self,request:SyntheticMarketStateRunRequest,result:Mapping[str,Any],negative_report:Mapping[str,Any]|None=None,determinism_report:Mapping[str,Any]|None=None) -> Path:
        run_dir=request.output_root/request.run_id
        if run_dir.exists() and any(run_dir.iterdir()): raise MarketStateContractError("FAIL_NONEMPTY_RUN_DIRECTORY",str(run_dir))
        run_dir.mkdir(parents=True,exist_ok=True)
        artifacts={
          'provider_handoff_adoption_record.json':json.loads(request.adoption_record.read_text(encoding='utf-8')),
          'market_state_physical_column_mapping.json':{'declared':list(PHYSICAL_COLUMNS),'envelope':list(ENVELOPE_COLUMNS),'payload':list(PAYLOAD_COLUMNS),'lineage':list(LINEAGE_COLUMNS),'declared_count':40,'mapped_count':40,'unmapped':[],'duplicately_mapped':[]},
          'bounded_market_state_event_schema.json':{'event_type':'BoundedMarketStateAvailable','immutable':True,'MarketData':False,'execution_input':False},
          'typed_core_four_payload_schema.json':{'objects':{'price_location_structure':5,'price_movement':5,'trading_activity':4,'volatility_range_state':3},'field_count':17,'physical_type':'float64','nullable':False},
          'market_state_audit_lineage_schema.json':{'separate_from_scientific_payload':True,'restriction_raw_preserved':True,'recursive_immutability':True,'raw_parsed_consistency_required':True},
          'market_state_store_contract.json':{'immutable':True,'recursive_immutability':True,'validated_receipt_only':True,'primary_key':'materialized_state_candidate_id','fallbacks':False},
          'synthetic_fixture_manifest.json':result['fixture_manifest'],
          'synthetic_raw_rows.json':self._read_stable_json(request.fixture_root/'synthetic_raw_rows.json'),
          'synthetic_sidecar.json':self._read_stable_json(request.fixture_root/'synthetic_sidecar.json'),
          'synthetic_market_bars.json':self._read_stable_json(request.fixture_root/'synthetic_market_bars.json'),
          'resolved_input_manifest.json':{'fixture_class':'SYNTHETIC_TYPED_MARKET_STATE','physical_rows':0,'inputs':result['resolved_input_inventory'],'outer_handoff_sha256':request.authority['provider_handoff_sha256'],'nested_provider_sha256':request.authority['nested_provider_evidence_sha256']},
          'state_aware_event_sequence.json':result['semantic']['event_sequence'],
          'market_state_validation_report.json':{k:v for k,v in result.items() if k not in {'semantic','fixture_manifest','schema'}},
          'market_state_store_trace.json':result['semantic']['store_trace'],
          'bounded_consumer_probe_observations.json':result['semantic']['observations'],
          'negative_derivative_report.json':negative_report or {'status':'NOT_EXECUTED'},
          'boundary_preservation_report.json':{'status':'PASS','physical_reads':0,'StateReplayFeed':'NOT_AUTHORIZED','Event_State':'NOT_OPEN','strategy_callbacks':0,'orders':0,'fills':0,'PnL':False},
          'determinism_report.json':determinism_report or {'status':'NOT_EXECUTED','deterministic_output_hash':result['deterministic_output_hash']},
        }
        hashes={}
        for name,data in artifacts.items():
            path=run_dir/name; self._write_json(path,data); hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        final={'gate_id':'BT-GATE-014','gate_name':'POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1','contract_version':'V0.1','implementation_phase':'BOUNDED_NON_PHYSICAL_IMPLEMENTATION','provider_handoff_package_name':request.outer_handoff.name,'provider_handoff_sha256':request.authority['provider_handoff_sha256'],'nested_provider_evidence_package_name':request.nested_evidence.name,'nested_provider_evidence_sha256':request.authority['nested_provider_evidence_sha256'],'structural_schema_sha256':request.authority['structural_schema_sha256'],'profile_provenance_sha256':'b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2','current_runtime_content_sha256':request.authority['current_runtime_content_sha256'],'state_bundle_ref_id':request.authority['state_bundle_ref_id'],'state_bundle_canonical_sha256':request.authority['state_bundle_canonical_sha256'],'profile_id':'market_state_core_four_intraday_profile_v0_1','state_schema_version':'core_four_market_state_candidate_physical_schema_v0_1','physical_column_count':40,'scientific_payload_field_count':17,'synthetic_fixture_class':'SYNTHETIC_TYPED_MARKET_STATE','synthetic_record_count':2,'physical_data_files_opened':0,'physical_state_rows_read':0,'market_state_events_received':result['market_state_events_received'],'market_state_store_inserts':result['market_state_store_inserts'],'consumer_probe_observations':result['consumer_probe_observations'],'early_observations':0,'strategy_callbacks':0,'signals_emitted':0,'orders_emitted':0,'fills_emitted':0,'positions_mutated':0,'cash_mutations':0,'equity_mutations':0,'PnL_calculated':False,'positive_case_count':(negative_report or {}).get('positive_case_count',0),'negative_case_count':(negative_report or {}).get('negative_case_count',0),'failed_case_count':(negative_report or {}).get('failed_case_count',0),'negative_test_aggregate_results':(negative_report or {}).get('status','NOT_EXECUTED'),'output_artifact_hashes':hashes,'deterministic_output_hash':result['deterministic_output_hash'],'boundary_preservation_status':'PASS','validation_status':'PASS','phase_b_external_review':'PENDING_RE_REVIEW','new_single_use_physical_authorization':'NOT_AUTHORIZED','next_required_authorization':'NEW_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION','next_required_action':'PHASE_B_EXTERNAL_RE_REVIEW'}
        final['scientific_manifest_hash']=canonical_hash({k:v for k,v in final.items() if k!='scientific_manifest_hash'})
        self._write_json(run_dir/'final_manifest.json',final)
        return run_dir

    @staticmethod
    def _bar_from_fixture(item: Mapping[str,Any]) -> ReplayBarEvent:
        required={"ticker","ts_start","ts_end","available_at","session_label","open","high","low","close","volume","price_view"}
        if set(item)!=required: raise MarketStateContractError('FAIL_SYNTHETIC_MARKET_BAR_FIXTURE_MISMATCH','bar shape')
        bar=MarketDataBar1m(str(item['ticker']),_utc(item['ts_start']),_utc(item['ts_end']),_utc(item['available_at']),str(item['session_label']),float(item['open']),float(item['high']),float(item['low']),float(item['close']),int(item['volume']),str(item['price_view']))
        return ReplayBarEvent('BAR',bar.ticker,bar.available_at,bar,{'synthetic':True,'independent_fixture':True})
    @staticmethod
    def _verify_file(path:Path,expected:str,code:str) -> None:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: raise MarketStateContractError(code,str(path))
    @staticmethod
    def _file_identity(path:Path) -> dict[str,Any]:
        raw=path.read_bytes()
        return {'relative_name':path.name,'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    @staticmethod
    def _read_stable_json_with_identity(path:Path) -> tuple[Any,dict[str,Any]]:
        before=path.read_bytes(); before_hash=hashlib.sha256(before).hexdigest(); data=strict_json_document(before.decode('utf-8-sig'),str(path)); after=path.read_bytes(); after_hash=hashlib.sha256(after).hexdigest()
        if before_hash!=after_hash: raise MarketStateContractError('FAIL_SOURCE_MUTATION',str(path))
        return data,{'relative_name':path.name,'size_bytes':len(before),'sha256_before_read':before_hash,'sha256_after_read':after_hash}
    @staticmethod
    def _read_stable_json(path:Path) -> Any:
        before=hashlib.sha256(path.read_bytes()).hexdigest(); data=strict_json_document(path.read_text(encoding='utf-8'),str(path)); after=hashlib.sha256(path.read_bytes()).hexdigest()
        if before!=after: raise MarketStateContractError("FAIL_SOURCE_MUTATION",str(path))
        return data
    @staticmethod
    def _write_json(path:Path,data:Any) -> None:
        path.write_text(json.dumps(to_market_state_jsonable(data),indent=2,sort_keys=True,ensure_ascii=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
