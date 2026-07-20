# Premisa

Construir una representación lo más fiel posible del mercado.

Este Explica:

```
por qué y como construimos variables/tablas
para alimentar Market State y Event State
mediante Objetos de Información
```

## Dos tablas finales

Estas dos tablas representan **granos semánticos distintos**:

**Market State** = cómo está el mercado en un timestamp.   
Describe el estado observable general en `t`, exista o no un evento.
```text
Market State
clave ≈ instrumento + decision_timestamp
```

**Event State** = cómo está el mercado respecto a un evento.  
Describe ese estado anclado a un `evento` concreto **:**  antes, durante, al producirse o en otra posición temporal permitida.
```text
Event State
clave ≈ evento + instrumento + decision_timestamp + state_role
```

Podrían almacenarse físicamente en una sola tabla, pero aparecerían problemas:

* repetición del mismo `Market State` para cada evento;
* filas sin evento mezcladas con filas event-conditioned;
* claves y granularidades ambiguas;
* mayor riesgo de introducir información posterior al evento;
* confusión entre «estado del mercado» y «estado respecto a una hipótesis o evento».

Por tanto:

```text
Market State = representación base reutilizable
Event State  = vista contextualizada y gobernada respecto a un evento
```

`Event State` debería reutilizar o referenciar el estado base, no inventar un segundo mercado.

## ¿Por qué precisamente estas dos?

Porque responden a dos preguntas científicas diferentes:

```text
¿Qué sabía el sistema en el instante t?
```

y:

```text
¿Qué sabía el sistema en t respecto al evento E?
```

La primera sirve para decisiones generales, scanners, clustering, predicción y políticas.  
La segunda sirve para estudiar transiciones alrededor de eventos, comparar casos equivalentes y construir muestras como:

```text
pre_event
at_event
post_event
```

Siempre separando cualquier tramo posterior que no pueda utilizarse como input observable.

La separación no es obligatoria universalmente, pero **sí es razonable y defendible para TSIS** porque evita mezclar el estado canónico con el contexto experimental.

## ¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableció que un sistema de aprendizaje exitoso deba contener dos tablas llamadas `Market State` y `Event State`. AlphaGo y AlphaGo Zero recibían una representación de la posición —y en algunas versiones información histórica auxiliar— para estimar política y valor. MuZero va más lejos: una función de representación transforma el historial de observaciones en un estado latente desde el que se predicen política, valor, recompensa y dinámica. ([Google DeepMind][1])

Por tanto, la conclusión precisa es:

```text
Las dos tablas NO proceden de DeepMind.

Sí implementan un principio compatible con sus éxitos:
construir una representación explícita, temporalmente válida
y suficiente del estado antes de aprender políticas o valores.
```

`Market State` se aproxima al **estado observable base**.

`Event State` es una adaptación propia de TSIS para organizar observaciones condicionadas por eventos, algo necesario en tu investigación pero no equivalente a una pieza específica de AlphaGo o MuZero.

**Certificación final:**

```text
Dos tablas = decisión arquitectónica coherente para TSIS.
Estado explícito antes de política = alineado con DeepMind.
Garantía de éxito por tenerlas = ninguna.
```

Lo que determinará su utilidad no será que existan dos tablas, sino que conjuntamente preserven información suficiente, legal en `decision_timestamp`, sin redundancia ni leakage.

[1]: https://deepmind.google/research/alphago/?utm_source=chatgpt.com "AlphaGo — Google DeepMind"


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
¿Con qué dirección, intensidad y aceleración se mueve el precio?

Liquidity
¿Es posible transaccionar ahora sin un coste o impacto excesivo?

Volatility
¿Cuál es la magnitud e inestabilidad actual del movimiento?

Participation
¿Existe actividad real y anómala o el movimiento ocurre sin participación?

Intraday Position
¿Dónde está el precio respecto a HOD, LOD, VWAP y otras referencias?

News Context
¿Existe un catalizador conocido y disponible en ese timestamp?

Fundamental Context
¿Qué características estructurales conocidas tiene la empresa?

Market Regime
¿En qué entorno general ocurre todo esto?
```

Después el builder traduce esas necesidades científicas a variables físicas:


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
- ¿Dónde están las variables que representan Momentum? en 014
- ¿Dónde está Liquidity? en 015
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

Además, varios objetos pueden obtener sus variables de una misma tabla:

```
014_master_intraday_bar_table

