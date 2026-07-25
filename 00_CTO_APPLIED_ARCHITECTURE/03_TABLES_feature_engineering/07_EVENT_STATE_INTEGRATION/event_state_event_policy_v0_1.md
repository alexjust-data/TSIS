# Event State Event Policy v0.1

Status: `recorded_no_execution_v0_18_operational_registry_policy_design_closed`
Date: `2026-07-24`
Scope: `event_semantics_registry_and_lifecycle_policy`

This document records the standing TSIS policy for Event Type, Event Family,
Event Instance and Event State work after promotion of
`market_state_core_four_intraday_profile_v0_1`.

It is a policy document only.
It records the current Event Type Registry state, including the initial admission review, Event Instance Binding Design, Event Window Binding Design, Market State Profile Compatibility Design, Instrument Session Projection Design, Event State Integration Design, execution-chain joint review, bounded execution-chain authorization, candidate dataset review, profile promotion review and semantic profile promotion.
It does not by itself admit any concrete event type; admission lives in the review records and successor snapshot.
It does not detect events.
It does not create event instances.
It does not authorize unbounded Event State builders, materialization,
production or downstream consumption. A separate bounded execution-chain run, bounded physical validation, candidate dataset review, profile promotion review and semantic profile promotion now exist. The promotion is profile-registry metadata only; no Event State dataset, parquet, materialization, production or downstream consumption has been authorized by this policy.

## 1. Current Policy State

```text
event_policy = RECORDED_NO_EXECUTION
event_type_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_contract_shape = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_schema = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_seed_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_initial_population_authorization = CONSUMED_WITH_RESTRICTIONS
event_type_registry_population = CANDIDATE_POPULATION_RECORDED_WITH_RESTRICTIONS
event_type_initial_admission_review = CLOSED_WITH_MIXED_DECISIONS_NO_EXECUTION
candidate_event_families = 1
candidate_event_types = 1
accepted_event_families = 1
accepted_event_types = 1
event_type_initial_admission_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_detection_execution = NOT_AUTHORIZED
event_instance_binding_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_instrument_session_projection_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
event_state_bounded_execution_chain_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_state_bounded_execution_chain_execution = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT
event_state_bounded_execution_chain_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
event_state_candidate_dataset_review = CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION
event_state_profile_promotion_review = APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS
event_state_profile_promotion_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_state_profile_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
event_state_core_four_intraday_profile_v0_1 = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
event_state_candidate_records_emitted = 8
event_state_bounded_execution_blocked_contexts = 1
event_instance_binding_execution_standalone = NOT_AUTHORIZED
event_window_binding_execution_standalone = NOT_AUTHORIZED
event_state_builder_execution_standalone = NOT_AUTHORIZED
```

This is intentional. TSIS can finish the grammar of events before it knows the
complete dictionary of accepted event types.

## 2. Core Distinctions

TSIS separates the following concepts:

```text
event architecture
    != event catalog

event grammar
    != populated event dictionary

event type contract
    != event detector

event occurrence
    != strategy response

event candidate
    != accepted event type

semantic profile compatibility
    != physical consumption authority
```

No future gate may collapse these distinctions without an explicit promotion
decision and changelog entry.

## 3. Event Definition Policy

An Event Type must describe an observable market, information, microstructure,
scanner or research phenomenon.

It must define:

```text
event_type_id
event_family_id
semantic_definition
observable_origin
source_dataset_authority
event_anchor_timestamp_policy
first_observable_timestamp_policy
detection_timestamp_policy
quality_requirements
window_policy
allowed_state_roles
allowed_consumption_legality
definition_hash
```

An Event Type must not be accepted only because it has a familiar trading name.
The contract must say what physically or semantically happened, where it is
observed, when it becomes legally observable and how ambiguity is blocked.

It must also separate the event's domain from its epistemic role:

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

A scanner candidate, a research annotation or a governance state change can be
a valid TSIS event class, but it must not be represented as a market
phenomenon unless its domain and role explicitly justify that classification.

