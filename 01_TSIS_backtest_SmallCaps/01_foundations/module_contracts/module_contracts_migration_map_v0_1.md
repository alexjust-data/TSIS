# Module Contracts Migration Map v0.1

## Rol

Este documento no ejecuta ninguna migracion fisica.

Su funcion es dejar preparado, de forma explicita, el mapa conceptual:

- `path actual`
- `path futuro previsto`

para que una reorganizacion posterior de `module_contracts` no dependa de memoria ni de intuicion.

## Regla de lectura

Mientras la migracion no se ejecute:

- el `path actual` sigue siendo el canonico;
- el `path futuro previsto` es solo destino de referencia;
- y ninguna referencia antigua debe considerarse rota.

Si en el futuro se mueve un documento, este mapa debera:

- actualizarse o versionarse;
- y usarse como autoridad de resolucion para referencias antiguas.

## Nota de compatibilidad futura

Si un documento del proyecto, un notebook, un readout o un agente se refiere a un path antiguo de `module_contracts`, la regla correcta es:

- asumir primero que esa referencia era valida en su momento;
- consultar este mapa;
- y resolver la equivalencia con el destino aprobado, si la migracion fisica ya se hubiera ejecutado.

No debe corregirse "a ojo" una ruta antigua sin pasar por un mapa oficial.

## Dominios futuros previstos

- `module_contracts/daily/`
- `module_contracts/quotes/`
- `module_contracts/trades/`
- `module_contracts/minute/`
- `module_contracts/transversal/`
- `module_contracts/consumers/`
- `module_contracts/governance/`

## Mapa origen -> destino previsto

### Governance

- `README.md` -> `module_contracts/governance/README.md`
- `module_contracts_migration_map_v0_1.md` -> `module_contracts/governance/module_contracts_migration_map_v0_1.md`
- `state_snapshot_standard.md` -> `module_contracts/governance/state_snapshot_standard.md`
- `policy_explanation_standard.md` -> `module_contracts/governance/policy_explanation_standard.md`
- `layer_validation_standard_v0_1.md` -> `module_contracts/governance/layer_validation_standard_v0_1.md`
- `layer_maturity_assessment_v0_1.md` -> `module_contracts/governance/layer_maturity_assessment_v0_1.md`
- `foundations_transversal_final_review_v0_1.md` -> `module_contracts/governance/foundations_transversal_final_review_v0_1.md`
- `foundations_transversal_final_review_v0_2.md` -> `module_contracts/governance/foundations_transversal_final_review_v0_2.md`

### Transversal

- `auditoria_and_certification_source_hierarchy.md` -> `module_contracts/transversal/auditoria_and_certification_source_hierarchy.md`
- `bad_evidence_and_rehabilitation.md` -> `module_contracts/transversal/bad_evidence_and_rehabilitation.md`
- `corporate_actions_adjustment_methodology.md` -> `module_contracts/transversal/corporate_actions_adjustment_methodology.md`
- `data_storage_topology_and_target_state.md` -> `module_contracts/transversal/data_storage_topology_and_target_state.md`
- `dataset_contract_template.md` -> `module_contracts/transversal/dataset_contract_template.md`
- `event_families_and_reference_inventory.md` -> `module_contracts/transversal/event_families_and_reference_inventory.md`
- `evidence_model.md` -> `module_contracts/transversal/evidence_model.md`
- `external_price_comparison_caveats.md` -> `module_contracts/transversal/external_price_comparison_caveats.md`
- `external_price_comparison_rules_line_by_line.md` -> `module_contracts/transversal/external_price_comparison_rules_line_by_line.md`
- `inspection_dossier_model.md` -> `module_contracts/transversal/inspection_dossier_model.md`
- `layer_model.md` -> `module_contracts/transversal/layer_model.md`
- `market_session_scope.md` -> `module_contracts/transversal/market_session_scope.md`
- `module_scope.md` -> `module_contracts/transversal/module_scope.md`
- `naming_authority.md` -> `module_contracts/transversal/naming_authority.md`
- `operational_boundaries.md` -> `module_contracts/transversal/operational_boundaries.md`
- `pipeline_price_view_policy.md` -> `module_contracts/transversal/pipeline_price_view_policy.md`
- `pipeline_price_view_policy_explained.md` -> `module_contracts/transversal/pipeline_price_view_policy_explained.md`
- `pipeline_price_view_rules_line_by_line.md` -> `module_contracts/transversal/pipeline_price_view_rules_line_by_line.md`
- `price_semantics_and_adjustment_policy.md` -> `module_contracts/transversal/price_semantics_and_adjustment_policy.md`
- `price_semantics_rules_line_by_line.md` -> `module_contracts/transversal/price_semantics_rules_line_by_line.md`
- `price_views_registry.md` -> `module_contracts/transversal/price_views_registry.md`
- `promotion_pipeline.md` -> `module_contracts/transversal/promotion_pipeline.md`
- `semantic_authority.md` -> `module_contracts/transversal/semantic_authority.md`

