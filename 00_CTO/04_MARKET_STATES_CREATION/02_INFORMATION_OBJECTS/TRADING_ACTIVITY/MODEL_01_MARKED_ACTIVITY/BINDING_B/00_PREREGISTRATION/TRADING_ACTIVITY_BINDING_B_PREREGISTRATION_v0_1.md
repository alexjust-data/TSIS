# Trading Activity Binding B preregistration v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_binding_b_preregistration` |
| `document_version` | `v0_1` |
| `document_role` | `DRAFT_EXPERIMENTAL_BINDING_PREREGISTRATION_PROPOSAL` |
| `document_status` | `DRAFT_FOR_HUMAN_AND_SCIENTIFIC_REVIEW_NOT_FROZEN` |
| `information_object_id` | `trading_activity` |
| `binding_id_proposed` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `representation_proposed` | `PIT_NORMALIZED_EVENT_TIME_MARKED_RENEWAL_AND_BURST_STATE` |
| `comparison_incumbent` | `trading_activity_binding_a_candidate_v0_2` |
| `binding_a_final_verdict` | `PASS_WITH_SCOPE_RESTRICTIONS` |
| `binding_a_percentile_replay` | `PASS_EXACT_240_BLOCKS_2400_SESSIONS` |
| `binding_a_final_manifest_sha256` | `634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857` |
| `inherited_incident_controls` | `RM-MAT-CTRL-001..006_MUST_BE_BOUND_BEFORE_FREEZE` |
| `implementation_authorized` | `false` |
| `long_materialization_authorized` | `false` |
| `temporal_oos_authorized` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## Regla de lectura

Este documento clona y convierte en artefacto versionado la propuesta
científica recibida para Binding B. Todavía no es una especificación física
congelada. Todas las cantidades, variables, escalas, thresholds, métricas,
márgenes y splits descritos como propuestas deben cerrarse mediante revisión
humana y científica antes de cambiar el estado a `FROZEN`.

No autoriza implementación, probes, materialización larga, comparación A/B ni
apertura de ningún lockbox OOS.

## Veredicto científico

He revisado el paquete de Binding A. Mi propuesta es que Binding B **no sea A con otras ventanas ni con más percentiles**. Debe ser un challenger metodológicamente distinto que represente el mismo objeto científico:

```text
Information Object
=
Trading Activity
```

```text
Significado mínimo
=
participación negociada observable
+
intensidad
+
escala temporal explícita
+
trading realizado
+
legalidad point-in-time
```

Debe seguir dejando fuera:

```text
dirección del precio
retornos
spread
depth
aggressor side
signed flow
OFI
scanner selection
outcomes futuros
```

porque esos conceptos pertenecen a otros Information Objects o a otras capas.

Mi candidato sería:

```text
binding_id
=
trading_activity_binding_b_event_time_renewal_burst_v0_1
```

```text
representation
=
PIT-NORMALIZED EVENT-TIME
MARKED RENEWAL AND BURST STATE
```

La hipótesis no es que B sea necesariamente mejor. Es:

> Binding B podría detectar antes y representar mejor la forma interna del cambio de actividad porque utiliza tiempo de eventos, decaimiento continuo, compresión de duraciones y tiempo económico, mientras Binding A depende principalmente de ventanas rectangulares de reloj.

---

# 1. Qué hace bien Binding A

Binding A ya es una representación seria y rica. No es simplemente volumen acumulado.

Congela:

```text
decision grid
=
symbol-second

clock windows
=
5s, 15s, 30s, 60s, 300s

short/long contrasts
=
5s / 60s
15s / 300s
```

Y materializa:

```text
número de trades
share volume
dollar volume
trade arrival rate
median/p10 intertrade duration
largest-trade share
actividad por subventanas
concentración
persistencia de subventanas activas
percentiles PIT
log-ratios respecto al baseline
contrastes multiescala
```

Además, utiliza baselines `B20`, `B60` y `B120`, siendo `B60` el principal, con población prior-only del mismo instrumento, minuto RTH, horizonte, policy de latencia y schema. Esto está especificado rigurosamente en la [especificación exacta de Binding A](TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md).

A también conserva correctamente:

