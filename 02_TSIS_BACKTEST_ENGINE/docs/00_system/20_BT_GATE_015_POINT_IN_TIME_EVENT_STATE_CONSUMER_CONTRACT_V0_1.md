# BT-GATE-015 - Point-in-Time Event State Consumer Contract V0.1

Status:

```text
BT-GATE-015 = NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PENDING_V0_3_PREEXECUTION_EXTERNAL_REVIEW
CONTRACT_STATUS = OWNER_APPROVED
CONTRACT_OWNER_REVIEW = PASS
BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS
BT-GATE-015_IMPLEMENTATION = ACCEPTED_NON_PHYSICAL_ONLY
IMPLEMENTATION_ACCEPTANCE = ACCEPTED_NON_PHYSICAL_ONLY
EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
SINGLE_USE_PHYSICAL_AUTHORIZATION = PREPARED_PENDING_PREEXECUTION_EXTERNAL_REVIEW
PHYSICAL_BINDING_CORRECTION = PENDING_PREEXECUTION_EXTERNAL_REVIEW
```

## 1. Capability

```text
capability_id =
POINT_IN_TIME_EVENT_STATE_CONSUMER_V0_1

bounded_profile =
event_state_core_four_intraday_profile_v0_1

bounded_event_type =
event_type:market_data:session_opened
```

The capability will prove that the accepted backtest event loop can receive,
validate, order, store and observe one bounded Event State record point in
time, without using it as MarketData, an execution price, a strategy input or
an economic claim.

Non-physical implementation is authorized and implemented pending external review. Physical Event State reads remain unauthorized.

## 2. Predecessor

The contract depends on the accepted result:

```text
BT-GATE-014 =
CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS
```

The accepted Market State consumer and its immutable evidence remain
unchanged. Event State is a distinct state kind, event envelope, store and
authorization boundary.

## 3. Adopted Provider Handoff

```text
handoff_id =
event_state_session_opened_bt_gate_015_contract_handoff_v0_1

handoff_zip =
event_state_session_opened_bt_gate_015_contract_handoff_v0_1_20260731T064518Z.zip

handoff_zip_sha256 =
b7a4783d0ab64ffaf37fbfdf2ee76dffacbe9b14cf3f059891908c87116369b2

handoff_entries = 21
manifest_artifacts = 20
physical_data_included = false
backtester_files_included = false
```

The handoff is accepted for contract drafting only. Its original selected-row
identity is retained as historical provider provenance and is not the
executable bounded identity.

The provider completion is also adopted:

```text
completion_handoff_id =
event_state_session_opened_bt_gate_015_provider_completion_v0_1

completion_handoff_zip =
event_state_session_opened_bt_gate_015_provider_completion_v0_1_20260731T071317Z.zip

completion_handoff_zip_sha256 =
3a6bf3ca04c0428a1728e1719cd6aeaea6bfaef43e12fb83939dde3cb6cb85d9

completion_handoff_entries = 33
completion_manifest_artifacts = 32
completion_validation = 52/52 PASS
completion_physical_data_included = false
completion_backtester_files_included = false
```

The completion handoff closes the temporal and typed-payload evidence
blockers. Neither handoff authorizes consumer implementation, Event State
delivery or a physical consumer read.

## 4. Frozen Acceptance Slice

```text
event_type_id =
event_type:market_data:session_opened

subject_scope =
exchange_session

profile_id =
event_state_core_four_intraday_profile_v0_1

exchange_id = XNYS
session_date = 2021-01-19
ticker = AAME
instrument_id = figi_share_class:BBG001S5N8T1
state_role = at_event

event_anchor_timestamp_utc =
2021-01-19T14:30:00Z

window_definition_id =
session_opened_at_anchor_context_v0_1

historical_window_definition_id =
event_window_definition:market_data:session_opened:at_open_v0_1

historical_window_definition_role =
HISTORICAL_PROVIDER_PROVENANCE_ONLY
```

