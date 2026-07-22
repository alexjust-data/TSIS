# Financial Operational Audit Schema Contract

Status: operational schema contract for `D:\financial\_audit`.

## Purpose

This contract defines the canonical schemas for financial dataset audit artifacts. These files describe coverage, file-level validity, severe issues and lifecycle/temporal validation for the financial datasets.

These are operational evidence files, not model input datasets.

## Physical Layout

Observed root:

`D:\financial\_audit`

Observed files:

- `audit_summary.json`
- `coverage_by_endpoint.csv`
- `date_ranges_by_ticker_endpoint.csv`
- `file_level_audit.csv`
- `missing_tickers_by_endpoint.csv`
- `severe_issues.csv`
- `temporal_issues.csv`
- `temporal_validation_by_ticker.csv`

## audit_summary.json

Canonical fields:

| Field | Logical role |
|---|---|
| `status` | aggregate audit status |
| `expected_tickers` | expected ticker universe count |
| `datasets` | audited dataset families |
| `missing_total` | total missing ticker/dataset outputs |
| `extra_total` | total unexpected ticker/dataset outputs |
| `multi_file_tickers_total` | total ticker/dataset cases with multiple files |
| `severe_issues` | count of severe file-level issues |
| `temporal_issues` | count of temporal/lifecycle issues |
| `temporal_status_counts` | counts by temporal status |
| `outdir` | audited financial root |
| `audit_dir` | audit output root |
| `lifecycle_path` | lifecycle reference used by audit |
| `tolerance_pre_days` | tolerated pre-lifecycle window |
| `tolerance_post_days` | tolerated post-lifecycle window |

Current observed status is `FAIL`. This means coverage can be complete while audit quality still blocks institutional promotion.

## coverage_by_endpoint.csv

Canonical columns:

| Column | Logical role |
|---|---|
| `dataset` | financial endpoint/family |
| `expected_tickers` | expected universe count |
| `downloaded_tickers` | ticker outputs present |
| `missing_tickers` | missing ticker count |
| `extra_tickers` | unexpected ticker count |
| `tickers_with_multiple_files` | multi-file ticker count |
| `coverage_pct` | endpoint coverage percentage |

## file_level_audit.csv

Canonical columns:

| Column | Logical role |
|---|---|
| `dataset` | financial endpoint/family |
| `file` | audited file path |
| `expected_ticker` | expected ticker from partition/file |
| `read_ok` | file can be read |
| `rows_total` | total physical rows |
| `rows_business` | rows excluding empty sentinels |
| `ticker_col_ok` | ticker column matches expectation |
| `ticker_values_nunique` | number of unique ticker values |
| `tickers_col_mismatch_rows` | rows where list/source ticker metadata mismatches |
| `cik_nunique` | unique CIK count |
| `dataset_col_ok` | `_dataset` matches dataset |
| `ingested_utc_parseable` | `_ingested_utc` can be parsed |
| `missing_required_cols` | missing required columns |
| `date_col_used` | date column used for temporal inspection |
| `date_start` | minimum observed business date |
| `date_end` | maximum observed business date |
| `suspicious_page_cap` | source pagination cap suspicion |
| `issues` | semicolon/list encoded issue labels |

## date_ranges_by_ticker_endpoint.csv

Canonical columns mirror the ticker/date-range subset of `file_level_audit.csv`:

`dataset`, `ticker`, `rows_business`, `date_col_used`, `date_start`, `date_end`, `ticker_col_ok`, `cik_nunique`, `dataset_col_ok`, `ingested_utc_parseable`, `missing_required_cols`, `suspicious_page_cap`, `issues`.

## severe_issues.csv

Canonical columns mirror `file_level_audit.csv`. This file is the filtered evidence set for file-level severe issues and must be treated as an audit failure input.

## temporal_validation_by_ticker.csv

Canonical columns:

| Column | Logical role |
|---|---|
| `ticker` | audited ticker |
| `cik` | issuer CIK from lifecycle/reference |
| `first_seen_date` | first observed reference/lifecycle date |
| `last_seen_date` | last observed reference/lifecycle date |
| `list_date` | listing date if available |
| `delisted_utc` | delisting timestamp if available |
| `fin_min_date` | first financial observation date |
| `fin_max_date` | last financial observation date |
| `datasets_with_rows` | financial families with business rows |
| `total_rows` | total business rows across families |
| `official_list_date` | official listing date used by audit |
| `official_delist_date` | official delist date used by audit |
| `cik_lifecycle` | lifecycle CIK |
| `start_ref` | audit start reference date |
| `end_ref` | audit end reference date |
| `anomaly_pre_start` | observations before tolerated start |
| `anomaly_post_end` | observations after tolerated end |
| `temporal_status` | temporal validation status |

## temporal_issues.csv

Canonical columns mirror `temporal_validation_by_ticker.csv`. This file is the filtered evidence set for temporal/lifecycle issues and must be treated as an audit failure input.

## missing_tickers_by_endpoint.csv

This file records missing ticker/dataset cases when present. An empty or header-only file is valid when no missing cases exist.

## Required Consumer Rules

- Do not treat 100% endpoint coverage as institutional approval.
- `audit_summary.status` is the top-level quality signal.
- `severe_issues.csv` and `temporal_issues.csv` must be read before promoting financial datasets.
- Operational audit files must not be mixed into research feature tables.

## Current Observed Evidence

Observed coverage is 100% for `income_statements`, `balance_sheets`, `cash_flow_statements` and `ratios`, but `audit_summary.json` currently reports `status = FAIL` with severe and temporal issues.

## Verdict

`D:\financial\_audit` is structurally coherent and provides the required evidence layer. Current observed evidence does not certify the financial datasets as institutionally good; it certifies that the audit found blocking issues.
