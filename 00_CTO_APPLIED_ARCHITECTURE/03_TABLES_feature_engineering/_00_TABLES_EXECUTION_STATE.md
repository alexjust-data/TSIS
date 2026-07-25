````md
# Arquitectura de construcción de `Execution State`

## Propósito

Este documento define cómo TSIS construye la representación canónica del estado observable de ejecución.

`Execution State` no constituye una representación del mercado.

Tampoco constituye una representación de un evento.

Representa únicamente las condiciones observables que determinan la capacidad real del sistema para ejecutar una decisión en un `decision_timestamp`.

`Execution State` parte siempre de representaciones previamente construidas.

Depende de:

```text
Market State
```

y, cuando exista un evento:

```text
Event State
```

La representación obtenida podrá materializarse posteriormente mediante:

```text
execution_state_table
```

o mediante los perfiles físicos autorizados para `Execution State`.

Sin embargo, este documento describe exclusivamente su arquitectura conceptual, no su implementación física, su materialización ni su ejecución.

## ¿Qué es `Execution State`?

`Execution State` es la representación canónica del estado observable de la capacidad de ejecución del sistema en un instante determinado.

No representa:

```text
el mercado
```

No representa:

```text
un evento
```

No representa:

```text
una estrategia
```

No representa:

```text
un resultado futuro
```

Representa únicamente:

```text
la información observable que el sistema podía conocer
sobre su capacidad real de ejecutar
una decisión
en el decision_timestamp t.
```

Su identidad conceptual es:

**Execution State** = *cómo podía ejecutarse una decisión en un instante determinado.*

Su grano semántico es:

```text
clave ≈ instrumento + decision_timestamp + execution_context
```

Toda la información contenida en un `Execution State` debe cumplir simultáneamente:

```text
• ser observable en decision_timestamp;
• ser legal desde el punto de vista temporal;
• describir condiciones reales de ejecución;
• no introducir leakage;
• no depender del resultado posterior de la orden.
```

Por tanto, `Execution State` responde únicamente a una pregunta científica:

```text
¿Qué capacidad real tenía el sistema
para ejecutar una decisión
en el instante t?
```

No responde:

```text
¿Debía comprar?
¿Debía vender?
¿Ganó dinero?
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
estado observable del mercado
respecto a un evento.
```

```text
Execution State
=
estado observable
de la capacidad de ejecución.
```

`Execution State` no redefine el mercado.

Únicamente representa las restricciones y condiciones reales bajo las que una decisión podría ejecutarse.
````


````md
## ¿Por qué existe `Execution State`?

`Market State` responde a una única pregunta:

```text
¿Qué sabía el sistema
sobre el mercado
en el instante t?
```

`Event State` responde a otra:

```text
¿Qué sabía el sistema
sobre el mercado
respecto al evento E
en el instante t?
```

Sin embargo, ninguna de esas representaciones responde a una tercera pregunta.

```text
¿Qué capacidad real tenía el sistema
para ejecutar una decisión
en ese instante?
```

Dos situaciones pueden tener exactamente el mismo:

```text
Market State
```

e incluso el mismo:

```text
Event State
```

y, sin embargo, poseer capacidades de ejecución completamente distintas.

Por ejemplo:

```text
Locate disponible
=
Sí
```

frente a:

```text
Locate disponible
=
No
```

o:

```text
Spread
=
5 bps
```

frente a:

```text
Spread
=
180 bps
```

o:

```text
Broker operativo
```

frente a:

```text
Broker desconectado
```

El mercado no ha cambiado.

El evento tampoco.

Lo que ha cambiado es la capacidad real del sistema para ejecutar una decisión.

Por ello, `Execution State` no existe para describir el mercado.

Existe para describir las condiciones observables bajo las que una decisión podría ejecutarse.

Por tanto:

```text
Market State
=
¿cómo estaba el mercado?
```

