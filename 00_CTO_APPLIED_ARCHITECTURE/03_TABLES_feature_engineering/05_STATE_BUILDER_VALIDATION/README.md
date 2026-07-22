# 05_STATE_BUILDER_VALIDATION

Status: `phase_b_core_four_builder_and_integration_execution_passed_with_restrictions_v0_1`
Date: `2026-07-21`

Esta carpeta define validaciones de builder para comprobar si un Information
Object admitido puede resolverse legalmente hacia perfiles de State.

No contiene builders de produccion. No autoriza consumo de State,
materializacion fisica, cambios de schema ni promocion de datasets.

## Current Phase Boundary

```text
TSIS Market Ontology Phase = CLOSED
TSIS Market Ontology v1 = FROZEN
Phase B = OPEN
Operational Mapping v1 = COMPLETE
Builder Validation Designs v1 = COMPLETE
experimental_builder_validation_execution_core_four = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
production_builder_development_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
```

## Builder Validation Inventory

```text
Core four executed experimentally:
    Trading Activity
    Price Movement
    Price Location / Structure
    Volatility / Range State

Design ready, not executed yet:
    Liquidity
    Market Microstructure State
    News / Catalyst Context
    Fundamental Context
    Short-Side Context
    Broad Market Context
    Halt Context

Blocked pending prerequisites:
    Order Flow Pressure
        unblock_requires = trade_quote_alignment_policy + side_classifier_policy + classifier_confidence_policy
```

## Experimental Builder Probe Result

Reference core-four builder validation run:

```text
run_id = experimental_state_builder_probe_v0_10_20260721T193918Z
mode = experimental_builder_validation_execution_core_four
overall_status = passed_core_four_builder_validation_with_restrictions
resolution_requests = 40
formula_rows = 170
formula_failures = 0
future_bar_leaks = 0
output_contract_failures = 0
nondeterministic_records = 0
conflicting_source_row_blocks = 0
```

Reference acceptance review:

```text
review_id = experimental_core_four_resolution_record_acceptance_review_v0_1
records_reviewed = 40
contexts_reviewed = 10
context_consistency_failures = 0
semantic_equality_failures = 0
blocked_records_with_diagnostic_partial_values = 6
review_status = CLOSED_PASS_WITH_RESTRICTIONS
```

## Downstream Integration Evidence

The accepted core-four records were integrated experimentally, without source
market data reads and without parquet materialization:

```text
run_id = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
contexts_seen = 10
candidate_records_emitted = 8
rejected_required_object_blocked_contexts = 2
failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
admitted_value_rows = 136
source_market_data_rows_read = 0
parquet_files_written = 0
```

Readout:

```text
../06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_readout_v0_1.md
```

## Active Findings

```text
004_master_daily_table:
    selected_price_view = split_normalized observed in bounded sample;
    promotion remains restricted until full-history price-view consistency validation.

014_master_intraday_bar_table_candidate:
    identical duplicate rows can be deterministically collapsed experimentally;
    conflicting duplicate rows would block builder execution.

core_four_builder_validation:
    40 bounded resolution requests executed across the four core objects;
    8 pre-bar requests block unavailable inputs instead of inventing state.

core_four_integration_execution:
    8 non-canonical Market State candidate records emitted;
    2 pre-bar contexts rejected under object atomicity;
    blocked diagnostic partial values were not admitted.

raw_quotes:
    as_of_utc remains unavailable pending governed quote availability contract;
    quote_ordering_key remains blocked because same-timestamp distinct quote states exist.
```

## Current Work Boundary

```text
next_possible_gate = core_four_market_state_materialization_design
next_gate_type = design_only_conditional

still_closed =
  production builder implementation
  production builder execution
  State consumption
  Market State parquet materialization
  full-history execution
  full-universe execution
  quote-dependent builder execution
  schema change
  physical materialization
  dataset promotion
  operational promotion
```

El vertical de `Trading Activity` se conserva como piloto ratificado. No otorga
autoridad operativa por si mismo.
