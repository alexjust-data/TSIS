# Market State Profile Compatibility Design Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_design_v0_1`
Date: `2026-07-24`
Scope: `event_state_core_four_session_opened_market_state_profile_compatibility_design`

## Purpose

This authorization opens one design-only gate:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

It permits TSIS to decide whether the official Market State profile:

```text
market_state_core_four_intraday_profile_v0_1
```

is semantically compatible with the current Event State grammar for:

```text
event_type_id = event_type:market_data:session_opened
event_subject_scope = exchange_session
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

## Critical Boundary

Compatibility design is not physical consumption.

This gate must not read Market State parquet, create Event Instances, create
Event Windows, build Event State, materialize a dataset, promote a dataset,
authorize production or open downstream consumption.

## Authorized Work

Allowed:

```text
read official Market State profile registry artifacts
read Event State profile contract design
read Event Type/Instance/Window design contracts
classify semantic compatibility
classify physical consumption authority separately
define required future join/projection constraints
define compatibility blockers and restrictions
write design, contract and readout artifacts
update README, policy, matrix, handoff and changelogs
```

## Explicitly Not Authorized

```text
market_state_physical_consumption = false
official_market_state_dataset_consumption = false
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

## Required Decision

The design must separate:

```text
semantic_profile_compatibility
physical_consumption_authority
execution_readiness
```

It must not convert the official semantic Market State profile into an
official physical dataset claim.

## Expected Finding

The expected compatibility finding is:

```text
semantically_compatible_with_restrictions
requires_instrument_session_projection_design
physical_consumption_not_authorized
```

because Market State core-four is instrument/timestamp scoped while
`session_opened` is exchange-session scoped.

## Next Gate

If this design closes, the next recommended gate is:

```text
event_state_instrument_session_projection_design_authorization_v0_1
```
