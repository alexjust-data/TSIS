# Regime Indicators Evidence Assets v0.1

This directory contains stable derived evidence for:

```text
regime_indicators_v0_1
```

Source root:

```text
E:/TSIS/data/regime_indicators
```

These files are evidence assets, not repaired data.

## Asset Index

| Asset | Purpose |
| --- | --- |
| `regime_indicators_audit_summary_v0_1.json` | Compact audit summary for physical inventory, daily blockers, minute review and metadata. |
| `regime_indicators_inventory_v0_1.csv` | File-level parquet inventory. |
| `regime_indicators_file_counts_v0_1.csv` | Counts by root group and file kind. |
| `regime_indicators_daily_date_quality_v0_1.csv` | Daily file date/datetime quality statistics. |
| `regime_indicators_daily_blocking_date_manifest_v0_1.csv` | Blocking daily-date manifest for all daily files. |
| `regime_indicators_minute_schema_review_v0_1.csv` | Minute schema and timestamp review summary. |
| `regime_indicators_minute_flagged_issue_manifest_v0_1.csv` | Minute files with observed non-schema quality flags. |
| `regime_indicators_metadata_summary_v0_1.csv` | Root JSON metadata shape summary. |
| `regime_indicators_read_errors_v0_1.csv` | File read-error table. Empty means no read errors were observed by this evidence build. |
| `regime_indicators_sample_payload_manifest_v0_1.csv` | Manifest of copied sample payload extracts. |
| `regime_indicators_evidence_assets_manifest_v0_1.csv` | Manifest of all dossier-local evidence assets. |
| `sample_payloads/spy_day_broken_sample_v0_1.csv` | Daily ETF sample showing the 1970 date blocker. |
| `sample_payloads/i_ndx_day_broken_sample_v0_1.csv` | Daily index sample showing the 1970 date blocker. |
| `sample_payloads/spy_minute_sample_v0_1.csv` | Representative ETF minute sample. |
| `sample_payloads/i_ndx_minute_sample_v0_1.csv` | Representative index minute sample. |
| `sample_payloads/minute_high_lt_low_issue_samples_v0_1.csv` | Concrete minute rows where `high < low`. |

## Required Reading

Read these assets through:

- `../regime_indicators_inspection_readout_v0_1.md`;
- `../good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md`;
- `../bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md`;
- `../flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md`;
- `../coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md`.

## Current Evidence Snapshot

| Metric | Value |
| --- | ---: |
| Parquet files | 67 |
| JSON metadata files | 2 |
| Read errors | 0 |
| Daily files | 34 |
| Daily files with only `1970-01-01` as `date` | 34 |
| Daily rows | 153,397 |
| Minute files | 33 |
| Minute rows | 64,348,953 |
| Minute duplicate timestamp rows | 0 |
| Minute non-monotonic files | 0 |
| Minute `high < low` rows | 204 |

The daily files are blocked for consumption. Minute files remain scoped/review,
not production feature-store evidence.
