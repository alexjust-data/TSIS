# Arquitectura de construcción de `Event State`

## Propósito

Este documento define cómo TSIS construye la representación canónica del estado observable del mercado respecto a un evento.

`Event State` no constituye una segunda representación independiente del mercado.

Parte siempre de un `Market State` previamente definido y añade únicamente el contexto necesario para representar la relación entre ese estado y un evento concreto.

La construcción de `Event State` depende de:

```text
Market State
```

y de la gobernanza definida dentro de:

```text
07_EVENT_STATE_INTEGRATION/
```

La representación obtenida podrá materializarse posteriormente mediante:

```text
event_state_table
```

o mediante los perfiles físicos autorizados para `Event State`.

Sin embargo, este documento describe exclusivamente su arquitectura conceptual, no su implementación física, su materialización ni su ejecución.

## ¿Qué es `Event State`?

`Event State` es la representación canónica del estado observable del mercado respecto a un evento concreto.

No representa:

```text
una estrategia
```

No representa:

```text
una decisión operativa
```

No representa:

```text
un resultado futuro
```

Representa únicamente:

```text
la información observable que el sistema podía conocer
sobre el mercado
respecto al evento E
en el decision_timestamp t.
```

Su identidad conceptual es:

**Event State** = *cómo estaba el mercado respecto a un evento en un instante determinado.*

Su grano semántico es:

```text
clave ≈ event_id + instrument_id + decision_timestamp
```

Toda la información contenida en un `Event State` debe cumplir simultáneamente:

```text
• ser observable en decision_timestamp;
• ser legal desde el punto de vista temporal;
• estar correctamente relacionada con el evento;
• no introducir leakage;
• no depender de resultados posteriores.
```

Por tanto, `Event State` responde únicamente a una pregunta científica:

```text
¿Qué sabía el sistema
sobre el mercado
respecto al evento E
en el instante t?
```

No responde:

```text
¿Qué debería hacer?
¿Era rentable?
¿Funcionó la estrategia?
```

Esas preguntas pertenecen a otras capas del sistema.

Por ello:

```text
Market State
=
estado observable del mercado.
```

```text
Event State
=
ese mismo estado
contextualizado respecto a un evento.
```

`Event State` no redefine el mercado.

Únicamente organiza una representación existente alrededor de una referencia temporal y semántica concreta denominada:

```text
evento
```

## ¿Por qué existe `Event State`?

`Market State` responde a una única pregunta:

```text
¿Qué sabía el sistema
sobre el mercado
en el instante t?
```

Sin embargo, muchas investigaciones necesitan responder una pregunta distinta.

No basta con conocer el estado general del mercado.

Necesitan conocer ese mismo estado respecto a un fenómeno concreto.

Por ejemplo:

```text
¿Qué sabía el sistema
sobre el mercado
180 segundos antes
de un PM Squeeze?
```

o:

```text
¿Qué sabía el sistema
exactamente cuando
se produjo un Halt Resume?
```

o:

```text
¿Qué sabía el sistema
durante la formación
de un VWAP Reclaim?
```

Todas esas preguntas comparten una característica.

No modifican el mercado.

Modifican el punto de referencia desde el que observamos ese mercado.

Por ello, `Event State` no construye un segundo estado del mercado.

Reutiliza un `Market State` ya existente y añade únicamente el contexto necesario para responder preguntas condicionadas por un evento.

Por tanto:

```text
Market State
=
estado observable del mercado.
```

```text
Event State
=
Market State
+
contexto respecto a un evento.
```

La existencia de `Event State` responde a una necesidad científica.

No a una necesidad técnica.

Su función consiste en organizar observaciones comparables alrededor de eventos comunes.

Por ejemplo:

```text
pre_event

at_event

post_event
```

permiten estudiar cómo evoluciona el mismo mercado alrededor de un fenómeno determinado.

Sin `Event State`, esas comparaciones quedarían mezcladas con el resto de observaciones del mercado.

Con `Event State`, todas ellas pueden organizarse mediante una representación gobernada y temporalmente consistente.

Por ello, `Event State` no existe para detectar eventos.

