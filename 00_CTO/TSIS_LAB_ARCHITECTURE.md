# TSIS Lab Architecture

Fecha de creacion: 2026-06-18
Estado: arquitectura promovida desde `00_private/arquitectura.md`.

## Proposito

Este documento es la version promovida, limpia y gobernada de:

```text
00_private/arquitectura.md
```

El documento privado conserva valor como source note historica. Este archivo es
la lectura activa para agentes y humanos cuando trabajen sobre la arquitectura
del laboratorio TSIS.

La promocion no es una copia literal. Se han aplicado tres correcciones:

1. encoding limpio en ASCII para evitar mojibake;
2. nombres alineados con el arbol actual de `13_TRADING_SYSTEMS`;
3. autoridad operativa separada entre `00_CTO` y los modulos productivos.

## Tesis

TSIS no esta disenado solo para responder:

```text
Funciona esta estrategia?
```

TSIS esta disenado para responder:

```text
Que eventos existen?
Por que algunos eventos generan grandes movimientos?
Que contexto produce los mejores resultados?
Cual es la mejor decision posible dentro de cada contexto?
Como puede el laboratorio mejorar la forma en que investiga?
```

La arquitectura separa:

```text
datos
eventos
outcomes
estrategias
patrones
clusters
probabilidades
decisiones
evolucion
```

Si esos niveles se mezclan, el sistema pierde trazabilidad y los resultados se
vuelven dificiles de auditar.

## Cadena logica del laboratorio

```text
Data Foundation
-> Event Library
-> Event Engine
-> Outcome Research
-> Strategy Library
-> Strategy Research
-> Edge Hypotheses
-> Pattern Discovery
-> Cluster Research
-> Machine Learning
-> Decision Models
-> Evolution Systems
```

Esta cadena es logica y funcional. No significa que cada capa tenga que vivir
como carpeta top-level dentro de `00_CTO`, ni que `00_CTO` sea la autoridad
operativa de todos los outputs.

## Autoridad por area

```text
Data Foundation
-> autoridad operativa: 01_TSIS_backtest_SmallCaps/01_foundations
-> autoridad CTO: 12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS

Trading knowledge architecture
-> autoridad CTO: 13_TRADING_SYSTEMS

Event Library
-> autoridad CTO: 13_TRADING_SYSTEMS/00_EVENT_LIBRARY

Strategy Library
-> autoridad CTO: 13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY

Machine Learning doctrine
-> autoridad CTO: 08_MACHINE_LEARNING
-> implementacion futura: modulo 01 o modulo 03 segun caso

Decision Models / Offline RL
-> autoridad metodologica: 09_REINFORCEMENT_LEARNING y 13_TRADING_SYSTEMS
-> implementacion futura: 03_TSIS_Offline_RL

Evolution Systems / AlphaEvolve / OpenEvolve
-> autoridad CTO: 10_AUTONOMOUS_RESEARCH_SYSTEMS
-> sandbox y gating: 12_TSIS_COGNITIVE_ARCHITECTURE
```

## Principio central

```text
Evento != setup != estrategia != decision
```

Un evento describe:

```text
Que esta ocurriendo?
```

Una estrategia describe:

```text
Que hago frente a eso?
```

Un modelo de decision responde:

```text
Debo actuar ahora, como, con que size y bajo que constraints?
```

Un sistema evolutivo pregunta:

```text
Como mejoro las definiciones, features, filtros, estrategias o politicas?
```

Esta separacion permite que el mismo evento pueda ser analizado por multiples
estrategias sin redefinir la realidad historica.

---

# CAPA 1 - DATA FOUNDATION

## Objetivo

Construir una representacion fiable, auditada y reproducible del mercado.

Esta capa no busca edge ni crea estrategias. Su funcion es garantizar que todo
el sistema trabaja sobre datos correctos, trazables y comparables.

Principio:

```text
Si la data es incorrecta,
todo lo que venga despues sera falso.
```

## Autoridad

La autoridad operativa vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

`00_CTO` puede documentar arquitectura, contratos esperados y operating models,
pero no debe crear una segunda source of truth para schemas, registries,
validators, dataset registry ni data consumption policies.

## Inputs esperados

```text
Polygon
DAS
News
Fundamentals
SEC Filings
Corporate Actions
Market Calendar
```

## Responsabilidades

