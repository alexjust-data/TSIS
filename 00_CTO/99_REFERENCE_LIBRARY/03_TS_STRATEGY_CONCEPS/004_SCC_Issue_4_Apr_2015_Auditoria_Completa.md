# Auditoría completa — TradeStation Strategy Concepts Club, Issue 4 (abril de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. CCI Bollinger Bands Combo Strategy
2. Put/Call VRAO Add-on Strategy
3. ideas secundarias de backtesting presentes en el issue
4. auditoría temporal, matemática y metodológica
5. evidencia adicional contenida en los workspaces y .ELD
6. contratos de réplica para TSIS
7. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 15 páginas: `SCC Issue 4 Apr 2015.pdf`
- ZIP original de apoyo: `2015-04.zip`
- Contenedores `.ELD` y workspaces `.tsw` de ambas estrategias
- Imágenes renderizadas de las 15 páginas, incluidas:
  - el ejemplo de formación de señal CCI/Bollinger de la página física 6;
  - el informe completo de rendimiento de la página física 7;
  - la comparación de las tres curvas de capital de la página física 8;
  - los inputs y el esquema de composición de VRAO de las páginas físicas 11–13;
  - la comparación condensada de resultados de la página física 14.
- Los Markdown de los Issues 1–3 se utilizan únicamente como **modelo de profundidad y organización**, nunca como autoridad factual para este número.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF, los workspaces .tsw y los contenedores .ELD

AUDIT:
inferencia técnica, crítica científica y propuesta de implementación en TSIS
```

Cuando el PDF o el paquete no resuelven una decisión, se registra como ambigüedad. No se completa silenciosamente.

No se ha incorporado investigación web externa en esta auditoría. Las fórmulas reconstruidas que no aparecen literalmente en el PDF se marcan como reconstrucciones o candidatos de implementación.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 007 | CCI Bollinger Bands Combo | Mean reversion por capas; ES daily con entrada stop intradía y salida a la apertura siguiente | PF 1.87, 136 trades, 60.29% ganadoras, $19,520.58, diez años | el workspace conserva **8,000 configuraciones distintas** de optimización; la configuración publicada ocupa el puesto **2/8,000 por net profit** | Replicar como state machine multietapa, pero no aceptar el edge publicado |
| 008 | Put/Call VRAO Add-on | Componente de pyramiding condicionado por sentimiento de opciones; SPY daily | comparación entre Moving Average Machine sola y con hasta cuatro add-ons | la validación mezcla cambio de señal con cambio de exposición; los dos grids declarados contienen **18,628 configuraciones candidatas in-sample**; el número efectivamente evaluado no consta | Implementar como prueba de composición de estrategias, no como evidencia de alpha incremental |

## 0.1 Veredicto global

El Issue 4 contiene dos lecciones distintas y especialmente útiles para TSIS.

`CCI Bollinger Bands Combo` enseña a construir una estrategia como una **secuencia persistente de condiciones**:

```text
extremo de precio
→
confirmación de giro de un oscilador
→
orden stop válida durante una ventana
→
activación intradía
→
salida temporal
```

Su complejidad real no está en los indicadores, sino en el estado que debe sobrevivir entre barras. Además, el workspace revela que la configuración publicada no fue una elección inocente: aparece casi en el extremo superior de una búsqueda de 8,000 trials almacenados.

`Put/Call VRAO Add-on` no es una estrategia autónoma. Es un **operador de tamaño de posición** dependiente de otra estrategia. Por eso no debe evaluarse comparando únicamente beneficios absolutos. Hay que separar:

```text
calidad del timing del add-on
cantidad de capital expuesto
número de lotes
riesgo incremental
regla de salida heredada
```

La revista aporta material valioso, pero ninguna de las dos estrategias demuestra científicamente un edge reproducible.

```text
ISSUE_STATUS:
VALUABLE_SOURCE_MATERIAL

EDGE_STATUS:
UNPROVEN

IMPLEMENTATION_STATUS:
TWO_REPRODUCTION_CANDIDATES

SCIENTIFIC_RISK:
HIGH

LIVE_STATUS:
NOT_ELIGIBLE
```

---

# Parte I — Estrategia 007: CCI Bollinger Bands Combo Strategy

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-04-STRAT-007`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 4
- **Fecha declarada:** abril de 2015
- **Artículo:** *CCI Bollinger Bands Combo Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 4–8
- **Páginas impresas del artículo:** 3–7
- **Estilo declarado:** Mean reversion
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Swing trading
- **Mercado del backtest publicado:** E-mini S&P 500 futures
- **Símbolo de investigación:** `@ES=107XN`
- **Frecuencia:** Daily
- **Resolución Look-Inside-Bar:** 30 minutos
- **Archivos del ZIP:** estrategia, dos indicadores y workspace

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `BBLength` | 15 | Longitud del componente medio de Bollinger Bands |
| `BBStDvUp` | 0.9 | Desviaciones estándar de la banda superior |
| `BBStDvDn` | -0.5 | Desviaciones estándar de la banda inferior |
| `CCILength` | 9 | Longitud del CCI |
| `CCIxAvgLength` | 2 | Longitud del promedio exponencial del CCI |
| `SwingLowStrength` | 1 | Barras requeridas a cada lado de un swing low del CCI suavizado |
| `SwingHighStrength` | 1 | Barras requeridas a cada lado de un swing high del CCI suavizado |
| `HighLength` | 2 | Barras usadas para fijar el stop de entrada long |
| `LowLength` | 3 | Barras usadas para fijar el stop de entrada short |

La revista declara expresamente que los defaults fueron **parcialmente encontrados mediante optimización**.

### Estudios complementarios

El paquete contiene:

```text
TSL: CCI Bollinger Bands Combo
TSL: CCI xAverage
Bollinger Bands, indicador estándar de TradeStation
```

El indicador `TSL: CCI xAverage` representa:

```text
CCIValue
CCIxAvg
OverBought
OverSold
```

con niveles visuales de `+100` y `-100`.

### Evidencia adicional del ZIP

El workspace confirma:

```text
chart:
@ES=107XN Daily [CME]
E-mini S&P 500 Custom Continuous Contract

analysis techniques:
Bollinger Bands
TSL: CCI Bollinger Bands Combo
TSL: CCI xAverage

inputs presentes:
BBLength
BBStDvUp
BBStDvDn
CCILength
CCIxAvgLength
SwingLowStrength
SwingHighStrength
HighLength
LowLength
```

El `.tsw` es un contenedor OLE y conserva un stream `OptimizationData` de **15,841,143 bytes**. Su análisis revela información que no aparece impresa en la revista y se documenta en la sección 6.

El `.ELD` es un contenedor propietario. En este entorno no expone el código EasyLanguage como texto legible. Por ello el paquete confirma identidad, inputs y artefactos, pero no permite verificar de forma literal cada función o cada prioridad de órdenes.

El workspace contiene cadenas de versión de TradeStation 9.1 y 10.x. Eso indica que pudo ser abierto o migrado posteriormente; se utiliza como evidencia corroborativa, no como una cápsula inmutable de 2015.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero necesita una state machine persistente y replay intradía. |
| ¿Puede replicarse aproximadamente con el PDF? | **Sí.** |
| ¿Puede replicarse exactamente sin el source EasyLanguage? | **No del todo.** Persisten ambigüedades sobre pivots, cancelaciones y prioridad. |
| ¿El artículo prueba que combinar CCI y Bollinger crea edge? | **No.** El combo y sus componentes fueron observados en la misma muestra. |
| ¿La idea económica es plausible? | **Sí:** sobreextensión de precio seguida de indicios de agotamiento y rebote. |
| ¿El resultado publicado es out-of-sample? | **No.** |
| ¿La configuración fue seleccionada intensamente? | **Sí.** El paquete la sitúa 2ª por net profit entre 8,000 trials almacenados. |
| ¿Está preparada para operar? | **No.** Falta validación postpublicación, slippage real y ejecución sobre contratos físicos. |

Clasificación TSIS:

