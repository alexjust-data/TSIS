# Raw 1m Schema-Only Lt1b Inspection Readout `v0_1`

## Rol

Este readout cierra visualmente la lectura del `5.89%` no-`vw` dentro del recalculo raw `1m <1B>`.

No reabre:

- la taxonomia `vw_*`;
- ni la auditoria de `ohlcv_1m_split_normalized`.

Hace una cosa mucho mas precisa:

- demostrar que `RESCUE_SCHEMA_ONLY` corresponde sobre todo a problemas de schema, lectura y compatibilidad estructural;
- y dejar un notebook interactivo para que el inspector pueda navegar cualquier caso del bloque.

## Artefactos

Script generador:

- [build_1m_schema_only_lt1b_inspection_notebook.py](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/inspection/minute/build_1m_schema_only_lt1b_inspection_notebook.py)

Notebook inspector:

- [raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_notebook_v0_1.ipynb)

Base cuantitativa:

- [raw_1m_lt1b_closeout_recalculation_v0_1.md](/C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md)
- `raw_1m_lt1b_filtered_closeout.parquet`
- `raw_1m_lt1b_bucket_summary.csv`
- `raw_1m_lt1b_exec_summary.csv`

## Que queda demostrado

### Masa total y peso del bloque

- masa total raw `1m <1B>`: `334660`
- masa `schema_only`: `19713`
- peso relativo: `5.890456%`

### Firma dominante

La firma dominante dentro de `schema_only` concentra:

- `18266` filas-mes
- `92.66%` del propio bloque `schema_only`

Y corresponde a:

- `dataset_read_incompatible_schema`
- `schema_merge_conflict_ticker_encoding`

## Lectura tecnica

Esto significa que el `5.89%` no aparece como una cola heterogenea de corrupciones arbitrarias.

Aparece sobre todo como:

- conflicto de lectura agregada del dataset;
- incompatibilidad de schema al mergear columnas o tipos;
- y, de forma secundaria, sparsity o `large_internal_gap_days`.

La consecuencia importante es esta:

- el bloque `schema_only` no queda rescatado porque este "limpio";
- queda rescatado porque su anomalia dominante es **estructural y homogénea**,
- y no una anomalia economica de `vw`.

## Como debe usarse el notebook

El notebook no depende de PNGs como interfaz principal.

El inspector puede seleccionar:

- firma de warning;
- ticker;
- `year-month`;

y ver para cualquier caso:

- metadatos del file-month;
- `rows_after_parse`;
- `active_days`;
- `coverage_ratio`;
- `vw_rows`;
- mensaje de error de lectura agregado;
- y la firma exacta de warning que justifica su pertenencia al bloque.

## Veredicto

Con este paquete, la afirmacion correcta queda cerrada asi:

- el problema dominante del raw `1m <1B>` sigue siendo `vw`;
- pero el `5.89%` fuera de `vw` tambien queda auditado visualmente;
- y su lectura correcta es:
  - problemas de schema,
  - problemas de lectura / compatibilidad estructural,
  - y conflictos de tipos o merge de columnas.
