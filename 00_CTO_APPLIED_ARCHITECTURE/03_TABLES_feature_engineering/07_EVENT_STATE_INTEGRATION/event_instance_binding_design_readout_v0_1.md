# Event Instance Binding Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design ID: `event_instance_binding_design_v0_1`

This gate closes the design of native Event Instance identity for
`event_type:market_data:session_opened` under `exchange_session` subject scope.

It does not create Event Instances.

## 1. Result

```text
event_instance_binding_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_type_id = event_type:market_data:session_opened
registry_snapshot_id = tsis_event_type_registry_v0_1_post_initial_admission_001
registry_snapshot_sha256 = f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43
accepted_subject_scope = exchange_session
native_instance_grain = event_type_id + exchange_id + session_date + calendar_version + event_anchor_timestamp_utc
instrument_id_in_native_identity = false
detector_required = false
```

## 2. Key Decision

```text
Event Type identity
    = exchange-session occurrence

Instrument association
    = future projection or binding
```

This prevents TSIS from silently creating one native `session_opened` occurrence
per ticker. Future instrument-level Event State work must bind instruments to
the exchange-session Event Instance through a separate design and execution
gate.

## 3. Timestamp Decision

```text
event_anchor_timestamp_utc = governed session_open_utc
first_observable_timestamp_utc = calendar-known-before-open may exist
detection_timestamp_utc = not_applicable_for_calendar_authority_v0_1
binding_created_at_utc = future execution metadata only
```

Standing boundary:

```text
regular_session_open_timestamp != first_observed_trade_timestamp
calendar knowledge timestamp != event occurrence timestamp
```

## 4. Source Lineage Decision

Future execution must preserve:

```text
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_binding_run_id = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_calendar_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
calendar_row_fingerprint
exchange_id
session_date
session_open_utc
timezone_authority
```

## 5. Boundary Attestation

```text
event_instance_binding_execution_authorized = false
event_instances_created = 0
historical_calendar_rows_consumed = 0
physical_parquet_reads_allowed = false
source_market_data_rows_read = 0
detector_execution_authorized = false
instrument_projection_execution_authorized = false
event_window_binding_execution_authorized = false
market_state_physical_consumption_authorized = false
event_state_builder_execution_authorized = false
event_state_materialization_authorized = false
downstream_consumption_authorized = false
production_authorized = false
```

## 6. Next Gate

Immediate next recommended gate, only if explicitly authorized:

```text
event_window_binding_design_authorization_v0_1
```

Then:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

Event Instance Binding Execution remains not authorized.