```text
1. Auditar calidad de datos
2. Normalizar simbolos y fechas
3. Ajustar splits y corporate actions
4. Detectar gaps, errores y outliers
5. Unificar temporalidades
6. Construir tablas maestras
7. Garantizar reproducibilidad
```

## Outputs objetivo

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
real_time_corporate_event_alerts_table
```

Estos outputs no quedan institucionales por estar nombrados aqui. Deben ser
materializados y gobernados en `01_foundations` mediante contracts, schemas,
registries, validators, policies, manifests y evidencia.

Referencia operativa actual:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
```

Ese contrato define el uso tecnico de estos outputs, sus nombres preferidos,
sus fuentes fisicas, su papel cuando aparece un evento y la politica de
materializacion compacta para no duplicar innecesariamente la raw data.

## `master_daily_table`

Representa el contexto estructural de cada ticker/dia.

Campos conceptuales:

```text
ticker
date
open
high
low
close
volume
gap_pct
rvol
market_cap
float
news_flag
former_runner
dilution_risk
```

## `master_intraday_table`

Representa la evolucion intradia del ticker.

Campos conceptuales:

```text
ticker
date
timestamp
open
high
low
close
volume
vwap
spread
relative_volume
distance_to_hod
distance_to_vwap
```

## Pregunta que responde

```text
Podemos confiar en los datos sobre los que TSIS va a investigar?
```

## Resultado conceptual

```text
Raw Data
    ->
Audited Data
    ->
Master Tables
```

## No-goals

Data Foundation no debe:

- decidir trades;
- definir estrategias;
- producir edge claims;
- inventar eventos sin contrato;
- mezclar datasets no comparables;
- sobrescribir outputs con semantica nueva bajo nombres antiguos.

---

# CAPA 2 - EVENT LIBRARY / EVENT RESEARCH

## Objetivo

Detectar y definir eventos de mercado.

Un evento es la unidad fundamental de investigacion de TSIS. Representa un
fenomeno observable del mercado, independiente de cualquier decision operativa.

Los eventos pueden ser definidos por:

```text
1. Hipotesis humanas
2. Descubrimiento estadistico
3. Clustering
4. AlphaEvolve u otros motores evolutivos, cuando exista laboratorio evaluable
```

Aqui todavia no existen estrategias.

Primero debemos responder:

```text
Que eventos existen?
```

## Autoridad CTO

La Event Library vive en:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY
```

## Ejemplos de eventos

```text
PM_Squeeze_Event
Gap_And_Go_Event
Red_To_Green_Event
VWAP_Reclaim_Event
First_Green_Day_Event
SSR_Event
Halt_Continuation_Event
Momentum_Exhaustion_Event
```

## Que describe un evento

Un evento describe:

```text
Que esta ocurriendo?
```

Ejemplo conceptual para `PM_Squeeze_Event`:

```text
Gap > 20%
Float < 20M
PM Volume > 500k
Primer Push > 15%
Pullback presente
HOD marcado
```

Todavia no existe trade.

Simplemente decimos:

```text
Esto parece un PM Squeeze.
```

## Diferencia entre evento y estrategia

```text
Evento = fenomeno de mercado
Estrategia = respuesta operativa ante ese fenomeno
```

Una estrategia describe:

```text
Que hago frente al evento?
```

Ejemplo:

```text
PM_Squeeze_Strategy_v1
Entrada: Break HOD
Stop: Pullback Low
Salida: 3R
```

Ahora si hay trade.

## Ejemplo de reutilizacion del mismo evento

Supongamos:

```text
PM_Squeeze_Event #34211
```

El evento historico es:

```text
Gap = 75%
Float = 2M
PM Volume = 5M
Primer Push = 25%
Pullback = 7%
```

Ese hecho historico puede ser operado con:

```text
Strategy A: Break HOD
Strategy B: First Higher Low
Strategy C: VWAP Reclaim
Strategy D: Tape Confirmation
```

El evento no cambia. Cambia la respuesta operacional.

## Por que AlphaEvolve debe empezar por eventos

AlphaEvolve probablemente trabajara mejor sobre:

```text
event_table
```

que sobre:

```text
strategy_table
```

Porque puede descubrir una mejor definicion del evento sin tocar todavia
entradas, salidas, stops o sizing.

## No-goals

La Event Library no debe contener:

- entradas;
- stops;
- targets;
- position sizing;
- gestion parcial;
- reglas de ejecucion;
- resultados de backtest como autoridad final.

Si contiene entrada, stop, target o sizing, no es evento: es estrategia o
execution model.

---

# CAPA 3 - EVENT ENGINE

## Objetivo

Transformar datos auditados de mercado en eventos estructurados que puedan ser
investigados, comparados, agrupados y evaluados.

El Event Engine es el primer componente que convierte:

```text
Datos
    ->
