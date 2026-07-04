# DAS Strategy Research

Estado: `strategy_research_experimental`
Scope: `03_STRATEGY_LIBRARY/LONG/DAS/`

Esta carpeta contiene la investigacion experimental de la estrategia long
`DAS` (`Dips After Squeeze`) dentro de TSIS.

DAS se estudia como estrategia de frontside momentum:

```text
scanner / ticker in-play
-> despertar con primer push
-> primer dip que no destruye estructura
-> rebreak o reactivacion alcista
-> secuencia frontside activa
-> continuacion, fallo o backside
```

## Documentos principales

| Documento | Rol |
| --- | --- |
| `STRATEGY.md` | Definicion humana inicial de la estrategia DAS. |
| `DAS_FRONTSIDE_STATE_AND_ALPHAEVOLVE_RESEARCH_PLAN_v0_1.md` | Plan de investigacion frontside, estados, after-hours, AlphaEvolve y relacion con Data Foundation. |
| `DAS_CANDIDATE_STATE_TABLE_EXPERIMENTAL_SPEC_v0_1.md` | Especificacion de la tabla experimental para convertir candidatos DAS en filas medibles. |
| `DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md` | Runbook operativo para consumir el scanner gobernado, declarar denominadores y evitar sesgo positivo en DAS. |

## Artefactos de trabajo

| Artefacto | Rol |
| --- | --- |
| `scripts/` | Scripts ejecutables y builders exploratorios DAS. |
| `scripts/das_widgets.py` | Script/widget exploratorio para buscar, visualizar y exportar candidatos DAS. |
| `scripts/build_das_candidate_state_table_experimental.py` | Builder experimental que normaliza candidatos DAS en una tabla de estados namespaced. |
| `scripts/build_das_experimental_stats_report.py` | Builder de reporte estadistico sobre la tabla experimental DAS. |
| `scripts/build_das_frontside_pattern_stats.py` | Builder de estadisticas frontside/patrones por run DAS. |
| `notebooks/` | Notebooks de inspeccion visual. No son source of truth productivo. |
| `notebooks/das_case_explorer.ipynb` | Notebook lanzadera para busqueda, charts, exports y estadisticas. |
| `runs/` | Runs experimentales, candidatos, exports y futuras tablas derivadas locales. |
| `DAS_VISUAL_CASEBOOK/` | Casebook visual humano para patrones DAS, ejemplos anotados y material de aprendizaje. |
| `DAS_VISUAL_CASEBOOK/img/archive/` | Imagenes copiadas desde Archive para lectura visual estructurada. |
| `DAS_VISUAL_CASEBOOK/img/human_good_cases/` | Casos humanos anotados como buenos o instructivos. Antes `BUENOS CORREGIDOS/`. |
| `DAS_VISUAL_CASEBOOK/img/human_bad_cases/` | Casos humanos anotados como malos/falsos positivos/review. Antes `MALOS/`. |

## Siguiente paso operativo

El siguiente paso no es crear `market_state_table` ni `event_state_table`.

El siguiente paso es construir una tabla local:

```text
das_candidate_state_table_experimental
```

desde el run DAS actual:

```text
runs\das_scanner_appearance_20260628T114046Z
```

Esa tabla debe separar:

- features observables;
- estados DAS/frontside;
- labels humanos;
- outcomes posteriores;
- quality flags;
- lineage visual y de datos.

Regla:

```text
human_label__ y outcome__ no son features.
```

Comando base:

```powershell
python 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\scripts\build_das_candidate_state_table_experimental.py' --run-dir 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z'
```

`notebooks/das_case_explorer.ipynb` separa dos superficies:

- celda principal: busqueda, carga de candidatos, render de charts y export de imagenes;
- celda de estadisticas: lectura de runs ya creados, construccion de tabla experimental, graficos de distribucion y reportes `.md`.

El reporte estadistico se escribe bajo:

```text
<run_dir>\state_tables\das_candidate_state_table_experimental_v0_1_stats_report.md
```

## Relacion con el scanner general

`daily_scanner_candidates_table_v0_2` existe hoy como builder y replay
controlado, no como tabla oficial promocionada en `E:/TSIS/data`.

DAS debe consumir esa tabla como denominador cuando estudie poblaciones de
candidatos. El manual operativo vive en:

```text
DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
```

Regla:

```text
scanner row = donde mirar
DAS state row = que estructura frontside/DAS aparecio
```

Si un run DAS no consume `daily_scanner_candidates_table_v0_2` y nace solo del
detector/notebook DAS actual, sus estadisticas deben declararse como:

```text
conditional_on_current_das_detector
```

y no como estadisticas poblacionales de todo el mercado.

Una vez exista un replay largo de `daily_scanner_candidates_table_v0_2`, los
runs DAS deben declarar si usan:

```text
all_filters_passed
selected_any_profile
selected_trade_station_like_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
manual_human_seed
conditional_on_current_das_detector
```
