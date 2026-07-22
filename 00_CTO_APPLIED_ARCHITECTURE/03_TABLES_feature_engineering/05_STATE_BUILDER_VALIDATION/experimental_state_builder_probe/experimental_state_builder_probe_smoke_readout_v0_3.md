# Experimental State Builder Probe Smoke Readout v0.3

Status: `executed`
Date: `2026-07-21`
Scope: `experimental_physical_source_binding_gate_opened`

This readout records the third experimental State Builder probe after
renaming the active mode to `binding_and_path_check_only` and separating path
binding from future schema validation.

## Run

```text
run_id = experimental_state_builder_probe_v0_3_20260721T095712Z
script_version = experimental_state_builder_probe_v0_3
config = configs/experimental_state_builder_probe_v0_1.json
source_binding_registry = configs/experimental_source_binding_registry_v0_1.json
mode = binding_and_path_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
```

## Gate Decision

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = OPEN
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
physical_candidate_roots = PENDING
physical_source_binding = INCOMPLETE
path_validation = NOT_EXECUTED
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
warn_count = 21
source_warn_count = 21
pass_count = 99
pass_with_finding_count = 21
blocked_expected_count = 1
blocked_capability_leaks = 0

active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 0
unbound_unique_source_aliases = 10
blocked_unique_source_aliases = 3

physical_paths_checked = 0
physical_paths_found = 0
physical_paths_missing = 0
```

## Unique Active Source Aliases Pending Binding

```text
004_master_daily_table
006_halts_table
009_fundamentals_asof_table
010_news_context_table
011_short_context_table
012_regime_context_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

## Mode Boundary

`binding_and_path_check_only` authorizes filesystem metadata checks for
declared physical candidate roots only.

It does not authorize:

```text
schema metadata discovery
bounded sample reads
full data reads
State materialization
builder execution
Market State Integration
```

## Next Binding Order

Bind source aliases by source family, not all at once.

First batch:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

Then:

```text
raw_quotes
015_microstructure_features_table_candidate
```

Then:

```text
010_news_context_table
009_fundamentals_asof_table
011_short_context_table
012_regime_context_table
006_halts_table
```

## Expected Next Run Shape

After binding only the first batch, the expected system-level result should be:

```text
bound_unique_source_aliases = 3
unbound_unique_source_aliases = 7
physical_source_binding = PARTIAL
path_validation = PASS
schema_validation = NOT_EXECUTED
data_validation = NOT_AUTHORIZED
```

`path exists` must not be treated as `source is valid`. Schema, grain,
temporal legality, quality and lineage validation remain separate future gates.
