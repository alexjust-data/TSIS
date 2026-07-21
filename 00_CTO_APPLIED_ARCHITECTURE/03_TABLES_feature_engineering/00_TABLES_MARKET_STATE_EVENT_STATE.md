# Arquitectura de construcciÃ³n de `Market State` y `Event State`

## PropÃ³sito

Este documento define cÃ³mo TSIS construye las representaciones canÃ³nicas del estado observable del mercado.  

La informaciÃ³n utilizada para construir esas representaciones procede de las tablas fuente de representaciÃ³n (`000â€“018`),   
revisadas y gobernadas dentro de:

```text
02_TABLE_REPRESENTATION_REVIEW/
```
A partir de esa informaciÃ³n, los builders construyen dos representaciones del estado:
```
Market State
Event State
```

Estas representaciones pueden materializarse posteriormente mediante:

```
market_state_table
event_state_table
```

pero este documento describe su arquitectura conceptual, no su implementaciÃ³n fÃ­sica.

## Market State y Event State

Estas dos representaciones del estado poseen granos semÃ¡nticos distintos.  
Su materializaciÃ³n fÃ­sica puede realizarse mediante:  

**Market State** = *cÃ³mo estÃ¡ el mercado en un timestamp.*   
Describe el estado observable general en `t`, exista o no un evento.
```text
clave â‰ˆ instrumento + decision_timestamp
```

**Event State** = *cÃ³mo estÃ¡ el mercado respecto a un evento.*  
Describe ese estado anclado a un `evento` concreto **:**  antes, durante, al producirse o en otra posiciÃ³n temporal permitida.
```text
clave â‰ˆ evento + instrumento + decision_timestamp + state_role
```

PodrÃ­an almacenarse fÃ­sicamente en una sola tabla, pero aparecerÃ­an problemas:

* repeticiÃ³n del mismo `Market State` para cada evento;
* filas sin evento mezcladas con filas event-conditioned;
* claves y granularidades ambiguas;
* mayor riesgo de introducir informaciÃ³n posterior al evento;
* confusiÃ³n entre Â«estado del mercadoÂ» y Â«estado respecto a una hipÃ³tesis o eventoÂ».

Por tanto:

```text
Market State = representaciÃ³n base reutilizable
Event State  = vista contextualizada y gobernada respecto a un evento
```

`Event State` deberÃ­a reutilizar o referenciar el estado base, no inventar un segundo mercado.

## Â¿Por quÃ© precisamente estas dos?

Porque responden a dos preguntas cientÃ­ficas diferentes:

```text
Â¿QuÃ© sabÃ­a el sistema en el instante t?
```

y:

```text
Â¿QuÃ© sabÃ­a el sistema en t respecto al evento E?
```

La primera sirve para decisiones generales, scanners, clustering, predicciÃ³n y polÃ­ticas.  
La segunda sirve para estudiar transiciones alrededor de eventos, comparar casos equivalentes y construir muestras como:

```text
pre_event
at_event
post_event
```

Siempre separando cualquier tramo posterior que no pueda utilizarse como input observable.

La separaciÃ³n no es obligatoria universalmente, pero **sÃ­ es razonable y defendible para TSIS** porque evita mezclar el estado canÃ³nico con el contexto experimental.

## Â¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableciÃ³ que un sistema de aprendizaje exitoso deba contener dos tablas llamadas `Market State` y `Event State`. AlphaGo y AlphaGo Zero recibÃ­an una representaciÃ³n de la posiciÃ³n â€”y en algunas versiones informaciÃ³n histÃ³rica auxiliarâ€” para estimar polÃ­tica y valor. MuZero va mÃ¡s lejos: una funciÃ³n de representaciÃ³n transforma el historial de observaciones en un estado latente desde el que se predicen polÃ­tica, valor, recompensa y dinÃ¡mica. ([Google DeepMind][1])

Por tanto, la conclusiÃ³n precisa es:

```text
Las dos tablas NO proceden de DeepMind.

SÃ­ implementan un principio compatible con sus Ã©xitos:
construir una representaciÃ³n explÃ­cita, temporalmente vÃ¡lida
y suficiente del estado antes de aprender polÃ­ticas o valores.
```

`Market State` se aproxima al **estado observable base**.

`Event State` es una adaptaciÃ³n propia de TSIS para organizar observaciones condicionadas por eventos, algo necesario en tu investigaciÃ³n pero no equivalente a una pieza especÃ­fica de AlphaGo o MuZero.

**CertificaciÃ³n final:**

```text
Dos tablas = decisiÃ³n arquitectÃ³nica coherente para TSIS.
Estado explÃ­cito antes de polÃ­tica = alineado con DeepMind.
GarantÃ­a de Ã©xito por tenerlas = ninguna.
```

