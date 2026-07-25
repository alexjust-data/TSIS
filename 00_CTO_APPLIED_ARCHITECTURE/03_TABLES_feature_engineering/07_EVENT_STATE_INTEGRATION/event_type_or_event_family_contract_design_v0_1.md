# Event Type Or Event Family Contract Design v0.1

Status: `closed_design_ready_with_restrictions_no_execution_v0_1`
Date: `2026-07-23`
Scope: `event_type_family_authority_before_event_instance_binding`

## Current-State Note

Date: `2026-07-24`

`event_type_registry_seed_design_v0_1` has since closed the empty registry schema design with restrictions, and `event_type_registry_initial_population_readout_v0_1` has recorded the first candidate-only population. This document remains the accepted prior contract-shape gate; the current next possible gate is `event_type_initial_admission_review_authorization_v0_1`, only if explicitly authorized. Accepted Event Types, detection, instances, builders, materialization, production and downstream consumption remain closed.

This document defines the operational contract design required before
`event_instance_binding_design_v0_1` can close.

It does not detect events.
It does not create event instances.
It does not materialize an event table.
It does not authorize Event State builders, integration, materialization,
production or downstream consumption.

## 1. Design Decision

```text
event_type_or_event_family_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_status = DESIGN_CONTRACT_READY_NOT_POPULATED
event_instance_binding_design = NOT_OPEN_NEXT_IF_EXPLICITLY_AUTHORIZED
event_detection_execution = NOT_AUTHORIZED
event_state_builder_execution = NOT_AUTHORIZED
```

TSIS already has conceptual event taxonomy authority. This gate converts that
authority into an operational contract shape for future `event_type_id`
references.

## 2. Conceptual Authorities

This design depends on:

```text
00_EPISTEMOLOGICAL_architecture/03_TSIS_EVENTS/02_Chapter_2_Event_Taxonomy_TSIS_Event_Research_Architecture.md
00_EPISTEMOLOGICAL_architecture/03_TSIS_EVENTS/03_Chapter_3_Event_Families_TSIS_Event_Research_Architecture.md
02_MATERIALIZATION_GOVERNANCE_REVIEW/03_event_state_governance/canonical_to_physical_mapping_event_state_v1.md
06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_v0_1.md
```

These sources define taxonomy, family rules and Event State physical-planning
constraints. They do not provide a populated operational `event_type_id`
registry by themselves.

## 3. Taxonomy Principle

```text
taxonomy defines meaning
implementation defines detection
```

An `event_type_id` must not be a strategy label, an outcome label, a trade
quality label or a post-hoc profitability class.

## 3.1 Event Policy Authority

Detailed event policy is recorded in:

```text
event_state_event_policy_v0_1.md
```

Binding rule:

```text
event grammar can be closed before the dictionary is populated.
event_type_registry_population remains closed.
accepted_event_types = 0.
```

Future work may define a registry seed schema and admission process, but it
must not treat informal names as accepted Event Types. Discovery, detector
experimentation and strategy research create candidates only until a separate
admission gate accepts a concrete type.

## 4. Event Family Contract

Allowed candidate family namespaces recognized by this design:

```text
market_data
regulatory
market_structure
information
scanner
geometry
microstructure
research
```

These are conceptual namespaces, not accepted registry family entries.
Accepted registry family entries remain zero until a future population and
admission gate creates them.

Every event family contract entry must define:

```text
event_family_id
event_family_version
canonical_name
semantic_definition
observable_origin
anchor_definition_policy
eligibility_policy_id
population_policy_id
window_policy_id
outcome_policy_id
allowed_event_type_namespace
forbidden_strategy_labels
governance_status
definition_hash
```

No event family may remain semantically ambiguous.

## 5. Event Type Contract

Every future `event_type_id` must be backed by a versioned contract entry with:

```text
event_type_id
event_type_version
event_family_id
canonical_name
semantic_definition
observable_origin
anchor_timestamp_policy
first_observable_timestamp_policy
detection_timestamp_policy
eligibility_policy_id
population_policy_id
window_policy_id
detector_contract_id
detector_version
source_dataset_authority
source_quality_requirements
event_variant_policy
promotion_status
definition_hash
```

