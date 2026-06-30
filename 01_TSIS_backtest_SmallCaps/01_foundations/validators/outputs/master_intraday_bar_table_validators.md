# Master Intraday Bar Table Validators `v0_1`

## Scope

Validators for:

```text
master_intraday_bar_table_v0_1
```

Physical root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table
```

## Required Artifacts

Must exist:

- parquet dataset: `master_intraday_bar_table_v0_1/`
- manifest: `_master_intraday_bar_table_manifest_v0_1.json`
- summary: `_master_intraday_bar_table_summary_v0_1.csv`
- schema contract
- dataset contract
- consumption policy
- registry entry

## Structural Validators

Hard fail if:

- row count is zero;
- price views are not exactly `1m_raw` and `1m_split_normalized`;
- any duplicate `ticker + ts_utc + bar_size + price_view` exists;
- output row count differs from `source_split_normalized_bar_rows * 2`;
- `full_universe_claim` is true for any row;
- more than one `materialization_scope` exists;
- `materialization_scope` is not `scoped_split_normalized_event_cases`;
- manifest tree hash does not match the physical parquet tree.

## Price Validators

Hard fail if:

- `open`, `high`, `low` or `close` is null;
- selected OHLC is non-positive;
- `high < low`;
- `open` or `close` lies outside `[low, high]`;
- `volume < 0`;
- `selected_price_hard_invalid` is not aligned with the selected OHLC checks.

## Split-Normalized Validators

For rows where:

```text
price_view = 1m_split_normalized
```

validate:

```text
open  ~= source_raw_open  * future_split_factor
high  ~= source_raw_high  * future_split_factor
low   ~= source_raw_low   * future_split_factor
close ~= source_raw_close * future_split_factor
vwap  ~= source_raw_vwap  * future_split_factor when vwap exists
```

Floating tolerance:

```text
absolute <= 1e-6
```

## Raw View Validators

For rows where:

```text
price_view = 1m_raw
```

validate:

```text
open  = source_raw_open
high  = source_raw_high
low   = source_raw_low
close = source_raw_close
vwap  = source_raw_vwap when present
```

## Quality-Gate Validators

Hard fail if:

- `backtest_core_bar_candidate` is true in v0.1;
- `event_research_bar_candidate` is true when `raw_quality_manifest_present` is false;
- `event_research_bar_candidate` is true when selected price integrity fails;
- `vwap_consumption_allowed` is true while `vwap_consumption_state` is not
  `allowed_with_declared_vw_policy`;
- rows with blocked VWAP are not marked as `blocked_by_raw_vw_quality`.

Soft/review condition:

- LIVE 2014-02 currently has no raw quality manifest match. This must remain
  visible through `raw_quality_manifest_present = false`.

## Source Reconciliation Validators

Validate:

- source split-normalized tree hash;
- source instrument master sha256;
- source corporate actions sha256;
- source dataset certification matrix sha256;
- source raw 1m quality manifest sha256;
- output parquet tree hash.

## Test Implementation

Current automated implementation:

```text
tests/data_foundation_outputs/test_master_intraday_bar_table_contract.py
```

Evidence root:

```text
C:/TSIS_Data/tests/test_runs/<date>/<run_id>/
```

## Final Rule

The validator must protect against the main failure mode:

```text
a scoped 8-ticker split-event output being mistaken for a full-universe 1m table
```

## Quote-Guarded Candidate Preflight Validators

Planned candidate:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

Preflight validators must pass before any materialization attempt:

- candidate config exists:
  `configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json`;
- candidate contract exists:
  `01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md`;
- target path is not the v0.1 dataset path;
- `full_universe_claim=false`;
- `official_dataset_created=false`;
- current bridge repair run is marked `running_or_not_final_validated`;
- final E-root quote-guarded repair manifest is required but not assumed;
- storage model is `raw_ohlcv_1m_plus_repair_manifest_overlay`;
- `creates_full_corrected_tree=false`;
- `raw_ohlcv_1m_mutation_allowed=false`;
- `D:/quotes` lineage is marked provisional candidate-only when inherited;
- promotion blockers include final validation and human review.

Hard fail if:

```text
target_dataset_path == E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_1
full_universe_claim == true
safe_to_launch_full_materialization == true before final quote-guarded validation
creates_full_corrected_tree == true without a separate physical-tree contract
raw_ohlcv_1m_mutation_allowed == true
```

Post-materialization validators, once the candidate exists, must add:

- denominator manifest reconciliation;
- row count by price view;
- duplicate `ticker + ts_utc + bar_size + price_view` check;
- raw-vs-quote-guarded OHLC overlay check;
- VWAP invalid-status preservation;
- non-negative volume;
- no execution truth claim;
- no direct ML/RL eligibility;
- no backtest-core eligibility unless quality gates explicitly allow it.
