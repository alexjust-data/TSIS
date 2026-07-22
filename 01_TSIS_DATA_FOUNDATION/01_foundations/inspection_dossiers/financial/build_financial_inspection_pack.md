# Build Financial Inspection Pack v0.1

## Role

This document records how the current `financial_v0_1` inspection evidence was assembled.

It is not a production pipeline. It is a reproducibility note for the dossier-local summaries and case evidence.

## Inputs

Primary physical root:

```text
E:/TSIS/data/financial
```

Audit inputs:

```text
E:/TSIS/data/financial/_audit/audit_summary.json
E:/TSIS/data/financial/_audit/coverage_by_endpoint.csv
E:/TSIS/data/financial/_audit/date_ranges_by_ticker_endpoint.csv
E:/TSIS/data/financial/_audit/file_level_audit.csv
E:/TSIS/data/financial/_audit/missing_tickers_by_endpoint.csv
E:/TSIS/data/financial/_audit/severe_issues.csv
E:/TSIS/data/financial/_audit/temporal_issues.csv
E:/TSIS/data/financial/_audit/temporal_validation_by_ticker.csv
```

Run inputs:

```text
E:/TSIS/data/financial/_run/download_fundamentals_v1.progress.json
E:/TSIS/data/financial/_run/download_fundamentals_v1.errors.csv
```

Representative payloads:

```text
E:/TSIS/data/financial/income_statements/ticker=A/income_statements_A.parquet
E:/TSIS/data/financial/balance_sheets/ticker=A/balance_sheets_A.parquet
E:/TSIS/data/financial/cash_flow_statements/ticker=A/cash_flow_statements_A.parquet
E:/TSIS/data/financial/ratios/ticker=A/ratios_A.parquet
E:/TSIS/data/financial/income_statements/ticker=AABA/income_statements_AABA.parquet
E:/TSIS/data/financial/ratios/ticker=AABA/ratios_AABA.parquet
```

## Outputs

Outputs are written to:

```text
01_foundations/inspection_dossiers/financial/evidence_assets/
```

The generated assets are indexed in:

```text
evidence_assets/financial_evidence_assets_manifest_v0_1.csv
```

## Transformation

The pack generation performs only summarization and sample extraction:

- copies compact audit summary fields;
- groups file-level audit rows by endpoint;
- groups severe issues by endpoint and issue family;
- extracts first representative payload, sentinel and multi-CIK examples;
- groups temporal statuses;
- extracts temporal issue samples;
- writes small representative payload excerpts.

It does not:

- rewrite source data;
- fix missing columns;
- waive severe issues;
- change the audit verdict;
- change the physical root.

## Regeneration Rule

If any of the following change, regenerate this pack and version the outputs:

- `_audit` contents;
- `_run` contents;
- financial schema contracts;
- validator semantics;
- empty sentinel policy;
- temporal/lifecycle policy;
- physical root.
