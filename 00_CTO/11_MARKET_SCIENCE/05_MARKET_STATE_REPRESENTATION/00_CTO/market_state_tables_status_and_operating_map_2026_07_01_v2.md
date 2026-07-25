# Market State Representation - Fotografia Legal Del Mundo Observable En T

Fecha: 2026-07-04
Estado: v2_refactor_fotografia_legal_observable
Documento base: `market_state_tables_status_and_operating_map_2026_07_01.md`

## Naturaleza De Este Documento

Este v2 no sustituye al mapa CTO original.

Su funcion es aclarar una regla central:

```text
tablas de estado = fotografia legal del mundo observable en t
```

Es decir:

```text
state(t, instrument, event_context, data_availability_cutoff)
```

Una tabla de estado no debe elegir que importa. No debe imponer una estrategia,
un scanner, un threshold, un label, un reward o un outcome. Debe representar lo
que TSIS podia saber legalmente en ese momento, usando datos disponibles,
gobernados, reproducibles y trazables.

## Regla Base

La regla correcta es:

```text
tablas de estado = observables neutrales as-of
no = decisiones, triggers, outcomes, labels o thresholds descubiertos
```

No usamos la palabra "relevante" como criterio de seleccion cientifica. La
primera capa no decide relevancia. La primera capa inventaria y versiona lo que
existe en nuestros datos y puede observarse legalmente en `t`.

Criterio de entrada al estado:

| Criterio | Pregunta |
| --- | --- |
| Disponible | existe en nuestros datos o en una fuente contratada |
| Observable | podia conocerse en o antes de `t` |
| Legal as-of | respeta timestamp, lag, cutoff y disponibilidad real |
| Reproducible | se puede reconstruir desde manifest, schema, policy y source roots |
| Neutral | no codifica una decision, threshold ganador, label, reward ni outcome |
| Gobernado | tiene calidad, coverage, lineage y policy de consumo |

Si falla uno de estos puntos, no entra como estado base.

## Que No Debe Entrar En Estado Base

No debe entrar:

```text
cruce +50% como verdad privilegiada
winner/loser
outcome futuro
label de estrategia
reward
mejor threshold encontrado
seleccionado_por_scanner = true como feature causal
daily close final antes del cierre
fill real posterior
PnL posterior
accion tomada por una estrategia
```

El `+50%` puede existir en un scanner humano o en una hipotesis parametrizable,
pero no como atributo base obligatorio para AlphaEvolve, RL o ML. Para discovery,
lo correcto es exponer observables continuos y as-of; el evaluador/modelo prueba
si el umbral util es 12%, 37%, 50%, 83%, una combinacion, una secuencia temporal
o nada.

# 1. Tablas Finales De Estado

Estas son las dos tablas institucionales de estado que TSIS quiere construir.
Hoy no existen como outputs oficiales promovidos.

| Tabla | Que es | Estado actual | Uso hoy |
| --- | --- | --- | --- |
| `market_state_table_v0_1` | snapshot legal/as-of del instrumento y mercado en un decision timestamp | official not materialized; candidate controlado | prueba de integracion, no ML/RL/backtest core |
| `event_state_table_v0_1` | `market_state` anclado a evento, ventana y rol de decision | official not materialized; candidate controlado | pattern discovery controlado, no ML/RL/backtest core |

Lectura simple:

```text
market_state_table = que sabia TSIS legalmente en t

event_state_table = ese estado anclado a evento/ventana/rol de decision
```

`event_state_table` no debe contener outcomes. Puede contener referencias a
outcomes para join posterior, pero no valores de outcome, label o reward inline.

## 1.1 Como Integran Componentes

Las tablas finales no copian fuentes enteras dentro de una fila. Integran
observables as-of bajo namespaces explicitos:

```text
market_state row en t
= identity__*
+ calendar__*
+ scanner__*          # solo lineage de candidatos, no senal causal
+ daily__*
+ intraday__*
+ microstructure__*
+ halt__*
+ fundamentals__*
+ news__*
+ short_context__*
+ short_constraints__*
+ regime__*
+ quality__*
```

Luego:

```text
event_state row
= subset controlado de market_state namespaces
+ event__*            # metadata del evento conocida <= cutoff
+ event/window references
+ state_role
+ leakage gates
```

Regla clave:

```text
X = market_state/event_state observables bajo cutoff legal
y = outcomes separados, unidos despues
```

Namespaces confirmados por los schemas actuales:

```text
market_state_table:
  identity__, 
  calendar__, 
  scanner__, 
  daily__, 
  intraday__, 
  microstructure__,
  halt__, 
  fundamentals__, 
  news__, 
  short_context__, 
  short_constraints__,
  regime__, 
  quality__

event_state_table:
  los anteriores + event__
```

No son namespaces confirmados hoy en esos schemas:

```text
float__
corporate_alert__
corporate_action__
lineage__
event_window__
```

