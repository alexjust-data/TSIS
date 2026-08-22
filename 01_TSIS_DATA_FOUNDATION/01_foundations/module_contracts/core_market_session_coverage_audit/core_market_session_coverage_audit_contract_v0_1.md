# Core Market Session Coverage Audit Contract v0.1

## Objetivo

Inventariar, para los 4.824 tickers gobernados y `2005-01-01`–`2026-08-20`, qué fechas de sesión ET están presentes en `ohlcv_daily`, `ohlcv_1m`, `quotes_` y `trades_ticks_prod_2005_2026`.

## Autoridades

- La auditoría física fuente es `20260821_core_market_raw_alignment_audit_v0_1`.
- Daily usa `date`.
- Quotes usa su partición `year/month/day`, certificada como fecha de sesión.
- Trades usa su partición `day=YYYY-MM-DD` solo cuando la tarea fuente está `committed`.
- 1m deriva `session_date_et` desde `ts_utc` con `America/New_York`; su columna `date` UTC no es comparable directamente.

## Reglas no negociables

- Los RAW son read-only.
- `SOURCE_PENDING` no equivale a data ausente.
- Una ausencia observada no demuestra por sí sola un fallo del proveedor: se conserva separada de `gap_class` y `diagnostic_confidence`.
- Los resultados se escriben primero por ticker, con manifest y hash, y después se consolidan atómicamente.
- `Full` requiere autorización humana posterior a un probe production-equivalent PASS.

## Condición técnica de cierre

Todas las tareas seleccionadas deben estar `committed`, todos sus artefactos deben ser legibles y el manifest final debe enlazar sus hashes. La certificación material de las familias no se concede hasta adjudicar los huecos candidatos y las diferencias legítimas de producto.
