# Core Market Family Download Audit Contract v0.1

Estado: `PROVISIONAL_READY_FOR_PRODUCTION_EQUIVALENT_PROBES`  
Owner: `01_TSIS_DATA_FOUNDATION`  
Scope: `ohlcv_daily`, `ohlcv_1m`, `quotes_`; 4.824 tickers; 2005-01-01 a 2026-08-20.

## Rol

Ejecutar tres auditorías independientes y reanudables. Cada familia usa su propio `run_id`, ledger SQLite, heartbeat, monitor, shards y manifest final. Daily y 1m se prueban primero; Quotes queda preparada para una segunda autorización.

## Evidencia física adoptada

El run cerrado `20260821_core_market_raw_alignment_audit_v0_1` ya abrió todos los Parquets y comprobó, archivo por archivo:

- tamaño mayor que cero;
- magic header y footer;
- metadata y schema legibles;
- al menos una fila;
- columnas requeridas completas.

El auditor nuevo valida el estado 4.824/4.824, los contadores cero-error y los SHA-256 de cada inventory/date shard. No vuelve a abrir millones de footers sin necesidad.

## Relojes y sesiones

- Daily: presencia de barra por fecha; no se inventa desglose intradía.
- 1m: `ts_utc` convertido a `America/New_York`.
- Quotes: `timestamp` nanosegundos UTC convertido a `America/New_York`.

Intervalos exactos:

```text
premarket   [04:00, 09:30)
RTH         [09:30, 16:00)
afterhours  [16:00, 20:00)
outside     resto del día ET
```

## Límites de certificación

Una fila presente y válida queda `PRESENT_VALID_FILE`. Una ausencia local no prueba una omisión de Massive. Sin ledger de solicitudes o autoridad lifecycle independiente, los límites y días no observados quedan `NOT_CERTIFIED_PROVIDER_EMPTY_UNRESOLVED`.

La comparación exacta entre familias se ejecutará después de cerrar las tres auditorías; no forma parte de un auditor familiar independiente.

## Gates

1. unit tests;
2. probe production-equivalent de cada familia con `AACT`, ticker literal `NA` y `MMMW`;
3. auditoría de los outputs del probe;
4. autorización humana separada para cada Full;
5. Full PASS solo con todas las tareas comprometidas, cero fallos y manifest final.

## Recovery

Cada ticker escribe shards privados de forma atómica. Tras caída de luz, repetir el mismo comando con `-Resume`; los shards comprometidos se validan por hash y no se recalculan. Nunca se escribe en G:.