```text
MULTI_STAGE_MEAN_REVERSION_CANDIDATE
PERSISTENT_SETUP_STATE_REQUIRED
INTRABAR_STOP_ENTRY_REQUIRED
OPTIMIZATION_SELECTION_CRITICAL
CONTINUOUS_FUTURES_RISK
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La estrategia no consiste simplemente en:

```text
precio fuera de Bollinger
+
CCI sobrecomprado o sobrevendido
```

Es una secuencia de cuatro etapas.

### Etapa A — Registrar un extremo de precio

Para un posible long:

```text
el low cruza por debajo de la banda inferior
```

Para un posible short:

```text
el high cruza por encima de la banda superior
```

Ese cruce establece el **último lado significativo** de Bollinger.

### Etapa B — Esperar un giro confirmado del CCI suavizado

Para long:

```text
CCIxAvg forma un swing low
por debajo de -100
```

Para short:

```text
CCIxAvg forma un swing high
por encima de +100
```

La condición no exige que precio y pivot se produzcan en la misma barra.

### Etapa C — Fijar un nivel de activación

Para long:

```text
buy stop = highest high de las últimas 2 barras
```

Para short:

```text
sell short stop = lowest low de las últimas 3 barras
```

La revista utiliza la expresión **“the threshold price is then fixed”**. La interpretación más fiel es que el nivel se congela al generarse la señal, en lugar de recalcularse cada día.

### Etapa D — Mantener la orden durante cinco barras

La orden de entrada permanece válida durante las cinco barras siguientes.

Si se ejecuta, la posición se liquida en la apertura de la barra siguiente.

En una frase:

> La estrategia busca una sobreextensión, espera una evidencia retardada de giro y sólo entra si el precio demuestra continuación suficiente para romper un nivel local en sentido contrario al extremo inicial.

Eso mezcla:

```text
mean reversion de contexto
+
confirmación de momentum para la entrada
```

No es una reversión inmediata al tocar la banda.

---

## 3. Reconstrucción matemática

## 3.1 Bollinger Bands

La reconstrucción candidata es:

\[
M_t = MA_{BBLength}(C_t)
\]

\[
S_t = SD_{BBLength}(C_t)
\]

\[
Upper_t = M_t + BBStDvUp\cdot S_t
\]

\[
Lower_t = M_t + BBStDvDn\cdot S_t
\]

Con los defaults:

\[
Upper_t = M_t + 0.9S_t
\]

\[
Lower_t = M_t - 0.5S_t
\]

Las bandas son marcadamente asimétricas:

```text
upper: +0.9 sigma
lower: -0.5 sigma
```

Por tanto, no se está usando un canal convencional simétrico de dos desviaciones. El lado long recibe más oportunidades de setup porque la banda inferior está más cerca de la media.

El PDF dice que se utilizan las Bollinger Bands convencionales de TradeStation, pero no imprime:

```text
función exacta de desviación
convención poblacional o muestral
tratamiento de warm-up
precio exacto si el workspace se modifica
```

Para la réplica hay que congelar estas decisiones.

## 3.2 CCI

La fórmula tradicional candidata utiliza el precio típico:

\[
TP_t = \frac{H_t + L_t + C_t}{3}
\]

\[
MA^{TP}_t = MA_{CCILength}(TP_t)
\]

\[
MD_t = \frac{1}{L}\sum_{i=0}^{L-1}|TP_{t-i}-MA^{TP}_t|
\]

\[
CCI_t = \frac{TP_t-MA^{TP}_t}{0.015\cdot MD_t}
\]

La revista no imprime el source y, por tanto, esta fórmula debe tratarse como **candidato de réplica**, no como prueba de la implementación interna.

## 3.3 Promedio exponencial del CCI

La modificación central respecto del indicador CCI Average tradicional es:

\[
CCIxAvg_t = EMA_{CCIxAvgLength}(CCI_t)
\]

Con longitud 2, el suavizado es mínimo y reacciona rápidamente.

Esto importa científicamente porque `CCIxAvgLength = 2` se encuentra en el límite inferior del rango observado en el workspace de optimización.

## 3.4 Swing low y swing high

Con strength 1, un swing low en la barra candidata (k) exige aproximadamente:

\[
CCIxAvg_k \le CCIxAvg_{k-1}
\]

\[
CCIxAvg_k < CCIxAvg_{k+1}
\]

Y un swing high:

\[
CCIxAvg_k \ge CCIxAvg_{k-1}
\]

\[
CCIxAvg_k > CCIxAvg_{k+1}
\]

El detalle igualdad/estricto depende de la función EasyLanguage empleada y no puede confirmarse con el PDF.

### Confirmación retardada

Un pivot con una barra a la derecha **no puede conocerse en la propia barra pivot**. Sólo queda confirmado cuando termina la barra siguiente.

Por tanto:

```text
pivot en t-1
se confirma al cierre de t
orden más temprana para t+1
```

Esto no es look-ahead si se implementa así. Sí lo sería si TSIS asignara la señal retrospectivamente a la fecha del pivot.

## 3.5 Setup Bollinger long

La condición de estado sería:

```text
if Low crosses below LowerBand:
    last_bollinger_event = LOWER_BAND_CROSS
```

El setup se invalida cuando precio cruza el midpoint. La revista no especifica si se usa:

```text
close
high/low
precio de entrada del indicador estándar
```

para ese cruce de cancelación.

## 3.6 Setup Bollinger short

```text
if High crosses above UpperBand:
    last_bollinger_event = UPPER_BAND_CROSS
```

También queda invalidado al cruzar el midpoint en el sentido correspondiente.

## 3.7 Condición long completa

En el cierre de decisión (t):

```text
last_bollinger_event == LOWER_BAND_CROSS
AND
existe swing low confirmado de CCIxAvg en las últimas 3 barras
AND
valor del swing low < -100
```

Entonces:

\[
LongStop_t = \max(H_t,H_{t-1})
\]

La orden se habilita para las cinco barras siguientes.

## 3.8 Condición short completa

```text
last_bollinger_event == UPPER_BAND_CROSS
AND
existe swing high confirmado de CCIxAvg en las últimas 3 barras
AND
valor del swing high > +100
```

Entonces:

\[
ShortStop_t = \min(L_t,L_{t-1},L_{t-2})
\]

La orden se habilita durante cinco barras.

## 3.9 Activación intradía

Long:

```text
si el mercado toca o atraviesa LongStop:
    entrar long mediante stop
```

Short:

```text
si el mercado toca o atraviesa ShortStop:
    entrar short mediante stop
```

Una barra diaria sólo informa de que el high/low pudo alcanzar el nivel. No informa de:

```text
primer precio ejecutable
orden temporal de movimientos
gap a través del stop
spread
slippage
```

De ahí el uso de Look-Inside-Bar a 30 minutos.

## 3.10 Salida

La salida publicada es:

```text
exit all positions at market on the open of the next bar
```

Si la entrada stop se ejecuta dentro de la sesión diaria (t), la salida se produce en la apertura de la sesión diaria siguiente (t+1).

No existe:

```text
stop loss
profit target
salida por midpoint
salida por CCI
```

## 3.11 Warm-up mínimo

El warm-up depende de:

```text
BBLength = 15
CCILength = 9
CCIxAvgLength = 2
swing search y right strength
```

La réplica debe declarar un `MaxBarsBack` gobernado y no permitir señales hasta que todas las series sean válidas.

---

## 4. State machine y ambigüedades contractuales

## 4.1 El “último cruce significativo” persiste

La redacción implica memoria entre barras. No basta con calcular una expresión booleana local.

Estado mínimo:

```text
NONE
LOWER_BAND_ACTIVE
UPPER_BAND_ACTIVE
```

## 4.2 Cancelación por midpoint

Debe resolverse:

```text
qué precio cruza el midpoint
si la cancelación sucede al cierre o intradía
si cancela una orden ya armada
si sólo cancela la fase previa al pivot
```

El PDF sólo afirma que el setup se niega cuando el precio cruza el midpoint.

## 4.3 Cruce de la banda opuesta

No se explica si un cruce posterior de la banda contraria:

```text
reemplaza inmediatamente el estado
cancela una orden pendiente
puede coexistir con el setup anterior
```

TSIS debe prohibir la coexistencia silenciosa y registrar la política.

## 4.4 Ventana de tres barras para el pivot

La expresión “a swing low has been identified in the previous three bars” puede significar:

```text
buscar el último pivot confirmado dentro de una ventana de 3
```

o una función concreta de TradeStation con semántica propia.

No debe asignarse retrospectivamente el pivot como si se hubiera conocido antes de la barra de confirmación.

## 4.5 Umbral fijado frente a recalculado

La fuente dice que el threshold queda fijado. La réplica propuesta utilizará:

```text
entry_stop_price = valor calculado al armar la señal
```

No:

```text
entry_stop_price = rolling high/low actualizado cada día
```

Esta decisión deberá validarse contra fechas de trades exportadas de TradeStation.

## 4.6 Cinco barras de validez

Hay que fijar si “following five bars” significa:

```text
barras t+1 ... t+5 inclusivas
```

La interpretación recomendada es TTL de cinco sesiones ejecutables después de la generación.

## 4.7 Setup nuevo mientras existe una orden pendiente

No se publica si una señal nueva:

```text
reinicia TTL
actualiza precio
sustituye dirección
se ignora
```

TSIS debe registrar un `pending_signal_id` y una causa de reemplazo.

## 4.8 Entry gap-through

Si la apertura de la nueva sesión ya está por encima del buy stop o por debajo del sell stop, la orden no puede rellenarse al nivel teórico anterior.

Modelo mínimo:

```text
long fill = max(session_open, stop_price) + slippage
short fill = min(session_open, stop_price) - slippage
```

sujeto a datos reales y a la política del motor.

## 4.9 No existe “ausencia de overnight risk”

La revista afirma que ES es básicamente un mercado de 24 horas y que la salida en el open siguiente no representa “true overnight risk”, salvo el fin de semana.

Desde un punto de vista de backtesting, la clasificación correcta es:

```text
posición mantenida entre sesiones daily
+
pausa de mantenimiento
+
posible gap de reapertura
+
riesgo de fin de semana los viernes
```

Que el mercado negocie muchas horas reduce, pero no elimina, el riesgo de discontinuidad.

---

## 5. Resultados publicados

### 5.1 Configuración

```text
Símbolo: @ES=107XN
Bar interval: Daily
Historia: 10 años, terminando 31/12/2014
Capital inicial: $10,000
Trade size: 1 contrato
Comisión: $2.36 por trade
Slippage: $0
Look-Inside-Bar: 30 minutos
```

El periodo efectivo del informe es:

```text
9 años, 9 meses y 17 días
```

### 5.2 Resultado agregado

| Métrica | Resultado |
|---|---:|
| Net Profit | $19,520.58 |
| Gross Profit | $41,912.96 |
| Gross Loss | -$22,392.38 |
| Profit Factor | 1.87 |
| Trades | 136 |
| Winning trades | 82 |
| Losing trades | 54 |
| Percent Profitable | 60.29% |
| Avg. Trade Net Profit | $143.53 |
| Avg. Winning Trade | $511.13 |
| Avg. Losing Trade | -$414.67 |
| Ratio Avg Win / Avg Loss | 1.23 |
| Largest Winning Trade | $2,020.28 |
| Largest Losing Trade | -$2,592.22 |
| Max consecutive winners | 11 |
| Max consecutive losers | 4 |
| Avg bars in winners | 2.00 |
| Avg bars in losers | 2.00 |
| Return on Initial Capital | 195.21% |
| Annual Rate of Return | 11.05% |
| RINA Index | 2,506.89 |
| Percent of Time in Market | 3.29% |
| Account Size Required | $2,653.32 |

El número de barras por trade aparece como 2 porque TradeStation cuenta la barra de entrada y la de salida, aunque la posición se liquide en la apertura de la barra siguiente.

### 5.3 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Net Profit | $14,408.76 | $5,111.82 |
| Profit Factor | 2.24 | 1.48 |
| Trades | 67 | 69 |
| Percent Profitable | 70.15% | 50.72% |
| Avg Trade | $215.06 | $74.08 |
| Avg Winner | $554.32 | $453.14 |
| Avg Loser | -$582.22 | -$316.12 |
| Largest Winner | $1,782.78 | $2,020.28 |
| Largest Loser | -$2,592.22 | -$1,267.22 |
| Max consecutive losers | 3 | 6 |

Aproximadamente:

\[
\frac{14,408.76}{19,520.58}=73.8\%
\]

 del beneficio procede del lado long.

La estrategia no demuestra una simetría fuerte. El lado short tiene un Profit Factor de 1.48 y sólo 50.72% de acierto.

### 5.4 Equity curve

La curva publicada es ascendente en conjunto, pero contiene:

```text
un periodo inicial negativo
mesetas prolongadas
un salto muy importante alrededor de 2011
poca actividad en varios tramos
```

La revista estima un maximum weekly drawdown cercano al 24%.

### 5.5 Comparación de componentes

Se publican tres versiones:

| Estrategia | Trades | RINA publicada | Drawdown semanal aproximado |
|---|---:|---:|---:|
| CCI + Bollinger Combo | 136 | 2,506.89 | 24% |
| CCI custom aislado | 200 | 744.34 | 40% |
| Bollinger custom aislado | 416 | 16.50 | 70% |

La curva combinada es visualmente más estable y opera mucho menos.

Esto sugiere que la intersección de condiciones selecciona un subconjunto más favorable. No demuestra todavía que la combinación aporte información incremental fuera de muestra.

---

## 6. Forense del workspace de optimización

Éste es el hallazgo más importante del paquete.

## 6.1 Estructura

El workspace contiene un stream:

```text
OptimizationData
size = 15,841,143 bytes
```

La estructura interna conserva tres bloques de 8,000 registros:

```text
bloque 1:
resultados completos

