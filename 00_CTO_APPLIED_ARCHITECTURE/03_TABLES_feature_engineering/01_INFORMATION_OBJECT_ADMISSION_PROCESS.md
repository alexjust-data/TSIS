**PLANTILLA**

ESPECIFICACIÃƒâ€œN Y CRITERIOS DE ADMISIÃƒâ€œN  
DE `OBJETOS DE INFORMACIÃƒâ€œN`  
PARA LA REPRESENTACIÃƒâ€œN DEL ESTADO
=== 

Status: `template_v0_7_state_profile_boundary`  
Date: `2026-07-17`  

Usar una copia de esta plantilla para cada `Objeto de InformaciÃƒÂ³n` candidato
a formar parte de la representaciÃƒÂ³n del estado.   
* Este documento ***no diseÃƒÂ±a tablas***.    
* SÃƒÂ­ decide si una determinada informaciÃƒÂ³n merece formar parte del estado del mercado.  
* No debe repetir contratos, schemas ni manifests.  
* SÃƒÂ­ debe referenciar los documentos, contratos, tablas, artefactos y literatura que justifican su existencia.  

**QuÃƒÂ© es este documento**

Es un proceso reproducible para identificar, justificar y representar  
`objetos de informaciÃƒÂ³n` que pueden formar parte del estado del mercado.  

Las tablas y sus atributos serÃƒÂ¡n una consecuencia de ese proceso.

Responde:

```
Ã‚Â¿QuÃƒÂ© objeto de informaciÃƒÂ³n existe?  
Ã‚Â¿Por quÃƒÂ© existe?  
Ã‚Â¿CÃƒÂ³mo se representa?  
Ã‚Â¿QuÃƒÂ© variables lo implementan?  
Ã‚Â¿DÃƒÂ³nde vive?  
Ã‚Â¿QuiÃƒÂ©n lo consume?  
Ã‚Â¿Merece formar parte del estado?  
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
## FilosofÃƒÂ­a

Premisa

```
Ã‚Â¿QuÃƒÂ© informaciÃƒÂ³n debe preservar la representaciÃƒÂ³n
para describir correctamente el estado del mercado?

Ã‚Â¿QuÃƒÂ© informaciÃƒÂ³n debe contener el estado
para que un agente pueda tomar decisiones ÃƒÂ³ptimas?
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
- Liquidez instantÃƒÂ¡nea.
```

```
VARIABLES:
- Gap
- Premarket Volume
- Relative Volume
- Float
- News

Pero juntas representan OBJETO DE INFORMACION:
- Potencial de expansiÃƒÂ³n.
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

Cada vez que alguien quiera aÃƒÂ±adir una variable, la primera pregunta deberÃƒÂ­a ser:
```
Ã‚Â¿Esta variable incorpora informaciÃƒÂ³n nueva sobre el estado del mercado
o solo es otra forma de representar informaciÃƒÂ³n que ya tenemos?
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
Ã‚Â¿QuÃƒÂ© "informaciÃƒÂ³n" del mercado todavÃƒÂ­a no estÃƒÂ¡ representada?
Ã‚Â¿Y cÃƒÂ³mo podemos representar esa informaciÃƒÂ³n?
```
Ejemplo

```
---
InformaciÃƒÂ³n : La liquidity
---
Modelo de representaciÃƒÂ³n:
- Spread
- Quoted Depth
- Dollar Volume
- Microprice
- OFI
- Bid Ask Imbalance
```

* Elegimos informaciÃƒÂ³n.  
* DespuÃƒÂ©s buscamos la representaciÃƒÂ³n mÃƒÂ­nima de esa informaciÃƒÂ³n con variables.


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
El significado no estÃƒÂ¡ en una variable aislada, sino en la informaciÃƒÂ³n conjunta.  

