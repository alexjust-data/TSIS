# Regime Indicators Minute Review Cases v0.1

This casepack documents scoped minute-file evidence for:

```text
regime_indicators_v0_1
```

Minute bars are not blocked by the daily 1970 date defect, but they are not
production feature-ready.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/regime_indicators_minute_schema_review_v0_1.csv` | Per-file minute timestamp and schema review. |
| `../evidence_assets/regime_indicators_minute_flagged_issue_manifest_v0_1.csv` | Minute files with observed issue flags. |
| `../evidence_assets/sample_payloads/minute_high_lt_low_issue_samples_v0_1.csv` | Concrete `high < low` examples. |

## Positive Review Findings

| Metric | Value |
| --- | ---: |
| Minute files | 33 |
| Minute rows | 64,348,953 |
| Duplicate timestamp rows | 0 |
| Non-monotonic files | 0 |
| Negative ETF volume rows | 0 |

## Flagged Finding

| Metric | Value |
| --- | ---: |
| Minute files with `high < low` rows | 1 |
| Total `high < low` rows | 204 |
| Affected file | `etfs/UVXY/minute.parquet` |

Representative issue:

```text
timestamp = 2018-05-01 20:45:00
high = 181862.0
low = 181862.5
```

## Interpretation

The minute files are suitable for source validation and scoped research
inspection. They are not yet suitable as a production feature-store input.

The next minute audit must include:

- complete OHLC sanity classification;
- timestamp coverage and gap analysis;
- session/timezone interpretation;
- ETF/index symbol mapping;
- policy for split/reverse-split-sensitive ETF proxies such as `UVXY`.
