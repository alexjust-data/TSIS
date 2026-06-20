# Short Review Evidence Assets v0.1

This directory contains stable derived evidence for:

```text
short_review_finra_v0_1
```

Source root:

```text
E:/TSIS/data/short_review/finra_short
```

These files are evidence assets for the FINRA official/free
baseline/provenance layer. They are not a production short-data replacement.

## Asset Index

| Asset | Purpose |
| --- | --- |
| `short_review_audit_summary_v0_1.json` | Compact audit summary for aggregate artifacts, normalized files, provenance assets and local comparison. |
| `short_review_aggregate_profile_v0_1.csv` | Aggregate artifact rows, tickers, dates and schema. |
| `short_review_key_quality_v0_1.csv` | Key uniqueness profile for aggregate artifacts. |
| `short_review_numeric_sanity_v0_1.csv` | Numeric nonnegative/null/infinite checks. |
| `short_review_null_profile_v0_1.csv` | Column null profile. |
| `short_review_compact_file_count_summary_v0_1.csv` | Compact physical file counts. |
| `short_review_normalized_file_counts_v0_1.csv` | Normalized per-ticker parquet counts. |
| `short_review_local_comparison_summary_v0_1.csv` | FINRA vs local/Polygon comparison snapshot. |
| `short_review_provenance_assets_v0_1.csv` | Build notes, research notes, README, manifests, logs and pipeline presence. |
| `short_review_artifact_manifest_summary_v0_1.csv` | Aggregate artifact manifest summaries. |
| `short_review_log_summary_v0_1.csv` | Download log status summaries. |
| `short_review_scope_limitations_v0_1.csv` | Official/free source scope limitations. |
| `short_review_short_volume_duplicate_key_manifest_v0_1.csv` | Duplicate `ticker + date` keys in short volume. |
| `short_review_short_volume_duplicate_key_by_ticker_v0_1.csv` | Duplicate short-volume keys summarized by ticker. |
| `short_review_sample_payload_manifest_v0_1.csv` | Sample payload manifest. |
| `short_review_read_errors_v0_1.csv` | Read-error table. Empty means no aggregate read errors were observed by this evidence build. |
| `short_review_evidence_assets_manifest_v0_1.csv` | Manifest of all evidence assets in this directory. |
| `sample_payloads/` | Representative short-interest, short-volume and duplicate-key extracts. |

## Current Evidence Snapshot

| Metric | Short interest | Short volume |
| --- | ---: | ---: |
| Rows | 505,745 | 4,689,038 |
| Tickers | 4,687 | 4,623 |
| Date min | 2017-12-29 | 2018-08-01 |
| Date max | 2026-04-15 | 2026-04-29 |
| Aggregate read errors | 0 | 0 |
| Duplicate logical keys | 0 | 824 |
| Duplicate excess rows | 0 | 5,250 |

The duplicate short-volume keys are a scoped technical flag. They block direct
use of short volume as a clean analytic table until deduplication or aggregation
semantics are documented.

## Scope Boundary

This evidence supports:

- official/free FINRA baseline review;
- source provenance;
- coverage comparison;
- repair planning for a future short layer.

It does not support:

- full 2005-2026 short history completeness;
- direct production replacement for `E:/TSIS/data/short`;
- same-day causal use of short interest;
- market-wide consolidated interpretation of `short_volume_ratio`.
