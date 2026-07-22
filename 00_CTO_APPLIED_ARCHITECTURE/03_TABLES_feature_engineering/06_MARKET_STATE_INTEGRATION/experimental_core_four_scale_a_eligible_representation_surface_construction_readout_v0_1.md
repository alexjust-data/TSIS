# Experimental Core Four Scale A Eligible Representation Surface Construction Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-22`
Reference Run: `experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184904Z`

This readout closes the bounded eligible representation surface construction
authorized by `experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1`.

The run constructed a non-production, run-local 014-derived candidate surface
from bounded `013_ohlcv_1m_quote_guarded` upstream evidence and the existing
014 candidate surface. It also emitted an accepted eligible instrument pool for
future Scale A sample preflight rerun.

It did not rerun Scale A sample preflight, execute builders, emit Information
Object resolution records, integrate Market State, materialize Market State
parquet, modify original 014, promote data or authorize downstream
consumption.

---

## Decision

```text
experimental_core_four_scale_a_eligible_representation_surface_authorization
    = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_construction
    = CLOSED_PASS_WITH_RESTRICTIONS

eligible_instrument_pool
    = ACCEPTED

experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization
    = NOT_OPEN_NEXT

experimental_core_four_market_state_scale_a_sample_preflight_rerun
    = NOT_AUTHORIZED

experimental_core_four_market_state_scale_a_execution
    = BLOCKED_NOT_STARTED
```

---

## Results

```text
candidate_instruments_discovered = 40
resolved_intraday_source_distinct_instruments = 40
candidate_instruments_with_daily_linkage = 14
candidate_instruments_with_5_compatible_sessions = 38
eligible_candidates_before_cap = 13
eligible_instruments_emitted = 13
selected_sessions_count = 10
source_market_data_rows_read = 221183
derived_014_rows_written = 91830
candidate_surface_parquet_files_written = 1
market_state_parquet_files_written = 0
required_output_files = 17
final_output_file_count = 17
missing_required_output_files = 0
unexpected_output_files = 0
authority_failures = 0
determinism_failures = 0
hard_contract_failures = 0
```

Fingerprints:

```text
source_snapshot_fingerprint =
401e94fe156ae6161ac93bc528ef848dd7b1f433f003fa963d51a1249b99572b

bounded_014_candidate_surface_fingerprint =
71cb2d7e4f441800cf3fe1a8c8e129d83b93b02b24a8f6ec76732c56d10f98c9

eligible_instrument_pool_fingerprint =
57e22e7eb616c0682db1d094e19dff2b31e35ca23320ec1757acf4e19323853d

eligible_surface_fingerprint =
00fb613881825ac9053be98b0875379d9ee4dff8c784f7b9906061358298b0fa
```

---

## Source Boundary

```text
004_master_daily_table rows read = 3404
014_master_intraday_bar_table_candidate rows read = 21670
013_ohlcv_1m_quote_guarded rows read = 196109
```

`013_ohlcv_1m_quote_guarded` was used only as bounded upstream evidence for
eligible-surface construction. It is not authorized as a direct builder,
integration, Market State, downstream or production input.

The original 014 candidate file was not modified:

```text
original_014_sha256_before =
6aec2e58c57d0dfc94da2f78b2738e3fcb956692d3b303f2ef5dde3c6d73de0d

original_014_sha256_after =
6aec2e58c57d0dfc94da2f78b2738e3fcb956692d3b303f2ef5dde3c6d73de0d

original_014_mtime_unchanged = true
```

---

## Eligible Pool

The accepted pool contains 13 eligible instrument identities. Each emitted
instrument has at least 10 eligible sessions in the construction evidence,
which exceeds the minimum requirement of five.

The future Scale A sample preflight may not rediscover eligibility. It must
consume this accepted pool by exact fingerprint after a separate rerun
authorization.

---

## Superseded Attempts

The following construction attempts are not accepted closure evidence:

```text
experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184113Z
experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184220Z
experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184456Z
```

They were superseded by the accepted run above due to script/reporting defects:
missing 014 `year/month` read columns, Windows long-path readout handling and
over-conservative daily source-row accounting. They are not evidence of an
eligible pool or candidate surface defect.

---

## Still Closed

```text
Scale_A_sample_preflight_rerun = NOT_AUTHORIZED
Scale_A_builder_execution = NOT_AUTHORIZED
Information_Object_resolution = NOT_AUTHORIZED
Market_State_integration = NOT_AUTHORIZED
Market_State_materialization = NOT_AUTHORIZED
Market_State_candidate_parquet = NOT_AUTHORIZED
official_Market_State = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
Scale_B = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
Scale_C = NOT_AUTHORIZED
```

---

## Next Gate

```text
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1
```

That future gate may authorize rerunning the existing Scale A sample preflight
against `eligible_instrument_pool_fingerprint =
57e22e7eb616c0682db1d094e19dff2b31e35ca23320ec1757acf4e19323853d`.
