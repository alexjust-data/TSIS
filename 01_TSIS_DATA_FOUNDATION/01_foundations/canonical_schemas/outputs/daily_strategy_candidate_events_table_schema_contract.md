# Daily Strategy Candidate Events Table Schema Contract `v0_1`

Status: `canonical_schema_target_not_materialized`

Dataset target:

```text
daily_strategy_candidate_events_table_v0_1
```

Physical target reserved:

```text
E:/TSIS/data/data_foundation_outputs/daily_strategy_candidate_events_table/daily_strategy_candidate_events_table_v0_1.parquet
```

## 1. Rol

`daily_strategy_candidate_events_table_v0_1` es la tabla gobernada de anclas de
eventos candidatos diarios/date-level para investigacion de estrategias TSIS.

Responde:

```text
que evento candidato diario ocurrio,
para que instrumento/sesion,
bajo que definicion de evento versionada,
con que ancla legal y lineage.
```

No es:

- una tabla de scanner;
- una tabla de market state;
- una tabla de event state;
- una tabla de outcomes;
- una tabla de labels/rewards;
- una tabla de verdad de ejecucion/fills;
- un dataset de entrenamiento AlphaEvolve/ML/RL.

## 2. Relacion Con Tablas Cercanas

Separacion correcta:

```text
daily_scanner_candidates_table
= donde mirar / denominador candidato diario

daily_strategy_candidate_events_table
= que evento candidato diario queda anclado y versionado

event_windows_table
= que ventanas se abren alrededor del evento

event_state_table
= fotografia legal observable anclada a evento/ventana/rol

outcomes_table
= que paso despues, unido aparte
```

`daily_strategy_candidate_events_table_v0_1` puede referenciar candidatos de
scanner. No debe copiar la seleccion del scanner como verdad causal.

## 3. Grano

Grano logico:

```text
event_definition_id + session_date + instrument_id + event_anchor_role
```

Primary key:

```text
daily_event_id
```

Id canonico para joins entre tablas:

```text
event_id
```

En v0.1, `daily_event_id` puede ser igual a `event_id` si la policy de IDs
declara ese mapping. Los joins downstream deben usar `event_id`.

## 4. Componentes Fuente Permitidos

Componentes fuente permitidos para el target schema v0.1:

```text
daily_scanner_candidates_table_v0_3 candidate/replay outputs
master_daily_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
fundamentals_asof_table_v0_1 cuando la definicion de evento lo declare
news_context_table_v0_1 cuando la definicion de evento lo declare
short_context_table_v0_1 cuando la definicion de evento lo declare
regime_context_table_v0_1 cuando la definicion de evento lo declare
halts_table_v0_1 cuando la definicion de evento declare contexto de halts
```

Clases de fuente bloqueadas/futuras:

```text
float_context_table hasta que exista fuente/schema point-in-time
real_time_corporate_event_alerts_table hasta que exista fuente con received_utc/latencia
short_sale_constraints_table hasta que exista fuente materializada
live broker/vendor scanners hasta que exista contrato de received_at_utc y replay
```

Una definicion de evento diario que afirme precision intradia debe apuntar a una
fuente intradia que pruebe ese timestamp. Si no, el evento sigue siendo anclado a
fecha/as_of.

## 5. Columnas Requeridas

### Identidad

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `daily_event_id` | yes | id estable y unico de la fila de evento diario |
| `event_id` | yes | id canonico usado por event windows y event state |
| `event_table_id` | yes | esperado `daily_strategy_candidate_events_table_v0_1` |
| `event_schema_version` | yes | esperado `daily_strategy_candidate_events_table_v0_1` |
| `event_definition_id` | yes | id de definicion de evento versionada |
| `event_definition_version` | yes | version de la definicion de evento |
| `event_family` | yes | familia amplia, por ejemplo `daily_gap`, `daily_momentum`, `daily_reversal` |
| `event_type` | yes | tipo concreto dentro de la familia |
| `event_subtype` | nullable | subtipo opcional |
| `event_anchor_role` | yes | rol del ancla, por ejemplo `daily_session_anchor`, `daily_eod_proxy`, `research_replay_anchor` |

