# Experimental Core Four Market State Integration Execution Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-21`
Run: `experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z`
Profile: `market_state_core_four_intraday_experimental_v0_1`

This readout records the first experimental non-materializing integration of
accepted core-four Information Object resolution records into Market State
candidate records.

It does not authorize production builders, parquet materialization, downstream
State consumption or dataset promotion.

## 1. Inputs

```text
reference_builder_run = experimental_state_builder_probe_v0_10_20260721T193918Z
reference_acceptance_review = experimental_core_four_resolution_record_acceptance_review_v0_1
design_contract = core_four_market_state_integration_design_contract_v0_1
execution_scope = core_four_market_state_integration_execution_scope_v0_1
```

The execution consumed only accepted builder/acceptance artifacts. It did not
read physical market source tables.

## 2. Result

```text
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
overall_status = passed_core_four_market_state_integration_execution_with_restrictions
contexts_seen = 10
input_resolution_records = 40
candidate_records_emitted = 8
rejected_contexts = 2
rejected_required_object_blocked_contexts = 2
failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
admitted_value_rows = 136
```

## 3. Correct Interpretation

The eight emitted records are experimental Market State candidate records.
They are useful evidence that the accepted resolution records can be assembled
under the core-four integration contract.

They are not canonical Market State rows.

The two rejected contexts are expected pre-bar contexts where all four required
Objects were `BLOCKED_INPUT_UNAVAILABLE`. Under object atomicity, no diagnostic
partial values from those blocked Objects were admitted.

## 4. Authority Boundary

```text
source_row_reads_allowed = false
source_market_data_rows_read = 0
state_materialization_allowed = false
parquet_write_allowed = false
parquet_files_written = 0
downstream_consumption_authorized = false
production_builder_authorized = false
dataset_promotion_authorized = false
candidate_records_are_canonical_market_state = false
candidate_records_are_downstream_consumable = false
```

## 5. Output Artifacts

```text
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/pre_manifest.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/heartbeat.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/market_state_candidate_records.jsonl
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/rejected_context_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/integration_context_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/integration_value_manifest.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/core_four_market_state_integration_execution_summary.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/core_four_market_state_integration_execution_findings.md
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/final_manifest.json
```

The prior run
`experimental_core_four_market_state_integration_execution_v0_1_20260721T203303Z`
is preserved but marked as `superseded_not_reference_run` because it was
executed before the script enforced that every scope input artifact is listed
in the design contract authority.

## 6. Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
```

## 7. Next Gate

The next logical gate is design only:

```text
core_four_market_state_materialization_design = CONDITIONAL_NEXT_DESIGN_GATE
```

Still not open:

```text
Market State parquet materialization
production builder
downstream State consumption
full-history execution
full-universe execution
quote-dependent object integration
operational promotion
```
