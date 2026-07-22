# Experimental Bounded Quality And Lineage Validation Authorization v0.1

status: `authorized_for_experimental_probe_only`
phase: `Phase B - experimental builder validation`
effective_scope: `bounded_quality_and_lineage_validation`

## Purpose

This artifact authorizes the bounded quality and lineage validation gate for the experimental State Builder probe.

The gate classifies, inside an explicitly bounded sample:

```text
what exists physically
what can be derived by governed policy
what still needs policy
what blocks builder execution
what only restricts promotion
```

It does not repair data, mutate source datasets, execute Information Object feature formulas, materialize State, validate full-history quality semantics or authorize operational use.

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
feature_builder_execution_allowed = false
```

The authorization is valid only when the executable scope is provided by:

```text
configs/experimental_bounded_quality_lineage_scope_v0_1.json
```

## Authorized Sources

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

These are the same five sources used by bounded identity/temporal validation and bounded grain validation.

## Hard Limits

```text
maximum_sources = 5
maximum_files_per_source = 3
maximum_rows_per_file = 2000
maximum_total_rows = 20000
full_scan_allowed = false
```

## Authorized Operations

The probe may read only allowed columns, classify quality and lineage fields, derive experimental quality flags where a policy permits it, classify duplicate rows, classify quote ordering readiness, and write reports only under the experimental probe run directory.

The probe may not write to source datasets, deduplicate rows, repair rows, perform full scans, calculate Information Object features, execute feature builders, materialize State, promote datasets, or authorize operational consumption.

## Required Policies

```text
policies/004_price_view_selection_policy_v0_1.md
policies/014_duplicate_intraday_bar_policy_v0_1.md
policies/raw_quote_ordering_policy_v0_1.md
policies/raw_quote_quality_policy_v0_1.md
```

## Expected Outputs

```text
bounded_quality_lineage_manifest.json
quality_lineage_read_limits_report.csv
quality_lineage_field_report.csv
quality_derivation_report.csv
builder_execution_blockers_report.csv
promotion_only_restrictions_report.csv
bounded_quality_lineage_summary.json
bounded_quality_lineage_findings.md
```

## Non-Claims

A passing bounded quality and lineage gate does not claim full-history quality/lineage validity, builder execution success, Market State Integration readiness, State materialization authority or production builder authority.

The next allowed gate, if no core-four builder blockers remain, is experimental builder validation execution for Trading Activity, Price Movement, Price Location / Structure and Volatility / Range State. Market State Integration remains closed.