Las tablas no deberÃƒÂ­an preguntarse "Ã‚Â¿quÃƒÂ© columnas aÃƒÂ±adimos?", sino "**Ã‚Â¿quÃƒÂ© informaciÃƒÂ³n necesitamos preservar?**"   
y solo despuÃƒÂ©s decidir cuÃƒÂ¡l es la representaciÃƒÂ³n fÃƒÂ­sica mÃƒÂ­nima y mÃƒÂ¡s robusta para conservar esa informaciÃƒÂ³n.


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
Ã¢â€ â€œ
FENÃƒâ€œMENOS - Ã‚Â¿QuÃƒÂ© fenÃƒÂ³menos observables existen?
Ã¢â€ â€œ
OBJETO DE INFORMACIÃƒâ€œN - Ã‚Â¿QuÃƒÂ© informaciÃƒÂ³n necesitamos conservar sobre esos fenÃƒÂ³menos?
Ã¢â€ â€œ
MODELOS DE REPRESENTACIÃƒâ€œN: - Ã‚Â¿Mediante quÃƒÂ© conjunto de medidas representamos este Objeto?
Ã¢â€ â€œ
IMPLEMENTACIÃƒâ€œN FÃƒÂSICA - Ã‚Â¿QuÃƒÂ© columnas, fÃƒÂ³rmulas, ventanas y parÃƒÂ¡metros implementan esas medidas?
Ã¢â€ â€œ
TABLAS - Ã‚Â¿DÃƒÂ³nde se materializa esa representaciÃƒÂ³n?
Ã¢â€ â€œ
Market State - Ã‚Â¿CuÃƒÂ¡l es el estado observable del mercado en un decision_timestamp?
Ã¢â€ â€œ
Event State - Ã‚Â¿CuÃƒÂ¡l es el estado observable del mercado respecto a un evento?
```

Ejemplos

```
FENÃƒâ€œMENO:
- Hay una fuerte presiÃƒÂ³n compradora.

OBJETO DE INFORMACIÃƒâ€œN:
- Buying Pressure

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en agresiÃƒÂ³n compradora, desequilibrio y consumo de liquidez:
    - Aggressor Buy Volume
    - Buy/Sell Imbalance
    - Tape Speed
    - Ask Consumption

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- Hay muy poca liquidez.

OBJETO DE INFORMACIÃƒâ€œN:
- Liquidity

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en coste de negociaciÃƒÂ³n, actividad y profundidad:
    - Spread
    - Dollar Volume
    - Quoted Depth

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- El precio estÃƒÂ¡ acelerando.

OBJETO DE INFORMACIÃƒâ€œN:
- Momentum

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en direcciÃƒÂ³n, pendiente y aceleraciÃƒÂ³n:
    - Returns
    - Slope
    - Price Acceleration

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- La participaciÃƒÂ³n del mercado aumenta de forma anÃƒÂ³mala.

OBJETO DE INFORMACIÃƒâ€œN:
- Trading Activity

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en intensidad de negociaciÃƒÂ³n:
    - Relative Volume
    - Volume Acceleration
    - Trade Count

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- El mercado entra en un entorno de alta incertidumbre.

OBJETO DE INFORMACIÃƒâ€œN:
- Volatility

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en amplitud y expansiÃƒÂ³n:
    - Rolling Volatility
    - True Range
    - Expansion Ratio

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- Existe un catalizador externo que puede alterar el comportamiento del mercado.

OBJETO DE INFORMACIÃƒâ€œN:
- News Context

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en existencia, antigÃƒÂ¼edad y naturaleza del catalizador:
    - News Presence
    - News Age
    - Source Type

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- La empresa presenta unas caracterÃƒÂ­sticas estructurales determinadas.

OBJETO DE INFORMACIÃƒâ€œN:
- Fundamental Context

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en estructura de capital:
    - Float
    - Market Cap
    - Shares Outstanding

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

- float:
    - float

- market_cap:
    - market_cap

- shares_outstanding:
    - shares_outstanding

TABLAS:
- 009_fundamentals_asof_table
```
(Si ***market_cap*** o ***shares_outstanding*** todavÃƒÂ­a no existen en la tabla, quedarÃƒÂ­an como candidatos futuros.)
```
FENÃƒâ€œMENO:
- El mercado global favorece o perjudica la continuaciÃƒÂ³n de los movimientos.

