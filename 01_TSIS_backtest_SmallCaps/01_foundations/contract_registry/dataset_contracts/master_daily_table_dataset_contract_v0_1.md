# Master Daily Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: master_daily_table_v0_1
family: data_foundation_outputs
class: analytical master table
grain: instrument_id + ticker + session_date + price_view
```

## 2. Purpose

`master_daily_table` provides the governed daily context surface for event
research, daily backtests and downstream CAPA 1 consumers.

It answers:

```text
For this instrument, session and price view, what daily bar/context is available
and what quality/evidence gate applies?
```

It does not answer intraday execution, quote book state or trade tape quality.

## 3. Source Lineage

Authoritative inputs v0.1:

- `expected_data_calendar_v0_1`
- `corporate_actions_table_v0_1`
- `dataset_certification_matrix_v0_1`
- `E:/TSIS/data/ohlcv_daily`
- `E:/TSIS/data/ohlcv_daily_adjusted`

## 4. Price Semantics

`daily_raw`:

```text
observed raw daily OHLCV
```

`split_normalized`:

```text
daily OHLC after split-normalization, with raw volume preserved
```

`adjusted`:

```text
daily OHLC adjusted for economic continuity, with raw volume preserved
```

`adjusted_proxy` fields are preserved only as diagnostic lineage fields. They
are not a core `price_view` in v0.1.

## 5. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/master_daily_table/
  master_daily_table_v0_1/
  _master_daily_table_summary_v0_1.csv
  _master_daily_table_manifest_v0_1.json
```

Partitioning:

```text
year/price_view
```

## 6. Current Materialization

```text
build_run_id: master_daily_table_v0_1_20260622T161747Z
rows: 21771864
expected_daily_rows: 7257288
price_views: daily_raw, split_normalized, adjusted
rows_per_price_view: 7257288
data_present_rows: 19782153
missing_expected_data_rows: 1989711
selected_price_hard_invalid_rows: 0
negative_volume_rows: 0
backtest_core_row_candidate_rows: 19782153
rows_with_corporate_action: 92979
parquet_file_count: 63
output_tree_sha256: 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e
hard_fail_count: 0
```

Rows by price view:

```text
daily_raw:
  rows: 7257288
  present_rows: 6594051
  missing_rows: 663237
  hard_invalid_rows: 0

split_normalized:
  rows: 7257288
  present_rows: 6594051
  missing_rows: 663237
  hard_invalid_rows: 0

adjusted:
  rows: 7257288
  present_rows: 6594051
  missing_rows: 663237
  hard_invalid_rows: 0
```

## 7. Allowed Consumers

Permitted:

- `event_engine`
- `outcome_research`
- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `research_only`
- `forensic_only`

Condition:

```text
Consumers must select the correct price_view and preserve row-level flags.
```

Restricted:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 8. Quality Policy

Structural pass requires:

- one row per expected daily session and price view;
- no duplicate `ticker + session_date + price_view`;
- three price views present;
- source build ids preserved;
- family-level quality gates linked;
- row-level price-integrity flags emitted.

`backtest_core_row_candidate` requires:

- data is present;
- selected OHLC is positive and internally coherent;
- volume is not negative;
- family gate is `declared_scope_allowed`.

## 9. Known Limitations

- v0.1 does not join full daily row-level audit labels.
- v0.1 does not include fundamentals, news, short, halts or regime fields.
- v0.1 uses expected coverage as denominator, so missing expected rows are preserved.
- v0.1 does not compute adjusted VWAP.
- v0.1 is not an execution or microstructure table.

## 10. Change Policy

Version bump required when:

- grain changes;
- price views change;
- row-level quality semantics change;
- additional context families are joined;
- adjusted VWAP semantics are introduced;
- output layout changes;
- consumers are materially expanded.

