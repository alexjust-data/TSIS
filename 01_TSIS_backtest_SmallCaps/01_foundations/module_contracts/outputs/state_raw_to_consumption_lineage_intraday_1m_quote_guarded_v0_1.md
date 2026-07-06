# State RAW To Consumption Lineage - Intradia 1m Quote-Guarded v0.1

## Estado

Tipo: lineage especifico ligado a `state_raw_to_consumption_lineage_contract_v0_1.md`.  
Modulo: `01_TSIS_backtest_SmallCaps`.  
Ambito: `CAPA 1 - MARKET STATE / INTRADIA 1M QUOTE-GUARDED`.  
Fecha: 2026-07-05.  

Status:

```text
state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1 = complete_through_controlled_intraday_event_candidate_scope
scope = lt1b_quote_guarded_repair_manifest_overlay
raw_ohlcv_1m_root = E:/TSIS/data/ohlcv_1m
quote_guarded_manifest_gate = passed
master_intraday_bar_table_v0_2_candidate_materialized = scoped_e_root_candidate_not_official
lightweight_preflight_status = passed
controlled_sample_materialization_status = passed_not_official
scoped_candidate_materialization_status = passed_not_official
e_root_scoped_candidate_materialization_status = passed_not_official
market_state_intraday_controlled_materialization_status = passed_not_official
intraday_scanner_candidates_table_v0_2_materialized = false
event_candidate_tables_intraday_1m_materialized = controlled_candidate_not_official
full_universe_claim = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

## 1. Proposito

Este documento traza la ruta intradia 1m quote-guarded desde el RAW 1m y el
manifest de reparacion LT1B hasta su consumo futuro por builders de estado.

Cadena cubierta:

```text
E:/TSIS/data/ohlcv_1m                         # RAW 1m inmutable
+ D:/quotes                                   # quotes provisional lineage root
-> build_ohlcv_1m_quote_guarded_repairs_v0_2.py
-> repair shards por ticker/mes
-> consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.py
-> E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
-> futura vista ohlcv_1m_quote_guarded
-> master_intraday_bar_table_v0_2_candidate_quote_guarded scoped E-root candidate
-> market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
-> adapter source candidates por ticker/session
-> intraday_1m_strategy_candidate_events_table_v0_1_candidate controlada
-> intraday__* y event__* para consumo controlado posterior
```

No cubre todavia:

```text
materializacion wider/full-scope de master_intraday_bar_table_v0_2_candidate_quote_guarded;
intraday_scanner_candidates_table_v0_2_quote_guarded_candidate materializada;
materializacion wider/full-universe de intraday_1m_strategy_candidate_events_table_v0_1;
materializacion wider/full-universe de event_windows 1m no-halt;
microestructura quotes/trades por ventanas;
outcomes;
ML/RL/AlphaEvolve.
```

## 2. Lectura Correcta

La reparacion 1m no convierte el raw 1m en una tabla corregida completa. El raw
sigue siendo inmutable y la vista defensible se obtiene aplicando un overlay.

Modelo correcto:

```text
raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet = vista ohlcv_1m_quote_guarded
```

Por tanto:

```text
repair manifest PASS = gate upstream cerrado
master_intraday_bar_table_v0_2_candidate = scoped E-root candidate materializada, no oficial/full-universe
scanner intradia quote-guarded v0_2 = todavia no materializado
eventos intradia 1m = materializados en scope controlado/no oficial; wider/full-universe pendiente
```

Este lineage permite disenar y ejecutar el builder/preflight intradia 1m sin
volver a discutir de donde sale la data. No permite tratar 1m como input oficial
ML/RL/AlphaEvolve hasta que existan candidate outputs con manifests, validators y
review.

## 3. Tramo 0 - Fuentes Base

| Componente | Path | Estado de lineage | Rol |
| --- | --- | --- | --- |
| `ohlcv_1m` RAW | `E:/TSIS/data/ohlcv_1m` | `raw_authority` | barras 1m originales; no se corrigen in place |
| quotes root provisional | `D:/quotes` | `provisional_lineage` | envelope de quotes usado por el repair mientras E-root parity queda pendiente |
| universo LT1B | `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet` | `support_only` | universo de tickers LT1B usado por la consolidacion |
| repair run root | `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838` | `lineage_only` | run broad original de repair shards |
| consolidation run root | `C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_lt1b_consolidation_manual_20260703_094500` | `lineage_only` | consolidacion manual promovida LT1B |
| output quote-guarded root | `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded` | `derived_authority_declared_scope` | artifacts promovidos del overlay LT1B |

Regla fisica:

```text
E:/TSIS/data/ohlcv_1m no se sobrescribe.
El overlay vive separado en E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded.
```

## 4. Tramo 1 - Repair Quote-Guarded

Builder/repair principal:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/minute/build_ohlcv_1m_quote_guarded_repairs_v0_2.py
```

