# Experimental Core Four Market State Scale A Sample Preflight Readout v0.1

run_id = `experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z`
script_version = `experimental_core_four_market_state_scale_a_sample_preflight_v0_1`

## Decision

```text
experimental_core_four_market_state_scale_a_sample_preflight = BLOCKED_SAMPLE_CARDINALITY
experimental_core_four_market_state_scale_a_execution = BLOCKED_NOT_STARTED
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

## Counts

```text
requested_contexts = 60
sample_manifest_rows = 0
required_instruments = 8
available_intraday_tickers = 3
eligible_instruments = 1
required_sessions = 5
calendar_sessions_checked = 5
calendar_compatible_sessions = 5
calendar_compatibility_failures = 0
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
estimated_daily_rows = 588
estimated_intraday_rows = 21670
estimated_total_source_rows = 22258
maximum_source_market_data_rows_read = 250000
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
identity_failures = 0
source_coverage_failures = 10
hard_preflight_failures = 1
```

## Interpretation

The preflight did not freeze the 60-context sample because the authorized 014 source surface does not contain enough eligible instruments under the Scale A calendar guard.

## Artifacts

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z
```

The preflight did not execute builders, did not emit Information Object resolution records, did not integrate Market State and did not write parquet.

## Next Gate

Do not open `experimental_core_four_market_state_scale_a_execution`. Adjust the authorized source surface or Scale A scope, then rerun this preflight.
