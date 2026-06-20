# Short Review FINRA Baseline Good Cases v0.1

This file documents positive scoped evidence for:

```text
short_review_finra_v0_1
```

The evidence supports official/free FINRA baseline and provenance use. It does
not promote a production short dataset replacement.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/short_review_aggregate_profile_v0_1.csv` | Aggregate rows, tickers, date ranges and schemas. |
| `../evidence_assets/short_review_numeric_sanity_v0_1.csv` | Numeric fields have no negative rows or infinite rows in aggregate artifacts. |
| `../evidence_assets/short_review_provenance_assets_v0_1.csv` | Build notes, source research, manifests, logs and pipeline are present. |
| `../evidence_assets/short_review_sample_payload_manifest_v0_1.csv` | Representative payload samples for common tickers. |

## Aggregate Baseline

| Dataset | Rows | Tickers | Date range |
| --- | ---: | ---: | --- |
| FINRA short interest | 505,745 | 4,687 | 2017-12-29 to 2026-04-15 |
| FINRA short volume | 4,689,038 | 4,623 | 2018-08-01 to 2026-04-29 |

## Numeric Sanity

Aggregate numeric sanity checks found:

- no negative rows in numeric quantity columns;
- no infinite rows;
- no date nulls in the aggregate date columns.

## Provenance

The following provenance assets are present:

- `finra_short_build_status.md`;
- `research_short_sources.md`;
- `short_data_recovery_plan.md`;
- `finra_short/README.md`;
- aggregate artifact manifests;
- raw download logs;
- `finra_short_pipeline.py`.

## Allowed Reading

This family can be used for:

- official/free source validation;
- FINRA coverage comparison;
- forensic review;
- scoped research with explicit date/source caveats.
