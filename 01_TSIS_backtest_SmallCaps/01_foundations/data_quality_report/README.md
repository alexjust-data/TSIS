# Data Quality Report

## Role

`data_quality_report/` is the Data Foundation reporting layer for the physical data roots under `E:/TSIS/data`.

Its job is to answer one institutional question:

```text
Can TSIS trust this data family for its declared role and declared consumers?
```

This report does not replace:

- canonical schemas;
- dataset contracts;
- dataset registry entries;
- data consumption policies;
- validators;
- inspection dossiers;
- evidence assets.

It summarizes and normalizes them into a common audit surface for humans and agents.

## Authority Rule

`E:/TSIS/data` is the physical data plane.

`01_foundations` is the semantic and audit authority.

Therefore, `data_quality_report/` lives in:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_quality_report/
```

and points back to physical roots only as audited storage locations.

## Status Separation Rule

`data_quality_report/` records the audit verdict and gives auditors a normalized entry point.

It does not, by itself, prove that every required foundation surface is complete.

The completion rule lives in:

```text
../FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
```

Every family must separate:

| Axis | Meaning |
| --- | --- |
| `data_quality_verdict` | What the audit concluded about the data. |
| `foundations_completion_status` | Whether the family is complete enough across `01_foundations` for a human inspector. |

Therefore:

- a blocked family can still be `human_inspector_ready`;
- a usable family can still be `dossier_partial`;
- a quality report can exist while `inspection_dossiers/<family>/` remains incomplete.

## Families In Scope

Initial physical roots:

- `E:/TSIS/data/additional`
- `E:/TSIS/data/financial`
- `E:/TSIS/data/Halts`
- `E:/TSIS/data/intraday_regime_features`
- `E:/TSIS/data/ohlcv_1m_split_normalized`
- `E:/TSIS/data/ohlcv_daily_adjusted`
- `E:/TSIS/data/reference`
- `E:/TSIS/data/regime_indicators`
- `E:/TSIS/data/short_review`

Core market physical roots now imported into this report format:

- `E:/TSIS/data/ohlcv_daily`
- `E:/TSIS/data/quotes`
- `E:/TSIS/data/trades_ticks_prod_2005_2026`
- `E:/TSIS/data/ohlcv_1m`
- `E:/TSIS/data/ohlcv_1m_split_normalized`

## Required Report Structure Per Family

Each family report must contain:

1. Scope and role.
2. Physical roots and source lineage.
3. Artifact map.
4. File structure and technical profile.
5. Schema expected vs schema observed.
6. Population and coverage.
7. Cleanliness and interpretability.
8. Semantic quality.
9. Case evidence.
10. Consumer matrix.
11. Verdict.
12. Open debt.

The structure follows:

- `../DATA_AUDIT_QUALITY_STANDARD.md`
- `../DATA_AUDIT_TOPIC_NAVIGATION.md`

## Required Evidence Per Family

At minimum, each family must point to or create:

- contract evidence;
- schema evidence;
- registry evidence;
- policy evidence;
- validator/check evidence;
- physical root audit;
- technical profile;
- quality tables;
- population summary;
- case evidence or a documented reason why casepacks do not apply;
- final human readout.

## Data Quality Status Classes

Use these data-quality classes consistently:

- `complete_import_ready`: existing audit is strong enough to import into this report format.
- `complete_scoped`: complete for a declared scope, but not for every possible downstream use.
- `provisional`: useful evidence exists, but one or more required report sections are missing.
- `blocked`: known defect or missing authority prevents institutional consumption.
- `not_started`: no usable modern audit surface exists.

These are not completion classes. Completion classes are defined in:

```text
../FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
```

## Working Order

The first pass must not re-audit complete families from scratch.

Priority order:

1. Families with blocking or missing audit authority.
2. Families with accepted evidence but no standalone quality report.
3. Families with scoped completion that need normalized reporting.
4. Families already complete, imported last as reference-quality reports.

## Current Index

- `family_status_matrix_v0_1.md`

Family-specific reports will be added under:

```text
families/
```

Current family reports:

- `families/additional_quality_report_v0_1.md`
- `families/daily_adjusted_quality_report_v0_1.md`
- `families/daily_quality_report_v0_1.md`
- `families/financial_quality_report_v0_1.md`
- `families/halts_quality_report_v0_1.md`
- `families/intraday_regime_features_quality_report_v0_1.md`
- `families/ohlcv_1m_raw_quality_report_v0_1.md`
- `families/ohlcv_1m_split_normalized_quality_report_v0_1.md`
- `families/quotes_quality_report_v0_1.md`
- `families/reference_quality_report_v0_1.md`
- `families/regime_indicators_quality_report_v0_1.md`
- `families/short_review_quality_report_v0_1.md`
- `families/trades_quality_report_v0_1.md`

## Rule Final

No family is considered complete in `data_quality_report/` until a human auditor can understand:

- what files exist;
- what each file contains;
- what was expected;
- what was observed;
- what is clean;
- what is dirty;
- what is missing;
- what is blocked;
- what can be consumed;
- what must not be consumed;
- and which evidence supports the verdict.