Tampoco existe para ejecutar estrategias.

Existe para responder preguntas científicas sobre el comportamiento del mercado respecto a un evento concreto, reutilizando siempre el mismo conocimiento observable definido previamente por `Market State`.


````md
## ¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableció que un sistema de aprendizaje exitoso deba contener una representación denominada `Event State`.

AlphaGo, AlphaGo Zero y MuZero aprenden sobre una representación del estado desde la que posteriormente estiman política, valor, recompensa o dinámica.

No existe una representación específica equivalente a `Event State`.

Por tanto, la conclusión rigurosa es:

```text
Event State NO procede de DeepMind.

Sí implementa un principio compatible
con sus sistemas de aprendizaje:

organizar observaciones
respecto a un contexto concreto,
manteniendo siempre la legalidad temporal
de la información utilizada.
```

En TSIS, `Event State` desempeña precisamente ese papel.

No crea un segundo mercado.

Reutiliza un `Market State` previamente construido y lo contextualiza respecto a un evento.

Por ello incorpora información adicional como:

```text
event_id

event_type

relación temporal

estado del evento

referencias del evento
```

pero mantiene exactamente el mismo conocimiento observable que existía en `Market State`.

La certificación correcta es:

```text
Event State
=
decisión arquitectónica propia de TSIS.

Estado contextualizado
respecto a un evento
=
principio compatible con DeepMind.

Garantía de éxito por existir
=
ninguna.
```

La utilidad de `Event State` dependerá de que preserve correctamente:

```text
la identidad del evento;

la relación temporal;

la legalidad del decision_timestamp;

la separación entre input y outcome;

la ausencia de leakage.
```

No dependerá simplemente de materializar una segunda tabla.
````

Tienes razón otra vez. Me he vuelto a ir al estilo editorial.

Aquí va con la densidad del original.

````md
## `Event State` consume `Market State`

A diferencia de `Market State`, `Event State` no comienza en los `Objetos de Información`.

Comienza en un `evento`.

Ese evento ya posee una identidad gobernada dentro del `Event Type Registry`.

Por ejemplo:

```
EVENTO

- event_id = E123
- event_type = PM_Squeeze_Event
- instrument_id = ABCD
- event_timestamp = 09:45:00
```

A partir de ese evento, `Event State` necesita conocer cuál era el estado observable del mercado en distintos `decision_timestamp`.

Por ello, no reconstruye el mercado.

Reutiliza un `Market State` previamente construido.

La cadena correcta es:

```
EVENTO
↓
Market State
↓
Event State
```

No:

```
EVENTO
↓
Variables
↓
Tablas
↓
Event State
```

Supongamos el siguiente ejemplo.

```
EVENTO

- event_id = PM_SQUEEZE_2026_07_18_ABCD_001
- event_timestamp = 09:45:00
```

Queremos conocer el estado del mercado tres minutos antes.

```
EVENT STATE

- event_id = PM_SQUEEZE_2026_07_18_ABCD_001
- decision_timestamp = 09:42:00
```

El Builder recupera primero el `Market State` correspondiente.

```
MARKET STATE

- instrument_id = ABCD
- decision_timestamp = 09:42:00
```

Ese estado ya contiene:

```
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

Posteriormente `Event State` añade únicamente el contexto necesario para representar la relación con el evento.

Por ejemplo:

```
event_id
event_type
event_timestamp
state_role
relative_time_to_event
event_phase
event_detection_status
event_reference_levels
event_specific_quality_flags
```

La diferencia conceptual es:

```
Market State

- organiza información por instrumento y decision_timestamp.
```

```
Event State