Pueden existir como componentes futuros, soporte, manifests, metadata o campos
estructurales, pero no deben presentarse como feature namespaces actuales hasta
que el contrato/schema los declare.

# 2. Componentes Que Alimentan Estado

Estos componentes si pertenecen a la arquitectura de estado, pero no son por si
solos el estado final completo. Son fuentes/base de observables.

Importante: las tablas de esta seccion describen familias de observables, no un
inventario cerrado de columnas finales. No esta comprobado que sean "solo esas".
Parte de ellas esta respaldada por schemas existentes; otra parte son
derivaciones as-of que deben convertirse en contrato antes de materializarse en
`market_state_table` o `event_state_table`.

Estado de auditoria de estas familias:

| Area | Estado de comprobacion | Lectura correcta |
| --- | --- | --- |
| Daily | comprobado contra `master_daily_table_schema_contract` | familias respaldadas por columnas existentes; no lista exhaustiva |
| Intradia 1m | comprobado contra `master_intraday_bar_table_schema_contract` y ruta quote-guarded | familias base respaldadas; `shape/speed/pace` requiere contrato de builder |
| Microestructura | comprobado contra `microstructure_features_table_schema_contract` y plan multi-window | familias respaldadas por seed/plan; no full-universe ni lista cerrada |
| Fundamentals/news/short/regime/halts | comprobado contra schemas de componente | familias respaldadas por tablas as-of existentes, con cutoff/lag propio |
| Short constraints | comprobado contra target contract | familia bloqueada: existe objetivo, no tabla materializada |
| Float / live corporate alerts | revisado en roadmap CTO | componentes futuros/pendientes; no namespaces de feature actuales |
| Soporte legal/calidad/lineage | comprobado como soporte | hace legal el estado, pero no es alpha ni inventario de features |

Trabajo pendiente para cerrar esto al 100%:

```text
1. extraer columnas reales de cada schema/componente
2. mapear cada columna a namespace final daily__/intraday__/...
3. marcar si es literal, derivada, quality, lineage, support o bloqueada
4. definir formulas/cutoff para cada derivada
5. generar contrato de observables para state builder
```

## 2.0 Componentes Por Tabla Final Con Evidencia

Este bloque fija la diferencia entre tabla final, componente fisico y familia de
observables. Los componentes y paths vienen de los contratos fuente impresos en
la revision de este documento.

### Impresion Contractual Base

```text
market_state_table_schema_contract.md:110-122
  identity_component_state, calendar_component_state, scanner_component_state,
  daily_component_state, intraday_component_state, microstructure_component_state,
  halt_component_state, fundamentals_component_state, news_component_state,
  short_context_component_state, short_constraints_component_state,
  regime_component_state, quality_component_state

market_state_table_schema_contract.md:141-153
  identity__, calendar__, scanner__, daily__, intraday__, microstructure__,
  halt__, fundamentals__, news__, short_context__, short_constraints__,
  regime__, quality__

event_state_table_schema_contract.md:154-167
  identity__, calendar__, scanner__, daily__, intraday__, microstructure__,
  halt__, fundamentals__, news__, short_context__, short_constraints__,
  regime__, quality__, event__

market_state_event_state_composition_contract_v0_1.md:207-224
  Identity, Calendar, Expected coverage, Dataset gates, Corporate actions,
  Scanner candidates, Daily price, Intraday bars, Microstructure, Halts,
  Event windows, Outcomes, Fundamentals, News, Short context, Regime,
  Short constraints, Real-time alerts
```

