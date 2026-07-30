# Bounded StateBundle Read and Replay Authorization Readout v0.2

Gate: `bounded_state_bundle_read_and_replay_authorization_v0_2`
Date: `2026-07-30`
Status: `CLOSED_AUTHORIZED_ONE_BOUNDED_MARKET_STATE_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS_NO_EXECUTION`

## Result

```text
case_count = 25
failed_cases = 0
missing_required_case_ids = 0
duplicate_case_ids = 0
authorization_to_read_issued = true
bounded_execution_authorized = true
```

One later execution gate may open the exact frozen candidate parquet and
project exactly two ACIU records for session 2021-03-15. The permitted row IDs,
fingerprints and replay timestamps are frozen in the selection manifest:

```text
selection_manifest_sha256 = a12c1bf3942c655115f521d0701f237f2cd9ad1a8fcf81a5ccc5c1c726d7b937
authorized_row_count = 2
maximum_rows = 2
maximum_physical_data_files = 1
```

This authorization gate did not open the parquet, read state rows, emit replay
records or execute any backtest behavior.

## Preserved Restrictions

```text
candidate_runtime_only
official_dataset = false
production = false
downstream = false
general StateReplayFeed = NOT_AUTHORIZED
strategy callbacks = 0
signals = 0
orders = 0
fills = 0
PnL = false
```

## Next Gate

```text
bounded_state_bundle_read_and_replay_execution_v0_1
```