```text
actividad absoluta
intensidad
marks
concentración temporal
sorpresa relativa
transición multiescala
```

Por eso B no debe competir proponiendo simplemente:

```text
ventana de 3 segundos
ventana de 10 segundos
otro RVOL
otro z-score fijo
```

Eso sería una variante de A, no un challenger independiente.

---

# 2. La limitación principal de Binding A

Binding A observa el proceso a través de **ventanas rectangulares fijadas por el reloj**:

```text
(t - W, t]
```

Esto introduce varias limitaciones potenciales.

## Efectos de borde

Un burst puede comenzar justo antes del borde de una ventana:

```text
burst real:
09:42:04.800 → 09:42:06.300
```

En una rejilla de un segundo, parte de la actividad puede quedar repartida de manera distinta entre ventanas contiguas, aunque el fenómeno económico sea prácticamente el mismo.

## Formas temporales distintas pueden producir agregados similares

Estas dos situaciones pueden tener:

```text
20 trades en 5 segundos
```

pero no son equivalentes:

```text
Caso 1:
20 trades distribuidos uniformemente

Caso 2:
18 trades en 200 ms
+
2 trades durante los 4,8 segundos siguientes
```

A incorpora concentración por subventanas, lo cual ayuda, pero la geometría sigue estando determinada por buckets de uno o cinco segundos.

## La llegada de eventos es endógena

El reloj informativo del mercado no siempre es el reloj cronológico.

```text
5 segundos en ticker dormido
=
quizá cero trades

5 segundos en activación
=
cientos de trades
```

Por eso Binding B debería representar directamente:

```text
cuánto tarda en llegar la información;
cómo se comprime el tiempo entre eventos;
cómo se encadenan los bursts;
cómo decae la actividad;
cuánto tiempo económico tarda en negociarse
una cantidad material.
```

Los modelos ACD formalizan el tratamiento estocástico de duraciones irregulares y tasas condicionales; los procesos autoexcitados ofrecen otra forma de representar clustering de eventos. Para B usaría una construcción no paramétrica inspirada en esos principios y reservaría un Hawkes completo para un posible Binding C. ([Engle y Russell, NBER Working Paper 4966][1])

---

# 3. Qué debe conservar Binding B

Binding B debe seguir representando todas las dimensiones exigidas por el mismo Representation Model:

```text
ABSOLUTE ACTIVITY
EVENT INTENSITY
ACTIVITY MARKS
TEMPORAL CONCENTRATION
RELATIVE SURPRISE
PERSISTENCE / DECAY
```

La base científica define Trading Activity como un **marked activity process relativo al baseline**, y contempla expresamente tres posibles implementaciones:

```text
A
=
rolling counts and volumes

B
=
conditional duration / intensity estimates

C
=
self-exciting point-process estimates
```

sin cambiar la identidad del modelo conceptual. [Base científica de los Representation Models](../REPRESENTATION_MODELS.md)

---

# 4. Construcción elemental de Binding B

Binding B debe aplicar primero exactamente las mismas reglas de:

```text
trade eligibility
source observability
simulated latency
RTH scope
missingness
coverage
duplicate policy
PIT baseline
```

Solo después cambia la representación.

## 4.1 Timestamp clusters

La fuente legacy contiene trades con timestamps idénticos y no posee un sequence/order causal completo. Binding A ordena ties mediante `physical_row_ordinal`, pero reconoce que eso no es una secuencia económica.

Binding B debería evitar inferir duraciones falsas de cero entre filas cuyo orden real desconocemos.

Agruparía todos los trades elegibles con el mismo `legacy_event_time` en un **timestamp cluster**:

```text
cluster j

τ_j
=
timestamp del cluster

n_j
=
número de trades del cluster

q_j
=
share volume del cluster

v_j
=
dollar volume del cluster
```

Y:

```text
Δ_j
=
τ_j - τ_(j-1)
```

La regla sería:

```text
same-timestamp trades
=
preservados como marks dentro del cluster

within-cluster causal order
=
not claimed
```

Esto utiliza honestamente la resolución disponible.

## 4.2 Rejilla de salida

Para comparar A y B sin cambiar el experimento:

```text
output decision grid
=
la misma rejilla symbol-second de Binding A
```

