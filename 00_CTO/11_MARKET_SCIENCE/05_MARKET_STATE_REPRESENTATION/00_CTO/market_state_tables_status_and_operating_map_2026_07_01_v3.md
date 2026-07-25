# Market State Representation - Fotografia Legal Del Mundo Observable En T

Fecha: 2026-07-04
Estado:
```
v3_refactor_lectura_humana_parte_0_2_micro_context_examples +
avance_2026_07_04 +
formulas_done +
timestamp_policy_done +
roles_done +
builder_contract_done +
event_candidate_tables_contract_done +
event_candidate_table_schema_contracts_done +
event_candidate_table_validators_contract_done +
canonical_vs_representation_contract_done +
event_candidate_executable_validators_fixture_scope_done +
event_candidate_builders_fixture_scope_done +
daily_event_candidate_controlled_materialization_done +
scientific_discovery_engine_alignment_done +
research_experiment_pipeline_inserted +
ruta_capas_definida
```
Documento base: `market_state_tables_status_and_operating_map_2026_07_01.md`
Documento anterior: `market_state_tables_status_and_operating_map_2026_07_01_v2.md`

## Lectura Oficial Desde 2026-07-05

Este mapa v3 sigue siendo la lectura humana principal para `market_state` y
`event_state`, pero ya no debe leerse como la arquitectura completa de TSIS.

La arquitectura superior vigente es:

```text
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
```

Nueva lectura:

```text
market_state / event_state = X legal as-of
outcomes = Y separado
research_experiment = unidad cientifica que disena como mirar X e Y
evidence = resultado reproducible del experimento
knowledge_object = conclusion candidata promovible
validated_knowledge = conocimiento que supero validacion
operational_component = detector, representacion, estrategia, policy o regla usable
```

Por tanto, este documento gobierna la base observable. No gobierna por si solo
la ciencia de descubrimiento, la validacion ni AlphaEvolve.

Relacion con la nueva arquitectura:

```text
state tables / event_state / outcomes controlados
-> Scientific Discovery Engine
-> research_experiment_contract
-> parameter_sweep / exploratory statistics
-> event family candidates / knowledge objects
-> evaluator_contract / locked evaluators
-> AlphaEvolve/RL/ML segun corresponda
```

Regla:

```text
las tablas de estado no descubren conocimiento por si solas;
proporcionan la fotografia legal del mundo observable para que los experimentos puedan ejecutarse.
```
## Alcance De Esta V3

Esta v3 no sustituye al mapa CTO original ni intenta cerrar todos los contratos.

Su funcion es refactorizar la parte inicial del v2 para que sea legible por un
humano sin perder informacion:

```text
0. regla base de estado
1. tablas finales de estado
2. componentes que alimentan estado
3. puente hacia el contrato columna-por-columna
```

Las secciones detalladas por area (`Daily`, `Intradia 1m`, `Microestructura`,
`Contexto As-Of`, `Soporte Legal`) se deben seguir trabajando despues usando
esta estructura.

## Lectura En Una Pagina

La idea central es:

```text
tablas de estado = fotografia legal del mundo observable en t
```

Formalmente:

```text
state(t, instrument, event_context, data_availability_cutoff)
```

Esto significa que una tabla de estado no decide que importa. No elige una
estrategia, no impone un scanner, no fija un threshold ganador, no contiene
labels, no contiene rewards y no contiene outcomes.

El flujo correcto es:

```text
componentes existentes
-> familias de observables
-> contrato de elegibilidad columna-por-columna
-> state builder
-> market_state_table / event_state_table
-> outcomes separados
-> research_experiment
-> evidence / knowledge_object
-> evaluadores exploratorios o bloqueados segun fase
```

La separacion mental que evita confusiones es esta:

| Nivel | Pregunta que responde | Ejemplo |
| --- | --- | --- |
| Componente | De que tabla/fuente sale la informacion? | `master_daily_table_v0_1` |
| Bloque interno | Que grupo de columnas existe dentro del componente? | OHLCV diario, calidad, lineage |
| Familia de observables | En que namespace conceptual entra? | `daily__prior_session_ohlcv` |
| Observable final | Que campo concreto podria entrar al state builder? | `daily__prior_close` |
| Contrato de elegibilidad | Puede entrar, como, con que cutoff y para que uso? | `state_observable_eligibility_contract_v0_1.md` |

## Regla Base

La regla correcta es:

```text
tablas de estado = observables neutrales as-of
no = decisiones, triggers, outcomes, labels o thresholds descubiertos
```

No usamos la palabra "relevante" como criterio de seleccion cientifica en la
capa base. La primera capa no decide relevancia. La primera capa inventaria y
versiona lo que existe en nuestros datos y puede observarse legalmente en `t`.

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
pero no como atributo base obligatorio para AlphaEvolve, RL o ML.

Para discovery, lo correcto es exponer observables continuos y as-of. Despues,
el evaluador/modelo prueba si el umbral util es 12%, 37%, 50%, 83%, una
combinacion, una secuencia temporal o nada.

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
observables as-of bajo namespaces explicitos.

Una fila de `market_state_table` en `t` puede componerse asi:

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

Una fila de `event_state_table` se construye encima:

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

Estos componentes pertenecen a la arquitectura de estado, pero no son por si
solos el estado final completo. Son fuentes/base de observables.

La idea correcta es:

```text
componentes alimentan estado
familias organizan observables
contrato de elegibilidad decide columna por columna
```

Importante:

```text
esta seccion describe familias de observables
no describe un inventario cerrado de columnas finales
```

Parte de estas familias esta respaldada por schemas existentes. Otra parte son
derivaciones as-of que deben convertirse en contrato antes de materializarse en
`market_state_table` o `event_state_table`.

## 2.1 Estado De Auditoria Por Area

| Area | Estado de comprobacion | Lectura correcta |
| --- | --- | --- |
| Daily | comprobado contra `master_daily_table_schema_contract` | familias respaldadas por columnas existentes; no lista exhaustiva |
| Intradia 1m | comprobado contra `master_intraday_bar_table_schema_contract` y ruta quote-guarded | familias base respaldadas; `shape/speed/pace` requiere contrato de builder |
| Microestructura | comprobado contra `microstructure_features_table_schema_contract` y plan multi-window | familias respaldadas por seed/plan; no full-universe ni lista cerrada |
| Fundamentals/news/short/regime/halts | comprobado contra schemas de componente | familias respaldadas por tablas as-of existentes, con cutoff/lag propio |
| Short constraints | comprobado contra target contract | familia bloqueada: existe objetivo, no tabla materializada |
| Float / live corporate alerts | revisado en roadmap CTO | componentes futuros/pendientes; no namespaces de feature actuales |
| Soporte legal/calidad/lineage | comprobado como soporte | hace legal el estado, pero no es alpha ni inventario de features |

## 2.2 Trabajo Pendiente Para Cerrar El Inventario Al 100%

Para pasar de mapa conceptual a contrato operativo falta este trabajo:

```text
1. extraer columnas reales de cada schema/componente
2. mapear cada columna a namespace final daily__/intraday__/...
3. marcar si es literal, derivada, quality, lineage, support o bloqueada
4. definir formulas/cutoff para cada derivada
5. generar contrato de observables para state builder
```

El contrato que cierra formalmente esto es:

```text
state_observable_eligibility_contract_v0_1.md
```

Ruta propuesta:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md
```

# 3. Contrato De Elegibilidad De Observables

## 3.1 Para Que Sirve

`state_observable_eligibility_contract_v0_1.md` no sustituye a este documento.

Su funcion es convertir el inventario conceptual en una matriz operativa
columna-por-columna.

Este documento responde:

```text
que familias existen y por que pertenecen a estado
```

El contrato de elegibilidad responde:

```text
de que area viene
que columna existe
que observable puede producir
si entra ahora o no
bajo que cutoff
para que usos esta permitido
```

## 3.2 Columnas Del Contrato

La matriz operativa debe tener, como minimo:

```text
source_component
source_schema_path
source_column
target_namespace
target_observable_name
literal_or_derived
observable_class
formula
cutoff_rule
quality_gate_required
allowed_for_market_state
allowed_for_event_state
allowed_for_ml
allowed_for_rl
allowed_for_alphaevolve
leakage_risk
status
```

## 3.3 Areas Del Contrato

El contrato debe tener secciones por area:

```text
1. Daily
2. Intradia 1m
3. Microestructura
4. Contexto As-Of
   - fundamentals
   - news
   - short_context
   - regime
   - halts
