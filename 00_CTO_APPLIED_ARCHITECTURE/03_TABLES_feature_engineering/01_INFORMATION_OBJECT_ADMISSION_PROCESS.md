**PLANTILLA**

ESPECIFICACIÓN Y CRITERIOS DE ADMISIÓN
DE `OBJETOS DE INFORMACIÓN`
PARA LA REPRESENTACIÓN DEL ESTADO
===

Status: `template_v0_7_state_profile_boundary`
Date: `2026-07-17`

Usar una copia de esta plantilla para cada `Objeto de Información` candidato
a formar parte de la representación del estado.
* Este documento ***no diseña tablas***.
* Sí decide si una determinada información merece formar parte del estado del mercado.
* No debe repetir contratos, schemas ni manifests.
* Sí debe referenciar los documentos, contratos, tablas, artefactos y literatura que justifican su existencia.

**Qué es este documento**

Es un proceso reproducible para identificar, justificar y representar
`objetos de información` que pueden formar parte del estado del mercado.

Las tablas y sus atributos serán una consecuencia de ese proceso.

Responde:

```
¿Qué objeto de información existe?
¿Por qué existe?
¿Cómo se representa?
¿Qué variables lo implementan?
¿Dónde vive?
¿Quién lo consume?
¿Merece formar parte del estado?
```

## Boundary: Object Discovery vs Object Admission

Este documento gobierna el **Object Admission Process**.

No gobierna por si solo el descubrimiento inicial de candidatos.

### Object Discovery Process

Puede empezar desde:

```text
fenomenos observados
preguntas cientificas
RAW observables
capacidades derivables
tablas existentes
variables reales
```

Su resultado es solamente:

```text
candidate_information_object
candidate_variables
candidate_representation_model
source_evidence
```

Discovery no acepta el Objeto.
Discovery no autoriza variables para State.
Discovery no convierte una tabla existente en significado cientifico oficial.

### Object Admission Process

La admision formal siempre debe reconstruir la direccion cientifica:

```text
fenomeno_o_necesidad_cientifica
    -> Objeto de Informacion
        -> Modelo de Representacion
            -> implementacion fisica candidata
                -> legalidad temporal
                    -> decision
```

Las tablas pueden descubrir candidatos.
La admision define el significado.

---
## Filosofía

Premisa

```
¿Qué información debe preservar la representación
para describir correctamente el estado del mercado?

¿Qué información debe contener el estado
para que un agente pueda tomar decisiones óptimas?
```

Disenamos representaciones fisicas de **objetos de informacion** del mercado.

**Concepto: `Objeto de Informacion` :**
```text
Unidad semantica de informacion que TSIS decide preservar
sobre uno o varios fenomenos observables, independiente
de su modelo de representacion y de su implementacion fisica.
```

Un Objeto de Informacion no existe en el mercado como objeto fisico.
Lo construye TSIS como una decision cientifica sobre que informacion merece conservarse.

El Objeto no es aun la representacion.
Es lo que debe ser representado.

Separacion obligatoria:

```text
Liquidity
= Information Object

coste de negociacion + profundidad + disponibilidad
= Representation Model

spread_bps + depth + quote_count
= Physical Implementation
```

Una variable no tiene valor por si misma.
Una variable no entra en TSIS porque sea un indicador conocido.
El objetivo no es construir muchas variables.
El objetivo es construir la representacion minima del mercado que conserve la maxima informacion util.
Una variable entra unicamente si implementa fisicamente un Modelo de Representacion aprobado para un Objeto de Informacion admitido.

Ejemplos:

```
VARIABLES:
- Spread
- Depth
- Quote Count
- OFI
- Microprice

Pero juntas representan un OBJETO DE INFORMACION:
- Liquidez instantánea.
```

```
VARIABLES:
- Gap
- Premarket Volume
- Relative Volume
- Float
- News

Pero juntas representan OBJETO DE INFORMACION:
- Potencial de expansión.
```

```
VARIABLES:
- Return 1m
- Slope
- Higher High
- VWAP Distance

Pero juntas representan un OBJETO DE INFORMACION:
- Momentum.
```

Cada vez que alguien quiera añadir una variable, la primera pregunta debería ser:
```
¿Esta variable incorpora información nueva sobre el estado del mercado
o solo es otra forma de representar información que ya tenemos?
```

