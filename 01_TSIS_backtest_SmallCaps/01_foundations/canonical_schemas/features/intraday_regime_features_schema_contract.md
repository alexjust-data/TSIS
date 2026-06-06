# Intraday Regime Features Schema Contract `v0_1`

## 1. Rol

Este documento fija el schema fisico observado de:

- `intraday_regime_features_v0_1`

No promociona la capa como full-universe `<1B>`.

La capa representa un consumidor piloto validado de `ohlcv_1m_split_normalized`, con grano `ticker-day`, orientado a features/states intradia para research, ML y backtest contextual.

## 2. Raiz fisica observada

Raiz:

- `E:\TSIS\data\intraday_regime_features`

Layout observado:

- `ticker=<TICKER>\year=<YYYY>\day_features_<TICKER>_<YYYY>.parquet`

Summary observado:

- `E:\TSIS\data\intraday_regime_features\_intraday_regime_features_materialization_summary.csv`

Muestra inspeccionada:

- `E:\TSIS\data\intraday_regime_features\ticker=BNGO\year=2025\day_features_BNGO_2025.parquet`

## 3. Cobertura fisica observada

La materializacion observada cubre el universo piloto conectado a `ohlcv_1m_split_normalized`:

- `BNGO`
- `BXRX`
- `CEI`
- `COSM`
- `EFSH`
- `LIVE`
- `PD`
- `SAVA`

Filas por ticker en el summary:

- `BNGO`: `47`
- `BXRX`: `48`
- `CEI`: `26`
- `COSM`: `26`
- `EFSH`: `26`
- `LIVE`: `23`
- `PD`: `23`
- `SAVA`: `24`

Lectura institucional:

- esto es materializacion piloto;
- no es coverage full-universe `<1B>`;
- no es feature layer productiva global;
- si es evidencia persistida de un consumidor real de `1m_split_normalized`.

## 4. Columnas canónicas

### Identidad y grano

- `date`: `timestamp[ns]`
- `ticker`: `string`
- `year`: `int64`
- `feature_contract`: `string`
- `feature_grain`: `string`

Valores esperados actuales:

- `feature_contract = intraday_regime_features_v0_1`
- `feature_grain = ticker_day`

### Features intrasesion locales sobre `1m raw`

Estas columnas describen la sesion observada localmente y deben interpretarse con semantica raw:

- `bar_count_raw`: `int64`
- `open_raw`: `double`
- `close_raw`: `double`
- `high_raw`: `double`
- `low_raw`: `double`
- `cum_volume_session_raw`: `double`
- `session_vwap_raw`: `double`
- `intraday_return_since_open_raw`: `double`
- `session_range_pct_raw`: `double`
- `opening_drive_30m_raw`: `double`
- `pullback_from_session_high_raw`: `double`
- `session_vwap_distance_raw`: `double`

### Base split-normalized para comparabilidad entre sesiones

Estas columnas proceden de la vista de escala comparable:

- `open_norm`: `double`
- `close_norm`: `double`
- `high_norm`: `double`
- `low_norm`: `double`
- `session_range_abs_norm`: `double`
- `realized_vol_1d_norm`: `double`
- `max_future_split_factor_in_day`: `double`

### Features cross-session sobre `1m_split_normalized`

Estas columnas cruzan sesiones y no deben calcularse sobre `1m raw` salvo auditoria explicita:

- `gap_open_vs_prev_close`: `double`
- `open_vs_prev_session_close`: `double`
- `open_vs_prev_session_high`: `double`
- `open_vs_prev_session_low`: `double`
- `multi_session_return_3d_to_open`: `double`
- `multi_session_return_5d_to_open`: `double`
- `distance_to_prev_day_range_center`: `double`
- `prev_day_range_pct_norm`: `double`
- `range_expansion_vs_prev_day_norm`: `double`
- `distance_to_n_day_high_5`: `double`
- `distance_to_n_day_low_5`: `double`
- `realized_vol_prev_3_sessions_norm`: `double`
- `overnight_gap_zscore_20`: `double`

### Provenance

- `cross_session_price_view`: `string`
- `intraday_price_view`: `string`
- `source_raw_root`: `string`
- `source_split_normalized_root`: `string`

Valores esperados actuales:

- `cross_session_price_view = 1m_split_normalized_v0_1`
- `intraday_price_view = 1m_raw`
- `source_raw_root = D:\ohlcv_1m`
- `source_split_normalized_root = E:\TSIS\data\ohlcv_1m_split_normalized`

## 5. Nulos esperados

En el inicio de cada serie pueden existir nulos en features que dependen de historia previa:

- `gap_open_vs_prev_close`
- `open_vs_prev_session_close`
- `open_vs_prev_session_high`
- `open_vs_prev_session_low`
- `multi_session_return_3d_to_open`
- `multi_session_return_5d_to_open`
- `distance_to_prev_day_range_center`
- `prev_day_range_pct_norm`
- `range_expansion_vs_prev_day_norm`
- `distance_to_n_day_high_5`
- `distance_to_n_day_low_5`
- `realized_vol_prev_3_sessions_norm`
- `overnight_gap_zscore_20`

Estos nulos no son automaticamente error; son consecuencia natural de lookback insuficiente.

## 6. Semantica obligatoria

Regla central:

- features que cruzan sesiones deben usar `1m_split_normalized`;
- features puramente intrasesion deben usar `1m raw`.

Esto evita que ML/backtest aprenda alpha falso de saltos mecanicos por splits, sin falsificar la geometria local observada de la sesion.

## 7. Estado institucional

Estado correcto:

- `Nivel 3 - Pilotada`
- `pilot_semantic_validation_consumer`

Estados no autorizados:

- `Nivel 6 - Promovida`
- `full_universe_feature_layer`
- `backtest_core_full_universe`

## 8. Documentos relacionados

- [intraday_regime_features_consumer_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md>)
- [intraday_regime_features_variable_taxonomy_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md>)
- [intraday_regime_features_initial_materialization_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md>)
- [intraday_regime_features_semantic_pilot_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md>)
- [intraday_regime_features_semantic_pilot_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md>)
