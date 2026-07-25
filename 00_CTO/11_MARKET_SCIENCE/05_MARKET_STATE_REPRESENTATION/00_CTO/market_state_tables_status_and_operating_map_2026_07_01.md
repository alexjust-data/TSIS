Fecha de estado: 2026-07-01

# Market State Tables Status And Operating Map

Estado: `00_CTO architectural snapshot`

Scope: CAPA 1 - DATA FOUNDATION hacia :  
Market State Representation, 
Event    
State,   
estrategia,   
ML,   
imitation learning,   
offline RL y   
sistemas evolutivos.

Este documento no promociona ningun dataset. Su funcion es dejar claro, a dia
2026-07-01, que tablas de estado esperamos construir, cuales existen, cuales
son solo componentes, cuales son candidatas, cuales no estan terminadas y como
deben usarse dentro de TSIS.

## Resumen Ejecutivo

La conclusion importante es esta:

```text
TSIS no esta construyendo solo tablas de precios.
TSIS esta construyendo representaciones gobernadas del estado del mercado.
```

Una *tabla diaria*, un *scanner*, un conjunto de *features microestructurales* o una
*tabla de halts* no son por si solos `market_state`. Son componentes.   
El ***estado institucional*** aparece cuando TSIS puede reconstruir:

```text
que instrumento era,
que sesion era,
que informacion estaba disponible,
que calidad tenia,
que evento o ventana se estaba observando,
que contexto diario/intradia/microestructural existia,
que no se podia saber todavia,
y que outcome posterior queda estrictamente separado.
```

Estado actual:

- Hay componentes de Data Foundation materializados y validados para su scope
  declarado:   
    - identidad,   
    - calendario,   
    - cobertura esperada,  
    - corporate actions, 
    - certificacion de datasets,  
    - master daily,  
    - halts,  
    - event windows,  
    - outcomes,  
    - diarios de halts,   
    - fundamentals as-of,   
    - news as-of,   
    - short context y   
    - regime context.  
- `master_daily_table_v0_1` 
  - esta materializada como full-scope diario para 2005-01-03 a 2026-03-09, con 22,109,097 filas. 
  - Es util para research diario,
  pero no contiene todo el estado.
- `ohlcv_1m_split_normalized_full_universe_candidate` 
  - termino para casos afectados por splits: 115,667 files/rows de manifest. 
  - Es candidato, no promocionado.
- El reparador `ohlcv_1m_quote_guarded` 
  - sigue siendo overlay/delta de reparaciones sobre `E:/TSIS/data/ohlcv_1m`. 
  - Mientras no exista manifest
  promocionado, no debe tratarse como vista intradia institucional final.
- `master_intraday_bar_table_v0_1` 
  - existe solo como scope/pilot. No es full universe 1m.
- `microstructure_features_table`, `market_state_table` y `event_state_table`
  - existen solo en muestras/candidatos controlados. No son ML/RL-ready.
- `short_sale_constraints`, `float_context_table` y alertas live de offerings/
  corporate events 
  - siguen pendientes o bloqueadas por fuente.

Regla de oro:

```text
Componentes materializados != estado institucional completo.
Scanner != estado.
Outcome != feature.
Estrategia != definicion del estado.
```

## Que Es Una Tabla De Estado

Una **tabla de estado** es una representacion point-in-time de lo que TSIS podia  
saber sobre un instrumento, una sesion, un momento y un contexto de evento sin  
usar informacion futura.

Formalmente:

```text
state(t, instrument, event_context, data_availability_cutoff)
```

La tabla debe responder:

- Que instrumento es?
- Era observable y elegible en ese momento?
- Que datos existian antes del cutoff?
- Que version de precio se esta usando?
- Que corporate actions afectaban la lectura?
- Que calidad tenian los datos?
- Que contexto diario habia?
- Que contexto intradia habia?
- Que contexto microestructural habia?
- Habia halts, news, offering, short pressure, SSR, borrow o constraints?
- Que regimen de mercado habia?
- Que evento o transicion se estaba midiendo?
- Que outcome posterior se mantiene fuera como label?

Lo que no debe hacer:

- No debe mezclar labels con features.
- No debe usar informacion futura.
- No debe ocultar si una columna viene de dato `usable`, `review`, `seed`,
  `candidate`, `blocked` o `missing`.
- No debe permitir que una estrategia cambie la semantica upstream.
- No debe convertir un notebook o replay en fuente institucional sin promocion.

## Que Significa Scope Declarado

Cuando este documento dice `scope declarado`, no esta usando una frase vaga.
Significa el alcance explicito que una tabla declara en su contrato, manifest,
run summary o status matrix.

Una declaracion de scope debe decir, como minimo:

```text
nombre logico de la tabla
version logica
familia de datos
rango temporal
universo cubierto
row semantics
price view cuando aplique
fuentes/root paths
calidad heredada
promotion_state
full_universe_claim
consumer_allowed_status
consumer_blocked_status
limitaciones conocidas
```

Ejemplo:

```text
master_daily_table_v0_1
scope declarado:
  daily bars x price views gobernadas
  2005-01-03 to 2026-03-09
  22,109,097 rows
  usable para research diario y backtest diario con flags
  no contiene microestructura ni estado intradia
```

Por tanto:

```text
validated_for_declared_scope
```

no significa:

```text
esta tabla sirve para todo
```

significa:

```text
esta tabla paso los checks para el alcance exacto que declara.
```

Si una tabla declara `scoped_pilot`, `controlled_candidate`,
`seed_event_window_smoke` o `full_universe_claim=false`, esa declaracion es
parte del resultado. No puede ocultarse despues.

## Que Significa As-Of

`as-of` significa:

```text
la informacion que legalmente estaba disponible hasta un instante de corte.
```

Ejemplo:

```text
observation_time_utc = 2021-02-03 09:45:00
data_availability_cutoff_utc = 2021-02-03 09:45:00
```

El estado solo puede usar datos publicados o disponibles antes de ese cutoff.

Esto importa porque muchas tablas financieras tienen fechas distintas:

```text
period_end_date:
  fecha del periodo contable.

filing_date:
  fecha en que la compania presento el documento.

published_utc:
  fecha/hora en que una noticia estuvo disponible.

available_to_system_at:
  fecha/hora en que TSIS o el feed la pudo consumir.
```

Para trading, ML y RL, manda la disponibilidad real, no la fecha economica del
dato. Usar un dato antes de que existiera es leakage.

Regla:

```text
as-of correcto = no mirar el futuro.
```

## Filosofia Cientifica

La premisa cientifica es que el mercado no se representa bien solo con OHLCV.

Dos tickers pueden tener la misma vela y estados completamente distintos:

```text
Ticker A:
  Gap 60%, 
  float bajo, 
  news FDA, 
  RVOL extremo, 
  spread estrecho,
  short pressure, 
  halt risk.

Ticker B:
  Gap 60%, 
  sin news, 
  float alto, 
  poca liquidez real,
  spread ancho, 
  volumen sospechoso.
```

La vela es parecida. El estado no.

Por eso TSIS separa:

```text
raw data
-> audited components
-> candidate selection
-> event windows
-> market_state
-> event_state
-> outcomes
-> strategy research
-> ML / imitation learning / offline RL
-> execution / live feedback
```

El marco cientifico conecta:

- **microestructura**: spread, liquidity withdrawal, order flow, toxicity,
  event time;
- **Financial ML**: labels separados, purged validation, leakage control,
  meta-labeling;
- **causalidad**: no confundir correlacion con mecanismo;
- **invariants/risk**: que caracteristicas sobreviven cambios de regimen;
- **RL**: `state -> action -> reward -> next_state`;
- **AlphaEvolve/FunSearch-style systems**: generar hipotesis solo cuando el
  evaluator esta bloqueado y trazado.

La frase operativa:

```text
La correlacion ayuda a encontrar patrones.
El estado bien definido permite decidir si esos patrones son estudiables,
reproducibles y entrenables.
```

## De 0 A 100 En La Operativa

| Fase | Pregunta | Artefactos | Estado actual |
|---|---|---|---|
| 0. Raw data | Que datos existen? | raw daily, 1m, trades, quotes, short, news, fundamentals, halts | Raw auditado por familias, con pendientes intradia/quotes clone/quote-guarded |
| 1. Calidad | Es usable? | inspection dossiers, validators, certification matrix | Varias familias institucionalizadas; algunas pendientes de homogeneizacion |
| 2. Identidad | Que instrumento es? | `instrument_master` | Materializado para scope declarado |
| 3. Calendario | Que sesiones existen? | `market_calendar`, `expected_data_calendar` | Materializado para scope declarado |
| 4. Precio diario | Que paso a nivel diario? | `master_daily_table` | Materializado full-scope diario |
| 5. Intradia base | Que paso minuto a minuto? | raw `ohlcv_1m`, split candidate, quote-guarded overlay, future `master_intraday_bar` | No final institucional full universe todavia |
| 6. Candidate selection | Donde mirar? | daily/intraday scanner candidates | Replays/candidatos; intraday requiere quote-guarded para promocion |
| 7. Event windows | Que ventana se analiza? | `event_windows_table`, future strategy event windows | Halts materializado; estrategias pendientes |
| 8. Microestructura | Como estaba la liquidez/tape? | `microstructure_features_table` | Seed/candidate controlado, no full |
| 9. Market state | Que sabia TSIS en t? | `market_state_table` | No oficial; existe candidate 50 rows |
| 10. Event state | Que estado tenia el evento? | `event_state_table` | No oficial; existe candidate 50 rows |
| 11. Outcomes | Que paso despues? | `outcomes_table`, future strategy outcomes | Halts daily outcomes materializados; otros pendientes |
| 12. Strategy research | Que patron funciona? | notebooks, strategy event tables, overlays | Permitido con denominadores claros |
| 13. ML | Que predice el estado? | X = state/event_state, y = outcomes | No usar candidates como primary ML todavia |
| 14. Imitation learning | Que haria un experto en ese estado? | expert action logs + state snapshots | Pendiente: faltan acciones expertas/fills gobernados |
| 15. Offline RL | Que politica maximiza reward? | transitions `(s,a,r,s',done)` | No listo: faltan state oficial, action/reward/simulator |
| 16. Live | Que hacemos en tiempo real? | live scanner, feeds, broker, DAS/API, newswire | Bloqueado/parcial; requiere contratos de latencia/fuente |
| 17. Evolution systems | Que hipotesis genera AlphaEvolve? | candidate generation + locked evaluator | Futuro; evaluator debe ser inmutable |

## Catalogo De Tablas Esperadas

### Estados De Preparacion

```text
validated_for_declared_scope:
  - Materializada y validada para el alcance que declara.
  - No significa que sea full universe de todo lo imaginable.

candidate_not_promoted:
  - Existe fisicamente, tiene manifest o evidencia, 
  - pero no es fuente oficial para ML/RL/backtest institucional.

scoped_pilot:
  - Prueba controlada para forma, schema, lineage o proceso.

blocked:
  - Falta fuente, contrato, validacion o dato historico.

not_materialized:
  - El contrato existe o se espera, pero no hay tabla oficial.
```

### Matriz De Estado A 2026-07-01

