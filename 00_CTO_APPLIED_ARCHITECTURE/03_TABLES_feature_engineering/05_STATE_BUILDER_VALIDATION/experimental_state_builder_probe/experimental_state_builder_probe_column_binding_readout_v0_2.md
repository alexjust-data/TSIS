# Experimental State Builder Probe Column Binding Readout v0.2

Status: `experimental_logical_to_physical_binding_passed_with_restrictions_v0_2`
Date: `2026-07-21`
Scope: `phase_b_non_production_metadata_only_gate`

This readout supersedes:

```text
experimental_state_builder_probe_column_binding_readout_v0_1.md
```

It records the rerun after resolving the three critical blockers from v0.1 and
correcting boolean expected type families in the column binding registry.

## Reference Run

```text
run_id = experimental_state_builder_probe_v0_6_20260721T154601Z
script_version = experimental_state_builder_probe_v0_6
mode = logical_to_physical_binding_check_only
overall_status = passed_logical_to_physical_binding_with_restrictions
allow_data_read = false
dry_run = true
objects_checked = 12
```

## Gate Result

```text
contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_candidate_roots = BOUND
physical_source_binding = PASS
path_validation = PASS
schema_resolution = REEXECUTED_WITH_COLUMN_BINDINGS
schema_validation = PASS_WITH_RESTRICTIONS
logical_column_resolution = PASS_WITH_RESTRICTIONS
physical_schema_compatibility = PASS_WITH_RESTRICTIONS

data_resolution = NOT_AUTHORIZED
data_validation = NOT_AUTHORIZED
grain_validation = NOT_EXECUTED
temporal_value_validation = NOT_EXECUTED
quality_semantics_validation = NOT_EXECUTED
```

Decision:

```text
experimental_logical_to_physical_binding = PASS_WITH_RESTRICTIONS
critical_blockers = 0
bounded_sample_data_read = NOT_AUTHORIZED
state_materialization = NOT_AUTHORIZED
```

## Metrics

```text
active_source_alias_usages = 21
unique_active_source_aliases = 10
bound_unique_source_aliases = 10
unbound_unique_source_aliases = 0
physical_paths_checked = 10
physical_paths_found = 10

unique_sources_schema_checked = 10
unique_sources_schema_passed = 2
unique_sources_schema_passed_with_findings = 8
unique_sources_schema_blocked = 0
unique_sources_schema_failed = 0

logical_fields_expected = 154
logical_fields_resolved = 125
logical_fields_resolved_with_restrictions = 22
logical_fields_unresolved = 6
fields_requiring_cast = 5
critical_state_fields_failed = 0
critical_state_fields_blocked = 0
critical_temporal_fields_unresolved = 0
quality_fields_unresolved = 5
lineage_fields_unresolved = 1
```

## Critical Blocker Resolution

The three prior critical blockers are now resolved as restricted bindings:

```text
004_master_daily_table.as_of_utc
    resolution = RESOLVED_WITH_RESTRICTIONS
    mechanism = derived_from_existing_column
    policy = daily_row_availability_policy_v0_1
    note = conservative legal availability only; observed source availability remains unavailable

014_master_intraday_bar_table_candidate.instrument_id
    resolution = RESOLVED_WITH_RESTRICTIONS
    mechanism = physical_column:ticker
    policy = intraday_bar_identity_and_cutoff_policy_v0_1
    note = ticker is identity evidence; canonical ticker->instrument_id normalization remains required

014_master_intraday_bar_table_candidate.decision_timestamp_or_bar_end
    resolution = NOT_REQUIRED
    mechanism = external builder context
    policy = intraday_bar_identity_and_cutoff_policy_v0_1
    note = source contributes bar_end; builder invocation contributes decision_timestamp_utc
```

## Registry Corrections

Corrected expected type families from `date` to `boolean` for:

```text
009_fundamentals_asof_table.valid_for_event_context_candidate
009_fundamentals_asof_table.valid_for_state_component_candidate
010_news_context_table.valid_for_event_context_candidate
010_news_context_table.valid_for_state_component_candidate
011_short_context_table.valid_for_event_context_candidate
011_short_context_table.valid_for_state_component_candidate
012_regime_context_table.valid_for_event_context_candidate
012_regime_context_table.valid_for_state_component_candidate
```

## Remaining Non-Critical Unresolved Fields

These remain unresolved and must stay visible for later quality/lineage gates:

```text
014_master_intraday_bar_table_candidate.component_quality_flag
014_master_intraday_bar_table_candidate.temporal_legality_flag
015_microstructure_features_table_candidate.temporal_legality_flag
raw_quotes.as_of_utc
raw_quotes.quote_quality_flag
raw_quotes.two_sided_flag
```

## Remaining Cast / Parse Policies

These bindings are physically resolved but need future value-level validation:

```text
013_ohlcv_1m_quote_guarded.bar_end -> ts_utc string_to_timestamp
014_master_intraday_bar_table_candidate.bar_end -> ts_utc string_to_timestamp
015_microstructure_features_table_candidate.window_start_utc string_to_timestamp
015_microstructure_features_table_candidate.window_end_utc string_to_timestamp
raw_quotes.quote_timestamp int64_to_timestamp_unit_policy
```

## Authority Boundary

```text
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
bounded_sample_data_read_allowed = false
full_data_read_allowed = false
state_materialization_allowed = false
```

This run inspected filesystem and Parquet footer metadata only. It did not read
market rows, validate grain uniqueness, validate temporal values, infer quality
semantics, materialize State or authorize operational use.

## Next Gate

The next possible non-production gate is bounded sample validation, but it is
not authorized by this artifact.

Before opening it, TSIS must create or approve an explicit bounded-sample scope
covering:

```text
instrument sample
partition sample
maximum rows
identity normalization check
bar_end parse policy
raw_quotes timestamp unit policy
quality/lineage restriction handling
heartbeat / manifest requirements if runtime becomes long
```
