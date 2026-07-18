# State Table Creation Process v0.1

## Proposito

Este documento resume el proceso operativo para crear y promover una tabla de estado en TSIS.

Alcance:

- `market_state_table_v0_1`
- `event_state_table_v0_1`

Esta nota vive en `C:\TSIS_Data\00_CTO_1\003_STATE_tables\` como superficie secundaria de lectura. La autoridad sigue estando en los contratos, schemas, registries, validators, scripts, tests y manifests ubicados en `01_foundations`, `scripts`, `tests` y las raices fisicas de datos.

## Estado institucional actual

```text
market_state_table_v0_1 = contract_defined_not_materialized
event_state_table_v0_1 = contract_defined_not_materialized
market_state_table_v0_1_candidate_microstructure_halt_controlled = controlled_candidate_not_promoted
event_state_table_v0_1_candidate_microstructure_halt_controlled = controlled_candidate_not_promoted
market_state_table_v0_1_candidate_intraday_quote_guarded_controlled = controlled_candidate_not_promoted
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled = controlled_candidate_not_promoted
```

Ningun candidato actual debe tratarse como tabla oficial, full-universe, ML/RL-ready, backtest-core ni execution truth.


## Fase 0. DiseÃ±o de la representaciÃ³n

Este documento comienza cuando ya existe una decisiÃ³n de que una representaciÃ³n merece convertirse en una tabla.

Esa decisiÃ³n no debe tomarse diseÃ±ando directamente columnas o schemas.

Antes de iniciar el proceso de materializaciÃ³n debe responderse, al menos, a las
siguientes preguntas:

```text
Â¿QuÃ© fenÃ³meno o representaciÃ³n queremos materializar?

â†“

Â¿Por quÃ© merece existir como entidad propia?

â†“

Â¿QuÃ© preguntas cientÃ­ficas debe responder?

â†“

Â¿QuÃ© otras representaciones la consumen?

â†“

Â¿QuÃ© informaciÃ³n mÃ­nima necesita contener?

â†“

Ahora sÃ­:

Â¿QuÃ© atributos debe tener?
```

Este orden evita diseÃ±ar tablas por intuiciÃ³n.

Cada atributo debe estar justificado por una necesidad de representaciÃ³n,
investigaciÃ³n o consumo dentro de la arquitectura de TSIS.

Por este motivo, antes de iniciar el diseÃ±o de una nueva familia de tablas,
debe realizarse una revisiÃ³n arquitectÃ³nica conjunta.

Por ejemplo, antes de definir individualmente las tablas:

```text
013
014
015
016
017
018
```

conviene responder primero:

```text
Â¿CuÃ¡l es la responsabilidad exacta de cada una?

Â¿QuÃ© relaciones existen entre ellas?

Â¿QuÃ© consume cada tabla?

Â¿QuÃ© produce cada tabla?

Â¿DÃ³nde termina una representaciÃ³n y comienza la siguiente?
```

Una vez definidas correctamente esas fronteras, la definiciÃ³n de atributos,
schemas, builders y contratos resulta mucho mÃ¡s sencilla y coherente con el
resto de la arquitectura de TSIS.

Solo entonces comienza el proceso de materializaciÃ³n descrito en este documento.

**Proceso**

```
Fase 0

DiseÃ±o conceptual

â†“

Fase 1

MaterializaciÃ³n

â†“

Fase 2

ConstrucciÃ³n

â†“

Fase 3

ValidaciÃ³n

â†“

Fase 4

PromociÃ³n
```




## Proceso exacto

### 1. Definir el target

La tabla se declara primero como salida objetivo de Data Foundation.

Documentos principales:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
```

En esta fase la lectura correcta es:

```text
market_state_table_v0_1 = contract_defined_not_materialized
event_state_table_v0_1 = contract_defined_not_materialized
```

### 2. Separar semantica

`market_state_table` representa una fotografia legal/as-of del instrumento y mercado en un `decision_timestamp`.

`event_state_table` representa ese estado anclado a un evento, ventana y `state_role`.

No pueden vivir inline en la tabla base:

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
strategy__*
signal__*
```

Outcomes, labels y rewards deben mantenerse separados y unirse despues mediante keys/manifests gobernados.

### 3. Cerrar contratos base

Antes de materializar cualquier candidato real, deben existir contratos que gobiernen composicion, builder, cobertura, timestamps, roles y observables.

Paths:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_build_loop_runbook_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_snapshot_roles_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_canonical_vs_representation_layer_contract_v0_1.md
```

### 4. Declarar linaje RAW -> consumo de estado

Cada componente usado por una state table debe explicar su cadena completa:

```text
RAW/staged source
-> derivadas intermedias
-> componente gobernado
-> state builder
-> consumer
```

Debe documentar:

- source roots;
- builders;
- manifests;
- summaries;
- hashes;
- formulas;
- cutoffs/as-of;
- quality gates;
- consumo permitido;
- gaps abiertos.

Paths:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1.md
```

Para 1m quote-guarded, la ruta controlada actual es:

```text
ohlcv_1m raw
+ quote lineage / repair manifest
-> master_intraday_bar_table_v0_2_candidate_quote_guarded
-> market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
-> intraday_1m_strategy_candidate_events_table_v0_1_candidate
-> event_windows_table_v0_1_candidate_intraday_1m_strategy_events
-> event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
-> outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled separado como y
```

### 5. Definir schema y dataset contract

Se fijan:

- columnas obligatorias;
- primary key;
- grano;
- namespaces permitidos;
- prohibited prefixes;
- layout esperado;
- flags de consumo;
- `full_universe_claim`;
- registry y consumption policy.

Paths:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\event_state_table_schema_contract.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\event_state_table_dataset_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\market_state_table_registry_entry.yaml
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\event_state_table_registry_entry.yaml
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\event_state_table_consumption_policy.md
```

### 6. Crear builder controlado

El builder no debe escribir una tabla oficial por defecto.

Primero debe poder producir:

- fixture determinista;
- candidato controlado;
- manifest;
- summary;
- validaciones;
- `build_run_id`;
- source paths;
- hashes;
- flags de no-promocion.

Scripts:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\_state_fixture_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_market_state_table.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_event_state_table.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_market_state_intraday_quote_guarded_candidate.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\materialize_event_state_intraday_quote_guarded_candidate.py
```

Configs/fixtures:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\market_state_builder_fixture_v0_1.json
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\configs\data_foundation_outputs\event_state_builder_fixture_v0_1.json
C:\TSIS_Data\tests\fixtures\data_foundation_outputs\market_event_state_v0_1\
```

### 7. Emitir artefactos reproducibles

Cada ejecucion relevante debe dejar:

```text
data/parquet
manifest
summary
build_run_id
created_at_utc
source input paths
source manifest hashes
output tree hash
validator status
promotion status
full_universe_claim
consumer gates
```

Materializaciones candidatas verificadas en esta instalacion:

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

Runs controlados intradia:

```text
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1\_market_state_table_summary_v0_1_candidate_intraday_quote_guarded_controlled.csv

C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\
C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled\_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_summary.csv
```

### 8. Validar

Los validators deben comprobar:

- no leakage;
- cutoff/as-of legal;
- `component_as_of_utc <= decision_timestamp_utc`;
- ids unicos;
- roles validos;
- namespaces permitidos;
- no prohibited prefixes;
- no outcomes/labels/rewards inline;
- `full_universe_claim=false` para candidatos controlados;
- ML/RL/execution disabled salvo contrato explicito;
- source manifests presentes;
- hashes y build lineage reproducibles.

Paths:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\market_state_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\event_state_table_validators.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_market_state_table_contract.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_event_state_table_contract.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_market_state_intraday_quote_guarded_candidate_builder.py
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs\test_event_state_intraday_quote_guarded_candidate_builder.py
```

### 9. Registrar candidato

Si el build y los validators pasan, el output se registra como candidato controlado:

```text
status = controlled_candidate_not_promoted
promotion_level = controlled_candidate
full_universe_claim = false
direct_ml_rl_backtest_execution_use_allowed = false
```

Ese estado permite inspeccion, pattern discovery controlado o prueba de integracion, pero no consumo institucional final.

### 10. Actualizar documentacion institucional

Todo cambio material debe actualizar:

- status matrix;
- target contract;
- schemas si cambia columna o semantica;
- dataset registry;
- consumption policy;
- validators;
- changelog si cambia semantica operativa;
- README/indice secundario si afecta a esta carpeta.

Paths secundarios relevantes:

```text
C:\TSIS_Data\00_CTO_1\003_STATE_tables\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\016\016.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\017\017.md
```

### 11. Promocion oficial

Una tabla solo puede pasar de candidato a oficial si existen y pasan:

- source roots oficiales o parity documentada;
- coverage declarado;
- manifests completos;
- validators ejecutables;
- leakage/adversarial tests;
- recomputation tests;
- hashes reproducibles;
- compatibilidad downstream;
- status matrix actualizado;
- registry actualizado;
- consumption policy actualizado;
- decision explicita de promocion.

La promocion debe cambiar el estado de forma explicita. No basta con que exista un parquet ni con que un candidato tenga buen score.

## Regla final

Hasta que ocurra la promocion explicita:

```text
contract_defined_not_materialized != official
controlled_candidate_not_promoted != official
candidate_not_official != official
```

La trazabilidad manda sobre la rapidez. Si no se puede reconstruir codigo, config, dataset, manifest, run id, tests y status, la tabla no debe tratarse como institucional.