Path base usado en las filas con `.../`:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/
```

### `market_state_table_v0_1` - Componentes Que La Alimentan

| Componente | Fuente / tabla | Namespace o uso | Ejemplos impresos de schema/contrato |
| --- | --- | --- | --- |
| Identity | `instrument_master_v0_1` | `identity__*` | instrument/ticker identity, temporal match, common-stock/LT1B flags cuando el componente fuente los expone |
| Calendar | `market_calendar_v0_1` | `calendar__*` | session boundaries, session phase, timezone, early-close context |
| Expected coverage | `expected_data_calendar_v0_1` | quality/calendar support | denominator/absence context, expected data flags, missing expected data |
| Dataset gates | `dataset_certification_matrix_v0_1` | `quality__*` support | family-level usable/review/blocked gates |
| Corporate actions | `corporate_actions_table_v0_1` | support for price semantics; no current `corporate_action__*` namespace | split/dividend/ticker-change context; daily schema has `has_split_action`; intraday schema has corporate action counts |
| Scanner candidates | `daily_scanner_candidates_table_v0_1` target | `scanner__*` lineage only | candidate-set lineage; not complete state and not strategy signal |
| Daily price | `master_daily_table_v0_1` | `daily__*` | `open`, `high`, `low`, `close`, `volume`, `vwap`, `prior_close`, `gap_pct`, `daily_return_pct`, `daily_range_pct`, `dollar_volume`, `volume_20d_avg`, `rvol_20d` |
| Intraday bars | `master_intraday_bar_table_v0_1`; future `master_intraday_bar_table_v0_2_candidate_quote_guarded` | `intraday__*` | `ts_utc`, `session_date`, `bar_size`, `price_view`, OHLCV, `vwap`, `transaction_count`, `session_segment`, quote-guarded repair flags |
| Microstructure | `microstructure_features_table_v0_1` / candidate multi-window | `microstructure__*` | `quotes_window_rows`, first/last quote timestamp, spread bps median, top depth, trade rows, odd-lot ratio, trade dollar volume, last trade price |
| Halts | `halts_table_v0_1` | `halt__*` | `halt_event_id`, `halt_event_state`, event quality vocabulary; `prohibited_as_alpha=true` |
| Fundamentals | `fundamentals_asof_table_v0_1` | `fundamentals__*` | `statement_family`, `filing_date`, `as_of_date`, revenue/cost/gross-profit, cash/assets/liabilities/debt, cash-flow fields |
| News | `news_context_table_v0_1` | `news__*` | `published_utc`, `as_of_utc`, publisher, ticker attribution, keywords; must join by published/cutoff, not session date alone |
| Short context | `short_context_table_v0_1` | `short_context__*` | `short_interest`, `days_to_cover`, `short_volume`, `short_volume_ratio`, source/lag/as_of semantics |
| Regime | `regime_context_table_v0_1` | `regime__*` | `regime_proxy_role`, `as_of_utc`, prices/returns, `bars_observed`, calendar coverage, regime quality |
| Short constraints | target/runbook only | `short_constraints__*`, blocked | SSR active, borrow availability, locate approval, hard-to-borrow state, borrow fee; not materialized |
| Outcomes | `outcomes_table_v0_1` | prohibited as feature | labels/y only; can be joined later by key, never inline as state feature |
| Real-time alerts | not materialized | future component, no current namespace | offerings/filings/newswire live alerts require source/feed/latency contract |

### `event_state_table_v0_1` - Componentes Que La Alimentan

| Componente | Fuente / tabla | Namespace o uso | Ejemplos |
| --- | --- | --- | --- |
| Market-state subset | `market_state_table` builder output / same component set above | preserves original namespaces | `identity__`, `calendar__`, `scanner__`, `daily__`, `intraday__`, `microstructure__`, `halt__`, `fundamentals__`, `news__`, `short_context__`, `short_constraints__`, `regime__`, `quality__` |
| Event metadata | event source known before cutoff | `event__*` | event metadata known at or before decision cutoff; no outcome labels |
| Event windows | `event_windows_table_v0_1` | structural references / boundaries; no confirmed `event_window__*` namespace today | event boundaries, role, pre/post/decision window anchoring; boundary not feature label |
| Scanner lineage | `daily_scanner_candidates_table` / intraday candidate lineage when allowed | `scanner__*` lineage only | candidate-set lineage, not complete state, not strategy signal |
| Outcomes | `outcomes_table_v0_1` | reference key only, prohibited as feature | `outcome_join_key` / `label_join_key` may exist, but no outcome/label/reward values inline |

### Protocolo P1-P5 Para Cerrar Cada Familia Al 100%

Cada familia listada en `daily__*`, `intraday__*`, `microstructure__*`,
`fundamentals__*`, `news__*`, `short_context__*`, `short_constraints__*`,
`halt__*`, `regime__*`, `quality__*`, `scanner__*`, `identity__*` y
`calendar__*` debe pasar por este protocolo antes de considerarse cerrada. Esto aplica fila por fila a las tablas de familias que siguen en las secciones 2.1 a 2.5:

```text
P1. extraer columnas reales de cada schema/componente
P2. mapear cada columna a namespace final daily__/intraday__/...
P3. marcar si es literal, derivada, quality, lineage, support o bloqueada
P4. definir formula/cutoff para cada derivada
P5. generar contrato de observables para state builder
```

Lectura correcta:

```text
componente demostrado != familia cerrada al 100%

Un componente queda demostrado por contrato/schema.
Una familia queda cerrada solo cuando P1-P5 existe y esta versionado.
```

## 2.1 Estado Diario / Contexto Diario

| Componente | Que aporta al estado | Estado actual |
| --- | --- | --- |
| `master_daily_table_v0_1` | fotografia diaria por ticker/sesion/price_view; OHLCV, price views, gaps, volumen, lookbacks y calidad | validated for declared scope |

Lectura correcta:

```text
master_daily_table_v0_1 = componente diario de estado
```

No es `market_state_table` final. Alimenta `daily__*` con observables diarios o
historicos conocidos as-of.

### Evidencia Impresa Del Componente `master_daily_table_v0_1`

Esta evidencia baja del nivel "familia conceptual" al nivel de bloques reales
que existen en el schema de la tabla componente.

| Bloque interno del componente | Ejemplos reales impresos |
| --- | --- |
| Cobertura diaria / denominador | daily expected coverage denominator, expected session, missing expected data |
| OHLCV diario por price view | `open`, `high`, `low`, `close`, `volume`, `vwap`, `transaction_count` |
| Contexto diario calculado | `prior_close`, `gap_pct`, `daily_return_pct`, `intraday_return_pct`, `daily_range_pct`, `dollar_volume`, `volume_20d_avg`, `rvol_20d` |
| Price views / ajustes | `daily_raw`, `split_normalized`, `adjusted`; adjusted OHLC proxy; VWAP raw-only |
| Corporate actions | `corporate_action_count`, `split_action_count`, `dividend_action_count`, `ticker_change_action_count`, `has_split_action`, `has_any_corporate_action` |
| Calidad / consumo | `row_level_price_integrity_state`, `selected_price_hard_invalid`, `negative_volume`, `backtest_core_row_candidate`, family gates |
| Lineage / reproducibilidad | build ids, policy versions, schema version, build run, created timestamp |

Impresion literal usada como evidencia:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md
```

