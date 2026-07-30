# Bounded StateBundle Read and Replay Authorization v0.2

Gate: `bounded_state_bundle_read_and_replay_authorization_v0_2`
Date: `2026-07-30`
Status: `CLOSED_AUTHORIZED_ONE_BOUNDED_MARKET_STATE_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS_NO_EXECUTION`

## Authority

This gate supersedes `v0.1` only for active navigation. The blocked `v0.1`
authorization remains historical evidence and is not modified.

Physical evidence alignment v0.2 proved that one accepted provider v0.1.2
bundle identifies the exact restricted scale-validation candidate and its
row-addressable replay-availability evidence.

This gate therefore authorizes one later execution gate. It does not perform
the physical read or replay itself.

## Exact Probe

```text
consumer_id = bounded_market_state_replay_integration_probe_v0_1
consumption_purpose = integration_validation_only
state_kind = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
instrument_id = cik_ticker:0001651625:ACIU
ticker = ACIU
session_date = 2021-03-15
authorized rows = 2
maximum rows = 2
maximum physical data files = 1
maximum files = 9
```

The two permitted row identities and fingerprints are frozen in:

```text
bounded_state_bundle_read_and_replay_selection_manifest_v0_2.json
```

No other row may be delivered, even if it belongs to the same candidate
dataset.

## Temporal Rule

The future bounded probe must deliver a record only when:

```text
EventLoop.clock >= state_available_at_utc
```

It must not use `decision_timestamp_utc` alone as delivery authority.

## Authorized Future Behavior

The execution gate may:

```text
verify the frozen metadata and physical hashes;
open the one exact candidate parquet;
select exactly the two authorized row identities;
validate schema and row fingerprints;
join exactly one sidecar record per row;
order records canonically by state_available_at_utc;
emit only bounded integration-probe records to a test EventLoop.
```

## Prohibited

```text
Event State
arbitrary or user-supplied paths
unlisted rows
scope expansion
strategy callbacks
signals
orders
fills
PnL
Market State as execution price
dataset or registry mutation
official dataset promotion
production
downstream
general backtest consumption
```

The bounded probe adapter is not general `StateReplayFeed` authority.

## Gate Counters

```text
authorization_to_read_issued = true
bounded_execution_authorized = true
parquet_opened = false
parquet_hash_recomputed = false
physical_state_rows_read = 0
bounded_probe_records_emitted = 0
general_StateReplayFeed_authorized = false
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```

## Next Gate

```text
bounded_state_bundle_read_and_replay_execution_v0_1
```