### Consumers

- `consumer_classes.md` -> `module_contracts/consumers/consumer_classes.md`
- `daily_return_labels_consumer_contract_v0_1.md` -> `module_contracts/consumers/daily_return_labels_consumer_contract_v0_1.md`
- `daily_return_labels_operational_landing_v0_1.md` -> `module_contracts/consumers/daily_return_labels_operational_landing_v0_1.md`
- `intraday_regime_features_consumer_contract_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_consumer_contract_v0_1.md`
- `intraday_regime_features_variable_taxonomy_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_variable_taxonomy_v0_1.md`
- `intraday_regime_features_operational_landing_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_operational_landing_v0_1.md`
- `intraday_regime_features_initial_materialization_results_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_initial_materialization_results_v0_1.md`
- `intraday_regime_features_semantic_pilot_results_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_semantic_pilot_results_v0_1.md`
- `intraday_regime_features_deferred_families_v0_1.md` -> `module_contracts/consumers/intraday_regime_features_deferred_families_v0_1.md`
- `price_view_consumer_integration_status.md` -> `module_contracts/consumers/price_view_consumer_integration_status.md`
- `price_view_integration_priority_plan_v0_1.md` -> `module_contracts/consumers/price_view_integration_priority_plan_v0_1.md`

### Daily

- `daily_acceptance_policy_explained.md` -> `module_contracts/daily/daily_acceptance_policy_explained.md`
- `daily_rules_explained_line_by_line.md` -> `module_contracts/daily/daily_rules_explained_line_by_line.md`
- `daily_adjusted_full_universe_promotion_plan_v0_1.md` -> `module_contracts/daily/daily_adjusted_full_universe_promotion_plan_v0_1.md`
- `daily_adjusted_incremental_materialization_plan_v0_1.md` -> `module_contracts/daily/daily_adjusted_incremental_materialization_plan_v0_1.md`
- `daily_adjusted_operational_landing_v0_1.md` -> `module_contracts/daily/daily_adjusted_operational_landing_v0_1.md`
- `daily_adjusted_pilot_manifest_v0_1.md` -> `module_contracts/daily/daily_adjusted_pilot_manifest_v0_1.md`
- `daily_adjusted_pilot_results_v0_1.md` -> `module_contracts/daily/daily_adjusted_pilot_results_v0_1.md`
- `daily_adjusted_pilot_results_v0_2.md` -> `module_contracts/daily/daily_adjusted_pilot_results_v0_2.md`

### Quotes

- `quotes_acceptance_policy_explained.md` -> `module_contracts/quotes/quotes_acceptance_policy_explained.md`
- `quotes_rules_explained_line_by_line.md` -> `module_contracts/quotes/quotes_rules_explained_line_by_line.md`

### Trades

- `trades_acceptance_policy_explained.md` -> `module_contracts/trades/trades_acceptance_policy_explained.md`
- `trades_rules_explained_line_by_line.md` -> `module_contracts/trades/trades_rules_explained_line_by_line.md`

### Minute

- `ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md` -> `module_contracts/minute/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `ohlcv_1m_split_normalized_operational_landing_v0_1.md` -> `module_contracts/minute/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `ohlcv_1m_split_normalized_pilot_manifest_v0_2.md` -> `module_contracts/minute/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
- `ohlcv_1m_split_normalized_pilot_results_v0_1.md` -> `module_contracts/minute/ohlcv_1m_split_normalized_pilot_results_v0_1.md`
- `ohlcv_1m_split_normalized_semantic_pilot_v0_1.md` -> `module_contracts/minute/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`

## Criterio de migracion

Cuando se promueva la migracion real, no bastara con mover archivos.

Habra que cerrar, como minimo, estas tres capas:

1. **mapa de paths**
- todo documento movido debe aparecer aqui;

2. **mapa de referencias**
- markdowns, notebooks, readouts, indices, changelog y agentes que lo mencionan;

3. **nota de compatibilidad**
- cualquier referencia antigua debe resolverse mediante este mapa hasta que todo el modulo quede actualizado.

## Veredicto

Este documento deja preparada la migracion correcta:

- explicita;
- versionada;
- y compatible con referencias antiguas.

La reorganizacion fisica ya no deberia empezar nunca desde cero ni depender de memoria humana.
