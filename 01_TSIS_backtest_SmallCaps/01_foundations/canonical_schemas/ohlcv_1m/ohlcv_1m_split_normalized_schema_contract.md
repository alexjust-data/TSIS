# OHLCV 1m Split-Normalized Schema Contract

Status: canonical physical schema contract for `E:\TSIS\data\ohlcv_1m_split_normalized`.

## Purpose

`ohlcv_1m_split_normalized` is a derived intraday minute-bar view that preserves raw intraday bar semantics while re-expressing price columns on a split-normalized scale.

It is not:

- a dividend-adjusted economic return layer
- an execution truth layer
- a substitute for raw quotes or trades
- a full-universe materialization

## Physical Layout

Observed root:

`E:\TSIS\data\ohlcv_1m_split_normalized`

Observed pattern:

`ticker=<TICKER>\year=<YYYY>\month=<MM>\minute_aggs_<TICKER>_<YYYY>_<MM>_split_normalized.parquet`

Observed pilot summary:

`E:\TSIS\data\ohlcv_1m_split_normalized\_split_normalized_materialization_summary.csv`

Observed pilot file count: 10 parquet files.

## Canonical Columns

Raw columns preserved:

| Column | Logical role |
|---|---|
| `ticker` | ticker |
| `ts_utc` | UTC minute timestamp |
| `date` | calendar date |
| `year` | calendar year |
| `month` | calendar month |
| `o` | raw minute open |
| `h` | raw minute high |
| `l` | raw minute low |
| `c` | raw minute close |
| `v` | raw minute volume |
| `vw` | raw minute VWAP |
| `n` | raw aggregate/trade count |
| `t` | raw timestamp epoch from source |

Derived split-normalized columns:

| Column | Logical role |
|---|---|
| `future_split_factor` | product of split ratios with execution_date greater than observation date |
| `o_split_normalized` | open re-expressed by future split factor |
| `h_split_normalized` | high re-expressed by future split factor |
| `l_split_normalized` | low re-expressed by future split factor |
| `c_split_normalized` | close re-expressed by future split factor |
| `vw_split_normalized` | VWAP re-expressed by future split factor |
| `materialized_price_view` | expected `1m_split_normalized_v0_1` |
| `source_1m_file` | source raw 1m parquet |
| `source_splits_file` | source splits parquet |

Pilot/provenance columns:

| Column | Logical role |
|---|---|
| `pilot_role` | pilot role: reverse_split, forward_split, control |
| `pilot_event_type` | event type used by pilot |
| `pilot_event_date` | split event date where applicable |

## Canonical Key

`ticker + ts_utc`

The physical partition key is:

`ticker + year + month`

## Transformation Rule

For every price-like raw field:

`px_split_normalized = px_raw * future_split_factor`

where:

`future_split_factor(date_t) = product(split_ratio for execution_date > date_t)`

The event date itself is not considered "future" for observations on that date.

## Pilot Coverage

Observed pilot cases:

| Ticker | Month | Role | Event date | Rows | Non-1 factor rows |
|---|---|---|---|---:|---:|
| `BXRX` | 2022-12 | reverse_split | 2022-12-01 | 7424 | 0 |
| `COSM` | 2022-12 | reverse_split | 2022-12-16 | 16986 | 9929 |
| `CEI` | 2022-12 | reverse_split | 2022-12-21 | 15660 | 10956 |
| `BNGO` | 2025-01 | reverse_split | 2025-01-27 | 10560 | 9256 |
| `EFSH` | 2025-01 | forward_split | 2025-01-10 | 6328 | 2430 |
| `SAVA` | 2023-12 | forward_split | 2023-12-21 | 7760 | 5393 |
| `PD` | 2006-03 | forward_split | 2006-03-13 | 9345 | 3200 |
| `LIVE` | 2014-02 | forward_split | 2014-02-12 | 7038 | 7038 |
| `BXRX` | 2022-11 | control pre-event | none | 3801 | 3801 |
| `BNGO` | 2025-02 | control post-event | none | 2724 | 0 |

## Required Consumer Rules

- Do not treat this as full-universe data.
- Do not use it as local execution truth when raw observed prices are required.
- Use it for cross-session comparability around split boundaries.
- Preserve `materialized_price_view` and source file columns for provenance.
- A control month can have `future_split_factor != 1` if it is before a future split.

## Verdict

The physical pilot schema is coherent and matches the split-normalized dataset contract. The layer is pilot-materialized and semantically validated, but not full-universe promoted.