5. Short Constraints
6. Float / Live Corporate Alerts
7. Soporte Legal / Calidad / Lineage
```

## 3.4 Vocabulario De Status

La diferencia entre areas no es solo semantica. Cada observable debe tener un
estado operativo.

Vocabulario inicial:

| Status | Significado |
| --- | --- |
| `eligible_now` | columna/observable puede entrar bajo cutoff y quality gate declarados |
| `candidate_requires_formula` | derivada posible, pero falta formula, ventana o cutoff formal |
| `candidate_requires_materialization` | contrato posible, pero falta tabla o output materializado |
| `blocked_no_source` | objetivo deseado, pero no hay fuente usable |
| `blocked_no_materialized_table` | existe target/contrato, pero no tabla materializada |
| `future_no_namespace` | componente futuro; hoy no tiene namespace confirmado |
| `support_only` | soporte legal/semantico, no feature alpha |
| `lineage_only` | trazabilidad/manifests/build ids, no senal causal |
| `quality_only` | calidad/coverage/gates de consumo, no senal alpha |

## 3.5 Como Leer El Paso De Familia A Observable

La relacion correcta es:

```text
Componente
-> Bloque interno del componente
-> Familia de observables
-> Observable final concreto
-> Decision de elegibilidad
```

El v2/v3 llega hasta familias y explica la arquitectura.

El contrato `state_observable_eligibility_contract_v0_1.md` baja un nivel mas:
expande cada familia a observables concretos columna-por-columna.

## 3.6 Ejemplo Daily

| Nivel | Valor |
| --- | --- |
| Componente | `master_daily_table_v0_1` |
| Bloque interno | Contexto diario calculado |
| Columnas reales | `prior_close`, `gap_pct`, `daily_return_pct`, `volume_20d_avg`, `rvol_20d` |
| Familias relacionadas | `daily__prior_session_ohlcv`, `daily__lookback_volume`, `daily__quality_state` |
| Observables finales ejemplo | `daily__prior_close`, `daily__gap_pct`, `daily__rvol_20d` |

Ejemplo de fila de contrato:

```text
area = Daily
source_component = master_daily_table_v0_1
source_column = prior_close
target_namespace = daily__
target_observable_name = daily__prior_close
literal_or_derived = literal
status = eligible_now
cutoff_rule = prior session closed and available
```

Lectura humana:

```text
prior_close existe en el componente diario.
Puede alimentar un observable daily__ porque representa informacion de una
sesion previa cerrada y disponible antes del decision timestamp.
```

## 3.7 Ejemplo Intradia 1m

| Nivel | Valor |
| --- | --- |
| Componente | `master_intraday_bar_table_v0_2_candidate_quote_guarded` |
| Bloque interno | OHLCV 1m |
| Columnas reales | `open`, `high`, `low`, `close`, `volume`, `vwap`, `transaction_count` |
| Familias relacionadas | `intraday__last_closed_bar_ohlcv`, `intraday__session_so_far_price`, `intraday__session_so_far_volume` |
| Observables finales ejemplo | `intraday__last_closed_bar_close`, `intraday__last_closed_bar_volume`, `intraday__last_closed_bar_vwap` |

Ejemplo de fila de contrato:

```text
area = Intradia 1m
source_component = master_intraday_bar_table_v0_2_candidate_quote_guarded
source_column = close
target_namespace = intraday__
target_observable_name = intraday__last_closed_bar_close
literal_or_derived = literal
status = eligible_now
cutoff_rule = closed 1m bar <= decision_timestamp_utc
```

Lectura humana:

```text
close existe en la barra 1m.
Solo puede alimentar estado como ultima vela cerrada si esa vela esta cerrada y
su timestamp respeta decision_timestamp_utc.
```

## 3.8 Ejemplo De Derivada Intradia

Las familias tipo `shape`, `speed` o `pace` no deben entrar como si fueran
columnas oficiales.

Ejemplo:

```text
area = Intradia 1m
source_column = open/high/low/close over declared window
target_observable_name = intraday__move_speed
literal_or_derived = derived
status = candidate_requires_formula
cutoff_rule = all bars in window <= decision_timestamp_utc
```

Lectura humana:

```text
move_speed puede ser una derivada legal, pero solo despues de declarar formula,
ventana, cutoff y quality gates. Mientras eso no exista, no es observable oficial
del estado.
```

## 3.9 Ejemplo Microestructura Y Segundos

Esta capa no debe mezclarse con daily ni con 1m.

La separacion correcta es:

```text
daily = memoria/contexto historico
1m = barras intradia y estado vivo agregado
microestructura = quotes/trades/tape dentro o alrededor de la vela
```

Para estrategias de segundos, 1m no basta. Se necesitan ventanas gobernadas de
microestructura.

### Componente Principal

| Componente | Que aporta al estado | Estado actual |
| --- | --- | --- |
| `microstructure_features_table` | observables de quotes/trades por ventana: spread, midpoint, quote/trade intensity, staleness, liquidity proxies | v0.1 seed; v0.2 candidate controlado, not promoted |

Lectura humana:

```text
microstructure_features_table
= componente de estado de microestructura por ventana
= no es daily
= no es barra 1m
= no es verdad de ejecucion ni fill garantizado
```

### Bloques Reales Del Componente

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

Evidencia fuente:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
```

### Familias De Observables Desde Microestructura

Estas familias no son inventario cerrado. El contrato
`state_observable_eligibility_contract_v0_1.md` debe expandirlas a observables
concretos columna-por-columna.

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

Lectura para el contrato de elegibilidad:

```text
Microestructura puede alimentar estado solo si la ventana, fuentes, cutoff,
lineage y calidad estan declarados. Si la tabla es candidate controlada, no debe
presentarse como full-universe ni como verdad de ejecucion.
```

## 3.10 Ejemplo Contexto As-Of

Esta capa no describe la vela ni el book. Describe informacion, restricciones y
contexto externo conocidos legalmente en o antes de `t`.

Regla practica:

```text
contexto as-of = informacion o restriccion conocida legalmente en t
```

### Componentes De Contexto As-Of

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

### Bloques Reales O Targets Revisados

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

Evidencia fuente:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01.md
```

### Familias De Observables Desde Contexto As-Of

Estas familias tampoco son inventario cerrado. Algunas estan respaldadas por
componentes as-of existentes; otras son targets bloqueados o futuros.

| Namespace | Que representa | Regla de cutoff / caveat |
| --- | --- | --- |
| `fundamentals__*` | filing recency, statement family, balance/cash/debt/revenue fields si estan gobernados | `filing_date/as_of_date <= t`; no usar `period_end` como disponibilidad |
| `news__*` | catalyst type, article_count, headline/source flags, `published_utc` | `published_utc <= t`; no prueba causalidad por si solo |
| `short_context__*` | short interest, short volume, source_system, lag model | no implica borrow, locate ni SSR |
| `short_constraints__*` | SSR active, borrow availability, locate status, fee | bloqueado hasta fuente broker/vendor/regulatoria |
| `halt__*` | halt/resume/suspension state, halt timestamps, halt context legal | solo si timestamp/event availability `<= t` |
| `regime__*` | SPY/QQQ/IWM/sector proxy, volatility/liquidity regime, session context | no usar close/regime final same-session antes de disponibilidad |

No debe usarse como:

```text
outcome
causalidad demostrada
feature sin lag/cutoff
shortability si solo hay short volume/interest
```

Lectura para el contrato de elegibilidad:

```text
Contexto as-of puede alimentar estado si demuestra disponibilidad legal en t.
Short context no equivale a borrow/locate/SSR. Float y live alerts siguen como
futuro o bloqueado hasta tener fuente, schema, namespace y cutoff.
```
## 3.11 Ejemplo De Bloqueado O Futuro

Short constraints:

```text
area = Short Constraints
source_column = borrow_fee_rate
status = blocked_no_materialized_table
```

Float:

```text
area = Float / Live Corporate Alerts
source_column = float_shares
status = future_no_namespace
```

Lectura humana:

```text
No todo lo deseable entra al estado hoy.
Algunas areas existen como target, otras como roadmap, y otras no tienen fuente o
namespace confirmado.
```

# 4. Regla Final De Esta Parte

La regla de cierre es:

```text
este documento organiza el mapa de estado
el contrato de elegibilidad decide columna por columna
el state builder solo puede usar observables aprobados por ese contrato
```

Y la barrera que no se debe cruzar es:

```text
shape/speed/pace, Attention, Crowding, thresholds o estados semanticos
no entran como columnas oficiales sin formula, fuente, cutoff, version y quality gate
```

Por tanto:

```text
market_state_table / event_state_table
= fotografia legal observable as-of

