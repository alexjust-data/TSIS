Para un agente, dale primero estos paths.

  Contratos y estado

  C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
  C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
  C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\leaf_slices\data_foundation_outputs_topology_20260629\

  Tablas materializadas

  E:\TSIS\data\data_foundation_outputs\
  E:\TSIS\data\data_foundation_outputs\instrument_master\
  E:\TSIS\data\data_foundation_outputs\market_calendar\
  E:\TSIS\data\data_foundation_outputs\corporate_actions_table\
  E:\TSIS\data\data_foundation_outputs\master_daily_table\
  E:\TSIS\data\data_foundation_outputs\master_intraday_bar_table\
  E:\TSIS\data\data_foundation_outputs\microstructure_features_table\
  E:\TSIS\data\data_foundation_outputs\halts_table\
  E:\TSIS\data\data_foundation_outputs\event_windows_table\
  E:\TSIS\data\data_foundation_outputs\outcomes_table\
  E:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\
  E:\TSIS\data\data_foundation_outputs\news_context_table\
  E:\TSIS\data\data_foundation_outputs\short_context_table\
  E:\TSIS\data\data_foundation_outputs\regime_context_table\
  E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\
  E:\TSIS\data\data_foundation_outputs\expected_data_calendar\
  E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\

  Runs y evidencia

  C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\
  C:\TSIS_Data\tests\data_foundation_outputs\
  C:\TSIS_Data\tests\test_runs\

  Importante
  short_sale_constraints_table, market_state_table y event_state_table tienen contrato/esqueleto, pero no son tablas materializadas finales
  todavía. El agente debe leer la status matrix antes de asumir que una tabla está lista para ML/RL o backtesting institucional.