bloque 2:
duplicado bit a bit de resultados completos

bloque 3:
mismos trial IDs e inputs, con métricas placeholder o nulas
```

Por tanto:

```text
NO son 24,000 tests independientes
SÍ son 8,000 configuraciones distintas almacenadas
```

## 6.2 Inputs y lattice observado

Valores distintos encontrados:

| Input | Valores observados | Número |
|---|---|---:|
| `BBLength` | 12, 15, 18, 21 | 4 |
| `BBStDvUp` | 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 | 6 |
| `BBStDvDn` | -1.0, -0.9, -0.8, -0.7, -0.6, -0.5 | 6 |
| `CCILength` | 6, 9, 12, 15 | 4 |
| `CCIxAvgLength` | 2, 4, 6, 8, 10 | 5 |
| `SwingLowStrength` | 1–5 | 5 |
| `SwingHighStrength` | 1–5 | 5 |
| `HighLength` | 1–5 | 5 |
| `LowLength` | 1–5 | 5 |

Un full factorial completo habría contenido:

\[
4\times6\times6\times4\times5^5=1,800,000
\]

configuraciones.

El workspace conserva 8,000, equivalentes al:

\[
\frac{8,000}{1,800,000}=0.444\%
\]

 del lattice posible.

## 6.3 Muestreo no uniforme

Los 8,000 trials no cubren uniformemente los valores. Por ejemplo:

```text
CCILength = 9:
5,286 de 8,000

CCIxAvgLength = 2:
7,238 de 8,000

SwingLowStrength = 1:
5,818 de 8,000

HighLength = 2:
4,998 de 8,000
```

La concentración es compatible con una búsqueda adaptativa o genética que converge hacia regiones prometedoras. El paquete no contiene una etiqueta inequívoca del método, de modo que **no se afirma** que fuera genética; sí puede afirmarse que no es una muestra uniforme ni un full grid.

## 6.4 Posición de la configuración publicada

Configuración publicada:

```text
15, 0.9, -0.5, 9, 2, 1, 1, 2, 3
```

Dentro de los 8,000 trials almacenados ocupa:

| Métrica | Resultado | Ranking |
|---|---:|---:|
| Net Profit | $19,520.57 | **2 / 8,000** |
| Avg Trade | $143.53 | **52 / 8,000** |
| Profit Factor | 1.8718 | **93 / 8,000** |
| Percent Profitable | 60.29% | **379 / 8,000** |

Esto sitúa el net profit publicado en el percentil aproximado:

```text
99.975%
```

No es una configuración representativa del espacio de búsqueda.

## 6.5 Mejor configuración almacenada por net profit

| Input | Valor |
|---|---:|
| `BBLength` | 18 |
| `BBStDvUp` | 0.6 |
| `BBStDvDn` | -0.5 |
| `CCILength` | 9 |
| `CCIxAvgLength` | 2 |
| `SwingLowStrength` | 1 |
| `SwingHighStrength` | 5 |
| `HighLength` | 2 |
| `LowLength` | 1 |

Resultados principales:

```text
Net Profit: $19,877.21
Profit Factor: 2.203
Trades: 124
Percent Profitable: 59.68%
Avg Trade: $160.30
```

La diferencia de net profit respecto del publicado es sólo:

```text
$356.63
```

Por tanto, el autor pudo haber descartado el máximo absoluto por razones cualitativas o de estabilidad. Aun así, la configuración publicada sigue siendo el segundo mejor net profit de toda la muestra almacenada.

## 6.6 Distribución del espacio almacenado

Entre los 8,000 trials:

```text
net profit positivo: 89.03%
net profit negativo: 878 configuraciones
Profit Factor > 1.5: 14.38%
net profit > $15,000: 122 configuraciones
```

La mediana fue aproximadamente:

```text
Net Profit: $5,283.88
Profit Factor: 1.219
Avg Trade: $43.14
```

La configuración publicada está muy por encima de la experiencia mediana del espacio explorado.

## 6.7 Parámetros en frontera

La configuración seleccionada utiliza:

```text
BBStDvDn = -0.5, extremo del rango
CCIxAvgLength = 2, extremo del rango
SwingLowStrength = 1, extremo del rango
```

Los mejores trials también se concentran en estas fronteras. Esto abre dos interpretaciones:

```text
A. existe una dirección monotónica real y debería ampliarse el rango
B. el optimizador está explotando un borde in-sample
```

La única forma de distinguirlas es mantener la configuración congelada y probarla después de la publicación.

## 6.8 Consecuencia científica

El resultado publicado debe tratarse como:

```text
winner selected after a broad search
```

No como:

```text
one hypothesis tested once
```

El número efectivo de grados de libertad es mucho mayor que nueve inputs porque incluye:

```text
rango de cada input
método de búsqueda
métrica observada
selección final
mercado elegido
periodo elegido
componentes comparados
```

---

## 7. ¿Dónde podría estar el edge?

La tesis funcional puede formularse así:

> Una penetración anormal de una banda de volatilidad identifica sobreextensión. Si después el CCI suavizado forma un pivot extremo y el precio rompe una resistencia o soporte local, existe una probabilidad elevada de continuación de la reversión durante el resto de la sesión, hasta la apertura de la siguiente sesión diaria.

Los posibles mecanismos son:

```text
agotamiento temporal de presión vendedora o compradora
liquidación forzada seguida de estabilización
reversión de volatilidad tras un shock moderado
confirmación de cambio de microtendencia
sesgo intradía de rebote en índices
```

Pero el documento no demuestra que el beneficio proceda de esa cadena causal.

### Hipótesis alternativas

El PnL podría proceder de:

```text
sesgo long estructural del ES
banda inferior muy cercana a la media
selección de parámetros in-sample
particularidades del periodo 2005–2014
fills favorables de stop orders
cero slippage
roll del continuo
una pequeña fracción de trades concentrados alrededor de 2011
```

La fuerte superioridad long obliga a comparar contra baselines long-only.

---

## 8. Problemas científicos y técnicos

## 8.1 Optimización in-sample intensa

El paquete demuestra 8,000 trials almacenados. La configuración publicada es la segunda por net profit.

No se publica:

```text
train/test split
walk-forward
métrica formal de selección
corrección por múltiples pruebas
preregistro
```

## 8.2 La comparación de componentes no es OOS

La curva combo, la CCI aislada y Bollinger aislada se evalúan en el mismo periodo y después de diseñar el combo.

La comparación puede describir la muestra. No prueba generalización.

## 8.3 Menor drawdown puede ser menor exposición

El combo genera:

```text
136 trades
```

frente a:

```text
CCI: 200
Bollinger: 416
```

Menos señales y 3.29% de tiempo en mercado reducen naturalmente oportunidades de drawdown. Hace falta una comparación:

```text
exposure-matched
trade-count-matched
signal-date-matched
```

## 8.4 RINA extremo

`RINA = 2,506.89` depende en gran parte de la exposición muy baja. No debe interpretarse como una medida universal de robustez.

## 8.5 Asimetría long/short

Long aporta 73.8% del beneficio y tiene PF 2.24. Short sólo PF 1.48.

Hay que probar:

```text
long-only combo
short-only combo
buy-and-hold filtered dates
random long dates con igual frecuencia
```

## 8.6 Slippage cero

Las entradas son stop orders intradía, precisamente el tipo de orden donde el slippage puede ser adverso.

```text
published slippage = $0
```

es una hipótesis demasiado favorable.

## 8.7 LIBB de 30 minutos

Una barra de 30 minutos sigue ocultando:

```text
trayectoria dentro de la subbarra
bid/ask
primer trade ejecutable
saltos a través del stop
```

No equivale a tick replay.

## 8.8 Continuous futures sintético

`@ES=107XN` no es un instrumento negociable. El backtest debe separar:

```text
continuo para construir señales
contrato físico para fills y PnL
```

## 8.9 Roll sin back adjustment

No usar back adjustment evita precios históricos ficticios, pero crea discontinuidades de roll. Una banda, un CCI o un highest high pueden reaccionar al cambio de contrato y producir señales mecánicas.

## 8.10 Trades que cruzan el roll

La estrategia puede armar un setup en un contrato y ejecutar o salir después del rollover. Hace falta una política de mapping físico.

## 8.11 Tick rounding

Los niveles calculados deben redondearse al tick legal del contrato. La dirección del redondeo debe ser conservadora:

```text
buy stop → redondeo hacia arriba
sell stop → redondeo hacia abajo
```

## 8.12 Gap-through

Un stop no garantiza el precio del stop. El modelo diario con LIBB puede rellenarlo demasiado favorablemente.

## 8.13 Pivots y timestamp legal

Los swings requieren datos posteriores al punto pivot. El sistema debe distinguir:

```text
pivot_timestamp
confirmation_timestamp
order_activation_timestamp
```

## 8.14 El “open siguiente” no elimina gap risk

Existe riesgo durante el mantenimiento diario y durante el fin de semana.

## 8.15 Capital inicial y leverage

Un contrato de ES sobre $10,000 implica leverage considerable. `Account Size Required = $2,653.32` no representa necesariamente:

```text
margen real histórico
stress margin
overnight margin
liquidación por variación
```

## 8.16 El lado inferior está más cerca

`-0.5 sigma` frente a `+0.9 sigma` produce distinta frecuencia y severidad de setups. El resultado long superior puede estar ligado a esa asimetría optimizada.

## 8.17 Cinco barras añaden otro grado de libertad

El TTL no es un input publicado, pero es una decisión de diseño que pudo elegirse tras explorar alternativas.

## 8.18 Salida única no explica el fenómeno

Salir en la apertura siguiente no demuestra que la reversión termine ahí. Se necesitan outcomes por horizonte:

```text
trigger → session close
trigger → next open
trigger → next close
1–5 sesiones
```

## 8.19 Riesgo de eventos concentrados

La curva muestra que una parte importante del beneficio se acumula en periodos concretos. Debe medirse contribución por año y por regime.

---

## 9. Cómo debe implementarse en TSIS

## 9.1 Separar estado, señal y orden

Tres objetos distintos:

```text
setup_state
armed_entry_signal
live_stop_order
```

No deben colapsarse en un único booleano.

## 9.2 Market State diario

Campos mínimos:

```text
session_date
bb_mid
bb_upper
bb_lower
low_cross_lower
high_cross_upper
midpoint_reset_long
midpoint_reset_short
cci
cci_xavg
confirmed_swing_low
confirmed_swing_high
swing_value
```

## 9.3 Pending signal

```text
signal_id
direction
decision_timestamp
source_bollinger_event_timestamp
pivot_timestamp
pivot_confirmation_timestamp
entry_stop_price
activation_session
ttl_sessions
expiry_session
status
cancel_reason
```

## 9.4 Ejecución intradía

Para equities futuras dentro de TSIS:

```text
013_ohlcv_1m_quote_guarded
```

sería el candidato de ejecución.

Para ES hará falta una fuente específica de contratos físicos y barras/trades intradía.

## 9.5 Contratos físicos

Cada evento debe guardar:

```text
continuous_symbol
physical_contract
roll_rule
roll_effective_timestamp
signal_contract
execution_contract
```

## 9.6 Modelo de fills

Escenarios mínimos:

```text
ideal stop
stop + medio spread
stop + spread completo
gap-through
1m quote-guarded
trade replay
```

## 9.7 Session template

Debe congelarse:

```text
session open
session close
maintenance break
holiday calendar
timezone
Friday/Sunday mapping
```

## 9.8 Optimización gobernada

El experimento debe guardar:

```text
full_lattice_size = 1,800,000
trials_evaluated = 8,000
search_method
random_seed o population seed
objective metric
selection rule
all trial results
selected_trial_id
```

## 9.9 Estado de indisponibilidad

```text
INSUFFICIENT_WARMUP
MISSING_INTRADAY_DATA
MISSING_PHYSICAL_CONTRACT
ROLL_AMBIGUITY
PIVOT_NOT_CONFIRMED
STOP_NOT_TICK_ALIGNED
SESSION_TEMPLATE_UNKNOWN
```

## 9.10 Lineage

Cada trade debe enlazar:

```text
setup event
pivot event
pending order
fill event
exit event
continuous-to-physical mapping
cost model
```

---

## 10. Pseudocódigo de referencia

```python
from dataclasses import dataclass
from enum import Enum


