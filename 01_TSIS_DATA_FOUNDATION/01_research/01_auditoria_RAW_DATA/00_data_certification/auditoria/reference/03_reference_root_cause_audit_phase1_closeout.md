# Reference Phase 1 Closeout

## Rol de esta fase

Esta fase cierra la auditoría estructural de `reference` sobre el contenido real de `D:\reference`, antes de entrar en el cruce causal con `daily`, `ohlcv_1m`, `quotes`, `trades` y `halts`.

El objetivo aquí no es todavía explicar fenómenos de mercado, sino fijar:

- qué endpoints existen y con qué cobertura real,
- qué granularidad trae cada subdataset,
- qué parte de `reference` es usable ya como identidad temporal,
- qué residuos duros o bloques vacíos siguen abiertos.

## Artefactos generados

Builder:

- [build_reference_audit_artifacts.py](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cell_code\build_reference_audit_artifacts.py)

Cache:

- [cache_v2](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2)

Loader:

- [00_load_reference_audit_artifacts.py](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cell_code\00_load_reference_audit_artifacts.py)

## Foto general de cobertura

Del `_run/download_reference_universe_polygon.audit.csv` sale esta lectura:

- `overview`: `12,468` requests, `12,243` `ok`, `200` errores, `25` `resume-skip`
- `events`: `12,468` requests, `12,443` `ok`, `6,250` con `http_status=404`
- `splits`: `12,468` requests, `12,443` `ok`
- `dividends`: `12,468` requests, `12,443` `ok`
- `all_tickers`: `3,109` snapshots, `3,032` `ok`

Dos matices importantes:

- `events` usa `404` como semántica de “no events”, no como corrupción dura del dataset.
- `ticker_types` y `exchanges` aparecen como `resume-skip` en el audit log; no son fallos funcionales del bloque.

## Identidad temporal: `overview`

`reference_identity_snapshot.parquet` quedó en `12,468` filas.

Buckets actuales:

- `good_identity_snapshot`: `12,093` filas, `96.99%`
- `bad_unresolved_identity`: `200` filas, `1.60%`
- `review_transient_symbol`: `175` filas, `1.40%`

Lectura:

- La gran mayoría del universo sí queda bien resuelta como snapshot de identidad.
- El residuo `bad_unresolved_identity` coincide con los `200` `overview 404` del downloader.
- La primera heurística de “símbolo transitorio” era demasiado agresiva; se corrigió para no marcar tickers legítimos como `ABR`, `ACHR` o `ACMR` solo por acabar en `R`.

### `overview 404`

Se separó en artefactos propios:

- [reference_overview_404_case_index.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_overview_404_case_index.parquet)
- [reference_overview_404_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\reference\cache_v2\reference_overview_404_summary.parquet)

Resumen:

- `review_overview_404_w_suffix`: `186`
- `review_overview_404_punctuation`: `7`
- `review_overview_404_other`: `7`

Conclusión:

- los `404` de `overview` están dominados por símbolos con sufijo `W`,
- los casos con puntuación existen pero son minoritarios,
- este bloque ya no debe leerse como “overview está roto”, sino como un residuo muy concentrado y entendible.

## Existencia temporal: `all_tickers`

`reference_listing_snapshots.parquet` quedó en `12,977,501` filas y `reference_listing_snapshot_summary.parquet` en `13,124` tickers.

Esta capa ya sirve como verdad de presencia temporal:

- primer snapshot observado,
- último snapshot observado,
- estabilidad de `exchange`,
- estabilidad de `type`,
- densidad temporal por ticker.

Lectura:

- `all_tickers` está muy por encima del nivel de simple inventario.
- ya puede actuar como capa fuerte para validar si un ticker estaba vivo en una fecha y si estaba listado bajo la forma esperada.

## Taxonomía de instrumento

De momento, sobre el universo efectivamente descargado, domina `CS`.

Resumen actual:

- `type=CS`: `12,268` filas en `overview`
- `type=None`: `200` filas, que son exactamente el residuo `overview 404`