├── Momentum
├── Participation
├── Intraday Position
└── Volatility
```

Eso significa que si mañana decides mover *relative_volume* de la tabla 014  
a otra tabla porque cambia la arquitectura física, el Objeto de Información *"Trading Activity"* no cambia.   
El *Market State Builder* seguirá pidiendo "Trading Activity"*;   
solo cambiará el lugar desde el que obtiene las variables que la representan.

```
Market State Builder
↓
necesita Objetos
↓
cada Objeto sabe
↓
qué variables necesita
↓
cada variable sabe
↓
en qué tabla vive

---

Market State Representation Contract declara qué debe conocer.
Los objetos definen el significado.
Las variables expresan ese significado.
Las tablas indican dónde obtenerlas.
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
↓
FENÓMENOS - ¿Qué fenómenos observables existen?
↓
OBJETO DE INFORMACIÓN - ¿Qué información necesitamos conservar sobre esos fenómenos?
↓
MODELOS DE REPRESENTACIÓN: - ¿Cómo decidimos representar esa información?
↓
IMPLEMENTACIÓN FÍSICA - ¿Qué variables implementan esa representación?
↓
TABLAS - ¿Dónde se materializa esa representación?
↓
Market State - ¿Cuál es el estado observable del mercado en un decision_timestamp?
↓
Event State - ¿Cuál es el estado observable del mercado respecto a un evento?
```

**Market State necesita objetos de información**  
No necesita un fenómeno.   
Porque el fenómeno ya ocurrió.  
Necesita Objetos de Información.   
Porque es lo único que puede almacenar es información.

### El `fenómeno` existe aunque TSIS no exista

```
Hay una fuerte presión compradora.
```
Eso ocurre en el mercado.  
Da igual que tú tengas datos.  
Da igual que exista TSIS.   
Es una propiedad del mercado.  
Es un fenómeno. 

```
Hay poca liquidez.
El precio acelera.
```
Eso ocurre.  
No depende de cómo la midamos.  

### El `Objeto de Información` no existe en el mercado

Lo construye TSIS.  
Es una decisión científica.  

```
FENÓMENO:
- Hay poca liquidez.
TSIS:
- Eso me interesa.
- Voy a conservar información sobre ese fenómeno.
- Creo un Objeto: 
    - Liquidity
```

### Un `modelo de representación` conceptualiza la representación del *Objeto*

El papel del modelo de representación es separar el significado (*Objeto de Información*) de la implementación física (*variables*).   
Si mañana descubres una forma mejor de medir la liquidez, cambias el modelo o su implementación,   pero no cambias el *Objeto "Liquidity"*. Esa separación es precisamente la que hace que la arquitectura sea estable a largo plazo.

Ejemplo:
```
OBJETO DE INFORMACIÓN:
- Liquidity

MODELO DE REPRESENTACIÓN A

    Representaremos la liquidez mediante:

    - Coste de ejecución
    - Facilidad para cruzar órdenes
    - Profundidad disponible

MODELO DE REPRESENTACIÓN B

    Representaremos la liquidez mediante:

    - Liquidez implícita del order book
    - Impacto esperado de una orden
    - Elasticidad del precio
```

Ambos modelos representan el mismo Objeto de Información: *Liquidity*  
Pero cada uno propone una representación conceptual distinta.

```
Solo después elegimos la implementación física.
```

### La `implementación física` ¿variables implementan esa representación?

Modelo A
```
OBJETO DE INFORMACIÓN:
- Liquidity

MODELO DE REPRESENTACIÓN A

Representaremos la liquidez mediante:

- Coste de ejecución
- Disponibilidad de contrapartida
- Profundidad del mercado

IMPLEMENTACIÓN FÍSICA

- Coste de ejecución
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
OBJETO DE INFORMACIÓN:
- Liquidity

MODELO DE REPRESENTACIÓN B

Representaremos la liquidez mediante:

- Impacto esperado de una orden
- Sensibilidad del precio al volumen
- Liquidez implícita

IMPLEMENTACIÓN FÍSICA

- Impacto esperado de una orden
    - amihud_illiquidity

- Sensibilidad del precio al volumen
    - kyle_lambda

- Liquidez implícita
    - roll_spread
```

La implementación física puede cambiar con el tiempo.  
El `Objeto de Información` permanece.  
El `Modelo de Representación` puede evolucionar.  
Lo único que cambia son las variables que implementan ese modelo.  

### Materialización en `tablas`

La *_table* es el lugar donde se materializan unas variables.  
Y esas variables pertenecen conceptualmente a `Objetos` distintos.

```
FENÓMENO:
- Hay una fuerte presión compradora.

