# Diseno Implementacion Additional v2

## Objetivo

Construir una auditoría profunda y reproducible para `additional`, separando explícitamente subbloques heterogéneos y evitando mezclar:

- datasets ticker-based de fundamentals
- datasets ticker-based de eventos
- datasets de noticias
- datasets macro no ticker-based

El patrón operativo será el mismo que en `halts`, `reference` y `short`:

- contrato
- builder offline
- cache de artefactos
- notebook metodológico
- closeout estructural
- closeout causal
- closeout final

## Raíces de entrada

### Data

- `C:\TSIS_Data\data\additional`

Subroots:

- `corporate_actions`
- `economic`
- `financials`
- `ipos`
- `news`

### Universo

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet`

### Artefactos previos reutilizables

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_audit\20260405_additional_lt1b_coverage\additional_ticker_datasets_summary.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_audit\20260405_additional_lt1b_coverage\additional_ticker_datasets_by_file.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_audit\20260405_additional_lt1b_coverage\additional_macro_datasets_summary.parquet`

### Cruces posteriores

- `halts/cache_v2`
- `reference/cache_v2`
- `short/cache_v2`
- `quotes_current.parquet`
- `trades_current.parquet`
- raw `ohlcv_daily`

## Restricciones técnicas

### 1. No usar lectura dataset-merge ciega

Se observaron conflictos de schema del tipo:

- `Field ticker has incompatible types: string vs dictionary...`

Por tanto:

- el builder debe leer archivo físico individual
- no debe depender de `dataset` merge a nivel de carpeta

### 2. Placeholders vacíos son semántica válida

Muchos parquets ticker-based traen:

- `ticker`
- `_empty`
- `_dataset`
- `_ingested_utc`

Eso significa:

- ausencia natural de dato para ese ticker
- no necesariamente error de descarga

Por tanto:

- `files_present` no es métrica de utilidad
- la métrica útil es `files_non_empty`

## Fases del builder

## Fase 1. Inventario estructural

Objetivo:

- consolidar cobertura efectiva por dataset
- reusar la auditoría `068`
- normalizar el lenguaje de subbloques

Artefactos:

- `additional_build_manifest.json`
- `additional_dataset_inventory.parquet`
- `additional_effective_coverage_summary.parquet`
- `additional_family_summary.parquet`
- `additional_macro_summary.parquet`

## Fase 2. Schema y shape real

Objetivo:

- tomar una muestra no vacía representativa por dataset
- fijar columnas reales, densidad y forma del dato

Artefactos:

- `additional_schema_samples.parquet`
- `additional_dataset_column_presence.parquet`

Campos a resumir:

- `dataset`
- `sample_file`
- `sample_rows`
- `columns`
- `has_empty_flag`
- `has_array_fields`
- `has_nested_object_fields`

## Fase 3. Subbloques estructurales

### `financials_core`

Artefactos:

- `additional_financials_summary.parquet`
- `additional_financials_timeframe_summary.parquet`
- `additional_financials_ticker_span_summary.parquet`

Preguntas:

- cobertura efectiva real
- timeframes presentes
- longitud temporal por ticker
- sparsity de columnas

### `financials_ratios`

Artefactos:

- `additional_ratios_summary.parquet`
- `additional_ratios_case_index.parquet`

Preguntas:

- si la escasez es natural del endpoint
- si los no vacíos traen estructura útil o no

### `news`

Artefactos:

- `additional_news_summary.parquet`
- `additional_news_ticker_density.parquet`
- `additional_news_date_density.parquet`
- `additional_news_publisher_summary.parquet`
- `additional_news_multi_ticker_summary.parquet`

Preguntas:

- cobertura
- densidad por ticker
- densidad temporal
- peso de artículos multi-ticker
- peso de publishers dominantes

### `ipos`

Artefactos:

- `additional_ipos_summary.parquet`
- `additional_ipos_case_index.parquet`

Preguntas:

- cobertura real
- si el dato útil es efectivamente escaso y estructural

### `corporate_actions_additional`

Artefactos:

- `additional_corporate_actions_summary.parquet`
- `additional_splits_summary.parquet`
- `additional_dividends_summary.parquet`
- `additional_ticker_events_summary.parquet`

Preguntas:

- cuántos eventos útiles hay
- si el valor incremental frente a `reference` es material o no

### `economic`

Artefactos:

- `additional_macro_calendar_summary.parquet`
- `additional_macro_missingness_summary.parquet`

Preguntas:

- cobertura temporal
- densidad
- missingness por serie

## Fase 4. Causal overlay

Solo para subbloques que de verdad lo merecen.

### `news`

Cruces:

- `news` vs `halts`
- `news` vs `quotes`
- `news` vs `trades`
- `news` vs `short`

Artefactos esperados:

- `additional_news_market_link_candidates.parquet`
- `additional_news_halt_link_candidates.parquet`

### `ipos`

Cruces:

- `ipos` vs `daily`
- `ipos` vs `quotes/trades`
- `ipos` vs `reference`

Artefactos:

- `additional_ipo_market_link_candidates.parquet`

### `corporate_actions_additional`

Cruces:

- principalmente contra `reference`
- secundariamente contra mercado

Artefactos:

- `additional_corp_actions_reference_overlap.parquet`
- `additional_corp_actions_market_link_candidates.parquet`

### `economic`

Cruces:

- calendario macro vs días de anomalía agregada de mercado

Artefactos:

- `additional_macro_market_context_candidates.parquet`

## Notebook

Archivo:

- `03_additional_root_cause_audit_notebook.ipynb`

Secciones:

1. snapshot ejecutivo
2. cobertura efectiva
3. schema y shape real
4. financials core
5. ratios
6. news
7. ipos
8. corporate actions additional
9. economic
10. lectura causal
11. conclusiones

## Viewer

No hace falta arrancar con un viewer único universal.

Prioridad:

1. `news viewer`
2. `ipos viewer`
3. `macro overlay` si aporta algo

No priorizar:

- viewer para `financials_core`
- viewer para `ratios`

## Criterio de cierre

`additional` se cierra si:

- queda clara la separación de subbloques
- queda claro qué parte es fuerte y cuál es meramente contextual
- queda explicitada la redundancia parcial con `reference`
- queda fijada política `good / review / bad` por subbloque

La decisión final será una agregación jerárquica:

- fuerte:
  - `financials_core`
  - parte de `news`
  - `economic` como dataset
- intermedio/review:
  - `ratios`
  - `ipos`
  - `corporate_actions_additional`
  - parte de `news`
