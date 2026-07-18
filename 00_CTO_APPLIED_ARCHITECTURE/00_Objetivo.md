# Premisa

Construir una representación lo más fiel posible del mercado.

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
Market State dice:

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

Market State declara qué debe conocer.
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
No dice necesito un fenómeno.   
Porque el fenómeno ya ocurrió.  
Dice Necesito Objetos de Información.   
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

*Market State* declara qué Objetos de Información necesita:
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

¿Quién motiva la necesidad de crear Estados de Mercado?    
Las ***preguntas científicas*** y los ***consumidores*** (sistemas que utilizan la representación *Market State*).  

Ejemplos de ***PREGUNTAS***:

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

Así, la formulación más rigurosa no sería:

```text
Market State dice:
“Necesito estos Objetos”.
```

Sino:

```text
El contrato de representación de Market State declara
qué Objetos de Información deben integrarse
para cumplir sus preguntas científicas,
sus consumidores y su criterio de suficiencia.
```

La distinción exacta es:

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

Por tanto, el círculo realmente empieza antes de `Market State`:

```text
PREGUNTAS CIENTÍFICAS
+
CONSUMIDORES
+
DECISIONES QUE DEBEN PODER TOMARSE
↓
REQUISITOS DE INFORMACIÓN
↓
OBJETOS DE INFORMACIÓN ADMITIDOS
↓
CONTRATO DE REPRESENTACIÓN DE MARKET STATE
↓
MARKET STATE BUILDER
↓
TABLAS Y VARIABLES
↓
MARKET STATE MATERIALIZADO
```

La fase final que cerraría correctamente el documento sería  
contestar a la pregunta :   **¿Quién necesita que existan Objetos**

Ejemplo de ***CONSUMIDORES***: 

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

Si Market State es la representación canónica del estado del mercado, entonces solo debería existir una definición canónica.

Lo que sí puede cambiar es la proyección que hace cada consumidor sobre esa representación.

Por ejemplo:
```
Market State
=
La mejor representación observable del mercado en t.
```
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

Incluso se podría tener un sistema así:

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

**Event State Builder**