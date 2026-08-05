# Auditoría completa — Relative Performance Strength Strategy

## 1) Identificación y rendimiento

- **ID:** 001
- **Archivo PDF:** SCC Issue 1 Jan 2015.pdf
- **Issue:** 1 (Jan 2015)
- **Revista:** Strategy Concepts (TradeStation)
- **Autor:** Stanley Dash, CMT
- **Mercado:** Futures
- **Horizonte:** No detectado

---

- **Profit Factor = 2.24** (se indica como alto para esta familia).
- **Percent Profitable = 64.79%** (en el contexto de esta estrategia se califica como "algo alto" para este tipo de estrategia).
- **RINA Index = 473.14** (alto, influido por baja exposición al mercado).
- **Comentario explícito:** se observan caídas pequeños (~5%), pero rendimiento cíclico y periodos de flat.

---

He revisado íntegramente la estrategia descrita en las páginas 4–8 del PDF, incluidas las reglas, parámetros, ejemplo gráfico, tabla de resultados y curva de capital. El documento original puede abrirse aquí: [Strategy Concepts Club — enero de 2015](sandbox:/mnt/data/SCC%20Issue%201%20Jan%202015.pdf). 

## Veredicto inicial

| Cuestión                                        | Conclusión                                                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| ¿Puede implementarse en TSIS?                   | **Sí, fácilmente.**                                                                                                 |
| ¿Podemos replicar aproximadamente el artículo?  | **Sí.** La réplica exacta exige recuperar el código `.ELD` enlazado por el PDF.                                     |
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

# 1. Qué estrategia es realmente

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

# 2. Reconstrucción matemática

## 2.1 Rendimientos de ambos activos

Con `Length = 7`, la interpretación compatible con el texto es:

[
r^A_t=\frac{C^A_t}{C^A_{t-7}}-1
]

[
r^B_t=\frac{C^B_t}{C^B_{t-7}}-1
]

donde:

```text
A = activo operado, V
B = activo de referencia, MA
C = cierre diario
```

La función estándar `RateOfChange` de EasyLanguage calcula precisamente:

[
100\left(\frac{P_t}{P_{t-L}}-1\right)
]

El factor 100 desaparece cuando se divide un ROC por el otro. ([Ayuda TradeStation][1])

## 2.2 Relative Performance Strength

[
RPS_t=\frac{r^A_t}{r^B_t}
]

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

## 2.3 Banda histórica

Los parámetros publicados son:

| Parámetro      | Valor | Función                            |
| -------------- | ----: | ---------------------------------- |
| `Length`       |     7 | Retorno acumulado de ambos activos |
| `AvgLength`    |    15 | Media móvil del RPS                |
| `StdDevLength` |   250 | Desviación histórica del RPS       |
| `StdDevNum`    |  0.75 | Anchura de la banda                |

La reconstrucción más probable es:

[
\mu_t=MA_{15}(RPS_t)
]

[
\sigma_t=SD_{250}(RPS_t)
]

[
Upper_t=\mu_t+0.75\sigma_t
]

[
Lower_t=\mu_t-0.75\sigma_t
]

Si el código utiliza la función estándar `StdDev` de EasyLanguage, se trata de desviación estándar poblacional, con divisor (N). ([Ayuda TradeStation][2])

Hay que confirmarlo con el `.ELD`, porque el PDF describe el cálculo pero no imprime el código.

## 2.4 Warm-up

Para obtener la primera banda válida se necesitan aproximadamente:

```text
7 barras para formar el primer retorno
+
250 observaciones del RPS
```

Por eso el informe muestra cinco años de datos cargados, pero solamente unos cuatro años efectivos de trading.

---

# 3. Reglas exactas de entrada y salida

## 3.1 Detección de extremo

```text
outside_t =
    RPS_t > Upper_t
    OR
    RPS_t < Lower_t
```

## 3.2 Filtro de tendencia

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

## 3.3 Dirección

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

## 3.4 Temporización

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

# 4. Ejemplo del artículo

En el ejemplo:

```text
V, rendimiento 7 días  = +3.20%
MA, rendimiento 7 días = +0.67%
```

Entonces:

[
RPS=\frac{3.20}{0.67}\approx4.77
]

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

[
RPS\approx-4.77
]

En ese caso rompería la banda inferior, pero V seguiría siendo el activo que más ha rendido.

Esto confirma que:

> La posición depende de `rV > rMA` o `rV < rMA`; no del signo del RPS.

---

# 5. Resultados publicados

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

## Resultado agregado

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

[
\frac{19.80}{5000}=0.00396
]

La expectativa publicada equivale aproximadamente a:

```text
39.6 puntos básicos por operación
```

La curva de capital de la página 8 es ascendente, pero muestra largos periodos planos y un comportamiento cíclico. El propio autor advierte que debe esperarse un Profit Factor inferior con datos reales y con otros activos. 

## Resultado long frente a short

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

# 6. ¿Dónde estaría el edge?

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

# 7. Problema matemático central: dividir retornos

La parte más débil de la estrategia es:

[
RPS=\frac{r_A}{r_B}
]

## 7.1 Denominador cercano a cero

Ejemplo:

```text
A = +0.10%
B = +0.01%
```

[
RPS=10
]

El indicador mostraría un extremo enorme, aunque la diferencia económica sea solamente:

```text
9 puntos básicos
```

En cambio:

```text
A = +3.00%
B = +2.00%
```

[
RPS=1.5
]

La diferencia económica es:

```text
100 puntos básicos
```

