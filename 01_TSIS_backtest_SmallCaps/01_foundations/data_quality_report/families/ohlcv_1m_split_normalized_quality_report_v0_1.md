# Ohlcv 1m Split-Normalized Quality Report v0.1

## 1. Scope And Role

Family:

```text
ohlcv_1m_split_normalized_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_1m_split_normalized
```

Role:

- derived ETL split-normalized intraday price view;
- designed for split-sensitive cross-session comparisons;
- not raw 1m data;
- not dividend-adjusted 1m;
- not universal intraday replacement.

## 2. Final Status

```text
complete_scoped
```

The family is complete for split-normalized semantics and split-event audit.

It is not promoted as full-universe raw 1m replacement.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md` |
| Final readout | present | `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md` |
| Full-universe split-event readout | present | `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md` |

## 4. Physical And Technical Profile

Observed physical root:

- 8 ticker directories;
- 10 parquet files;
- 1 materialization summary CSV.

This physical root is not declared full-universe materialized.

## 5. Semantic Rule

The contractual transformation is:

```text
px_split_normalized = px_raw * future_split_factor
```

where:

```text
future_split_factor(date_t) = product of all split_ratio with execution_date > date_t
```

The layer must reexpress observations before future splits and leave post-split observations neutral.

## 6. Split-Event Audit

Full-universe split-event audit:

| Status | Cases | Share |
| --- | ---: | ---: |
| `PASS` | 2,280 | 68.37% |
| `FAIL` | 0 | 0.00% |
| `NO_PRE_COVERAGE` | 164 | 4.92% |
| `NO_POST_COVERAGE` | 151 | 4.53% |
| `NO_1M_COVERAGE` | 740 | 22.19% |

Interpretation:

- all cases with sufficient bilateral coverage pass;
- no semantic failure observed;
- non-PASS cases are empirical coverage limits, not transformation failures.

## 7. Consumer Validation

The minimal real consumer:

```text
intraday_regime_features
```

demonstrates that the split-normalized view removes false cross-session gaps and false regime shocks in the tested split cases while controls remain neutral.

## 8. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| split-sensitive intraday research | allowed |
| `intraday_regime_features` pilot | allowed |
| full-universe feature production | restricted |
| raw 1m replacement | prohibited |
| execution simulator | prohibited |
| live/RL | not enabled |

## 9. Open Debt

- no full physical materialization claim for every ticker-month;
- not a universal `1m_adjusted` view;
- not a substitute for raw 1m audit;
- future consumers need explicit price-view contracts.

## 10. Verdict

`ohlcv_1m_split_normalized_v0_1` meets the standard for a scoped split-normalized intraday derived view.

Final verdict:

```text
complete_scoped_split_normalized_view_not_raw_1m_replacement
```