```text
Event State
=
¿cómo estaba el mercado
respecto a un evento?
```

```text
Execution State
=
¿cómo podía ejecutarse
una decisión
en ese instante?
```

Esa es la única razón por la que `Execution State` existe.
````


````md id="y3vx7k"
## ¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableció que un sistema de aprendizaje exitoso deba contener una representación denominada `Execution State`.

AlphaGo, AlphaGo Zero y MuZero aprenden sobre una representación del estado desde la que posteriormente estiman política, valor, recompensa o dinámica.

La ejecución de una acción pertenece al entorno donde esos sistemas operan, no a la representación del estado en sí.

Por tanto, la conclusión rigurosa es:

```text
Execution State NO procede de DeepMind.

Sí implementa un principio compatible
con sus sistemas de aprendizaje:

representar explícitamente
toda la información observable
necesaria para que una decisión
pueda ejecutarse correctamente.
```

En TSIS, `Execution State` desempeña precisamente ese papel.

No representa el mercado.

No representa el evento.

Representa las condiciones reales de ejecución existentes en un `decision_timestamp`.

La certificación correcta es:

```text
Execution State
=
decisión arquitectónica propia de TSIS.

Representación explícita
de las condiciones de ejecución
=
principio compatible con DeepMind.

Garantía de éxito por existir
=
ninguna.
```

La utilidad de `Execution State` dependerá de que preserve correctamente:

```text
la capacidad observable de ejecución;
las restricciones existentes;
la legalidad temporal;
la separación entre decisión y resultado;
la ausencia de leakage.
```

No dependerá simplemente de materializar una tabla adicional.
````


## `Execution State` consume `Market State` y `Event State`

`Execution State` no comienza en el mercado.

Tampoco comienza en un evento.

Ambos ya han sido representados previamente.

`Execution State` comienza cuando el sistema necesita conocer si una decisión puede ejecutarse realmente.

La cadena correcta es:

```
Market State
↓
Event State
(opcional)
↓
Execution State
```

No:

```
Mercado
↓
Execution State
```

Ni:

```
Evento
↓
Execution State
```

Supongamos el siguiente ejemplo.

```
MARKET STATE

- instrument_id = ABCD
- decision_timestamp = 09:42:00
```

y, si existe:

```
EVENT STATE

- event_id = E123
- decision_timestamp = 09:42:00
```

A partir de ese conocimiento, `Execution State` incorpora únicamente las condiciones observables de ejecución.

Por ejemplo:

```
locate_available

locate_cost

observable_spread

observable_depth

expected_slippage

broker_status

routing_status

execution_restrictions

market_session

halt_status
```

La diferencia conceptual es:

```
Market State

- describe el mercado.
```

```
Event State

- describe el mercado respecto a un evento.
```

```
Execution State

- describe la capacidad observable
de ejecutar una decisión.
```

Por tanto, `Execution State` no modifica el mercado.

No modifica el evento.

Únicamente añade el contexto operativo necesario para evaluar si una decisión podría ejecutarse bajo las condiciones observables existentes en ese instante.

````md id="a7mk4p"
## Arquitectura

La arquitectura de `Execution State` sigue una dirección distinta a la de `Market State` y `Event State`.

No comienza en el mercado.

No comienza en los fenómenos.

No comienza en los Objetos de Información.

No comienza en un evento.

Todo eso ya ha sido resuelto previamente.

`Execution State` comienza cuando existe una decisión potencial cuya capacidad de ejecución debe evaluarse.

```
MARKET STATE
↓
EVENT STATE
(opcional)
↓
CAPACIDAD DE EJECUCIÓN
↓
EXECUTION STATE BUILDER
↓
EXECUTION STATE
```

Cada nivel responde a una pregunta distinta.

```
MARKET STATE

¿Cómo estaba el mercado?
```

↓

```
EVENT STATE

¿Cómo estaba el mercado
respecto al evento?
```