Selection is based on operational coverage and existing governed evidence, not
profitability.

## 5. Frozen Identities

```text
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


event_state_record_id =
e71cad82e71783bbc50ebb8df1e44e2f9118dd4843c3cb4f0fbf2ee5a2a8ca76

event_state_record_fingerprint =
31f1463baf0dc8f0dba3bc130c0bb1d61092897595849df57abc6b1023853a01

market_state_dependency_dataset_fingerprint =
433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

market_state_availability_evidence_dataset_fingerprint =
516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416

market_state_cross_dataset_binding =
EXACT_ROW_ID_AND_FINGERPRINT_EQUIVALENCE
```

Missing, empty, duplicate or conflicting identities must fail closed.

The identities from the first handoff (`47102c58...`, `4ab9bda...`,
`0061ac40...`, `793fc860...`, `5bbdbfdb...`, `ab048da6...`) and its
`event_state_record_ordinal = 1` are
`HISTORICAL_PROVIDER_PROVENANCE_ONLY`. They must never select runtime content
or be asserted for the executable `e71cad...` row.

### 5.1 Physical row to sidecar join

The future bounded consumer must establish a complete 1:1 bijection before
constructing an event:

| Physical Event State field | Sidecar or consumer field |
|---|---|
| `event_state_record_fingerprint` | `event_state_record_fingerprint` |
| `state_output_fingerprint` | `market_state_state_output_fingerprint` |
| `event_state_instrument_session_projection_id` | `instrument_projection_id` |
| `consumption_legality` | `state_replay_consumption_legality` |
| parsed `restriction_codes_json` | `event_state_provenance_restriction_codes` |
| `source_market_state_value_snapshot_json` | closed 17-field scientific payload |

The exact Market State dependency fingerprint is sourced from the governed
Market State replay-availability sidecar row:

```text
Market State sidecar field = state_output_fingerprint
Event State sidecar field = market_state_state_output_fingerprint
required relation = exact equality
```

The provider completion candidate is the on-demand executable row, not the
earlier 38-field synthetic projection. Its closed physical shape contains 44
fields:

```text
41 fields governed by
event_state_bounded_execution_chain_physical_validation_scope_v0_1

+ source_market_state_candidate_dataset_fingerprint
+ market_state_dependency_request_fingerprint
+ market_state_dependency_execution_plan_fingerprint
```

Its fingerprint is:

```text
event_state_record_fingerprint =
SHA256(canonical JSON of the complete physical row,
       excluding created_at_utc and event_state_record_fingerprint)
```

Join cardinality is exactly one physical row to exactly one sidecar record.
Missing rows, orphan sidecars, duplicate keys, reused sidecars or conflicting
values fail closed.

`source_market_state_value_snapshot_json` is hashed as the exact original
UTF-8 byte sequence before parsing:

```text
source_market_state_value_snapshot_sha256 =
SHA256(original UTF-8 bytes)
```

The original bytes and hash remain audit lineage. Parsing, normalization or
re-serialization must not replace the original-byte hash.

## 6. Provider Authorities

The following authorities are adopted by exact relative path and SHA-256:

