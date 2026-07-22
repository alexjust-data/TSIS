# 01_research

Fecha de actualizacion: 2026-06-20
Estado: README raiz para organizacion conceptual de research.

`01_research/` es el espacio de investigacion del modulo
`01_TSIS_DATA_FOUNDATION`.

No es la autoridad de datos.
No es una carpeta de outputs institucionales.
No es el lugar final para logica productiva promovida.

Su funcion es organizar el trabajo de research por areas conceptuales antes de
que una pieza sea promovida a pipelines, scripts productivos, contratos
institucionales o outputs gobernados.

## Regla de lectura por fecha

Este README es la referencia local mas reciente para interpretar la
organizacion de `01_research/`.

Algunas carpetas fisicas existentes pueden conservar nombres historicos. La
fecha de actualizacion de este README indica la organizacion objetivo vigente
hasta que se ejecute una migracion formal de nombres.

Este documento no renombra carpetas por si mismo.

## Principio central

Las carpetas de `01_research/` deben representar areas conceptuales de trabajo,
no scripts sueltos ni resultados temporales.

Cada area conceptual debe tener, como minimo:

- proposito;
- inputs;
- outputs esperados;
- no-goals;
- relacion con Data Foundation;
- relacion con scripts;
- relacion con runs;
- estado de madurez.

## Separacion entre research, scripts y runs

La organizacion debe mantenerse local por area conceptual:

```text
01_research/<area_conceptual>/
  notebooks/
  scripts/
  configs/
  runs/
  notes/
```

### `01_research/<area_conceptual>/`

Contiene:

- notebooks lanzadera;
- scripts exploratorios repetibles;
- configs exploratorias;
- runs runtime reconstruibles;
- notas de research;
- revisiones humanas;
- definiciones preliminares;
- documentacion metodologica.

No debe contener:

- outputs pesados promocionados;
- datasets materializados;
- logica productiva final.

### `01_research/<area_conceptual>/scripts/`

Contiene scripts ejecutables asociados a esa area.

Los notebooks deben llamar a scripts de esta carpeta cuando la logica deje de
ser trivial pero todavia sea exploratoria/local al area.

Regla:

```text
notebook = lanzadera e inspeccion
script = logica repetible
```

### `01_research/<area_conceptual>/runs/`

Contiene outputs runtime reconstruibles:

- resultados de busqueda;
- parquet/csv temporales;
- manifests;
- paneles graficos;
- logs;
- outputs de notebooks o scripts locales.

Nada en `01_research/<area_conceptual>/runs/` es source of truth institucional
salvo promocion explicita.

Regla de promocion:

```text
research local -> 01_research/<area>/scripts
runtime local  -> 01_research/<area>/runs
codigo promovido/reusable -> scripts/ o src/
```

## Ubicacion operativa de datos

Para trabajo operativo nuevo de research, la data activa debe asumirse en:

```text
E:\TSIS\data
```

Esta es la ubicacion operativa que debe usarse como punto de partida para
busquedas, notebooks lanzadera y scripts nuevos de Event Discovery.

No se debe asumir como fuente operativa principal:

- `C:\TSIS_Data\data`;
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data`;
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs`;
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest`;
- `D:\`.

`runs/` sigue siendo carpeta de outputs runtime, manifests, logs y resultados
reconstruibles. No es la raiz de consumo de market data operativa.

Si algun contrato historico, registry o dossier apunta a una ruta diferente,
este README fija la lectura operativa vigente para la fase actual:

```text
data operativa nueva -> E:\TSIS\data
```

## Universo `<1B>` certificado para research

Para busquedas de eventos, preparacion de estrategias, backtests de research y
labels derivados sobre smallcaps `<1B`, la fuente de verdad de universo es:

```text
lt1b_universe_v0_1
```

El certificado local de consumo vive en:

```text
01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
```

Regla corta:

```text
data operativa -> E:\TSIS\data
universo <1B   -> lt1b_universe_v0_1
filtro         -> ticker + ventana [first_seen_date, last_observed_date]
```

Para Event Discovery y backtests smallcap `<1B`, el conteo de carpetas fisicas
en `E:\TSIS\data\ohlcv_1m` no define el universo. Esa carpeta puede contener
mas simbolos que el universo objetivo. La primera puerta de consumo debe ser:

```text
LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md
-> lt1b_universe_v0_1
-> market_cap_cutoff_lt_1b_active_inactive.parquet
-> ticker + [first_seen_date, last_observed_date]
```

Por tanto, una busqueda no debe escanear ni reportar como poblacion valida los
~12k tickers fisicos de `ohlcv_1m`. Debe filtrar primero a los 4.824 tickers
certificados del universo `<1B` y despues respetar la ventana temporal de cada
ticker.

`01_research` no debe reconstruir el universo `<1B>` desde `financial`,
`reference`, conteos de carpetas o snapshots ad hoc. La autoridad viva sigue en
`01_foundations`.

### Regla operativa para backtest 1m

Para un backtest 1m full-universe en la fase actual, usar como fuente base:

```text
E:\TSIS\data\ohlcv_1m
```

La razon operativa es cobertura: `ohlcv_1m` es la fuente amplia disponible.

La carpeta:

```text
E:\TSIS\data\ohlcv_1m_split_normalized
```

debe tratarse como piloto/validacion de normalizacion split-aware mientras no
exista materializacion completa para el universo objetivo. No debe asumirse
como fuente full-universe de backtesting 1m.

Regla estricta:

- si la estrategia o busqueda es intradia pura y no cruza sesiones, raw
  `ohlcv_1m` esta permitido con flags/calidad;
- si la logica usa gaps, retornos multi-dia, medias, `prev_close`, rangos
  previos o cualquier comparacion cross-session, raw `ohlcv_1m` no debe
  consumirse ciegamente alrededor de splits/reverse splits;
- resultados globales basados en raw no son promocionables como limpios si no
  controlan split risk;
- antes de declarar un backtest institucional, debe existir una capa
  split-normalized completa para el universo objetivo o, como minimo, para:
  - todos los tickers con splits/reverse splits;
  - todos los tickers usados por la estrategia;
  - controles sin split para comprobar que `factor = 1` no cambia nada.

Mientras esa capa completa no exista:

- intradia puro sin cruzar sesiones: raw permitido;
- cross-session o lookbacks multi-dia: raw permitido solo con flags/exclusion de
  ventanas afectadas por splits;
- resultados globales: no promocionables como limpios sin controlar split risk.

Para ejecucion/fills, usar raw `ohlcv_1m`, porque los fills deben ocurrir en
precios observados de mercado, no en precios normalizados.

Regla de separacion:

```text
senal/research global actual -> E:\TSIS\data\ohlcv_1m con split-risk flags
senal/research split-aware piloto -> E:\TSIS\data\ohlcv_1m_split_normalized
ejecucion/fills -> E:\TSIS\data\ohlcv_1m
```

## Notebook / Lab operativo de Daily Scanner Candidates

Para inspeccionar visualmente el primer replay controlado del scanner diario,
usar:

```text
01_research/notebooks/data_foundation_outputs/daily_scanner_candidates_replay_view_v0_1.ipynb
```

Ese notebook historico permite ver muestras de v0.1:

- `trade_station_like_scanner_v0_1`;
- `broad_in_play_discovery_scanner_v0_1`;
- candidatos broad descubiertos por debajo de `500k` de volumen;
- summary, manifest, columnas, flags de prohibicion y deduplicacion.

El builder historico `v0.1` vive en:

```text
scripts/materialize_daily_scanner_candidates_table.py
```

La evidencia de replay controlado inicial vive en:

```text
C:\TSIS_Data\tests\test_runs\2026-06-29\daily_scanner_candidates_replay_20250102_20250110_v0_1
```

El builder vigente para nuevos labs `v0.3` vive en:

```text
scripts/materialize_daily_scanner_candidates_table_v0_3.py
```

El runner obligatorio para ejecuciones largas/multi-year vive en:

```text
scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
```

Regla:

```text
notebook / python builder directo = muestras pequenas y desarrollo
runner PowerShell v0.3 = ejecuciones largas con pre-manifest, heartbeat, PID,
logs, summary y monitor compacto
```

La evidencia controlada vigente alineada con contrato vive en:

```text
C:\TSIS_Data\tests\test_runs\2026-06-30\daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum
```

Lectura obligatoria:

```text
base_eligible_smallcap_denominator_v0_3 = todo smallcap observable que TSIS puede inspeccionar
in_play_momentum_candidate_denominator_v0_3 = base eligible + move >= 50% + tradability
trade_station_like_profile_v0_3 = visibilidad operativa humana, no estrategia
selected_das_research_profile = false en el scanner global
daily_eod_proxy = no certifica primer segmento premarket/regular/afterhours
```

Regla:

```text
notebook = inspeccion visual / research
builder  = logica repetible
contrato = autoridad semantica
```

Politica de carpetas para ejecutar scanners:

```text
muestras pequenas / tests / demos:
  C:\TSIS_Data\tests\test_runs\<run_date>\<run_id>\

