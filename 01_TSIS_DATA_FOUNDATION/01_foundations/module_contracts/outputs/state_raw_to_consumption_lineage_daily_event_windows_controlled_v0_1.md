# State RAW To Consumption Lineage - Daily Event Windows Controlled v0.1

## Estado

Tipo: lineage especifico ligado a `state_raw_to_consumption_lineage_contract_v0_1.md`.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - MARKET STATE / CAMINO A DAILY CONTROLADO`.
Fecha: 2026-07-05.

Status:

```text
state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1 = complete_for_controlled_scope
scope = daily_eod_controlled_replay_2025-01-02_to_2025-01-10
full_universe_claim = false
official_e_root_materialization = false
intraday_1m_claim = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

## 1. Proposito

Este documento traza el Camino A controlado desde fuentes gobernadas hasta las
ventanas de evento daily que se usaran como input para el primer fixture
controlado de `market_state/event_state`.

Cadena cubierta:

```text
master_daily_table_v0_1 + instrument_master + market_calendar + scanner definitions
-> daily_scanner_candidates_table_v0_3_candidate_replay
-> daily_strategy_candidate_events_table_v0_1 controlled candidate
-> event_windows_table_v0_1_candidate_daily_strategy_events
-> futuro controlled market_state/event_state fixture
```

No cubre todavia:

```text
intradia 1m quote-guarded;
quotes/trades/microestructura;
news/fundamentals/short/regime;
outputs oficiales E-root de event candidates/event windows;
outcomes;
ML/RL/AlphaEvolve.
```

## 2. Lectura Correcta

Los `69` eventos daily controlados no vienen de 1m. Vienen de un replay daily
EOD proxy sobre `master_daily_table_v0_1` con `price_view = daily_raw`.

```text
EOD daily proxy = se conoce despues del cierre/session close.
No certifica premarket, regular, afterhours ni primer cruce intradia.
```

Por tanto, este lineage sirve para probar la mecanica:

```text
scanner candidate -> event candidate -> event windows -> state fixture
```

No sirve para afirmar que ya tenemos la ruta intradia 1m de estrategias.

## 3. Tramo 0 - Fuentes Gobernadas Base

| Componente | Path | Estado de lineage | Rol |
| --- | --- | --- | --- |
| `master_daily_table_v0_1` | `E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1` | `derived_authority_declared_scope` | superficie daily `daily_raw`, `split_normalized`, `adjusted` |
| `master_daily_table_v0_1` manifest | `E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_manifest_v0_1.json` | `lineage_only` | build id, sources, hashes, validations |
| `instrument_master_v0_1` | `E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet` | `support_only` | identidad instrument/ticker |
| `instrument_master_v0_1` manifest | `E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json` | `lineage_only` | build id y version de identidad |
| `market_calendar_v0_1` | `E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet` | `support_only` | sesiones, open/close UTC, session close cutoff |
| `market_calendar_v0_1` manifest | `E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json` | `lineage_only` | build id y calendario fuente |
| scanner definitions | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions` | `definition_only` | parametros versionados del scanner |

Linea RAW resumida de `master_daily_table_v0_1`:

```text
E:/TSIS/data/ohlcv_daily
+ E:/TSIS/data/ohlcv_daily_adjusted
+ expected_data_calendar
+ corporate_actions_table
+ dataset_certification_matrix
-> scripts/materialize_master_daily_table.py
-> master_daily_table_v0_1
```

La trazabilidad completa de `master_daily_table_v0_1` esta cerrada en:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
```

## 4. Tramo 1 - Daily Scanner Candidates v0.3 Controlled Replay

### Identidad

```text
dataset_id = daily_scanner_candidates_table_v0_3
physical_dataset_id = daily_scanner_candidates_table_v0_3_candidate_replay
status = materialized_controlled_replay_not_official
promotion_level = controlled_replay_candidate
build_run_id = daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d_year_2025
created_at_utc = 2026-06-30T16:26:43Z
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/parts/year=2025/daily_scanner_candidates_table_v0_3_candidate_replay/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/parts/year=2025/_daily_scanner_candidates_table_manifest_v0_3_candidate_replay.json
```

### Scope

```text
start_date = 2025-01-02
end_date = 2025-01-10
sessions = 6
price_view = daily_raw
as_of_policy = session_close_utc_from_market_calendar
intraday_decision_allowed = false
full_universe_claim = false
population_scope = controlled_daily_eod_in_play_momentum_proxy_replay
```

### Fuentes

```text
master_daily_root = E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
master_daily_manifest = E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_manifest_v0_1.json
instrument_master = E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
instrument_master_manifest = E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json
market_calendar = E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
market_calendar_manifest = E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json
scanner_definitions_dir = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions
```

### Scanner Definitions

