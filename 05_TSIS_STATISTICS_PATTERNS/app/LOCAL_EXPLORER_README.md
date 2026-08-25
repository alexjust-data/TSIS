# Daily Pattern Atlas — explorador local

Vista local de los Parquet certificados de `EXP_DAILY_PATTERN_ATLAS_0001`. No
calcula señales ni modifica el censo. La API escucha solo en `127.0.0.1`.

## Requisito

El lanzador selecciona el full más reciente solo si contiene certificación
terminal `pass`; de lo contrario usa el probe PASS más reciente. Ignora de
forma fail-closed carpetas incompletas, certificaciones fallidas o JSON
ilegible. Si no existe ningún run terminal PASS, el lanzador se detiene.

## Inicio

```powershell
cd C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\app
.\start_atlas_local.ps1
```

Abrir `http://localhost:3000`.

## Uso

1. seleccionar una etiqueta de activación;
2. revisar trayectoria mediana, pico y first red day sobre todas sus apariciones;
3. abrir un caso real;
4. usar rueda para zoom y arrastrar para recorrer 120 observaciones anteriores y
   60 posteriores;
5. mover el cursor para consultar fecha, OHLC y volumen;
6. redimensionar los paneles de precio y volumen si se desea;
7. pulsar `Recentrar D0` para volver al evento;
8. guardar notas humanas separadas del resultado calculado.

D0 se marca debajo de la vela. Los outcomes de la misma fecha se agrupan y se
marcan por encima. La autoescala y los márgenes evitan superponer las marcas a
las mechas. El panel inferior muestra volumen daily.

Las notas viven en `api/annotations.sqlite`, artefacto runtime local no
gobernado.

## Monitor de un run

```powershell
python C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\scripts\monitor_atlas_run.py `
  --run-root <RUN_ROOT> --watch --compact
```

El monitor muestra etapa, PIDs, edad del heartbeat, progreso por shard, espacio
disponible y estado final sin borrar líneas anteriores.

## Verificación técnica

```powershell
npm.cmd run lint
npm.cmd run build
Invoke-RestMethod http://127.0.0.1:8765/api/meta
```

`/api/meta` debe devolver `status: pass`.
