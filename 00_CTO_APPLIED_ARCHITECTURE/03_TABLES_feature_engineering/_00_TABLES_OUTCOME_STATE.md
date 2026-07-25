# Arquitectura de construcción de `Outcome`

## Propósito

Este documento define cómo TSIS construye la representación canónica del resultado observable de una decisión o de una investigación.

`Outcome` no constituye una representación del mercado.

Tampoco constituye una representación de un evento.

Tampoco constituye una representación de la ejecución.

Representa únicamente aquello que ocurrió después.

`Outcome` parte siempre de representaciones previamente construidas.

Depende de:

```text
Market State
```

y, cuando exista:

```text
Event State
```

y:

```text
Execution State
```

La representación obtenida podrá materializarse posteriormente mediante:

```text
outcome_table
```

o mediante los perfiles físicos autorizados para `Outcome`.

Sin embargo, este documento describe exclusivamente su arquitectura conceptual, no su implementación física, su materialización ni su ejecución.

## ¿Qué es `Outcome`?

`Outcome` es la representación canónica del resultado observable posterior a un `decision_timestamp`.

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
la capacidad de ejecución
```

Representa únicamente:

```text
lo que ocurrió
después del decision_timestamp.
```

Su identidad conceptual es:

**Outcome** = *qué ocurrió después de una decisión o de una observación.*

Su grano semántico es:

```text
clave ≈ decision_id + outcome_definition
```

Toda la información contenida en un `Outcome` debe cumplir simultáneamente:

```text
• ser posterior al decision_timestamp;
• estar correctamente definida por una política temporal;
• no utilizarse como input predictivo;
• ser reproducible;
• conservar su trazabilidad.
```

Por tanto, `Outcome` responde únicamente a una pregunta científica:

```text
¿Qué ocurrió
después?
```

No responde:

```text
¿Cómo estaba el mercado?
¿Cómo estaba el mercado respecto a un evento?
¿Cómo podía ejecutarse una decisión?
```

Esas preguntas pertenecen respectivamente a:

```text
Market State
Event State
Execution State
```

Por ello:

```text
Market State
=
conocimiento observable.
```

```text
Event State
=
conocimiento observable
respecto a un evento.
```

```text
Execution State
=
capacidad observable
de ejecución.
```

```text
Outcome
=
resultado posterior.
```

`Outcome` nunca debe incorporarse como parte del estado observable.

Su separación constituye una de las principales garantías contra el leakage temporal.


## ¿Por qué existe `Outcome`?

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

`Execution State` responde a una tercera:

```text
¿Qué capacidad real tenía el sistema
para ejecutar una decisión
en ese instante?
```

Sin embargo, ninguna de esas representaciones responde a la última pregunta del proceso.

```text
¿Qué ocurrió
después?
```

Toda investigación termina necesitando conocer el resultado posterior.

Por ejemplo:

```text
¿El movimiento continuó?
```

o:

```text
¿Se alcanzó el objetivo?
```

o:

```text
¿Cuál fue el MFE?
```

o:

```text
¿Cuál fue el MAE?
```

o:

```text
¿Cuál fue el retorno
después de 5 minutos?
```

Todas esas preguntas poseen una característica común.

No describen información observable en el `decision_timestamp`.

Describen únicamente aquello que ocurrió posteriormente.

Por ello, `Outcome` no existe para representar el mercado.

Tampoco existe para representar eventos.

Tampoco existe para representar ejecución.

Existe únicamente para representar el resultado posterior de una observación, una decisión o una investigación.

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
respecto al evento?
```

```text
Execution State
=
¿cómo podía ejecutarse
una decisión?
```

```text
Outcome
=
¿qué ocurrió
después?
```

Esa es la única razón por la que `Outcome` existe.


## ¿Esto reproduce demostrablemente el proceso de DeepMind?

**No en el sentido literal.**

DeepMind no estableció que un sistema de aprendizaje exitoso deba contener una representación denominada `Outcome`.

AlphaGo, AlphaGo Zero y MuZero aprenden utilizando objetivos posteriores como política, valor o recompensa, pero esos resultados no forman parte del estado observable desde el que se toma una decisión.

Por tanto, la conclusión rigurosa es:

```text
Outcome NO procede de DeepMind.

Sí implementa un principio compatible
con sus sistemas de aprendizaje:

mantener completamente separado
el estado observable
del resultado posterior.
```

