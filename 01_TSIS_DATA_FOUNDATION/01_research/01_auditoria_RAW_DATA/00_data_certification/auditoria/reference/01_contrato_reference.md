# Contrato de Auditoria Profunda para `reference`

## Objetivo

Fijar el contrato analitico de `reference` como bloque de identidad, existencia temporal, taxonomia de instrumento y corporate actions, para auditarlo con el mismo nivel de exigencia que `daily`, `ohlcv_1m`, `quotes`, `trades` y `halts`.

`reference` no responde como cotizo el mercado.

Responde:

- que era este ticker en una fecha concreta
- si ese instrumento existia realmente en esa fecha
- que tipo de instrumento era
- que corporate actions lo afectaron
- si esa capa de referencia explica o no lo visto despues en `daily`, `1m`, `quotes`, `trades` y `halts`

## Base real observada en `D:\reference`

La estructura actual ya materializada contiene:

- `overview`
- `all_tickers`
- `events`
- `splits`
- `dividends`
- `ticker_types`
- `exchanges`
- `_run`

Granularidad real observada:

- `overview`
  - un parquet por `ticker` y `request_date`
- `all_tickers`
  - un parquet por `snapshot_date`
- `events`
  - una fila por ticker con una lista `events` embebida
- `splits`
  - filas ya cercanas a evento individual
- `dividends`
  - requiere auditoria especifica de contenido real y no debe asumirse usable sin medirlo
- `_run`
  - contiene `audit.csv`, `errors.csv` y `progress.json`, que forman parte de la evidencia auditada

## Principio funcional

- `reference` es la capa de verdad de identidad y corporate actions.
- `daily`, `ohlcv_1m`, `quotes`, `trades` y `halts` son la evidencia de mercado.
- La auditoria de `reference` debe validar si el objeto financiero observado en mercado es el correcto y si los cambios corporativos explican lo que vemos en precios, prints, libro y halts.

## Unidades logicas auditadas

No existe una sola unidad.

Se auditan cuatro unidades distintas:

### 1. `identity_snapshot`

- `ticker + request_date`

Sirve para responder:

- que era este ticker en esa fecha
- si la respuesta `overview` es coherente
- si el instrumento es el correcto

### 2. `listing_snapshot`

- `ticker + snapshot_date`

Sirve para responder:

- si el ticker existia en esa fecha
- si estaba activo
- en que exchange estaba
- con que `type`

### 3. `reference_event`

- una fila por split, dividend o evento corporativo normalizado

Sirve para responder:

- que corporate action ocurrio
- cuando fue efectiva
- que mecanismo corporativo puede explicar discontinuidades de mercado

### 4. `reference_market_link`

- enlace entre `identity_snapshot` o `reference_event` y evidencia observada en mercado

Sirve para responder:

- si `reference` explica lo visto en `daily`, `1m`, `quotes`, `trades` o `halts`

## Rol de cada subdataset

### `overview`

Rol:

- verdad de identidad rica del instrumento en una fecha

Campos importantes observados:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `cik`
- `composite_figi`
- `share_class_figi`
- `market_cap`
- `sic_code`
- `sic_description`
- `ticker_root`
- `list_date`
- `round_lot`
- `request_date`

Preguntas:

- si el instrumento existe en esa fecha
- si es common, preferred, warrant, ADR, unit o similar
- si hay ambiguedad de identidad
- si un `404` implica ticker inexistente o ticker transitorio

### `all_tickers`

Rol:

- verdad de presencia temporal por snapshot

Campos importantes observados:

- `ticker`
- `name`
- `primary_exchange`
- `type`
- `active`
- `snapshot_date`
- `last_updated_utc`

Preguntas:

- si el ticker estaba listado en esa fecha
- si aparece con forma distinta
- si hay candidatos de remap o ticker base

### `events`

Rol:

- historia de eventos corporativos de identidad

Estado real observado:

- viene como una fila por ticker con una lista `events`

Consecuencia:

- la primera obligacion del builder es explotar `events` a granularidad de evento individual

Preguntas:

- si hay `ticker_change`
- si hay reestructuraciones relevantes
- si esos eventos explican discontinuidades o remaps

### `splits`

Rol:

- capa causal principal para explicar scale mismatches

Campos observados:

- `execution_date`
- `id`
- `split_from`
- `split_to`
- `ticker`

Preguntas:

- si el split es plausible
- si el ratio explica discontinuidades de precio o volumen
- si explica mismatches de escala en `trades`, `daily` o `1m`

### `dividends`

Rol:

- capa de corporate action suave

Estado real observado:

- debe auditarse con cautela
- un sample real puede venir practicamente vacio a nivel de columnas utiles

Consecuencia:

- no debe asumirse usable
- primero hay que medir si el contenido real de `dividends` esta poblado, vacio, truncado o mal normalizado

### `ticker_types`

Rol:

- taxonomia dura de instrumento

Ejemplos observados:

- `CS`
- `PFD`
- `WARRANT`

Preguntas:

- si el universo esta mezclando instrumentos heterogeneos
- si algunos errores de `reference` son en realidad errores de taxonomia

### `exchanges`

Rol:

- normalizacion de venues y exchanges

Campos utiles:

