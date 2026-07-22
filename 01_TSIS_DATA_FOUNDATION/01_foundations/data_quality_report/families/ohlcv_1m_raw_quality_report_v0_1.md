# OHLCV 1m Raw Quality Report v0.1

## 1. Scope And Role

Family:

```text
ohlcv_1m_raw_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_1m
```

Historical closeout evidence also references:

```text
D:/ohlcv_1m
```

Role:

- RAW/STAGED intraday one-minute OHLCV market bars;
- raw minute-bar foundation for intraday diagnostics and split-normalized construction checks;
- not split-normalized, not adjusted, not clean production backtest data, and not a quote/fill execution layer.

## 2. Final Status

```text
complete_scoped
```

`ohlcv_1m_raw_v0_1` is institutionally reconciled for the `<1B>` scope, but the raw layer is not globally clean. This report imports the raw 1m closeout and schema-only readout into the normalized `data_quality_report/` surface.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md` |
| Validators | present | `01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md` |
| Raw `<1B>` closeout readout | present | `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md` |
| Schema-only inspection readout | present | `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md` |
| Minute dossier README | present | `01_foundations/inspection_dossiers/minute/README.md` |
| Core/vw visual casepack | present | `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md` |
| Core/vw visual case manifest | present | `01_foundations/inspection_dossiers/minute/core_quality_case_evidence_packs/minute_core_quality_visual_case_manifest_v0_1.csv` |
| Core quality manifest | present | `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/minute_core_quality_manifest_v0_1.parquet` |
| Core quality summaries | present | `01_foundations/inspection_dossiers/minute/evidence_assets/core_quality/` |
| Modern core/vw notebooks | present | `01_foundations/inspection_dossiers/minute/minute_00_*` through `minute_05_*` |
| Historical reconciliation contract | present | `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md` |
| Evidence assets | present | `01_foundations/inspection_dossiers/minute/evidence_assets/raw_1m_lt1b_closeout/` |

## 4. File Structure And Technical Profile

Primary audited unit:

```text
1m file-month / task key under the <1B> universe and PTI window
```

Expected logical content:

- `ticker`;
- minute timestamp;
- `open`, `high`, `low`, `close`;
- `volume`;
- conditional `transactions`;
- conditional `vw`.

The raw layer preserves observed source scale. It does not guarantee split-continuous cross-session prices. Consumers requiring split continuity must use `ohlcv_1m_split_normalized_v0_1`.

## 5. Population And Coverage

Raw `<1B>` closeout:

| Metric | Value |
| --- | ---: |
| `lt1b_tickers_reference` | 4,824 |
| `lt1b_current_1m_unique_tickers` | 4,822 |
| `lt1b_current_1m_unique_task_keys` | 334,660 |
| `lt1b_current_1m_rows` | 334,660 |

Operational inherited buckets:

| Bucket | Count | Share |
| --- | ---: | ---: |
| `RESCUE_SCHEMA_ONLY` | 19,713 | 5.890456% |
| `RESCUE_SCHEMA_PLUS_VW` | 314,947 | 94.109544% |

Refined `<1B>` quality state:

| State | Count | Share |
| --- | ---: | ---: |
| `good` | 46,652 | 13.940118% |
| `review` | 75,245 | 22.484014% |
| `bad` | 212,763 | 63.575868% |

## 6. Cleanliness And Interpretability

The raw 1m layer is understood, but not clean.

The dominant problem is not `schema_only`. The dominant mass is `schema_plus_vw`, especially severe `vw` families:

| `vw_*` taxonomy | Count | Share |
| --- | ---: | ---: |
| `vw_mild_low_ratio` | 26,939 | 8.049662% |
| `vw_moderate_ratio` | 23,933 | 7.151437% |
| `vw_severe_tiny_base` | 12,035 | 3.596187% |
| `vw_severe_small_mass` | 39,277 | 11.736389% |
| `vw_severe_large_mass_diffuse` | 90,159 | 26.940477% |
| `vw_severe_large_mass_persistent` | 122,604 | 36.635391% |

The non-`vw` `schema_only` block is also audited:

| Metric | Value |
| --- | ---: |
| raw `1m <1B>` mass | 334,660 |
| `schema_only` mass | 19,713 |
| `schema_only` share | 5.890456% |
| dominant schema-only signature rows | 18,266 |
| dominant signature share inside `schema_only` | 92.66% |

Dominant schema-only signature:

```text
dataset_read_incompatible_schema
schema_merge_conflict_ticker_encoding
```

This means `schema_only` is mostly a structural reading and schema-compatibility problem, not an arbitrary economic corruption tail.

## 7. Modern Core/VW Split

The modern minute dossier separates:

- `core_quality_state`: OHLCV/window/coverage quality when `vw` is not consumed;
- `vw_quality_state`: reliability of the `vw` field;
- `combined_quality_state`: combined reading;
- `allowed_consumption`: consumer state derived from those axes.

Current manifest:

| Metric | Value |
| --- | ---: |
| rows / file-month task keys | 334,660 |
| tickers | 4,822 |
| temporal range | 2005-2026 |

Core OHLCV state:

| State | Count |
| --- | ---: |
| `core_good` | 331,511 |
| `core_review` | 3,149 |
| `core_bad` | 0 |

VW state:

| State | Count |
| --- | ---: |
| `vw_good` | 46,652 |
| `vw_review` | 75,245 |
| `vw_bad` | 212,763 |

Allowed consumption:

| State | Count |
| --- | ---: |
| `controlled_ohlcv_research` | 118,818 |
| `ohlcv_without_vw_only` | 212,693 |
| `flagged_research_or_sensitivity` | 3,149 |

Interpretation:

- the core OHLCV axis is overwhelmingly usable for controlled research;
- the dominant debt lives in `vw`, not in raw OHLCV price bars;
- consumers must declare whether they use `vw`;
- `schema_readability_known_warning` remains tracked but does not by itself downgrade core OHLCV quality.

## 8. Semantic Quality

Final raw-state interpretation:

| State | Meaning |
| --- | --- |
| `good` | controlled raw intraday diagnostics and validation baseline |
| `review` | flagged exploratory or forensic use only |
| `bad` | forensic only, not production research or ML training |

The `vw` field is the dominant raw-layer quality debt. Consumers that use `vw` must obey the validator taxonomy and cannot treat the raw layer as globally clean. Consumers that do not use `vw` still must preserve file-level flags.

The layer is also raw price scale. It does not replace:

- `ohlcv_1m_split_normalized` for split-safe intraday continuity;
- `daily_adjusted` for adjusted daily economic returns;
- `quotes` or `trades` for book or execution evidence.

## 9. Case Evidence

The human auditor should read evidence in this order:

1. `inspection_dossiers/minute/README.md`
2. `raw_1m_lt1b_closeout_recalculation_v0_1.md`
3. `raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
4. `raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb`
5. `minute_00_universe_quality_overview_v0_1.ipynb`
6. `minute_01_core_quality_model_v0_1.ipynb`
7. `minute_02_core_quality_population_readout_v0_1.ipynb`
8. `minute_03_casepack_builder_v0_1.ipynb`
9. `minute_04_ticker_month_inspector_v0_1.ipynb`
10. `minute_05_final_readout_v0_1.ipynb`
11. `core_quality_case_evidence_packs/minute_core_quality_visual_cases_v0_1.md`
12. `raw_1m_lt1b_bucket_summary.csv`
13. `raw_1m_lt1b_exec_summary.csv`
14. `evidence_assets/core_quality/minute_core_quality_summary_v0_1.csv`
15. `evidence_assets/core_quality/minute_core_quality_family_counts_v0_1.csv`

