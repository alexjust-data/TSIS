# Core Market Session Coverage Audit — Handoff v0.1

## Estado actual

La auditoría corregida está implementada y su probe production-equivalent está `PASS`. No se ha lanzado el Full.

Rutas operativas:

- runner: `01_TSIS_DATA_FOUNDATION/scripts/core_market_session_coverage_audit/audit_core_market_session_coverage.py`;
- wrapper: `run_core_market_session_coverage.ps1`;
- monitor: `monitor_core_market_session_coverage.ps1`;
- parada: `stop_core_market_session_coverage.ps1`;
- config: `01_TSIS_DATA_FOUNDATION/configs/core_market_session_coverage_audit_v0_1.yaml`;
- probe válido: `runs/data_ops/core_market_session_coverage_audit/20260822T135000Z_core_market_session_coverage_probe_v0_1`.

## Qué hace

Reutiliza la auditoría física ya cerrada de Daily, 1m y Quotes y las tareas Trades comprometidas. Solo vuelve a leer `ohlcv_1m.ts_utc` para derivar `session_date_et` con `America/New_York`.

Una tarea Trades pendiente queda `SOURCE_PENDING`; nunca se trata como ausencia. Si su estado cambia, el hash de snapshot invalida únicamente el checkpoint de ese ticker.

El auditor también expone por `ticker x family` los intervalos civiles
anteriores al primer dato y posteriores al último. Los llama `UNVERIFIED`
porque el calendario gobernado termina en 2026-03-09 y no resuelve por sí solo
listing/delisting hasta 2026-08-20.

## Por qué no iniciar Full todavía

En el snapshot de preparación, 1m y Quotes estaban completamente cerrados:

```text
ohlcv_1m: 4.824 tasks, 466.945 Parquets, 44.882.364.693 bytes, 0 errores
quotes_:  4.824 tasks, 7.764.906 Parquets, 596.582.660.375 bytes, 0 errores
```

Trades aún tenía miles de tareas pendientes. Ejecutar ahora produciría un cierre parcial y obligaría a releer 1m para cada ticker cuyo Trades pase posteriormente a `COMMITTED`. La ruta eficiente es esperar a `Trades committed = 4.824` y después pedir autorización humana del Full.

## Comando Full propuesto — no ejecutar sin autorización

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_session_coverage_audit\run_core_market_session_coverage.ps1" -Mode Full -RunId "20260822_core_market_session_coverage_audit_v0_1" -HumanAuthorizedFull -Detach
```

Monitor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_session_coverage_audit\monitor_core_market_session_coverage.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_session_coverage_audit\20260822_core_market_session_coverage_audit_v0_1" -Watch
```

Parada controlada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_session_coverage_audit\stop_core_market_session_coverage.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_session_coverage_audit\20260822_core_market_session_coverage_audit_v0_1"
```

Resume: repetir el comando Full con `-Resume`.

## Impacto esperado

- Lectura: exactamente `466.945` Parquets 1m / `44.882.364.693` bytes comprimidos; Daily, Quotes y Trades RAW no se releen.
- Escritura: solo manifests, shards de auditoría y cierres bajo `C:/TSIS_Data/runs`; presupuesto conservador `<5 GB`.
- Tiempo orientativo: `3–6 horas` en G:, dependiente de la contención con el worker Trades.
- Paralelismo: un lector secuencial 1m para no castigar el HDD; la aceleración vendrá de reutilizar los inventarios de las otras familias.

## Artefactos finales esperados

- `ohlcv_1m_session_dates_et.parquet`;
- `ticker_family_session_presence.parquet`;
- `family_gap_ledger.parquet`;
- `ticker_family_windows.parquet`;
- resúmenes CSV/JSON;
- `final_manifest.json`;
- `CORE_MARKET_SESSION_COVERAGE_AUDIT.md`.

El Full solo será `PASS` técnico con 4.824 tareas comprometidas y cero fallidas. La certificación material exige después adjudicar los huecos candidatos frente a diferencias legítimas de producto.