**Hay niveles y ejes separados**

El termino `family` no debe usarse sin calificarlo.
TSIS separa cuatro taxonomias distintas:

```text
Information Object Family
= eje semantico: que tipo de informacion preserva el Objeto.

Source Domain
= eje de origen: de que fuente observable procede la evidencia.

Temporal Resolution
= eje temporal: a que granularidad o ventana aplica.

Institutional Role
= eje institucional: para que sirve dentro del sistema.
```

Taxonomia semantica inicial para `Information Object Family`:

```text
Price Dynamics
Trading Activity
Liquidity
Market Microstructure
Instrument Context
External Context
Market Context
```

Taxonomias separadas:

```text
Source Domain:
- OHLCV
- Trades
- Quotes
- News
- Fundamentals
- SEC
- Short
- Halts
- Reference
- Market / Economic Context

Temporal Resolution:
- daily
- intraday_bar
- second
- event_window
- as_of

Institutional Role:
- observable
- quality
- lineage
- governance
- outcome
```

Regla:

```text
No usar una unica columna llamada family para mezclar
semantica, fuente, escala temporal y rol institucional.
```

Ejemplo:

```text
Liquidity
= Information Object

Information Object Family
= Liquidity

Source Domain
= Quotes + Trades + OHLCV

Temporal Resolution
= intraday_bar / event_window

Institutional Role
= observable
```

Pipeline de significado:

```text
Information Object
-> Representation Model
-> Physical Implementation
-> State integration
```

**Proceso inicial**

Te has de preguntar:

```
¿Qué "información" del mercado todavía no está representada?
¿Y cómo podemos representar esa información?
```
Ejemplo

```
---
Información : La liquidity
---
Modelo de representación:
- Spread
- Quoted Depth
- Dollar Volume
- Microprice
- OFI
- Bid Ask Imbalance
```

* Elegimos información.
* Después buscamos la representación mínima de esa información con variables.


Ejemplos

```text
information_object_family:
- Liquidity

source_domain:
- Quotes
- Trades
- OHLCV

temporal_resolution:
- intraday_bar
- event_window

institutional_role:
- observable

OBJETO DE INFORMACION  (Concepto cientifico):
- Liquidity

MODELO DE REPRESENTACION:
- trading cost
- depth
- availability

IMPLEMENTACION FISICA CANDIDATA:
- spread
- depth
- quote_count
- OFI
- microprice
```

```text
information_object_family:
- Trading Activity

source_domain:
- OHLCV
- Trades

temporal_resolution:
- daily
- intraday_bar
- event_window

institutional_role:
- observable

OBJETO DE INFORMACION  (Concepto cientifico):
- Trading Activity

MODELO DE REPRESENTACION:
- participation intensity
- relative activity
- turnover

IMPLEMENTACION FISICA CANDIDATA:
- relative_volume
- trade_count
- dollar_volume
- turnover
```

```text
information_object_family:
- Price Dynamics

source_domain:
- OHLCV

temporal_resolution:
- daily
- intraday_bar
- event_window

institutional_role:
- observable

OBJETO DE INFORMACION  (Concepto cientifico):
- Momentum

MODELO DE REPRESENTACION:
- direction
- intensity
- persistence
- location versus references

IMPLEMENTACION FISICA CANDIDATA:
- slope
- returns
- vwap_distance
- HH_HL_structure
```

**Concepto final**

Un `Objeto de informacion` emerge de una o varias variables conjuntamente.
El significado no está en una variable aislada, sino en la información conjunta.

Las tablas no deberían preguntarse "¿qué columnas añadimos?", sino "**¿qué información necesitamos preservar?**"
y solo después decidir cuál es la representación física mínima y más robusta para conservar esa información.


**Regla para State**

Aceptar un Objeto de Informacion no obliga a meter todas sus variables en una mega-tabla de Market State.

La admision del Objeto decide que informacion merece existir.
El Modelo de Representacion decide como se expresa.
El perfil fisico decide donde se materializa:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Una variable solo puede entrar en el core si es necesaria para la semantica minima del estado.
Las variables pesadas, especializadas o de consumidor deben vivir en perfiles/extensiones gobernadas.


## Arquitectura

