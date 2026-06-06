# Short Review Consumption Policy v0.1

## 1. Scope

This policy governs `short_review_finra_v0_1`.

It complements `short_consumption_policy.md` and makes the FINRA review layer explicit as its own institutional dataset.

## 2. Primary Rule

`short_review` may be used as official/free FINRA baseline and provenance. It must not be consumed as a silent substitute for `E:\TSIS\data\short`.

Any consumer must preserve:

- source family;
- date window;
- ticker coverage;
- venue/source scope;
- known official/free history gaps.

## 3. Short Interest

Allowed:

- coverage comparison against local `short_interest`;
- source validation;
- slow crowding context;
- flagged research features with explicit lag assumptions.

Rules:

- use `settlement_date`;
- treat as slow/biweekly information;
- do not use as same-day intraday causal evidence without a lag contract;
- do not claim full 2005-2026 completeness.

## 4. Short Volume

Allowed:

- coverage comparison against local `short_volume`;
- source validation;
- daily source-scope short-volume context;
- flagged research features with scope explicitly declared.

Rules:

- use `date`;
- preserve venue/source components;
- treat `short_volume_ratio` as FINRA source-scope ratio;
- do not claim consolidated market-wide shorting pressure;
- do not claim pre-2018 official/free completeness.

## 5. Provenance Assets

Manifests and download logs are audit/provenance assets.

Allowed:

- audit reproducibility;
- source coverage review;
- download diagnostics;
- data lineage documentation.

Not allowed:

- direct model features unless explicitly declared as source-quality metadata;
- replacement for analytic short-interest or short-volume fields.

## 6. Relationship To `short`

`short_review` explains and validates `short`; it does not supersede it.

When both layers are used together, the consumer must report:

- whether the source is FINRA or local/Polygon;
- whether a ticker is in the intersection or local-only set;
- whether the feature relies on `short_interest`, `short_volume`, or both;
- whether the selected date is inside the FINRA available window.

## 7. Non-Enabled Consumers

This policy does not enable:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

Those require a downstream feature contract and explicit validation.