semantic representations / AlphaEvolve / RL / ML
= capas posteriores que usan esa fotografia bajo evaluadores bloqueados
```
# 5. Ruta Ordenada Hasta El Final

1. Cerrar `market_state_tables_status_and_operating_map_2026_07_01_v3.md`

   Objetivo: dejarlo como mapa humano. No meter mÃƒÂ¡s detalle tÃƒÂ©cnico ahÃƒÂ­.

2. Crear `state_observable_eligibility_contract_v0_1.md`

   Ruta:

   ```text
   C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\
   ```

3. Rellenar elegibilidad `Daily`

   Desde:

   ```text
   master_daily_table_schema_contract.md
   ```

   Resultado: columnas daily reales mapeadas a `daily__*`.

4. Rellenar elegibilidad `Intradia 1m`

   Desde:

   ```text
   master_intraday_bar_table_schema_contract.md
   master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
   ```

   Resultado: columnas 1m reales mapeadas a `intraday__*`.

5. Rellenar elegibilidad `Microestructura`

   Desde:

   ```text
   microstructure_features_table_schema_contract.md
   microstructure_features_table_multi_window_materialization_plan_v0_1.md
   ```

   Resultado: columnas quotes/trades/ventanas mapeadas a `microstructure__*`.

6. Rellenar elegibilidad `Contexto As-Of`

   Incluye:

   ```text
   fundamentals__
   news__
   short_context__
   regime__
   halt__
   short_constraints__
   float / live alerts
   ```

7. Rellenar elegibilidad `Soporte Legal / Quality / Lineage`

   Incluye:

   ```text
   identity__
   calendar__
   quality__
   lineage/support fields
   corporate actions support
   expected data coverage
   dataset gates
   ```

8. Cerrar `state_decision_timestamp_policy_v0_1.md` - DONE

   Define tipos de `t` y queda cerrado en el contrato de timestamp policy:

   ```text
   end_of_bar_t
   event_anchor_t
   entry_decision_t
   exit_decision_t
   halt_resume_t
   premarket_snapshot_t
   ```

9. Cerrar `state_snapshot_roles_contract_v0_1.md` - DONE

   Define roles y queda cerrado en el contrato de snapshot roles:

   ```text
   DISCOVERY_STATE
   EVENT_ANCHOR_STATE
   ENTRY_DECISION_STATE
   RISK_STATE
   EXECUTION_STATE
   RL_TRANSITION_STATE
   POST_EVENT_ANALYSIS_STATE
   ```

10. Ajustar `market_state_event_state_composition_contract_v0_1.md`

    Incorporar referencias explÃƒÂ­citas a:

    ```text
    state_observable_eligibility_contract_v0_1.md
    state_decision_timestamp_policy_v0_1.md
    state_snapshot_roles_contract_v0_1.md
    ```

11. Definir `market_state_table_v0_1` schema final candidate

    Ya no conceptual: columnas/namespaces concretos permitidos.

12. Definir `event_state_table_v0_1` schema final candidate

    Igual que market_state, pero anclado a evento/ventana/rol.

13. Construir fixture pequeÃƒÂ±o de `market_state_table`

    Pocas filas, casos controlados, validacion de cutoff y lineage.

14. Construir fixture pequeÃƒÂ±o de `event_state_table`

    Usando eventos/ventanas controladas.

15. Validadores de leakage

    Reglas duras:

    ```text
    no componente con as_of > decision_timestamp
    no outcomes inline
    no labels inline
    no scanner threshold como feature causal
    no daily close final antes de cierre
    ```

16. Validadores de calidad y lineage

    Comprobar:

    ```text
    source manifests
    schema versions
    quality gates
    missingness
    coverage
    build_run_id
    ```

17. Materializar candidate controlado de `market_state_table`

    No full universe todavÃƒÂ­a. Scope declarado.

18. Materializar candidate controlado de `event_state_table`

    Para eventos/estrategias concretas.

19. Crear `outcomes_table_v0_1` o contrato equivalente

    Separado de estado. Esto es `y`, no `X`.

20. Crear `event_window` / strategy event windows gobernados

    Para estrategia concreta:

    ```text
    pre_event
    trigger
    response
    same_session
    next_session
    ```

21. Crear evaluadores bloqueados

    Antes de AlphaEvolve/ML/RL:

    ```text
    retorno
    MFE/MAE
    slippage
    robustness
    leakage checks
    stability
    complexity
    ```

22. Crear `semantic_state_representation_candidate_contract_v0_1.md`

    Para cosas como:

    ```text
    liquidity_state
    attention
    crowding
    book_fragility
    ```

    Pero derivadas desde estado legal, no mezcladas con estado base.

23. Crear contrato AlphaEvolve

    Nombre sugerido:

    ```text
    alphaevolve_state_usage_contract_v0_1.md
    ```

    Regla:

    ```text
    AlphaEvolve no inventa la verdad observable.
    Solo muta representaciones, detectores, thresholds, transiciones o politicas
    usando estados legales y evaluadores bloqueados.
    ```

24. Crear tablas/run registry de AlphaEvolve

    Separadas de estado:

    ```text
    candidate_definition_table
    candidate_evaluation_table
    fitness_score_table
    mutation_history_table
    rejected_candidate_table
    ```

25. Crear transition/reward contracts para RL

    Solo despuÃƒÂ©s de tener:

    ```text
    state
    action
    outcome/reward
    timestamp policy
    leakage gates
    ```

26. Promocion controlada

    Promover solo si:

    ```text
    schemas cerrados
    contratos cerrados
    validators pasan
    fixtures reproducibles
    lineage completo
    quality gates claros
    no leakage
    ```

27. Uso cientÃƒÂ­fico

    Con todo lo anterior:

    ```text
    ML
    RL
    AlphaEvolve
    FACTORS / causalidad
    estadisticas de movimientos/eventos
    ```

Resumen corto:

```text
v3 mapa humano
-> contrato de elegibilidad
-> timestamp policy
-> state roles
-> schemas candidate
-> fixtures
-> validators
-> market_state/event_state candidate
-> outcomes/windows
-> evaluadores bloqueados
-> semantic representations
-> AlphaEvolve/RL/ML
```
# 6. Actualizacion 2026-07-04 - Avance Cerrado Y Siguiente Paso

Esta seccion actualiza la parte final del v3 despues de cerrar el primer contrato operativo que salia de este mapa.

## 6.1 Ya Hecho En Este Ciclo

Se creo y cerro el contrato:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
```

Estado del contrato:

```text
state_observable_eligibility_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
schemas/componentes fuente
-> columnas reales o grupos de columnas reales
-> observable final posible
-> cutoff/legalidad
-> quality gate
-> allowed usage
-> status de elegibilidad
```

Areas cubiertas:

```text
1. Daily
2. Intradia 1m
3. Microestructura
4. Contexto As-Of
   - fundamentals
   - news
   - short_context
   - regime
   - halts
5. Short Constraints / Float / Live Alerts
6. Soporte Legal / Calidad / Lineage
7. Prohibiciones explicitas
8. Requisitos del State Builder
```

Lectura correcta:

```text
El contrato no materializa datos.
El contrato no crea market_state_table ni event_state_table.
El contrato no habilita ML/RL/AlphaEvolve directamente.
El contrato si gobierna que observables puede consumir un futuro state builder.
```

La regla central queda fijada asi:

```text
estado base = fotografia legal del mundo observable en t
no = scanner, threshold ganador, outcome, label, reward, fill, PnL o accion
```

## 6.2 Que Cambia En La Ruta Original

En la ruta de la seccion 5, el paso de elegibilidad ya no esta pendiente.
Ahora el orden vivo pasa a ser:

```text
v3 mapa humano
-> state_observable_eligibility_contract_v0_1.md                 DONE
-> state_derived_observables_formula_contract_v0_1.md            DONE
-> state_decision_timestamp_policy_v0_1.md                       DONE
-> state_snapshot_roles_contract_v0_1.md                         DONE
-> state_builder_contract_v0_1.md                              DONE
-> event_candidate_tables_contract_v0_1.md                      DONE
-> daily_strategy_candidate_events_table_schema_contract.md      DONE
-> intraday_1m_strategy_candidate_events_table_schema_contract.md DONE
-> event_candidate_table_validators_contract_v0_1.md          DONE
-> state_canonical_vs_representation_layer_contract_v0_1.md   DONE
-> state_raw_to_consumption_lineage_contract_v0_1.md       DONE
-> state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md DONE controlled
-> state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md DONE upstream manifest lineage
-> preflight_master_intraday_quote_guarded_candidate.py              DONE passed
-> materialize_master_intraday_quote_guarded_candidate_sample.py      DONE controlled sample
-> materialize_master_intraday_quote_guarded_candidate_scoped.py      DONE scoped candidate
-> E-root scoped master_intraday_bar_table_v0_2_candidate_quote_guarded DONE not official
-> materialize_market_state_intraday_quote_guarded_candidate.py DONE controlled market_state intraday
-> leakage/formula/timestamp/role/builder validators
-> validators ejecutables de event_candidate_table             DONE fixture-scope
-> builders ejecutables de event_candidate_table                DONE fixture-scope
-> daily_strategy_candidate_events_table controlled materialization DONE
-> daily_strategy_candidate_events_table wider/E-root materialization PENDING
-> intraday_1m_strategy_candidate_events_table quote-guarded materialization DONE controlled
-> event_windows controlled daily expansion                    DONE controlled
-> event_windows controlled intradia expansion                DONE controlled
-> event_windows wider daily/1m expansion                       PENDING
-> controlled market_state intradia fixture                  DONE
-> controlled event_state intradia fixture                  DONE controlled
-> controlled outcomes intradia separados                  DONE controlled
-> controlled multi-component fixture                         PENDING
-> candidate materialization
-> evaluadores bloqueados
-> semantic representations
-> AlphaEvolve/RL/ML
```

## 6.3 Gate De Formulas Cerrado Y Siguiente Paso Inmediato

El contrato practico ya fue creado y cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
las derivadas no son libres;
cada formula necesita inputs, unidad, ventana, baseline, cutoff, missingness,
quality gate, lineage, status y version.
```

Tambien queda fijado que AlphaEvolve, ML, RL o estadisticas de estrategia pueden
proponer variantes, pero no modificar silenciosamente el estado base. Toda
variante ganadora debe entrar como observable candidato/versionado antes de
alimentar el state builder.

Siguiente paso inmediato:

```text
leakage/formula/timestamp/role/builder validators
controlled market_state/event_state fixture
```

Motivo:

```text
Ya sabemos que observables pueden entrar y como se calculan las derivadas v0.1.
Ahora falta fijar exactamente que timestamp/rol permite consumir cada observable.
```

## 6.4 Siguiente Paso En Paralelo, Pero No Antes De Formulas

El carril operativo que sigue vivo es:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

Motivo:

```text
1m reparado/quote-guarded desbloquea una base intradia defensible,
pero no materializa automaticamente los estados.
```

Este carril debe seguir como preflight/materializacion candidate, usando el repair manifest quote-guarded promovido y sin declarar full-universe final hasta pasar sus gates.

## 6.5 Documentos De Avance Actualizados

Este avance queda anotado en:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/CHANGELOG.md
C:/TSIS_Data/00_CTO/CHANGELOG.md
C:/TSIS_Data/00_CTO/GRAPHIFY_REFRESH_QUEUE.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
```

