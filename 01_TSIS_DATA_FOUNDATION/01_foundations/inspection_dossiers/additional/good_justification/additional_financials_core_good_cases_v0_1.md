# Additional Financials Core Good Cases v0.1

Financial statement subfamilies are the strongest Additional ticker-based block.

| dataset | files_present | files_non_empty | coverage_non_empty_pct | rows_total | validator_focus | forbidden_interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| income_statements | 4824.0 | 4813.0 | 99.772 | 242897 | filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity | Do not treat filing-period facts as decision-time fields without point-in-time filing logic. |
| balance_sheets | 4824.0 | 4813.0 | 99.772 | 136672 | filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity | Do not treat balance-sheet fields as always-known on period_end. |
| cash_flow_statements | 4824.0 | 4810.0 | 99.71 | 242223 | filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity | Do not use as alpha-ready features without point-in-time filing availability. |

Institutional reading:

- Coverage is high enough for contextual audit use.
- The mandatory guardrail is point-in-time filing availability.
- These files can inform CAPA 1 quality/context tables, but they are not alpha features by default.
