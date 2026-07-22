# `trades` Label Taxonomy And Cut Policy

## Purpose

This document defines how `trades` labels must be interpreted and cut institutionally.

Interpretive companions:

- `01_foundations/module_contracts/policy_explanation_standard.md`
- `01_foundations/module_contracts/trades_acceptance_policy_explained.md`

It separates three layers that the historical notebooks kept distinct but that are easy to confuse:

1. severity snapshot labels (`PASS`, `SOFT_FAIL`, `HARD_FAIL`)
2. explanatory taxonomies (`confirmed_by_1m_and_not_scale`, etc.)
3. final file-acceptance labels (`review`, `reference_scale_mismatch`, etc.)

The final contractual policy for `trades` must be driven by layer 3, not by layer 1 alone.

## Layer 1: Snapshot Severity

Historical snapshot severity from `04_trades_full_C_D_*`:

- `PASS`
- `SOFT_FAIL`
- `HARD_FAIL`

This layer is useful for:

- population stress
- triage
- concentration analysis
- showing that the universe is structurally pressured

This layer is not sufficient for final operational consumption. A file can enter a severe snapshot bucket but later be reinterpreted as:

- reference mismatch
- odd-lot / microstructure review
- reference-coverage problem
- or a smaller true `bad_data` tail

## Layer 2: Explanatory Families

The historical notebooks identified several explanatory families that matter conceptually, including:

- `confirmed_by_1m_and_not_scale`
- `confirmed_by_1m_and_dup_heavy`
- `not_confirmed_by_1m`
- `below_only`
- `above_only`
- `both`
- scale-factor buckets (`~4x`, `~5x`, `~10x`, etc.)
- odd-lot dominance
- off-session discrepancies

These families matter because they explain why an apparent break exists. But they still do not directly define the operational policy label.

## Layer 3: Final File-Acceptance Labels

The authoritative current full-closeout labels are the ones materialized in `57f/layer6_policy_summary_full.parquet`:

- `good`
- `review`
- `reference_scale_mismatch`
- `review_microstructure`
- `review_no_1m_reference`
- `review_1m_reference_alignment`
- `bad_data`

These are the labels that must drive file-level acceptance policy in `01_foundations`.

## Full Final Counts

Current final counts from the full `<1B>` closeout are:

- `review = 4,851,211`
- `reference_scale_mismatch = 2,418,062`
- `review_microstructure = 2,130,781`
- `bad_data = 15,869`
- `review_no_1m_reference = 8,091`
- `review_1m_reference_alignment = 4,992`
- `good = 106`

## Interpretation Of Each Final Label

### `good`

Meaning:

- the file remains usable without material tape-level concern under the current policy
- disagreement with references is absent or de minimis after conservative reading

Important caution:

- the full-closeout leaves only `106 good` files
- therefore `good` must not be assumed to represent the typical state of the raw trades universe

### `review`

Meaning:

- the file remains unresolved enough to require caution
- but the evidence does not justify immediate classification as intrinsically bad tape

This is the generic residual review class, not the same as population-level `SOFT_FAIL`.

### `reference_scale_mismatch`

Meaning:

- disagreement against `daily` or `1m` is dominated by scale inconsistency between tape and reference
- the raw trade tape may be internally plausible while reference comparison is semantically mismatched

This label is one of the most important discoveries of the historical audit.

### `review_microstructure`

Meaning:

- the file is not best explained by gross corruption
- the conflict is more consistent with odd-lot behavior, tape microstructure, or hard comparability of raw prints to aggregated references

This must not be treated as equivalent to `bad_data`.

### `review_no_1m_reference`

Meaning:

- conflict exists against `daily`
- but confirmation or rejection through `1m` is unavailable or insufficient

This is fundamentally a reference-coverage / comparability label, not a statement that the raw tape is broken.

### `review_1m_reference_alignment`

Meaning:

- the file produces an awkward configuration where `daily` and `VWAP` style references can appear aligned while `1m` still breaks materially in a conservative core view

These are high-interest forensic cases because they test whether `1m` itself, rather than `trades`, is the misaligned layer.

### `bad_data`

Meaning:

- after the full-closeout logic, the remaining file still looks best explained as intrinsically untrustworthy tape material
- it cannot be safely reduced to scale mismatch, odd-lot comparability, or reference coverage gaps

This is the true hard-negative tail for `trades`.

## Why `bad_data` must stay separate from `review`

Even though `bad_data` is small relative to the full population, keeping it separate is institutionally necessary.

Why:

- it prevents an overly optimistic reading of the file-level sample
- it preserves a true forensic-only exclusion bucket
- it avoids the methodological error of calling all residual conflict "just microstructure"

Operationally, this is the bucket that protects downstream execution research, microstructure features and benchmark comparisons from learning on tape that remains intrinsically suspect.

## Cut Logic Principles

The final cut policy must obey these principles:

1. never infer `bad_data` from snapshot severity alone
2. never infer `bad_data` from disagreement against `daily` alone
3. prefer explanatory labels when scale mismatch, session, odd-lot structure or reference gaps dominate
4. reserve `bad_data` for the residual tail that survives those explanations
5. keep `good` narrow and conservative

## Scientific And Institutional Justification

This policy is consistent with modern microstructure reasoning:

- O'Hara (1995): trade interpretation depends on market state and tape context
- Hasbrouck (2007): trade prints and aggregated reference series are not interchangeable objects
- Menkveld (2013): modern liquidity formation makes small-size and non-core prints structurally different from benchmark-like flow
- Lopez de Prado: labels and features must respect data-generating structure; raw execution tape and adjusted return series must not be conflated

In short:

- a raw trade print can be valid as tape
- while still disagreeing materially with `daily` or `1m`
- because comparability and scaling are separate questions from tape integrity

## Contractual Rule For Future Inspection

Any future trades inspection dossier must distinguish explicitly between:

- tape-intrinsic failure
- reference-relative disagreement
- microstructure-driven disagreement
- scale mismatch
- missing / insufficient reference support

If that distinction is not explicit, the dossier is not methodologically acceptable.
