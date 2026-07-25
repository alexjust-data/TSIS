# Governed Exchange Session Calendar Binding Validation Readout v0.1

Status: `CLOSED_PASS_WITH_RESTRICTIONS`
Date: `2026-07-23`
Accepted Run: `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z`
Superseded Run: `governed_exchange_session_calendar_binding_validation_v0_1_20260723T061003Z`

This run validates the bounded governed calendar binding required before any Scale B calendar-aware Market State execution. It does not authorize Scale B execution, builders, Information Object resolution, Market State integration, Market State materialization, Market State parquet, production, downstream consumption, full-history/full-universe execution or promotion.

---

## Result

```text
governed_exchange_session_calendar_binding_validation = CLOSED_PASS_WITH_RESTRICTIONS
source_rows = 5328
bound_rows = 5328
bound_schema_column_count = 18
early_close_sessions = 45
calendar_source_sha256_match = true
source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
bound_parquet_bytes = 563799
total_run_output_bytes = 3395434
maximum_bound_calendar_parquet_bytes = 1000000
maximum_total_run_output_bytes = 5000000
hard_validation_failures = 0
```

---

## Validation Evidence

```text
calendar_values = [XNYS]
timezone_values = [America/New_York]
first_session = 2005-01-03
last_session = 2026-03-09
session_date_duplicates = 0
open_utc_before_close_utc_failures = 0
open_local_before_close_local_failures = 0
utc_local_equivalence_failures = 0
session_minutes_duration_mismatches = 0
early_close_mismatches = 0
calendar_row_fingerprint_mismatches = 0
roundtrip_row_differences = 0
determinism_failures = 0
authority_failures = 0
```

---

## Source Boundary

The documented processed table path is unavailable in this workspace:

```text
E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet
documented_processed_path_exists = false
```

The accepted binding evidence is the resolved local official source artifact plus SHA-256:

```text
active_source_path = C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet
calendar_source_sha256 = 5e423e444e1228a671a05159eda0a707f9bb2446f5b17860740f3001edbbd954
meta_declared_hash_match = true
meta_declared_resolved_path_match = false
```

The `meta_declared_resolved_path_match = false` restriction reflects a historical folder-name string inside the meta file. The hash matches, so binding authority is by resolved local path plus SHA-256, not by the stale path string.

---

## Supersession

The first run `governed_exchange_session_calendar_binding_validation_v0_1_20260723T061003Z` is not closure evidence. It had zero calendar hard failures, but it exposed that the authorization used one ambiguous `maximum_output_bytes` field. The accepted run `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z` uses the corrected contract:

```text
maximum_bound_calendar_parquet_bytes = 1000000
maximum_total_run_output_bytes = 5000000
```

---

## Preserved Restrictions

```text
closed_day_rows_not_authorized
holiday_absence_inference_not_authorized
fixed_utc_probe_calendar_not_scale_b_authority
scale_a_not_relabelled_calendar_aware
official_calendar_not_promoted
scale_b_execution_not_authorized
market_state_parquet_not_authorized
production_not_authorized
downstream_consumption_not_authorized
full_history_full_universe_not_authorized
```

---

## Next Gate

```text
next_allowed_gate = experimental_core_four_market_state_scale_b_authorization_v0_1
```

The next gate may design and authorize a bounded calendar-aware Scale B sample using this accepted calendar binding. It still must not execute Scale B by implication.
