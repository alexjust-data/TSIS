# Paths de lectura para creacion de tablas de estado/features

Status: reading_index_not_authority
Scope: rutas de documentos que pudieran o debieran leerse para crear/promover `014-018` y dependencias relacionadas.
Authority: no
Source of truth: contratos, schemas, registries, policies, validators y manifests en `01_TSIS_backtest_SmallCaps/01_foundations`.

---

Esta es la lista que yo leeria para crear o promover `014-018` y sus dependencias. La autoridad real esta en `01_foundations`; `003_STATE_tables` es indice/aclaracion secundaria.

## Base TSIS

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
C:\TSIS_Data\README.md
C:\TSIS_Data\00_CTO\TSIS_LAB_ARCHITECTURE_v3.md
C:\TSIS_Data\00_TSIS_Lab\README.md
G:\TSIS\data\README.md
```

## Indice y aclaraciones en `003_STATE_tables`

```text
C:\TSIS_Data\00_CTO_1\003_STATE_tables\README.md
C:\TSIS_Data\00_CTO_1\003_STATE_tables\state_table_creation_process_v0_1.md
C:\TSIS_Data\00_CTO_1\003_STATE_tables\revision_completa_data_features_estados_tsis.md
C:\TSIS_Data\00_CTO_1\003_STATE_tables\aclaracion_01_features_microestructura.md
C:\TSIS_Data\00_CTO_1\003_STATE_tables\confirmacion_arquitectura_eventos_tsis.md
```

## Arquitectura CTO relacionada

```text
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\market_state_representation_contract_v0_1.md
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\market_state_representation_source_file_map_v0_1.md
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\00_CTO\market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\00_SCANNER_CANDIDATE_SELECTION\scanner_to_market_state_promotion_path_v0_1.md
```

## Contratos/protocolos centrales

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_build_loop_runbook_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_snapshot_roles_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_canonical_vs_representation_layer_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md
```

## `014` / `015` / `016` / `017` / `018` especificos

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\intraday_scanner_candidates_table_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\intraday_scanner_framework_and_definitions_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\event_candidate_tables_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\event_candidate_table_validators_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\event_research_design_contract_v0_1.md
```

## Lineage controlado

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md
```

## Schemas, dataset contracts, policies, registries y validators

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\master_intraday_bar_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\microstructure_features_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\event_state_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\event_windows_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\outcomes_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\intraday_scanner_candidates_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\master_intraday_bar_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\microstructure_features_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\event_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\master_intraday_bar_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\microstructure_features_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\event_state_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\master_intraday_bar_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\microstructure_features_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\market_state_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\event_state_table_validators.md
```

## Configs de builder/materializacion

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\master_intraday_bar_table_quote_guarded_candidate_v0_2.json
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\microstructure_features_seed_windows_v0_1.csv
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\market_state_builder_fixture_v0_1.json
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\event_state_builder_fixture_v0_1.json
```

## Orden practico de lectura

```text
1. Base TSIS.
2. C:\TSIS_Data\00_CTO_1\003_STATE_tables\README.md
3. data_foundation_outputs_status_matrix_v0_1.md
4. data_foundation_outputs_target_contract_v0_1.md
5. market_state_coverage_and_lookback_policy_v0_1.md
6. market_state_event_state_composition_contract_v0_1.md
7. state_builder_contract_v0_1.md
8. Contrato/plan especifico de la tabla que se vaya a tocar.
9. Schema canonico de esa tabla.
10. Dataset contract.
11. Consumption policy.
12. Registry entry.
13. Validators.
14. Configs/manifests del builder o run controlado.
```