La diferencia es:

```text
Binding A
=
calcula en ventanas rectangulares

Binding B
=
mantiene un proceso continuo en event time
y lo proyecta sobre la misma rejilla de decisión
```

Así cualquier diferencia de resultado se atribuye a la representación, no a una población o frecuencia de muestreo distinta.

---

# 5. Propuesta exacta de variables de Binding B

Dividiría la materialización en:

```text
PRIMARY REPRESENTATION FEATURES
+
MANDATORY RAW/AUDIT COMPANIONS
+
DIAGNOSTIC-ONLY VARIABLES
```

Los tres grupos se congelan antes de materializar, pero solo el primero entra en la comparación principal.

---

## Familia B1 — Reloj de eventos y renovación

Estas variables representan cuánto tarda en llegar nueva participación.

| Variable | Definición |
|---|---|
| `time_since_last_trade_cluster_us` | Microsegundos desde `τ_last` hasta `t`. |
| `elapsed_time_last_5_clusters_us` | `τ_last - τ_(last-4)`. |
| `elapsed_time_last_20_clusters_us` | Tiempo necesario para observar los últimos 20 clusters. |
| `elapsed_time_last_50_clusters_us` | Tiempo necesario para observar los últimos 50 clusters. |
| `last_intercluster_duration_us` | Último `Δ_j`. Audit companion. |

Interpretación:

```text
menos tiempo para acumular K clusters
=
más intensidad de participación realizada
```

Estas variables son distintas de:

```text
trade_count_5s
```

porque mantienen fijo el número de eventos y dejan variar el tiempo, en lugar de fijar el tiempo y contar eventos.

---

## Familia B2 — Tiempo operacional PIT

Necesitamos normalizar las duraciones contra el régimen esperado del instrumento.

Definiría una intensidad baseline prior-only:

```text
λ0(instrument, RTH minute, baseline candidate)
```

estimada únicamente con las sesiones anteriores admitidas bajo `B20`, `B60` o `B120`.

Para cada duración:

```text
rescaled_duration_j
=
∫[τ_(j-1), τ_j] λ0(u) du
```

Con baseline aproximadamente constante dentro del bucket:

```text
rescaled_duration_j
≈
λ0 × Δ_j
```

Variables principales:

| Variable | Significado |
|---|---|
| `rescaled_duration_current_B60` | Duración actual expresada en unidades de actividad esperada. |
| `operational_time_compression_20_B60` | `-log(median(rescaled_duration_last_20))`. |
| `fast_rescaled_duration_fraction_20_B60` | Fracción de las últimas 20 duraciones más rápidas que el nivel preregistrado. |
| `fast_rescaled_duration_run_length_B60` | Longitud de la secuencia consecutiva de duraciones anormalmente cortas. |
| `baseline_zero_fraction_B60` | Masa de actividad cero del contexto PIT. |
| `silence_break_surprise_B60` | Sorpresa de observar actividad cuando el baseline estaba dominado por silencio. |

### Baseline con actividad cero

No aplicaría un floor oculto para fabricar una intensidad.

Si el baseline no permite estimar `λ0`:

```text
operational-time variables
=
NULL

baseline_state
=
ZERO_DOMINATED
o
BASELINE_INSUFFICIENT_HISTORY
```

Pero sí se conserva:

```text
baseline_zero_fraction
```

y una variable separada de ruptura del silencio, con fórmula congelada.

Esto evita que el ticker más muerto del universo produzca un score infinito por una sola operación.

---

## Familia B3 — Intensidades con kernel continuo

En lugar de incluir o excluir abruptamente eventos al cruzar el borde de una ventana, utilizaría kernels exponenciales.

Para mark `m_j`:

```text
K_m,τ(t)
=
Σ [m_j × exp(-(t - τ_j) / τ)] / τ
```

Escalas preregistradas propuestas:

```text
τ
=
2s, 10s, 60s
```

Y `300s` como escala secundaria de contexto.

### Trade intensity

```text
m_j = n_j
```

Variables principales:

```text
trade_kernel_surprise_2s_B60
trade_kernel_surprise_10s_B60
trade_kernel_surprise_60s_B60

trade_kernel_log_ratio_2s_60s
=
log(
  (trade_kernel_intensity_2s + ε)
  /
  (trade_kernel_intensity_60s + ε)
)
```

