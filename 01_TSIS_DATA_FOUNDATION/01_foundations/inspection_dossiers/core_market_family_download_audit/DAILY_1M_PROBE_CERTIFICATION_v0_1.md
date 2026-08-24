# Daily and 1m Production-Equivalent Probe Certification v0.1

Fecha: 2026-08-23  
Estado: `PASS_DAILY_AND_1M`; `QUOTES_NOT_RUN`

## Código y scope

Mismo runner, wrapper, ledger, workers, writer, finalizador y ruta de manifest previstos para Full. Tickers: `AACT`, literal `NA`, `MMMW`.

## Daily

- 3/3 tareas committed; cero fallos.
- 14 Parquets y 2.327 filas/fechas adoptadas desde la auditoría física cerrada.
- SHA-256 de evidencia verificados.
- desglose intradía correctamente `NULL`, no fabricado.

Run: `C:/TSIS_Data/runs/data_ops/core_market_family_download_audit/20260823_ohlcv_daily_download_audit_probe_v0_1`.

## 1m

- 3/3 tareas committed; cero fallos.
- 125 Parquets; 102.750 filas leídas y reconciliadas contra metadata.
- 9.483 premarket, 88.624 RTH, 4.643 after-hours, 0 fuera de 04:00-20:00.
- cero timestamps inválidos y cero filas perdidas.
- fechas ET coinciden exactamente con el auditor anterior para los tres tickers.

Run: `C:/TSIS_Data/runs/data_ops/core_market_family_download_audit/20260823_ohlcv_1m_download_audit_probe_v0_1`.

## Gate

Daily y 1m están técnicamente preparados para Full. El contrato de operaciones largas exige que el humano lance o autorice expresamente esos Full después de recibir comandos, impacto, monitor y parada. Quotes conserva su gate independiente pendiente.