## 6.6 No Cambia Todavia

Sigue sin estar materializado/promovido:

```text
market_state_table_v0_1 oficial
event_state_table_v0_1 oficial
state builder oficial
ML-ready event-state dataset
RL transition/reward dataset
AlphaEvolve evaluator
semantic_state_representation_candidate
```

Conclusion:

```text
Hemos cerrado el gate de elegibilidad de observables y el gate de formulas/cutoffs de derivadas.
Ahora toca implementar validators de leakage/formula/timestamp/role/builder y despues un fixture/controlado multi-componente antes de construir estados oficiales.
```

## 6.7 Actualizacion Formulas Derivadas

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope
```

Lectura correcta:

```text
literal_or_derived no decide si algo es nuclear.
observable_role y formula contract deciden como se gobierna.
```

Queda completado:

```text
observable eligibility gate
formula/cutoff/unit/window gate para derivadas v0.1
```

No queda completado todavia:

```text
leakage/formula/timestamp/role/builder validators
controlled event_state / multi-component fixture
schema candidate alignment si hace falta
```

## 6.8 Ruta Por Capas Y Objetivo De Cada Paso

Esta ruta no es una lista de tablas ya materializadas. Es una secuencia de gates.
Cada paso responde una pregunta distinta y produce una salida que desbloquea el
paso siguiente. La regla es simple:

```text
no avanzar a materializacion si el contrato anterior no fija autoridad,
cutoff, rol, formula, schema, lineage y validator aplicable.
```

Ruta compacta:

```text
v3 mapa humano
-> state_observable_eligibility_contract_v0_1.md                 DONE
-> state_derived_observables_formula_contract_v0_1.md            DONE
-> state_decision_timestamp_policy_v0_1.md                       DONE
-> state_snapshot_roles_contract_v0_1.md                         DONE
-> state_builder_contract_v0_1.md                              DONE
-> event_candidate_tables_contract_v0_1.md                      DONE
-> daily_strategy_candidate_events_table_schema_contract.md      DONE
-> intraday_1m_strategy_candidate_events_table_schema_contract.md DONE
-> event_candidate_table_validators_contract_v0_1.md          DONE
-> state_canonical_vs_representation_layer_contract_v0_1.md   DONE
-> state_raw_to_consumption_lineage_contract_v0_1.md       DONE
-> state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md DONE controlled
-> state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md DONE upstream manifest lineage
-> preflight_master_intraday_quote_guarded_candidate.py              DONE passed
-> materialize_master_intraday_quote_guarded_candidate_sample.py      DONE controlled sample
-> materialize_master_intraday_quote_guarded_candidate_scoped.py      DONE scoped candidate
-> E-root scoped master_intraday_bar_table_v0_2_candidate_quote_guarded DONE not official
-> materialize_market_state_intraday_quote_guarded_candidate.py DONE controlled market_state intraday
-> leakage/formula/timestamp/role/builder validators
-> validators ejecutables de event_candidate_table             DONE fixture-scope
-> builders ejecutables de event_candidate_table                DONE fixture-scope
-> daily_strategy_candidate_events_table controlled materialization DONE
-> daily_strategy_candidate_events_table wider/E-root materialization PENDING
-> intraday_1m_strategy_candidate_events_table quote-guarded materialization DONE controlled
-> event_windows controlled daily expansion                    DONE controlled
-> event_windows controlled intradia expansion                DONE controlled
-> event_windows wider daily/1m expansion                       PENDING
-> controlled market_state intradia fixture                  DONE
-> controlled event_state intradia fixture                  DONE controlled
-> controlled outcomes intradia separados                  DONE controlled
-> controlled multi-component fixture                         PENDING
-> candidate materialization
-> evaluadores bloqueados
-> semantic_state_representation_contract_v0_1.md
-> semantic representations candidates
-> state_transition_contract_v0_1.md
-> transition datasets / transition evaluators
-> AlphaEvolve/RL/ML
```

### Lectura Por Paso

| Paso | Estado | Pregunta que cierra | Salida directa | Segunda derivada / desbloqueo | No permite todavia |
| --- | --- | --- | --- | --- | --- |
| `v3 mapa humano` | DONE | Que es estado y que no es estado en TSIS? | lectura humana: estado = fotografia legal observable en `t` | contratos operativos posteriores | no valida columnas, formulas ni materializa tablas |
| `state_observable_eligibility_contract_v0_1.md` | DONE | Que observable o familia puede existir legalmente como estado? | matriz de elegibilidad por area, namespace, uso, cutoff y status | formula contract, builder contract, validators | no calcula derivadas ni decide timestamp/rol final |
| `state_derived_observables_formula_contract_v0_1.md` | DONE | Como se calcula una derivada gobernada? | formulas, ventanas, unidades, baselines, missingness, quality gates y version | formula parity validators, builder determinista | no decide el decision timestamp ni el rol del snapshot |
| `state_decision_timestamp_policy_v0_1.md` | DONE | Cual es el `t` legal de cada snapshot y cada decision? | taxonomia de timestamps: decision, bar close, event anchor, entry, exit, halt, live received time | leakage gates y reglas de disponibilidad por componente | no compone estados ni elige columnas finales |
| `state_snapshot_roles_contract_v0_1.md` | DONE | Para que rol se toma el snapshot? | roles como discovery, event_anchor, entry_decision, risk, execution, rl_transition, post_event_analysis | schemas diferentes por rol y joins correctos a outcomes | no define estrategia ni outcome ganador |
| `state_builder_contract_v0_1.md` | DONE | Como se ensambla una fila de estado desde observables elegibles? | contrato de inputs, joins, namespaces, cutoff order, manifests y error handling | validators y fixture/controlado multi-componente | no promociona `market_state_table` ni `event_state_table` |
| `event_candidate_tables_contract_v0_1.md` | DONE | Donde entran las tablas de eventos daily/1m? | separa scanner candidates, event candidate tables, event windows y event_state | schema contracts daily/1m cerrados; validators/builders despues | no materializa eventos ni convierte scanner en estado |
| `daily_strategy_candidate_events_table_schema_contract.md` | DONE | Que columnas debe tener la tabla diaria de eventos candidatos? | schema canonico target, grano, columnas, timestamp policies, quality gates y non-goals | validators/builders de daily event candidates | no materializa la tabla ni contiene outcomes |
| `intraday_1m_strategy_candidate_events_table_schema_contract.md` | DONE | Que columnas debe tener la tabla 1m de eventos candidatos? | schema canonico target, timestamp 1m legal, quote-guarded promotion rule, quality gates y non-goals | validators/builders de intraday event candidates | no promociona raw-only ni contiene outcomes |
| `event_candidate_table_validators_contract_v0_1.md` | DONE | Que debe fallar antes de construir o consumir eventos candidatos? | contrato de validators comunes, daily, intradia, quote-guarded, lineage, prohibiciones y consumer gates | validators ejecutables y fixtures minimos | no materializa tablas ni valida outputs reales hasta que existan |
| `state_canonical_vs_representation_layer_contract_v0_1.md` | DONE | Que vive en Canonical State y que debe pasar a Representation Layer? | frontera formal entre fotografia observable estable y representaciones candidatas mutables | validators de estado/representacion y semantic state contract futuro | no cambia schemas ni materializa representaciones |
| `state_raw_to_consumption_lineage_contract_v0_1.md` | DONE | De donde sale cada componente desde RAW hasta consumo de estado? | contrato obligatorio de trazabilidad RAW/staged -> derivadas -> componente -> state builder -> consumer; ejemplo cerrado master_daily | validators de lineage y builders defensibles | no materializa tablas ni sustituye manifests reales |
| `state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md` | DONE controlled | De donde salen los 69 eventos daily y las 207 event_windows controladas? | lineage Camino A: master_daily -> scanner daily v0.3 -> daily events -> event windows | fixture controlado market_state/event_state | no cubre intradia 1m ni E-root official |
| `state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md` | DONE controlled consumption | De donde sale el 1m quote-guarded hasta `intraday__*` y eventos 1m controlados? | RAW 1m + repair manifest -> master intraday scoped E-root -> market_state intradia controlado -> intraday events controlados | event_windows intradia y fixture `event_state` | no cubre universo amplio, outcomes ni promocion oficial |
| `leakage/formula/timestamp/role/builder validators` | PENDING | Podemos probar que el estado no usa futuro, respeta formulas/roles y conserva lineage? | tests de cutoff, formula parity, role/window gates, quality gates, manifests y source roots | candidate materialization defensible | no decide valor cientifico de una estrategia |
| `validators ejecutables de event_candidate_table` | DONE fixture-scope + controlled tables | Podemos ejecutar esos checks sobre fixtures/tablas candidatas? | CLI `validate_event_candidate_tables.py`, fixtures minimos y runs controlados daily/intradia passed | builders diarios/1m defensibles y validator run sobre wider/full-universe cuando exista | no promociona eventos, estados ni outcomes |
| `builders ejecutables de event_candidate_table` | DONE fixture-scope | Podemos convertir fuentes upstream en tablas de eventos gobernadas? | CLI `materialize_strategy_candidate_events_table.py`, parquet/manifest/summary para daily o intradia 1m y tests fixture-scope | run sobre daily scanner real y ruta intradia quote-guarded real | no promociona tablas oficiales ni valida universo real |
| `daily_strategy_candidate_events_table controlled materialization` | DONE controlled | Que eventos daily quedan anclados por definicion versionada en replay controlado? | 69 filas desde `daily_scanner_candidates_table_v0_3` replay 2025-01-02..2025-01-10; validator passed | event_windows expansion daily controlada | no es full-universe, no es E-root oficial, no contiene outcomes |
| `daily_strategy_candidate_events_table wider/E-root materialization` | PENDING | Que eventos daily quedan anclados para scope mas amplio/gobernado? | rerun del builder sobre fuente daily scanner decidida | event_windows expansion daily amplia | no sustituye state/event/outcomes |
| `intraday_1m_strategy_candidate_events_table quote-guarded materialization` | DONE controlled | Que eventos 1m quedan anclados con timestamp legal? | 5 eventos desde `master_intraday_bar_table_v0_2_candidate_quote_guarded` scoped E-root; validator passed | event_windows expansion intradia | no es full-universe, no promociona raw-only, no contiene outcomes |
| `event_windows controlled daily expansion` | DONE controlled | Que ventanas se abren alrededor de los 69 eventos daily controlados? | `event_windows_table_v0_1_candidate_daily_strategy_events`, 207 filas, validator passed | controlled event_state fixture | no es tabla oficial, no es full-universe, no cubre intradia 1m |
| `event_windows controlled intradia expansion` | DONE controlled | Que ventanas se abren alrededor de los 5 eventos intradia quote-guarded? | 15 ventanas: pre_event_30m, event_anchor_1m, post_event_30m; validator passed | controlled event_state fixture | no es full-universe, no sustituye event_state ni outcomes |
| `event_windows wider daily/1m expansion` | PENDING | Que ventanas se abren alrededor de eventos daily amplios o intradia 1m no-halt en scope amplio? | event windows candidate desde daily/1m event tables gobernadas | event_state fixture mas amplio | no sustituye event_state ni outcomes |
| `controlled market_state intradia fixture` | DONE controlled | Podemos consumir `intraday__*` desde el E-root scoped quote-guarded sin leakage? | `market_state_table_v0_1_candidate_intraday_quote_guarded_controlled`, 10.835 filas, validator passed | fixture event_state/multi-componente | no es oficial, no es full-universe, no contiene eventos ni outcomes |
| `controlled event_state intradia fixture` | DONE controlled | Podemos anclar estado intradia a evento/ventana sin leakage? | 15 filas desde market_state intradia quote-guarded + 15 event_windows intradia; validator passed | outcomes separados | no es universo completo ni dataset ML/RL |
| `controlled outcomes intradia separados` | DONE controlled | Que paso despues sin contaminar `X`? | 5 filas `outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled`; 3 good, 2 review por barras faltantes; validator passed | evaluadores bloqueados y labels/rewards gobernados | no es full-universe, no es ML label, no es RL reward, no es execution truth |
| `controlled multi-component fixture` | PENDING | Podemos mezclar componentes adicionales sin leakage? | fixture con micro/contexto/fundamentals/news/short/regime declarados | candidate materialization mas rica | no es universo completo ni dataset ML/RL |
| `candidate materialization` | PENDING | Podemos producir parquet/manifest candidate bajo contrato? | `market_state_table`/`event_state_table` candidate con manifest | outcomes/evaluadores amplios | no es promocion oficial ni ML-ready automatico |
| `outcomes separados wider/unified` | PENDING | Que outcomes faltan fuera del scope controlado 1m? | daily/1m unificados, labels gobernados, rewards y execution outcomes bajo contrato | evaluadores bloqueados y datasets ML/RL especificos | nunca deben ir inline dentro del estado base |
| `evaluadores bloqueados` | PENDING | Como se compara objetivamente una hipotesis/candidato? | fitness, leakage checks, robustness, costs, stability, complexity | AlphaEvolve/ML/RL con feedback reproducible | no puede cambiar la verdad observable base |
| `semantic_state_representation_contract_v0_1.md` | FUTURE | Como se transforma estado observable en representacion semantica/latente? | contrato para objetos como Attention, Liquidity Stress, Crowding, Fragility | semantic representation candidates | no entra en `market_state_table` base como verdad primaria |
| `semantic representations candidates` | FUTURE | Que representaciones candidatas se pueden evaluar? | vectores, ontologias o scores semanticos versionados | transition contracts, policies, evaluadores | no son observables base; son interpretaciones derivadas |
| `state_transition_contract_v0_1.md` | FUTURE | Como se gobierna `state(t) -> state(t+k)`? | schema de transicion, horizonte, sampling, legalidad y estado origen/destino | transition datasets, offline RL, causalidad, pattern discovery | no equivale a outcome ni reward por si solo |
| `transition datasets / transition evaluators` | FUTURE | Como se entrenan/evaluan secuencias de estado? | datasets y evaluadores de trayectoria bajo cutoff | RL, causal discovery, AlphaEvolve transition functions | no define politica operativa automaticamente |
| `AlphaEvolve/RL/ML` | FUTURE | Como se buscan formulas, representaciones, detectores, transiciones o politicas mejores? | candidatos versionados + resultados de evaluador | promocion/rechazo de hipotesis | no puede mutar contratos oficiales ni introducir leakage silencioso |

### Regla De Dependencia

La dependencia correcta no es solo tecnica; es epistemologica:

```text
observable legal
-> formula legal
-> frontera Canonical State vs Representation Layer
-> timestamp legal
-> rol legal
-> builder reproducible
-> estado candidate
-> outcome separado
-> evaluador bloqueado
-> representacion/transicion/politica candidata
```

Por eso `semantic_state_representation_contract_v0_1.md` y
`state_transition_contract_v0_1.md` son importantes, pero no deben adelantarse al
state builder. Si se adelantan, Attention, Liquidity Stress, Crowding o
Transitions pueden acabar contaminando el estado base como si fueran verdades
observables.

### Que Puede Mutar AlphaEvolve Mas Adelante

AlphaEvolve no debe mutar la fotografia legal del mundo observable en `t`.
Puede proponer candidatos versionados sobre capas posteriores:

```text
1. formulas derivadas candidatas
2. representaciones semanticas del estado
3. detectores de eventos
4. funciones de transicion entre estados
5. politicas de decision
```

Cada mutacion que sobreviva debe volver al sistema como contrato candidato,
con fuente, formula/modelo, cutoff, version, tests, evaluador y decision de
promocion separada.
## 6.9 Actualizacion Decision Timestamp Policy

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
state_decision_timestamp_policy_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
que significa t;
que diferencia hay entre observation time, availability time, received time,
state_cutoff_utc, decision_timestamp_utc y build_created_at_utc;
que ventanas pueden alimentar X pre-decision;
que ventanas pertenecen a post-analysis/outcomes/evaluators;
que leakage gates temporales debe implementar el builder/validator.
```

