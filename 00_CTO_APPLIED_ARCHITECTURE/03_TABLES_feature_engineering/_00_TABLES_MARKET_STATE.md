# Arquitectura de construcción de `Market State`

## Propósito

Este documento define cómo TSIS construye la representación canónica del estado observable del mercado.

La información utilizada para construir dicha representación procede de las tablas fuente de representación (`000–018`),
revisadas y gobernadas dentro de:

```text
02_TABLE_REPRESENTATION_REVIEW/
```

A partir de esa información, el *Market State Builder* construye una representación única del estado observable del mercado:

```text
Market State
```

Esta representación puede materializarse posteriormente mediante:

```text
market_state_table
```

o mediante distintos perfiles físicos compatibles de representación, siempre gobernados por el mismo contrato semántico.

Sin embargo, este documento describe exclusivamente la arquitectura conceptual de `Market State`, no su implementación física, sus perfiles de materialización ni sus políticas de almacenamiento.

`Market State` constituye la representación base sobre la que posteriormente podrán construirse otras representaciones especializadas, como `Event State`, `Execution State` o futuras representaciones de investigación, sin alterar la definición canónica del estado del mercado.

## ¿Qué es `Market State`?

`Market State` es la representación canónica del estado observable del mercado en un `decision_timestamp`.

No representa:

```text
una estrategia
```

No representa:

```text
un evento
```

No representa:

```text
una decisión de trading
```

No representa:

```text
un resultado futuro
```

Representa únicamente:

```text
la información observable que el sistema podía conocer
sobre el mercado
en el instante t.
```

Su identidad conceptual es:

**Market State** = *cómo está el mercado en un instante determinado.*

Describe el estado observable general en `t`, exista o no cualquier fenómeno de interés, hipótesis de investigación, oportunidad operativa o evento registrado.

Su grano semántico es:

```text
clave ≈ instrumento + decision_timestamp
```

Toda la información contenida en un `Market State` debe cumplir simultáneamente las siguientes propiedades:

```text
• observable en decision_timestamp;
• legal desde el punto de vista temporal;
• independiente de cualquier resultado posterior;
• independiente de cualquier estrategia;
• independiente de cualquier consumidor concreto.
```

Por tanto, `Market State` no intenta responder:

```text
¿Debo comprar?

¿Debo vender?

¿Existe una oportunidad?
```

Responde únicamente:

```text
¿Qué sabía objetivamente el sistema
sobre el mercado
en ese instante?
```

Ese estado constituye la representación base reutilizable de TSIS.

Todos los consumidores posteriores deben partir de esa misma representación canónica.

Por ejemplo:

```text
Clustering
Offline RL
Pattern Discovery
Prediction
Policy Learning
Event State
Execution State
```

pueden utilizar subconjuntos diferentes de información, pero ninguno debería redefinir qué significa el estado del mercado.

Por tanto:

```text
Market State
=
una única representación semántica del mercado.

Los consumidores
=
proyecciones distintas
sobre esa representación.
```

La canonicidad no implica una única tabla física ni una única materialización.

Implica una única definición científica de:

```text
qué información debe preservarse;

cómo debe representarse;

qué reglas temporales debe respetar;

qué significado tiene cada componente del estado.
```

Todo lo demás —perfiles, resoluciones, materializaciones o datasets derivados— constituye únicamente distintas formas de reutilizar esa misma representación canónica.


## ¿Por qué existe `Market State`?

La necesidad de construir una representación explícita del estado del mercado
surge directamente de las preguntas científicas que TSIS pretende responder.

Antes de aprender patrones, descubrir relaciones, construir políticas o evaluar
resultados, el sistema debe disponer de una descripción coherente, reproducible
y temporalmente válida del mercado.

Esa representación es `Market State`.

Su función no consiste en decidir.

Su función consiste en conservar, de forma gobernada, la información observable
que cualquier consumidor posterior podría necesitar.

Por tanto, `Market State` responde a una única pregunta científica:

```text
¿Qué sabía el sistema
sobre el mercado
en el instante t?
```

No responde:

```text
¿Qué debería hacer?

¿Qué ocurrirá después?

¿Qué estrategia debería ejecutarse?
```

Esas preguntas pertenecen a capas posteriores del sistema.

Precisamente por ello, `Market State` debe permanecer independiente de:

```text
eventos;

estrategias;

políticas;

algoritmos;

modelos de Machine Learning;

consumidores concretos.
```

Su misión consiste únicamente en preservar conocimiento observable.

Una vez construido, distintos consumidores reutilizan exactamente la misma
representación.

Ejemplos:

```text
Clustering

Pattern Discovery

Prediction

Offline RL

Policy Learning

Execution Research

Event State
```

Todos ellos parten del mismo estado observable.

Lo que cambia no es el estado.

Lo que cambia es la información que cada consumidor decide utilizar.

Por ello, el sistema no necesita construir un Market State distinto para cada
algoritmo o investigación.

Necesita una única representación canónica suficientemente rica y
científicamente gobernada.

Posteriormente cada consumidor puede proyectar únicamente la parte de esa
representación que resulte relevante para su objetivo.

Ejemplo:

```text
Market State
│
├── Momentum
├── Liquidity
├── Trading Activity
├── Volatility
├── Intraday Position
├── News Context
├── Fundamental Context
├── Market Regime
└── ...
```

Entonces:

```text
Offline RL

lee:
- subconjunto de atributos
```

```text
Clustering

lee:
- otro subconjunto
```

```text
Prediction

lee:
- otro subconjunto diferente
```

```text
Event State

parte del mismo Market State
y añade únicamente
la contextualización respecto al evento.
```

La representación canónica permanece invariable.

Los consumidores cambian.

Nunca al contrario.

Por tanto, la existencia de `Market State` no responde a una necesidad técnica.

Responde a una necesidad científica:

```text
Toda decisión posterior debe poder justificarse
utilizando únicamente la información
observable y disponible
en el instante donde esa decisión podía tomarse.
```

Ese principio convierte a `Market State` en la fuente canónica del conocimiento
observable del mercado dentro de TSIS.


````md id="tz82ak"
## ¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableció que un sistema de aprendizaje exitoso deba contener una representación denominada `Market State`.

