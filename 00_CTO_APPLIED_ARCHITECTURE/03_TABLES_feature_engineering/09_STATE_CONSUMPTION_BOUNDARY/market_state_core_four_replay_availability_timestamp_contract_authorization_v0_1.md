# Market State Core Four Replay Availability Timestamp Contract v0.1 - Authorization

Gate: `market_state_core_four_replay_availability_timestamp_contract_v0_1`
Date: `2026-07-29`
Status: `AUTHORIZED_CONTRACT_ONLY_NO_PHYSICAL_READ`

## Purpose

Authorize a narrow shared-boundary contract that defines replay-safe temporal evidence for `market_state_core_four_intraday_profile_v0_1` before any future StateBundle read or replay authorization can reopen.

The previous physical evidence alignment blocked because the existing evidence did not prove:

```text
state_as_of_utc
state_available_at_utc
```

and replay delivery must be governed by:

```text
event_loop.clock >= state_available_at_utc
```

not by `decision_timestamp_utc` alone.

## Authorized Outputs

```text
market_state_core_four_replay_availability_timestamp_contract_authorization_v0_1.md
configs/market_state_core_four_replay_availability_timestamp_contract_scope_v0_1.json
market_state_core_four_replay_availability_timestamp_contract_v0_1.md
market_state_core_four_replay_availability_timestamp_contract_v0_1.json
market_state_core_four_replay_availability_timestamp_contract_matrix_v0_1.json
market_state_core_four_replay_availability_timestamp_contract_readout_v0_1.md
scripts/market_state_core_four_replay_availability_timestamp_contract_runner_v0_1.py
```

## Hard Boundaries

```text
physical_artifacts_opened = 0
parquet_opened = false
parquet_hash_recomputed = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```

## Non-Authority

This authorization does not update the physical candidate, reissue a runtime response, open a bundle, read parquet rows, execute `StateReplayFeed`, run a backtest, add Liquidity, add Event State, add Event Types, or promote any dataset.
