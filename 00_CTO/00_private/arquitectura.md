
# TSIS - Lab

**Trading Science & Intelligence System**

Arquitectura de Investigación, Aprendizaje y Evolución.   
De eventos de mercado a sistemas autónomos de descubrimiento.


**Filosofía**

TSIS no está diseñado para responder únicamente:

```text
¿Funciona esta estrategia?
```

TSIS está diseñado para responder:

```text
¿Qué eventos existen?
¿Por qué algunos eventos generan grandes movimientos?
¿Qué contexto produce los mejores resultados?
¿Cuál es la mejor decisión posible dentro de cada contexto?
```


# CAPA 1 — DATA FOUNDATION

**Objetivo**

Construir una representación fiable, auditada y reproducible del mercado.

Esta capa no busca encontrar edge ni crear estrategias.  
Su función es garantizar que todo el sistema trabaja sobre datos correctos, trazables y comparables.

**Principio fundamental**

```text
Si la data es incorrecta,
todo lo que venga después será falso.
````

**Inputs**

```text
Polygon
DAS
News
Fundamentals
SEC Filings
Corporate Actions
Market Calendar
```

**Responsabilidades**

```text
1. Auditar calidad de datos
2. Normalizar símbolos y fechas
3. Ajustar splits y corporate actions
4. Detectar gaps, errores y outliers
5. Unificar temporalidades
6. Construir tablas maestras
7. Garantizar reproducibilidad
```

**Outputs**

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
```

**`master_daily_table`**

Representa el contexto estructural de cada ticker/día.

Ejemplos:

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

**`master_intraday_table`**

Representa la evolución intradía del ticker.

Ejemplos:

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

**Pregunta que responde esta capa**

```text
¿Podemos confiar en los datos
sobre los que TSIS va a investigar?
```

**Resultado conceptual**

```text
Raw Data
    ↓
Audited Data
    ↓
Master Tables
```


# CAPA 2 — EVENT RESEARCH

## Objetivo

Detectar eventos de mercado.

```
Evento :

Unidad fundamental de investigación de TSIS.

Representa un fenómeno observable
del mercado, independiente de cualquier
decisión operativa.

Los eventos pueden ser definidos:

1. Por hipótesis humanas
2. Por descubrimiento estadístico
3. Por clustering
4. Por AlphaEvolve
```

Aquí todavía NO existen estrategias.

Primero debemos responder:

```text
¿Qué eventos existen?
```

Los eventos iniciales son hipótesis humanas.  
Más adelante  Pattern Mining, Clustering y AlphaEvolve , podrán descubrir nuevas familias de eventos no definidas previamente.

**Ejemplos de eventos**

```text
PM_Squeeze_Event
Gap_And_Go_Event
Red_To_Green_Event
VWAP_Reclaim_Event
First_Green_Day_Event
SSR_Event
```


Un `EVENTO` describe

```
¿Qué está ocurriendo?
```

por ejemplo para `PM_Squeeze_Event`

```
Gap > 20%
Float < 20M
PM Volume > 500k
Primer Push > 15%
Pullback presente
HOD marcado
```

Todavía **NO** existe trade.  
Simplemente dices:

```
Esto parece un PM Squeeze.
```

Un `EVENTO` no es una estrategia porque no tiene trade. 

**Diferencia entra evento y estrategia**

```
Evento = fenómeno de mercado
Estrategia = respuesta operativa ante ese fenómeno
```
  
Una `ESTRATEGIA` describe:

``` 
¿Qué hago frente al evento?
```

Ejemplo: 

```sh
# PM_Squeeze_Strategy_v1
Entrada: Break HOD
Stop: Pullback Low
Salida: 3R
```

Ahora sí hay trade.

**Ejemplo**:   
Diferencia entra evento y estrategia.  
Supongamos:
```
PM_Squeeze_Event #34211
```

El evento es:

```
Gap = 75%
Float = 2M
PM Volume = 5M
Primer Push = 25%
Pullback = 7%
```
Eso es un hecho histórico.

Ahora puedes aplicar:

```
Strategy A
Break HOD
```
o