Conocimiento investigable
```

## Funcion principal

Recorrer el historico y detectar automaticamente cada aparicion de eventos
definidos por el sistema.

Horizonte conceptual:

```text
2005-2026
```

## Inputs

```text
master_daily_table
master_intraday_table
event_definitions
symbol_master
corporate_actions_table
calendar_table
```

## Output

```text
event_table
```

## Que hace el Event Engine

Para cada dia y cada ticker:

```text
1. Evalua definiciones de eventos
2. Detecta candidatos
3. Extrae atributos
4. Genera registros normalizados
5. Preserva version de definicion y trazabilidad
```

## Ejemplo

Supongamos:

```text
ABCD
2020-05-14
```

El sistema detecta:

```text
Gap = 72%
Float = 3M
PM Volume = 4M
Primer Push = 25%
Pullback = 8%
```

La definicion de:

```text
PM_Squeeze_Event
```

se cumple.

Entonces genera:

```text
event_id = 12345
```

## `event_table`

Cada fila representa:

```text
Un evento observado en el mercado.
```

No representa:

```text
Un trade.
Una estrategia.
Una posicion.
Una decision.
```

Estructura conceptual:

```text
event_id
ticker
date
event_type
event_definition_version
event_start
event_end
gap_pct
float
market_cap
pm_volume
rvol
news_flag
first_push_pct
pullback_pct
vwap_distance
spread
sector
data_quality_state
source_dataset_versions
```

## Importancia

`event_table` se convierte en uno de los activos mas importantes de TSIS.

A partir de ella se construyen:

```text
Outcome Research
Strategy Research
Clustering
Pattern Discovery
Machine Learning
Decision Models
Evolution Systems
Offline RL
```

## Pregunta que responde

```text
Que ocurrio?
```

Las capas posteriores responderan:

```text
Que paso despues?
Que patrones existen?
Que decision era mejor?
```

---

# CAPA 4 - OUTCOME RESEARCH

## Objetivo

Medir que ocurrio despues de cada evento detectado.

En esta fase todavia no evaluamos estrategias.
No existen entradas.
No existen stops.
No existen salidas.
Todavia no existe ningun trade.

El objetivo es medir la evolucion natural del evento.

## Filosofia

El Event Engine responde:

```text
Que ocurrio?
```

Outcome Research responde:

```text
Que paso despues?
```

## Principio fundamental

Un mismo evento puede producir resultados muy diferentes.

Ejemplo:

```text
PM_Squeeze_Event #1001 -> +10%
PM_Squeeze_Event #1002 -> +150%
```

El objetivo es cuantificar esas diferencias.

## Input

```text
event_table
```

## Output

```text
outcome_table
```

## Que hace Outcome Research

Para cada evento detectado:

```text
1. Observa la evolucion posterior
2. Calcula metricas objetivas
3. Genera etiquetas de resultado
4. Almacena outcomes reproducibles
5. Preserva horizonte, version y dataset lineage
```

## Ejemplo

Evento:

```text
event_id = 12345
ticker = ABCD
event_type = PM_Squeeze_Event
event_start = 09:34:12
```

Posteriormente el precio:

```text
Sube +65%
Retrocede -12%
Hace maximo a las 10:07
Cierra +22%
```

Outcome Research genera:

```text
max_extension = +65%
max_adverse_excursion = -12%
time_to_peak = 33 min
close_return = +22%
```

## `outcome_table`

Estructura conceptual:

```text
event_id
outcome_horizon
max_extension_pct
max_adverse_excursion_pct
close_return_pct
time_to_peak
time_to_failure
peak_price
close_price
outcome_label
squeeze_score
runner_score
liquidity_degradation_score
halt_risk_realized
```

## Outcome labels

Los outcomes permiten crear etiquetas.

Ejemplos:

```text
Failed_Event
Weak_Event
Average_Event
Strong_Event
Exceptional_Event
```

Tambien:

```text
Top_1_Percent
Top_5_Percent
Top_10_Percent
```

## Resultado conceptual

```text
Evento
    ->