class BollingerState(str, Enum):
    NONE = "NONE"
    LOWER_ACTIVE = "LOWER_ACTIVE"
    UPPER_ACTIVE = "UPPER_ACTIVE"


@dataclass
class PendingEntry:
    direction: str
    stop_price: float
    created_session: str
    remaining_sessions: int = 5


def on_daily_close(state, bar, indicators):
    # 1. Actualizar estado Bollinger.
    if crossed_below(bar.low, indicators.lower_band):
        state.bollinger_state = BollingerState.LOWER_ACTIVE

    elif crossed_above(bar.high, indicators.upper_band):
        state.bollinger_state = BollingerState.UPPER_ACTIVE

    # La semántica exacta del midpoint debe fijarse por contrato.
    if midpoint_invalidates_long(bar, indicators.midline):
        if state.bollinger_state == BollingerState.LOWER_ACTIVE:
            state.bollinger_state = BollingerState.NONE

    if midpoint_invalidates_short(bar, indicators.midline):
        if state.bollinger_state == BollingerState.UPPER_ACTIVE:
            state.bollinger_state = BollingerState.NONE

    # 2. Armar señal long tras pivot confirmado.
    if (
        state.bollinger_state == BollingerState.LOWER_ACTIVE
        and confirmed_recent_swing_low(
            indicators.cci_xavg,
            strength=1,
            search_bars=3,
            max_value=-100.0,
        )
    ):
        stop = tick_round_up(max(bar.high, state.previous_bar.high))
        state.pending = PendingEntry("LONG", stop, bar.session_date, 5)

    # 3. Armar señal short.
    elif (
        state.bollinger_state == BollingerState.UPPER_ACTIVE
        and confirmed_recent_swing_high(
            indicators.cci_xavg,
            strength=1,
            search_bars=3,
            min_value=100.0,
        )
    ):
        stop = tick_round_down(
            min(bar.low, state.previous_bar.low, state.two_bars_ago.low)
        )
        state.pending = PendingEntry("SHORT", stop, bar.session_date, 5)


def on_intraday_event(state, event):
    if state.pending is None or state.position is not None:
        return

    if state.pending.direction == "LONG" and event.ask >= state.pending.stop_price:
        fill = max(event.ask, state.pending.stop_price)
        state.position = enter_long(fill, signal=state.pending)
        state.pending = None

    elif state.pending.direction == "SHORT" and event.bid <= state.pending.stop_price:
        fill = min(event.bid, state.pending.stop_price)
        state.position = enter_short(fill, signal=state.pending)
        state.pending = None


def on_session_open(state, open_event):
    # Exit de la posición tomada en la sesión anterior.
    if state.position is not None and state.position.entry_session != open_event.session:
        exit_position_at_open(state.position, open_event)
        state.position = None


def on_session_end(state):
    if state.pending is not None:
        state.pending.remaining_sessions -= 1
        if state.pending.remaining_sessions == 0:
            cancel(state.pending, reason="TTL_EXPIRED")
            state.pending = None
```

Este pseudocódigo no pretende sustituir el source EasyLanguage. Explicita las decisiones que el backtester debe gobernar.

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica de checksum

Objetivo:

```text
136 trades
67 long
69 short
Net Profit ≈ $19,520.58
PF ≈ 1.87
```

Periodo:

```text
30/12/2004–31/12/2014
```

### Fase 2 — Reconciliación de señales

Exportar desde TradeStation:

```text
fecha de cruce Bollinger
fecha y valor del pivot
fecha de armado
stop price
fecha/hora de fill
fecha/hora de exit
```

### Fase 3 — Resolver ambigüedades

Comparar variantes:

```text
threshold fixed vs rolling
midpoint cancels before vs after arming
TTL t+1..t+5
pivot search exact
```

La variante que reconcilie la trade list se congela.

### Fase 4 — Reproducción del search space

Registrar los 8,000 trials del paquete como evidencia histórica y reconstruir:

```text
rangos
método de búsqueda
objetivo
ranking
```

No volver a seleccionar parámetros todavía.

### Fase 5 — Verdadero OOS postpublicación

Congelar:

```text
15, 0.9, -0.5, 9, 2, 1, 1, 2, 3
```

Probar desde la primera sesión posterior a la publicación de abril de 2015 hasta el final de datos disponibles.

Reportar por bloques:

```text
2015–2017
2018–2020
2021–2023
2024–actualidad disponible
```

### Fase 6 — Contratos físicos

Repetir sobre contratos individuales con roll gobernado.

### Fase 7 — Slippage y gap-through

Escenarios:

```text
0.25, 0.5, 1 y 2 ticks
medio spread
spread completo
gap fill
```

### Fase 8 — Ablation científica

Comparar:

```text
Bollinger solo
CCI solo
combo
combo con dates aleatorias
combo exposure-matched
combo trade-count-matched
```

### Fase 9 — Long/short

Evaluar por separado:

```text
long-only
short-only
simétrico
```

### Fase 10 — Descomposición temporal

Outcome desde trigger:

```text
hasta session close
hasta next session open
hasta next close
1–5 sesiones
```

### Fase 11 — Robustez local

No buscar el mejor punto. Medir la superficie alrededor del publicado.

Especial atención a:

```text
CCIxAvgLength 2–6
SwingLowStrength 1–3
BBStDvDn -0.5 a -0.8
```

### Fase 12 — Regímenes

Separar:

```text
volatilidad alta/baja
bull/bear market
pre/post 2020
roll windows
macro announcement days
```

### Fase 13 — Corrección por búsqueda

El test de la familia debe considerar al menos los 8,000 trials almacenados, no sólo el ganador publicado.

---

## 12. Variantes posteriores a la réplica

No deben mezclarse con la reproducción original.

### Variante A — Bandas simétricas

```text
+0.5/-0.5
+0.9/-0.9
```

para aislar el efecto del sesgo direccional.

### Variante B — Distancia normalizada

Usar `%B` o z-score de precio en lugar de un cruce binario.

### Variante C — Pivot sin valores retrospectivos

Registrar sólo el `confirmation_timestamp` y usarlo como tiempo del evento.

### Variante D — Threshold ATR

Sustituir highest/lowest por un nivel normalizado por ATR.

### Variante E — Entry market tras confirmación

Aislar si el stop de confirmación añade información o simplemente empeora precio.

### Variante F — Exits por horizonte

Comparar next open con:

```text
session close
next close
CCI midpoint
Bollinger midpoint
trailing stop
```

### Variante G — Dynamic TTL

Relacionar validez con volatilidad o tiempo desde extremo.

### Variante H — No-trade alrededor del roll

Excluir ventanas de cambio de contrato para medir artefactos del continuo.

---

## 13. Encaje en Market State y Event State

### Market State

```text
bb_mid
bb_upper
bb_lower
price_percent_b
cci
cci_xavg
volatility_regime
session_context
roll_context
```

### Event State 1 — Extremo Bollinger

```text
event_type:
price_volatility_band_extreme

