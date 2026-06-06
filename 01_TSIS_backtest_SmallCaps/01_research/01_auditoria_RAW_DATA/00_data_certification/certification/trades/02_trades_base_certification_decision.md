# Trades | Base certificadora

La base certificadora de `trades` no debe salir de una sola capa. Debe salir de la combinación correcta de tres capas ya materializadas.

## 1. Universo full

El universo full `<1B>` sí está indexado completo: `9,429,112` files.

Rutas:

- [full_index_shards | 57f](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema\full_index_shards)
- [full_index_shards | full](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full\full_index_shards)

## 2. Residuo root-cause de amplitud

El root-cause `D full` sí da un residuo grande y cerrado para anchura de problema.

Rutas:

- [trades_full_root_cause_final_bucket.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket.parquet)
- [trades_full_root_cause_final_bucket_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket_summary.parquet)

Distribución:

![D full distribution](img/11_d_full_final_bucket_distribution.png)

Lectura:

- `likely_real_break_confirmed_by_1m`: `290,664` (`74.439%`)
- `likely_dup_heavy_break`: `90,390` (`23.149%`)
- `likely_minor_unconfirmed_break`: `8,656` (`2.217%`)
- `manual_review`: `608`
- `scale_suspect`: `157`

## 3. Problema del bucket final viejo

El bucket final viejo de `D full` no aísla bien la escala. Mucha señal de escala queda absorbida dentro de `likely_real_break_confirmed_by_1m` y `likely_dup_heavy_break`.

Qué significa esto:

- `1x`
  - `trades` y referencias `daily/1m` están en la misma escala
- `far from 1x`
  - el factor de escala ya no está cerca de igualdad
- `extreme scale`
  - la diferencia de escala es muy fuerte y ya apunta a comparabilidad rota, no a un simple break económico

Punto importante:

- esto no significa que `D full` esté mal
- significa que su `final_bucket` viejo describe bien la masa residual
- pero no separa fino la causa dominante
- por eso no debe usarse solo como política certificadora final

![Scale contamination](img/12_d_full_scale_contamination_by_bucket.png)

Evidencia cuantitativa:

- `likely_real_break_confirmed_by_1m`
  - `far from 1x`: `58.779%`
  - `extreme scale`: `54.792%`
  - `VWAP diff >= 20%`: `60.131%`
- `likely_dup_heavy_break`
  - `far from 1x`: `71.614%`
  - `extreme scale`: `64.591%`
  - `VWAP diff >= 20%`: `75.761%`
- `likely_minor_unconfirmed_break`
  - `near 1x`: `99.838%`

Conclusión:

- el root-cause `D full` sirve bien para medir masa residual
- pero no sirve solo como política certificadora final
- necesita reinterpretación por la capa `file_acceptance`

## 4. Capa fina de reinterpretación

La capa metodológicamente correcta para reinterpretar ese residuo es `file_acceptance`, en especial `57f/full_clean_fast_same_schema`, porque separa:

- `reference_scale_mismatch`
- `review_microstructure`
- `review_1m_reference_alignment`
- `review_no_1m_reference`
- `review`
- `bad_data`

Rutas:

- [05_trades_file_acceptance_notebook.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\v2\05_trades_file_acceptance_notebook.md)
- [file_acceptance_cache_lt1b_full_clean_fast_same_schema](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema)
- [file_acceptance_cache_lt1b_full](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full)

## Decisión

Base certificadora recomendada para `trades`:

1. cobertura y universo esperado:
   `full_index_shards` de `57f/full_clean_fast_same_schema`
2. anchura del residuo:
   `trades_full_root_cause_final_bucket.*`
3. política final de aceptación:
   `file_acceptance` reinterpretando el residuo viejo

No conviene certificar `trades` directamente con el `final_bucket` viejo de `D full`, porque mezcla demasiada señal de escala dentro de buckets que aparentan ser “real break”.
