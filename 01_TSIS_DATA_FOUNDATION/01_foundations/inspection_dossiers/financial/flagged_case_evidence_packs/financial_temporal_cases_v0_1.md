# Financial Temporal Cases v0.1

## Role

This document records temporal and lifecycle evidence for `financial_v0_1`.

It is a flagged/blocking evidence pack, not a production-use approval.

## Evidence Assets

| Asset | Role |
| --- | --- |
| `../evidence_assets/financial_temporal_status_summary_v0_1.csv` | Ticker counts by temporal status. |
| `../evidence_assets/financial_temporal_issue_sample_manifest_v0_1.csv` | Sample temporal issue cases. |
| `../evidence_assets/financial_date_range_summary_v0_1.csv` | Endpoint date ranges and issue counts. |

## Temporal Status Summary

| Temporal status | Tickers |
| --- | ---: |
| `OK` | 4,859 |
| `NO_DATA` | 4,438 |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

The operational audit summary records:

```text
temporal_issues = 3,171
```

## Representative Cases

The sample manifest includes cases such as:

- `AA`: financial data extends after the reference end window;
- `AAC`: financial data begins after the observed lifecycle window and extends after it;
- `A`: financial data begins before and extends after the tight reference window;
- `AAL`: financial data begins before the reference start.

The exact sample rows live in:

```text
../evidence_assets/financial_temporal_issue_sample_manifest_v0_1.csv
```

## Interpretation

Temporal findings must not be collapsed into a simple "bad data" label.

They may reflect:

- incomplete lifecycle/reference windows;
- ticker reuse or identity changes;
- CIK continuity across ticker windows;
- statements filed outside market-trading windows;
- vendor endpoint behavior;
- missing or stale delisting metadata.

But until resolved or explicitly flagged, they block master-table and point-in-time feature promotion.

## Consumer Rule

Financial statements must use `filing_date` for point-in-time availability.

`period_end` is not decision-time availability.

No downstream join may treat this family as clean lifecycle-aligned data until the temporal issue set is:

- repaired;
- filtered;
- or explicitly carried as a versioned flag.