Siguiente paso inmediato:

```text
leakage/formula/timestamp/role/builder validators
controlled market_state/event_state fixture
```

Motivo:

```text
Ya sabemos que observables pueden entrar, como se calculan las derivadas y cual
es el reloj legal. Ahora falta fijar para que rol se toma cada snapshot y que
joins quedan permitidos por rol.
```
## 6.10 Actualizacion State Snapshot Roles

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
state_snapshot_roles_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
que significa state_role;
que roles canonicos existen en v0.1;
que timestamp types puede usar cada rol;
que ventanas puede mirar cada rol;
que usos ML/RL/AlphaEvolve son candidatos, restringidos o futuros;
que outcomes, labels, rewards y actions no pueden ir inline en estado base;
que validators de rol debe implementar el builder.
```

Siguiente paso inmediato:

```text
leakage/formula/timestamp/role/builder validators
controlled market_state/event_state fixture
controlled market_state/event_state fixture
```

Motivo:

```text
Ya sabemos que observables pueden entrar, como se calculan, cual es el reloj
legal y para que rol se toma cada snapshot. Ahora falta definir como el builder
ensambla filas reales y como se validan leakage, calidad, lineage y roles.
```

## 6.11 Actualizacion State Builder Contract

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
state_builder_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
como se ensambla una fila market_state/event_state;
que inputs normativos debe consumir el builder;
que config minima debe declarar;
como se seleccionan componentes por cutoff/as-of;
como se consumen eligibility, formulas, timestamps y roles;
que manifest debe emitir;
que validators deben cerrar el siguiente paso;
que los candidatos existentes son integration proof, no tabla oficial.
```

Siguiente paso inmediato:

```text
leakage/formula/timestamp/role/builder validators
controlled market_state/event_state fixture o sample multi-componente
schema candidate alignment si hace falta por roles canonicos vs aliases legacy
```

Motivo:

```text
Ya sabemos que observables pueden entrar, como se calculan, cual es el reloj
legal, para que rol se toma cada snapshot y como debe ensamblarlos el builder.
Ahora falta probarlo con validators ejecutables y fixture/candidate controlado.
```

No desbloquea todavia:

```text
market_state_table oficial
event_state_table oficial
ML/RL training directo
AlphaEvolve evaluator production
semantic state representation candidate
state transition dataset
```
## 6.12 Actualizacion Event Candidate Tables Daily / 1m

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
event_candidate_tables_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
donde entran las tablas de eventos daily y 1m;
por que scanner candidates no son eventos;
por que event windows no sustituyen a event tables;
que targets nuevos necesitamos:
  daily_strategy_candidate_events_table_v0_1
  intraday_1m_strategy_candidate_events_table_v0_1