```
MERCADO - simplemente existe
↓
FENÓMENOS - ¿Qué fenómenos observables existen?
↓
OBJETO DE INFORMACIÓN - ¿Qué información necesitamos conservar sobre esos fenómenos?
↓
MODELOS DE REPRESENTACIÓN: - ¿Mediante qué conjunto de medidas representamos este Objeto?
↓
IMPLEMENTACIÓN FÍSICA - ¿Qué columnas, fórmulas, ventanas y parámetros implementan esas medidas?
↓
TABLAS - ¿Dónde se materializa esa representación?
↓
Market State - ¿Cuál es el estado observable del mercado en un decision_timestamp?
↓
Event State - ¿Cuál es el estado observable del mercado respecto a un evento?
```

Ejemplos

```
FENÓMENO:
- Hay una fuerte presión compradora.

OBJETO DE INFORMACIÓN:
- Buying Pressure

MODELO DE REPRESENTACIÓN:
- Modelo basado en agresión compradora, desequilibrio y consumo de liquidez:
    - Aggressor Buy Volume
    - Buy/Sell Imbalance
    - Tape Speed
    - Ask Consumption

IMPLEMENTACIÓN FÍSICA:

- aggressor_buy_volume:
    - aggressor_buy_volume
    - aggressor_buy_ratio

- buy_sell_imbalance:
    - buy_sell_imbalance

- tape_speed:
    - tape_speed

- ask_consumption:
    - ask_consumption_rate

TABLAS:
- 015_microstructure_features_table
```
```
FENÓMENO:
- Hay muy poca liquidez.

OBJETO DE INFORMACIÓN:
- Liquidity

MODELO DE REPRESENTACIÓN:
- Modelo basado en coste de negociación, actividad y profundidad:
    - Spread
    - Dollar Volume
    - Quoted Depth

IMPLEMENTACIÓN FÍSICA:

- spread:
    - quotes_spread_bps_median

- dollar_volume:
    - dollar_volume
    - rolling_dollar_volume

- quoted_depth:
    - quotes_top_depth_mean
    - bid_depth_mean
    - ask_depth_mean

TABLAS:
- 004_master_daily_table
- 014_master_intraday_bar_table
- 015_microstructure_features_table
```

```
FENÓMENO:
- El precio está acelerando.

OBJETO DE INFORMACIÓN:
- Momentum

MODELO DE REPRESENTACIÓN:
- Modelo basado en dirección, pendiente y aceleración:
    - Returns
    - Slope
    - Price Acceleration

IMPLEMENTACIÓN FÍSICA:

- returns:
    - return_1m
    - return_5m

- slope:
    - slope

- price_acceleration:
    - rolling_close_change
    - price_acceleration

TABLAS:
- 014_master_intraday_bar_table
```

```
FENÓMENO:
- La participación del mercado aumenta de forma anómala.

OBJETO DE INFORMACIÓN:
- Trading Activity

MODELO DE REPRESENTACIÓN:
- Modelo basado en intensidad de negociación:
    - Relative Volume
    - Volume Acceleration
    - Trade Count

IMPLEMENTACIÓN FÍSICA:

- relative_volume:
    - relative_volume
    - volume_zscore

- volume_acceleration:
    - volume_acceleration

- trade_count:
    - trade_count_proxy

TABLAS:
- 004_master_daily_table
- 014_master_intraday_bar_table
```

```
FENÓMENO:
- El mercado entra en un entorno de alta incertidumbre.

OBJETO DE INFORMACIÓN:
- Volatility

MODELO DE REPRESENTACIÓN:
- Modelo basado en amplitud y expansión:
    - Rolling Volatility
    - True Range
    - Expansion Ratio

IMPLEMENTACIÓN FÍSICA:

- rolling_volatility:
    - rolling_volatility

- true_range:
    - true_range_proxy

- expansion_ratio:
    - rolling_range_5m
    - volatility_expansion_ratio

TABLAS:
- 014_master_intraday_bar_table
- 015_microstructure_features_table
```

```
FENÓMENO:
- Existe un catalizador externo que puede alterar el comportamiento del mercado.

OBJETO DE INFORMACIÓN:
- News Context

MODELO DE REPRESENTACIÓN:
- Modelo basado en existencia, antigüedad y naturaleza del catalizador:
    - News Presence
    - News Age
    - Source Type

IMPLEMENTACIÓN FÍSICA:

- news_presence:
    - news_presence

- news_age:
    - news_timestamp
    - news_age

- source_type:
    - source_type
    - topic_or_category

TABLAS:
- 010_news_context_table
```

