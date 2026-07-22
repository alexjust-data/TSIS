# Experimental Bounded Sample Validation Authorization v0.1

status: `authorized_for_experimental_probe_only`
phase: `Phase B - experimental builder validation`
effective_scope: `bounded_identity_and_temporal_validation`

## Purpose

This artifact authorizes the first bounded row-read gate for the experimental
State Builder probe.

It does not authorize production builder execution, State materialization,
State consumption, dataset promotion, or any full-data read.

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
configs/experimental_bounded_sample_scope_v0_1.json
```

## Authorized Sources

The first bounded sample gate is limited to these source aliases:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

These sources are selected because they contain the current execution-critical
restrictions:

```text
identity evidence
timestamp parsing
timestamp unit detection
bar cutoff legality
conservative daily row availability
quality restrictions still pending
```

Contextual sources remain out of scope for this first bounded sample.

## Hard Limits

```text
maximum_sources = 5
maximum_files_per_source = 3
maximum_rows_per_file = 1000
maximum_total_rows = 10000
full_scan_allowed = false
```

The probe must stop before exceeding these limits.

## Authorized Operations

The probe may:

```text
read only allowed columns declared in the bounded sample scope
read only bounded row samples from selected representative parquet files
parse timestamp fields according to explicit policy logic
detect raw quote timestamp unit from bounded numeric evidence
validate bounded physical identity evidence
check bounded bar cutoff legality
execute daily_row_availability_policy_v0_1 on bounded rows
write reports only under the experimental probe run directory
```

The probe may not:

```text
write to source datasets
rewrite or repair source datasets
perform full scans
infer grain uniqueness as system-wide truth
validate complete temporal legality over history
calculate Information Object features
materialize Market State or Event State
promote any dataset or output
authorize operational consumption
```

## Expected Outputs

The authorized run may produce:

```text
bounded_sample_manifest.json
sample_read_limits_report.json
identity_resolution_report.csv
timestamp_parse_report.csv
cutoff_legality_report.csv
daily_availability_policy_report.csv
bounded_sample_summary.json
bounded_sample_findings.md
```

All outputs are experimental evidence only.

## Non-Claims

A passing bounded sample gate does not claim:

```text
builder_validation = PASS
grain_validation = PASS
temporal_value_validation = PASS
quality_semantics_validation = PASS
Market State Integration = ready
production readiness
```

The next gate after this authorization is bounded identity and temporal
validation only.
