# Intraday Regime Features Quality Report v0.1

## 1. Scope And Role

Family:

```text
intraday_regime_features_v0_1
```

Physical root:

```text
E:/TSIS/data/intraday_regime_features
```

Role:

- feature/state pilot layer;
- consumer proof for `ohlcv_1m_split_normalized`;
- not raw market data;
- not production alpha;
- not full-universe feature store.

## 2. Final Status

```text
complete_scoped_pilot
```

This family is complete for its declared pilot role.

It is not complete as a production feature layer.

Foundations completion status:

```text
human_inspector_ready_scoped
```

Visual inspection status:

```text
visual_complete_scoped
```

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/intraday_regime_features_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/features/intraday_regime_features_schema_contract.md` |
| Validator | present as contract | `01_foundations/validators/intraday_regime_features/intraday_regime_features_validators.md` |
| Semantic pilot readout | present | `01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md` |
| Consumer contract | present | `01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md` |
| Variable taxonomy | present | `01_foundations/module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md` |
| Dossier evidence assets | present | `01_foundations/inspection_dossiers/intraday_regime_features/evidence_assets/` |
| Good/scoped cases | present | `01_foundations/inspection_dossiers/intraday_regime_features/good_justification/intraday_regime_features_semantic_pilot_good_cases_v0_1.md` |
| Review/boundary cases | present | `01_foundations/inspection_dossiers/intraday_regime_features/flagged_case_evidence_packs/intraday_regime_features_lookback_and_boundary_cases_v0_1.md` |
| Production-boundary evidence | present | `01_foundations/inspection_dossiers/intraday_regime_features/bad_case_evidence_packs/intraday_regime_features_production_boundary_v0_1.md` |
| Coverage evidence | present | `01_foundations/inspection_dossiers/intraday_regime_features/coverage_case_evidence_packs/intraday_regime_features_materialization_coverage_v0_1.md` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/intraday_regime_features/visual_inspector_pack/` |

## 4. File Structure And Technical Profile

Observed physical footprint:

| Item | Count |
| --- | ---: |
| ticker directories | 8 |
| parquet files | 8 |
| materialization summary CSV | 1 |
| ticker-day rows | 243 |
| columns | 41 |
| read errors | 0 |
| duplicate `ticker + date` rows | 0 |
| visual case images | 10 |
| formal visual pack images | 15 |

Observed ticker partitions:

- `BNGO`;
- `BXRX`;
- `CEI`;
- `COSM`;
- `EFSH`;
- `LIVE`;
- `PD`;
- `SAVA`.

Materialization summary:

```text
E:/TSIS/data/intraday_regime_features/_intraday_regime_features_materialization_summary.csv
```

Evidence summary:

```text
01_foundations/inspection_dossiers/intraday_regime_features/evidence_assets/intraday_regime_features_audit_summary_v0_1.json
```

## 5. Semantic Pilot

The pilot compares cross-session features computed:

- from raw 1m as counterfactual;
- from `ohlcv_1m_split_normalized` as contractual view.

The tested population includes:

- 4 reverse split cases;
- 4 forward split cases;
- 2 controls.

Main question:

```text
Does the feature layer change where a split would create false cross-session shocks, and stay neutral where it should?
```

## 6. Key Findings

Positive strong cases:

| Ticker/month | Role | Max absolute gap difference |
| --- | --- | ---: |
| `BNGO 2025-01` | reverse split | 5,183.28% |
| `CEI 2022-12` | reverse split | 4,900.00% |
| `BXRX 2022-12` | reverse split | 3,897.11% |
| `COSM 2022-12` | reverse split | 2,450.70% |
| `EFSH 2025-01` | forward split | 111.76% |
| `LIVE 2014-02` | forward split | 66.67% |

Boundary coherent cases:

| Ticker/month | Role | Max absolute gap difference |
| --- | --- | ---: |
| `PD 2006-03` | forward split | 49.81% |
| `SAVA 2023-12` | forward split | 28.49% |

