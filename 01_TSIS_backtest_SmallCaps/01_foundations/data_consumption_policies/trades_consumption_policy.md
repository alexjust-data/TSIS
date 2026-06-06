# `trades` Consumption Policy

## Purpose

This document defines how `trades` labels map into real pipeline usage.

It complements:

- [trades_dataset_contract_v0_1.md](../contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md)
- [trades_label_taxonomy_and_cut_policy.md](../contract_registry/dataset_contracts/trades_label_taxonomy_and_cut_policy.md)
- [pipeline_price_view_policy.md](../module_contracts/pipeline_price_view_policy.md)
- [policy_explanation_standard.md](../module_contracts/policy_explanation_standard.md)
- [trades_acceptance_policy_explained.md](../module_contracts/trades_acceptance_policy_explained.md)

The policy is designed around one core principle:

- `trades` is a raw execution and microstructure layer first
- not a generic economic price layer

## Primary Native View

Primary native price view for this dataset:

- `trades_raw`

Reference and reconciliation views that may accompany it:

- `split_normalized`
- `adjusted_proxy`
- eventually institutional `adjusted`

## Final Certification States

The final operational vocabulary for `trades` is not just the file-level label list.

It is:

- `good`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

This policy therefore works in two stages:

1. read the file-level label
2. decide whether that label is already final-bad, final-good, recoverable-with-flag, or still non-rehabilitated

## Pipeline Mapping

### 1. Execution Research

Primary status:

- `trades_raw` is required

Default final states allowed:

- `good`
- `recoverable_with_flag`

Conditionally inspectable:

- `review_not_rehabilitated`

Disallowed by default:

- `bad`

Why:

Execution research studies observed tape behavior, not adjusted portfolio returns. A file can still be useful for execution realism even if it compares badly to `daily`, provided the disagreement is explained by tape structure, missing reference support or scale mismatch rather than intrinsic corruption.

### 2. Microstructure Feature Engineering

Primary status:

- `trades_raw` is required

Default final states allowed:

- `good`
- `recoverable_with_flag`

Conditionally inspectable:

- `review_not_rehabilitated`

Disallowed by default:

- `bad`

Why:

Features like trade clustering, size structure, venue mix and condition-code behavior remain meaningful when the tape is structurally plausible even if benchmark comparison is hard.

### 3. Direct Comparison Against `daily` / `1m`

Primary status:

- not a standalone consumption pipeline
- treated as forensic / reconciliation work

Required views:

- `trades_raw`
- `daily_raw` or `1m` reference
- `split_normalized`
- optionally `adjusted_proxy`

Allowed final states:

- all of them, but with explicit interpretation

Why:

This pipeline diagnoses why disagreement exists. It is not a simple accept/reject pipeline. Therefore all states may be inspected, but no naive promotion from disagreement to bad tape is allowed.

### 4. Daily Return Labels / Portfolio Benchmarking

Primary status:

- `trades_raw` is not the primary series

Allowed usage:

- supporting evidence only
- not the main return series

Why:

Portfolio returns, benchmarking and cross-sectional daily labels must be built from `adjusted` daily semantics, not from raw print-by-print tape.

### 5. ML Daily Labels

Primary status:

- `trades` may support labels or diagnostics
- but is not itself the canonical daily-target layer

Allowed support roles:

- validating unusual daily events
- enriching execution-aware or microstructure-aware samples
- diagnosing label disagreement

Disallowed by default:

- using raw trades as the daily target view

Why:

Financial ML requires separation between observation layer and target construction. Raw execution data and economically comparable daily labels are not interchangeable.

## File-Level Label To Final-State Mapping

### `good`

Final state:

- `good`

Allowed:

- all execution and microstructure uses
- eligible supporting evidence in reconciliation

### `bad_data`

Final state:

- `bad`

Allowed:

- forensic-only

Disallowed:

- execution production research
- microstructure model training
- direct benchmark comparison
- automated label support

### `review_no_1m_reference`

Default final state:

- `recoverable_with_flag`

Meaning:

- reference support is incomplete, but the tape is not thereby proven corrupt

### Generic `review`

Default final state:

- `recoverable_with_flag` if explicit rehabilitation rule is satisfied
- otherwise `review_not_rehabilitated`

