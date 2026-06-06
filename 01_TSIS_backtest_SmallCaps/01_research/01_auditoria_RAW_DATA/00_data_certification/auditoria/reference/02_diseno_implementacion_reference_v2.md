# Diseno de implementacion `reference v2`

## Objetivo

Llevar `reference` a un patron de auditoria profunda comparable a `daily`, `ohlcv_1m`, `quotes`, `trades` y `halts`.

El bloque debe cerrar:

- identidad temporal del instrumento
- existencia real por fecha
- taxonomia de instrumento
- corporate actions
- calidad operativa de la descarga
- cruce causal con mercado

## Regla arquitectonica

- Jupyter no debe releer recursivamente todo `D:\reference`.
- Jupyter no debe explotar listas pesadas ni rehacer joins causales.
- El trabajo pesado debe quedar en un builder offline.
- El notebook debe consumir artefactos pequenos, ya normalizados y listos para auditoria.

## Estructura objetivo

- `reference/01_contrato_reference.md`
- `reference/02_diseno_implementacion_reference_v2.md`
- `reference/cell_code/build_reference_audit_artifacts.py`
- `reference/03_reference_root_cause_audit_notebook.ipynb`
- `reference/04_reference_causal_overlay_closeout.md`
- `reference/04_reference_closeout.md`

## Inputs reales

- `D:\reference\overview\...`
- `D:\reference\all_tickers\...`
- `D:\reference\events\...`
- `D:\reference\splits\...`
- `D:\reference\dividends\...`
- `D:\reference\ticker_types\ticker_types.parquet`
- `D:\reference\exchanges\exchanges.parquet`
- `D:\reference\_run\download_reference_universe_polygon.audit.csv`
- `D:\reference\_run\download_reference_universe_polygon.errors.csv`
- universo canonico `<1B>`
- artefactos clave ya cerrados de:
  - `daily`
  - `ohlcv_1m`
  - `quotes`
  - `trades`
  - `halts`

## Builder offline

Script objetivo:

- `reference/cell_code/build_reference_audit_artifacts.py`

Responsabilidades:

1. Inventariar la estructura real de `D:\reference`.
2. Resumir calidad operativa por endpoint.
3. Normalizar `overview` a unidad `identity_snapshot`.
4. Normalizar `all_tickers` a unidad `listing_snapshot`.
5. Explotar `events` a granularidad `reference_event`.
6. Auditar `splits`.
7. Auditar `dividends`.
8. Materializar taxonomia de instrumento.
9. Cruzar identidad y eventos con mercado.
10. Escribir artefactos ligeros para notebook y viewer.

## Fases del builder

## Fase 0. Inventario y run audit

Objetivo:

- medir cobertura fisica y huella del downloader

Salidas esperadas:

- conteo de archivos por endpoint
- suma de filas por endpoint cuando aplique
- resumen de `_run/audit.csv`
- resumen de `_run/errors.csv`
- ratios de `200/404/otros`
- patrones de error por ticker y por sufijo

## Fase 1. Identidad temporal

Objetivo:

- construir `identity_snapshot`

Unidad:

- `ticker + request_date`

Fuente:

- `overview`

Campos importantes:

- `ticker`
- `name`
- `market`
- `primary_exchange`
- `type`
- `active`
- `ticker_root`
- `cik`
- `composite_figi`
- `share_class_figi`
- `market_cap`
- `sic_code`
- `sic_description`
- `list_date`
- `round_lot`
- `request_date`

Validaciones:

- nulls criticos
- duplicados por `ticker + request_date`
- conflictos de identidad en el tiempo
- cambios de `type`
- cambios de exchange
- instrumentos que responden 200 pero siguen siendo dudosos

## Fase 2. Presencia temporal

Objetivo:

- construir `listing_snapshot`

Unidad:

- `ticker + snapshot_date`

Fuente:

- `all_tickers`

Validaciones:

- presencia / ausencia por fecha
- continuidad temporal
- cambios de `active`
- cambios de `type`
- cambios de exchange
- posible ticker base / remap candidato

## Fase 3. Taxonomia de instrumento

Objetivo:

- separar instrumentos que no deben tratarse igual

Fuentes:

- `overview`
- `all_tickers`
- `ticker_types`

Buckets esperados:

- `common_stock`
- `preferred`
- `warrant`
- `unit`
- `right`
- `adr_or_foreign`
- `transient_or_review`
- `unknown_type`

Uso:

- limpiar interpretaciones falsas de `reference`
- explicar parte de los `404` y de los remaps

## Fase 4. Events

Objetivo:

- explotar la lista embebida `events`

Problema real observado:

- `events` no viene fila por evento
- viene una fila por ticker con una lista `events`

Accion obligatoria:

- explotar cada lista a una fila por evento

Unidad final:

- `reference_event`

Campos esperados:

- `ticker`
- `event_type`
- `event_date`
- `event_payload_raw`
- `ticker_change_target` si aplica
- `composite_figi`
- `cik`