que campos minimos debe tener un evento candidato;
como se versionan thresholds y definiciones de evento;
como se conectan eventos -> event_windows -> event_state -> outcomes.
```

Lectura correcta:

```text
daily_scanner_candidates_table
= donde mirar / denominador candidato diario

intraday_scanner_candidates_table
= donde mirar / detecciones intradia candidatas

daily_strategy_candidate_events_table
= eventos daily con event_id y ancla legal

intraday_1m_strategy_candidate_events_table
= eventos 1m con event_id y event_timestamp_utc

event_windows_table
= ventanas alrededor de esos eventos

event_state_table
= fotografia legal observable anclada al evento/ventana/rol
```

Siguiente paso inmediato:

```text
leakage/formula/timestamp/role/builder validators
event candidate table executable validators
builders/materializacion para daily_strategy_candidate_events_table_v0_1
builders/materializacion para intraday_1m_strategy_candidate_events_table_v0_1
event_windows expansion para source_event_table != halts_table_v0_1
controlled event_state fixture con eventos daily/1m
```

No desbloquea todavia:

```text
event candidate tables oficiales/full-universe
market_state_table oficial
event_state_table oficial
ML/RL training directo
AlphaEvolve evaluator production
outcomes inline
```
## 6.13 Actualizacion Schema Contracts De Event Candidate Tables

Nuevos schema contracts cerrados:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
daily_strategy_candidate_events_table_schema_contract_v0_1 = complete_for_contract_defined_scope

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
intraday_1m_strategy_candidate_events_table_schema_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelven:

```text
que columnas minimas debe tener cada tabla de eventos candidata;
cual es su grano y primary key;
como se separan scanner, evento, event_windows, event_state y outcomes;
que timestamp policies son legales;
que lineage debe conservarse;
que reglas evitan outcomes/labels/rewards inline;
que condiciones bloquean materializacion;
que la ruta intradia canonica debe ser quote-guarded, no raw-only.
```

Lectura correcta:

```text
schema contract DONE
builder/materializacion DONE controlled para daily e intradia quote-guarded
validators DONE fixture-scope y tabla controlada; wider/full-universe PENDING
```

Esto empezo como cierre de schema. Ahora ya existen outputs controlados/no oficiales para daily e intradia quote-guarded; siguen pendientes los scopes wider/full-universe y la promocion oficial.

Siguiente paso inmediato:

```text
outcomes separados usando `event_state` intradia controlado y ventanas post-event con eventos daily/1m
wider/full-universe daily/intradia solo despues de validators/review
```

No desbloquea todavia:

```text
event candidate tables oficiales/full-universe
market_state_table oficial
event_state_table oficial
ML/RL training directo
AlphaEvolve evaluator production
outcomes inline
```
## 6.14 Actualizacion Event Candidate Table Validators Contract

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
event_candidate_table_validators_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
que debe fallar antes de construir o consumir tablas de eventos candidatas;
que severidades existen: hard_fail, review_fail, warning, info;
que validators comunes aplican a daily e intradia;
que validators especificos aplican a daily date-level;
que validators especificos aplican a intradia 1m y quote-guarded;
que outcomes, labels, rewards, fills, PnL y acciones siguen prohibidos inline;
que consumer gates ML/RL/AlphaEvolve siguen cerrados;
que full_universe/materializacion oficial sigue bloqueado sin promotion barrier.
```

Lectura correcta:

```text
validators contract DONE
validators ejecutables DONE fixture-scope y tabla controlada
builders/materializacion DONE controlled; wider/full-universe PENDING
```

Siguiente paso inmediato:

```text
event_windows intradia desde la tabla quote-guarded controlada
controlled event_state fixture con eventos daily/1m
wider/full-universe daily/intradia solo despues de validators/review
controlled event_state fixture con eventos daily/1m
```

No desbloquea todavia:

```text
event candidate tables oficiales/full-universe
market_state_table oficial
event_state_table oficial
ML/RL training directo
AlphaEvolve evaluator production
outcomes inline
```
## 6.15 Actualizacion Canonical State Vs Representation Layer Contract

Nuevo contrato cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
state_canonical_vs_representation_layer_contract_v0_1 = complete_for_contract_defined_scope
```

Que resuelve:

```text
que Canonical State no es raw-only;
que Canonical State tampoco es una feature table experimental;
que una derivada mecanica estable puede ser estado si tiene formula, cutoff,
quality y lineage;
que parameter grids, scores, embeddings, semantic states y thresholds optimizados
viven primero en Representation Layer;
que AlphaEvolve puede mutar representaciones, detectores, transiciones,
politicas y evaluadores, pero no puede mutar silenciosamente la verdad observable
canonica;
que una representacion candidata solo puede moverse hacia Canonical State con
promocion formal, contrato, formula/modelo, cutoff, evidencia y validators.
```

Lectura correcta:

```text
Canonical State = tablero estable y legal del laboratorio.
Representation Layer = espacio de busqueda y experimentacion.
AlphaEvolve/RL/ML = consumidores o generadores de candidatos sobre ese tablero.
```

Esto no cambia todavia:

```text
schemas oficiales de market_state/event_state
materializacion de state tables
materializacion de semantic representations
validacion sobre tablas reales no materializadas
ML/RL/AlphaEvolve production
```

Siguiente paso inmediato sigue siendo:

```text
construir builders/materializacion candidate daily/1m;
ejecutar validators de event candidate sobre esos outputs reales;
implementar leakage/formula/timestamp/role/builder validators;
crear fixture controlado market_state/event_state despues de event_windows.
```

Impacto en la ruta futura:

```text
controlled market_state/event_state fixture
-> Canonical State claramente separado de Representation Layer
-> semantic_state_representation_contract_v0_1.md
-> semantic representation candidates
-> state_transition_contract_v0_1.md
-> transition datasets / transition evaluators
-> AlphaEvolve/RL/ML
```
## 6.16 Actualizacion Event Candidate Executable Validators Fixture-Scope

Nuevo avance cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/validate_event_candidate_tables.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_event_candidate_table_validators.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/fixtures/data_foundation_outputs/event_candidate_tables_v0_1/
event_candidate_table_executable_validators_fixture_scope = passed
```

Tests ejecutados:

```text
python -m pytest tests/data_foundation_outputs/test_event_candidate_table_validators.py -q
7 passed
```

Que resuelve:

```text
el contrato de validators ya tiene una primera implementacion ejecutable;
el validator puede leer fixtures JSON/JSONL o parquet;
el fixture daily bueno pasa;
el fixture intradia quote-guarded bueno pasa;
los fixtures malos bloquean outcome inline, claim intradia daily sin fuente,
raw-only intradia promovido y cutoff/barra futura;
el output mantiene ML/RL/AlphaEvolve production deshabilitados.
```

Lectura correcta:

```text
validator executable + fixtures = DONE
validator run sobre tablas controladas daily/intradia = DONE; wider/full-universe = PENDING
```

Motivo:

```text
Ya existen materializaciones controladas/no oficiales de `daily_strategy_candidate_events_table_v0_1` y `intraday_1m_strategy_candidate_events_table_v0_1`, y el validator paso sobre ambas. Lo que sigue pendiente es la certificacion de runs wider/full-universe y cualquier promocion oficial.
```

Siguiente paso inmediato:

```text
outcomes separados usando `event_state` intradia controlado y ventanas post-event con eventos daily/1m
wider/full-universe daily/intradia solo despues de validators/review
```
## 6.17 Actualizacion Event Candidate Builders Fixture-Scope

Nuevo avance cerrado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_strategy_candidate_events_table.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_strategy_candidate_events_table_builder.py
event_candidate_table_builders_fixture_scope = passed
```

Tests ejecutados:

```text
python -m pytest tests/data_foundation_outputs/test_strategy_candidate_events_table_builder.py tests/data_foundation_outputs/test_event_candidate_table_validators.py -q
10 passed
```

Que resuelve:

```text
existe un builder ejecutable para daily_strategy_candidate_events_table_v0_1;
existe un builder ejecutable para intraday_1m_strategy_candidate_events_table_v0_1;
el builder escribe parquet, manifest, summary y validator summary;
el builder diario convierte fuentes scanner/directas seleccionadas en eventos gobernados;
el builder intradia exige ruta quote-guarded confirmada para filas candidatas;
raw-only intradia no puede promoverse como candidate si no hay confirmacion quote-guarded;
ML/RL/AlphaEvolve production siguen deshabilitados.
```

Lectura correcta:

```text
builder executable + fixtures = DONE
materializacion controlada daily = DONE
materializacion controlada sobre fuente intradia quote-guarded = DONE; wider/full-universe intradia = PENDING
validator run sobre tablas controladas = DONE; wider/full-universe = PENDING
```

Siguiente paso inmediato:

```text
expandir event_windows intradia desde la tabla controlada quote-guarded;
mantener pendiente el scanner intradia v0_2 quote-guarded completo;
ejecutar wider/full-universe daily/intradia solo despues de validators/review;
construir controlled event_state fixture despues de tener ventanas intradia.
```
## 6.18 Actualizacion Daily Strategy Candidate Events Controlled Materialization

Nuevo avance cerrado:

```text
C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/
daily_strategy_candidate_events_table_v0_1_controlled_candidate = passed
```

Fuente upstream:

```text
C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/parts/year=2025/daily_scanner_candidates_table_v0_3_candidate_replay/data.parquet
```

Salida:

```text
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/daily_strategy_candidate_events_table_v0_1_candidate/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/_daily_strategy_candidate_events_table_v0_1_manifest_candidate.json
summary = C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/_daily_strategy_candidate_events_table_v0_1_summary_candidate.csv
```

Evidencia:

```text
source_rows = 15323
selected_source_rows = 69
event_candidate_rows = 69
validator_status = passed
validator_hard_fail_count = 0
validator_review_fail_count = 0
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
alphaevolve_production_enabled_rows = 0
```

Lectura correcta:

```text
daily event candidate controlled materialization = DONE
wider/E-root daily materialization = PENDING
intraday quote-guarded event candidate materialization = DONE controlled
event_windows controlled daily expansion = DONE controlled
event_windows wider daily/1m expansion = PENDING
```

No desbloquea todavia:

```text
market_state_table oficial
event_state_table oficial
ML/RL datasets
AlphaEvolve production evaluator
outcomes inline
```

## 6.19 Actualizacion Daily Strategy Event Windows Controlled Candidate

Nuevo avance cerrado:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/
event_windows_table_v0_1_candidate_daily_strategy_events = passed
```