Esto no significa que la taxonomía de instrumento sea irrelevante. Significa:

- en esta primera fase, el problema principal no es mezcla de `type`,
- el problema principal es identidad resuelta vs no resuelta, y símbolos especiales.

## `events`

Aquí hubo un hallazgo importante durante la construcción:

- el parquet no trae una fila por evento,
- trae una fila por ticker con una columna `events` como `ndarray` de dicts.

Eso ya quedó corregido en `reference_events_exploded.parquet`.

Foto actual:

- `ok_event / ticker_change`: `6,953` filas, `6,206` tickers
- `empty_events_payload`: `6,262` filas, `6,262` tickers

Conclusión:

- `events` sí aporta señal real,
- hoy esa señal es casi enteramente `ticker_change`,
- media base del universo no trae eventos útiles en este endpoint,
- por tanto `events` parece más capa de cambios de identidad que capa amplia de corporate actions ricas.

## `splits`

`reference_split_case_index.parquet` quedó en `14,909` filas.

Buckets actuales:

- `good_split_event`: `5,902`
- `review_no_split_payload`: `9,007`

Lectura:

- `splits` sí tiene una base real de eventos utilizables,
- pero también tiene muchísimos placeholders vacíos por ticker,
- esos placeholders no deben leerse como “split dudoso”, sino como “ticker sin split payload”.

Esto es importante para la fase causal:

- `splits` ya parece bastante fuerte para explicar `scale mismatch`,
- pero no debe medirse por `% de tickers con fila`, sino por `% de filas con payload real`.

## `dividends`

El sample inicial de `dividends_A.parquet` sugería que `dividends` podía estar vacío. Esa lectura ya quedó corregida.

`reference_dividend_case_index.parquet` quedó en `273,799` filas.

Buckets actuales:

- `good_dividend_event`: `266,586`
- `review_no_dividend_payload`: `7,213`

Conclusión:

- `dividends` sí trae payload masivo y usable,
- el problema no es “dataset vacío”,
- el residuo real es un subconjunto de placeholders por ticker sin evento.

Esto cambia bastante la prioridad del bloque:

- `dividends` ya no es foco rojo,
- `events` y la identidad temporal son hoy más importantes que `dividends`.

## Universo `<1B>`

La fase 1 ya está cruzada contra el universo operativo `<1B>` ya establecido en la auditoría general.

Ejemplos:

- `lt1b_rows` en identidad, splits y dividends
- `in_lt1b_universe` por fila en snapshots, eventos y placeholders

Esto no redefine el universo; solo alinea `reference` con el contrato operativo ya usado en `quotes`, `trades` y `halts`.

## Residuos realmente abiertos

Después de esta fase, los residuos que siguen mereciendo trabajo son estos:

1. `overview 404`

- ya está acotado,
- pero falta usar `all_tickers` y mercado para decidir remap, exclusión o aceptación.

2. `review_transient_symbol`

- ya no está inflado por falsos positivos obvios,
- pero aún mezcla share classes, ADR temporales, units históricas y símbolos con puntuación.

3. `events`

- está explotado y entendido,
- pero hoy casi todo es `ticker_change`;
- falta medir cómo enlaza eso con `halts` y con discontinuidades de mercado.

4. `splits`

- fuerte a nivel estructural,
- falta el cruce causal contra `daily`, `ohlcv_1m` y `trades`.

5. `dividends`

- estructuralmente mucho mejor de lo esperado,
- falta decidir cuánto valor causal añade realmente al resto del pipeline.

## Decisión de fase 1

`reference` ya supera la fase de simple documentación operativa.

Con esta cache actual:

- `overview` es usable como capa de identidad temporal, con un residuo `404` ya aislado,
- `all_tickers` es usable como capa fuerte de presencia temporal,
- `events` ya quedó normalizado a granularidad de evento,
- `splits` es usable como bloque serio para causalidad futura,
- `dividends` es usable y no está vacío, contra la sospecha inicial.

Estado final de esta fase:

- `reference` queda listo para fase 2: cruce causal con mercado.
