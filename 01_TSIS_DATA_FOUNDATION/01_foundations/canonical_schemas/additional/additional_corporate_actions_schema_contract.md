# Additional Corporate Actions Schema Contract

Status: canonical schema contract for `E:\TSIS\data\additional\corporate_actions`.

## Purpose

`additional\corporate_actions` stores Polygon corporate action endpoints downloaded for the `<1B>` operating universe.

It is a secondary corporate actions layer. The primary institutional corporate actions/reference authority remains `reference` unless a downstream contract explicitly says otherwise.

## Physical Layout

Observed root:

`E:\TSIS\data\additional\corporate_actions`

Observed datasets:

- `dividends`
- `splits`
- `ticker_events`

Observed pattern:

`<dataset>\ticker=<TICKER>\<dataset>_<TICKER>.parquet`

## Valid Physical Forms

Ticker files may contain either:

- payload event rows
- empty sentinel rows with `ticker`, `_empty`, `_dataset`, `_ingested_utc`

Empty sentinel rows are valid no-data outputs.

## Dividends

Observed columns:

`cash_amount`, `currency`, `declaration_date`, `dividend_type`, `ex_dividend_date`, `frequency`, `id`, `pay_date`, `record_date`, `ticker`, `_dataset`, `_ingested_utc`.

Canonical event key:

`ticker + ex_dividend_date + id`

## Splits

Observed columns:

`execution_date`, `id`, `split_from`, `split_to`, `ticker`, `_dataset`, `_ingested_utc`.

Canonical event key:

`ticker + execution_date + id`

## Ticker Events

Observed columns:

`type`, `date`, `ticker`, `name`, `ticker_change.ticker`, `_dataset`, `_ingested_utc`.

Canonical event key:

`ticker + date + type`

Ticker events may contain nested/dotted source fields and require taxonomy reconciliation before replacing `reference` semantics.

## Coverage Evidence

Audited against 4824 `<1B>` tickers:

| Dataset | files_present | files_non_empty | coverage_non_empty_pct |
|---|---:|---:|---:|
| `ticker_events` | 4824 | 2703 | 56.032 |
| `splits` | 4824 | 1876 | 38.889 |
| `dividends` | 4824 | 1258 | 26.078 |

Reference overlap evidence:

- `splits`: strong exact overlap with `reference`
- `dividends`: strong exact overlap with `reference`
- `ticker_events`: present but not exact-overlap stable enough to displace `reference`

## Required Consumer Rules

- Treat this layer as secondary to `reference`.
- Do not use it as the primary split/dividend adjustment source without explicit reconciliation.
- Preserve `_empty` sentinel semantics.
- Use it for confirmation, redundancy checks and incremental ticker-event review.

## Verdict

`additional\corporate_actions` is structurally valid but remains `review` as an institutional source. It is mostly secondary/redundant for splits and dividends, with potential review value in ticker events.
