# Experimental State Builder Probe Column Binding Readout v0.1

Status: `experimental_logical_to_physical_binding_blocked_v0_1`
Date: `2026-07-21`
Scope: `phase_b_non_production_logical_to_physical_binding_gate`

## Reference Run

```text
run_id = experimental_state_builder_probe_v0_5_20260721T144225Z
script_version = experimental_state_builder_probe_v0_5
mode = logical_to_physical_binding_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
```

Registry:

```text
configs/experimental_column_binding_registry_v0_1.json
registry_id = experimental_column_binding_registry_v0_1
logical_fields_bound = 154
active_source_aliases = 10
```

Artifacts:

```text
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/final_manifest.json
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/logical_physical_binding_report.csv
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/unresolved_logical_fields_report.csv
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/partition_binding_report.csv
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/manifest_binding_report.csv
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/cast_policy_requirements_report.csv
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/column_binding_schema_fingerprint_report.json
runs/experimental_state_builder_probe_v0_5_20260721T144225Z/column_binding_summary.json
```

## Institutional Result

```text
overall_status = blocked_logical_to_physical_binding
contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_candidate_roots = BOUND
physical_source_binding = PASS
path_validation = PASS
schema_resolution = REEXECUTED_WITH_COLUMN_BINDINGS
schema_validation = BLOCKED
logical_column_resolution = BLOCKED
physical_schema_compatibility = BLOCKED
data_resolution = NOT_AUTHORIZED
data_validation = NOT_AUTHORIZED
grain_validation = NOT_EXECUTED
temporal_value_validation = NOT_EXECUTED
quality_semantics_validation = NOT_EXECUTED
```

Interpretation:

```text
The v0.4 physical schema failure is no longer a raw missing-column problem.
Logical-to-physical binding resolves most fields explicitly.
The gate is blocked by critical unresolved availability and identity readiness.
```

This run used filesystem metadata and Parquet footer metadata only. It did not
read market rows, validate grain uniqueness, validate temporal values, infer
quality semantics, materialize State or authorize operational use.

## Aggregate Metrics

```text
active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 10
unbound_unique_source_aliases = 0
physical_paths_checked = 10
physical_paths_found = 10
physical_paths_missing = 0

unique_sources_schema_checked = 10
unique_sources_schema_passed_with_findings = 8
unique_sources_schema_blocked = 2
unique_sources_schema_failed = 0
schema_files_inspected = 17

logical_fields_expected = 154
logical_fields_resolved = 118
logical_fields_resolved_with_restrictions = 27
logical_fields_unresolved = 9

resolved_by_physical_column = 136
resolved_by_partition_key = 4
resolved_by_manifest_field = 1
resolved_by_dataset_metadata = 4
resolved_by_derivation = 0
resolved_by_constant_scope = 0

fields_requiring_cast = 5
critical_state_fields_failed = 0
critical_state_fields_blocked = 1
critical_temporal_fields_unresolved = 2
quality_fields_unresolved = 5
lineage_fields_unresolved = 1
```

## Alias Status

```text
004_master_daily_table = BLOCKED
014_master_intraday_bar_table_candidate = BLOCKED

006_halts_table = PASS_WITH_FINDINGS
009_fundamentals_asof_table = PASS_WITH_FINDINGS
010_news_context_table = PASS_WITH_FINDINGS
011_short_context_table = PASS_WITH_FINDINGS
012_regime_context_table = PASS_WITH_FINDINGS
013_ohlcv_1m_quote_guarded = PASS_WITH_FINDINGS
015_microstructure_features_table_candidate = PASS_WITH_FINDINGS
raw_quotes = PASS_WITH_FINDINGS
```

## Critical Blocks

```text
004_master_daily_table.as_of_utc
    criticality = temporal_required
    status = BLOCKED
    reason = no as_of_utc column or manifest-level availability timestamp
    rule = do not derive availability from session_date

014_master_intraday_bar_table_candidate.instrument_id
    criticality = state_required
    status = BLOCKED
    reason = physical column exists but inspected schema reports NullType
    required = identifier readiness review

014_master_intraday_bar_table_candidate.decision_timestamp_or_bar_end
    criticality = temporal_required
    status = BLOCKED
    reason = no governed physical resolution declared
```

## Non-Critical Unresolved Governance Fields

```text
014_master_intraday_bar_table_candidate.component_quality_flag
014_master_intraday_bar_table_candidate.temporal_legality_flag
015_microstructure_features_table_candidate.temporal_legality_flag
raw_quotes.as_of_utc
raw_quotes.quote_quality_flag
raw_quotes.two_sided_flag
```

These are not permitted to disappear. They remain governed restrictions for
future quality, lineage or availability policy work.

## Cast / Parse Policies Required

```text
013_ohlcv_1m_quote_guarded.bar_end -> ts_utc [string -> timestamp]
014_master_intraday_bar_table_candidate.bar_end -> ts_utc [string -> timestamp]
015_microstructure_features_table_candidate.window_start_utc [string -> timestamp]
015_microstructure_features_table_candidate.window_end_utc [string -> timestamp]
raw_quotes.quote_timestamp -> timestamp [int64 -> timestamp; unit policy required]
```

These bindings are resolved with restrictions. They do not authorize temporal
value validation until parse/unit/timezone policy is explicit.

## Partition Bindings Confirmed

```text
009_fundamentals_asof_table.statement_family -> statement_family=<family>
011_short_context_table.source_system -> source_system=<source>
011_short_context_table.observation_family -> observation_family=<family>
raw_quotes.instrument_id -> positional ticker directory under G:/TSIS/data/quotes_
```

Partition bindings are metadata bindings. Future readers must propagate the
partition value into logical resolution explicitly; no row-level assumption is
allowed.

## Prior v0.5 Attempt

```text
run_id = experimental_state_builder_probe_v0_5_20260721T133023Z
status = aborted_by_probe_reporting_bug
successor = experimental_state_builder_probe_v0_5_20260721T144225Z
```

The aborted run is not reference evidence. It is preserved with
`error_manifest.json` only for traceability.

## Decision

```text
experimental_physical_schema_validation = REEXECUTED_WITH_COLUMN_BINDINGS
experimental_logical_to_physical_binding = EXECUTED_BLOCKED
bounded_sample_read = NOT_AUTHORIZED
grain_validation = NOT_EXECUTED
temporal_value_validation = NOT_EXECUTED
builder_execution = NOT_AUTHORIZED
market_state_integration = NOT_OPEN
```

## Next Required Work

Resolve the blocked critical bindings before opening bounded sample reads:

```text
1. 004 availability contract:
       as_of_utc or manifest-level availability timestamp for master daily.

2. 014 identifier readiness:
       resolve NullType instrument_id or bind instrument identity via a governed
       alternative such as ticker plus identity normalization.

3. 014 decision timestamp alias:
       decide whether decision_timestamp_or_bar_end is an allowed logical alias
       for ts_utc/bar_end or requires a separate temporal field.
```

After those are governed, rerun:

```text
logical_to_physical_binding_check_only
```

Do not open bounded sample reads until the critical blocks are resolved or an
explicit accepted-with-restrictions decision is recorded.