| Tabla / artefacto | Tipo | Estado | Uso permitido hoy | Uso prohibido hoy |
|---|---|---|---|---|
| `instrument_master_v0_1` | componente identidad | validated_for_declared_scope | identidad, lineage, joins | lifecycle completo diario/PTI si no esta cubierto |
| `market_calendar_v0_1` | componente calendario | validated_for_declared_scope | sesiones, calendario base | asumir todos los venues/horarios especiales sin contrato |
| `expected_data_calendar_v0_1` | cobertura esperada | validated_for_declared_scope | cobertura/holes por familia | feature alpha |
| `corporate_actions_table_v0_1` | corporate actions | validated_for_declared_scope | splits/dividendos/price semantics | ajuste silencioso sin price_view |
| `dataset_certification_matrix_v0_1` | quality gate | validated_for_declared_scope | decidir usable/review/blocked | sustituir inspeccion tecnica |
| `master_daily_table_v0_1` | daily component | validated_for_declared_scope | research diario, denominadores, daily states parciales | tratar como estado completo |
| `ohlcv_1m_split_normalized_full_universe_candidate` | intraday price candidate | materialized_audited_candidate | preparar promocion split-safe; research controlado | usar como oficial ML/RL/backtest sin promocion |
| `ohlcv_1m_quote_guarded repair_manifest_lt1b_v0_1` | overlay intradia LT1B | promoted / PASS | construir vista quote-guarded LT1B como raw `ohlcv_1m` + manifest | asumir que el raw fue sobrescrito o que existe una copia fisica completa corregida |
| `master_intraday_bar_table_v0_1` | intraday component | scoped_pilot | pruebas/event cases | full universe, ML/RL, execution |
| `daily_scanner_candidates_table` | candidate selection diaria | controlled replays / not official E-root | denominador diario exploratorio | certificar first-push intradia |
| `intraday_scanner_candidates_table` | candidate selection intradia | controlled replay raw / not promoted | detectar forma de scanner 1m; DAS research preliminar | canonical 20-year scanner sin quote-guarded |
| `microstructure_features_table_v0_1` | microstructure seed | seed_event_window_smoke | prueba de schema/lineage | entrenar modelos |
| `microstructure_features_table_v0_2_candidate_controlled_25_per_role` | microstructure candidate | controlled_candidate_not_promoted | pattern discovery controlado | ML/RL/backtest/execution |
| `halts_table_v0_1` | event context | validated_for_declared_scope | halt context y ventanas | asumir causalidad por si solo |
| `event_windows_table_v0_1` | event boundary | validated_for_declared_scope | ventanas de halts/eventos | feature alpha por si solo |
| `outcomes_table_v0_1` | labels/outcomes | validated_for_declared_scope | labels separados de X | mezclar como feature |
| `fundamentals_asof_table_v0_1` | fundamentals as-of | validated_for_declared_scope | contexto as-of | usar sin lag/cutoff |
| `news_context_table_v0_1` | news as-of | validated_for_declared_scope | contexto informativo historico | asumir live latency segundos |
| `short_context_table_v0_1` | short context | validated_for_declared_scope | short interest/short volume | SSR/borrow/locate |
| `regime_context_table_v0_1` | regime context | validated_for_declared_scope | regimen/session context | intraday causal state directo |
| `short_sale_constraints_table` | constraints live/historical | blocked | nada institucional | short realism sin fuente |
| `float_context_table` | float / shares / free float | pending | nada como filtro oficial | hard filter PTI sin fuente |
| `real_time_corporate_event_alerts_table` | live events | blocked | diseno/contrato | backtest/live sin fuente latency |
| `market_state_table_v0_1` | final state snapshot | not_materialized oficial | candidate controlado solo para arquitectura | ML/RL oficial |
| `event_state_table_v0_1` | final event state | not_materialized oficial | candidate controlado para pattern discovery | ML/RL oficial |
| `strategy_candidate_events_table` | estrategia/eventos | expected per strategy | research con contrato propio | sustituir scanner global |
| `data_quality_report` | auditoria humana | required governance | explicar estado/calidad al inspector | feature modelable |

## Detalle Por Tabla O Familia

### 1. `instrument_master_v0_1`

Rol tecnico:

- Define identidad de instrumentos.
- Permite que ticker, instrumento, simbolos historicos y metadatos no se
  mezclen sin trazabilidad.

Rol filosofico:

- Ningun estado existe sin sujeto.
- La pregunta no es solo "que ticker subio?", sino "que entidad estaba
  observando TSIS en ese momento?".

Asociaciones:

- Se une con daily, intraday, news, fundamentals, short, halts y future float.
- Debe alimentar `market_state.instrument_id`.

Limitacion actual:

- No sustituye una tabla diaria point-in-time. Es decir, no responde por si
  sola: "en esta fecha concreta, esta compania estaba listada, entraba en el
  universo LT1B, tenia este float, estas shares outstanding y este market cap".
  Esa funcion requiere futuras tablas de lifecycle, float/context y market-cap
  as-of.

Estado:

```text
Status: validated_for_declared_scope
Rows: 4,824
Files: 1

Declaracion exacta de scope:
  roster/snapshot de identidades incluidas en el universo LT1B v0.1.
  Es una tabla de identidad instrumental, no una tabla diaria ticker/date.

Universo cubierto:
  4,824 identidades/instrumentos seleccionados para la salida institucional
  v0.1 del universo LT1B disponible. El objetivo es identificar que entidad
  hay detras de cada ticker y evitar mezclar companias distintas cuando un
  simbolo cambia, se reutiliza o aparece en ventanas historicas distintas.

Cobertura temporal:
  snapshot/window de identidad del universo seleccionado. Puede describir
  instrumentos historicos incluidos en el universo, pero no declara una fila
  por instrumento/dia entre 2005 y 2026.

Acabada para ese scope declarado:
  Si. Seven-table rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es full para el roster de identidades LT1B v0.1, pero no es un panel
  diario point-in-time que diga para cada fecha si el instrumento estaba
  listado, activo, dentro/fuera del universo, con que float, shares o market
  cap.

Scope declarado:
  componente de identidad instrumental para Data Foundation.
  Sirve para joins, lineage e identidad basica de instrumentos.

Full-universe claim:
  cubre el roster de identidad LT1B disponible en v0.1. No cubre todos los
  pares ticker/dia ni reconstruye membresia historica diaria.

No declara:
  membresia diaria del universo,
  lifecycle diario point-in-time completo,
  float historico completo,
  shares outstanding historico completo,
  reconstruccion diaria de market cap.

Uso permitido hoy:
  identidad, joins, lineage, context table joins.

Uso prohibido hoy:
  usarlo como fuente unica para float/market cap diario si no existe
  `float_context_table` o fuente point-in-time adicional.
```

#### Evidencia De AuditorÃ­a Que Sustenta Este Estado

```
Donde inspeccionar el detalle:  
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/    
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/    
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/reference_identity.csv  
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/reference_causal.csv  
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md  
- tests/data_foundation_outputs/README.md  

AuditorÃ­a/certificaciÃ³n primaria:
- C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/

Inputs RAW auditados para reference/identity:
  D:/reference/overview/...
  D:/reference/all_tickers/...
  D:/reference/events/...
  D:/reference/splits/...
  D:/reference/dividends/...
  D:/reference/ticker_types/ticker_types.parquet
  D:/reference/exchanges/exchanges.parquet

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
  E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json

Tests de output Data Foundation:
  C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
    - Seven-table rerun passed.
    - tests=29.
    - Valida 
      - manifests, 
      - rutas, 
      - run_id, 
      - hashes, 
      - schema y 
      - reconciliacion de outputs contra su scope declarado.
```

Artefactos RAW/certificacion que explican la procedencia del estado:

```
auditoria/reference/02_diseno_implementacion_reference_v2.md
  define inputs reales,  
  normalizacion de overview/all_tickers/events,  
  artefactos esperados y   
  preguntas de auditoria.

auditoria/reference/03_reference_root_cause_audit_phase1_closeout.md
  deja evidencia de ejecucion y cobertura:
    overview: 12,468 requests; 12,243 ok; 200 errors; 25 resume-skip.   
    all_tickers: 3,109; snapshots; 3,032 ok.
    reference_identity_snapshot.parquet: 12,468 rows.
    reference_listing_snapshots.parquet: 12,977,501 rows.
    reference_split_case_index.parquet: 14,909 rows.
    reference_dividend_case_index.parquet: 273,799 rows.

certification/reference/00_reference_current_state.md  
  - resume el estado certificado de reference como capa de identidad,  
  - existencia temporal,  
  - corporate actions y  
  - causalidad parcial.

certification/reference/02_reference_closeout.md
  - fija la policy final good/review/bad y el veredicto operativo:  
  - reference es usable como identity layer con valor causal real,  
  - pero no sustituye paneles diarios point-in-time de float/shares/market cap.

Evidencia numerica de identidad:
certification/global_metrics/reference_identity.csv  
  - good_identity_snapshot: 12,093 rows; lt1b_rows=4,812.  
  - review_transient_symbol: 175 rows; lt1b_rows=10.  
  - bad_unresolved_identity: 200 rows; lt1b_rows=2.  
  - LT1B total auditado para esta salida: 4,812 + 10 + 2 = 4,824.  

Evidencia causal relacionada, no usada como sustituto de identidad diaria:
certification/global_metrics/reference_causal.csv
  - ticker_change_near_halt: 775.
  - ticker_change_near_quotes_anomaly: 2,330.
  - split_explains_trade_scale_mismatch: 9.
  - split_near_scale_mismatch_review: 13.
```

### 2. `market_calendar_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 5,328
Files: 1

Declaracion exacta de scope:
  XNYS sessions, 2005-01-03 to 2026-03-09.

Universo cubierto:
  sesiones de calendario XNYS incluidas en la fuente actual.

Cobertura temporal:
  2005-01-03 to 2026-03-09.

Acabada para ese scope declarado:
  Si. 2026-07-01 targeted contract rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No aplica a tickers. Es calendario de sesiones, no universo de instrumentos.

Coverage declarado:
  XNYS sessions from 2005-01-03 to 2026-03-09.

Scope declarado:
  calendario base de sesiones para Data Foundation.

Uso permitido hoy:
  session_date, valid trading sessions, joins de calendario, expected coverage.

Uso prohibido hoy:
  asumir por si solo todos los horarios especiales intradia, premarket,
  afterhours o reglas de todos los venues sin contrato adicional.
```

Rol tecnico:

- Define sesiones y calendario base.
- Evita inventar dias de trading o mezclar eventos fuera de sesion.

Rol filosofico:

- El estado siempre ocurre dentro de una estructura temporal.
- Para intradia no basta la fecha; importa segmento: premarket, regular,
  afterhours.

Asociaciones:

- Base para scanners, daily states, intraday states, event windows, lookbacks y
  leakage cutoffs.

Limitacion actual:

- No sustituye una tabla de microestructura temporal ni un calendario live de
  todos los venues. Dice que dias son sesiones XNYS dentro del scope actual,
  pero no certifica por si solo premarket, afterhours, liquidez por segmento,
  half-days operativos ni disponibilidad live futura.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md
- 01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md
- 01_foundations/data_consumption_policies/market_calendar_consumption_policy.md
- 01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml
- tests/data_foundation_outputs/README.md

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
  E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json

Tests de output Data Foundation:
  2026-07-01 targeted contract rerun.
    - coverage = 2005-01-03 to 2026-03-09.
    - market_calendar_rows = 5,328.
    - incluido en el rerun de 12 tests passed junto a expected_data_calendar
      y master_daily_table.
```

### 3. `expected_data_calendar_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 29,478,796
Files: 88

Declaracion exacta de scope:
  expected rows by dataset family/year, 2005-01-03 to 2026-03-09.

Universo cubierto:
  familias de datasets cubiertas por el expected calendar v0.1 y sus
  instrumentos/sesiones esperadas.

Cobertura temporal:
  2005-01-03 to 2026-03-09.

Acabada para ese scope declarado:
  Si. 2026-07-01 targeted contract rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  Es denominador de cobertura esperada, no presencia fisica garantizada.

