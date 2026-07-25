# Event State Integration Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `event_state_integration_design_v0_1_20260724T150000Z`

## 1. Scope

This design defines the first Event State integration grammar for:

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_type_id = event_type:market_data:session_opened
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
```

It is design-only. It does not consume physical Market State records, create
Event Instances, bind windows, project instruments, emit Event State records or
materialize any dataset.

## 2. Integration Purpose

Event State integration must not be a loose column copy around an event. It is
an atomic binding between:

```text
Market State record
Event Instance
Event Window Binding
Instrument Session Projection
State role
Consumption legality
```

For `session_opened`, the Event Type is exchange-session scoped. The projection
layer is therefore mandatory before a Market State record can be attached to
the event context.

## 3. Future Event State Grain

Future Event State records for this profile must be uniquely identified at this
conceptual grain:

```text
event_state_profile_id
event_type_id
event_instance_id
event_window_binding_id
event_state_instrument_session_projection_id
market_state_record_id or state_output_fingerprint
state_role
consumption_legality
integration_policy_version
```

No native Event State record may exist without a Market State record reference
and the projection that legally maps the exchange-session event/window to the
instrument-session context.

## 4. Future Record Identity

Conceptual deterministic identity:

```text
event_state_record_id =
sha256(
    event_state_profile_id
    + event_type_id
    + event_instance_id
    + event_window_binding_id
    + event_state_instrument_session_projection_id
    + market_state_record_id_or_state_output_fingerprint
    + state_role
    + consumption_legality
    + integration_policy_version
)
```

The identity must change when any binding, state role, consumption legality or
integration policy changes. It must not change because of unrelated runtime
location or file layout changes.

## 5. Exact-One Binding Rule

Future integration may emit a row only when all bindings resolve exactly once:

```text
source_market_state_record_binding = exactly_one
event_instance_binding = exactly_one
event_window_binding = exactly_one
instrument_session_projection_binding = exactly_one
state_role_classification = exactly_one
consumption_legality_classification = exactly_one
```

Failure policy:

```text
missing_binding -> blocked
multiple_bindings -> blocked
partial_event_state_record -> prohibited
substituted_market_state_record -> prohibited
fallback_to_unprofiled_market_state -> prohibited
```

There is no valid Event State row with missing Market State values, missing
event lineage, missing projection lineage or inferred legality.

## 6. Required Future Fields

Future Event State records should preserve at least:

```text
event_state_record_id
event_state_profile_id
event_state_schema_version
integration_policy_id
integration_policy_version
event_type_id
event_family_id
event_instance_id
event_instance_version
event_window_definition_id
event_window_binding_id
event_state_instrument_session_projection_id
source_market_state_profile_id
source_market_state_schema_version
market_state_record_id
state_output_fingerprint
instrument_id
ticker
exchange_id
session_date
decision_timestamp_utc
event_anchor_timestamp_utc
window_start_utc
window_end_utc
relative_time_to_event
state_role
consumption_legality
object_completeness_status
integration_status
quality_status
calendar_version
calendar_row_fingerprint
source_lineage_json
policy_versions_json
restriction_codes_json
created_at_utc
supersedes_event_state_record_id
superseded_by_event_state_record_id
```

This is not a physical schema authorization. It is the minimum integration
contract for a later execution gate.

## 7. State Role Policy

`state_role` is the temporal relationship between the Market State record and
the Event Instance:

```text
pre_event
at_event
post_event
post_event_review
```

For `session_opened`, `at_event` is anchored at governed regular-session open,
not at first observed trade.

`post_event` and `post_event_review` never imply decision-safe usage.

## 8. Consumption Legality Policy

`consumption_legality` is separate from `state_role`:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Future integration must prove legality from the Event Window Binding, Market
State cutoff/as-of evidence and first-observable policies. It must not infer
legality from the event name or from the existence of a later outcome.

## 9. Market State Consumption Boundary

This design references the official semantic profile:

```text
market_state_core_four_intraday_profile_v0_1
```

It does not authorize reading any physical Market State parquet. Future
integration execution must use an explicitly authorized Market State evidence
source, dataset or record registry. It must not rebuild Market State from
Data Foundation tables unless a separate gate authorizes that mode.

## 10. Event And Execution Boundaries

Event State integration does not define:

```text
locates
borrow availability
broker routing
fills
slippage
commissions
API latency
tradability
```

Those belong to future Execution State or execution policy. Their absence must
not mutate Event Type, Event Instance, Event Window or Event State identity.

## 11. Closed Boundaries

Still closed:

```text
event_state_integration_execution
event_state_builder_execution
event_instance_binding_execution
event_window_binding_execution
instrument_session_projection_execution
market_state_physical_consumption
event_state_materialization
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 12. Next Work

The next recommended gate is:

```text
event_state_execution_chain_joint_review_authorization_v0_1
```

That review should inspect the complete design chain before opening any Event
State execution authorization.
