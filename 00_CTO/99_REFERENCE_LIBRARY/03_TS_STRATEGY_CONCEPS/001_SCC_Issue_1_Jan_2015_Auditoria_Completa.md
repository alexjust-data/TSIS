# Auditoría completa — TradeStation Strategy Concepts Club, Issue 1 (enero de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. Relative Performance Strength Strategy
2. Moving Average Channel Strategy
3. ideas secundarias de backtesting presentes en el issue
4. auditoría metodológica
5. contratos de réplica para TSIS
6. planes de falsificación y validación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 16 páginas: `SCC Issue 1 Jan 2015.pdf`
- ZIP original de apoyo: `2015-01.zip`
- Workspace y `.ELD` de ambas estrategias
- Markdown de ejemplo aportado por el usuario, utilizado como **modelo de profundidad**, no como autoridad factual

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma o muestra la revista

PACKAGE:
lo que confirman los archivos .tsw / .ELD

AUDIT:
inferencia técnica, crítica científica y propuesta TSIS
```

Cuando el PDF o el paquete no resuelven una decisión, se registra como ambigüedad. No se completa silenciosamente.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo | Evidencia publicada | Riesgo principal | Decisión |
|---|---|---|---|---|---|
| 001 | Relative Performance Strength | Mean reversion, equities, daily | PF 2.24, 71 trades, un solo par optimizado | ratio de retornos inestable, selección in-sample, single-leg | Replicar y falsificar post-2015 |
| 002 | Moving Average Channel | Trend following, ES 15m | PF 1.11, 1,280 trades | esperanza ≈ 1 tick, sin slippage publicado, continuo sintético | Replicar con máxima prioridad en costes y roll |

## 0.1 Veredicto global

El issue contiene dos estrategias **implementables**, pero ninguna queda científicamente validada por la publicación.

La primera presenta una cifra de rendimiento atractiva, pero con una formulación matemática frágil y una muestra pequeña. La segunda posee una muestra mucho mayor y una lógica clara, pero su beneficio medio equivale aproximadamente a un tick por operación, por lo que cualquier error de ejecución puede eliminarlo.

```text
ISSUE_STATUS:
VALUABLE_SOURCE_MATERIAL

EDGE_STATUS:
UNPROVEN

IMPLEMENTATION_STATUS:
TWO_REPRODUCTION_CANDIDATES

LIVE_STATUS:
NOT_ELIGIBLE
```

---

# Parte I — Estrategia 001: Relative Performance Strength Strategy

## 1) Identificación y rendimiento

- **ID de estrategia:** `SCC-2015-01-STRAT-001`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 1
- **Fecha de publicación:** 14 de enero de 2015
- **Artículo:** *Relative Performance Strength Strategy*
- **Autor correcto:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 4–8
- **Páginas impresas del artículo:** 2–6
- **Estilo declarado:** Mean reversion
- **Mercado declarado:** Equities
- **Horizonte declarado:** Swing trading
- **Frecuencia:** Daily
- **Activo operado en el ejemplo:** Visa (`V`)
- **Activo de referencia:** Mastercard (`MA`)
- **Archivos auxiliares del ZIP:** estrategia/indicador `.ELD` y workspace `.tsw`

### Resultados destacados publicados

- **Profit Factor:** 2.24
- **Percent Profitable:** 64.79%
- **RINA Index:** 473.14
- **Operaciones:** 71
- **Beneficio neto:** $1,405.78
- **Trading period efectivo mostrado:** 4 años y 2 días
- **Tiempo en mercado:** 7.38%
- **Comentario visual del artículo:** curva globalmente ascendente, drawdowns pequeños descritos como cercanos al 5%, comportamiento cíclico y varios periodos sin actividad.

### Evidencia adicional del ZIP

El workspace `TSL Relative Performance Strength.tsw` confirma, mediante sus metadatos internos legibles:

```text
Data1 / chart principal: V, Daily, NYSE, Visa Inc.
Data2: MA, NYSE, Mastercard Inc.
Inputs aplicados:
Length
AvgLength
StdDevLength
StdDevNum
```

También contiene referencias a la estrategia y al indicador homónimos. Sin embargo, el `.ELD` es un contenedor binario de TradeStation: no equivale a una exportación de código fuente legible fuera de la plataforma. Por ello, el ZIP mejora la trazabilidad, pero **no elimina por sí solo las ambigüedades algorítmicas**.

> Corrección respecto del Markdown de ejemplo: la cabecera original atribuía por error esta estrategia a Stanley Dash, al mercado de futuros y a un horizonte no detectado. El PDF identifica inequívocamente a Frederic Palmliden, acciones y swing trading.

### Veredicto inicial

| Cuestión                                        | Conclusión                                                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| ¿Puede implementarse en TSIS?                   | **Sí, fácilmente.**                                                                                                 |
| ¿Podemos replicar aproximadamente el artículo?  | **Sí.** La réplica exacta exige importar el `.ELD` en TradeStation o disponer de una exportación legible del código. El ZIP aportado conserva el `.ELD`, pero en este entorno es un binario compilado y no permite auditar directamente la lógica fuente.                                     |
| ¿El artículo demuestra científicamente un edge? | **No.** Muestra un único backtest optimizado sobre V/MA.                                                            |
| ¿La tesis económica es plausible?               | **Sí:** reversión de divergencias entre empresas relacionadas.                                                      |
| ¿La formulación matemática es sólida?           | **Tiene un problema grave:** divide un retorno por otro retorno.                                                    |
| ¿Está preparada para operar en real?            | **No.** Primero necesita réplica, falsificación y validación fuera de muestra.                                      |
| ¿Merece estudiarse?                             | **Sí.** Es un candidato especialmente interesante porque podemos hacer un verdadero test postpublicación 2015–2026. |

La clasificación correcta dentro de TSIS sería:

```text
SOURCE_REPRODUCTION_CANDIDATE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 1. Qué estrategia es realmente

TradeStation la presenta como:

```text
Estilo: Mean Reversion
Mercado: Acciones
Horizonte: Swing trading
Frecuencia de datos: Daily
```

La tesis declarada es:

```text
Dos acciones muy correlacionadas suelen seguir estando correlacionadas.

Cuando su rendimiento relativo alcanza un extremo
respecto de su comportamiento histórico,
la divergencia tiende a revertir.
```

El ejemplo utiliza:

```text
Activo operado: Visa, V
Activo de referencia: Mastercard, MA
```

Pero hay una distinción fundamental:

> **No es originalmente una estrategia de pairs trading.**

Utiliza dos activos para producir la señal, pero **solamente compra o vende V**. No abre simultáneamente una posición opuesta en MA.

Por tanto, conserva:

```text
exposición al mercado
exposición al sector
beta de Visa
riesgo direccional
riesgo overnight
```

El propio artículo propone como mejora abrir la posición contraria en el segundo activo para convertirla en una estrategia de pares más convencional. También advierte que invertir el orden V/MA no produce automáticamente las señales opuestas, porque cada orientación constituye una estrategia independiente. 

---

## 2. Reconstrucción matemática

### 2.1 Rendimientos de ambos activos

Con `Length = 7`, la interpretación compatible con el texto es:

\[
r^A_t=\frac{C^A_t}{C^A_{t-7}}-1
\]

\[
r^B_t=\frac{C^B_t}{C^B_{t-7}}-1
\]

donde:

```text
A = activo operado, V
B = activo de referencia, MA
C = cierre diario
```

La función estándar `RateOfChange` de EasyLanguage calcula precisamente:

\[
100\left(\frac{P_t}{P_{t-L}}-1\right)
\]

El factor 100 desaparece cuando se divide un ROC por el otro. ([Ayuda TradeStation][1])

### 2.2 Relative Performance Strength

\[
RPS_t=\frac{r^A_t}{r^B_t}
\]

No es:

```text
RSI
precio A / precio B
diferencia entre rendimientos
spread cointegrado
residuo de una regresión
```

Es específicamente:

```text
retorno acumulado de A durante 7 barras
dividido por
retorno acumulado de B durante 7 barras
```

### 2.3 Banda histórica

Los parámetros publicados son:

| Parámetro      | Valor | Función                            |
| -------------- | ----: | ---------------------------------- |
| `Length`       |     7 | Retorno acumulado de ambos activos |
| `AvgLength`    |    15 | Media móvil del RPS                |
| `StdDevLength` |   250 | Desviación histórica del RPS       |
| `StdDevNum`    |  0.75 | Anchura de la banda                |

La reconstrucción más probable es:

\[
\mu_t=MA_{15}(RPS_t)
\]

\[
\sigma_t=SD_{250}(RPS_t)
\]

\[
Upper_t=\mu_t+0.75\sigma_t
\]

\[
Lower_t=\mu_t-0.75\sigma_t
\]

Si el código utiliza la función estándar `StdDev` de EasyLanguage, se trata de desviación estándar poblacional, con divisor (N). ([Ayuda TradeStation][2])

Hay que confirmarlo importando el `.ELD` en TradeStation o mediante una exportación legible, porque el PDF describe el cálculo pero no imprime el código.

### 2.4 Warm-up

Para obtener la primera banda válida se necesitan aproximadamente:

```text
7 barras para formar el primer retorno
+
250 observaciones del RPS
```

Por eso el informe muestra cinco años de datos cargados, pero solamente unos cuatro años efectivos de trading.

