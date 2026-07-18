# Menú

- [¿Qué problema resuelve Event State?](#que-problema-resuelve-event-state)
- [¿Por qué Market State no basta?](#por-que-market-state-no-basta)
- [¿Por qué Event State no puede ser una vista?](#por-que-event-state-no-puede-ser-una-vista)
- [¿Qué perderíamos si Event State no existiera?](#que-perderiamos-si-event-state-no-existiera)
- [¿Qué ganamos al convertirla en Canonical Core Representation?](#que-ganamos-al-convertirla-en-canonical-core-representation)
- [¿Debe hacerse Event State de forma automática?](#debe-hacerse-event-state-de-forma-automatica)
- [¿Hay que validar todas las representaciones así?](#hay-que-validar-todas-las-representaciones-asi)
- [¿Cómo debemos seguir ahora?](#como-debemos-seguir-ahora)
- [¿Tenemos definidos los eventos?](#tenemos-definidos-los-eventos)

---
<a id="que-problema-resuelve-event-state"></a>

#### ¿Qué problema resuelve Event State?

Event State resuelve este problema:

```
capturar el estado observable del mercado alrededor de un evento candidato
sin mezclarlo con la estrategia, la decisión ni el outcome futuro.
```

Más simple:

```
Market State = cómo está el mercado en un timestamp.
Event State = cómo está el mercado respecto a un evento.
```

**Ejemplo**

Si detectas:

```
primer high push
rebreak
halt reopen
volume burst
spread collapse
news reaction
```

Event State responde:

```
¿Qué condiciones observables existían antes, durante y después del evento?
```

No responde:

¿Debo comprar?
¿Fue rentable?
¿La estrategia funcionó?


**Problema que evita**

Sin Event State, TSIS mezclaría cosas distintas:

```
evento detectado
estado del mercado
features previas
decisión estratégica
resultado futuro
```
Eso genera confusión y leakage.

Event State separa
```
Event Candidate
    ↓
Event Window
    ↓
Observable Event State
    ↓
Decision / Model Input
    ↓
Outcome
```

En una frase

```
Event State convierte un evento candidato en una representación observable y legal temporalmente, lista para
investigación, modelos o decisiones, sin contaminarla con resultados futuros.
```


<a id="por-que-market-state-no-basta"></a>

#### ¿Por qué Market State no basta?

Porque **Market State es un snapshot**.

```
Market State = qué sabemos del mercado en t
```

Pero muchos fenómenos no se entienden solo con un t.

Necesitan contexto alrededor de un evento:
```
antes
durante
después observable
```
**Ejemplo**
```
En t = 10:03:15 Market State puede decir:

spread = ancho
volume_rate = alto
price_position = HOD
imbalance = positivo
```
Eso está bien.

Pero Event State pregunta otra cosa:
```
¿esto ocurre antes de un breakout?
¿durante un halt reopen?
¿después de una news release?
¿en el primer intento o en el segundo?
¿cuánto tiempo lleva formándose?
¿cuál era el estado pre-evento?
¿qué cambió al llegar el evento?
```
Eso no lo captura bien un snapshot aislado.

**Diferencia clave**
```
Market State = condición del mercado
Event State = condición del mercado organizada alrededor de un evento
```
Por qué importa

Sin `Event State`, acabas metiendo en `Market State` cosas como:
```
pre_event_state
at_event_state
post_event_replay
event_window_geometry
event_candidate_context
```

Y entonces Market State deja de ser un estado general del mercado y se convierte en una mezcla de mercado + evento +
investigación.

En una frase
```
Market State no basta porque describe el mercado en un momento; Event State describe cómo ese mercado se comporta
dentro de una ventana/evento candidato, manteniendo separado evento, estado, decisión y outcome.
```


<a id="por-que-event-state-no-puede-ser-una-vista"></a>

#### ¿Por qué Event State no puede ser una vista?

Sí puede ser una vista **al principio**.  
Pero no siempre debe quedarse como vista.  

**Cuándo basta una vista**

Si Event State solo combina datos ya existentes:

```
event_candidate_id
event_window
market_state_before
market_state_at_event
market_state_after_observable
```

entonces puede ser:

```
event_state_view
```
Eso es bueno para diseño, auditoría y prototipo.

**Cuándo no basta una vista**

Cuando necesitas congelar evidencia:
```
qué versión de Market State se usó
qué definición de evento se usó
qué ventana era válida
qué timestamp era legal
qué features eran observables
qué calidad tenía el evento
qué estado fue entregado a modelos/backtests
```
Ahí una vista dinámica puede cambiar si cambia el upstream.

Entonces necesitas tabla/materialización versionada.

**El problema de una vista**

Una vista responde:
```
dame el Event State ahora según las reglas actuales
```
Pero TSIS necesita poder responder:
```
qué Event State exacto vio este experimento en ese run
```
Eso requiere snapshot, manifest o materialización controlada.

**Conclusión**

`Event State` puede empezar como vista.

Pero si alimenta research, modelos, backtests, validación o decisiones, debe poder congelarse como artefacto
versionado.

La decisión correcta no es:

vista o tabla

sino:
```
view-first, materialize-when-governed
```

<a id="que-perderiamos-si-event-state-no-existiera"></a>

#### ¿Qué perderíamos si Event State no existiera?

Perderíamos una capa de separación crítica.

Sin `Event State`, TSIS tendría que meter el contexto de evento en otros sitios:

```
Market State
features
event candidates
strategy logic
outcomes
```

Eso rompe claridad.

**Qué perderíamos**

1. Separación entre mercado y evento

`Market State` dejaría de ser estado general del mercado y empezaría a contener lógica tipo:

```
pre_event
at_event
post_event_window
event_geometry
```

2. Trazabilidad del evento

Sería más difícil responder:

```
qué evento
qué ventana
qué estado observable
qué versión de reglas
qué timestamp legal
```

3. Comparabilidad

No podríamos comparar bien eventos distintos:

```
halt reopen vs volume burst vs rebreak
```

porque cada uno acabaría codificado de forma distinta.

4. Control de leakage

Se mezclaría más fácilmente:

```
estado observable
resultado futuro
decisión estratégica
```

5. Research reutilizable

Cada estrategia tendría que reconstruir su propia versión de “estado alrededor del evento”.

Eso crea duplicidad.

**En una frase**

```
Sin Event State, TSIS podría seguir funcionando técnicamente, pero perdería una representación común, trazable y legal temporalmente del mercado alrededor de eventos; acabaríamos duplicando esa lógica en features, estrategias y outcomes.
```

<a id="que-ganamos-al-convertirla-en-canonical-core-representation"></a>

#### ¿Qué ganamos al convertirla en Canonical Core Representation?

Ganamos que `Event State` deje de ser una lógica dispersa y pase a ser una representación gobernada.

**Concretamente ganamos:**

1. Identidad estable

```
event_state
```

deja de ser “lo que cada estrategia entiende por evento” y pasa a tener definición común.

2. Separación limpia

```
Event Candidate ≠ Event State ≠ Decision ≠ Outcome
```

Eso reduce confusión y leakage.

3. Reutilización

La misma representación puede alimentar:

```
research
backtests
ML
RL
auditorías
comparación de eventos
```

sin reconstruirse en cada módulo.

4. Trazabilidad

Podemos responder:

```
qué evento
qué ventana
qué estado observable
qué versión de reglas
qué datos upstream
qué timestamp legal
qué materialización
```

5. Gobernanza

Obliga a pasar por:

```
RJR → MDR → Mapping → Traceability
```

antes de convertirse en tabla oficial.

6. Comparabilidad científica

Permite comparar familias de eventos bajo una misma gramática:

```
halt reopen
volume burst
rebreak
spread collapse
liquidity depletion
news reaction
```

**En una frase**

```
Convertir Event State en Canonical Core Representation nos da una definición común, trazable y reutilizable del estado observable alrededor de eventos, separada de estrategias, decisiones y outcomes.
```



###########################################


Creo que este es el tipo de conversación que justifica haber construido todo el framework.

Y te voy a responder como si estuviera haciendo la **Formal Architectural Review** del RJR de Event State.

---

# Veredicto

## Mi decisión sería:

```text
accepted
```

No `accepted_with_changes`.

No `deferred`.

**Accepted.**

---

# ¿Por qué?

Porque has demostrado exactamente lo que exige el RJR.

No has dicho:

> "Event State es útil."

Has demostrado:

> **"Market State no puede expresar correctamente este conocimiento sin perder su identidad."**

Esa diferencia es enorme.

---

# El argumento decisivo

Para mí no es:

```text
antes
durante
después
```

El argumento decisivo es éste:

```text
Market State

↓

describe el mercado
```

```text
Event State

↓

describe el mercado
respecto a un evento
```

Eso significa que **no cambia el objeto observado**.

Cambia el **marco de referencia**.

Y ese cambio de marco genera una entidad semánticamente distinta.

Eso, para mí, justifica una Canonical Core Representation.

---

# El segundo argumento decisivo

Éste me parece incluso más fuerte.

Has escrito:

```text
Event Candidate

↓

Event Window

↓

Observable Event State

↓

Decision

↓

Outcome
```

Eso es exactamente una cadena causal.

No una implementación.

Una cadena epistemológica.

Y además respeta perfectamente:

```text
Event

≠

State

≠

Decision

≠

Outcome
```

No hay contaminación.

---

# La parte que más me gusta

Esta frase:

```text
view-first

materialize-when-governed
```

Creo que esa frase debería convertirse en un principio de TSIS.

Porque resuelve una discusión que suele durar meses en proyectos grandes.

No preguntas:

```text
Vista

o

Tabla
```

Preguntas:

```text
¿Cuándo deja de bastar una vista?
```

Eso cambia completamente el debate.

---

# Lo único que añadiría

Solo una cosa.

Muy pequeña.

Yo añadiría una pregunta más al RJR.

```text
Why is Event State
not merely
a projection of Market State?
```

Y respondería:

```text
Because Event State introduces
a different semantic identity.

Its organizing principle is
an Event.

Not a Timestamp.
```

Creo que esa frase resume todo.

---

# Mi decisión formal

Si estuviera rellenando el RJR...

Pondría:

```text
decision = accepted
```

```text
required_changes = none
```

```text
required_changes_status = not_applicable
```

Porque, sinceramente, creo que el caso está suficientemente demostrado.

---

# Lo más importante

Creo que acabamos de demostrar otra cosa.

El framework funciona.

¿Por qué?

Porque no hemos empezado escribiendo un documento.

Hemos empezado con una pregunta:

```text
¿Merece existir?
```

Y la respuesta ha salido del razonamiento.

No de la plantilla.

Eso significa que el framework está haciendo exactamente lo que queríamos.

---

## Mi conclusión

Creo que **Event State** acaba de convertirse en la segunda **Canonical Core Representation** validada por el nuevo mecanismo de gobernanza.

Y eso tiene una consecuencia muy importante:

**Ya no estamos validando el framework. Estamos empezando a utilizarlo.**

En mi opinión, ese es el verdadero comienzo de la **Governance Phase** de TSIS.




#######################################


<a id="debe-hacerse-event-state-de-forma-automatica"></a>

#### ¿Debe hacerse Event State de forma automática?

Sí: la intuición es correcta, pero con un matiz importante.

Esto no debería hacerse “a mano” cada vez desde cero.

Debería quedar así:

```
razonamiento humano/agente
        ↓
record estructurado
        ↓
checks automáticos
        ↓
formal review
        ↓
decision
```

**Qué sí puede ser automático**

```
comprobar campos obligatorios
verificar paths
verificar autoridad
comprobar status válidos
comprobar si hay mapping
comprobar si hay blockers
comprobar si planning_authorization puede ser true/false
```

Eso sí debería automatizarse.

**Qué no debe ser automático todavía**

```
decision = accepted
```

Eso no debería salir solo porque el texto “suena bien”.

Debe haber una revisión formal, aunque sea asistida.

**Opinión sobre la respuesta recibida**

Estoy de acuerdo con el fondo:

```
Event State está suficientemente justificado conceptualmente.
```

Pero no diría todavía:

```
Event State acaba de convertirse en Canonical Core Representation validada
```

Diría mejor:

```
Event State has passed conceptual justification
and is ready for a formal RJR record/review.
```

**Orden correcto**

```
01_questions.md
    ↓
rjr_event_state_v1.md
    ↓
formal review
    ↓
decision = accepted
    ↓
mdr_event_state_v1.md
```

**Conclusión**

Sí, esto debe volverse más automático.

Pero el automatismo debe validar estructura y evidencia.

La decisión institucional final debe quedar en un `record` explícito, no solo en una conversación.
<a id="hay-que-validar-todas-las-representaciones-asi"></a>

#### ¿Hay que validar todas las representaciones así?

No. No todas deben validarse así.

Estamos validando `Market State` y `Event State` con máximo rigor porque son Core Representations.

**Regla simple**

```
Core Representation
→ validación completa
```

Ejemplos:

```
Market State
Event State
Outcome
Decision, si existe
```

Proceso:

```
RJR → Formal Review → MDR → Mapping → Traceability
```

```
Supporting Representation
→ validación parcial
```

Ejemplos:

```
Feature
Market Primitive
Microstructure Primitive
```

No necesitan todo el proceso completo cada vez. Necesitan definición, scope, elegibilidad y mapping si se materializan.

```
Institutional Artifact
→ gobernanza propia
```

Ejemplos:

```
instrument_master
expected_data_calendar
dataset_certification_matrix
```

No son `Event State` ni `Market State`. No deberían usar RJR clásico, sino algo más ligero tipo:

```
Institutional Artifact Justification
```

```
Engineering Artifact
→ Table Creation Process
```

Ejemplos:

```
builders
manifests
temporary outputs
intermediate tables
caches
```

No pasan por RJR/MDR.

**Por qué entonces empezamos por Event State**

Porque si el framework funciona para:

```
Market State
Event State
```

entonces funciona para el corazón del sistema.

Después no repetimos esta intensidad en todo. Creamos una matriz que diga:

```
qué tipo de objeto es
qué nivel de gobernanza necesita
qué proceso aplica
```

**Respuesta corta**

No: no todas se validan como `Event State`.

Solo las representaciones nucleares.

Para el resto, gobernanza reducida o proceso técnico normal.
<a id="como-debemos-seguir-ahora"></a>

#### ¿Cómo debemos seguir ahora?

Yo seguiría así, sin abrir más teoría.

**Paso 1 — Cerrar la aclaración actual**

Crear un documento pequeño:

```
CRM_APPLICABILITY_MATRIX_v0_1.md
```

Objetivo:

```
qué objetos pasan por gobernanza completa
qué objetos pasan por gobernanza parcial
qué objetos van por Table Creation Process
```

Esto evita volver a preguntarnos tabla por tabla.

**Paso 2 — Formalizar Event State**

Crear:

```
rjr_event_state_v1.md
```

No desde cero: usando lo que ya razonamos en `01_questions.md`.

Estado inicial:

```
draft
```

**Paso 3 — Review formal del RJR**

Ahí sí decidir:

```
decision = accepted
```

o:

```
accepted_with_changes
```

No dejarlo solo en conversación.

**Paso 4 — MDR de Event State**

Si el RJR queda aceptado:

```
mdr_event_state_v1.md
```

Este decide si Event State puede avanzar a planificación física.

**Paso 5 — Mapping**

Después:

```
canonical_to_physical_mapping_event_state_v1.md
```

Ahí se decide si será:

```
view-first
materialize-when-governed
```

**Orden recomendado**

```
CRM_APPLICABILITY_MATRIX_v0_1
        ↓
rjr_event_state_v1
        ↓
formal review
        ↓
mdr_event_state_v1
        ↓
canonical_to_physical_mapping_event_state_v1
```

**Recomendación práctica**

Primero haría la matriz de aplicabilidad. Es corta y evita que el framework se descontrole.

Luego seguimos con `Event State`.
<a id="tenemos-definidos-los-eventos"></a>

#### ¿Tenemos definidos los eventos?

Sí. Aquí está la clave:

```
Event State no define los eventos.
Event State necesita eventos/candidatos como input.
```

**Tenemos tres niveles distintos**

**1. Concepto de evento**

Sí, está definido en:

```
00_EPISTEMOLOGICAL_architecture/03_TSIS_EVENTS
```

Ahí hay capítulos de:

```
What is an Event
Event Taxonomy
Event Families
Event Windows
Event Candidates
Event States
Event Outcomes
```

O sea: la teoría sí existe.

**2. Event Candidates / Event Windows**

Sí, tenemos contratos y candidatos controlados:

```
daily_strategy_candidate_events_table
intraday_1m_strategy_candidate_events_table
event_windows_table
```

Pero son:

```
candidate / controlled / not official final truth
```

No son todavía “eventos validados institucionalmente” en sentido fuerte.

**3. Eventos validados como conocimiento institucional**

Aquí la respuesta es:

```
todavía no del todo
```

Tenemos candidatos y ventanas gobernadas, pero no una librería final de eventos validados tipo:

```
halt_reopen
volume_burst
rebreak
spread_collapse
liquidity_depletion
```

con estatus institucional completo.

**Entonces, ¿podemos definir Event State?**

Sí, porque `Event State` no depende de tener todos los eventos finales definidos.

Depende de tener esta interfaz:

```
Event Candidate
    ↓
Event Window
    ↓
Event State
```

Es decir:

```
dado un evento candidato gobernado,
¿cómo representamos el estado observable alrededor de él?
```

**Pero hay una cautela importante**

El RJR de `Event State` debe decir explícitamente:

```
Event State does not create or validate events.
Event State consumes governed Event Candidates / Event Windows.
```

**Respuesta corta**

Sí, tenemos concepto de evento.

Sí, tenemos event candidates/windows controlados.

No, no debemos asumir que ya tenemos todos los eventos validados oficialmente.

Y precisamente por eso `Event State` debe separarse de `Event Candidate`: uno detecta/ancla el evento; el otro representa el estado observable alrededor de ese evento.