AlphaGo y AlphaGo Zero recibían una representación del estado del tablero —y en algunas versiones información histórica auxiliar— para estimar política y valor.

MuZero va un paso más allá: una función de representación transforma el historial de observaciones en un estado latente desde el que posteriormente se predicen política, valor, recompensa y dinámica.

Por tanto, la conclusión rigurosa es:

```text
Market State NO procede de DeepMind.

Sí implementa un principio compatible
con sus sistemas de aprendizaje:

construir una representación explícita,
temporalmente válida
y suficiente del estado
antes de aprender políticas,
valores o decisiones.
```

En TSIS, `Market State` desempeña precisamente ese papel.

Representa el estado observable del mercado en un `decision_timestamp`,
sin incorporar todavía:

```text
eventos;

estrategias;

ejecución;

resultados futuros.
```

Su objetivo no es aprender.

Su objetivo es representar correctamente el conocimiento disponible.

Solo después podrán aparecer otras capas que consuman esa representación:

```text
Event State

Execution State

Pattern Discovery

Prediction

Offline RL

Policy Learning

Outcome Research
```

Todas ellas parten del mismo estado observable.

Ninguna redefine el mercado.

Por tanto, la certificación correcta es:

```text
Market State
=
decisión arquitectónica propia de TSIS.

Representación explícita del estado
antes del aprendizaje
=
principio compatible con DeepMind.

Garantía de éxito por existir
=
ninguna.
```

La utilidad de `Market State` no dependerá de que exista una tabla llamada así.

Dependerá de que la representación preserve información suficiente,
legalmente observable en `decision_timestamp`,
científicamente gobernada,
sin redundancia innecesaria
y sin introducir leakage temporal.

Ese es el criterio que determina la calidad de la representación,
independientemente del algoritmo que posteriormente la consuma.
````

````md id="84fj2m"
## `Market State` consume `Objetos de Información`

Supongamos que queremos capturar el estado observable del instrumento ***ABCD*** a las **09:42:00**.

```
MARKET STATE

- instrument_id = ABCD
- decision_timestamp = 09:42:00
```

Para describir correctamente ese instante, `Market State` no necesita conocer estrategias, eventos o consumidores.

Necesita únicamente `Objetos de Información`.

Por ejemplo:

```
Momentum
¿Con qué dirección, intensidad y aceleración se mueve el precio?

Liquidity
¿Es posible transaccionar ahora sin un coste o impacto excesivo?

Volatility
¿Cuál es la magnitud e inestabilidad actual del movimiento?

Trading Activity
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

Cada uno de esos Objetos representa una necesidad científica distinta.

`Market State` no almacena fenómenos.

Tampoco almacena directamente tablas físicas.

Almacena información sobre esos fenómenos mediante Objetos de Información previamente admitidos.

Posteriormente, el builder traduce esas necesidades científicas a variables físicas.

```
Market State Representation Contract dice:

Necesito estos Objetos:

- Momentum
- Liquidity
- Volatility
- Trading Activity
- News Context
- ...

Builder:

- ¿Dónde están las variables que representan Momentum?
- ¿Dónde está Liquidity?
- ¿Dónde está Trading Activity?
- ...
```

Ejemplo para un único Objeto:

```
Necesito el Objeto:

- Liquidity

Builder:

Busca las columnas aprobadas que representan Liquidity.

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

Las tablas no contienen Objetos.

Las tablas contienen variables.

Las variables implementan Modelos de Representación.

Los Modelos representan Objetos de Información.

Y `Market State` integra únicamente esos Objetos.

Además, distintos Objetos pueden obtener información de una misma tabla física.

Por ejemplo:

```
014_master_intraday_bar_table

├── Momentum
├── Trading Activity
├── Intraday Position
└── Volatility
```

Eso significa que si en el futuro una variable cambia de tabla por una decisión de arquitectura física, el Objeto de Información permanece inalterado.

Por ejemplo:

```
Trading Activity
```

seguirá existiendo aunque:

```
relative_volume
```

deje de vivir en `014` y pase a otra superficie física.

El contrato de `Market State` seguirá solicitando el mismo Objeto.

Solo cambiará la localización física de las variables que lo implementan.

La cadena completa queda:

```
Market State Builder

↓

necesita Objetos

↓

cada Objeto conoce

↓

qué Modelo de Representación utiliza

↓

cada Modelo conoce

↓

qué variables lo implementan

↓

cada variable conoce

↓

en qué tabla vive
```

Por tanto:

```
Market State Representation Contract
declara qué Objetos deben preservarse.

Los Objetos definen el significado.

Los Modelos de Representación
definen cómo representar ese significado.

Las variables implementan esos modelos.

Las tablas indican dónde obtenerlas.

El Market State Builder
integra legalmente toda esa información
en el decision_timestamp t.
```

Para ello, el builder realiza únicamente joins temporalmente legales mediante claves y relaciones aprobadas, por ejemplo:

```
- instrument_id
- session_date
- decision_timestamp
- source_timestamp
- valid_from
- valid_to
- as_of_utc
```

y produce una representación canónica del estado del mercado para ese instante.
````


````md
## Arquitectura

La arquitectura de `Market State` nace siguiendo una única dirección conceptual.

No comienza en las tablas.

No comienza en las variables.

No comienza en los algoritmos.

Comienza en el propio mercado.

```
MERCADO
↓
FENÓMENOS
↓
OBJETOS DE INFORMACIÓN
↓
MODELOS DE REPRESENTACIÓN
↓
IMPLEMENTACIÓN FÍSICA
↓
TABLAS
↓
MARKET STATE BUILDER
↓
MARKET STATE
```

Cada capa responde a una pregunta científica distinta.

```
MERCADO

¿Qué existe independientemente de TSIS?
```

↓

```
FENÓMENOS

¿Qué fenómenos observables ocurren realmente?
```

↓

```
OBJETOS DE INFORMACIÓN

¿Qué información merece conservar TSIS
sobre esos fenómenos?
```

↓

```
MODELOS DE REPRESENTACIÓN

¿Cómo decidimos representar
esa información?
```

↓

```
IMPLEMENTACIÓN FÍSICA

¿Qué variables implementan
esa representación?
```

↓

