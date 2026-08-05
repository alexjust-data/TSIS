# La idea central

`Market State` y `Event State` **no sustituyen el backtest clásico** ni producen edge por existir.

Su función es convertir cada oportunidad histórica en una observación científica:

```text
Se produjo una oportunidad de estrategia E
en el instante t
bajo este estado observable X_t
y después ocurrió este resultado Y.
```

El backtest clásico responde:

```text
¿Esta política concreta habría ganado dinero?
```

Los estados permiten responder algo más profundo:

```text
¿En qué contextos esta señal tiene edge?
¿En cuáles deja de tenerlo?
¿Qué variables modifican su distribución de resultados?
¿Debe operarse, ignorarse, priorizarse o dimensionarse de otra manera?
```

Tu arquitectura ya establece correctamente que `Market State` describe el mercado observable en `t`, mientras que `Event State` contextualiza ese mismo estado respecto a un evento, separando además las filas utilizables para decidir de las reservadas a investigación posterior. 

---

# 1. Tres experimentos diferentes

Para cada estrategia deben existir tres etapas claramente separadas.

## A. Reproducción mecánica

Primero se implementa exactamente la estrategia publicada o descrita:

```text
datos históricos
↓
reglas mecánicas congeladas
↓
órdenes
↓
fills
↓
posiciones
↓
PnL
```

Aquí `Market State` y `Event State` no deben modificar la decisión.

El objetivo es demostrar:

```text
La estrategia está completamente definida.
El motor reproduce legalmente sus decisiones.
Las órdenes y salidas funcionan.
El resultado base es reproducible.
```

## B. Ejecución observacional

Después se vuelve a ejecutar la misma estrategia, pero los estados se adjuntan como información de investigación:

```text
la estrategia sigue tomando exactamente las mismas operaciones
+
se captura el estado observable en cada oportunidad
```

Los estados todavía **no filtran ni cambian** ninguna operación.

Así puedes descubrir qué caracteriza:

* las operaciones ganadoras;
* las perdedoras;
* los grandes recorridos favorables;
* los fakeouts;
* las operaciones imposibles de ejecutar;
* los resultados por fase del pump.

## C. Estrategia condicionada

Sólo después se permite que los estados cambien la política:

```text
operar / no operar
priorizar
dimensionar
modificar entrada
seleccionar salida
```

Esta tercera versión es una estrategia nueva y debe validarse fuera de muestra frente a la estrategia base.

---

# 2. Cómo cubrir mecánicamente cada estrategia antes de optimizar

Tus documentos de small caps describen correctamente las estrategias en términos de `Trigger`, `Confirmación` y `Riesgo`, pero todavía contienen expresiones discrecionales como:

```text
nivel importante
volumen convincente
explosión de volatilidad
primer dip
sobreextensión interesante
precio separándose con violencia
bastante tiempo bajo VWAP
```

Por ejemplo, el breakout exige una resistencia, volumen, confirmación y entrada en el primer dip; las estrategias short exigen extensión, pérdida de interés, overhead y confirmaciones como VWAP o Green-to-Red.   El PDF utiliza la misma estructura conceptual de trigger, confirmación e invalidación, pero varias condiciones siguen siendo cualitativas. 

Antes de optimizar, cada estrategia necesita un contrato mecánico con estos elementos:

| Componente          | Pregunta que debe quedar cerrada                                       |
| ------------------- | ---------------------------------------------------------------------- |
| Universo            | ¿Qué acciones podían pertenecer al universo en ese momento?            |
| Setup previo        | ¿Qué condiciones permiten empezar a observar la estrategia?            |
| Nivel de referencia | ¿Cómo se calcula exactamente PMH, VWAP, breakout, overhead, open, HOD? |
| Evento candidato    | ¿Qué condición objetiva declara que existe una oportunidad?            |
| Confirmación        | ¿Qué debe suceder después para autorizar una entrada?                  |
| Decision timestamp  | ¿En qué instante exacto se conoce la señal?                            |
| Orden               | ¿Market, limit, stop, bid, ask?                                        |
| Vigencia            | ¿Cuántos segundos o barras permanece activa?                           |
| Entrada             | ¿Primer cruce, primer dip, cierre de barra, siguiente apertura?        |
| Invalidación        | ¿Qué hecho destruye la tesis?                                          |
| Salidas             | Stop, target, tiempo máximo, cierre de sesión, salida parcial          |
| Reentradas          | Número máximo de intentos, cooldown, pyramiding                        |
| Ejecución           | Spread, slippage, halts, gaps, partial fills, SSR, locate              |
| Tamaño              | Riesgo fijo, nominal fijo, liquidez máxima                             |
| Ambigüedades        | Variantes explícitas que todavía no pueden resolverse                  |