- organiza esa misma información respecto a un evento concreto.
```

Por tanto, `Event State` no debería duplicar ni inventar un segundo estado del mercado.

Debe reutilizar o referenciar un `Market State` previamente válido.

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

La arquitectura permanece estable:

```
EVENTO
↓
Market State
↓
Event State
```

No:

```
EVENTO
↓
nuevo mercado
↓
Event State
```

El estado observable del mercado continúa siendo único.

`Event State` únicamente añade el contexto necesario para estudiar ese mismo estado respecto a un evento gobernado.
````

A partir del siguiente bloque ya no volveré a dejar líneas vacías dentro de los bloques `text` o `code`. Voy a copiar exactamente la densidad visual de tu documentación original.


## Arquitectura

La arquitectura de `Event State` sigue una dirección distinta a la de `Market State`.
No comienza en el mercado.
No comienza en los fenómenos.
No comienza en los Objetos de Información.
Todo eso ya ha sido resuelto previamente por `Market State`.
`Event State` comienza cuando existe un evento gobernado.

```
EVENTO
↓
MARKET STATE
↓
CONTEXTO DEL EVENTO
↓
EVENT STATE BUILDER
↓
EVENT STATE
```

Cada nivel responde a una pregunta distinta.

```
EVENTO
¿Qué fenómeno concreto queremos estudiar?
```

↓

```
MARKET STATE
¿Cuál era el estado observable del mercado
en ese decision_timestamp?
```

↓

```
CONTEXTO DEL EVENTO
¿Cómo se relaciona ese estado
con el evento?
```

↓

```
EVENT STATE BUILDER
¿Cómo construimos legalmente
esa representación?
```

↓

```
EVENT STATE
¿Cuál era el estado observable del mercado
respecto al evento
en t?
```

La dirección nunca debería invertirse.

No debería ocurrir:

```
Tengo este evento.
↓
Voy a reconstruir el mercado.
```

Ni tampoco:

```
Tengo unas variables.
↓
Crearé un Event State.
```

La dirección correcta siempre es:

```
Existe un evento.
↓
Existe un Market State válido.
↓
Se define la relación temporal
entre ambos.
↓
El Builder añade únicamente
el contexto específico del evento.
↓
Se obtiene un único Event State.
```

Por ello, `Event State` no necesita volver a representar el mercado.  
El mercado ya está representado.  
Lo único que añade es la relación entre:  

```text
un Market State
y
un evento gobernado.
```

La estabilidad de `Event State` depende precisamente de mantener esa separación.  
El `Market State` puede evolucionar.  
El `Event Registry` puede evolucionar.  
Los detectores pueden evolucionar.  
Las ventanas pueden evolucionar.  

Pero mientras permanezcan estables:

```text
la identidad del evento;
la identidad del Market State;
la relación temporal;
las reglas de consumo;
las políticas de observabilidad;
```

`Event State` seguirá representando exactamente el mismo conocimiento científico respecto al evento.

````md id="yjv6kt"
### `Event State Builder`

El `Event State Builder` materializa la representación canónica del estado observable del mercado respecto a un evento.
No detecta eventos.
No decide qué Event Types existen.
No admite eventos en el registro.
No interpreta el mercado.
Su responsabilidad consiste únicamente en ejecutar el contrato de representación aprobado para `Event State`.

Ese contrato declara qué información adicional debe incorporarse para contextualizar un `Market State` respecto a un evento gobernado.

Por ejemplo:

```
EVENT STATE REPRESENTATION CONTRACT

required_components

- Market State
- Event Identity
- Temporal Relationship
- Event Context
```

A partir de esa declaración, el Builder realiza una secuencia completamente gobernada.

```
Event State Builder
↓
Lee el contrato de representación.
↓
Obtiene el evento correspondiente.
↓
Recupera el Market State requerido.
↓
Calcula la relación temporal entre ambos.
↓
Añade únicamente el contexto permitido del evento.
↓
Valida cobertura,
calidad,
temporalidad
y restricciones.
↓
Materializa el Event State.
```

El Builder nunca realiza preguntas del tipo:

```
¿Qué columnas tiene esta tabla?
```

Siempre trabaja en sentido descendente:

```
¿Qué Event State debo construir?
```

↓

```
¿A qué evento pertenece?
```

↓

```
¿Qué Market State necesita?
```

↓

```
¿Qué contexto del evento
debo incorporar?
```

↓

```
¿Es legal construirlo
en ese decision_timestamp?
```

El Builder nunca reconstruye el mercado.

Siempre parte de un `Market State` previamente válido.

Posteriormente añade únicamente información propia del evento.

Por ejemplo:

```
event_id