Resultado
```

Ejemplo:

```text
Gap = 80%
Float = 2M
PM Volume = 6M
    ->
+120%
```

Otro ejemplo:

```text
Gap = 25%
Float = 50M
PM Volume = 500k
    ->
-8%
```

## Preguntas que responde

```text
Que eventos producen los mayores runners?
Que eventos fallan con mas frecuencia?
Que variables preceden los mayores squeezes?
Que contextos generan los mejores resultados?
```

## No-goals

Outcome Research no mide:

```text
Que habria hecho el trader?
```

Mide:

```text
Que hizo el mercado?
```

Esta separacion evita introducir sesgo de estrategia antes de comprender la
respuesta natural del mercado.

---

# CAPA 5 - STRATEGY LIBRARY

## Objetivo

Definir respuestas operativas propuestas frente a eventos.

Esta capa contiene estrategias, pero no las valida como edge por el hecho de
existir.

## Autoridad CTO

```text
13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY
```

## Que es una estrategia

Una estrategia es una respuesta operacional ante un evento.

Recordatorio:

```text
Evento = fenomeno de mercado
Estrategia = respuesta operativa frente al fenomeno
```

## Ejemplo

Evento:

```text
PM_Squeeze_Event
```

Estrategias:

```text
PM_Squeeze_Strategy_v1
Entrada: Break HOD
Stop: Pullback Low
Salida: 3R
```

```text
PM_Squeeze_Strategy_v2
Entrada: First Higher Low
Stop: Higher Low
Salida: 5R
```

Ambas estrategias pueden operar exactamente el mismo evento.

## Inputs

```text
event_definitions
outcome_research
edge_hypotheses
execution_doctrine
```

## Outputs

```text
strategy_definition
entry_rules
exit_rules
stop_rules
sizing_notes
invalidation_conditions
execution_constraints
failure_modes
```

## No-goals

La Strategy Library no debe:

- redefinir eventos;
- redefinir datos upstream;
- presentar resultados como validados sin research;
- mezclar discretion con reglas mecanicas sin etiquetarlo;
- convertir una idea humana en institucional sin evidencia.

---

# CAPA 6 - STRATEGY RESEARCH

## Objetivo

Responder:

```text
La ventaja sobrevive en el tiempo?
```

Por primera vez introducimos decisiones operativas en evaluacion.

Hasta este punto TSIS estudio:

```text
Que ocurrio?
Que paso despues?
```

Ahora estudia:

```text
Que habria hecho un trader?
```

## Inputs

```text
event_table
outcome_table
strategy_library
execution_constraints
cost_model
risk_policy
```

## Outputs

```text
strategy_results
strategy_performance
walk_forward_results
robustness_report
failure_mode_report
promotion_candidate_report
```

## Backtesting clasico

Las estrategias se evaluan sobre historico completo con ventanas temporales
controladas.

Ejemplo:

```text
2005-2015 Train -> 2016 Test
2005-2016 Train -> 2017 Test
2005-2017 Train -> 2018 Test
...
```

## Metricas

TSIS debe medir:

```text
Profit Factor
Win Rate
Expectancy
Average R
Max Drawdown
Sharpe
Sortino
Exposure
Trade Frequency
Capacity
Slippage sensitivity
```

## Robustez

No buscamos unicamente estrategias rentables.
Buscamos estrategias robustas.

El objetivo es encontrar:

```text
mesetas
```

No:

```text
picos
```

Pequenos cambios no deberian destruir el edge.

## Preguntas que responde

```text
Funciona la estrategia?
La ventaja sobrevive en el tiempo?
La estrategia es robusta?
Que variantes funcionan mejor?
Que entradas son superiores?
Que salidas son superiores?
```

## Lo que no responde

Esta capa todavia no responde:

```text
Por que funciona?
Que patrones existen?
Que contexto produce los mejores runners?
```

Eso pertenece a:

```text
Pattern Discovery
Cluster Research
Machine Learning
```

## Resultado conceptual

```text
Evento
    ->
Outcome
    ->
Estrategia
    ->
Performance
```

## Principio fundamental

Strategy Research valida hipotesis humanas.

```text
Humano
    ->
Hipotesis
    ->
Backtest
    ->