---

## 3. Reglas exactas de entrada y salida

### 3.1 Detección de extremo

```text
outside_t =
    RPS_t > Upper_t
    OR
    RPS_t < Lower_t
```

### 3.2 Filtro de tendencia

El artículo dice que cuando el RPS permanece fuera de la banda durante dos barras consecutivas se considera que está “trending”.

La interpretación mínima sería:

```text
trending_t = outside_t AND outside_t-1
eligible_t = outside_t AND NOT trending_t
```

Esto significa que se intenta operar solamente la primera aparición del extremo y no perseguir una divergencia persistente.

Sin el código original quedan dos posibilidades:

```text
A. Dos barras fuera de cualquier banda
B. Dos barras consecutivas fuera del mismo lado de la banda
```

Esta ambigüedad debe quedar representada como una decisión contractual y no resolverse silenciosamente.

### 3.3 Dirección

La banda que se rompe **no determina la dirección**.

La dirección depende de qué activo haya rendido más durante los siete días:

```text
Si rA < rB:
    comprar A

Si rA > rB:
    vender A en corto
```

La lógica completa es:

```text
LONG:
outside_t
AND NOT trending_t
AND rA_t < rB_t

SHORT:
outside_t
AND NOT trending_t
AND rA_t > rB_t
```

### 3.4 Temporización

La señal se conoce al cierre del día (t):

```text
Cierre t:
calcular RPS y generar señal

Apertura t+1:
entrar

Apertura t+2:
salir
```

Por tanto:

```text
holding period = una barra diaria
return target = open-to-open
```

No es una operación close-to-open. Incluye:

```text
sesión regular completa de t+1
+
overnight de t+1 a t+2
```

No utiliza:

```text
stop loss
profit target
salida por convergencia del RPS
```

Todas las posiciones se liquidan obligatoriamente en la apertura siguiente. 

---

## 4. Ejemplo del artículo

En el ejemplo:

```text
V, rendimiento 7 días  = +3.20%
MA, rendimiento 7 días = +0.67%
```

Entonces:

\[
RPS=\frac{3.20}{0.67}\approx4.77
\]

La banda superior era aproximadamente:

```text
Upper = 2.48
```

Como:

```text
RPS > Upper
V ha rendido más que MA
RPS no está clasificado como trending
```

la estrategia:

```text
vende V en corto en la siguiente apertura
y cubre en la apertura posterior.
```

El artículo explica que también vendería V si:

```text
V  = +3.20%
MA = -0.67%
```

porque:

\[
RPS\approx-4.77
\]

En ese caso rompería la banda inferior, pero V seguiría siendo el activo que más ha rendido.

Esto confirma que:

> La posición depende de `rV > rMA` o `rV < rMA`; no del signo del RPS.

---

## 5. Resultados publicados

Configuración:

```text
Periodo de datos: 5 años
Informe: 30/09/2009–30/09/2014
Trading efectivo: aproximadamente 4 años y 2 días
Capital inicial: $7,000
Tamaño por operación: $5,000
Comisión: $0.01 por acción
Slippage: $0.01 por acción
```

### Resultado agregado

| Métrica                      |        Resultado |
| ---------------------------- | ---------------: |
| Operaciones                  |               71 |
| Ganadoras                    |               46 |
| Perdedoras                   |               25 |
| Porcentaje ganador           |           64.79% |
| Beneficio neto               |        $1,405.78 |
| Profit Factor                |             2.24 |
| Ganancia media               |           $55.11 |
| Pérdida media                |          -$45.17 |
| Ratio ganancia/pérdida       |             1.22 |
| Expectativa media            |           $19.80 |
| Retorno sobre $7,000         |           20.08% |
| Retorno anual indicado       |            4.57% |
| Tiempo en mercado            |            7.38% |
| Rina Index                   |           473.14 |
| Drawdown aproximado descrito | alrededor del 5% |

Con un nominal de $5,000:

\[
\frac{19.80}{5000}=0.00396
\]

La expectativa publicada equivale aproximadamente a:

```text
39.6 puntos básicos por operación
```

La curva de capital de la página 8 es ascendente, pero muestra largos periodos planos y un comportamiento cíclico. El propio autor advierte que debe esperarse un Profit Factor inferior con datos reales y con otros activos. 

### Resultado long frente a short

| Métrica                |    Long V | Short V |
| ---------------------- | --------: | ------: |
| Operaciones            |        36 |      35 |
| Beneficio neto         | $1,158.17 | $247.61 |
| Profit Factor          |      3.57 |    1.37 |
| Porcentaje ganador     |    72.22% |  57.14% |
| Expectativa media      |    $32.17 |   $7.07 |
| Ratio ganancia/pérdida |      1.37 |    1.02 |

Esto es extremadamente importante:

```text
82.4% del beneficio neto provino de las operaciones long.
```

El lado short produjo solamente:

```text
$7.07 por operación
≈ 14.1 puntos básicos sobre $5,000
```

Ese margen podría desaparecer con una pequeña diferencia de datos, apertura, spread o slippage.

Por tanto, el resultado publicado **no demuestra una reversión simétrica** entre outperformers y underperformers.

---

## 6. ¿Dónde estaría el edge?

La hipótesis real podría formularse así:

> Cuando una empresa se desvía anormalmente de una compañía económicamente relacionada, una parte de la desviación es temporal e idiosincrática y se corrige durante la siguiente sesión open-to-open.

El posible mecanismo económico podría proceder de:

```text
sobre-reacción temporal
presión transitoria de órdenes
liquidez desigual
reajustes de cartera
información que se incorpora de forma asíncrona
reversión idiosincrática de corto plazo
```

Pero el documento **no demuestra cuál de estos mecanismos produce el beneficio**.

Tampoco demuestra que el beneficio provenga realmente de la relación V–MA. Podría proceder de:

```text
reversión propia de Visa
tendencia alcista estructural de Visa
sesgo del lado long
efecto overnight
efecto de apertura
selección favorable del periodo
selección favorable del par
optimización de parámetros
```

La evidencia académica demuestra que ciertas familias de pairs trading pueden haber generado rentabilidades, pero utiliza metodologías distintas. Gatev, Goetzmann y Rouwenhorst construyeron carteras autofinanciadas long/short, seleccionaron pares por distancia entre precios normalizados y realizaron pruebas bootstrap; no utilizaron esta división de retornos ni operaron una sola pata. ([OUP Academic][3])

Investigaciones posteriores encontraron que la rentabilidad del pairs trading descendió con el tiempo y que tendía a mejorar en periodos prolongados de turbulencia. ([CFA Institute Research and Policy Center][4]) Después de comisiones, impacto y costes de short, Do y Faff encontraron beneficios mucho más modestos y señalaron que estas estrategias fueron en gran medida no rentables después de 2002. ([Monash University][5])

Avellaneda y Lee utilizan residuos de modelos factoriales y carteras market-neutral, tratando explícitamente de separar el componente idiosincrático del movimiento sistemático. Esa aproximación está científicamente mucho más próxima a la tesis que queremos comprobar que la simple correlación entre dos acciones. ([Departament de Matemàtiques NYU][6])

En consecuencia:

> La literatura respalda la posibilidad general de reversión relativa, pero **no valida esta fórmula concreta ni sus cuatro parámetros**.

---

## 7. Problema matemático central: dividir retornos

La parte más débil de la estrategia es:

\[
RPS=\frac{r_A}{r_B}
\]

### 7.1 Denominador cercano a cero

Ejemplo:

```text
A = +0.10%
B = +0.01%
```

\[
RPS=10
\]

El indicador mostraría un extremo enorme, aunque la diferencia económica sea solamente:

```text
9 puntos básicos
```

En cambio:

```text
A = +3.00%
B = +2.00%
```

\[
RPS=1.5
\]

La diferencia económica es:

```text
100 puntos básicos
```

pero el RPS parece mucho menos extremo.

Por tanto, el RPS puede responder más al pequeño denominador que a la magnitud real de la divergencia.

### 7.2 Problemas de signo

```text
A = -4%
B = -2%
```

\[
RPS=2
\]

El RPS es positivo y relativamente alto, aunque A ha rendido claramente peor.

```text
A = +1%
B = -1%
```

\[
RPS=-1
\]

Aunque la separación económica es de 2 puntos porcentuales.

El filtro `rA > rB` o `rA < rB` resuelve la dirección de la operación, pero **no resuelve la medición defectuosa del grado de extremidad**.

### 7.3 División por cero

Cuando:

```text
rB = 0
```

el indicador no está definido.

Cuando:

```text
|rB| ≈ 0
```

se producen valores extremos artificiales.

El artículo no define:

```text
epsilon mínimo
winsorización
cap del RPS
tratamiento de infinitos
tratamiento de NaN
```

### 7.4 Distribución no robusta

La ratio de dos variables que pueden atravesar cero suele producir:

```text
colas muy pesadas
saltos enormes
media inestable
desviación estándar inestable
```

Esto cuestiona el uso de:

```text
media aritmética
+
bandas Gaussianas de desviación estándar
```

La figura de la página 5 ya muestra bandas muy amplias y asimétricas alrededor de valores próximos a cero, coherente con esta inestabilidad.

---

## 8. Correlación no equivale a reversión