La sorpresa se calcularía como robust z-score PIT de:

```text
log1p(trade_kernel_intensity_τ)
```

contra el mismo baseline prior-only de instrumento, minuto y policy.

### Dollar activity

```text
m_j = v_j
```

Variables:

```text
dollar_kernel_surprise_2s_B60
dollar_kernel_surprise_10s_B60
dollar_kernel_surprise_60s_B60

dollar_kernel_log_ratio_2s_60s
```

### Share activity

Como companion para no perder la semántica de acciones negociadas:

```text
share_kernel_surprise_10s_B60
share_kernel_surprise_60s_B60
```

Los valores raw de todos los kernels también deben materializarse como campos de auditoría:

```text
trade_kernel_intensity_τ
share_kernel_rate_τ
dollar_kernel_rate_τ
```

No son sustituibles únicamente por sus z-scores.

---

## Familia B4 — Tiempo económico

Esta familia responde:

> ¿Cuánto tiempo tarda el ticker en negociar una cantidad económicamente normal para su contexto?

Definimos provisionalmente:

```text
U_B60
=
mediana PIT positiva
del dollar volume de 60 segundos
para el mismo contexto
```

Y:

```text
elapsed_time_to_pit_dollar_unit_us
=
tiempo necesario para acumular U_B60
```

Variable normalizada:

```text
dollar_clock_compression_B60
=
log(
  60 segundos
  /
  elapsed_time_to_pit_dollar_unit
)
```

Interpretación:

```text
> 0
=
negocia una unidad económica normal
más rápidamente de lo esperado

< 0
=
la negocia más lentamente
```

Esto es especialmente útil para comparar:

```text
ticker de $0,50
vs.
ticker de $15
```

sin depender únicamente de número de acciones.

---

## Familia B5 — Distribución de marks por cluster

Estas variables distinguen participación amplia de actividad concentrada en uno o pocos timestamps.

| Variable | Definición |
|---|---|
| `cluster_dollar_hhi_20` | HHI de dollar volume entre los últimos 20 clusters. |
| `top3_cluster_dollar_share_20` | Proporción del dollar volume atribuida a los tres clusters mayores. |
| `median_dollar_per_trade_20` | Mediana de dollar size por trade en los últimos 20 clusters. |
| `dollar_mark_shift_robust_z_20_B60` | Cambio robusto en el tamaño económico de los marks frente al baseline. |

Estas variables no intentan inferir:

```text
comprador
vendedor
agresor
dirección
```

Solo describen la textura de la participación realizada.

---

## Familia B6 — Persistencia, decaimiento y reactivación

| Variable | Significado |
|---|---|
| `trade_intensity_slope_event_time_20` | Pendiente robusta de intensidad sobre los últimos 20 clusters. |
| `current_to_recent_peak_trade_intensity_50` | Intensidad actual dividida por la intensidad máxima observada durante los últimos 50 clusters. |
| `burst_age_us` | Tiempo desde que comenzó la secuencia de duraciones rápidas vigente. |
| `burst_reactivation_count_300s` | Número de reactivaciones separadas por silencios preregistrados dentro de 300 segundos. Diagnostic-only inicialmente. |

Interpretación:

```text
ratio próximo a 1
=
la intensidad sigue en máximos recientes

ratio bajo
=
el burst está decayendo
```

Esto representa una dimensión que A captura solo indirectamente mediante las subventanas activas.

---

# 6. Esquema primario recomendado

Mantendría un núcleo de unas veinte variables para evitar que B se convierta en una biblioteca abierta.

## Primary Binding B

```text
1.  time_since_last_trade_cluster_us
2.  elapsed_time_last_5_clusters_us
3.  elapsed_time_last_20_clusters_us
4.  elapsed_time_last_50_clusters_us

5.  rescaled_duration_current_B60
6.  operational_time_compression_20_B60
7.  fast_rescaled_duration_fraction_20_B60
8.  fast_rescaled_duration_run_length_B60
9.  baseline_zero_fraction_B60
10. silence_break_surprise_B60

11. trade_kernel_surprise_2s_B60
12. trade_kernel_surprise_10s_B60
13. trade_kernel_surprise_60s_B60
14. trade_kernel_log_ratio_2s_60s

15. dollar_kernel_surprise_2s_B60
16. dollar_kernel_surprise_10s_B60
17. dollar_kernel_surprise_60s_B60
18. dollar_kernel_log_ratio_2s_60s

19. dollar_clock_compression_B60
20. cluster_dollar_hhi_20
21. top3_cluster_dollar_share_20
22. current_to_recent_peak_trade_intensity_50
```

