# Event State `session_opened` BT-GATE-015 Contract Handoff v0.1

Status:

```text
CLOSED_CONTRACT_HANDOFF_READY_WITH_RESTRICTIONS
BT_GATE_015_IMPLEMENTATION = NOT_AUTHORIZED
EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
```

## Purpose

Provide the BT-GATE-015 owner with one exact, governed Event State slice and
the temporal contract it must consume. This handoff does not deliver Event
State rows and does not authorize consumer implementation.

## Exact Slice

```text
event_type_id = event_type:market_data:session_opened
subject_scope = exchange_session
profile_id = event_state_core_four_intraday_profile_v0_1
exchange_id = XNYS
session_date = 2021-01-19
ticker = AAME
instrument_id = figi_share_class:BBG001S5N8T1
state_role = at_event
window = exact session-open anchor, PT0S / PT0S
```

The machine-readable selection manifest freezes the Event Instance, Event
Window, Instrument Projection, Market State dependency and the Event State
record identity/fingerprint already validated by historical physical evidence.

## Temporal Rule

BT-GATE-015 must never infer delivery eligibility from the event anchor alone.

```text
event_state_available_at_utc
=
max(
  event_instance_available_at_utc,
  event_window_binding_available_at_utc,
  instrument_projection_available_at_utc,
  market_state_available_at_utc
)
+
event_state_publication_latency
```

Consumer visibility requires:

```text
event_loop.clock >= event_state_available_at_utc
```

## Proven and Missing Evidence

Proven:

```text
Event Type admission
Event Instance identity
Event Window identity
Instrument Projection identity with restrictions
exact Market State dependency identity and fingerprint
Event State record identity and fingerprint
candidate file hash
physical schema/fingerprint validation
```

Not yet proven:

```text
event_state_available_at_utc
dependency-level available_at reconciliation
row-addressable Event State replay availability sidecar
```

Therefore:

```text
BT-GATE-015 contract drafting = READY
BT-GATE-015 non-physical implementation = NOT_AUTHORIZED
Event State delivery = NOT_AUTHORIZED
```

## Required Consumer Shape

The future consumer contract should separate:

```text
BoundedEventStateAvailable
├── PIT envelope
├── typed Event State payload
└── audit lineage
```

Event State must be stored separately from MarketData and MarketState. It must
not become an execution or valuation price.

## Next Provider Gate

```text
event_state_session_opened_replay_availability_evidence_sidecar_v0_1
```

That gate must derive row-addressable availability evidence from governed
dependencies. It must not copy `event_anchor_timestamp_utc` into every
availability field without evidence.

## Prohibitions

```text
no physical Event State read
no Market State parquet read
no StateReplayFeed
no backtest implementation
no strategy, orders, fills or PnL
no production or downstream
no Event Type scope expansion
```