Validacion
```

Las capas posteriores buscan descubrir conocimiento que inicialmente no formaba
parte de las hipotesis humanas.

---

# CAPA 7 - EDGE HYPOTHESES

## Objetivo

Explicar por que podria existir edge antes de optimizar una estrategia.

Una hipotesis de edge conecta:

```text
fenomeno observable
-> mecanismo de mercado
-> consecuencia esperada
-> restricciones bajo las que podria explotarse
```

## Inputs

```text
event_library
outcome_research
market_science
reference_material
visual_case_review
```

## Outputs

```text
edge_hypothesis
mechanism_note
falsification_criteria
expected_failure_modes
required_data_evidence
```

## No-goals

Edge Hypotheses no debe ser:

- una estrategia completa;
- un resultado de backtest maquillado;
- una narrativa sin falsabilidad;
- una razon para saltarse Outcome Research.

---

# CAPA 8 - PATTERN DISCOVERY

## Objetivo

Responder:

```text
Que tienen en comun los mejores eventos?
```

Hasta este punto TSIS valida hipotesis humanas. Ahora empieza a buscar
conocimiento nuevo dentro de los datos.

## Cambio conceptual

Backtesting clasico:

```text
Humano
    ->
Hipotesis
    ->
Test
    ->
Resultado
```

Pattern Discovery:

```text
Datos
    ->
Patron
    ->
Hipotesis
    ->
Validacion
```

En backtesting, el humano propone.
En Pattern Discovery, los datos sugieren.

## Inputs

```text
event_table
outcome_table
strategy_results
```

## Objetivo principal

Encontrar relaciones estadisticas que expliquen:

```text
Por que algunos eventos producen resultados excepcionales
y otros fracasan.
```

## Ejemplo

Supongamos que analizamos:

```text
100000 PM_Squeeze_Events
```

Descubrimos:

```text
80% de los runners >100%
ocurren cuando:

Float < 3M
PM Volume > 4M
Gap > 40%
```

Nadie programo esa regla. La regla emerge de los datos.

## Filosofia

No buscamos:

```text
Funciona una estrategia?
```

Buscamos:

```text
Que propiedades tienen los eventos excepcionales?
```

## Ejemplos de descubrimientos

```text
Float < 3M
PM Volume / Float
Distancia a VWAP
Velocidad del Primer Push
Numero de intentos al HOD
Volume Compression
Time To HOD
```

## Outputs

```text
discovered_patterns
candidate_hypotheses
support_metrics
stability_notes
limits_of_evidence
```

## Principio fundamental

Pattern Discovery no produce estrategias.
Produce conocimiento.

Resultado:

```text
Hipotesis nuevas
```

Ejemplo:

```text
Los runners >150% aparecen principalmente cuando:

Float < 2M
Gap > 50%
PM Volume > 5M
```

Esto no es una estrategia. Es una observacion estadistica que despues debe ser
validada y, si procede, transformada en hipotesis o estrategia.

## Diferencia con Strategy Research

Strategy Research pregunta:

```text
Funciona esta idea?
```

Pattern Discovery pregunta:

```text
Que esta intentando decirnos el mercado?
```

---

# CAPA 9 - CLUSTER RESEARCH

## Objetivo

Agrupar eventos por contexto y comportamiento.

No agrupamos tickers.
No agrupamos estrategias.
Agrupamos comportamientos.

## Pregunta central

```text
Existen familias distintas de eventos?
```

o:

```text
Existen distintos tipos de PM Squeeze?
```

## Cambio conceptual

Pattern Discovery:

```text
Evento
    ->
Patron
```

Cluster Research:

```text
Eventos
    ->
