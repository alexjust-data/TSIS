# Income Statements Financial Schema Contract

Status: canonical schema contract for `D:\financial\income_statements`.

## Purpose

This contract defines the canonical physical and logical schema for income statement fundamentals. Each row represents one reported income statement observation for one requested ticker and one reporting period.

This dataset is accounting/fundamental data. Consumers must apply point-in-time logic before joining it to market data.

## Physical Layout

Observed root:

`D:\financial\income_statements\ticker=<TICKER>\income_statements_<TICKER>.parquet`

Observed representative payload file:

`D:\financial\income_statements\ticker=A\income_statements_A.parquet`

Observed empty sentinel file:

`D:\financial\income_statements\ticker=AABA\income_statements_AABA.parquet`

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
| `_dataset` | dataset family identifier | string, expected `income_statements` |
| `_ingested_utc` | ingestion timestamp | timestamp/string timestamp |

Payload files may include these income statement fields:

| Column | Logical role |
|---|---|
| `revenue` | revenue |
| `cost_of_revenue` | cost of revenue |
| `gross_profit` | gross profit |
| `selling_general_administrative` | SG&A |
| `research_development` | research and development |
| `other_operating_expenses` | other operating expenses |
| `total_operating_expenses` | total operating expenses |
| `operating_income` | operating income |
| `interest_expense` | interest expense |
| `interest_income` | interest income |
| `other_income_expense` | other income/expense |
| `total_other_income_expense` | total other income/expense |
| `income_before_income_taxes` | pretax income |
| `income_taxes` | income taxes |
| `consolidated_net_income_loss` | consolidated net income/loss |
| `net_income_loss_attributable_common_shareholders` | net income/loss attributable to common shareholders |
| `basic_earnings_per_share` | basic EPS |
| `diluted_earnings_per_share` | diluted EPS |
| `basic_shares_outstanding` | basic shares outstanding |
| `diluted_shares_outstanding` | diluted shares outstanding |
| `ebitda` | EBITDA |
| `discontinued_operations` | discontinued operations |

Numeric accounting fields are expected to be nullable numeric values.

### Empty Sentinel Form

For tickers with no available rows, a file may exist with:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `_empty` | explicit no-data marker, expected true |
| `_dataset` | dataset family identifier, expected `income_statements` |
| `_ingested_utc` | ingestion timestamp |

Empty sentinel files are valid structural outputs. They must not be treated as business rows.

## Canonical Keys

The logical observation key is:

`ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe`

Consumers must treat restatements, duplicates and multi-CIK cases as audit-visible events rather than silently collapsing rows.

## Required Consumer Rules

- Use `filing_date` for point-in-time availability.
- Treat `_empty = true` rows as no-data sentinels.
- Preserve nullable numeric accounting fields; missing values are not zero.
- Do not mix EPS/share fields with split-adjusted price data unless the downstream model explicitly defines the alignment semantics.

## Current Observed Evidence

The representative payload file for `A` contains 143 rows and conforms to this schema. The representative no-data file for `AABA` contains the empty sentinel form.

## Verdict

`D:\financial\income_statements` has a coherent canonical schema with two valid physical forms: payload and empty sentinel. Dataset quality must be evaluated through the financial audit contracts, not inferred from schema conformity alone.
