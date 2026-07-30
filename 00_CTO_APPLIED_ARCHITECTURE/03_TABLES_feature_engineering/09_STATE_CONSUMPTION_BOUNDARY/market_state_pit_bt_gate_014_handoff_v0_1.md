# Market State PIT Evidence Handoff to BT-GATE-014 v0.1

Status: `READY_FOR_BT_GATE_014_CONTRACT_AND_IMPLEMENTATION_NOT_PHYSICAL_EXECUTION`
Date: `2026-07-30`
Owner boundary: `09_STATE_CONSUMPTION_BOUNDARY`
Receiving owner: `BT-GATE-014`

## Accepted Provider Evidence

```text
package =
bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_20260730T080831Z.zip

SHA-256 =
8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7
```

The package proves one provider/shared-boundary physical read and temporal
envelope replay for:

```text
state_kind = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
instrument = ACIU
session = 2021-03-15
physical rows = 2
bounded envelope events = 2
```

It does not prove delivery of the 17 scientific core-four values inside a
typed backtester event.

## Schema and Runtime Content Authority

The receiving consumer must apply:

```text
structural schema authority =
PHYSICAL_SCHEMA_CONTRACT.json
SHA-256 595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b

profile provenance parquet reference =
b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2

current bounded runtime content authority =
bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
```

The provenance hash and current runtime hash are not interchangeable. The
machine-readable authority is:

```text
market_state_core_four_scale_validation_physical_schema_binding_v0_1.json
```

## Work Authorized For BT-GATE-014

```text
adopt and verify this handoff package;
design BoundedMarketStateAvailable;
define a typed core-four payload with 17 scientific values;
define audit lineage;
implement MarketStateStore separately from MarketData;
freeze equal-timestamp priority;
build tests without physical Market State reads.
```

Required equal-timestamp precedence:

```text
source bar closed and incorporated
-> Market State becomes eligible
-> Market State stored
-> bounded consumer probe may observe it
```

## Work Not Yet Authorized

```text
BT-GATE-014 physical parquet read
reuse of the consumed provider authorization
general StateReplayFeed
general backtest consumption
Event State
strategy callbacks
orders
fills
PnL
production
downstream
official dataset
```

After the consumer contract and implementation exist, the backtester owner may
request a new single-use authorization scoped to the same two exact rows.