### Familias De Observables Desde Daily (No Inventario Cerrado)

Estos nombres son guia conceptual agrupada. `master_daily_table_schema_contract`
ya contiene columnas concretas como OHLCV, `prior_close`, `gap_pct`, returns,
range, dollar volume, `volume_20d_avg`, `rvol_20d`, corporate-action flags,
quality y lineage. El contrato final de estado debe decidir que subconjunto o
que derivaciones entran como `daily__*`.

| Familia | Que representa | Regla de cutoff |
| --- | --- | --- |
| `daily__price_view` | vista usada: raw, split_normalized, adjusted | debe ser la vista legal para ese uso |
| `daily__prior_session_ohlcv` | OHLCV de sesiones cerradas previas | solo sesiones ya cerradas y disponibles |
| `daily__current_session_open` | apertura de la sesion actual | solo despues de que sea observable |
| `daily__current_session_so_far` | datos diarios parciales si existen como acumulado legal | nunca usar close/high/low/volume final antes de cierre |
| `daily__lookback_extrema` | max/min/ranges en ventanas historicas declaradas | ventanas cerradas antes de `t` |
| `daily__lookback_volume` | volumen, dollar volume y liquidez historica | sesiones previas cerradas |
| `daily__lookback_volatility` | volatilidad/rango historico | sesiones previas cerradas |
| `daily__corporate_action_adjustment_state` | estado de ajustes por split/dividend/ticker change | segun effective dates y policy |
| `daily__quality_state` | usable/review/blocked/scoped | arrastra policy de consumo |
| `daily__source_manifest` | lineage de fuente diaria | obligatorio |

Cuidado:

- despues del cierre puede representar la sesion completa;
- antes del cierre no puede usarse como si `high`, `low`, `close` o `volume`
  final del dia ya fueran conocidos;
- los lookbacks son mediciones declaradas, no factores ganadores por si mismos.

## 2.2 Estado Intradia 1m / Base Principal Para Estrategias 1m

Esta pieza es central para nuestras estrategias. No debe estar escondida en
"no son estado".

| Componente | Que aporta al estado | Estado actual |
| --- | --- | --- |
| `master_intraday_bar_table_v0_1` | superficie intradia 1m scoped/piloto; barras, price views, session_date, ts_utc, calidad | scoped pilot, not full universe |
| `master_intraday_bar_table_v0_2_candidate_quote_guarded` | futura base intradia 1m quote-guarded para estados intradia defensibles | candidate contract defined; not materialized |

Lectura correcta:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
= equivalente intradia 1m de la base diaria
= componente/base principal para construir estados 1m
```

No es todavia:

```text
market_state_table final
```

Pero si debe alimentar:

```text
market_state_table
event_state_table
strategy event states
estadisticas de movimientos 1m
```

### Evidencia Impresa Del Componente `master_intraday_bar_table`

Esta evidencia baja del nivel "familia conceptual" al nivel de bloques reales
que existen en el schema intradia y en la ruta candidate quote-guarded.

| Bloque interno del componente | Ejemplos reales impresos |
| --- | --- |
| Identidad temporal intradia | `ticker`, `instrument_id`, `ts_utc`, `session_date`, `bar_size`, `price_view` |
| OHLCV 1m | `open`, `high`, `low`, `close`, `volume`, `vwap`, `transaction_count` |
| Raw/split-normalized lineage | `source_raw_open`, `source_raw_high`, `source_raw_low`, `source_raw_close`, split-normalized OHLC/VWAP fields |
| Session / segment | `session_segment` |
| Raw quality / coverage | raw quality manifest flags, negative/zero OHLC rows, duplicate timestamp rows, VW outside range rows |
| Corporate actions | corporate action counts and split/dividend/ticker-change flags |
| Consumption gates | row price integrity, invalid price, negative volume, core/vwap consumption allowed, full universe claim |
| Build lineage | certification/instrument build ids, quality policy, schema version, build run, created timestamp |
| Quote-guarded candidate flags | `quote_guarded_view`, `quote_guarded_repair_applied`, `repair_state`, `repair_reason`, `source_quote_guarded_repair_manifest`, `source_quote_guarded_run_id` |

Impresion literal usada como evidencia:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
```