El artículo exige acciones con correlación positiva histórica superior aproximadamente a 0.7, pero no especifica:

```text
ventana de correlación
frecuencia exacta
método Pearson/Spearman
periodo de formación
frecuencia de recalibración
si la correlación se calculó con toda la muestra
```

Dos series pueden tener retornos muy correlacionados y, sin embargo:

```text
su spread no ser estacionario
su beta cambiar
la relación económica romperse
la divergencia no converger
```

La correlación mide co-movimiento contemporáneo. La tesis de pairs trading necesita algo más parecido a:

```text
un spread o residuo estable
+
una fuerza de reversión
+
un horizonte de convergencia razonable
```

Por ello debemos separar:

```text
pair eligibility por correlación
```

de:

```text
evidencia de mean reversion del spread
```

---

## 9. Problemas científicos del backtest publicado

El resultado del PDF es insuficiente para afirmar edge por los siguientes motivos esenciales.

### 9.1 Parámetros optimizados en la misma muestra

El propio documento declara:

> Los valores por defecto fueron encontrados mediante optimización de la estrategia.

No presenta:

```text
periodo de entrenamiento
periodo de validación
periodo out-of-sample
walk-forward
número de combinaciones probadas
corrección por múltiples pruebas
```

El Profit Factor 2.24 es, por tanto, **in-sample y postselección**. 

### 9.2 Un único par

El resultado principal procede solamente de:

```text
V / MA
```

También menciona ADI/TXN y ACE/CB, pero no publica sus resultados.

No sabemos si:

```text
V/MA fue elegido antes del estudio
fue el mejor de muchos pares
otros pares fracasaron
la orientación MA/V fue peor
```

### 9.3 Solamente 71 operaciones

Setenta y una observaciones son pocas para evaluar:

```text
colas
drawdown
estabilidad temporal
asimetría
dependencia de regímenes
```

Además, las operaciones están serialmente relacionadas porque utilizan ventanas superpuestas de siete, quince y 250 días.

### 9.4 Concentración en el lado long

El lado long produce la mayor parte del beneficio.

Esto permite hipótesis alternativas:

```text
la estrategia detecta buenos puntos para comprar V
pero no detecta correctamente buenos puntos para vender V

o

el periodo simplemente favoreció la exposición long en V
```

### 9.5 Ejecución simplificada

El modelo utiliza:

```text
open diario
$0.01 de slippage por acción
$0.01 de comisión por acción
```

No incluye explícitamente:

```text
apertura por subasta frente a primer print
bid-ask real
market impact
borrow fee
locate
dividendos en posiciones short
rechazos
partial fills
```

Para V estos problemas son moderados. Para small caps podrían destruir completamente el resultado.

---

## 10. Cómo debe implementarse en TSIS

### 10.1 Separación señal–ejecución

```text
Signal price view:
cierres diarios ajustados correctamente por corporate actions

Execution price view:
precio raw realmente operable en la apertura
```

En la arquitectura actual:

```text
Señal:
004_master_daily_table
o vista diaria gobernada equivalente

Ejecución:
013_ohlcv_1m_quote_guarded
/ 1m_quote_guarded_raw
```

No debemos ejecutar con precios históricos ajustados.

### 10.2 Contrato de datos

Cada observación necesita:

```text
pair_id
primary_symbol
reference_symbol
session_date
decision_timestamp
primary_close
reference_close
primary_return_L
reference_return_L
rps
rps_mean
rps_std
upper_band
lower_band
outside_band
outside_streak
relative_rank_direction
signal
next_session_open
following_session_open
```

### 10.3 Alineación temporal

Las dos series deben compartir exactamente:

```text
misma sesión
mismo calendario
mismo cierre oficial
```

No debe hacerse forward-fill de precios cuando falte una sesión.

Si falta una de las patas:

```text
context_status = UNAVAILABLE
signal = NO_DECISION
```

### 10.4 Corporate actions

Para el cálculo de retornos deben eliminarse saltos mecánicos por:

```text
splits
reverse splits
dividendos, según la variante de retorno
```

Conviene mantener dos pruebas explícitas:

```text
A. split-adjusted price return
B. total shareholder return
```

La ejecución y el PnL deben permanecer en precios raw, añadiendo los flujos de dividendos cuando corresponda.

### 10.5 Apertura

Debemos diferenciar:

```text
official_open
opening_auction_fill
first_regular_session_trade
first_valid_quote_mid
first_1m_bar_open
```

La reproducción del artículo utilizará:

```text
official daily open
```

La prueba realista utilizará un modelo MOO o una política de apertura gobernada mediante datos de un minuto y quotes.

### 10.6 Posiciones consecutivas

El artículo no aclara qué ocurre cuando en la misma apertura:

```text
debe cerrarse la posición anterior
y existe una nueva entrada
```

TSIS debe fijar una política:

```text
exit_then_entry
entry_then_exit
net_position_transition
no_same_open_reentry
```

La réplica debe aproximarse al comportamiento de TradeStation; la versión científica debe declarar explícitamente la política.

### 10.7 División por cero

Para la réplica:

```text
Si |return_reference| <= epsilon:
    RPS = UNAVAILABLE
    no generar señal
```

No conviene sumar arbitrariamente un epsilon al denominador, porque cambiaría la distribución completa.

Después deben probarse distintos valores de exclusión como análisis de sensibilidad.

---

## 11. Pseudocódigo de referencia

```python
for session_t in aligned_sessions:

    ret_a = adjusted_close_a[t] / adjusted_close_a[t - length] - 1.0
    ret_b = adjusted_close_b[t] / adjusted_close_b[t - length] - 1.0

    if abs(ret_b) <= denominator_epsilon:
        mark_unavailable(t, reason="REFERENCE_RETURN_NEAR_ZERO")
        continue

    rps[t] = ret_a / ret_b

    if not enough_history(rps, max(avg_length, std_length)):
        continue

    mean_rps = rolling_mean(rps, avg_length)
    std_rps = rolling_population_std(rps, std_length)

    upper = mean_rps + std_num * std_rps
    lower = mean_rps - std_num * std_rps

    outside = rps[t] > upper or rps[t] < lower

    trending = outside and outside_previous_bar
    eligible = outside and not trending

    if eligible:
        if ret_a < ret_b:
            schedule_long(
                entry=session_open[t + 1],
                exit=session_open[t + 2],
            )

        elif ret_a > ret_b:
            schedule_short(
                entry=session_open[t + 1],
                exit=session_open[t + 2],
            )
```

Parámetros congelados:

```text
length      = 7
avg_length  = 15
std_length  = 250
std_num     = 0.75
```

---

## 12. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica histórica

Periodo:

```text
30/09/2009–30/09/2014
V como Data1
MA como Data2
parámetros publicados sin modificar
```

Objetivo:

```text
aproximarse a 71 operaciones
reconciliar fechas de entrada
reconciliar dirección
reconciliar PnL
explicar cualquier diferencia
```

El informe publicado debe utilizarse como checksum, no como prueba de edge.

### Fase 2 — Verdadero out-of-sample postpublicación

El número fue publicado el 14 de enero de 2015. Esto nos permite congelar completamente la especificación y probar:

```text
15/01/2015
hasta
última sesión completa disponible en TSIS
```

Este periodo es especialmente valioso:

> Los parámetros ya eran públicos antes de producirse los datos.

Si no modificamos nada, es un auténtico test postpublicación.

Debemos informar:

```text
2015–2017
2018–2020
2021–2023
2024–2026
```

además del resultado agregado.

### Fase 3 — Descomposición del origen del PnL

Hay que comparar, utilizando exactamente las mismas fechas:

| Modelo                        | Pregunta                                      |
| ----------------------------- | --------------------------------------------- |
| RPS original                  | ¿Funciona la regla publicada?                 |
| Reversión propia de V         | ¿MA aporta información?                       |
| Diferencia `rV-rMA`           | ¿Es necesaria la división?                    |
| Residuo `rV-βrMA`             | ¿Funciona mejor ajustando beta?               |
| Pair trade V/MA               | ¿La convergencia está realmente en el spread? |
| Fechas aleatorias             | ¿La selección temporal supera un placebo?     |
| Peer aleatorio correlacionado | ¿MA es especial?                              |

La prueba crucial es:

```text
RPS(V, MA)
versus
reversión de V con igual número de señales
```

Si ambas producen resultados similares, la relación con MA no es la fuente del edge.

### Fase 4 — Descomposición temporal

El retorno open-to-open debe dividirse en:

```text
open t+1 → close t+1
close t+1 → open t+2
```

Así sabremos si el beneficio procede de:

```text
reversión intradía
reversión overnight
o ambas
```

Esto tiene consecuencias operativas completamente diferentes.

### Fase 5 — Robustez

Sin buscar el mejor punto, debemos estudiar la superficie alrededor de:

```text
Length: 3–20
AvgLength: 5–60
StdDevLength: 60–500
StdDevNum: 0.5–3.0
```

El objetivo no es elegir el máximo, sino comprobar:

```text
¿Existe una meseta estable?
¿O solamente funciona 7/15/250/0.75?
```

Si realizamos una búsqueda amplia, habrá que aplicar:

```text
Deflated Sharpe Ratio
PBO / CSCV
White Reality Check o Hansen SPA
block bootstrap
```

### Fase 6 — Costes y ejecución