En TSIS, `Outcome` desempeña precisamente ese papel.

No representa el mercado.

No representa el evento.

No representa la ejecución.

Representa únicamente aquello que ocurrió después del `decision_timestamp`.

La certificación correcta es:

```text
Outcome
=
decisión arquitectónica propia de TSIS.

Representación explícita
del resultado posterior
=
principio compatible con DeepMind.

Garantía de éxito por existir
=
ninguna.
```

La utilidad de `Outcome` dependerá de que preserve correctamente:

```text
la definición del resultado;
la política temporal utilizada;
la trazabilidad;
la separación entre input y resultado;
la ausencia de leakage.
```

No dependerá simplemente de materializar una tabla adicional.



## `Outcome` consume `Market State`, `Event State` y `Execution State`

`Outcome` no comienza en el mercado.

No comienza en un evento.

No comienza en la ejecución.

Todo eso ya ha sido representado previamente.

`Outcome` comienza cuando existe una observación cuya evolución posterior debe medirse.

La cadena correcta es:

```
Market State
↓
Event State
(opcional)
↓
Execution State
(opcional)
↓
Outcome
```

No:

```
Mercado
↓
Outcome
```

Ni:

```
Evento
↓
Outcome
```

Ni:

```
Ejecución
↓
Outcome
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

y, si existe:

```
EXECUTION STATE

- decision_timestamp = 09:42:00
```

A partir de esas representaciones, `Outcome` incorpora únicamente información posterior.

Por ejemplo:

```
mfe

mae

holding_time

exit_timestamp

exit_price

return

stop_hit

target_hit

timeout

final_status
```

La diferencia conceptual es:

```
Market State

- describe el mercado.
```

```
Event State

- describe el mercado
respecto a un evento.
```

```
Execution State

- describe la capacidad
de ejecutar una decisión.
```

```
Outcome

- describe únicamente
lo que ocurrió después.
```

Por tanto, `Outcome` nunca modifica el mercado.

Nunca modifica el evento.

Nunca modifica la ejecución.

Únicamente representa el resultado posterior asociado a esas representaciones.

La separación entre:

```text
State
```

y:

```text
Outcome
```

constituye una de las reglas fundamentales de TSIS.

Toda información utilizada como input debe pertenecer a:

```text
Market State

Event State

Execution State
```

Toda información posterior pertenece exclusivamente a:

```text
Outcome
```

Nunca al contrario.

## Arquitectura

La arquitectura de `Outcome` sigue una dirección distinta a la de `Market State`, `Event State` y `Execution State`.

No comienza en el mercado.

No comienza en un evento.

No comienza en la ejecución.

Todo eso ya ha sido representado previamente.

`Outcome` comienza cuando existe una observación cuya evolución posterior debe medirse.

```
MARKET STATE
↓
EVENT STATE
(opcional)
↓
EXECUTION STATE
(opcional)
↓
OUTCOME POLICY
↓
OUTCOME BUILDER
↓
OUTCOME
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
EXECUTION STATE

¿Cómo podía ejecutarse
una decisión?
```

↓

```
OUTCOME POLICY

¿Qué resultado
queremos medir?
```

↓

```
OUTCOME BUILDER

¿Cómo calculamos legalmente
ese resultado?
```

↓

```
OUTCOME

