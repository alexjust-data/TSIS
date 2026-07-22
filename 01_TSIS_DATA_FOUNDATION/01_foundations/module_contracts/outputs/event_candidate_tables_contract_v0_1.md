# Event Candidate Tables Contract v0.1

## Estado

Tipo: event candidate tables contract.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
event_candidate_tables_contract_complete_for_declared_scope = true
daily_strategy_candidate_events_table_materialized = controlled_candidate_not_official
intraday_1m_strategy_candidate_events_table_materialized = controlled_candidate_not_official
event_windows_expansion_materialized = controlled_candidates_daily_and_intraday_not_official
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato inserta la capa que faltaba entre scanners y `event_state_table`:
las tablas candidatas de eventos daily y 1m.

Regla corta:

```text
scanner candidates = donde mirar / denominador candidato
event candidate tables = que evento candidato ocurrio y cual es su ancla legal
event_windows_table = que ventanas se abren alrededor del evento
event_state_table = fotografia legal observable anclada a evento/ventana/rol
outcomes_table = que paso despues, separado
```

Estas tablas no son tablas de estado. Son tablas de eventos/anclas que permiten
construir `event_state_table` sin mezclar deteccion, estado y outcome.

## 1. Por Que Existe Este Contrato

TSIS no puede construir un `event_state_table` serio para estrategias daily/1m si
solo tiene scanners y ventanas. Falta una capa intermedia que diga:

```text
este instrumento tuvo este evento candidato,
en este timestamp/date legal,
segun esta definicion versionada,
con esta evidencia de origen,
y con esta calidad/lineage.
```

Sin esa capa, futuros agentes podrian:

- usar `daily_scanner_candidates_table` como si fuera evento;
- usar `intraday_scanner_candidates_table` como si fuera estado;
- abrir ventanas sin `event_id` gobernado;
- meter thresholds de estrategia dentro del estado base;
- unir outcomes sin ancla legal reproducible;
- o entrenar/evaluar sobre eventos imposibles de auditar.

## 2. Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
```

## 3. Tablas Candidatas Definidas

Este contrato define dos targets conceptuales nuevos:

```text
daily_strategy_candidate_events_table_v0_1
intraday_1m_strategy_candidate_events_table_v0_1
```

Lectura:

```text
daily_strategy_candidate_events_table_v0_1
= eventos candidatos anclados a session_date/as_of_utc diario

intraday_1m_strategy_candidate_events_table_v0_1
= eventos candidatos anclados a event_timestamp_utc intradia 1m
```

No existen todavia como outputs materializados.

## 4. Relacion Con Scanners

### Daily

`daily_scanner_candidates_table_v0_3` responde:

```text
que tickers/dias entraron en el denominador candidato diario/in-play?
```

`daily_strategy_candidate_events_table_v0_1` debe responder:

```text
que evento candidato diario, segun que definicion, queda anclado para estudio?
```

Ejemplos de eventos daily candidates:

```text
daily_in_play_momentum_candidate
daily_gap_candidate
daily_first_red_day_candidate
daily_high_volume_breakout_candidate
daily_offering_context_candidate si existe fuente gobernada
```

Estos nombres son familias candidatas. Cada una necesita `event_definition_id`,
version, inputs, cutoff, source y validator antes de materializarse.

### Intradia 1m

`intraday_scanner_candidates_table` responde:

```text
que tickers/sesiones tuvieron detecciones intradia candidatas y cuando?
```

`intraday_1m_strategy_candidate_events_table_v0_1` debe responder:

```text
que evento candidato intradia, con event_timestamp_utc legal, queda anclado?
```

Ejemplos de eventos 1m candidates:

```text
intraday_first_motion_threshold_cross_candidate
intraday_vwap_reclaim_candidate
intraday_frontside_acceleration_candidate
intraday_failed_breakout_candidate
intraday_halt_resume_continuation_candidate
intraday_offering_dump_candidate si existe fuente gobernada
```

Estos nombres no significan que el evento sea causal ni rentable. Son anclas
candidatas para construir ventanas, estados y outcomes separados.

## 5. Regla Sobre Thresholds

Un threshold puede existir en una tabla de eventos si pertenece a una definicion
versionada de evento.

Ejemplo:

```text
first_cross_50
```

No debe entrar como verdad privilegiada del estado base, pero puede existir como:

```text
event_definition_id = intraday_first_cross_pct_v0_1
threshold_pct = 50
event_timestamp_utc = primer timestamp que cumple la definicion
```

Esto permite que AlphaEvolve, estadisticas o investigacion propongan variantes:

```text
first_cross_12
first_cross_37
first_cross_83
secuencia multi-condicion
sin threshold fijo
```

Pero cada variante debe quedar como definicion/version candidate. No se cambia
silenciosamente el estado observable base.

## 6. Grain Requerido

### `daily_strategy_candidate_events_table_v0_1`

Grain logico:

```text
event_definition_id + session_date + instrument_id + event_anchor_role
```

Primary key:

```text
daily_event_id
```

### `intraday_1m_strategy_candidate_events_table_v0_1`

Grain logico:

```text
event_definition_id + event_timestamp_utc + instrument_id + event_anchor_role
```

Primary key:

```text
intraday_event_id
```

## 7. Campos Minimos Comunes

Ambas tablas deben conservar:

```text
event_id
source_candidate_id
source_candidate_dataset_id
source_candidate_build_run_id
event_definition_id
event_definition_version
event_family
event_type
event_subtype
event_anchor_role
instrument_id
ticker
session_date
event_date
event_timestamp_utc
event_timestamp_policy
as_of_utc
event_availability_utc
detection_timestamp_utc
source_price_view
source_manifest_path
source_manifest_sha256
source_data_root_state
event_quality_state
event_selection_state
event_evidence_bundle
event_definition_params_bundle
cutoff_policy_version
leakage_policy_version
full_universe_claim
materialization_scope
schema_version
build_run_id
created_at_utc
```

Para daily events, `event_timestamp_utc` puede ser null si el evento solo es
EOD/date-level. En ese caso debe declararse:

```text
event_anchor_role = daily_session_event
event_timestamp_policy = date_level_or_eod_proxy
```

Para intradia 1m, `event_timestamp_utc` es obligatorio.

## 8. Prohibiciones

Estas tablas no pueden contener:

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
```