Escenarios:

```text
official open ideal
open + medio spread
open + spread completo
slippage 5, 10, 20 y 50 bps
borrow y dividendos
retraso de 1 minuto
```

El break-even cost es más informativo que un único PnL.

---

## 13. Variantes matemáticas que merecen estudiarse

No debemos sustituir la estrategia original antes de replicarla. Primero se reproduce y después se comparan variantes preregistradas.

### Variante A — Diferencia de retornos

\[
D_t=r^A_t-r^B_t
\]

Ventajas:

```text
no divide por cero
magnitud económicamente interpretable
mantiene el signo correcto
```

Después:

\[
Z_t=\frac{D_t-\mu_D}{\sigma_D}
\]

### Variante B — Residuo con hedge ratio

\[
r^A_t=\alpha_t+\beta_t r^B_t+\epsilon_t
\]

Se opera el residuo:

\[
Z^\epsilon_t=\frac{\epsilon_t-\mu_\epsilon}{\sigma_\epsilon}
\]

Esto responde:

```text
¿Cuánto se ha movido A
más o menos de lo esperado
dado el movimiento de B?
```

Es conceptualmente más sólido.

### Variante C — Spread de precios logarítmicos

\[
S_t=\log P^A_t-\beta\log P^B_t
\]

Sólo debe operarse si presenta evidencia de estabilidad o mean reversion.

### Variante D — Par market-neutral

Si A ha sobre-rendido:

```text
short A
long β unidades de B
```

Si A ha infra-rendido:

```text
long A
short β unidades de B
```

Esto permite evaluar directamente la convergencia entre las dos patas.

### Variante E — Peer basket

En lugar de depender de un único denominador:

\[
residual_A=r_A-\sum_i\beta_i r_i
\]

El benchmark podría ser:

```text
cesta de competidores
ETF sectorial
factor industrial
componente PCA
```

Esto reduce el riesgo de que un movimiento idiosincrático de MA provoque una falsa señal sobre V.

---

## 14. Encaje dentro de Market State y Event State

La estrategia confirma una distinción muy útil para TSIS.

### Market State observable en (t)

```text
ret_primary_7d
ret_reference_7d
rps
rps_mean_15
rps_std_250
rps_upper_band
rps_lower_band
outside_band
outside_streak
pair_correlation
```

Todo debe conocerse al cierre del día (t).

### Evento de investigación

```text
event_type:
relative_performance_divergence_extreme

subject_scope:
ordered_security_pair

primary_subject:
V

reference_subject:
MA

decision_timestamp:
session_close_t
```

### Outcome

```text
primary_open_to_open_return_1d
pair_hedged_return_1d
intraday_component
overnight_component
MFE
MAE
convergence_amount
time_to_convergence
```

Así TSIS no confunde:

```text
Evento:
se ha producido una divergencia relativa extrema

Estrategia:
comprar o vender la primera pata durante una sesión
```

Podemos descubrir que el evento contiene información, pero que la respuesta operativa publicada no es la mejor.

---

## 15. Transferencia a small caps y futuros

### Small caps

No la trasladaría directamente.

El ejemplo original utiliza dos acciones:

```text
muy líquidas
grandes
relacionadas económicamente
fáciles de vender en corto
sin halts frecuentes
```

En small caps aparecen:

```text
catalizadores idiosincráticos
halts
dilución
offerings
borrow caro o inexistente
gaps discontinuos
correlaciones inestables
spreads grandes
```

Una divergencia frente a un supuesto peer puede ser información fundamental nueva y no una desviación transitoria.

Para small caps tendría más sentido:

```text
retorno residual frente a mercado/sector
+
catalyst state
+
liquidity state
+
halt state
+
short-side context
```

### Futuros

La idea general puede aplicarse, pero no esta implementación sin cambios.

Habría que resolver:

```text
roll de contratos
vencimientos
sesiones distintas
multiplicadores
hedge ratio
continuous contract artifacts
carry
```

En futuros relacionados suele ser más natural estudiar el spread directamente que dividir dos retornos.

---

## Conclusión

La estrategia merece ser implementada por tres razones:

1. Es sencilla y auditable.
2. Obliga al backtester a manejar dos series sincronizadas y operar solamente una.
3. Disponemos de más de diez años de datos posteriores a su publicación para falsificarla limpiamente.

Pero no debemos aceptar como evidencia el Profit Factor 2.24.

La estrategia original contiene tres señales de alarma:

```text
parámetros optimizados in-sample
un solo par
ratio de retornos matemáticamente inestable
```

Mi decisión técnica sería:

```text
IMPLEMENTAR:
sí, como réplica histórica gobernada

ACEPTAR COMO EDGE:
no

OPTIMIZAR:
no antes del test postpublicación congelado

OPERAR EN REAL:
no

SIGUIENTE GATE:
RPS-REPLICATION-AND-POSTPUBLICATION-OOS-GATE
```

Antes de escribir el backtest debe fijarse el contrato exacto de la réplica: ambigüedades pendientes de resolver con el `.ELD`, datos físicos TSIS, timestamps de decisión y ejecución, y checksums de los resultados publicados.

---


# Parte II — Estrategia 002: Moving Average Channel Strategy

## 1) Identificación y rendimiento

- **ID de estrategia:** `SCC-2015-01-STRAT-002`
- **Artículo:** *Moving Average Channel Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas del PDF:** 10–15
- **Páginas impresas del artículo:** 8–13
- **Estilo declarado:** Trend following
- **Mercado declarado:** Futures
- **Horizonte declarado:** Day trading
- **Instrumento del backtest:** E-mini S&P 500
- **Símbolo TradeStation:** `@ES=107XN`
- **Bar interval:** 15 minutos
- **Sesión cargada:** sesión completa de 23.25 horas
- **Ventana de entrada por defecto:** 09:45–15:15, hora configurada en el chart
- **Liquidación obligatoria:** cierre de sesión
- **Archivos auxiliares del ZIP:** estrategia/indicador `.ELD` y workspace `.tsw`

### Resultados destacados publicados

| Métrica | Total | Long | Short |
|---|---:|---:|---:|
| Beneficio neto | $15,933.40 | $7,257.36 | $8,676.04 |
| Gross profit | $167,414.12 | $81,889.24 | $85,524.88 |
| Gross loss | -$151,480.72 | -$74,631.88 | -$76,848.84 |
| Profit Factor | 1.11 | 1.10 | 1.11 |
| Operaciones | 1,280 | 687 | 593 |
| Percent profitable | 37.42% | 41.19% | 33.05% |
| Ganadoras | 479 | 283 | 196 |
| Perdedoras | 801 | 404 | 397 |
| Ganancia media | $349.51 | $289.36 | $436.35 |
| Pérdida media | -$189.11 | -$184.73 | -$193.57 |
| Ratio avg. win / avg. loss | 1.85 | 1.57 | 2.25 |
| Esperanza media por operación | $12.45 | $10.56 | $14.63 |
| Mayor ganadora | $2,007.78 | $1,670.28 | $2,007.78 |
| Mayor perdedora | -$854.72 | -$854.72 | -$767.22 |
| Máx. ganadoras consecutivas | 6 | 9 | 6 |
| Máx. perdedoras consecutivas | 11 | 7 | 12 |
| Barras medias en ganadoras | 23.28 | 23.45 | 23.03 |
| Barras medias en perdedoras | 7.91 | 7.57 | 8.27 |

Otros campos mostrados:

```text
Initial capital: $20,000
Trade size: 1 contrato
Commissions: $2.36 por lado
Account Size Required: $6,355.92
Return on Initial Capital: 79.67%
Annual Rate of Return: 11.70%
History: 5 años, hasta el 30 de junio de 2014
Slippage publicado: no indicado
```

El panel de rendimiento aparece en la página física 13 del PDF. La curva de capital de la página física 14 muestra una tendencia positiva a largo plazo, pero también un drawdown inicial visible, amplios periodos sin nuevos máximos y una caída importante desde el máximo final antes del cierre de la muestra.

---

## 2. Qué estrategia es realmente

No es una estrategia convencional de cruce entre una media rápida y una lenta.

Utiliza dos medias simples de **igual longitud** pero aplicadas a dos campos diferentes:

```text
media superior = SMA de los máximos
media inferior = SMA de los mínimos
```

Con el parámetro por defecto:

```text
AvgLength = 20 barras
```

Como el máximo de cada barra nunca es inferior a su mínimo, la media de máximos debe situarse normalmente por encima de la media de mínimos. Las dos líneas forman un canal y no se usan para cruzarse entre ellas.

La señal se produce cuando **la barra completa** queda fuera del canal:

```text
Long candidate:
el mínimo de la barra está por encima de la media de máximos

Short candidate:
el máximo de la barra está por debajo de la media de mínimos
```

Esto es más exigente que pedir simplemente:

```text
Close > UpperBand
o
Close < LowerBand
```

La idea operacional es:

> Una barra enteramente fuera de un canal construido con información suavizada de máximos y mínimos puede representar una ruptura suficientemente fuerte como para que la dirección continúe durante el resto de la sesión.

El objetivo explícito del artículo es capturar **trend days**, es decir, sesiones en las que el mercado toma una dirección clara y la mantiene durante buena parte del día.

---

## 3. Reconstrucción matemática

### 3.1 Canal

