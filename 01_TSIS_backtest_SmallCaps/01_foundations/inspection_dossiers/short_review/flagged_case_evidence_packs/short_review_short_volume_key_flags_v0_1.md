# Short Review Short Volume Key Flags v0.1

This casepack documents a scoped technical flag in:

```text
short_review_finra_v0_1
```

The flag affects FINRA short volume aggregate uniqueness.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/short_review_key_quality_v0_1.csv` | Aggregate key uniqueness profile. |
| `../evidence_assets/short_review_short_volume_duplicate_key_manifest_v0_1.csv` | Duplicate `ticker + date` key manifest. |
| `../evidence_assets/short_review_short_volume_duplicate_key_by_ticker_v0_1.csv` | Duplicate keys summarized by ticker. |
| `../evidence_assets/sample_payloads/short_volume_duplicate_key_sample_v0_1.csv` | Concrete duplicate-key row examples. |

## Finding

| Dataset | Key | Rows | Unique keys | Duplicate excess rows |
| --- | --- | ---: | ---: | ---: |
| FINRA short interest | `ticker + settlement_date` | 505,745 | 505,745 | 0 |
| FINRA short volume | `ticker + date` | 4,689,038 | 4,683,788 | 5,250 |

Affected short-volume tickers:

| Ticker | Duplicate keys | Duplicate rows | Excess rows | Date range |
| --- | ---: | ---: | ---: | --- |
| `CPS` | 638 | 5,188 | 4,550 | 2018-08-01 to 2021-02-11 |
| `OP` | 173 | 828 | 655 | 2024-01-23 to 2024-09-27 |
| `LFTR` | 13 | 58 | 45 | 2022-01-20 to 2022-02-10 |

## Interpretation

This does not invalidate `short_review` as a provenance/source baseline.

It does block direct treatment of FINRA short volume as a clean
`ticker + date` analytic table until a future repair or consumer contract
defines one of:

- deduplication;
- aggregation across duplicate source rows;
- source-row preservation at a finer grain;
- explicit exclusion of affected ticker-date rows.

## Consumer Rule

Consumers must not silently collapse duplicate short-volume keys.
