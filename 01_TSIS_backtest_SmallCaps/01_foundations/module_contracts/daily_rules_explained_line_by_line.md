# `daily` Rules Explained Line By Line

## Purpose

This document rewrites the `daily` policy stack in compressed line-by-line form.

It complements:

- `daily_acceptance_policy_explained.md`
- `daily_dataset_contract_v0_1.md`
- `daily_label_taxonomy_and_cut_policy.md`
- `daily_consumption_policy.md`

## 1. Core Interpretation Rules

- `daily` is governed first by bar integrity and coverage, not by microstructure semantics.
- `vw` is diagnostically important but it is not the single authority of the dataset.
- Final use is decided by combining `quality` and `coverage`.

## 2. Quality Axis

- `good`: bar remains usable without material quality caveat.
- `recoverable_with_flag`: bar is not pristine but still usable under explicit warning.
- `bad`: parse or price integrity is broken strongly enough for hard exclusion.

## 3. Quality Families

- `schema_only_or_other`: remains in `good`.
- `vw_edge_absmax_only`: remains in `good`.
- `vw_low_ratio_limited_days`: maps to `recoverable_with_flag`.
- `vw_mid_ratio_illiquid_regime`: maps to `recoverable_with_flag`.
- `vw_high_ratio_illiquid_regime`: maps to `recoverable_with_flag`.
- `vw_warn_minor_or_material`: maps to `recoverable_with_flag`.
- `hard_invalid_parse_or_price`: maps to `bad`.

## 4. Coverage Axis

- `LIKELY_VALID_GAP_ONLY`: maps to `recoverable_without_penalty`.
- `AMBIGUOUS_REVIEW`: maps to `recoverable_with_flag`.
- `REALLY_PROBLEMATIC_UNEXPECTED`: maps to `review_not_rehabilitated`.

## 5. Final Combined Operational States

- `good`: quality `good` with no degrading coverage state.
- `recoverable_without_penalty`: coverage recoverable without harming core use.
- `recoverable_with_flag`: either quality or coverage ambiguity survives but remains operable with explicit warning.
- `review_not_rehabilitated`: open coverage frontier that must not be quietly promoted.
- `bad`: hard invalid parse or price tail.

## 6. Rules About `vw`

- `vw` disagreement opens diagnosis; it does not automatically invalidate the whole daily bar.
- Edge or illiquid `vw` behavior is typically flagged, not automatically rejected.
- The policy avoids treating every `vw` anomaly as if OHLCV were semantically broken.

## 7. Rules About Coverage

- Missing coverage is not automatically equivalent to bad data.
- Valid-looking gaps can stay in `recoverable_without_penalty`.
- Ambiguous gaps require `recoverable_with_flag`.
- Unexpected problematic gaps stay in `review_not_rehabilitated`.

## 8. Pipeline Rules

- `backtest_core` accepts `good` and `recoverable_without_penalty`.
- `backtest_extended` may also accept `recoverable_with_flag`.
- `ml_primary` accepts `good` and `recoverable_without_penalty`.
- `ml_flagged` may accept `recoverable_with_flag`.
- `research_only` may inspect all non-`bad` states.
- `forensic_only` can inspect every state including `bad`.

## 9. Price-View Rules

- Vendor audit and forensic reconciliation use `daily_raw`, `split_normalized`, `adjusted_proxy`.
- Signal research uses `adjusted`.
- Portfolio valuation uses `adjusted`.
- Daily return labels use `adjusted`.
- `daily_raw` must not be the default return view when cross-corporate-action comparability is required.

## 10. Inspector-Evidence Rules

- Every daily image must say whether it is proving a quality issue, a coverage issue, or both.
- Every daily graph must declare `que muestra`.
- Every daily graph must declare `responde`.
- Every daily graph must declare `no responde`.
- Every daily graph must declare `consecuencia`.

## Relation To The Explanatory Standard

This document follows:

- `01_foundations/module_contracts/policy_explanation_standard.md`