```
Strategy B
First Higher Low
```
o

```
Strategy C
VWAP Reclaim
```

sobre el mismo evento.

**Ejemplo estratura de carpetas**

```
13_TRADING_SYSTEMS
│
├── 01_EVENT_LIBRARY
│
├── 02_STRATEGY_LIBRARY
```

`AlphaEvolve` probablemente trabajará mucho mejor sobre:

```
event_table
```

que sobre:

```
strategy_table
```
Porque puede descubrir:

```
Una mejor definición
del evento PM_Squeeze
```

sin tocar todavía entradas y salidas.

---


Y cuanto más separadas estén ambas cosas en tu arquitectura, más fácil será hacer:

* Backtesting  
* Clustering  
* Pattern Mining  
* ML Supervisado  
* AlphaEvolve  
* Offline RL  

sin mezclar conceptos. Esa separación entre fenómeno observado y decisión tomada es muy típica de los sistemas cuantitativos más avanzados.

# CAPA 3 — EVENT ENGINE

## Objetivo

Transformar datos brutos de mercado en eventos estructurados que puedan ser investigados, comparados, agrupados y evaluados.

El Event Engine es el primer componente que convierte:

```text
Datos
    ↓
Conocimiento investigable
```

**Función principal**

Recorrer todo el histórico:

```text
2005-2026
```

y detectar automáticamente cada aparición de eventos definidos por el sistema.


**Inputs**

```text
master_daily_table
master_intraday_table
```

**Outputs**

```text
event_table
```

**¿Qué hace el Event Engine?**

Para cada día y para cada ticker:

```text
1. Evalúa definiciones de eventos
2. Detecta candidatos
3. Extrae atributos
4. Genera registros normalizados
```

**Ejemplo**

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

La definición de:

```text
PM_Squeeze_Event
```

se cumple.

Entonces genera:

```text
event_id = 12345
```

**Resultado**

```text
event_table
```

Ejemplo:

```text
event_id = 12345
ticker = ABCD
date = 2020-05-14
event_type = PM_Squeeze_Event
event_start = 09:34:12
event_end = 09:47:55
```

**Event Table**

Cada fila representa:

```text
Un evento observado 
en el mercado.
```

No representa:

```text
Un trade.
Una estrategia.
Una posición.
```

**Estructura conceptual de `event_table`**


```text
event_id
ticker
date
event_type
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
...
```

**Importancia**

Esta tabla se convierte en el activo más importante de TSIS.
A partir de ella se construyen: 

```text
Outcome Engine
Strategy Engine
Clustering
Pattern Mining
Machine Learning
AlphaEvolve
Offline RL
```

**Principio fundamental**

Un mismo evento puede ser utilizado por múltiples estrategias.

Ejemplo:

```text
PM_Squeeze_Event #12345
```

puede ser operado mediante:

```text
Break HOD
Higher Low
VWAP Reclaim
Tape Confirmation
```

Por tanto:

```text
Evento ≠ Estrategia
```

**Objetivo final**

Construir una representación estructurada de todos los fenómenos relevantes observados en el universo de Small Caps entre 2005 y 2026.

El Event Engine responde a la pregunta:

```text
¿Qué ocurrió?
```

Las capas posteriores responderán:

```text
¿Qué pasó después?
¿Qué patrones existen?
¿Qué decisión era óptima?
```


# CAPA 4 — OUTCOME RESEARCH

**Objetivo**

Medir qué ocurrió después de cada evento detectado.  
En esta fase todavía no evaluamos estrategias.  
No existen entradas.  
No existen stops.  
No existen salidas.  
Todavía no existe ningún trade.  

El objetivo es medir la evolución natural del evento.

**Filosofía**

El `Event Engine` responde:

```text
¿Qué ocurrió?
```

El `Outcome Engine` responde:

```text
¿Qué pasó después?
```


**Principio fundamental**

Un mismo evento puede producir resultados muy diferentes.

Ejemplo:

```text
PM_Squeeze_Event #1001
```

puede terminar:

```text
+10%
```

mientras que:

```text
PM_Squeeze_Event #1002
```