```text
PROFILE_MANIFEST.json =
77937dca78391d354a3c394c7fc3886c4042209e6a567425a301553b962997e1

EVENT_STATE_SCHEMA_CONTRACT.json =
e68be24763c4320419f7f2216a3560dc94ce36f02b293fdf2dad2ea88bba9515

event_type_registry_post_initial_admission_snapshot_v0_1.json =
f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43

bounded execution final manifest =
f403566bd4c41253b1b18a232d94a7694080e04b5dce73c98411291daca59abf

candidate manifest =
aee3e7243d82244074075d21dddf361c8dd60079c9ca6d72a04ffbb886144004

physical validation final manifest =
742694fa4c298fa8b6c590199b5c7301b0cad660499ba6f3837219795a00bc81

record fingerprint report =
2843a670038cb63f3b9e4b063384d0989ced9b52de56f778948fc0a8eb0dbd3a

binding reconciliation report =
f7ae3cbf91616e2501426dd9a117c407aa550e2ba376bc884c4b94c880127ed5

provider completion handoff =
507ce42607ea308e39a71eb66b3d5ffeceb62830c11d4677975e5bf05dd7eb16

replay availability sidecar authorization consumption =
006ca91cc04746759f623d152cee2eb5650ba1ce463412c5b11d0deca66eb859

replay availability sidecar manifest =
fded92d3f213f926cae9024a6aa31379c87e4485ac25afd51ea30ac848eec8f6

replay availability sidecar schema =
7d814dcb50fdd9b0da604e4f443497f3b733082070ccc2ed8ff89293e773ad77

typed payload binding =
320fc3e9dfb532aad0e12a48af6117d50a214642b2b827a4628265808d4d3d43

Market State replay availability sidecar =
8e426b09bb1cafac26e49c7a81de31ef4ea60ca3b56ac3aa766ba13a0772c5ac

Market State schema =
595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b
```

Absolute provider paths are inspection locations only and must not enter a
scientific hash.

## 7. Evidence Proven by the Handoff

```text
Event Type admission = PROVEN
Event Instance identity = PROVEN
Event Window identity = PROVEN
Instrument Projection identity = PROVEN_WITH_RESTRICTIONS
exact Market State dependency identity = PROVEN_WITH_RESTRICTIONS
Event State record identity and fingerprint = PROVEN
candidate file identity = PROVEN
physical schema/fingerprint validation = PROVEN
```

The evidence chronology is:

```text
initial contract handoff:
validation = 36/36 PASS
provider physical files opened = 0
provider physical rows read = 0

provider completion:
validation = 52/52 PASS
provider candidate files opened = 1
provider candidate rows scanned = 8
provider candidate rows selected = 1
Market State Parquet opened = false

backtester consumer:
Event State physical files opened = 0
Event State physical rows read = 0
```

The provider completion read is immutable provider evidence. It is not a
backtester consumer read and does not authorize one.

## 8. Provider Evidence Closure

Both material evidence blockers are closed by the provider completion handoff.
Contract owner review passed. The corrected non-physical implementation remains pending external review;
physical reads remain unauthorized.

### 8.1 Replay availability sidecar

```text
event_instance_available_at_utc = 2021-01-19T14:30:00Z
event_window_binding_available_at_utc = 2021-01-19T14:30:00Z
instrument_projection_available_at_utc = 2021-01-19T14:30:00Z
market_state_available_at_utc = 2021-01-19T14:30:00Z
event_state_as_of_utc = 2021-01-19T14:30:00Z
event_state_available_at_utc = 2021-01-19T14:30:00Z
event_state_publication_latency = PT0S
state_replay_consumption_legality = research_only
```

The availability sidecar is row-addressable and the delivery boundary remains
`event_loop.clock >= event_state_available_at_utc`.

### 8.2 Typed scientific payload binding

The provider schema freezes the base envelope; the executable row is the
44-field on-demand shape defined in Section 5.1. The separate
scientific payload is exactly these 17 numeric fields:

```text
price_location_structure__daily_open_price
price_location_structure__daily_prior_close
price_location_structure__intraday_bar_close_price
price_location_structure__intraday_return_vs_prior_close_ratio_as_location
price_location_structure__intraday_return_vs_session_open_ratio_as_location
price_movement__daily_gap_pct
price_movement__daily_prior_close
price_movement__intraday_bar_close_price
price_movement__intraday_return_vs_prior_close_ratio
price_movement__intraday_return_vs_session_open_ratio
trading_activity__daily_volume_20d_avg
trading_activity__intraday_bar_volume
trading_activity__intraday_session_volume_to_time
trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
volatility_range_state__intraday_high_so_far
volatility_range_state__intraday_low_so_far
volatility_range_state__intraday_range_so_far_ratio
```