Lo que determinarÃ¡ su utilidad no serÃ¡ que existan dos tablas, sino que conjuntamente preserven informaciÃ³n suficiente, legal en `decision_timestamp`, sin redundancia ni leakage.

[1]: https://deepmind.google/research/alphago/?utm_source=chatgpt.com "AlphaGo â€” Google DeepMind"


## Market State y Event State : consumen `Objetos de informacion`

Ejemplo: queremos capturar el estado del tiker ***ABCD*** a las 09:42:00.

```
MARKET STATE

- instrument_id = ABCD  
- decision_timestamp = 09:42:00
```
Para describir ese momento necesita `Objetos` de informacion:

```
Momentum
Â¿Con quÃ© direcciÃ³n, intensidad y aceleraciÃ³n se mueve el precio?

Liquidity
Â¿Es posible transaccionar ahora sin un coste o impacto excesivo?

Volatility
Â¿CuÃ¡l es la magnitud e inestabilidad actual del movimiento?

Participation
Â¿Existe actividad real y anÃ³mala o el movimiento ocurre sin participaciÃ³n?

Intraday Position
Â¿DÃ³nde estÃ¡ el precio respecto a HOD, LOD, VWAP y otras referencias?

News Context
Â¿Existe un catalizador conocido y disponible en ese timestamp?

Fundamental Context
Â¿QuÃ© caracterÃ­sticas estructurales conocidas tiene la empresa?

Market Regime
Â¿En quÃ© entorno general ocurre todo esto?
```

DespuÃ©s el builder traduce esas necesidades cientÃ­ficas a variables fÃ­sicas:


```
Market State Representation Contract dice:

Necesito estos "Objetos":

- Momentum
- Liquidity
- Volatility
- Participation
- News Context
- ...

Builder: 
- Â¿DÃ³nde estÃ¡n las variables que representan Momentum? en 014
- Â¿DÃ³nde estÃ¡ Liquidity? en 015
- ...
```

Ejemplo por Objeto:

```
Necesito el Objeto:
- Liquidity.

Builder: Busca las columnas aprobadas que representan Liquidity:

    - 004_master_daily_table:
        - dollar_volume,
        - rvol_20d

    - 014_master_intraday_bar_table:
        - volume,
        - vwap,
        - transaction_count

    - 015_microstructure_features_table:
        - quotes_spread_bps_median,
        - quotes_top_depth_mean
```

La *_table* es el lugar donde se materializan unas variables.  
Y esas variables pertenecen conceptualmente a `Objetos` distintos.

AdemÃ¡s, varios objetos pueden obtener sus variables de una misma tabla:

```
014_master_intraday_bar_table

â”œâ”€â”€ Momentum
â”œâ”€â”€ Participation
â”œâ”€â”€ Intraday Position
â””â”€â”€ Volatility
```

Eso significa que si maÃ±ana decides mover *relative_volume* de la tabla 014  
a otra tabla porque cambia la arquitectura fÃ­sica, el Objeto de InformaciÃ³n *"Trading Activity"* no cambia.   
El *Market State Builder* seguirÃ¡ pidiendo "Trading Activity"*;   
solo cambiarÃ¡ el lugar desde el que obtiene las variables que la representan.

```
Market State Builder
â†“
necesita Objetos
â†“
cada Objeto sabe
â†“
quÃ© variables necesita
â†“
cada variable sabe
â†“
en quÃ© tabla vive

---

Market State Representation Contract declara quÃ© debe conocer.
Los objetos definen el significado.
Las variables expresan ese significado.
Las tablas indican dÃ³nde obtenerlas.
El builder las integra legalmente en t.
```

El builder hace joins legales mediante claves y relaciones temporales apropiadas:

```
- instrument_id = ABCD
- session_date
- decision_timestamp = 09:42:00
- source_timestamp
- valid_from 
- valid_to
- as_of_utc
```

y produce la representacino de un *Objeto* para *Market State* en una fila como:

```
market_state_id
instrument_id
decision_timestamp

momentum__return_1m
momentum__return_5m
momentum__slope

participation__relative_volume
participation__volume_acceleration

position__distance_to_hod
position__distance_to_vwap

liquidity__spread_pct
liquidity__depth_proxy

news__presence
news__age

regime__risk_on_off_state

component_quality_flags
component_as_of_utc
```


## Arquitectura