¿Qué ocurrió
después?
```

La dirección nunca debería invertirse.

No debería ocurrir:

```
Tengo un MFE.
↓
Voy a reconstruir el mercado.
```

Ni tampoco:

```
Tengo un beneficio.
↓
Crearé un Outcome.
```

La dirección correcta siempre es:

```
Existe un Market State.
↓
Existe opcionalmente un Event State.
↓
Existe opcionalmente un Execution State.
↓
Se aplica una política
de Outcome.
↓
El Builder calcula
el resultado.
↓
Se obtiene un único Outcome.
```

Por ello, `Outcome` no necesita volver a representar el mercado.

El mercado ya está representado.

El evento ya está representado.

La ejecución ya está representada.

Lo único que añade es la medición del resultado posterior.

La estabilidad de `Outcome` depende precisamente de mantener esa separación.

`Market State` puede evolucionar.

`Event State` puede evolucionar.

`Execution State` puede evolucionar.

Las políticas de Outcome pueden evolucionar.

Pero mientras permanezcan estables:

```text
la identidad del Market State;
la identidad del Event State;
la identidad del Execution State;
la definición del Outcome;
las reglas temporales;
```

`Outcome` seguirá representando exactamente el mismo conocimiento científico sobre lo ocurrido después del `decision_timestamp`.



````md id="r4zk8m"
## `Outcome Builder`

El `Outcome Builder` es el componente responsable de construir la representación canónica de `Outcome`.

Su misión no consiste en analizar estrategias.

No consiste en decidir entradas.

No consiste en optimizar parámetros.

No consiste en generar señales.

Su única responsabilidad es transformar una definición formal de `Outcome` en una representación reproducible del resultado posterior.

La dirección es siempre la misma.

```
Market State
↓
Event State
(opcional)
↓
Execution State
(opcional)
↓
Outcome Policy
↓
Outcome Builder
↓
Outcome
```

El `Outcome Builder` nunca decide qué debe medirse.

Esa responsabilidad pertenece a la política de definición del resultado.

Por ejemplo:

```text
Return_5m

Return_30m

MFE

MAE

Target_Hit

Stop_Hit

VWAP_Reached

HOD_Broken

Holding_Time

Gap_Closed
```

Cada una constituye una definición distinta de `Outcome`.

Una vez definida esa política, el `Outcome Builder` únicamente debe calcularla de forma reproducible.

Su proceso conceptual puede resumirse como:

```
Representaciones previas
↓
Validación temporal
↓
Aplicación de la política
↓
Cálculo del resultado
↓
Materialización
```

Durante ese proceso el Builder puede consultar cualquier información posterior autorizada por la política temporal correspondiente.

Por ejemplo:

```text
barras posteriores

trades posteriores

quotes posteriores

halts posteriores

eventos posteriores
```

Pero toda esa información posee una restricción fundamental.

Nunca puede reutilizarse posteriormente como información observable del estado.

Es decir:

```
Outcome
→
NO vuelve
a Market State.
```

```
Outcome
→
NO vuelve
a Event State.
```

```
Outcome
→
NO vuelve
a Execution State.
```

La información posterior únicamente existe para describir el resultado.

Nunca para reconstruir el estado desde el cual se tomó una decisión.

Por ello, el `Outcome Builder` constituye la frontera temporal de TSIS.

A partir del `decision_timestamp`, el sistema deja de construir representaciones del estado y comienza a construir representaciones del resultado.

Mantener esa frontera perfectamente definida garantiza que cualquier investigación posterior pueda reproducirse sin introducir contaminación temporal ni leakage entre los datos de entrada y los resultados observados.
````


## ¿Quién necesita `Outcome`?

`Outcome` constituye la última representación canónica del flujo científico de TSIS.

No describe el estado observable.

Describe las consecuencias observables posteriores.

Por ello, todos los sistemas cuya finalidad sea evaluar, comparar, descubrir o aprender a partir de resultados deben consumir `Outcome`.

Nunca deberían reconstruirlo.

La dirección correcta siempre es:

```
Market State
↓
Event State
(opcional)
↓
Execution State
(opcional)
↓
Outcome
↓
Consumidores
```

Los principales consumidores son:

```text
Outcome Research
```

para estudiar qué resultados aparecen con mayor frecuencia bajo determinadas condiciones.

```text
Pattern Discovery
```

para descubrir patrones asociados a determinados resultados.

```text
Machine Learning
```

para aprender relaciones entre estados observables y resultados posteriores.

```text
Prediction Models
```

para estimar probabilidades futuras sin incorporar información posterior al instante de decisión.

```text
Policy Learning
```

para comparar distintas políticas utilizando exactamente los mismos resultados observados.

```text
Offline Reinforcement Learning
```

para aprender políticas a partir de transiciones completas:

```
State

↓

Action

↓

Outcome
```

```text
AlphaEvolve
```

para explorar automáticamente nuevas hipótesis, políticas o reglas utilizando métricas objetivas obtenidas de `Outcome`.

```text
Backtesting
```

para evaluar estrategias sobre resultados perfectamente reproducibles.

```text
Statistical Validation
```

para calcular métricas de robustez, estabilidad, significación y capacidad predictiva.

Todos esos consumidores comparten una característica.

No vuelven a calcular el resultado.

Utilizan exactamente la misma representación de `Outcome`.

Gracias a ello:

```text
dos investigadores;