OBJETO DE INFORMACIÓN:
- Buying Pressure

MODELOS DE REPRESENTACIÓN:
- Aggressor Buy Volume
- Buy/Sell Imbalance
- Tape Speed
- Ask Consumption

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- Hay muy poca liquidez.

OBJETO DE INFORMACIÓN:
- Liquidity

MODELOS DE REPRESENTACIÓN:
- Spread
- Dollar Volume
- Quoted Depth

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- El precio está acelerando.

OBJETO DE INFORMACIÓN:
- Momentum

MODELOS DE REPRESENTACIÓN:
- Returns
- Slope
- Price Acceleration

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- La participación del mercado aumenta de forma anómala.

OBJETO DE INFORMACIÓN:
- Trading Activity

MODELOS DE REPRESENTACIÓN:
- Relative Volume
- Volume Acceleration
- Trade Count

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- El mercado entra en un entorno de alta incertidumbre.

OBJETO DE INFORMACIÓN:
- Volatility

MODELOS DE REPRESENTACIÓN:
- Rolling Volatility
- True Range
- Expansion Ratio

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- Existe un catalizador externo que puede alterar el comportamiento del mercado.

OBJETO DE INFORMACIÓN:
- News Context

MODELOS DE REPRESENTACIÓN:
- News Presence
- News Age
- Source Type

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- La empresa presenta unas características estructurales determinadas.

OBJETO DE INFORMACIÓN:
- Fundamental Context

MODELOS DE REPRESENTACIÓN:
- Float
- Market Cap
- Shares Outstanding

IMPLEMENTACIÓN FÍSICA:
- float
- market_cap
- shares_outstanding

TABLA:
- 009_fundamentals_asof_table:
    - float
    - market_cap
    - shares_outstanding
```
(Si ***market_cap*** o ***shares_outstanding*** todavía no existen en la tabla, quedarían como candidatos futuros.)

```
FENÓMENO:
- El mercado global favorece o perjudica la continuación de los movimientos.

OBJETO DE INFORMACIÓN:
- Market Regime

MODELOS DE REPRESENTACIÓN:
- Index Return
- Volatility Proxy
- Risk On/Off

IMPLEMENTACIÓN FÍSICA:
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
FENÓMENO:
- El precio se encuentra en una posición concreta dentro de la sesión.

OBJETO DE INFORMACIÓN:
- Intraday Position

MODELOS DE REPRESENTACIÓN:
- Distance to HOD
- Distance to LOD
- Distance to VWAP

IMPLEMENTACIÓN FÍSICA:
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

*Market State Representation Contract* declara qué Objetos de Información necesita:
```
- Momentum
- Liquidity
- Trading Activity
- Volatility
- Intraday Position
- ...
```
El *Market State Builder* construye la representación necesaria para responder a esta pregunta.

```
¿Qué información observable estaba disponible
para el instrumento ABCD
en el decision_timestamp 09:42:00?
```

El builder consulta el contrato aprobado de cada Objeto de Información.
Ejemplo  
```
Market State necesita el Objeto:
- Liquidity

El contrato de Liquidity indica qué variables aprobadas lo representan y dónde están materializadas:

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
Selecciona únicamente:  
```
- variables admitidas;
- variables necesarias para los Objetos requeridos;
- valores observables legalmente en decision_timestamp;
- versiones válidas según as_of_utc;
- registros con suficiente calidad y cobertura.
```

No todas las tablas se unen mediante igualdad exacta de timestamp.

```
014_master_intraday_bar_table - selecciona la barra cerrada o el valor intradía permitido en t. 009_fundamentals_asof_table - selecciona la última observación fundamental conocida antes de t. 010_news_context_table - selecciona noticias publicadas y disponibles antes o en t. 012_regime_context_table - selecciona el régimen vigente y observable en t. 015_microstructure_features_table - selecciona la ventana microestructural cerrada y válida en t.
```

### Market State

La necesidad de construir una representación del estado del mercado  
surge de las *PREGUNTAS científicas*.

Una vez construida,  
los distintos *CONSUMIDORES* reutilizan esa representación. 

Ejemplos de *PREGUNTA CIENTÍFICA*

```text
PREGUNTA CIENTÍFICA:
- ¿La probabilidad de continuación aumenta cuando el precio acelera?

