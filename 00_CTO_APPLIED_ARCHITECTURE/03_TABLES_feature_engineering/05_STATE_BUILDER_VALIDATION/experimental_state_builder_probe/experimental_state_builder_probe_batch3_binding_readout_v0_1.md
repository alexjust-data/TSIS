# Experimental State Builder Probe - Batch 3 Binding Readout

Status: `experimental_physical_source_binding_complete_v0_1`
Date: `2026-07-21`
Scope: `non_production_path_probe_only`

## Decision

The governed experimental physical binding layer is complete for the 10 active
source aliases used by the 12 `TSIS Market Ontology v1` Information Objects.

Result:

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = CLOSED_PASS
path_validation = PASS
schema_resolution = NOT_EXECUTED
data_read = NOT_AUTHORIZED
builder_execution = NOT_AUTHORIZED
market_state_integration = NOT_OPEN
```

No production builder, State consumption, schema metadata discovery, bounded or
full data read, physical materialization, dataset promotion or Market State
Integration is authorized by this run.

## Run

```text
run_id = experimental_state_builder_probe_v0_3_20260721T105146Z
script_version = experimental_state_builder_probe_v0_3
mode = binding_and_path_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
```

## Gate Results

```text
overall_status = passed_with_findings_and_expected_blocks
contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_candidate_roots = BOUND
physical_source_binding = PASS
path_validation = PASS
schema_resolution = NOT_EXECUTED
schema_validation = NOT_EXECUTED
data_resolution = NOT_AUTHORIZED
data_validation = NOT_AUTHORIZED
fail_count = 0
warn_count = 0
source_warn_count = 0
pass_count = 120
pass_with_finding_count = 0
blocked_expected_count = 1
blocked_capability_leaks = 0
```

The non-`passed` wording comes from the expected `Order Flow Pressure` block.
It is not a physical binding warning.

## Source Binding Coverage

```text
active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 10
unbound_unique_source_aliases = 0
blocked_unique_source_aliases = 3
physical_paths_checked = 10
physical_paths_found = 10
physical_paths_missing = 0
```

Bound active aliases:

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

Expected blocked aliases:

```text
future_borrow_locate_ssr_sources
future_macro_economic_source
future_trade_quote_aligned_surface
```

## Batch 3 Bindings

```text
010_news_context_table
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1
    official_root = E:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1
    registry = 01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/news_context_table_registry_entry.yaml
    partition_convention = published_year=<YYYY>/data_*.parquet

009_fundamentals_asof_table
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1
    official_root = E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1
    registry = 01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/fundamentals_asof_table_registry_entry.yaml
    partition_convention = statement_family=<family>/as_of_year=<YYYY>/data_*.parquet

011_short_context_table
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1
    official_root = E:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1
    registry = 01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/short_context_table_registry_entry.yaml
    partition_convention = source_system=<source_system>/observation_family=<short_interest|short_volume>/observation_year=<YYYY>/data_*.parquet

012_regime_context_table
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1
    official_root = E:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1
    registry = 01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/regime_context_table_registry_entry.yaml
    partition_convention = source_proxy_family=<etf|index>/observation_year=<YYYY>/data_*.parquet

006_halts_table
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
    official_primary_file = E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
    registry = 01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/outputs/halts_table_registry_entry.yaml
    partition_convention = single_file_halts_table_v0_1.parquet
```

## Boundary Notes

This run confirms only:

```text
source_alias resolves to one governed experimental physical candidate surface
candidate surface is inside an allowed root
candidate surface exists
```

It does not confirm:

```text
physical schema presence
schema type compatibility
grain uniqueness
decision-time temporal legality
quality flag semantics
lineage completeness
data usability
State materialization readiness
```

Special restrictions preserved:

```text
raw_quotes:
    uses G:/TSIS/data/quotes_ as local mirror of official E:/TSIS/data/quotes_

015_microstructure_features_table_candidate:
    controlled_candidate_not_promoted

011_short_context_table:
    borrow / locate / SSR claims remain blocked unless separate sources exist

012_regime_context_table:
    same-session intraday causal state remains blocked

006_halts_table:
    decision-time availability contract remains required
```

## Next Gate

The next executable gate should not be data read.

Recommended next mode:

```text
binding_and_schema_check_only
```

Allowed scope:

```text
filesystem_metadata_read_allowed = true
schema_metadata_read_allowed = true
bounded_sample_data_read_allowed = false
full_data_read_allowed = false
state_materialization_allowed = false
```

The next probe should compare only physical schema metadata against the minimum
required columns declared in the binding registry. Grain uniqueness, temporal
legality and quality semantics remain separate later gates.
