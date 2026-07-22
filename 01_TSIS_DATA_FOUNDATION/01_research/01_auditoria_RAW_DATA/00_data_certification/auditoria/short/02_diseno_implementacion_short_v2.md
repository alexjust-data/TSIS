# Diseno e Implementacion Short v2

## Arquitectura

El bloque `short` se implementa en cuatro capas:

1. `build offline`
2. `artifacts/cache`
3. `notebook metodologico`
4. `closeout`

## Inputs

### Official baseline

- `C:\TSIS_Data\data\short_review\finra_short\artifacts\short_interest_all_biweekly_finra.parquet`
- `C:\TSIS_Data\data\short_review\finra_short\artifacts\short_volume_all_daily_finra.parquet`
- `C:\TSIS_Data\data\short_review\finra_short\normalized\short_interest\*.parquet`
- `C:\TSIS_Data\data\short_review\finra_short\normalized\short_volume\*.parquet`

### Provider paralelo

- `C:\TSIS_Data\data\short\short_interest\*.parquet`
- `C:\TSIS_Data\data\short\short_volume\*.parquet`

### Capas de apoyo

- universo `<1B>`
- `reference` auditado
- `halts` auditado
- artefactos de `quotes`, `trades`, `daily`, `ohlcv_1m`

## Builder

Archivo objetivo:

- `short\cell_code\build_short_audit_artifacts.py`

## Artefactos obligatorios

### Inventario y cobertura

- `short_provider_inventory.parquet`
- `short_interest_quality_summary.parquet`
- `short_volume_quality_summary.parquet`
- `short_provider_comparison_summary.parquet`
- `short_only_polygon_tickers.parquet`
- `short_only_finra_tickers.parquet`

### Integridad interna

- `short_interest_arithmetic_checks.parquet`
- `short_volume_arithmetic_checks.parquet`
- `short_volume_venue_consistency_checks.parquet`
- `short_zero_or_sparse_series.parquet`

### Identidad

- `short_identity_links.parquet`
- `short_possible_reuse_mix.parquet`
- `short_outside_life_window.parquet`

### Causal

- `short_volume_market_link_candidates.parquet`
- `short_volume_halt_link_candidates.parquet`
- `short_interest_market_context_candidates.parquet`
- `short_causal_alignment_summary.parquet`

## Notebook

Archivo objetivo:

- `short\03_short_root_cause_audit_notebook.ipynb`

Secciones esperadas:

1. snapshot ejecutivo
2. inventario y comparison `FINRA vs Polygon`
3. integridad de `short_interest`
4. integridad de `short_volume`
5. identidad y `ticker reuse`
6. cruces causales con mercado
7. viewer por caso
8. lectura final

## Viewer

Dos modos:

### Modo `short_volume`

Caso:

- `ticker + date`

Paneles:

- timeline del caso
- `quotes`
- `trades`
- `short_volume_ratio`
- breakdown por venue
- overlay de `halts` si aplica

### Modo `short_interest`

Caso:

- `ticker + settlement_date`

Paneles:

- serie `short_interest`
- `avg_daily_volume`
- `days_to_cover`
- precio diario / contexto temporal
- `halts` o eventos cercanos si aplica

## Politica de comparacion provider

### short_volume

La regla base es:

- `FINRA` manda en historico y trazabilidad official/free
- `Polygon` se evalua por:
  - filas extra
  - filas ausentes
  - fechas desplazadas
  - schema derivado

### short_interest

La regla base es:

- `FINRA` manda como baseline oficial
- `Polygon` puede conservar utilidad operacional, pero debe justificarse contra `FINRA`

## Criterio de cierre

`short` se considerara auditado al nivel del resto solo si quedan cerrados:

1. provider baseline definido y defendible
2. integridad aritmetica de ambos subdatasets
3. mapa de `ticker reuse` / identidad
4. cruces causales con mercado
5. politica `good / review / bad`
6. closeout final explicito