```
MERCADO - simplemente existe
â†“
FENÃ“MENOS - Â¿QuÃ© fenÃ³menos observables existen?
â†“
OBJETO DE INFORMACIÃ“N - Â¿QuÃ© informaciÃ³n necesitamos conservar sobre esos fenÃ³menos?
â†“
MODELOS DE REPRESENTACIÃ“N: - Â¿CÃ³mo decidimos representar esa informaciÃ³n?
â†“
IMPLEMENTACIÃ“N FÃSICA - Â¿QuÃ© variables implementan esa representaciÃ³n?
â†“
TABLAS - Â¿DÃ³nde se materializa esa representaciÃ³n?
â†“
Market State - Â¿CuÃ¡l es el estado observable del mercado en un decision_timestamp?
â†“
Event State - Â¿CuÃ¡l es el estado observable del mercado respecto a un evento?
```

**Market State necesita objetos de informaciÃ³n**  
No necesita un fenÃ³meno.   
Porque el fenÃ³meno ya ocurriÃ³.  
Necesita Objetos de InformaciÃ³n.   
Porque es lo Ãºnico que puede almacenar es informaciÃ³n.

### El `fenÃ³meno` existe aunque TSIS no exista

```
Hay una fuerte presiÃ³n compradora.
```
Eso ocurre en el mercado.  
Da igual que tÃº tengas datos.  
Da igual que exista TSIS.   
Es una propiedad del mercado.  
Es un fenÃ³meno. 

```
Hay poca liquidez.
El precio acelera.
```
Eso ocurre.  
No depende de cÃ³mo la midamos.  

### El `Objeto de InformaciÃ³n` no existe en el mercado

Lo construye TSIS.  
Es una decisiÃ³n cientÃ­fica.  

Definicion operativa del Objeto de Informacion:

```text
Unidad semantica de informacion que TSIS decide preservar
sobre uno o varios fenomenos observables, independiente
de su modelo de representacion y de su implementacion fisica.
```

El Objeto no es aun la representacion.
Es lo que debe ser representado.


### Taxonomias que no deben mezclarse

```text
Information Object Family
= significado semantico del Objeto.

Source Domain
= fuente observable que aporta evidencia.

Temporal Resolution
= escala temporal o ventana.

Institutional Role
= funcion dentro de TSIS.
```

Ejemplo:

```text
Liquidity
= Objeto de Informacion

information_object_family
= Liquidity

source_domain
= Quotes + Trades + OHLCV

temporal_resolution
= intraday_bar / event_window

institutional_role
= observable
```

No se debe usar una unica etiqueta `family` para mezclar dominio, fuente, escala temporal y rol institucional.

```
FENÃ“MENO:
- Hay poca liquidez.
TSIS:
- Eso me interesa.
- Voy a conservar informaciÃ³n sobre ese fenÃ³meno.
- Creo un Objeto: 
    - Liquidity
```

### Un `modelo de representaciÃ³n` conceptualiza la representaciÃ³n del *Objeto*

El papel del modelo de representaciÃ³n es separar el significado (*Objeto de InformaciÃ³n*) de la implementaciÃ³n fÃ­sica (*variables*).   
Si maÃ±ana descubres una forma mejor de medir la liquidez, cambias el modelo o su implementaciÃ³n,   pero no cambias el *Objeto "Liquidity"*. Esa separaciÃ³n es precisamente la que hace que la arquitectura sea estable a largo plazo.

Ejemplo:
```
OBJETO DE INFORMACIÃ“N:
- Liquidity

MODELO DE REPRESENTACIÃ“N A

    Representaremos la liquidez mediante:

    - Coste de ejecuciÃ³n
    - Facilidad para cruzar Ã³rdenes
    - Profundidad disponible

MODELO DE REPRESENTACIÃ“N B

    Representaremos la liquidez mediante:

    - Liquidez implÃ­cita del order book
    - Impacto esperado de una orden
    - Elasticidad del precio
```

Ambos modelos representan el mismo Objeto de InformaciÃ³n: *Liquidity*  
Pero cada uno propone una representaciÃ³n conceptual distinta.

```
Solo despuÃ©s elegimos la implementaciÃ³n fÃ­sica.
```

### La `implementaciÃ³n fÃ­sica` Â¿variables implementan esa representaciÃ³n?

Modelo A
```
OBJETO DE INFORMACIÃ“N:
- Liquidity

MODELO DE REPRESENTACIÃ“N A

Representaremos la liquidez mediante:

- Coste de ejecuciÃ³n
- Disponibilidad de contrapartida
- Profundidad del mercado

IMPLEMENTACIÃ“N FÃSICA

- Coste de ejecuciÃ³n
    - spread
    - spread_pct

- Disponibilidad de contrapartida
    - quote_count
    - trade_count

- Profundidad del mercado
    - bid_depth
    - ask_depth
    - depth_imbalance
```

Modelo B

