# Financial Validators

## Scope

This validator contract governs:

```text
financial_v0_1
```

Physical root:

```text
E:/TSIS/data/financial
```

The current validator state is documented, not fully automated in CI.

## Authorities

This validator must be read with:

- `contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md`
- `data_consumption_policies/financial_consumption_policy.md`
- `dataset_registry/financial/financial_registry_entry.yaml`
- `canonical_schemas/financial/`
- `inspection_dossiers/financial/financial_inspection_readout_v0_1.md`
- `data_quality_report/families/financial_quality_report_v0_1.md`

## Validation Units

| Subfamily | Validation unit |
| --- | --- |
| `income_statements` | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `balance_sheets` | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `cash_flow_statements` | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `ratios` | `ticker + date` |
| `_audit/file_level_audit.csv` | file path |
| `_audit/temporal_validation_by_ticker.csv` | ticker |
| `_run/*` | run artifact |

## Required Checks

### Root And Layout

The validator must check:

- root exists: `E:/TSIS/data/financial`;
- required subroots exist:
  - `income_statements`;
  - `balance_sheets`;
  - `cash_flow_statements`;
  - `ratios`;
  - `_audit`;
  - `_run`;
- each endpoint has exactly one parquet file per expected ticker unless a new registry version says otherwise;
- `_audit` and `_run` artifacts are present and parseable.

### Coverage

The validator must emit:

- expected ticker count;
- downloaded ticker count by endpoint;
- missing ticker outputs;
- extra ticker outputs;
- multi-file ticker cases;
- endpoint coverage percentage.

Files-present coverage must not be interpreted as quality approval.

### File-Level Validity

The validator must check:

- `read_ok`;
- `rows_total`;
- `rows_business`;
- `ticker_col_ok`;
- `ticker_values_nunique`;
- `tickers_col_mismatch_rows`;
- `cik_nunique`;
- `_dataset` correctness;
- `_ingested_utc` parseability;
- missing required columns;
- date column used for temporal validation;
- suspicious source page caps.

Any nonzero `severe_issues.csv` row count blocks promotion unless a revised validator explicitly reclassifies the issue.

### Empty Sentinel Semantics

Financial files may have valid empty sentinel form:

```text
ticker
_empty
_dataset
_ingested_utc
```

The current audit flags many zero-business statement files as `missing_required_cols`, while schema contracts permit empty sentinels.

Required validator action:

- distinguish valid empty sentinel from malformed payload;
- report sentinel counts by endpoint;
- report whether `missing_required_cols` is a real data defect or validator/schema mismatch;
- do not promote while this remains unresolved.

### Temporal And Lifecycle Validity

The validator must compare business rows to lifecycle/reference evidence and emit:

- `OK`;
- `NO_DATA`;
- `ANOMALY_PRE_START`;
- `ANOMALY_POST_END`;
- any future status introduced by revised audits.

Promotion requires an explicit policy for:

- observations before official listing/lifecycle start;
- observations after lifecycle end;
- ticker reuse;
- CIK conflicts;
- missing official lifecycle fields.

### Point-In-Time Availability

Statement consumers must use:

```text
filing_date
```

not:

```text
period_end
```

as availability date.

Any feature or master-table use must demonstrate lag/availability rules.

### Ratio-Specific Checks

The validator must treat `ratios` as vendor-derived snapshots.

It must not accept:

- ratio `price` as TSIS price authority;
- ratio `market_cap` as universe membership authority;
- sparse one-row snapshots as full fundamentals history.

## Current Observed Status

Current audit facts:

| Metric | Value |
| --- | ---: |
| audit status | `FAIL` |
| expected tickers | 12,468 |
| endpoint coverage | 100% |
| severe issues | 13,337 |
| temporal issues | 3,171 |
| read errors | 0 |
| missing outputs | 0 |
| extra outputs | 0 |

Severe issue distribution:

| Dataset | Severe issues |
| --- | ---: |
| `balance_sheets` | 4,449 |
| `cash_flow_statements` | 4,445 |
| `income_statements` | 4,443 |
| `ratios` | 0 |

All observed severe issues are:

```text
missing_required_cols
```

## Acceptance States

Allowed states:

- `blocked_audit_fail`
- `blocked_temporal_lifecycle`
- `review_empty_sentinel_reconciliation`
- `review_ratio_snapshot`
- `usable_after_filtering`
- `promoted_subfamily`

Current family state:

```text
blocked_audit_fail
```

## Forbidden Conclusions

The validator must not conclude:

- 100% endpoint coverage means clean financial data;
- empty sentinel rows are business observations;
- `period_end` is decision-time availability;
- ratios are audited accounting truth;
- ratio `price` is project OHLCV truth;
- current `financial_v0_1` can feed master tables or ML without a new promotion gate.

## Output Contract

A compliant future validator must emit:

- root audit summary;
- endpoint coverage table;
- file-level validity table;
- empty sentinel profile;
- severe issue table;
- temporal/lifecycle table;
- consumer readiness matrix;
- final human readout;
- run manifest.

Until those outputs resolve the current `FAIL`, the family remains blocked.
