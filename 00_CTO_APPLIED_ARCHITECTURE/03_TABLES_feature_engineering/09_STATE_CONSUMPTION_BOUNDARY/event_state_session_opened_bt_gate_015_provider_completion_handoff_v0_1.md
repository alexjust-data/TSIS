# Event State `session_opened` BT-GATE-015 Provider Completion Handoff v0.1

## Status

```text
provider temporal evidence
=
CLOSED_PASS_ROW_ADDRESSABLE_EVENT_STATE_REPLAY_AVAILABILITY_EVIDENCE_WITH_RESTRICTIONS

provider typed payload binding
=
CLOSED_BINDING_READY_WITH_RESTRICTIONS

BT-GATE-015 contract revision
=
READY

BT-GATE-015 implementation
=
NOT_AUTHORIZED
```

## Executable bounded identity

The earlier contract handoff selected the accepted historical profile record.
It remains provenance evidence, but it is not the bounded delivery identity
because its Market State dependency predates the governed replay sidecar.

The bounded consumer contract must use this on-demand identity chain:

```text
event_state_record_id =
e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76

event_state_record_fingerprint =
31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01

event_instance_id =
3d5afb67c49949b7db5ab85ef4a230e36282c36d1086eaa42e3dfdc90279ff63

event_window_binding_id =
0c4f1090ea7caf55d888d1601914af90357f4aa828474b78df1e01e22ca7479d

instrument_projection_id =
718b8df0b5ae8fdc547b06c73299cc037ef7f964bfad1682b2304d6698ff41f7

market_state_record_id =
ba92895493bdc05e2ad07b78b1491f1b62d74d1079869b58c3df95cefdc622ee

market_state_state_output_fingerprint =
9430c9903b6172c9183e8cce264bfdfcb0da83d391becc05eb7ef56f11509685
```

The Market State dependency dataset and the later availability-evidence
dataset are not represented as identical datasets. Their binding is:

```text
EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE
```

## Temporal evidence

For this exact `AAME / XNYS / 2021-01-19 / at_event` record:

```text
event_anchor_timestamp_utc = 2021-01-19T14:30:00Z
event_state_as_of_utc = 2021-01-19T14:30:00Z
event_state_available_at_utc = 2021-01-19T14:30:00Z
event_state_publication_latency = PT0S
state_replay_consumption_legality = research_only
```

The equality is derived from the governed Event Instance, Event Window,
Instrument Projection and exact Market State replay sidecar. It is not derived
from `created_at_utc` or materialization time.

Delivery remains:

```text
event_loop.clock >= event_state_available_at_utc
```

## Typed payload

`BoundedEventStateAvailable` must separate:

```text
envelope
event_context
market_state_core_four_payload
audit_lineage
```

The scientific payload contains exactly 17 numeric core-four fields:

```text
Price Location / Structure = 5
Price Movement = 5
Trading Activity = 4
Volatility / Range State = 3
```

The field-level authority is:

```text
event_state_session_opened_typed_payload_binding_v0_1.json
```

No additional Event State scientific indicator is authorized in v0.1.
Event identity, window, role and legality are typed event context, not hidden
scientific features.

## Preserved boundary

This handoff does not authorize:

```text
Event State physical consumer read
BT-GATE-015 implementation
StateReplayFeed general
strategy callbacks
signals
orders
fills
positions
PnL
production
downstream
official dataset promotion
```

The backtester must revise its draft contract against this exact handoff and
submit that contract to its owner review before any implementation authority.
