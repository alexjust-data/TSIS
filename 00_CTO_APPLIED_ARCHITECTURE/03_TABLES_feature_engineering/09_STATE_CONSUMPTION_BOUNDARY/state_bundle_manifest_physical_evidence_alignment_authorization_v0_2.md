# StateBundle Manifest Physical Evidence Alignment Authorization v0.2

Gate: `state_bundle_manifest_physical_evidence_alignment_v0_2`
Date: `2026-07-30`
Status: `AUTHORIZED_READ_ONLY_METADATA_NO_PHYSICAL_READ`

## Purpose

Align the accepted provider v0.1.2 request, response and `StateBundleManifest`
with the exact Market State scale-validation candidate, its 120-context ledger,
104-row replay-availability sidecar and governed metadata hash chain.

This gate may read JSON, Markdown and Python validation logic. It identifies the
candidate parquet and consumes its previously governed SHA-256, but it must not
open or hash the parquet, read state rows, emit replay records or execute a
backtest.

## Hard Boundaries

```text
parquet_opened = false
parquet_hash_recomputed = false
physical_state_rows_read = 0
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
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```
