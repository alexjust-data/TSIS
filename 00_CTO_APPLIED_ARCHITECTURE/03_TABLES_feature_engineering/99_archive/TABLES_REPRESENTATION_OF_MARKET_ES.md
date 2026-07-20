# Representacion Del Mercado En Las Tablas

Status: `feature_engineering_guardrails_v0_1`

Date: `2026-07-16`

Scope:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

Este documento define los guardrails para auditar y disenar variables en las tablas de TSIS. No sustituye schemas, contratos, registries, validadores, manifests ni matrices de estado.

Existe para responder una pregunta operativa antes de aceptar o anadir cualquier variable:

```text
Que necesitamos saber
para describir correctamente
el estado del mercado
en un instante t?
```

Y una pregunta cientifica:

```text
Que informacion puede ayudar
a explicar o predecir
el comportamiento futuro
del fenomeno representado?
```

---

## 1. Autoridad

Este documento debe leerse bajo:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\00_EPISTEMOLOGICAL_architecture
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\01_REPRESENTATION_MATERIALIZATION_REVIEW
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\02_MATERIALIZATION_GOVERNANCE_REVIEW
```

La autoridad operativa sigue viviendo en:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

Por tanto:

```text
encaje_conceptual != materializado
materializado != validado
validado != promovido
promovido != uso_irrestricto_para_todos_los_consumidores
```

---

## 2. Rol De Este Documento

Gobierna la lectura de feature engineering de las tablas:

```text
000-018
```

Su objetivo es evitar acumular ruido en las tablas finales de estado e investigacion.

Para cada tabla, TSIS debe poder explicar:

- que representa la tabla;
- que no debe representar;
- que variables se crearon;
- si cada variable es raw, derivada, contextual, de gobernanza o outcome;
- que hipotesis cientifica representa cada variable derivada;
- por que esas variables y no otras;
- que consumidor downstream usa cada variable;
- si ayuda a describir market state en `t`;
- si ayuda a explicar o predecir el fenomeno representado;
- si introduce leakage, redundancia o ruido injustificado.

---

## 3. Regla De Admision De Variables

Ninguna variable debe entrar en TSIS solo porque sea comun.

Justificacion prohibida:

```text
Porque todo el mundo la usa.
```

Cada variable debe responder:

```text
Por que esta variable merece existir?
Que hipotesis cientifica representa?
Que decision, estado, evento, outcome o gate de auditoria puede usarla?
```

Ejemplos:

```text
Variable: distance_to_vwap
Hipotesis: la distancia al precio medio negociado puede influir en reversion,
continuacion o participacion forzada.
```

```text
Variable: relative_volume
Hipotesis: la intensidad de participacion condiciona el comportamiento futuro
de precio, liquidez y validez de eventos.
```

```text
Variable: gap_percent
Hipotesis: el desequilibrio overnight modifica el regimen observado durante la sesion.
```

---

## 4. Coste Cientifico De Una Variable

Toda variable tiene coste cientifico:

- complejidad;
- riesgo de overfitting;
- correlacion con variables existentes;
- ruido;
- coste computacional;
- coste de interpretacion;
- riesgo de leakage;
- carga de gobernanza;
- riesgo de mal uso downstream.

Estado por defecto de una variable nueva:

```text
not_accepted_until_justified
```

---

## 5. Clasificacion De Variables

Cada columna fisica debe clasificarse en una clase primaria:

```text
identity
raw_observable
derived_observable
context
quality_gate
lineage
asof_control
event_descriptor
outcome_label
governance_status
```

Reglas:

- `identity` localiza la entidad.
- `raw_observable` conserva dato observado directo.
- `derived_observable` transforma observaciones sin leakage futuro.
- `context` describe condiciones alrededor.
- `quality_gate` protege consumidores downstream.
- `lineage` conserva fuente y reproducibilidad.
- `asof_control` impone legalidad temporal.
- `event_descriptor` describe evento o ventana.
- `outcome_label` debe quedar fuera de state/features.
- `governance_status` describe certificacion, promocion o gates de uso.

Si una columna no puede clasificarse, debe revisarse.

---

## 6. Familias De Representacion De Mercado

Las variables se clasifican por familia de informacion, no por nombre de indicador:

```text
Market Representation