runs largos / multi-year / 20 anos:
  E:\TSIS\data\data_foundation_outputs\daily_scanner_candidates_table\candidate_replays\<run_id>\

root oficial reservado:
  E:\TSIS\data\data_foundation_outputs\daily_scanner_candidates_table\daily_scanner_candidates_table_v0_3\
```

El notebook no es autoridad productiva, no materializa el output oficial en
`E:\TSIS\data` y no convierte scanner rows en `market_state_table`, labels,
rewards, senales de estrategia, fills, PnL ni autoridad live.

Para estrategias especificas como DAS, el notebook no debe inventar un scanner
oculto ni seleccionar solo casos positivos. Debe consumir el parquet de
`daily_scanner_candidates_table_v0_3` y aplicar un overlay de estrategia
separado, o declarar explicitamente que el resultado es
`conditional_on_current_das_detector`.

Runbook DAS:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
```

## Lab operativo de Intraday Scanner Candidates

Para estrategias intradia, DAS/frontside, event-state y futuros estados ML/RL,
el scanner diario v0.3 es solo contexto coarse. No certifica:

```text
first_cross_ts
premarket / regular / afterhours
volume_to_time_at_first_cross
dollar_volume_to_time_at_first_cross
```

El builder intradia vigente vive en:

```text
scripts/materialize_intraday_scanner_candidates_table_v0_1.py
```

El runner obligatorio para ejecuciones largas/multi-month vive en:

```text
scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
```

La evidencia controlada inicial vive en:

```text
C:\TSIS_Data\tests\test_runs\2026-06-30\intraday_scanner_candidates_replay_20250102_20250110_v0_1
```

Lectura obligatoria:

```text
intraday_scanner_candidates_table_v0_1 = detector de primer push desde ohlcv_1m
selected_intraday_in_play_candidate = +50% vs prior_close + tradability gate
daily_scanner_candidates_table_v0_3 = proxy daily/EOD, no autoridad de timing intradia
```

Contratos:

```text
01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION\00_SCANNER_CANDIDATE_SELECTION\intraday_scanner_candidates_contract_v0_1.md
```

## Secuencia event-first vigente

Para la fase actual, la secuencia conceptual correcta es:

```text
event_discovery
-> event_definition
-> feature_requirements
-> event_engine
-> event_table
-> outcome_research
```

La razon es simple:

1. primero se descubren fenomenos candidatos;
2. despues se definen como eventos humanos revisables;
3. despues se decide que features hacen falta para detectarlos bien;
4. solo entonces se construye el Event Engine.

Por tanto, la primera fase no debe llamarse `feature_engine` ni `event_engine`
si todavia estamos buscando ejemplos, inspeccionando graficos y convirtiendo
conocimiento humano en eventos candidatos.

La fase inicial debe llamarse:

```text
event_discovery
```

`event_discovery` responde:

```text
Que fenomenos candidatos vemos en daily/intraday?
```

`event_engine` responde despues:

```text
Como detectamos eventos ya definidos y producimos event_table?
```

`feature_requirements` responde en medio:

```text
Que variables necesita este evento para poder ser detectado de forma robusta?
```