Coverage declarado:
  expected rows by family/instrument/session over the governed coverage window.

Scope declarado:
  matriz de cobertura esperada por familia para distinguir missing real,
  expected missing y gaps de datos.

Uso permitido hoy:
  coverage audits, missingness flags, quality inheritance, denominators.

Uso prohibido hoy:
  usar missingness como alpha sin declarar que es quality/context y sin
  estudiar sesgo de cobertura.
```

Rol tecnico:

- Marca que se esperaba encontrar por familia/dia/instrumento.
- Sirve para distinguir "no hubo dato" de "dato faltante".

Rol filosofico:

- La ausencia tambien es informacion de calidad.
- Un modelo no debe aprender de holes sin saber que son holes.

Asociaciones:

- Quality flags de `market_state`.
- Auditoria de cobertura.

Limitacion actual:

- No demuestra que el dato exista fisicamente ni que sea usable. Declara lo que
  se esperaba por familia/instrumento/sesion para poder distinguir expected
  missing, unexpected missing y cobertura pendiente. La presencia real debe
  validarse contra manifests, parquets y validators de cada familia.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md
- 01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml
- tests/data_foundation_outputs/README.md

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/expected_data_calendar/
  E:/TSIS/data/data_foundation_outputs/expected_data_calendar/_expected_data_calendar_manifest_v0_1.json

Tests de output Data Foundation:
  2026-07-01 targeted contract rerun.
    - coverage = 2005-01-03 to 2026-03-09.
    - expected_data_calendar_rows = 29,478,796.
    - incluido en el rerun de 12 tests passed junto a market_calendar
      y master_daily_table.
```

### 4. `corporate_actions_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 104,757
Files: 1

Declaracion exacta de scope:
  splits/dividends/ticker changes from reference/additional.

Universo cubierto:
  corporate actions disponibles en las fuentes reference/additional ingeridas.

Cobertura temporal:
  source-driven; no declara una fila diaria por instrumento.

Acabada para ese scope declarado:
  Si. Seven-table rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Cubre acciones corporativas observadas en fuentes, no continuidad
  economica completa de todos los tickers cada dia.

Scope declarado:
  corporate actions table para splits/dividends/price semantics disponibles
  en Data Foundation.

Uso permitido hoy:
  price-view governance, split/dividend context, ajustes declarados.

Uso prohibido hoy:
  ajustar precios silenciosamente sin declarar `price_view`,
  usar adjusted/split/raw como si fueran equivalentes.
```

Rol tecnico:

- Explica splits, dividendos y price semantics.
- Permite separar raw, split-normalized y adjusted views.

Rol filosofico:

- Un precio no tiene sentido sin semantica.
- El mismo grafico raw y ajustado puede contar historias distintas.

Asociaciones:

- `master_daily_table`.
- `ohlcv_1m_split_normalized_full_universe_candidate`.
- Future `market_state.price_view`.

Limitacion actual:

- No resuelve por si sola continuidad economica completa cuando hay ticker
  changes, mergers, delistings o instrumentos reutilizados. Sirve para declarar
  price semantics y corporate actions disponibles, pero cualquier ajuste debe
  quedar ligado a `price_view`, manifest y policy de consumo.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/reference_causal.csv
- 01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
- 01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- tests/data_foundation_outputs/README.md

Inputs RAW auditados:
  D:/reference/splits/...
  D:/reference/dividends/...
  D:/reference/events/...
  additional/corporate actions cuando aplica.

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
  E:/TSIS/data/data_foundation_outputs/corporate_actions_table/_corporate_actions_table_manifest_v0_1.json

Tests de output Data Foundation:
  C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
    - Seven-table rerun passed.
    - tests=29.
```

### 5. `dataset_certification_matrix_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 13
Files: 1

Declaracion exacta de scope:
  family-level quality gates.

Universo cubierto:
  13 familias/datasets incluidas en la matriz v0.1.

Cobertura temporal:
  no es temporal row-level; resume readiness por familia.

Acabada para ese scope declarado:
  Si. Seven-table rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es gate por familia, no validacion ticker/date.

Scope declarado:
  family-level certification matrix para Data Foundation outputs.

Uso permitido hoy:
  gates de calidad, consumer_allowed_status, family readiness.

Uso prohibido hoy:
  sustituir inspeccion tecnica detallada o evidencia visual/forense de una
  familia concreta.
```

Rol tecnico:

- Resume estado por familia de datos.
- Ayuda a decidir si una fuente esta `usable`, `review`, `blocked` o
  `candidate`.

Rol filosofico:

- La calidad de la fuente se hereda al estado.
- Un estado con datos `review` no debe parecer igual que uno `usable`.

Asociaciones:

- `quality_state`, `quality_flags`, `consumer_allowed_status`.

Limitacion actual:

- Es una matriz de readiness por familia. No sustituye los inspection dossiers,
  visual evidence packs, validators ni tests row-level. Un `usable/review` por
  familia debe heredarse como contexto de calidad, no convertirse en alpha.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- 01_foundations/inspection_dossiers/
- 01_foundations/validators/
- tests/data_foundation_outputs/README.md

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
  E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/_dataset_certification_matrix_manifest_v0_1.json

Tests de output Data Foundation:
  C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
    - Seven-table rerun passed.
    - tests=29.
```

### 6. `master_daily_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 22,109,097
Files: 66

Declaracion exacta de scope:
  daily rows x three price views, 2005-01-03 to 2026-03-09.

Universo cubierto:
  universo diario disponible en la salida v0.1, con tres price views
  gobernadas.

Cobertura temporal:
  2005-01-03 to 2026-03-09.

Acabada para ese scope declarado:
  Si. 2026-07-01 targeted contract rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  Si para el alcance diario declarado y sus expected/present flags; no quiere
  decir que cada ticker tenga fila todos los dias ni que haya microestructura.

Coverage declarado:
  2005-01-03 to 2026-03-09

Scope declarado:
  daily bars x governed price views for Data Foundation.
  Incluye price views diarios, no microestructura.

Full-universe claim:
  full-scope diario para el universo disponible en la tabla v0.1 y sus
  price views declaradas.

No declara:
  estado intradia,
  first-push timing,
  spread/depth/trades/quotes,
  float point-in-time,
  SSR/borrow/locate,
  live news latency.

Uso permitido hoy:
  research diario, denominadores daily, estrategias daily como first red day
  con `price_view`, quality flags y outcomes separados.

Uso prohibido hoy:
  tratarla como `market_state` completo o como fuente para DAS/frontside
  intradia.
```

Rol tecnico:

- Provee OHLCV diario y price views gobernadas.
- Es la base para gappers diarios, red day, green day, prior high/low,
  resistance/support daily, daily range expansion y lookbacks compactos.

Rol filosofico:

- Es contexto diario, no el estado completo.
- Sirve para saber el marco de la accion antes de entrar en microestructura.

Puede usarse hoy para:

- Research diario.
- Estrategias daily como "first red day", siempre que:
  - se declare `price_view`;
  - se filtren flags de calidad;
  - los outcomes se mantengan separados;
  - se unan solo contextos as-of validos;
  - no se afirme que contiene microestructura ni live state.

No contiene por si sola:

- first push intradia;
- premarket/afterhours timing;
- spread/depth/trades/quotes;
- float point-in-time completo;
- SSR/borrow/locate;
- news live latency;
- event_state final.

Asociaciones:

- Se une con `instrument_master`, `market_calendar`, `corporate_actions_table`,
  `expected_data_calendar`, `outcomes_table`, scanners diarios/intradia y
  futuras tablas `market_state`/`event_state`.
- Debe alimentar contexto diario, lookbacks, gaps, previous close, prior
  high/low, daily range y price-view governance.

Limitacion actual:

- No es una tabla de estado completa. Aunque esta materializada para su scope
  diario declarado, no contiene microestructura, first-push intradia, news live
  latency, float point-in-time ni restricciones de short. Puede servir para
  estrategias daily como "first red day", pero no para certificar DAS/frontside
  intradia sin `intraday_scanner_candidates_table` y 1m quote-guarded.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md
- 01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml
- 01_foundations/module_contracts/price_views_registry.md
- 01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
- tests/data_foundation_outputs/README.md

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1/
  E:/TSIS/data/data_foundation_outputs/master_daily_table/_master_daily_table_manifest_v0_1.json

Tests de output Data Foundation:
  2026-07-01 targeted contract rerun.
    - coverage = 2005-01-03 to 2026-03-09.
    - master_daily_table_rows = 22,109,097.
    - incluido en el rerun de 12 tests passed junto a market_calendar
      y expected_data_calendar.
```

### 7. `ohlcv_1m_split_normalized_full_universe_candidate`

Estado:

```text
Status: materialized_audited_candidate
Run: split_affected_20260627_192314
Manifest rows: 115,667
Output files present: 115,667
Chunks: 24
Promotion: pending_promotion_gate

Declaracion exacta de scope:
  split-affected 1m files/ticker-periods detected by the split-normalization
  manifest.

Universo cubierto:
  casos afectados por splits dentro del universo detectado, no todos los
  parquets 1m.

Cobertura temporal:
  depende de los files/ticker-periods afectados por splits en el manifest.

Acabada para ese scope declarado:
  Materializada y auditada como candidate; no promocionada.

Full universe 2005-2026 para todos los tickers/dias:
  No como copia fisica completa. Es cobertura logica de afectados por splits.

Scope declarado:
  materializacion split-normalized candidate para archivos/ticker-periodos 1m
  afectados por splits.

Full-universe claim:
  logico para casos afectados por splits dentro del universo detectado, no
  copia fisica completa de todo `ohlcv_1m`.

No declara:
  reparacion quote-guarded,
  VWAP reconstruction,
  sustitucion oficial de raw 1m,
  ML/RL/backtest institucional.

Uso permitido hoy:
  promotion review, validator development, loader design, research controlado.

Uso prohibido hoy:
  usarlo como 1m oficial final sin promotion gate.
```

Para que se construyo:

- Para materializar una version split-normalized de los parquets 1m afectados
  por splits.
- Para demostrar y preparar una vista 1m compatible con corporate actions en
  los casos donde raw 1m no se puede usar directamente.

Que operaciones abarca:

- Normalizacion por splits en archivos/ticker-periodos afectados.
- Produccion de output candidate y run summary.
- Auditoria inicial de manifest/chunks/output files.

Que no abarca:

- No es una copia fisica completa de todo `ohlcv_1m`.
- No repara mechas imposibles por quotes.
- No reconstruye VWAP.
- No sustituye el repair manifest quote-guarded.
- No esta promocionada como fuente oficial para ML/RL/backtest.

Como hacerla operativa:

1. Revisar promotion gate.
2. Registrar contrato de consumo.
3. Validar contra corporate actions y raw 1m.
4. Definir loader oficial:
   - raw 1m para no afectados;
   - split-normalized candidate para afectados;
   - quote-guarded overlay donde aplique.
5. Promocionar solo con manifest, changelog, validator y policy.

Rol tecnico:

- Normaliza 1m solo en archivos/ticker-periodos afectados por splits.
- Permite separar el problema de split normalization del problema distinto de
  mechas imposibles/quotes inconsistentes.

Rol filosofico:

- Un ajuste corporativo no debe contaminar silenciosamente el raw.
- Primero se declara la vista ajustada; despues se decide si se promueve como
  consumo oficial.

Asociaciones:

- Se apoya en `corporate_actions_table_v0_1`.
- Debe combinarse con raw `ohlcv_1m` para no afectados y con
  `ohlcv_1m_quote_guarded repair_manifest_lt1b_v0_1` para repairs LT1B promovidos.
