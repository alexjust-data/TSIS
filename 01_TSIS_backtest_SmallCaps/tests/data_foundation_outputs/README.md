# Data Foundation Output Tests

Este directorio contiene los tests ejecutables de las tablas objetivo de
`CAPA 1 - DATA FOUNDATION`.

Las tablas viven bajo:

```text
E:/TSIS/data/data_foundation_outputs/
```

Los contratos viven bajo:

```text
01_foundations/module_contracts/outputs/
```

## Tablas objetivo

Aqui deben validarse, como minimo:

- `instrument_master`
- `market_calendar`
- `expected_data_calendar`
- `corporate_actions_table`
- `dataset_certification_matrix`
- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `halts_table`
- `event_windows_table`
- `outcomes_table`
- `real_time_corporate_event_alerts_table`
- `fundamentals_asof_table`
- `news_context_table`
- `short_context_table`
- `short_sale_constraints_table`
- `regime_context_table`
- `market_state_table`
- `event_state_table`
- `data_quality_report`
- `daily_scanner_candidates_table`
- `intraday_scanner_candidates_table`

## Estado actual

Tablas CAPA 1 con tests contractuales ejecutables y materializacion v0.1:

- `instrument_master`
- `market_calendar`
- `expected_data_calendar`
- `corporate_actions_table`
- `dataset_certification_matrix`
- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `halts_table`
- `event_windows_table`
- `outcomes_table`
- `fundamentals_asof_table`
- `news_context_table`
- `short_context_table`
- `regime_context_table`

Contract/fixture stacks with executable tests but no materialized parquet yet:

- `market_state_table`
- `event_state_table`
- `daily_scanner_candidates_table_v0_3`
- `intraday_scanner_candidates_table_v0_1`

Ultima evidencia fixture de `daily_scanner_candidates_table_v0_3`:

```text
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py
tests = 1
passed = 1
failed = 0
skipped = 0
```

Esta evidencia prueba el modelo activo:

```text
base_eligible_smallcap_denominator_v0_3
  = common stock
  + market cap < 100M
  + 0.5 < last_price <= 20
  + data quality usable/review

in_play_momentum_candidate_denominator_v0_3
  = base eligible
  + strong move >= 50%
  + tradability gate
```

Regla:

```text
strategy overlays != global scanner denominator
```

`DAS` y cualquier estrategia futura deben aplicarse despues del scanner global.
El builder global v0.3 mantiene `selected_das_research_profile = false`.

Ultimo replay controlado real de `daily_scanner_candidates_table_v0_3`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum/
rows = 15323
sessions = 6
instruments = 2590
scanner_semantic_alignment_version = v0_3_0_in_play_momentum_denominator
base_eligible_rows = 6184
selected_in_play_momentum_candidate_rows = 69
selected_trade_station_like_profile_rows = 150
selected_das_research_profile_rows = 0
selected_without_50_move = 0
selected_without_tradability = 0
min_selected_motion_pct = 50.2851
max_selected_motion_pct = 363.6408
duplicate_key_groups = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
live_downstream_candidate_rows = 0
in_play_detection_scope = daily_eod_proxy
in_play_segment_detection_state = available_in_intraday_scanner_candidates_table_v0_1_controlled_replay
```

Interpretacion obligatoria:

```text
controlled_replay_candidate != official promoted dataset
daily_eod_proxy != certified premarket/regular/afterhours segment detection
```

Ultima evidencia fixture de `intraday_scanner_candidates_table_v0_1`:

```text
tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py
tests = 1
passed = 1
failed = 0
skipped = 0
```

Esta evidencia prueba:

```text
premarket first cross
regular first cross
afterhours motion without tradability
non-common-stock exclusion
market-cap exclusion
duplicate ticker-session prevention
```

Ultimo replay controlado real de `intraday_scanner_candidates_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
run_id = intraday_scanner_candidates_v0_1_20260630T175311Z
rows = 33413
tickers = 5690
session_dates = 6
base_eligible_rows = 7498
motion_threshold_rows = 235
tradability_pass_rows = 176
selected_intraday_in_play_candidate_rows = 102
first_cross_premarket_rows = 114
first_cross_regular_rows = 82
first_cross_afterhours_rows = 39
duplicate_ticker_session_keys = 0
full_universe_claim = false
```

Interpretacion obligatoria:

```text
intraday scanner v0.1 = first-push timing candidate surface
daily scanner v0.3 = daily/EOD coarse context
scanner rows != market_state/event_state/label/reward/strategy signal
```

Runner largo validado para `daily_scanner_candidates_table_v0_3`:

```text
scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
```

Smoke runner:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/
status = completed
year_window_count = 1
elapsed_seconds = 24
full_universe_claim = false
```