Familias
```

Pattern Discovery busca relaciones.
Cluster Research busca estructura.

## Inputs

```text
event_table
outcome_table
discovered_patterns
```

## Objetivo principal

Encontrar grupos de eventos que comparten caracteristicas similares.

No buscamos:

```text
Que ticker es?
```

Buscamos:

```text
Que tipo de comportamiento representa?
```

## Ejemplo

Supongamos:

```text
100000 PM_Squeeze_Events
```

El sistema descubre:

```text
Cluster A
Gap 50-80%
Float 2-5M
PM Volume >3M
Primer Push moderado
Pullback corto
```

```text
Cluster B
Gap >100%
Float <1M
PM Volume >10M
Primer Push explosivo
Spread amplio
```

```text
Cluster C
Gap 20-40%
Float >20M
PM Volume medio
Movimiento lento
```

Nadie definio esos grupos previamente. Emergen de los datos.

## Ejemplos de clusters posibles

```text
Low Float Momentum Cluster
Parabolic Runner Cluster
High Liquidity Gapper Cluster
Failed Squeeze Cluster
Multi-Day Runner Cluster
```

Los nombres son secundarios. Lo importante es que representan familias
recurrentes de comportamiento.

## Principio fundamental

Un mismo evento humano puede contener multiples subtipos.

Ejemplo:

```text
PM_Squeeze_Event
```

puede contener:

```text
PM_Squeeze_Type_A
PM_Squeeze_Type_B
PM_Squeeze_Type_C
```

con resultados completamente distintos.

## Outputs

```text
cluster_table
cluster_profiles
behavior_families
cluster_outcome_stats
cluster_failure_modes
```

## Diferencia con Pattern Discovery

Pattern Discovery pregunta:

```text
Que tienen en comun los mejores eventos?
```

Cluster Research pregunta:

```text
Que familias distintas de eventos existen?
```

---

# CAPA 10 - MACHINE LEARNING

## Objetivo

Modelar:

```text
Estado de mercado
    ->
Resultado futuro
```

Hasta este punto TSIS ha descubierto:

```text
Eventos
Outcomes
Patrones
Clusters
```

Ahora construye modelos capaces de estimar probabilidades.

## Cambio conceptual

Las capas anteriores responden:

```text
Que ocurrio?
Que paso despues?
Que patrones existen?
Que familias existen?
```

Machine Learning responde:

```text
Que es probable que ocurra?
```

## Inputs

```text
context
event
cluster
outcome_labels
data_quality_state
```

## Objetivo principal

Aprender relaciones entre:

```text
estado del mercado
```

y:

```text
resultado futuro
```

## Ejemplo

Supongamos:

```text
Gap = 75%
Float = 2M
PM Volume = 6M
Cluster = PM_Squeeze_Type_A
Primer Push = 25%
Pullback = 6%
```

El modelo estima:

```text
Probabilidad Runner >100% = 68%
Probabilidad Top 5% = 22%
Probabilidad Failure = 11%
```

No esta tomando decisiones. Esta estimando probabilidades.

## Tareas

Clasificacion:

```text
Runner
No Runner
```

Clasificacion ordinal:

```text
Top 1%
Top 5%
Top 10%
Normal
```

Regresion:

```text
Expected Move %
Expected Extension %
Expected MAE
Expected Time To Peak
```

Ranking:

```text
Ordenar eventos por calidad esperada
```

## Outputs

```text
success_probability
runner_probability
top_percentile_probability
expected_move
expected_extension
expected_risk
feature_importance_with_caution
model_validation_report
```

## Diferencia con Cluster Research

Cluster Research pregunta:

```text
Que familias existen?
```

Machine Learning pregunta:

```text
A que familia pertenece este evento?
Que resultado es mas probable?
```

## Principio fundamental

Machine Learning no toma decisiones.
Machine Learning estima probabilidades.

Las decisiones aparecen en capas posteriores.

---

# CAPA 11 - DECISION MODELS

## Objetivo

Responder:

```text
Cual es la mejor decision posible ahora?
```

Hasta este punto TSIS ha aprendido:

```text
Que ocurrio
Que paso despues
Que patrones existen
Que familias existen
Que resultado es probable
```

Ahora optimiza decisiones.

## Cambio conceptual

Machine Learning:

```text
Estado de mercado
    ->
Prediccion
```

Decision Models:

```text
Estado de mercado
    ->
