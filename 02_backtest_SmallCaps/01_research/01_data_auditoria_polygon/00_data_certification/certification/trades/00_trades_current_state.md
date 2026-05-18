# Trades | Estado actual util

Ancla correcta para `trades`:

- metodologia y lectura muestral: `auditoria/trades/v2/05_trades_file_acceptance_notebook.md`
- cierre full previsto: `auditoria/trades/v2/06_trades_file_acceptance_full_lt1b_closeout.ipynb`
- runner historico parcial: `auditoria/trades/cell_code/57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py`
- runner final correcto: `auditoria/trades/cell_code/57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py`

Rutas exactas:

- [05_trades_file_acceptance_notebook.md](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_notebook.md)
- [06_trades_file_acceptance_full_lt1b_closeout.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/06_trades_file_acceptance_full_lt1b_closeout.ipynb)
- [57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py)
- [57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py)

## Que hay realmente en disco

Hay tres runs full distintos que conviene separar:

1. `file_acceptance_cache_lt1b_full`
- corresponde al runner anterior `57c/57d`
- esta terminado
- resume `690,000` files
- sus `raw_metrics_shards` son de `5,000` files cada uno

2. `file_acceptance_cache_lt1b_full_clean`
- corresponde al runner `57e`
- conserva el universo indice completo `9,429,112`
- quedo parcial en recompute
- materializa `56` `raw_metrics_shards`
- total recompute observado: `5,600,000`

3. `file_acceptance_cache_lt1b_full_clean_fast_same_schema`
- corresponde al runner `57f`
- es el cierre operativo final correcto
- reutiliza el mismo universo y el mismo esquema de `57e`
- materializa `95` `raw_metrics_shards`
- total recompute observado: `9,429,112`
- `progress.json` queda en `phase = done`

## Separacion correcta de capas

Hay que separar tres cosas distintas:

1. universo full indexado `<1B>`
2. residuo root-cause `D full`
3. file-acceptance posterior

### 1. Universo full indexado `<1B>`

Esto si existe completo y materializado.

Prueba directa:

- `file_acceptance_cache_lt1b_full_clean/full_index_shards`
  - `95` shards
  - total: `9,429,112`
- `file_acceptance_cache_lt1b_full_clean_fast_same_schema/full_index_shards`
  - `95` shards
  - total: `9,429,112`
- los shards indice de `57e` y `57f` son equivalentes shard a shard

Rutas:

- [full_index_shards | 57e](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b_full_clean/full_index_shards)
- [full_index_shards | 57f](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema/full_index_shards)
- [05_trades_file_acceptance_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_audit.ipynb)

### 2. Residuo root-cause `D full`

Esto tambien existe y esta materializado aparte. No es el universo total, sino el conjunto de files que entran en el residuo `HARD_FAIL` ya bucketizado para root cause.

Tamano observado:

- `390,475` files

Rutas:

- [trades_full_root_cause_final_bucket.parquet](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_validation/trades_validate_2005_2026_d_full/root_cause_exports/trades_full_root_cause_final_bucket.parquet)
- [trades_full_root_cause_final_bucket.csv](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_validation/trades_validate_2005_2026_d_full/root_cause_exports/trades_full_root_cause_final_bucket.csv)
- [trades_full_root_cause_final_bucket_summary.parquet](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_validation/trades_validate_2005_2026_d_full/root_cause_exports/trades_full_root_cause_final_bucket_summary.parquet)
- [trades_full_root_cause_final_bucket_summary.csv](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_validation/trades_validate_2005_2026_d_full/root_cause_exports/trades_full_root_cause_final_bucket_summary.csv)

### 3. File-acceptance posterior

Aqui vive la capa metodologicamente mas fina para certificacion de `trades`, y la lectura correcta ya no es esperar a que termine `57e`, sino usar `57f` como cierre final.

- `57d/full`
  - terminado
  - pero solo agrega `690,000`
- `57e/full_clean`
  - dejo el indice completo `9,429,112`
  - dejo recompute parcial
  - materializa `56` shards compatibles con `57f`
- `57f/full_clean_fast_same_schema`
  - conserva el mismo indice que `57e`
  - contiene tambien todos los `raw_metrics_shards` de `57e`
  - anade los `39` shards faltantes
  - cierra el recompute full y el agregado final

## Que usar como cierre final ahora

El cierre final de `trades` ya no debe anclarse en `file_acceptance_cache_lt1b_full` ni en `file_acceptance_cache_lt1b_full_clean`.

La referencia correcta para certificacion es:

- [file_acceptance_cache_lt1b_full_clean_fast_same_schema](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema)

Motivos:

- `57e` quedo parcial en recompute
- `57f` usa el mismo universo indice y el mismo esquema
- `57f` deja `95` `raw_metrics_shards`
- `57f` cubre `9,429,112` files raw `<1B>`
- los shards compartidos entre `57e` y `57f` son compatibles

## Estado actual desde raw shards finales de `57f`

La corrida final cerrada en disco es `57f/full_clean_fast_same_schema`.

Resumen materializado:

- `review = 4,851,211`
- `reference_scale_mismatch = 2,418,062`
- `review_microstructure = 2,130,781`
- `bad_data = 15,869`
- `review_no_1m_reference = 8,091`
- `review_1m_reference_alignment = 4,992`
- `good = 106`

Cobertura observada:

- `files_total_full_raw = 9,429,112`
- `files_with_1m_reference_pct = 98.33032`
- `files_with_daily_reference_pct = 98.44038`

## Lectura operativa

Lo importante ya no es demostrar que `57e` quedo abierto, sino fijar que el cierre real existe y esta localizado.

Conclusion actual:

- si existio un full anterior terminado, pero era `57d` sobre `690k`
- si existio un run limpio posterior `57e`, pero quedo parcial
- el cierre full correcto en disco es `57f/full_clean_fast_same_schema`
- para certificacion de `trades` ya no hace falta buscar otro agregado posterior mientras no aparezca una evidencia mas nueva que contradiga este estado
