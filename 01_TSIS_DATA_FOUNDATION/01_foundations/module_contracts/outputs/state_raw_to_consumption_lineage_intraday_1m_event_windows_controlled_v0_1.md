# State RAW To Consumption Lineage - Intraday 1m Event Windows Controlled v0.1

## Estado

Tipo: lineage especifico ligado a `state_raw_to_consumption_lineage_contract_v0_1.md`.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - MARKET STATE / INTRADIA 1M EVENT WINDOWS CONTROLADAS`.
Fecha: 2026-07-05.

Status:

```text
state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1 = complete_for_controlled_scope
source_intraday_event_candidate_table = intraday_1m_strategy_candidate_events_table_v0_1_candidate
event_windows_candidate = event_windows_table_v0_1_candidate_intraday_1m_strategy_events
source_event_count = 5
event_window_rows = 15
full_universe_claim = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

## 1. Proposito

Este documento traza la ruta controlada desde el 1m quote-guarded hasta ventanas
intradias alrededor de eventos candidatos. No define outcomes y no promociona
ninguna tabla oficial.

Cadena cubierta:

```text
E:/TSIS/data/ohlcv_1m
+ D:/quotes provisional lineage
-> repair_manifest_lt1b_v0_1.parquet
-> master_intraday_bar_table_v0_2_candidate_quote_guarded scoped E-root
-> intraday_1m_strategy_candidate_events_table_v0_1_candidate
-> event_windows_table_v0_1_candidate_intraday_1m_strategy_events
```

No cubre todavia:

```text
wider/full-universe intraday event windows;
event_state_table_v0_1 candidate;
outcomes;
transition datasets;
ML/RL/AlphaEvolve.
```

## 2. Fuente De Eventos

Eventos fuente:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/intraday_1m_strategy_candidate_events_table_v0_1_candidate/data.parquet
```

Manifest fuente:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/_intraday_1m_strategy_candidate_events_table_v0_1_manifest_candidate.json
```

Evidencia de la fuente:

```text
source_session_count = 58
event_candidate_rows = 5
event_definition_id = intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1
validator_status = passed
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
alphaevolve_production_enabled_rows = 0
```

Lectura correcta:

```text
el +50% vive como definicion de evento versionada;
no es estado base;
no es threshold privilegiado para AlphaEvolve;
no contiene outcome.
```

## 3. Builder De Ventanas

Builder:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_event_windows_candidate.py
```

Test:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_strategy_event_windows_candidate_builder.py
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
```

## 4. Ventanas Materializadas

Roles generados por evento:

| Window role | Inicio | Fin | Uso permitido |
| --- | --- | --- | --- |
| `pre_event_30m` | `event_timestamp_utc - 30m` | `event_timestamp_utc` | contexto pre-evento, `leakage_safe_as_pre_event_feature=true` |
| `event_anchor_1m` | `event_timestamp_utc` | `event_bar_end_utc` | ancla/decision del evento; no feature pre-evento |
| `post_event_30m` | `event_bar_end_utc` | `event_bar_end_utc + 30m` | ventana candidata de outcome; no feature pre-evento |

Evidencia:

```text
source_event_count = 5
row_count = 15
window_role_counts = event_anchor_1m: 5, post_event_30m: 5, pre_event_30m: 5
validator_status = passed
validator_hard_fail_count = 0
full_universe_claim_rows = 0
ml_feature_candidate_rows = 5
outcome_window_candidate_rows = 5
microstructure_feature_candidate_rows = 15
rl_state_component_candidate_rows = 0
```

## 5. Reglas De Leakage

```text
pre_event_30m puede alimentar features pre-evento porque termina en event_timestamp_utc.
event_anchor_1m puede alimentar event_state/ancla, pero no ML feature pre-evento.
post_event_30m puede alimentar outcomes separados, pero no X.
```

Regla central:

```text
X = estado/event_state bajo cutoff legal
y = outcomes separados despues
```

## 6. Consumo Permitido Hoy

| Uso | Estado hoy | Regla |
| --- | --- | --- |
| `event_state` fixture controlado | siguiente paso | usar estas ventanas con state builder y leakage gates |
| microestructura por ventanas | permitido como candidate controlado | respetar `window_role` y no usar post-event como feature pre-decision |
| outcomes separados | siguiente paso posterior | usar `post_event_30m` como frontera, no como valor de outcome |
| ML/RL/AlphaEvolve | bloqueado | requiere event_state, outcomes y evaluadores bloqueados |
| promocion oficial/full-universe | bloqueado | requiere wider scope, validators y review |

## 7. No Es

```text
No es event_windows_table_v0_1 oficial.
No es full-universe.
No es event_state_table.
No contiene outcomes.
No habilita ML/RL/AlphaEvolve.
No convierte el +50% en estado base.
```

## 8. Siguiente Paso

```text
event_windows_table_v0_1_candidate_intraday_1m_strategy_events
-> controlled event_state fixture DONE
-> outcomes separados NEXT
-> evaluadores bloqueados
```

## 9. Actualizacion 2026-07-05 - Event State Intradia Controlado

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled = passed
rows = 15
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
```

Lectura correcta: el siguiente paso de esta cadena ya no es `event_state`; ahora son outcomes separados y evaluadores.