```text
base_eligible_smallcap_denominator_v0_3
sha256 = 50206e32683e7c86262f85b2a6e590d2bcec5b522ebe5cdb8b9ffee3a202b31d
role = base_observable_smallcap_denominator

in_play_momentum_candidate_denominator_v0_3
sha256 = 17297e73d1b2dbd1d8aa3bc026593e80e2bac58c93deeb3a932e989ae56f1931
role = governed_in_play_candidate_selection

trade_station_like_profile_v0_3
sha256 = e558880c548e331288b435a24bded111f80449084439c5bdccd52c04b03ea591
role = operational_visibility_replay
```

### Transformacion

El scanner evalua filas daily EOD del master daily. Su seleccion `in-play` en
este replay aplica una definicion de movimiento/tradabilidad daily proxy.

Puntos contractuales:

```text
minimum_push_move_pct = 50.0
percent_change_min_threshold_applied = true
relative_volume_profile_status = unavailable_without_intraday_asof
dollar_volume_profile_semantic_role = tradability_not_alpha
DAS = removed_from_global_scanner_strategy_overlay_only
float_filter_used_rows = 0
```

Lectura correcta:

```text
El umbral 50% vive en una definicion versionada de scanner/evento.
No entra como atributo base de estado ni como verdad cientifica fija.
```

### Evidencia

```text
row_count = 15323
instrument_count = 2590
selected_any_profile_rows = 69
selected_in_play_momentum_candidate_rows = 69
trade_station_like_profile_rows = 150
relative_volume_profile_rows = 0
percent_change_profile_rows = 20
dollar_volume_tradability_profile_rows = 2930
future_information_flagged_rows = 0
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
duplicate_key_groups = 0
```

### No Es

```text
market_state_table;
event_state_table;
evento canonical;
feature causal;
label/reward/outcome;
scanner intradia 1m;
full-universe official E-root.
```

## 5. Tramo 2 - Daily Strategy Candidate Events v0.1 Controlled Candidate

### Identidad

```text
dataset_id = daily_strategy_candidate_events_table_v0_1
schema_version = daily_strategy_candidate_events_table_v0_1
promotion_level = candidate_not_promoted
materialization_scope = controlled_candidate_not_promoted
build_run_id = daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled
created_at_utc = 2026-07-04T00:00:00Z
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/daily_strategy_candidate_events_table_v0_1_candidate/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/_daily_strategy_candidate_events_table_v0_1_manifest_candidate.json
```

### Fuente Inmediata

```text
source_candidate_dataset_id = daily_scanner_candidates_table_v0_3
source_candidates_path = C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/parts/year=2025/daily_scanner_candidates_table_v0_3_candidate_replay/data.parquet
source_candidate_manifest = C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/parts/year=2025/_daily_scanner_candidates_table_manifest_v0_3_candidate_replay.json
source_candidates_sha256 = fb383ba35dcde5528911c1352c2f1f1195e40bc75717193d4f56ab6f4916ac0e
source_candidate_manifest_sha256 = 772ce14cb337f056625c8b239358ea946758de2ba458d5d26d771815040f12d1
```

### Transformacion

El builder convierte filas seleccionadas por scanner en anclas de evento con
`event_id`, definicion versionada, timestamp legal y lineage.

```text
selection_column = selected_any_profile
event_definition_id = daily_in_play_momentum_candidate_event_v0_1
event_definition_version = v0_1
```

No copia outcomes ni labels. No convierte el scanner en estado. Solo formaliza
un evento candidato daily EOD a partir de una seleccion gobernada.

### Evidencia

```text
source_row_count = 15323
selected_source_row_count = 69
row_count = 69
validator_status = passed
validator_hard_fail_count = 0
validator_review_fail_count = 0
warning_count = 0
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
alphaevolve_production_enabled_rows = 0
```

Validator:

```text
validator_contract_id = event_candidate_table_validators_contract_v0_1
validator_version = event_candidate_table_validators_executable_v0_1
validator_run_id = event_candidate_table_validators_executable_v0_1_20260704T202131Z
```

### Consumo Permitido

```text
event_windows_candidate = permitido en scope controlado
market_state/event_state fixture = permitido como event lineage controlado
ML/RL/AlphaEvolve production = false
promotion oficial = false
```

### No Es

```text
tabla de estado;
scanner;
outcome;
label;
reward;
fill/PnL;
evento intradia 1m;
E-root official;
full-universe.
```

## 6. Tramo 3 - Event Windows Candidate Daily Strategy Events

### Identidad

```text
dataset_id = event_windows_table_v0_1_candidate_daily_strategy_events
schema_version = event_windows_table_v0_1_candidate_daily_strategy_events
promotion_level = controlled_candidate_not_promoted
materialization_scope = daily_strategy_event_windows_controlled_candidate
build_run_id = daily_strategy_event_windows_from_69_daily_events_controlled
created_at_utc = 2026-07-05T00:00:00Z
```

Output:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/event_windows_table_v0_1_candidate_daily_strategy_events/data.parquet
```

Manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/_event_windows_table_v0_1_candidate_daily_strategy_events_manifest.json
```

### Fuentes Inmediatas