OBJETO DE INFORMACIÃƒâ€œN:
- Market Regime

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en contexto macro del mercado:
    - Index Return
    - Volatility Proxy
    - Risk On/Off

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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
FENÃƒâ€œMENO:
- El precio se encuentra en una posiciÃƒÂ³n concreta dentro de la sesiÃƒÂ³n.

OBJETO DE INFORMACIÃƒâ€œN:
- Intraday Position

MODELO DE REPRESENTACIÃƒâ€œN:
- Modelo basado en referencias intradÃƒÂ­a:
    - Distance to HOD
    - Distance to LOD
    - Distance to VWAP

IMPLEMENTACIÃƒâ€œN FÃƒÂSICA:

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

Un mismo Objeto de InformaciÃƒÂ³n puede tener varios modelos de representaciÃƒÂ³n.

```
Liquidity
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Modelo A
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Spread
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Depth
Ã¢â€â€š     Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ Dollar Volume
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Modelo B
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Kyle Lambda
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Amihud
Ã¢â€â€š     Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ Roll Spread
Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ Modelo C
      Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ Embedding aprendido
```

**Consecuencia 2**

Una misma tabla puede implementar parcialmente varios Objetos de InformaciÃƒÂ³n.

```
014_master_intraday_bar_table

Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Momentum
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ return_1m
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ slope
Ã¢â€â€š     Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ price_acceleration
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Trading Activity
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ relative_volume
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ volume_acceleration
Ã¢â€â€š     Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ trade_count_proxy
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Intraday Position
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ distance_to_session_hod
Ã¢â€â€š     Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ distance_to_session_lod
Ã¢â€â€š     Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ intraday_vwap_distance
Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ Volatility
      Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ rolling_range_5m
```

**Consecuencia 3**

Un mismo Objeto de InformaciÃƒÂ³n puede necesitar variables procedentes de varias tablas.

```
Liquidity

Ã¢â€ â€œ

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
primero defines quÃƒÂ© quieres representar, despuÃƒÂ©s el modelo conceptual con el que lo representarÃƒÂ¡s, y solo al final eliges las medidas concretas (variables) que implementan ese modelo.
 
una misma tabla (por ejemplo, 014_master_intraday_bar_table) implementa parcialmente la representaciÃƒÂ³n fÃƒÂ­sica de varios Objetos de InformaciÃƒÂ³n (Momentum, Trading Activity, Intraday Position, etc.). 

## Proceso de admisiÃƒÂ³n

```
Nuevo Objeto de InformaciÃƒÂ³n candidato
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© queremos representar?
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© fenÃƒÂ³meno del mercado representa?
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© significado cientÃƒÂ­fico tiene?
Ã¢â€ â€œ
Ã‚Â¿Por quÃƒÂ© merece existir?
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© preguntas cientÃƒÂ­ficas permite responder?
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© hipÃƒÂ³tesis cientÃƒÂ­fica representa?
Ã¢â€ â€œ
Ã‚Â¿Existe evidencia cientÃƒÂ­fica que lo respalde?
Ã¢â€ â€œ
Ã‚Â¿QuiÃƒÂ©n utilizarÃƒÂ¡ esta informaciÃƒÂ³n?
(Market State, Event State, ML, RL...)
Ã¢â€ â€œ
Ã‚Â¿CÃƒÂ³mo vamos a representar este Objeto?
(Modelo(s) de RepresentaciÃƒÂ³n)
Ã¢â€ â€œ
Ã‚Â¿QuÃƒÂ© variables implementan ese modelo?
Ã¢â€ â€œ
Ã‚Â¿En quÃƒÂ© tablas vivirÃƒÂ¡n esas variables?
Ã¢â€ â€œ
Ã‚Â¿Existe ya otra representaciÃƒÂ³n equivalente?
Ã¢â€ â€œ
Ã‚Â¿Puede calcularse legalmente en decision_timestamp?
Ã¢â€ â€œ
Ã‚Â¿CuÃƒÂ¡l es su coste computacional?
Ã¢â€ â€œ
Ã‚Â¿CuÃƒÂ¡nto ruido introduce?
Ã¢â€ â€œ
Ã‚Â¿CuÃƒÂ¡l es su ganancia informativa?
Ã¢â€ â€œ
Ã‚Â¿Debe admitirse dentro de la representaciÃƒÂ³n del estado?
```


# PLANTILLA : `Objeto de InformaciÃƒÂ³n`


## 1. IdentificaciÃƒÂ³n

### Nombre

```text
<Nombre del Objeto de InformaciÃƒÂ³n>
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

