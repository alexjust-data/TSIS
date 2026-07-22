# Intraday 1m Strategy Candidate Events Table Schema Contract `v0_1`

Status: `canonical_schema_target_controlled_candidate_materialized_not_official`

Dataset target:

```text
intraday_1m_strategy_candidate_events_table_v0_1
```

Physical target reserved:

```text
E:/TSIS/data/data_foundation_outputs/intraday_1m_strategy_candidate_events_table/intraday_1m_strategy_candidate_events_table_v0_1.parquet
```

## 1. Rol

`intraday_1m_strategy_candidate_events_table_v0_1` es la tabla gobernada de
anclas de eventos candidatos intradia 1m para investigacion de estrategias TSIS.

Responde:

```text
que evento candidato intradia 1m ocurrio,
para que instrumento/sesion,
en que timestamp legal de evento,
bajo que definicion de evento versionada,
con que lineage de fuente/quote-guarded.
```

No es:

- una tabla de scanner;
- una tabla de market state;
- una tabla de event state;
- una tabla de microestructura;
- una tabla de outcomes;
- una tabla de labels/rewards;
- una tabla de verdad de ejecucion/fills;
- un dataset de entrenamiento AlphaEvolve/ML/RL.

## 2. Relacion Con Tablas Cercanas

Separacion correcta:

```text
intraday_scanner_candidates_table
= donde mirar / detecciones intradia y denominador

intraday_1m_strategy_candidate_events_table
= que evento candidato 1m queda anclado y versionado

event_windows_table
= que ventanas se abren alrededor del evento

event_state_table
= fotografia legal observable anclada a evento/ventana/rol

outcomes_table
= que paso despues, unido aparte
```

La tabla de eventos puede conservar evidencia del scanner. No debe promocionar
la seleccion del scanner como verdad causal y no debe convertir spikes raw-only
en eventos candidatos canonicos si la reparacion quote-guarded los rechaza.

## 3. Grano

Grano logico:

```text
event_definition_id + event_timestamp_utc + instrument_id + event_anchor_role
```

Primary key:

```text
intraday_event_id
```

Id canonico para joins entre tablas:

```text
event_id
```

En v0.1, `intraday_event_id` puede ser igual a `event_id` si la policy de IDs
declara ese mapping. Los joins downstream deben usar `event_id`.

## 4. Componentes Fuente Permitidos

Fuentes preferidas cuando la ruta repair-aware este disponible:

```text
intraday_scanner_candidates_table_v0_2_quote_guarded_candidate
master_intraday_bar_table_v0_2_candidate_quote_guarded
master_daily_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
ohlcv_1m_quote_guarded repair manifest overlay
```

Fuentes permitidas solo como control/review:

```text
intraday_scanner_candidates_table_v0_1 raw controlled replay
master_intraday_bar_table_v0_1 scoped pilot
raw ohlcv_1m con flags explicitas raw-only/review
```

Fuentes contextuales opcionales solo cuando la definicion de evento las declare:

```text
halts_table_v0_1
news_context_table_v0_1
short_context_table_v0_1
regime_context_table_v0_1
microstructure_features_table solo para contexto post-window, no como timestamp base 1m salvo contrato separado
```

Clases de fuente bloqueadas/futuras:

```text
short_sale_constraints_table hasta que exista fuente materializada
float_context_table hasta que exista fuente/schema point-in-time
real_time_corporate_event_alerts_table hasta que exista fuente con received_utc/latencia
live broker/vendor feeds hasta que exista contrato de received_at_utc y replay
```

## 5. Columnas Requeridas

### Identidad

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `intraday_event_id` | yes | id estable y unico de la fila de evento intradia |
| `event_id` | yes | id canonico usado por event windows y event state |
| `event_table_id` | yes | esperado `intraday_1m_strategy_candidate_events_table_v0_1` |
| `event_schema_version` | yes | esperado `intraday_1m_strategy_candidate_events_table_v0_1` |
| `event_definition_id` | yes | id de definicion de evento versionada |
| `event_definition_version` | yes | version de la definicion de evento |
| `event_family` | yes | familia amplia, por ejemplo `first_motion`, `vwap_reclaim`, `frontside_acceleration` |
| `event_type` | yes | tipo concreto dentro de la familia |
| `event_subtype` | nullable | subtipo opcional |
| `event_anchor_role` | yes | rol del ancla, por ejemplo `first_observed_bar`, `trigger_bar_close`, `research_replay_anchor` |

### Instrumento Y Sesion

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `instrument_id` | yes | id temporal del instrumento |
| `ticker` | yes | ticker en mayusculas |
| `session_date` | yes | fecha de sesion del calendario de mercado |
| `event_date` | yes | fecha representada por el evento |
| `market_timezone` | yes | timezone esperada del exchange/calendario |
| `listing_exchange` | nullable | contexto de listing/exchange cuando exista |
| `is_common_stock` | yes | flag heredada de instrumento |
| `is_lt1b_operational` | yes | flag heredada de universo |
| `instrument_identity_temporal_match` | yes | true solo si la identidad del instrumento es valida en el timestamp del evento |
| `calendar_session_valid` | yes | true solo si la sesion existe en el calendario de mercado |
| `event_session_phase` | yes | `premarket`, `regular`, `afterhours` o `unknown_review` |

