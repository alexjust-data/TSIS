# Event Window Binding Design Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_design_v0_1`
Date: `2026-07-24`
Scope: `event_window_binding_design_only_for_session_opened_exchange_session`

## Purpose

This authorization opens one design-only gate:

```text
event_window_binding_design_authorization_v0_1
```

It permits TSIS to define the contractual grammar for future Event Window
Binding around the accepted-with-restrictions Event Type:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

The gate must not create Event Window rows, bind historical Event Instances,
consume Market State data, materialize Event State, write parquet, authorize
production or open downstream consumption.

## Required Authorities

The design must cite:

```text
event_type_registry_snapshot =
event_type_registry_post_initial_admission_snapshot_v0_1.json

event_type_registry_snapshot_sha256 =
f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43

event_instance_binding_design =
event_instance_binding_design_v0_1.md

data_foundation_reference_pattern =
01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md
```

The Data Foundation `event_windows_table_v0_1` documents existing physical
window boundaries, mainly halt-derived. It is reference evidence only in this
gate. This authorization does not consume it, promote it, modify it or assert
that it already implements the new Event State profile grammar.

## Authorized Work

Allowed:

```text
read prior Event State design documents
read Data Foundation event_windows_table contracts as reference evidence
define Event Window Definition identity
define future Event Window Binding identity
define state_role and consumption_legality requirements
define clipping and calendar-boundary policies
define lineage and supersession requirements
write a design contract and readout
update README, policy, matrix, handoff and changelog documents
```

## Explicitly Not Authorized

```text
event_window_binding_execution = false
event_windows_created = 0
event_window_registry_created = false
event_window_parquet_files_written = 0
event_instances_created = 0
historical_calendar_rows_consumed = 0
event_detection_execution = false
market_state_physical_consumption = false
event_state_builder_execution = false
event_state_materialization = false
dataset_promotion = false
production = false
downstream_consumption = false
```

## Design Constraints

The design must preserve these identities:

```text
Event Type identity = exchange-session occurrence
Event Instance identity = one native instance per governed exchange session open
Event Window Definition = reusable relative/context policy
Event Window Binding = future association between one Event Instance and one Window Definition
Instrument association = future projection, not native identity
```

For `session_opened`:

```text
event_anchor_timestamp_utc = governed session_open_utc
regular_session_open_timestamp != first_observed_trade_timestamp
```

The design must not infer an instrument-level event or window population from
the exchange-session Event Type.

## Required Temporal Separation

The design must distinguish:

```text
event_anchor_timestamp_utc
first_observable_timestamp_utc
binding_created_at_utc
window_start_utc
window_end_utc
```

Calendar knowledge may be available before the session opens, but the
`session_opened` occurrence itself does not exist before the governed open
timestamp.

## Closure Criteria

The gate can close only if:

```text
design_contract_written = true
readout_written = true
event_type_scope = event_type:market_data:session_opened
subject_scope = exchange_session
event_window_binding_execution_authorized = false
event_windows_created = 0
event_instances_created = 0
historical_calendar_rows_consumed = 0
market_state_physical_consumption = false
parquet_files_written = 0
downstream_consumption = false
```

## Next Gate

If this design closes, the next recommended gate is:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

Event Window Binding execution should remain closed until Event Instance
Binding Design, Event Window Binding Design and Market State Profile
Compatibility Design have all closed and a separate execution authorization is
issued.