Sea \(H_t\) el máximo y \(L_t\) el mínimo de la barra de 15 minutos \(t\). Con longitud \(n=20\):

\[
Upper_t = \frac{1}{n}\sum_{i=0}^{n-1} H_{t-i}
\]

\[
Lower_t = \frac{1}{n}\sum_{i=0}^{n-1} L_{t-i}
\]

El artículo dice “simple moving averages”. TradeStation documenta `Average` y `AverageFC` como medias aritméticas móviles y permite usar `High` o `Low` como input. La función exacta elegida por el `.ELD` no puede confirmarse sin importar el archivo o exportar su código, pero ambas producirían el mismo valor matemático bajo la misma precisión numérica. [TS-AVERAGEFC]

### 3.2 Ruptura de barra completa

\[
LongBreak_t = L_t > Upper_t
\]

\[
ShortBreak_t = H_t < Lower_t
\]

La desigualdad estricta importa:

```text
Low == UpperBand
no activa long

High == LowerBand
no activa short
```

El PDF utiliza “greater than” y “less than”, no “greater than or equal” ni “less than or equal”.

### 3.3 Stops

Con `TicksForStops = 2`:

\[
LongStop_t = Lower_t - 2 \times TickSize
\]

\[
ShortStop_t = Upper_t + 2 \times TickSize
\]

Para el E-mini S&P 500, un tick es 0.25 puntos, por lo que dos ticks equivalen a 0.50 puntos. Esta conversión debe obtenerse del contrato físico y no codificarse como constante universal en TSIS.

La media opuesta actúa como stop dinámico:

```text
posición long  -> stop bajo LowerBand
posición short -> stop sobre UpperBand
```

Aunque el artículo lo describe como “usually trailing”, no es estrictamente monotónico. Una media móvil puede retroceder y alejar el stop del precio. Por ello, **no debe implementarse como `max(previous_stop, new_stop)` para long ni como `min(...)` para short** salvo que el código original lo haga expresamente.

### 3.4 Warm-up

La primera señal matemáticamente válida requiere, como mínimo:

```text
20 barras completas
```

Pero la primera señal económicamente comparable necesita además:

```text
sesión y calendario correctos
contrato activo correcto
roll policy definida
ventana temporal correctamente interpretada
```

---

## 4. Reglas exactas de entrada y salida

### 4.1 Control de frecuencia diaria

El parámetro:

```text
MaxTradesPerDay = 1
```

limita el total combinado de entradas long y short de cada día.

No significa:

```text
1 long + 1 short
```

sino:

```text
máximo de una entrada total,
independientemente de la dirección
```

El artículo afirma que el test de este parámetro favorece la primera señal diaria. TradeStation dispone de funciones como `EntriesToday` para contar entradas por fecha, pero la implementación concreta del `.ELD` permanece sin auditar. [TS-ENTRIESTODAY]

### 4.2 Ventana de entrada

Inputs publicados:

```text
EarliestBarTimetoEnter = 945
LastBarTimeToEnter     = 1515
```

El texto es preciso:

```text
la entrada más temprana se ejecuta en la apertura
de la barra marcada 09:45

la entrada más tardía se ejecuta en la apertura
de la barra marcada 15:15
```

Como la regla de señal dice “buy/sell short on the open of the next bar”, se deduce:

```text
señal para entrar 09:45:
debe confirmarse con la barra anterior, marcada 09:30

señal para entrar 15:15:
debe confirmarse con la barra anterior, marcada 15:00
```

Esta diferencia entre:

```text
hora de la barra que genera la señal
y
hora de la barra en la que se ejecuta
```

debe fijarse contractualmente para evitar un desplazamiento de una barra.

### 4.3 Entrada long

En la barra \(t\):

```text
Low_t > UpperBand_t
AND
la siguiente apertura está dentro de la ventana permitida
AND
EntriesToday < MaxTradesPerDay
```

Orden:

```text
Buy next bar at market
```

Ejecución histórica prevista:

```text
Open_{t+1}
```

TradeStation distingue expresamente las órdenes “next bar at market” como uno de los tipos básicos de orden de estrategia. [TS-ORDER-TYPES]

### 4.4 Entrada short

En la barra \(t\):

```text
High_t < LowerBand_t
AND
la siguiente apertura está dentro de la ventana permitida
AND
EntriesToday < MaxTradesPerDay
```

Orden:

```text
Sell short next bar at market
```

Ejecución histórica prevista:

```text
Open_{t+1}
```

### 4.5 Salida protectora long

Mientras exista una posición long:

```text
Sell next bar at LowerBand - TicksForStops * TickSize stop
```

Hay que confirmar en el código si el nivel se calcula:

```text
con la banda actual
o
con la banda de la barra anterior
```

En EasyLanguage, una orden generada al cierre de una barra suele estar activa en la barra siguiente. La diferencia de un índice puede alterar materialmente el resultado.

### 4.6 Salida protectora short

Mientras exista una posición short:

```text
Buy to cover next bar at UpperBand + TicksForStops * TickSize stop
```

La misma ambigüedad temporal debe resolverse con el código original o mediante reconciliación de trades.

### 4.7 Salida de fin de sesión

El artículo indica:

```text
toda posición abierta se cierra al cierre de la sesión
```

Y concreta para el chart utilizado:

```text
17:15 Eastern Time
```

También advierte que no había negociación entre 16:15 y 16:30.

TradeStation documenta que `SetExitOnClose` genera, en simulación histórica, una orden de mercado en el evento de cierre de la última barra intradía de la sesión definida por el chart. En automatización real su comportamiento puede ser distinto, especialmente si existe post-market. [TS-SETEXITONCLOSE]

Por tanto deben separarse:

```text
reproducción histórica de TradeStation
y
política real de liquidación antes del cierre
```

No basta con reutilizar literalmente `SetExitOnClose` como especificación de ejecución live.

---

## 5. Por qué usa la sesión completa aunque sólo entra durante el día

Ésta es una de las ideas metodológicas más valiosas del artículo.

El chart contiene la sesión completa de futuros, pero las entradas se restringen a las horas de mayor actividad del “day session”.

Motivo:

```text
las medias de 20 barras deben incorporar la acción overnight
antes de que comience la ventana de entrada
```

Con barras de 15 minutos:

```text
20 barras = 5 horas
```

Si se cargara únicamente la sesión diurna, la media disponible en la apertura estaría formada principalmente por las últimas barras de la tarde anterior y no reflejaría el movimiento overnight de la nueva sesión.

Por tanto el diseño separa correctamente:

```text
information window:
sesión completa

execution window:
horario restringido
```

Esta separación encaja muy bien con TSIS:

```text
Market State puede observar overnight + premarket
mientras la estrategia limita su ejecución a un horario legal
```

El artículo menciona además una posible arquitectura multi-activo:

```text
generar la señal con futuros ES,
pero ejecutar sobre SPY
```

No la implementa ni la valida. Es una **idea de investigación**, no un resultado demostrado.

---

## 6. Ejemplo de la página 13

La figura 2 muestra una entrada long:

1. La barra completa queda por encima de la banda superior.
2. La estrategia compra en la apertura de la barra siguiente.
3. La banda inferior funciona como stop protector.
4. La operación permanece abierta muchas barras mientras la tendencia continúa.
5. El stop termina liquidando la posición cerca de las 15:00.

Visualmente, el ejemplo ilustra la intención de:

```text
entrar tarde respecto del inicio absoluto del movimiento,
pero permanecer mientras el movimiento sea persistente
```

El ejemplo no demuestra rentabilidad estadística. Sólo demuestra la mecánica.

---

## 7. Configuración exacta del backtest publicado

```text
Símbolo:
@ES=107XN

Descripción:
E-mini S&P 500 Custom Continuous Contract

Bar interval:
15-minute

Periodo:
cinco años, finalizando el 30/06/2014

Capital inicial:
$20,000

Tamaño:
1 contrato

Comisión:
$2.36 por lado

Ajuste del continuo:
sin price adjustment

Regla de roll:
custom continuous diseñado para aproximar las reglas CME

Slippage:
no publicado

Profit target:
no existe

Entrada máxima diaria:
1
```

El PDF también muestra en el encabezado del informe:

```text
6/28/2009–7/1/2014
```

mientras la tabla textual resume “5 years, ending June 30, 2014”. Esta diferencia de uno o varios timestamps debe considerarse una discrepancia de reporte menor hasta reconciliar el workspace.

---

## 8. Qué nos dicen realmente los resultados

### 8.1 Edge medio extremadamente pequeño

La esperanza publicada es:

\[
\frac{\$15{,}933.40}{1{,}280}
=
\$12.45 \text{ por operación}
\]

En ES:

```text
1 punto = $50
1 tick  = 0.25 puntos = $12.50
```

Por tanto:

```text
esperanza media neta publicada ≈ 0.249 puntos
esperanza media neta publicada ≈ 0.996 ticks
```

Es decir:

> El beneficio medio de toda la estrategia equivale aproximadamente a **un solo tick por operación**.

Esto es la alerta central del backtest.

Si el informe no incorpora slippage, añadir solamente:

```text
1 tick total adicional por round trip
```

reduciría el resultado aproximadamente en:

\[
1{,}280 \times \$12.50 = \$16{,}000
\]

El beneficio neto pasaría de:

```text
+$15,933.40
```

