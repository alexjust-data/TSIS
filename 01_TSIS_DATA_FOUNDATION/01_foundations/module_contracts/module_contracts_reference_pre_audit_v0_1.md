# Module Contracts Reference Pre-Audit v0.1

## Rol

Este documento mide cuantas referencias a paths planos de `module_contracts` siguen vivas en el proyecto antes de cualquier migracion fisica real.

## Que se considero una referencia relevante

- menciones a `01_foundations/module_contracts/<documento>.md`
- menciones relativas del tipo `../../module_contracts/<documento>.md`
- y menciones con path absoluto que siguen apuntando al root plano actual de `module_contracts`

## Resultado agregado

- `reference_hits_total = 188`
- `unique_source_files = 41`
- `unique_target_documents = 55`

## Targets mas citados

- `policy_explanation_standard.md` -> `20` referencias en `20` archivos; destino previsto: `module_contracts/governance/policy_explanation_standard.md`
- `price_semantics_and_adjustment_policy.md` -> `13` referencias en `10` archivos; destino previsto: `module_contracts/transversal/price_semantics_and_adjustment_policy.md`
- `pipeline_price_view_policy.md` -> `8` referencias en `8` archivos; destino previsto: `module_contracts/transversal/pipeline_price_view_policy.md`
- `external_price_comparison_caveats.md` -> `9` referencias en `7` archivos; destino previsto: `module_contracts/transversal/external_price_comparison_caveats.md`
- `market_session_scope.md` -> `8` referencias en `6` archivos; destino previsto: `module_contracts/transversal/market_session_scope.md`
- `corporate_actions_adjustment_methodology.md` -> `6` referencias en `6` archivos; destino previsto: `module_contracts/transversal/corporate_actions_adjustment_methodology.md`
- `price_views_registry.md` -> `6` referencias en `6` archivos; destino previsto: `module_contracts/transversal/price_views_registry.md`
- `data_storage_topology_and_target_state.md` -> `5` referencias en `5` archivos; destino previsto: `module_contracts/transversal/data_storage_topology_and_target_state.md`
- `event_families_and_reference_inventory.md` -> `5` referencias en `5` archivos; destino previsto: `module_contracts/transversal/event_families_and_reference_inventory.md`
- `ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md` -> `5` referencias en `5` archivos; destino previsto: `module_contracts/minute/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `ohlcv_1m_split_normalized_operational_landing_v0_1.md` -> `5` referencias en `5` archivos; destino previsto: `module_contracts/minute/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `bad_evidence_and_rehabilitation.md` -> `5` referencias en `4` archivos; destino previsto: `module_contracts/transversal/bad_evidence_and_rehabilitation.md`
- `auditoria_and_certification_source_hierarchy.md` -> `4` referencias en `4` archivos; destino previsto: `module_contracts/transversal/auditoria_and_certification_source_hierarchy.md`
- `intraday_regime_features_consumer_contract_v0_1.md` -> `4` referencias en `4` archivos; destino previsto: `module_contracts/consumers/intraday_regime_features_consumer_contract_v0_1.md`
- `ohlcv_1m_split_normalized_pilot_manifest_v0_2.md` -> `4` referencias en `4` archivos; destino previsto: `module_contracts/minute/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`

## Sources mas cargados

- `CHANGELOG.md` -> `56` referencias a `module_contracts` sobre `50` documentos objetivo
- `01_foundations/module_contracts/layer_maturity_assessment_v0_1.md` -> `13` referencias a `module_contracts` sobre `13` documentos objetivo
- `01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md` -> `10` referencias a `module_contracts` sobre `7` documentos objetivo
- `AGENTS.md` -> `9` referencias a `module_contracts` sobre `9` documentos objetivo
- `README.md` -> `8` referencias a `module_contracts` sobre `8` documentos objetivo
- `01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md` -> `7` referencias a `module_contracts` sobre `7` documentos objetivo
- `01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md` -> `7` referencias a `module_contracts` sobre `4` documentos objetivo
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md` -> `6` referencias a `module_contracts` sobre `6` documentos objetivo
- `LOCAL_RULES.md` -> `6` referencias a `module_contracts` sobre `6` documentos objetivo
- `01_foundations/contract_registry/dataset_contracts/quotes_label_taxonomy_and_cut_policy.md` -> `6` referencias a `module_contracts` sobre `5` documentos objetivo
- `01_foundations/inspection_dossiers/quotes/build_quotes_inspection_pack.md` -> `5` referencias a `module_contracts` sobre `5` documentos objetivo
- `01_foundations/module_contracts/inspection_dossier_model.md` -> `5` referencias a `module_contracts` sobre `5` documentos objetivo
- `01_foundations/data_consumption_policies/daily_consumption_policy.md` -> `4` referencias a `module_contracts` sobre `4` documentos objetivo
- `01_foundations/data_consumption_policies/quotes_consumption_policy.md` -> `4` referencias a `module_contracts` sobre `4` documentos objetivo
- `01_foundations/module_contracts/price_view_integration_priority_plan_v0_1.md` -> `4` referencias a `module_contracts` sobre `4` documentos objetivo

## Lectura tecnica

Esta pre-auditoria no mueve nada.
Su valor institucional es otro:

- cuantifica la superficie real de ruptura potencial;
- permite priorizar que documentos requeriran mas actualizacion si se ejecuta la migracion fisica;
- y evita una migracion cosmetica que rompa referencias por volumen oculto.

En particular, si un target tiene muchas referencias distribuidas en muchos archivos fuente, ese target debe tratarse como documento de alta sensibilidad de migracion.

## Artefactos exportados

- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_hits.csv`
- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_summary.csv`
- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_sources.csv`

## Veredicto

El proyecto ya tiene medido el perimetro de referencias a paths planos de `module_contracts`.
Eso no ejecuta la migracion, pero si convierte una futura reorganizacion en una operacion trazable en vez de una apuesta ciega.
