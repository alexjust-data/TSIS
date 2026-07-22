# Short Consumption Policy - Modulo 01

## 1. Role

This policy defines how `short` and `short_review` may be consumed inside module 01.

It operationalizes the short dataset contract and does not replace it.

## 2. Primary Principle

Short data is useful but certification-bound.

Consumers must distinguish:

- file presence
- clean lifecycle/reference certification
- limited-window certification
- ticker reuse or reference conflict review
- FINRA official/free source limits

## 3. Consumption By Certification Status

### CERTIFIED_OK

Allowed for:

- `research_only`
- `backtest_extended`
- `ml_flagged`
- event/context studies

Can be considered for stronger use only after a downstream contract defines the exact feature and window.

### CERTIFIED_OK_WITH_LIMITED_WINDOW

Allowed for:

- `research_only`
- `backtest_extended`
- `ml_flagged`

Conditions:

- valid window must travel with the data
- no feature may assume full ticker lifetime coverage

### REVIEW_TICKER_REUSE

Allowed for:

- `research_only`
- `forensic_only`

Not allowed for:

- `backtest_core`
- `ml_primary`
- automated labels/features without identity disambiguation

### REVIEW_REFERENCE_CONFLICT

Allowed for:

- `research_only`
- `forensic_only`

Not allowed for:

- `backtest_core`
- `ml_primary`
- automated consumption without reference reconciliation

## 4. FINRA Review Layer

`short_review\finra_short` is an official/free baseline and provenance layer.

Dataset-specific contracts:

- `01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml`
- `01_foundations/data_consumption_policies/short_review_consumption_policy.md`

Allowed for:

- source validation
- coverage comparison
- forensic review
- rebuilding modern short-volume and short-interest features with documented source scope

Not allowed as:

- silent replacement for `short`
- proof of 2005-2026 completeness

## 5. Short Volume Rules

- Do not treat FINRA short volume as full consolidated market short volume.
- Preserve venue scope and breakdown fields.
- Do not claim pre-2018 official/free short-volume completeness.
- `short_volume_ratio` must be interpreted in source scope, not as universal market shorting pressure.

## 6. Short Interest Rules

- Use `settlement_date` as the observation date.
- Treat short interest as slow/biweekly crowding information.
- Do not use it as same-day intraday causal evidence without lag assumptions.
- Pre-modern FINRA semantics require caution per source research.

## 7. Non-Enabled Consumers

This policy does not automatically enable:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 8. Final Rule

Short data is institutionally useful, but only with certification status, source scope and date-window limits preserved.
