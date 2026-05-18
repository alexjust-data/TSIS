# Trades | Política certificadora provisional

Esta política no rediseña la auditoría. Solo traduce lo ya sostenido por `05_trades_file_acceptance_notebook.md` a una regla operativa provisional de certificación.

Rutas base:

- [05_trades_file_acceptance_notebook.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\v2\05_trades_file_acceptance_notebook.md)
- [layer6_policy_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b\layer6_policy_summary.parquet)
- [layer6_policy_examples.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b\layer6_policy_examples.parquet)

## Regla base

Para certificación de `trades`, los labels de `file_acceptance` deben leerse así:

- `reference_scale_mismatch`
  - no es `bad_data`
  - queda como `review` explicable por escala
- `review_microstructure`
  - queda como `review`
  - dominante en odd-lots y comparabilidad difícil
- `review_no_1m_reference`
  - queda como `review`
  - conflicto con `daily`, pero sin confirmación `1m`
- `review_1m_reference_alignment`
  - queda como `review`
  - bucket pequeño pero específico
- `review`
  - queda como `review`
  - no debe leerse como limpio
- `bad_data`
  - queda como `bad`
  - salvo fuga puntual de escala extrema que conviene vigilar
- `good`
  - sería `good`
  - pero en el estado observado es prácticamente inexistente

## Traducción provisional a certificación

### `good`

Solo puede entrar aquí:

- `good`

Estado actual:

- todavía no hay base para promover `review` a `good` por defecto
- la muestra `<1B>` observada en `layer6_policy_summary.parquet` no trae bucket `good`
- en el material final de `57f/full_clean_fast_same_schema`, `good` existe pero sigue siendo residual

## `review`

Entran aquí de forma provisional:

- `reference_scale_mismatch`
- `review_microstructure`
- `review_no_1m_reference`
- `review_1m_reference_alignment`
- `review`

Razón:

- la propia auditoría de `05` sostiene que el problema dominante observado no parece mala calidad intrínseca del tape
- parece comparabilidad imperfecta contra `daily` y `1m`

## `bad`

Entra aquí de forma provisional:

- `bad_data`

Salvedad:

- conviene vigilar la fuga residual de escala extrema dentro de `bad_data`
- pero eso no justifica vaciar el bucket ni promoverlo entero

## Decisión práctica

La política provisional de certificación de `trades` queda así:

1. no usar `D full` viejo directamente como política final
2. usar `file_acceptance` como semántica principal
3. tratar casi todo el residuo explicado como `review`, no como `bad`
4. reservar `bad` para `bad_data`
5. no inflar `good` hasta que exista evidencia suficiente en el run full canónico

## Lo que sigue abierto

Antes de cerrar `trades` de forma definitiva todavía queda:

1. decidir si `review_1m_reference_alignment` merece bucket propio final o se absorbe en `review`
2. decidir si una parte de `review` simple puede promoverse a `good`
3. usar como estado final canonico `57f/full_clean_fast_same_schema` y dejar `57e` documentado solo como run parcial historico