puede terminar:

```text
+150%
```

El objetivo del `Outcome Engine` es cuantificar esas diferencias.

**Inputs**

```text
event_table
```

**Outputs**

```text
outcome_table
```

**¿Qué hace el Outcome Engine?**

Para cada evento detectado:

```text
1. Observa la evolución posterior
2. Calcula métricas objetivas
3. Genera etiquetas de resultado
4. Almacena los outcomes
```

**Ejemplo**

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
Hace máximo a las 10:07
Cierra +22%
```

El Outcome Engine genera:

```text
max_extension = +65%
max_adverse_excursion = -12%
time_to_peak = 33 min
close_return = +22%
```

**Estructura conceptual de outcome_table**

```text
event_id
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
...
```

**Outcome Labels**

Los outcomes permiten crear etiquetas.

Ejemplo:

```text
Failed_Event
Weak_Event
Average_Event
Strong_Event
Exceptional_Event
```

o

```text
Top_1_Percent
Top_5_Percent
Top_10_Percent
```

**Ejemplo**

```text
event_id = 12345
max_extension = +140%
outcome_label = Exceptional_Event
runner_score = 0.98
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Resultado
```

**Importancia**

Esta es la primera vez que TSIS conecta:

```text
Contexto
      ↓
Outcome
```

Ejemplo:

```text
Gap = 80%
Float = 2M
PM Volume = 6M
```
↓
```text
+120%
```

---

Otro ejemplo:

```text
Gap = 25%
Float = 50M
PM Volume = 500k
```
↓
```text
-8%
```

**Preguntas que ahora podemos responder**

```text
¿Qué eventos producen los mayores runners?
¿Qué eventos fallan con más frecuencia?
¿Qué variables preceden los mayores squeezes?
¿Qué contextos generan los mejores resultados?
```

**Relación con las capas posteriores**

Una vez existe:

```text
event_table
```
y
```text
outcome_table
```
podemos construir:

```text
Pattern Mining
Clustering
Machine Learning
AlphaEvolve
Offline RL
Strategy Research
```

**Principio fundamental**

El Outcome Engine no evalúa decisiones.  
Evalúa consecuencias.  
No mide:

```text
¿Qué habría hecho el trader?
```

Mide:

```text
¿Qué hizo el mercado?
```

Esa separación es crítica porque permite estudiar el comportamiento real del mercado antes de introducir cualquier sesgo derivado de estrategias específicas.

# CAPA 5 — STRATEGY RESEARCH

**Objetivo**

Responder:

```text
¿La ventaja sobrevive en el tiempo?
```

Por primera vez introducimos decisiones operativas.

Hasta este punto TSIS ha estudiado:

```text
Qué ocurrió
```

y

```text
Qué pasó después
```

Ahora comenzamos a estudiar:

```text
¿Qué habría hecho un trader?
```

**Filosofía**

Las capas anteriores estudian el mercado.
Esta capa estudia decisiones.
Por primera vez aparecen:

```text
Entradas
Stops
Salidas
Gestión de posición
Gestión del riesgo
```


**Inputs**

```text
event_table
outcome_table
strategy_library
```

**Outputs**

```text
strategy_results
strategy_performance
walk_forward_results
```

**¿Qué es una estrategia?**

Una estrategia es una respuesta operativa frente a un evento.

Recordatorio:

```text
Evento
=
Fenómeno de mercado
```

```text
Estrategia
=
Respuesta operativa frente al fenómeno
```

**Ejemplo**

Evento:

```text
PM_Squeeze_Event
```

Estrategias:

```sh
# PM_Squeeze_Strategy_v1
Entrada: Break HOD
Stop: Pullback Low
Salida: 3R
```

```sh
# PM_Squeeze_Strategy_v2
Entrada: First Higher Low
Stop: Higher Low
Salida: 5R
```

Ambas estrategias pueden operar exactamente el mismo evento.

**Principio fundamental**

Un evento puede generar múltiples estrategias.

Ejemplo:

```text
PM_Squeeze_Event #12345
```
↓
```text
Break HOD
Higher Low
VWAP Reclaim
Tape Confirmation
SSR Reclaim
```
↓
```text
Resultados diferentes
```

**Backtesting clásico**

Las estrategias son evaluadas sobre el histórico completo.

Ejemplo:

```text
2005-2015 Train
2016 Test