Una frase ambigua no debe convertirse silenciosamente en una optimización.

Debe convertirse en variantes separadas:

```text
BREAKOUT_CONFIRMATION_V1
= cierre de una barra de 1m por encima del nivel

BREAKOUT_CONFIRMATION_V2
= precio permanece dos barras por encima

BREAKOUT_CONFIRMATION_V3
= ruptura + volumen mayor que referencia congelada
```

Cada variante es una hipótesis distinta, no un único sistema al que se le busca retrospectivamente la mejor combinación.

---

# 3. Los atributos de Market State no son hiperparámetros

Esta distinción es fundamental.

## Atributos observados

```text
gap_pct
relative_volume
spread_bps
distance_to_vwap
distance_to_hod
float_rotation
price_acceleration
news_age
market_cap
```

Son características del mercado. No se “optimizan”; se observan.

## Parámetros de estrategia

```text
lookback = 20
entry_buffer = 1 tick
stop_distance = 2 ATR
max_holding = 15 minutos
```

Son decisiones operativas.

## Hiperparámetros de un modelo

```text
tree_depth
regularization
learning_rate
number_of_trees
sequence_length
```

Controlan cómo aprende un modelo.

## Umbrales de política

```text
operar sólo si predicted_EV > 0
spread_bps < límite
probabilidad_de_target > 0.62
```

Transforman una predicción en una decisión.

La ventaja de haber construido cientos de atributos no consiste en optimizarlos todos.

Consiste en poder estimar:

[
E[Y\mid \text{evento},X_t]
]

donde:

* (X_t) es el estado observable;
* (Y) es el resultado posterior.

---

# 4. No debes construir estados solamente para entradas y salidas

Para auditar una estrategia, tener el estado de sus entradas y salidas es suficiente.

Para descubrir edge, **no lo es**.

Debes construir estados para todas las oportunidades candidatas, incluidas las que finalmente:

* no activaron entrada;
* fueron canceladas;
* no tuvieron fill;
* resultaron ser fakeouts;
* fueron rechazadas por un filtro;
* produjeron una señal mientras ya existía otra posición.

De lo contrario sólo observarás los casos seleccionados por la estrategia actual y no podrás descubrir correctamente cómo debería cambiar el filtro.

La población correcta es:

```text
TODOS LOS EVENTOS CANDIDATOS
├── activados
│   ├── con fill
│   └── sin fill
├── no confirmados
├── expirados
├── rechazados
└── ambiguos / no ejecutables
```

Para cada candidato:

```text
event_id
strategy_id
instrument_id
candidate_timestamp
confirmation_timestamp
decision_timestamp
entry_timestamp
event_status
market_state_id
event_state_window
outcome_id
```

---

# 5. Qué debe contener el outcome

No conviene definir el resultado solamente como el PnL de la salida elegida por la estrategia.

Eso mezcla:

```text
calidad de la señal
+
calidad de la entrada
+
calidad de la salida
```

Para cada evento candidato debes calcular outcomes neutrales:

```text
return_1m
return_5m
return_15m
return_30m
MFE
MAE
time_to_MFE
time_to_MAE
target_1R_before_stop
target_2R_before_stop
breakout_failed
VWAP_lost
new_HOD_reached
halt_after_signal
fill_possible
estimated_slippage
```

Después, en una capa separada, calculas el PnL de la política:

```text
entrada concreta
+
stop concreto
+
target concreto
+
costes
```

Así puedes descubrir, por ejemplo:

```text
La señal sí predice movimiento favorable,
pero la salida original destruye el edge.
```

o:

```text
La señal no tiene información;
el beneficio aparente procede de una salida favorable al régimen.
```

---

# 6. Cómo se extrae ventaja de los estados

Supongamos un evento `Breakout`.

El edge base sería:

[
EV_0=E[R_{net}\mid Breakout]
]

Después estudias regiones del estado:

[
EV_A=E[R_{net}\mid Breakout,X_t\in A]
]

Y su aportación incremental:

[
\Delta EV_A=EV_A-EV_0
]

`Market State` es útil solamente cuando esa diferencia:

```text
es económicamente relevante
+
se mantiene en periodos posteriores
+
sobrevive a costes
+
no depende de tres observaciones extremas
```

## Nivel 1 — Análisis condicional sencillo

Antes de usar machine learning:

```text
breakout por run_day
breakout por gap bucket
breakout por relative_volume
breakout por distancia a VWAP
breakout por número de intentos
breakout con/sin catalyst
breakout con/sin dilution risk
breakout por spread
breakout por hora
breakout por float rotation
```

No se busca automáticamente el mejor bucket. Se comprueba si existe una relación estable y coherente.

## Nivel 2 — Interacciones

Es posible que ninguna variable aislada produzca edge, pero sí su combinación:

```text
primer día del run
+
volumen histórico
+
primer intento
+
spread ejecutable
+
sin overhead cercano
```

Aquí entran modelos como:

```text
logistic regression
GAM
árboles pequeños
gradient boosting
random forest
```

El modelo no entrega una estrategia. Estima algo como:

```text
P(target antes que stop | estado)
E[MFE | estado]
E[retorno neto | estado]
```

Luego tú conviertes esa estimación en política:

```text
si EV estimado > umbral:
    operar
si no:
    ignorar
```

## Nivel 3 — Ranking

Cuando hay varias oportunidades simultáneas:

```text
ordena los candidatos por EV esperado
y opera sólo los mejores dentro del presupuesto
```

Para tu universo de 4.800 compañías, el ranking puede ser más útil que un simple filtro binario.

## Nivel 4 — Tamaño

Después de demostrar estabilidad:

```text
size mayor:
    buen EV
    incertidumbre baja
    spread reducido
    profundidad suficiente

size menor:
    EV positivo pero ejecución débil
```

El tamaño nunca debería depender sólo de la probabilidad de acierto; también debe considerar pérdida esperada, colas, liquidez y concentración.

## Nivel 5 — Política dinámica

Finalmente puedes permitir que nuevos estados posteriores a la entrada modifiquen la salida:

```text
mantener
reducir
cerrar
añadir
mover stop
```

Eso deja de ser un filtro de entrada y se convierte en una política secuencial. Debe reproducirse estado a estado dentro del `EventLoop`, no mediante un join posterior.

---

# 7. Ejemplo concreto: Breakout de una small cap

## Evento

```text
event_type = breakout_candidate
event_timestamp = primer cruce del nivel
```

## Market State en la decisión

```text
run_day
gap_pct
multi_day_extension
distance_to_vwap
distance_to_hod
relative_volume
volume_acceleration
spread_bps
quoted_depth
float_rotation
market_cap_asof
news_presence
news_age
dilution_context
overhead_distance
halt_state
time_of_day
sector_activity
```

## Event State

```text
distance_to_breakout_level
time_since_first_test
breakout_attempt_number
pre_break_consolidation_duration
pre_break_range_contraction
volume_change_from_setup
state_role = pre_event / at_event
event_phase = setup / break / first_dip / failure
```

## Outcomes

```text
ruptura confirmada
máximo recorrido tras ruptura
retroceso hasta el nivel
primer dip ejecutable
target antes que stop
tiempo hasta fakeout
slippage de entrada
halt posterior
retorno neto
```

Entonces puedes comparar:

```text
Breakout mecánico original
```

contra:

```text
Breakout sólo en primer intento
Breakout sin overhead cercano
Breakout con spread ejecutable
Breakout en frontside
Breakout en primer día del run
Breakout con combinación de estados
```

No porque esas condiciones “suenen bien”, sino porque su mejora debe aparecer en desarrollo y mantenerse en validación y test.

---

# 8. Para pump-and-dumps, la unidad estadística no es cada barra

Tu dataset puede contener millones de barras y miles de señales, pero la muestra efectiva es mucho menor.

Doscientas señales del mismo ticker durante el mismo pump no son doscientas observaciones independientes.

La unidad económica debería agruparse como:

```text
pump_episode_id
run_id
ticker-cycle
```

Y dentro de cada episodio:

```text
frontside
climax
transition
backside
destruction
first bounce
```

La validación debe impedir que barras o eventos del mismo pump aparezcan simultáneamente en train y test.

También deben agruparse o purgarse:

* eventos del mismo ticker muy cercanos;
* sympathy plays del mismo sector;
* múltiples señales durante el mismo régimen;
* oportunidades solapadas temporalmente.