|-- Precio
|-- Tendencia
|-- Volatilidad
|-- Liquidez
|-- Participacion
|-- Microestructura
|-- Temporalidad
|-- Contexto Diario
|-- Contexto Intradia
|-- Noticias
|-- Fundamentales
|-- Regimen
|-- Eventos
|-- Estructura
```

Cada familia debe responder:

```text
Que fenomeno de mercado representa?
Que hipotesis cientifica la justifica?
Que preguntas permite responder?
Que variables minimas representan esa informacion?
En que tabla deben vivir?
Quien consume esa informacion?
```

---

## 7. Definiciones De Familias

### Precio

Fenomeno: nivel y localizacion del precio observado.

Hipotesis: la posicion absoluta y relativa del precio condiciona continuacion, reversion, validez de eventos y riesgo de ejecucion.

Preguntas:

- Donde esta el precio ahora?
- Esta cerca de open, close, HOD, LOD, VWAP o referencias previas?
- El movimiento sobrevive al quote guarding?

Variables minimas:

```text
open
high
low
close
vwap
distance_to_vwap
distance_to_hod
distance_to_lod
raw_vs_quote_guarded_difference
```

Tablas probables: `004`, `013`, `014`, `016`, `017`.

### Tendencia

Fenomeno: persistencia o cambio direccional en el tiempo.

Hipotesis: la pendiente y persistencia del movimiento afectan continuacion, agotamiento y transiciones de evento.

Variables minimas:

```text
return_1m
return_5m
return_15m
slope
rolling_close_change
consecutive_up_down_minutes
trend_alignment_daily_intraday
```

Tablas probables: `014`, `015`, `016`, `017`.

### Volatilidad

Fenomeno: magnitud e inestabilidad del movimiento.

Hipotesis: expansion, compresion e inestabilidad alteran riesgo, continuacion y fallo.

Variables minimas:

```text
range_pct
true_range_proxy
rolling_range_5m
rolling_range_15m
rolling_volatility
volatility_expansion_ratio
compression_flag
```

Tablas probables: `004`, `014`, `015`, `016`, `017`.

### Liquidez

Fenomeno: facilidad o dificultad de transaccionar sin impacto excesivo.

Hipotesis: la liquidez condiciona impacto, fiabilidad de evento y riesgo de ejecucion.

Variables minimas:

```text
volume
dollar_volume
rolling_dollar_volume
liquidity_bucket
tradability_gate
```

Tablas probables: `004`, `014`, `015`, `016`.

### Participacion

Fenomeno: intensidad y anormalidad de participacion.

Hipotesis: la intensidad de participacion distingue atencion real, ignicion de eventos y artefactos raw.

Variables minimas:

```text
relative_volume
volume_zscore
volume_acceleration
trade_count_proxy
participation_regime
```

Tablas probables: `014`, `015`, `016`, `017`, `018`.

### Microestructura

Fenomeno: interaccion fina entre trades, quotes, spread, depth y order flow.

Hipotesis: order flow, quotes y presion de liquidez revelan calidad de evento que las velas solas no expresan.

Variables minimas:

```text
spread
quote_count
quote_guarded_repair_applied
signed_flow
ofi
microprice
imbalance
depth_proxy
```

Regla: si no se usan trades/quotes, llamar `proxy`; no llamar microestructura real a variables solo de velas.

### Temporalidad

Fenomeno: el significado cambia con hora, fase de sesion y calendario.

Variables minimas:

```text
session_date
minute_of_session
session_phase
minutes_from_open
minutes_to_close
is_early_close
calendar_expected_session
```

### Contexto Diario

Fenomeno: condicion diaria alrededor de una observacion intradia.

Variables minimas:

```text
prior_close
gap_percent
daily_range
daily_volume
daily_quality_state
corporate_action_context
halt_context
```

### Contexto Intradia

Fenomeno: estructura de la sesion antes, durante y despues de un evento intradia.

Variables minimas:

```text
session_hod
session_lod
distance_to_session_hod
distance_to_session_lod
intraday_vwap_distance
rolling_activity_state
pre_event_context
```

### Noticias

Fenomeno: flujo externo de informacion asociado al instrumento.

Variables minimas:

```text
news_presence
news_timestamp
news_age
source_type
headline_hash
topic_or_category
asof_news_available
```

### Fundamentales

Fenomeno: contexto financiero y de reporting observable legalmente en `t`.

Variables minimas:

```text
as_of_date
filing_date
period_end
fundamental_metric
metric_staleness
availability_flag
```

### Regimen

Fenomeno: entorno de mercado amplio, sector, indice o volatilidad.

Variables minimas:

```text
regime_symbol
regime_proxy_role
as_of_utc
index_return
volatility_proxy
risk_on_off_state
regime_data_quality
```

### Eventos

Fenomeno: ocurrencias discretas y ventanas alrededor de ellas.

Variables minimas:

```text
event_id
event_family
event_type
event_timestamp
window_role
window_start
window_end
event_source
```

### Estructura

Fenomeno: estructura institucional y relacional necesaria para que las observaciones sean coherentes.

Variables minimas:

```text
instrument_id
ticker
valid_from
valid_to
expected_session
certification_state
lineage_fields
consumption_gate
```

---

## 8. Requisito De Auditoria Por Tabla

Cada carpeta de tabla debe contener una auditoria tecnica basada en:

```text
TABLE_REPRESENTATION_AUDIT_TEMPLATE_ES.md
```

La auditoria debe comparar:

```text
conceptual_expected_state
vs
documented_current_state
vs
physical_observed_state
```

Debe responder:

- cual es el ser de la tabla;
- que familias cubre;
- que variables se crearon;
- por que se crearon;
- que hipotesis representan;
- que variables faltan;
- que variables generan ruido o deben moverse;
- que puede consumir esta tabla ahora;
- que no puede consumirla aun.

---

## 9. Regla Final

No disenar variables por lista de indicadores.

Disenar variables por:

```text
fenomeno
-> hipotesis
-> familia de informacion
-> variables minimas
-> columnas fisicas
-> consumidores
-> evidencia de validacion
```

El objetivo no es hacer tablas mas grandes.

El objetivo es que TSIS pueda describir, testear y gobernar conocimiento de mercado sin supuestos ocultos.

