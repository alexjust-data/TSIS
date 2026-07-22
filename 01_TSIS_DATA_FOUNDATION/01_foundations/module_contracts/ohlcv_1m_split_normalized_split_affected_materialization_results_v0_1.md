# Ohlcv 1m Split-Normalized Split-Affected Materialization Results `v0_1`

## 1. Role

This document records the completed split-affected materialization run for the
candidate full-universe logical `1m_split_normalized` view.

It does not promote the output root as an official production source.

It records that the Path A1 candidate described in
`ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md` has
been physically materialized and audited.

## 2. Run Identity

```text
run_id: split_affected_20260627_192314
mode: split-affected
finished_at: 2026-06-27T21:56:23.0470395+02:00
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314
manifest: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314/manifest_split_affected.csv
summary: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314/_run_summary.json
output_root: E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
audit_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314/full_universe_split_event_audit
```

## 3. Materialization Result

```text
manifest_rows: 115667
chunk_count: 24
output_files_present: 115667
tickers_in_manifest: 1589
scan_strategy: split_tickers_then_partition_direct
files_seen: 202993
files_in_year_window: 202993
files_without_split_effect: 87326
split_tickers_seen: 4824
split_tickers_without_minute_dir: 0
```

Interpretation:

- the output was materialized for ticker-months where a future split changes
  the scale;
- the run did not physically duplicate ticker-months with no split effect;
- this is a logical full-universe split-safe candidate, not a physical full copy.

## 4. Audit Result

The run executed the full-universe split-event audit after materialization.

This audit must be read as the same semantic audit family already documented
under `01_foundations/inspection_dossiers/1m_split_normalized/`, not as a new
discovery that the split-normalization logic was uncertain. The semantic
meaning was already defended there: all fully auditable split cases passed, and
coverage-limited cases were explicitly classified instead of being hidden.

What is new in this run is the physical materialization of the wider
split-affected candidate root:

```text
E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
```

The post-run audit confirms that the materialized candidate remains consistent
with the established split-normalization audit: `FAIL = 0`.

```text
split_files_seen: 4824
non_empty_split_files_with_1m_ticker: 1876
total_event_cases: 3335
PASS: 2280
FAIL: 0
NO_PRE_COVERAGE: 164
NO_POST_COVERAGE: 151
NO_1M_COVERAGE: 740
```

Status summary:

```text
PASS: 68.365817%
FAIL: 0.000000%
NO_PRE_COVERAGE: 4.917541%
NO_POST_COVERAGE: 4.527736%
NO_1M_COVERAGE: 22.188906%
```

Interpretation:

- `PASS` means the case had sufficient bilateral coverage and no invariant
  violation was observed;
- `NO_PRE_COVERAGE`, `NO_POST_COVERAGE` and `NO_1M_COVERAGE` are coverage
  limits, not semantic failures;
- `FAIL = 0` is the key audit result.

## 4.1 How To Read Coverage States

The `NO_*_COVERAGE` statuses are not errors in the split-normalization
algorithm. They are honest declarations about the empirical coverage available
in `1m_raw` for a given split event.

`NO_PRE_COVERAGE` means:

```text
The split exists, but there is not enough loadable 1m history before the event
to test the pre-split side of the invariant.
```

`NO_POST_COVERAGE` means:

```text
The split exists, but there is not enough loadable 1m history after the event
to test the post-split side of the invariant.
```

`NO_1M_COVERAGE` means:

```text
The split exists in corporate_actions/splits, but the raw 1m dataset does not
provide loadable 1m coverage for that ticker/event.
```

Therefore the institutional reading is:

```text
All fully auditable cases pass. Coverage-limited cases are classified as limits
of the raw 1m evidence, not as split-normalization failures.
```

The difference between the existing `01_foundations` audit and this completed
run is:

```text
Existing audit:
  proved the split-normalization semantics over all auditable split events.

This run:
  materialized the wider split-affected candidate root and confirmed again that
  the post-materialization audit has FAIL = 0.
```

## 5. Institutional Status

```text
status: materialized_audited_candidate
promotion_state: pending_promotion_gate
source_of_truth: no
official_backtest_ml_source: not yet
execution_truth: no
raw_1m_replacement: no
```

This root may be used for:

- promotion review;
- controlled downstream integration tests;
- table-builder development with explicit candidate lineage;
- validating split-safe fallback logic for non-affected ticker-months.

It must not be used silently as:

- the official `ohlcv_1m_split_normalized_v0_1` root;
- a replacement for `1m_raw`;
- a full physical copy claim;
- an execution-price truth source;
- a production ML/RL feature root without a downstream contract update.

## 6. Promotion Gate

Promotion still requires:

- registry decision for whether the candidate root replaces, complements or
  remains separate from `E:/TSIS/data/ohlcv_1m_split_normalized`;
- consumer policy update for official fallback semantics;
- validators or tests parameterized against the candidate root;
- downstream table contracts updated where this root is consumed;
- Graphify refresh of the affected Data Foundation price-view slice;
- explicit changelog entry and promotion wording.

Until that gate is closed, the correct wording is:

```text
The split-affected full-universe logical candidate was materialized and audited
with zero observed split invariant failures, but it is not yet a promoted
production source.
```
