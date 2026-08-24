# Core Market Family Download Audit

Readouts y evidencia de las auditorías independientes de descarga para
`ohlcv_daily`, `ohlcv_1m` y `quotes_`.

## Documentos

- `DAILY_1M_PROBE_CERTIFICATION_v0_1.md`: gate production-equivalent previo a
  los runs Full.
- `OHLCV_1M_FULL_AUDIT_READOUT_v0_1.md`: cierre reproducible del run Full 1m,
  interpretación de los 5.238 ticker-fecha sin RTH, forense cruzado que aísla
  ocho candidatos locales de alta confianza, muestra 2025/2026, limitación
  temporal hasta 2026-08-20 y decisión de no reparar hasta disponer de Trades
  completo y de las entradas reales del screener diario.

## Código

El código reproducible vive en:

`C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/core_market_family_download_audit/`

Los artefactos pequeños del cierre 1m viven en:

`evidence_assets/ohlcv_1m_full_audit_v0_1/`

El RAW y los runs cerrados permanecen inmutables.

La ruta operativa congelada es: completar Trades y SEC PIT, ejecutar el
screener diario, cruzar solo sus seleccionados con las incidencias 1m y
reconstruir desde Trades una vista derivada únicamente cuando sea necesario.