Este runner escribe:

```text
pre_manifest
heartbeat
heartbeat.jsonl
pids
logs
_run_summary.json
```

Regla:

```text
multi-year / 20-year scanner candidate runs must use the runner, not direct
python builder execution.
```

La evidencia v0.2 queda como historica porque documento la etapa intermedia
con perfiles paralelos y el error de incluir overlays de estrategia dentro del
builder global.

Ultima evidencia fixture de `daily_scanner_candidates_table_v0_2`:

```text
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
tests = 1
passed = 1
failed = 0
skipped = 0
```

Esta evidencia prueba el modelo:

```text
base_in_play_universe_scanner_v0_2
  = base_eligible_smallcap_denominator
  + governed parallel profile flags
```

Esta evidencia no prueba que los perfiles sean un embudo secuencial ni que
`das_research_profile_v0_2` sea un scanner DAS final.

No materializa parquet oficial ni escribe en `E:/TSIS/data`.

Ultimo replay controlado real de `daily_scanner_candidates_table_v0_2`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_2_1_contract_aligned/
rows = 15323
sessions = 6
instruments = 2590
scanner_semantic_alignment_version = v0_2_1_contract_aligned
selected_any_profile_rows = 2314
selected_trade_station_like_profile_rows = 150
selected_relative_volume_profile_rows = 0
selected_percent_change_profile_rows = 150
selected_dollar_volume_tradability_profile_rows = 150
selected_das_research_profile_rows = 2261
selected_below_500k_volume_rows = 1800
duplicate_key_groups = 0
float_filter_used_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
live_downstream_candidate_rows = 0
relative_volume_profile_status = unavailable_without_intraday_asof
percent_change_min_threshold_pct = 3.0
dollar_volume_profile_semantic_role = tradability_not_alpha
das_research_profile_status = provisional_strategy_overlay_seed_not_final_scanner
```

Interpretacion obligatoria:

```text
controlled_replay_candidate != official promoted dataset
```

Ultima evidencia integrada:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
tests = 3
passed = 3
failed = 0
skipped = 0
```

Ultima evidencia aislada de `halts_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `event_windows_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `outcomes_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `fundamentals_asof_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `news_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `short_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `regime_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia skeleton de `market_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia skeleton de `event_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia fixture/adversarial conjunta de `market_state_table_v0_1` y
`event_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
tests = 14
passed = 14
failed = 0
skipped = 0
```

Esta evidencia ejecuta builders fixture-only contra:

- fixtures buenos deterministas;
- fixture `market_state` con as-of futuro;
- fixture `market_state` con feature prohibida `label__*`;
- fixture `event_state` con label inline;
- fixture `event_state` con `post_event_review` marcado como feature ML.

No materializa parquet oficial ni escribe en `E:/TSIS/data`.

Ultima evidencia de manifest candidato para
`microstructure_features_table_v0_2_candidate`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
tests = 5
passed = 5
failed = 0
skipped = 0
```

Esta evidencia ejecuta
`scripts/build_microstructure_candidate_window_manifest.py` contra
`event_windows_table_v0_1` y despues ejecuta
`scripts/materialize_microstructure_features_table.py` en modo candidato bajo
`artifacts/`.

Resultado semantico:

```text
source_event_windows_rows = 214112
eligible_microstructure_rows = 85658
eligible_role_counts:
  pre_event_30m = 42829
  same_session_regular = 42829
selected_rows_in_test_manifest = 6
candidate_feature_rows_materialized_under_test_artifacts = 6
candidate_quotes_file_present_rows = 6
candidate_trades_file_present_rows = 6
candidate_hard_fail_count = 0
official_dataset_created = false
```

