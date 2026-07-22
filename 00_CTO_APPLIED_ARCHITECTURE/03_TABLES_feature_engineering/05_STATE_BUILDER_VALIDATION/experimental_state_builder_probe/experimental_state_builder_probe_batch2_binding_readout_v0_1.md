# Experimental State Builder Probe - Batch 2 Binding Readout

Status: `experimental_physical_source_binding_batch2_partial_v0_1`
Date: `2026-07-21`
Scope: `non_production_path_probe_only`

## Decision

Batch 2 extends the governed experimental physical binding layer.

Result:

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = PARTIAL_OPEN
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
run_id = experimental_state_builder_probe_v0_3_20260721T103259Z
script_version = experimental_state_builder_probe_v0_3
mode = binding_and_path_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
```

## Gate Results

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
fail_count = 0
warn_count = 5
source_warn_count = 5
pass_count = 115
pass_with_finding_count = 5
blocked_expected_count = 1
blocked_capability_leaks = 0
```

## Source Binding Coverage

```text
active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 5
unbound_unique_source_aliases = 5
blocked_unique_source_aliases = 3
physical_paths_checked = 5
physical_paths_found = 5
physical_paths_missing = 0
```

Bound active aliases:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

Unbound active aliases:

```text
006_halts_table
009_fundamentals_asof_table
010_news_context_table
011_short_context_table
012_regime_context_table
```

Expected blocked aliases:

```text
future_borrow_locate_ssr_sources
future_macro_economic_source
future_trade_quote_aligned_surface
```

## Batch 2 Bindings

```text
raw_quotes
    binding_status = candidate_bound_for_path_probe
    physical_candidate_root = G:/TSIS/data/quotes_
    dataset_format = partitioned_parquet_dataset
    discovery_rule = explicit_official_root_path_check_only
    partition_convention = ticker=<ticker>/year=<YYYY>/month=<MM>/day=<DD>/quotes.parquet
    read_scope = filesystem_metadata_only

015_microstructure_features_table_candidate
    binding_status = candidate_bound_for_path_probe
    physical_candidate_root = G:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate_controlled_25_per_role
    dataset_format = partitioned_parquet_dataset
    discovery_rule = explicit_controlled_candidate_root_path_check_only
    partition_convention = year=<YYYY>/month=<MM>/part-*.parquet
    read_scope = filesystem_metadata_only
```

## Quotes Root Decision

`raw_quotes` uses:

```text
G:/TSIS/data/quotes_
```

as the local path-probe mirror of the approved official quotes root:

```text
E:/TSIS/data/quotes_
```

Evidence basis:

```text
C:/TSIS_Data/CHANGELOG.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/CHANGELOG.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/transversal/raw_storage_parity_audit_requirement_v0_1.md
```

Those documents record the `2026-07-07` `D:/quotes -> E:/TSIS/data/quotes_`
transfer approval after structural parity and SHA256 retry closure.

For this decision:

```text
G:/TSIS/data/quotes_ = local official-root mirror candidate
G:/TSIS/data/quotes = not used for raw_quotes binding
```

Path existence is not dataset promotion and does not validate physical schema,
grain, temporal legality, quote quality or lineage completeness.

## 015 Candidate Boundary

`015_microstructure_features_table_candidate` binds to the controlled v0.2
candidate surface:

```text
microstructure_features_table_v0_2_candidate_controlled_25_per_role
```

This remains:

```text
controlled_candidate_not_promoted
full_universe_claim = false
path_probe_only = true
```

The path probe confirms candidate root existence only. It does not validate
schema, candidate grain uniqueness, temporal observability, quality fields,
lineage fields or production readiness.

## Next Batch

Continue governed experimental physical binding for the context family:

```text
010_news_context_table
009_fundamentals_asof_table
011_short_context_table
012_regime_context_table
006_halts_table
```

Do not open schema validation or data reads until the active physical binding
layer is complete or an explicit intermediate gate is approved.