↓

```
CAPACIDAD DE EJECUCIÓN

¿Qué condiciones reales
de ejecución existían?
```

↓

```
EXECUTION STATE BUILDER

¿Cómo construimos legalmente
esa representación?
```

↓

```
EXECUTION STATE

¿Cuál era la capacidad observable
de ejecutar una decisión
en t?
```

La dirección nunca debería invertirse.

No debería ocurrir:

```
Tengo un broker.
↓
Voy a representar el mercado.
```

Ni tampoco:

```
Tengo unos costes.
↓
Crearé un Execution State.
```

La dirección correcta siempre es:

```
Existe un Market State.
↓
Existe opcionalmente un Event State.
↓
Se observan las condiciones reales
de ejecución.
↓
El Builder incorpora únicamente
ese contexto operativo.
↓
Se obtiene un único Execution State.
```

Por ello, `Execution State` no necesita volver a representar el mercado.

El mercado ya está representado.

Lo único que añade es la representación de las condiciones observables bajo las que una decisión podría ejecutarse.

La estabilidad de `Execution State` depende precisamente de mantener esa separación.

`Market State` puede evolucionar.

`Event State` puede evolucionar.

Los brokers pueden cambiar.

Las políticas de routing pueden cambiar.

Los costes pueden cambiar.

Pero mientras permanezcan estables:

```text
la identidad del Market State;
la identidad del Event State;
la definición de las condiciones de ejecución;
las reglas temporales;
las políticas de observabilidad;
```

`Execution State` seguirá representando exactamente el mismo conocimiento científico sobre la capacidad de ejecución del sistema.
````


````md id="k5vq2n"
### `Execution State Builder`

El `Execution State Builder` materializa la representación canónica del estado observable de ejecución.
No decide si debe ejecutarse una operación.
No envía órdenes.
No selecciona estrategias.
No interpreta el mercado.
Su responsabilidad consiste únicamente en ejecutar el contrato de representación aprobado para `Execution State`.

Ese contrato declara qué información adicional debe incorporarse para describir las condiciones reales de ejecución.

Por ejemplo:

```
EXECUTION STATE REPRESENTATION CONTRACT

required_components

- Market State
- Event State (opcional)
- Execution Context
```

A partir de esa declaración, el Builder realiza una secuencia completamente gobernada.

```
Execution State Builder
↓
Lee el contrato de representación.
↓
Obtiene el Market State correspondiente.
↓
Obtiene el Event State
(si existe).
↓
Recupera las condiciones observables
de ejecución.
↓
Valida cobertura,
calidad,
temporalidad
y restricciones.
↓
Materializa el Execution State.
```

El Builder nunca realiza preguntas del tipo:

```
¿Qué orden debo enviar?
```

Siempre trabaja en sentido descendente:

```
¿Qué Execution State debo construir?
```

↓

```
¿Qué Market State necesita?
```

↓

```
¿Existe un Event State asociado?
```

↓

```
¿Qué condiciones observables
de ejecución debo incorporar?
```

↓

```
¿Es legal construirlo
en ese decision_timestamp?
```

El Builder nunca modifica el mercado.

Nunca modifica el evento.

Únicamente incorpora información observable sobre la capacidad de ejecución.

Por ejemplo:

```
locate_available

locate_cost

observable_spread

observable_depth

expected_slippage

broker_status

routing_status

execution_restrictions

market_session

halt_status
```

Cada uno de esos componentes posee su propia política de observabilidad.

El Builder únicamente ejecuta dichas políticas.

Nunca las redefine.

El resultado es una representación contextualizada de la capacidad observable de ejecución.

Por ello, el `Execution State Builder` integra únicamente:

```text
un Market State válido;
un Event State válido cuando exista;
condiciones observables de ejecución;
restricciones operativas vigentes.
```

Nunca incorpora:

```text
órdenes ejecutadas;
fills;
beneficios;
pérdidas;
información posterior;
variables con leakage.
```

Su resultado no constituye una decisión.

Constituye la representación del entorno operativo bajo el que una decisión podría ejecutarse.
````


````md id="r9xp3m"
### `Execution State`

La necesidad de construir una representación del estado de ejecución surge directamente de las preguntas científicas que TSIS pretende responder.
Una vez construida esa representación, los distintos consumidores reutilizan exactamente el mismo `Execution State`.

Ejemplos de preguntas científicas.

```text
PREGUNTA CIENTÍFICA

¿Era posible ejecutar
esta decisión
en ese instante?

↓

NECESIDAD DE INFORMACIÓN

Conocer las condiciones
observables de ejecución.

↓

REPRESENTACIÓN REQUERIDA

Execution State
```

```text
PREGUNTA CIENTÍFICA

¿El coste observable
hacía inviable la operación?

↓

NECESIDAD DE INFORMACIÓN

Conocer el entorno operativo
existente en t.

↓

REPRESENTACIÓN REQUERIDA

Execution State
```

```text
PREGUNTA CIENTÍFICA

¿Dos situaciones con el mismo
Market State producían decisiones
operativamente distintas?

↓

NECESIDAD DE INFORMACIÓN

Comparar condiciones reales
de ejecución.

↓

REPRESENTACIÓN REQUERIDA

Execution State
```

El diseño científico es quien razona:

```text
Para responder estas preguntas,
el sistema necesita representar
las condiciones observables
de ejecución.
```

Posteriormente esa decisión queda formalizada en un contrato.

```text
EXECUTION STATE REPRESENTATION CONTRACT

required_components

- Market State
- Event State (opcional)
- Execution Context
```

El Builder recibe ese contrato y lo ejecuta.

```text
Execution State Builder

1. Lee el contrato.
2. Obtiene el Market State.
3. Obtiene el Event State si existe.
4. Recupera el contexto de ejecución.
5. Valida cobertura, calidad y temporalidad.
6. Materializa la fila de Execution State.
```

La separación exacta queda:

```text
Gobernanza científica
=
decide qué conocimiento
de ejecución
debe preservarse.

Contrato de Execution State
=
declara qué componentes
deben integrarse.

Execution State Builder
=
ejecuta esa declaración.

Execution State
=
resultado materializado.
```

Por ello, `Execution State` no depende de un broker concreto.
No depende de un algoritmo de ejecución.
No depende de una estrategia.
Depende únicamente del contrato científico que define cómo debe representarse la capacidad observable de ejecución.

Ese contrato constituye la definición canónica de `Execution State`.

Todos los consumidores posteriores reutilizan esa misma representación.

Nunca construyen un `Execution State` distinto para cada investigación.
````

````md id="x2vn7m"
### ¿Quién necesita que exista `Execution State`?

`Execution State` no existe por sí mismo.
Tampoco existe porque exista un broker.
Existe porque distintos consumidores necesitan conocer las condiciones reales bajo las que una decisión podría ejecutarse.

Por ejemplo:

```
MARKET STATE

ABCD
09:42:00
```

¿Por qué necesitamos `Execution State`?

Porque dos decisiones pueden compartir exactamente el mismo `Market State` y, sin embargo, poseer capacidades de ejecución completamente distintas.

No porque exista una variable llamada:

```
locate_cost
```

Ni porque exista una tabla llamada:

```
execution_state_table
```

Sino porque múltiples consumidores necesitan reutilizar exactamente la misma representación de las condiciones observables de ejecución.

Por ejemplo:

```text
Execution State

Lo necesitan:

- Backtesting
- Execution Research
- Outcome Research
- Policy Learning
- Offline RL
```

Cada consumidor puede utilizar una parte distinta de la representación.

Pero todos parten del mismo `Execution State`.

Nunca deberían construir una representación distinta de las mismas condiciones de ejecución.

