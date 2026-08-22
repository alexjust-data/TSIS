# Readme del arbol de Market States Creation

Estado: `ACTIVE_TREE_GUIDE`

Este README explica el significado humano de la estructura fisica de
`04_MARKET_STATES_CREATION`. La estructura esta disenada para ser legible sin
depender de siglas opacas y para permanecer por debajo del presupuesto de rutas
de `PATH_NAMING_POLICY.md`.

## Regla de lectura

```text
numero inicial
= orden de navegacion, no jerarquia cientifica

nombre de carpeta
= responsabilidad fisica reconocible

titulo interno del documento
= significado cientifico completo
```

## Significado de las carpetas principales

| Carpeta | Nombre completo y funcion |
|---|---|
| `00_CTO` | `Chief Technology Officer governance`: decisiones sobre el propio arbol, mapa de rutas y manifests de migracion. |
| `00_START_HERE` | Punto de entrada operativo: estado vigente, handoff y roadmap actual. |
| `01_ARCHITECTURE` | Arquitectura conceptual transversal de Information Objects, Representation Models, variables y tablas. |
| `02_INFORMATION_OBJECTS` | Objetos de informacion y sus modelos de representacion candidatos. |
| `03_STATE_TABLES` | Arquitectura de las tablas `current_state`, `market_state`, `event_candidate` y `event_state`. |
| `04_EVENTS` | Perfiles de evento, definiciones, labels, detectores, admision y outcomes. |
| `05_DAILY_UNIVERSE` | Universo diario elegible y puentes temporales de consumo. No es el detector Wake-up. |
| `06_GOVERNANCE` | Ciclo de vida, materializacion, operaciones largas, promocion y frontera con Data Foundation. |
| `07_UPSTREAM_DATA` | Dependencias y programas upstream de adquisicion o reconciliacion de datos. |
| `08_REGISTRIES` | Autoridades, registros y actualizaciones pendientes de parent registries. |
| `90_HANDOFFS` | Paquetes y documentos de transferencia entre agentes o auditores. |
| `98_SUPERSEDED` | Artefactos sustituidos que se conservan como evidencia historica. |
| `99_ARCHIVE` | Archivo no vigente separado por tipo de artefacto. |

## Information Objects

| Carpeta | Nombre completo |
|---|---|
| `TRADING_ACTIVITY` | Trading Activity / Actividad Negociada. |
| `MARKET_MICROSTRUCTURE` | Market Microstructure / Microestructura de Mercado. |
| `PRICE_MOTION` | Price Motion / Movimiento del Precio. |
| `LIQUIDITY_QUALITY` | Liquidity Quality / Calidad de Liquidez. |
| `VOLATILITY_RANGE_STATE` | Volatility and Range State / Estado de Volatilidad y Rango. |
| `PRICE_LOCATION_STRUCTURE` | Price Location and Structure / Localizacion y Estructura del Precio. |
| `FLOAT_CONTEXT` | Float Context / Contexto de Float y Escala PIT. |
| `NEWS_CATALYST_CONTEXT` | News and Catalyst Context / Contexto de Noticias y Catalizadores. |
| `HALT_CONTINUITY` | Halt and Continuity / Paradas y Continuidad de Negociacion. |
| `ORDER_FLOW_PRICE` | Order Flow and Price Conversion / Conversion de Flujo en Movimiento del Precio. |

## Representation Models

`MODEL_01_` significa `Representation Model Candidate 01` dentro del
Information Object padre. No significa modelo ML ni promocion canonica.

| Carpeta | Nombre completo |
|---|---|
| `MODEL_01_MARKED_ACTIVITY` | PIT-Normalized Multiscale Marked Activity Process. |
| `MODEL_01_TRADE_QUOTE_COUPLING` | Trade-Quote Coupling Representation Model. |
| `MODEL_01_PRICE_PATH_RESPONSE` | Price Path and Response Representation Model. |
| `MODEL_01_TOP_BOOK_RESILIENCE` | Top-of-Book Resilience Representation Model. |
| `MODEL_01_RANGE_EXPANSION` | Range Expansion Representation Model. |
| `MODEL_01_ANCHOR_LOCATION` | Anchor and Price Location Representation Model. |
| `MODEL_01_PIT_SCALE_ELIGIBILITY` | Point-in-Time Scale and Eligibility Representation Model. |
| `MODEL_01_CATALYST_CONTEXT` | Catalyst Context Representation Model. |
| `MODEL_01_CONTINUITY_STATE` | Trading Continuity State Representation Model. |
| `MODEL_01_FLOW_PRICE_CONVERSION` | Order-Flow to Price-Conversion Representation Model. |

## Binding y etapas de modelo

| Carpeta | Nombre completo y funcion |
|---|---|
| `BINDING_A` | Experimental Physical Binding A: ventanas multiescala rectangulares de reloj. |
| `BINDING_B` | Experimental Physical Binding B: event time, renewal, kernels, economic time y burst dynamics. |
| `00_SHARED_CONTRACTS` | Contratos comunes que ambos bindings deben heredar. |
| `00_SPECIFICATION` | Especificacion exacta del binding. |
| `00_PREREGISTRATION` | Preregistro cientifico previo a implementacion. |
| `01_IMPLEMENTATION` | Implementacion, equivalencia de engine y probes acotados. |
| `01_INHERITANCE` | Contrato de herencia y delta de Binding B frente a Binding A. |
| `02_MATERIALIZATION` | Planes, ejecucion y readouts de materializacion fisica. |
| `02_EXACT_SPECIFICATION` | Especificacion exacta y resolucion B-02. |
| `02_BINDING_COMPARISON` | Autoridades y preparacion para comparar Binding A contra Binding B. |
| `03_AUDIT` | Auditorias independientes, preflights, recertificaciones e incidentes. |
| `03_DEVELOPMENT_CERTIFICATION` | Plan de desarrollo y certificacion previo a materializacion de Binding B. |
| `03_POPULATION_AND_SAMPLE` | Poblacion y muestra experimental compartida. |
| `04_VERDICT` | Veredicto cientifico terminal del binding. |
| `04_IMPLEMENTATION` | Implementacion futura de Binding B; carpeta preparada, no autorizacion. |
| `05_MATERIALIZATION` | Materializacion futura de Binding B; carpeta preparada, no autorizacion. |
| `06_CERTIFICATION` | Certificacion futura de Binding B; carpeta preparada, no autorizacion. |

