# Financial Payload Examples v0.1

## Role

This document provides positive evidence that `financial_v0_1` contains parseable business payload files.

It does not claim the family is clean. It shows that the blocked verdict is not caused by universal unreadability.

## Evidence Assets

| Asset | Role |
| --- | --- |
| `../evidence_assets/financial_payload_example_manifest_v0_1.csv` | Sample payload files with business rows. |
| `../evidence_assets/financial_file_level_quality_summary_v0_1.csv` | Endpoint-level file quality summary. |
| `../evidence_assets/sample_payloads/income_statements_A_sample_v0_1.csv` | Representative income statement rows. |
| `../evidence_assets/sample_payloads/balance_sheets_A_sample_v0_1.csv` | Representative balance sheet rows. |
| `../evidence_assets/sample_payloads/cash_flow_statements_A_sample_v0_1.csv` | Representative cash-flow rows. |
| `../evidence_assets/sample_payloads/ratios_A_sample_v0_1.csv` | Representative ratios row. |

## Positive Technical Findings

From the file-level audit:

| Dataset | Files | Read errors | Business rows |
| --- | ---: | ---: | ---: |
| `income_statements` | 12,468 | 0 | 491,907 |
| `balance_sheets` | 12,468 | 0 | 275,836 |
| `cash_flow_statements` | 12,468 | 0 | 491,339 |
| `ratios` | 12,468 | 0 | 4,311 |

Additional positive checks:

- no read errors;
- no missing endpoint outputs;
- no extra endpoint outputs;
- no multi-file ticker outputs;
- ticker column checks pass;
- `_dataset` checks pass;
- `_ingested_utc` is parseable;
- suspicious page cap count is zero.

## Representative Payload Semantics

Statement payloads include:

- ticker identity;
- `cik`;
- `period_end`;
- `filing_date`;
- fiscal quarter/year;
- timeframe;
- accounting metrics;
- `_dataset`;
- `_ingested_utc`.

Ratios payloads include:

- `ticker`;
- `cik`;
- `date`;
- vendor-derived ratio values;
- `price`;
- `market_cap`;
- `_dataset`;
- `_ingested_utc`.

## Interpretation

The family is not blocked because every file is unreadable or empty.

The family is blocked because:

- severe issue handling around empty statement sentinels is unresolved;
- temporal/lifecycle alignment has a large unresolved tail;
- point-in-time and CIK/ticker semantics are not promotion-ready.

## Consumer Rule

These positive examples are useful for:

- source validation;
- schema review;
- repair planning;
- forensic inspection.

They do not authorize:

- master-table joins;
- backtest use;
- ML/RL use;
- live consumers.
