# Financial Ratios Schema Contract

Status: canonical schema contract for `D:\financial\ratios`.

## Purpose

This contract defines the canonical physical and logical schema for financial ratio snapshots. Each row represents one ratio snapshot for one requested ticker and one source date.

This dataset is derived fundamentals/valuation data. It must not be treated as raw accounting statements.

## Physical Layout

Observed root:

`D:\financial\ratios\ticker=<TICKER>\ratios_<TICKER>.parquet`

Observed representative payload file:

`D:\financial\ratios\ticker=A\ratios_A.parquet`

Observed empty sentinel file:

`D:\financial\ratios\ticker=AABA\ratios_AABA.parquet`

## Valid Physical Forms

### Payload Form

Payload files contain one or more business rows and must include:

| Column | Logical role | Type expectation |
|---|---|---|
| `ticker` | requested ticker identity | string |
| `cik` | issuer CIK | string/int-compatible |
| `date` | ratio snapshot/source date | date/string date |
| `_dataset` | dataset family identifier | string, expected `ratios` |
| `_ingested_utc` | ingestion timestamp | timestamp/string timestamp |

Payload files may include these valuation, market and balance metrics:

| Column | Logical role |
|---|---|
| `price` | source price used by ratios |
| `average_volume` | average volume metric |
| `market_cap` | market capitalization |
| `earnings_per_share` | EPS |
| `price_to_earnings` | P/E |
| `price_to_book` | P/B |
| `price_to_sales` | P/S |
| `price_to_cash_flow` | price/cash flow |
| `price_to_free_cash_flow` | price/free cash flow |
| `dividend_yield` | dividend yield |
| `return_on_assets` | ROA |
| `return_on_equity` | ROE |
| `debt_to_equity` | debt/equity |
| `current` | current ratio |
| `quick` | quick ratio |
| `cash` | cash ratio |
| `ev_to_sales` | EV/sales |
| `ev_to_ebitda` | EV/EBITDA |
| `enterprise_value` | enterprise value |
| `free_cash_flow` | free cash flow |

Numeric ratio and valuation fields are expected to be nullable numeric values.

### Empty Sentinel Form

For tickers with no available rows, a file may exist with:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `_empty` | explicit no-data marker, expected true |
| `_dataset` | dataset family identifier, expected `ratios` |
| `_ingested_utc` | ingestion timestamp |

Empty sentinel files are valid structural outputs. They must not be treated as business rows.

## Canonical Keys

The logical observation key is:

`ticker + date`

If multiple rows exist for the same key, consumers must either preserve all rows or apply a documented de-duplication rule.

## Required Consumer Rules

- Treat ratios as derived data; do not use them as substitutes for audited statement values.
- Treat `_empty = true` rows as no-data sentinels.
- Preserve nullable numeric fields; missing values are not zero.
- The `price` field has its own source semantics and must not be assumed equivalent to project OHLCV close without explicit validation.

## Current Observed Evidence

The representative payload file for `A` contains 1 row and conforms to this schema. The representative no-data file for `AABA` contains the empty sentinel form.

## Verdict

`D:\financial\ratios` has a coherent canonical schema with two valid physical forms: payload and empty sentinel. Dataset quality must be evaluated through the financial audit contracts, not inferred from schema conformity alone.
