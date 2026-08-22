# Core Market Session Coverage Audit — Probe Readout v0.1

## Veredicto

```text
PRODUCTION_EQUIVALENT_PROBE = PASS
FULL_RUN = NOT_STARTED
FULL_RUN_AUTHORITY = AWAIT_TRADES_SOURCE_CLOSEOUT_AND_HUMAN_AUTHORIZATION
```

Probe autoritativo:

`C:/TSIS_Data/runs/data_ops/core_market_session_coverage_audit/20260822T135000Z_core_market_session_coverage_probe_v0_1`

`final_manifest.json` SHA-256:

`016ED82FBC5135732B1A388F07C41240D3721792B2D71D5BCA828413F4FF77C6`

## Cobertura ejecutada

- Tickers: `RAD, YHOO, AAME, FCEL, ALTS, DJCO, NA`.
- Shards 1m leídos: `1.297`.
- Filas minuto leídas: `5.772.614`.
- Bytes fuente 1m: `183.600.059`.
- Fechas 1m ET: `24.637`.
- Filas de presencia: `26.876`.
- Ausencias observadas: `11.295`.
- Windows: `28`.
- Tareas físicas fuente con error: `0`.

Trades estaba `COMMITTED` para cuatro casos y `SOURCE_PENDING` para tres. Las presencias pendientes se escribieron como `NULL`; no generaron falsos huecos.

## Casos certificados

- Los rollovers UTC de `RAD 2005-02-12`, `YHOO 2006-11-04`, `AAME 2021-02-06`, `FCEL 2026-01-31` y `ALTS 2026-03-07` desaparecen como falsos días y mapean a la sesión ET anterior.
- `FCEL` tiene 24 sesiones posteriores a `2026-01-30` sin 1m; faltan los shards 1m de febrero y marzo de 2026. Clase: `DOWNLOAD_TAIL_MISSING`.
- `DJCO 2005-03-09` está en Daily y Quotes, falta en 1m aunque existe el shard mensual. Clase: `MISSING_INTRAMONTH_SESSION`; requiere reconciliación Massive antes de llamarlo omisión del proveedor.
- Las claves de los cuatro Parquets de cierre son únicas.
- Los hashes de runner, wrapper, monitor y parada están fijados en el pre-manifest.
- Ninguna familia del probe alcanza `2026-08-20`: 1m termina globalmente en
  `2026-03-09`; Daily, Quotes y los Trades disponibles terminan en
  `2026-03-06`. Las colas posteriores quedan explícitas como
  `UNVERIFIED_COMMON_TAIL`, no como sesiones faltantes inventadas.

## Incidentes heredables cerrados

1. PyArrow Dataset intentó inferir Hive bajo `ticker=...`; se sustituyó por `ParquetFile` y se añadió regresión.
2. El wrapper detached creaba `00_control` antes del runner; el gate ahora exige `-Resume` solo si existe `pre_manifest.json`.
3. `stop.requested` ahora se consume como `stop.acknowledged`, permitiendo reanudar.

Smoke de parada/reanudación:

`20260822T133500Z_core_market_session_coverage_stop_probe_v0_1`

Resultado: primera parada antes de leer; reanudación hasta 15 checkpoints; segunda parada con `15 committed`, `85 pending`, `0 failed` y artefactos conservados.

## Límite del veredicto

`observed absence` es un hecho local. `gap_class` es diagnóstico. Daily, 1m, Quotes y Trades no tienen obligación económica de producir evento todos los mismos días; las diferencias de producto no se promocionan silenciosamente a “data faltante”. El calendario institucional disponible termina en `2026-03-09`, por lo que los boundaries hasta agosto son intervalos civiles no verificados, no una lista de sesiones esperadas por ticker.