dos modelos;

dos algoritmos;

dos estrategias;
```

pueden comparar sus resultados utilizando exactamente la misma definición del fenómeno observado.

La representación del resultado permanece estable.

Únicamente cambian las preguntas científicas formuladas sobre ella.

Por ello, `Outcome` constituye la fuente de verdad para todo el conocimiento posterior derivado de los resultados observados.

Ningún consumidor debería redefinir qué ocurrió.

Todos deben partir del mismo `Outcome`.


````md id="n2wp7c"
## Representaciones derivadas

`Outcome` constituye la representación canónica del resultado observado.

Sin embargo, no todos los consumidores necesitan exactamente la misma representación física.

Por ello, TSIS distingue entre:

```text
representación canónica
```

y:

```text
representaciones derivadas.
```

La representación canónica responde siempre a una única pregunta:

```text
¿Qué ocurrió
después?
```

Las representaciones derivadas responden a preguntas particulares formuladas por distintos procesos de investigación.

Por ejemplo:

```
Outcome

↓

Classification Dataset
```

para problemas de clasificación.

```
Outcome

↓

Regression Dataset
```

para estimar magnitudes continuas.

```
Outcome

↓

Survival Dataset
```

para estudiar tiempos hasta un determinado resultado.

```
Outcome

↓

RL Dataset
```

para construir transiciones:

```
State

↓

Action

↓

Reward

↓

Next State
```

```
Outcome

↓

Research Dataset
```

para investigaciones estadísticas específicas.

```
Outcome

↓

Validation Dataset
```

para procesos de validación científica.

Todas estas representaciones tienen una propiedad común.

Nunca redefinen el resultado.

Únicamente reorganizan la información ya representada en `Outcome`.

Por ello:

```
Outcome

↓

Representación derivada
```

es correcto.

Mientras que:

```
Representación derivada

↓

Nuevo Outcome
```

no lo es.

La representación canónica permanece única.

Las representaciones derivadas únicamente cambian el formato, la estructura o el propósito con el que ese conocimiento será utilizado posteriormente.

Gracias a ello, distintos modelos pueden trabajar sobre estructuras diferentes sin alterar la definición oficial del resultado observado.

El conocimiento permanece estable.

Únicamente cambia su representación para un consumidor concreto.
````

## Materialización

`Outcome` constituye una representación canónica.

Sin embargo, esa representación no implica una única implementación física.

Al igual que ocurre con `Market State`, `Event State` y `Execution State`, la representación conceptual permanece independiente de la forma en que finalmente se almacena.

La relación es:

```
Outcome

↓

Modelo de Representación

↓

Variables

↓

Tablas

↓

Materialización Física
```

No:

```
Tabla

↓

Outcome
```

La representación siempre existe antes que su implementación física.

Por ello, un mismo `Outcome` puede materializarse mediante distintos perfiles autorizados.

Por ejemplo:

```text
outcome_core
```

para la representación mínima compartida.

```text
outcome_intraday
```

para resultados definidos sobre ventanas intradía.

```text
outcome_daily
```

para investigaciones sobre horizontes diarios.

```text
outcome_execution
```

para estudios centrados en la calidad de ejecución.

```text
outcome_research
```

para investigaciones experimentales autorizadas.

Todos esos perfiles representan exactamente el mismo concepto.

Lo único que cambia es:

```text
el conjunto de variables;

el horizonte temporal;

el nivel de detalle;

la finalidad de investigación.
```

La identidad de `Outcome` permanece inalterada.

La materialización física únicamente adapta esa representación a un determinado contexto operativo o científico.

Por ello, la implementación física nunca debería modificar:

```text
la definición del Outcome;

la política temporal;

la trazabilidad;

la reproducibilidad;

la separación entre estado y resultado.
```

Esas propiedades pertenecen a la representación canónica.

Las tablas únicamente constituyen el mecanismo mediante el cual dicha representación queda persistida para su utilización posterior.

## `Outcome` no debe convertirse en una mega-tabla

El hecho de que `Outcome` represente el resultado posterior no implica que deba contener todas las métricas posibles en una única estructura física.

Una mega-tabla presenta los mismos problemas que en el resto de representaciones:

```text
crecimiento descontrolado;

campos sin utilizar;