### Instrumento Y Sesion

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `instrument_id` | yes | id temporal del instrumento |
| `ticker` | yes | ticker en mayusculas |
| `session_date` | yes | fecha de sesion del calendario de mercado |
| `event_date` | yes | fecha representada por el evento, normalmente igual a `session_date` |
| `market_timezone` | yes | timezone esperada del exchange/calendario |
| `listing_exchange` | nullable | contexto de listing/exchange cuando exista |
| `is_common_stock` | yes | flag heredada de instrumento |
| `is_lt1b_operational` | yes | flag heredada de universo |
| `instrument_identity_temporal_match` | yes | true solo si la identidad del instrumento es valida para la fecha del evento |
| `calendar_session_valid` | yes | true solo si la sesion existe en el calendario de mercado |

### Tiempo Y Disponibilidad

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `as_of_utc` | yes | timestamp en el que la fila de evento se considera conocida para replay/uso |
| `event_availability_utc` | yes | primer timestamp en que la evidencia del evento esta disponible para TSIS |
| `detection_timestamp_utc` | nullable | timestamp de deteccion del detector/scanner cuando exista |
| `event_timestamp_utc` | nullable | timestamp intradia del evento solo cuando este legalmente probado |
| `event_timestamp_policy` | yes | `date_level`, `session_close_available`, `intraday_proven` o `research_replay_proxy` |
| `decision_timestamp_policy_id` | yes | policy id del contrato de decision timestamp |
| `source_data_availability_cutoff_utc` | yes | maximo timestamp de disponibilidad de fuentes usado por esta fila |
| `contains_intraday_timestamp_claim` | yes | true si la fila afirma un timestamp intradia preciso |

### Lineage Del Candidato Fuente

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `source_candidate_id` | nullable | id upstream de scanner/source candidate si el evento viene de un candidato |
| `source_candidate_dataset_id` | yes | dataset id upstream o `direct_event_definition_source` |
| `source_candidate_build_run_id` | nullable | build run id de la fuente upstream |
| `source_candidate_quality_state` | nullable | estado de calidad de la fuente upstream |
| `source_scanner_definition_id` | nullable | id de definicion del scanner upstream si aplica |
| `source_scanner_definition_version` | nullable | version de definicion del scanner upstream si aplica |
| `source_scanner_run_id` | nullable | run id del scanner upstream si aplica |
| `source_price_view` | nullable | price view usada por la definicion del evento |
| `source_manifest_path` | yes | bundle de manifest/path que prueba las fuentes |
| `source_manifest_sha256` | nullable | hash del bundle manifest/path cuando exista |

### Definicion De Evento Y Parametros

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `event_definition_params_bundle` | yes | parametros serializados/versionados de la definicion de evento |
| `thresholds_bundle` | nullable | thresholds usados por la definicion, si existen |
| `trigger_observables_bundle` | yes | observables fuente usados por el detector/definicion |
| `definition_cutoff_policy_version` | yes | policy de cutoff usada por la definicion de evento |
| `definition_formula_contract_id` | nullable | formula contract id si la logica derivada esta gobernada por formula |
| `definition_is_parametric` | yes | true cuando thresholds/ventanas/condiciones son parametros |
| `definition_is_alphaevolve_candidate` | yes | true solo para definiciones candidatas generadas/propuestas por flujo AlphaEvolve |

### Calidad Y Consumer Gates

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `event_quality_state` | yes | `usable_candidate`, `review`, `blocked` o `raw_replay_only` |
| `event_selection_state` | yes | `candidate`, `rejected`, `review` o `blocked` |
| `event_anchor_quality_state` | yes | calidad del ancla timestamp/fecha |
| `valid_for_event_windows_candidate` | yes | puede sembrar filas de event windows |
| `valid_for_event_state_candidate` | yes | puede sembrar event state fixture/candidate despues de existir windows |
| `valid_for_pattern_discovery_candidate` | yes | permitido para discovery controlado |
| `valid_for_backtest_event_candidate` | yes | candidato solamente; no verdad de ejecucion |
| `valid_for_ml_feature_candidate` | yes | false salvo que exista construccion legal de estado pre-decision |
| `valid_for_rl_state_candidate` | yes | false en v0.1 salvo aprobacion por state builder y transition contract |
| `valid_for_alphaevolve_candidate` | yes | solo definicion/evaluacion candidata de evento; no evaluador production |
| `full_universe_claim` | yes | false salvo que contrato de denominador pruebe full scope |
| `contains_outcome_information` | yes | debe ser false |
| `contains_label_information` | yes | debe ser false |
| `contains_reward_information` | yes | debe ser false |
| `execution_truth` | yes | debe ser false |
| `requires_asof_filter` | yes | debe ser true |