- Es input candidato para loaders intradia, no sustituto automatico del 1m raw.

Limitacion actual:

- Esta materializada como candidate para casos afectados por splits, no como
  arbol oficial completo 1m. No corrige outliers quote-guarded ni reconstruye
  VWAP. Para backtesting/ML/RL intradia oficial falta promotion gate y loader
  que combine raw, split-normalized y repair overlay.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
- 01_foundations/module_contracts/price_semantics_and_adjustment_policy.md
- 01_foundations/GRAPHIFY_REFRESH_QUEUE.md

Run materializado:
  C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314/

Output candidate:
  E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate/

Evidencia del run:
  run_id = split_affected_20260627_192314
  manifest_rows = 115,667
  chunks = 24
  output_files_present = 115,667

Lectura obligatoria:
  candidate != promoted official dataset.
  split-affected coverage != copia fisica completa de todo `ohlcv_1m`.
```

### 8. `ohlcv_1m_quote_guarded repair_manifest_lt1b_v0_1`

Estado:

```text
Status: promoted / PASS as of 2026-07-03

Rows:
  301278342 manifest rows.

Declaracion exacta de scope:
  repair overlay quote-guarded LT1B sobre raw `ohlcv_1m` para minutos
  incompatibles con quotes; 4824 LT1B tickers completed, 0 missing.

Universo cubierto:
  en progreso sobre el universo procesado por el reparador; no hay output
  final promocionado.

Cobertura temporal:
  en progreso; depende de meses/tickers procesados por el run.

Acabada para ese scope declarado:
  No. A 2026-07-01 esta en progreso/no promocionada.

Full universe 2005-2026 para todos los tickers/dias:
  No todavia. Solo sera claimable despues de manifest final + validator +
  promotion gate.

Progress known at last inspection:
  ticker_status_files: 7,446
  DONE: 7,434
  RUNNING: 12
  months_done: 789,190 / 790,261
  repair_rows: 211,157,282
  ohlc_repair_rows: 142,015,914
  vw_invalid_rows: 210,427,620

Scope declarado:
  overlay/delta de reparaciones quote-guarded sobre raw `ohlcv_1m`.

Full-universe claim:
  todavia no promocionado; no existe claim oficial final.

Fuente provisional:
  OHLCV desde `E:/TSIS/data/ohlcv_1m`.
  Quotes desde `D:/quotes` mientras se completa/valida `E:/TSIS/data/quotes_`.

No declara:
  arbol completo corregido,
  modificacion de raw,
  1m institucional final.

Uso permitido hoy:
  seguimiento del run, validacion, futura vista `raw + repair_manifest`.

Uso prohibido hoy:
  asumir que todo 1m ya esta corregido o promocionado.
```

Rol tecnico:

- No duplica todo el universo OHLCV 1m.
- Lee `E:/TSIS/data/ohlcv_1m`.
- Lee quotes de `D:/quotes` de forma provisional mientras se completa/valida
  `E:/TSIS/data/quotes_`.
- Detecta minutos donde `o/h/l/c` o `vw` son incompatibles con el envelope de
  quotes.
- Escribe solo filas problematicas como overlay/delta.

Lectura correcta:

```text
raw ohlcv_1m
+ repair_manifest_lt1b_v0_1.parquet
= ohlcv_1m_quote_guarded view
```


Rol filosofico:

- El raw es inmutable.
- La correccion se expresa como evidencia reproducible, no como sobrescritura
  silenciosa.
- El estado intradia debe saber si una barra fue reparada o rechazada.

Impacto:

- Es prerequisito para promocionar un scanner intradia canonico de 20 anos.
- Es prerequisito para microstructure/event states mas serios.

Asociaciones:

- Se une logicamente con raw `E:/TSIS/data/ohlcv_1m`.
- Usa quotes de `D:/quotes` de forma provisional mientras se completa y valida
  `E:/TSIS/data/quotes_`.
- Debe alimentar `master_intraday_bar_table` futura,
  `intraday_scanner_candidates_table_v0_2_quote_guarded_candidate` y
  microstructure/event states.

Limitacion actual:

- No es un arbol corregido completo ni modifica raw. Es un overlay/delta de
  reparaciones. Hasta que exista manifest final promocionado y validator final,
  no se puede decir que el 1m completo esta institucionalmente corregido.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
- 01_foundations/GRAPHIFY_REFRESH_QUEUE.md

Run en progreso:
  script = build_ohlcv_1m_quote_guarded_repairs_v0_2.py
  minute_root = E:/TSIS/data/ohlcv_1m
  quotes_root = D:/quotes
  run_root = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838

Artefactos del run:
  month_summaries/*.json
  repair_shards/*.parquet
  ticker_status/*.json
  progress_snapshot.json

Target de promocion esperado:
  E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet

Lectura obligatoria:
  raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet = vista ohlcv_1m_quote_guarded.
  repair manifest != copia fisica completa del mercado 1m.
```

### 9. `master_intraday_bar_table_v0_1`

Estado:

```text
Status: scoped_pilot / validated_for_declared_scope only for scoped cases
Rows: 175,252
Files: 14
Scope: scoped_split_normalized_event_cases
full_universe_claim: false

Declaracion exacta de scope:
  `scoped_split_normalized_event_cases`.

Universo cubierto:
  casos/eventos intradia acotados incluidos en el pilot, no todo el universo.

Cobertura temporal:
  solo los casos/eventos incluidos en el scope pilot.

Acabada para ese scope declarado:
  Si para el pilot/scoped cases. No para universo completo.

Full universe 2005-2026 para todos los tickers/dias:
  No. `full_universe_claim=false`.

Scope declarado:
  tabla intradia piloto para casos/eventos split-normalized acotados.

No declara:
  full universe 1m,
  backtest core intradia,
  ML/RL-ready state,
  execution truth.

Uso permitido hoy:
  pruebas de schema, lineage y event cases.

Uso prohibido hoy:
  usarla como tabla 1m oficial para todo 2005-2026.
```

Rol tecnico:

- Prueba de estructura de tabla intradia, no tabla 1m final.

Rol filosofico:

- Sirve para demostrar schema/lineage, no para declarar que tenemos todo el
  universo intradia gobernado.

Trabajo pendiente:

- Construir version quote-guarded/split-safe con cobertura declarada.
- Decidir si sera fisica full tree o vista logica raw + overlays.
- Validar performance, quality inheritance y as-of semantics.

Asociaciones:

- Depende de `instrument_master`, `market_calendar`,
  `ohlcv_1m_split_normalized_full_universe_candidate`,
  `ohlcv_1m_quote_guarded repair_manifest_lt1b_v0_1` y future intraday loaders.
- Debe alimentar scanners intradia, event windows, market_state y event_state
  cuando exista version full/safe.

Limitacion actual:

- Es un piloto acotado. No representa todo el universo 1m 2005-2026 y no debe
  usarse como core intraday backtest table. El trabajo actual serio para
  intradia debe pasar por quote-guarded/split-safe o declarar raw diagnostic.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
- tests/data_foundation_outputs/README.md

Output institucional/piloto:
  E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/

Tests de output Data Foundation:
  C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
    - Seven-table rerun passed para el scope piloto.
    - full_universe_claim = false.

Lectura obligatoria:
  scoped_pilot != full-universe 1m.
  175,252 rows en 14 files no equivalen a 20 anos de barras 1m.
```

### 10. `daily_scanner_candidates_table`

Estado:

```text
Status: controlled_replays / not_official_E_root
Rows:
  dependen del run/replay; no hay tabla canonica E-root promocionada a
  2026-07-01.

Declaracion exacta de scope:
  replays/controlados de candidate selection diaria; no canonical E-root.

Universo cubierto:
  depende de cada replay; no hay universo canonico promocionado.

Cobertura temporal:
  depende de cada run; los replays conocidos son muestras, no 2005-2026
  oficial.

Acabada para ese scope declarado:
  No como tabla institucional. Si solo como replay exploratorio/controlado
  cuando el run concreto termina.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Scope declarado:
  candidate selection diaria / EOD proxy para decidir que tickers mirar a
  nivel diario.

Full-universe claim:
  no promocionado como canonical 20-year scanner.

No declara:
  first-push timestamp,
  premarket/regular/afterhours segment,
  movimiento intradia completo,
  estrategia DAS,
  market_state/event_state.

Uso permitido hoy:
  research diario, pruebas de denominador, notebooks exploratorios, contexto
  para estrategias daily.

Uso prohibido hoy:
  certificar movimientos intradia tipo +50% a las 04:30 o usarlo como estado
  intradia.
```

Rol tecnico:

- Denominador diario o proxy EOD: "que tickers merecen mirar a nivel diario".
- Puede usar daily high, pct change, gap, volume, market cap y quality flags.

Rol filosofico:

- Scanner dice donde mirar.
- No dice que estado existe.
- No dice que trade ejecutar.

Limitacion critica:

- Una tabla diaria no puede certificar que un ticker hizo +50% a las 04:30,
  subio y luego volvio a cero antes del cierre.
- Para frontside/DAS, el scanner diario es ciego al timing intradia.

Uso correcto:

- Denominador daily.
- Research de estrategias daily.
- Contexto para gappers y first red day.
- No usar como fuente final de first-push intradia.

Asociaciones:

- Consume `instrument_master`, `market_calendar`, `master_daily_table`,
  `dataset_certification_matrix` y scanner definitions.
- Debe alimentar research diario y overlays de estrategia, pero no reemplaza
  `intraday_scanner_candidates_table`.

Limitacion actual:

- Los replays controlados prueban semantica, no promocion E-root canonica.
  Ademas, la deteccion daily/EOD no captura el momento exacto del pump si el
  ticker subio y devolvio el movimiento antes del cierre. Para frontside/DAS
  se necesita scanner intradia.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
- 01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
- 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
- 01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
- 01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
- 01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions/
- tests/data_foundation_outputs/README.md

Replay controlado v0.3:
  C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum/
    - rows = 15,323.
    - sessions = 6.
    - instruments = 2,590.
    - base_eligible_rows = 6,184.
    - selected_in_play_momentum_candidate_rows = 69.
    - selected_das_research_profile_rows = 0.
    - full promoted dataset = no.

Lectura obligatoria:
  controlled_replay_candidate != official promoted dataset.
  daily_eod_proxy != certified premarket/regular/afterhours segment detection.
```

### 11. `intraday_scanner_candidates_table`

Estado:

```text
Status: controlled_replay_raw / not_promoted

Controlled replay known:
  path:
    C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
  rows: 33,413
  tickers: 5,690
  base_eligible_rows: 7,498
  motion_threshold_rows: 235
  tradability_pass_rows: 176
  selected_intraday_in_play_candidate_rows: 102
  first_cross_premarket: 114
  first_cross_regular: 82
  first_cross_afterhours: 39

Declaracion exacta de scope:
  controlled replay sobre raw `ohlcv_1m` para inspeccionar scanner intradia.

Universo cubierto:
  replay conocido 2025-01-02 to 2025-01-10, no universo completo.

Cobertura temporal:
  muestra 2025-01-02 to 2025-01-10 en el replay citado.

Acabada para ese scope declarado:
  Si para ese replay de inspeccion. No para canonical/full 2005-2026.

Full universe 2005-2026 para todos los tickers/dias:
  No. El full run raw diagnostic puede existir como ejecucion, pero no esta
  promocionado como tabla institucional y requiere quote-guarded successor.

Scope declarado:
  replay/controlado para demostrar scanner intradia sobre raw `ohlcv_1m`.

Full-universe claim:
  no promocionado; no canonico 20-year.

Dependencia pendiente:
  rehacer o promover solo tras vista quote-guarded/split-safe, o marcar raw
  diagnostic explicitamente.

No declara:
  market_state,
  event_state,
  strategy signal,
  ML/RL-ready dataset.

Uso permitido hoy:
  inspeccion, DAS research preliminar, validacion de definicion de scanner.

Uso prohibido hoy:
  presentarlo como scanner institucional final.
```