### Familias De Observables Base Desde 1m (No Inventario Cerrado)

Correccion importante: esta seccion no define factores elegidos por ciencia ni
umbrales descubiertos. Define familias de observables que existen o pueden
derivarse legalmente desde barras 1m, calendario, contexto diario y lineage.
Las familias basicas salen de columnas reales de `master_intraday_bar_table`
como `ts_utc`, `session_date`, `bar_size`, `price_view`, OHLCV, VWAP,
`transaction_count`, price-view lineage, quality gates y repair/manifest flags.
Las familias tipo velocidad, aceleracion, pace o shape son derivadas: necesitan
formula, ventana y cutoff antes de ser schema oficial.

| Familia | Que representa | Regla de cutoff |
| --- | --- | --- |
| `intraday__last_closed_bar_ohlcv` | ultima vela 1m cerrada: open/high/low/close/volume/VWAP permitido | no usar vela incompleta salvo policy explicita |
| `intraday__session_so_far_price` | last price/close observable, high_so_far, low_so_far, range_so_far | solo barras observadas hasta `t` |
| `intraday__session_so_far_volume` | volume_so_far, dollar_volume_so_far, trade/count proxies si existen | no usar volumen final de sesion |
| `intraday__returns_continuous` | return vs prior close, open, segment open, VWAP permitido | valores continuos, sin threshold fijo |
| `intraday__move_shape` | velocidad, aceleracion, rango, expansion, pullback, retrace sobre ventanas declaradas | solo historia `<= t` |
| `intraday__volume_shape` | rvol_to_time, volume acceleration, dollar volume pace | baseline diario/as-of; no volumen futuro |
| `intraday__time_context` | session phase, minutes since open, minutes to close, segment | desde calendario/session clocks |
| `intraday__coverage_state` | bars_observed, missing bars, expected bars, stale bars | evidencia de cobertura as-of |
| `intraday__quote_guarded_state` | repair applied, repair state, repair reason, source manifest | lineage del overlay, no inferencia posterior |
| `intraday__quality_state` | consumo permitido, blocked/review/scoped flags | arrastra repair/quality policy |
| `intraday__source_manifest` | manifest/bundle raw + overlay + build run | obligatorio para reproducibilidad |

Lo que no entra aqui:

```text
first_cross_50_ts_utc como feature base
selected_intraday_in_play_candidate como feature causal
threshold de scanner como verdad del estado
```

Si se quiere estudiar cruces, el estado debe exponer la materia prima:

```text
return_vs_prior_close_pct
max_return_so_far_pct
move_speed
range_expansion
volume_so_far
rvol_to_time
liquidity_state
time_since_open
quality/coverage/lineage
```

Luego AlphaEvolve, RL, ML o un evaluador parametrico prueban si existe un cruce
util, con que porcentaje, en que ventana, bajo que liquidez y con que coste.

## 2.3 Microestructura Y Segundos

No mezclar esta capa con daily ni con 1m.

```text
daily = memoria/contexto historico
1m = barras intradia y estado vivo agregado
microestructura = quotes/trades/tape dentro o alrededor de la vela
```

| Componente | Que aporta al estado | Estado actual |
| --- | --- | --- |
| `microstructure_features_table` | observables de quotes/trades por ventana: spread, midpoint, quote/trade intensity, staleness, liquidity proxies | v0.1 seed; v0.2 candidate controlado, not promoted |

Para estrategias de segundos, 1m no basta. Se necesitan ventanas gobernadas de
microestructura.

### Evidencia Impresa Del Componente `microstructure_features_table`

Esta evidencia baja del nivel "familia conceptual" al nivel de bloques reales
que existen en el schema de microestructura y el plan multi-window.

| Bloque interno del componente | Ejemplos reales impresos |
| --- | --- |
| Ventana / identidad | `event_window_id`, `ticker`, `instrument_id`, `session_date`, `window_start_utc`, `window_end_utc`, `window_label` |
| Source roots / lineage | `quotes_root_used`, `quotes_root_state`, `trades_root_used`, `source_quotes_file`, `source_trades_file`, source hashes |
| Quote activity / coverage | `quotes_rows`, `quotes_window_rows`, first/last quote timestamp, zero bid/ask ratios, two-sided rows |
| Spread / book state | crossed/locked rows, crossed/locked ratios, spread bps median/p90, top depth mean |
| Trade activity / tape | `trades_rows`, `trades_window_rows`, first/last trade timestamp, invalid price/size rows, odd-lot ratio, duplicate ratio |
| Trade volume / price/size | `trades_total_volume`, `trades_dollar_volume`, min/max/last trade price, median/p90 size |
| Quality / eligibility | quote/trade family gates, `microstructure_quality_state`, event/backtest/execution candidates, full universe claim |
| Multi-window required additions | missingness reason, empty-in-window flags, staleness/sparse-window state, event role/family, leakage-safe flag, decision-time eligibility |