Controls:

| Ticker/month | Role | Max absolute gap difference |
| --- | --- | ---: |
| `BXRX 2022-11` | control | 0.00% |
| `BNGO 2025-02` | control | 0.00% |

Interpretation:

- the feature layer detects exactly the family of split-driven false regime shocks it was meant to expose;
- controls remain neutral;
- the pilot validates the downstream usefulness of `ohlcv_1m_split_normalized`.

## 7. Technical Cleanliness Inside Pilot Scope

Key/provenance evidence:

| Check | Result |
| --- | --- |
| `ticker + date` duplicate rows | 0 |
| Feature files readable | yes |
| `feature_contract` | `intraday_regime_features_v0_1` in all files |
| `feature_grain` | `ticker_day` in all files |
| `cross_session_price_view` | `1m_split_normalized_v0_1` in all files |
| `intraday_price_view` | `1m_raw` in all files |

Expected lookback nulls:

| Column | Nulls | Null pct |
| --- | ---: | ---: |
| `overnight_gap_zscore_20` | 48 | 19.753086 |
| `multi_session_return_5d_to_open` | 40 | 16.460905 |
| `multi_session_return_3d_to_open` | 24 | 9.876543 |
| `distance_to_n_day_high_5` | 16 | 6.584362 |
| `distance_to_n_day_low_5` | 16 | 6.584362 |

## 8. Cleanliness And Interpretability

The current evidence is semantically strong but scoped.

Known limits:

- no full-universe feature audit;
- no standalone null/outlier profile for all future feature columns;
- no production drift audit;
- no model-consumer contract;
- no full leakage gate beyond pilot scope.

## 9. Case Evidence

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good/scoped cases | `01_foundations/inspection_dossiers/intraday_regime_features/good_justification/intraday_regime_features_semantic_pilot_good_cases_v0_1.md` | Strong split cases, controls and provenance checks. |
| Review/boundary cases | `01_foundations/inspection_dossiers/intraday_regime_features/flagged_case_evidence_packs/intraday_regime_features_lookback_and_boundary_cases_v0_1.md` | Lookback nulls and coherent boundary cases. |
| Production boundary | `01_foundations/inspection_dossiers/intraday_regime_features/bad_case_evidence_packs/intraday_regime_features_production_boundary_v0_1.md` | Claims blocked by pilot scope. |
| Coverage evidence | `01_foundations/inspection_dossiers/intraday_regime_features/coverage_case_evidence_packs/intraday_regime_features_materialization_coverage_v0_1.md` | Physical footprint and key quality. |
| Evidence assets | `01_foundations/inspection_dossiers/intraday_regime_features/evidence_assets/` | Stable CSV/JSON summaries, manifests and samples. |
| Visual inspector pack | `01_foundations/inspection_dossiers/intraday_regime_features/visual_inspector_pack/intraday_regime_features_visual_inspector_pack_v0_1.md` | Aggregate panels, concrete semantic case images, visual manifest and asset audit. |

## 10. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `ohlcv_1m_split_normalized validation` | allowed |
| `feature semantic inspection` | allowed |
| `research_only` | allowed with pilot scope |
| `backtest_extended` | restricted |
| `ml_flagged` | restricted |
| `backtest_core` | not enabled |
| `ml_primary` | not enabled |
| `execution_simulator` | not enabled |
| `rl_allowed` | not enabled |
| `live_downstream_candidate` | not enabled |

## 11. Open Debt

Before production feature promotion:

- full-universe materialization decision;
- feature null/outlier profile;
- duplicate/key audit;
- drift audit;
- leakage review;
- model-consumer contract;
- stable run manifest and reproducible builder entrypoint.

## 12. Verdict

`intraday_regime_features_v0_1` meets the standard for a scoped semantic pilot.

It does not meet the standard for a promoted production feature layer.

Final verdict:

```text
complete_scoped_pilot_not_production_feature_store
```
