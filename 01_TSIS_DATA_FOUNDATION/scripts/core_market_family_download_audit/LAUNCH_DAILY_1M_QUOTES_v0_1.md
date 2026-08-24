# Lanzamiento Daily, 1m y Quotes v0.1

## Estado

```text
Daily probe: pendiente
1m probe: pendiente
Quotes probe: preparado, no lanzar todavía
Full: requiere probe PASS y autorización humana explícita
```

## Probes

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family ohlcv_daily -Mode Probe -RunId "20260823_ohlcv_daily_download_audit_probe_v0_1"

powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family ohlcv_1m -Mode Probe -RunId "20260823_ohlcv_1m_download_audit_probe_v0_1"
```

## Full Daily y 1m — no ejecutar antes del gate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family ohlcv_daily -Mode Full -RunId "20260823_ohlcv_daily_download_audit_v0_1" -HumanAuthorizedFull -Detach

powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family ohlcv_1m -Mode Full -RunId "20260823_ohlcv_1m_download_audit_v0_1" -HumanAuthorizedFull -Detach
```

Monitores:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\monitor_family_download_audit.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_family_download_audit\20260823_ohlcv_daily_download_audit_v0_1" -Watch

powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\monitor_family_download_audit.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_family_download_audit\20260823_ohlcv_1m_download_audit_v0_1" -Watch
```

Parada: sustituir el script de monitor por `stop_family_download_audit.ps1` y conservar `-RunRoot`. Resume: repetir el comando original con `-Resume`.

## Quotes — preparada para después

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_family_download_audit\run_family_download_audit.ps1" -Family quotes_ -Mode Probe -RunId "20260823_quotes_download_audit_probe_v0_1"
```

No lanzar Quotes Full hasta revisar su probe y el impacto de abrir 7.764.906 archivos.