## Secondary preregistered sensitivity

```text
share_kernel_surprise_10s_B60
share_kernel_surprise_60s_B60
trade_intensity_slope_event_time_20
median_dollar_per_trade_20
dollar_mark_shift_robust_z_20_B60

trade/dollar kernels τ=300s
short-long ratios 10s/300s

B20
B120

latency sensitivity 100ms
latency sensitivity 5000ms
duplicate-exclusion sensitivity
```

La selección principal no puede abrir estas variables una vez observados los resultados. Deben figurar desde el preregistro como:

```text
primary
secondary
diagnostic-only
```

---

# 7. Por qué B es realmente distinto de A

| Dimensión | Binding A | Binding B propuesto |
|---|---|---|
| Reloj interno | Tiempo cronológico fijo | Tiempo de eventos y tiempo económico |
| Agregación | Ventanas rectangulares | Decaimiento continuo |
| Unidad de burst | Subventanas de 1s/5s | Secuencia de clusters y duraciones |
| Intensidad | Count / W | Renewal intensity y kernels |
| Baseline | Percentiles de agregados | Duraciones reescaladas + kernel surprise |
| Concentración | Shares por subventanas | Distribución de marks por timestamp cluster |
| Persistencia | Subventanas activas consecutivas | Run length, slope y decay respecto al peak |
| Ties | Duraciones cero por ordinal físico | Cluster único sin afirmar orden causal |
| Materialidad económica | Dollar volume por ventana | Reloj de acumulación de unidad económica PIT |

Binding B no corrige a A.

Plantea una respuesta alternativa a la misma pregunta:

```text
A:
¿Cuánta actividad hubo en las últimas W unidades de reloj?

B:
¿A qué velocidad endógena está llegando
y acumulándose la participación,
cómo se agrupa,
y cómo está evolucionando el burst?
```

---

# 8. Por qué no recomiendo Hawkes como Binding B principal

Un Hawkes completo sería metodológicamente independiente, pero no es la mejor primera alternativa con la fuente legacy actual.

La fuente presenta:

```text
timestamps colapsados desde varias columnas;
ties;
ausencia de sequence causal gobernado;
physical_row_ordinal no causal;
latencia simulada;
RTH legacy;
duplicados preservados.
```

Un modelo Hawkes podría interpretar como autoexcitación una estructura introducida por:

```text
resolución temporal;
timestamps empatados;
duplicados;
orden físico;
reconciliación del proveedor.
```

Por eso recomendaría:

```text
Binding B
=
event-time renewal
+
nonparametric exponential kernels
+
PIT rescaling
+
economic time
```

Y reservar:

```text
Binding C
=
parametric ACD / Hawkes / BOCPD candidate
```

para una fuente enriquecida con:

```text
event timestamp autoritativo;
sequence;
trade ID;
arrival timestamp;
mejor tratamiento de corrections/duplicates.
```

Un `log-ACD` reducido puede ejecutarse como **diagnóstico secundario de B**, pero no como la identidad de su materialización principal.

---

# 9. Qué no puede entrar en Binding B

Para mantener la validez discriminante de `Trading Activity`, excluiría expresamente:

```text
midprice return
price velocity
HOD distance
VWAP distance
spread
depth
quote update rate
OFI
aggressor buy ratio
signed dollar imbalance
news
halts
wake-up detector score
500k scanner flag
event labels
future continuation
future return
MFE / MAE
```

Algunas podrían mejorar la detección de Wake-up, pero demostrarían valor del **perfil combinado**, no de Trading Activity.

La comparación A/B debe responder exclusivamente:

> ¿Qué representación de Trading Activity es mejor?

No:

> ¿Qué conjunto general de datos detecta mejor Wake-up?

---

# 10. Diseño correcto de la comparación A/B

Hay una precisión crítica sobre OOS.

El lifecycle vigente exige:

```text
1. Construir A en development.
2. Construir B en la misma población y periodos.
3. Comparar candidatos sin abrir el lockbox final.
4. Seleccionar un candidato.
5. Evaluar únicamente el seleccionado
   en el temporal OOS final intacto.
```

Esto aparece explícitamente en el [lifecycle A→B](../EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_2.md).

Por tanto, propondría distinguir y congelar antes de cualquier comparación:

```text
TEMPORAL VALIDATION OOS
=
se usa para comparar A y B

FINAL TEMPORAL OOS LOCKBOX
=
solo lo abre el candidato seleccionado
```

No debemos ejecutar A y B repetidamente sobre el lockbox final y escoger después. Eso convertiría el OOS en otro development set.

---

## 10.1 Población idéntica

A y B deben usar exactamente:

```text
mismos instrument_id
mismas session_date
mismos symbol-seconds
mismo target manifest
mismo denominator manifest
mismos positivos
mismos negativos
mismos unavailable/degraded states
misma eligibility policy
misma latency policy
misma duplicate policy
mismos baselines B20/B60/B120
```

No:

```text
A en una población
B en otra más favorable
```

---

## 10.2 Detector común

Para comparar representaciones no conviene permitir que cada Binding utilice un clasificador completamente distinto.

Propondría:

### Primary probe

```text
regularized discrete-time hazard/logistic probe
```

Baja capacidad, mismo presupuesto de búsqueda y misma regularización para ambos.

### Sensitivity probe

```text
shallow gradient-boosted tree
```

Con el mismo número de trials y límites de profundidad.

Si B solo gana con un modelo mucho más complejo, no queda claro si gana la representación o el detector.

---

## 10.3 Presupuesto común de falsas alarmas

El threshold de cada Binding se calibra en development para alcanzar exactamente el mismo presupuesto:

```text
false activations
per million eligible symbol-seconds
```

o el presupuesto operacional que ya esté congelado.

Después se comparan:

```text
median detection delay
p90 detection delay
wake-up recall
missed episodes
lead frente al scanner 500k
false alerts por sesión
máxima carga diaria
persistence after alert
coverage
degraded/unavailable rate
```

La comparación al mismo accuracy o al mismo threshold no sería justa. Debe ser al mismo coste de falsa alarma.

---

## 10.4 Estratificación

Como mínimo:

```text
año
precio
market cap
actividad baseline
zero-dominated vs non-zero baseline
hora/minuto RTH
ticker nuevo vs historial amplio
cantidad de trades
dollar-volume regime
source/schema regime
```

Y los casos negativos deben incluir:

```text
dormant symbol-seconds
un solo print grande
actividad dispersa sin burst
burst breve que desaparece
actividad alta pero normal para el ticker
duplicados
same-timestamp clusters
RTH open con historial insuficiente
data gaps
```

---

# 11. Criterio de selección

Congelaría una regla parecida a esta antes de materializar B:

```text
Binding B solo puede sustituir a Binding A si:

1. Pasa todos los hard gates:
   semántica,
   temporalidad,
   missingness,
   determinismo,
   lineage,
   incident controls.

2. Mantiene el mismo false-alarm budget.

3. Es no inferior en recall.

4. Mejora materialmente el detection delay
   en la validación temporal.

5. No empeora de forma material el p90/p95 de delay.

6. La mejora aparece en varios strata
   y no en un único año o ticker.

7. La cobertura y el coste computacional
   permanecen dentro del presupuesto.

8. La ventaja sobrevive a las ablations
   de variables más importantes.
```

Como margen preliminar —que debe aprobarse antes del run— utilizaría algo como:

```text
recall noninferiority
=
no peor que A por más de 2 puntos porcentuales

median delay improvement
=
al menos 1 segundo
o 10 % relativo

coverage noninferiority
=
no peor por más de 1 punto porcentual
```

Estos valores son una propuesta de preregistro, no una decisión vigente.

Si A y B son estadísticamente equivalentes:

```text
gana A por parsimonia,
menor complejidad
y mayor madurez operativa
```

