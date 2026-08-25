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

1. seleccionar una de las 27 etiquetas, agrupadas en 5 familias;
2. consultar en el lateral la definición, fórmula y cautela de la familia;
3. revisar los agregados sobre todas sus apariciones;
4. abrir uno de los 90 casos recientes iniciales o cargar páginas adicionales;
5. mover el cursor para consultar fecha, OHLC y volumen;
6. usar rueda para zoom y arrastrar para recorrer toda la vida daily disponible;
7. pulsar una etiqueta de D0 para cambiar la activación y marcar todas sus
   ocurrencias en la vida completa del ticker;
8. alternar entre `Vida completa` y `Centrar D0`;
9. redimensionar los paneles de precio y volumen si se desea;
10. guardar notas humanas separadas del resultado calculado.

El total de casos y tickers de la cohorte se presenta en la misma línea que la
activación. `Mostrando N ... de TOTAL` distingue la página visible del censo
completo. D0 y las ocurrencias se marcan debajo de la vela; los outcomes se
agrupan por fecha y se marcan por encima. La autoescala y los márgenes evitan
superponer las marcas a las mechas. El panel inferior muestra volumen daily.
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
