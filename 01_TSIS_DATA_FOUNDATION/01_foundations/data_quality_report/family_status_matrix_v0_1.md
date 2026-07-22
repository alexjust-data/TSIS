# Family Status Matrix v0.1

Fecha de referencia: 2026-06-20

Esta fecha marca el estado inicial de la matriz. Cualquier modificacion futura debe conservar esta referencia y anadir una nota fechada cuando cambie el estado de una familia.

## Scope

This matrix records the initial audit state of the `E:/TSIS/data` families selected for Data Foundation quality reporting.

It is not the final report. It is the work queue and evidence map used to complete the family reports one by one.

## Mandatory Three-Axis Reading

This matrix separates three concepts that must not be collapsed:

| Axis | Meaning |
| --- | --- |
| `data_quality_verdict` | What the audit concluded about the data itself. |
| `foundations_completion_status` | Whether the family package across `01_foundations` is complete enough for a human inspector. |
| `visual_inspection_status` | Whether the family has visual evidence at the `quotes`/`daily`/`trades`/`1m` casepack standard, or a documented waiver. |

Completion is governed by:

```text
../FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
```

Important:

- `blocked_by_data_defect` can still become `human_inspector_ready`.
- `usable_for_declared_scope` does not automatically mean `human_inspector_ready`.
- A family with only a `README.md` and one readout is not complete at the `quotes`/`daily`/`trades` standard.
- Strong CSV/JSON evidence without a visual inspector pack or explicit waiver is not complete at the human-inspector standard.

## Summary Table

| Family | Physical root | Role | Data quality verdict | Foundations completion status | Visual inspection status | Main reading | Completion gap / next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `additional` | `E:/TSIS/data/additional` | RAW vendor context by subfamily | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Has schema, contract, registry, policy, validators, dossier, quality tables, casepacks and a formal visual inspector pack. It is not one uniform dataset. | Maintain subfamily boundaries; no direct feature/alpha promotion without PIT, attribution and authority controls. |
| `daily` | `E:/TSIS/data/ohlcv_daily` | RAW/STAGED daily market bars | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Institutional raw daily layer with separate quality and coverage axes. Hard invalid tail is small and coverage frontier is explicit. | Maintain existing dossier, coverage evidence and visual casepacks as benchmark. |
| `financial` | `E:/TSIS/data/financial` | RAW/vendor-preserved fundamentals and ratios | `blocked_by_data_defect` | `human_inspector_ready` | `visual_complete` | Operational audit states `status = FAIL`, with 13,337 severe issues and 3,171 temporal issues, now backed by dossier-local evidence assets, casepacks and a visual inspector pack. | Keep blocked for consumption until sentinel severity, temporal/lifecycle issues and identity/PIT policy are repaired or explicitly waived. |
| `Halts` | `E:/TSIS/data/Halts` | RAW reference/event data | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Modern dossier exists with root audit, source quality, event taxonomy, universe coverage, multisource reconciliation, casepacks and a 10-image visual inspector pack. | Maintain event/context boundary; do not promote to alpha, live, RL or execution simulation without a downstream contract. |
| `intraday_regime_features` | `E:/TSIS/data/intraday_regime_features` | Feature layer / consumer pilot | `complete_scoped` | `human_inspector_ready_scoped` | `visual_complete_scoped` | Semantic pilot proves a real consumer for `ohlcv_1m_split_normalized`; the 8-ticker, 243-row pilot has key/provenance evidence, 10 concrete semantic images and a formal 15-image visual inspector pack. It is not a full production feature store. | Keep pilot boundary explicit; production feature-store promotion requires a future full-universe audit and new visuals. |
| `ohlcv_1m_raw` | `E:/TSIS/data/ohlcv_1m` | RAW/STAGED intraday 1m bars | `complete_scoped` | `human_inspector_ready_scoped` | `visual_complete_scoped` | `<1B>` raw closeout is reconciled and the modern minute dossier separates core OHLCV from `vw` debt. Core OHLCV is mostly usable for controlled research; `vw` remains the dominant debt. | Keep raw/split-normalized scopes separate; do not promote raw 1m to unflagged production use. |
| `ohlcv_1m_split_normalized` | `E:/TSIS/data/ohlcv_1m_split_normalized` | Derived ETL price view | `complete_scoped` | `human_inspector_ready_scoped` | `visual_complete_scoped` | Split-normalization semantics and split-event audit are strong. It does not claim full 1m universal replacement or full materialization. | Keep scope limitation visible in every consumer; future full-universe materialization requires new visuals. |
| `ohlcv_daily_adjusted` | `E:/TSIS/data/ohlcv_daily_adjusted` | Derived ETL price view | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Full-universe materialization audit shows 100% ticker-with-files and year-file coverage against raw daily files, no read errors, no missing required columns, no bad factors and a 7-image visual inspector pack. | Maintain boundary: derived economic daily view for declared consumers, not raw/intraday/execution authority. |
| `quotes` | `E:/TSIS/data/quotes` | RAW/STAGED book observations | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Institutional raw book layer with `9,525,272` audited ticker-date files, explicit `good/review/bad` policy and open decision mass of `2.991%`. | Use as primary dossier completeness benchmark. |
| `reference` | `E:/TSIS/data/reference` | RAW reference/lifecycle/corporate-action support | `usable_for_declared_scope` | `human_inspector_ready` | `visual_complete` | Modern dossier exists with physical root audit, population summaries, visual overview, casepacks, restrictions and an 11-image visual inspector pack. | Maintain boundaries: `all_tickers` is not final universe, ticker changes are not signals, and overview market cap is not daily PTI membership. |
| `regime_indicators` | `E:/TSIS/data/regime_indicators` | RAW/context regime bars | `blocked_by_data_defect` | `human_inspector_ready` | `visual_complete` | Daily ETF/index files have invalid `date`/`datetime` semantics clustered in 1970; minute files are scoped/review with 204 `high < low` rows in `UVXY`, now backed by a visual inspector pack. | Keep daily blocked and minute scoped until daily files are repaired/regenerated and minute OHLC flags are classified or repaired. |
| `short_review` | `E:/TSIS/data/short_review` | FINRA official/free baseline and provenance | `complete_scoped` | `human_inspector_ready_scoped` | `visual_complete` | Standalone FINRA baseline/provenance layer with casepacks and visual inspector pack. Short volume has 5,250 duplicate `ticker + date` excess rows concentrated in `CPS`, `OP` and `LFTR`, so it is not clean short replacement input. | Keep scoped baseline/provenance boundary; production short replacement requires duplicate-key policy, full-history proof and local-only ticker review. |
| `trades` | `E:/TSIS/data/trades_ticks_prod_2005_2026` | RAW/STAGED trade tape | `complete_scoped` | `human_inspector_ready` | `visual_complete` | `57f` closeout is governed but not globally clean: `bad_data` is small, `good` is tiny and most usable mass needs flags or reconciliation. | Maintain family casepacks and global universe readout as benchmark. |