No se crea automáticamente:

```text
Binding A + Binding B
```

Una combinación sería:

```text
Binding C
```

y exigiría un nuevo preregistro.

---

# 12. Controles heredados obligatorios

Binding B debe importar y probar explícitamente:

```text
RM-MAT-CTRL-001
typed metadata vs family counts

RM-MAT-CTRL-002
exact target membership;
no inferir targets por min/max date

RM-MAT-CTRL-003
una única autoridad de cardinalidad

RM-MAT-CTRL-004
identidad compuesta;
no confiar en ordinal

RM-MAT-CTRL-005
lectura explícita de Parquet;
no Hive inference accidental

RM-MAT-CTRL-006
validator ligado a spec y SHA exactos
```

Cada variable debe pasar:

```text
unit test
boundary test
zero/missingness test
same-timestamp test
PIT test
one production-equivalent probe per shard
terminal certifier rehearsal
```

El [registro institucional de incidentes](../REPRESENTATION_MODEL_MATERIALIZATION_INCIDENT_REGISTER_v0_1.md) deja claro que estos controles no son documentación opcional: son aprendizaje institucional de incidentes.

---

# 13. Qué debe ocurrir antes de congelar B

El orden correcto es:

```text
1. Referenciar el full percentile replay terminal PASS de A.

2. Ligar el final manifest exacto:
   634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857

3. Congelar la población exacta
   para comparación A/B.

4. Revisar y congelar este artefacto:
   TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md

5. Congelar:
   variables;
   fórmulas;
   K;
   τ;
   baseline;
   floors;
   missingness;
   schemas;
   primary/secondary/diagnostic sets;
   common detector heads;
   metrics;
   false-alarm budgets;
   selection margins;
   strata;
   temporal splits.

6. Implementar kernel y tests.

7. Ejecutar probe por variable y shard.

8. Auditar el terminal certifier.

9. Emitir autorización separada
   para la materialización completa B.

10. Materializar B.

11. Comparar A/B en development
    y temporal validation OOS.

12. Seleccionar.

13. Abrir el final temporal OOS lockbox
    únicamente para el ganador.
```

El full replay de A ya terminó `PASS_EXACT`: 240/240 bloques, 2.400/2.400 sesiones, 3.351.960.000 celdas percentile y cero diferencias. Binding B referencia el [readout terminal exacto](TRADING_ACTIVITY_BINDING_A_INDEPENDENT_PERCENTILE_REPLAY_FULL_EXECUTION_READOUT_v0_1.md), no un heartbeat intermedio.

---

# Recomendación final

Mi propuesta es:

```text
BINDING A
=
FIXED CLOCK MULTISCALE
RECTANGULAR WINDOW REPRESENTATION
```

```text
BINDING B
=
PIT-NORMALIZED EVENT-TIME
MARKED RENEWAL AND BURST REPRESENTATION
```

Binding B debe intentar superar a A en:

```text
detección temprana;
forma del burst;
compresión del tiempo;
persistencia;
decaimiento;
comparabilidad entre tickers;
reducción de artefactos de bordes temporales.
```

Pero debe preservar exactamente:

```text
el mismo Information Object;
la misma legalidad;
la misma población;
los mismos outcomes;
el mismo presupuesto de falsas alarmas;
la misma disciplina OOS.
```

La frase rectora para su prerregistro sería:

> Binding B representa Trading Activity mediante la velocidad endógena de llegada y acumulación de participación negociada, la compresión PIT del tiempo entre eventos, la intensidad continua de los marks y la persistencia o decadencia del burst; no mediante un segundo conjunto de ventanas fijas.

El siguiente gate es cerrar las decisiones abiertas, emitir una revisión
versionada y obtener autorización humana explícita para cambiar este artefacto a
`FROZEN`. Hasta entonces:

```text
implementation = NOT_AUTHORIZED
probe execution = NOT_AUTHORIZED
long materialization = NOT_AUTHORIZED
A/B comparison = NOT_AUTHORIZED
temporal OOS = NOT_AUTHORIZED
```

[1]: https://www.nber.org/papers/w4966 "Autoregressive Conditional Duration: A New Model for Irregularly Spaced Transaction Data"
