# `quotes` Rules Explained Line By Line

## Purpose

This document rewrites the `quotes` policy stack in compressed line-by-line form.

It complements:

- `quotes_acceptance_policy_explained.md`
- `quotes_label_taxonomy_and_cut_policy.md`
- `quotes_consumption_policy.md`

## 1. Core Interpretation Rules

- `quotes` answers the state of the observed book, not the final causal explanation of the day.
- External context can explain an episode, but it does not automatically rehabilitate local book quality.
- Local book quality must be judged before external narrative is used.

## 2. Final Local States

- `good`: acceptable for the strictest institutional use of the block.
- `review`: not clean enough for `good`, not uniformly severe enough for `bad`.
- `bad`: too aggressive for normal core use even after contextual explanation.

## 3. Good Families

- `clean_pass_or_other`: maps to `good`.
- `soft_crossed_micro_noise`: maps to `good`.
- `persistent_soft_crossed_low`: maps to `good`.
- `utc_rollover_large_day_clean`: maps to `good`.

## 4. Review Families

- `persistent_soft_crossed_mid_large_scale`: maps to `review`.
- `large_file_threshold_edge_hard_many_crosses`: maps to `review`.

## 5. Bad Families

- `medium_file_threshold_edge_hard_many_crosses`: maps to `bad`.
- `high_hard_crossed_10_to_20`: maps to `bad`.

## 6. Economic Severity Rules

- `halt` or other context may explain an episode, but does not neutralize severe positive crossed by itself.
- The decisive severity signal is positive crossed with `ask > 0`.
- `mild` crossed does not imply exclusion by itself.
- `moderate` crossed opens caution and often `review`.
- `severe` crossed hardens the reading toward `bad` when the positive crossed remains economically alive.

## 7. `ask = 0` Rules

- `ask = 0` may create dramatic-looking episodes.
- `ask = 0` is not automatically equivalent to live positive crossed with economic ask.
- Degenerate `ask = 0` behavior must be separated from positive crossed that survives with `ask > 0`.

## 8. Consumption Rules

- `good` is allowed for `backtest_core`, `backtest_extended`, `ml_flagged`, `research_only`.
- `review` is allowed for `backtest_extended`, `ml_flagged`, `research_only`.
- `bad` is `forensic_only`.
- `review` must travel with explicit review semantics; it must not be presented as equivalent to `good`.
- `bad` must not enter `backtest_core`, `backtest_extended` or `ml_flagged`.

## 9. Price-View Rules

- Execution and microstructure work use `quotes_raw` and `trades_raw`.
- Forensic reconciliation may use `quotes_raw`, `split_normalized`, `adjusted_proxy`.
- `quotes_raw` must not be the primary multi-day economic return view.

## 10. Inspector-Evidence Rules

- Every quotes image must explain whether the observed stress is economic, structural or mixed.
- Every graph must declare `que muestra`.
- Every graph must declare `responde`.
- Every graph must declare `no responde`.
- Every graph must declare `consecuencia`.
- A causal explanation does not by itself prove that the local book is clean.

## Relation To The Explanatory Standard

This document follows:

- `01_foundations/module_contracts/policy_explanation_standard.md`