Impresion literal usada como evidencia:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
```

### Familias De Observables Desde Microestructura (No Inventario Cerrado)

| Familia | Que representa | Regla de cutoff |
| --- | --- | --- |
| `microstructure__spread_state` | spread, spread bps, midpoint, locked/crossed flags | quotes `<= t` o ventana declarada |
| `microstructure__quote_activity` | quote count, quote rate, quote staleness, missingness | cobertura de ventana |
| `microstructure__trade_activity` | trade count, tape intensity, size distribution si existe | trades `<= t` o ventana declarada |
| `microstructure__liquidity_proxy` | depth/proxy disponible, liquidity texture | depende de fuente disponible |
| `microstructure__price_impact_proxy` | impacto estimado por observables previos, no fill real | research/execution context, no truth posterior |
| `microstructure__quality_state` | usable/review/blocked/scoped | arrastra policy de consumo |
| `microstructure__source_manifest` | lineage quotes/trades | obligatorio |

No debe usarse como:

```text
outcome
fill garantizado
execution truth
full-universe claim si solo hay ventanas controladas
```

## 2.4 Contexto As-Of

Esta capa no describe la vela ni el book. Describe informacion, restricciones y
contexto externo conocidos legalmente en o antes de `t`.

| Componente | Que aporta al estado | Estado actual |
| --- | --- | --- |
| `fundamentals_asof_table_v0_1` | fundamentales conocidos por filing/as_of date | materialized for declared scope |
| `news_context_table_v0_1` | noticias conocidas por `published_utc` | materialized for declared scope |
| `short_context_table_v0_1` | short interest/short volume con lag/source scope | materialized for declared scope; no es borrow/SSR |
| `regime_context_table_v0_1` | regimen de mercado/session-level context | materialized for declared scope; cuidado intradia same-session |
| `halts_table_v0_1` | halt/resume/suspension context con timestamp | validated for declared scope; permitido si respeta timestamp legality |
| `short_sale_constraints_table` | SSR, borrow, locate, availability, HTB/ETB | blocked/not materialized |
| `float_context_table` | float/shares/free float point-in-time | pending/not materialized; no namespace confirmado hoy |
| `real_time_corporate_event_alerts_table` | offerings, filings, newswire/live alerts con `received_utc` y latencia | blocked/future live; no namespace confirmado hoy |

### Evidencia Impresa De Componentes `Contexto As-Of`

Esta evidencia separa componentes materializados, targets bloqueados y requisitos
pendientes. No todos tienen el mismo estado operativo.

| Componente | Ejemplos reales impresos |
| --- | --- |
| `fundamentals_asof_table_v0_1` | `statement_family`, `filing_date`, `as_of_date`, revenue/cash/assets/debt/cash-flow fields, cutoff as-of |
| `news_context_table_v0_1` | `published_utc`, `as_of_utc`, publisher fields, keywords, `news_quality_state`, intraday cutoff caveat |
| `short_context_table_v0_1` | `as_of_date`, `short_interest`, `days_to_cover`, `short_volume`, `short_volume_ratio`, source/lag scope |
| `regime_context_table_v0_1` | `regime_proxy_role`, `as_of_utc`, `as_of_date`, `bars_observed`, `regime_quality_state`, decision cutoff |
| `halts_table_v0_1` | `halt_event_id`, `halt_event_state`, `prohibited_as_alpha`, allowed event taxonomy |
| `short_sale_constraints_table` | SSR windows, `as_of_utc`, `hard_to_borrow_flag`, `locate_approved`, `borrow_fee_rate` |
| `float_context_table` | requisito pendiente de float/shares/free float point-in-time; no tabla oficial/schema hoy |
| `real_time_corporate_event_alerts_table` | requisito futuro/bloqueado de live alerts con latencia/received time; no feed promocionado |

Impresion literal usada como evidencia:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01.md
```

### Familias De Observables Desde Contexto As-Of (No Inventario Cerrado)

| Namespace | Que representa | Regla de cutoff / caveat |
| --- | --- | --- |
| `fundamentals__*` | filing recency, statement family, balance/cash/debt/revenue fields si estan gobernados | `filing_date/as_of_date <= t`; no usar period_end como disponibilidad |
| `news__*` | catalyst type, article_count, headline/source flags, `published_utc` | `published_utc <= t`; no prueba causalidad por si solo |
| `short_context__*` | short interest, short volume, source_system, lag model | no implica borrow, locate ni SSR |
| `short_constraints__*` | SSR active, borrow availability, locate status, fee | bloqueado hasta fuente broker/vendor/regulatoria |
| `halt__*` | halt/resume/suspension state, halt timestamps, halt context legal | solo si timestamp/event availability <= `t` |
| `regime__*` | SPY/QQQ/IWM/sector proxy, volatility/liquidity regime, session context | no usar close/regime final same-session antes de disponibilidad |

