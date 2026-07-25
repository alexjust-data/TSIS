# Event State Instrument Session Projection Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `event_state_instrument_session_projection_design_v0_1_20260724T144500Z`

## Result

The projection design is closed.

It defines the future bridge from:

```text
exchange-session Event Instance
+
exchange-session Event Window Binding
```

to:

```text
instrument-session Market State context
```

No projections were created and no source rows were read.

## Key Decision

Projection is a separate identity layer.

```text
event_instance_id does not gain instrument_id
event_window_binding_id does not gain instrument_id
instrument association lives in projection
```

## Required Future Join

Future Event State integration must bind exactly one:

```text
Market State profile record/reference
Event Instance
Event Window Binding
Instrument Session Projection
state_role
consumption_legality
```

Missing or ambiguous bindings block Event State rows.

## Boundary Report

```text
instrument_session_projection_execution = false
instrument_session_projections_created = 0
instrument_master_rows_read = 0
market_calendar_rows_read = 0
event_instances_created = 0
event_windows_created = 0
market_state_physical_consumption = false
event_state_builder_execution = false
event_state_materialization = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
```

## Next Gate

```text
event_state_integration_design_authorization_v0_1
```