De lo contrario, el modelo memorizará el episodio en vez de aprender una relación generalizable.

---

# 9. Similitud con alta frecuencia

Sí existe una similitud profunda.

| Alta frecuencia                      | TSIS                                                |
| ------------------------------------ | --------------------------------------------------- |
| Estado del order book en (t)         | Market State en (t)                                 |
| Estado respecto a una orden o evento | Event State                                         |
| Next-tick return / fill probability  | MFE, MAE, retorno, target-before-stop               |
| Modelo de alpha                      | Predictor de outcome condicionado                   |
| Política de quoting/ejecución        | Entrada, filtro, size y salida                      |
| Simulador de colas e impacto         | Backtester con quotes, spread, halts, SSR y locates |
| Latencia de señal                    | `state_available_at`                                |
| Walk-forward                         | Walk-forward temporal por episodios                 |

La forma científica es la misma:

```text
estado observable
↓
predicción de distribución futura
↓
política
↓
simulación de ejecución
↓
PnL neto
```

La diferencia principal no es conceptual, sino de régimen:

```text
HFT:
muchísimas decisiones,
horizontes cortísimos,
libro de órdenes,
colas y latencia extrema.

TSIS:
eventos más escasos,
horizontes mayores,
halts,
dilución,
locates,
cambios estructurales,
dependencia entre episodios.
```

Los equipos HFT tampoco “optimizan todos los parámetros y ya está”. Separan:

```text
calidad predictiva de la señal
calidad de la política
calidad de la ejecución
costes e impacto
```

Y validan cada parte.

---

# 10. Validación adecuada para 2005–2026

Tu inclusión de compañías deslistadas elimina una fuente importante de survivorship bias, pero además necesitas:

```text
universe point-in-time
market cap point-in-time
float y fundamentals as-of
corporate actions
símbolos y cambios de ticker
news disponible en t
```

Para las estrategias de las revistas de 2015 existe una oportunidad especialmente limpia:

```text
1. Replicar el periodo publicado.
2. Congelar reglas y parámetros.
3. Probar desde la fecha de publicación hasta 2026.
```

Ese tramo postpublicación puede funcionar como verdadero test histórico fuera de muestra.

Para el playbook actual de small caps, que contiene ejemplos y conocimiento hasta 2026, el periodo histórico completo ya ha influido potencialmente en la definición. Puede utilizarse para investigación y walk-forward, pero no debería llamarse un holdout completamente virgen. El test realmente limpio tendrá que ser un segmento congelado no consultado o datos futuros posteriores a la preregistración.

---

# 11. Flujo profesional recomendado

```text
1. STRATEGY SOURCE
   revista / playbook

2. MECHANICAL STRATEGY CONTRACT
   reglas completas y variantes congeladas

3. BASELINE BACKTEST
   sin Market State ni Event State como filtros

4. CANDIDATE EVENT REGISTRY
   todas las oportunidades, no sólo trades

5. STATE ATTACHMENT
   Market State en cada decision_timestamp
   Event State en ventanas relativas

6. OUTCOME TABLE
   MFE, MAE, retornos, fillability y outcomes

7. CONDITIONAL RESEARCH
   qué estados cambian la distribución

8. MODEL / RANKER
   entrenado solamente en train

9. POLICY
   operar, ignorar, priorizar o dimensionar

10. OUT-OF-SAMPLE BACKTEST
    ejecución y costes completos

11. COMPARISON
    estrategia base vs estrategia condicionada
```

La regla que debe gobernar todo el proceso es:

```text
La estrategia clásica define cuándo existe una oportunidad.

Market State describe el contexto observable.

Event State alinea y contextualiza la oportunidad.

Outcome mide lo que sucedió.

El modelo estima qué contextos contienen edge.

La política convierte esa estimación en una decisión.

El backtester comprueba si sobrevive después de ejecución y costes.
```

# Siguiente paso técnico correcto

No necesitas añadir más atributos antes de demostrar este circuito.

El siguiente incremento debería utilizar **una sola estrategia**:

```text
estrategia mecánica congelada
↓
todos sus eventos candidatos
↓
Market State en el instante de decisión
↓
Event State pre/at-event
↓
outcomes independientes
↓
backtest base
↓
primer análisis condicional
```

Tu propio documento ya establece que los estados son opcionales para un backtest mecánico, que deben entrar mediante replay causal y que nunca deben proporcionar directamente el precio de ejecución. Esa separación es exactamente la adecuada. 