## Artifact Presence Matrix

| Family | Physical | Schema | Contract | Registry | Policy | Validators | Dossier/readout | Evidence assets | Visual inspector pack | Technical-profile report |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `additional` | yes | yes | yes | yes | yes | yes | yes | yes | yes | partial, normalize |
| `daily` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `financial` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `Halts` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `intraday_regime_features` | yes | yes | yes | yes | yes | yes | yes, scoped | yes | yes, scoped | yes, scoped |
| `ohlcv_1m_raw` | yes | yes | yes | yes | yes | yes | yes, scoped | yes | yes, scoped | yes, scoped |
| `ohlcv_1m_split_normalized` | yes | yes | yes | yes | yes | yes | yes | yes | yes, scoped | yes, scoped |
| `ohlcv_daily_adjusted` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `quotes` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `reference` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `regime_indicators` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `short_review` | yes | yes | yes | yes | yes | yes | yes, scoped | yes | yes | yes, scoped |
| `trades` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |

## Completion Work Queue

No family in this matrix remains in `visual_casepack_required`.

1. Completed after the visual standard correction:
   - Families: `financial`, `regime_indicators`, `short_review`, `additional`, `intraday_regime_features`, `Halts`, `reference`, `ohlcv_daily_adjusted`.
   - Completion status: `human_inspector_ready` or `human_inspector_ready_scoped`.
   - Visual status: `visual_complete` or `visual_complete_scoped`.
   - Remaining work: data repair only; the audit packages themselves are complete.

2. Existing benchmark families:
   - Families: `daily`, `quotes`, `trades`, `ohlcv_1m_raw`, `ohlcv_1m_split_normalized`.
   - Status: maintain as benchmarks, while respecting each declared scope.

## Change Notes

