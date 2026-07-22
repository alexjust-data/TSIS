# Experimental State Builder Probe - Bounded Identity And Temporal Readout v0.1

Status: `bounded_identity_temporal_passed_with_restrictions`
Date: `2026-07-21`
Run: `experimental_state_builder_probe_v0_7_20260721T161612Z`

## Decision

```text
bounded_sample_validation = PASS_WITH_RESTRICTIONS
bounded_identity_validation = PASS_WITH_RESTRICTIONS
bounded_temporal_parse_validation = PASS_WITH_RESTRICTIONS
bounded_cutoff_legality = PASS
daily_availability_policy_execution = PASS_WITH_RESTRICTIONS
```

This closes the first bounded row-read gate for the experimental State Builder
probe.

It does not authorize:

```text
grain_validation = PASS
quality_semantics_validation = PASS
builder_validation_execution = PASS
Market State Integration = ready
production builder execution
State materialization
State consumption
dataset promotion
```

## Run Scope

Authorized by:

```text
experimental_bounded_sample_validation_authorization_v0_1.md
configs/experimental_bounded_sample_scope_v0_1.json
```

Mode:

```text
bounded_identity_and_temporal_validation
```

Sources sampled:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

Limits:

```text
maximum_sources = 5
maximum_files_per_source = 3
maximum_rows_per_file = 1000
maximum_total_rows = 10000
full_data_read_allowed = false
state_materialization_allowed = false
```

Observed:

```text
sources_sampled = 5
files_sampled = 8
rows_read = 6271
maximum_rows_authorized = 10000
rows_limit_respected = true
```

## Gate Result

```text
overall_status = passed_bounded_identity_temporal_validation_with_restrictions
contract_resolution = PASS
ontology_to_mapping_resolution = PASS
blocked_capability_masking = PASS
order_flow_expected_block = PASS
binding_contract_structure = PASS
physical_source_binding = PASS
path_validation = PASS
schema_resolution = REEXECUTED_WITH_COLUMN_BINDINGS
schema_validation = PASS_WITH_RESTRICTIONS
logical_column_resolution = PASS_WITH_RESTRICTIONS
data_resolution = BOUNDED_SAMPLE_AUTHORIZED_BY_SCOPE
data_validation = BOUNDED_SAMPLE_EXECUTED_WITH_LIMITS
grain_validation = NOT_EXECUTED
temporal_value_validation = BOUNDED_PARSE_AND_CUTOFF_EXECUTED
quality_semantics_validation = PARTIAL_NOT_EXECUTED
builder_validation_execution = NOT_EXECUTED
market_state_integration = NOT_EXECUTED
```

## Identity Findings

```text
identity_failures = 0
partition_row_mismatch_count = 0
ambiguous_reference_ticker_count = 0
```

`004_master_daily_table` provides internally consistent bounded identity
evidence.

`013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate`,
`015_microstructure_features_table_candidate` and `raw_quotes` remain
`PASS_WITH_RESTRICTIONS` because canonical identity normalization is not fully
validated by this bounded sample.

This is not a blocker for the current gate. It remains a blocker for later
builder execution unless a governed identity resolution policy/reference is
used.

## Temporal Findings

```text
timestamp_parse_failures = 0
cutoff_future_bar_leaks = 0
daily_availability_policy_failures = 0
```

Parsed fields:

```text
004.session_date = 2000 / 2000 parsed
013.ts_utc = 1221 / 1221 parsed
014.ts_utc = 1000 / 1000 parsed
015.window_start_utc = 50 / 50 parsed
015.window_end_utc = 50 / 50 parsed
raw_quotes.timestamp = 2000 / 2000 parsed
```

`raw_quotes.timestamp` is detected as:

```text
detected_unit = nanoseconds
unit_detection_evidence = median_abs_epoch=1765875600003352576
```

This remains `PASS_WITH_RESTRICTIONS` until the timestamp-unit policy is
promoted from bounded evidence to governed parse policy.

## Cutoff Findings

For both intraday bar surfaces:

```text
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

the bounded resolver selected:

```text
max(bar_end) where bar_end <= decision_timestamp
```

Result:

```text
future_bar_leaks = 0
cutoff_legality = PASS
```

This validates cutoff mechanics only for the bounded samples. It does not
validate complete temporal legality over all rows, sessions, instruments or
profiles.

## Daily Availability Policy

`004_master_daily_table.as_of_utc` remains governed by:

```text
daily_row_availability_policy_v0_1
```

Bounded execution result:

```text
daily_availability_policy_execution = PASS_WITH_RESTRICTIONS
policy_cases_checked = 40
policy_failures = 0
```

Restriction:

```text
calendar_status = weekend_and_holiday_calendar_not_validated_in_v0_1
```

The policy executed conservatively in sample, but full calendar-aware legal
availability remains a later gate.

## Artifacts

```text
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/pre_manifest.json
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/final_manifest.json
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/bounded_sample_manifest.json
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/sample_read_limits_report.csv
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/identity_resolution_report.csv
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/timestamp_parse_report.csv
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/cutoff_legality_report.csv
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/daily_availability_policy_report.csv
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/bounded_sample_summary.json
runs/experimental_state_builder_probe_v0_7_20260721T161612Z/bounded_sample_findings.md
```

## Next Gate

Open next:

```text
bounded_grain_validation
```

Do not open yet:

```text
feature_formula_execution
builder_validation_execution
Market State Integration
State materialization
production builder development
```
