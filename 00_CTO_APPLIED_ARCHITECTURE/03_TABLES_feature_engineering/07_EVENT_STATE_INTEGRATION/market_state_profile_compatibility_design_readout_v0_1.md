# Market State Profile Compatibility Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `market_state_profile_compatibility_design_v0_1_20260724T142500Z`

## Result

The compatibility design is closed.

```text
semantic_profile_compatibility =
SEMANTICALLY_COMPATIBLE_WITH_RESTRICTIONS

physical_consumption_authority =
NOT_AUTHORIZED

execution_readiness =
NOT_READY_REQUIRES_INSTRUMENT_SESSION_PROJECTION_DESIGN
```

## Key Finding

The official Market State profile can serve as the semantic parent of
`event_state_core_four_intraday_profile_v0_1`, but no Event State execution is
ready yet.

The reason is grain mismatch:

```text
Market State core-four
    = instrument_id + session_date + decision_timestamp_utc

session_opened Event Instance/Window
    = exchange_id + session_date + calendar_version + event_anchor_timestamp_utc
```

A future instrument-session projection design must bridge the exchange-session
event/window to instrument-level Market State records.

## Boundaries Preserved

```text
market_state_physical_consumption = false
candidate_market_state_parquet_read = false
event_instance_binding_execution = false
event_window_binding_execution = false
instrument_session_projection_execution = false
event_state_builder_execution = false
event_state_materialization = false
official_event_state_profile_promotion = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
```

## Validation Summary

```text
market_state_profile_id_match = true
event_state_source_market_state_profile_match = true
accepted_event_type_scope_preserved = true
event_instance_design_dependency_closed = true
event_window_design_dependency_closed = true
direct_join_without_projection_allowed = false
official_physical_dataset_inferred = false
closed_boundary_invariants_pass = true
```

## Next Gate

```text
event_state_instrument_session_projection_design_authorization_v0_1
```
