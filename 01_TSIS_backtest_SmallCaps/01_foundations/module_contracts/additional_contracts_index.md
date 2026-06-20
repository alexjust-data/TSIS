# Additional Contracts Index

## Scope

This index groups the authority documents for `additional_v0_1`.

`additional` is RAW vendor context data from Polygon. It is not one uniform
dataset and not raw market price/book/tape authority.

## Core Authorities

- Dataset contract: `contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md`
- Consumption policy: `data_consumption_policies/additional_consumption_policy.md`
- Registry entry: `dataset_registry/additional/additional_registry_entry.yaml`
- Validator: `validators/additional/additional_validators.md`
- Master-table policy: `module_contracts/additional_to_master_tables_policy_v0_1.md`
- RAW/derived authority map: `module_contracts/raw_data_authority_and_derivation_map.md`

## Schemas

- `canonical_schemas/additional/additional_financials_schema_contract.md`
- `canonical_schemas/additional/additional_corporate_actions_schema_contract.md`
- `canonical_schemas/additional/additional_economic_schema_contract.md`
- `canonical_schemas/additional/additional_ipos_schema_contract.md`
- `canonical_schemas/additional/additional_news_schema_contract.md`

## Inspection Dossier

- `inspection_dossiers/additional/README.md`
- `inspection_dossiers/additional/additional_institutional_closeout_v0_1.md`
- `inspection_dossiers/additional/additional_inspection_readout_v0_2.md`
- `inspection_dossiers/additional/build_additional_inspection_pack.md`

Generated evidence assets:

- `inspection_dossiers/additional/evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`
- `inspection_dossiers/additional/evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/reference_reconciliation/additional_corporate_actions_reference_reconciliation_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/news_attribution/additional_news_attribution_quality_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/ipo_context/additional_ipo_context_quality_v0_1.csv`
- `inspection_dossiers/additional/evidence_assets/run_manifest.json`

Human casepacks:

- `inspection_dossiers/additional/good_justification/additional_financials_core_good_cases_v0_1.md`
- `inspection_dossiers/additional/flagged_case_evidence_packs/additional_news_attribution_review_cases_v0_1.md`
- `inspection_dossiers/additional/flagged_case_evidence_packs/additional_corporate_actions_reference_review_v0_1.md`
- `inspection_dossiers/additional/coverage_case_evidence_packs/additional_sparse_valid_context_cases_v0_1.md`

## Historical Evidence

Historical evidence remains preserved under:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/
```

Futures agents may read this tree and the historical Graphify research graph for
context, but must not rewrite or reorganize it during `01_foundations` work.

## Subfamily Roles

| Subfamily | Institutional role |
| --- | --- |
| `financials_core` | fundamentals/context with point-in-time filing guardrails |
| `financials_ratios` | sparse vendor-derived context under review |
| `news` | event/news context with attribution guardrails |
| `ipos` | sparse listing and early-life context |
| `corporate_actions_additional` | secondary reconciliation against `reference` |
| `economic` | macro/calendar context |

## Final Rule

Additional can enrich CAPA 1 quality and context tables.

It cannot certify raw market data, replace reference, or become a feature layer
without a separate downstream promotion.