2005-2016 Train
2017 Test

2005-2017 Train
2018 Test

...
```

pregunta principal

```text
¿La ventaja sobrevive en el tiempo?
```

**Métricas**

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
```

**Robustez**

No buscamos únicamente estrategias rentables.  
Buscamos estrategias robustas.

**Walk Forward**

```text
Train
    ↓
Test
```

en múltiples ventanas temporales.

**Anchored Walk Forward**

```text
2005-2015
       ↓
2016

2005-2016
       ↓
2017

2005-2017
       ↓
2018
```


**Stability Analysis**

Pregunta:

```text
¿La estrategia sigue funcionando
cuando modificamos ligeramente
sus parámetros?
```

**Parameter Surface Analysis**

Buscamos:

```text
Mesetas
```

No:

```text
Picos
```

---

Porque:

```text
Pequeños cambios
no deberían destruir el edge.
```

**Preguntas que esta capa responde**

```text
¿Funciona la estrategia?
¿La ventaja sobrevive en el tiempo?
¿La estrategia es robusta?
¿Qué variantes funcionan mejor?
¿Qué entradas son superiores?
¿Qué salidas son superiores?
```

**Lo que NO responde**

Esta capa todavía no responde:

```text
¿Por qué funciona?
¿Qué patrones existen?
¿Qué contexto produce los mejores runners?
```

Eso pertenece a:

```text
Pattern Mining
Clustering
Machine Learning
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Estrategia
      ↓
Performance
```

**Relación con las capas posteriores**

Una vez existen:

```text
event_table
outcome_table
strategy_results
```

podemos investigar:

```text
Qué eventos producen los mejores resultados
Qué contextos producen los mejores resultados
Qué patrones explican los mejores resultados
```

y comenzar el trabajo de:

```text
Pattern Mining
Clustering
Machine Learning
AlphaEvolve
Decision Models
```

**Principio fundamental**

El objetivo de esta capa no es descubrir conocimiento nuevo.

El objetivo es validar hipótesis humanas.

```text
Humano
      ↓
Hipótesis
      ↓
Backtest
      ↓
Validación
```

Las capas posteriores estarán enfocadas en descubrir conocimiento que inicialmente no forma parte de las hipótesis humanas.


# CAPA 6 — PATTERN DISCOVERY

**Objetivo**

Responder:

```text
¿Qué tienen en común
los mejores eventos?
```

Hasta este punto TSIS ha validado hipótesis humanas.  
Ahora comienza a buscar conocimiento nuevo dentro de los datos.  

**Cambio conceptual**

`Backtesting clásico`:

```text
Humano
    ↓
Hipótesis
    ↓
Test
    ↓
Resultado
```

`Pattern Discovery`:

```text
Datos
    ↓
Patrón
    ↓
Hipótesis
    ↓
Validación
```

---

La diferencia es fundamental.

En Backtesting:

```text
El humano propone.
```

En Pattern Discovery:

```text
Los datos sugieren.
```

**Inputs**

```text
event_table
outcome_table
strategy_results
```

**Objetivo principal**

Encontrar relaciones estadísticas que expliquen:

```text
Por qué algunos eventos
producen resultados excepcionales
y otros fracasan.
```

**Ejemplo**

Supongamos que analizamos:

```text
100.000 PM_Squeeze_Events
```

Descubrimos:

```text
80% de los runners >100%

ocurren cuando:

Float < 3M
PM Volume > 4M
Gap > 40%
```

Nadie programó esa regla.
La regla emerge de los datos.  


**Filosofía**

No buscamos:

```text
¿Funciona una estrategia?
```

Buscamos:

```text
¿Qué propiedades tienen
los eventos excepcionales?
```

**Preguntas que esta capa responde**

```text
¿Qué tienen en común los mejores squeezes?
¿Qué variables preceden los mayores runners?
¿Qué condiciones aparecen antes de los movimientos extremos?
¿Qué configuraciones del mercado generan las mayores probabilidades?
```

