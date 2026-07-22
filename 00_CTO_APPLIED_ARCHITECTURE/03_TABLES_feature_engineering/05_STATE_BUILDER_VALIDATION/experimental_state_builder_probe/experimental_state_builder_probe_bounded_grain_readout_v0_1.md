# Experimental State Builder Probe - Bounded Grain Readout v0.1

Status: `bounded_grain_validation_passed_with_restrictions`
Date: `2026-07-21`
Run: `experimental_state_builder_probe_v0_8_20260721T171358Z`
Script: `experimental_state_builder_probe_v0_8`
Mode: `bounded_grain_validation`

## Decision

```text
bounded_grain_validation = PASS_WITH_RESTRICTIONS
bounded_grain_data_read = EXECUTED_WITH_LIMITS
builder_validation_execution = NOT_EXECUTED
market_state_integration = NOT_EXECUTED
```

The bounded grain gate is closed for the five execution-critical sources in
this scope. It validates only candidate key usability inside the authorized
sample. It does not claim full-history grain uniqueness, feature correctness,
builder correctness, State readiness, or operational authority.

## Authority Preserved

```text
bounded_sample_data_read_allowed = true_via_explicit_grain_scope_only
full_data_read_allowed = false
production_builder_authorized = false
state_materialization_allowed = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
```

Authorization artifact:

```text
experimental_bounded_grain_validation_authorization_v0_1.md
configs/experimental_bounded_grain_scope_v0_1.json
```

## Run Metrics

```text
sources_sampled = 5
files_sampled = 8
rows_read = 12271
maximum_rows_authorized = 20000
rows_limit_respected = true

null_key_rows = 0
duplicate_key_groups = 1016
duplicate_key_rows = 2032
identical_duplicate_groups = 1001
conflicting_duplicate_groups = 15
physical_key_unique_sources = 3
physical_key_non_unique_sources = 2
canonical_key_unique_sources = 3
canonical_key_non_unique_sources = 2
```

## Source Results

```text
004_master_daily_table:
    status = PASS_WITH_RESTRICTIONS
    key = instrument_id + session_date
    finding = key unique in bounded sample
    restriction = price_view observed as hidden dimension; daily availability policy remains restricted

013_ohlcv_1m_quote_guarded:
    status = PASS_WITH_RESTRICTIONS
    key = ticker + ts_utc
    finding = key unique in bounded sample
    restriction = governed canonical identity normalization still required

014_master_intraday_bar_table_candidate:
    status = PASS_WITH_RESTRICTIONS
    key = ticker + ts_utc
    finding = 1000 duplicate candidate key groups, all identical in checked state columns
    restriction = duplicate handling policy required before builder execution; instrument_id NullType remains non-authoritative

015_microstructure_features_table_candidate:
    status = PASS
    key = event_window_id + instrument_id + window_start_utc + window_end_utc
    finding = key unique in bounded sample; no invalid or overlapping windows observed in this sample

raw_quotes:
    status = PASS_WITH_RESTRICTIONS
    key = partition:ticker + timestamp
    finding = 16 same-timestamp groups; 15 contain distinct quote states
    restriction = additional governed ordering key required before quote-level builder execution
```

## Interpretation

The builder can now resolve bounded identity, time and candidate grain without
critical blockers or limit violations. The remaining issues are engineering
policies, not ontology failures:

```text
014 duplicate identical row handling policy pending
raw_quotes additional ordering key policy pending
canonical identity normalization pending
quality and lineage semantics pending
daily availability calendar/timezone policy still restricted
```

## Artifacts

```text
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/bounded_grain_manifest.json
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/grain_key_report.csv
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/duplicate_key_groups.csv
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/null_key_report.csv
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/hidden_dimension_findings.csv
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/raw_quotes_same_timestamp_report.csv
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/bounded_grain_summary.json
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/bounded_grain_findings.md
runs/experimental_state_builder_probe_v0_8_20260721T171358Z/final_manifest.json
```

## Next Gate

```text
bounded_quality_and_lineage_validation = OPEN_FOR_DESIGN
bounded_quality_and_lineage_data_read = NOT_AUTHORIZED
feature_builder_execution = NOT_OPEN
Market State Integration = NOT_OPEN
```

The next gate should classify or resolve the remaining quality and lineage
fields without executing feature formulas or materializing State.