- `2026-06-20`: tightened the completion standard by adding `visual_inspection_status`. Families without a benchmark-level visual inspector pack or explicit waiver are no longer marked `human_inspector_ready`; they now use `visual_casepack_required` until the visual layer is complete. Image requirements by family live in `../VISUAL_INSPECTION_PACK_REQUIREMENTS.md`.
- `2026-06-20`: completed the `financial` visual inspector pack with six generated images, a visual case manifest, an asset audit and a reproducible builder. `financial` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; the data-quality verdict remains `blocked_by_data_defect`.
- `2026-06-20`: completed the `regime_indicators` visual inspector pack with six generated images, a visual case manifest, an asset audit and a reproducible builder. `regime_indicators` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; daily bars remain blocked and minute bars remain scoped/review.
- `2026-06-20`: completed the `short_review` visual inspector pack with six generated images, a visual case manifest, an asset audit and a reproducible builder. `short_review` returns to `human_inspector_ready_scoped` with `visual_inspection_status = visual_complete`; it remains a scoped FINRA baseline/provenance layer, not a production short replacement.
- `2026-06-20`: completed the `additional` visual inspector pack with six generated images, a visual case manifest, an asset audit and a reproducible builder. `additional` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; it remains a subfamily-governed context block.
- `2026-06-20`: completed the `intraday_regime_features` visual inspector pack with five generated aggregate panels, ten governed semantic case images, a visual case manifest, an asset audit and a reproducible builder. `intraday_regime_features` returns to `human_inspector_ready_scoped` with `visual_inspection_status = visual_complete_scoped`; it remains a scoped pilot, not a production feature store.
- `2026-06-20`: completed the `Halts` visual inspector pack with five generated aggregate panels, five governed population visuals, a visual case manifest, an asset audit and a reproducible builder. `Halts` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; it remains an event/context layer, not alpha or execution input.
- `2026-06-20`: completed the `reference` visual inspector pack with six generated aggregate panels, five governed population visuals, a visual case manifest, an asset audit and a reproducible builder. `reference` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; it remains identity/lifecycle/corporate-action support, not final universe membership or alpha input.
- `2026-06-20`: completed the `ohlcv_daily_adjusted` visual inspector pack with seven generated panels, a wrapper dossier, a visual case manifest, an asset audit and a reproducible builder. `ohlcv_daily_adjusted` returns to `human_inspector_ready` with `visual_inspection_status = visual_complete`; it remains a derived economic daily view, not raw/intraday/execution authority.
- `2026-06-20`: added normalized reports for `daily`, `quotes`, `trades` and `ohlcv_1m_raw` so the core market families are visible from the same matrix as the other `E:/TSIS/data` families.
- `2026-06-20`: split the previous single status column into `data_quality_verdict` and `foundations_completion_status` after clarifying that "institutionalized" means complete for human inspection across all `01_foundations` surfaces, not production usability.
- `2026-06-20`: corrected `ohlcv_1m_raw` completion from `dossier_partial` to `human_inspector_ready_scoped` after verifying the modern `minute` dossier, core/vw manifests, population visuals, 60 fixed case images and contact sheets.
- `2026-06-20`: completed `financial` as `human_inspector_ready` by adding dossier-local evidence assets, endpoint examples, blocking schema case evidence, temporal case evidence and coverage case evidence. The data-quality verdict remains `blocked_by_data_defect`.
- `2026-06-20`: completed `regime_indicators` as `human_inspector_ready` by adding dossier-local evidence assets, daily date blocker casepack, scoped minute/metadata examples, minute flagged case evidence and inventory coverage evidence. The data-quality verdict remains `blocked_by_data_defect`.
- `2026-06-20`: completed `intraday_regime_features` as `human_inspector_ready_scoped` by adding dossier-local feature evidence assets, semantic pilot good cases, lookback/boundary cases, production-boundary evidence and materialization coverage evidence.
- `2026-06-20`: completed `short_review` as `human_inspector_ready_scoped` by adding dossier-local FINRA baseline evidence assets, short-volume duplicate-key case evidence, source/history boundary evidence and coverage/provenance evidence. The data-quality verdict remains `complete_scoped`.

## Non-Negotiable Interpretation

The matrix does not downgrade completed historical work.

It only says whether each family already has the same visible report shape required by the current standard.

Where evidence exists but is stored under older structures, the job is to normalize the report, not to pretend the audit never happened.

Where tabular evidence exists without visual explanation, the job is to build the visual inspector pack or write a defensible waiver. The family must not be called `human_inspector_ready` until one of those two things exists.