event_type

event_timestamp

state_role

relative_time_to_event

event_phase

event_detection_status

event_reference_levels

event_specific_quality_flags
```

Cada uno de esos componentes posee su propia política de observabilidad.

El Builder únicamente ejecuta dichas políticas.

Nunca las redefine.

El resultado es una representación contextualizada del mismo estado observable del mercado.

Por ello, el `Event State Builder` integra únicamente:

```text
un Market State válido;
un evento gobernado;
una relación temporal válida;
el contexto específico autorizado del evento.
```

Nunca incorpora:

```text
estrategias;
órdenes;
resultados;
información posterior;
variables con leakage.
```

Su resultado no constituye un segundo mercado.

Constituye el mismo mercado observado desde la referencia de un evento concreto.
````


````md id="5pk1mr"
### `Event State`

La necesidad de construir una representación del estado del mercado respecto a un evento surge directamente de las preguntas científicas que TSIS pretende responder.
Una vez construida esa representación, los distintos consumidores reutilizan exactamente el mismo `Event State`.

Ejemplos de preguntas científicas.

```text
PREGUNTA CIENTÍFICA

¿Cómo era el mercado
antes de un Halt Resume?

↓

NECESIDAD DE INFORMACIÓN

Conocer el estado observable
antes de la reanudación.

↓

REPRESENTACIÓN REQUERIDA

Event State
```

```text
PREGUNTA CIENTÍFICA

¿Cómo evolucionó el mercado
durante un PM Squeeze?

↓

NECESIDAD DE INFORMACIÓN

Comparar estados
respecto al mismo evento.

↓

REPRESENTACIÓN REQUERIDA

Event State
```

```text
PREGUNTA CIENTÍFICA

¿Qué diferencias existen
entre los eventos
que continúan
y los que fracasan?

↓

NECESIDAD DE INFORMACIÓN

Comparar estados equivalentes
respecto al mismo tipo de evento.

↓

REPRESENTACIÓN REQUERIDA

Event State
```

El diseño científico es quien razona:

```text
Para responder estas preguntas,
el sistema necesita organizar
Market State
respecto a un evento.
```

Posteriormente esa decisión queda formalizada en un contrato.

```text
EVENT STATE REPRESENTATION CONTRACT

required_components

- Market State
- Event Identity
- Temporal Relationship
- Event Context
```

El Builder recibe ese contrato y lo ejecuta.

```text
Event State Builder

1. Lee el contrato.
2. Obtiene el evento correspondiente.
3. Recupera el Market State requerido.
4. Calcula la relación temporal.
5. Añade el contexto permitido del evento.
6. Valida cobertura, calidad y temporalidad.
7. Materializa la fila de Event State.
```

La separación exacta queda:

```text
Gobernanza científica
=
decide qué conocimiento
debe preservarse
respecto a un evento.

Contrato de Event State
=
declara qué componentes
deben integrarse.

Event State Builder
=
ejecuta esa declaración.

Event State
=
resultado materializado.
```

Por ello, `Event State` no depende de un algoritmo concreto.
No depende de una estrategia.
No depende de un detector concreto.
Depende únicamente del contrato científico que define cómo debe contextualizarse un `Market State` respecto a un evento gobernado.

Ese contrato constituye la definición canónica de `Event State`.

Todos los consumidores posteriores reutilizan esa misma representación.

Nunca construyen un Event State diferente para cada investigación.
````


### ¿Quién necesita que exista `Event State`?

`Event State` no existe por sí mismo.
Tampoco existe porque exista un `Event Type`.
Existe porque distintos consumidores necesitan estudiar el mismo estado del mercado respecto a un mismo evento.

Por ejemplo:

```
EVENTO

Halt Resume
```

¿Por qué necesitamos `Event State`?

Porque distintos consumidores necesitan comparar cómo era el mercado antes, durante y después de ese mismo evento.

No porque exista una variable llamada:

```
relative_time_to_event
```

Ni porque exista una tabla llamada:

```
event_state_table
```

Sino porque múltiples consumidores necesitan reutilizar exactamente la misma contextualización del mercado.

Por ejemplo:

```text
Event State