side:
lower_cross | upper_cross

decision_timestamp:
session_close_t
```

### Event State 2 — Pivot confirmado

```text
event_type:
cci_xavg_pivot_confirmed

pivot_timestamp:
t-k

confirmation_timestamp:
t

extreme_value:
cci_xavg_pivot
```

### Event State 3 — Señal armada

```text
event_type:
combo_reversal_entry_armed

entry_stop
activation_start
expiry
```

### Event State 4 — Activación

```text
event_type:
stop_entry_triggered

trigger_timestamp
fill_timestamp
fill_price
slippage
```

### Outcomes

```text
trigger_to_close_return
trigger_to_next_open_return
MFE
MAE
one_bar_return
five_bar_return
roll_overlap
```

### Distinción clave

```text
fenómeno:
sobreextensión + pivot + ruptura local

estrategia:
entrar por stop y salir al open siguiente
```

TSIS puede descubrir que el evento contiene información pero que la respuesta publicada no es óptima.

---

## 14. Transferencia a small caps y otros mercados

### Small caps

La estructura conceptual puede ser útil:

```text
extremo
→
agotamiento
→
confirmación
```

pero los defaults de ES no se trasladan.

En small caps hay que añadir:

```text
news_catalyst_context
halt_context
liquidity
spread
short availability
float
session segmentation
```

Un low bajo una banda puede ser una dilución o un offering, no una desviación temporal.

### Equities líquidas

Es más viable, pero la salida al siguiente open implica riesgo overnight real y corporate actions.

### FX

Requiere definir:

```text
daily cutoff
bid/ask
rollover financing
weekend gap
```

### Futuros

Es el mercado original, pero sólo con contratos físicos y roll auditable.

### Uso recomendado en TSIS

```text
primero:
evento genérico de sobreextensión + pivot

más adelante:
respuesta operativa específica
```

---

## 15. Veredicto de CCI Bollinger Bands Combo

La idea merece ser implementada porque obliga a TSIS a representar correctamente:

```text
estado persistente
confirmación retardada
señal con TTL
orden stop intradía
salida intersesión
optimización registrada
```

Pero el resultado publicado no es evidencia suficiente de edge debido a:

```text
8,000 trials almacenados
configuración 2ª por net profit
cero slippage
continuo sintético
fuerte asimetría long/short
sin OOS
```

Decisión:

```text
IMPLEMENTAR:
sí, como reproducción gobernada

ACEPTAR EDGE:
no

OPTIMIZAR DE NUEVO:
no antes del OOS congelado

LIVE:
no
```

Gate propuesto:

```text
CCI-BOLLINGER-PERSISTENT-STATE-INTRABAR-AND-POSTPUBLICATION-OOS-GATE
```

---

# Parte II — Estrategia 008: Put/Call VRAO Add-on Strategy

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-04-STRAT-008`
- **Artículo:** *Put/Call VRAO Add-on Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas:** 10–14
- **Páginas impresas:** 9–13
- **Estilo declarado:** Trend following
- **Mercado declarado:** Equities
- **Horizonte declarado:** Position trading
- **Activo del backtest:** SPY daily
- **Dependencia:** TSL:Mov Avg Machine como estrategia primaria
- **Naturaleza:** componente de add-on; no abre una posición inicial

### Inputs default publicados

| Input | Default | Función |
|---|---:|---|
| `PCVolRatioAvgLength` | 63 | Longitud de media del put/call volume ratio |
| `OscLength` | 126 | Longitud del rango usado para normalizar el oscilador |
| `BullLevel` | 0.9 | Área de sentimiento extremo bullish/contrarian |
| `BearLevel` | 0.1 | Área de sentimiento extremo bearish/contrarian |
| `MaxAdds` | 4 | Máximo de entradas adicionales tras la entrada inicial |

### Inputs finalmente utilizados en el backtest

Tras la optimización:

```text
PCVolRatioAvgLength = 15
OscLength = 20
BullLevel = 0.87
BearLevel = 0.13
MaxAdds = 4
```

La estrategia primaria utiliza:

```text
NumMAs = 2
MA1 = SMA 36
MA2 = EMA 53
```

### Evidencia adicional del ZIP

El workspace confirma:

```text
SPY Daily [ARCX]
TSL:Mov Avg Machine
TSL:Mov Avg Machine indicator
TSL:Put/Call VRAO
TSL:Put/Call VRAO Add-on
```

También conserva los valores visibles:

```text
BullLevel = .87
BearLevel = .13
```

Las etiquetas del gráfico y la tabla del artículo confirman el conjunto optimizado:

```text
2, 1, 36, 3, 53
15, 20, .87, .13, 4
```

El `.ELD` sigue siendo propietario y no permite leer el source en texto.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Es una estrategia completa? | **No.** Depende de una estrategia primaria. |
| ¿Puede implementarse en TSIS? | **Sí**, cuando exista una fuente histórica point-in-time de opciones. |
| ¿Está disponible con los datos actuales de TSIS? | **No consta una fuente raw de opciones put/call volume.** |
| ¿El artículo demuestra alpha incremental? | **No.** Cambia simultáneamente timing y tamaño de posición. |
| ¿La idea es plausible? | **Sí:** usar extremos contrarios de sentimiento para añadir a tendencias existentes. |
| ¿Está validada fuera de muestra? | **No.** |
| ¿Tiene controles de riesgo? | **No.** Hereda las salidas de la estrategia primaria. |

Clasificación TSIS:

```text
DEPENDENT_STRATEGY_COMPONENT
POSITION_SIZING_EVENT_CANDIDATE
OPTIONS_SENTIMENT_CONTEXT
PYRAMIDING_AND_LOT_LEDGER_REQUIRED
TWO_STAGE_OPTIMIZATION_RISK
SOURCE_DATA_NOT_CURRENTLY_GOVERNED
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La estrategia no predice por sí sola si SPY debe estar long o short.

Su lógica es:

```text
una estrategia primaria define la dirección
+
un oscilador de sentimiento decide cuándo incrementar tamaño
```

Por tanto, el objeto científico correcto no es:

```text
Put/Call VRAO Strategy
```

sino:

```text
Put/Call VRAO conditional position-scaling policy
```

La posición máxima es:

```text
100 shares iniciales
+
4 add-ons de 100
=
500 shares
```

Cada lote permanece abierto hasta que la estrategia primaria se revierte.

---

## 3. Reconstrucción matemática

## 3.1 Put/call volume ratio

\[
PCR_t = \frac{PutVolume_t}{CallVolume_t}
\]

Un valor elevado indica más actividad relativa en puts. La interpretación contraria de la revista es:

```text
PCR alto → miedo/extremo bajista → potencialmente bullish
PCR bajo → entusiasmo en calls → potencialmente bearish
```

## 3.2 Media del ratio

La revista describe una media simple:

\[
PCRAvg_t = MA_{L}(PCR_t)
\]

con `L = PCVolRatioAvgLength`.

## 3.3 Oscilador de rango

La reconstrucción natural del texto es:

\[
PCVRAO_t=
\frac{PCRAvg_t-\min(PCRAvg_{t-n+1:t})}
{\max(PCRAvg_{t-n+1:t})-\min(PCRAvg_{t-n+1:t})}
\]

con:

```text
n = OscLength
```

El resultado queda entre 0 y 1.

### Interpretación

```text
PCVRAO cerca de 1:
PCRAvg está cerca de su máximo reciente
sentimiento extremo en puts
zona contraria bullish