Builder ejecutable:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_strategy_event_windows_candidate.py
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_daily_strategy_event_windows_candidate_builder.py
```

Fuente upstream:

```text
C:/TSIS_Data/tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/daily_strategy_candidate_events_table_v0_1_candidate/data.parquet
```

Salida:

```text
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/event_windows_table_v0_1_candidate_daily_strategy_events/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/_event_windows_table_v0_1_candidate_daily_strategy_events_manifest.json
summary = C:/TSIS_Data/tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/_event_windows_table_v0_1_candidate_daily_strategy_events_summary.csv
```

Evidencia:

```text
source_event_count = 69
calendar_covered_event_count = 69
row_count = 207
window_role_counts = prior_session_regular: 69, event_session_regular: 69, next_session_regular: 69
ml_feature_candidate_rows = 69
outcome_window_candidate_rows = 69
rl_state_component_candidate_rows = 0
full_universe_claim_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
Camino A queda cerrado en su primera expansion:
69 eventos daily controlados -> 207 event_windows controladas.

prior_session_regular = ventana pre-evento utilizable como feature candidate controlada
event_session_regular = ventana de sesion del evento, no ML pre-event
next_session_regular = ventana candidata de outcome, separada del estado
```

No es:

```text
event_windows_table_v0_1 oficial
materializacion E-root
full-universe
intraday 1m quote-guarded
event_state_table
outcomes table
dataset ML/RL/AlphaEvolve listo
```

Siguiente paso operativo:

```text
usar este output controlado para construir controlled market_state/event_state fixture
mantener wider/E-root daily e intradia 1m quote-guarded como carriles pendientes separados
```

## 6.20 Actualizacion Trazabilidad RAW -> Consumo De Estado

Nueva regla institucional cerrada:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
state_raw_to_consumption_lineage_contract_v0_1 = complete_for_contract_defined_scope
```

Lectura correcta:

```text
Toda tabla, componente o derivada que alimente market_state/event_state debe poder explicar su cadena:
RAW/staged -> derived view -> governed component -> event/scanner/window si aplica -> state builder -> consumer final.
```

A partir de ahora cada contrato nuevo o revisado debe incluir una seccion:

```text
## Trazabilidad RAW -> Consumo De Estado
```

Esa seccion debe mostrar:

```text
fuentes RAW/staged;
fuentes derivadas intermedias;
builders/scripts/configs;
manifest/summary/hash/build_run_id;
columnas literales y derivadas;
cutoff/as-of;
quality/coverage gates;
consumo permitido;
no-goals;
evidencia de validacion;
gaps abiertos.
```

Primer ejemplo cerrado en el contrato:

```text
master_daily_table_v0_1
E:/TSIS/data/ohlcv_daily
+ E:/TSIS/data/ohlcv_daily_adjusted
+ expected_data_calendar
+ corporate_actions_table
+ dataset_certification_matrix
-> scripts/materialize_master_daily_table.py
-> E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
-> daily__* para futuros market_state/event_state builders
```

Regla para AlphaEvolve/RL/ML:

```text
pueden mutar formulas, representaciones, detectores, transiciones o politicas;
no pueden mutar silenciosamente la verdad de lineage.
```

Siguiente trabajo practico:

```text
la ruta intradia 1m quote-guarded ya llega hasta un fixture controlado de `market_state_table_v0_1_candidate` con `intraday__*`. Para el siguiente salto quedan pendientes microestructura/contexto as-of si entran en un fixture multi-componente, `event_state` anclado a eventos/ventanas y scope wider/declared-universe antes de cualquier promocion oficial.
```

Actualizacion Camino A controlado:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md
state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1 = complete_for_controlled_scope
```

Cubre:

```text
master_daily_table_v0_1 + instrument_master + market_calendar + scanner definitions
-> daily_scanner_candidates_table_v0_3_candidate_replay
-> daily_strategy_candidate_events_table_v0_1 controlled candidate
-> event_windows_table_v0_1_candidate_daily_strategy_events
-> futuro controlled market_state/event_state fixture
```

Lectura correcta:

```text
trazabilidad diaria EOD controlada = cerrada;
intradia 1m quote-guarded upstream manifest lineage = DONE; lightweight preflight = passed; controlled sample materialization = passed_not_official; scoped candidate materialization = passed_not_official; E-root scoped candidate materialization = passed_not_official; controlled market_state intradia fixture = passed_not_official; wider/declared-universe materialization = pendiente;
E-root official = pendiente;
ML/RL/AlphaEvolve = pendiente.
```



## 6.11 Actualizacion 2026-07-05 - Market State Intradia Controlado

Controlled market_state intradia 1m quote-guarded materializado:

```text
script = scripts/materialize_market_state_intraday_quote_guarded_candidate.py
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
output = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/market_state_table_v0_1_candidate_intraday_quote_guarded_controlled
status = controlled_candidate_not_promoted
source_quote_guarded_intraday_rows = 10835
state_rows = 10835
ticker_count = 3
quote_guarded_repair_applied_rows = 96
qg_ohlc_changed_rows = 96
manifest_qg_diff_not_applied_rows = 10
full_universe_claim_rows = 0
ml_candidate_rows = 0
rl_candidate_rows = 0
execution_truth_rows = 0
intraday_as_of_after_decision_rows = 0
bar_end_decision_timestamp_mismatch_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta: este fixture prueba consumo `intraday__*` desde el E-root scoped candidate quote-guarded hacia `market_state_table_v0_1_candidate`. No es tabla oficial, no es full-universe, no tiene evento, no contiene outcomes y no habilita ML/RL/AlphaEvolve.

Siguiente paso optimo:

```text
1. no ampliar todavia a full/wider 1m sin validar consumo de estado;
2. usar este fixture intradia como prueba de `intraday__*` legal;
3. construir despues un fixture `event_state` o multi-componente con ventanas/eventos gobernados;
4. mantener outcomes/evaluadores/AlphaEvolve separados.
```

## 6.21 Actualizacion Intraday 1m Strategy Candidate Events Quote-Guarded Controlled

Nuevo avance cerrado:

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/
source_candidates = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_source_candidates.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/_intraday_1m_strategy_candidate_events_from_master_intraday_qg_manifest.json
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/intraday_1m_strategy_candidate_events_table_v0_1_candidate/data.parquet
event_table_manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled/event_candidate_table/_intraday_1m_strategy_candidate_events_table_v0_1_manifest_candidate.json
status = controlled_candidate_not_promoted
```

Definicion de evento usada en este run controlado:

```text
event_definition_id = intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1
event_definition_version = v0_1
event_family = intraday_first_motion_threshold_cross_candidate
event_type = first_motion_threshold_cross
threshold_pct = 50.0
```

Evidencia:

```text
source_quote_guarded_bar_rows = 10835
source_raw_bar_rows = 10835
source_session_count = 58
selected_source_row_count = 5
event_candidate_rows = 5
validator_status = passed
validator_hard_fail_count = 0
validator_review_fail_count = 0
full_universe_claim_true_rows = 0
ml_feature_candidate_rows = 0
rl_state_candidate_rows = 0
alphaevolve_production_enabled_rows = 0
```

Eventos anclados:

```text
AAGR 2023-12-08 2023-12-08T09:29:00Z premarket trigger_price=12.00 move_vs_segment_open=73.913043
AAGR 2023-12-14 2023-12-14T11:18:00Z premarket trigger_price=1.14 move_vs_segment_open=53.020134
AAGR 2023-12-19 2023-12-19T17:30:00Z regular trigger_price=0.75 move_vs_segment_open=59.472677
AAGR 2023-12-20 2023-12-20T18:15:00Z regular trigger_price=1.12 move_vs_segment_open=51.351351
AAMC 2023-12-06 2023-12-06T22:59:00Z afterhours trigger_price=5.85 move_vs_segment_open=75.675676
```

Lectura correcta:

```text
intraday_1m_strategy_candidate_events_table quote-guarded controlled = DONE
wider/full-universe intraday materialization = PENDING
intraday event_windows expansion = DONE controlled
```

El umbral `+50%` no entra como estado base ni como verdad privilegiada. Aqui vive en una `event_definition_id` versionada para abrir ventanas y estudiar outcomes despues. La tabla resultante es una tabla de eventos candidatos, no `market_state_table`, no `event_state_table`, no full-universe, no ML/RL/AlphaEvolve-ready y no contiene outcomes.

## 6.22 Actualizacion Intraday 1m Strategy Event Windows Controlled

Nuevo avance cerrado:

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_event_windows_candidate.py
test = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_strategy_event_windows_candidate_builder.py
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json
status = controlled_candidate_not_promoted
```