Lo necesitan:

- Pattern Discovery
- Clustering
- Outcome Research
- Prediction
- Offline RL
- Policy Learning
```

Cada consumidor puede utilizar una parte distinta de la representación.

Pero todos parten del mismo `Event State`.

Nunca deberían construir una contextualización distinta del mismo evento.

La cadena completa queda cerrada así:

```
PREGUNTAS CIENTÍFICAS
↓
EVENTO
↓
MARKET STATE
↓
CONTEXTO DEL EVENTO
↓
EVENT STATE BUILDER
↓
EVENT STATE
↓
CONSUMIDORES
```

Cada nivel responde a una pregunta distinta.

```
PREGUNTAS CIENTÍFICAS

¿Qué queremos investigar?
```

↓

```
EVENTO

¿Respecto a qué fenómeno
queremos observar el mercado?
```

↓

```
MARKET STATE

¿Cuál era el estado observable
del mercado?
```

↓

```
CONTEXTO DEL EVENTO

¿Cómo se relaciona ese estado
con el evento?
```

↓

```
EVENT STATE BUILDER

¿Cómo construimos legalmente
esa representación?
```

↓

```
EVENT STATE

¿Cuál era el estado observable
del mercado
respecto al evento?
```

↓

```
CONSUMIDORES

¿Cómo reutiliza cada consumidor
esa representación?
```

Esta dirección nunca debería invertirse.

Los consumidores no definen `Event State`.

Únicamente lo reutilizan.

Del mismo modo, el `Event Registry` no define `Event State`.

Únicamente proporciona la identidad gobernada del evento.

Y `Market State` tampoco cambia.

Únicamente constituye la representación base sobre la que `Event State` añade contexto.

Por ello, la arquitectura permanece estable incluso cuando:

```text
cambian los detectores;
cambian los Event Types;
cambian las ventanas;
cambian los Builders;
```

Mientras permanezcan estables:

```text
la identidad del evento;
la identidad del Market State;
la relación temporal;
el contrato de Event State;
```

`Event State` seguirá representando exactamente el mismo conocimiento científico respecto al evento.


### Representaciones de patrones o investigaciones

Si `Event State` constituye la representación canónica del estado observable del mercado respecto a un evento,

entonces únicamente debería existir una definición canónica de esa representación.

```
Event State

=

La mejor representación observable
del mercado
respecto a un evento
en un decision_timestamp.
```

Lo que sí puede cambiar es la proyección que hace cada consumidor sobre esa representación.

Por tanto, TSIS debería mantener una única representación canónica:

```
event_state_table
```

y posteriormente construir datasets derivados específicos para cada investigación.

Por ejemplo:

```
halt_resume_research_dataset

pm_squeeze_research_dataset

vwap_reclaim_research_dataset

gap_and_go_research_dataset

...
```

Esos datasets no redefinen `Event State`.

Simplemente seleccionan las filas necesarias para estudiar un determinado tipo de evento.

Ejemplo.

Supongamos una investigación sobre:

```
PM_Squeeze_Event
```

Cada evento posee su propia ventana.

```
event_id = E001

↓

pre_event

↓

at_event

↓

post_event
```

El sistema no crea una representación distinta para cada estrategia.

Recupera los `Event State` correspondientes a ese evento.

Del mismo modo, distintos algoritmos pueden necesitar subconjuntos diferentes del mismo `Event State`.

Por ejemplo:

```
Event State

│

├── Market State

├── Event Identity

├── Temporal Relationship

├── Event Context

└── ...
```

Entonces:

```
Offline RL

↓

consume

un subconjunto
```

```
Clustering

↓

consume

otro subconjunto
```

```
Prediction

↓

consume

otro subconjunto diferente
```

Todos ellos reutilizan exactamente el mismo `Event State`.

Nunca construyen una representación distinta del mismo evento.

La arquitectura queda:

```
Event State
↓
Feature Selector
↓
Dataset RL
```

---

```
Event State
↓
Feature Selector
↓
Dataset Clustering
```

---

```
Event State
↓
Feature Selector
↓
Dataset Prediction
```

Cada dataset derivado constituye una proyección sobre la representación canónica.

Nunca una representación alternativa del mismo evento.

Por ello:

```text
Canonicalidad