Rol tecnico:

- Detecta candidatos in-play por movimiento intrasesion.
- Debe evaluar premarket, regular y afterhours.
- Debe guardar:
  - first cross timestamp;
  - segment;
  - move vs reference;
  - volume-to-time;
  - dollar-volume-to-time;
  - tradability gate;
  - quality flags;
  - lineage.

Rol filosofico:

- Para estrategias de momentum/frontside, el evento real ocurre dentro del dia.
- El edge no esta solo en "cerrar +50%"; esta en detectar el pump, el primer
  push, el fallo, la liquidez y la estructura mientras ocurre.

Estado actual:

- Existe replay/controlado raw.
- No debe promocionarse hasta incorporar quote-guarded 1m o marcar
  explicitamente raw spikes rechazados.


Uso para DAS:

- La salida intradia sera el denominador que DAS consume.
- DAS debe aplicar overlay propio despues:
  - estructura frontside;
  - first dip;
  - reclaim;
  - VWAP/EMA context;
  - human labels;
  - outcomes.

Asociaciones:

- Consume `instrument_master`, `market_calendar`, raw `ohlcv_1m`,
  `master_daily_table` para referencias como previous close y futuras vistas
  quote-guarded/split-safe.
- Debe alimentar `strategy_candidate_events_table`, `event_state_table` y
  notebooks/research de estrategias como DAS.

Limitacion actual:

- El replay conocido usa raw `ohlcv_1m`; por tanto puede capturar spikes que
  despues deben confirmarse o rechazarse con quote-guarded. No es tabla
  promocionada para 20 anos, no es senal de estrategia y no es ML/RL-ready.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/intraday_scanner_candidates_contract_v0_1.md
- 01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
- 01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
- 01_foundations/canonical_schemas/outputs/intraday_scanner_candidates_table_schema_contract.md
- 01_foundations/validators/outputs/intraday_scanner_candidates_table_validators.md
- 01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions/intraday_in_play_momentum_candidate_denominator_v0_1.yaml
- tests/data_foundation_outputs/README.md

Replay controlado:
  C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
    - rows = 33,413.
    - tickers = 5,690.
    - session_dates = 6.
    - selected_intraday_in_play_candidate_rows = 102.
    - first_cross_premarket_rows = 114.
    - first_cross_regular_rows = 82.
    - first_cross_afterhours_rows = 39.
    - duplicate_ticker_session_keys = 0.
    - full_universe_claim = false.

Lectura obligatoria:
  intraday scanner v0.1 = first-push timing candidate surface.
  Debe existir sucesor quote-guarded antes de promocion canonica.
```

### 12. `microstructure_features_table`

Estado:

```text
Status:
  v0.1 = seed_event_window_smoke
  v0.2 = controlled_candidate_not_promoted
v0.1 rows: 1
v0.2 rows: 50
v0.2 tickers: 9
v0.2 event_windows: 50
v0.2 trades present: 24/50

Quote root:
  D:/quotes provisional in candidate.

Declaracion exacta de scope:
  v0.1 seed smoke; v0.2 halt event-window candidate, 25 rows per selected
  role, `full_universe_claim=false`.

Universo cubierto:
  50 ventanas controladas, 9 tickers; no universo completo.

Cobertura temporal:
  solo ventanas/casos seleccionados en el candidate.

Acabada para ese scope declarado:
  Si para diagnostic/control candidate. No para full microstructure.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Scope declarado:
  prueba/candidato de features microestructurales en ventanas controladas.

Full-universe claim:
  false.

No declara:
  full-universe microstructure,
  training-ready ML/RL dataset,
  execution truth.

Uso permitido hoy:
  pattern discovery controlado, schema, lineage, feature design.

Uso prohibido hoy:
  entrenar modelos primarios o backtests institucionales.
```

Rol tecnico:

- Resume microestructura en ventanas gobernadas:
  - spread;
  - locked/crossed;
  - quote count;
  - trade intensity;
  - odd lots;
  - missingness;
  - tape/book texture;
  - liquidity stress proxies.

Rol filosofico:

- La microestructura es lo que separa "sube" de "se puede operar".
- Para microcaps, la retirada de liquidez y el stress del proveedor de
  liquidez pueden explicar mas que un indicador tecnico clasico.

Estado actual:

- v0.1 seed: 1 row.
- v0.2 controlled candidate: 50 rows, 9 tickers, 50 event windows.
- No ML/RL/backtest/execution.

Por que no se materializa ciegamente full-universe:

- Quotes/trades son pesados.
- La microestructura debe calcularse en ventanas gobernadas.
- El full-history debe ser compacto; la microestructura pesada debe estar por
  eventos, scanners, estrategias, halts, news, offerings o ventanas de
  investigacion.

Asociaciones:

- Consume quotes, trades, event windows, halts, intraday scanner candidates y
  quality flags.
- Debe alimentar `market_state_table`, `event_state_table`, execution realism,
  liquidity stress research y future ML/RL solo cuando se materialice con
  cobertura y validators suficientes.

Limitacion actual:

- v0.1/v0.2 prueban forma, lineage y recomputacion en ventanas controladas. No
  hay microestructura para cada momento/ticker del universo. No debe usarse
  como dataset entrenable ni como execution truth.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/inspection_dossiers/microstructure_features/
- 01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb
- tests/data_foundation_outputs/README.md

Evidencia v0.1:
  C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
    - status = passed.
    - tests = 3.
    - rows = 1 seed window.

Evidencia v0.2 candidate:
  C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
    - status = passed.
    - tests = 5.
    - candidate_rows = 6 visual smoke.
    - official_dataset_created = false.

Output candidate:
  E:/TSIS/data/data_foundation_outputs/microstructure_features_table/

Lectura obligatoria:
  controlled_candidate_not_promoted != ML/RL-ready table.
  D:/quotes provisional lineage debe quedar visible hasta validar E:/TSIS/data/quotes_.
```

### 13. `halts_table_v0_1` y `event_windows_table_v0_1`

Estado:

```text
halts_table_v0_1:
  Status: validated_for_declared_scope
  Rows: 133,116
  Files: 1

  Declaracion exacta de scope:
    Nasdaq/NYSE halts and SEC suspensions from `halts_v0_1`.

  Universo cubierto:
    halt/suspension events presentes en la fuente halts_v0_1.

  Cobertura temporal:
    source-driven dentro de la cobertura de halts_v0_1.

  Acabada para ese scope declarado:
    Si. isolated rerun passed.

  Full universe 2005-2026 para todos los tickers/dias:
    No aplica como ticker/day grid; cubre eventos de halt/suspension
    disponibles.

  Scope declarado:
    halt event context.

event_windows_table_v0_1:
  Status: validated_for_declared_scope
  Rows: 214,112
  Files: 1

  Declaracion exacta de scope:
    halt-derived event windows for LT1B/calendar-covered intraday halt events.

  Universo cubierto:
    ventanas derivadas de halt events cubiertos, no todas las familias de
    eventos.

  Cobertura temporal:
    derivada de halts/calendar coverage.

  Acabada para ese scope declarado:
    Si. isolated rerun passed.

  Full universe 2005-2026 para todos los tickers/dias:
    No. Son ventanas de eventos halt-derived, no todo ticker/dia.

  Scope declarado:
    ventanas derivadas de halts para event studies y outcomes.

Uso permitido hoy:
  halt context, exclusions, halt event windows, outcome construction.

Uso prohibido hoy:
  asumir que halt/event window demuestra causalidad o que cubre todas las
  familias futuras de eventos estrategicos.
```

Rol tecnico:

- Halts: interrupciones reales de mercado.
- Event windows: ventanas antes/despues de eventos.

Rol filosofico:

- Un evento no es una fila de precio.
- Un evento crea un antes, un durante y un despues.

Uso:

- Exclusions.
- Event studies.
- Contexto para `event_state`.
- Construccion de outcomes.

Asociaciones:

- Se une con `instrument_master`, `market_calendar`, `master_daily_table`,
  `intraday_scanner_candidates_table`, `microstructure_features_table` y
  `outcomes_table`.
- Debe alimentar event boundaries, pre/post windows, exclusions y future
  `event_state.event_id`.

Limitacion actual:

- `event_windows_table_v0_1` esta derivada de halts. No cubre todas las
  familias de eventos que TSIS necesitara: offerings, first push, news,
  reclaim, backside, resistance rejection o liquidity withdrawal. Un halt
  window no prueba causalidad por si mismo.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/
- 01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/reference_causal.csv
- tests/data_foundation_outputs/README.md

Outputs institucionales Data Foundation:
  E:/TSIS/data/data_foundation_outputs/halts_table/
  E:/TSIS/data/data_foundation_outputs/event_windows_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - halts_table_rows = 133,116.
    - event_windows_table_rows = 214,112.

Lectura obligatoria:
  halt/event window = contexto y delimitacion temporal.
  No equivale a causalidad ni a cobertura de todos los eventos estrategicos.
```

### 14. `outcomes_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 128,388
Files: 1

Declaracion exacta de scope:
  next-session daily outcomes for halt-derived event windows x three daily
  price views.

Universo cubierto:
  outcomes diarios posteriores para ventanas derivadas de halts cubiertas.

Cobertura temporal:
  derivada de halts/event_windows/master_daily coverage.

Acabada para ese scope declarado:
  Si. isolated rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es outcome table de halts, no outcomes de todas las estrategias/eventos.

Scope declarado:
  next-session daily outcomes for halt windows x 3 daily price views.

Uso permitido hoy:
  labels separados para event research y ML supervisado cuando el evento y el
  cutoff sean validos.

No declara:
  intraday execution outcome,
  RL reward,
  outcomes para todas las estrategias,
  outcomes para todos los eventos posibles.

Uso prohibido hoy:
  usar outcomes como features o como filtro previo de candidatos.
```

Rol tecnico:

- Labels/resultados posteriores, actualmente para halts y outcomes daily.

Rol filosofico:

- El resultado es lo que se predice o evalua.
- No debe entrar como feature.

Uso:

- ML supervised: `y`.
- Evaluacion de estrategias.
- Backtest/research.

Prohibido:

- Meter outcomes dentro de `market_state`.
- Usar outcome futuro para seleccionar entradas historicas sin declarar
  leakage.

Asociaciones:

- Depende de `event_windows_table`, `master_daily_table`, `market_calendar` y
  price views.
- Debe conectarse con `event_state` y strategy research como `y`, label u
  outcome posterior, nunca como feature de entrada.

Limitacion actual:

- Solo cubre outcomes diarios next-session para ventanas derivadas de halts y
  tres price views. No contiene outcomes intradia, execution fills, RL rewards,
  slippage ni outcomes de todas las estrategias.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- tests/data_foundation_outputs/README.md

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/outcomes_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - outcomes_table_rows = 128,388.
    - scope = next-session daily outcomes for halt-derived event windows
      x three daily price views.

Lectura obligatoria:
  outcome table = label/evaluation surface.
  outcome table != feature table.
```

### 15. `fundamentals_asof_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 621,756
Files: 51

Declaracion exacta de scope:
  additional financial statement rows with `filing_date` as `as_of_date`;
  ratios and standalone `financial_v0_1` excluded.

Universo cubierto:
  financial statement rows disponibles en additional/financial sources
  incluidas en la tabla.

Cobertura temporal:
  source-driven by filing_date/as_of_date; no es grilla diaria por ticker.

