# Full Run Authorization v0.2

Fecha: 2026-08-25
Estado: `PASS_FULL_AUTHORIZED`
Experimento: `EXP_DAILY_PATTERN_ATLAS_0001`
Probe autorizante: `20260825_probe_v0_3`
Implementación autorizada: commit `2091e75f`

## Evidencia autorizante

- suite sintética/operacional: 18/18 PASS;
- production-equivalent probe: 8/8 shards PASS;
- 8 tickers reales y 11.459 sesiones;
- mismo runner, wrapper, agregador, terminal y manifests previstos para el full;
- 12 fórmulas seleccionadas recalculadas: error absoluto máximo 0;
- 5 tablas sharded: una variante física de schema en 8/8 parts;
- claves duplicadas o nulas: 0;
- valores infinitos: 0 en los 11 Parquet finales;
- outcomes/eventos sobre filas inválidas: 0;
- running highs y peaks inconsistentes: 0;
- D0 de cohortes directas distinto de activaciones: 0;
- casos de estadísticas de eventos distintos de activaciones: 0;
- rutas source ausentes: 0;
- 11 artifacts con SHA-256 y schema verificados;
- commit, config hash y upstream hash: PASS;
- superficie operacional: 50 heartbeats, PID manifest, JSONL, log, monitor y
  final operativo, todos PASS.

## Incidentes heredados

Los controles de INC-20260824-001/002 e INC-20260825-003..009 pasan en el probe
v0.3. Cualquier cambio posterior en código, config, schema, wrapper, agregador o
certificador invalida esta autorización y exige repetir los ocho shards.

## Alcance autorizado

Se autoriza `20260825_full_v0_1` sobre la membresía exacta de 4.824 tickers y
9.290.966 sesiones. El run debe usar el mismo código/config del probe. Se permite
que el commit de ejecución sea descendiente del commit de implementación solo
si el diff intermedio contiene exclusivamente esta autorización y documentos de
estado, nunca código o configuración ejecutable.

## Comando de ejecución

```powershell
$env:PYTHONPATH='C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\src'
python -m tsis_statistics_patterns.orchestrate `
  --config "C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\configs\daily_pattern_atlas_v0_1.yaml" `
  --run-root "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_v0_1" `
  --mode full --workers 4
```

## Impacto y control humano

- scope: 4.824 tickers, 9.290.966 sesiones y 8 shards;
- IO esperado: lectura de los 44.423 Parquet raw/ajustados del universo y varios
  GB de outputs derivados;
- duración orientativa: decenas de minutos, dependiente de almacenamiento;
- overwrite: prohibido; un root existente aborta;
- resume: prohibido con mezcla de versiones; un reintento usa otro run ID.

Monitor:

```powershell
python "C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\scripts\monitor_atlas_run.py" `
  --run-root "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_v0_1" `
  --watch --compact
```

Stop seguro solicitado por el humano:

```powershell
Stop-Process -Id ((Get-Content -LiteralPath `
  "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAILY_PATTERN_ATLAS_0001\runs\20260825_full_v0_1\pid_manifest.json" `
  -Raw | ConvertFrom-Json).wrapper_pid)
```

El stop no borra outputs; deja el run no promocionable y el reintento requiere
nuevo ID.

## Criterio terminal

Solo se acepta el full si el orquestador, la certificación terminal, la auditoría
post-run, los tests de API y el smoke local de la app terminan en PASS. Esta
autorización no anticipa ese resultado.