The source field is `source_market_state_value_snapshot_json`. It is parsed
exactly once into a closed typed object with no additional properties. Its
original bytes and hash remain audit lineage. The other 38 Event State fields
remain envelope, context, restrictions and lineage; they are not additional
scientific indicators.
## 9. Temporal Contract

The accepted binding satisfies:

```text
base_available_at_utc =
max(
  event_instance_available_at_utc,
  event_window_binding_available_at_utc,
  instrument_projection_available_at_utc,
  market_state_available_at_utc
)

event_state_available_at_utc =
base_available_at_utc + event_state_publication_latency

delivery_eligible =
event_loop.clock >= event_state_available_at_utc
```

Additional invariants:

```text
event_anchor_timestamp_utc <= event_state_as_of_utc
event_state_as_of_utc <= event_state_available_at_utc
each dependency available_at_utc <= event_state_available_at_utc
```

Every timestamp must be timezone-aware UTC and serialize with suffix `Z`.

## 10. Proposed Event Type

After implementation authorization, the consumer may define an immutable:

```text
BoundedEventStateAvailable
```

Required envelope categories:

```text
event_type and state_kind
profile and schema identity
Event Type identity
Event Instance identity
Event Window identity
Instrument Projection identity
Market State dependency identity and fingerprint
Event State record identity and fingerprint
instrument, exchange and session identity
event anchor, as-of and availability timestamps
publication-latency policy
replay-consumption legality and availability status
typed Event State payload
domain-labelled restrictions
audit lineage
```

It must not inherit from or masquerade as:

```text
ReplayBarEvent
ReplayGapEvent
BoundedMarketStateAvailable
MarketDataBar1m
execution order
fill
```

## 11. Proposed Global Ordering

The draft extends the accepted state-aware order without changing existing
priorities:

```text
ReplayGapEvent priority = 0
ReplayBarEvent priority = 1
BoundedMarketStateAvailable priority = 2
BoundedEventStateAvailable priority = 3
```

Canonical key:

```text
(
  available_at_utc,
  event_type_priority,
  session_date,
  canonical_ticker,
  source_event_identity
)
```

At equal availability:

```text
BAR -> MARKET_STATE -> EVENT_STATE
```

Any unresolved total-order tie fails closed.

## 12. Proposed EventStateStore

Event State must use a dedicated store:

```text
EventStateStore != MarketData
EventStateStore != MarketStateStore
EventStateStore != HistoricalReplayFeed
EventStateStore != StateReplayFeed
EventStateStore != execution or valuation state
```

The store must accept only a typed validation receipt produced atomically by
the Event State validator. Visibility requires:

```text
validated = true
stored_at_utc <= observed_at_utc
event_state_available_at_utc <= observed_at_utc
```

Duplicate identity with identical content is rejected as duplicate. Duplicate
identity with different content is rejected as conflict.

## 13. Restriction Domains

The bounded provider sidecar materializes exactly two row-level domains:

```text
event_state_provenance_restriction_codes
replay_consumption_restriction_codes
```

The exact bounded replay-consumption restrictions are:

```text
candidate_runtime_only
no_downstream
no_production
not_official_dataset
research_only
```

Provenance restrictions remain immutable audit lineage. Replay-consumption
restrictions govern delivery and must match the frozen sidecar exactly as a
closed set: duplicates, omissions and additions fail closed.

The provider architecture describes a possible third domain:

```text
component_replay_restriction_codes
```

However, the accepted bounded sidecar does not materialize row-addressable
values for Event Instance, Event Window, Instrument Projection and Market
State components. Therefore:

```text
component_replay_restriction_codes =
NOT_MATERIALIZED_NOT_AUTHORIZED_IN_V0_1

implicit union or inference =
PROHIBITED
```

V0.1 may validate component identities, timestamps and the row-level
`research_only` legality already proven, but it must not claim component-level
restriction propagation. Introducing that capability requires a separate
provider binding and owner-approved contract correction.
## 14. Fail-Closed Conditions

