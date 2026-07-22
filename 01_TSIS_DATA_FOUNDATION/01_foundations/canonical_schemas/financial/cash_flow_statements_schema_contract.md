# Cash Flow Statements Financial Schema Contract

Status: canonical schema contract for `D:\financial\cash_flow_statements`.

## Purpose

This contract defines the canonical physical and logical schema for cash flow statement fundamentals. Each row represents one reported cash flow statement observation for one requested ticker and one reporting period.

This dataset is accounting/fundamental data. Consumers must apply point-in-time logic before joining it to market data.

## Physical Layout

Observed root:

`D:\financial\cash_flow_statements\ticker=<TICKER>\cash_flow_statements_<TICKER>.parquet`

Observed representative payload file:

`D:\financial\cash_flow_statements\ticker=A\cash_flow_statements_A.parquet`

Observed empty sentinel file:

`D:\financial\cash_flow_statements\ticker=AABA\cash_flow_statements_AABA.parquet`

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
| `_dataset` | dataset family identifier | string, expected `cash_flow_statements` |
| `_ingested_utc` | ingestion timestamp | timestamp/string timestamp |

Payload files may include these cash flow fields:

| Column | Logical role |
|---|---|
| `net_income` | net income bridge value |
| `depreciation_depletion_and_amortization` | DDA adjustment |
| `other_operating_activities` | other operating cash flow activity |
| `change_in_other_operating_assets_and_liabilities_net` | working-capital/operating asset-liability change |
| `cash_from_operating_activities_continuing_operations` | continuing operations operating cash flow |
| `net_cash_from_operating_activities` | net operating cash flow |
| `purchase_of_property_plant_and_equipment` | capital expenditure |
| `sale_of_property_plant_and_equipment` | sale of PP&E |
| `other_investing_activities` | other investing cash flow activity |
| `net_cash_from_investing_activities_continuing_operations` | continuing operations investing cash flow |
| `net_cash_from_investing_activities` | net investing cash flow |
| `long_term_debt_issuances_repayments` | long-term debt issuance/repayment |
| `short_term_debt_issuances_repayments` | short-term debt issuance/repayment |
| `dividends` | dividend cash flow |
| `other_financing_activities` | other financing cash flow activity |
| `net_cash_from_financing_activities_continuing_operations` | continuing operations financing cash flow |
| `net_cash_from_financing_activities` | net financing cash flow |
| `change_in_cash_and_equivalents` | change in cash and equivalents |
| `effect_of_currency_exchange_rate` | FX effect on cash |
| `noncontrolling_interests` | noncontrolling interest cash flow component |

Numeric accounting fields are expected to be nullable numeric values.

### Empty Sentinel Form

For tickers with no available rows, a file may exist with:

| Column | Logical role |
|---|---|
| `ticker` | requested ticker |
| `_empty` | explicit no-data marker, expected true |
| `_dataset` | dataset family identifier, expected `cash_flow_statements` |
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
- Keep sign conventions from the source unless a downstream accounting-normalization contract explicitly remaps them.

## Current Observed Evidence

The representative payload file for `A` contains 143 rows and conforms to this schema. The representative no-data file for `AABA` contains the empty sentinel form.

## Verdict

`D:\financial\cash_flow_statements` has a coherent canonical schema with two valid physical forms: payload and empty sentinel. Dataset quality must be evaluated through the financial audit contracts, not inferred from schema conformity alone.