## 4. Strategy And Outcome Boundary

The event describes:

```text
what happened
```

The strategy describes:

```text
what to do about it
```

The outcome describes:

```text
what happened after it
```

Therefore, Event Type ids must not encode trade direction, intended action,
profitability, edge, score, reward or post-hoc quality.

Forbidden as Event Type or Event Family identities:

```text
long_vwap_reclaim
short_first_red_day
buy_first_pullback
sell_into_resistance
winning_trades
best_entries
high_probability_longs
alpha_signals
profitable_setups
good_entries
```

Potentially valid event names, only after definition and admission, would be
phenomenon labels such as:

```text
vwap_cross_from_below
halt_resume
high_of_day_break
approach_to_prior_resistance
first_pullback_after_expansion
```

These examples are not admitted by this document.

## 5. Event Type Registry Policy

The registry now has one post-initial-admission snapshot. One Event Type is
accepted with restrictions; one remains investigational:

```text
candidate_event_types = 1
candidate_event_families = 1
accepted_event_types = 1
accepted_event_families = 1
event_type_admission_execution_status = CLOSED_WITH_MIXED_DECISIONS_NO_EXECUTION
recognized taxonomy family identifiers != accepted registry family entries
investigational_candidate != accepted event type
```

The seed registry schema is designed by `event_type_registry_seed_design_v0_1.md`; the candidate-only snapshot is recorded by `event_type_registry_initial_population_readout_v0_1.md`; and the initial admission decision is recorded by `event_type_initial_admission_review_readout_v0_1.md` plus `event_type_registry_post_initial_admission_snapshot_v0_1.json`.

Allowed future phases:

```text
event_type_registry_seed_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS; schema, namespaces, status model, review mechanics

event_type_registry_initial_population_authorization
    = CONSUMED_WITH_RESTRICTIONS; created investigational candidates only

event_type_initial_admission_review_authorization
    = CONSUMED_WITH_RESTRICTIONS; one accepted_with_restrictions, one not_admitted

event_type_admission_review
    = scientific review of concrete event type definitions

event_instance_binding_design_authorization
    = next possible gate for accepted Event Types only; design only, no instance creation

event_detection_authorization
    = detector execution only after accepted Event Type and separate detector authority
```

If an event instance gate cites an `event_type_id` that is not backed by an
accepted registry entry, it must block.

## 6. Admission Status Policy

Future event type entries must carry one explicit status:

```text
investigational_candidate
contract_draft
accepted_with_restrictions
accepted
rejected
quarantined
superseded
```

Only `accepted_with_restrictions` or `accepted` entries may be used by a
concrete Event Instance binding gate.

`investigational_candidate` and `contract_draft` entries may be studied, but
cannot be treated as Event State authority.

## 7. Family, Type, Variant And Composition

Event Families group related phenomena. They do not replace Event Type
definitions.

Event Types define a specific phenomenon.

Variants may specialize implementation parameters, but they cannot change the
scientific meaning of the parent Event Type.

Compositions may combine multiple accepted Event Types into a higher-order
construct, but the composition must remain separate from each elemental type.

Example:

```text
squeeze
    may be a composition,
    not necessarily an elemental event type.
```

No complex label may be admitted until TSIS decides whether it is elemental,
variant-based or compositional.

## 8. Temporal And Leakage Policy

Every Event Type must distinguish:

```text
event_anchor_timestamp_utc
first_observable_timestamp_utc
detection_timestamp_utc
event_confirmation_timestamp_utc
event_invalidation_timestamp_utc
event_end_timestamp_utc
```

Not every event requires confirmation, invalidation or end timestamps, but the
contract must declare whether each field is required, optional or not
applicable.

The critical rule is:

```text
event_anchor_timestamp_utc
    != first_observable_timestamp_utc
    != detection_timestamp_utc
```

unless a contract explicitly proves equality.

`at_event = decision_safe` is allowed only if the detector could legally emit
the event instance at or before the decision timestamp.

