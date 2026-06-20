# Financial Blocking Schema Cases v0.1

## Role

This document records the blocking severe issue family in `financial_v0_1`.

The issue is not hidden in prose. It is materialized in:

```text
../evidence_assets/financial_severe_issue_summary_v0_1.csv
../evidence_assets/financial_severe_issue_sample_manifest_v0_1.csv
../evidence_assets/financial_empty_sentinel_example_manifest_v0_1.csv
```

## Severe Issue Summary

| Dataset | Issue | Count |
| --- | --- | ---: |
| `income_statements` | `missing_required_cols` | 4,443 |
| `balance_sheets` | `missing_required_cols` | 4,449 |
| `cash_flow_statements` | `missing_required_cols` | 4,445 |
| `ratios` | none observed | 0 |

Total severe issues:

```text
13,337
```

## Representative Blocking Pattern

Representative sentinel file:

```text
E:/TSIS/data/financial/income_statements/ticker=AABA/income_statements_AABA.parquet
```

Observed form:

```text
ticker, _empty, _dataset, _ingested_utc
```

Observed business rows:

```text
0
```

Operational audit issue:

```text
missing_required_cols = cik
issues = missing_required_cols
```

## Why This Blocks

The schema contracts allow empty sentinel files as a physical no-data form.

The operational audit still flags many zero-business statement files as severe `missing_required_cols` because the statement payload required fields, especially `cik`, are absent.

This creates a governance conflict:

```text
empty sentinel accepted by schema
vs
empty statement sentinel flagged severe by operational audit
```

Until resolved, the family cannot be promoted.

## What A Human Inspector Should Check

Use:

```text
../evidence_assets/financial_empty_sentinel_example_manifest_v0_1.csv
../evidence_assets/sample_payloads/income_statements_AABA_sample_v0_1.csv
../evidence_assets/sample_payloads/ratios_AABA_sample_v0_1.csv
```

Inspect whether:

- the sentinel form is intentional;
- no business row is present;
- `_empty = True`;
- `_dataset` is correct;
- `_ingested_utc` is present and parseable;
- missing `cik` should be a severe defect or an allowed sentinel condition.

## Possible Resolutions

Valid future resolutions require a versioned decision:

1. Treat statement sentinels as valid no-data forms and update validator severity.
2. Require sentinel files to include `cik` or another identity field.
3. Split the issue into `no_data_sentinel` and `missing_required_cols_payload`.
4. Keep the current severe issue and block promotion.

No resolution should be implicit.
