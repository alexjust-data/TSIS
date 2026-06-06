# `price_semantics_and_adjustment_policy` Rules Line By Line

## Purpose

This document rewrites the transversal price-semantics policy in compressed line-by-line form.

It complements:

- `price_semantics_and_adjustment_policy.md`

## 1. General Rule

- There is no single institutional price in the module.
- Every price series must declare `price_basis`, `adjustment_policy`, `corporate_action_scope`, `time_scope`, and `consumer_intent`.

## 2. `quotes_raw`

- Represents observed `bid / ask` book state.
- Primary use: microstructure, crossed diagnostics, execution realism.
- Must not be the default multi-day economic return view.

## 3. `trades_raw`

- Represents observed intraday prints.
- Primary use: activity reconstruction, execution, microstructure validation.
- Must not be the default portfolio valuation view.

## 4. `daily_raw`

- Represents vendor daily bars in their primary operational scale.
- Primary use: vendor audit, OHLCV integrity, daily raw reconciliation.
- Must not be presumed economically adjusted unless explicitly declared.

## 5. `split_normalized`

- Reexpresses price to a coherent split base.
- Primary use: scale reconciliation across time and datasets.
- Main mistake avoided: mistaking split-driven scale mismatch for corruption.

## 6. `adjusted`

- Represents the comparable economic-return view.
- Primary use: returns, factor research, labels, valuation, benchmarking.
- Main mistake avoided: learning or backtesting corporate actions as if they were alpha.

## 7. `adjusted_proxy`

- Represents an internal explanatory approximation of an external adjusted series.
- Primary use: external visual reconciliation and forensic explanation.
- Must not replace the institutional `adjusted` view.

## 8. Reconciliation Workflow

- First identify comparison class: `raw_vs_raw`, `raw_vs_adjusted`, `adjusted_proxy_vs_adjusted`, or `external_series_not_fully_identified`.
- Then check dividends, splits and remaps.
- Then test split-scale reconciliation.
- Then test adjusted or adjusted-proxy reconciliation.
- Only afterwards open a true internal data-error hypothesis.

## 9. Hierarchy Of Truth

- `quotes_raw` and `trades_raw`: primary truth of observed microstructure.
- `daily_raw`: primary truth of vendor daily bars.
- `split_normalized`: primary reconciliation layer for scale.
- `adjusted`: primary truth of economic comparability.
- `adjusted_proxy`: auxiliary explanatory layer only.

## Relation To The General Standard

This document follows:

- `01_foundations/module_contracts/policy_explanation_standard.md`
