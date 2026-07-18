# 03_TABLES_feature_engineering

## Current Role

This folder is now the table representation and feature engineering audit surface for TSIS applied architecture.

Its central guardrail is:

```text
What do we need to know
to correctly describe
the state of the market
at an instant t?
```

And:

```text
What information can help
explain or predict
the future behavior
of the phenomenon represented?
```

Core documents:

| Document | Function |
| --- | --- |
| `TABLES_REPRESENTATION_OF_MARKET.md` | Defines market representation families and variable admission rules. |
| `TABLE_REPRESENTATION_AUDIT_TEMPLATE.md` | Template for auditing each table technically against conceptual role, variables, hypotheses, consumers and evidence. |

The purpose is not to accumulate indicators. The purpose is to decide which variables deserve to exist, what hypothesis they represent and where they belong.

## Proposito

Esta carpeta es una superficie secundaria de lectura para las tablas de estado y salidas Data Foundation.
Sirve para tener juntos:

- los contratos/status clonados desde `01_foundations`;
- un indice ordenado de las salidas operativas por scope declarado;
- muestras impresas transpuestas de parquet para entender la forma fisica/logica de cada tabla.

No es una source of truth independiente.

## Regla de sincronizacion

Esta carpeta esta ligada a los originales. Si cambia informacion material en los documentos originales, la copia aqui debe actualizarse en la misma operacion.

Originales principales:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\leaf_slices\data_foundation_outputs_topology_20260629\
```

Copias/indice secundario:

```text
C:\TSIS_Data\00_CTO_1\003_TABLES\
```

## Documentos raiz

| Documento | Funcion |
| --- | --- |
| `data_foundation_outputs_target_contract_v0_1.md` | Copia secundaria del contrato objetivo de salidas Data Foundation. |
| `data_foundation_outputs_status_matrix_v0_1.md` | Copia secundaria de la matriz de estado. Es el documento que se debe leer antes de asumir que una tabla esta lista. |
| `README.md` | Indice operativo de esta carpeta secundaria. |

## Corpus de creacion de state tables

Esta seccion concentra los paths usados para reconstruir el proceso de creacion de:

- `market_state_table_v0_1`
- `event_state_table_v0_1`

Lectura obligatoria: esta carpeta es indice secundario. La autoridad sigue viviendo en `01_foundations`, scripts, tests y manifests fisicos.

### Superficie secundaria

```text
C:\TSIS_Data\00_CTO_1\003_TABLES\
C:\TSIS_Data\00_CTO_1\003_TABLES\README.md
C:\TSIS_Data\00_CTO_1\003_TABLES\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\00_CTO_1\003_TABLES\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\016\016.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\017\017.md
```

### Source of truth de estado y status

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\00_CTO\market_state_tables_status_and_operating_map_2026_07_01_v3.md
```

### Contratos de creacion y composicion

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_build_loop_runbook_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md
```

### Contratos auxiliares que gobiernan el builder

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_snapshot_roles_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_canonical_vs_representation_layer_contract_v0_1.md
```

### Schemas canonicos

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\event_state_table_schema_contract.md
```

### Dataset contracts, registry y consumption policies

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\event_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\market_state_table_registry_entry.yaml
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\event_state_table_registry_entry.yaml
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\event_state_table_consumption_policy.md
```

### Validators documentales

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\market_state_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\event_state_table_validators.md
```

### Linaje RAW -> consumo de estado

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1.md
```

### Scripts que crean o prueban la creacion

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\_state_fixture_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_market_state_table.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_event_state_table.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_market_state_intraday_quote_guarded_candidate.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_event_state_intraday_quote_guarded_candidate.py
```

### Configs y fixtures de builder

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\market_state_builder_fixture_v0_1.json
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\event_state_builder_fixture_v0_1.json
C:\TSIS_Data\tests\fixtures\data_foundation_outputs\market_event_state_v0_1\
```

### Tests ejecutables

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_market_state_table_contract.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_event_state_table_contract.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_market_state_intraday_quote_guarded_candidate_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_event_state_intraday_quote_guarded_candidate_builder.py
```

### Materializaciones candidatas fisicas

Raiz fisica verificada en esta instalacion:

```text
G:\TSIS\data\data_foundation_outputs\
```

Los contratos historicos pueden referenciar `E:\TSIS\data\...`; para esta instalacion, los outputs fisicos verificados de state tables estan bajo `G:\TSIS\data\...`.

```text
G:\TSIS\data\data_foundation_outputs\market_state_table\
G:\TSIS\data\data_foundation_outputs\market_state_table\market_state_table_v0_1_candidate_microstructure_halt_controlled\
G:\TSIS\data\data_foundation_outputs\market_state_table\_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
G:\TSIS\data\data_foundation_outputs\market_state_table\_market_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv

G:\TSIS\data\data_foundation_outputs\event_state_table\
G:\TSIS\data\data_foundation_outputs\event_state_table\event_state_table_v0_1_candidate_microstructure_halt_controlled\
G:\TSIS\data\data_foundation_outputs\event_state_table\_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
G:\TSIS\data\data_foundation_outputs\event_state_table\_event_state_table_summary_v0_1_candidate_microstructure_halt_controlled.csv
```

### Runs controlados intradia quote-guarded

```text
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\market_state_table_v0_1_candidate_intraday_quote_guarded_controlled\
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\_market_state_table_summary_v0_1_candidate_intraday_quote_guarded_controlled.csv

C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\
C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled\data.parquet
C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_summary.csv
```

### Cadena relacionada que alimenta o consume state tables

Estos artefactos no son `market_state_table` ni `event_state_table`, pero forman parte del loop de creacion y consumo:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\event_candidate_tables_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\event_candidate_table_validators_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\daily_strategy_candidate_events_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\intraday_1m_strategy_candidate_events_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\outcomes_table_schema_contract.md
```

Scripts y tests relacionados:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\validate_event_candidate_tables.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_strategy_candidate_events_table.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_intraday_1m_strategy_event_windows_candidate.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_intraday_1m_event_outcomes_candidate.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_event_candidate_table_validators.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_strategy_candidate_events_table_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_intraday_1m_strategy_candidate_events_from_master_intraday_qg.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_intraday_1m_strategy_event_windows_candidate_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_intraday_1m_event_outcomes_candidate_builder.py
```

### Estado institucional de estos paths

```text
market_state_table_v0_1 = contract_defined_not_materialized
event_state_table_v0_1 = contract_defined_not_materialized
market_state_table_v0_1_candidate_microstructure_halt_controlled = controlled_candidate_not_promoted
event_state_table_v0_1_candidate_microstructure_halt_controlled = controlled_candidate_not_promoted
market_state_table_v0_1_candidate_intraday_quote_guarded_controlled = controlled_candidate_not_promoted
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled = controlled_candidate_not_promoted
```

Nada en esta carpeta promueve por si mismo una tabla oficial, full-universe, ML/RL-ready, backtest-core ni execution truth.

## Carpetas de muestras

Las carpetas `000` a `013` representan salidas operativas para su scope declarado o manifest/overlay documentado. Las carpetas `014` a `018` son slots pendientes: tienen un sample `.md` nombrado como la carpeta, pero no contienen muestra operativa porque esas familias no estan promovidas/full-universe. Cuando sea viable, cada carpeta debe contener muestra impresa transpuesta: campos en filas y muestras en columnas.

| Carpeta | Tabla / salida | Lectura correcta | Muestra |
| --- | --- | --- | --- |
| `000_instrument_master` | `instrument_master_v0_1` | Universo/identidad LT1B, 4,824 instrumentos. | OK |
| `001_market_calendar` | `market_calendar_v0_1` | Sesiones XNYS, 2005-01-03 a 2026-03-09. | OK |
| `002_expected_data_calendar` | `expected_data_calendar_v0_1` | Denominador esperado de cobertura; no prueba presencia fisica. | OK |
| `003_dataset_certification_matrix` | `dataset_certification_matrix_v0_1` | Gates por familia; no valida fila ticker/date individual. | OK |
| `004_master_daily_table` | `master_daily_table_v0_1` | Tabla diaria operativa para research/backtest diario donde los flags lo permitan. | OK |
| `005_corporate_actions_table` | `corporate_actions_table_v0_1` | Splits/dividendos/cambios ticker para contexto y price views. | OK |
| `006_halts_table` | `halts_table_v0_1` | Eventos de halts/suspensions para su scope declarado. | OK |
| `007_event_windows_table` | `event_windows_table_v0_1` | Ventanas derivadas principalmente de halts; no todas las familias de eventos. | OK |
| `008_outcomes_table` | `outcomes_table_v0_1` | Outcomes diarios post-evento; no outcome intradia ni reward RL. | OK |
| `009_fundamentals_asof_table` | `fundamentals_asof_table_v0_1` | Contexto fundamental as-of tras join explicito. | OK |
| `010_news_context_table` | `news_context_table_v0_1` | Contexto/news historico as-of; no prueba causalidad ni feed live. | OK |
| `011_short_context_table` | `short_context_table_v0_1` | Short interest/short volume por fuente; no borrow/SSR. | OK |
| `012_regime_context_table` | `regime_context_table_v0_1` | Contexto de regimen por sesion; no estado intradia causal. | OK |
| `013_ohlcv_1m_quote_guarded` | `repair_manifest_lt1b_v0_1` | Manifest promovido/PASS para overlay quote-guarded 1m; no tabla fisica institucional de barras 1m. | Pendiente especial |
| `014` | `master_intraday_bar_table` | Slot pendiente para tabla intradia oficial/promovida; hoy piloto/candidato, no full-universe. | Explicativo |
| `015` | `microstructure_features_table` | Slot pendiente para microestructura oficial/promovida; hoy seed/candidato controlado. | Explicativo |
| `016` | `market_state_table` | Slot pendiente para market state oficial; hoy candidatos controlados/no promovidos. | Explicativo |
| `017` | `event_state_table` | Slot pendiente para event state oficial; hoy candidatos controlados/no promovidos. | Explicativo |
| `018` | `intraday_scanner_candidates_table` | Slot pendiente para scanner/candidatos intradia si se consolidan como superficie gobernada. | Explicativo |

## Lectura operativa

No todas las salidas son completas en el sentido `full universe x ticker x tiempo x estado`.

Lo correcto es:

- Data Foundation tiene varias salidas completas y operativas para su scope declarado.
- La base diaria esta bastante operativa.
- `expected_data_calendar_v0_1` sirve como denominador de cobertura, no como prueba de que todos los datos fisicos existan.
- `ohlcv_1m_quote_guarded` tiene un repair manifest promovido/PASS para el universo LT1B declarado.
- Las tablas oficiales de estado full-universe todavia no estan materializadas/promovidas.

Lo que no debe decirse:

```text
todo esta completo para ML/RL/backtesting intradia full-universe
```

Lo correcto es:

```text
Data Foundation tiene varias salidas completas para su scope declarado.
La capa 1m quote-guarded tiene manifest completo como overlay.
Las tablas oficiales de estado full-universe todavia no estan materializadas/promovidas.
```

## Limites criticos

`market_state_table_v0_1` y `event_state_table_v0_1` no son tablas oficiales materializadas/promovidas.
Existen candidatos/controlados, pero no deben tratarse como tablas finales, full-universe, ML/RL-ready, backtest-core ni execution truth.

Tambien deben leerse como no promovidas/full-universe:

- `master_intraday_bar_table_v0_1`: scope piloto, `full_universe_claim=false`.
- `master_intraday_bar_table_v0_2_candidate_quote_guarded`: candidato scoped, no oficial/full-universe.
- `microstructure_features_table`: seed/candidato controlado, no full-universe.
- `market_state_table` candidates: controlados/no promovidos.
- `event_state_table` candidates: controlados/no promovidos.

## Nota sobre 1m quote-guarded

Hay dos capas distintas:

1. Manifest promovido:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
status = PASS
completed_tickers = 4824
missing_tickers = 0
manifest_rows = 301278342
```

