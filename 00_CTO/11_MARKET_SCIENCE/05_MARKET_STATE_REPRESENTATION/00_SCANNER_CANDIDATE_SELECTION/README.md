# Scanner Candidate Selection

Fecha: 2026-06-30
Estado: candidate_policy
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION`
Authority type: CTO architecture and navigation

## Rol

Esta carpeta explica, a nivel CTO, como TSIS debe seleccionar candidatos
in-play antes de construir `market_state` o `event_state`.

No es la autoridad operativa de schemas, builders, validators o registries.

La autoridad operativa vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

Esta carpeta existe para que un humano o agente entienda:

- por que existe una capa de scanner;
- que problema resuelve;
- que tablas y contratos ya existen;
- que no debe confundirse con estado, evento, estrategia, label o reward;
- como conecta con DAS, Market State, Event State, ML/RL y AlphaEvolve.

## Regla central

```text
El scanner decide donde mirar.
El market_state decide que sabia TSIS en ese momento.
La estrategia decide si ese estado encaja con una hipotesis.
ML/RL no entrena directamente sobre scanner rows.
```

## Orden de lectura

1. `scanner_candidate_selection_architecture_v0_1.md`
2. `scanner_definitions_trade_station_vs_broad_discovery_v0_1.md`
3. `scanner_table_and_contract_map_v0_1.md`
4. `scanner_to_market_state_promotion_path_v0_1.md`

## Cadena conceptual

```text
raw / audited foundation tables
-> scanner_candidate_selection
-> daily_scanner_candidates_table
-> strategy-specific experimental state tables
-> event_state_candidate / market_state_candidate
-> institutional_market_state
-> ML/RL / backtest / decision / AlphaEvolve evaluators
```

## No-goals

Esta carpeta no debe:

- redefinir schemas canonicos;
- duplicar dataset registry;
- reemplazar validators;
- guardar outputs de runs;
- contener parquets;
- convertirse en una estrategia;
- esconder thresholds ejecutables no versionados;
- promocionar un scanner como feature store ML/RL.

## Fuentes operativas relacionadas

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/scanner_definitions/
01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table.py
```

