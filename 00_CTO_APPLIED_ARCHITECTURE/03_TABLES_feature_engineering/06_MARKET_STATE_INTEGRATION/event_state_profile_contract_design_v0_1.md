# Event State Profile Contract Design v0.1

Status: `closed_design_ready_with_restrictions_no_execution_v0_1`
Date: `2026-07-23`
Scope: `event_state_core_four_intraday_profile_contract_design`

This document defines the first governed Event State profile contract design
that can depend on an official TSIS Market State profile.

It does not authorize event detection.
It does not authorize Event State builder execution.
It does not authorize Event State integration.
It does not authorize Event State materialization.
It does not authorize parquet output, production or downstream consumption.

## 1. Design Decision

```text
event_state_profile_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
source_market_state_profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
event_state_builder_execution = NOT_AUTHORIZED
event_state_materialization = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
```

The profile is concrete at the Event State profile-contract level. It is not an
event-family implementation. Specific event families and event instances must
be bound by later gates.

## 2. Parent Profile Binding

Required parent:

```text
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
profile_registry_path = 06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1
promotion_run = official_market_state_candidate_promotion_v0_1_20260723T193403Z
artifact_validation_run = official_market_state_profile_artifact_validation_v0_1_20260723T193711Z
```

Event State must reference a valid Market State profile contract. It must not
rebuild Market State, read upstream source tables directly, or silently expand
the source Market State profile.

## 3. Required Contract Fields

Any future Event State row or candidate record for this profile must carry:

```text
event_state_profile_id
event_state_profile_version
source_market_state_profile_id
source_market_state_profile_version
event_type_id
event_instance_id
event_window_id
instrument_id
ticker
event_anchor_timestamp_utc
decision_timestamp_utc
state_role
consumption_legality
window_definition_id
market_state_reference_id_or_fingerprint
join_policy_id
object_atomicity_policy_id
lineage_manifest_id
quality_state
```

The fields are requirements for a future builder contract. They are not
materialized by this design.

## 4. Event Identity Boundary

This design requires, but does not define or validate:

```text
event_type_id
event_instance_id
event_anchor_timestamp_utc
event_source_dataset_id
event_source_quality_state
```

Those must be supplied by a separate event instance binding design and later
validated before any Event State builder can execute. Event type/family
authority must exist before event instance binding can close.

## 5. Window Definition Boundary

This design requires, but does not define or validate:

```text
window_definition_id
event_window_id
event_window_start_utc
event_window_end_utc
pre_event_window_start_utc
pre_event_window_end_utc
state_cutoff_utc
state_cutoff_reason
relative_time_to_event
```

Those belong to a separate Event Window Binding design. Event State cannot infer
windows from available bars or from post-hoc outcomes.

## 6. State Role

Profile-level allowed `state_role` values:

```text
pre_event
at_event
post_event
post_event_review
```

Compatibility note:

```text
research_replay
```

exists in the current table-017 representation materialization vocabulary. If a
future physical Event State design uses it, it must map it explicitly to
`research_only` or `prohibited_as_input`; it cannot be treated as
`decision_safe`.

## 7. Consumption Legality

Allowed `consumption_legality` values:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Rules:

```text
state_role describes event-relative position.
consumption_legality decides whether the record can be used as input.
pre_event may be decision_safe only if all as-of and cutoff checks pass.
at_event may be decision_safe only if event detection timing makes it legal.
post_event cannot be decision_safe for a decision made before or at the event.
post_event_review cannot be decision_safe for predictive event-time input.
outcome_adjacent records must not be used as X features.
```

## 8. Join Semantics

Future Event State builders must join:

```text
Market State Profile
    + Event Instance
    + Event Window
    + Temporal Role
    + Consumption Legality
```

Minimum join requirements:

```text
instrument_id must match between event and Market State reference.
decision_timestamp_utc must be at or before the state cutoff.
market_state_reference_id_or_fingerprint must resolve to accepted profile evidence.
event_anchor_timestamp_utc must belong to the event instance contract.
event_window_id must resolve to exactly one window binding.
```

No join may use future outcome labels, reward fields or post-hoc performance as
state input.

## 9. Object Atomicity

Event State rows must not contain partial unclassified Market State.

Future builders must enforce:

```text
source_market_state_profile_binding = exactly_one
event_instance_binding = exactly_one
event_window_binding = exactly_one
state_role_classification = exactly_one
consumption_legality_classification = exactly_one
missing_required_binding = blocked
ambiguous_required_binding = blocked
```

Partial candidate rows may be reported as rejected evidence, but must not be
materialized as valid Event State.

## 10. Lineage Requirements

Every candidate and every future materialized row must be reconstructible from:

```text
event_state_profile_id
event_state_profile_version
source_market_state_profile_id
source_market_state_profile_validation_run
event_instance_binding_run
event_window_binding_run
builder_run_id
integration_run_id
materialization_run_id
validation_run_id
source_manifest_hash_bundle
restriction_manifest_hash
```

## 11. Closed Boundaries

Still closed:

```text
event_detection_execution
event_instance_table_materialization
event_window_binding_execution
market_state_physical_consumption
event_state_builder_execution
event_state_integration_execution
event_state_materialization
event_state_physical_validation
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 12. Event Policy Dependency

The Event State profile depends on the standing event policy recorded in:

```text
../07_EVENT_STATE_INTEGRATION/event_state_event_policy_v0_1.md
```

Policy boundary:

```text
event grammar can be defined before the event dictionary is populated.
event_type_registry_contract_shape = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_schema = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_population = NOT_AUTHORIZED
accepted_event_types = 0
event_type_registry_population = NOT_AUTHORIZED
event type identity must not encode strategy, outcome, trade action or profitability.
```

A future Event Instance binding design may be abstract, but it cannot close over
concrete instances until it cites accepted event type authority.

## 13. Next Gates

Next work requires explicit authorization. Recommended sequence:

```text
event_type_or_event_family_contract_design_v0_1 = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_seed_design_v0_1 = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_initial_population_authorization_v0_1
event_instance_binding_design_v0_1
event_window_binding_design_v0_1
market_state_profile_compatibility_design_v0_1
event_state_integration_design_v0_1
event_state_builder_validation_authorization_v0_1
```

No execution gate is opened by this contract design.

Subsequent gates after seed design, not immediate gates:

```text
event_instance_binding_design_v0_1
event_window_binding_design_v0_1
market_state_profile_compatibility_design_v0_1
event_state_integration_design_v0_1
event_state_builder_validation_authorization_v0_1
```


## Current Compatibility Note

Date: `2026-07-24`

Event Instance Binding Design, Event Window Binding Design and Market State
Profile Compatibility Design are now recorded under:

```text
../07_EVENT_STATE_INTEGRATION/event_instance_binding_design_readout_v0_1.md
../07_EVENT_STATE_INTEGRATION/event_window_binding_design_readout_v0_1.md
../07_EVENT_STATE_INTEGRATION/market_state_profile_compatibility_design_readout_v0_1.md
```

Compatibility with `market_state_core_four_intraday_profile_v0_1` is semantic
only and requires a future instrument-session projection design before any Event
State execution.


## Current Projection Note

Date: `2026-07-24`

Instrument Session Projection Design is now recorded under:

```text
../07_EVENT_STATE_INTEGRATION/event_state_instrument_session_projection_design_readout_v0_1.md
```

It defines the future bridge from exchange-session `session_opened` Event
Instance/Event Window Binding to instrument-session Market State context. It
creates no projections and authorizes no Event State execution.
