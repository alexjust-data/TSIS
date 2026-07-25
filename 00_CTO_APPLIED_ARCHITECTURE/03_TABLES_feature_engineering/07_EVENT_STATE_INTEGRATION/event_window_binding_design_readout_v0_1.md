# Event Window Binding Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `event_window_binding_design_v0_1_20260724T140500Z`

## Result

The design-only Event Window Binding gate is closed for:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
```

No Event Windows, Event Instances, detector outputs, Event State rows, parquet
files, production artifacts or downstream-consumable datasets were created.

## Contract Decisions

The gate separates:

```text
Event Instance
Event Window Definition
Event Window Binding
Event State
```

The future binding grain is:

```text
one Event Window Binding
=
one exchange-session Event Instance
+
one Event Window Definition
```

Native `session_opened` windows remain exchange-session scoped. Instrument
association is still a future projection or binding layer and is not part of
the native Event Type, Event Instance or Event Window identity.

## Temporal Policy

For `session_opened`:

```text
event_anchor_timestamp_utc = governed session_open_utc
regular_session_open_timestamp != first_observed_trade_timestamp
```

The design preserves separate timestamps:

```text
event_anchor_timestamp_utc
first_observable_timestamp_utc
binding_created_at_utc
window_start_utc
window_end_utc
```

Calendar knowledge can exist before open, but `session_opened` itself occurs at
the governed open timestamp.

## State And Consumption Policy

Allowed state roles:

```text
pre_event
at_event
post_event
post_event_review
```

Allowed consumption legality classes:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

The gate preserves:

```text
post_event != decision_safe
post_event_review != decision_safe
outcome_adjacent != feature input
```

## Data Foundation Alignment

Data Foundation `event_windows_table_v0_1` remains a governed physical table
and a useful reference pattern. This gate did not consume it and did not claim
that it physically implements the current Event State profile grammar.

Shared principle preserved:

```text
event windows are boundaries
event windows are not features, labels, alpha, price data or execution truth
```

## Boundary Report

```text
event_window_binding_execution_authorized = false
event_windows_created = 0
event_window_registry_created = false
event_window_parquet_files_written = 0
event_instances_created = 0
historical_calendar_rows_consumed = 0
instrument_projection_execution = false
event_detection_execution = false
market_state_physical_consumption = false
event_state_builder_execution = false
event_state_materialization = false
dataset_promotion = false
production = false
downstream_consumption = false
```

## Validation Summary

```text
design_contract_written = true
machine_readable_contract_written = true
scope_json_written = true
readout_written = true
event_type_scope_preserved = true
exchange_session_scope_preserved = true
instrument_id_in_native_window_identity = false
closed_boundary_invariants_pass = true
```

## Next Gate

The next recommended gate is:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

Event Window Binding execution remains not recommended until Event Instance
Binding Design, Event Window Binding Design and Market State Profile
Compatibility Design have all closed and a separate execution authorization is
issued.
