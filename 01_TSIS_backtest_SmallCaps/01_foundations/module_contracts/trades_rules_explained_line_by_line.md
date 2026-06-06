# `trades` Rules Explained Line By Line

## Purpose

This document rewrites the `trades` policy stack in a compressed, line-by-line format.

It is meant for moments where the reader does not need a long essay, but does need:

- every important rule,
- one rule per line,
- grouped by section,
- with the formula or cut condition when it exists.

It complements:

- `trades_acceptance_policy_explained.md`
- `trades_label_taxonomy_and_cut_policy.md`
- `trades_consumption_policy.md`

## 1. Historical Severity

- `PASS`: historical snapshot without relevant conflict under the original severity audit; it is **not** a final usage label.
- `SOFT_FAIL`: historical snapshot with moderate conflict; it is **not** a final usage label.
- `HARD_FAIL`: historical snapshot with strong conflict; it is **not** a final usage label.

## 2. Mother Interpretation Rules

- Never classify `bad` from `PASS / SOFT_FAIL / HARD_FAIL` alone.
- Never classify `bad` from `outside_daily_regular_pct` alone.
- Never classify `bad` from `outside_1m_regular_pct` alone.
- Every final decision must separate `arbiter-relative disagreement` from `intrinsic tape corruption`.

## 3. File-Level Explanatory Families

- `good`: the file is clean enough under the final conservative policy and does not retain a material unresolved caveat.
- `review`: residual ambiguous class for files that are not `good`, not `bad_data`, and not better explained by the more specific explanatory families.
- `reference_scale_mismatch`: the dominant conflict is scale or comparability against arbiters, not obvious intrinsic tape corruption.
- `review_microstructure`: the dominant conflict is odd-lot structure, sparse prints, bursts or tape texture rather than gross corruption.
- `review_no_1m_reference`: the file cannot be decided cleanly because `1m` reference support is missing or insufficient.
- `review_1m_reference_alignment`: `daily` may look aligned while `1m` still breaks materially.
- `bad_data`: even after removing benign explanations, the file remains best explained as intrinsically untrustworthy tape.

## 4. Final Operational States

- `good`: usable without material caveat.
- `recoverable_with_flag`: usable only with explicit warning attached.
- `review_not_rehabilitated`: not proved bad enough for hard exclusion, but not rehabilitated.
- `bad`: excluded from normal downstream operational use.

## 5. Strict Rehabilitation Rule For `review`

- Applies only when `acceptance_label == "review"`.
- Requires `scale_bucket_vw in {"~1x", "near_1x"}`.
- Requires `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`.
- Requires `outside_daily_regular_pct <= 1`.
- Requires `outside_1m_regular_pct <= 15`.
- If all conditions pass: `review -> recoverable_with_flag`.
- If any condition fails: `review -> review_not_rehabilitated`.

## 6. Extended Rehabilitation Rule

- Applies only when `acceptance_label == "review"`.
- Requires `scale_bucket_vw in {"~1x", "near_1x"}`.
- Requires `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`.
- Requires `outside_daily_regular_pct <= 2`.
- Requires `outside_1m_regular_pct <= 20`.
- If all conditions pass: `review -> recoverable_with_flag` under extended sensitivity.
- If any condition fails: it remains outside extended rehabilitation.

## 7. Comparability Metrics

- `daily_vw_to_trade_vw = daily_vw / trade_vwap`; asks whether tape and daily arbiter live on a similar scale.
- `scale_bucket_vw = _nearest_scale_bucket(daily_vw_to_trade_vw)`; compresses scale into discrete families such as `~1x`, `~4x`, `~5x`, `~10x`, `nan`.
- "Scale acceptable for rehabilitation" means `scale_bucket_vw in {"~1x", "near_1x"}`.
- `trade_vwap_vs_daily_vw_diff_pct_raw = abs(trade_vwap - daily_vw) / abs(daily_vw) * 100`; measures economic separation against daily VW.
- `outside_daily_regular_pct = 100 * (# regular trades outside [daily_low, daily_high]) / (# regular trades)`; measures contradiction against daily range.
- `outside_1m_regular_pct = 100 * (# regular trades outside their minute range) / (# regular trades)`; measures contradiction against fine intraday structure.

## 8. Structural Tape Integrity Rules

