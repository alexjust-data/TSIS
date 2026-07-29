# 06 STATE REPLAY FEED IMPLEMENTATION PLAN V0.1

Status: PROPOSED_CONSUMER_CONTRACT_NOT_IMPLEMENTED
Date: 2026-07-28
Scope: deterministic delivery of authorized `Market State` and `Event State` into the backtest event loop.

This document is a local implementation plan.

Current gate:

```text
provider portable strict hardening = pending
provider/consumer compatibility = not validated
backtest state consumption = not authorized
StateReplayFeed implementation against the real provider = blocked
```

The architectural authority belongs to:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/04_STATE.md
```

## 1. Objective

Implement `StateReplayFeed` so the backtest can consume authorized states without:

```text
reading state paths from user config
joining state tables inside a strategy
rebuilding state features
delivering state before it is legally available
delivering research-only Event State to a decision
using a state field as a fill price
```

The runtime chain is:

```text
BacktestInputManifest
├── HistoricalReplayFeed
└── StateReplayFeed
        ↓
EventLoop
        ↓
Decision / Strategy
```

## 2. Preconditions

`StateReplayFeed` may open only when:

```text
BacktestInputManifest validates
preflight_status = BACKTEST_INPUTS_PASS
StateBundleManifest identity and SHA-256 match
all provider contract identities, versions and SHA-256 match
EffectiveCapabilityView identity and SHA-256 match
exactly one StateResolutionRequest and RuntimeInvocationResponse binding exists per requested state_kind
request IDs and request fingerprints are unique
request/fingerprint/response correspondence is complete
the single aggregated StateBundleManifest covers all and only the requested state kinds
partial provider success is absent
a separate authorization artifact explicitly authorizes purpose = backtest
all requested state datasets are official
all requested state datasets are downstream-authorized
backtest consumption is authorized
coverage policy is satisfied
all required artifact hashes verify
provider/consumer compatibility has a closed PASS gate
```

If the run does not request state:

```text
StateReplayFeed is not instantiated
```

## 3. Files To Create Or Extend

```text
src/tsis_backtest/replay/
├── state_contracts.py
├── state_feed.py
├── event_ordering.py
└── historical_feed.py

src/tsis_backtest/mechanics/
└── event_loop.py

tests/unit/
├── test_state_replay_feed.py
└── test_combined_event_ordering.py
```

The existing `HistoricalReplayFeed` remains the source of observable market facts and the execution clock.

## 4. Minimum Event Contracts

```text
MarketStateAvailableEvent
EventStateAvailableEvent
```

Minimum common fields:

```text
event_type
event_id
state_kind
ticker or instrument_id
session_date
decision_timestamp
state_available_at
event_priority
profile_id
representation_version
state_dataset_id
state_row_id
state_payload
quality_flags
causal_parent_refs
```

Additional `EventStateAvailableEvent` fields:

```text
event_id represented
event_timestamp
event_detected_at
event_available_at
state_role
consumption_legality
```

The payload must contain only the fields authorized by `BacktestInputManifest`.

## 5. Time Semantics

The feed must preserve:

```text
decision_timestamp
=
time represented by the state
```

```text
state_available_at
=
first time the state can legally be known
```

The strategy may receive a state only when:

```text
state_available_at <= event_loop.clock
```

For every delivered state:

```text
feature_input_max_available_at <= event_loop.clock
future_window_used = false
outcome_dependency = false
```

For Event State:

```text
max(
    event_detected_at,
    event_available_at,
    state_available_at
) <= event_loop.clock
```

## 6. Deterministic Causal Order

The combined event stream must not sort only by timestamp.

Minimum priority:

```text
1. ReplayGapEvent
2. ReplayBarEvent
3. MarketStateAvailableEvent
4. EventStateAvailableEvent
5. ScheduledDecision
6. Order / Fill
7. Position / Ledger update
```

The stable ordering key should include:

```text
available_at
event_priority
ticker or instrument_id
stable_source_sequence
event_id
```

The exact priority values must live in one shared registry or enum.

They must not be independently encoded in multiple feeds.

Critical invariant:

```text
If BAR and MARKET_STATE share available_at:

BAR is processed first
MARKET_STATE is processed second
SCHEDULED_DECISION is processed after both
```

`causal_parent_refs` must permit a state event to identify the source facts or prior state artifacts on which it depends.

## 7. Market State Delivery

A `MarketStateAvailableEvent` may be emitted only if:

```text
state_kind = market_state
profile_id matches the manifest
representation_version matches the manifest
field set is a subset of the authorized fields
validation_status = PASS
consumption authorization includes backtest
official_dataset = true
downstream_authorized = true
state_available_at is present
temporal legality checks pass
```

The feed must not expose:

```text
unrequested fields
unrequested partitions
physical storage paths
provider-derived fields not admitted by TSIS
future-derived values
```

## 8. Event State Delivery

An `EventStateAvailableEvent` may be emitted to the decision stream only if:

```text
state_kind = event_state
consumption_legality = decision_safe
state_role is compatible with the requested profile
event detection is legally available
all common temporal checks pass
```

The following values must be blocked from the decision stream:

```text
research_only
outcome_adjacent
prohibited_as_input
```

They may be processed by a separate research/outcome pipeline in the future.

They are not inputs to the strategy event loop.

## 9. Strategy Interface

The strategy receives:

```text
authorized market facts
authorized state payloads
current event-loop clock
```

The strategy does not receive:

```text
StateBundleManifest internals
registry paths
artifact locations
authorization logic
feature builder access
research-only state rows
```

State access should be read-only and scoped by:

```text
instrument
profile
representation version
latest legal availability
```

## 10. Separation From Execution

State is a decision input.

It is not an execution-price source.

Prohibited:

```text
fill_price = market_state.close
```

Required:

```text
Decision
↓
Order
↓
ExecutionModel
↓
HistoricalReplayFeed price view
↓
Fill
```

Even when a state value equals a replay value numerically, their institutional roles remain different.

## 11. Gaps, Missing Rows And Duplicates

State replay must fail or emit an explicit governed event according to policy.

It must never silently:

```text
forward-fill a missing state
reuse a later state
select one duplicate arbitrarily
change state resolution
broaden coverage
drop a restriction
```

Minimum outcomes:

```text
STATE_ROW_DUPLICATE
STATE_ROW_ORDER_INVALID
STATE_REQUIRED_CONTEXT_MISSING
STATE_REQUIRED_FIELD_MISSING
STATE_ARTIFACT_HASH_MISMATCH
STATE_CAUSAL_PARENT_UNRESOLVED
STATE_AVAILABLE_AT_MISSING
STATE_TEMPORAL_LEAKAGE_DETECTED
EVENT_STATE_NOT_DECISION_SAFE
```

Coverage behavior must match the `coverage_policy` sealed by preflight.

## 12. Hash And Identity Verification

Before reading state rows:

```text
verify BacktestInputManifest hash chain
verify StateBundleManifest SHA-256
verify every provider contract SHA-256
verify every StateResolutionRequest and RuntimeInvocationResponse SHA-256
verify EffectiveCapabilityView SHA-256
verify separate backtest-authorization artifact SHA-256
verify referenced artifact hashes
verify feature-lineage manifest SHA-256
verify state data artifact and state schema artifact SHA-256
verify dataset/profile/version identity
verify request/fingerprint/response/dataset correspondence
```

Hash verification cannot be disabled by run configuration.

Any drift fails closed before the first state event is emitted.

## 13. Tests

Minimum unit tests:

```text
feed cannot open without BacktestInputManifest
feed cannot open when manifest status is not PASS
feed cannot open on bundle hash drift
feed cannot open on any provider contract hash drift
feed cannot open on request or response hash drift
feed cannot open on EffectiveCapabilityView hash drift
feed cannot open without separate backtest authorization
feed cannot open when compatibility gate is not PASS
feed cannot open on duplicate request ID or fingerprint
feed cannot open on missing request/response correspondence
feed cannot open when aggregated bundle omits or adds a request
feed cannot open on partial success
feed cannot open for unofficial state dataset
feed cannot open when downstream authorization is false
only requested fields enter payload
state is invisible before state_available_at
state becomes visible at state_available_at
BAR precedes MARKET_STATE at equal available_at
MARKET_STATE precedes EVENT_STATE at equal available_at
state events precede ScheduledDecision at equal available_at
ordering is deterministic across repeated runs
duplicate state row fails closed
missing available_at fails closed
future input dependency fails closed
research_only Event State never reaches strategy
decision_safe Event State reaches strategy only after detection
state value cannot bypass ExecutionModel as fill price
data-only run does not instantiate StateReplayFeed
```

First bounded integration test:

```text
1 symbol
1 session
1 Market State profile
1 authorized state field
Event State absent
1 ScheduledDecision
1 Order → Fill → Position path
```

Second bounded integration test:

```text
1 decision_safe Event State row
1 research_only Event State row
```

Expected:

```text
decision_safe -> delivered after all temporal checks
research_only -> blocked from decision delivery
```

## 14. Outputs

Minimum run evidence:

```text
runs/<run_id>/
├── backtest_input_manifest.json
├── state_replay_summary.json
└── state_replay_event_sample.json
```

`state_replay_summary.json` should include:

```text
run_id
state_bundle_manifest_sha256
effective_capability_view_sha256
backtest_authorization_sha256
provider_contract_set_sha256
request_binding_count
market_state_event_count
event_state_event_count
blocked_research_only_count
first_state_available_at
last_state_available_at
event_sequence_sha256
warning_codes
```

## 15. Done Criteria

Implementation is closed when:

```text
only a valid BacktestInputManifest can open the feed
all referenced hashes are verified
combined causal ordering is deterministic
state availability is enforced against event_loop.clock
Event State legality is enforced
payload fields are manifest-scoped
execution remains separated from state
all unit tests pass
bounded integration test passes
AGENTS.md and CHANGELOG.md are updated
```

This cannot be marked as a real provider integration until:

```text
provider v0.1 contracts are frozen
provider schemas compile under portable strict Draft 2020-12 validation
provider adversarial fail-closed matrix passes
all provider protocol hashes are reproducible
provider/consumer compatibility review = PASS
one official state dataset exists
downstream backtest authorization is true
one real StateBundleManifest is available
```

## 16. Explicit Non-Claims

This plan does not claim:

```text
State Runtime production readiness
official state availability
full-history state replay scalability
execution realism
broker-cost realism
short tradability
strategy edge
full 2005-2026 readiness
```