## Tablas, eventos y universo

| Carpeta | Nombre completo |
|---|---|
| `00_GRAIN` | Grain and Cardinality / Grano y Cardinalidad. |
| `01_CURRENT_STATE` | Current State Table. |
| `02_MARKET_STATE` | Market State Table. |
| `03_EVENT_CANDIDATE` | Event Candidate Table. |
| `04_EVENT_STATE` | Event State Table. |
| `05_QUALITY_LINEAGE` | Quality and Lineage fields. |
| `06_MACHINE_LEARNING` | Machine Learning consumption boundary. |
| `07_OFFLINE_REINFORCEMENT_LEARNING` | Offline Reinforcement Learning consumption boundary. |
| `08_OUTCOMES` | Outcomes separados de features y estados. |
| `WAKE_UP` | Evento Wake-up: transicion desde regimen dormido hacia actividad negociada. |
| `02_REQUIRED_OBJECTS` | Information Objects requeridos por el evento. |
| `03_LABELS` | Definicion y materializacion de labels y negativos. |
| `04_OOS_LOCKBOX` | Out-of-Sample lockbox y contratos de sellado. |
| `05_DETECTOR` | Detector futuro del evento. |
| `01_BINDING_AB_BRIDGE` | Puente controlado del universo diario hacia el experimento Binding A/Binding B. |
| `02_PIT_RECOVERY` | Recuperacion Point-in-Time del selector de poblacion. |
| `03_CANONICAL_REVALIDATION` | Revalidacion futura sobre el Screener canonico con O/S SEC PIT. |

## Upstream y gobierno

| Carpeta | Nombre completo |
|---|---|
| `MASSIVE` | Massive market-data dependency. |
| `MASSIVE_SEC` | Reconciliacion entre datos Massive y datos SEC. |
| `SEC` | United States Securities and Exchange Commission data program. |
| `PIT` | Point-in-Time: solo informacion legalmente disponible en el instante evaluado. |
| `PGAC` | Presession Governance and Audit Cohort. |
| `03_SEVEN_TICKER_PROBES` | Probes estratificados iniciales sobre siete tickers. |
| `04_COHORT_01` | Primera cohorte descendente del programa de 4.824 instrumentos. |
| `05_FORM_13F` | Form 13F institutional holdings acquisition. |
| `01_LIFECYCLE` | Ciclo experimental a canonico. |
| `02_MATERIALIZATION` | Gobierno de materializaciones e incidentes. |
| `03_LONG_RUNNING_OPERATIONS` | Contratos para operaciones largas observables y reanudables. |
| `04_PROMOTION` | Gates de promocion institucional. |
| `05_DATA_FOUNDATION_BOUNDARY` | Frontera CTO/Data Foundation. |

## Acrónimos permitidos en este árbol

| Acrónimo | Nombre completo |
|---|---|
| `CTO` | Chief Technology Officer. |
| `PIT` | Point-in-Time. |
| `SEC` | Securities and Exchange Commission. |
| `OOS` | Out-of-Sample. |
| `PGAC` | Presession Governance and Audit Cohort. |
| `AB` | Binding A versus Binding B. |
| `B01` | Binding B Gate 01: Inheritance and Delta. |
| `B02` | Binding B Gate 02: Exact Scientific Specification. |
| `13F` | SEC Form 13F. |
| `ML` | Machine Learning; se escribe completo en carpetas nuevas. |
| `RL` | Reinforcement Learning; se escribe completo en carpetas nuevas. |
| `O/S` | Shares Outstanding; se evita en nombres de carpeta porque `/` no es valido. |

No se deben introducir nuevas siglas de navegacion sin añadir aqui su nombre
completo y demostrar que la ruta sigue siendo legible a primera vista.

## Presupuesto medido de esta migracion

```text
files before migration          = 126
files moved                     = 123
root indexes kept in place      = 3
duplicate targets               = 0
collisions                      = 0
hash mismatches during move     = 0
root entrypoints updated later  = 3
maximum final absolute path     = 232
preferred operational maximum  = 235
hard operational maximum       = 240
Windows legacy MAX_PATH         = 260 including terminating null
```

Artefactos de trazabilidad:

```text
PATH_MAP_v0_1.csv
MIGRATION_v0_1.json
TREE_v0_2.md
```

Los nombres y bytes de los 123 archivos trasladados se preservaron. Los tres
entrypoints raiz se actualizaron despues para enlazar el arbol nuevo. El mapa
conserva el hash anterior a la migracion y resuelve cada ruta antigua.

## Autoridad de naming

La policy general es:

```text
C:/TSIS_Data/PATH_NAMING_POLICY.md
```

Este README es la especializacion local. Si una carpeta nueva no cabe dentro
del presupuesto, se rediseña el nivel; no se convierte el arbol en una cadena
de abreviaturas opacas.