## 2. Significado cientÃƒÂ­fico

### InformaciÃƒÂ³n que se desea preservar

```text
Ã‚Â¿QuÃƒÂ© informaciÃƒÂ³n del mercado queremos preservar?
```

### FenÃƒÂ³meno del mercado observado

```text
Ã‚Â¿QuÃƒÂ© fenÃƒÂ³meno observable representa?
```

### Significado cientÃƒÂ­fico

```text
Ã‚Â¿QuÃƒÂ© conocimiento aporta al estado del mercado?
```

---

## 3. JustificaciÃƒÂ³n cientÃƒÂ­fica

### HipÃƒÂ³tesis cientÃƒÂ­fica

```text
Ã‚Â¿QuÃƒÂ© hipÃƒÂ³tesis representa?
```

### JustificaciÃƒÂ³n

```text
Ã‚Â¿Por quÃƒÂ© este Objeto de InformaciÃƒÂ³n merece formar parte del estado?
```

### Preguntas cientÃƒÂ­ficas

```text
Ã‚Â¿QuÃƒÂ© preguntas permite responder?

Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
```

---

## 4. Evidencia cientÃƒÂ­fica

```text
Papers

Libros

Autores

Referencias
```

---

## 5. Modelo(s) de representaciÃƒÂ³n

### Modelo A

#### DescripciÃƒÂ³n

```text
Ã‚Â¿CÃƒÂ³mo representaremos este Objeto?
```

#### Medidas utilizadas

```text
Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
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

#### DescripciÃƒÂ³n

```text
...
```

#### Medidas utilizadas

```text
Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
Ã¢â‚¬Â¢
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

## 6. ImplementaciÃƒÂ³n fÃƒÂ­sica

### Modelo seleccionado

```text
Modelo A
```

### Variables fÃƒÂ­sicas

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

## 7. MaterializaciÃƒÂ³n

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
Ã‚Â¿Puede calcularse completamente en decision_timestamp?

Ã‚Â¿Necesita as-of?

Ã‚Â¿Existe riesgo de leakage?

Ã‚Â¿Tiene dependencias temporales?
```

---

## 10. EvaluaciÃƒÂ³n tÃƒÂ©cnica

### Coste computacional

```text
...
```

### Complejidad del estado

```text
Dimensionalidad

CorrelaciÃƒÂ³n

Overfitting
```

### Estabilidad temporal

```text
Ã‚Â¿Es estable entre distintos regÃƒÂ­menes?
```

### Ganancia informativa

```text
Ã‚Â¿QuÃƒÂ© incertidumbre reduce?
```

### PÃƒÂ©rdida de informaciÃƒÂ³n

```text
Ã‚Â¿QuÃƒÂ© informaciÃƒÂ³n se perderÃƒÂ­a si este Objeto desapareciera?
```

---

## 11. Representaciones equivalentes

```text
Ã‚Â¿Existe otro Objeto que represente prÃƒÂ¡cticamente la misma informaciÃƒÂ³n?

Ã‚Â¿Existe otro modelo equivalente?

Ã‚Â¿Debe reutilizarse?

Ã‚Â¿Debe fusionarse?
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
Ã‚Â¿QuÃƒÂ© aporta este Objeto a Market State?

Ã‚Â¿Es obligatorio?

Ã‚Â¿Es opcional?

Ã‚Â¿QuÃƒÂ© ocurre si se elimina?
```

---

## 14. DecisiÃƒÂ³n

```text
Aceptado

Aceptado con restricciones

Pendiente de evidencia

Rechazado
```

### JustificaciÃƒÂ³n

```text
...
```

### Condiciones de revisiÃƒÂ³n futura

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