Wrappers y supervision relacionados:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/run_ohlcv_1m_quote_guarded_repair_v0_2.ps1
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

Operacion conceptual:

```text
1. lee parquets mensuales desde E:/TSIS/data/ohlcv_1m;
2. lee quotes desde D:/quotes;
3. compara OHLC/VWAP contra envelope de quotes;
4. escribe repair shards solo para minutos afectados;
5. preserva source_ohlcv_path y source_quotes_path;
6. no modifica el raw 1m.
```

Campos esperados del overlay:

```text
ticker
ts_utc
minute_utc
minute_ny
session_date
year
month
repair_state
repair_reason
quote_guarded_repair_applied
o_raw / h_raw / l_raw / c_raw
o_qg / h_qg / l_qg / c_qg
vw
v
n
vw_quote_guarded_status
quote_bid_floor
quote_bid_p50
quote_ask_p50
quote_ask_cap
quote_mid_p50
quote_spread_p50
quote_spread_pct_p50
quote_count
quote_guard_config
source_ohlcv_path
source_quotes_path
manifest_created_at_utc
run_root
```

## 5. Tramo 2 - Consolidacion LT1B Promovida

Consolidator:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/minute/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.py
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1
```

Artifacts promovidos:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_sample.csv
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_lt1b_consolidation_manual_20260703_094500/consolidation_summary.json
```

Resumen verificado del summary JSON:

```text
status = PASS
created_at_utc = 2026-07-03T16:13:47.256010+00:00
universe_dataset = lt1b_universe_v0_1
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
selected_repair_shards = 421533
skipped_out_scope_shards = 19510
skipped_incomplete_lt1b_shards = 0
malformed_shard_names = 0
manifest_rows = 301278342
written_shards = 421533
promoted_manifest = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
```

Interpretacion:

```text
PASS = el manifest LT1B promovido existe y puede alimentar preflight/builders candidate.
PASS != master_intraday_bar_table_v0_2 materializada.
PASS != scanner intradia v0_2 materializado.
PASS != dataset ML/RL/AlphaEvolve.
```

## 6. Tramo 3 - Vista 1m Quote-Guarded

La vista no es un nuevo raw completo. Es una lectura controlada:

```text
para cada ticker/session/rango:
  cargar barras desde E:/TSIS/data/ohlcv_1m;
  buscar rows correspondientes en repair_manifest_lt1b_v0_1.parquet;
  reemplazar OHLC por o_qg/h_qg/l_qg/c_qg donde aplique;
  conservar VWAP como observado y bloquearlo si vw_quote_guarded_status lo exige;
  emitir flags de repair/quality/lineage;
  no escribir sobre raw.
```

Campos minimos que debe arrastrar cualquier consumer 1m:

```text
quote_guarded_view
quote_guarded_repair_applied
repair_state
repair_reason
vw_quote_guarded_status
source_quote_guarded_repair_manifest
source_quote_guarded_run_id
source_quotes_root
source_quotes_root_state
requires_rebuild_after_e_quotes_parity
requires_rebuild_after_quote_guarded_e_promotion
```