Evidencia:

```text
source_event_count = 5
row_count = 15
window_role_counts = event_anchor_1m: 5, post_event_30m: 5, pre_event_30m: 5
validator_status = passed
validator_hard_fail_count = 0
full_universe_claim_rows = 0
ml_feature_candidate_rows = 5
outcome_window_candidate_rows = 5
microstructure_feature_candidate_rows = 15
rl_state_component_candidate_rows = 0
```

Lectura correcta:

```text
event_windows intradia controlled = DONE
event_state fixture = NEXT
outcomes separados = despues de event_state/ventanas
wider/full-universe = PENDING
```

Regla de leakage:

```text
pre_event_30m = feature-safe, termina en event_timestamp_utc
event_anchor_1m = ancla/decision, no feature pre-evento
post_event_30m = frontera de outcome, no X
```

Esta tabla candidata no es `event_windows_table_v0_1` oficial, no es full-universe, no contiene outcomes y no habilita ML/RL/AlphaEvolve.

## 6.23 Actualizacion Event State Intraday 1m Quote-Guarded Controlled

Nuevo avance cerrado:

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
test = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_event_state_intraday_quote_guarded_candidate_builder.py
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
status = controlled_candidate_not_promoted
```

Evidencia:

```text
source_event_window_rows = 15
joined_event_state_rows = 15
missing_market_state_window_rows = 0
event_count = 5
event_window_count = 15
market_state_count = 15
ticker_count = 2
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
state_quality_counts = event_state_review_scoped_intraday_component: 15
valid_for_pattern_discovery_rows = 15
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
valid_for_rl_training_direct_rows = 0
execution_truth_rows = 0
full_universe_claim_rows = 0
contains_future_information_without_event_filter_rows = 5
validator_status = passed
validator_hard_fail_count = 0
```

Lectura correcta:

```text
controlled event_state intradia = DONE
outcomes separados intradia controlados = DONE
event_research_design_contract_v0_1 = DONE; sampling_probe/window/parameter_sweep = NEXT antes de evaluadores bloqueados
wider/full-universe = PENDING
```

`post_event_review` queda marcado con informacion posterior y nunca como feature ML. No hay `outcome__*`, `label__*`, `reward__*`, acciones, fills, PnL ni signals inline.



## 6.24 Actualizacion Outcomes Intraday 1m Quote-Guarded Controlled

Nuevo avance cerrado:

```text
script = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_event_outcomes_candidate.py
test = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_event_outcomes_candidate_builder.py
run_root = C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled/
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled/outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled/_outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_manifest.json
status = controlled_candidate_not_promoted
```

Evidencia:

```text
source_event_state_rows = 15
source_event_window_rows = 15
post_event_window_rows = 5
reference_anchor_event_state_rows = 5
outcome_rows = 5
event_count = 5
ticker_count = 2
outcome_horizon = post_event_30m_intraday_1m
price_view = 1m_quote_guarded_raw
quality_counts = good_intraday_1m_outcome: 3, review_intraday_missing_bars: 2
good_intraday_1m_outcome_rows = 3
review_intraday_missing_bars_rows = 2
valid_for_outcome_research_rows = 5
valid_for_backtest_outcome_candidate_rows = 3
valid_for_ml_label_candidate_rows = 0
valid_for_rl_reward_candidate_rows = 0
bars_expected_total = 150
bars_observed_total = 134
quote_guarded_repair_applied_rows_total = 9
full_universe_claim_rows = 0
execution_truth_rows = 0
validator_status = passed
validator_hard_fail_count = 0
```

Regla de referencia:

```text
reference_price = close quote-guarded del event_state at_event
outcome_window = post_event_30m
barras = master_intraday_bar_table_v0_2_candidate_quote_guarded con ts_utc dentro de la ventana
```

Lectura correcta:

```text
outcomes intradia controlados = DONE
labels ML = bloqueados hasta label contract
rewards RL = bloqueados hasta reward/action contract
event_research_design_contract_v0_1 = DONE; sampling_probe/window/parameter_sweep = NEXT antes de evaluadores bloqueados
wider/full-universe = PENDING
```

Esta tabla candidata es `y`, no `X`. No debe copiarse dentro de `market_state_table` ni `event_state_table`. MFE, MAE y returns son informacion posterior; se unen despues para investigacion/evaluacion, nunca como feature pre-evento.


## 6.25 Actualizacion 2026-07-05 - Event Research Design Layer

Nuevo contrato creado:

```text
contract = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_research_design_contract_v0_1.md
status = contract_defined
research_design_layer_defined = true
```

Correccion conceptual importante:

```text
la unidad basica del laboratorio no es el evento
la unidad basica del laboratorio es el experimento
```

Lectura actualizada:

```text
+50% = sampling_probe_human_seed
pre_event_30m = sampling_window_controlled_seed
post_event_30m = sampling_window_controlled_seed
```

Esto significa que el `+50%` usado en el run intradia controlado no es una
verdad cientifica, no es edge, no es evento validado y no es estrategia. Es un
instrumento humano de muestreo para encontrar movimientos historicos grandes y
estudiar casos.

Del mismo modo, las ventanas de 30 minutos no son ventanas demostradas
estadisticamente. Son ventanas controladas razonables para empezar a observar
antes y despues del probe.

Regla de laboratorio:

```text
sampling_probe
-> parameter_sweep
-> exploratory_statistics
-> event_family_candidate
-> validation_protocol
-> validated_event_definition
-> locked_evaluator
```

Por tanto, el siguiente paso real ya no es saltar directamente a evaluadores
bloqueados. Antes hay que disenar y materializar la capa de investigacion de
eventos.

Ruta corregida:

```text
controlled outcomes intradia separados = DONE controlled
controlled multi-component fixture = PENDING

event_research_design_contract_v0_1.md = DONE
sampling_probe_registry_v0_1 = PENDING
sampling_window_registry_v0_1 = PENDING
parameter_sweep_plan_v0_1 = PENDING
exploratory event statistics = PENDING
event family candidates = PENDING
validated event definitions = PENDING

evaluator_contract_v0_1 = PENDING
locked evaluators = PENDING
semantic_state_representation_contract_v0_1.md = PENDING
semantic representations candidates = PENDING
state_transition_contract_v0_1.md = PENDING
transition datasets / transition evaluators = PENDING
AlphaEvolve/RL/ML = PENDING
```

Limite para AlphaEvolve y optimizadores:

```text
research_mutable = true
human_research_mutable = true
optimizer_mutable = configurable
production_locked = false
```

No se usa `mutable_by_alphaevolve = true` como regla global. Cada experimento
debe declarar si AlphaEvolve u otro optimizador puede modificar probes,
ventanas, parametros, detectores o representaciones. El laboratorio no queda
abierto por defecto a modificaciones automaticas.

Consecuencia practica:

```text
evaluadores exploratorios = permitidos para medir fenomenos
evaluadores bloqueados = solo despues de event families/definitions candidatas promovidas por evidencia
```

Criterio filosofico:

```text
TSIS no busca primero automatizar una estrategia conocida.
TSIS busca descubrir fenomenos repetibles del mercado.
```

## 6.26 Actualizacion 2026-07-05 - Alineacion Con TSIS Lab Architecture v3

Nueva lectura oficial:

```text
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
status = arquitectura_v3_cto_vigente
```

Consecuencia para este mapa:

```text
market_state/event_state ya no son el final conceptual de la ruta.
Son la base observable X legal as-of.
```

Los outcomes siguen siendo:

```text
Y separado
```

Y la nueva unidad cientifica de trabajo es:

```text
research_experiment
```

Rutas nuevas relacionadas:

```text
C:/TSIS_Data/03_TSIS_Lab/README.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/research_experiment_execution_protocol_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/parameter_sweep_protocol_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/scientific_validation_pipeline_contract_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/experiment.yaml
```

Lectura correcta de lo ya construido:

```text
controlled market_state intradia = base X controlada
controlled event_state intradia = X anclada a probe/ventana
controlled outcomes intradia separados = Y controlada
+50% = sampling_probe_human_seed
30m = sampling_window_controlled_seed
```

Lo que cambia:

```text
antes: state -> event -> outcome -> evaluator -> AlphaEvolve
ahora: state/outcome -> research_experiment -> evidence -> knowledge_object -> validation -> operational component
```

Por tanto, el siguiente paso no es materializar mas tablas de estado ni saltar a
evaluadores bloqueados. El siguiente paso es ejecutar el primer experimento
cientifico declarativo:

```text
EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Ese experimento debe estudiar historicamente movimientos intradia fuertes sin
asumir que `+50%` es evento validado ni que `30m` es ventana final.

AlphaEvolve queda reclasificado:

```text
AlphaEvolve = generador posible de candidate experiments
AlphaEvolve != autoridad de validacion
AlphaEvolve != destino final del pipeline
```

La validacion cientifica gobierna tanto al humano como a AlphaEvolve.