No Event State row may use future outcome labels, post-hoc profitability,
reward fields, later event confirmation or later event invalidation as an input
for an earlier decision.

## 9. State Role And Consumption Legality

Event State must preserve two separate classifications:

```text
state_role
    = pre_event
    | at_event
    | post_event
    | post_event_review
```

```text
consumption_legality
    = decision_safe
    | research_only
    | outcome_adjacent
    | prohibited_as_input
```

Rules:

```text
post_event does not imply decision_safe.
post_event_review does not imply decision_safe.
outcome_adjacent must not be used as feature input.
prohibited_as_input may exist as evidence but not as model input.
```

## 10. Event Discovery Policy

Concrete Event Types may originate from:

```text
human discretionary market knowledge
statistical discovery over governed Market State
sequence discovery
change-point detection
clustering
forensic review of validated cases
```

Discovery does not equal admission.

Any discovered candidate starts as:

```text
investigational_candidate
```

and must pass contract definition, source authority, leakage review, detector
review and admission review before it can support Event Instance binding.

## 11. First Event Type Policy

The first populated event type should validate the lifecycle, not maximize edge.

Preferred first candidates should be:

```text
simple
observable
timestamp-clear
source-clear
deterministically reproducible
low ambiguity
```

Examples for a future admission process:

```text
halt_resume
vwap_cross_from_below
```

These examples are not accepted Event Types until a separate population and
admission gate says so.

## 12. Market State Compatibility Policy

Event State may depend on a Market State profile contract, but this policy does
not authorize physical Market State parquet consumption.

Current semantic parent:

```text
market_state_core_four_intraday_profile_v0_1
```

Future compatibility gates must distinguish:

```text
semantic_profile_compatibility
physical_consumption_authority
```

A gate may conclude semantic compatibility without authorizing reads from a
physical dataset.

## 13. Closed Boundaries

Still closed outside the separately authorized bounded execution-chain scope:

```text
event_type_registry_population_without_separate_authorization
event_type_admission_execution_without_separate_authorization
event_detection_execution
standalone_event_instance_binding_execution
standalone_event_window_binding_execution
unbounded_market_state_physical_consumption
unbounded_event_state_builder_execution
unbounded_event_state_integration_execution
event_state_profile_artifact_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS
event_state_operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_materialization
unbounded_event_state_physical_validation
official_event_state_dataset_promotion
production
downstream_consumption
```

## 14. Next Work

Immediate next allowed gate, only if explicitly authorized:

```text
market_state_on_demand_capability_design_authorization_v0_1
```

The registry now records one candidate-only population snapshot and one post-initial-admission successor snapshot.

