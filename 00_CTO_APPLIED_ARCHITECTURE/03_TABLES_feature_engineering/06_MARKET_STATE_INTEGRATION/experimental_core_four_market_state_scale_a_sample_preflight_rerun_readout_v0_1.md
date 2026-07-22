# Experimental Core Four Market State Scale A Sample Preflight Rerun Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-22`
Reference Run: `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z`

This readout closes the authorized Scale A sample preflight rerun after the
accepted eligible representation surface construction. The rerun consumed the
accepted eligible pool and the accepted run-local 014-derived candidate surface.
It did not read `013`, execute builders, emit Information Object records,
integrate Market State, materialize Market State parquet, promote data or
authorize downstream consumption.

---

## Decision

```text
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization
    = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_sample_preflight_rerun
    = CLOSED_PASS_WITH_RESTRICTIONS

scale_a_sample_manifest
    = FROZEN

experimental_core_four_market_state_scale_a_execution_authorization
    = NOT_OPEN_NEXT

experimental_core_four_market_state_scale_a_execution
    = NOT_EXECUTED
```

---

## Results

```text
requested_contexts = 60
sample_manifest_rows = 60
selected_instruments = 8
eligible_instruments = 13
selected_sessions = 5
calendar_sessions_checked = 5
calendar_compatible_sessions = 5
calendar_compatibility_failures = 0
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
estimated_daily_rows = 3152
estimated_intraday_rows = 91830
estimated_total_source_rows = 94982
maximum_source_market_data_rows_read = 250000
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
identity_failures = 0
source_coverage_failures = 0
source_coverage_failures_in_frozen_sample = 0
stratification_failures = 0
duplicate_status_diversity_frozen_contexts = 5
hard_preflight_failures = 0
builders_executed = false
resolution_records_emitted = 0
integration_executed = false
materialization_executed = false
candidate_parquet_files_written = 0
```

Frozen sample composition:

```text
selected_tickers = AACT, AAME, AARD, ABL, ABLV, ABOS, ABTS, ABVC
selected_sessions = 2025-09-02, 2025-09-03, 2025-09-04, 2025-09-05, 2025-09-08
pre_first_observable_bar_expected_blocked = 8
first_closed_bar_or_early_regular_intraday = 16
mid_session_regular_intraday = 24
after_last_sampled_bar_not_session_close = 12
expected_materialized_contexts = 52
expected_blocked_contexts = 8
```

Fingerprints:

```text
instrument_selection_fingerprint = c78243213b3f131ae5c5bc0b63b2f1c8fe617e8945d896f03cef4ed2b01ad6fc
session_selection_fingerprint = 9df5af273bd9af7845f54b9d1106128ee10072f3f53c3be89656aaf3593293fd
scale_a_sample_fingerprint = 65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1
accepted_eligible_pool_fingerprint = 57e22e7eb616c0682db1d094e19dff2b31e35ca23320ec1757acf4e19323853d
accepted_bounded_014_surface_sha256 = e729bceab6bd75e891dcac9f6bbf5eefa9ed78c8b6ecb8c6be79f4bc535f955b
```

---

## Superseded Rerun

```text
experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194131Z
    = not accepted closure evidence
```

That run froze 60 contexts but did not preserve the duplicate-status
stratification correctly. The preflight script was corrected so a required
stratification failure cannot close as PASS, and the accepted run above includes
5 frozen contexts with preserved duplicate evidence against a requirement of 4.

---

## Authority Boundary

```text
013_ohlcv_1m_quote_guarded_read = false
raw_quotes_read = false
builders_executed = false
resolution_records_emitted = 0
integration_executed = false
materialization_executed = false
candidate_parquet_files_written = 0
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

The frozen sample is non-production evidence only. It may be consumed by a
future Scale A execution only after a separate execution authorization names
this exact `scale_a_sample_fingerprint`.

---

## Next Gate

```text
experimental_core_four_market_state_scale_a_execution_authorization_v0_1
    = NOT_OPEN_NEXT
```

The next gate may authorize bounded Scale A builder/resolution, integration,
candidate materialization and independent validation against the frozen sample.
It must consume the exact accepted sample fingerprint and keep production,
official Market State, downstream consumption, promotion, full-history and
full-universe execution closed.
