# State RAW To Consumption Lineage - Intraday 1m Event State Controlled v0.1

## Estado

Tipo: lineage especifico ligado a `state_raw_to_consumption_lineage_contract_v0_1.md`.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - MARKET STATE / INTRADIA 1M EVENT STATE CONTROLADO`.
Fecha: 2026-07-05.

Status:

```text
state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1 = complete_for_controlled_scope
event_state_dataset = event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
source_event_window_rows = 15
event_state_rows = 15
source_event_count = 5
full_universe_claim = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

## 1. Proposito

Este documento cierra la trazabilidad controlada desde RAW 1m hasta
`event_state_table_v0_1_candidate` para la ruta intradia quote-guarded.

Cadena cubierta:

```text
E:/TSIS/data/ohlcv_1m
+ D:/quotes provisional lineage
-> repair_manifest_lt1b_v0_1.parquet
-> master_intraday_bar_table_v0_2_candidate_quote_guarded scoped E-root
-> market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
-> intraday_1m_strategy_candidate_events_table_v0_1_candidate
-> event_windows_table_v0_1_candidate_intraday_1m_strategy_events
-> event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
```

No cubre todavia:

```text
wider/full-universe intraday event_state;
multi-componente completo con microestructura/fundamentals/news/short/regime;
outcomes separados;
evaluadores bloqueados;
transition datasets;
ML/RL/AlphaEvolve.
```

## 2. Fuentes Controladas

Market state intradia:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
```

Market state manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
```

Event windows intradia:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
```

Event windows manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
```

## 3. Builder

Builder:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
```

Test:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_intraday_quote_guarded_candidate_builder.py
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
```

## 4. Evidencia

```text
source_event_window_rows = 15
joined_event_state_rows = 15
missing_market_state_window_rows = 0
event_count = 5
event_window_count = 15
market_state_count = 15
ticker_count = 2
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
state_quality_counts = event_state_review_scoped_intraday_component: 15
valid_for_pattern_discovery_rows = 15
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
valid_for_rl_training_direct_rows = 0
execution_truth_rows = 0
full_universe_claim_rows = 0
contains_future_information_without_event_filter_rows = 5
validator_status = passed
validator_hard_fail_count = 0
```

## 5. Regla De Join Temporal

El builder no exige coincidencia exacta para todos los roles. Usa:

```text
market_state seleccionado = ultimo market_state del ticker con decision_timestamp_utc <= decision timestamp de la ventana
```

Decision timestamp por rol:

| State role | Ventana fuente | Decision timestamp usado |
| --- | --- | --- |
| `pre_event` | `pre_event_30m` | `window_end_utc` = `event_timestamp_utc` |
| `at_event` | `event_anchor_1m` | `event_anchor_decision_timestamp_utc` |
| `post_event_review` | `post_event_30m` | `window_end_utc` |

Lectura correcta:

```text
pre_event y at_event son X legal bajo cutoff.
post_event_review contiene informacion posterior y no puede alimentar X pre-decision.
```

## 6. Prohibiciones

```text
No outcome__*
No label__*
No reward__*
No action__*
No policy__*
No fill__*
No pnl__*
No future__*
No strategy__*
No signal__*
```

Valores obligatorios:

```text
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
valid_for_ml_feature_candidate = false
valid_for_rl_state_candidate = false
valid_for_rl_training_direct = false
execution_truth = false
full_universe_claim = false
```

## 7. Consumo Permitido Hoy

| Uso | Estado hoy | Regla |
| --- | --- | --- |
| pattern discovery controlado | permitido | no usar como full-universe ni ML-ready |
| outcome separado posterior | siguiente paso | unir por `outcome_join_key`/`event_window_id`, no inline |
| evaluadores bloqueados | pendiente | requiere outcomes separados y fitness contract |
| ML/RL/AlphaEvolve | bloqueado | requiere promotion gates, outcomes/evaluadores y datasets especificos |
| oficial/full-universe | bloqueado | requiere scope amplio, validators y review |

## 8. Siguiente Paso

```text
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
-> outcomes separados
-> evaluadores bloqueados
-> semantic representations / AlphaEvolve despues
```
