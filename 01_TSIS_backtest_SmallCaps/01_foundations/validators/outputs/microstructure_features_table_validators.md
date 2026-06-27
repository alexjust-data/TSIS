# Microstructure Features Table Validators `v0_1`

## Scope

Validators for:

```text
microstructure_features_table_v0_1
```

Physical root:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table
```

## Required Artifacts

Must exist:

- parquet dataset: `microstructure_features_table_v0_1/`
- manifest: `_microstructure_features_table_manifest_v0_1.json`
- summary: `_microstructure_features_table_summary_v0_1.csv`
- seed windows CSV
- schema contract
- dataset contract
- consumption policy
- registry entry

## Structural Validators

Hard fail if:

- row count is zero;
- duplicate `event_window_id + ticker + window_start_utc + window_end_utc`;
- `materialization_scope` is not `seed_event_window_smoke` for v0.1;
- any row has `full_universe_claim = true`;
- any row has `execution_sim_candidate = true`;
- any row has `backtest_core_microstructure_candidate = true`;
- output tree hash does not match the manifest;
- source windows CSV hash does not match the manifest;
- contract paths referenced in the manifest do not exist.

## Source Reconciliation Validators

Hard fail if:

- a present source quotes file has no SHA-256;
- a present source trades file has no SHA-256;
- source quotes file hash in the row differs from the physical file;
- source trades file hash in the row differs from the physical file;
- row quotes count differs from recomputing the source file over the event
  window;
- row trades count differs from recomputing the source file over the event
  window.

## Quality Validators

Hard fail if:

- `hard_fail_count > 0` in the current v0.1 seed;
- `instrument_identity_temporal_match = false` for the current seed row;
- `event_research_microstructure_candidate = false` for the current seed row;
- any invalid trade price or size rows appear without a review quality state.

Review condition:

- non-zero quote crossed ratio;
- non-zero exact duplicate trade ratio;
- high odd-lot ratio;
- provisional `D:/quotes` lineage.

These are not structural failures in v0.1, but they must remain visible.

## Test Implementation

Current automated implementation:

```text
tests/data_foundation_outputs/test_microstructure_features_table_contract.py
```

Evidence root:

```text
C:/TSIS_Data/tests/test_runs/<date>/<run_id>/
```

## Final Rule

The validator must protect against the main failure mode:

```text
a one-window seed table being mistaken for full-universe quote/trade
microstructure coverage
```