La cadena completa queda cerrada así:

```
PREGUNTAS CIENTÍFICAS
↓
MARKET STATE
↓
EVENT STATE
(opcional)
↓
CONDICIONES DE EJECUCIÓN
↓
EXECUTION STATE BUILDER
↓
EXECUTION STATE
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
MARKET STATE

¿Cómo estaba el mercado?
```

↓

```
EVENT STATE

¿Cómo estaba el mercado
respecto al evento?
```

↓

```
CONDICIONES DE EJECUCIÓN

¿Qué capacidad real
existía para ejecutar?
```

↓

```
EXECUTION STATE BUILDER

¿Cómo construimos legalmente
esa representación?
```

↓

```
EXECUTION STATE

¿Cuál era la capacidad observable
de ejecución
en t?
```

↓

```
CONSUMIDORES

¿Cómo reutiliza cada consumidor
esa representación?
```

Esta dirección nunca debería invertirse.

Los consumidores no definen `Execution State`.

Únicamente lo reutilizan.

Del mismo modo, el broker no define `Execution State`.

Únicamente constituye una fuente de evidencia sobre determinadas condiciones de ejecución.

Y `Market State` tampoco cambia.

Únicamente constituye la representación base sobre la que `Execution State` incorpora el contexto operativo.

Por ello, la arquitectura permanece estable incluso cuando:

```text
cambian los brokers;
cambian los costes;
cambian las rutas;
cambian los modelos de ejecución;
```

Mientras permanezcan estables:

```text
la identidad del Market State;
la definición de las condiciones de ejecución;
las reglas temporales;
el contrato de Execution State;
```

`Execution State` seguirá representando exactamente el mismo conocimiento científico sobre la capacidad observable de ejecutar una decisión.
````


````md id="e4qt8n"
### Representaciones de investigaciones y ejecución

Si `Execution State` constituye la representación canónica del estado observable de ejecución,

entonces únicamente debería existir una definición canónica de esa representación.

```
Execution State

=

La mejor representación observable
de las condiciones de ejecución
en un decision_timestamp.
```

Lo que sí puede cambiar es la proyección que hace cada consumidor sobre esa representación.

Por tanto, TSIS debería mantener una única representación canónica:

```
execution_state_table
```

y posteriormente construir datasets derivados específicos para cada investigación.

Por ejemplo:

```
execution_cost_research_dataset

slippage_research_dataset

routing_research_dataset

execution_quality_dataset

...
```

Esos datasets no redefinen `Execution State`.

Simplemente seleccionan las filas necesarias para estudiar un determinado aspecto de la ejecución.

Ejemplo.

Supongamos una investigación sobre:

```
Coste observable
de ejecución
```

Cada decisión potencial posee un único contexto de ejecución.

```
decision_timestamp

↓

Execution State
```

El sistema no crea una representación distinta para cada estrategia.

Recupera el `Execution State` correspondiente a ese instante.

Del mismo modo, distintos algoritmos pueden necesitar subconjuntos diferentes del mismo `Execution State`.

Por ejemplo:

```
Execution State

│

├── Market State

├── Event State
(opcional)

├── Execution Context

└── ...
```

Entonces:

```
Backtesting

↓

consume

un subconjunto
```

```
Execution Research

↓

consume

otro subconjunto
```

```
Policy Learning

↓

consume

otro subconjunto diferente
```

Todos ellos reutilizan exactamente el mismo `Execution State`.

Nunca construyen una representación distinta de las mismas condiciones de ejecución.

La arquitectura queda:

```
Execution State
↓
Feature Selector
↓
Dataset Backtesting
```

---

```
Execution State
↓
Feature Selector
↓
Dataset Execution Research
```

---

```
Execution State
↓
Feature Selector
↓
Dataset Policy Learning
```

Cada dataset derivado constituye una proyección sobre la representación canónica.