```text
source_event_dataset_id = daily_strategy_candidate_events_table_v0_1
source_event_table = C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/daily_strategy_candidate_events_table_v0_1_candidate/data.parquet
source_event_manifest = C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/_daily_strategy_candidate_events_table_v0_1_manifest_candidate.json
source_market_calendar = E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
source_market_calendar_manifest = E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json
```

Hashes:

```text
source_event_table_sha256 = 69a7f2efba2283feee2c635a9e54f9f03db3bbedb27f431069bb3428d0f725b5
source_event_manifest_sha256 = 4ab07f59964be98c4cd1029633a6a691469c2a8cd9dd13e615d1cb5c958c4ce4
source_market_calendar_sha256 = cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c
source_market_calendar_manifest_sha256 = 60e6ccaeb00a50e1033e8120ae97564ca9cce34aadbbd96fc8d2f860e7955306
```

### Transformacion

Por cada evento daily se abren tres ventanas de sesion regular usando
`market_calendar`:

```text
prior_session_regular
event_session_regular
next_session_regular
```

Lectura de roles:

```text
prior_session_regular = ventana pre-evento utilizable como feature candidate controlada
event_session_regular = ventana de sesion del evento, no ML pre-event
next_session_regular = ventana candidata de outcome, separada del estado
```

### Evidencia

```text
source_event_count = 69
calendar_covered_event_count = 69
excluded_no_market_calendar_session_event_count = 0
row_count = 207
unique_event_window_id_count = 207
duplicate_event_window_id_count = 0
ticker_count = 59
instrument_count = 59
window_role_counts = prior_session_regular: 69, event_session_regular: 69, next_session_regular: 69
event_window_quality_state_counts = good: 207
ml_feature_candidate_rows = 69
outcome_window_candidate_rows = 69
microstructure_feature_candidate_rows = 0
backtest_event_window_candidate_rows = 207
rl_state_component_candidate_rows = 0
full_universe_claim_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

### Consumo Permitido

```text
controlled market_state/event_state fixture = permitido como ventana/ancla controlada
outcome join futuro = permitido solo desde tabla outcome separada
ML feature candidate = solo prior_session_regular y solo en scope controlado
RL state component = false
AlphaEvolve production = false
```

### No Es

```text
event_windows_table_v0_1 oficial;
tabla halts-only oficial;
E-root official;
full-universe;
intradia 1m;
state table;
outcome table;
execution truth;
ML/RL/AlphaEvolve-ready dataset.
```

## 7. Cadena Completa Compacta

```text
E:/TSIS/data/ohlcv_daily
+ E:/TSIS/data/ohlcv_daily_adjusted
+ expected_data_calendar
+ corporate_actions_table
+ dataset_certification_matrix
-> master_daily_table_v0_1

master_daily_table_v0_1
+ instrument_master_v0_1
+ market_calendar_v0_1
+ scanner definitions v0.3
-> daily_scanner_candidates_table_v0_3_candidate_replay

selected_any_profile rows
-> daily_strategy_candidate_events_table_v0_1 controlled candidate

69 daily event candidates
+ market_calendar_v0_1
-> event_windows_table_v0_1_candidate_daily_strategy_events

207 event windows controlled
-> futuro controlled market_state/event_state fixture
```

## 8. Cutoff / As-Of

| Tramo | Cutoff legal |
| --- | --- |
| `master_daily_table_v0_1` | daily EOD; no usar high/low/close/volume final antes del cierre |
| `daily_scanner_candidates_table_v0_3_candidate_replay` | `session_close_utc_from_market_calendar`; intraday decision disabled |
| `daily_strategy_candidate_events_table_v0_1` | `as_of_utc`/event availability daily EOD desde source candidate |
| `event_windows_table_v0_1_candidate_daily_strategy_events` | ventanas de calendario; no introduce observables de mercado nuevos |
| futuro `event_state` | debe respetar decision timestamp y snapshot role antes de unir observables |

## 9. Reglas De Consumo Para El Fixture De Estado

Para el fixture controlado de `market_state/event_state`:

```text
se puede usar daily__* desde master_daily_table_v0_1 bajo cutoff;
se puede usar event__* desde daily_strategy_candidate_events_table_v0_1 como metadata de evento;
se puede usar window references desde event_windows_table_v0_1_candidate_daily_strategy_events;
no se puede usar next_session_regular como feature X;
no se puede meter outcome inline;
no se puede afirmar intraday timing;
no se puede activar ML/RL/AlphaEvolve production.
```

## 10. Gaps Abiertos

```text
1. Falta lineage equivalente para intradia 1m quote-guarded.
2. Falta lineage equivalente para microestructura quotes/trades.
3. Falta lineage equivalente para contexto as-of si entra en el fixture.
4. Falta builder controlado de market_state/event_state que consuma esta cadena.
5. Falta validator ejecutable de RAW-to-consumption lineage parity.
6. Falta E-root/wider materialization para daily event candidates y event windows.
```

## 11. Regla Final

Este Camino A queda trazado para uso controlado:

```text
daily EOD governed lineage = OK para fixture controlado;
intraday strategy truth = no;
state official = no;
outcome/evaluator/AlphaEvolve = no.
```
