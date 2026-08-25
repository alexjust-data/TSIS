# Daily Pattern Atlas — explorador local

Vista local de los Parquet certificados de `EXP_DAILY_PATTERN_ATLAS_0001`. No
calcula señales ni modifica el censo. La API escucha solo en `127.0.0.1`.

## Requisito

El lanzador selecciona `20260825_full_v0_1` si existe; de lo contrario usa
`20260825_probe_v0_2`. Si ninguno contiene certificación `pass`, la app no debe
presentarse como válida.

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

## Verificación técnica

```powershell
npm.cmd run lint
npm.cmd run build
Invoke-RestMethod http://127.0.0.1:8765/api/meta
```

`/api/meta` debe devolver `status: pass`.