```
OBJETO DE INFORMACIÃ“N:
- Liquidity

MODELO DE REPRESENTACIÃ“N B

Representaremos la liquidez mediante:

- Impacto esperado de una orden
- Sensibilidad del precio al volumen
- Liquidez implÃ­cita

IMPLEMENTACIÃ“N FÃSICA

- Impacto esperado de una orden
    - amihud_illiquidity

- Sensibilidad del precio al volumen
    - kyle_lambda

- Liquidez implÃ­cita
    - roll_spread
```

La implementaciÃ³n fÃ­sica puede cambiar con el tiempo.  
El `Objeto de InformaciÃ³n` permanece.  
El `Modelo de RepresentaciÃ³n` puede evolucionar.  
Lo Ãºnico que cambia son las variables que implementan ese modelo.  

### MaterializaciÃ³n en `tablas`

La *_table* es el lugar donde se materializan unas variables.  
Y esas variables pertenecen conceptualmente a `Objetos` distintos.

```
FENÃ“MENO:
- Hay una fuerte presiÃ³n compradora.

OBJETO DE INFORMACIÃ“N:
- Buying Pressure

MODELOS DE REPRESENTACIÃ“N:
- Aggressor Buy Volume
- Buy/Sell Imbalance
- Tape Speed
- Ask Consumption

IMPLEMENTACIÃ“N FÃSICA:
- aggressor_buy_volume
- aggressor_buy_ratio
- buy_sell_imbalance
- tape_speed
- ask_consumption_rate

TABLA:
- 015_microstructure_features_table:
    - aggressor_buy_volume
    - aggressor_buy_ratio
    - buy_sell_imbalance
    - tape_speed
    - ask_consumption_rate
```
```
FENÃ“MENO:
- Hay muy poca liquidez.

OBJETO DE INFORMACIÃ“N:
- Liquidity

MODELOS DE REPRESENTACIÃ“N:
- Spread
- Dollar Volume
- Quoted Depth

IMPLEMENTACIÃ“N FÃSICA:
- spread
- spread_pct
- dollar_volume
- depth_proxy

TABLA:
- 004_master_daily_table:
    - dollar_volume,
    - rvol_20d

- 014_master_intraday_bar_table:
    - volume,
    - vwap,
    - transaction_count

- 015_microstructure_features_table:
    - quotes_spread_bps_median,
    - quotes_top_depth_mean
```

```
FENÃ“MENO:
- El precio estÃ¡ acelerando.

OBJETO DE INFORMACIÃ“N:
- Momentum

MODELOS DE REPRESENTACIÃ“N:
- Returns
- Slope
- Price Acceleration

IMPLEMENTACIÃ“N FÃSICA:
- return_1m
- return_5m
- slope
- rolling_close_change
- price_acceleration

TABLA:
- 014_master_intraday_bar_table:
    - return_1m
    - return_5m
    - slope
    - rolling_close_change
    - price_acceleration
```

```
FENÃ“MENO:
- La participaciÃ³n del mercado aumenta de forma anÃ³mala.

OBJETO DE INFORMACIÃ“N:
- Trading Activity

MODELOS DE REPRESENTACIÃ“N:
- Relative Volume
- Volume Acceleration
- Trade Count

IMPLEMENTACIÃ“N FÃSICA:
- relative_volume
- volume_zscore
- volume_acceleration
- trade_count_proxy

TABLA:
- 004_master_daily_table:
    - rvol_20d

- 014_master_intraday_bar_table:
    - relative_volume
    - volume_zscore
    - volume_acceleration
    - trade_count_proxy
```

```
FENÃ“MENO:
- El mercado entra en un entorno de alta incertidumbre.

OBJETO DE INFORMACIÃ“N:
- Volatility

MODELOS DE REPRESENTACIÃ“N:
- Rolling Volatility
- True Range
- Expansion Ratio

IMPLEMENTACIÃ“N FÃSICA:
- rolling_volatility
- true_range_proxy
- rolling_range_5m
- volatility_expansion_ratio

TABLA:
- 014_master_intraday_bar_table:
    - rolling_range_5m

- 015_microstructure_features_table:
    - rolling_volatility
    - true_range_proxy
    - volatility_expansion_ratio
```

```
FENÃ“MENO:
- Existe un catalizador externo que puede alterar el comportamiento del mercado.

OBJETO DE INFORMACIÃ“N:
- News Context

MODELOS DE REPRESENTACIÃ“N:
- News Presence
- News Age
- Source Type

IMPLEMENTACIÃ“N FÃSICA:
- news_presence
- news_timestamp
- news_age
- source_type
- topic_or_category

TABLA:
- 010_news_context_table:
    - news_presence
    - news_timestamp
    - news_age
    - source_type
    - topic_or_category
```

