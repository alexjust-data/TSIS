# Regime Indicators Good/Usable Evidence v0.1

This file documents what is usable for inspection in:

```text
regime_indicators_v0_1
```

It does not promote the family for production consumption.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/regime_indicators_minute_schema_review_v0_1.csv` | Minute files are parseable and timestamp-keyed. |
| `../evidence_assets/regime_indicators_metadata_summary_v0_1.csv` | Root metadata JSON files are parseable. |
| `../evidence_assets/sample_payloads/spy_minute_sample_v0_1.csv` | Representative ETF minute payload. |
| `../evidence_assets/sample_payloads/i_ndx_minute_sample_v0_1.csv` | Representative index minute payload. |

## Minute Positive Findings

| Metric | Value |
| --- | ---: |
| Minute files | 33 |
| Minute rows | 64,348,953 |
| Timestamp nulls | 0 observed in summary |
| Duplicate timestamp rows | 0 |
| Non-monotonic files | 0 |
| Negative ETF volume rows | 0 |

Observed timestamp range:

```text
2004-01-02 13:00:00 to 2025-12-02 14:29:00
```

## Metadata Positive Findings

Root metadata files:

- `download_metadata.json`;
- `ticker_ranges.json`.

Observed metadata shape:

| File | Top-level type | Top-level key count |
| --- | --- | ---: |
| `download_metadata.json` | dict | 2 |
| `ticker_ranges.json` | dict | 34 |

`ticker_ranges.json` is useful as coverage and repair-planning evidence.

## Boundary

This good evidence is scoped:

- it supports source validation and repair planning;
- it supports minute-level forensic review;
- it does not clear daily bars;
- it does not make minute bars production feature-ready;
- it does not permit metadata to silently repair daily bars.
