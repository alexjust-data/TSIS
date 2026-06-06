# Additional Financials Schema Contract

Status: canonical schema contract for `E:\TSIS\data\additional\financials`.

## Purpose

`additional\financials` is the financial subblock downloaded as part of the `additional` Polygon refresh for the `<1B>` operating universe.

It is not the same institutional root as `E:\TSIS\data\financial`. It is a universe-scoped auxiliary materialization with the same financial endpoint families:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`
- `ratios`

## Physical Layout

Observed root:

`E:\TSIS\data\additional\financials`

Observed pattern:

`<dataset>\ticker=<TICKER>\<dataset>_<TICKER>.parquet`

Examples:

- `E:\TSIS\data\additional\financials\balance_sheets\ticker=AACT\balance_sheets_AACT.parquet`
- `E:\TSIS\data\additional\financials\income_statements\ticker=AACT\income_statements_AACT.parquet`
- `E:\TSIS\data\additional\financials\cash_flow_statements\ticker=AACT\cash_flow_statements_AACT.parquet`
- `E:\TSIS\data\additional\financials\ratios\ticker=AAGR\ratios_AAGR.parquet`

## Valid Physical Forms

Ticker files may contain either:

- payload rows
- empty sentinel rows with `ticker`, `_empty`, `_dataset`, `_ingested_utc`

Empty sentinel rows are valid no-data outputs and must not be counted as business rows.

## Statement Families

The three statement families share the same analytical key pattern:

`ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe`

Common identity and period columns:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `tickers` | source ticker aliases attached to the record |
| `cik` | issuer CIK |
| `period_end` | fiscal period end |
| `filing_date` | filing/publication date |
| `fiscal_quarter` | fiscal quarter |
| `fiscal_year` | fiscal year |
| `timeframe` | report cadence, including quarterly or trailing twelve months where present |
| `_dataset` | endpoint family |
| `_ingested_utc` | ingestion timestamp |

Statement-specific accounting columns are nullable numeric fields and must preserve missing values as missing, not zero.

## Ratios Family

Observed ratios columns include:

`ticker`, `cik`, `date`, `price`, `average_volume`, `market_cap`, `earnings_per_share`, `price_to_book`, `price_to_sales`, `dividend_yield`, `return_on_assets`, `return_on_equity`, `debt_to_equity`, `current`, `quick`, `cash`, `ev_to_sales`, `ev_to_ebitda`, `enterprise_value`, `free_cash_flow`, `_dataset`, `_ingested_utc`.

Canonical ratios key:

`ticker + date`

Ratios are derived snapshot data and must not be treated as audited statement values.

## Coverage Evidence

Audited against 4824 `<1B>` tickers:

| Dataset | files_present | files_non_empty | coverage_non_empty_pct | status |
|---|---:|---:|---:|---|
| `income_statements` | 4824 | 4813 | 99.772 | good |
| `balance_sheets` | 4824 | 4813 | 99.772 | good |
| `cash_flow_statements` | 4824 | 4810 | 99.710 | good |
| `ratios` | 4824 | 2232 | 46.269 | review |

## Required Consumer Rules

- Use `filing_date` for point-in-time availability.
- Treat `_empty = true` as a no-data sentinel.
- Do not read this root with blind dataset merge if it reintroduces partition/schema conflicts.
- Do not collapse this root into `E:\TSIS\data\financial` without reconciliation.
- Use `ratios` only as sparse auxiliary context unless a downstream contract promotes it.

## Verdict

`additional\financials` is an accepted auxiliary financial block for `<1B>`. Statement families are strong. `ratios` remains review due to sparse effective coverage.