a aproximadamente:

```text
-$66.60
```

Un tick por lado produciría una pérdida mucho mayor.

No significa que el backtest sea necesariamente falso. Significa que:

```text
la conclusión depende críticamente
del modelo exacto de ejecución
```

### 8.2 Profit Factor 1.11

Un Profit Factor de 1.11 implica:

```text
gross profit apenas supera gross loss en un 10.5% aproximado
```

No existe un colchón amplio frente a:

```text
slippage
roll artifacts
errores de sesión
cambios de comisión
latencia
diferencias entre stop simulado y fill real
```

### 8.3 Perfil típico de trend following

La estrategia gana sólo el 37.42% de las operaciones, pero:

```text
ganancia media = $349.51
pérdida media  = -$189.11
ratio          = 1.85
```

Los ganadores duran:

```text
23.28 barras × 15 minutos
≈ 349.2 minutos
≈ 5 horas y 49 minutos
```

Los perdedores duran:

```text
7.91 barras × 15 minutos
≈ 118.7 minutos
≈ 1 hora y 59 minutos
```

Esto es coherente con una estrategia que:

```text
corta pérdidas relativamente pronto
y retiene los pocos días tendenciales
```

Pero la forma del payoff no compensa automáticamente el problema de costes.

### 8.4 Long y short

A diferencia de la estrategia RPS, el beneficio no está concentrado casi enteramente en una dirección:

```text
Long net profit  = $7,257.36
Short net profit = $8,676.04
```

Los dos lados tienen Profit Factor cercano a 1.1. Esto aporta cierta simetría, pero también muestra que **ninguno de los dos lados posee un margen fuerte**.

### 8.5 Streaks y capital psicológico

El informe muestra:

```text
máximo de 11 pérdidas consecutivas total
máximo de 12 pérdidas consecutivas en short
```

Con una sola entrada diaria, una racha así puede prolongarse durante varias semanas de calendario. La dificultad conductual señalada por el autor es real, aunque no constituye evidencia científica.

### 8.6 Curva de capital

La página física 14 muestra:

```text
un drawdown temprano cercano visualmente a -$4,000
recuperación posterior
varios periodos prolongados sin nuevos máximos
un máximo próximo a +$20,000
retroceso final hacia +$16,000
```

El PDF no publica una tabla exacta de maximum drawdown en las páginas visibles. No debe inventarse un valor a partir del gráfico.

---

## 9. Optimización publicada

El artículo afirma que sólo se optimizó `MaxTradesPerDay`.

Resultados mostrados:

| MaxTradesPerDay | Net Profit | Total Trades | % Profitable |
|---:|---:|---:|---:|
| 1 | $15,934.59 | 1,280 | 37.42% |
| 2 | $9,813.52 | 1,952 | 38.27% |
| 3 | $9,307.86 | 2,083 | 38.50% |
| 4 | $8,923.42 | 2,085 | 38.47% |

La conclusión del artículo es:

```text
la primera señal del día parece contener la mayor oportunidad
las señales posteriores reducen el resultado
```

La tabla respalda esa lectura dentro de la muestra.

Sin embargo, hay tres cautelas:

1. `MaxTradesPerDay = 1` queda seleccionado **con los mismos datos** sobre los que se informa el rendimiento.
2. El artículo no muestra un periodo independiente para confirmar la selección.
3. La tabla de optimización presenta $15,934.59 para el valor 1, mientras el Performance Summary muestra $15,933.40: existe una discrepancia de $1.19 que debe reconciliarse.

Aunque sólo se comparen cuatro variantes, el resultado final ya es post-selección y no debe tratarse como out-of-sample.

---

## 10. ¿Dónde podría estar el edge?

La hipótesis económica mínima sería:

> Cuando una barra de 15 minutos queda completamente fuera de un canal suavizado de máximos y mínimos, durante una ventana líquida y después de incorporar la información overnight, aumenta la probabilidad de que la dirección persista durante el resto de la sesión.

Posibles mecanismos:

```text
continuación tras desequilibrio fuerte de órdenes
actualización tardía de expectativas
cobertura institucional
feedback trading
ruptura de rangos overnight
concentración de información en días macro
persistencia intradía en días de alta volatilidad o volumen
```

La literatura académica documenta formas de time-series momentum en futuros a horizontes mucho más largos y también patrones específicos de momentum intradía en índices. [MOP-TSM] [GAO-INTRADAY]

Pero esto no valida directamente:

```text
SMA de highs/lows de 20 barras
barra completa fuera del canal
entrada 09:45–15:15
stop en banda opuesta ±2 ticks
una sola entrada diaria
```

La familia conceptual es plausible. La parametrización concreta sigue sin validación científica.

---

## 11. Problemas científicos y técnicos del backtest

### 11.1 Slippage ausente

La tabla publica comisión, pero no slippage.

Con una esperanza de un tick por trade, ésta no es una omisión secundaria: puede cambiar el signo del resultado.

### 11.2 Selección in-sample

`MaxTradesPerDay` fue comparado en la misma muestra y se eligió el mejor valor.

No se publica:

```text
train/test
walk-forward
periodo post-selección
corrección por múltiples pruebas
```

### 11.3 Posibles decisiones de diseño no contabilizadas como optimización

El autor afirma que no optimizó los demás inputs, pero el sistema contiene múltiples decisiones:

```text
AvgLength = 20
TicksForStops = 2
09:45
15:15
15-minute bars
full session
ES
cierre 17:15
barra completa, no cierre
```

Aunque no se hayan ejecutado grids formales, estas decisiones pueden haber surgido de experiencia previa con la muestra. Científicamente forman parte del grado de libertad total.

### 11.4 Continuous contract sin ajuste

El símbolo `@ES=107XN` enlaza contratos y no aplica ajuste de precios.

Riesgos:

```text
gaps artificiales de roll
cambios en la posición relativa de las medias
stops activados por discontinuidades
PnL calculado sobre un precio sintético no directamente operable
```

TradeStation documenta que los símbolos continuos conectan contratos según parámetros configurables. [TS-CONTINUOUS]

Para una réplica histórica debe reproducirse `@ES=107XN`. Para una prueba científica debe mapearse cada señal y cada fill al contrato físico realmente activo.

### 11.5 Sesiones históricas variables

La sesión del ES, pausas, horarios y liquidez han cambiado con el tiempo.

No debe aplicarse un único calendario moderno retroactivamente sin verificar:

```text
exchange calendar por fecha
session template del workspace
DST
festivos
early closes
maintenance breaks
```

### 11.6 Semántica de stop con barras de 15 minutos

El stop se evalúa dentro de una barra OHLC.

Debe definirse:

```text
fill en stop exacto
fill en open si hay gap a través del stop
prioridad temporal
redondeo a tick
actualización de la banda
```

No hay profit target simultáneo, por lo que el problema de secuencia intrabar es menor que en estrategias con stop y target, pero no desaparece.

### 11.7 Fin de sesión histórico frente a live

`SetExitOnClose` no debe asumirse como una garantía de ejecución exacta en live. La propia documentación de TradeStation diferencia simulación y automatización. [TS-SETEXITONCLOSE]

### 11.8 Un solo mercado

El artículo sólo informa ES.

No sabemos si la lógica:

```text
funciona en NQ
YM
RTY
Treasuries
FX
commodities
SPY
```

ni si ES fue seleccionado después de probar otros mercados.

### 11.9 Régimen 2009–2014

La muestra incluye la recuperación posterior a la crisis financiera y varios episodios de fuerte tendencia intradía.

El patrón puede depender de:

```text
volatilidad
política monetaria
microestructura
tick-to-volatility ratio
participación electrónica
```

---

## 12. Cómo debe implementarse en TSIS

### 12.1 Dos vistas de datos

```text
Signal / state view:
serie continua gobernada o barras del contrato activo
con overnight incluido

Execution view:
contrato físico operable
con precios raw y tick size correcto
```

Nunca debe ejecutarse directamente contra un precio continuo sintético sin conocer el contrato subyacente.

### 12.2 Campos mínimos

```text
session_id
exchange_session_date
contract_symbol
continuous_symbol
roll_state
bar_open_timestamp
bar_close_timestamp
open
high
low
close
upper_band_20
lower_band_20
long_break
short_break
entry_window_eligible
entries_today
signal_timestamp
scheduled_entry_timestamp
entry_price_policy
long_stop
short_stop
end_of_day_exit_timestamp
exit_reason
slippage_assumption
commission_assumption
```

### 12.3 Estado de roll

Cada barra debe incluir:

```text
active_contract
days_to_roll
is_roll_session
roll_method
continuous_price_adjustment
```

La réplica original puede usar el continuo sin ajuste. La validación debe repetir el test:

```text
incluyendo sesiones de roll
excluyendo sesiones de roll
ejecutando en contratos físicos
```

### 12.4 Calendario

La ventana 09:45–15:15 debe representarse en una timezone explícita:

```text
America/New_York
```

Y convertirse a UTC sólo después de resolver DST por fecha.

### 12.5 Política de fills

Versión de réplica:

```text
next-bar entry = open de la barra siguiente
stop fill = reglas equivalentes a TradeStation
end-of-day = close de última barra de sesión
```

Versión científica realista:

```text
entry = first executable quote/trade tras timestamp
stop = gap-aware
slippage = función de volatilidad/spread/participación
end-of-day = liquidación antes del cierre con buffer
```

