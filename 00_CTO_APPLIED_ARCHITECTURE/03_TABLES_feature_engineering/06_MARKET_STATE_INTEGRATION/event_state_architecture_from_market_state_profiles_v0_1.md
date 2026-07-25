# Event State Architecture From Market State Profiles v0.1

Status: `event_state_architecture_seed_recorded_no_execution_v0_1`
Date: `2026-07-23`
Scope: `event_state_design_seed_after_core_four_market_state_profile_promotion`

This document records the first Event State architecture seed that can depend
on an official TSIS Market State profile.

It does not authorize Event State builders, event detection, event table
materialization, Market State physical consumption, production or downstream
use.

## 1. Parent Market State Profile

The currently available parent profile is:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
registry_path = 06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1
```

Event Type names are not authority. Future Event State gates must distinguish
phenomenon definition from strategy response, outcome label, detector
implementation and physical Market State consumption authority.

This parent is a semantic profile contract, not an operational dataset.
Physical consumption still requires a separate consumption policy or
operational registry design.

## 2. Event State Role

Event State answers:

```text
What observable state was available for instrument I,
relative to event E,
at decision timestamp t?
```

It must not answer by rebuilding Market State independently.

Required relation:

```text
Event State
    references valid Market State profile evidence
    adds event identity
    adds temporal relation to the event
    adds event-specific context and quality flags
```

## 3. Required Separation

Event State must keep these layers separate:

```text
event_ontology
event_detection
event_instance_table
event_window_binding
market_state_profile_binding
event_state_integration
event_state_materialization
event_state_independent_validation
outcome_research
```

Event State must not merge outcomes into state. Outcome labels, future returns
and post-decision performance remain downstream research artifacts.

## 4. Minimum Event State Keys

Any future design must define, at minimum:

```text
event_id
event_type
instrument_id
event_timestamp
decision_timestamp
market_state_profile_id
market_state_profile_version
market_state_reference_id_or_fingerprint
state_role
consumption_legality
relative_time_to_event
event_phase
event_quality_flags
```

The `market_state_reference_id_or_fingerprint` cannot point to an unaudited
candidate unless the Event State gate explicitly authorizes candidate evidence.

## 5. State Role And Consumption Legality

Event State must preserve two independent axes:

```text
state_role
    = pre_event | at_event | post_event

consumption_legality
    = decision_safe | research_only | outcome_adjacent | prohibited_as_input
```

Rule:

```text
post_event may be valid Event State for research,
but it cannot be consumed as input for a decision made before or at the event.
```

## 6. Gate Sequence

Recommended future sequence:

```text
event_state_architecture_design_authorization
event_ontology_or_event_family_contract
event_detector_validation
event_instance_table_candidate
event_window_binding_validation
market_state_profile_binding_validation
event_state_integration_execution
event_state_candidate_materialization
event_state_independent_physical_validation
event_state_promotion_review
```

No execution step in this sequence is opened by this document. The first design
continuation has now been recorded separately:

```text
event_state_profile_contract_design_v0_1.md
event_state_profile_contract_design_contract_v0_1.json
../07_EVENT_STATE_INTEGRATION/event_state_event_policy_v0_1.md

../07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_v0_1.md
../07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_contract_v0_1.json
../07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_v0_1.md
../07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_contract_v0_1.json
```

## 7. Current Boundary

Current status:

```text
event_state_architecture_seed = RECORDED_NO_EXECUTION
event_policy = RECORDED_NO_EXECUTION
event_type_registry_schema = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
accepted_event_types = 0
event_type_registry_population = NOT_AUTHORIZED
event_state_builder_execution = NOT_AUTHORIZED
event_detection_execution = NOT_AUTHORIZED
event_instance_table_materialization = NOT_AUTHORIZED
event_state_materialization = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
production = NOT_AUTHORIZED
```

The only architectural change recorded here is that Event State now has a
valid official-profile parent candidate:

```text
market_state_core_four_intraday_profile_v0_1
```

Event domains and epistemic roles must be explicit before Event State
instance binding can close over concrete populations. Scanner, research and
system events are valid TSIS concepts only when they are not confused with
market phenomena.