The fixed visual dossier contains:

- 7 population maps;
- 60 individual case images;
- 67 embedded images in total;
- one reproducible population manifest;
- one reproducible visual case manifest;
- contact sheets for core/vw families.

This evidence is strong enough for `human_inspector_ready_scoped` within the raw 1m scope. It still does not promote raw 1m to clean production use.

## 10. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `raw_intraday_diagnostics` | allowed for declared states |
| `split_normalized_layer_validation` | allowed |
| `flagged_exploratory_intraday_research` | allowed for `review` with explicit state |
| `forensic_only` | allowed for `bad` |
| `unflagged_production_backtest` | prohibited |
| `unflagged_ml_training` | prohibited |
| `cross_session_return_engineering` | prohibited |
| `execution/fill simulation` | prohibited as fill authority |
| `RL/live` | not enabled by this report |

## 11. Verdict

`ohlcv_1m_raw_v0_1` meets the data-quality standard as a scoped, reconciled raw intraday bar layer for `<1B>` evidence and diagnostics.

Final verdict:

```text
complete_scoped_raw_1m_layer_reconciled_lt1b_not_globally_clean
```

Foundations completion status:

```text
human_inspector_ready_scoped
```

## 12. Open Debt

- The refined `<1B>` raw state remains dominated by `bad`.
- `vw` quality debt must stay explicit in all consumers.
- Schema-aware reading remains required for ticker encoding and merge conflicts.
- This report does not upgrade raw 1m into split-normalized or adjusted truth.
- Any promotion beyond scoped diagnostics requires a new closeout, validator run and contract update.