- `mic`
- `operating_mic`
- `participant_id`
- `acronym`
- `name`

Preguntas:

- si el listing del instrumento es coherente
- si algunos conflictos de identidad vienen por exchange

### `_run`

Rol:

- huella operativa auditada de la descarga

Archivos observados:

- `download_reference_universe_polygon.audit.csv`
- `download_reference_universe_polygon.errors.csv`
- `download_reference_universe_polygon.progress.json`

Preguntas:

- que endpoints fallan
- cuantos `404` hay
- que tickers o sufijos concentran fallos
- que parte del dataset esta vacia aunque exista el parquet

## Semantica de cobertura

La cobertura de `reference` no debe medirse solo como:

- ticker con archivo

Debe medirse como:

- `identity_snapshot` usable
- `listing_snapshot` usable
- `reference_event` usable
- `reference_market_link` explicativo

Un ticker puede tener:

- archivo existente
- pero identidad no resoluble
- o evento no explotado
- o dividend dataset vacio

Por tanto:

- existencia de parquet no equivale a cobertura analitica

## Preguntas que debe responder la auditoria

### Identidad

1. Si el ticker estaba correctamente identificado en la fecha consultada.
2. Si el instrumento era el correcto.
3. Si el `type` era consistente con el uso que hacemos del universo.
4. Si el `404` de `overview` indica ticker roto, ticker transitorio o instrumento no comparable.

### Existencia temporal

5. Si el ticker existia en `all_tickers` en la fecha esperada.
6. Si cambia de presencia, estado o forma a lo largo del tiempo.
7. Si hay candidatos de remap respaldados por snapshots y no solo por heuristica textual.

### Corporate actions

8. Si `events` debe explotarse y tipificarse mejor antes de usarse.
9. Si los `splits` son completos y plausibles.
10. Si `dividends` esta realmente poblado y es usable.
11. Si los corporate actions explican discontinuidades observadas en mercado.

### Cruce causal con mercado

12. Si un split explica mismatches de escala en `trades`, `daily` o `1m`.
13. Si un evento de `reference` explica un halt o una rareza microestructural.
14. Si una anomalia de mercado no explicada por `halts` si queda explicada por `reference`.
15. Si un problema aparente de `quotes/trades` es en realidad un problema de identidad mal resuelta.

### Calidad operativa

16. Si la descarga por endpoint es reproducible y trazable.
17. Si los errores de `_run` revelan patrones sistematicos por ticker o tipo de instrumento.

## Cruce obligatorio con otros bloques

`reference` debe cruzarse como minimo con:

- `daily`
- `ohlcv_1m`
- `quotes`
- `trades`
- `halts`

Cruces prioritarios:

### `splits` vs `trades / daily / 1m`

Objetivo:

- explicar scale mismatches
- explicar discontinuidades de precio
- explicar comparabilidad rota contra referencias agregadas

### `events` vs `halts / quotes / trades`

Objetivo:

- explicar dias con halts
- explicar anomalias microestructurales o administrativas
- explicar cambios de ticker o identidad

### `overview / all_tickers` vs residuos de identidad

Objetivo:

- detectar si el objeto observado en mercado era realmente el correcto

### `dividends` vs `daily`

Objetivo:

- validar cobertura real y posible capacidad explicativa sobre ajustes suaves

## Buckets de uso esperados

La auditoria debe poder clasificar snapshots, eventos y enlaces causales.

### Identidad

- `good_identity_snapshot`
- `review_transient_symbol`
- `review_instrument_type_ambiguity`
- `review_listing_state_conflict`
- `bad_unresolved_identity`

### Existencia temporal

- `good_snapshot_presence`
- `review_sparse_presence`
- `review_possible_remap`
- `bad_not_present_when_expected`

### Corporate actions

- `good_split_event`
- `review_split_scale_uncertain`
- `good_dividend_event`
- `review_dividend_empty_or_partial`
- `review_event_needs_explosion_cleanup`
- `bad_reference_event`

### Cruce causal

- `reference_explains_market_behavior`
- `reference_partially_explains_market_behavior`
- `reference_present_but_market_not_explained`
- `market_anomaly_without_reference_support`
- `review_timing_or_identity_conflict`

## Politica agregada esperada

Al final el bloque debe poder clasificarse como:

- `good_for_identity_and_corporate_action_overlay`
- `review_for_partial_reference_usage`
- `not_defensible_as_reference_truth`

## Regla de interpretacion

- Si `reference` identifica bien el instrumento y explica el evento de mercado, refuerza la validez del bloque completo.
- Si `reference` existe pero no explica el fenomeno, el caso entra en `review`.
- Si el mercado parece raro pero `reference` muestra split, ticker change o corporate action compatible, el problema puede no ser de data de mercado sino de comparabilidad o identidad.
- Si ni identidad ni corporate actions soportan el caso, el residuo queda abierto como conflicto real.

## Implicacion para la siguiente fase

Este contrato obliga a que la auditoria de `reference` no se limite a:

- coverage por endpoint
- conteo de archivos
- existencia de parquet

Debe llegar a:

- identidad temporal auditada
- eventos explotados a granularidad real
- corporate actions auditados
- cruce causal con mercado
- politica final `good / review / bad`
