# Balance Sheets Financial Schema Contract

Status: canonical schema contract for `D:\financial\balance_sheets`.

## Purpose

This contract defines the canonical physical and logical schema for balance sheet fundamentals. Each row represents one reported balance sheet observation for one requested ticker and one reporting period.

This is a fundamentals dataset, not a market data price dataset. It must not be joined to price bars without explicit point-in-time rules based on filing availability.

## Physical Layout

Observed root:

`D:\financial\balance_sheets\ticker=<TICKER>\balance_sheets_<TICKER>.parquet`

Observed representative payload file:

`D:\financial\balance_sheets\ticker=A\balance_sheets_A.parquet`

Observed empty sentinel file:

`D:\financial\balance_sheets\ticker=AABA\balance_sheets_AABA.parquet`

## Valid Physical Forms

### Payload Form

Payload files contain one or more business rows and must include the following identity and period fields:

| Column | Logical role | Type expectation |
|---|---|---|
| `ticker` | requested ticker partition identity | string |
| `tickers` | source ticker aliases attached to the filing/record | list<string> |
| `cik` | issuer CIK | string/int-compatible |
| `period_end` | fiscal period end date | date/string date |
| `filing_date` | filing/publication date | date/string date |
| `fiscal_quarter` | fiscal quarter | string/int-compatible |
| `fiscal_year` | fiscal year | int-compatible |
| `timeframe` | report cadence, for example annual/quarterly | string |
| `_dataset` | dataset family identifier | string, expected `balance_sheets` |
| `_ingested_utc` | ingestion timestamp | timestamp/string timestamp |

Payload files may include these balance sheet fields:

| Column | Logical role |
|---|---|
| `cash_and_equivalents` | cash and equivalents |
| `short_term_investments` | short-term investments |
| `receivables` | receivables |
| `inventories` | inventories |
| `other_current_assets` | other current assets |
| `total_current_assets` | total current assets |
| `property_plant_equipment_net` | net property, plant and equipment |
| `goodwill` | goodwill |
| `intangible_assets_net` | net intangible assets |
| `other_assets` | other assets |
| `total_assets` | total assets |
| `accounts_payable` | accounts payable |
| `deferred_revenue_current` | current deferred revenue |
| `debt_current` | current debt |
| `accrued_and_other_current_liabilities` | accrued and other current liabilities |
| `total_current_liabilities` | total current liabilities |
| `long_term_debt_and_capital_lease_obligations` | long-term debt and capital lease obligations |
| `other_noncurrent_liabilities` | other noncurrent liabilities |
| `total_liabilities` | total liabilities |
| `common_stock` | common stock |
| `additional_paid_in_capital` | additional paid-in capital |
| `treasury_stock` | treasury stock |
| `accumulated_other_comprehensive_income` | accumulated other comprehensive income |
| `retained_earnings_deficit` | retained earnings or deficit |
| `other_equity` | other equity |
| `total_equity_attributable_to_parent` | equity attributable to parent |
| `noncontrolling_interest` | noncontrolling interest |
| `total_equity` | total equity |
| `total_liabilities_and_equity` | total liabilities and equity |
| `preferred_stock` | preferred stock |

Numeric accounting fields are expected to be nullable numeric values.

### Empty Sentinel Form

For tickers with no available rows, a file may exist with:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `_empty` | explicit no-data marker, expected true |
| `_dataset` | dataset family identifier, expected `balance_sheets` |
| `_ingested_utc` | ingestion timestamp |

Empty sentinel files are valid structural outputs. They must not be treated as business rows.

## Canonical Keys

The logical observation key is:

`ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe`

Consumers must handle duplicate or revised filings explicitly. If `cik` changes within a ticker history, the row is still physically valid but must be surfaced by audit as an issuer-identity risk.

## Required Consumer Rules

- Use `filing_date` for point-in-time availability, not `period_end`.
- Treat `_empty = true` rows as no-data sentinels.
- Do not forward-fill balance sheet values across ticker lifecycle boundaries unless a downstream contract explicitly permits it.
- Preserve nullable numeric accounting fields; missing values are not zero.

## Current Observed Evidence

The representative payload file for `A` contains 80 rows and conforms to this schema. The representative no-data file for `AABA` contains the empty sentinel form.

## Verdict

`D:\financial\balance_sheets` has a coherent canonical schema with two valid physical forms: payload and empty sentinel. Dataset quality must be evaluated through the financial audit contracts, not inferred from schema conformity alone.
