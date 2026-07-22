# Experimental State Builder Probe Batch 1 Binding Readout v0.1

Status: `executed`
Date: `2026-07-21`
Scope: `experimental_physical_source_binding_batch_1`

This readout records the first governed physical binding batch for the
experimental non-production State Builder probe.

The run binds only the first source family batch:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

No schema metadata, sample data, full data, State materialization, production
builder execution or Market State Integration was authorized.

## Run

```text
run_id = experimental_state_builder_probe_v0_3_20260721T102009Z
script_version = experimental_state_builder_probe_v0_3
config = configs/experimental_state_builder_probe_v0_1.json
source_binding_registry = configs/experimental_source_binding_registry_v0_1.json
mode = binding_and_path_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
```

## Bound Candidate Roots

```text
004_master_daily_table
    G:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1

013_ohlcv_1m_quote_guarded
    C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate

014_master_intraday_bar_table_candidate
    G:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded
```

These bindings prove only that the logical aliases now point to governed
candidate filesystem surfaces inside allowed roots and that those roots exist.

They do not prove:

```text
schema validity
minimum column presence
type compatibility
grain uniqueness
temporal observability
lineage sufficiency
dataset promotion
operational readiness
```

## Gate Decision

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = PARTIAL
path_validation = PASS
schema_resolution = NOT_OPEN
data_read = NOT_AUTHORIZED
builder_execution = NOT_AUTHORIZED
market_state_integration = NOT_OPEN
```

## Institutional Result

```text
overall_status = passed_contract_check_pending_source_binding

contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_candidate_roots = PARTIAL
physical_source_binding = PARTIAL
path_validation = PASS
schema_resolution = NOT_EXECUTED
schema_validation = NOT_EXECUTED
data_resolution = NOT_AUTHORIZED
data_validation = NOT_AUTHORIZED
```

## Metrics

```text
fail_count = 0
contract_fail_count = 0
source_fail_count = 0
warn_count = 9
source_warn_count = 9
pass_count = 111
pass_with_finding_count = 9
blocked_expected_count = 1
blocked_capability_leaks = 0

active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 3
unbound_unique_source_aliases = 7
blocked_unique_source_aliases = 3

physical_paths_checked = 3
physical_paths_found = 3
physical_paths_missing = 0
```

## Remaining Unbound Active Aliases

```text
006_halts_table
009_fundamentals_asof_table
010_news_context_table
011_short_context_table
012_regime_context_table
015_microstructure_features_table_candidate
raw_quotes
```

## Next Binding Batch

The next batch should bind the L1/microstructure family:

```text
raw_quotes
015_microstructure_features_table_candidate
```

This should remain inside `binding_and_path_check_only` unless the registry
authority and script mode are explicitly advanced to schema discovery.

## Boundary

This run does not close the physical binding gate for the full system. It
converts the gate from:

```text
physical_source_binding = INCOMPLETE
```

to:

```text
physical_source_binding = PARTIAL
```

`path exists` remains strictly weaker than `source is valid`.
