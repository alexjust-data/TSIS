# Experimental Core Four Resolution Record Acceptance Review v0.1

status: `CLOSED_PASS_WITH_RESTRICTIONS`
reference_run: `experimental_state_builder_probe_v0_10_20260721T193918Z`
review_scope: `core_four_resolution_records_only`
source_row_reads: `none`
market_state_integration: `NOT_OPEN`
state_materialization: `NOT_AUTHORIZED`

## Decision

The 40 core-four resolution records from v0.10 are accepted as valid experimental Information Object resolution evidence with restrictions.

```text
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_integration_execution = NOT_OPEN
Market State materialization = NOT_AUTHORIZED
production_builder = NOT_AUTHORIZED
```

This review does not join objects into Market State and does not read market source tables. It reviews only the artifacts already produced by the reference run.

## Evidence Reviewed

```text
core_four_resolution_records.jsonl
builder_request_report.csv
selected_source_rows_report.csv
cutoff_enforcement_report.csv
builder_output_contract_report.csv
determinism_report.csv
```

Reference metrics:

```text
records_reviewed = 40
contexts_reviewed = 10
context_consistency_failures = 0
semantic_equality_checks = 20
semantic_equality_failures = 0
output_contract_failures = 0
determinism_failures = 0
cutoff_future_leaks = 0
unique_record_fingerprints = 40
duplicate_record_fingerprints = 0
```

## Context Consistency

Each reviewed `context_id` contains exactly four object records:

```text
Trading Activity
Price Movement
Price Location / Structure
Volatility / Range State
```

For every context, the four records share:

```text
ticker
instrument_id
session_date
decision_timestamp_utc
decision_case
004 daily evidence
014 selected bar evidence
```

A `context_input_fingerprint` was computed in the context report for each shared observable input set.

Report:

```text
experimental_core_four_resolution_record_acceptance_context_report_v0_1.csv
```

## Semantic Equality

The review compared equivalent numeric formulas across semantic namespaces:

```text
price_movement__intraday_return_vs_prior_close_ratio
=
price_location_structure__intraday_return_vs_prior_close_ratio_as_location

price_movement__intraday_return_vs_session_open_ratio
=
price_location_structure__intraday_return_vs_session_open_ratio_as_location
```

Result:

```text
semantic_equality_failures = 0
```

Report:

```text
experimental_core_four_resolution_record_acceptance_semantic_report_v0_1.csv
```

## Atomicity Restriction

Blocked records are valid diagnostic records, but not admissible integration records.

```text
blocked_records = 8
blocked_records_with_diagnostic_partial_values = 6
```

Some blocked records contain partial values, such as daily values available before a closed intraday bar exists. These values are diagnostic evidence only.

Integration rule for the next gate:

```text
object_atomicity = required

if resolution_status starts with BLOCKED:
    admit no values from that object into Market State
```

The first integration design must enforce this rule explicitly.

## Restrictions Preserved

```text
session calendar:
    v0.10 uses fixed UTC session_open/session_close times.
    Market State design must replace this with governed_exchange_session_calendar.

after_last_sampled_bar:
    means after the last sampled input bar, not after market close.

Trading Activity rvol_20d:
    remains an experimental volume-to-time over prior full-session volume mean.
    Naming or mapping must preserve that exact semantics.

duplicate metrics:
    current duplicate counts are request-impact evidence, not physical group counts.
```

## Next Allowed Gate

The next allowed design gate has been completed:

```text
core_four_market_state_integration_design_v0_1.md
```

It defines:

```text
join key
context completeness
namespace composition
object atomicity
shared lineage
integration status
conflict handling
schema of the integrated experimental profile
```

It still may not execute:

```text
parquet materialization
full-history execution
production scheduling
downstream consumption
quote-dependent object integration
```