Accion
```

Machine Learning responde:

```text
Que creo que ocurrira?
```

Decision Models responden:

```text
Que deberia hacer?
```

## Inputs

```text
context
event
cluster
ml_probabilities
outcome_history
execution_constraints
risk_state
portfolio_context
```

## Objetivo principal

Aprender politicas de decision.

Una politica responde:

```text
Dado este contexto,
que accion maximiza el resultado esperado?
```

## Ejemplo

Evento:

```text
PM_Squeeze_Event
```

Estado actual:

```text
Gap = 75%
Float = 2M
PM Volume = 5M
Pullback = 7%
Cluster = Type_A
Success Probability = 81%
```

El problema ya no es:

```text
Va a funcionar?
```

El problema es:

```text
Donde entro?
Cuanto riesgo tomo?
Cuando salgo?
Debo operar?
```

## Preguntas que responde

```text
Debo entrar?
Debo esperar?
Que entrada es mejor?
Que stop es mejor?
Que salida es mejor?
Cuanto capital debo asignar?
Vale la pena operar este evento?
```

## Tecnologias candidatas

```text
Offline RL
Decision Transformer
CQL
IQL
Behavioral Cloning
Meta-labeling decision layer
```

## Conservative Q-Learning

Objetivo:

```text
Evitar decisiones fuera de distribucion.
```

Especialmente importante en trading.

## Implicit Q-Learning

Objetivo:

```text
Aprender de buenos ejemplos sin necesidad de explorar.
```

Interesante para:

```text
Trades de operadores expertos
```

## Outputs

```text
action_policy
entry_policy
exit_policy
sizing_policy
risk_policy
abstention_rules
decision_validation_report
```

## Diferencia con Machine Learning

Machine Learning pregunta:

```text
Que resultado es probable?
```

Decision Models preguntan:

```text
Que accion maximiza el resultado esperado?
```

## Principio fundamental

Machine Learning aprende el mercado.
Decision Models aprenden decisiones.

---

# CAPA 12 - EXECUTION MODELS

## Objetivo

Convertir decisiones teoricas en acciones realistas bajo friccion de mercado.

Una decision sin ejecucion realista no vale.

## Inputs

```text
action_policy
market_state
quotes
trades
spread
liquidity
halts
borrow_constraints
risk_policy
```

## Outputs

```text
fill_model
slippage_model
partial_fill_model
capacity_model
execution_risk_report
realistic_strategy_results
```

## Debe cubrir

```text
bid/ask
spread
slippage
fills parciales
volumen utilizable
borrows y locates
SSR
halts
latency
capacity
```

## Principio

La senal puede ser correcta y el trade inviable.

TSIS debe saber la diferencia.

---

# CAPA 13 - EVOLUTION SYSTEMS

## Objetivo

Evolucionar automaticamente:

```text
Detectores de eventos
Features
Clusters
Filtros
Estrategias
Reglas de entrada
Reglas de salida
Modelos
Politicas de decision
```

Hasta este punto TSIS dispone de un laboratorio completo. Ahora el sistema puede
generar hipotesis nuevas y validarlas automaticamente.

## Cambio conceptual

Capas anteriores:

```text
Humano
    ->
Idea
    ->
Implementacion
    ->
Evaluacion
```

Evolution Systems:

```text
Sistema
    ->
Hipotesis
    ->
Evaluacion
    ->
Seleccion
    ->
Nueva hipotesis
```

## Filosofia

No buscamos solo:

```text
Validar ideas humanas.
```

Buscamos:

```text
Generar ideas nuevas.
```

## Inputs

```text
event_table
outcome_table
cluster_table
ml_models
decision_models
strategy_library
locked_evaluators
constraints
```

## Objetivo principal

Explorar espacios de busqueda demasiado grandes para ser recorridos
manualmente.

Un investigador humano puede probar:

```text
10
50
100
```

variantes.

Un sistema evolutivo puede explorar:

```text
10000
100000
1000000
```

variantes, siempre que existan evaluadores bloqueados y trazabilidad.

## Tecnologias candidatas

```text
AlphaEvolve
OpenEvolve
```

## Ciclo general

```text
Hipotesis
    ->
Evaluacion
    ->
Score
    ->
Mutacion
    ->
