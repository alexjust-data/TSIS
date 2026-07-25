# Governed Exchange Session Calendar Binding Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `governed_exchange_session_calendar_binding_scope_v0_1`

This authorization opens only the bounded binding and validation path for governed exchange-session calendar evidence required before Scale B.

It does not execute the binding validation. It does not authorize Scale B, builders, Information Object resolution, Market State integration, Market State materialization, Market State parquet, production, State consumption, downstream use, full-history execution, full-universe execution or promotion.

---

## 1. Decision

```text
governed_exchange_session_calendar_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
governed_exchange_session_calendar_binding_authorization = AUTHORIZED_WITH_RESTRICTIONS
governed_exchange_session_calendar_binding_validation = NOT_EXECUTED
experimental_core_four_market_state_scale_b_authorization = BLOCKED_UNTIL_GOVERNED_EXCHANGE_SESSION_CALENDAR
experimental_core_four_market_state_scale_b_execution = NOT_AUTHORIZED

official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
state_consumption = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

---

## 2. Authorized Calendar Source Boundary

The design identified `001_market_calendar / market_calendar_v0_1` as the preferred calendar evidence. The documented processed output path is not currently available in this workspace:

```text
E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet
```

The available physical source is the official XNYS calendar artifact declared by the `001_market_calendar` lineage:

```text
calendar_source_artifact = C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet
calendar_source_meta = C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.meta.json
calendar = XNYS
timezone = America/New_York
first_session = 2005-01-03
last_session = 2026-03-09
sessions = 5328
early_close_sessions = 45
calendar_source_sha256 = 5e423e444e1228a671a05159eda0a707f9bb2446f5b17860740f3001edbbd954
```

The binding validation must report the documented processed-path absence and validate the local source artifact by hash. The meta file currently contains a historical path string from a previous folder name; the validator must treat SHA-256 and resolved local path as the binding evidence, and report the path-string mismatch explicitly.

---

## 3. Authorized Actions

Allowed only inside the future binding-validation run:

```text
read calendar source parquet
read calendar source meta JSON
create source snapshot manifest
validate schema and source metadata
normalize calendar rows into governed logical fields
write one run-local governed calendar binding artifact
write validation reports
write readout and final manifest
```

The run-local binding artifact is evidence only. It is not an official calendar table and cannot be used by Scale B until the validation closes with restrictions or better.

---

## 4. Forbidden Actions

```text
read market price data
read 004/013/014 as feature-builder inputs
read raw quotes
execute Information Object builders
emit resolution records
integrate Market State
write Market State parquet
authorize Scale B
construct production calendar datasets
write official 001 outputs
modify the source calendar parquet or meta JSON
modify previous Scale A evidence
consume State downstream
promote datasets
execute full-history or full-universe runs
read or stage 00_CTO/99_REFERENCE_LIBRARY
```

---

## 5. Binding Output Contract

The future validation run may emit only these required outputs under its own run directory:

```text
pre_manifest.json
heartbeat.json
calendar_source_snapshot_manifest.json
governed_exchange_session_calendar_bound_v0_1.parquet
governed_exchange_session_calendar_binding_report.csv
calendar_schema_report.json
calendar_duration_report.csv
calendar_timezone_equivalence_report.csv
calendar_early_close_report.csv
calendar_fingerprint_report.csv
calendar_coverage_report.json
calendar_authority_report.json
calendar_binding_determinism_report.json
governed_exchange_session_calendar_binding_validation_readout_v0_1.md
final_manifest.json
```

Limits:

```text
required_output_files = 15
maximum_output_files = 16
unexpected_output_files = 0
maximum_calendar_source_files_read = 2
maximum_calendar_rows_read = 6000
expected_calendar_rows = 5328
maximum_bound_calendar_rows = 5328
maximum_bound_calendar_parquet_files = 1
maximum_bound_calendar_parquet_bytes = 1000000
maximum_total_run_output_bytes = 5000000
```

---

## 6. Logical Binding Rules

The binding must produce the governed logical calendar fields required by the design:

```text
calendar_id
exchange_calendar_code
mic_or_exchange_code
session_date
session_open_utc
session_close_utc
session_open_local
session_close_local
timezone
session_minutes
session_type
is_regular_session
is_early_close
is_closed_or_holiday
calendar_version
source_calendar_artifact
source_snapshot_fingerprint
calendar_row_fingerprint
```

Rules:

```text
exchange_calendar_code = source.calendar
mic_or_exchange_code = source.calendar
session_open_utc = source.open_utc parsed as UTC instant
session_close_utc = source.close_utc parsed as UTC instant
session_open_local = source.open_et parsed as America/New_York local instant
session_close_local = source.close_et parsed as America/New_York local instant
session_minutes = minutes between session_open_utc and session_close_utc
session_type = early_close when is_early_close else regular
is_regular_session = true only when not early close and duration is 390 minutes
is_closed_or_holiday = false for emitted trading-session rows
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_id = XNYS::session_date::calendar_version
calendar_row_fingerprint = non-circular SHA-256 over governed row payload
```

Closed-day rows are not authorized in this gate. Absence-based holiday inference requires a separate expected-date universe and separate authorization.

---

## 7. Closure Criteria For The Future Validation

The validation can close successfully only if:

```text
calendar_source_sha256_match = true
source_rows = 5328
bound_rows = 5328
calendar_all_rows = XNYS
timezone_all_rows = America/New_York
session_date_duplicates = 0
open_utc_before_close_utc_failures = 0
open_local_before_close_local_failures = 0
utc_local_equivalence_failures = 0
session_minutes_duration_mismatches = 0
early_close_mismatches = 0
calendar_row_fingerprint_mismatches = 0
source_snapshot_fingerprint_present = true
determinism_failures = 0
authority_failures = 0
hard_validation_failures = 0
```

---

## 8. Next Gate

```text
next_allowed_gate = governed_exchange_session_calendar_binding_validation_execution_v0_1
```

Scale B authorization remains blocked until the binding validation closes with restrictions or better.
