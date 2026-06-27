# Master Intraday Bar Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: master_intraday_bar_table_v0_1
family: data_foundation_outputs
class: analytical master table
grain: instrument_id + ticker + ts_utc + bar_size + price_view
materialization_scope: scoped_split_normalized_event_cases
full_universe_claim: false
```

## 2. Purpose

`master_intraday_bar_table` provides a governed intraday bar surface for event
research and split-normalized 1m validation.

Important scope clarification:

```text
ohlcv_1m_split_normalized was created to prove and inspect that the 1m split
normalization method is structurally and semantically correct on representative
split cases. It was not created as a full physical normalization of every
ticker-month in the <1B> universe.
```

Therefore `master_intraday_bar_table_v0_1` is a governed evidence/sample
surface for that validated mechanism. It is useful because it makes the pilot
materialization queryable and testable, but it must not be treated as the final
intraday universe for strategy backtesting.

It answers:

```text
For this instrument, minute and price view, what intraday bar is available and
what quality/evidence gate applies?
```

It does not answer quote-book state, trade-tape execution quality or full raw
1m universe coverage.

Operationally, when a future strategy/event window needs split-safe 1m data,
the expected workflow is:

1. identify the required ticker-months or event windows;
2. run the already audited split-normalization code on those scoped inputs;
3. materialize a new governed output/scope with manifest, tests and policy;
4. never infer that the current 8-ticker sample covers the whole universe.

## 3. Source Lineage

Authoritative inputs v0.1:

- `E:/TSIS/data/ohlcv_1m_split_normalized`
- `E:/TSIS/data/ohlcv_1m`
- `instrument_master_v0_1`
- `corporate_actions_table_v0_1`
- `dataset_certification_matrix_v0_1`
- `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/minute_core_quality_manifest_v0_1.parquet`

The source row denominator is the physical `ohlcv_1m_split_normalized` scope:
10 parquet files, 8 tickers and 87,626 bars. v0.1 expands that scope into two
price views.

This denominator is a proof/inspection denominator, not a universe denominator.

## 4. Price Semantics

`1m_raw`:

```text
observed raw 1m OHLCV values preserved in the split-normalized files
```

`1m_split_normalized`:

```text
1m OHLCV values mechanically re-scaled by future split factor
```

For both views, `volume` and `transaction_count` remain raw observed values.
Direct use of `vwap` must respect `vwap_consumption_state`.

## 5. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/
  master_intraday_bar_table_v0_1/
  _master_intraday_bar_table_summary_v0_1.csv
  _master_intraday_bar_table_manifest_v0_1.json
```

Partitioning:

```text
year/month/price_view
```

## 6. Current Materialization

```text
build_run_id: master_intraday_bar_table_v0_1_20260623T155007Z
rows: 175252
source_split_normalized_bar_rows: 87626
tickers: 8
ticker_months: 10
price_views: 1m_raw, 1m_split_normalized
first_ts_utc: 2006-03-01 13:02:00+00:00
last_ts_utc: 2025-02-28 22:10:00+00:00
duplicate_key_groups: 0
selected_price_hard_invalid_rows: 0
negative_volume_rows: 0
event_research_bar_candidate_rows: 161176
backtest_core_bar_candidate_rows: 0
raw_quality_manifest_missing_rows: 14076
raw_quality_manifest_missing_ticker_months: 1
parquet_file_count: 14
output_tree_sha256: 288b5b296bfec4a629ef5cf841340d8b72ca3f00cbda7f51b9092a34b84bb79e
hard_fail_count: 0
```

Rows by price view:

```text
1m_raw:
  rows: 87626
  event_research_bar_candidate_rows: 80588
  backtest_core_bar_candidate_rows: 0
  raw_quality_manifest_missing_rows: 7038
  vwap_blocked_rows: 71243
  rows_with_corporate_action: 3787

1m_split_normalized:
  rows: 87626
  event_research_bar_candidate_rows: 80588
  backtest_core_bar_candidate_rows: 0
  raw_quality_manifest_missing_rows: 7038
  vwap_blocked_rows: 71243
  rows_with_corporate_action: 3787
```

## 7. Allowed Consumers

Permitted with scope flags:

- `event_engine`
- `outcome_research`
- `backtest_extended`
- `ml_flagged`
- `research_only`
- `forensic_only`

Restricted:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Condition:

```text
Consumers must preserve materialization_scope, full_universe_claim,
price_view, raw_allowed_consumption and vwap_consumption_state.
```

## 8. Quality Policy

Structural pass requires:

- one row per source split-normalized bar and price view;
- no duplicate `ticker + ts_utc + bar_size + price_view`;
- no selected-price hard invalid rows;
- no negative volume rows;
- no full-universe claim;
- source hashes and contract links preserved.

`event_research_bar_candidate` requires:

- selected OHLC integrity pass;
- non-negative volume;
- linked raw 1m quality manifest;
- raw allowed consumption in controlled/scoped states;
- family event consumption gate allowing scoped flags.

`backtest_core_bar_candidate` is always false in v0.1 because both source
families are `scoped_only` in `dataset_certification_matrix_v0_1`.

## 9. Known Limitations

- v0.1 is not a full-universe 1m materialization.
- v0.1 only covers ticker-months present in `ohlcv_1m_split_normalized`.
- `ohlcv_1m_split_normalized` is a validated split-normalization pilot/proof
  surface, not a precomputed normalized copy of all raw 1m ticker-months.
- LIVE 2014-02 has no matching row in the raw 1m quality manifest and is
  explicitly marked by `raw_quality_manifest_present = false`.
- Direct VWAP consumption is blocked for 71,243 rows per price view.
- v0.1 does not include quote/trade microstructure, halts, news, short data,
  fundamentals or regime context.
- v0.1 should not be used as raw execution truth.

## 10. Change Policy

Version bump required when:

- the scope expands beyond split-normalized event cases;
- a new event-window/ticker-month split-normalized materialization is promoted
  as a reusable output;
- full raw 1m is materialized;
- price views change;
- row-level quality semantics change;
- VWAP policy changes;
- event/backtest eligibility semantics change;
- output layout changes;
- consumers are materially expanded.