### Tiempo Y Disponibilidad

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `event_timestamp_utc` | yes | timestamp intradia legal del evento |
| `event_timestamp_et` | nullable | render ET solo para inspeccion humana |
| `event_bar_ts_utc` | yes | timestamp de la barra 1m usada como ancla del evento |
| `event_bar_end_utc` | yes | timestamp de cierre/fin de la barra 1m anclada |
| `event_bar_size` | yes | esperado `1m` |
| `as_of_utc` | yes | timestamp en el que la fila de evento se considera conocida para replay/uso |
| `event_availability_utc` | yes | primer timestamp en que la evidencia del evento esta disponible para TSIS |
| `detection_timestamp_utc` | yes | timestamp de deteccion del detector/scanner |
| `event_timestamp_policy` | yes | `closed_1m_bar`, `live_bar_policy` o `research_replay_proxy` |
| `decision_timestamp_policy_id` | yes | policy id del contrato de decision timestamp |
| `source_data_availability_cutoff_utc` | yes | maximo timestamp de disponibilidad de fuentes usado por esta fila |
| `uses_incomplete_bar` | yes | true solo bajo policy live explicita; default false |

### Lineage Del Candidato Fuente Y Quote-Guarded

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `source_candidate_id` | nullable | id upstream de intraday scanner/source candidate |
| `source_candidate_dataset_id` | yes | dataset id upstream |
| `source_candidate_build_run_id` | nullable | build run id de la fuente upstream |
| `source_candidate_quality_state` | nullable | estado de calidad de la fuente upstream |
| `source_scanner_definition_id` | nullable | id de definicion del scanner upstream si aplica |
| `source_scanner_definition_version` | nullable | version de definicion del scanner upstream si aplica |
| `source_scanner_run_id` | nullable | run id del scanner upstream si aplica |
| `source_price_view` | yes | esperado `ohlcv_1m_quote_guarded` para la ruta candidate canonica |
| `source_ohlcv_1m_root` | nullable | root fuente raw 1m cuando se use |
| `source_master_intraday_table_path` | nullable | path de master intraday table cuando se use |
| `source_quote_guarded_repair_manifest` | nullable | bundle path/hash del repair manifest quote-guarded |
| `source_quote_guarded_run_id` | nullable | run id quote-guarded |
| `quote_guarded_view` | yes | true si el evento se genero contra la vista quote-guarded |
| `quote_guarded_repair_applied_at_event` | yes | si se aplico reparacion en la barra del evento |
| `repair_state_at_event` | nullable | estado de reparacion en la barra del evento |
| `repair_reason_at_event` | nullable | razon de reparacion en la barra del evento |
| `raw_event_detected` | yes | la ruta raw vio el evento/threshold |
| `quote_guarded_event_confirmed` | yes | la ruta quote-guarded confirma la definicion de evento |
| `raw_only_rejected_reason` | nullable | razon por la que un evento raw-only no es seleccionable/promocionable |
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

### Evidencia Del Trigger

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `trigger_price` | nullable | precio usado por la definicion de evento si aplica |
| `trigger_move_vs_prior_close_pct` | nullable | valor continuo de movimiento en el trigger si aplica |
| `trigger_move_vs_segment_open_pct` | nullable | valor continuo de movimiento vs segment open si aplica |
| `trigger_volume_to_time` | nullable | volumen observado hasta el trigger si aplica |
| `trigger_dollar_volume_to_time` | nullable | dollar volume observado hasta el trigger si aplica |
| `bars_observed_to_event` | nullable | barras 1m observadas hasta el evento |
| `trigger_source_bar_file` | nullable | file/path fuente de la barra de evento si existe |

Estos campos de trigger son evidencia para una definicion de evento versionada.
No son verdad base de estado y no sustituyen observables `intraday__*` en
market/event state.

### Calidad Y Consumer Gates

| Columna | Requerida | Semantica |
| --- | --- | --- |
| `event_quality_state` | yes | `usable_candidate`, `review`, `blocked` o `raw_replay_only` |
| `event_selection_state` | yes | `candidate`, `rejected`, `review` o `blocked` |
| `event_anchor_quality_state` | yes | calidad del ancla timestamp intradia |
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
| `schema_version` | yes | esperado `intraday_1m_strategy_candidate_events_table_v0_1` |
| `build_run_id` | yes | build run id de la tabla de eventos |
| `created_at_utc` | yes | timestamp de materializacion |
| `source_instrument_master_path` | yes | path fuente de instrument master |
| `source_instrument_master_sha256` | nullable | hash de instrument master |
| `source_market_calendar_path` | yes | path fuente de market calendar |
| `source_market_calendar_sha256` | nullable | hash de market calendar |
| `source_master_daily_table_path` | nullable | path de fuente daily cuando se use como contexto |
| `source_master_daily_table_sha256` | nullable | hash de fuente daily cuando se use |