### 12.6 Estado de no decisión

```text
insuficiente warm-up
barra faltante
sesión incompleta
contrato no resuelto
roll ambiguo
tick size ausente
stop no representable en tick
```

deben producir:

```text
NO_DECISION
```

y nunca forward-fill silencioso.

---

## 13. Pseudocódigo de referencia

```python
for bar_t in full_session_bars:

    upper_t = sma(high, length=20)
    lower_t = sma(low, length=20)

    if not bands_are_valid(bar_t):
        continue

    next_bar = get_next_bar(bar_t)

    entry_time_ok = (
        next_bar.open_time_local >= time(9, 45)
        and next_bar.open_time_local <= time(15, 15)
    )

    daily_capacity = entries_today(next_bar.session_date) < max_trades_per_day

    if flat() and entry_time_ok and daily_capacity:

        if bar_t.low > upper_t:
            schedule_market_entry(
                side="LONG",
                timestamp=next_bar.open_time,
                reason="FULL_BAR_ABOVE_UPPER_BAND",
            )

        elif bar_t.high < lower_t:
            schedule_market_entry(
                side="SHORT",
                timestamp=next_bar.open_time,
                reason="FULL_BAR_BELOW_LOWER_BAND",
            )

    if long_position():
        stop_price = round_to_tick(
            lower_t - ticks_for_stops * tick_size
        )
        schedule_stop_exit(
            side="SELL",
            active_during=next_bar,
            stop_price=stop_price,
        )

    elif short_position():
        stop_price = round_to_tick(
            upper_t + ticks_for_stops * tick_size
        )
        schedule_stop_exit(
            side="BUY_TO_COVER",
            active_during=next_bar,
            stop_price=stop_price,
        )

    if is_last_bar_of_session(bar_t) and has_position():
        exit_at_session_close()
```

Ambigüedad pendiente:

```text
¿El stop activo en la barra t+1 usa la banda calculada en t
o se recalcula intrabar / al inicio de t+1?
```

La réplica no debe cerrar esa decisión sin evidencia.

---

## 14. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica histórica

```text
@ES=107XN
15 minutos
full session
2009-06/07 a 2014-06/07
AvgLength = 20
TicksForStops = 2
MaxTradesPerDay = 1
09:45–15:15
1 contrato
$2.36 por lado
sin slippage
```

Checksums objetivo:

```text
1,280 trades
37.42% profitable
Profit Factor 1.11
Net Profit ≈ $15,933
Avg Trade ≈ $12.45
```

### Fase 2 — Reconciliación trade a trade

No basta con aproximar el PnL.

Debe reconciliarse:

```text
fecha
dirección
timestamp de señal
timestamp de entrada
precio de entrada
trayectoria de stop
timestamp de salida
motivo de salida
PnL
```

El `.ELD` importado en TradeStation sería la referencia más fuerte.

### Fase 3 — Out-of-sample postpublicación

Congelar el sistema publicado y probar:

```text
15/01/2015
hasta
última sesión completa disponible
```

Bloques sugeridos:

```text
2015–2017
2018–2020
2021–2023
2024–2026
```

Esto ofrece un test postpublicación real siempre que no se modifique ningún parámetro después de ver los resultados.

### Fase 4 — Coste de break-even

Calcular directamente:

```text
slippage máximo total por operación
que hace Net PnL = 0
```

El artículo sugiere aproximadamente:

```text
break-even adicional ≈ 0.996 ticks por round trip
```

Debe estimarse también por:

```text
año
lado long/short
hora de entrada
régimen de volatilidad
```

### Fase 5 — Contratos físicos

Comparar:

```text
A. continuo original
B. continuo back-adjusted
C. ratio-adjusted
D. contratos físicos con roll explícito
E. excluir ventanas cercanas al roll
```

Si el resultado sólo existe en `@ES=107XN`, el edge puede ser un artefacto de construcción.

### Fase 6 — Placebos

| Modelo | Pregunta |
|---|---|
| `Close > UpperBand` | ¿Hace falta que toda la barra quede fuera? |
| Donchian breakout | ¿La media de highs/lows aporta algo frente a un breakout clásico? |
| Keltner/ATR channel | ¿El canal debe adaptarse a volatilidad? |
| Primer breakout aleatorio | ¿El “primer signal” supera un placebo temporal? |
| Misma entrada, salida fija | ¿El edge procede del stop dinámico? |
| Misma señal, exit 16:00 | ¿La franja final añade o destruye valor? |
| RTH-only calculation | ¿El overnight mejora realmente la señal? |
| Señal ES, ejecución SPY | ¿Se transfiere a un activo distinto? |

### Fase 7 — Robustez sin elegir el máximo

Explorar una malla predefinida:

```text
AvgLength: 10, 15, 20, 25, 30, 40
TicksForStops: 0, 1, 2, 3, 4, 6, 8
Earliest: 09:30, 09:45, 10:00, 10:30
Last: 14:30, 15:00, 15:15, 15:45
MaxTradesPerDay: 1–4
Bar interval: 5m, 10m, 15m, 30m
```

Objetivo:

```text
no elegir el mejor punto
sino comprobar si existe una región estable
```

Si se explora todo, aplicar:

```text
Deflated Sharpe Ratio
Probability of Backtest Overfitting / CSCV
White Reality Check o Hansen SPA
block bootstrap
```

[DSR] [PBO] [WHITE-RC]

### Fase 8 — MFE/MAE

El propio artículo propone estudiar Maximum Favorable Excursion.

Para cada trade:

```text
MFE
MAE
profit give-back
bars to MFE
distance del stop al entrar
distance del stop al MFE
exit efficiency
```

Pregunta clave:

> ¿La banda opuesta deja devolver demasiado beneficio antes de cerrar?

---

## 15. Variantes que merecen estudiarse después de la réplica

### Variante A — Stop monotónico

```text
Long:
stop_t = max(stop_{t-1}, LowerBand_t - offset)

Short:
stop_t = min(stop_{t-1}, UpperBand_t + offset)
```

Esto convierte la salida en un trailing stop estricto. No es la estrategia original.

### Variante B — Canal normalizado por volatilidad

```text
Upper = SMA(Close, n) + k * ATR
Lower = SMA(Close, n) - k * ATR
```

Permite comparar si el valor procede del uso específico de highs/lows o de un breakout ajustado por volatilidad.

### Variante C — Clearance continuo

En vez de un booleano:

\[
ClearanceLong_t =
\frac{Low_t - Upper_t}{ATR_t}
\]

\[
ClearanceShort_t =
\frac{Lower_t - High_t}{ATR_t}
\]

Así el modelo puede evaluar la intensidad de la ruptura sin introducir decenas de umbrales arbitrarios.

### Variante D — Clasificador de trend day

Usar el evento de ruptura como candidato y estimar:

```text
P(trend_day | state_t)
```

con variables preregistradas:

```text
overnight return
gap
premarket / overnight range
realized volatility
volume pace
breadth
market regime
distance a VWAP
time of day
channel slope
channel width
```

El clasificador no debe sustituir la réplica original; debe ser una fase posterior.

### Variante E — Exit por información

Comparar:

```text
banda opuesta
VWAP
Chandelier / ATR
time stop
MFE give-back
cierre 16:00
```

### Variante F — Portafolio de mercados

Aplicar sin reoptimizar a una cesta de futuros líquidos y agregar riesgos por volatilidad.

Esto evalúa si la idea es:

```text
un fenómeno general de trend following
o
una coincidencia específica del ES
```

---

## 16. Encaje dentro de Market State y Event State

### Market State observable en \(t\)

```text
upper_band_20
lower_band_20
channel_mid
channel_width
channel_slope
low_minus_upper
lower_minus_high
full_bar_above
full_bar_below
overnight_return
overnight_range
session_position
time_of_day
entries_today
active_contract
roll_state
liquidity_state
volatility_state
```

### Event State

```text
event_type:
intraday_full_bar_channel_breakout

subject_scope:
tradable_contract

event_side:
up / down

decision_timestamp:
bar_close_t

earliest_execution_timestamp:
bar_open_t+1
```

### Outcome

```text
trend_day_label
entry_to_close_return
MFE
MAE
time_to_MFE
stop_distance
profit_give_back
exit_reason
slippage_realized
```

### Information Objects TSIS

La estrategia consume principalmente:

```text
price_movement
volatility_range_state
intraday_position
trading_activity
broad_market_context
market_microstructure_state
liquidity
```

No debería introducirse como un nuevo Information Object. Es una representación/estrategia que consume objetos ya admitidos.

---

## 17. Transferencia a small caps

La idea abstracta sí puede investigarse:

```text
una barra completa supera un canal
y la ruptura persiste
```

Pero la transferencia directa desde ES es peligrosa.

Small caps presentan:

```text
halts
spreads amplios
borrow incierto
gaps por news
ofertas y dilución
prints erráticos
barras sin liquidez
cambios de tick relativo
premarket dominante
```

En TSIS habría que exigir, como mínimo:

```text
news_catalyst_context
halt_context
liquidity
market_microstructure_state
short_side_context
trading_activity
intraday_position
```

Además:

```text
long y short deben validarse por separado
ejecución debe usar quote_guarded/raw
el stop debe modelar gaps y halts
no puede asumirse fill al nivel de stop
```

