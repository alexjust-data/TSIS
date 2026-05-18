# Quotes Quality Policy

## Fuente canonica

La politica de calidad de `quotes` ya esta cerrada en:

- `auditoria\quotes\v2\04_quotes_full_C_D_closeout.md`

Y el marco para explicar residuos fuera de `quotes` ya esta en:

- `auditoria\05_crosswalk_multidataset.md`

## Politica vigente

No se cambia aqui.
La politica vigente es:

- `good`
- `review`
- `bad`

## Buckets

Segun el `closeout`, los buckets principales quedan asi:

- `good`
  - `clean_pass_or_other`
  - `soft_crossed_micro_noise`
  - `persistent_soft_crossed_low`
  - `utc_rollover_large_day_clean`
- `review`
  - `large_file_threshold_edge_hard_many_crosses`
  - `persistent_soft_crossed_mid_large_scale`
- `bad`
  - `high_hard_crossed_10_to_20`
  - `medium_file_threshold_edge_hard_many_crosses`

## Regla de lectura

Si un caso necesita explicacion transversal:

- primero manda la lectura local de `quotes`
- despues se contrasta con `halts`, `reference`, `news`, `ipos` y demas segun el `crosswalk`

Este documento no introduce estados nuevos ni reemplaza el criterio ya aprobado en `auditoria`.
