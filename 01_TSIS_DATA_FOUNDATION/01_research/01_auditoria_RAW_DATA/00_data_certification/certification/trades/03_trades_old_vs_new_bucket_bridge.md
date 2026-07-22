# Trades | Puente viejo vs nuevo

Objetivo:

- no tirar el trabajo viejo de `D full`
- pero tampoco certificar `trades` usando directamente su `final_bucket`

## Qué aporta cada capa

`D full` viejo:

- aporta amplitud
- ya deja materializado el residuo grande
- sirve para saber cuánto problema hay y de qué tipo general

Rutas:

- [trades_full_root_cause_final_bucket.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket.parquet)
- [trades_full_root_cause_final_bucket_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket_summary.parquet)

`file_acceptance` nuevo:

- aporta semántica de aceptación útil para certificación
- separa mejor:
  - `reference_scale_mismatch`
  - `review_microstructure`
  - `review_1m_reference_alignment`
  - `review_no_1m_reference`
  - `review`
  - `bad_data`

Rutas:

- [05_trades_file_acceptance_notebook.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\v2\05_trades_file_acceptance_notebook.md)
- [file_acceptance_cache_lt1b](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b)
- [file_acceptance_cache_lt1b_full](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full)
- [file_acceptance_cache_lt1b_full_clean_fast_same_schema](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema)

## Lectura práctica del puente

Mapeo conceptual útil:

- `scale_suspect`
  - puente natural hacia `reference_scale_mismatch`
- `likely_minor_unconfirmed_break`
  - puente natural hacia `review_no_1m_reference` o `review`
- `manual_review`
  - sigue `review`

Buckets que no deben mapearse en bloque:

- `likely_real_break_confirmed_by_1m`
- `likely_dup_heavy_break`

Razón:

- dentro de esos dos buckets viejos hay mezcla fuerte de:
  - break real
  - duplicado pesado
  - escala rota

Por tanto:

- no conviene traducirlos directamente a `good`, `review` o `bad`
- primero hay que reinterpretarlos con la lógica nueva de `file_acceptance`

## Decisión operativa

Para la certificación de `trades`:

1. usar `D full` para cuantificar el residuo grande
2. usar `file_acceptance` para poner semántica certificadora
3. no promocionar ni condenar buckets viejos enteros sin reinterpretación
