# Experimental State Builder Probe Smoke Readout v0.2

Status: `executed`
Date: `2026-07-21`
Scope: `binding_and_schema_check_only_non_production_probe`

This readout records the second experimental State Builder probe after
separating logical source aliases from governed experimental physical bindings.

## Run

```text
run_id = experimental_state_builder_probe_v0_2_20260721T093704Z
script_version = experimental_state_builder_probe_v0_2
config = configs/experimental_state_builder_probe_v0_1.json
source_binding_registry = configs/experimental_source_binding_registry_v0_1.json
mode = binding_and_schema_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
```

## Institutional Result

```text
overall_status = passed_contract_check_pending_source_binding

contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
physical_source_binding = INCOMPLETE
schema_resolution = NOT_EXECUTED
data_resolution = NOT_AUTHORIZED
```

This means:

```text
No contract or governance failures were detected.

The run cannot yet evaluate physical resolvability because active source
surfaces remain unbound in the experimental registry.
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

## Finding

The probe now distinguishes:

```text
active_source_alias_usages = object-source references
unique_active_source_aliases = governed logical source surfaces
```

The 21 warnings represent 21 object-source usages, not 21 different datasets.
The next engineering gate is to bind the 10 unique aliases to governed
experimental physical candidate roots.

## Authority Boundary

```text
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
full_data_read_authorized = false
```

The run is an experimental resolution probe only. It does not materialize
Market State and does not authorize production builder development.

## Next Step

```text
source_alias
    -> governed experimental physical binding
        -> grain
        -> keys
        -> temporal fields
        -> minimum schema
        -> quality / lineage
```

Then rerun the probe in `binding_and_schema_check_only` mode. Do not enable
bounded sample reads or full data reads until the physical binding layer passes.
