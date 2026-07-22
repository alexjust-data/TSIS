# `pipeline_price_view_policy` Rules Line By Line

## Purpose

This document rewrites the transversal pipeline price-view policy in compressed line-by-line form.

It complements:

- `pipeline_price_view_policy.md`
- `pipeline_price_view_policy_explained.md`

## 1. Forensic Reconciliation

- Primary views: `daily_raw`, `quotes_raw`, `trades_raw`.
- Auxiliary views: `split_normalized`, `adjusted_proxy`.
- Main question: what was observed, and what kind of mismatch explains the discrepancy?
- Main mistake avoided: collapsing raw, split-scale and adjusted mismatches into one undifferentiated "price error".

## 2. Execution Research

- Primary views: `quotes_raw`, `trades_raw`.
- Auxiliary views: `split_normalized` when historical scale reconciliation is needed.
- Main question: what could be executed, at what spread, with what local liquidity and tape texture?
- Main mistake avoided: using an adjusted return view as if it represented an executable book.

## 3. Signal Research

- Primary view: `adjusted`.
- Auxiliary views: `daily_raw`, `split_normalized`.
- Main question: what is the comparable economic return object for signal construction?
- Main mistake avoided: letting splits or dividends look like predictive returns.

## 4. Portfolio Valuation

- Primary view: `adjusted`.
- Main question: how does portfolio value evolve economically through time?
- Main mistake avoided: distorting PnL and drawdown through raw corporate-action discontinuities.

## 5. Benchmarking

- Primary view: `adjusted`.
- Main question: how does strategy performance compare to a benchmark on the same economic basis?
- Main mistake avoided: benchmark mismatch created by corporate actions rather than by strategy behavior.

## 6. ML Microstructure Features

- Primary views: `quotes_raw`, `trades_raw`.
- Auxiliary sources: `halts`, `news`, `short_volume` when relevant.
- Main question: what local market-structure state is being modeled?
- Main mistake avoided: destroying the tape-level object through adjusted or smoothed price semantics.

## 7. ML Daily Labels

- Primary view: `adjusted`.
- Main question: what economic return object is the model trying to predict?
- Main mistake avoided: learning split or dividend mechanics as if they were alpha.

## 8. External Comparison

- Required views: some combination of `daily_raw`, `split_normalized`, `adjusted_proxy`, depending on the case.
- Main question: is the difference explained by raw scale, split normalization or external adjustment?
- Main mistake avoided: treating every external chart mismatch as proof of internal data error.

## Relation To The General Standard

This document follows:

- `01_foundations/module_contracts/policy_explanation_standard.md`
