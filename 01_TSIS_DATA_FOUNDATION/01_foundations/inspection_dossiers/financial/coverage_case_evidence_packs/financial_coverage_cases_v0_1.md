# Financial Coverage Cases v0.1

## Role

This document explains the coverage state of `financial_v0_1`.

Coverage is strong at the endpoint-output level, but it does not override the quality blockers.

## Evidence Assets

| Asset | Role |
| --- | --- |
| `../evidence_assets/financial_coverage_by_endpoint_v0_1.csv` | Endpoint coverage counts. |
| `../evidence_assets/financial_file_level_quality_summary_v0_1.csv` | File and row counts by endpoint. |
| `../evidence_assets/financial_date_range_summary_v0_1.csv` | Business-row and date-range summary by endpoint. |

## Endpoint Coverage

| Dataset | Expected tickers | Downloaded tickers | Missing | Extra | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `income_statements` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `balance_sheets` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `cash_flow_statements` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `ratios` | 12,468 | 12,468 | 0 | 0 | 100.0% |

## File-Level Coverage Reading

| Dataset | Files | Rows total | Business rows | Zero-business files |
| --- | ---: | ---: | ---: | ---: |
| `income_statements` | 12,468 | 496,350 | 491,907 | 4,443 |
| `balance_sheets` | 12,468 | 280,285 | 275,836 | 4,449 |
| `cash_flow_statements` | 12,468 | 495,784 | 491,339 | 4,445 |
| `ratios` | 12,468 | 12,470 | 4,311 | 8,159 |

## Interpretation

The downloader produced one endpoint file per expected ticker for every dataset.

That is a positive operational result.

It does not mean:

- every ticker has business rows;
- the statements are point-in-time usable;
- CIK/lifecycle alignment is solved;
- ratios are complete;
- the family is production-ready.

The main coverage distinction is:

```text
endpoint file coverage = complete
business-data coverage = sparse and quality-gated
```

## Human Inspection Rule

When inspecting this family, start with coverage to verify the downloader completed.

Then move immediately to:

- schema/sentinel severe issues;
- temporal/lifecycle issues;
- point-in-time availability.

Do not present 100% endpoint coverage as a clean-data verdict.
