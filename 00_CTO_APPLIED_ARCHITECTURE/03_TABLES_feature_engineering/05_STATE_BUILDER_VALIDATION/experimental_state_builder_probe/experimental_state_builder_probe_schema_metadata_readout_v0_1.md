# Experimental State Builder Probe Schema Metadata Readout v0.1

Status: `experimental_physical_schema_validation_failed_v0_1`
Date: `2026-07-21`
Scope: `phase_b_non_production_schema_metadata_gate`

## Reference Run

```text
run_id = experimental_state_builder_probe_v0_4_20260721T123345Z
script_version = experimental_state_builder_probe_v0_4
mode = binding_and_schema_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
```

Artifacts:

```text
runs/experimental_state_builder_probe_v0_4_20260721T123345Z/final_manifest.json
runs/experimental_state_builder_probe_v0_4_20260721T123345Z/schema_availability_report.csv
runs/experimental_state_builder_probe_v0_4_20260721T123345Z/column_compatibility_report.csv
runs/experimental_state_builder_probe_v0_4_20260721T123345Z/schema_fingerprint_report.json
runs/experimental_state_builder_probe_v0_4_20260721T123345Z/schema_gate_summary.json
```

## Institutional Result

```text
overall_status = failed_schema_check
contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_candidate_roots = BOUND
physical_source_binding = PASS
path_validation = PASS
schema_resolution = EXECUTED
schema_validation = FAILED
data_resolution = NOT_AUTHORIZED
data_validation = NOT_AUTHORIZED
grain_validation = NOT_EXECUTED
temporal_value_validation = NOT_EXECUTED
quality_semantics_validation = NOT_EXECUTED
```

Interpretation:

```text
The ontology-to-mapping-to-binding chain remains valid.
The 10 active logical source aliases resolve to existing governed candidate
surfaces.
The next failure is physical schema compatibility, not source availability.
```

This run used filesystem and Parquet footer metadata only. It did not read
market rows, validate grain uniqueness, validate temporal values, infer quality
semantics, materialize State or authorize operational use.

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
unique_sources_schema_passed = 3
unique_sources_schema_failed = 7
schema_files_discovered = 17
schema_files_inspected = 17
minimum_columns_expected = 70
minimum_columns_found = 57
minimum_columns_missing = 13
temporal_fields_expected = 16
temporal_fields_found = 11
temporal_fields_missing = 5
quality_fields_missing = 9
lineage_fields_missing = 15
type_mismatches = 4
```

## Sources Passing Minimum Schema Metadata

```text
006_halts_table
010_news_context_table
012_regime_context_table
```

Passing schema metadata does not mean these sources are State-ready. It only
means the inspected physical schema metadata contains the required fields with
compatible type families for this gate. Grain uniqueness, temporal value
legality, quality semantics and row-level usability remain unexecuted.

## Failed Source Findings

```text
004_master_daily_table
    missing temporal field: as_of_utc
    note: minimum price/activity columns are physically present.

009_fundamentals_asof_table
    missing minimum field: statement_family
    likely next review: partition field or manifest-level binding.

011_short_context_table
    missing minimum fields: observation_family, source_system
    likely next review: partition field or source-scope binding.

013_ohlcv_1m_quote_guarded
    missing logical fields: instrument_id, bar_end, open, high, low, close, volume
    observed physical pattern: ticker, ts_utc, o, h, l, c, v
    required action: logical-to-physical column binding.

014_master_intraday_bar_table_candidate
    missing logical field: bar_end
    observed physical pattern: ts_utc plus open/high/low/close/volume
    additional finding: instrument_id exists but has null physical type in the inspected file.
    required action: column binding plus identifier readiness review.

015_microstructure_features_table_candidate
    required fields are mostly present, but window_start_utc and window_end_utc
    are observed as string while timestamp semantics are expected.
    required action: type policy or parse/cast capability gate.

raw_quotes
    missing logical fields: instrument_id, quote_timestamp
    observed physical pattern: timestamp, bid_price, ask_price, bid_size, ask_size,
    plus partition-level ticker/year/month/day.
    required action: logical-to-physical column and partition binding.
```

Governance/lineage fields are also missing for several aliases. Those findings
must not be silently waived. They may resolve through physical columns,
partition keys, manifests or dataset-level evidence, but the resolution must be
declared explicitly.

## Decision

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = CLOSED_PASS
experimental_physical_schema_validation = EXECUTED_FAILED
logical_to_physical_column_binding = REQUIRED_NEXT
data_read = NOT_AUTHORIZED
builder_execution = NOT_AUTHORIZED
market_state_integration = NOT_OPEN
```

## Next Required Artifact

Create a governed experimental column binding registry:

```text
configs/experimental_column_binding_registry_v0_1.json
```

Minimum expected fields:

```text
source_alias
logical_field
binding_status
physical_resolution_type
physical_column
partition_key
manifest_field
derivation_rule
expected_type_family
observed_type
semantic_role
criticality
temporal_role
quality_or_lineage_role
review_status
binding_evidence
```

Allowed `physical_resolution_type` examples:

```text
physical_column
partition_key
manifest_field
derived_from_existing_column
unavailable_pending_source_fix
not_required_for_current_gate
```

The next probe increment should resolve:

```text
logical_field
    -> physical_column | partition_key | manifest_field | derived metadata
```

and then rerun schema compatibility against resolved physical names.

Do not open bounded sample reads until this gate passes or produces an explicit
accepted-with-restrictions decision.
