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