### Build Lineage

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `materialization_scope` | yes | scope candidate declarado |
| `quality_policy_version` | yes | version de quality policy de la tabla de eventos |
| `schema_version` | yes | esperado `daily_strategy_candidate_events_table_v0_1` |
| `build_run_id` | yes | build run id de la tabla de eventos |
| `created_at_utc` | yes | timestamp de materializacion |
| `source_instrument_master_path` | yes | path fuente de instrument master |
| `source_instrument_master_sha256` | nullable | hash de instrument master |
| `source_market_calendar_path` | yes | path fuente de market calendar |
| `source_market_calendar_sha256` | nullable | hash de market calendar |
| `source_master_daily_table_path` | nullable | path de fuente daily cuando se use |
| `source_master_daily_table_sha256` | nullable | hash de fuente daily cuando se use |

## 6. Event Timestamp Policies Permitidas

Valores permitidos:

```text
date_level
session_open_available
session_close_available
intraday_proven
research_replay_proxy
```

Reglas:

- `date_level` significa que el evento esta anclado a sesion/fecha, no a un
  timestamp intradia preciso.
- `session_close_available` puede usar campos diarios de sesion completa solo
  despues de que la sesion este cerrada y disponible.
- `intraday_proven` requiere `event_timestamp_utc`, `detection_timestamp_utc`,
  lineage de fuente y evidencia de timestamp desde una fuente intradia/live.
- `research_replay_proxy` se permite solo para investigacion controlada y no
  debe promocionarse a produccion ni a uso directo ML/RL.

## 7. Familias De Evento En Scope Inicial

Familias compatibles con el schema inicial:

```text
daily_in_play_momentum_candidate
daily_gap_candidate
daily_first_red_day_candidate
daily_high_volume_breakout_candidate
daily_halt_context_candidate
```

Familias futuras/bloqueadas que requieren contratos de fuente antes de usarse:

```text
daily_offering_context_candidate
live_corporate_alert_candidate
float_change_candidate
borrow_or_ssr_context_candidate
```

Estos nombres son familias de evento, no prueba de causalidad ni rentabilidad.

## 8. Fallos Duros De Validacion

Los validators deben fallar si:

- falta `event_id`, `daily_event_id`, `event_definition_id` o
  `event_definition_version`;
- existe `daily_event_id` duplicado;
- existe grano duplicado sin policy explicita de duplicados;
- `event_availability_utc > as_of_utc`;
- `source_data_availability_cutoff_utc > as_of_utc`;
- `contains_outcome_information = true`;
- `contains_label_information = true`;
- `contains_reward_information = true`;
- `execution_truth = true`;
- existen campos de threshold sin `event_definition_id/version` y
  `thresholds_bundle`;
- `contains_intraday_timestamp_claim = true` mientras `event_timestamp_utc` es null;
- `event_timestamp_policy = intraday_proven` sin lineage de fuente intradia;
- `full_universe_claim = true` sin prueba de denominador/certificacion;
- `valid_for_ml_feature_candidate = true` mientras no este probada la construccion
  legal de event-state y cutoff pre-decision;
- se anade cualquier columna de outcome/label/reward fuera de las flags prohibidas.

## 9. No Objetivos

Este schema no:

- materializa la tabla de eventos;
- define la ontologia final de eventos;
- sustituye `daily_scanner_candidates_table`;
- sustituye `event_windows_table`;
- sustituye `event_state_table`;
- construye outcomes;
- aprueba entrenamiento ML/RL;
- aprueba evaluacion AlphaEvolve production;
- prueba que ninguna familia de evento sea causal, operable o rentable.

## 10. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| rol de tabla de evento daily declarado | `done` |
| grano y primary key declarados | `done` |
| columnas requeridas declaradas | `done` |
| timestamp policies declaradas | `done` |
| separacion scanner/event/event_window/event_state preservada | `done` |
| regla no outcome/label/reward inline declarada | `done` |
| validators requeridos antes de materializacion declarados | `done` |
| tabla no materializada y ML/RL/AlphaEvolve no habilitados | `done` |

Status final:

```text
daily_strategy_candidate_events_table_schema_contract_v0_1 = complete_for_contract_defined_scope
```