The contract entry must be immutable once referenced by an event instance. Any
semantic change requires a new version.

## 5.1 Event Domain And Epistemic Role

Every future Event Type contract must distinguish:

```text
event_domain
    = market
    | information
    | microstructure
    | regulatory
    | system
    | research
    | scanner

event_epistemic_role
    = observed_phenomenon
    | system_generated_candidate
    | research_annotation
    | governance_state_change
```

This prevents scanner candidates, research annotations or governance events
from being treated as market phenomena merely because they are time-stamped.

## 6. Event Variant Boundary

Variants may specialize implementation, but cannot change the event type's
scientific meaning.

Required variant fields when variants exist:

```text
event_variant_id
event_variant_version
parent_event_type_id
implementation_parameters
threshold_policy
detector_variant_version
variant_hash
```

Variants are not allowed to become hidden strategy rules.

## 7. Anchor And Observability

Every event type must distinguish:

```text
event_anchor_timestamp_utc
first_observable_timestamp_utc
detection_timestamp_utc
```

Rules:

```text
event_anchor_timestamp_utc = where the event is anchored in market time.
first_observable_timestamp_utc = earliest time the event could be observed.
detection_timestamp_utc = time a governed detector can emit the instance.
```

`at_event = decision_safe` requires proof that detection timing made the event
legally observable at or before the decision timestamp.

## 8. Forbidden Classes

The following cannot be event families or event types:

```text
winning_trades
best_entries
high_probability_longs
alpha_signals
profitable_setups
good_entries
```

These are strategy or outcome abstractions, not observable event classes.

## 9. Registry Boundary

This design defines the registry contract shape. It does not populate or
promote an operational event type registry.

Current note: the empty Event Type Registry seed schema is now closed by `event_type_registry_seed_design_v0_1`; registry population still remains closed.

Future event instance binding must cite one of:

```text
accepted_event_type_contract_entry
accepted_event_family_contract_entry + explicitly bounded event_type_contract_entry
```

If neither exists for the selected event population, the instance binding must
block.

## 9.1 Current Registry State

```text
event_type_registry_contract_shape = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_schema = CLOSED_BY_EVENT_TYPE_REGISTRY_SEED_DESIGN_V0_1
event_type_registry_seed_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_population = NOT_AUTHORIZED
accepted_event_families = 0
accepted_event_types = 0
candidate_event_types = future_gate_only
```

This absence of accepted types is not a defect. It means the architecture is
ready to host a registry, while the scientific catalog remains unpopulated until
future admission work.

## 10. Validation Requirements For Future Gates

Future gates must prove:

```text
event_type_id resolves to exactly one contract entry
event_family_id resolves to exactly one family entry
event_type belongs to exactly one primary family
definition_hash matches the referenced contract
detector_contract_id is present or explicitly not_applicable for non-detector events
anchor_timestamp_policy is explicit
first_observable_timestamp_policy is explicit
detection_timestamp_policy is explicit
source_dataset_authority is explicit
outcome labels are not part of event identity
strategy labels are not part of event identity
```

## 11. Closed Boundaries

Still closed:

```text
event_type_registry_population
event_detection_execution
event_instance_binding_execution
event_window_binding_execution
event_state_builder_execution
event_state_integration_execution
event_state_materialization
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 12. Next Gates

Immediate next allowed gate, only after explicit authorization:

```text
event_type_registry_initial_population_authorization_v0_1
```

`event_instance_binding_design_v0_1` may close only if it cites an accepted
event type contract entry or declares a hard block for missing event type
authority. If it is purely abstract, it must explicitly state that no concrete
`event_type_id` population or instance binding is being used.


Subsequent gates after seed design, not immediate gates:

```text
event_type_registry_initial_population_authorization_v0_1
event_type_admission_review_design_v0_1
event_instance_binding_design_v0_1
event_window_binding_design_v0_1
market_state_profile_compatibility_design_v0_1
```