**Pattern Mining**

El sistema analiza:

```text
Contexto
Eventos
Outcomes
```

y busca:

```text
Frecuencias
Asociaciones
Correlaciones
Dependencias
Relaciones no obvias
```

**Ejemplos de descubrimientos**

```text
Float < 3M
```

```text
PM Volume / Float
```

```text
Distancia a VWAP
```

```text
Velocidad del Primer Push
```

```text
Número de intentos al HOD
```

Variables que inicialmente no formaban parte de ninguna hipótesis humana.

**Principio fundamental**

`Pattern Discovery` no produce estrategias.  
Produce conocimiento.  

Resultado:  

```text
Hipótesis nuevas
```

Ejemplo:

```text
Los runners >150% aparecen principalmente cuando:

Float < 2M
Gap > 50%
PM Volume > 5M
```

Esto NO es una estrategia.  
Es una observación estadística.  

**Relación con las capas posteriores**

Los patrones descubiertos alimentan:

```text
Clustering
Machine Learning
AlphaEvolve
Decision Models
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Patrón
```

**Diferencia con Strategy Research**

Strategy Research pregunta:

```text
¿Funciona esta idea?
```

Pattern Discovery pregunta:

```text
¿Qué está intentando decirnos el mercado?
```


**Principio fundamental**

El objetivo no es optimizar reglas existentes.  
El objetivo es descubrir estructura oculta dentro de los datos.  
Por primera vez en TSIS, el sistema puede generar hipótesis que nunca fueron propuestas por un operador humano.



# CAPA 7 — CLUSTER RESEARCH

**Objetivo**

Agrupar eventos por contexto.   

* No agrupamos tickers.  
* No agrupamos estrategias.  
* Agrupamos comportamientos.  


Hasta este punto TSIS ha descubierto patrones.

Ahora queremos responder:

```text
¿Existen familias distintas de eventos?
```

o

```text
¿Existen distintos tipos de PM Squeeze?
```


**Cambio conceptual**

`Pattern Discovery`:

```text
Evento
    ↓
Patrón
```

`Cluster Research`:

```text
Eventos
    ↓
Familias
```

La diferencia es importante.

Pattern Discovery busca:

```text
Relaciones
```

Cluster Research busca:

```text
Estructura
```

**Inputs**

```text
event_table
outcome_table
discovered_patterns
```

**Objetivo principal**

Encontrar grupos de eventos que comparten características similares.

No buscamos:

```text
Qué ticker es.
```

Buscamos:

```text
Qué tipo de comportamiento representa.
```

**Ejemplo**

Supongamos:

```text
100.000 PM_Squeeze_Events
```

El sistema descubre:

`Cluster A`

```text
Gap 50-80%
Float 2-5M
PM Volume >3M
Primer Push moderado
Pullback corto
```

`Cluster B`

```text
Gap >100%
Float <1M
PM Volume >10M
Primer Push explosivo
Spread amplio
```

`Cluster C`

```text
Gap 20-40%
Float >20M
PM Volume medio
Movimiento lento
```

Nadie definió estos grupos previamente.  
Emergen de los datos.  

**Filosofía**

No buscamos:

```text
¿Funciona una estrategia?
```

Buscamos:

```text
¿Qué tipos de eventos existen?
```

**Preguntas que esta capa responde**

```text
¿Existen familias distintas de PM Squeeze?
¿Existen tipos distintos de runners?
¿Qué clusters producen los mayores movimientos?
¿Qué clusters fracasan con más frecuencia?
¿Qué configuraciones de mercado se repiten?
```

**Clustering**

El sistema analiza:

```text
Contexto
Eventos
Outcomes
```

y busca:

```text
Similitud
Proximidad
Densidades
Regiones de comportamiento
```


**Ejemplos de clusters posibles**

```text
Low Float Momentum Cluster
```


```text
Parabolic Runner Cluster
```


```text
High Liquidity Gapper Cluster
```


```text
Failed Squeeze Cluster
```