Una barra completa fuera del canal en una small cap con catalyst puede representar **nueva información permanente**, no una tendencia suave comparable al ES.

---

## 18. Veredicto de la estrategia

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí.** |
| ¿Puede replicarse aproximadamente con el PDF? | **Sí.** |
| ¿La réplica exacta requiere código/workspace? | **Sí**, especialmente para semántica temporal de stops, sesiones y contador diario. |
| ¿El backtest publicado demuestra edge? | **No.** |
| ¿La tesis de trend continuation es plausible? | **Sí, como familia general.** |
| ¿El margen publicado es robusto a costes? | **No parece:** la esperanza media es aproximadamente un tick. |
| ¿Es útil científicamente? | **Sí**, como benchmark simple, test de continuous futures y verdadero OOS post-2015. |
| ¿Está lista para live? | **No.** |

Clasificación TSIS:

```text
SOURCE_REPRODUCTION_CANDIDATE
EXECUTION_COST_CRITICAL
CONTINUOUS_FUTURES_RISK
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

Siguiente gate propuesto:

```text
MAC-REPLICATION-CONTINUOUS-CONTRACT-AND-COST-GATE
```


---


# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. VWAP intradía e históricos

La página física 9 presenta un producto de TradeStation Labs, no una estrategia validada.

Ideas descritas:

```text
VWAP intradía actual
reset al inicio de cada sesión
hasta cuatro VWAP diarios históricos
VWAP históricos como posibles soportes/resistencias
entrada long bajo VWAP considerada favorable frente al benchmark
entrada sobre VWAP considerada desfavorable
```

Clasificación correcta:

```text
RESEARCH_NOTE
NOT_A_STRATEGY
NO_RULES
NO_BACKTEST
NO_EDGE_EVIDENCE
```

Candidato TSIS:

```text
event_type:
historical_session_vwap_interaction
```

Outcomes posibles:

```text
bounce probability
break probability
distance-normalized forward return
liquidity-conditioned behavior
```

No debe incorporarse como estrategia hasta definir:

```text
qué VWAP
qué sesión
qué condición de toque/ruptura
qué entrada
qué salida
qué costes
```

## 2. Señal en un activo y ejecución en otro

El artículo Moving Average Channel sugiere:

```text
señal generada por ES
ejecución potencial en SPY
```

Es una idea arquitectónica relevante para TSIS:

```text
signal instrument != execution instrument
```

Requiere contrato explícito de:

```text
sincronización
latencia
basis risk
horarios
corporate actions
precio de ejecución
```

No hay resultados publicados.

## 3. Portfolio de pares

El artículo RPS propone:

```text
aplicar múltiples pares
usar posiciones opuestas
usar Portfolio Maestro
```

Ideas diferenciadas:

```text
single-leg relative signal
pair-neutral trade
portfolio of pairs
```

No deben mezclarse en un único backtest, porque responden a hipótesis distintas.

## 4. Lookbacks dinámicos

RPS sugiere periodos adaptativos.

Esto puede significar:

```text
ventana según volatilidad
ventana según half-life
ventana según estabilidad de correlación
ventana según régimen
```

No existe especificación ni resultado. Debe tratarse como una familia de investigación con presupuesto de grados de libertad, no como una “mejora gratuita”.

## 5. MFE para diseñar salidas

Moving Average Channel propone estudiar Maximum Favorable Excursion.

Es una idea metodológica fuerte:

```text
primero medir cuánto beneficio potencial se devuelve
después diseñar una salida
```

Pero reutilizar el mismo histórico para descubrir y evaluar la salida produciría sesgo. El diseño debe usar:

```text
train
validation
test post-congelación
```

## 6. Primera señal del día

La tabla de `MaxTradesPerDay` sugiere que:

```text
primera señal > señales posteriores
```

Esto es una hipótesis generalizable que puede evaluarse en otros eventos intradía:

```text
first_break
first_halt_resume
first_vwap_reclaim
first_HOD_break
```

Debe compararse por posición ordinal del evento y no sólo mediante un input optimizado.

## 7. Uso de información full-session con ejecución restringida

La revista aporta una lección arquitectónica clara:

```text
observar más horas
no implica poder operar todas esas horas
```

TSIS debe separar:

```text
observation entitlement
decision timestamp
execution eligibility
```

Esto es directamente aplicable a small caps:

```text
premarket informa el estado
RTH puede ser la única ventana de ejecución
```

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — Moving Average Channel como prueba de infraestructura

Motivos:

```text
1,280 trades publicados
reglas simples
futuros continuos
sesión completa + ventana restringida
stops dinámicos
fin de sesión
cost sensitivity
```

Es un excelente banco de pruebas para:

```text
event loop
session calendar
continuous-to-physical mapping
stop execution
cost model
trade reconciliation
```

### Prioridad B — Relative Performance Strength como prueba multi-data

Motivos:

```text
dos series sincronizadas
una sola pata ejecutada
daily signal / next-open execution
postpublication OOS limpio
corporate actions
pair eligibility
```

Es un buen banco de pruebas para:

```text
multi-asset state
point-in-time alignment
ordered pair identity
signal/execution separation
```

## 2. Artefactos futuros derivados

Este Markdown no sustituye los contratos de implementación. Cuando se autorice el trabajo físico deberían existir, como mínimo:

```text
SCC_2015_01_RPS_REPLICATION_CONTRACT.md
SCC_2015_01_MAC_REPLICATION_CONTRACT.md
```

Pero esos serían artefactos del repositorio TSIS, no archivos adicionales de la revista ni resúmenes editoriales.

## 3. Qué contenido pedir en revistas futuras

Por defecto será suficiente:

```text
PDF completo
```

Sólo se pedirá material adicional cuando una ambigüedad afecte a:

```text
fórmula
orden temporal
datos secundarios
sesión
stop/target
optimización
resultados
```

En ese caso se solicitará específicamente:

```text
ZIP del issue
.ELD/.TSW
captura de inputs
exportación de EasyLanguage como texto
Strategy Performance Report
trade list
```

No se pedirá un ZIP de forma rutinaria.

---

# Apéndice A — Integridad del paquete de esta revista

## Archivos relevantes

```text
SCC Issue 1 Jan 2015.pdf
Relative Performance Strength/TSL Relative Performance Strength.ELD
Relative Performance Strength/TSL Relative Performance Strength.tsw
Moving Average Channel/TSL MOVING AVERAGE CHANNEL.ELD
Moving Average Channel/TSL.Moving Average Channel.tsw
```

## SHA-256

```text
PDF:
4c0addefd2c77442b63df05133a5b7278a0ff80a0f8f76f1829d981a2bb5513b

ZIP:
f9177b6a553e7debdadd6fdc9bfb25e350f6f679966650e254c277711036c315

RPS .ELD:
1addc75b4d41ec514cc8ebeb85c3055849ebb0c2cab927aa09c805f95cd6bfd5

RPS .tsw:
4cf9a7197cd2188caaaa83346253f99479fe6ebcdaadf973b54bed461158f485

Moving Average Channel .ELD:
44b56222677e6501b6c53174c0d274ab19f6e332d665359ed8e252e714ae67ee

Moving Average Channel .tsw:
c39addeb8467583dffe05eda35020291126a36795ad4696bdecd6446530ace54
```

## Limitación del paquete

```text
.tsw:
workspace binario con metadatos parcialmente legibles

.ELD:
contenedor de TradeStation no legible como código fuente
en este entorno
```

La evidencia máxima requeriría importar los archivos en una instalación compatible de TradeStation y exportar:

```text
código EasyLanguage
inputs
strategy properties
trade list
performance report
session template
```

---

# Referencias externas

Las referencias siguientes contextualizan la auditoría. No forman parte de la evidencia publicada por la revista.

[TS-AVERAGEFC]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/averagefc_function_.htm
[TS-ENTRIESTODAY]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/entriestoday_function_.htm
[TS-ORDER-TYPES]: https://help.tradestation.com/09_01/tradestationhelp/st_testing/about_strategy_order_types.htm
[TS-SETEXITONCLOSE]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/word/setexitonclose_reserved_word_.htm
[TS-CONTINUOUS]: https://help.tradestation.com/10_00/eng/tradestationhelp/symbology/custom_continous_futures_symbology.htm
[MOP-TSM]: https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf
[GAO-INTRADAY]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866
[DSR]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
[PBO]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
[WHITE-RC]: https://www.ssc.wisc.edu/~bhansen/718/White2000.pdf


[1]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/rateofchange_function_.htm "https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/rateofchange_function_.htm"
[2]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/standarddev_function_.htm "https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/standarddev_function_.htm"
[3]: https://academic.oup.com/rfs/article-abstract/19/3/797/1646694 "https://academic.oup.com/rfs/article-abstract/19/3/797/1646694"
[4]: https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work "https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work"
[5]: https://research.monash.edu/en/publications/are-pairs-trading-profits-robust-to-trading-costs/ "https://research.monash.edu/en/publications/are-pairs-trading-profits-robust-to-trading-costs/"
[6]: https://math.nyu.edu/inmemoriam/avellaneda/AvellanedaLeeStatArb20090616.pdf "https://math.nyu.edu/inmemoriam/avellaneda/AvellanedaLeeStatArb20090616.pdf"
