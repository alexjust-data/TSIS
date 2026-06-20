# Financial Evidence Assets v0.1

## Role

This folder contains normalized evidence assets for the `financial_v0_1` inspection dossier.

The source-of-truth operational audit remains:

```text
E:/TSIS/data/financial/_audit
E:/TSIS/data/financial/_run
```

The files here are compact, dossier-local extracts and summaries so a human inspector can review the family without opening the full physical root first.

## Asset Index

| Asset | Role |
| --- | --- |
| `financial_audit_summary_v0_1.json` | Compact copy of `_audit/audit_summary.json`. |
| `financial_audit_summary_v0_1.csv` | Tabular audit summary. |
| `financial_coverage_by_endpoint_v0_1.csv` | Endpoint coverage summary. |
| `financial_file_level_quality_summary_v0_1.csv` | File-level quality summary by endpoint. |
| `financial_severe_issue_summary_v0_1.csv` | Severe issue counts by endpoint and issue family. |
| `financial_severe_issue_sample_manifest_v0_1.csv` | Human sample of severe issue rows. |
| `financial_empty_sentinel_example_manifest_v0_1.csv` | Human sample of zero-business sentinel files. |
| `financial_payload_example_manifest_v0_1.csv` | Human sample of payload files with business rows. |
| `financial_multi_cik_example_manifest_v0_1.csv` | Human sample of multi-CIK warning cases. |
| `financial_temporal_status_summary_v0_1.csv` | Ticker-level temporal status counts. |
| `financial_temporal_issue_sample_manifest_v0_1.csv` | Human sample of temporal issue cases. |
| `financial_date_range_summary_v0_1.csv` | Endpoint-level date-range and issue summary. |
| `financial_run_progress_v0_1.json` | Compact copy of `_run` progress state. |
| `financial_run_errors_sample_v0_1.csv` | First 100 rows of run errors, if readable. |
| `sample_payloads/*.csv` | Small payload/sentinel excerpts for representative files. |
| `financial_evidence_assets_manifest_v0_1.csv` | Manifest of all dossier-local evidence assets. |

## Interpretation Rules

- These assets are audit evidence, not data products.
- They do not repair `financial_v0_1`.
- They do not authorize downstream consumers.
- They make the blocked verdict inspectable.
- Any later repair or waiver must regenerate or supersede these assets with a new version.

## Source Lineage

Generated from:

```text
E:/TSIS/data/financial/_audit/*.csv
E:/TSIS/data/financial/_audit/audit_summary.json
E:/TSIS/data/financial/_run/*
E:/TSIS/data/financial/<endpoint>/ticker=<TICKER>/*.parquet
```

Generation date:

```text
2026-06-20
```