Esto significa que el manifest de reparacion quote-guarded esta completo para el universo LT1B declarado y se usa como overlay/vista sobre raw `ohlcv_1m`.

2. Materializacion fisica candidate:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1
```

Existe un arbol fisico candidate para 2005..2026, pero no debe tratarse como dataset institucional/promoted full-universe limpio: los summaries disponibles muestran `complete_with_failures` / `failed_tickers > 0` para 2015..2020, y el builder lo marca `candidate_not_official` / `full_universe_claim=false`.

## Raices de datos

Raiz fisica usada/verificada en esta instalacion:

```text
G:\TSIS\data\data_foundation_outputs\
G:\TSIS\data\data_foundation_outputs\instrument_master\
G:\TSIS\data\data_foundation_outputs\market_calendar\
G:\TSIS\data\data_foundation_outputs\expected_data_calendar\
G:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\
G:\TSIS\data\data_foundation_outputs\master_daily_table\
G:\TSIS\data\data_foundation_outputs\corporate_actions_table\
G:\TSIS\data\data_foundation_outputs\halts_table\
G:\TSIS\data\data_foundation_outputs\event_windows_table\
G:\TSIS\data\data_foundation_outputs\outcomes_table\
G:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\
G:\TSIS\data\data_foundation_outputs\news_context_table\
G:\TSIS\data\data_foundation_outputs\short_context_table\
G:\TSIS\data\data_foundation_outputs\regime_context_table\
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\
G:\TSIS\data\data_foundation_outputs\market_state_table\
G:\TSIS\data\data_foundation_outputs\event_state_table\
```

Nota: algunos contratos historicos referencian `E:\TSIS\data\...`. Esta carpeta conserva la semantica contractual, pero documenta `G:\TSIS\data\...` como raiz fisica usada/verificada en esta instalacion.

## Evidencia y runs

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\
C:\TSIS_Data\tests\data_foundation_outputs\
C:\TSIS_Data\tests\test_runs\
```

## Regla de uso para agentes

Antes de usar cualquier tabla de esta carpeta como base para research, backtest, ML/RL o decision institucional:

1. Leer `data_foundation_outputs_status_matrix_v0_1.md`.
2. Confirmar `status`, `scope`, filas, rango temporal y exclusiones.
3. Usar el sample `.md` nombrado como la carpeta solo para entender forma y valores de ejemplo.
4. No convertir una muestra impresa en certificacion de cobertura.
5. No promover candidatos ni state tables sin los gates indicados en `01_foundations`.