Regla practica:

```text
contexto as-of = informacion o restriccion conocida legalmente en t
```

No debe usarse como:

```text
outcome
causalidad demostrada
feature sin lag/cutoff
shortability si solo hay short volume/interest
```

## 2.5 Soporte Que Hace Legal El Estado

Estas tablas no son estado por si solas, pero hacen que el estado sea legal,
trazable y reproducible.

| Soporte | Funcion |
| --- | --- |
| `instrument_master_v0_1` | identidad temporal, ticker lineage, universo |
| `market_calendar_v0_1` | sesiones, horarios, timezone, early closes |
| `expected_data_calendar_v0_1` | denominador de cobertura esperada |
| `corporate_actions_table_v0_1` | splits, dividends, ticker changes, continuidad de precio |
| `dataset_certification_matrix_v0_1` | quality gates por familia |
| `data_quality_report` | evidencia humana/visual/tecnica de calidad; no feature alpha |

### Evidencia Impresa De Componentes De Soporte Legal

Estos componentes no son alpha ni outcome. Hacen legal, trazable y reproducible
la fotografia observable en `t`.

| Soporte | Ejemplos reales impresos |
| --- | --- |
| `instrument_master_v0_1` | `instrument_id`, `ticker`, identity scope, exchange fields, ticker-change counters, build lineage |
| `market_calendar_v0_1` | `session_date`, `is_early_close`, `timezone`, build lineage, windows premarket/regular/after-hours |
| `expected_data_calendar_v0_1` | expected dataset-family/ticker/session denominator, `expected_session`, timezone, lineage |
| `corporate_actions_table_v0_1` | `corporate_action_id`, `action_type`, dividends, ticker changes, build lineage, leak caveat |
| `dataset_certification_matrix_v0_1` | family status source, blocked gates, `build_run_id`, allowed/scoped/blocked decision support |
| `data_quality_report` | reporting layer over physical roots, audit verdict, human-auditor completion criteria, blocked evidence |