```text
Multi-Day Runner Cluster
```


Los nombres son secundarios.  
Lo importante es que representan familias recurrentes de comportamiento.  


**Principio fundamental**

Un mismo evento humano puede contener múltiples subtipos.

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


**Ejemplo**

Supongamos:

```text
PM_Squeeze_Type_A
```

produce:

```text
Average Move = +120%
```


Mientras:

```text
PM_Squeeze_Type_C
```

produce:

```text
Average Move = +18%
```

Ahora ya no estamos estudiando simplemente PM Squeeze.  
Estamos estudiando qué versión de PM Squeeze tenemos delante.


**Relación con las capas posteriores**

Los clusters descubiertos alimentan:

```text
Machine Learning
AlphaEvolve
Decision Models
Offline RL
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Patrón
      ↓
Cluster
```

**Diferencia con Pattern Discovery**

`Pattern Discovery` pregunta:

```text
¿Qué tienen en común
los mejores eventos?
```


`Cluster Research` pregunta:

```text
¿Qué familias distintas
de eventos existen?
```


**Principio fundamental**

El objetivo no es descubrir reglas.  
El objetivo es descubrir categorías ocultas dentro del mercado.  

Por primera vez en TSIS dejamos de pensar en eventos individuales y  
comenzamos a pensar en poblaciones completas de comportamientos.



# CAPA 8 — MACHINE LEARNING

**Objetivo**

Modelar:

```text
Estado de mercado
        ↓
Resultado
```

Hasta este punto TSIS ha descubierto:

```text
Eventos
Outcomes
Patrones
Clusters
```

Ahora queremos construir modelos capaces de estimar probabilidades.


**Cambio conceptual**

Las capas anteriores responden:

```text
¿Qué ocurrió?
```

```text
¿Qué pasó después?
```

```text
¿Qué patrones existen?
```

```text
¿Qué familias existen?
```


`Machine Learning` responde:

```text
¿Qué es probable que ocurra?
```


**Inputs**

```text
Contexto
Evento
Cluster
Outcome Labels
```

**Objetivo principal**

Aprender relaciones entre:

```text
Estado del mercado
```
y  
```text
Resultado futuro
```


**Ejemplo**

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

No está tomando decisiones.    
Está estimando probabilidades.    


**Filosofía**

No buscamos:

```text
Comprar
Vender
```
Buscamos:

```text
Estimar
Clasificar
Predecir
```


**Preguntas que esta capa responde**

```text
¿Cuál es la probabilidad de éxito?
¿Cuál es la probabilidad de fracaso?
¿Cuál es la probabilidad de Top 1%?
¿Cuál es la probabilidad de un runner excepcional?
¿Qué variables explican más el resultado?
```

**Machine Learning**

El sistema analiza:

```text
Contexto
Eventos
Clusters
Outcomes
```

y aprende:

```text
Relaciones
Dependencias
Interacciones
Probabilidades
```

**Ejemplos de tareas**

Clasificación:

```text
Runner
No Runner
```

Clasificación:

```text
Top 1%
Top 5%
Top 10%
Normal
```

Regresión:

```text
Expected Move %
Expected Extension %
Expected MAE
Expected Time To Peak
```

Ranking:

```text
Ordenar eventos
por calidad esperada
```

**Outputs**

```text
Probabilidad de éxito
Probabilidad de runner
Probabilidad de Top 1%
Expected Move
Expected Extension
Expected Risk
```

**Ejemplo**

Evento:

```text
PM_Squeeze_Event #54218
```
Predicción:
```text
Success Probability = 81%
Top 5% Probability = 31%
Expected Extension = +87%
```

**Importancia**

Por primera vez TSIS deja de analizar únicamente el pasado.  
Comienza a realizar inferencias sobre eventos futuros.  


**Relación con las capas posteriores**

Los modelos generados alimentan:

```text
AlphaEvolve
Decision Models
Offline RL
Position Sizing
Risk Models
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Patrón
      ↓
Cluster
      ↓
Probabilidad
```

**Diferencia con Cluster Research**

Cluster Research` pregunta:
`
```text
¿Qué familias existen?
```