```
FENÓMENO:
- La empresa presenta unas características estructurales determinadas.

OBJETO DE INFORMACIÓN:
- Fundamental Context

MODELO DE REPRESENTACIÓN:
- Modelo basado en estructura de capital:
    - Float
    - Market Cap
    - Shares Outstanding

IMPLEMENTACIÓN FÍSICA:

- float:
    - float

- market_cap:
    - market_cap

- shares_outstanding:
    - shares_outstanding

TABLAS:
- 009_fundamentals_asof_table
```
(Si ***market_cap*** o ***shares_outstanding*** todavía no existen en la tabla, quedarían como candidatos futuros.)
```
FENÓMENO:
- El mercado global favorece o perjudica la continuación de los movimientos.

OBJETO DE INFORMACIÓN:
- Market Regime

MODELO DE REPRESENTACIÓN:
- Modelo basado en contexto macro del mercado:
    - Index Return
    - Volatility Proxy
    - Risk On/Off

IMPLEMENTACIÓN FÍSICA:

- index_return:
    - index_return

- volatility_proxy:
    - volatility_proxy

- risk_on_off:
    - risk_on_off_state
    - regime_symbol

TABLAS:
- 012_regime_context_table
```

```
FENÓMENO:
- El precio se encuentra en una posición concreta dentro de la sesión.

OBJETO DE INFORMACIÓN:
- Intraday Position

MODELO DE REPRESENTACIÓN:
- Modelo basado en referencias intradía:
    - Distance to HOD
    - Distance to LOD
    - Distance to VWAP

IMPLEMENTACIÓN FÍSICA:

- distance_to_hod:
    - distance_to_session_hod

- distance_to_lod:
    - distance_to_session_lod

- distance_to_vwap:
    - intraday_vwap_distance

TABLAS:
- 014_master_intraday_bar_table
```



**Consecuencia 1**

Un mismo Objeto de Información puede tener varios modelos de representación.

```
Liquidity
│
├── Modelo A
│     ├── Spread
│     ├── Depth
│     └── Dollar Volume
│
├── Modelo B
│     ├── Kyle Lambda
│     ├── Amihud
│     └── Roll Spread
│
└── Modelo C
      └── Embedding aprendido
```

**Consecuencia 2**

Una misma tabla puede implementar parcialmente varios Objetos de Información.

```
014_master_intraday_bar_table

├── Momentum
│     ├── return_1m
│     ├── slope
│     └── price_acceleration
│
├── Trading Activity
│     ├── relative_volume
│     ├── volume_acceleration
│     └── trade_count_proxy
│
├── Intraday Position
│     ├── distance_to_session_hod
│     ├── distance_to_session_lod
│     └── intraday_vwap_distance
│
└── Volatility
      └── rolling_range_5m
```

**Consecuencia 3**

Un mismo Objeto de Información puede necesitar variables procedentes de varias tablas.

```
Liquidity

↓

004_master_daily_table
    - dollar_volume
    - rvol_20d

014_master_intraday_bar_table
    - volume
    - transaction_count

015_microstructure_features_table
    - quotes_spread_bps_median
    - quotes_top_depth_mean
```

**Concepto clave**
primero defines qué quieres representar, después el modelo conceptual con el que lo representarás, y solo al final eliges las medidas concretas (variables) que implementan ese modelo.

una misma tabla (por ejemplo, 014_master_intraday_bar_table) implementa parcialmente la representación física de varios Objetos de Información (Momentum, Trading Activity, Intraday Position, etc.).

## Proceso de admisión

```
Nuevo Objeto de Información candidato
↓
¿Qué queremos representar?
↓
¿Qué fenómeno del mercado representa?
↓
¿Qué significado científico tiene?
↓
¿Por qué merece existir?
↓
¿Qué preguntas científicas permite responder?
↓
¿Qué hipótesis científica representa?
↓
¿Existe evidencia científica que lo respalde?
↓
¿Quién utilizará esta información?
(Market State, Event State, ML, RL...)
↓
¿Cómo vamos a representar este Objeto?
(Modelo(s) de Representación)
↓
¿Qué variables implementan ese modelo?
↓
¿En qué tablas vivirán esas variables?
↓
¿Existe ya otra representación equivalente?
↓
¿Puede calcularse legalmente en decision_timestamp?
↓
¿Cuál es su coste computacional?
↓
¿Cuánto ruido introduce?
↓
¿Cuál es su ganancia informativa?
↓
¿Debe admitirse dentro de la representación del estado?
```