Acabada para ese scope declarado:
  Si. isolated rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es tabla as-of de statements disponibles, no snapshot latest-before-event
  para cada ticker/dia.

Scope declarado:
  filing-date-aware financial statements/context, ratios y fundamentals
  disponibles bajo reglas as-of.

No declara:
  standalone `financial_v0_1` completo como feature directa,
  uso sin filing_date/as-of,
  garantia de que todas las companias tienen cobertura simetrica.

Uso permitido hoy:
  contexto fundamental as-of, research con lag/cutoff explicito.

Uso prohibido hoy:
  usar period_end como si fuese fecha de disponibilidad.
```

Rol tecnico:

- Contexto fundamental con filing-date/as-of.

Rol filosofico:

- El mercado solo puede reaccionar a informacion disponible.
- Filing date y availability importan mas que periodo contable.

Uso:

- Features as-of.
- Contexto de solvencia, dilution, balance, revenue, cash, etc.

Asociaciones:

- Se une con `instrument_master`, `market_calendar`, `market_state`,
  `event_state`, strategy overlays y future `float_context_table`.
- Debe entrar con cutoff/as-of explicito, no como snapshot posterior.

Limitacion actual:

- Es statement context disponible por `filing_date/as_of_date`. No es una
  tabla diaria latest-before-event ya precalculada, no reconstruye market cap
  historico, no da float completo y no garantiza cobertura simetrica por
  compania.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/financial/
- tests/data_foundation_outputs/README.md

Inputs RAW auditados:
  E:/TSIS/data/financial/
  E:/TSIS/data/additional/financial/ cuando aplica al builder.

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - fundamentals_asof_table_rows = 621,756.
    - files = 51.

Lectura obligatoria:
  filing_date/as_of_date gobierna disponibilidad.
  period_end no debe usarse como fecha de conocimiento del mercado.
```

### 16. `news_context_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 287,138
Files: 9

Declaracion exacta de scope:
  additional news rows with `published_utc` as `as_of_utc`; ticker attribution
  preserved.

Universo cubierto:
  noticias disponibles en la fuente additional/news incluida en v0.1.

Cobertura temporal:
  source-driven by `published_utc`; no es garantia de news completas para cada
  ticker/dia.

Acabada para ese scope declarado:
  Si. isolated rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es contexto de noticias disponibles, no feed completo live/historico.

Scope declarado:
  news context historico con `published_utc` como base as-of.

No declara:
  live feed latency de segundos,
  newswire institutional feed,
  SEC EDGAR real-time completeness,
  causalidad del movimiento.

Uso permitido hoy:
  catalyst/news context historico, features as-of con cutoff.

Uso prohibido hoy:
  tratarlo como alerta live equivalente a DAS/Benzinga/Newswire/EDGAR real-time.
```

Rol tecnico:

- Contexto de noticias con `published_utc`.

Rol filosofico:

- Catalyst y attention shock son parte central del estado smallcap.

Limitacion:

- No equivale a feed live de segundos.
- No sustituye SEC EDGAR real-time, newswire/vendor, broker/platform feed ni
  alertas DAS/TradeStation.

Asociaciones:

- Se une con `instrument_master`, `event_state`, `market_state`,
  real-time alert contracts, scanners y strategy candidate events.
- Puede explicar catalyst/attention context, pero debe conservar
  `published_utc`, source lineage y cutoff.

Limitacion actual:

- Es news context historico disponible, no feed live institucional de segundos.
  No prueba causalidad por si solo y no cubre necesariamente PRNewswire,
  BusinessWire, Benzinga, DAS/TradeStation alertas ni SEC EDGAR live completo.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/
- tests/data_foundation_outputs/README.md

Inputs RAW auditados:
  E:/TSIS/data/additional/news/ o fuente additional equivalente.

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/news_context_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - news_context_table_rows = 287,138.
    - files = 9.

Lectura obligatoria:
  published_utc/as_of_utc != received-latency live feed.
  historical news context != real-time offering alert system.
```

### 17. `short_context_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 7,145,337
Files: 32

Declaracion exacta de scope:
  source-scoped short interest/short volume from `short` and FINRA
  `short_review`; no borrow/SSR.

Universo cubierto:
  short interest/short volume disponible en esas fuentes.

Cobertura temporal:
  source-driven; depende de short/FINRA source coverage.

Acabada para ese scope declarado:
  Si. isolated rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. No cubre borrow/SSR/locate ni garantiza fila diaria por ticker.

Scope declarado:
  short interest / short volume context segun fuentes disponibles.

No declara:
  SSR,
  borrow availability,
  locate availability,
  broker-level shortability,
  intraday live short constraints.

Uso permitido hoy:
  short pressure context y stratified research.

Uso prohibido hoy:
  simular shorts realistas sin `short_sale_constraints_table`.
```

Rol tecnico:

- Short interest y short volume historico segun fuentes disponibles.

Rol filosofico:

- Short pressure puede cambiar la mecanica del squeeze y del backside.

Limitacion:

- No contiene SSR, borrow, locate ni availability.
- No permite realismo completo de short strategies.

Asociaciones:

- Se une con `instrument_master`, `market_state`, `event_state`,
  `short_sale_constraints_table`, scanners y strategy overlays short/long.
- Aporta short pressure/crowding context, no permisos reales de ejecucion.

Limitacion actual:

- No contiene SSR, borrow, locate, broker-level shortability ni availability
  live. Por tanto no puede validar por si sola estrategias short ejecutables.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short_review/
- tests/data_foundation_outputs/README.md

Inputs RAW auditados:
  E:/TSIS/data/short/
  E:/TSIS/data/short_review/

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/short_context_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - short_context_table_rows = 7,145,337.
    - files = 32.

Lectura obligatoria:
  short interest/short volume context != borrow/locate/SSR constraint.
```

### 18. `regime_context_table_v0_1`

Estado:

```text
Status: validated_for_declared_scope
Rows: 154,692
Files: 25

Declaracion exacta de scope:
  session-level regime proxy context from `regime_indicators` minute bars;
  `day.parquet` blocked.

Universo cubierto:
  sesiones/regime indicators disponibles en esa fuente.

Cobertura temporal:
  source-driven by regime_indicators; no ticker-level universe.

Acabada para ese scope declarado:
  Si. isolated rerun passed.

Full universe 2005-2026 para todos los tickers/dias:
  No. Es contexto/regimen session-level, no tabla por ticker/dia.

Scope declarado:
  session-level regime proxy from regime_indicators minute bars.

No declara:
  same-session intraday causal state directo,
  regime live decision engine,
  sustituto de microstructure/event state.

Uso permitido hoy:
  contexto de regimen, stratified evaluation, robustness.

Uso prohibido hoy:
  usarlo como senal intradia causal sin estudio adicional.
```

Rol tecnico:

- Contexto de regimen por sesion/indicadores.

Rol filosofico:

- El mismo patron puede comportarse distinto en regimenes distintos.

Uso:

- Feature contextual.
- Stratified evaluation.
- Robustness.

Limitacion:

- No es causal intraday state directo.

Asociaciones:

- Se une con `market_calendar`, `market_state`, `event_state`, outcomes y
  strategy evaluation para stratified analysis.
- Debe usarse para comparar robustez por regimen, no para reemplazar
  microestructura o eventos.

Limitacion actual:

- Es contexto/proxy session-level. No es un motor causal intradia ni una senal
  directa de entrada. `day.parquet` esta bloqueado segun el scope declarado.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/regime_indicators/
- tests/data_foundation_outputs/README.md

Inputs RAW auditados:
  E:/TSIS/data/regime_indicators/

Output institucional Data Foundation:
  E:/TSIS/data/data_foundation_outputs/regime_context_table/

Tests de output Data Foundation:
  isolated rerun passed.
    - regime_context_table_rows = 154,692.
    - files = 25.

Lectura obligatoria:
  regime context = stratification/robustness context.
  No sustituye same-session intraday causal state.
```

### 19. `float_context_table`

Estado:

```text
Status: pending / not_materialized
Rows: 0 official rows

Declaracion exacta de scope:
  no existe tabla oficial; solo requerimiento de future `float_context_table`.

Universo cubierto:
  ninguno institucional a 2026-07-01.

Cobertura temporal:
  ninguna institucional.

Acabada para ese scope declarado:
  No. Pendiente de fuente y builder.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Scope esperado:
  point-in-time float/shares/free-float context.

Fuente:
  no definida/promocionada a 2026-07-01.

No declara:
  hard filter institucional por float,
  daily float history,
  market-cap reconstruction,
  free-float point-in-time.

Uso permitido hoy:
  documentar necesidad y buscar fuentes.

Uso prohibido hoy:
  usar float como filtro institucional sin cobertura point-in-time auditada.
```

Campos esperados:

```text
ticker
instrument_id
as_of_date
float_shares
shares_outstanding
free_float_pct
source
source_document
source_field
point_in_time_valid
quality_state
is_estimated
```

Rol tecnico:

- Proveer float/shares point-in-time.

Rol filosofico:

- Float bajo es central para microcap momentum, pero si no es point-in-time
  puede introducir leakage.

Uso actual:

- No usar como hard filter institucional hasta tener fuente y cobertura
  auditadas.

Asociaciones:

- Debe unirse con `instrument_master`, `fundamentals_asof_table`,
  `master_daily_table`, scanners, market-cap reconstruction y strategy overlays.
- Puede alimentar filtros long/squeeze cuando sea point-in-time, pero hoy no
  debe ser autoridad institucional.

Limitacion actual:

- No existe tabla oficial ni fuente point-in-time validada. El float visible en
  notebooks/runs puede estar vacio o no gobernado. Cualquier filtro por float
  en estrategias debe declararse experimental hasta que exista esta tabla.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- tests/data_foundation_outputs/README.md

Estado documental:
  pendiente / not_materialized.

Output institucional Data Foundation:
  no existe a 2026-07-01.

Requisito documentado:
  ticker
  instrument_id
  as_of_date
  float_shares
  shares_outstanding
  free_float_pct
  source
  source_document
  source_field
  point_in_time_valid
  quality_state
  is_estimated

Lectura obligatoria:
  float es importante para microcaps, pero sin point-in-time validado puede
  introducir leakage y reconstruccion falsa de market cap.
```

### 20. `short_sale_constraints_table`

Estado:

```text
Status: blocked / not_materialized
Rows: 0 official rows

Declaracion exacta de scope:
  no existe tabla oficial; requerimiento de SSR/borrow/locate/availability.

Universo cubierto:
  ninguno institucional a 2026-07-01.

Cobertura temporal:
  ninguna institucional.

Acabada para ese scope declarado:
  No. Bloqueada por fuente oficial/vendor/broker o proxy validado.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Scope esperado:
  SSR, borrow, locate, availability y restricciones broker/vendor as-of.

Fuente:
  pendiente de fuente oficial/vendor/broker o proxy validado.

No declara:
  realismo short institucional.

Uso permitido hoy:
  documentar requisitos y preparar integracion futura.

Uso prohibido hoy:
  simular short strategies como si siempre hubiera borrow/locate.
```

Debe cubrir:

- SSR;
- borrow availability;
- locate availability;
- broker constraints;
- source latency;
- as-of time;
- historical availability cuando exista.

Rol filosofico:

- Una estrategia short no es realista si asume que siempre se puede shortear.

Rol tecnico:

- Debe modelar restricciones reales de short: SSR, borrow, locate,
  availability, broker/platform source, timestamp y calidad de la fuente.

Asociaciones:

- Se une con `short_context_table`, `market_state`, `event_state`,
  execution simulator, strategy overlays short y live trading.

Limitacion actual:

- Esta bloqueada porque no hay fuente oficial/vendor/broker promocionada ni
  proxy validado. `short_context_table` no sustituye esta tabla.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- tests/data_foundation_outputs/README.md

Estado documental:
  blocked / not_materialized.

Output institucional Data Foundation:
  no existe a 2026-07-01.

Fuentes requeridas:
  official/vendor/broker SSR.
  borrow/locate/availability.
  broker/platform capture para live si aplica.

Lectura obligatoria:
  sin esta tabla no hay realismo institucional para estrategias short.
```

### 21. `real_time_corporate_event_alerts_table`

Estado:

```text
Status: blocked / future_live
Rows: 0 official rows

Declaracion exacta de scope:
  no existe tabla oficial; requerimiento futuro para offerings/filings/news
  real-time con latencia.

Universo cubierto:
  ninguno institucional a 2026-07-01.

Cobertura temporal:
  ninguna institucional.

Acabada para ese scope declarado:
  No. Bloqueada por feed/fuente/latencia.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Scope esperado:
  offerings, SEC filings, PR/newswire, headlines y alertas corporativas con
  detection timestamp y source latency.

Fuente:
  pendiente de SEC EDGAR, newswire/vendor, broker/platform feed o API live.

No declara:
  alerta live de segundos,
  historical full feed,
  coverage de offerings.

Uso permitido hoy:
  diseno de contrato y fuente.

Uso prohibido hoy:
  backtest/live trading de offerings sin feed y latencia gobernados.
```

Debe cubrir:

- offerings;
- filings SEC/EDGAR;
- PR/newswire;
- catalyst headlines;
- source latency;
- detection timestamp;
- vendor/broker feed lineage.

Rol filosofico:

- En microcaps, segundos importan.
- Una alerta de offering puede destruir el precio antes de que una vela diaria
  lo explique.

Rol tecnico:

- Debe capturar eventos corporativos live/historicos con `published_utc`,
  `received_utc`, source latency, ticker attribution, event type y lineage.

Asociaciones:

- Se une con `news_context_table`, `market_state`, `event_state`,
  strategy_candidate_events, offering-dump research, live risk controls y
  future DAS/broker/platform feeds.

Limitacion actual:

- No existe feed promocionado. `news_context_table_v0_1` no es equivalente a
  alerta live de segundos. Para offerings y filings se necesita fuente con
  latencia declarada.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/

Estado documental:
  blocked / future_live.

Output institucional Data Foundation:
  no existe a 2026-07-01.

Fuentes candidatas futuras:
  SEC EDGAR APIs para filings oficiales.
  newswire/vendor feed para low-latency headlines.
  broker/platform/API live feed cuando tenga contrato de latencia.

Lectura obligatoria:
  historical context != real-time alert.
  live alert table requiere received time y source latency, no solo publish time.
```

### 22. `market_state_table_v0_1`

Estado:

```text
Official status: not_materialized
Official rows: 0
Declaracion exacta de scope oficial:
  no existe `market_state_table_v0_1` institucional.

Universo cubierto oficial:
  ninguno. Solo existe candidate controlado.

Cobertura temporal oficial:
  ninguna full-universe.

Acabada para scope oficial:
  No.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Candidate:
  market_state_table_v0_1_candidate_microstructure_halt_controlled
  rows: 50
  tickers: 9
  event_windows: 50
  valid_for_event_context: 50
  valid_for_ml: 0
  valid_for_rl: 0
  full_universe_claim_rows: 0
  quality: state_review_microstructure_seed_only

Promotion:
  candidate_not_promoted

Scope declarado del candidate:
  controlled microstructure/halt sample for schema and architecture.

No declara:
  institutional market_state,
  full-universe state,
  ML/RL-ready state.

Uso permitido hoy:
  arquitectura, pruebas controladas, pattern discovery limitado.

Uso prohibido hoy:
  training primary, RL, backtest/execution institutional.
```

Rol tecnico:

- Snapshot gobernado de lo que TSIS sabia sobre instrumento/mercado en un
  timestamp.

Columnas minimas esperadas:

```text
market_state_id
state_version
instrument_id
ticker
observation_time_utc
data_availability_cutoff_utc
session_date
event_clock
event_candidate_id
event_id
source_lineage
quality_state
feature_domains
leakage_boundary
promotion_state
```

Namespaces esperados:

```text
identity__
calendar__
daily__
intraday__
microstructure__
halts__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
lineage__
```

Rol filosofico:

- Es la memoria legal del sistema.
- Es lo que se entrega a modelos, estrategias y evaluadores como "lo que se
  podia saber".

Asociaciones:

- Integra identidad, calendario, daily, intraday, microestructura, halts,
  fundamentals, news, short context, constraints, regime, quality y lineage.
- Debe alimentar ML supervisado, imitation learning, offline RL, backtests,
  strategy evaluators y AlphaEvolve solo cuando sea promocionada.

Limitacion actual:

- No existe tabla oficial institucional. El candidate de 50 filas sirve para
  probar schema/integracion, no para entrenar, backtestear ni ejecutar. No
  declara full universe, ni ML-ready, ni RL-ready.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- tests/data_foundation_outputs/README.md

Output/candidate:
  E:/TSIS/data/data_foundation_outputs/market_state_table/

Candidate controlado:
  market_state_table_v0_1_candidate_microstructure_halt_controlled
    - rows = 50.
    - tickers = 9.
    - event_windows = 50.
    - valid_for_ml = 0.
    - valid_for_rl = 0.
    - full_universe_claim_rows = 0.

Tests:
  market/event state tests passed 2026-06-29.

Lectura obligatoria:
  candidate controlled sample != official market_state_table_v0_1.
  La tabla final requiere coverage, as-of, quality inheritance, feature/label
  separation y promotion gate.
```

### 23. `event_state_table_v0_1`

Estado:

```text
Official status: not_materialized
Official rows: 0

Declaracion exacta de scope oficial:
  no existe `event_state_table_v0_1` institucional.

Universo cubierto oficial:
  ninguno. Solo existe candidate controlado.

Cobertura temporal oficial:
  ninguna full-universe.

Acabada para scope oficial:
  No.

Full universe 2005-2026 para todos los tickers/dias:
  No.

Candidate:
  event_state_table_v0_1_candidate_microstructure_halt_controlled
  rows: 50
  tickers: 9
  event_windows: 50
  pre_event: 25
  post_event_review: 25
  valid_for_pattern_discovery: 50
  valid_for_ml: 0
  valid_for_rl: 0
  full_universe_claim: 0
  quality: event_state_review_microstructure_seed_only

Promotion:
  candidate_not_promoted

Scope declarado del candidate:
  controlled event-state sample around microstructure/halt contexts.

No declara:
  official event_state,
  event library coverage,
  strategy event coverage,
  ML/RL-ready event states.

Uso permitido hoy:
  pattern discovery controlado y validacion de schema.

Uso prohibido hoy:
  usar como dataset entrenable institucional.
```

Rol tecnico:

- Vista del estado alrededor de un evento o transicion.
- No es solo `market_state` repetido; agrega rol dentro de una ventana:
  pre-event, trigger, post-event, review, label horizon.

Rol filosofico:

- TSIS no quiere estudiar "tickers" en abstracto.
- TSIS quiere estudiar eventos: first push, halt, offering, reclaim, backside,
  red day, resistance rejection, short squeeze, liquidity withdrawal.

Uso:

- Pattern discovery.
- Strategy research.
- ML feature table cuando sea promocionada.
- Offline RL state base cuando exista accion/reward/simulator.

Asociaciones:

- Depende de `market_state_table`, `event_windows_table`,
  `strategy_candidate_events_table`, outcomes y futuros action/reward datasets.
- Debe conectar evento, rol temporal, contexto anterior/posterior y frontera de
  leakage.

Limitacion actual:

- No existe tabla oficial institucional. El candidate controlado prueba forma y
  pattern discovery limitado, pero no cubre todos los eventos ni contiene
  labels/rewards/acciones suficientes para ML/RL institucional.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- tests/data_foundation_outputs/README.md

Output/candidate:
  E:/TSIS/data/data_foundation_outputs/event_state_table/

Candidate controlado:
  event_state_table_v0_1_candidate_microstructure_halt_controlled
    - rows = 50.
    - tickers = 9.
    - event_windows = 50.
    - pre_event = 25.
    - post_event_review = 25.
    - valid_for_pattern_discovery = 50.
    - valid_for_ml = 0.
    - valid_for_rl = 0.
    - full_universe_claim = 0.

Tests:
  market/event state tests passed 2026-06-29.

Lectura obligatoria:
  event_state candidate != trainable institutional dataset.
  La tabla final necesita biblioteca de eventos, outcomes/rewards separados y
  cutoffs as-of.
```

### 24. `strategy_candidate_events_table`

Estado:

```text
Status: expected_per_strategy / not_global_materialized
Rows:
  0 official global rows.

Declaracion exacta de scope:
  no hay tabla global; cada estrategia debe declarar su propio scope.

Universo cubierto:
  ninguno global institucional.

Cobertura temporal:
  ninguna global institucional.

Acabada para ese scope declarado:
  No.

Full universe 2005-2026 para todos los tickers/dias:
  No. Se construira por estrategia y denominador.

Scope esperado:
  cada estrategia debe crear su propia tabla de eventos candidatos, con
  denominador, reglas, ventanas, lineage, quality flags y outcomes separados.

Ejemplos:
  DAS frontside candidate events,
  First Red Day candidate events,
  Short Into Resistance candidate events,
  Halt continuation candidate events,
  Offering dump candidate events.

No declara:
  una estrategia global unica,
  que el scanner sea una estrategia,
  que los winners definan el universo.

Uso permitido hoy:
  diseno por estrategia y research controlado.

Uso prohibido hoy:
  seleccionar solo winners y llamarlo denominador.
```

Rol tecnico:

- Cada estrategia define eventos candidatos propios.
- Ejemplos:
  - DAS frontside candidate;
  - Short Into Resistance candidate;
  - First Red Day candidate;
  - Halt continuation candidate;
  - Offering dump candidate.

Rol filosofico:

- El scanner global no debe convertirse en estrategia.
- La estrategia consume denominadores y estados; no redefine la fuente.

Asociaciones:

- Consume `daily_scanner_candidates_table`, `intraday_scanner_candidates_table`,
  `market_state_table`, `event_state_table`, outcomes y strategy-specific
  overlays.
- Cada estrategia debe documentarse en `00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/`.

Limitacion actual:

- No hay tabla global institucional porque no debe existir una unica estrategia
  global. Cada estrategia tiene que construir su denominador, eventos,
  ventanas, labels y criterios good/review/bad sin seleccionar solo winners.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/
- 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md

Estado documental:
  expected_per_strategy / not_global_materialized.

Output institucional global:
  no existe a 2026-07-01.

Ejemplo actual:
  DAS tiene documentos de research/overlay, pero no debe sustituir el scanner
  global ni convertirse en denominador universal.

Lectura obligatoria:
  estrategia != scanner global.
  strategy overlay se aplica despues del denominador observable.
```

### 25. `data_quality_report`

Estado:

```text
Status: required_governance_output / partially_documented_by_family
Rows:
  no aplica necesariamente como rows; es artefacto documental/reporting.

Declaracion exacta de scope:
  governance/reporting de calidad por familia/tabla/run; no dataset tabular
  unico terminado.

Universo cubierto:
  parcial por familias ya auditadas; no homogeneo para todas las familias.

Cobertura temporal:
  depende de cada familia/inspection dossier.

Acabada para ese scope declarado:
  No como sistema global unificado. Parcial por familias con evidencia fuerte.