PCVRAO cerca de 0:
PCRAvg está cerca de su mínimo reciente
sentimiento extremo en calls
zona contraria bearish
```

## 3.4 División por rango cero

Si:

\[
\max(PCRAvg)=\min(PCRAvg)
\]

el oscilador no está definido.

El artículo no especifica:

```text
epsilon
valor por defecto
carry-forward
UNAVAILABLE
```

TSIS debe devolver `UNAVAILABLE`, no inventar 0 o 0.5 silenciosamente.

## 3.5 Salida de la zona extrema

Long add-on:

```text
PCVRAO cruza hacia abajo BullLevel
```

La tesis es que el miedo extremo ya ha empezado a normalizarse mientras la tendencia primaria sigue long.

Short add-on:

```text
PCVRAO cruza hacia arriba BearLevel
```

La tesis es que el extremo de calls empieza a revertirse mientras la tendencia primaria sigue short.

No se añade en la entrada a la zona extrema, sino en su **salida**.

---

## 4. Reglas temporales exactas

## 4.1 Precondición long

```text
MarketPosition > 0
adds_since_initial < MaxAdds
```

## 4.2 Señal long

La revista dice:

```text
If PCVRAO crosses under BullLevel on the last bar,
then buy next bar at market.
```

Y aclara que la entrada se retrasa una barra para reducir conflictos con las señales primarias.

La reconstrucción temporal más prudente es:

```text
cruce confirmado al cierre de t-1
comprobación de que sigue long al cierre de t
orden market para apertura t+1
```

Esto introduce una barra completa de retraso respecto del cruce.

Debe confirmarse con el source o con una trade list porque otra lectura posible sería usar la condición en t y ejecutar en t+1 sin una barra adicional.

## 4.3 Precondición short

```text
MarketPosition < 0
adds_since_initial < MaxAdds
```

## 4.4 Señal short

```text
PCVRAO cruza por encima de BearLevel en la barra anterior
sell short next bar at market
```

## 4.5 Salidas

No existen exits dentro del add-on.

```text
primary strategy reversal
→
close all existing lots
→
establish opposite initial entry
→
reset add counter
```

## 4.6 Trade counting

TradeStation considera cada pareja entry/exit como un trade.

Con pyramiding:

```text
una tendencia primaria
puede generar varios “trades” contables
```

Por eso:

```text
27 trades baseline
vs
86 trades con add-on
```

no significa 86 tendencias independientes.

## 4.7 Conflicto de órdenes

El delay intenta evitar que el add-on se ejecute el mismo día que una reversión primaria, pero no elimina todos los casos.

TSIS debe definir prioridad:

```text
1. procesar exit/reversal primario
2. actualizar direction state
3. invalidar add-on contrario
4. sólo entonces permitir nuevo add-on
```

---

## 5. Optimización publicada

## 5.1 Primera etapa — Estrategia primaria

Rangos:

| Input | Rango | Combinaciones |
|---|---|---:|
| MA1Type | 1–3 | 3 |
| MA1Length | 20–45 | 26 |
| MA2Type | 1–3 | 3 |
| MA2Length | 50–75 | 26 |

Total exhaustivo posible:

\[
3\times26\times3\times26=6,084
\]

La configuración elegida fue:

```text
SMA 36 / EMA 53
```

## 5.2 Segunda etapa — Add-on

Rangos:

| Input | Rango | Valores |
|---|---|---:|
| PCVolRatioAvgLength | 15–30 paso 1 | 16 |
| OscLength | 15–30 paso 1 | 16 |
| BullLevel | 0.87–0.93 paso 0.01 | 7 |
| BearLevel | 0.07–0.13 paso 0.01 | 7 |

Total:

\[
16\times16\times7\times7=12,544
\]

`MaxAdds` se mantuvo fijo en 4.

## 5.3 Tamaño de los espacios declarados

Los dos grids contienen conjuntamente:

\[
6,084+12,544=18,628
\]

configuraciones candidatas sobre el mismo periodo de siete años. Si las optimizaciones fueron exhaustivas, ese sería también el número de evaluaciones. El workspace no conserva el informe de optimización y, por tanto, el número efectivamente ejecutado no puede afirmarse.

El espacio declarado tampoco incluye decisiones previas como:

```text
familia de media elegida
definición del oscilador
salida de zona frente a entrada en zona
una barra de delay
MaxAdds = 4
trade size = 100
```

## 5.4 Dos etapas no crean validación

Optimizar primero la estrategia primaria y después el add-on sobre los mismos datos no produce un OOS.

Es una búsqueda secuencial:

```text
seleccionar base ganadora
→
seleccionar overlay ganador sobre esa base
```

## 5.5 Soluciones en fronteras

Los valores elegidos del add-on son:

```text
PCVolRatioAvgLength = 15, límite inferior
BullLevel = 0.87, límite inferior
BearLevel = 0.13, límite superior
```

Tres de cuatro inputs optimizados caen en fronteras.

Esto puede indicar:

```text
tendencia monotónica no explorada fuera del rango
```

o:

```text
sobreajuste a los límites elegidos
```

## 5.6 Inconsistencia de position limits

La página física 13 indica:

```text
Allow up to 50 entry orders
```

pero también afirma:

```text
MaxAdds was left at 4
largest position = 500 shares
```

Si sólo se admiten cuatro add-ons, bastaría permitir cinco entradas contando la inicial.

El valor 50 puede ser una configuración genérica o una reliquia de otras pruebas. Debe tratarse como una inconsistencia del artefacto y no copiarse automáticamente.

---

## 6. Resultados publicados

### 6.1 Configuración

```text
SPY Daily
7 años terminando 31/12/2014
100 shares por entrada inicial
100 shares por add-on
$0.01 por acción de comisión
hasta 4 add-ons
máximo 500 shares
casi 100% del tiempo en mercado
```

### 6.2 Comparación publicada

| Métrica | Mov Avg Machine | Mov Avg + VRAO |
|---|---:|---:|
| Net Profit | $17,198 | $58,839 |
| Gross Profit | $22,383 | $70,875 |
| Gross Loss | -$5,185 | -$12,036 |
| Profit Factor | 4.32 | 5.89 |
| Trades contables | 27 | 86 |
| Percent Profitable | 66.67% | 65.12% |
| Winning trades | 18 | 56 |
| Losing trades | 9 | 30 |
| Avg Trade | $636.96 | $684.17 |
| Avg Winner | $1,243.50 | $1,265.63 |
| Avg Loser | -$576.11 | -$401.20 |
| Ratio Avg Win / Avg Loss | 2.16 | 3.15 |
| Largest Winner | $3,715 | $4,290 |
| Largest Loser | -$1,467 | -$1,467 |
| Max shares | 100 | 500 |
| Total shares held | 2,700 | 8,600 |
| Account Size Required | $1,467 | $3,155 |
| RINA | 38.93 | 124.04 |
| Time in market | 98.16% | 98.16% |
| Intraday peak-to-valley DD | -$3,194 | -$14,777 |
| Trade-close DD | -$1,467 | -$3,155 |
| Max trade DD | -$1,500 | -$1,657 |

### 6.3 Posición media aproximada

La revista calcula:

\[
\frac{8,600}{27}=318.5
\]

shares por tendencia primaria.

Esto no es exactamente exposición media diaria, pero sí una aproximación al número medio total de shares asociados a cada entrada inicial.

### 6.4 Comparación escalada

Si el baseline de 100 shares escalara linealmente a 318.5 shares:

```text
Net Profit aproximado: $54,778.81
Intraday DD aproximado: $10,173.48
Trade-close DD aproximado: $4,672.67
```

El add-on obtuvo:

```text
Net Profit: $58,839
Intraday DD: $14,777
Trade-close DD: $3,155
```

Respecto del baseline escalado por tamaño medio:

```text
beneficio adicional aproximado: +7.4%
intraday drawdown adicional: +45.3%
```

Por tanto, la mejora depende de la definición de riesgo utilizada.

### 6.5 Net profit sobre intraday drawdown

Baseline:

\[
\frac{17,198}{3,194}=5.38
\]

Add-on:

\[
\frac{58,839}{14,777}=3.98
\]

La relación empeora.

### 6.6 Net profit sobre trade-close drawdown

Baseline:

\[
\frac{17,198}{1,467}=11.72
\]

Add-on:

\[
\frac{58,839}{3,155}=18.65
\]

La relación mejora.

Esto demuestra por qué no existe una única conclusión de “mejor riesgo ajustado” sin especificar la definición de drawdown.

### 6.7 Comparación con 300 y 500 shares constantes

Baseline lineal de 300 shares:

```text
Net Profit ≈ $51,594
```

Baseline lineal de 500 shares:

```text
Net Profit ≈ $85,990
```

La propia revista admite que 500 shares constantes habrían generado más beneficio que el add-on. Afirma, sin mostrar el informe completo, que el add-on supera a 300 shares constantes.

La comparación científicamente correcta debe incluir:

```text
100 constante
300 constante
318.5 constante
500 constante
VRAO variable
random variable con la misma trayectoria de tamaños
```

### 6.8 El número de trades no es comparable

En el add-on, cada lote adicional cuenta como un trade. `Avg Trade` y `% profitable` se calculan sobre unidades contables diferentes al baseline.

La unidad adecuada es:

```text
trend episode
```

no cada entry/exit pair.

---

## 7. ¿Dónde podría estar el edge?

La hipótesis funcional es:

> Dentro de una tendencia ya identificada, una reversión parcial desde un extremo de put/call sentiment marca un momento favorable para aumentar exposición en la misma dirección.

Posibles mecanismos:

```text
capitulación temporal
cobertura extrema de opciones
normalización del miedo tras un shock
reanudación de tendencia después de un pullback
```

Pero el resultado también puede explicarse por:

```text
mayor tamaño medio
base trend-following muy rentable in-sample
selección dentro de dos grids con 18,628 configuraciones candidatas
mercado alcista de SPY
adds concentrados en tendencias ganadoras ya visibles
```

El hecho de añadir después de que una posición ya vaya a favor puede crear una ventaja aparente incluso con fechas aleatorias, porque condiciona el tamaño a la supervivencia de la tendencia.

---

## 8. Problemas científicos y técnicos

## 8.1 No hay alpha aislado de sizing

La intervención cambia simultáneamente:

```text
momento de entrada
número de lotes
capital utilizado
path del drawdown
```

## 8.2 Optimización doble in-sample

grids de 6,084 configuraciones candidatas de base y 12,544 de overlay, sin OOS; el número de trials efectivamente ejecutados no está disponible.

## 8.3 Fuente point-in-time de opciones

El sistema necesita saber cuándo estaban disponibles los totales diarios de put y call volume.

Debe documentarse:

```text
exchange timestamp
vendor publication timestamp
revision timestamp
availability before next open
```

## 8.4 Call volume cero

Si `CallVolume = 0`, el ratio no está definido.

En SPY es improbable, pero en otros activos es común. No debe resolverse con un epsilon arbitrario sin registrar.

## 8.5 Denominador del oscilador cero

Un rango plano de `PCRAvg` produce división por cero.

## 8.6 Ventanas solapadas

`PCRAvgLength = 15` y `OscLength = 20` generan observaciones altamente dependientes. Los add-on signals no son muestras independientes.

## 8.7 Régimen estructural de opciones

El volumen de opciones y la participación retail/institucional cambian con el tiempo. Un threshold relativo reduce parte del problema, pero no garantiza estabilidad.

## 8.8 Delay ambiguo

“Crosses on the last bar” más “buy next bar” puede representar un retraso de dos aperturas desde el cruce. Debe reconciliarse con trades reales.

## 8.9 Conflictos entre componentes

La estrategia primaria y el add-on pueden emitir órdenes alrededor de la misma reversión.

## 8.10 Reset de add count

Debe quedar ligado a un `primary_episode_id`, no simplemente al signo de la posición.

## 8.11 Pyramiding y precio medio

Cada lot tiene:

```text
entry timestamp
entry price
quantity
MFE/MAE
```

No se debe colapsar todo en un average price sin lineage.

## 8.12 Sin exits de riesgo

La estrategia primaria reversa, pero no tiene stops. El portfolio está invertido 98.16% del tiempo y puede acumular hasta 500 shares.

## 8.13 Slippage no publicado explícitamente

La tabla informa comisiones, pero no presenta una hipótesis detallada de slippage para las órdenes market de apertura.

## 8.14 SPY como único caso

No hay portfolio de activos ni pruebas cruzadas publicadas.

## 8.15 Comparación con 300 shares no mostrada

La afirmación de superioridad frente a 300 shares constantes no incluye el reporte.

## 8.16 RINA no resuelve el cambio de exposición

Que el tiempo en mercado sea igual no significa que el capital en riesgo sea igual.

## 8.17 Escalar después de una señal ganadora puede introducir convexidad

El add-on puede aumentar exposición sólo después de que la tendencia ha sobrevivido suficiente tiempo. Eso debe compararse con reglas simples de pyramiding basadas en precio o tiempo.

## 8.18 Put/call ratio de un activo no equivale a sentimiento puro

El volumen incluye:

```text
hedging
spreads
market making
calendar trades
rolls
```

No todo put es bearish ni todo call bullish.

---

## 9. Cómo debe implementarse en TSIS

## 9.1 Contrato de dependencia

El add-on requiere:

```text
primary_strategy_id
primary_episode_id
primary_direction
primary_entry_timestamp
primary_position_quantity
```

Sin una posición primaria válida:

```text
NO_SIGNAL
```

## 9.2 Datos de opciones

Campos mínimos:

```text
symbol
session_date
put_volume
call_volume
source_timestamp
available_timestamp
revision_id
coverage_status
```

## 9.3 Estado del oscilador

```text
put_call_ratio
put_call_ratio_avg
range_min
range_max
pcvrao
bull_level
bear_level
cross_event
```

## 9.4 Lot ledger

```text
lot_id
episode_id
entry_type = PRIMARY | ADD_ON
entry_timestamp
quantity
entry_price
signal_id
exit_timestamp
exit_price
```

## 9.5 Add counter

```text
adds_used_by_episode
max_adds
```

Se reinicia sólo con un nuevo episodio primario.

## 9.6 Prioridad de órdenes

Orden recomendado en cada apertura:

```text
1. exits/reversal del primario
2. cierre de todos los lots anteriores
3. nueva entrada primaria
4. invalidación de add-ons pendientes contrarios
5. add-on elegible sólo si sigue existiendo episodio compatible
```

## 9.7 Comparación de tamaño normalizada

Cada experimento debe informar:

```text
average gross exposure
peak gross exposure
capital-time integral
dollar-volatility exposure
margin usage
```

## 9.8 Estado de indisponibilidad

```text
MISSING_OPTIONS_VOLUME
CALL_VOLUME_ZERO
OSCILLATOR_RANGE_ZERO
SOURCE_NOT_AVAILABLE_PIT
PRIMARY_POSITION_ABSENT
MAX_ADDS_REACHED
PRIMARY_REVERSAL_CONFLICT
```

---

## 10. Pseudocódigo de referencia

```python
@dataclass
class PrimaryEpisode:
    episode_id: str
    direction: int          # +1 long, -1 short
    initial_quantity: int
    adds_used: int = 0


