# Experimental Bounded Grain Validation Authorization v0.1

status: `authorized_for_experimental_probe_only`
phase: `Phase B - experimental builder validation`
effective_scope: `bounded_grain_validation`

## Purpose

This artifact authorizes the bounded grain validation gate for the experimental
State Builder probe.

The gate checks whether declared physical key components are usable and
sufficiently unique inside an explicitly bounded sample.

It does not claim full-history uniqueness, builder correctness, feature
correctness, State readiness, production readiness, or Market State Integration
readiness.

## Authority

```text
bounded_sample_data_read_allowed = true
full_data_read_allowed = false
production_builder_authorized = false
state_materialization_allowed = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
writes_to_source_allowed = false
```

The authorization is valid only when the executable scope is provided by:

```text
configs/experimental_bounded_grain_scope_v0_1.json
```

## Authorized Sources

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

These are the same five execution-critical sources used by the bounded
identity and temporal validation gate, preserving continuity between identity,
time and candidate grain evidence.

## Hard Limits

```text
maximum_sources = 5
maximum_files_per_source = 3
maximum_rows_per_file = 2000
maximum_total_rows = 20000
full_scan_allowed = false
```

The probe must stop before exceeding these limits.

## Authorized Operations

The probe may:

```text
read only allowed columns declared in the bounded grain scope
read bounded row samples from selected representative parquet files
parse key timestamp/date fields needed for candidate key comparison
build physical key tuples inside the bounded sample
build restricted canonical key tuples where declared
count null key rows
count duplicate key groups
classify duplicate groups as identical or conflicting where possible
inspect declared partition/hidden dimensions from file paths
write reports only under the experimental probe run directory
```

The probe may not:

```text
write to source datasets
deduplicate rows
repair rows
perform full scans
claim full-history grain uniqueness
calculate Information Object features
execute feature builders
materialize Market State or Event State
promote any dataset or output
authorize operational consumption
```

## Expected Outputs

```text
bounded_grain_manifest.json
sample_read_limits_report.csv
grain_key_report.csv
duplicate_key_groups.csv
null_key_report.csv
hidden_dimension_findings.csv
raw_quotes_same_timestamp_report.csv
bounded_grain_summary.json
bounded_grain_findings.md
```

All outputs are experimental evidence only.

## Non-Claims

A passing bounded grain gate does not claim:

```text
grain_validation = PASS over full history
quality_semantics_validation = PASS
builder_validation_execution = PASS
Market State Integration = ready
State materialization = authorized
production builder = authorized
```

The next gate after bounded grain validation remains separate:

```text
bounded_quality_and_lineage_validation
```