pero el RPS parece mucho menos extremo.

Por tanto, el RPS puede responder más al pequeño denominador que a la magnitud real de la divergencia.

## 7.2 Problemas de signo

```text
A = -4%
B = -2%
```

[
RPS=2
]

El RPS es positivo y relativamente alto, aunque A ha rendido claramente peor.

```text
A = +1%
B = -1%
```

[
RPS=-1
]

Aunque la separación económica es de 2 puntos porcentuales.

El filtro `rA > rB` o `rA < rB` resuelve la dirección de la operación, pero **no resuelve la medición defectuosa del grado de extremidad**.

## 7.3 División por cero

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

## 7.4 Distribución no robusta

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

# 8. Correlación no equivale a reversión

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

# 9. Problemas científicos del backtest publicado

El resultado del PDF es insuficiente para afirmar edge por los siguientes motivos esenciales.

## 9.1 Parámetros optimizados en la misma muestra

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

## 9.2 Un único par

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

## 9.3 Solamente 71 operaciones

Setenta y una observaciones son pocas para evaluar:

```text
colas
drawdown
estabilidad temporal
asimetría
dependencia de regímenes
```

Además, las operaciones están serialmente relacionadas porque utilizan ventanas superpuestas de siete, quince y 250 días.

## 9.4 Concentración en el lado long

El lado long produce la mayor parte del beneficio.

Esto permite hipótesis alternativas:

```text
la estrategia detecta buenos puntos para comprar V
pero no detecta correctamente buenos puntos para vender V

o

el periodo simplemente favoreció la exposición long en V
```

## 9.5 Ejecución simplificada

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

# 10. Cómo debe implementarse en TSIS

## 10.1 Separación señal–ejecución

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

## 10.2 Contrato de datos

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

## 10.3 Alineación temporal

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

## 10.4 Corporate actions

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

## 10.5 Apertura

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

## 10.6 Posiciones consecutivas

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

## 10.7 División por cero

Para la réplica:

```text
Si |return_reference| <= epsilon:
    RPS = UNAVAILABLE
    no generar señal
```

No conviene sumar arbitrariamente un epsilon al denominador, porque cambiaría la distribución completa.

Después deben probarse distintos valores de exclusión como análisis de sensibilidad.

---

# 11. Pseudocódigo de referencia

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

# 12. Cómo demostrar o destruir el supuesto edge

## Fase 1 — Réplica histórica

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

## Fase 2 — Verdadero out-of-sample postpublicación

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

## Fase 3 — Descomposición del origen del PnL

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

## Fase 4 — Descomposición temporal

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

## Fase 5 — Robustez

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

## Fase 6 — Costes y ejecución

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

# 13. Variantes matemáticas que merecen estudiarse

No debemos sustituir la estrategia original antes de replicarla. Primero se reproduce y después se comparan variantes preregistradas.

## Variante A — Diferencia de retornos

[
D_t=r^A_t-r^B_t
]

Ventajas:

```text
no divide por cero
magnitud económicamente interpretable
mantiene el signo correcto
```

Después:

[
Z_t=\frac{D_t-\mu_D}{\sigma_D}
]

## Variante B — Residuo con hedge ratio

[
r^A_t=\alpha_t+\beta_t r^B_t+\epsilon_t
]

Se opera el residuo:

[
Z^\epsilon_t=\frac{\epsilon_t-\mu_\epsilon}{\sigma_\epsilon}
]

Esto responde:

```text
¿Cuánto se ha movido A
más o menos de lo esperado
dado el movimiento de B?
```

Es conceptualmente más sólido.

## Variante C — Spread de precios logarítmicos

[
S_t=\log P^A_t-\beta\log P^B_t
]

Sólo debe operarse si presenta evidencia de estabilidad o mean reversion.

## Variante D — Par market-neutral

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

## Variante E — Peer basket

En lugar de depender de un único denominador:

[
residual_A=r_A-\sum_i\beta_i r_i
]

El benchmark podría ser:

```text
cesta de competidores
ETF sectorial
factor industrial
componente PCA
```

Esto reduce el riesgo de que un movimiento idiosincrático de MA provoque una falsa señal sobre V.

---

# 14. Encaje dentro de Market State y Event State

La estrategia confirma una distinción muy útil para TSIS.

## Market State observable en (t)

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

## Evento de investigación

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

## Outcome

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

# 15. Transferencia a small caps y futuros

## Small caps

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

## Futuros

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

# Conclusión

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

El primer artefacto debería fijar el contrato exacto de la réplica, las ambigüedades que requieren el `.ELD`, los datos físicos TSIS, los timestamps y los checksums publicados antes de escribir el backtest.

[1]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/rateofchange_function_.htm "https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/rateofchange_function_.htm"
[2]: https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/stddev_function_.htm "https://help.tradestation.com/10_00/eng/tsdevhelp/elword/function/stddev_function_.htm"
[3]: https://academic.oup.com/rfs/article-abstract/19/3/797/1646694 "https://academic.oup.com/rfs/article-abstract/19/3/797/1646694"
[4]: https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work "https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work"
[5]: https://research.monash.edu/en/publications/are-pairs-trading-profits-robust-to-trading-costs/ "https://research.monash.edu/en/publications/are-pairs-trading-profits-robust-to-trading-costs/"
[6]: https://math.nyu.edu/inmemoriam/avellaneda/AvellanedaLeeStatArb20090616.pdf "https://math.nyu.edu/inmemoriam/avellaneda/AvellanedaLeeStatArb20090616.pdf"