```
TABLAS

¿Dónde se materializan
esas variables?
```

↓

```
MARKET STATE BUILDER

¿Cómo recuperamos legalmente
esa información
en el decision_timestamp?
```

↓

```
MARKET STATE

¿Cuál era el estado observable
del mercado
en t?
```

La dirección nunca debería invertirse.

No debería ocurrir:

```
Tengo esta variable.

↓

¿Dónde la pongo?
```

Ni tampoco:

```
Tengo una tabla.

↓

¿Qué significado podría darle?
```

La dirección correcta siempre es:

```
Existe un fenómeno.

↓

TSIS decide que merece conservar
información sobre él.

↓

Se crea un Objeto de Información.

↓

Se diseña un Modelo de Representación.

↓

Se implementa mediante variables.

↓

Las variables se materializan
en tablas gobernadas.

↓

El Market State Builder
las integra legalmente.

↓

Se obtiene un único
Market State.
```

Por ello, `Market State` no necesita fenómenos.

Los fenómenos ya ocurrieron.

Lo único que puede almacenar una representación es información.

Por tanto, `Market State` consume exclusivamente:

```
Objetos de Información.
```

No fenómenos.

No tablas.

No estrategias.

No consumidores.

Todo lo demás pertenece a capas posteriores de la arquitectura.

La estabilidad de `Market State` depende precisamente de mantener esa separación.

Los fenómenos pueden descubrirse.

Los modelos pueden evolucionar.

Las implementaciones físicas pueden cambiar.

Las tablas pueden reorganizarse.

Pero mientras los Objetos de Información permanezcan estables, la representación canónica del estado del mercado seguirá representando exactamente el mismo conocimiento científico.
````

### El `fenómeno` existe aunque TSIS no exista

Un fenómeno es una propiedad observable del mercado.

Existe independientemente de:

```text
TSIS

Data Foundation

Market State

cualquier algoritmo

cualquier representación
```

Por ejemplo:

```
Hay una fuerte presión compradora.
```

Ese fenómeno ocurre en el mercado.

Da igual que existan datos.

Da igual que exista una base de datos.

Da igual que alguien esté observándolo.

Simplemente ocurre.

Otro ejemplo:

```
Hay poca liquidez.
```

También ocurre.

No depende de cómo decidamos medirla.

Otro:

```
El precio acelera.
```

Otro:

```
La volatilidad aumenta.
```

Otro:

```
La participación disminuye.
```

Todos ellos pertenecen al mercado.

No pertenecen a TSIS.

No pertenecen a la representación.

TSIS nunca crea fenómenos.

Únicamente decide cuáles considera suficientemente importantes como para conservar información sobre ellos.

---

### El `Objeto de Información` no existe en el mercado

El mercado no contiene Objetos de Información.

Los Objetos de Información son una construcción científica realizada por TSIS.

Representan una decisión epistemológica.

No describen directamente el fenómeno.

Describen la información que TSIS considera necesario preservar sobre ese fenómeno.

Definición operativa:

```text
Unidad semántica de información que TSIS decide preservar
sobre uno o varios fenómenos observables,
independientemente de su modelo de representación
y de su implementación física.
```

Un Objeto de Información todavía no es una representación.

Tampoco es una variable.

Tampoco es una tabla.

Es únicamente aquello que merece ser representado.

Por ejemplo.

Existe el fenómeno:

```
Hay poca liquidez.
```

TSIS razona:

```
Ese fenómeno es importante.

Necesito conservar información sobre él.

Creo un Objeto de Información:

Liquidity
```

Otro ejemplo.

Existe el fenómeno:

```
El precio acelera.
```

TSIS decide:

```
Necesito preservar información
sobre ese comportamiento.

Creo el Objeto:

Momentum
```

Otro ejemplo.

Existe el fenómeno:

```
La actividad negociada aumenta
de forma anómala.
```

TSIS responde:

```
Ese comportamiento merece
una representación estable.

Creo el Objeto:

Trading Activity
```

Los Objetos no aparecen porque exista una tabla.

Tampoco aparecen porque exista una variable.

Aparecen porque previamente existe una necesidad científica de conservar información sobre un fenómeno observable.

Por ello, la secuencia correcta siempre es:

```
FENÓMENO

↓

TSIS decide conservar información

↓

OBJETO DE INFORMACIÓN
```

Nunca al contrario.

---

### Taxonomías que no deben mezclarse

Un Objeto de Información posee distintas dimensiones.

Cada una responde a una pregunta diferente.

```text
Information Object Family
=
significado semántico del Objeto.

Source Domain
=
fuente observable que aporta evidencia.

Temporal Resolution
=
escala temporal o ventana de observación.

Institutional Role
=
función del Objeto dentro de TSIS.
```

Ejemplo:

```text
Liquidity

Information Object Family
=
Liquidity

Source Domain
=
Quotes + Trades + OHLCV

Temporal Resolution
=
intraday_bar

Institutional Role
=
observable
```

Estas taxonomías describen aspectos distintos del mismo Objeto.

No deben fusionarse bajo una única etiqueta como:

```text
family
```

porque mezclarían:

```text
significado

fuente

resolución temporal

función institucional
```

que pertenecen a planos conceptuales diferentes.

Mantener esa separación permite que un mismo Objeto pueda evolucionar en su implementación física sin perder su identidad científica.


````md id="xt84nk"
### Un `Modelo de Representación` conceptualiza la representación del `Objeto`

Una vez que TSIS ha decidido qué `Objeto de Información` debe preservar,
todavía queda una decisión científica importante.

Debe decidir:

```text
¿Cómo vamos a representar ese Objeto?
```

Esa decisión pertenece al `Modelo de Representación`.

El papel del Modelo de Representación es separar:

```text
el significado
```

de:

```text
la implementación física.
```

Es decir,

el Objeto define **qué información** debe preservarse.

El Modelo define **cómo** representarla conceptualmente.

Solo después aparecerán las variables concretas.

Por ejemplo.

```
OBJETO DE INFORMACIÓN

Liquidity
```

Todavía no sabemos qué variables utilizaremos.

Primero debemos decidir qué entendemos por liquidez.

---

Modelo de Representación A

