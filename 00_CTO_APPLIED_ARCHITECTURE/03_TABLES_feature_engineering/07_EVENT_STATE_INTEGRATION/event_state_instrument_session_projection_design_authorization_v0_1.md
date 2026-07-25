# Event State Instrument Session Projection Design Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_design_v0_1`
Date: `2026-07-24`
Scope: `session_opened_exchange_session_to_instrument_session_projection_design`

## Purpose

This authorization opens one design-only gate:

```text
event_state_instrument_session_projection_design_authorization_v0_1
```

It permits TSIS to define how an exchange-session Event Instance and Event
Window Binding may later be projected to instrument-session contexts for Event
State.

The gate exists because:

```text
event_type:market_data:session_opened
    = exchange_session scope

market_state_core_four_intraday_profile_v0_1
    = instrument_id + session_date + decision_timestamp_utc scope
```

## Required Prior Designs

```text
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

## Authorized Work

Allowed:

```text
define instrument-session projection identity
define future projection fields
define exchange/instrument matching policy
define listing/lifecycle eligibility policy
define ambiguity and missing-binding blockers
define lineage and supersession requirements
write design, contract, scope and readout artifacts
update active Event State documentation, matrix, handoff and changelogs
```

## Explicitly Not Authorized

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

## Boundary Rule

Projection must not mutate native Event Type, Event Instance or Event Window
identity.

```text
exchange-session event occurrence remains one occurrence
instrument association is a projection layer
Market State remains instrument/timestamp scoped
```

## Next Gate

If this design closes, the next recommended gate is:

```text
event_state_integration_design_authorization_v0_1
```