## Organizacion objetivo para eventos

La organizacion objetivo para la fase actual es:

```text
01_TSIS_DATA_FOUNDATION/
  01_research/
    04_event_discovery/
      README.md
      notebooks/
        event_case_explorer.ipynb
      scripts/
        find_event_candidates.py
        render_event_case_panel.py
        event_case_widgets.py
      configs/
        queries/
      runs/
        <run_id>/
          query_config.json
          candidate_events.parquet
          candidate_events.csv
          case_panels/
          manifest.json
      notes/
      candidate_reviews/

    05_event_definition/
      README.md
      draft_events/
      notes/

    06_feature_requirements/
      README.md
      event_feature_specs/
```

Mas adelante, cuando existan eventos definidos y aceptados:

```text
01_TSIS_DATA_FOUNDATION/
  01_research/
    07_event_engine/
      README.md
      contracts/
      prototypes/
      scripts/
        build_event_table.py
      runs/
        <run_id>/
          event_table.parquet
          manifest.json

```

## Notebook lanzadera de Event Discovery

El notebook de Event Discovery debe servir para inspeccion humana, no para
guardar logica canonica pesada.

Caso esperado:

```text
notebooks/event_case_explorer.ipynb
```

La celda principal debe permitir seleccionar, mediante widgets:

- query/run;
- ticker;
- fecha;
- evento o caso candidato;
- ventana temporal;
- modo de visualizacion.

Debe llamar a scripts bajo:

```text
01_research/04_event_discovery/scripts/
```

## Panel grafico esperado

Para cada caso candidato, el panel minimo debe incluir un grafico interactivo:

- velas de 1m;
- tres dias antes del evento y tres dias despues;
- scroll, pan y zoom tipo TradingView;
- premarket, regular market y after-hours separados visualmente;
- push de tres velas marcado;
- aire visual suficiente por arriba y por abajo.

Este grafico sirve para inspeccion y formulacion de eventos. No prueba edge.

## Queries humanas iniciales

Las instrucciones humanas pueden expresarse como busquedas exploratorias.

Ejemplos:

```text
Busca momentos en cualquier ticker donde en premarket o mercado sube en las
tres primeras velas de 1m mas de 20%.

Busca momentos en que hubo +100% de subida.
```

Estas instrucciones deben convertirse en configs o parametros reproducibles y
luego ejecutarse por scripts de `event_discovery`.

El resultado son candidatos observables, no eventos promovidos.

## Relacion con 00_CTO

`00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/` gobierna el lenguaje conceptual de
eventos.

`01_research/event_discovery` encuentra, inspecciona y documenta casos
candidatos usando data daily/intraday.

La direccion correcta es:

```text
casos candidatos observados
-> concepto humano de evento
-> definicion revisada en Event Library
-> requerimientos de features
-> detector futuro
-> event_table
```

## Arbol fisico historico observado

En la fecha de este README, el arbol fisico contiene carpetas historicas:

```text
01_auditoria_RAW_DATA
02_reference_layer
03_universe_builder
04_feature_engine
05_event_engine
06_strategy_engine
07_execution_simulator
08_research_backtests
09_edge_statistico
10_regime_modeling
11_ml_preparation
```

La carpeta historica `04_feature_engine` no debe interpretarse como fase previa
obligatoria para esta etapa. En el flujo event-first, primero se descubren los
eventos candidatos y despues se documentan los requerimientos de features que
permiten detectarlos.

La carpeta historica `05_event_engine` tambien debe revisarse antes de usarla
para la fase actual. Si todavia no produce `event_table`, no debe actuar como
Event Engine real.

La organizacion objetivo futura para esta zona es:

```text
04_event_discovery
05_event_definition
06_feature_requirements
07_event_engine
```

No se debe renombrar de forma silenciosa. Cualquier migracion de nombres debe
ser explicita, pequena y documentada.

## Regla final

Primero discovery.
Despues definicion.
Despues requerimientos de features.
Despues engine.

No se debe llamar Feature Engine ni Event Engine a una fase que todavia esta
buscando, visualizando y entendiendo fenomenos candidatos.
