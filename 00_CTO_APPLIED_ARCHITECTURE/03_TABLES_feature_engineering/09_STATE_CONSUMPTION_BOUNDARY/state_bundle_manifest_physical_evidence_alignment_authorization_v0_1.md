# StateBundle Manifest Physical Evidence Alignment Authorization v0.1

Gate: `state_bundle_manifest_physical_evidence_alignment_v0_1`
Date: `2026-07-29`
Status: `AUTHORIZED_READ_ONLY_METADATA_NO_PHYSICAL_READ`

## Purpose

Check whether the existing Market State control-plane bundle and response can be aligned to physical candidate evidence after provider hardening v0.1.2.

This gate may read JSON manifests, contracts and hash small metadata files. It must not open parquet bytes, read state rows, emit StateReplayFeed records, execute runtime requests or run a backtest.

## Inputs

```text
old_response = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000/case_01_response.json
old_bundle = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000/case_01_bundle.json
market_state_final_manifest = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/market_state_on_demand_scale_validation_v0_1_20260727T133641Z/final_manifest.json
candidate_output_manifest = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/market_state_on_demand_scale_validation_v0_1_20260727T133641Z/candidate_output_manifest.json
candidate_registry_entry = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/market_state_on_demand_scale_validation_v0_1_20260727T133641Z/candidate_registry_entry.json
lineage_manifest = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runs/market_state_on_demand_scale_validation_v0_1_20260727T133641Z/lineage_manifest.json
physical_schema_contract = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1/PHYSICAL_SCHEMA_CONTRACT.json
state_bundle_manifest_contract_v0_1_2 = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/state_bundle_manifest_contract_v0_1_2.json
```

## Hard Boundaries

```text
parquet_opened = false
parquet_hash_recomputed = false
state_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```