`Machine Learning` pregunta:

```text
¿A qué familia pertenece este evento?
```

y

```text
¿Qué resultado es más probable?
```

**Principio fundamental**

Machine Learning no toma decisiones.  
Machine Learning estima probabilidades.  
Las decisiones aparecen en las capas posteriores.  

Por primera vez TSIS puede evaluar un evento en tiempo real y   
asignarle una expectativa estadística basada en todo el conocimiento acumulado del sistema.


# CAPA 9 — DECISION MODELS

**Objetivo**

Responder:

```text
¿Cuál es la mejor decisión
posible ahora?
```

Hasta este punto TSIS ha aprendido:

```text
Qué ocurrió
Qué pasó después
Qué patrones existen
Qué familias existen
Qué resultado es probable
```

Ahora queremos optimizar decisiones.


**Cambio conceptual**

`Machine Learning`:

```text
Estado de mercado
        ↓
Predicción
```

`Decision Models`:

```text
Estado de mercado
        ↓
Acción
```

La diferencia es fundamental.

`Machine Learning` responde:

```text
¿Qué creo que ocurrirá?
```

`Decision Models` responden:

```text
¿Qué debería hacer?
```


**Inputs**

```text
Contexto
Evento
Cluster
Probabilidades ML
Outcome History
```

**Objetivo principal**

Aprender políticas de decisión.

Una política responde:

```text
Dado este contexto

¿Qué acción maximiza
el resultado esperado?
```

**Ejemplo**

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
¿Va a funcionar?
```

El problema es:

```text
¿Dónde entro?
¿Cuánto riesgo tomo?
¿Cuándo salgo?
¿Debo operar?
```

**Filosofía**

No buscamos:

```text
Predecir
```

Buscamos:

```text
Decidir
```

**Preguntas que esta capa responde**

```text
¿Debo entrar?
¿Debo esperar?
¿Qué entrada es mejor?
¿Qué stop es mejor?
¿Qué salida es mejor?
¿Cuánto capital debo asignar?
¿Vale la pena operar este evento?
```

**Decision Models**

El sistema analiza:

```text
Contexto
Eventos
Clusters
Probabilidades
Resultados históricos
```

y aprende:

```text
Políticas
Acciones
Secuencias de decisión
```

**Tecnologías**

```text
Offline RL
Decision Transformer
CQL
IQL
```

**Offline RL**

Aprende políticas a partir de datasets históricos.  
No necesita interactuar con el mercado real.   

Problema que intenta resolver:

```text
¿Qué habría hecho un agente óptimo?
```

**Decision Transformer**

Reformula el problema como:

```text
Historia
      ↓
Próxima acción
```

Aprende directamente desde secuencias de eventos.

**CQL**

`Conservative Q-Learning`

Objetivo:

```text
Evitar decisiones fuera de distribución.
```

Especialmente importante en trading.


**IQL**

`Implicit Q-Learning`

Objetivo:

```text
Aprender de buenos ejemplos
sin necesidad de explorar.
```

Muy interesante para:

```text
Trades de traders expertos
```

**Ejemplo**

Supongamos:

```text
100.000 PM_Squeeze_Events
```

El modelo descubre:

```text
En Cluster_A

Break HOD
supera sistemáticamente

a

VWAP Reclaim
```

O:

```text
En Cluster_B

Esperar Higher Low

genera mejor expectancy.
```

Nadie programó esas reglas.  
La política emerge de los datos.  


**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Patrón
      ↓
Cluster
      ↓
Probabilidad
      ↓
Decisión
```


**Diferencia con Machine Learning**

`Machine Learning` pregunta:

```text
¿Qué resultado es probable?
```

`Decision Models` preguntan:

```text
¿Qué acción maximiza
el resultado esperado?
```


**Relación con las capas posteriores**

Los modelos de decisión alimentan:

```text
AlphaEvolve
Execution Models
Position Sizing
Autonomous Agents
```

**Principio fundamental**

Machine Learning aprende el mercado.  
Decision Models aprenden decisiones.  