```
OBJETO DE INFORMACIÓN

Liquidity

MODELO DE REPRESENTACIÓN

Representaremos la liquidez mediante:

- Coste esperado de ejecución
- Facilidad para cruzar órdenes
- Profundidad disponible
```

---

Modelo de Representación B

```
OBJETO DE INFORMACIÓN

Liquidity

MODELO DE REPRESENTACIÓN

Representaremos la liquidez mediante:

- Liquidez implícita del Order Book
- Impacto esperado de una orden
- Elasticidad del precio
```

---

Ambos modelos representan exactamente el mismo Objeto de Información:

```
Liquidity
```

Pero cada uno propone una conceptualización distinta de cómo representar ese significado.

El Objeto permanece.

Lo que cambia es la representación conceptual.

Por tanto:

```text
Objeto de Información

↓

¿Qué información quiero conservar?

Modelo de Representación

↓

¿Cómo decido representar esa información?
```

Todavía no existen variables.

Todavía no existen tablas.

Todavía no existe implementación física.

Solo existe una decisión científica acerca de cuál es la mejor representación conceptual del Objeto.

Esta separación es uno de los principios fundamentales de la arquitectura.

Si mañana descubres una forma mejor de representar:

```text
Liquidity
```

no cambia el Objeto.

Simplemente cambia el Modelo de Representación.

Del mismo modo,

si dentro de cinco años descubres una representación superior para:

```text
Momentum

Trading Activity

Volatility

Market Regime
```

la arquitectura permanece estable.

Únicamente evoluciona el Modelo.

Por eso el Modelo de Representación constituye el puente entre:

```text
el significado científico
```

y:

```text
la implementación física.
```

Esa separación permite que TSIS evolucione científicamente sin romper la identidad de los Objetos de Información que representa.
````


````md id="m31dqw"
### La `Implementación Física` implementa el Modelo de Representación

Una vez definido el `Modelo de Representación`, todavía queda una última decisión antes de llegar a las tablas.

Debe responderse a la pregunta:

```text
¿Qué variables implementan ese modelo?
```

Esa decisión pertenece a la `Implementación Física`.

Mientras que el Modelo de Representación sigue siendo conceptual,

la Implementación Física ya define:

```text
columnas

atributos

features

variables derivadas

fórmulas

métricas
```

que materializan esa representación.

Por ejemplo.

Modelo de Representación A

```
OBJETO DE INFORMACIÓN

Liquidity

MODELO DE REPRESENTACIÓN

Representaremos la liquidez mediante:

- Coste esperado de ejecución
- Disponibilidad de contrapartida
- Profundidad del mercado
```

La Implementación Física podría ser:

```
IMPLEMENTACIÓN FÍSICA

Coste esperado de ejecución

    - spread
    - spread_pct

Disponibilidad de contrapartida

    - quote_count
    - trade_count

Profundidad del mercado

    - bid_depth
    - ask_depth
    - depth_imbalance
```

---

El mismo Objeto podría tener otro Modelo.

Modelo de Representación B

```
OBJETO DE INFORMACIÓN

Liquidity

MODELO DE REPRESENTACIÓN

Representaremos la liquidez mediante:

- Impacto esperado de una orden
- Sensibilidad del precio al volumen
- Liquidez implícita
```

La Implementación Física correspondiente sería distinta:

```
IMPLEMENTACIÓN FÍSICA

Impacto esperado de una orden

    - amihud_illiquidity

Sensibilidad del precio al volumen

    - kyle_lambda

Liquidez implícita

    - roll_spread
```

En ambos casos:

```text
el Objeto es el mismo;

el Modelo cambia;

la Implementación Física cambia.
```

Por tanto, las variables nunca deberían convertirse en la definición del Objeto.

Las variables únicamente implementan una representación previamente aprobada.

La cadena correcta permanece:

```
OBJETO DE INFORMACIÓN

↓

MODELO DE REPRESENTACIÓN

↓

IMPLEMENTACIÓN FÍSICA
```

Nunca:

```
Tengo estas variables.

↓

Buscaré qué Objeto podrían representar.
```

---

La Implementación Física tampoco pertenece todavía a una tabla.

Una variable como:

```
spread_pct
```

no "es" una tabla.

Una variable como:

```
rolling_volatility
```

no "es" un dataset.

Simplemente constituye una implementación concreta de un Modelo de Representación.

Posteriormente, la arquitectura decidirá dónde materializar esas variables.

Por ello, la Implementación Física responde exclusivamente a esta pregunta:

```text
¿Qué variables implementan
la representación aprobada
del Objeto de Información?
```

No responde:

```text
¿Dónde se almacenan?

¿Cómo se consumen?

¿Qué Builder las utilizará?
```

Esas decisiones pertenecen a las siguientes capas de la arquitectura.

Mantener separadas estas responsabilidades permite que TSIS pueda:

- sustituir variables por otras mejores;
- incorporar nuevas implementaciones;
- retirar variables obsoletas;
- evolucionar la representación científica;

sin modificar la identidad del Objeto de Información que se pretende conservar.
````


````md
### Materialización en `Tablas`

La `Implementación Física` define qué variables representan un Modelo.

Las tablas responden a una pregunta distinta:

```text
¿Dónde se materializan esas variables?
```

Una tabla no define el significado.

Una tabla no define el Objeto.

Una tabla no define el Modelo de Representación.

Una tabla únicamente constituye el soporte físico donde viven determinadas variables.

Por ello, una misma tabla puede contener variables pertenecientes a varios Objetos de Información distintos.

Por ejemplo:

```
014_master_intraday_bar_table

├── Momentum
├── Trading Activity
├── Intraday Position
└── Volatility
```

No significa que la tabla represente un único Objeto.

Significa únicamente que materializa variables utilizadas por varios Modelos de Representación diferentes.

Del mismo modo, un único Objeto puede obtener sus variables desde varias tablas.

Por ejemplo:

```
OBJETO DE INFORMACIÓN

Liquidity
```

puede materializarse mediante variables procedentes de distintas superficies físicas.

```
004_master_daily_table

- dollar_volume
- rvol_20d
```

```
014_master_intraday_bar_table

- volume
- vwap
- transaction_count
```

```
015_microstructure_features_table

- quotes_spread_bps_median
- quotes_top_depth_mean
```

