# 04_event_discovery

Fecha de creacion: 2026-06-20
Estado: area de research exploratorio para descubrimiento de eventos.

`04_event_discovery/` es la primera fase event-first dentro de
`01_research/`.

Su funcion es buscar, inspeccionar y documentar fenomenos candidatos en datos
daily e intraday antes de definir eventos gobernados o construir Event Engine.

## Pregunta principal

```text
Que fenomenos candidatos vemos en daily/intraday?
```

## Inputs

- datos intraday operativos en `E:\TSIS\data\ohlcv_1m`;
- universo primario certificado `lt1b_universe_v0_1`;
- instrucciones humanas de busqueda;
- conocimiento discrecional documentado en `00_CTO/00_private/eventos.md`;
- definiciones conceptuales vigentes en `00_CTO/13_TRADING_SYSTEMS/`.

La carpeta fisica `E:\TSIS\data\ohlcv_1m` no define el universo. Antes de
buscar eventos, las queries deben filtrar por:

```text
01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
```

Regla:

```text
ticker in lt1b_universe_v0_1
event_date >= first_seen_date
event_date <= last_observed_date
```

Esto evita tratar los ~12k tickers fisicos del raw 1m como universo valido de
smallcaps `<1B`.

## Outputs esperados

- queries exploratorias;
- listas de casos candidatos;
- notebooks de inspeccion;
- revisiones humanas de casos;
- notas sobre posibles eventos;
- requerimientos preliminares para `05_event_definition` y
  `06_feature_requirements`.

## No-goals

Esta carpeta no produce:

- eventos promovidos;
- `event_table`;
- detectores productivos;
- estrategias;
- backtests;
- entradas;
- stops;
- targets;
- sizing;
- claims de edge.

## Subcarpetas

```text
notebooks/
scripts/
configs/
  queries/
runs/
notes/
candidate_reviews/
```

### `notebooks/`

Contiene notebooks lanzadera de inspeccion visual.

El notebook principal esperado es:

```text
event_case_explorer.ipynb
```

Ese notebook debe llamar a scripts bajo:

```text
01_research/04_event_discovery/scripts/
```

### `scripts/`

Contiene logica repetible local al area:

```text
find_event_candidates.py
render_event_case_panel.py
event_case_widgets.py
```

Esta logica sigue siendo exploratoria. Si una pieza se vuelve reusable fuera de
Event Discovery, debe promocionarse despues a `scripts/` o `src/` con contrato
separado.

### `configs/queries/`

Contiene definiciones reproducibles de busquedas humanas.

Ejemplos:

```text
first_day_3bar_push_gt_20pct.yaml
intraday_move_gt_100pct.yaml
```

La query activa de primer impulso no significa "cualquier push de 20%".
Su semantica por defecto es:

```text
primer bloque cualificado de 3 velas 1m del dia ET
scope de deteccion: premarket + regular
after-hours: excluido de la deteccion por defecto
ventanas que cruzan premarket/regular: excluidas por defecto
```

### `notes/`

Contiene notas de research, hipotesis humanas y observaciones que todavia no
son definiciones gobernadas.

### `candidate_reviews/`

Contiene revisiones humanas de casos candidatos.

Debe separar:

- fenomeno observado;
- posible evento;
- posible outcome;
- partes que pertenecerian a estrategia y no al evento.

## Relacion con scripts

La logica repetible debe vivir en:

```text
01_research/04_event_discovery/scripts/
```

Regla:

```text
notebook = lanzadera e inspeccion
script = busqueda y render repetible
```

## Relacion con runs

Los outputs runtime deben vivir en:

```text
01_research/04_event_discovery/runs/
```

Nada en `01_research/04_event_discovery/runs/` es source of truth
institucional.

Para busquedas amplias, el flujo recomendado es terminal-first:

```text
notebook -> construir comando con filtros
terminal -> ejecutar busqueda y mostrar progreso
notebook -> cargar run_dir terminado y revisar casos
```

Esto evita que Jupyter sea el ejecutor principal de scans largos. Jupyter debe
quedar como lanzadera, visor y panel de inspeccion.

## Panel grafico minimo

Cada caso candidato debe poder renderizar:

- un unico grafico interactivo en velas de 1m;
- tres dias antes del evento y tres dias despues;
- scroll, pan y zoom tipo TradingView;
- premarket, regular market y after-hours diferenciados visualmente;
- el push de tres velas marcado en el chart;
- suficiente aire visual por encima del high y por debajo del low.

## Regla final

Event Discovery encuentra y observa.

No define estrategias.
No ejecuta trades.
No promueve eventos por si solo.
