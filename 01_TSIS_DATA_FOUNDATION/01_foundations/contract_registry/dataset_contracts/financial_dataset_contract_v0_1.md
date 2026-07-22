# Financial Dataset Contract v0.1 - Modulo 01

## 1. Role

This contract defines `financial_v0_1` as the standalone financial/fundamentals root observed under:

```text
E:/TSIS/data/financial
```

It covers:

- `balance_sheets`
- `cash_flow_statements`
- `income_statements`
- `ratios`
- `_audit`
- `_run`

This is a fundamentals/context dataset family. It is not raw market price data, not quote data, not tape data, and not a point-in-time feature layer by default.

## 2. Current Institutional Status

Status:

```text
audited_blocked_v0_1
```

Reason:

- physical endpoint coverage is complete;
- files are readable;
- schemas are documented;
- but the existing operational audit reports `status = FAIL`;
- severe file-level issues and lifecycle/temporal issues remain unresolved.

Therefore `financial_v0_1` is governed and visible, but not approved for production consumption.

## 3. Primary Semantics

Financial statements use this logical observation unit:

```text
ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe
```

Ratios use this logical observation unit:

```text
ticker + date
```

Operational audit files use file-level and ticker-level audit units and are not model input datasets.

## 4. Source And Scope

Observed physical root:

```text
E:/TSIS/data/financial
```

Observed endpoint structure:

| Subroot | Files | Primary file type |
| --- | ---: | --- |
| `income_statements` | 12,468 | parquet |
| `balance_sheets` | 12,468 | parquet |
| `cash_flow_statements` | 12,468 | parquet |
| `ratios` | 12,468 | parquet |
| `_audit` | 8 | csv/json |
| `_run` | 2 | csv/json |

Operational audit scope:

| Metric | Value |
| --- | ---: |
| expected tickers | 12,468 |
| datasets | 4 |
| endpoint coverage | 100% for all four datasets |
| missing ticker outputs | 0 |
| extra ticker outputs | 0 |
| multi-file ticker outputs | 0 |

## 5. Canonical Schema Contracts

Schemas live in:

- `01_foundations/canonical_schemas/financial/balance_sheets_schema_contract.md`
- `01_foundations/canonical_schemas/financial/cash_flow_statements_schema_contract.md`
- `01_foundations/canonical_schemas/financial/income_statements_schema_contract.md`
- `01_foundations/canonical_schemas/financial/ratios_schema_contract.md`
- `01_foundations/canonical_schemas/financial/operational_audit_schema_contract.md`
- `01_foundations/canonical_schemas/financial/operational_run_schema_contract.md`

Known schema-location debt:

- the schema files currently describe roots as `D:/financial`;
- the active physical root in this report is `E:/TSIS/data/financial`;
- this path drift must be reconciled before promotion.

## 6. Evidence Dossier

Primary current-state evidence:

- `E:/TSIS/data/financial/_audit/audit_summary.json`
- `E:/TSIS/data/financial/_audit/coverage_by_endpoint.csv`
- `E:/TSIS/data/financial/_audit/file_level_audit.csv`
- `E:/TSIS/data/financial/_audit/severe_issues.csv`
- `E:/TSIS/data/financial/_audit/temporal_validation_by_ticker.csv`
- `E:/TSIS/data/financial/_audit/temporal_issues.csv`
- `E:/TSIS/data/financial/_run/download_fundamentals_v1.progress.json`
- `E:/TSIS/data/financial/_run/download_fundamentals_v1.errors.csv`

Modern foundation readout:

- `01_foundations/inspection_dossiers/financial/financial_inspection_readout_v0_1.md`

Data-quality report:

- `01_foundations/data_quality_report/families/financial_quality_report_v0_1.md`

## 7. Current Quality Findings

The current operational audit reports:

| Finding | Count |
| --- | ---: |
| audit status | `FAIL` |
| severe issues | 13,337 |
| temporal issues | 3,171 |
| read errors | 0 |
| missing outputs | 0 |
| extra outputs | 0 |
| files missing required columns | 13,337 |

All severe issues currently observed are:

```text
missing_required_cols
```

The severe issues are concentrated in statement endpoint files with zero business rows:

| Dataset | Severe issues |
| --- | ---: |
| `balance_sheets` | 4,449 |
| `cash_flow_statements` | 4,445 |
| `income_statements` | 4,443 |
| `ratios` | 0 |

Temporal validation reports:

| Status | Tickers |
| --- | ---: |
| `OK` | 4,859 |
| `NO_DATA` | 4,438 |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

## 8. Required Consumer Rules

Consumers must:

- treat `financial_v0_1` as blocked until the audit `FAIL` is resolved or explicitly waived by a new contract;
- use `filing_date` for point-in-time availability, not `period_end`;
- treat empty sentinels as no-data outputs, not business rows;
- preserve nullable accounting values as missing, not zero;
- not join statements to prices without explicit point-in-time and lifecycle rules;
- not treat ratios as audited accounting truth;
- not treat ratio `price` or `market_cap` as equivalent to TSIS OHLCV price authority without validation;
- preserve lifecycle and CIK conflict risks.

## 9. Allowed Consumers

Allowed now:

- `data_quality_report`
- `source_validation`
- `forensic_review`
- `repair_planning`
- `schema_review`
- `research_only_blocked_until_filtered`

Not enabled:

- `master_daily_table`
- `symbol_master`
- `backtest_core`
- `backtest_extended`
- `ml_primary`
- `ml_flagged`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Promotion to any non-audit consumer requires a new readout or revised validator output.

## 10. Non-Goals

This contract does not:

- certify financial data as clean;
- certify ratios as complete;
- certify point-in-time feature usability;
- resolve lifecycle conflicts;
- replace `additional/financials`;
- replace `reference`;
- replace raw market data;
- repair the current audit failure.

## 11. Verdict

`financial_v0_1` is now documented as a governed but blocked dataset family.

The correct operational state is:

```text
blocked_for_consumption_until_financial_audit_fail_is_resolved
```