El Objeto permanece único.

Lo que cambia es la procedencia física de las variables que implementan su Modelo de Representación.

Esto proporciona una propiedad muy importante.

Supongamos que mañana la arquitectura física cambia.

Por ejemplo:

```
relative_volume
```

deja de vivir en:

```
014_master_intraday_bar_table
```

y pasa a otra tabla.

Nada cambia desde el punto de vista científico.

El Objeto:

```
Trading Activity
```

sigue siendo exactamente el mismo.

El Modelo de Representación tampoco cambia.

Únicamente cambia la localización física desde la que el Builder recupera la variable.

Por ello, las tablas nunca deberían convertirse en la referencia semántica del sistema.

La referencia siempre debe mantenerse en los Objetos de Información y en sus Modelos de Representación.

Las tablas únicamente indican dónde encontrar la implementación física correspondiente.

La cadena completa queda:

```
OBJETO DE INFORMACIÓN

↓

MODELO DE REPRESENTACIÓN

↓

IMPLEMENTACIÓN FÍSICA

↓

TABLAS
```

No al revés.

---

Cuando posteriormente el `Market State Builder` construya una representación, nunca preguntará:

```
¿Qué columnas tiene esta tabla?
```

Preguntará:

```
¿Qué Objetos necesita Market State?
```

Después resolverá:

```
¿Qué Modelo representa cada Objeto?
```

Posteriormente:

```
¿Qué variables implementan ese Modelo?
```

Y únicamente entonces:

```
¿En qué tablas viven esas variables?
```

La dirección de la arquitectura permanece constante.

Las tablas son el último nivel físico de representación.

Nunca el primero.
````



````md id="7mkn2q"
### `Market State Builder`

El `Market State Builder` materializa la representación canónica del estado del mercado.

No descubre fenómenos.

No decide qué Objetos deben existir.

No selecciona variables por criterio propio.

No interpreta el mercado.

Su responsabilidad consiste únicamente en ejecutar el contrato de representación aprobado para `Market State`.

Ese contrato declara qué Objetos de Información son necesarios para describir correctamente el estado observable del mercado.

Por ejemplo:

```
MARKET STATE REPRESENTATION CONTRACT

required_information_objects

- Momentum
- Liquidity
- Trading Activity
- Volatility
- Intraday Position
- News Context
- Fundamental Context
- Market Regime
```

A partir de esa declaración, el Builder realiza una secuencia completamente gobernada.

```
Market State Builder

↓

Lee el contrato de representación.

↓

Obtiene los Objetos de Información requeridos.

↓

Consulta el Modelo de Representación
de cada Objeto.

↓

Resuelve qué variables implementan
cada Modelo.

↓

Localiza las tablas donde viven
esas variables.

↓

Recupera únicamente los valores
legalmente observables
en el decision_timestamp.

↓

Valida cobertura,
calidad,
temporalidad
y restricciones.

↓

Materializa
el Market State.
```

El Builder nunca realiza preguntas del tipo:

```
¿Qué columnas tiene esta tabla?
```

Siempre trabaja en sentido descendente:

```
¿Qué Objetos necesita
Market State?
```

↓

```
¿Qué Modelos representan
esos Objetos?
```

↓

```
¿Qué variables implementan
esos Modelos?
```

↓

```
¿Dónde viven esas variables?
```

↓

```
¿Pueden observarse legalmente
en t?
```

---

Por ello, el Builder no realiza joins indiscriminados entre tablas.

Recupera únicamente:

```
variables admitidas;

variables necesarias para los Objetos
requeridos;

valores legalmente observables
en decision_timestamp;

versiones válidas
según as_of_utc;

registros con cobertura,
calidad
y restricciones compatibles.
```

Para conseguirlo utiliza únicamente relaciones temporales y claves gobernadas.

Por ejemplo:

```
instrument_id

session_date

decision_timestamp

source_timestamp

valid_from

valid_to

as_of_utc
```

Cada superficie física puede requerir una política temporal distinta.

Por ejemplo:

```
014_master_intraday_bar_table

↓

selecciona la barra cerrada
o el valor intradía permitido
en t.
```

```
009_fundamentals_asof_table

↓

selecciona la última información
fundamental conocida
antes o en t.
```

```
010_news_context_table

↓

selecciona únicamente noticias
publicadas y disponibles
antes o en t.
```

```
012_regime_context_table

↓

selecciona el régimen vigente
y observable
en t.
```

```
015_microstructure_features_table

↓

selecciona la ventana
microestructural válida
para ese decision_timestamp.
```

Cada tabla mantiene su propia política de observabilidad.

El Builder únicamente las ejecuta.

Nunca las redefine.

---

El resultado es una única representación integrada del mercado.

Por ejemplo:

```
market_state_id

instrument_id

decision_timestamp

momentum__return_1m
momentum__return_5m
momentum__slope

trading_activity__relative_volume
trading_activity__volume_acceleration

intraday_position__distance_to_hod
intraday_position__distance_to_vwap

liquidity__spread_pct
liquidity__depth_proxy

news_context__presence
news_context__age

market_regime__risk_on_off_state

component_quality_flags
component_as_of_utc
```

No todas las variables proceden de la misma tabla.

No todos los Objetos utilizan la misma resolución temporal.

No todos los componentes tienen la misma política de observabilidad.

El `Market State Builder` es precisamente el componente responsable de integrar toda esa información respetando:

```text
el contrato;

la legalidad temporal;

la autoridad de Data Foundation;

las políticas de consumo;

las restricciones activas;

la semántica aprobada
de Market State.
```

Su resultado no es una colección de columnas.

Es la materialización coherente del estado observable del mercado en un instante determinado.
````


````md id="msb913"
### `Market State`

La necesidad de construir una representación del estado del mercado
surge directamente de las preguntas científicas que TSIS pretende responder.

Una vez construida esa representación,
los distintos consumidores reutilizan exactamente el mismo `Market State`.

---

Ejemplos de preguntas científicas.

```text
PREGUNTA CIENTÍFICA

¿La probabilidad de continuación
aumenta cuando el precio acelera?

↓

NECESIDAD DE INFORMACIÓN

Conocer dirección,
intensidad
y aceleración del movimiento.

↓

OBJETO DE INFORMACIÓN

Momentum
```