Tampoco pueden contener:

```text
winner/loser
MFE/MAE futuro
realized PnL
fill posterior
reward RL
best threshold discovered como verdad oficial
selected_by_model_without_definition
```

Permitido:

```text
outcome_join_key
event_window_join_key
market_state_join_key si ya existe
```

Solo como llaves/referencias, no como valores de resultado.

## 9. Inputs Permitidos Por Version

| Input | Uso permitido | Caveat |
| --- | --- | --- |
| `daily_scanner_candidates_table_v0_3` | seed/denominador para eventos daily | no es evento por si solo |
| `intraday_scanner_candidates_table_v0_1` | evidencia controlada raw para eventos 1m | raw-only, no promocion canonica |
| `intraday_scanner_candidates_table_v0_2_quote_guarded_candidate` | target preferido para eventos 1m defensibles | contrato requerido, no materializado aun |
| `halts_table_v0_1` | fuente de eventos halt existentes | ya alimenta `event_windows_table_v0_1` |
| `real_time_corporate_event_alerts_table` | eventos live/fundamental futuros | bloqueado hasta fuente/latencia |
| `news_context_table_v0_1` | posible contexto/catalyst as-of | no prueba causalidad ni evento por si solo |
| `fundamentals_asof_table_v0_1` | filings/as-of context | evento solo si definicion lo declara |

## 10. Relacion Con Event Windows

`event_candidate_tables` son upstream de `event_windows_table`.

Ruta:

```text
daily_strategy_candidate_events_table_v0_1
intraday_1m_strategy_candidate_events_table_v0_1
-> event_windows_table_v0_2_candidate o expansion equivalente
-> event_state_table candidate
```

`event_windows_table_v0_1` actual esta limitado a halts. No debe presentarse
como cobertura de todas las familias de eventos de estrategia.

La expansion futura de event windows debe declarar:

```text
source_event_table
source_event_id
event_family
event_definition_id
event_timestamp_utc/event_date
window_role
window_start_utc
window_end_utc
leakage_safe_as_pre_event_feature
valid_for_outcome_window_candidate
valid_for_event_state_candidate
```

## 11. Relacion Con Event State

`event_state_table` no debe inventar eventos. Debe anclarse a:

```text
event_id
event_window_id
decision_timestamp_utc
state_role
```

Por eso el orden correcto para estrategias daily/1m es:

```text
scanner candidates
-> event candidate tables
-> event windows
-> event_state_table
-> outcomes separados
-> evaluadores bloqueados
```

## 12. Relacion Con AlphaEvolve / ML / RL

AlphaEvolve puede proponer:

```text
nuevas definiciones de evento
nuevos thresholds
nuevas combinaciones de condiciones
nuevos detectores intradia
nuevas ventanas alrededor de eventos
```

Pero esas propuestas deben entrar como:

```text
event_definition_candidate
candidate event table output
manifest/evaluator result
```

No pueden modificar silenciosamente:

```text
market_state_table base
event_state_table base
outcomes
labels
rewards
```

ML/RL no puede consumir estas tablas como labels o rewards. Las puede usar como
anclas/denominador para construir `event_state` y outcomes separados.

## 13. Validators Requeridos Antes De Materializar