## 6. Event Timestamp Policies Permitidas

Valores permitidos:

```text
closed_1m_bar
live_bar_policy
research_replay_proxy
```

Reglas:

- `closed_1m_bar` es el default y requiere que la barra del evento este cerrada
  en o antes de `as_of_utc`.
- `live_bar_policy` queda bloqueada hasta que exista una policy live explicita de
  decision-time y contrato de disponibilidad de live feed.
- `research_replay_proxy` se permite solo para investigacion controlada y no
  debe promocionarse a produccion ni a uso directo ML/RL.

## 7. Familias De Evento En Scope Inicial

Familias compatibles con el schema inicial:

```text
intraday_first_motion_threshold_cross_candidate
intraday_vwap_reclaim_candidate
intraday_frontside_acceleration_candidate
intraday_failed_breakout_candidate
intraday_halt_resume_continuation_candidate
```

Familias futuras/bloqueadas que requieren contratos de fuente antes de usarse:

```text
intraday_offering_dump_candidate
live_news_alert_reaction_candidate
borrow_or_ssr_reaction_candidate
microstructure_seconds_event_candidate
```

Estos nombres son familias de evento, no prueba de causalidad ni rentabilidad.

## 8. Regla De Promocion Quote-Guarded

La promocion canonica candidate requiere:

```text
quote_guarded_view = true
quote_guarded_event_confirmed = true
source_quote_guarded_repair_manifest is not null
```

Los eventos raw-only pueden conservarse como evidencia con:

```text
raw_event_detected = true
quote_guarded_event_confirmed = false
event_selection_state = rejected
raw_only_rejected_reason = rejected_raw_spike_not_confirmed_by_quotes
```

Las filas raw-only/replay no deben marcar:

```text
valid_for_ml_feature_candidate = true
valid_for_rl_state_candidate = true
valid_for_alphaevolve_candidate = true
```

## 9. Fallos Duros De Validacion

Los validators deben fallar si:

- falta `event_id`, `intraday_event_id`, `event_definition_id` o
  `event_definition_version`;
- existe `intraday_event_id` duplicado;
- existe grano duplicado sin policy explicita de duplicados;
- falta `event_timestamp_utc`, `event_bar_ts_utc` o `event_bar_end_utc`;
- `event_bar_end_utc > as_of_utc` bajo policy `closed_1m_bar`;
- `event_availability_utc > as_of_utc`;
- `source_data_availability_cutoff_utc > as_of_utc`;
- `uses_incomplete_bar = true` sin contrato de live policy;
- `contains_outcome_information = true`;
- `contains_label_information = true`;
- `contains_reward_information = true`;
- `execution_truth = true`;
- existen campos de threshold sin `event_definition_id/version` y
  `thresholds_bundle`;
- un evento raw-only aparece marcado como seleccionable/promocionable;
- `source_price_view` afirma `ohlcv_1m_quote_guarded` sin lineage de repair
  manifest;
- `full_universe_claim = true` sin prueba de denominador/certificacion;
- `valid_for_ml_feature_candidate = true` mientras no este probada la construccion
  legal de event-state y cutoff pre-decision;
- se anade cualquier columna de outcome/label/reward fuera de las flags prohibidas.

## 10. No Objetivos

Este schema no:

- materializa la tabla de eventos;
- define la ontologia final de eventos;
- sustituye `intraday_scanner_candidates_table`;
- sustituye `event_windows_table`;
- sustituye `event_state_table`;
- calcula microestructura;
- construye outcomes;
- aprueba entrenamiento ML/RL;
- aprueba evaluacion AlphaEvolve production;
- prueba que ninguna familia de evento sea causal, operable o rentable.

## 11. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| rol de tabla de evento intradia 1m declarado | `done` |
| grano y primary key declarados | `done` |
| columnas requeridas declaradas | `done` |
| timestamp policies declaradas | `done` |
| regla de promocion quote-guarded declarada | `done` |
| separacion scanner/event/event_window/event_state preservada | `done` |
| regla no outcome/label/reward inline declarada | `done` |
| validators requeridos antes de materializacion declarados | `done` |
| tabla no materializada y ML/RL/AlphaEvolve no habilitados | `done` |

Status final:

```text
intraday_1m_strategy_candidate_events_table_schema_contract_v0_1 = complete_for_contract_defined_scope
```

## Evidencia Controlada 2026-07-05

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
source = E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/intraday_1m_strategy_candidate_events_table_v0_1_candidate/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_from_master_intraday_qg_manifest.json
source_session_count = 58
event_candidate_rows = 5
validator_status = passed
status = controlled_candidate_not_promoted
```

Esta evidencia demuestra que el schema puede materializar un candidato controlado desde la ruta quote-guarded. No cambia el target oficial E-root declarado y no habilita consumo full-universe, ML, RL ni AlphaEvolve.