---

```text
PREGUNTA CIENTÍFICA

¿Es posible ejecutar una operación
sin un coste o impacto excesivo?

↓

NECESIDAD DE INFORMACIÓN

Conocer las condiciones
observables de liquidez.

↓

OBJETO DE INFORMACIÓN

Liquidity
```

---

```text
PREGUNTA CIENTÍFICA

¿El movimiento ocurre
con participación anómala?

↓

NECESIDAD DE INFORMACIÓN

Conocer la intensidad
de actividad negociada.

↓

OBJETO DE INFORMACIÓN

Trading Activity
```

---

No es el Builder quien razona.

No son las tablas.

No son las variables.

Es el diseño científico el que concluye:

```text
Para responder correctamente
estas preguntas,

el estado observable del mercado
debe preservar información sobre:

Momentum

Liquidity

Trading Activity

Volatility

Intraday Position

News Context

Fundamental Context

Market Regime

...
```

Posteriormente esa decisión queda formalizada en un contrato.

```text
MARKET STATE REPRESENTATION CONTRACT

required_information_objects

- Momentum

- Liquidity

- Trading Activity

- Volatility

- Intraday Position

- News Context

- Fundamental Context

- Market Regime
```

Ese contrato constituye la autoridad semántica de `Market State`.

El Builder no modifica ese contrato.

Lo ejecuta.

Su secuencia es:

```text
Market State Builder

1.
Lee el contrato.

2.
Obtiene los Objetos requeridos.

3.
Consulta el Modelo de Representación
de cada Objeto.

4.
Resuelve las variables
que implementan ese Modelo.

5.
Localiza las tablas
donde viven esas variables.

6.
Recupera únicamente
información legalmente observable
en decision_timestamp.

7.
Valida cobertura,
calidad,
temporalidad
y restricciones.

8.
Materializa
Market State.
```

La separación exacta queda:

```text
Gobernanza científica

↓

decide qué información
merece preservarse.
```

```text
Market State Representation Contract

↓

declara qué Objetos
deben integrarse.
```

```text
Market State Builder

↓

ejecuta esa declaración.
```

```text
Market State

↓

resultado materializado.
```

Por ello,
`Market State` no depende de un algoritmo concreto.

No depende de una estrategia.

No depende de un modelo de Machine Learning.

Depende únicamente del contrato científico que define qué conocimiento observable debe preservarse sobre el mercado.

Ese contrato constituye la definición canónica de `Market State`.

Todos los consumidores posteriores reutilizan esa misma representación.

Nunca construyen un mercado distinto.
````


````md id="r6m2kp"
### ¿Quién necesita que existan los `Objetos de Información`?

Los Objetos de Información no existen por sí mismos.

Tampoco existen porque una tabla los contenga.

Existen porque distintas representaciones y consumidores necesitan preservar
conocimiento sobre el mercado.

Por ejemplo.

```
OBJETO DE INFORMACIÓN

Momentum
```

¿Por qué existe?

Porque distintos componentes del sistema necesitan conservar información sobre
la dirección, intensidad y aceleración del movimiento.

No porque exista una variable llamada:

```
return_1m
```

Ni porque exista una tabla:

```
014_master_intraday_bar_table
```

Sino porque múltiples consumidores necesitan ese conocimiento.

Por ejemplo:

```text
Momentum

Lo necesitan:

- Market State
- Event State
- Pattern Discovery
- Clustering
- Prediction
- Offline RL
- Policy Learning
```

Otro ejemplo.

```text
Liquidity

Lo necesitan:

- Market State
- Event State
- Execution Research
- Pattern Discovery
- Outcome Research
```

Otro.

```text
Trading Activity

Lo necesitan:

- Market State
- Event State
- Clustering
- Prediction
- Policy Learning
```

Cada consumidor puede utilizar una parte distinta de la representación.

Pero todos parten del mismo Objeto de Información.

Nunca deberían crear Objetos paralelos.

---

La arquitectura completa queda entonces cerrada.

```
PREGUNTAS CIENTÍFICAS

↓

MERCADO

↓

FENÓMENOS

↓

OBJETOS DE INFORMACIÓN

↓

MODELOS DE REPRESENTACIÓN

↓

IMPLEMENTACIÓN FÍSICA

↓

TABLAS

↓

MARKET STATE BUILDER

↓

MARKET STATE

↓

CONSUMIDORES
```

Cada nivel responde a una pregunta diferente.

```
PREGUNTAS CIENTÍFICAS

↓

¿Qué queremos investigar?
```

↓

```
FENÓMENOS

↓

¿Qué ocurre realmente
en el mercado?
```

↓

```
OBJETOS DE INFORMACIÓN

↓

¿Qué conocimiento merece
ser preservado?
```

↓

```
MODELOS DE REPRESENTACIÓN

↓

¿Cómo representamos
ese conocimiento?
```

↓

```
IMPLEMENTACIÓN FÍSICA

↓

¿Qué variables implementan
esa representación?
```

↓

```
TABLAS

↓

¿Dónde viven
esas variables?
```

↓

```
MARKET STATE BUILDER

↓

¿Cómo reconstruimos
legalmente ese conocimiento
en decision_timestamp?
```

↓

```
MARKET STATE

↓

¿Cuál era el estado observable
del mercado
en ese instante?
```

↓

```
CONSUMIDORES

↓

¿Cómo reutiliza cada consumidor
esa representación?
```

Esta dirección nunca debería invertirse.

Los consumidores no definen `Market State`.

Únicamente lo reutilizan.

De la misma forma:

Las tablas no definen los Objetos.

Únicamente materializan las variables que los implementan.

Y las variables tampoco definen el conocimiento.

Únicamente constituyen una implementación concreta de un Modelo de Representación previamente aprobado.

Por ello, la arquitectura permanece estable incluso cuando:

```text
cambian las variables;

cambian las tablas;

cambian los modelos;

aparecen nuevas implementaciones.
```

Mientras los Objetos de Información continúen representando el mismo conocimiento científico, `Market State` seguirá describiendo exactamente el mismo estado observable del mercado.
````

````md
### Representaciones de patrones o estrategias