Por primera vez en TSIS el objetivo deja de ser comprender el mercado y  
pasa a ser actuar de forma óptima dentro de él.


# CAPA 10 — EVOLUTION SYSTEMS

**Objetivo**

Evolucionar automáticamente:

```text
Detectores de eventos
Features
Clusters
Filtros
Estrategias
Reglas de entrada
Reglas de salida
Modelos
Políticas de decisión
```

Hasta este punto TSIS dispone de un laboratorio completo.

Ahora queremos que el sistema genere hipótesis nuevas y las valide automáticamente.


**Cambio conceptual**

Las capas anteriores funcionan así:

```text
Humano
      ↓
Idea
      ↓
Implementación
      ↓
Evaluación
```

`Evolution Systems` introduce:

```text
Sistema
      ↓
Hipótesis
      ↓
Evaluación
      ↓
Selección
      ↓
Nueva hipótesis
```

Por primera vez el sistema participa activamente en el proceso de investigación.


**Filosofía**

No buscamos:

```text
Validar ideas humanas.
```

Buscamos:

```text
Generar ideas nuevas.
```

**Inputs**

```text
event_table
outcome_table
cluster_table
ml_models
decision_models
strategy_library
```

**Objetivo principal**

Explorar espacios de búsqueda demasiado grandes para ser recorridos manualmente.

Ejemplo:

Un investigador humano puede probar:

```text
10
50
100
```

variantes.

Un sistema evolutivo puede explorar:

```text
10.000
100.000
1.000.000
```
variantes.


**Tecnologías**

```text
AlphaEvolve
OpenEvolve
```

**¿Qué es un sistema evolutivo?**

Un sistema evolutivo combina:

```text
Generación
Evaluación
Selección
Mutación
Iteración
```

Ciclo general:

```text
Hipótesis
      ↓
Evaluación
      ↓
Score
      ↓
Mutación
      ↓
Nueva hipótesis
```

**Ejemplo 1 — Evolución de eventos**

Definición inicial:

```text
Gap > 20%
Float < 20M
PM Volume > 500k
```

Después de miles de iteraciones:

```text
Gap > 45%
Float < 5M
PM Volume > 3M
Primer Push > 20%
```

El sistema descubre una definición más útil.


**Ejemplo 2 — Evolución de Features**

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

Variables que inicialmente no existían.



**Ejemplo 3 — Evolución de estrategias**

Versión inicial:

```text
Break HOD
Stop Pullback Low
Target 3R
```

Después de múltiples generaciones:

```text
First Higher Low
Dynamic Stop
Volatility Exit
```

El sistema descubre nuevas variantes.


**Ejemplo 4 — Evolución de políticas**

El sistema modifica:

```text
Entradas
Salidas
Position Sizing
Risk Allocation
```

para maximizar resultados históricos.


**Requisito fundamental**

Los sistemas evolutivos necesitan un laboratorio previamente construido.

Necesitan:

```text
event_table
outcome_table
strategy_evaluator
```

Porque toda hipótesis debe poder ser evaluada objetivamente.  
Sin evaluador:

```text
No existe evolución.
```

**Preguntas que esta capa responde**

```text
¿Puede una variante superar a la hipótesis humana?
¿Existe una mejor definición del evento?
¿Existen mejores features?
¿Existen mejores filtros?
¿Existen mejores estrategias?
¿Existen mejores decisiones?
```

**Resultado conceptual**

Ahora tenemos:

```text
Evento
      ↓
Outcome
      ↓
Patrón
      ↓
Cluster
      ↓
Probabilidad
      ↓
Decisión
      ↓
Evolución
```

**Diferencia con Decision Models**

`Decision Models` preguntan:

```text
¿Cuál es la mejor decisión
dado el conocimiento actual?
```

`Evolution Systems` preguntan:

```text
¿Cómo podemos mejorar
el propio conocimiento?
```

**Principio fundamental**

El objetivo no es optimizar una única estrategia.
El objetivo es evolucionar continuamente el laboratorio completo de investigación.
Por primera vez en TSIS el sistema no solo aprende del mercado.
También aprende a mejorar la forma en que aprende del mercado.