NECESIDAD DE INFORMACIÓN:
- Conocer dirección, intensidad y aceleración del movimiento.

OBJETO DE INFORMACIÓN REQUERIDO:
- Momentum
```

```text
PREGUNTA CIENTÍFICA:
- ¿Es ejecutable una oportunidad sin un coste o impacto excesivo?

NECESIDAD DE INFORMACIÓN:
- Conocer las condiciones de negociación disponibles.

OBJETO DE INFORMACIÓN REQUERIDO:
- Liquidity
```

```text
PREGUNTA CIENTÍFICA:
- ¿El movimiento tiene participación anómala?

NECESIDAD DE INFORMACIÓN:
- Conocer la intensidad de actividad respecto a su referencia.

OBJETO DE INFORMACIÓN REQUERIDO:
- Trading Activity
```

Es el diseño científico el que razona:

```text
Para responder estas preguntas
y servir a estos consumidores,
el estado debe preservar información sobre Momentum.
```

Después esa decisión queda formalizada en un contrato:

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
2. Consulta la especificación aprobada de cada Objeto.
3. Resuelve qué variables implementan cada representación.
4. Localiza las tablas donde viven esas variables.
5. Recupera únicamente valores legalmente observables en t.
6. Valida cobertura, calidad y temporalidad.
7. Materializa la fila de Market State.
```

La distinción exacta es:

```text
El contrato de representación de Market State declara
qué Objetos de Información deben integrarse
para cumplir sus preguntas científicas,
sus consumidores y su criterio de suficiencia.
```

```text
Gobernanza científica
= decide qué información merece preservarse.

Contrato de Market State
= declara qué Objetos son obligatorios u opcionales.

Market State Builder
= ejecuta esa declaración.

Market State
= resultado materializado.
```

La fase final que cerraría correctamente el documento sería  
contestar a la pregunta :   **¿Quién necesita que existan Objetos**

Ejemplo de *CONSUMIDORES*: 

```
Objeto de Información:
Momentum

¿Por qué existe?

Porque es necesario para:

- representar el estado del mercado;
- estudiar eventos;
- agrupar contextos similares;
- aprender políticas;
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

La cadena completa queda cerrada así:

```
PREGUNTAS CIENTÍFICAS

MERCADO
↓
FENÓMENOS
↓
OBJETOS DE INFORMACIÓN
↓
MODELOS DE REPRESENTACIÓN
↓
VARIABLES
↓
TABLAS
↓
MARKET STATE BUILDER
↓
MARKET STATE
↓
CONSUMIDORES
```

**Representaciones de patrones o estrategias**

Por otra parte,   

si *Market State* es la representación canónica del estado del mercado,   
entonces solo debería existir una definición canónica.

```
Market State
=
La mejor representación observable del mercado en t.
```

Lo que sí puede cambiar es la proyección que hace cada consumidor sobre esa representación.

Deberías tener:

```
market_state_table
```

y después construir datasets derivados:

```
breakout_research_dataset
vwap_reclaim_research_dataset
squeeze_research_dataset
```

Esos datasets seleccionan las filas de Market State necesarias para estudiar cada patrón.

```
PM_Squeeze_Event
↓
event_timestamp = 09:45
↓
se solicitan estados:
09:35
09:36
...
09:45
```
El sistema no crea diez tablas canónicas nuevas.  
Recupera diez filas o ventanas de la representación canónica.


Incluso se podría tener un sistema así:

```
Market State
│
├── 500 Objetos atributos
│
├── Momentum
├── Liquidity
├── News
├── Regime
├── ...
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
- imágenes
(no Market State directamente)
```

```
Transformer

lee:
- secuencias de Market State
```


```
Market State
↓
Feature Selector
↓
Dataset RL
---

Market State
↓
Feature Selector
↓
Dataset Clustering
---

