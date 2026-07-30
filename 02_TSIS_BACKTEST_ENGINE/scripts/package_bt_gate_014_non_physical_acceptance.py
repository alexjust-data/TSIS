from __future__ import annotations
import hashlib,json,zipfile
from datetime import datetime,timezone
from pathlib import Path
BT=Path(__file__).resolve().parents[1]; TSIS=BT.parent; GOV=TSIS/'00_CTO/14_BACKTEST_ENGINE'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); out=BT/f'bt_gate_014_non_physical_consumer_acceptance_packet_{stamp}.zip'
 files=[]
 for rel in ['pyproject.toml','AGENTS.md','README.md','CHANGELOG.md','RUN_BT_GATE_014_INCLUDED_TESTS.py','RUN_FULL_REPOSITORY_TESTS.py','docs/00_system/15_BT_GATE_014_POINT_IN_TIME_MARKET_STATE_CONSUMER_CONTRACT_V0_1.md','docs/00_system/16_BT_GATE_014_NON_PHYSICAL_CONSUMER_ACCEPTANCE_PACKET_V0_1.md','docs/00_system/BACKTEST_ENGINE_ROADMAP.md','configs/runs/bt_gate_014_non_physical_market_state_consumer_v0_1.json','scripts/run_bt_gate_014_non_physical_market_state_consumer.py','scripts/package_bt_gate_014_non_physical_acceptance.py','tests/__init__.py','tests/unit/__init__.py','tests/unit/test_market_state_consumer.py','tests/unit/test_market_state_acceptance_matrix.py','tests/unit/test_market_state_external_review_regressions.py']:
  files.append((BT/rel,f'02_TSIS_BACKTEST_ENGINE/{rel}'))
 for base,arcbase in [(BT/'src','02_TSIS_BACKTEST_ENGINE/src'),(BT/'tests','02_TSIS_BACKTEST_ENGINE/tests'),(BT/'configs','02_TSIS_BACKTEST_ENGINE/configs'),(BT/'tests/fixtures/bt_gate_014_synthetic_market_state','02_TSIS_BACKTEST_ENGINE/tests/fixtures/bt_gate_014_synthetic_market_state'),(BT/'evidence/provider_handoffs/bt_gate_014','02_TSIS_BACKTEST_ENGINE/evidence/provider_handoffs/bt_gate_014'),(BT/'runs/bt_gate_014_non_physical_market_state_consumer_v0_1','02_TSIS_BACKTEST_ENGINE/runs/bt_gate_014_non_physical_market_state_consumer_v0_1')]:
  for q in sorted(x for x in base.rglob('*') if x.is_file() and '__pycache__' not in x.parts and q_suffix(x)):
   files.append((q,f'{arcbase}/{q.relative_to(base).as_posix()}'))
 pm=json.loads((GOV/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
 for rel in sorted(pm['files']): files.append((TSIS/rel,rel))
 files.append((GOV/'PACKAGE_MANIFEST.json','00_CTO/14_BACKTEST_ENGINE/PACKAGE_MANIFEST.json'))
 seen={};
 for source,arc in files:
  if not source.is_file(): raise FileNotFoundError(source)
  if source.suffix.lower()=='.parquet' and '02_TSIS_BACKTEST_ENGINE/tests/fixtures/' not in arc.replace('\\','/'): raise RuntimeError(f'Provider/state Parquet prohibited: {source}')
  if arc in seen:
   if seen[arc]!=source: raise RuntimeError(f'duplicate {arc}')
   continue
  seen[arc]=source
 market_bar_parquets=sum(1 for arc in seen if arc.lower().endswith('.parquet'))
 direct_json=sum(1 for arc in seen if arc.lower().endswith('.json'))
 nested_json=0
 for source in seen.values():
  if source.suffix.lower()=='.zip':
   with zipfile.ZipFile(source) as nested: nested_json+=sum(1 for name in nested.namelist() if name.lower().endswith('.json'))
 manifest={'declared_file_json_count_excluding_zip_manifest':direct_json,'zip_json_entry_count_including_zip_manifest':direct_json + 1,'json_entries_directly_inside_included_zips':nested_json,'provider_state_parquet_files':0,'market_bar_fixture_parquet_files':market_bar_parquets,'package_id':'BT_GATE_014_NON_PHYSICAL_CONSUMER_ACCEPTANCE_PACKET','status':'IMPLEMENTED_PENDING_PHASE_B_EXTERNAL_RE_REVIEW','phase_b_external_review':'PENDING_RE_REVIEW','new_single_use_physical_authorization':'NOT_AUTHORIZED','physical_consumer_read':'NOT_EXECUTED','physical_state_rows_read':0,'files':{arc:{'sha256':sha(source),'size_bytes':source.stat().st_size} for arc,source in sorted(seen.items())}}
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for arc,source in sorted(seen.items()): z.write(source,arc)
  z.writestr('ZIP_MANIFEST.json',json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 print(json.dumps({'zip_path':str(out),'zip_sha256':sha(out),'zip_entries':len(seen)+1,'manifest_declared_files':len(seen)},indent=2)); return 0
def q_suffix(p): return p.suffix.lower() not in {'.pyc','.pyo'}
if __name__=='__main__': raise SystemExit(main())