```
FENÃ“MENO:
- La empresa presenta unas caracterÃ­sticas estructurales determinadas.

OBJETO DE INFORMACIÃ“N:
- Fundamental Context

MODELOS DE REPRESENTACIÃ“N:
- Float
- Market Cap
- Shares Outstanding

IMPLEMENTACIÃ“N FÃSICA:
- float
- market_cap
- shares_outstanding

TABLA:
- 009_fundamentals_asof_table:
    - float
    - market_cap
    - shares_outstanding
```
(Si ***market_cap*** o ***shares_outstanding*** todavÃ­a no existen en la tabla, quedarÃ­an como candidatos futuros.)

```
FENÃ“MENO:
- El mercado global favorece o perjudica la continuaciÃ³n de los movimientos.

OBJETO DE INFORMACIÃ“N:
- Market Regime

MODELOS DE REPRESENTACIÃ“N:
- Index Return
- Volatility Proxy
- Risk On/Off

IMPLEMENTACIÃ“N FÃSICA:
- index_return
- volatility_proxy
- risk_on_off_state
- regime_symbol

TABLA:
- 012_regime_context_table:
    - index_return
    - volatility_proxy
    - risk_on_off_state
    - regime_symbol
```

```
FENÃ“MENO:
- El precio se encuentra en una posiciÃ³n concreta dentro de la sesiÃ³n.

OBJETO DE INFORMACIÃ“N:
- Intraday Position

MODELOS DE REPRESENTACIÃ“N:
- Distance to HOD
- Distance to LOD
- Distance to VWAP

IMPLEMENTACIÃ“N FÃSICA:
- distance_to_session_hod
- distance_to_session_lod
- intraday_vwap_distance

TABLA:
- 014_master_intraday_bar_table:
    - session_hod
    - session_lod
    - distance_to_session_hod
    - distance_to_session_lod
    - intraday_vwap_distance
```

### Market State `Builder`

*Market State Representation Contract* declara quÃ© Objetos de InformaciÃ³n necesita:
```
- Momentum
- Liquidity
- Trading Activity
- Volatility
- Intraday Position
- ...
```
El *Market State Builder* construye la representaciÃ³n necesaria para responder a esta pregunta.

```
Â¿QuÃ© informaciÃ³n observable estaba disponible
para el instrumento ABCD
en el decision_timestamp 09:42:00?
```

El builder consulta el contrato aprobado de cada Objeto de InformaciÃ³n.
Ejemplo  
```
Market State necesita el Objeto:
- Liquidity

El contrato de Liquidity indica quÃ© variables aprobadas lo representan y dÃ³nde estÃ¡n materializadas:

- 004_master_daily_table:
    - dollar_volume
    - rvol_20d

- 014_master_intraday_bar_table:
    - volume
    - vwap
    - transaction_count

- 015_microstructure_features_table:
    - quotes_spread_bps_median
    - quotes_top_depth_mean
```

Y no copia indiscriminadamente toda la tabla.  
Selecciona Ãºnicamente:  
```
- variables admitidas;
- variables necesarias para los Objetos requeridos;
- valores observables legalmente en decision_timestamp;
- versiones vÃ¡lidas segÃºn as_of_utc;
- registros con suficiente calidad y cobertura.
```

No todas las tablas se unen mediante igualdad exacta de timestamp.

```
014_master_intraday_bar_table - selecciona la barra cerrada o el valor intradÃ­a permitido en t. 009_fundamentals_asof_table - selecciona la Ãºltima observaciÃ³n fundamental conocida antes de t. 010_news_context_table - selecciona noticias publicadas y disponibles antes o en t. 012_regime_context_table - selecciona el rÃ©gimen vigente y observable en t. 015_microstructure_features_table - selecciona la ventana microestructural cerrada y vÃ¡lida en t.
```

### Market State

La necesidad de construir una representaciÃ³n del estado del mercado  
surge de las *PREGUNTAS cientÃ­ficas*.

Una vez construida,  
los distintos *CONSUMIDORES* reutilizan esa representaciÃ³n. 

Ejemplos de *PREGUNTA CIENTÃFICA*

```text
PREGUNTA CIENTÃFICA:
- Â¿La probabilidad de continuaciÃ³n aumenta cuando el precio acelera?

NECESIDAD DE INFORMACIÃ“N:
- Conocer direcciÃ³n, intensidad y aceleraciÃ³n del movimiento.

OBJETO DE INFORMACIÃ“N REQUERIDO:
- Momentum
```

```text
PREGUNTA CIENTÃFICA:
- Â¿Es ejecutable una oportunidad sin un coste o impacto excesivo?

NECESIDAD DE INFORMACIÃ“N:
- Conocer las condiciones de negociaciÃ³n disponibles.

OBJETO DE INFORMACIÃ“N REQUERIDO:
- Liquidity
```

