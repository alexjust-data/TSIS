**PLANTILLA**

ESPECIFICACIÓN Y CRITERIOS DE ADMISIÓN  
DE `OBJETOS DE INFORMACIÓN`  
PARA LA REPRESENTACIÓN DEL ESTADO
=== 

Status: `template_v0_4_information_driven`  
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

## Filosofía

Premisa

```
¿Qué información debe preservar la representación
para describir correctamente el estado del mercado?

¿Qué información debe contener el estado
para que un agente pueda tomar decisiones óptimas?
```

Diseñamos representaciones físicas de **objetos de información** del mercado.

**Concepto: `Objeto de Información` :** 
```
Representación de una propiedad observable del mercado:

- que aporte conocimiento nuevo sobre el estado del mercado
  en un decision_timestamp.

. que ayude a representar su estado de forma más completa
  para tomar una decisión óptima.
```

Una variable no tiene valor por sí misma.   
Una variable no entra en TSIS porque sea un indicador conocido.  
El objetivo no es construir muchas variables.    
El objetivo es construir la **representación mínima del mercado** que conserve la máxima información útil.  
Una variable entra únicamente si implementa una representación física de un Objeto de Información admitido.  

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

**Hay 4 niveles**

Nivel 1
```
FAMILAS DE OBJETOS DE INFORMACION

Microstructure
│
├── Liquidity
├── Buying Pressure
├── Order Flow
└── Queue Dynamics

Participation
│
├── Trading Activity
├── Participation Rate
└── Relative Activity

Price Structure
│
├── Momentum
├── Trend
├── Pullback
└── Extension

Context
│
├── News Context
├── Fundamental Context
└── Market Regime
```

Nivel 2
```
OBJETOS DE INFORMACIÓN
(Conceptos científicos)

- Liquidity
- Trading Activity
- Momentum
- Market Regime
- News Context
- Buying Pressure
- Aggressiveness
```

Nivel 3
```
MODELOS DE REPRESENTACIÓN

Cada modelo es un conjunto de variables
que representa un Objeto de Información.

Liquidity
↓
Modelo 1:
- spread
- dollar_volume
- quoted_depth

Modelo 2:
- kyle_lambda
- amihud_illiquidity
- roll_spread

Momentum
↓
Modelo 1:
- return_1m
- return_5m
- slope
- vwap_distance
```


Nivel 4 
```
ESTADO (Integración de todos los Objetos de Información en un instante t): 
- Liquidez + 
- Participación + 
- Momentum + 
- Régimen + 
- Contexto + 
...
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

```
FAMILIA:
- Microstructure

OBJETO DE INFORMACION  (Concepto científico): 
- Liquidity

VARIABLES (Modelo de representación) :
- Spread
- Depth
- Quote Count
- OFI
- Microprice
```
```
FAMILIA:
- Participation

OBJETO DE INFORMACION  (Concepto científico): 
- Trading Activity

VARIABLES (Modelo de representación) :
- Relative Volume
- Trade Count
- Dollar Volume
- Turnover
```
```
FAMILIA:
- Price Structure

OBJETO DE INFORMACION  (Concepto científico): 
- Momentum

VARIABLES (Modelo de representación):
- Slope
- Returns
- VWAP Distance
- HH HL Structure
```

**Concepto final**

Un `Objeto de informacion` emerge de una o varias variables conjuntamente.   
El significado no está en una variable aislada, sino en la información conjunta.  

Las tablas no deberían preguntarse "¿qué columnas añadimos?", sino "**¿qué información necesitamos preservar?**"   
y solo después decidir cuál es la representación física mínima y más robusta para conservar esa información.


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

### Familia

```text
<Microstructure | Participation | Price Structure | Context | ...>
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