```text
event_type:market_data:session_opened = accepted_with_restrictions
event_type:regulatory:halt_resumed = investigational_candidate; not_admitted
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_instrument_session_projection_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_state_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
event_state_bounded_execution_chain_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
event_state_bounded_execution_chain_execution = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT
event_state_bounded_execution_chain_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
event_state_candidate_dataset_review = CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION
event_state_profile_promotion_review = APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS
event_state_profile_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
event_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS
event_state_operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

No detector execution, unbounded Event Instance execution, unbounded Event State execution, official materialization, production or downstream consumption is authorized by this policy.

Subsequent gate after the accepted profile artifact validation:

```text
market_state_on_demand_capability_design_authorization_v0_1
```


## Initial Candidate Population Note

Date: `2026-07-24`

The first candidate-only registry population is recorded in:

```text
event_type_registry_initial_population_snapshot_v0_1.json
```

It creates two investigational candidate Event Types:

```text
event_type:regulatory:halt_resumed
event_type:market_data:session_opened
```

The initial admission review moved `event_type:market_data:session_opened`
to `accepted_with_restrictions` and kept `event_type:regulatory:halt_resumed`
as `investigational_candidate` with blocking findings. The current Event
Instance Binding Design is design-only for `session_opened`; it does not create
instances.

For `session_opened`, the standing temporal rule is:

```text
regular_session_open_timestamp != first_observed_trade_timestamp
```

The event is the governed regular-session open from calendar authority.

## Execution State Boundary

Event Types describe observable occurrences. They do not encode whether the
event was tradable or executable. Locates, slippage, broker availability, order
routing, API latency, partial fills, commissions, order acceptance and other
execution-capacity facts belong to a future Execution State or execution-policy
layer.


## Event Window Binding Design Note

Date: `2026-07-24`

The Event Window Binding Design is recorded in:

```text
event_window_binding_design_v0_1.md
event_window_binding_design_contract_v0_1.json
event_window_binding_design_readout_v0_1.md
```

It is design-only for `event_type:market_data:session_opened` under
`exchange_session` scope. It creates no Event Windows and authorizes no Event
Window Binding execution.

The standing rule is:

```text
Event Window Definition = reusable temporal policy
Event Window Binding = future association between one Event Instance and one Window Definition
```

`state_role` and `consumption_legality` must remain separate. Event windows are
boundaries; they are not features, labels, alpha, price data or execution truth.


## Market State Profile Compatibility Design Note

Date: `2026-07-24`

The Market State Profile Compatibility Design is recorded in:

```text
market_state_profile_compatibility_design_v0_1.md
market_state_profile_compatibility_design_contract_v0_1.json
market_state_profile_compatibility_design_readout_v0_1.md
```

It concludes that `market_state_core_four_intraday_profile_v0_1` is
semantically compatible with the Event State profile under restrictions, but
physical Market State consumption remains unauthorized.

The next required design is instrument-session projection because
`session_opened` is exchange-session scoped and Market State is
instrument/timestamp scoped.


## Instrument Session Projection Design Note

Date: `2026-07-24`

The Instrument Session Projection Design is recorded in:

```text
event_state_instrument_session_projection_design_v0_1.md
event_state_instrument_session_projection_design_contract_v0_1.json
event_state_instrument_session_projection_design_readout_v0_1.md
```

It preserves native exchange-session Event Instance and Event Window identities
while defining a future instrument-session projection layer. It creates no
projections and authorizes no Event State execution.

## Event State Integration Design Note

Date: `2026-07-24`

The Event State Integration Design is recorded in:

```text
event_state_integration_design_v0_1.md
event_state_integration_design_contract_v0_1.json
event_state_integration_design_readout_v0_1.md
```

It is design-only. It requires exact-one binding across Event Instance, Event
Window, Instrument Session Projection, Market State record, state_role and
consumption_legality. It creates no Event State records and authorizes no
materialization.

## Execution Chain Joint Review Note

Date: `2026-07-24`

The Event State Execution Chain Joint Review is recorded in:

```text
event_state_execution_chain_joint_review_readout_v0_1.md
event_state_execution_chain_joint_review_matrix_v0_1.json
```

It approved opening a bounded execution-chain authorization with restrictions.
It did not execute Event State and did not promote any Event State profile or
dataset.

## Bounded Execution Chain Authorization Note

Date: `2026-07-24`

The first bounded Event State execution-chain authorization is recorded in:

```text
event_state_bounded_execution_chain_authorization_v0_1.md
configs/event_state_bounded_execution_chain_scope_v0_1.json
event_state_bounded_execution_chain_contract_v0_1.json
event_state_bounded_execution_chain_authorization_readout_v0_1.md
```

It is restricted to `event_type:market_data:session_opened`,
`exchange_session` scope, 3 governed XNYS sessions, 3 instruments and at most 9
instrument-session contexts. It may consume only the validated non-official
Scale C Market State candidate parquet identified in the authorization scope.

The authorization remains not executed:

```text
event_state_bounded_execution_chain_execution = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT
event_state_candidate_records_emitted = 8
blocked_contexts = 1
event_state_parquet_files_written = 0
official_event_state_dataset_promotion = false
downstream_consumption = false
```