```text
PREGUNTA CIENTÃFICA:
- Â¿El movimiento tiene participaciÃ³n anÃ³mala?

NECESIDAD DE INFORMACIÃ“N:
- Conocer la intensidad de actividad respecto a su referencia.

OBJETO DE INFORMACIÃ“N REQUERIDO:
- Trading Activity
```

Es el diseÃ±o cientÃ­fico el que razona:

```text
Para responder estas preguntas
y servir a estos consumidores,
el estado debe preservar informaciÃ³n sobre Momentum.
```

DespuÃ©s esa decisiÃ³n queda formalizada en un contrato:

```text
MARKET STATE REPRESENTATION CONTRACT

required_information_objects:

- Momentum
- Liquidity
- Volatility
- Trading Activity
- Intraday Position
- News Context
- Fundamental Context
- Market Regime
```

El builder recibe ese contrato y lo ejecuta:

```text
Market State Builder:

1. Lee los Objetos requeridos por el contrato.
2. Consulta la especificaciÃ³n aprobada de cada Objeto.
3. Resuelve quÃ© variables implementan cada representaciÃ³n.
4. Localiza las tablas donde viven esas variables.
5. Recupera Ãºnicamente valores legalmente observables en t.
6. Valida cobertura, calidad y temporalidad.
7. Materializa la fila de Market State.
```

La distinciÃ³n exacta es:

```text
El contrato de representaciÃ³n de Market State declara
quÃ© Objetos de InformaciÃ³n deben integrarse
para cumplir sus preguntas cientÃ­ficas,
sus consumidores y su criterio de suficiencia.
```

```text
Gobernanza cientÃ­fica
= decide quÃ© informaciÃ³n merece preservarse.

Contrato de Market State
= declara quÃ© Objetos son obligatorios u opcionales.

Market State Builder
= ejecuta esa declaraciÃ³n.

Market State
= resultado materializado.
```

La fase final que cerrarÃ­a correctamente el documento serÃ­a  
contestar a la pregunta :   **Â¿QuiÃ©n necesita que existan Objetos**

Ejemplo de *CONSUMIDORES*: 

```
Objeto de InformaciÃ³n:
Momentum

Â¿Por quÃ© existe?

Porque es necesario para:

- representar el estado del mercado;
- estudiar eventos;
- agrupar contextos similares;
- aprender polÃ­ticas;
- investigar patrones;
- evaluar resultados.   
```

```text
Objeto:
Momentum

Lo necesitan:

- Market State
- Event State
- Clustering
- Outcome Engine
- Pattern Discovery
- Offline RL
- Policy Learning
```

La cadena completa queda cerrada asÃ­:

```
PREGUNTAS CIENTÃFICAS

MERCADO
â†“
FENÃ“MENOS
â†“
OBJETOS DE INFORMACIÃ“N
â†“
MODELOS DE REPRESENTACIÃ“N
â†“
VARIABLES
â†“
TABLAS
â†“
MARKET STATE BUILDER
â†“
MARKET STATE
â†“
CONSUMIDORES
```

**Representaciones de patrones o estrategias**

Por otra parte,   

si *Market State* es la representaciÃ³n canÃ³nica del estado del mercado,   
entonces solo deberÃ­a existir una definiciÃ³n canÃ³nica.

```
Market State
=
La mejor representaciÃ³n observable del mercado en t.
```

Lo que sÃ­ puede cambiar es la proyecciÃ³n que hace cada consumidor sobre esa representaciÃ³n.

DeberÃ­as tener:

```
market_state_table
```

y despuÃ©s construir datasets derivados:

```
breakout_research_dataset
vwap_reclaim_research_dataset
squeeze_research_dataset
```

Esos datasets seleccionan las filas de Market State necesarias para estudiar cada patrÃ³n.

```
PM_Squeeze_Event
â†“
event_timestamp = 09:45
â†“
se solicitan estados:
09:35
09:36
...
09:45
```
El sistema no crea diez tablas canÃ³nicas nuevas.  
Recupera diez filas o ventanas de la representaciÃ³n canÃ³nica.


Incluso se podrÃ­a tener un sistema asÃ­:

```
Market State
â”‚
â”œâ”€â”€ 500 Objetos atributos
â”‚
â”œâ”€â”€ Momentum
â”œâ”€â”€ Liquidity
â”œâ”€â”€ News
â”œâ”€â”€ Regime
â”œâ”€â”€ ...
```
entonces 

```
Offline RL

lee:
- 420 atributos
```

```
Clustering

lee:
- 80 atributos
```

```
CNN

lee:
- imÃ¡genes
(no Market State directamente)
```

```
Transformer

lee:
- secuencias de Market State
```