Nueva hipotesis
```

## Ejemplo 1 - Evolucion de eventos

Definicion inicial:

```text
Gap > 20%
Float < 20M
PM Volume > 500k
```

Despues de iteraciones:

```text
Gap > 45%
Float < 5M
PM Volume > 3M
Primer Push > 20%
```

El sistema descubre una definicion mas util del evento.

## Ejemplo 2 - Evolucion de features

Variables iniciales:

```text
Gap
Float
PM Volume
```

El sistema descubre:

```text
PM Volume / Float
Push Velocity
Time To HOD
Volume Compression
```

## Ejemplo 3 - Evolucion de estrategias

Version inicial:

```text
Break HOD
Stop Pullback Low
Target 3R
```

Despues de multiples generaciones:

```text
First Higher Low
Dynamic Stop
Volatility Exit
```

## Ejemplo 4 - Evolucion de politicas

El sistema modifica:

```text
Entradas
Salidas
Position Sizing
Risk Allocation
```

para maximizar resultados historicos dentro de constraints.

## Requisito fundamental

Los sistemas evolutivos necesitan un laboratorio previamente construido.

Necesitan:

```text
event_table
outcome_table
strategy_evaluator
locked_fitness_functions
lineage
constraints
```

Sin evaluador:

```text
No existe evolucion.
```

## Preguntas que responde

```text
Puede una variante superar a la hipotesis humana?
Existe una mejor definicion del evento?
Existen mejores features?
Existen mejores filtros?
Existen mejores estrategias?
Existen mejores decisiones?
```

## Principio fundamental

El objetivo no es optimizar una unica estrategia.
El objetivo es evolucionar continuamente el laboratorio completo de
investigacion.

Por primera vez TSIS no solo aprende del mercado. Tambien aprende a mejorar la
forma en que aprende del mercado.

---

# Ruta de implementacion

## Paso 1 - Cerrar Data Foundation

Ruta:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

Outputs objetivo:

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
real_time_corporate_event_alerts_table
```

Condicion de avance:

```text
contracts + schemas + validators + registry + manifests + evidence
```

## Paso 2 - Gobernar Event Library

Ruta:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY
```

Input fuente inmediato:

```text
00_private/eventos.md
```

Salida:

```text
event definitions gobernadas
```

## Paso 3 - Definir Event Engine Model

Ruta:

```text
00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL
```

Salida:

```text
event_table conceptual contract
event detection model
event versioning model
```

## Paso 4 - Definir Outcome Research

Ruta:

```text
00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH
```

Salida:

```text
outcome_table conceptual contract
outcome horizons
outcome labels
```

## Paso 5 - Revisar Strategy Library

Ruta:

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY
```

Accion:

```text
separar estrategia, edge hypothesis, execution model y discretionary material
```

## Paso 6 - Construir evaluadores antes que generadores

Rutas:

```text
00_CTO/05_EVALUATION_SYSTEMS
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE
```

Condicion:

```text
AlphaEvolve no puede operar antes de evaluadores bloqueados.
```

## Paso 7 - ML, Decision Models y Evolution Systems

Solo avanzar cuando existan:

```text
data auditada
event_table
outcome_table
strategy_results
execution realism
evaluation gates
```

---

# Mapeo funcional a carpetas actuales

```text
Data Foundation
-> 01_TSIS_backtest_SmallCaps/01_foundations
-> 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS

Event Library
-> 00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY

Event Engine
-> 00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL

Outcome Research
-> 00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH

Strategy Library
-> 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY

Strategy Research
-> 00_CTO/13_TRADING_SYSTEMS/04_STRATEGY_RESEARCH

Edge Hypotheses
-> 00_CTO/13_TRADING_SYSTEMS/05_EDGE_HYPOTHESES

Pattern Discovery
-> 00_CTO/13_TRADING_SYSTEMS/06_PATTERN_DISCOVERY

Cluster Research
-> 00_CTO/13_TRADING_SYSTEMS/07_CLUSTER_RESEARCH

Execution Models
-> 00_CTO/13_TRADING_SYSTEMS/08_EXECUTION_MODELS

Decision Models
-> 00_CTO/13_TRADING_SYSTEMS/09_DECISION_MODELS

Evolution Systems
-> 00_CTO/13_TRADING_SYSTEMS/10_EVOLUTION_SYSTEMS

Squeeze Research
-> 00_CTO/13_TRADING_SYSTEMS/11_SQUEEZE_RESEARCH

Discretionary Frameworks
-> 00_CTO/13_TRADING_SYSTEMS/90_DISCRETIONARY_FRAMEWORKS

Experimental
-> 00_CTO/13_TRADING_SYSTEMS/99_EXPERIMENTAL

Machine Learning doctrine
-> 00_CTO/08_MACHINE_LEARNING

Offline RL doctrine
-> 00_CTO/09_REINFORCEMENT_LEARNING

Autonomous Research / AlphaEvolve
-> 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS
-> 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE
```

---

# Regla final

La arquitectura de TSIS Lab debe hacer imposible confundir:

```text
dato
evento
outcome
estrategia
patron
cluster
probabilidad
decision
ejecucion
evolucion
```

Si una carpeta, documento, output o agente mezcla esos niveles sin contrato
explicito, debe corregirse antes de tratarse como arquitectura activa.