At minimum:

```text
FAIL_EVENT_STATE_HANDOFF_HASH_MISMATCH
FAIL_EVENT_STATE_SCHEMA_MISMATCH
FAIL_EVENT_STATE_IDENTITY_MISMATCH
FAIL_EVENT_STATE_FINGERPRINT_MISMATCH
FAIL_EVENT_STATE_MARKET_STATE_DEPENDENCY_MISMATCH
FAIL_EVENT_STATE_TEMPORAL_EVIDENCE_MISSING
FAIL_EVENT_STATE_TEMPORAL_AVAILABILITY_VIOLATION
FAIL_EVENT_STATE_PAYLOAD_CONTRACT_MISSING
FAIL_EVENT_STATE_RESTRICTION_DOMAIN_MISMATCH
FAIL_EVENT_STATE_COMPONENT_RESTRICTIONS_NOT_AUTHORIZED
FAIL_EVENT_STATE_EARLY_STORE_INSERT
FAIL_DUPLICATE_EVENT_STATE_EVENT
FAIL_CONFLICTING_EVENT_STATE_EVENT
FAIL_EVENT_STATE_SCOPE_LEAKAGE
```

Failure must leave strategy, orders, fills and PnL untouched.

## 15. Planned Non-Physical Acceptance

After owner approval, the non-physical phase must prove using explicitly
synthetic fixtures:

```text
typed envelope validation
typed payload validation
row-to-sidecar bijection
dependency identity validation
availability formula validation
BAR -> MARKET_STATE -> EVENT_STATE ordering
EventStateStore visibility barrier
determinism across input permutations and absolute roots
strict JSON and canonical UTC serialization
zero strategy/orders/fills/PnL
zero provider or physical reads
```

Synthetic values must never be represented as provider observations.

## 16. Physical Authorization Model

No physical read is authorized by this physical reads remain unauthorized.

If the non-physical phase later passes external review, any physical Event
State consumer run requires:

```text
new consumer identity
new exact row authorization
new immutable input binding
new single-use state machine
preexecution external review
durable evidence before consumption
postexecution external review
```

Market State authorization V0.5 is consumed and cannot authorize Event State.

## 17. Acceptance Outputs

The eventual acceptance package must include:

```text
resolved input manifest
provider authority hashes
availability-sidecar validation
payload-contract validation
identity and fingerprint report
two-domain restriction report
state-aware event sequence
EventStateStore trace
bounded probe observations
positive and negative test matrix
determinism report
boundary-preservation report
final manifest
```

## 18. Explicit Exclusions

```text
general Event State consumption
other Event Types
other instruments or sessions
Event State detection or materialization
general StateReplayFeed
strategy access
orders, fills or PnL
execution or valuation prices
provider modification
upstream rebuild
production or downstream
full-history backtest
optimization or edge claims
```

## 19. Authorization Decision Required

Required current state:

```text
BT-GATE-015 = NON_PHYSICAL_IMPLEMENTATION_ACCEPTED_PENDING_V0_3_PREEXECUTION_EXTERNAL_REVIEW
CONTRACT_STATUS = OWNER_APPROVED
CONTRACT_OWNER_REVIEW = PASS
BT_GATE_015_NON_PHYSICAL_EXTERNAL_REVIEW = PASS
BT-GATE-015_IMPLEMENTATION = ACCEPTED_NON_PHYSICAL_ONLY
IMPLEMENTATION_ACCEPTANCE = ACCEPTED_NON_PHYSICAL_ONLY
EVENT_STATE_PHYSICAL_READ = NOT_AUTHORIZED
SINGLE_USE_PHYSICAL_AUTHORIZATION = NOT_AUTHORIZED
```

Owner review and non-physical external review are complete. The next required increment is a separately reviewed single-use physical authorization candidate; physical execution remains unauthorized.
Physical Event State
consumption remains a later, separately bound single-use authorization.
