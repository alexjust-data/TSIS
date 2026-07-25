# Event Window Binding Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `event_window_binding_design_v0_1_20260724T140500Z`

## 1. Scope

This design defines the Event Window Binding grammar for the accepted Event
Type:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
```

It depends on the closed Event Instance Binding Design, which defines one
native `session_opened` Event Instance per governed exchange session open.

This document is design-only. It does not create Event Windows, read historical
calendar rows, consume Market State data, run detectors, materialize Event
State or authorize downstream consumption.

## 2. Distinct Objects

TSIS must keep these objects separate:

```text
Event Type
    = governed occurrence class

Event Instance
    = one concrete governed occurrence

Event Window Definition
    = reusable temporal policy around an Event Type or Event Instance class

Event Window Binding
    = future association of one Event Instance with one Window Definition

Event State
    = Market State Profile + Event Instance + Event Window + state_role + consumption_legality
```

For `session_opened`, the native event remains exchange-session scoped. A
future instrument association can project an exchange-session event into many
instrument-session contexts, but that projection must not change the native
Event Instance identity.

## 3. Window Definition Identity

An Event Window Definition is a contract object, not a row of historical data.

Canonical identity components:

```text
window_definition_id
event_type_id
event_subject_scope
anchor_role
relative_start_offset
relative_end_offset
calendar_boundary_policy
state_role
consumption_legality_policy
window_definition_version
```

For v0.1, `event_subject_scope` must remain:

```text
exchange_session
```

The definition must not include:

```text
instrument_id
ticker
strategy_id
trade_direction
entry_rule
exit_rule
outcome_label
profitability_label
execution_route
broker_id
locate_status
```

Those belong to future projection, strategy, outcome or Execution State layers.

## 4. Future Binding Identity

A future Event Window Binding will bind exactly one Event Instance to exactly
one Window Definition.

Conceptual deterministic identity:

```text
event_window_binding_id =
sha256(
    event_instance_id
    + window_definition_id
    + event_type_id
    + event_anchor_timestamp_utc
    + window_start_utc
    + window_end_utc
    + calendar_version
    + calendar_row_fingerprint
    + window_policy_version
)
```

The exact implementation may be encoded later, but the identity rule must
preserve:

```text
same governed occurrence + same window policy -> same binding id
changed calendar authority or corrected boundary -> traceable new version or supersession
```

## 5. Required Binding Fields

A future binding record must preserve at least:

```text
event_window_binding_id
event_instance_id
event_type_id
event_family_id
window_definition_id
window_definition_version
state_role
consumption_legality
event_anchor_timestamp_utc
first_observable_timestamp_utc
binding_created_at_utc
relative_start_offset
relative_end_offset
window_start_utc
window_end_utc
window_duration_seconds
calendar_authority_id
calendar_version
calendar_source_snapshot_fingerprint
calendar_row_fingerprint
exchange_id
session_date
session_open_utc
session_close_utc
session_type
is_early_close
calendar_boundary_policy
clipping_policy_id
window_quality_state
leakage_assessment
supersedes_event_window_binding_id
superseded_by_event_window_binding_id
correction_reason
```

This field list is a minimum contract for future execution design. It is not a
schema for a physical parquet in this gate.

## 6. Timestamp Policy

For `session_opened`:

```text
event_anchor_timestamp_utc = governed session_open_utc
regular_session_open_timestamp != first_observed_trade_timestamp
```

The design distinguishes:

```text
event_anchor_timestamp_utc
first_observable_timestamp_utc
binding_created_at_utc
window_start_utc
window_end_utc
```

Calendar knowledge may be known before open. The event occurrence itself exists
at the governed open timestamp, not earlier.

## 7. State Role

Allowed v0.1 state roles:

```text
pre_event
at_event
post_event
post_event_review
```

Interpretation:

```text
pre_event
    window ends no later than the event anchor.

at_event
    window is anchored at the event boundary.

post_event
    window includes information after the event anchor.

post_event_review
    window is explicitly for retrospective research, labels, outcomes or audit.
```

`state_role` is temporal position. It is not a permission to use the row as a
feature.

## 8. Consumption Legality

Allowed v0.1 consumption legality classes:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Rules:

```text
post_event != decision_safe
post_event_review != decision_safe
outcome_adjacent != feature input
```

A future consumer must preserve both `state_role` and `consumption_legality`.
If a consumer cannot explain whether a window is pre-event, at-event,
post-event or outcome-adjacent, it must not consume the window.

## 9. Calendar Boundary And Clipping Policy

All boundaries must use governed calendar authority:

```text
session_open_utc
session_close_utc
calendar_version
calendar_row_fingerprint
```

No fixed UTC calendar fallback is allowed.

Required clipping semantics:

```text
holidays/weekends
    no Event Instance; therefore no Event Window Binding.

DST transitions
    resolved through governed UTC timestamps from the accepted calendar.

early closes
    preserve early-close lineage; post-event windows must not silently extend
    beyond governed session_close_utc.

exceptional closures or corrections
    require explicit quality state or supersession.
```

For `session_opened`, early close does not change the event anchor. It does
affect any same-session or post-event clipping.

## 10. Design Window Templates

This design records non-executable templates only. They are not registry rows
and do not create windows.

```text
template_id = session_opened_pre_event_context_v0_1
state_role = pre_event
relative_end_offset = PT0S
consumption_legality_policy = decision_safe_only_for_observable_pre_anchor_fields

template_id = session_opened_at_anchor_context_v0_1
state_role = at_event
relative_start_offset = PT0S
relative_end_offset = PT0S
consumption_legality_policy = research_only_until_at_event_field_legality_is_reviewed

template_id = session_opened_post_open_context_v0_1
state_role = post_event
relative_start_offset = PT0S
relative_end_offset = bounded_by_future_window_definition
consumption_legality_policy = research_only_or_outcome_adjacent_not_pre_event_feature
```

The exact offsets for executable windows must be frozen by a later execution
authorization or registry population gate.

## 11. Instrument Projection Boundary

Native binding remains:

```text
exchange_session Event Instance
    +
exchange_session Event Window Definition
```

Future instrument projection must answer separately:

```text
which instruments were listed or eligible for the exchange session
which venue/exchange identity applies
whether instrument-specific halts or trading availability affect usability
which Market State profile may be joined
which Execution State facts affect tradability
```

An instrument being halted at the regular open does not invalidate the exchange
session opening event. It affects future instrument projection, Market State,
Event State or Execution State interpretation.

## 12. Data Foundation Alignment

Data Foundation already documents `event_windows_table_v0_1` as a governed
physical table of event boundaries with leakage, quality and consumption
restrictions.

This design uses that as reference evidence only. It does not claim the
existing Data Foundation table is a physical implementation of
`event_state_core_four_intraday_profile_v0_1`, and it does not authorize reads
from that table.

The shared principle is preserved:

```text
event windows are boundaries
event windows are not features, labels, alpha, price data or execution truth
```

## 13. Closed Boundaries

Still closed:

```text
event_window_binding_execution
event_window_registry_population
event_instance_binding_execution
instrument_projection_execution
event_detection_execution
Market State physical consumption
Event State builder execution
Event State materialization
official Event State profile promotion
official Event State dataset promotion
production
downstream consumption
```

## 14. Next Work

The next recommended gate is:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

Event Window Binding execution should remain closed until Event Instance
Binding Design, Event Window Binding Design and Market State Profile
Compatibility Design have all closed and a separate execution authorization is
issued.
