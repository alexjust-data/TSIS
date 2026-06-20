# Additional Quality Report v0.1

## 1. Scope And Role

Family:

```text
additional_v0_1
```

Physical root:

```text
E:/TSIS/data/additional
```

Role:

- RAW vendor context data by subfamily;
- not one homogeneous dataset;
- auxiliary CAPA 1 context for quality reporting and selected master-table design.

## 2. Final Status

```text
complete_import_ready
```

The existing dossier is strong enough to import into `data_quality_report/`.

Visual inspection status:

```text
visual_complete
```

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/additional/additional_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/additional_consumption_policy.md` |
| Validators | present | `01_foundations/validators/additional/additional_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/additional/additional_inspection_readout_v0_2.md` |
| Institutional closeout | present | `01_foundations/inspection_dossiers/additional/additional_institutional_closeout_v0_1.md` |
| Evidence assets | present | `01_foundations/inspection_dossiers/additional/evidence_assets/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/additional/visual_inspector_pack/additional_visual_inspector_pack_v0_1.md` |
| Schemas | present | `01_foundations/canonical_schemas/additional/` |

## 4. Subfamily Status

| Subfamily | Status | Consumption reading |
| --- | --- | --- |
| financial statements | `good_context_candidate` | Context/PIT guardrails required. |
| ratios | `review_sparse_snapshot` | Sparse auxiliary context only. |
| news | `good_review_attribution_aware` | Attribution-aware event context. |
| IPOs | `good_review_sparse_event` | Sparse event/listing context. |
| corporate actions | `review_secondary_to_reference` | Secondary to `reference`. |
| economic | `good_macro_context` | Calendar/macro context, not ticker causality. |

## 5. Quality Reading

The family is not uniform. Effective quality must be read by subfamily.

Strong findings:

- financial core is useful as context with filing-date guardrails;
- macro/economic series are useful as calendar context;
- news and IPOs are useful only with attribution and sparse-event limits;
- corporate actions are review/secondary to `reference`.

## 6. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `master_daily_table` | partial/context only |
| `master_intraday_table` | indirect context only |
| `symbol_master` | partial context |
| `corporate_actions_table` | secondary reconciliation only |
| `calendar_table` | macro context allowed |
| `backtest_core` | not enabled |
| `ML/RL/live` | not enabled by this report |

## 7. Open Limits

- not one dataset;
- no direct alpha promotion;
- news attribution remains sensitive;
- corporate actions do not override `reference`;
- ratios remain sparse/review.

## 8. Verdict

`additional_v0_1` meets the data-quality standard as a governed auxiliary context block.

Final verdict:

```text
complete_subfamily_governed_context_block
```
