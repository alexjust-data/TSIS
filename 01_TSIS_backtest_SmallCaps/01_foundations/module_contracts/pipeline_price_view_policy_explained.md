# `pipeline_price_view_policy` Explained

## Purpose

This document explains, in plain but rigorous terms, why each major pipeline in the module uses a different price view.

The formal source remains:

- `01_foundations/module_contracts/pipeline_price_view_policy.md`

This companion does not redefine the rule.
It explains the rule and the mistake each choice avoids.

## Core Principle

There is no single price view that is valid for:

- execution,
- return research,
- benchmarking,
- ML labels,
- and forensic reconciliation

at the same time.

The right price view depends on the question being asked.

## Why forensic reconciliation uses `daily_raw`, `quotes_raw`, `trades_raw`, `split_normalized`, `adjusted_proxy`

Forensic reconciliation is not trying to compute economic returns.
It is trying to answer:

- what was observed
- whether scale is mismatched
- whether a discrepancy is mechanical or economic
- and whether an external chart is using another semantic basis

That is why it needs:

- `daily_raw`
- `quotes_raw`
- `trades_raw`
- `split_normalized`
- `adjusted_proxy`

and not only `adjusted`.

If only `adjusted` were used, the investigator could lose the difference between:

- raw observed scale
- split-driven scale mismatch
- and external adjustment mismatch

## Why execution research uses `quotes_raw` and `trades_raw`

Execution research studies:

- spread
- slippage
- crossed
- local liquidity
- and sequence of observed prints and book states

Those are properties of the raw book and raw tape.

They are **not** properties of an economically adjusted series.

If `adjusted` were used as the primary execution view, the research would stop reflecting:

- what could actually be hit or lifted
- and what was actually printed

So the raw views are mandatory.

## Why signal research uses `adjusted`

Signal research needs comparable economic returns.

Without adjustment:

- splits look like false shocks
- dividends look like false negative returns
- and models or backtests can learn corporate actions as if they were alpha

That is why the primary signal view must be:

- `adjusted`

## Why valuation and benchmarking use `adjusted`

Valuation and benchmark comparison do not want to know only what raw price was observed.

They want to know:

- economic trajectory
- comparable PnL
- comparable drawdown
- comparable benchmark-relative performance

So the primary view must again be:

- `adjusted`

Using `daily_raw` by default here would distort:

- curves
- drawdowns
- and benchmark comparisons

across corporate actions.

## Why ML microstructure uses raw views

Microstructure features describe:

- book shape
- liquidity deterioration
- print clustering
- venue behavior
- crossed behavior

These are properties of:

- `quotes_raw`
- `trades_raw`

An adjusted price view would destroy or blur the object being modeled.

## Why ML daily labels use `adjusted`

Daily ML labels try to predict economic return objects.

So the label view must normally be:

- `adjusted`

Otherwise the model may learn:

- split mechanics
- dividend mechanics

instead of true economic signal.

## Why this policy matters institutionally

This policy avoids three major institutional errors:

1. using a single price view for all departments
2. treating raw execution prices as if they were multi-day economic return series
3. treating adjusted return views as if they were execution-realistic

## Relation To The General Standard

The transversal explanation rule lives in:

- `01_foundations/module_contracts/policy_explanation_standard.md`
