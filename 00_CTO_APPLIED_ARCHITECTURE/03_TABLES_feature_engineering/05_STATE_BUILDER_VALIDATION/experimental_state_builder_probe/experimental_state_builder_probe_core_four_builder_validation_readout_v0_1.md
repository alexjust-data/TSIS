# Experimental State Builder Probe Core Four Builder Validation Readout v0.1

status: `REFERENCE_RUN_CLOSED_PASS_WITH_RESTRICTIONS`
reference_run: `experimental_state_builder_probe_v0_10_20260721T193918Z`
script_version: `experimental_state_builder_probe_v0_10`
mode: `experimental_builder_validation_execution_core_four`

## Decision

`experimental_builder_validation_execution_core_four` is closed as:

```text
PASS_WITH_RESTRICTIONS
```

The run executed bounded, non-materializing experimental builder resolution for exactly four Information Objects:

```text
Trading Activity
Price Movement
Price Location / Structure
Volatility / Range State
```

It did not execute quote-dependent builders, did not create Market State rows, did not materialize parquet State tables, did not authorize production builder execution and did not authorize downstream consumption.

## Evidence

```text
rows_read = 22076
maximum_rows_authorized = 30000
limits_respected = true

resolution_requests = 40
formula_rows = 170
formula_failures = 0
future_bar_leaks = 0
output_contract_failures = 0
nondeterministic_records = 0
conflicting_source_row_blocks = 0
```

Resolution status counts:

```text
PASS = 24
PASS_WITH_RESTRICTIONS = 8
BLOCKED_INPUT_UNAVAILABLE = 8
```

Per object:

```text
Price Location / Structure: PASS 8, BLOCKED_INPUT_UNAVAILABLE 2
Price Movement: PASS 8, BLOCKED_INPUT_UNAVAILABLE 2
Trading Activity: PASS_WITH_RESTRICTIONS 8, BLOCKED_INPUT_UNAVAILABLE 2
Volatility / Range State: PASS 8, BLOCKED_INPUT_UNAVAILABLE 2
```

The blocked requests are expected bounded edge cases where no closed intraday bar exists yet at the decision timestamp. They are evidence that the builder withholds unavailable input rather than inventing state.

## Scope Correction

The first v0.10 attempt produced no executable requests because the bounded 004 and 014 samples had no ticker-session overlap.

The reference scope now uses explicit bounded ticker filters and selects:

```text
004_master_daily_table:
    year=2023
    price_view=split_normalized
    row_filter_tickers = AACT, AAGR, AAMC

014_master_intraday_bar_table_candidate:
    row_filter_tickers = AACT, AAGR, AAMC
```

This is a scope correction, not a semantic change to the ontology or mappings.

## Restrictions Preserved

```text
Trading Activity daily__rvol_20d
    uses intraday volume-to-time over prior 20-session volume mean.
    Final same-session daily volume is not consumed.

014 duplicate bars
    identical duplicates are collapsed deterministically under policy.
    conflicting duplicates would block execution.

quote-dependent builder execution
    remains blocked pending raw_quotes.as_of_utc and raw_quotes.quote_ordering_key.
```

## Non-Authority

This run does not authorize:

```text
Market State Integration
State materialization
full-universe execution
full-history execution
production scheduling
downstream ML/RL consumption
event detection consumption
quote-dependent object execution
dataset promotion
```

## Run Lineage

Reference artifacts live under:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\runs\experimental_state_builder_probe_v0_10_20260721T193918Z
```

Important artifacts:

```text
core_four_builder_execution_manifest.json
builder_request_report.csv
capability_resolution_report.csv
selected_source_rows_report.csv
cutoff_enforcement_report.csv
duplicate_handling_report.csv
formula_validation_report.csv
builder_output_contract_report.csv
determinism_report.csv
builder_restrictions_report.csv
core_four_resolution_records.jsonl
core_four_builder_validation_summary.json
core_four_builder_validation_findings.md
final_manifest.json
```

Superseded v0.10 runs are retained for traceability:

```text
experimental_state_builder_probe_v0_10_20260721T192335Z
experimental_state_builder_probe_v0_10_20260721T193012Z
```

## Next Gate

The immediate next gate was the resolution record review:

```text
core_four_resolution_record_acceptance_review
```

It has been closed in `experimental_core_four_resolution_record_acceptance_review_v0_1.md` as `CLOSED_PASS_WITH_RESTRICTIONS`. The next allowed gate is design-only:

```text
core_four_market_state_integration_design = OPEN_FOR_DESIGN_ONLY
```

Market State execution and materialization remain closed.
