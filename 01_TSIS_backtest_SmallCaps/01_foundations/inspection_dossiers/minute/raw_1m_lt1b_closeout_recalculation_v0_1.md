# Raw 1m Lt1b Closeout Recalculation `v0_1`

## Rol

Este documento recalcula el cierre historico raw de `1m` sobre el universo `<1B>` explicito.

No reabre:

- la policy historica de `1m`;
- ni la auditoria de `ohlcv_1m_split_normalized`.

Hace una sola cosa:

- aplicar el cierre raw historico sobre el corte canónico `lt1b`

para poder citar porcentajes y conteos de `1m raw` con alcance correcto.

## Inputs

- cierre raw historico:
  - `runs/backtest/ohlcv_1m_v2_materialized/ohlcv_1m_current_full/root_cause_operational_outputs/*.parquet`
- corte canonico:
  - `runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet`

Script:

- [audit_1m_raw_lt1b_closeout.py](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/minute/audit_1m_raw_lt1b_closeout.py)

Evidencia:

- [raw_1m_lt1b_exec_summary.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/evidence_assets/raw_1m_lt1b_closeout/raw_1m_lt1b_exec_summary.csv)
- [raw_1m_lt1b_bucket_summary.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/evidence_assets/raw_1m_lt1b_closeout/raw_1m_lt1b_bucket_summary.csv)
- [raw_1m_lt1b_ticker_bucket_counts.csv](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/evidence_assets/raw_1m_lt1b_closeout/raw_1m_lt1b_ticker_bucket_counts.csv)
- `raw_1m_lt1b_filtered_closeout.parquet`

Paquete inspector especifico para el bloque no-`vw`:

- [raw_1m_schema_only_lt1b_inspection_readout_v0_1.md](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md)
- [raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb)

## Regla de filtrado

El recalculo no filtra solo por ticker.

Filtra por:

- ticker presente en `lt1b`
- y interseccion temporal entre:
  - la ventana del file `1m`
  - y la ventana PTI del ticker en el corte `<1B>`

Esto evita dos errores:

- incluir tickers fuera de `lt1b`
- o incluir meses del ticker fuera de su ventana `<1B>`

## Resultado agregado

Resultado real del recalculo:

- `lt1b_tickers_reference = 4824`
- `lt1b_current_1m_rows = 334660`
- `lt1b_current_1m_unique_tickers = 4822`
- `lt1b_current_1m_unique_task_keys = 334660`

Buckets operativos heredados del cierre raw historico, ya restringidos a `<1B>`:

- `RESCUE_SCHEMA_ONLY = 19713` (`5.890456%`)
- `RESCUE_SCHEMA_PLUS_VW = 314947` (`94.109544%`)

Refinado final `good/review/bad` sobre el universo `<1B>`:

- `good = 46652` (`13.940118%`)
- `review = 75245` (`22.484014%`)
- `bad = 212763` (`63.575868%`)

Taxonomia `vw_*` reconstruida exactamente con la logica del notebook historico:

- `vw_mild_low_ratio = 26939` (`8.049662%`)
- `vw_moderate_ratio = 23933` (`7.151437%`)
- `vw_severe_tiny_base = 12035` (`3.596187%`)
- `vw_severe_small_mass = 39277` (`11.736389%`)
- `vw_severe_large_mass_diffuse = 90159` (`26.940477%`)
- `vw_severe_large_mass_persistent = 122604` (`36.635391%`)

Lectura inmediata:

- el matiz de alcance ya queda cerrado cuantitativamente;
- el cierre raw historico de `1m` no necesita reinterpretacion semantica nueva;
- pero en `<1B>` la masa dominante no es `schema_only`, sino `schema_plus_vw` refinado en familias severas de `vw`.

## Lectura esperada

La utilidad de este recalculo no es cambiar la policy historica.

La utilidad es cerrar el matiz de alcance:

- dejar de citar porcentajes `full-scope`
- y poder citar ya porcentajes raw `1m` realmente compatibles con el universo `lt1b`

Tambien deja una conclusion mas fuerte que antes no se podia sostener:

- el universo `<1B>` no suaviza artificialmente el problema `vw`;
- al contrario, incluso tras filtrar por alcance correcto, la parte `bad` sigue siendo dominante.

## Consecuencia institucional

Con estos conteos ya exportados:

- el cierre historico raw de `1m` quedara reconciliado no solo en policy;
- tambien en alcance cuantitativo frente al marco moderno `<1B>`.

Y a partir de ahora, cuando se cite calidad raw de `1m`, la regla correcta sera:

- usar el cierre historico `full-scope` solo como antecedente metodologico;
- y usar este recalculo cuando la afirmacion exija numeros raw `1m` estrictamente `<1B>`.