Regla de VWAP:

```text
No reconstruir VWAP desde quotes.
Si VWAP queda invalido por el manifest, preservar estado invalido y bloquear consumo directo.
```

## 7. Tramo 4 - Futura Master Intraday Candidate

Contrato downstream:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
```

Config candidate:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
```

Target reservado:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/
```

Estado actual:

```text
dataset_id = master_intraday_bar_table_v0_2_candidate_quote_guarded
promotion_state = candidate_contract_defined_not_materialized
quote_guarded_manifest_gate = passed
next_executable_action = implement/execute builder preflight against repair_manifest_lt1b_v0_1.parquet
```

Lectura correcta:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
= futura superficie gobernada 1m para intraday__*
!= tabla materializada hoy
!= market_state_table
!= event_state_table
```

## 7.1 Preflight Ligero Ejecutado

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/preflight_master_intraday_quote_guarded_candidate.py
```

Reporte:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_preflight_v0_1/master_intraday_quote_guarded_candidate_preflight_v0_1.json
```

Resultado:

```text
validator_status = passed
validator_hard_fail_count = 0
validator_warning_count = 0
path_checks = all true
repair_sample_required_columns_missing = []
repair_sample_column_count = 36
manifest_rows = 301278342
completed_tickers = 4824
missing_tickers = 0
```

Lectura correcta:

```text
El preflight confirma que config, paths, summary, sample y lineage upstream
son coherentes para el siguiente builder candidate.
No lee el parquet completo de 27GB.
No materializa master_intraday_bar_table_v0_2.
No habilita scanner/eventos 1m ni ML/RL/AlphaEvolve.
```

## 7.2 Materializacion Controlada De Muestra

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_sample.py
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_sample_v0_1/_master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample_manifest.json
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_sample_v0_1/master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample/data.parquet
```

Resultado:

```text
status = controlled_sample_materialized_not_official
source_sample_rows = 30
source_raw_file_count = 7
raw_rows_found = 30
raw_rows_missing = 0
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_source_rows = 20
qg_ohlc_changed_source_rows = 20
output_rows = 60
price_view_counts = 1m_raw:30, 1m_quote_guarded_raw:30
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
Esta muestra prueba que podemos leer raw rows referenciadas por el sample del
repair manifest y construir dos price views controladas: 1m_raw y
1m_quote_guarded_raw.
No escribe en el target E-root de master_intraday_bar_table.
No es full-universe.
No habilita scanner/eventos 1m ni ML/RL/AlphaEvolve.
```

## 7.3 Materializacion Scoped Candidate

Script:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_scoped_v0_1/_master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped_manifest.json
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_scoped_v0_1/master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped/data.parquet
```

Scope:

```text
AACT:2025-09
AAGR:2023-12
AAMC:2023-12
```

Resultado:

```text
status = scoped_candidate_materialized_not_official
raw_rows = 10835
repair_manifest_rows_in_scope = 1106
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
output_rows = 21670
price_view_counts = 1m_raw:10835, 1m_quote_guarded_raw:10835
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
Esta materializacion ya no depende del CSV sample como fuente de datos de
precio. Lee raw mensual completo y repair shard completo para cada ticker/mes
del scope. Sigue siendo candidate scoped bajo tests/test_runs, no E-root
official, no full-universe, no ML/RL/AlphaEvolve.
```

Regla confirmada:

```text
OHLC quote-guarded efectivo solo se aplica cuando
quote_guarded_repair_applied = true.
manifest_qg_diff_not_applied_rows = lineage/anomalia conservadora, no precio aplicado.
```

## 7.4 E-root Scoped Candidate

Manifest E-root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json
```

Output E-root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
```

Resultado:

```text
status = scoped_candidate_materialized_not_official
writes_e_root_target = true
official_dataset_created = false
full_universe_claim = false
raw_rows = 10835
repair_manifest_rows_in_scope = 1106
raw_ohlc_mismatch_rows = 0
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
output_rows = 21670
validator_status = passed
```

