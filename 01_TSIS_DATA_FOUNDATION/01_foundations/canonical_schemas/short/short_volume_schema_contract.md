# Short Volume Schema Contract

Status: canonical schema contract for short volume data.

## Purpose

This contract defines the physical and logical schema for daily short sale volume observations used by module 01.

Short volume is daily short-sale activity/pressure evidence. It is not full consolidated market volume, and FINRA official/free data does not provide a complete 2005-2026 history.

## Active Roots

Current operational root:

`E:\TSIS\data\short\short_volume`

FINRA review/reference root:

`E:\TSIS\data\short_review\finra_short\normalized\short_volume`

FINRA aggregate artifact:

`E:\TSIS\data\short_review\finra_short\artifacts\short_volume_all_daily_finra.parquet`

## Physical Layout

Observed per-ticker pattern:

`<ROOT>\<TICKER>.parquet`

Examples:

- `E:\TSIS\data\short\short_volume\AAME.parquet`
- `E:\TSIS\data\short_review\finra_short\normalized\short_volume\AAME.parquet`

## Canonical Columns

Core columns:

| Column | Logical role | Type expectation |
|---|---|---|
| `ticker` | reported ticker | string |
| `date` | trading/report date | date |
| `total_volume` | total reported volume in source scope | numeric |
| `short_volume` | reported short sale volume | numeric |
| `exempt_volume` | short exempt volume | numeric |
| `non_exempt_volume` | short volume excluding exempt volume | numeric |
| `short_volume_ratio` | short volume as percentage/ratio of total volume | numeric |

Venue breakdown columns observed in local and FINRA layers:

- `nyse_short_volume`
- `nyse_short_volume_exempt`
- `nasdaq_carteret_short_volume`
- `nasdaq_carteret_short_volume_exempt`
- `nasdaq_chicago_short_volume`
- `nasdaq_chicago_short_volume_exempt`
- `adf_short_volume`
- `adf_short_volume_exempt`

Additional FINRA-normalized columns:

- `orf_short_volume`
- `orf_short_volume_exempt`

## Canonical Key

`ticker + date`

Duplicate keys must not be silently collapsed without source/revision policy.

## Coverage Evidence

Polygon/local short refresh:

- universe: 4824 `<1B>` tickers
- files present: 4824
- rows total: 1430506
- download tasks: 4824
- errors: 0
- observed local example range for `AAME`: `2024-02-06` to `2026-04-02`

FINRA parallel build:

- rows: 4689038
- tickers: 4623
- date range: `2018-08-01` to `2026-04-29`

The FINRA layer extends the observed local short-volume history materially but still does not close 2005-2018 under official/free constraints.

## Required Consumer Rules

- Do not treat short volume as complete consolidated exchange + off-exchange market short volume.
- Preserve source scope and venue-breakdown semantics.
- Use FINRA as official/free baseline for 2018-08-01+ review work.
- Do not claim 2005-2026 full-history short-volume completeness without paid/additional source evidence.
- Apply ticker reuse/reference conflict certification before model consumption.

## Verdict

Short volume has a coherent schema but two active semantic planes: local operational data and FINRA official/free review baseline. FINRA is stronger for modern history; neither layer certifies complete 2005-2026 coverage.
