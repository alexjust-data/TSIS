# Short Review Validators

## Scope

This validator contract governs:

```text
short_review_finra_v0_1
```

Physical root:

```text
E:/TSIS/data/short_review/finra_short
```

## Authorities

Read with:

- `contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `data_consumption_policies/short_review_consumption_policy.md`
- `dataset_registry/short_review/short_review_registry_entry.yaml`
- `canonical_schemas/short_review/`
- `inspection_dossiers/short_review/short_review_inspection_readout_v0_1.md`
- `data_quality_report/families/short_review_quality_report_v0_1.md`

## Validation Units

| Subfamily | Validation unit |
| --- | --- |
| FINRA short interest | `ticker + settlement_date` |
| FINRA short volume | `ticker + date` |
| raw short volume downloads | `date + prefix + venue + file` |
| raw short interest downloads | `settlement_date + file` |
| provenance logs | source download event |
| manifests | aggregate artifact |

## Required Checks

### Root And Layout

The validator must check:

- root exists: `E:/TSIS/data/short_review/finra_short`;
- subroots exist:
  - `raw`;
  - `normalized`;
  - `artifacts`;
  - `logs`;
- root README exists;
- build status and research notes exist under `E:/TSIS/data/short_review`.

### Short Interest

Required checks:

- aggregate parquet exists;
- normalized per-ticker parquet files exist;
- required columns exist:
  - `settlement_date`;
  - `ticker`;
  - `short_interest`;
  - `avg_daily_volume`;
  - `days_to_cover`;
- date range is emitted;
- ticker count is emitted;
- rows are nonnegative where applicable;
- settlement-date cadence is treated as slow/biweekly information.

### Short Volume

Required checks:

- aggregate parquet exists;
- normalized per-ticker parquet files exist;
- required columns exist:
  - `ticker`;
  - `date`;
  - `total_volume`;
  - `short_volume`;
  - `exempt_volume`;
  - `non_exempt_volume`;
  - `short_volume_ratio`;
  - venue/source components;
- date range is emitted;
- ticker count is emitted;
- `ticker + date` uniqueness is emitted;
- volume fields are nonnegative;
- `short_volume_ratio` is source-scope and must not be interpreted as consolidated market shorting pressure.
- duplicate `ticker + date` keys produce a review/blocking flag for direct analytic consumption until handling semantics are defined.

### Provenance

Required checks:

- manifests parse;
- download logs parse;
- raw files exist for declared ranges;
- source URLs/status fields are preserved where available;
- official/free source scope is explicit.

### Comparison To Local `short`

The validator must emit:

- intersection with local/Polygon `short_volume`;
- local-only `short_volume`;
- FINRA-only `short_volume`;
- intersection with local/Polygon `short_interest`;
- local-only `short_interest`;
- FINRA-only `short_interest`.

Current known values:

| Comparison | Intersection | Local-only | FINRA-only |
| --- | ---: | ---: | ---: |
| `short_volume` | 4,623 | 201 | 0 |
| `short_interest` | 4,687 | 137 | 0 |

## Current Observed Status

| Dataset | Rows | Tickers | Date range |
| --- | ---: | ---: | --- |
| FINRA short interest | 505,745 | 4,687 | `2017-12-29` to `2026-04-15` |
| FINRA short volume | 4,689,038 | 4,623 | `2018-08-01` to `2026-04-29` |

Current key quality:

| Dataset | Key | Rows | Unique keys | Duplicate excess rows |
| --- | --- | ---: | ---: | ---: |
| FINRA short interest | `ticker + settlement_date` | 505,745 | 505,745 | 0 |
| FINRA short volume | `ticker + date` | 4,689,038 | 4,683,788 | 5,250 |

Short-volume duplicate-key rows are concentrated in `CPS`, `OP` and `LFTR`.

## Acceptance States

Allowed states:

- `official_free_baseline_provenance`;
- `coverage_comparison_ready`;
- `research_only_with_scope`;
- `blocked_as_short_replacement`;
- `short_volume_key_flags_require_handling`;
- `paid_gap_required_for_full_history`.

Current family state:

```text
official_free_baseline_provenance
```

## Forbidden Conclusions

The validator must not conclude:

- `short_review` replaces `short`;
- FINRA free data proves full 2005-2026 completeness;
- short volume is consolidated market-wide pressure;
- duplicate short-volume keys can be silently collapsed;
- short interest is same-day intraday causal evidence;
- local-only tickers are bad without review.

## Output Contract

A compliant validator or readout must emit:

- source scope;
- date windows;
- ticker coverage;
- local-vs-FINRA comparison;
- known official/free gaps;
- short-volume duplicate-key profile;
- provenance artifacts;
- consumer restrictions.