Lectura correcta:

```text
Esta es la primera candidate acotada escrita en E-root para
master_intraday_bar_table_v0_2_candidate_quote_guarded.
No es oficial/promoted.
No es full-universe.
No habilita scanner/eventos 1m ni ML/RL/AlphaEvolve.
```

## 7.5 Consumo Controlado Por Market State Intradia

Controlled market_state intradia 1m quote-guarded materializado:

```text
script = scripts/materialize_market_state_intraday_quote_guarded_candidate.py
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
output = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
status = controlled_candidate_not_promoted
source_quote_guarded_intraday_rows = 10835
state_rows = 10835
ticker_count = 3
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
full_universe_claim_rows = 0
ml_candidate_rows = 0
rl_candidate_rows = 0
execution_truth_rows = 0
intraday_as_of_after_decision_rows = 0
bar_end_decision_timestamp_mismatch_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta: este fixture prueba consumo `intraday__*` desde el E-root scoped candidate quote-guarded hacia `market_state_table_v0_1_candidate`. No es tabla oficial, no es full-universe, no tiene evento, no contiene outcomes y no habilita ML/RL/AlphaEvolve.

Regla de timestamp usada:

```text
decision_timestamp_utc = ts_utc + 1 minuto
intraday__bar_end_utc = decision_timestamp_utc
intraday_as_of_utc <= decision_timestamp_utc
```

Esto representa la ultima vela 1m cerrada. No permite usar vela incompleta ni datos posteriores al cierre de la vela.

## 8. Consumo Futuro Por Estado

Cuando la candidate intradia exista, podra alimentar familias `intraday__*` del
state builder.

Ejemplos de consumo permitido solo tras builder/gates:

```text
intraday__last_closed_bar_ohlcv
intraday__session_so_far_price
intraday__session_so_far_volume
intraday__returns_continuous
intraday__coverage_state
intraday__quote_guarded_state
intraday__quality_state
intraday__source_manifest
```

Estas familias no son thresholds de estrategia. Son observables o estados de
calidad/lineage bajo cutoff legal.

No deben entrar como estado base:

```text
first_cross_50_ts_utc como verdad privilegiada
selected_intraday_in_play_candidate como feature causal
threshold ganador descubierto
winner/loser
outcome futuro
reward
PnL
fill real posterior
```

## 9. Relacion Con Scanner Intradia

Scanner raw previo:

```text
dataset_id = intraday_scanner_candidates_table_v0_1
source_price_view = raw ohlcv_1m
status = controlled_replay_candidate_not_official
```

Sucesor requerido:

```text
dataset_id = intraday_scanner_candidates_table_v0_2_quote_guarded_candidate
source_price_view = ohlcv_1m_quote_guarded
storage_model = raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay
status = not_materialized
```

El scanner intradia v0_2 debe comparar raw vs quote-guarded y rechazar spikes raw
no confirmados por quotes cuando aplique. Pero ese scanner seguira siendo
detector/candidato, no tabla de estado base.

## 10. Cutoff / As-Of

Para consumo de estado intradia:

```text
decision_timestamp_utc = t
solo pueden usarse barras 1m cerradas <= t
si se permite barra incompleta, debe existir policy explicita
repair overlay solo puede aplicarse a minutos <= t
quotes usadas por el overlay deben pertenecer a la ventana/minuto declarado
lineage/quality flags deben viajar con la fila
```

Regla de causalidad:

```text
1m quote-guarded corrige observabilidad de precio.
No demuestra causalidad de eventos.
No convierte un scanner en feature causal.
No permite outcomes dentro de X.
```

## 11. Consumo Permitido Hoy

| Uso | Estado hoy | Regla |
| --- | --- | --- |
| diseno de builder/preflight | permitido | usar manifest LT1B promovido |
| materializacion candidate `master_intraday_bar_table_v0_2` | siguiente paso | requiere builder, validators, manifest y review |
| scanner intradia v0_2 quote-guarded | pendiente | la materializacion controlada actual usa adapter directo desde master_intraday; el scanner completo sigue pendiente |
| event candidates intradia 1m quote-guarded | DONE controlled | 5 eventos desde 58 sesiones; no oficial/full-universe |
| market_state/event_state fixture con 1m | DONE controlled | market_state intradia DONE; event_windows intradia DONE; event_state intradia DONE; outcomes separados NEXT |
| ML/RL/AlphaEvolve | bloqueado | requiere state/event_state + outcomes + evaluadores separados |

## 12. Gaps Abiertos

```text
1. preflight ligero, muestra controlada, scoped candidate y E-root scoped candidate ejecutados y passed; falta decidir scope wider/declared-universe;
2. existe parquet/manifest candidate de master_intraday_bar_table_v0_2 en target E-root para scope acotado;
3. falta scanner intradia v0_2 quote-guarded materializado;
4. intraday_1m_strategy_candidate_events_table_v0_1 sobre fuente quote-guarded = DONE controlled, falta wider/full-universe;
5. event_windows intradia 1m = DONE controlled, falta wider/full-universe;
6. D:/quotes sigue como lineage provisional hasta E-root parity/rebuild;
7. falta decidir si el primer fixture de state sera daily-only o incluira 1m tras este builder;
8. falta validators de parity RAW -> overlay -> state consumer.
```

## 13. Regla Final

```text
1m reparado desbloquea la ruta intradia defensible.
No promociona automaticamente ninguna tabla downstream.
```

Para usar 1m en `market_state/event_state`, la ruta minima es:

```text
repair_manifest_lt1b_v0_1 PASS
-> preflight ligero passed
-> materializacion controlada de muestra passed
-> scoped candidate passed
-> E-root scoped candidate passed
-> E-root scoped master_intraday_bar_table_v0_2_candidate_quote_guarded DONE controlled
-> market_state intradia controlado DONE
-> intraday_1m_strategy_candidate_events_table_v0_1 DONE controlled
-> event_windows intradia 1m DONE controlled
-> event_state candidate DONE controlled
-> outcomes separados NEXT
-> wider/declared-universe solo despues de validators/review
```

## 7.6 Consumo Controlado Por Intraday 1m Strategy Candidate Events

Controlled intraday 1m strategy candidate events quote-guarded materializado:

```text
script = scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
source = E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/
source_candidates = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_source_candidates.parquet
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/intraday_1m_strategy_candidate_events_table_v0_1_candidate/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_from_master_intraday_qg_manifest.json
status = controlled_candidate_not_promoted
source_quote_guarded_bar_rows = 10835
source_session_count = 58
selected_source_row_count = 5
event_candidate_rows = 5
validator_status = passed
validator_hard_fail_count = 0
validator_review_fail_count = 0
```

Lectura correcta: este tramo crea eventos candidatos versionados desde la base intradia quote-guarded. No convierte el `+50%` en estado base; el umbral vive en `event_definition_id` como hipotesis/definicion operativa para abrir ventanas y medir outcomes separados. No es scanner completo v0_2, no es tabla oficial, no es full-universe y no habilita ML/RL/AlphaEvolve.

## 7.7 Consumo Controlado Por Intraday 1m Event Windows

```text
script = scripts/materialize_intraday_1m_strategy_event_windows_candidate.py
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
row_count = 15
window_role_counts = event_anchor_1m: 5, post_event_30m: 5, pre_event_30m: 5
validator_status = passed
```

Lectura correcta: este tramo abre ventanas para `event_state` y outcomes separados. `pre_event_30m` puede alimentar X bajo cutoff; `post_event_30m` no puede alimentar X.

## 7.8 Consumo Controlado Por Event State Intradia 1m

```text
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
rows = 15
validator_status = passed
```

Lectura correcta: cierra la ruta controlada `1m quote-guarded -> market_state -> events -> windows -> event_state`. No cierra outcomes ni evaluadores.