Nunca una representación alternativa del mismo estado de ejecución.

Por ello:

```text
Canonicalidad

=

una única definición
de las condiciones observables
de ejecución.
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

TSIS evita crear múltiples definiciones incompatibles del mismo entorno de ejecución.

Todos los consumidores parten siempre del mismo `Execution State`.

Lo único que cambia es la parte de esa representación que cada uno decide utilizar.
````


````md id="k7mv2r"
### ¿Se materializa una fila para cada `decision_timestamp`?

Depende del grano definido para la representación.

La definición canónica de `Execution State` no obliga a una resolución física concreta.

Únicamente exige que toda representación responda a la misma pregunta:

```text
¿Cuál era la capacidad observable
de ejecutar una decisión
en el decision_timestamp t?
```

Por ejemplo.

Si el grano canónico adoptado es:

```
instrument_id
+
decision_timestamp
```

podrá existir una representación para cada instante donde la ejecución sea evaluable.

Si la investigación requiere una resolución mayor:

```
instrument_id
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
execution_state_1m

execution_state_1s

execution_state_tick_window
```

Todas ellas representan exactamente el mismo `Execution State`.

Lo único que cambia es la resolución física utilizada para construir la representación.

Todas deben respetar la misma semántica:

```text
condiciones observables
de ejecución
legalmente disponibles
en el decision_timestamp.
```

La resolución nunca modifica el significado.

Únicamente modifica el nivel de detalle con el que dicho significado queda materializado.

### Arquitectura práctica recomendable

La construcción práctica de `Execution State` puede entenderse como la siguiente secuencia.

```
CONTRATO CANÓNICO DE EXECUTION STATE
↓
define:
- semántica
- relación con Market State
- relación con Event State
- contexto de ejecución
- reglas temporales
↓
EXECUTION STATE BUILDER
↓
recupera el Market State
↓
recupera el Event State
(si existe)
↓
incorpora el contexto de ejecución
↓
valida
↓
materializa
↓
EXECUTION STATE STORE
↓
es reutilizado por los consumidores
```

El almacenamiento no constituye la definición de `Execution State`.

Simplemente conserva representaciones ya construidas y validadas para evitar reconstrucciones innecesarias.

### ¿Se guardan los `Execution State` ya construidos?

Sí.

Una vez construido y validado un `Execution State`, resulta razonable conservarlo para permitir su reutilización posterior.

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
execution_state/
    version=v0_1/
        year=2026/
            month=07/
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
- ejecución detallada;
- materialización bajo demanda.
```

```
3.

Datasets derivados

- específicos para investigación;
- específicos para algoritmos;
- no constituyen Execution State canónico.
```

La canonicidad reside en:

```
la definición;
el contrato;
la semántica;
la relación con Market State;
la relación con Event State;
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

seguirán representando exactamente el mismo `Execution State`.
````


````md id="n5qx8r"
### `Execution State` no debe convertirse en una mega-tabla universal

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

Ese no es el objetivo de `Execution State`.

Convertiría la representación canónica en una unión ilimitada de necesidades downstream.

Cada nuevo consumidor añadiría nuevas columnas.

Cada nueva investigación ampliaría la representación.

Cada nuevo algoritmo modificaría la definición de `Execution State`.

La consecuencia sería que el propio concepto de `Execution State` dejaría de ser estable.

Por ello, la canonicidad no debe definirse por la cantidad de variables que contiene una fila.

Debe definirse por la estabilidad de su semántica.

La regla correcta es:

```text
Canonicalidad
=
una única semántica del estado de ejecución
+
un único identificador lógico
+
una única relación con Market State
+
una única relación con Event State
+
reglas temporales comunes
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
execution_state_core
execution_state_execution_context
execution_state_microstructure_extension
execution_state_cost_extension
```

Todos ellos representan exactamente el mismo `Execution State`.

Lo único que cambia es el perfil físico utilizado para materializar la representación.

Todos los perfiles deben poder relacionarse mediante una identidad común.

Por ejemplo:

```text
execution_state_id
market_state_id
event_state_id
decision_timestamp
representation_profile_version
```

El perfil `core` debería contener únicamente la información mínima gobernada necesaria para describir correctamente las condiciones observables de ejecución.

Las extensiones especializadas permanecen separadas.

Solo se incorporan cuando:

```text
el contrato lo permite;
el perfil lo requiere;
la política temporal lo autoriza;
la investigación realmente las necesita.
```

De este modo, un consumidor que únicamente necesite conocer el contexto básico de ejecución no tendrá que cargar información microestructural detallada.

Y una investigación sobre slippage o profundidad del mercado no obligará a que todos los `Execution State` incorporen permanentemente cientos de variables adicionales.

La canonicidad permanece única.

La materialización permanece modular.

Por ello, la definición correcta de `Execution State` no es:

```text
La mayor tabla posible.
```

Sino:

```text
La representación canónica
de las condiciones observables
de ejecución,
capaz de materializarse mediante distintos perfiles físicos compatibles,
sin alterar su significado científico.
```


## Conclusión

`Execution State` constituye la representación canónica de las condiciones observables de ejecución dentro de TSIS.

Su misión no consiste en decidir.

No consiste en enviar órdenes.

No consiste en ejecutar estrategias.

No consiste en optimizar costes.

No consiste en predecir resultados.

Su misión consiste únicamente en preservar, de forma gobernada, el conocimiento observable sobre la capacidad real del sistema para ejecutar una decisión en un `decision_timestamp`.

La arquitectura completa queda definida por una única dirección conceptual.

```
PREGUNTAS CIENTÍFICAS
↓
MARKET STATE
↓
EVENT STATE
(opcional)
↓
CONDICIONES DE EJECUCIÓN
↓
EXECUTION STATE BUILDER
↓
EXECUTION STATE
```

Cada capa responde a una pregunta distinta.

```
PREGUNTAS CIENTÍFICAS
↓
¿Qué queremos investigar?
```

↓

```
MARKET STATE
↓
¿Cómo estaba el mercado?
```

↓

```
EVENT STATE
↓
¿Cómo estaba el mercado
respecto al evento?
```

↓

```
CONDICIONES DE EJECUCIÓN
↓
¿Qué capacidad observable
existía para ejecutar?
```

↓

```
EXECUTION STATE BUILDER
↓
¿Cómo construimos legalmente
esa representación?
```

↓

```
EXECUTION STATE
↓
¿Cuál era la capacidad observable
de ejecución
en t?
```

Cada una de esas capas puede evolucionar sin romper las demás.

Por ello:

```text
los brokers pueden cambiar;
las rutas pueden cambiar;
los costes pueden cambiar;
las implementaciones físicas pueden cambiar;
```

Sin embargo, mientras permanezcan estables:

```text
la identidad del Market State;
la identidad del Event State;
el contrato de representación;
las reglas temporales;
las políticas de observabilidad;
```

`Execution State` seguirá representando exactamente el mismo conocimiento científico.

La representación canónica no pertenece a un broker concreto.

No pertenece a una plataforma.

No pertenece a una estrategia.

Pertenece al entorno observable de ejecución.

Todos los consumidores posteriores deben partir de esa misma representación.

Posteriormente podrán aparecer otras capas especializadas que reutilicen ese estado para responder preguntas diferentes.

Por ejemplo:

```text
Outcome

↓

¿Qué ocurrió
después?
```

Pero ninguna de ellas redefine las condiciones de ejecución.

Todas parten del mismo `Execution State`.

Por ello, `Execution State` constituye la representación canónica del conocimiento observable sobre la capacidad real del sistema para ejecutar una decisión y el puente natural entre el conocimiento del mercado y la evaluación posterior de sus resultados.






