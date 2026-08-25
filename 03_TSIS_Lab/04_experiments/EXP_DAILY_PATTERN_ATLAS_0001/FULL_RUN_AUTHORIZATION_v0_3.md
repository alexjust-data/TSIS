# Full Run Authorization v0.3

Fecha: 2026-08-25
Estado: `PASS_FULL_AUTHORIZED_AWAITING_HUMAN_LAUNCH`
Experimento: `EXP_DAILY_PATTERN_ATLAS_0001`
Probe autorizante: `20260825_probe_raw_daily_v0_2`
Implementación autorizada: commit `bf4d0fb4e454a70bb8018302104121bfb48c59bf`

## Corrección semántica

El full previo `20260825_full_v0_1` queda invalidado científicamente porque leyó
`ohlcv_daily_adjusted` y aplicó por segunda vez splits sobre datos Massive ya
obtenidos con `adjusted=true`. Esta autorización consume exclusivamente
`G:/TSIS/data/ohlcv_daily`; `o_split_normalized/h/l/c` son alias directos de
`o/h/l/c`, sin factor local.

## Evidencia autorizante

- suite sintética, operacional y API: 35/35 PASS;
- regresión IBG: `3.3525 -> 3.73`, sin salto local fabricado;
- production-equivalent probe: 8/8 shards PASS, 8 tickers y 11.459 sesiones;
- mismo runner, wrapper, agregador y certificador del full;
- 12 fórmulas independientes: error absoluto máximo 0;
- schemas: una variante por tabla, 8/8 parts;
- duplicados, claves nulas e infinitos: 0;
- terminal, lineage, scope, outcomes y superficie operacional: PASS.

## Alcance

4.824 tickers, 9.290.966 sesiones, 8 shards. Output inmutable:
`runs/20260825_full_raw_daily_v0_1`. Duración observada anterior aproximada:
67 minutos. Workers autorizados: 4. Overwrite y mezcla mediante resume prohibidos.

## Comando humano autorizado

```powershell
$env:PYTHONPATH='C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\src'
python -m tsis_statistics_patterns.orchestrate `
  --config "C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\configs\daily_pattern_atlas_v0_1.yaml" `
  --run-root "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_raw_daily_v0_1" `
  --mode full --workers 4
```

## Monitor

```powershell
python "C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\scripts\monitor_atlas_run.py" `
  --run-root "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_raw_daily_v0_1" `
  --watch --compact
```

## Stop seguro

```powershell
Stop-Process -Id ((Get-Content -LiteralPath `
  "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_raw_daily_v0_1\pid_manifest.json" `
  -Raw | ConvertFrom-Json).wrapper_pid)
```

Solo se aceptará el full tras terminal PASS, auditoría independiente PASS,
readout final, pruebas de API y smoke de localhost contra el nuevo run.