Meaning:

- the class is not final-bad by default
- but it needs rule-based promotion

### `review_microstructure`

Default final state:

- partially `recoverable_with_flag`
- otherwise `review_not_rehabilitated`

Meaning:

- useful as tape, difficult as benchmark-comparable reference object

### `review_1m_reference_alignment`

Default final state:

- partially `recoverable_with_flag`
- otherwise `review_not_rehabilitated`

Meaning:

- important for methodology and reference alignment, not automatically fit for operational promotion

### `reference_scale_mismatch`

Current final state:

- `review_not_rehabilitated` by default

Potential future state:

- `recoverable_with_flag` once stable scale reconciliation is validated

Meaning:

- disagreement is largely semantic or scaling-related
- but the project should not operationally promote it until a validated reconciliation view exists

## Operational Rule

Any downstream use of `trades` must declare:

1. pipeline purpose
2. chosen price view
3. chosen final-state subset
4. whether the task is execution, microstructure, reconciliation or economic return work

Without those four declarations, `trades` use is considered semantically ambiguous and therefore non-compliant.

## Current Practical Summary

Use this shorthand:

- execution / microstructure: `trades_raw`, allow `good` and `recoverable_with_flag`, keep `bad` out
- reconciliation: inspect all, but distinguish semantics from intrinsic tape failure
- daily-return / benchmark work: do not use `trades_raw` as the primary price series
- ML labels: use `adjusted` daily semantics; use `trades` only as support or microstructure context

## Important Pending Work

This policy already encodes the final certification semantics from `certification/trades`, but the visual evidence layer is still pending in `01_foundations`.

Before a final institutional `trades` readout is declared closed, the future inspection pack should reuse the historical certification images for:

- `reference_scale_mismatch`
- `review_microstructure`
- `review_1m_reference_alignment`
- `bad_data`
- `review_no_1m_reference`
- generic `review`
- `good`
- and the aggregated population views from `11_d_full_final_bucket_distribution.png` and `12_d_full_scale_contamination_by_bucket.png`
## Actualizacion cuantitativa de la rehabilitacion

La politica de consumo de `trades` ya no debe apoyarse solo en el parcial historico `57e/full_clean`.

Sobre el cache canonico real:

- `root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema`

la rematerializacion del bucket `review` da:

- `review_total = 4,851,211`
- `review_recoverable_strict = 3,327,955` (`68.6005%`)
- `review_not_rehabilitated_strict = 1,523,256`
- `review_recoverable_extended = 3,505,290` (`72.2560%`)
- `review_not_rehabilitated_extended = 1,345,921`

Consecuencia de policy:

- `backtest_extended` y `ml_flagged` pueden seguir usando `review` rehabilitable estricto como baseline;
- pero ya no debe presentarse el bucket `review` como mayoritariamente limpio por inercia del parcial `57e`;
- la parte no rehabilitada sigue siendo demasiado grande como para trivializar el flag.

La policy no debe parar ahi, porque `review` no es la unica familia parcialmente util.

Sobre el mismo cierre real, y con recuperacion operativa provisional anclada en la semantica historica de `certification`, tambien aparece:

- `review_microstructure_total = 2,130,781`
- `review_microstructure_recoverable_strict_provisional = 1,516,547` (`71.1733%`)
- `review_microstructure_recoverable_extended_provisional = 1,636,379` (`76.7971%`)
- `review_1m_reference_alignment_total = 4,992`
- `review_1m_reference_alignment_recoverable_strict_provisional = 2,591` (`51.9030%`)
- `review_1m_reference_alignment_recoverable_extended_provisional = 3,715` (`74.4191%`)

Consecuencia de policy:

- `execution_research` y `microstructure_feature_engineering` pueden tratar parte de `review_microstructure` como masa util bajo flag cuando el uso tolere conflicto de comparabilidad fina;
- `review_1m_reference_alignment` no debe verse como residuo irrelevante: es pequeno en masa, pero metodologicamente importante porque revela conflicto precisamente cuando se abre el arbitro `1m`;
- ningun pipeline debe promocionar estas familias a `good`;
- y toda promocion a `recoverable_with_flag` debe quedar trazada como rehabilitacion explicita, no como aceptacion por defecto.