Full universe 2005-2026 para todos los tickers/dias:
  No aplica como tabla de mercado; debe documentar cobertura por familia.

Scope esperado:
  reportes humanos y visuales de calidad por familia, dataset, tabla,
  evidencia, limitaciones y readiness.

Estado actual:
  trades/quotes/daily/1m tienen evidencia mas fuerte.
  familias nuevas requieren homogeneizacion al mismo estandar visual/forense.

No declara:
  feature modelable,
  source of truth de precios,
  sustituto de validators/manifests.

Uso permitido hoy:
  auditoria humana, inspeccion institucional, promotion gates.
  
Uso prohibido hoy:
  usarlo como input directo de modelos o como reemplazo de datos.
```

Rol tecnico:

- Agrupa evidencia humana: imagenes, casos good/review/bad, estadisticas,
  limitaciones, manifests y conclusiones de calidad.

Rol filosofico:

- Una tabla no es institucional solo porque exista.
- Debe poder explicarse a un inspector humano con evidencia concreta.

Asociaciones:

- `inspection_dossiers`.
- Validators.
- Status matrix.
- Promotion gates.
- Future Graphify evidence maps.

Limitacion actual:

- No existe todavia un sistema global homogeneo para todas las familias con el
  mismo nivel visual/forense de quotes/trades/daily/1m. Donde haya reportes
  parciales, deben tratarse como evidencia de su familia/scope, no como
  certificacion total de toda la Data Foundation.

#### Evidencia De Auditoria Que Sustenta Este Estado

```text
Donde inspeccionar el detalle:
- 01_foundations/inspection_dossiers/
- 01_foundations/validators/
- 01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_research/01_auditoria_RAW_DATA/00_data_certification/
- 01_foundations/data_quality_report/

Evidencia fuerte conocida:
  quotes:
    inspection_dossiers/quotes/quotes_inspection_readout_v0_1.md
    inspection_dossiers/quotes/good_justification/quotes_good_cases_v0_1.md
    inspection_dossiers/quotes/flagged_case_evidence_packs/quotes_review_cases_v0_1.md
    inspection_dossiers/quotes/bad_case_evidence_packs/quotes_bad_cases_v0_1.md

  trades:
    inspection_dossiers/trades/trades_global_universe_readout_v0_1.md
    inspection_dossiers/trades/population_evidence_packs/trades_population_readout_v0_1.md
    inspection_dossiers/trades/family_case_evidence_packs/family_casepacks_index_v0_1.md

Estado documental:
  required_governance_output / partially_documented_by_family.

Lectura obligatoria:
  data_quality_report = evidencia humana y promotion gate.
  No es feature modelable ni reemplazo de validators/manifests.
```

## Como Buscar Estrategias Con Estas Tablas

El proceso correcto no es:

```text
buscar winners
-> construir tabla solo con winners
-> entrenar modelo
```

Eso genera sesgo.

El proceso correcto es:

```text
1. Definir denominador observable.
2. Definir in-play candidate universe.
3. Definir evento candidato.
4. Construir event_state con informacion as-of.
5. Separar outcome posterior.
6. Comparar winners, failures y neutral cases.
7. Formular hipotesis.
8. Validar fuera de muestra.
9. Solo despues promover features o estrategia.
```

Ejemplo DAS/frontside:

```text
base eligible smallcap
-> intraday in-play momentum candidate
-> first cross +50% / tradability / segment
-> DAS event candidate
-> frontside state
-> first dip / reclaim / failure / backside
-> outcome separado
```

Ejemplo First Red Day:

```text
base eligible smallcap
-> daily/intraday in-play momentum history
-> prior run-up / extension
-> first red daily event candidate
-> daily event_state
-> next-day or multi-day outcomes
```

Ejemplo Short Into Resistance:

```text
base eligible smallcap
-> in-play candidate
-> resistance lookback 20/60/90/252
-> distance to resistance
-> prior touches / failed breaks
-> intraday approach to level
-> borrow/SSR constraints cuando existan
-> outcome separado
```

## ML, Imitation Learning, Offline RL Y AlphaEvolve

### ML Supervisado

ML debe recibir:

```text
X = market_state / event_state features as-of
y = outcomes posteriores separados
```

Puede buscar:

- probabilidad de continuation;
- probabilidad de failure;
- probabilidad de halt;
- expected move;
- probability of backside;
- quality of setup;
- meta-labeling de senales humanas/algoritmicas.

No debe recibir:

- future high/low dentro de features;
- outcome como columna de estado;
- filas solo de winners;
- datasets sin denominator.

### Imitation Learning

Imitation learning no aprende "lo que paso"; aprende acciones expertas:

```text
state_t
expert_action_t
optional confidence/context
```

Para TSIS necesitaremos:

- logs de decision humana o estrategia experta;
- timestamp exacto de decision;
- estado disponible en ese instante;
- acciones no tomadas si se quieren comparar;
- fills o simulacion de ejecucion si aplica.

Estado actual:

```text
No listo.
Faltan action logs/fills/expert policy datasets gobernados.
```

### Offline RL

Offline RL necesita transiciones:

```text
state_t
action_t
reward_t
state_t_plus_1
done
policy_behavior_metadata
```

Para microcaps, ademas necesita:

- execution realism;
- slippage/fill probability;
- halt risk;
- borrow/SSR para shorts;
- liquidity constraints;
- out-of-distribution guards.

Estado actual:

```text
No listo para RL institucional.
Los componentes actuales preparan el camino, pero no son dataset RL.
```

### AlphaEvolve / Evolution Systems

AlphaEvolve-style TSIS no debe modificar el juez.

Puede proponer:

- nuevas features;
- nuevas definiciones de eventos;
- nuevas reglas de estrategia;
- nuevas policies;
- nuevos filtros;
- optimizaciones de codigo.

Pero debe evaluarse con:

- data versionada;
- estado as-of;
- outcomes separados;
- evaluator bloqueado;
- fitness cientifico;
- penalizacion por overfitting y complejidad.

## Que Esta 100% Terminado Y Que No

### Terminado Para Su Scope Declarado

Estas tablas pueden usarse hoy dentro de lo que declaran:

- `instrument_master_v0_1`
- `market_calendar_v0_1`
- `expected_data_calendar_v0_1`
- `corporate_actions_table_v0_1`
- `dataset_certification_matrix_v0_1`
- `master_daily_table_v0_1`
- `halts_table_v0_1`
- `event_windows_table_v0_1`
- `outcomes_table_v0_1`
- `fundamentals_asof_table_v0_1`
- `news_context_table_v0_1`
- `short_context_table_v0_1`
- `regime_context_table_v0_1`

Importante:

```text
Terminado para su scope declarado no significa que todo TSIS este terminado.
```

### Materializado Pero No Promocionado

- `ohlcv_1m_split_normalized_full_universe_candidate`
- `microstructure_features_table_v0_2_candidate_controlled_25_per_role`
- `market_state_table_v0_1_candidate_microstructure_halt_controlled`
- `event_state_table_v0_1_candidate_microstructure_halt_controlled`
- replays de `daily_scanner_candidates_table`
- replays de `intraday_scanner_candidates_table`

### Input Promovido Disponible

- `ohlcv_1m_quote_guarded repair_manifest_lt1b_v0_1`: PASS, 301278342 rows,
  4824 LT1B tickers completed, 0 missing.

### En Progreso

- consumo de la vista 1m quote-guarded/split-safe en loaders downstream;
- scanner intradia 20-year quote-guarded candidate;
- master intraday broader/full scope.

### Pendiente / Bloqueado

- `float_context_table`
- `short_sale_constraints_table`
- `real_time_corporate_event_alerts_table`
- `market_state_table_v0_1` oficial
- `event_state_table_v0_1` oficial
- strategy-specific event tables por estrategia;
- ML-ready event-state datasets;
- imitation learning datasets;
- offline RL transition datasets.

## Respuesta Directa A Preguntas Operativas

### Estan las tablas de estado 100% full terminadas?

No.

Hay muchos componentes terminados para su scope, pero las tablas finales:

```text
market_state_table_v0_1
event_state_table_v0_1
```

no estan institucionalizadas full universe.

### El diario esta terminado?

`master_daily_table_v0_1` esta materializada y validada para su scope diario.
Eso permite research diario serio, pero no contiene todas las columnas de un
estado completo.

### Se puede usar para buscar "primer dia rojo"?

Si, como estrategia daily research, con condiciones:

- declarar universo;
- usar `master_daily_table_v0_1`;
- declarar `price_view`;
- controlar splits/corporate actions;
- aplicar quality flags;
- separar labels/outcomes;
- no llamarlo `market_state` completo si no se unen contextos adicionales.

Para version mas institucional, unir:

- halts/event windows;
- news as-of;
- short context;
- regime context;
- fundamentals as-of;
- future float context cuando exista.

### Para que sirve la tabla split-normalized 1m candidate?

Sirve para corregir el problema de splits en archivos 1m afectados. Es una
pieza para construir una vista intradia mas legal, no el producto final.

### Que falta para tener intradia operativo?

1. Consumir el manifest LT1B promovido `repair_manifest_lt1b_v0_1`.
2. Definir vista oficial downstream:

```text
raw ohlcv_1m
+ split-normalized affected view
+ quote-guarded repair overlay
= official intraday 1m view
```

3. Materializar/validar `master_intraday_bar_table` o loader equivalente.
4. Rehacer scanner intradia sobre esa vista.
5. Construir event windows de estrategia.
6. Construir microstructure/event_state en ventanas gobernadas.

## Secuencia Recomendada Desde Aqui

1. Cerrar consumo downstream de `ohlcv_1m_quote_guarded`:
   - builder preflight contra `repair_manifest_lt1b_v0_1`;
   - validation report de candidate tables;
   - promotion decision de los consumers;
   - consumption policy ya alineada al manifest LT1B.

2. Resolver promocion de `ohlcv_1m_split_normalized_full_universe_candidate`:
   - que cubre;
   - que no cubre;
   - como entra en loader.

3. Definir vista intradia oficial:

```text
official_1m_view = raw + split + quote_guarded
```

4. Rehacer `intraday_scanner_candidates_table` 20-year candidate sobre la vista
   oficial o marcar explicitamente raw diagnostic.

5. Crear denominadores:
   - base eligible smallcap;
   - intraday in-play momentum;
   - daily in-play where relevant.

6. Para cada estrategia:
   - crear `strategy_candidate_events_table`;
   - crear event windows;
   - crear `event_state_candidate`;
   - crear outcomes;
   - analizar winners/failures/neutral cases.

7. Promocionar solo despues de:
   - schema;
   - manifest;
   - tests;
   - anti-leakage;
   - quality inheritance;
   - visual/forensic cases;
   - documentation;
   - changelog.

8. Solo despues construir:
   - ML feature datasets;
   - imitation learning datasets;
   - offline RL transition datasets.

## Fuentes Internas Que Soportan Este Snapshot

Leer estos documentos antes de modificar esta linea de trabajo:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/README.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/intraday_scanner_candidates_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/ohlcv_1m_quote_guarded_repair_manifest_policy_v0_1.md
```

## Regla Final

Si un futuro agente no sabe si una tabla es:

```text
component
candidate
event boundary
outcome
market_state
event_state
strategy overlay
ML dataset
RL transition dataset
```

entonces no debe promocionarla ni usarla como fuente institucional.

Debe documentar:

- que sabe;
- que no sabe;
- que fuente usa;
- que cutoff aplica;
- que calidad hereda;
- que consumer esta permitido;
- y que consumer esta prohibido.

Ese es el estandar minimo para que TSIS siga siendo una maquina cientifica y
no una coleccion de backtests ambiguos.