dependencias innecesarias;

mayor coste de mantenimiento;

dificultad para evolucionar;

menor reutilización.
```

Por ello, la representación canónica debe permanecer independiente de su implementación física.

Diferentes investigaciones pueden requerir perfiles distintos de `Outcome`.

Por ejemplo:

```text
outcome_core
```

para resultados comunes compartidos por todo el sistema.

```text
outcome_intraday
```

para horizontes de segundos o minutos.

```text
outcome_daily
```

para estudios diarios.

```text
outcome_execution
```

para investigaciones sobre slippage, fills o calidad de ejecución.

```text
outcome_rl
```

para la construcción de transiciones utilizadas por algoritmos de aprendizaje por refuerzo.

```text
outcome_research
```

para experimentos científicos todavía no promovidos al núcleo estable.

Todos esos perfiles representan exactamente el mismo concepto.

Ninguno redefine qué significa un `Outcome`.

Únicamente materializan subconjuntos diferentes de la representación canónica.

Gracias a ello:

```text
las investigaciones pueden crecer;

los modelos pueden evolucionar;

las métricas pueden ampliarse;
```

sin necesidad de modificar continuamente una única tabla gigantesca.

La arquitectura permanece estable.

Únicamente evolucionan los perfiles físicos autorizados para representar el resultado observado.


## Conclusión

`Outcome` constituye la representación canónica del resultado observable dentro de TSIS.

Su misión no consiste en describir el mercado.

No consiste en describir un evento.

No consiste en describir la ejecución.

No consiste en decidir.

No consiste en generar estrategias.

Su misión consiste únicamente en preservar, de forma gobernada, aquello que ocurrió después del `decision_timestamp`.

La arquitectura completa queda definida por una única dirección conceptual.

```
PREGUNTAS CIENTÍFICAS
↓
MARKET STATE
↓
EVENT STATE
(opcional)
↓
EXECUTION STATE
(opcional)
↓
OUTCOME POLICY
↓
OUTCOME BUILDER
↓
OUTCOME
```

Cada capa responde a una pregunta diferente.

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
EXECUTION STATE
↓
¿Qué capacidad observable
existía para ejecutar?
```

↓

```
OUTCOME POLICY
↓
¿Qué resultado
queremos medir?
```

↓

```
OUTCOME BUILDER
↓
¿Cómo calculamos
ese resultado?
```

↓

```
OUTCOME
↓
¿Qué ocurrió
después?
```

La arquitectura mantiene una separación estricta entre:

```text
Estado observable
```

y:

```text
Resultado observable.
```

Esa separación garantiza que ningún dato posterior pueda contaminar la representación desde la que se toman decisiones.

Por ello:

```text
Market State

Event State

Execution State
```

constituyen exclusivamente el conocimiento disponible en el instante de decisión.

Mientras que:

```text
Outcome
```

representa exclusivamente aquello que ocurrió posteriormente.

Nunca al contrario.

Esta separación convierte a TSIS en un sistema temporalmente consistente.

Las investigaciones pueden evolucionar.

Las estrategias pueden cambiar.

Los algoritmos de Machine Learning pueden sustituirse.

Los modelos de Reinforcement Learning pueden mejorar.

Las políticas de ejecución pueden modificarse.

Incluso la definición de nuevos `Outcome` puede ampliarse.

Sin embargo, mientras permanezcan estables:

```text
la identidad del Market State;

la identidad del Event State;

la identidad del Execution State;

la política de definición del Outcome;

las reglas de observabilidad;

las reglas temporales;

la trazabilidad científica;
```

el conocimiento representado seguirá siendo exactamente el mismo.

`Outcome` no pertenece a una estrategia.

No pertenece a un algoritmo.

No pertenece a un modelo de Machine Learning.

No pertenece a Reinforcement Learning.

No pertenece a AlphaEvolve.

Pertenece al resultado observable del fenómeno investigado.

Todos los consumidores posteriores deben partir de la misma representación canónica del resultado.

A partir de ella podrán formular hipótesis diferentes, entrenar modelos distintos o construir nuevas políticas de decisión, pero ninguno de ellos deberá redefinir qué ocurrió realmente.

Por ello, `Outcome` constituye el cierre natural del flujo de representación de TSIS y la fuente de verdad para toda la investigación posterior basada en los resultados observados.