# PLANTILLA : `Objeto de Información`


## 1. Identificación

### Nombre

```text
<Nombre del Objeto de Información>
```

### Taxonomy Axes

Information Object Family:

```text
<Price Dynamics | Trading Activity | Liquidity | Market Microstructure | Instrument Context | External Context | Market Context | ...>
```

Source Domain:

```text
<OHLCV | Trades | Quotes | News | Fundamentals | SEC | Short | Halts | Reference | Market / Economic Context | ...>
```

Temporal Resolution:

```text
<daily | intraday_bar | second | event_window | as_of | ...>
```

Institutional Role:

```text
<observable | quality | lineage | governance | outcome | ...>
```

Rule:

```text
Do not collapse these axes into a single generic family field.
```

---

## 2. Significado científico

### Información que se desea preservar

```text
¿Qué información del mercado queremos preservar?
```

### Fenómeno del mercado observado

```text
¿Qué fenómeno observable representa?
```

### Significado científico

```text
¿Qué conocimiento aporta al estado del mercado?
```

---

## 3. Justificación científica

### Hipótesis científica

```text
¿Qué hipótesis representa?
```

### Justificación

```text
¿Por qué este Objeto de Información merece formar parte del estado?
```

### Preguntas científicas

```text
¿Qué preguntas permite responder?

•
•
•
```

---

## 4. Evidencia científica

```text
Papers

Libros

Autores

Referencias
```

---

## 5. Modelo(s) de representación

### Modelo A

#### Descripción

```text
¿Cómo representaremos este Objeto?
```

#### Medidas utilizadas

```text
•
•
•
```

#### Ventajas

```text
...
```

#### Limitaciones

```text
...
```

---

### Modelo B (opcional)

#### Descripción

```text
...
```

#### Medidas utilizadas

```text
•
•
•
```

#### Ventajas

```text
...
```

#### Limitaciones

```text
...
```

---

## 6. Implementación física

### Modelo seleccionado

```text
Modelo A
```

### Variables físicas

```text
Concepto:

- variable_1
- variable_2

Concepto:

- variable_3
- variable_4
```

### Variables descartadas

```text
...
```

---

## 7. Materialización

### Tabla principal

```text
...
```

### Tablas auxiliares

```text
...
```

### Tablas opcionales

```text
...
```

---

## 8. Consumidores

```text
Market State
Event State
Scanners
Pattern Discovery
Clustering
Machine Learning
Imitation Learning
Offline RL
Decision Transformer
AlphaEvolve
Execution
Risk Engine
```

---

## 9. Legalidad temporal

```text
¿Puede calcularse completamente en decision_timestamp?

¿Necesita as-of?

¿Existe riesgo de leakage?

¿Tiene dependencias temporales?
```

---

## 10. Evaluación técnica

### Coste computacional

```text
...
```

### Complejidad del estado

```text
Dimensionalidad

Correlación

Overfitting
```

### Estabilidad temporal

```text
¿Es estable entre distintos regímenes?
```

### Ganancia informativa

```text
¿Qué incertidumbre reduce?
```

### Pérdida de información

```text
¿Qué información se perdería si este Objeto desapareciera?
```

---

## 11. Representaciones equivalentes

```text
¿Existe otro Objeto que represente prácticamente la misma información?

¿Existe otro modelo equivalente?

¿Debe reutilizarse?

¿Debe fusionarse?
```

---

## 12. Dependencias

### Requiere

```text
L1

Trades

News

Fundamentals

...
```

### Opcional

```text
L2

MBO

L3

...
```

---

## 13. Impacto sobre el estado

```text
¿Qué aporta este Objeto a Market State?

¿Es obligatorio?

¿Es opcional?

¿Qué ocurre si se elimina?
```

---

## 14. Decisión

```text
Aceptado

Aceptado con restricciones

Pendiente de evidencia

Rechazado
```

### Justificación

```text
...
```

### Condiciones de revisión futura

```text
...
```

---

## 15. Referencias TSIS

```text
Contracts

Schemas

Builders

Validators

Tables

Artifacts

Research

README

Otros documentos relacionados
```
