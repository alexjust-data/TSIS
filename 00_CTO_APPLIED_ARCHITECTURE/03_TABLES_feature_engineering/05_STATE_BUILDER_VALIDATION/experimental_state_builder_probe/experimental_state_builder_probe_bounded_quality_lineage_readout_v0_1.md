# Experimental State Builder Probe Bounded Quality And Lineage Readout v0.1

Status: `closed_pass_with_restrictions`
Date: `2026-07-21`
Run: `experimental_state_builder_probe_v0_9_20260721T184537Z`
Mode: `bounded_quality_and_lineage_validation`
Script: `experimental_state_builder_probe_v0_9`

## Verdict

```text
bounded_quality_lineage_validation = PASS_WITH_RESTRICTIONS
quality_semantics_validation = PASS_WITH_RESTRICTIONS
lineage_validation = PASS_WITH_RESTRICTIONS
core_four_builder_execution_readiness = OPEN_FOR_EXPERIMENTAL_BUILDER_VALIDATION_DESIGN
quote_dependent_builder_execution_readiness = BLOCKED_PENDING_QUOTE_ORDERING_OR_ASOF
builder_validation_execution = NOT_EXECUTED
market_state_integration = NOT_OPEN
```

The gate is closed as `PASS_WITH_RESTRICTIONS`.

It does not authorize production builders, State materialization, State
consumption, dataset promotion, full data reads or Market State Integration.

## Scope And Limits

```text
sources_sampled = 5
files_sampled = 8
rows_read = 12271
maximum_rows_authorized = 20000
rows_limit_respected = true
```

Authorized sources:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
raw_quotes
```

## Policies Added

```text
004_price_view_selection_policy_v0_1
014_duplicate_intraday_bar_policy_v0_1
raw_quote_ordering_policy_v0_1
raw_quote_quality_policy_v0_1
```

These policies classify what can be derived, what remains restricted for
promotion and what blocks builder execution.

## Execution Blockers

```text
builder_execution_blockers = 2
core_four_builder_execution_blockers = 0
quote_dependent_builder_execution_blockers = 2
promotion_only_restrictions = 8
```

Builder blockers are scoped.

`raw_quotes.as_of_utc` remains blocked pending a governed quote availability
contract.

`raw_quotes.quote_ordering_key` remains blocked because the bounded sample found
same-timestamp quote rows with distinct quote states. Timestamp alone is not a
governed quote-level ordering key.

These blockers apply to quote-dependent builders. They do not block the first
core-four experimental builder execution path.

## Core Four Readiness

The next allowed execution gate is limited to:

```text
Trading Activity
Price Movement
Price Location / Structure
Volatility / Range State
```

Allowed next status:

```text
experimental_builder_validation_execution = OPEN_FOR_CORE_FOUR_DESIGN
```

Not allowed:

```text
Liquidity builder execution
Market Microstructure builder execution
Order Flow Pressure builder execution
Market State Integration
State materialization
production builder development
```

## Key Findings

```text
004_master_daily_table.price_view_selection
    derivable by policy with restrictions
    selected_price_view = split_normalized
    promotion restricted until full-history price-view consistency validation

014_master_intraday_bar_table_candidate.component_quality_flag
    derivable by policy with restrictions
    identical duplicate rows may be deterministically collapsed experimentally
    conflicting duplicate rows would block builder execution

014_master_intraday_bar_table_candidate.temporal_legality_flag
    derivable by builder validation with restrictions
    full temporal legality remains a later validation layer

raw_quotes.quote_quality_flag / two_sided_flag
    derivable by policy with restrictions
    full-history quote quality validation not executed

raw_quotes.as_of_utc / quote_ordering_key
    builder blockers for quote-dependent objects
```

## Artifacts

```text
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/bounded_quality_lineage_manifest.json
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/quality_lineage_read_limits_report.csv
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/quality_lineage_field_report.csv
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/quality_derivation_report.csv
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/builder_execution_blockers_report.csv
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/promotion_only_restrictions_report.csv
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/bounded_quality_lineage_summary.json
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/bounded_quality_lineage_findings.md
runs/experimental_state_builder_probe_v0_9_20260721T184537Z/final_manifest.json
```

## Decision

```text
bounded_grain_validation = CLOSED_PASS_WITH_RESTRICTIONS
bounded_quality_and_lineage_validation = CLOSED_PASS_WITH_RESTRICTIONS
experimental_builder_validation_execution = OPEN_FOR_CORE_FOUR_DESIGN
Market State Integration = NOT_OPEN
```
