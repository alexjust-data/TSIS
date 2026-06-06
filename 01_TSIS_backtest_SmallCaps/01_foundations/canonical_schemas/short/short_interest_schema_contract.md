# Short Interest Schema Contract

Status: canonical schema contract for short interest data.

## Purpose

This contract defines the physical and logical schema for short interest observations used by module 01.

Short interest is a slow, biweekly crowding/short-pressure dataset. It is not intraday executable liquidity and must not be interpreted as same-day tape evidence.

## Active Roots

Current operational root:

`E:\TSIS\data\short\short_interest`

FINRA review/reference root:

`E:\TSIS\data\short_review\finra_short\normalized\short_interest`

FINRA aggregate artifact:

`E:\TSIS\data\short_review\finra_short\artifacts\short_interest_all_biweekly_finra.parquet`

## Physical Layout

Observed per-ticker pattern:

`<ROOT>\<TICKER>.parquet`

Examples:

- `E:\TSIS\data\short\short_interest\AAGR.parquet`
- `E:\TSIS\data\short_review\finra_short\normalized\short_interest\AAGR.parquet`

## Canonical Columns

| Column | Logical role | Type expectation |
|---|---|---|
| `settlement_date` | short interest settlement/report date | date |
| `ticker` | reported ticker | string |
| `short_interest` | shares sold short / reported short interest | integer/numeric |
| `avg_daily_volume` | average daily volume used by source for days-to-cover | integer/numeric |
| `days_to_cover` | short_interest divided by average daily volume | numeric |

## Canonical Key

`ticker + settlement_date`

Duplicate keys must not be silently collapsed without source/revision policy.

## Coverage Evidence

Polygon/local short refresh:

- universe: 4824 `<1B>` tickers
- files present: 4824
- rows total: 520048
- download tasks: 4824
- errors: 0

FINRA parallel build:

- rows: 505745
- tickers: 4687
- date range: `2017-12-29` to `2026-04-15`

Certification v2 for local `short`:

| Status | Tickers |
|---|---:|
| `CERTIFIED_OK` | 1130 |
| `CERTIFIED_OK_WITH_LIMITED_WINDOW` | 738 |
| `REVIEW_TICKER_REUSE` | 761 |
| `REVIEW_REFERENCE_CONFLICT` | 2195 |

## Required Consumer Rules

- Use `settlement_date`, not file timestamp, as the observation date.
- Do not assume 2005-2026 full-history coverage from official/free sources.
- Preserve ticker reuse/reference conflict flags from certification.
- `CERTIFIED_OK_WITH_LIMITED_WINDOW` is usable only with explicit window limitation.
- Review buckets are not allowed as primary model input without downstream review policy.

## Verdict

Short interest has a coherent schema and usable modern coverage, but institutional consumption must be certification-aware. It is not a universally clean full-history layer.