=

una única definición
del estado observable del mercado
respecto a un evento.
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

TSIS evita crear múltiples definiciones incompatibles de un mismo evento.

Todos los consumidores parten siempre del mismo `Event State`.

Lo único que cambia es la parte de esa representación que cada uno decide utilizar.


### ¿Se materializa una fila para cada `decision_timestamp`?

Depende del grano definido para la representación.

La definición canónica de `Event State` no obliga a una resolución física concreta.

Únicamente exige que toda representación responda a la misma pregunta:

```text
¿Cuál era el estado observable del mercado
respecto al evento E
en el decision_timestamp t?
```

Por ejemplo.

Si el grano canónico adoptado es:

```
event_id
+
decision_timestamp_minute
```

podrá existir una representación por cada minuto válido de la ventana del evento.

Si, en cambio, la investigación requiere resolución de segundos:

```
event_id
+
decision_timestamp_second
```

el número de estados crecerá considerablemente.

Por ello, nunca debe confundirse:

```text
la definición canónica
```

con:

```text
la resolución física.
```

La primera pertenece a la arquitectura conceptual.

La segunda pertenece a la materialización.

Por tanto, distintas resoluciones pueden coexistir sin dejar de representar el mismo concepto.

Ejemplo:

```
event_state_1m

event_state_1s

event_state_microstructure_window
```

Todas ellas representan exactamente el mismo `Event State`.

Lo único que cambia es la resolución física utilizada para construir la representación.

Todas deben respetar la misma semántica:

```text
estado observable del mercado
respecto al evento
legalmente disponible
en el decision_timestamp.
```

La resolución nunca modifica el significado.

Únicamente modifica el nivel de detalle con el que dicho significado queda materializado.

### Arquitectura práctica recomendable

La construcción práctica de `Event State` puede entenderse como la siguiente secuencia.

```
CONTRATO CANÓNICO DE EVENT STATE
↓
define:
- semántica
- relación con Market State
- contexto del evento
- reglas temporales
↓
EVENT STATE BUILDER
↓
recupera el Market State
↓
añade el contexto del evento
↓
valida
↓
materializa
↓
EVENT STATE STORE
↓
es reutilizado por los consumidores
```

El almacenamiento no constituye la definición de `Event State`.

Simplemente conserva representaciones ya construidas y validadas para evitar reconstrucciones innecesarias.

### ¿Se guardan los `Event State` ya construidos?

Sí.

Una vez construido y validado un `Event State`, resulta razonable conservarlo para permitir su reutilización posterior.

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
event_state/
    version=v0_1/
        event_type=PM_Squeeze/
            year=2026/
                part-000.parquet
```

o cualquier otra política de particionado equivalente.

Lo importante no es el formato.

Lo importante es que todas las representaciones compartan exactamente la misma definición canónica.

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
- no constituyen Event State canónico.
```

La canonicidad reside en:

```
la definición;
el contrato;
la semántica;
la relación con Market State;
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

seguirán representando exactamente el mismo `Event State`.


````md id="z2r8vc"
### `Event State` no debe convertirse en una mega-tabla universal

La existencia de una representación canónica no implica que toda la información que algún consumidor pudiera necesitar deba materializarse en una única fila física.

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

Ese no es el objetivo de `Event State`.

Convertiría la representación canónica en una unión ilimitada de necesidades downstream.

Cada nuevo consumidor añadiría nuevas columnas.

Cada nueva investigación ampliaría la representación.

Cada nuevo algoritmo modificaría la definición de `Event State`.

La consecuencia sería que el propio concepto de `Event State` dejaría de ser estable.

Por ello, la canonicidad no debe definirse por la cantidad de variables que contiene una fila.

Debe definirse por la estabilidad de su semántica.

La regla correcta es:

```text
Canonicalidad
=
una única semántica del estado respecto a un evento
+
una única identidad lógica del evento
+
una única relación con Market State
+
reglas temporales comunes
+
componentes de representación compatibles
```

No:

```text
una única tabla gigantesca
con todas las columnas posibles.
```

La materialización física puede organizarse mediante perfiles compatibles.

Por ejemplo:

```text
event_state_core
event_state_market_context
event_state_microstructure_extension
event_state_event_context
```

Todos ellos representan exactamente el mismo `Event State`.

Lo único que cambia es el perfil físico utilizado para materializar la representación.

Todos los perfiles deben poder relacionarse mediante una identidad común.

Por ejemplo:

```text
event_state_id
event_id
market_state_id
decision_timestamp
representation_profile_version
```

El perfil `core` debería contener únicamente la información mínima gobernada necesaria para describir correctamente el estado del mercado respecto al evento.

Las extensiones especializadas permanecen separadas.

Solo se incorporan cuando:

```text
el contrato lo permite;
el perfil lo requiere;
la política temporal lo autoriza;
la investigación realmente las necesita.
```

De este modo, un consumidor que únicamente necesite estudiar la evolución temporal del evento no tendrá que cargar información microestructural.

Y una investigación basada en microestructura no obligará a que todos los `Event State` incorporen permanentemente cientos de variables adicionales.

La canonicidad permanece única.

La materialización permanece modular.

Por ello, la definición correcta de `Event State` no es:

```text
La mayor tabla posible.
```

Sino:

```text
La representación canónica del estado observable del mercado
respecto a un evento,
capaz de materializarse mediante distintos perfiles físicos compatibles,
sin alterar su significado científico.
```
````


## Conclusión

`Event State` constituye la representación canónica del estado observable del mercado respecto a un evento dentro de TSIS.

Su misión no consiste en detectar eventos.

No consiste en admitir Event Types.

No consiste en ejecutar detectores.

No consiste en decidir.

No consiste en predecir resultados.

Su misión consiste únicamente en preservar, de forma gobernada, el conocimiento observable que el sistema podía conocer respecto a un evento en un `decision_timestamp`.

La arquitectura completa queda definida por una única dirección conceptual.

```
PREGUNTAS CIENTÍFICAS
↓
EVENTO
↓
MARKET STATE
↓
CONTEXTO DEL EVENTO
↓
EVENT STATE BUILDER
↓
EVENT STATE
```

Cada capa responde a una pregunta distinta.

```
PREGUNTAS CIENTÍFICAS
↓
¿Qué queremos investigar?
```

↓

```
EVENTO
↓
¿Respecto a qué fenómeno
queremos observar el mercado?
```

↓

```
MARKET STATE
↓
¿Cuál era el estado observable
del mercado?
```

↓

```
CONTEXTO DEL EVENTO
↓
¿Cómo se relaciona ese estado
con el evento?
```

↓

```
EVENT STATE BUILDER
↓
¿Cómo construimos legalmente
esa representación?
```

↓

```
EVENT STATE
↓
¿Cuál era el estado observable
del mercado
respecto al evento?
```

Cada una de esas capas puede evolucionar sin romper las demás.

Por ello:

```text
los Event Types pueden evolucionar;
los detectores pueden evolucionar;
las ventanas pueden evolucionar;
los Builders pueden evolucionar;
las implementaciones físicas pueden cambiar;
```

Sin embargo, mientras permanezcan estables:

```text
la identidad del evento;
la identidad del Market State;
la relación temporal;
el contrato de representación;
las reglas temporales;
```

`Event State` seguirá representando exactamente el mismo conocimiento científico.

La representación canónica no pertenece a un detector concreto.

No pertenece a una estrategia.

No pertenece a una investigación.

Pertenece al evento.

Todos los consumidores posteriores deben partir de esa misma representación.

Posteriormente podrán aparecer otras capas especializadas que reutilicen ese estado contextualizado para responder preguntas diferentes.

Por ejemplo:

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

Pero ninguna de ellas redefine el evento.

Todas parten del mismo `Event State`.

Por ello, `Event State` constituye la representación canónica del conocimiento observable del mercado respecto a un evento y el puente natural entre `Market State` y las capas posteriores de investigación, aprendizaje y evaluación de TSIS.