Futuros validators deben fallar si:

| Validator | Debe fallar si |
| --- | --- |
| `event_bad_missing_event_definition_id` | evento sin definicion versionada |
| `event_bad_missing_source_candidate` | no hay lineage a scanner/source event |
| `event_bad_intraday_missing_timestamp` | evento 1m sin `event_timestamp_utc` |
| `event_bad_daily_timestamp_claim` | evento daily date-level afirma precision intradia sin evidencia |
| `event_bad_future_availability` | `event_availability_utc > as_of_utc/decision cutoff` |
| `event_bad_outcome_inline` | outcomes/labels/rewards en la tabla de eventos |
| `event_bad_threshold_without_definition` | threshold usado sin `event_definition_id/version` |
| `event_bad_raw_only_promoted` | evento 1m raw-only marcado como canonico/promoted |
| `event_bad_full_universe_claim` | full universe sin contrato/cobertura |
| `event_bad_missing_manifest_lineage` | faltan manifest/hash/build ids |

## 14. Siguiente Trabajo Permitido

Con los schema contracts daily/1m ya cerrados, el siguiente trabajo permitido es:

```text
1. implementar validators ejecutables de event candidate tables
2. builders/materializacion candidate para daily_strategy_candidate_events_table_v0_1 DONE controlled
3. builders/materializacion candidate para intraday_1m_strategy_candidate_events_table_v0_1 DONE controlled
4. elegir una primera familia de evento daily/1m para fixture controlado
5. expandir event_windows para source_event_table != halts_table_v0_1
6. construir event_state fixture anclado a esos eventos
```

No queda permitido todavia:

```text
materializacion oficial full-universe
ML/RL training directo
AlphaEvolve evaluator production
outcomes inline
promocion de intraday raw-only como canonico
```

## 15. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| separacion scanner/event/event_window/event_state declarada | `done` |
| daily strategy candidate events target definido | `done` |
| intraday 1m strategy candidate events target definido | `done` |
| campos minimos comunes definidos | `done` |
| reglas sobre thresholds/versiones definidas | `done` |
| relacion con event_windows declarada | `done` |
| relacion con event_state declarada | `done` |
| validators futuros definidos | `done` |
| no materializa tablas ni habilita ML/RL/AlphaEvolve | `done` |

Status final:

```text
event_candidate_tables_contract_v0_1 = complete_for_contract_defined_scope
```
## 16. Actualizacion 2026-07-04 - Schema Contracts Cerrados

Despues de cerrar este contrato, se crearon los dos schema contracts que estaban
marcados como siguiente trabajo permitido:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
```

Lectura actualizada:

```text
schema contracts daily/1m = DONE
validators contract de event candidate tables = DONE
validators ejecutables y builders/materializacion candidate daily/1m = DONE controlled
event_windows daily controlled = DONE; event_windows intradia controlled = DONE; wider/full-universe = PENDING
```

Los schemas no materializan tablas. Solo fijan grano, columnas obligatorias,
timestamp policies, lineage, quality gates, no-outcomes y quote-guarded promotion
rule para la ruta intradia.
## 17. Actualizacion 2026-07-04 - Validators Contract Cerrado

Despues de cerrar los schema contracts, se creo el contrato de validators:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
event_candidate_table_validators_contract_v0_1 = complete_for_contract_defined_scope
```

Lectura actualizada:

```text
schema contracts daily/1m = DONE
validators contract = DONE
validators ejecutables = DONE fixture-scope y tabla controlada
builders/materializacion candidate daily/1m = DONE controlled
event_windows daily controlled = DONE; event_windows intradia controlled = DONE; wider/full-universe = PENDING
```

El contrato de validators no implementa codigo. Fija que debe fallar antes de
permitir builders/materializacion y consumo downstream.


## Evidencia 2026-07-05 - Intraday 1m Candidate Quote-Guarded Controlado

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
source = E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/intraday_1m_strategy_candidate_events_table_v0_1_candidate/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_from_master_intraday_qg_manifest.json
validator_status = passed
source_session_count = 58
event_candidate_rows = 5
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
alphaevolve_production_enabled_rows = 0
```

Lectura correcta: este contrato ya tiene evidencia de materializacion controlada para daily y para intradia 1m quote-guarded. Sigue sin existir promocion oficial/full-universe ni permission para ML/RL/AlphaEvolve.

## Evidencia 2026-07-05 - Intraday 1m Event Windows Controladas

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_event_windows_candidate.py
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
source_event_count = 5
row_count = 15
validator_status = passed
full_universe_claim_rows = 0
rl_state_component_candidate_rows = 0
```

Lectura correcta: event_windows intradia existe solo como candidato controlado/no oficial. La ventana `post_event_30m` es frontera de outcome, no feature de estado.