Impresion literal usada como evidencia:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/data_quality_report/README.md
```

### Familias / Metadata De Soporte Legal (No Inventario De Features)

| Namespace | Ejemplos | Para que sirve |
| --- | --- | --- |
| `identity__*` | instrument_id, ticker_at_t, issuer/name, asset_type, exchange, active flags | evitar survivorship/ticker confusion |
| `calendar__*` | session_date, session_phase, regular_start/end, early_close, timezone | construir ventanas legales |
| `quality__expected_data_*` | expected session/data flags, missing expected data | distinguir ausencia esperada de fallo |
| `quality__dataset_gate_*` | usable/review/blocked/scoped por familia | controlar consumo downstream |
| corporate action metadata / price-view policy | split/dividend/ticker-change flags, effective dates | soporte de semantica de precio; no namespace confirmado `corporate_action__*` |
| lineage fields / manifest bundle | source roots, manifests, build_run_id, schema/policy versions | reproducibilidad y auditoria; no namespace confirmado `lineage__*` |

No debe hacerse:

```text
usar soporte legal como alpha
ocultar quality flags
ignorar ticker lineage
ignorar corporate actions en price views
```

# 3. Lo Que No Es Estado

## 3.1 Scanners

No son estado. Seleccionan donde mirar o detectan condiciones bajo reglas
humanas o parametrizadas.

| Tabla | Que es | Por que no es estado |
| --- | --- | --- |
| `daily_scanner_candidates_table` | universo/candidatos por dia bajo una definicion de scanner | selecciona candidatos, no describe fotografia completa |
| `intraday_scanner_candidates_table` | detector intradia/in-play desde 1m | detecta timing/candidatos, no compone estado completo |

Regla:

```text
scanner = donde mirar o que evento disparar
state = que se sabia legalmente en t
```

`first_cross_50_ts_utc` pertenece aqui si se usa como regla de scanner. Tambien
puede existir como hipotesis parametrizable en un evaluador. No debe entrar como
observable base privilegiado para AlphaEvolve/RL/ML.

## 3.2 Eventos, Ventanas Y Labels

No son estado base.

| Tabla | Que es | Uso correcto |
| --- | --- | --- |
| `halts_table_v0_1` | log/fuente de eventos de halt/resume/suspension | no es estado final por si sola; si el timestamp es legal alimenta `halt__*` |
| `event_windows_table_v0_1` | fronteras temporales gobernadas por evento | define donde tomar snapshots; no es feature causal por si sola |
| `strategy_candidate_events_table` | eventos candidatos especificos de estrategia | seleccion/definicion de fenomeno; no estado completo |
| `outcomes_table_v0_1` | labels/resultados posteriores | es `y`, no `X`; nunca feature pre-evento |

Regla:

```text
event/window = donde anclar estado
outcome = que paso despues
```

## 3.3 Raw Data, Overlays Y Price Views Aisladas

No son estado final ni componente completo por si solos.

| Artefacto | Que es | Uso correcto |
| --- | --- | --- |
| `ohlcv_1m` | raw/staged 1m base | fuente base, no se modifica in place |
| `ohlcv_1m_split_normalized` | vista derivada por splits | price view derivada, no estado completo |
| `ohlcv_1m_quote_guarded` repair manifest | overlay de reparacion quote-guarded | construir vista 1m defendible |

Lectura actual del 1m reparado:

```text
raw ohlcv_1m
+ repair_manifest_lt1b_v0_1.parquet
= LT1B quote_guarded view
```

Esto desbloquea la tabla/base intradia que falta fortalecer:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

## 3.4 Estrategias, Decisiones, Ejecucion Y Modelos

No son estado.

| Objeto | Que es |
| --- | --- |
| estrategia | respuesta operativa propuesta |
| decision model | decide accion bajo constraints |
| execution model | evalua fills, slippage, borrow, latency, halts |
| reward/RL transition | capa posterior a estado + accion + resultado |
| AlphaEvolve | capa posterior, solo con evaluadores bloqueados |
| ML/RL dataset | derivado de estados + acciones/outcomes separados, no fuente primaria de estado |

Regla:

```text
estado no decide
estado permite decidir de forma auditable
```

# 4. Metodo Cientifico De Seleccion

La seleccion de columnas de estado no debe hacerse por intuicion de estrategia.
Debe hacerse por protocolo:

```text
1. Inventariar datos disponibles
2. Declarar timestamp/as-of/cutoff de cada familia
3. Convertir datos en observables neutrales y reproducibles
4. Guardar quality, coverage y lineage
5. Separar scanners, labels, outcomes y rewards
6. Permitir que evaluadores/modelos descubran utilidad, thresholds y reglas
```

Quien decide que:

| Actor | Decide |
| --- | --- |
| Data Foundation / CTO | que observables existen, son legales, reproducibles y gobernados |
| Market Science / Research | que mecanismos o familias causales investigar |
| Scanners | donde mirar o como crear eventos/candidatos bajo reglas declaradas |
| Evaluadores | si una hipotesis funciona out-of-sample y sin leakage |
| AlphaEvolve / ML / RL | combinaciones, thresholds, politicas o reglas bajo evaluador bloqueado |

Por tanto:

```text
Data Foundation no debe fijar el +50% como verdad cientifica.
Data Foundation debe exponer returns, volumen, velocidad, liquidez, tiempo y calidad.
El evaluador/modelo descubre si hay threshold util y cual es.
```

# 5. Ruta Pragmatica Despues Del 1m Reparado

El 1m quote-guarded ya permite avanzar, pero no saltar directamente a ML/RL ni
a `market_state_table_v0_1` oficial.

Orden simple:

```text
1. ohlcv_1m quote-guarded view
2. master_intraday_bar_table_v0_2_candidate_quote_guarded
3. inventario de observables 1m as-of disponibles
4. contrato de observables intraday__* sin thresholds privilegiados
5. microstructure_features_table multi-window donde haya fuente legal
6. contexto as-of: fundamentals/news/short/regime/float/constraints segun disponibilidad
7. soporte legal: identity/calendar/corporate_actions/quality/lineage
8. market_state_table controlled real sample
9. event anchors/windows/scanners separados
10. event_state_table controlled real sample
11. outcomes separados
12. estadisticas de winners/failures/neutral
13. hipotesis FACTORS/causalidad
14. evaluadores bloqueados
15. AlphaEvolve / ML / RL
```

## Que Puede Avanzar Ahora

Puede avanzar ahora:

- `master_intraday_bar_table_v0_2_candidate_quote_guarded` como candidate/preflight;
- inventario y contrato de observables `intraday__*` neutrales desde 1m;
- `intraday_scanner_candidates_table_v0_2_quote_guarded_candidate` como detector, no como estado base;
- `microstructure_features_table` hacia multi-window/multi-event candidate;
- muestras controladas mas ricas de `market_state_table` y `event_state_table` despues de fortalecer intradia/microestructura.

No debe promocionarse todavia:

- `market_state_table_v0_1` oficial;
- `event_state_table_v0_1` oficial;
- datasets ML/RL directos;
- execution simulator truth;
- thresholds de scanner como ciencia definitiva.

# 6. Frase De Cierre

La arquitectura correcta no es:

```text
scanner -> outcome -> estrategia
```

Tampoco es:

```text
humano elige +50% -> estado -> ML/RL
```

Es:

```text
datos gobernados
-> fotografia legal del mundo observable en t
-> market_state
-> eventos/ventanas/scanners separados para anclar preguntas
-> event_state
-> outcomes separados
-> estadistica/causalidad
-> evaluadores bloqueados
-> AlphaEvolve / ML / RL
```

La base intradia 1m no es secundaria. Para nuestras estrategias es una pieza
central. Solo hay que llamarla correctamente:

```text
componente/base intradia de observables as-of
```

no:

```text
market_state final
threshold de estrategia
factor descubierto
```







