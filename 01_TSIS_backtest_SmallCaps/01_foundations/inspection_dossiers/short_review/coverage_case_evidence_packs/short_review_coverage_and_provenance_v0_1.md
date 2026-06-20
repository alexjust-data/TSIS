# Short Review Coverage And Provenance Evidence v0.1

This casepack documents physical coverage and provenance for:

```text
short_review_finra_v0_1
```

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/short_review_compact_file_count_summary_v0_1.csv` | Compact physical file counts. |
| `../evidence_assets/short_review_normalized_file_counts_v0_1.csv` | Normalized per-ticker parquet counts. |
| `../evidence_assets/short_review_artifact_manifest_summary_v0_1.csv` | Artifact manifest summaries. |
| `../evidence_assets/short_review_log_summary_v0_1.csv` | Download log status summaries. |
| `../evidence_assets/short_review_provenance_assets_v0_1.csv` | Provenance asset presence. |

## Physical Footprint

| Segment | Logical group | Files |
| --- | --- | ---: |
| `artifacts` | aggregate artifacts/manifests | 4 |
| `logs` | download logs | 2 |
| `normalized` | short interest | 4,687 |
| `normalized` | short volume | 4,623 |
| `raw` | short interest | 193 |
| `raw` | short volume | 11,676 |

## Download Logs

| Log | Rows | Status summary |
| --- | ---: | --- |
| `download_short_interest_raw.csv` | 240 | `ok=189`, `exists=4`, `http_error=47` |
| `download_short_volume_raw.csv` | 3,234 | `exists=3108`, `http_error=126` |

## Interpretation

The source package has strong provenance for the official/free FINRA baseline.
Download-log `http_error` rows are part of the documented source-recovery
surface and must be reviewed before any claim of wider historical completeness.