- `size <= 0`: semantically invalid for `trades`, because a real execution must have strictly positive quantity.
- `size NA`: semantically invalid because the executed quantity is missing.
- `price NA`: semantically invalid because the executed price is missing.
- `duplicate_exact_ratio_pct_raw = 100 * (# exact duplicate rows) / (# rows in file)`; measures how much of the tape looks replayed or duplicated.
- `duplicate_excess_ratio_gt_hard_cap`: activates when `duplicate_exact_ratio_pct_raw` exceeds the historical hard cap.
- The combination `size <= 0` plus heavy duplication plus a small file hardens the reading toward structural tape failure.

## 9. Visual Rules Inside `bad_data`

- `colapso_escala_rango`: dominant when the file breaks by scale or range against arbiters and the price panel itself proves the failure.
- `integridad_estructural`: dominant when the core problem does not live in the visible price path but in rows such as `size <= 0`, `price NA` or excessive duplicates.
- `mixto_estructural_rango`: dominant when both strong range conflict and structural corruption coexist.
- `conflicto_ralo_o_sparse`: dominant when the file is so small or sparse that interpretation is governed by lack of tape density.
- `conflicto_rango_local`: dominant when the file does not show global collapse but still breaches range constraints materially in a local way.

## 10. Rules About `good`

- `good` is not the same thing as "all useful mass".
- `good` is the pristine tail only.
- `count(good) / total` must not be read as the useful-mass ratio of the dataset.
- Useful mass must be estimated mainly through rehabilitation, not through `good`.

## 11. Rules About `reference_scale_mismatch`

- Dominant signal: scale not close to `1x`, typically `scale_bucket_vw` outside `{"~1x", "near_1x"}`.
- If the tape is internally plausible but scale is incompatible with arbiters, the right family is `reference_scale_mismatch`.
- High `% outside` alone must not force `bad` if scale mismatch is the main explanation.

## 12. Rules About `review_microstructure`

- Dominant signal: conflict better explained by odd-lots, sparsity, bursts or tape texture.
- Typical indicators: high `odd_lot_trade_pct`, sparse files, hard comparability against `1m`.
- Hard comparability must not be collapsed into `bad` if the tape still looks more like microstructure stress than corruption.

## 13. Rules About `review_no_1m_reference`

- Dominant criterion: conflict against `daily` with insufficient `1m` support for clean confirmation or rejection.
- This is a reference-coverage problem, not a proof of broken tape.

## 14. Rules About `review_1m_reference_alignment`

- Dominant criterion: `daily` may look aligned while `1m` still opens a material conflict.
- These are forensic cases of high interest because they can reveal arbiter-layer problems, not just tape problems.

## 15. Pipeline Rules

- Execution research uses `trades_raw`.
- Microstructure research uses `trades_raw`.
- Execution accepts by default only `good` and `recoverable_with_flag`.
- `review_not_rehabilitated` does not enter execution by default.
- `bad` stays excluded from execution.
- Forensic inspection may inspect all states.
- External comparison must not be done with `trades_raw` alone; arbiter and price semantics must be declared.

## 16. Inspector-Evidence Rules

- Every family must explain what it represents, not only its name.
- Every graph must declare `que muestra`.
- Every graph must declare `responde`.
- Every graph must declare `no responde`.
- Every graph must declare `consecuencia`.
- If the current panel does not prove the real cause, the dossier must say so explicitly.
- If the real cause does not live in price, the case requires an extra integrity or structure panel.
- Bucket name plus metric list is not an acceptable final justification.

## 17. Rules Specific To `size = 0`

- Detection rule: `size <= 0`.
- Evidence count: `non_positive_size_rows_raw = count(size <= 0)`.
- If `non_positive_size_rows_raw > 0`, the file contains at least one row that fails the semantic definition of a real execution.
- This may coexist with a visually normal price path.
- If it also coexists with heavy duplication, the reading hardens toward `integridad_estructural` and potentially `bad_data`.

## 18. Rules Specific To Exact Duplicates

- Base formula: `duplicate_exact_ratio_pct_raw = 100 * (# exact duplicate rows) / (# rows in file)`.
- Panel evidence: `duplicate_rows_exact_panel = # exact duplicate rows visible in panel scope`.
- If `duplicate_exact_ratio_pct_raw` exceeds the historical hard cap, the warning `duplicate_excess_ratio_gt_hard_cap` activates.
- Heavy duplication may not destroy the top price path, but it does damage confidence in the file as a real execution stream.

## Relation To The Explanatory Standard

This document follows the transversal rule defined in:

- `01_foundations/module_contracts/policy_explanation_standard.md`