Validaciones:

- tipos de evento presentes
- cobertura por ticker
- fechas nulas
- eventos duplicados
- ticker changes

## Fase 5. Splits

Objetivo:

- validar la capa mas fuerte de corporate actions para mercado

Unidad:

- `split_event = ticker + execution_date`

Campos:

- `execution_date`
- `split_from`
- `split_to`
- `id`
- `ticker`

Validaciones:

- ratios plausibles
- duplicados
- gaps de cobertura
- fecha usable

Cruce obligatorio:

- contra `daily`
- contra `ohlcv_1m`
- contra `trades`
- y en menor nivel contra `quotes`

## Fase 6. Dividends

Objetivo:

- demostrar primero si la capa es real y usable

Problema real observado:

- un sample puede venir con columnas practicamente vacias

Accion obligatoria:

- medir schema real en muchos tickers
- detectar si hay estructura anidada, vacia o perdida
- separar:
  - dataset vacio legitimo
  - parquet placeholder
  - normalizacion incompleta

Cruce posterior:

- solo si la capa demuestra contenido suficiente
- principalmente contra `daily`

## Fase 7. Cruce causal con mercado

Objetivo:

- medir si `reference` explica fenomenos de mercado

Cruces obligatorios:

### A. `overview / all_tickers` vs identidad de mercado

Responder:

- si el ticker en mercado era el correcto
- si el instrumento observado era realmente comparable

### B. `splits` vs `daily / 1m / trades`

Responder:

- si un split explica scale mismatch
- si explica discontinuidad de precio
- si explica conflicto de comparabilidad

### C. `events` vs `halts / quotes / trades`

Responder:

- si un evento corporativo explica un halt
- si explica rarezas microestructurales o administrativas

### D. `dividends` vs `daily`

Responder:

- si hay capacidad explicativa para ajustes suaves

## Artefactos esperados

### Inventario y run audit

- `reference_endpoint_inventory.parquet`
- `reference_download_audit_summary.parquet`
- `reference_download_error_summary.parquet`
- `reference_schema_summary.parquet`

### Identidad y presencia temporal

- `reference_identity_snapshot.parquet`
- `reference_identity_quality_summary.parquet`
- `reference_identity_case_index.parquet`
- `reference_listing_snapshot_summary.parquet`
- `reference_ticker_presence_timeline.parquet`
- `reference_snapshot_presence_gaps.parquet`
- `reference_remap_candidates.parquet`
- `reference_transient_symbol_review.parquet`

### Taxonomia de instrumento

- `reference_instrument_type_summary.parquet`
- `reference_exchange_summary.parquet`

### Corporate actions

- `reference_events_exploded.parquet`
- `reference_event_type_summary.parquet`
- `reference_splits_summary.parquet`
- `reference_split_case_index.parquet`
- `reference_dividends_summary.parquet`
- `reference_dividend_case_index.parquet`

### Cruce causal

- `reference_overview_market_identity_links.parquet`
- `reference_split_market_link_candidates.parquet`
- `reference_event_halt_link_candidates.parquet`
- `reference_event_quotes_trades_link_candidates.parquet`
- `reference_dividend_daily_link_candidates.parquet`
- `reference_causal_alignment_summary.parquet`

### Viewer

- `reference_visual_cases.parquet`

## Notebook metodologico

`03_reference_root_cause_audit_notebook.ipynb` debe responder:

1. Que parte de `reference` esta estructuralmente sana.
2. Que parte de `overview` y `all_tickers` resuelve bien identidad temporal.
3. Que parte de los `404` es ruido estructural de instrumentos transitorios.
4. Si `events` esta explotado y utilizable.
5. Si `splits` explica scale mismatches observados en mercado.
6. Si `dividends` es realmente usable o no.
7. Que parte de `reference` explica fenomenos en `halts`, `quotes` y `trades`.

## Criterio de cierre

`reference` solo debe considerarse auditado al nivel de los otros bloques si al final existen:

- contrato formal
- builder reproducible
- artefactos reutilizables
- notebook metodologico
- closeout causal
- closeout final
- politica `good / review / bad`

## Politica esperada final

La politica final debe poder separar:

### `good`

- identidad resuelta
- presencia temporal coherente
- split o evento que explica bien el mercado

### `review`

- remap posible
- instrumento ambiguo
- dividend dataset parcial
- evento util pero no concluyente
- referencia presente pero explicacion causal parcial

### `bad`

- identidad no resoluble
- ticker no presente cuando deberia
- corporate action inutilizable
- conflicto fuerte entre `reference` y mercado sin explicacion mejor

## Orden de ejecucion recomendado

1. implementar builder base
2. cerrar inventario y `_run`
3. cerrar identidad temporal
4. explotar `events`
5. cerrar `splits`
6. validar `dividends`
7. materializar cruces causales
8. montar notebook
9. cerrar politica final