```
Market State
â†“
Feature Selector
â†“
Dataset RL
---

Market State
â†“
Feature Selector
â†“
Dataset Clustering
---

Market State
â†“
Feature Selector
â†“
Dataset Prediction
```

**Â¿Se materializa una fila para cada t?**

Depende del grano definido.  
Si el grano canÃ³nico es un minuto:  
```
instrument_id + decision_timestamp_minute
```
entonces puede existir una fila por minuto vÃ¡lido.

Si el estado necesita resoluciÃ³n de segundos:
```
instrument_id + decision_timestamp_second
```
el volumen crece muchÃ­simo.  
Por eso no debes mezclar:
```
definiciÃ³n canÃ³nica
```
con:
```
resoluciÃ³n fÃ­sica universal.
```
Puede existir una arquitectura multirresoluciÃ³n:
```
market_state_1d
market_state_1m
market_state_1s
market_state_microstructure_window
```
Pero todas deben respetar la misma semÃ¡ntica:
```
estado observable legalmente en t
```
No son estados distintos por algoritmo.   
Son resoluciones fÃ­sicas distintas del mismo concepto.


**La arquitectura prÃ¡ctica recomendable**

```
CONTRATO CANÃ“NICO DE MARKET STATE
â†“
define esquema, semÃ¡ntica y temporalidad
â†“
MARKET STATE BUILDER
â†“
consulta tablas fuente
â†“
construye estados solicitados
â†“
valida
â†“
materializa de forma persistente
â†“
MARKET STATE STORE
â†“
es reutilizado por Event State y consumidores
```

**Â¿Se guardan los Market State ya creados?**

El almacenamiento podrÃ­a tener tres niveles:


```
1. Core histÃ³rico
   - materializado ampliamente;
   - datos baratos y frecuentes.

2. Extensiones pesadas
   - microestructura;
   - materializadas por universo, evento o ventana autorizada.

3. Datasets derivados
   - especÃ­ficos para investigaciÃ³n o algoritmos;
   - no son Market State canÃ³nico.
```

Ejemplo concreto

SupÃ³n que investigas 2.000 squeezes.

```
NO -> 2.000 tablas Market State.
```
```
SI -> event_registry
        - contiene los 2.000 eventos

DespuÃ©s solicitas:

por cada evento:
- 30 minutos pre_event;
- instante at_event;
- 20 minutos post_event.

El sistema obtiene:
- 2.000 Ã— 51 estados
```
pero los guarda en un repositorio comÃºn:
```
market_state_table
```
Luego Event State crea las relaciones:
```
event_id â†” market_state_id â†” state_role
```

Si dos eventos utilizan el mismo estado de ABCD a las 09:42, ese Market State se reutiliza.

**Lo canÃ³nico es, ante todo:**

una definiciÃ³n Ãºnica y gobernada
de cÃ³mo representar el mercado en t.

```
- la definiciÃ³n;
- el contrato;
- el esquema;
- las reglas temporales;
- los Objetos de InformaciÃ³n admitidos;
- las reglas para construir cada estado en t.
```

La materializaciÃ³n fÃ­sica puede hacerse por capas sin perder la canonicalidad:

```
- de forma histÃ³rica;
- por particiones;
- bajo demanda;
- por ventanas de eventos;
- en distintas resoluciones;
- con extensiones opcionales;
```
La fÃ³rmula
```
Canonicalidad = misma definiciÃ³n.

MaterializaciÃ³n = cuÃ¡ndo, dÃ³nde, con quÃ© cobertura
y a quÃ© resoluciÃ³n se construye esa definiciÃ³n.
```


### Market State no debe convertirse en mega-tabla universal

La canonicidad no significa:

```text
una unica fila fisica con toda la informacion que algun consumidor pudiera necesitar
```

Ese criterio convertiria `Market State` en una union ilimitada de necesidades downstream.
La regla correcta es:

```text
Canonicalidad
= una unica semantica de estado
+ un unico identificador logico de estado
+ reglas temporales comunes
+ perfiles de representacion compatibles
```

La materializacion fisica puede separarse en perfiles:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Todos los perfiles deben poder vincularse mediante:

```text
market_state_id
instrument_id
decision_timestamp
representation_profile_version
```

El `core` debe contener solo lo necesario para identificar y describir el estado minimo gobernado.
Las extensiones pesadas deben permanecer separadas y consumirse solo cuando el perfil, contrato y politica temporal lo autoricen.



### Event State: state_role no basta

`Event State` debe separar dos cosas:

```text
state_role
= donde esta la fila respecto al evento.

consumption_legality
= si esa fila puede consumirse como input predictivo, research, outcome-adjacent o no input.
```

Valores de `state_role`:

```text
pre_event
at_event
post_event
```

Valores de `consumption_legality`:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Regla critica:

```text
post_event puede ser Event State valido para investigacion,
pero no puede ser X para una decision tomada antes o en el evento.
```

Por eso una fila debe evaluarse por ambos ejes, no solo por `state_role`.


### Event State Builder

El `Event State Builder` responde a una pregunta diferente:
```
Â¿QuÃ© informaciÃ³n observable estaba disponible
respecto al evento E
en el decision_timestamp 09:42:00?
```
Event State no reconstruye el mercado desde cero.

Parte de:
- un `evento` concreto;
- un `Market State` vÃ¡lido;
- una `relaciÃ³n temporal` entre el estado y el evento;
- variables especÃ­ficas del contexto del evento.

Ejemplo:
```
event_id = PM_SQUEEZE_2026_07_18_ABCD_001
instrument_id = ABCD
event_timestamp = 09:45:00
decision_timestamp = 09:42:00
state_role = pre_event
```
El `Event State Builder` realiza dos operaciones.

**1. Recupera el estado base**

Busca el Market State correspondiente a:
```
instrument_id = ABCD
decision_timestamp = 09:42:00
```
Ese estado ya contiene:
```
- Momentum
- Liquidity
- Trading Activity
- Volatility
- Intraday Position
- Buying Pressure
- News Context
- Fundamental Context
- Market Regime
```

**2. AÃ±ade la contextualizaciÃ³n respecto al evento**

El builder incorpora informaciÃ³n como:
```
- event_id
- event_type
- event_timestamp
- state_role
- time_to_event
- time_from_event
- event_phase
- event_detection_status
- event_reference_levels
- event_specific_quality_flags
```

Por ejemplo:
```
event_type = PM_Squeeze_Event
state_role = pre_event
time_to_event_seconds = 180
event_phase = setup_forming
distance_to_event_reference_hod = -0.012
event_detection_status = not_yet_confirmed
```
---
La diferencia esencial es:
```
Market State:
- organiza informaciÃ³n por instrumento y decision_timestamp.

Event State:
- organiza esa misma informaciÃ³n respecto a un evento concreto.
```

Por tanto, `Event State` no deberÃ­a duplicar ni inventar un segundo estado del mercado.

Debe reutilizar o referenciar el Market State base:
```
Event State
â†“
referencia un Market State vÃ¡lido
â†“
aÃ±ade identidad del evento
â†“
aÃ±ade posiciÃ³n temporal respecto al evento
â†“
aÃ±ade contexto especÃ­fico del evento
```
Ejemplo completo:
```
MERCADO
â†“
aparecen fenÃ³menos observables
â†“
TSIS (investigador) define Objetos de InformaciÃ³n
â†“
los modelos determinan cÃ³mo representarlos
â†“
las variables implementan esos modelos
â†“
las tablas materializan las variables
â†“
Market State Builder recupera e integra
las variables vÃ¡lidas en decision_timestamp
â†“
MARKET STATE
â†“
Event State Builder toma ese estado base
y lo contextualiza respecto al evento E
â†“
EVENT STATE
â†“
CONSUMIDORES
```

**Â¿QuÃ© ocurre cuando una estrategia solicita una ventana?**

```
Evento:
VWAP_Reclaim_Event

event_timestamp:
10:17:00

ventana solicitada:
10 minutos antes
5 minutos despuÃ©s
```
El `Event State Builder` realiza algo como:

```
1. Identifica el evento.
2. Calcula los decision_timestamp requeridos.
3. Busca los Market State ya materializados.
4. Construye los que falten, si estÃ¡n autorizados.
5. Los referencia mediante market_state_id.
6. AÃ±ade state_role y relaciÃ³n temporal con el evento.
```

Resultado

```
event_id
market_state_id
decision_timestamp
state_role
relative_time_to_event
```

Ejemplo:

```
E123 | MS9001 | 10:07 | pre_event
E123 | MS9002 | 10:08 | pre_event
...
E123 | MS9011 | 10:17 | at_event
E123 | MS9012 | 10:18 | post_event
```

No se crea una nueva copia completa del mercado para cada estrategia.

### Persistencia

Debes distinguir:
```
Memoria temporal
- RAM;
- cachÃ©;
- usada durante una ejecuciÃ³n;
- puede desaparecer.
```
de:
```
MaterializaciÃ³n persistente
- Parquet;
- Delta/Iceberg;
- base de datos;
- object storage;
- permanece disponible y versionada.
```
Una vez construido y validado un Market State, puedes guardarlo para no recalcularlo cada vez.

Ejemplo:
```
market_state/
    version=v0_1/
        year=2025/
            month=01/
            symbol=ABCD/
                part-000.parquet
```
O particionado por:
```
- date;
- instrument;
- resolution;
- representation_version.
```