def compute_pcvrao(put_volume, call_volume, avg_length, osc_length):
    if call_volume <= 0:
        return None, "CALL_VOLUME_ZERO"

    ratio = put_volume / call_volume
    ratio_avg = rolling_mean(ratio, avg_length)
    lo = rolling_min(ratio_avg, osc_length)
    hi = rolling_max(ratio_avg, osc_length)

    if hi == lo:
        return None, "OSCILLATOR_RANGE_ZERO"

    return (ratio_avg - lo) / (hi - lo), None


def on_daily_close(t, episode, pcvrao, bull_level, bear_level, max_adds):
    if episode is None or episode.adds_used >= max_adds:
        return None

    # La revista indica que se usa el cruce de la barra anterior.
    if episode.direction > 0 and crossed_under(pcvrao[t-1], bull_level):
        return schedule_market_add(
            direction="LONG",
            execute_session=t+1,
            episode_id=episode.episode_id,
        )

    if episode.direction < 0 and crossed_over(pcvrao[t-1], bear_level):
        return schedule_market_add(
            direction="SHORT",
            execute_session=t+1,
            episode_id=episode.episode_id,
        )


def on_session_open(open_event, primary_order, add_order, ledger):
    # Prioridad del primario.
    if primary_order is not None:
        process_primary_reversal_or_entry(primary_order, ledger)

    # Revalidar después de procesar la estrategia primaria.
    if add_order is not None:
        episode = current_primary_episode(ledger)
        if episode is None or episode.episode_id != add_order.episode_id:
            cancel(add_order, "PRIMARY_EPISODE_CHANGED")
            return

        fill = market_open_fill(open_event, add_order.direction)
        ledger.add_lot(
            episode_id=episode.episode_id,
            entry_type="ADD_ON",
            quantity=100,
            price=fill,
        )
        episode.adds_used += 1
```

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica de la estrategia primaria

Checksum:

```text
27 trades
Net Profit ≈ $17,198
PF ≈ 4.32
```

### Fase 2 — Réplica de add-ons

Checksum:

```text
86 entry/exit pairs
8,600 total shares held
Net Profit ≈ $58,839
```

### Fase 3 — Reconciliar delay

Probar las dos interpretaciones:

```text
cruce t → entry open t+1
cruce t-1 → entry open t+1
```

### Fase 4 — Agrupar por trend episode

Recalcular métricas por los 27 episodios primarios, no por 86 lots.

### Fase 5 — Size-matched baselines

Comparar:

```text
100 constante
300 constante
318.5 constante
500 constante
VRAO variable
```

### Fase 6 — Exposure-matched randomization

Mantener exactamente:

```text
número de adds
cantidades
episodios
```

pero aleatorizar la fecha del add dentro de cada episodio.

Si VRAO no supera ese placebo, no aporta timing.

### Fase 7 — Price-based pyramiding baseline

Comparar contra:

```text
add cada +1 ATR a favor
add después de n días
add en breakout de máximo
```

### Fase 8 — Verdadero OOS postpublicación

Congelar:

```text
SMA36 / EMA53
VRAO 15 / 20 / .87 / .13 / 4
```

Probar desde abril de 2015 en adelante sin recalibrar.

### Fase 9 — Walk-forward legítimo

Si se permite recalibración, debe ser anidada y sólo con datos anteriores.

### Fase 10 — Calidad de datos

Auditar:

```text
missing days
zero call volume
vendor revisions
options corporate action mapping
availability time
```

### Fase 11 — Regímenes

```text
bull/bear
low/high volatility
pre/post 2020
options-volume expansion eras
```

### Fase 12 — Risk exits

Introducir stops después de replicar y comparar por episodio.

### Fase 13 — Component contribution

Medir incrementalmente:

```text
base only
base + random adds
base + price adds
base + VRAO adds
```

---

## 12. Variantes posteriores a la réplica

### Variante A — Z-score del log put/call ratio

Reduce la dependencia del min/max y sus saturaciones.

### Variante B — Percentile rank

Usar percentil histórico robusto en vez de rango extremo.

### Variante C — Market-wide put/call context

Comparar ratio del activo, del índice y del mercado completo.

### Variante D — Add size adaptativo

Cantidad proporcional a riesgo, no 100 shares fijas.

### Variante E — Scale-out simétrico

Reducir lotes cuando el oscilador entra en el extremo contrario.

### Variante F — Max adds dependiente de volatilidad

Evitar acumular tamaño durante shocks.

### Variante G — No add durante primary reversal proximity

Filtrar cuando la distancia entre medias es pequeña.

### Variante H — Add-on como feature, no como regla

Usar PCVRAO dentro del Market State y dejar que un modelo estime el incremento de expectativa.

---

## 13. Encaje en Market State y Event State

### Market State

```text
primary_trend_direction
primary_trend_strength
put_call_ratio
put_call_ratio_avg
pcvrao
pcvrao_percentile
current_quantity
adds_used
margin_usage
```

### Event State — Sentiment extreme exit

```text
event_type:
put_call_sentiment_extreme_exit

side:
bull_extreme_exit | bear_extreme_exit

decision_timestamp:
options_data_available_timestamp
```

### Event State — Add-on eligibility

```text
event_type:
position_scale_up_eligible

primary_episode_id
current_direction
current_quantity
remaining_add_capacity
```

### Outcomes

```text
incremental_lot_pnl
incremental_lot_MFE
incremental_lot_MAE
episode_total_pnl
pnl_vs_random_add
pnl_vs_constant_size
marginal_drawdown
```

### Distinción clave

```text
información:
extremo y reversión de sentiment

