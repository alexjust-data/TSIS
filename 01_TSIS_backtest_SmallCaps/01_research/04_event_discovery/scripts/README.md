# 04_event_discovery/scripts

Fecha de creacion: 2026-06-20
Estado: carpeta de scripts repetibles para Event Discovery.

Esta carpeta contiene la logica ejecutable usada por los notebooks y configs de:

```text
01_research/04_event_discovery/
```

## Responsabilidad

Los scripts de esta carpeta deben:

- ejecutar queries exploratorias sobre daily/intraday;
- producir listas de candidatos;
- renderizar paneles de inspeccion;
- dar soporte a widgets de notebooks;
- guardar outputs runtime bajo `01_research/04_event_discovery/runs/`.

## Fuente operativa y universo

Para la fase actual, la fuente operativa 1m full-universe es:

```text
E:\TSIS\data\ohlcv_1m
```

Pero esa carpeta fisica no define el universo de smallcaps `<1B`.

La primera puerta de consumo para Event Discovery debe ser:

```text
01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
```

Concretamente:

```text
universe_dataset_id: lt1b_universe_v0_1
universe_run_id: 20260320_market_cap_last_observed_cutoff
universe_filter_policy: ticker_plus_pti_window
universe_rows: 4824
```

Regla:

```text
ticker in certified universe
event_date >= first_seen_date
event_date <= last_observed_date
```

Por tanto, los scripts no deben tratar los ~12k tickers fisicos de
`E:\TSIS\data\ohlcv_1m` como poblacion valida de busqueda.

## Semantica activa: primer push del dia

La query activa inicial es:

```text
first_day_3bar_push_gt_20pct
```

Por defecto no busca cualquier push de 20%.

Busca:

```text
primer bloque cualificado de 3 velas 1m del dia ET
scope de deteccion: premarket + regular
after-hours: excluido de la deteccion por defecto
ventanas que cruzan premarket/regular: excluidas por defecto
```

`all_pushes` queda solo como modo diagnostico para inspeccionar si el primer
filtro esta descartando demasiado o si hay multiples pushes relevantes.

## Workflow recomendado

Para busquedas grandes, usar terminal como ejecutor principal y Jupyter como
visor.

Flujo:

```text
1. Ajustar filtros en el notebook.
2. Copiar el comando PowerShell que muestra la lanzadera.
3. Ejecutarlo en una terminal.
4. Esperar a que termine y copie/imprima run_dir.
5. Pegar run_dir en el notebook o usar Load latest.
6. Inspeccionar candidatos y renderizar charts desde Jupyter.
```

El script de terminal imprime progreso con:

```text
files_to_scan=...
progress files_scanned=... raw_candidates=...
scan_complete files_scanned=... raw_candidates=...
```

Mientras el run esta vivo, la carpeta del run se crea al inicio y se actualiza:

```text
manifest.json                  estado/progreso/candidato parcial
candidate_events_partial.csv   candidatos detectados hasta el ultimo flush
```

Por defecto:

```powershell
--partial-flush-every 1
```

Esto significa que `candidate_events_partial.csv` se reescribe cada vez que
aparecen nuevos candidatos crudos. Para reducir escritura en runs grandes:

```powershell
--partial-flush-every 25
```

Para scans grandes, usar paralelismo desde terminal:

```powershell
--workers 4
```

o, si el disco aguanta bien:

```powershell
--workers 8
```

El primer cuello de botella no requiere C++: primero hay que evitar bucles de
Python por vela y leer multiples parquets en paralelo. C++ o Rust solo tendrian
sentido despues si el cuello sigue estando en CPU y no en I/O/parquet.

Los runs exploratorios se pueden borrar con:

```powershell
Remove-Item -LiteralPath 'C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\04_event_discovery\runs\<run_id>' -Recurse -Force
```

## Scripts

```text
find_event_candidates.py
render_event_case_panel.py
event_case_widgets.py
```

## No-goals

Esta carpeta no debe contener:

- Event Engine productivo;
- construccion de `event_table`;
- estrategia;
- backtest;
- logica de ejecucion.

## Regla final

Event Discovery scripts buscan candidatos y ayudan a inspeccionarlos.

No promueven eventos.