Market State
↓
Feature Selector
↓
Dataset Prediction
```

**¿Se materializa una fila para cada t?**

Depende del grano definido.  
Si el grano canónico es un minuto:  
```
instrument_id + decision_timestamp_minute
```
entonces puede existir una fila por minuto válido.

Si el estado necesita resolución de segundos:
```
instrument_id + decision_timestamp_second
```
el volumen crece muchísimo.  
Por eso no debes mezclar:
```
definición canónica
```
con:
```
resolución física universal.
```
Puede existir una arquitectura multirresolución:
```
market_state_1d
market_state_1m
market_state_1s
market_state_microstructure_window
```
Pero todas deben respetar la misma semántica:
```
estado observable legalmente en t
```
No son estados distintos por algoritmo.   
Son resoluciones físicas distintas del mismo concepto.


**La arquitectura práctica recomendable**

```
CONTRATO CANÓNICO DE MARKET STATE
↓
define esquema, semántica y temporalidad
↓
MARKET STATE BUILDER
↓
consulta tablas fuente
↓
construye estados solicitados
↓
valida
↓
materializa de forma persistente
↓
MARKET STATE STORE
↓
es reutilizado por Event State y consumidores
```

**¿Se guardan los Market State ya creados?**

El almacenamiento podría tener tres niveles:


```
1. Core histórico
   - materializado ampliamente;
   - datos baratos y frecuentes.

2. Extensiones pesadas
   - microestructura;
   - materializadas por universo, evento o ventana autorizada.

3. Datasets derivados
   - específicos para investigación o algoritmos;
   - no son Market State canónico.
```

Ejemplo concreto

Supón que investigas 2.000 squeezes.

```
NO -> 2.000 tablas Market State.
```
```
SI -> event_registry
        - contiene los 2.000 eventos

Después solicitas:

por cada evento:
- 30 minutos pre_event;
- instante at_event;
- 20 minutos post_event.

El sistema obtiene:
- 2.000 × 51 estados
```
pero los guarda en un repositorio común:
```
market_state_table
```
Luego Event State crea las relaciones:
```
event_id ↔ market_state_id ↔ state_role
```

Si dos eventos utilizan el mismo estado de ABCD a las 09:42, ese Market State se reutiliza.

**Lo canónico es, ante todo:**

una definición única y gobernada
de cómo representar el mercado en t.

```
- la definición;
- el contrato;
- el esquema;
- las reglas temporales;
- los Objetos de Información admitidos;
- las reglas para construir cada estado en t.
```

La materialización física puede hacerse por capas sin perder la canonicalidad:

```
- de forma histórica;
- por particiones;
- bajo demanda;
- por ventanas de eventos;
- en distintas resoluciones;
- con extensiones opcionales;
```
La fórmula
```
Canonicalidad = misma definición.

Materialización = cuándo, dónde, con qué cobertura
y a qué resolución se construye esa definición.
```


### Event State Builder

El `Event State Builder` responde a una pregunta diferente:
```
¿Qué información observable estaba disponible
respecto al evento E
en el decision_timestamp 09:42:00?
```
Event State no reconstruye el mercado desde cero.

Parte de:
- un `evento` concreto;
- un `Market State` válido;
- una `relación temporal` entre el estado y el evento;
- variables específicas del contexto del evento.

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

**2. Añade la contextualización respecto al evento**

El builder incorpora información como:
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
- organiza información por instrumento y decision_timestamp.

Event State:
- organiza esa misma información respecto a un evento concreto.
```

Por tanto, `Event State` no debería duplicar ni inventar un segundo estado del mercado.

Debe reutilizar o referenciar el Market State base:
```
Event State
↓
referencia un Market State válido
↓
añade identidad del evento
↓
añade posición temporal respecto al evento
↓
añade contexto específico del evento
```
Ejemplo completo:
```
MERCADO
↓
aparecen fenómenos observables
↓
TSIS (investigador) define Objetos de Información
↓
los modelos determinan cómo representarlos
↓
las variables implementan esos modelos
↓
las tablas materializan las variables
↓
Market State Builder recupera e integra
las variables válidas en decision_timestamp
↓
MARKET STATE
↓
Event State Builder toma ese estado base
y lo contextualiza respecto al evento E
↓
EVENT STATE
↓
CONSUMIDORES
```

**¿Qué ocurre cuando una estrategia solicita una ventana?**

```
Evento:
VWAP_Reclaim_Event

event_timestamp:
10:17:00

ventana solicitada:
10 minutos antes
5 minutos después
```
El `Event State Builder` realiza algo como:

```
1. Identifica el evento.
2. Calcula los decision_timestamp requeridos.
3. Busca los Market State ya materializados.
4. Construye los que falten, si están autorizados.
5. Los referencia mediante market_state_id.
6. Añade state_role y relación temporal con el evento.
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
- caché;
- usada durante una ejecución;
- puede desaparecer.
```
de:
```
Materialización persistente
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