acción:
aumentar tamaño de una tendencia existente
```

No debe asumirse que una señal informativa obliga a pyramiding.

---

## 14. Transferencia a small caps y otros mercados

### Small caps

No es trasladable directamente.

Muchas small caps tienen:

```text
opciones inexistentes
volumen casi cero
series discontinuas
strikes muy concentrados
actividad dominada por market makers
```

El estado correcto sería:

```text
OPTIONS_CONTEXT_UNAVAILABLE
```

no imputar el ratio de SPY.

Para small caps con opciones líquidas podría estudiarse como contexto, pero no como regla universal.

### ETFs líquidos

Es el entorno más natural para la idea.

### Índices

Puede estudiarse con ratios de opciones de índice, pero el activo y la serie de sentimiento deben alinearse point-in-time.

### Futuros

La transferencia requeriría opciones sobre futuros o un índice de sentimiento externo; no es la misma estrategia.

---

## 15. Veredicto de Put/Call VRAO Add-on

El valor principal de esta estrategia para TSIS no es afirmar que el put/call ratio produce alpha. Es enseñar que una estrategia puede componerse de módulos independientes:

```text
primary signal
+
position scaling policy
+
exit policy
```

Eso encaja muy bien con una arquitectura de agentes y artefactos separados, siempre que el backtester conserve la dependencia y el lineage.

El resultado publicado no demuestra alpha incremental porque:

```text
18,628 configuraciones candidatas en los grids in-sample
cambio de tamaño y timing simultáneo
comparación por trade contable no homogénea
sin risk exits
sin OOS
```

Decisión:

```text
IMPLEMENTAR:
sí, como componente dependiente cuando existan datos de opciones

ACEPTAR EDGE:
no

USAR EN SMALL CAPS:
no por defecto

LIVE:
no
```

Gate propuesto:

```text
VRAO-DEPENDENT-STRATEGY-COMPOSITION-SIZE-NORMALIZATION-AND-POSTPUBLICATION-OOS-GATE
```

---

# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. Combinar indicadores crea un state machine

No basta con escribir:

```text
BB_condition AND CCI_condition
```

Las condiciones ocurren en momentos distintos y persisten.

## 2. Una intersección de filtros reduce exposición

Menor drawdown puede surgir de operar menos, no de tener mejor información.

## 3. La optimización puede quedar escondida en el workspace

El PDF dice “partially found by optimization”. El `.tsw` revela 8,000 configuraciones almacenadas y un lattice potencial de 1.8 millones.

TSIS debe conservar el search log como evidencia primaria.

## 4. El ganador publicado no es una hipótesis única

Una configuración en el puesto 2/8,000 necesita corrección de selección antes de interpretar el PF.

## 5. Pivots tienen dos timestamps

```text
fecha del extremo
fecha de confirmación
```

Confundirlos crea look-ahead.

## 6. Pending orders son artefactos persistentes

Una señal válida cinco días debe existir como objeto gobernado con TTL y cancel reason.

## 7. “24-hour market” no elimina riesgo intersesión

Las pausas, gaps y fines de semana siguen existiendo.

## 8. Add-on strategy no es primary strategy

Debe representarse como política dependiente y no poder operar sola.

## 9. Comparar estrategias con distinto tamaño exige normalización

Net profit absoluto no demuestra mejor timing.

## 10. TradeStation cuenta lotes como trades

Con pyramiding, la unidad científica debe ser el episodio de tendencia.

## 11. El drawdown depende de la definición

VRAO empeora la relación net profit / intraday DD y mejora net profit / closed-trade DD.

## 12. Inputs en frontera requieren ampliar o congelar

No debe elegirse automáticamente ampliar rangos y volver a optimizar. Primero se hace OOS con el punto publicado.

## 13. Sentiment debe tener availability timestamp

Los datos diarios de opciones sólo son legales para una decisión cuando el total de la sesión ha sido publicado.

## 14. Component ablation debe conservar el mismo presupuesto

Comparar combo contra componentes requiere igualar:

```text
trade count
exposure
capital
costes
```

## 15. Fibonacci Retracement Channel

La página física 3 promociona indicadores de canales basados en regresión lineal y niveles Fibonacci.

Clasificación:

```text
RESEARCH_NOTE
INDICATOR_CONCEPT
NO_STRATEGY_RULES
NO_BACKTEST
NO_EDGE_EVIDENCE
```

Posible encaje futuro:

```text
trend_channel_state
regression_slope
channel_break
normalized_channel_position
```

## 16. Options Volume and Open Interest Indicators

La página física 9 vuelve a presentar una suite para detectar actividad anormal en opciones.

Clasificación:

```text
POTENTIAL_OPTIONS_ACTIVITY_CONTEXT
NO_PUBLISHED_STRATEGY
NO_EDGE_EVIDENCE
```

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — CCI/Bollinger como gate de state machine

Aunque TSIS todavía no disponga de ES físico, la lógica puede modelarse sobre equities para validar:

```text
persistent setup
pivot confirmation
pending signal TTL
stop entry
one-bar exit
```

### Prioridad B — VRAO como gate de composición

Debe esperar a una fuente gobernada de opciones, pero su contrato puede servir para diseñar:

```text
primary strategy dependency
add-on policy
lot ledger
order priority
size normalization
```

## 2. Estado respecto de los datos actuales de TSIS

### CCI/Bollinger en equities

Posible con:

```text
004_master_daily_table para señales
013_ohlcv_1m_quote_guarded para ejecución
```

Siempre separando adjusted signal view y raw execution view.

### CCI/Bollinger en ES

No disponible hasta incorporar:

```text
physical futures contracts
roll calendar
intraday bars/trades
session templates
```

### VRAO

No disponible con la enumeración actual de RAW, porque no consta:

```text
options volume
options open interest
options reference mapping
```

## 3. Artefactos futuros derivados

Cuando se abran los gates:

```text
SCC_2015_04_CCI_BOLLINGER_REPLICATION_CONTRACT.md
SCC_2015_04_VRAO_STRATEGY_COMPOSITION_CONTRACT.md
```

No deben crearse ahora como resúmenes duplicados.

## 4. Material adicional necesario para réplica exacta

El ZIP es suficiente para cerrar la auditoría documental.

Al abrir la implementación sería útil exportar:

```text
EasyLanguage source como texto
trade list completa
Strategy Properties
MaxBarsBack
session template
optimization report completo
optimization method y objective
LIBB settings
put/call source metadata
order priority settings
pyramiding settings
```

Sólo debe solicitarse cuando se abra el gate correspondiente.

---

# Apéndice A — Integridad del paquete

## Archivos relevantes

```text
SCC Issue 4 Apr 2015.pdf
2015-04/CCI Bollinger Bands Combo/TSL CCI BOLLINGER BANDS COMBO.ELD
2015-04/CCI Bollinger Bands Combo/TSL CCI Bollinger Bands Combo.tsw
2015-04/Put Call VRAO Add On/TSL PUT CALL VRAO ADD ON.ELD
2015-04/Put Call VRAO Add On/TSL.Put_Call VRAO Add-on.tsw
```

El PDF incluido dentro del ZIP es bit a bit idéntico al PDF cargado por separado.

## Tamaños

```text
PDF: 5,137,605 bytes
ZIP: 9,868,345 bytes
CCI/Bollinger .ELD: 17,541 bytes
CCI/Bollinger .tsw: 16,265,728 bytes
VRAO .ELD: 16,261 bytes
VRAO .tsw: 24,064 bytes
```

## SHA-256

```text
PDF:
31f7fe39562ecfe89f878666fa110d8cf55d9d7437d376a95a81c0301848bc14

ZIP:
be0ab26694a1273d5929a02432c11206541c024c135e241633b415290679d421

CCI/Bollinger .ELD:
f973274ab046b3a55429b98fa63719c975332ce4771af4dcae56c2bba288990b

CCI/Bollinger .tsw:
68edf30e053cb33b4edd5fdb351d1de8a86553b2bc12a1429d2c2a9daee8d62b

VRAO .ELD:
055491924e77a81c3a546876390f30bf0257b21285738126a359d00677b79026

VRAO .tsw:
03ed22d8da4d9e770eb579df2b383fb0a0be66acafa75810f709725c4f4df190
```

## Metadata PDF

```text
Title: Strategy Concepts Club, Issue 4, April 2015
Author: TradeStation Labs
Pages: 15
CreationDate: 7 de abril de 2015, 21:00:37 UTC
ModificationDate: 12 de octubre de 2015, 18:13:18 UTC
Creator: Adobe InDesign CC 2014
Producer: Adobe PDF Library 11.0
PDF version: 1.7
```

## Evidencia binaria del workspace CCI

```text
OLE stream OptimizationData:
15,841,143 bytes

trials distintos reconstruidos:
8,000

full lattice implícito:
1,800,000

configuración publicada:
rank 2/8,000 por net profit
```

## Limitación del paquete

```text
.tsw:
workspace OLE binario con metadatos, inputs y optimización parcialmente recuperables

.ELD:
contenedor propietario no legible como source EasyLanguage
en este entorno
```

No contiene exportaciones de texto directamente legibles de:

```text
source code
trade lists
order logs
session properties
optimization objective
```

---

# Cierre del issue

El Issue 4 debe conservarse en TSIS como dos lecciones institucionales:

```text
CCI Bollinger Bands Combo:
una estrategia de indicadores combinados es una state machine temporal,
y su búsqueda de parámetros forma parte de la evidencia científica

Put/Call VRAO Add-on:
una señal de sentimiento aplicada al tamaño no puede evaluarse
sin separar timing, exposición, lotes y estrategia primaria
```

Decisión final:

```text
ARCHIVE_STATUS:
AUDITED_COMPLETE

CCI_BOLLINGER_STATUS:
PERSISTENT_STATE_AND_INTRABAR_REPLICATION_CANDIDATE

VRAO_STATUS:
DEPENDENT_STRATEGY_COMPOSITION_CANDIDATE

EDGE_ACCEPTED:
NO

ADDITIONAL_SOURCE_NEEDED_NOW:
NO

NEXT_ACTION:
ARCHIVE AND CONTINUE WITH ISSUE 5
```
