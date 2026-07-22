# State RAW To Consumption Lineage - Intraday 1m Outcomes Controlled v0.1

## Estado

Tipo: lineage especifico ligado a `state_raw_to_consumption_lineage_contract_v0_1.md`.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - MARKET STATE / INTRADIA 1M OUTCOMES SEPARADOS`.
Fecha: 2026-07-05.

Status:

```text
state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1 = complete_for_controlled_scope
outcomes_dataset = outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
source_event_state_rows = 15
post_event_window_rows = 5
outcome_rows = 5
source_event_count = 5
full_universe_claim = false
ml_label_dataset_enabled = false
rl_reward_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

## 1. Proposito

Este documento cierra la trazabilidad controlada desde RAW 1m hasta outcomes
post-evento intradia separados para la ruta quote-guarded.

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
-> outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
```

La tabla de outcomes es `y`. No es estado, no es feature table, no es reward
table y no es execution truth.

No cubre todavia:

```text
wider/full-universe intraday outcomes;
daily/1m unified outcomes;
labels gobernados para ML;
reward contract para RL;
slippage/fills/execution outcomes;
evaluadores bloqueados;
AlphaEvolve/ML/RL.
```

## 2. Fuentes Controladas

Event state intradia:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
```

Event state manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
```

Event windows intradia:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
```

Event windows manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
```

Master intraday quote-guarded:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
```

Master intraday manifest:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json
```

## 3. Builder

Builder:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_event_outcomes_candidate.py
```

Test:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_event_outcomes_candidate_builder.py
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled/outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled/_outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_manifest.json
```

## 4. Evidencia

```text
source_event_state_rows = 15
source_event_window_rows = 15
post_event_window_rows = 5
reference_anchor_event_state_rows = 5
outcome_rows = 5
event_count = 5
ticker_count = 2
outcome_horizon = post_event_30m_intraday_1m
price_view = 1m_quote_guarded_raw
quality_counts = good_intraday_1m_outcome: 3, review_intraday_missing_bars: 2
good_intraday_1m_outcome_rows = 3
review_intraday_missing_bars_rows = 2
valid_for_outcome_research_rows = 5
valid_for_backtest_outcome_candidate_rows = 3
valid_for_ml_label_candidate_rows = 0
valid_for_rl_reward_candidate_rows = 0
bars_expected_total = 150
bars_observed_total = 134
quote_guarded_repair_applied_rows_total = 9
full_universe_claim_rows = 0
execution_truth_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

## 5. Regla De Referencia Y Ventana

Precio de referencia:

```text
reference_price = event_state at_event intraday__last_closed_bar_close
```

Ventana de outcome:

```text
window_role = post_event_30m
outcome_horizon = post_event_30m_intraday_1m
bars = master_intraday quote-guarded rows with window_start_utc <= ts_utc < window_end_utc
```

Lectura correcta:

```text
at_event cierra el precio legal de referencia.
post_event_30m mide lo que paso despues.
El outcome se une despues por event_window_id/outcome_join_key, nunca inline en event_state.
```

## 6. Campos De Outcome

El builder materializa outcomes continuos:

```text
reference_to_outcome_open_return_pct
reference_to_outcome_high_return_pct
reference_to_outcome_low_return_pct
reference_to_outcome_close_return_pct
mfe_pct
mae_pct
outcome_open_to_close_return_pct
outcome_range_pct
bars_expected
bars_observed
bars_missing
```

No materializa labels ni rewards:

```text
label_columns_materialized = false
reward_columns_materialized = false
valid_for_ml_label_candidate = false
valid_for_rl_reward_candidate = false
```

Si mas adelante se necesitan labels o rewards, deben nacer en contratos
separados:

```text
label contract -> ML labels gobernados
reward contract -> RL rewards gobernados
evaluation contract -> AlphaEvolve fitness
```

## 7. Prohibiciones

```text
No usar outcomes como feature pre-evento.
No copiar MFE/MAE/returns dentro de market_state/event_state.
No activar ML labels sin label contract.
No activar RL rewards sin reward/action contract.
No interpretar como fill, slippage, execution truth o PnL.
No interpretar como full-universe.
```

Valores obligatorios:

```text
contains_post_event_information = true
prohibited_as_pre_event_feature = true
requires_feature_label_separation = true
full_universe_claim = false
execution_truth = false
```

## 8. Consumo Permitido Hoy

| Uso | Estado hoy | Regla |
| --- | --- | --- |
| outcome research controlado | permitido | usar solo como `y` separado |
| pattern discovery controlado | permitido | unir despues, nunca inline en X |
| backtest outcome candidate | permitido solo en filas `good_intraday_1m_outcome` | no es ejecucion ni slippage |
| ML labels | bloqueado | requiere label contract y gates propios |
| RL rewards | bloqueado | requiere action/reward contract |
| AlphaEvolve evaluators | pendiente | requiere evaluator contract bloqueado |
| oficial/full-universe | bloqueado | requiere scope amplio, validators y review |

## 9. Siguiente Paso

```text
outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
-> evaluadores bloqueados
-> labels/rewards solo si hay contratos especificos
-> semantic representations / AlphaEvolve despues
```