Ultima evidencia de regresion para el builder de manifiesto
`ohlcv_1m_split_normalized`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_1m_split_manifest_builder_v0_1/
tests = 2
passed = 2
failed = 0
skipped = 0
```

Esta evidencia usa fixtures sinteticos y bloquea que el builder vuelva a usar
`Path.rglob()` para el smoke `split-affected`. La ruta correcta es:

```text
splits_root -> ticker con split -> ticker/year/month esperado en ohlcv_1m
```

No escribe parquet oficial y no modifica `microstructure_features_table_v0_1`.
La prueba reconcilia hashes y conteos de filas contra raw quotes/trades para
las ventanas candidatas seleccionadas.

Ultima evidencia de candidato controlado materializado para
`microstructure_features_table_v0_2_candidate`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_v0_2_controlled_candidate/
tests = 5
passed = 5
failed = 0
skipped = 0
```

Esta evidencia valida el candidato fisico:

```text
dataset_id = microstructure_features_table_v0_2_candidate
materialization_scope = halt_event_windows_microstructure_candidate_controlled_25_per_role
output = E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate_controlled_25_per_role
manifest = E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json
rows = 50
tickers = 9
windows = 50
quotes_file_present_rows = 50
trades_file_present_rows = 24
review_partial_source_rows = 26
pass_seed_window_rows = 24
hard_fail_count = 0
duplicate_key_groups = 0
full_universe_claim_rows = 0
execution_sim_candidate_rows = 0
backtest_core_microstructure_candidate_rows = 0
quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity
trades_root_state = official_e_raw_root
visual_readout = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
visual_manifest = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json
visual_case_count = 50
visual_cached_quote_files_read = 9
visual_cached_trade_files_read = 5
```

El test comprueba manifest, summary, hash del arbol parquet, paths de contratos,
semantica de source-window, flags de no promocion, missingness de trades y
recomputacion puntual desde raw quotes/trades. Tambien valida que exista el pack
visual/forense de 50 imagenes. No hace scans amplios sobre roots con millones
de archivos: lee la particion declarada del candidato, dos muestras raw por path
exacto y el manifest visual con rutas de imagen exactas.

Interpretacion obligatoria:

```text
candidate materialized != official promoted dataset
```

Este candidato no autoriza ML/RL primario, core backtesting, execution
simulation ni claim full-universe.

Guardia de regresion de `microstructure_features_table_v0_1` despues de
parametrizar el materializer:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_features_table_v0_1_default_guard/
tests = 3
passed = 3
failed = 0
skipped = 0
```

Evidencia anterior de las siete primeras tablas:

```text
C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
tests = 29
passed = 29
failed = 0
skipped = 0
```

## Cinco capas minimas de test

Cada tabla institucional debe tener cinco familias de pruebas.

1. Schema contract test

Valida columnas, tipos, nullability, claves, unicidad, version logica y campos
obligatorios. No basta con que el parquet abra.

2. Manifest and hash test

Valida que el output materializado coincide con su manifest: ruta, `run_id`,
`sha256`, conteos, version, source fingerprints y timestamp de construccion.

3. Source reconciliation test

Reconcilia la tabla contra las fuentes declaradas. Ejemplos: `instrument_master`
contra universe/reference, `market_calendar` contra el parquet oficial XNYS,
`corporate_actions_table` contra splits/dividends/events declarados.

4. Third-party evidence test

Compara una muestra deterministica contra fuentes externas independientes o
evidencia congelada. Ejemplos: SEC EDGAR, NYSE, Nasdaq, OpenFIGI o proveedor
certificado.

Estos tests no deben depender de internet por defecto. Deben usar evidencia
cacheada o requerir una variable como `TSIS_RUN_THIRD_PARTY=1`.

5. Adversarial or mutation test

Inyecta errores controlados y comprueba que el validador falla. Ejemplos:
duplicados, fechas imposibles, `open_utc >= close_utc`, tickers vacios, CIK mal
formateado, outputs sin manifest o hashes incorrectos.

## Criterio contra trampas al solitario

Una tabla no queda institucionalizada porque su propio script diga que esta bien.
Debe haber pruebas que la ataquen desde fuera:

- contrato independiente;
- manifest independiente;
- reconciliacion con fuentes;
- evidencia externa o cacheada;
- mutaciones que demuestren que el test falla cuando debe fallar.

## Evidencia humana

Los tests ejecutables no sustituyen los dossiers visuales. Cuando una tabla o
familia de datos requiere inspeccion humana, el test debe validar que existe la
ruta de evidencia esperada bajo:

```text
01_foundations/data_quality_report/
```

o bajo el dossier especifico definido por contrato.