Si `Market State` constituye la representación canónica del estado observable del mercado,

entonces únicamente debería existir una definición canónica de ese estado.

```
Market State

=

La mejor representación observable
del mercado
en el decision_timestamp t.
```

Lo que sí puede cambiar es la proyección que cada consumidor realiza sobre esa representación.

Por tanto, TSIS debería mantener una única representación canónica:

```
market_state_table
```

y posteriormente construir datasets derivados específicos para cada investigación.

Por ejemplo:

```
breakout_research_dataset

vwap_reclaim_research_dataset

squeeze_research_dataset

gap_and_go_research_dataset

...
```

Esos datasets no redefinen el estado del mercado.

Simplemente seleccionan los `Market State` necesarios para estudiar un determinado fenómeno.

Ejemplo.

Supongamos un estudio sobre:

```
PM_Squeeze_Event
```

con:

```
event_timestamp = 09:45
```

La investigación solicita:

```
09:35

09:36

...

09:45
```

Lo que hace el sistema es recuperar las representaciones ya existentes para esos instantes.

No construye diez definiciones nuevas del mercado.

Recupera diez representaciones distintas del mismo concepto canónico.

---

Del mismo modo, distintos algoritmos pueden necesitar subconjuntos diferentes del estado.

Por ejemplo:

```
Market State

│

├── Momentum

├── Liquidity

├── Trading Activity

├── Volatility

├── News Context

├── Market Regime

├── ...

└── cientos de atributos gobernados
```

Entonces:

```
Offline RL

↓

consume

420 atributos
```

```
Clustering

↓

consume

80 atributos
```

```
Prediction

↓

consume

otro subconjunto
```

```
CNN

↓

consume

imágenes

(no directamente Market State)
```

```
Transformer

↓

consume

secuencias de Market State
```

En todos los casos,

el algoritmo no modifica `Market State`.

Únicamente selecciona la información que necesita.

La arquitectura queda:

```
Market State

↓

Feature Selector

↓

Dataset RL
```

---

```
Market State

↓

Feature Selector

↓

Dataset Clustering
```

---

```
Market State

↓

Feature Selector

↓

Dataset Prediction
```

Cada dataset derivado constituye una proyección sobre la representación canónica.

Nunca una representación alternativa del mercado.

Por ello:

```text
Canonicalidad

=

una única definición
del estado observable del mercado.
```

Mientras que:

```text
Datasets derivados

=

distintas selecciones
de esa misma representación
para responder preguntas científicas diferentes.
```

De este modo,

TSIS evita crear múltiples definiciones incompatibles del mercado.

Todos los consumidores parten siempre del mismo conocimiento observable.

Lo único que cambia es la parte de ese conocimiento que cada uno decide utilizar.
````


````md id="m4pk81"
### ¿Se materializa una fila para cada `decision_timestamp`?

Depende del grano definido para la representación.

La definición canónica de `Market State` no obliga a una resolución física concreta.

Únicamente exige que toda representación responda a la misma pregunta:

```text
¿Cuál era el estado observable del mercado
en el decision_timestamp t?
```

Por ejemplo.

Si el grano canónico adoptado es:

```
instrument_id
+
decision_timestamp_minute
```

podrá existir una representación por cada minuto válido.

Si, en cambio, la investigación requiere resolución de segundos:

```
instrument_id
+
decision_timestamp_second
```

la cantidad de estados crecerá enormemente.

Por ello, nunca debe confundirse:

```text
la definición canónica
```

con:

```text
la resolución física
```

La primera pertenece a la arquitectura conceptual.

La segunda pertenece a la materialización.

Por tanto, distintas resoluciones pueden coexistir sin dejar de representar el mismo concepto.

Ejemplo:

```
market_state_1d

market_state_1m

market_state_1s

market_state_microstructure_window
```

No representan mercados distintos.

Representan exactamente el mismo concepto científico con distintas resoluciones físicas.

Todas ellas deben respetar la misma semántica:

```text
estado observable
legalmente disponible
en decision_timestamp.
```

La resolución nunca modifica el significado.

Únicamente modifica el nivel de detalle con el que ese significado queda materializado.

---

### Arquitectura práctica recomendada

La construcción práctica de `Market State` puede entenderse como la siguiente secuencia.

```
CONTRATO CANÓNICO DE MARKET STATE

↓

define:

- semántica

- Objetos de Información

- reglas temporales

- perfiles compatibles

↓

MARKET STATE BUILDER

↓

consulta las tablas fuente

↓

recupera únicamente
la información legalmente observable

↓

valida

↓

materializa

↓

MARKET STATE STORE

↓

es reutilizado
por todos los consumidores
```

El almacenamiento no constituye la definición de `Market State`.

Simplemente conserva representaciones ya construidas y validadas para evitar reconstrucciones innecesarias.

---

### ¿Se guardan los `Market State` ya construidos?

Sí.

Una vez construido y validado un `Market State`, resulta razonable conservarlo para permitir su reutilización posterior.

Debe distinguirse claramente entre:

```
Memoria temporal

- RAM

- caché

- estructuras temporales

- desaparecen al finalizar la ejecución
```

y:

```
Materialización persistente

- Parquet

- Delta

- Iceberg

- base de datos

- object storage

- permanece disponible
```

Por ejemplo:

```
market_state/

    version=v0_1/

        year=2025/

            month=01/

                symbol=ABCD/

                    part-000.parquet
```

o cualquier otra política de particionado equivalente.

Lo importante no es el formato.

Lo importante es que todas las representaciones compartan exactamente la misma definición canónica.

---

El almacenamiento puede organizarse en distintos niveles.

```
1.

Core histórico

- ampliamente materializado;

- información frecuente;

- bajo coste de almacenamiento.
```

```
2.

Extensiones especializadas

- microestructura;

- perfiles pesados;

- materialización bajo demanda
o por ventanas autorizadas.
```

```
3.

Datasets derivados

- específicos para investigación;

- específicos para algoritmos;

- no constituyen
Market State canónico.
```

---

Ejemplo.

Supongamos una investigación sobre:

```
2.000 PM Squeezes
```

No deberían construirse:

```
2.000 Market State distintos.
```

Lo correcto sería:

```
Event Registry

↓

contiene
los 2.000 eventos
```

Después, para cada evento:

```
30 minutos pre_event

↓

instante del evento

↓

20 minutos posteriores
```

El sistema solicita los `Market State`
correspondientes a esos `decision_timestamp`.

Si ya existen:

```
los reutiliza.
```

Si no existen y la política lo autoriza:

```
los construye.
```

Pero todos ellos permanecen dentro del mismo repositorio canónico:

```
market_state_table
```

De este modo,

si dos investigaciones utilizan exactamente el mismo:

```
instrument_id

+

decision_timestamp
```

ambas reutilizarán el mismo `Market State`.

Nunca se crearán dos definiciones distintas del mismo estado observable.

---

La canonicidad reside en:

```
la definición;

el contrato;

la semántica;

los Objetos de Información;

las reglas temporales;

las reglas de construcción.
```

La materialización puede variar.

Puede hacerse:

```
de forma histórica;

por particiones;

bajo demanda;

por resolución;

mediante perfiles;

mediante extensiones autorizadas.
```

Pero mientras todas esas representaciones respeten el mismo contrato semántico,

seguirán representando exactamente el mismo `Market State`.
````

````md id="m8z2qw"
### `Market State` no debe convertirse en una mega-tabla universal

La existencia de una representación canónica no implica que toda la información
que algún consumidor pudiera necesitar deba materializarse en una única fila física.

Ese enfoque conduciría inevitablemente a una arquitectura del tipo:

```text
Una única fila física

↓

con toda la información

↓

para todos los consumidores

↓

para todas las investigaciones

↓

para todos los algoritmos
```

Ese no es el objetivo de `Market State`.

Convertiría la representación canónica en una unión ilimitada de necesidades
downstream.

Cada nuevo consumidor añadiría nuevas columnas.

Cada nueva investigación ampliaría la tabla.

Cada nuevo algoritmo modificaría la definición del estado.

La consecuencia sería que el propio concepto de `Market State` dejaría de ser
estable.

Por ello, la canonicidad no debe definirse por la cantidad de variables que
contiene una fila.

Debe definirse por la estabilidad de su semántica.

La regla correcta es:

```text
Canonicalidad

=

una única semántica del estado

+

un único identificador lógico

+

reglas temporales comunes

+

Objetos de Información gobernados

+

perfiles de representación compatibles
```

No:

```text
una única tabla gigantesca
con todas las columnas posibles.
```

La materialización física puede organizarse mediante perfiles compatibles.

Por ejemplo:

```text
market_state_core

market_state_daily_context

market_state_intraday

market_state_microstructure_extension

market_state_news_extension
```

Todos ellos representan el mismo estado observable.

Lo único que cambia es el perfil físico de representación.

Todos los perfiles deben poder relacionarse mediante una identidad común.

Por ejemplo:

```text
market_state_id

instrument_id

decision_timestamp

representation_profile_version
```

El perfil `core` debería contener únicamente la información mínima gobernada
necesaria para identificar y describir el estado canónico.

Las extensiones especializadas permanecen separadas.

Solo se incorporan cuando:

```text
el contrato lo permite;

el perfil lo requiere;

la política temporal lo autoriza;

la investigación realmente las necesita.
```

De este modo, un consumidor que únicamente necesite contexto diario nunca
deberá cargar información microestructural.

Y un estudio basado en microestructura no obligará a que todos los Market State
históricos incorporen permanentemente cientos de variables adicionales.

La canonicidad permanece única.

La materialización permanece modular.

Por ello, la definición correcta de `Market State` no es:

```text
La mayor tabla posible.
```

Sino:

```text
La representación canónica del estado observable del mercado,

capaz de materializarse mediante distintos perfiles físicos compatibles,

sin alterar su significado científico.
```

````md id="6y9gk1"
## Conclusión

`Market State` constituye la representación canónica del estado observable del mercado dentro de TSIS.

Su misión no consiste en decidir.

No consiste en detectar eventos.

No consiste en ejecutar estrategias.

No consiste en predecir resultados.

Su misión consiste únicamente en preservar, de forma gobernada, el conocimiento observable que el sistema podía conocer en un `decision_timestamp`.

La arquitectura completa queda definida por una única dirección conceptual.

```
PREGUNTAS CIENTÍFICAS

↓

MERCADO

↓

FENÓMENOS

↓

OBJETOS DE INFORMACIÓN

↓

MODELOS DE REPRESENTACIÓN

↓

IMPLEMENTACIÓN FÍSICA

↓

TABLAS

↓

MARKET STATE BUILDER

↓

MARKET STATE
```

Cada capa responde a una pregunta distinta.

Cada una posee una autoridad diferente.

Y cada una puede evolucionar sin romper las demás.

Por ello:

```text
los fenómenos pueden descubrirse;

los Objetos pueden ampliarse;

los Modelos pueden mejorar;

las variables pueden sustituirse;

las tablas pueden reorganizarse;

los perfiles pueden evolucionar.
```

Sin embargo, mientras permanezcan estables:

```text
los Objetos de Información;

la semántica;

las reglas temporales;

el contrato de representación;
```

`Market State` seguirá representando exactamente el mismo conocimiento científico.

La representación canónica no pertenece a ningún algoritmo concreto.

No pertenece a ninguna estrategia.

No pertenece a ninguna investigación.

Pertenece al mercado.

Todos los consumidores posteriores deben partir de esa misma representación.

Posteriormente podrán aparecer otras capas especializadas que reutilicen ese estado observable para responder preguntas diferentes.

Por ejemplo:

```text
Event State

↓

¿Cómo estaba el mercado
respecto a un evento concreto?
```

```text
Execution State

↓

¿Qué capacidad real existía
para ejecutar una decisión
en ese instante?
```

```text
Outcome

↓

¿Qué ocurrió
después?
```

Pero ninguna de ellas redefine el mercado.

Todas parten del mismo `Market State`.

Por ello, la representación canónica constituye el punto de partida sobre el que se apoya toda la arquitectura de conocimiento de TSIS.

Mientras esa representación permanezca científicamente gobernada, temporalmente legal y conceptualmente estable, el resto del sistema podrá evolucionar sin perder coherencia ni reproducibilidad.
````





