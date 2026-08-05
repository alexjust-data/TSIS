# Auditoría completa — TradeStation Strategy Concepts Club, Issue 14 (febrero de 2016)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. Breakout Score Strategy
2. Trend Capture Strategy
3. Strategy Concepts Club Utility Kit 1 — reimpresión
4. ideas secundarias de investigación y backtesting
5. reconstrucción matemática, temporal y de máquinas de estado
6. auditoría de los resultados publicados
7. inspección forense de los archivos .ELD, .tsw y .pmx
8. contratos de implementación y réplica para TSIS
9. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia ni por el Utility Kit.

### Incidencia documental de la entrega

El archivo cargado por separado con nombre:

```text
SCC Issue 14 Feb 2016.pdf…Zone.Identifier
```

no era el PDF de la revista. Era un stream NTFS `Zone.Identifier` de **25 bytes**.

El ZIP sí contenía todo el material necesario:

```text
2016-02/SCC Issue 14 Feb 2016.pdf
```

junto con los `.ELD`, los workspaces `.tsw`, el proyecto de Portfolio Maestro `.pmx` y el Utility Kit. No ha sido necesario solicitar otra carga.

### Fuentes examinadas

- PDF correcto de 21 páginas extraído de `2016-02.zip`.
- Archivo de apoyo completo `2016-02.zip`.
- PDF auxiliar `Strategy Concepts Club Inventory.pdf`.
- Dos contenedores propietarios correspondientes a las estrategias nuevas:
  - `TSL BREAKOUT SCORE.ELD`;
  - `TSL TREND CAPTURE.ELD`.
- Dos workspaces OLE/Compound Document:
  - `TSL.Breakout Score.tsw`;
  - `TSL Trend Capture.tsw`.
- Proyecto de Portfolio Maestro:
  - `TSL Trend Capture.pmx`.
- Reimpresión del Utility Kit:
  - `UTILITY KIT 1.ELD`.
- Las 21 páginas renderizadas, incluidas:
  - definición del score, reglas, informe y curva de Breakout Score;
  - fórmula de position sizing, universo, informe de Portfolio Maestro, equity y P/L por símbolo de Trend Capture;
  - documentación del Utility Kit 1.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF, los workspaces,
el proyecto .pmx y los contenedores .ELD

AUDIT:
inferencia técnica, crítica científica
y propuesta de implementación en TSIS
```

Cuando una decisión no queda resuelta, se registra como ambigüedad. No se completa silenciosamente.

No se ha utilizado investigación web externa para rellenar reglas o resultados.

---

## 0.1 Inventario forense

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `2016-02.zip` | 8,583,456 bytes | `1de95a2ee8ac8b740c722f6c57a6a73f47abbe0e287a3f2acc730bac017bae99` |
| `SCC Issue 14 Feb 2016.pdf` | 8,125,692 bytes | `173624472a94d6e996153d91bcedcc8c631310ff5b710b44afa8064f6b78b5dd` |
| `Strategy Concepts Club Inventory.pdf` | 27,024 bytes | `a0742adf457de78859560e0fe852a1e7cd7ffd7892f5bd2a91c7810af37acf07` |
| `TSL BREAKOUT SCORE.ELD` | 14,385 bytes | `bf6afd4f994f6f49c90ba715a4ca5375fcacd539207bc838257808f2052ec5ee` |
| `TSL.Breakout Score.tsw` | 24,064 bytes | `b0a75bc2b6b67a8952b87fdffd721cf1f46a5fa8060b97cf4909027f1ecee6bd` |
| `TSL TREND CAPTURE.ELD` | 20,625 bytes | `8514345dd2af309491b46418ca72a2fda231f22df3c19371fb7fa8287027063b` |
| `TSL Trend Capture.tsw` | 81,920 bytes | `f2621aec0b121f72e52653429de10d6f00d7d19f6d3ca26aa996b461167876a2` |
| `TSL Trend Capture.pmx` | 263,358 bytes | `ed74480ea120fd9a4efe79b2a4d59e9b2bbee437b51f247ebb270425aabe387d` |
| `UTILITY KIT 1.ELD` | 25,643 bytes | `f3b08dbff8bfbd5802ad8053b9126b6572f9a881936a0e482b2ae2a09f50a7a1` |

Los pequeños archivos `Zone.Identifier` internos son metadatos del sistema operativo y no forman parte del contenido científico.

> Nota: el valor exacto de hash del ZIP no se utiliza como autoridad para ninguna regla. La trazabilidad sustantiva se basa en los hashes de los artefactos internos.

---

## 0.2 Errores editoriales detectados

### Número de issue incorrecto en Contents

La portada identifica correctamente:

```text
Issue 14, February 2016
```

pero la página de contenidos imprime:

```text
Issue 13
```

Es un error editorial de copia.

### Caption incorrecto en Trend Capture

En la primera figura del artículo Trend Capture aparece el caption:

```text
SPY 130-minute bars with TSL:Regression Angles strategy and indicator
```

pero el gráfico es:

```text
SPY Daily
TSL:Trend Capture
EMA 50 / EMA 120
price channel
```

El texto del caption fue reutilizado erróneamente del Issue 13.

Estos errores no alteran las reglas, pero se registran porque demuestran que los captions y labels editoriales no deben consumirse automáticamente como contrato.

---

## 0.3 Limitación de los `.ELD`

Los `.ELD` son contenedores propietarios de TradeStation y no exponen el EasyLanguage como texto legible en este entorno.

Por tanto:

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la semántica exacta de los channels;
no puede certificarse la prioridad de órdenes;
no puede resolverse sólo por lectura:
    - High/Low vs Close para contabilizar breakouts;
    - inclusión de la barra actual;
    - barras que rompen ambos lados del canal;
    - redondeo exacto del sizing ATR;
    - orden entre señales simultáneas del portfolio;
    - semántica exacta de Lowest/Highest.
```

---

## 0.4 Workspaces OLE

### Breakout Score

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 15,251 bytes |
| `Embedding 1/DrawingObjects` | 1,635 bytes |
| `Embedding 1/ChartSetting` | 666 bytes |
| `Embedding 1/AnalisysTechniques` | 299 bytes |
| `Embedding 1/optdatafile` | **0 bytes** |

### Trend Capture

El workspace contiene dos embeddings:

```text
Embedding 1:
RadarScreen / lista de símbolos

Embedding 2:
chart diario de FXE con estrategia e indicador
```

Streams relevantes:

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 3,999 bytes |
| `Embedding 1/TSEngine_0/AnalysisEngine` | 12,516 bytes |
| `Embedding 2/Contents` | 13,700 bytes |
| `Embedding 2/AnalisysTechniques` | 295 bytes |
| `Embedding 2/optdatafile` | **0 bytes** |

Conclusión:

```text
ningún workspace conserva el grid de optimización;
no hay ranking de configuraciones;
no hay candidate count;
no hay función objetivo;
no hay seed;
no hay historial de generaciones.
```

---

## 0.5 Proyecto Portfolio Maestro `.pmx`

El `.pmx` es un `System.Data.DataSet` serializado mediante tecnología .NET/BinaryFormatter.

La inspección física confirma:

```text
nombre:
TSL:Trend Capture

money management:
Fixed Fractional with ATR Risk

valores finales:
Percent Risk = 0.01
ATR Multiplier = 2
ATR Lookback = 20
Maximum Contracts = 5000

inputs de estrategia:
50 / 120 / 80 / 40 / 2 / 100000 / 0.01 / 2 / 20
```

También aparecen valores predeterminados internos del módulo de money management:

```text
0.05 / 1 / 10 / 5000
```

y, separadamente, los valores seleccionados para el proyecto:

```text
0.01 / 2 / 20 / 5000
```

El `.pmx` confirma la configuración final del proyecto, pero **no conserva evidencia suficiente de la optimización genética**:

```text
population size:
no recuperado

número de generaciones:
no recuperado

criterio de fitness:
no recuperado

seed:
no recuperado

candidatos visitados:
no recuperado

ranking:
no recuperado
```

---

## 0.6 Resultado ejecutivo

| ID | Estrategia | Tipo real | Resultado publicado | Hallazgo crítico | Decisión |
|---|---|---|---|---|---|
| 028 | Breakout Score | Acumulación rolling de eventos de breakout sobre un canal, con neutral zone y salidas por score | SPY diario; 44 trades; $13,364.30; PF 2.99 | una operación short aporta 88.73% del net short; sólo 44 trades; mismatch gráfico `15/-9` frente al contrato `14/-8`; no hay stop | candidato de réplica, no edge aceptado |
| 029 | Trend Capture | EMA regime + price-channel breakout + channel exit + sizing ATR sobre un portfolio de 18 ETFs/ETNs | $460,492.70 total return; 290 trades; PF 1.42; CAR 18.82%; drawdown semanal ~41% | el “1% risk” no es pérdida máxima porque no existe stop 2 ATR; universe y genetic search introducen muchos grados de libertad; resultado incluye $20,804.84 open P/L | candidato de portfolio research, no estrategia validada |
| UK-001-R | Utility Kit 1 | Reimpresión de herramientas de engine | no aplica | texto idéntico al Issue 13, binario `.ELD` diferente | no se asigna nuevo edge ni estrategia |

Estado:

```text
ISSUE_14_STATUS:
DOCUMENTALLY_CLOSED

NEW_STRATEGIES:
2

UTILITY_KIT_REPRINTS:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

---

# Parte I — Estrategia 028: Breakout Score

## 1) Identificación

- **ID:** `SCC-2016-02-STRAT-028`
- **Artículo:** *Breakout Score*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas:** 4–9
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** position trading
- **Activo:** SPY
- **Intervalo:** diario
- **Historia:** diez años terminando el 31 de diciembre de 2015
- **Tamaño:** $15,000 por operación
- **Redondeo:** hacia abajo al múltiplo de 10 acciones
- **Comisión:** $0.01 por acción
- **Slippage publicado:** cero/no indicado como coste positivo
- **Inputs finales:** `8 / 17 / 5 / -5 / 14 / -8`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí.** |
| ¿Puede replicarse exactamente? | **No todavía.** Hay que reconciliar la definición física de breakout. |
| ¿Es un price-channel breakout convencional? | **No.** El breakout individual sólo incrementa o reduce un score. |
| ¿Es always-in? | **No.** Usa neutral zone y dos tipos de salida. |
| ¿El resultado tiene una muestra suficiente? | **No.** Sólo 44 operaciones. |
| ¿El lado short es robusto? | **No.** Depende casi totalmente de 2008. |
| ¿Tiene stop de emergencia? | **No.** |
| ¿Los inputs fueron optimizados? | **Sí.** El artículo lo afirma, pero no conserva el proceso. |
| ¿Merece implementación? | **Sí**, como evento agregado de market structure. |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
ROLLING_BREAKOUT_EVENT_SCORE
PRICE_CHANNEL_TREND
NEUTRAL_ZONE_STATE_MACHINE
SMALL_SAMPLE
NO_EMERGENCY_STOP
NOT_SCIENTIFICALLY_VALIDATED
```

---

## 2) Evidencia contractual del workspace

El workspace activo confirma:

```text
SPY Daily [ARCX]
TSL:Breakout Score Strategy
TSL:Breakout Score Indicator

ChannelLength = 8
BarSpan = 17
LongLevel = 5
ShortLevel = -5
LXTarget = 14
SXTarget = -8
```

El stream `optdatafile` está vacío.

### Contradicción visual

La figura 3 —captura del diálogo de propiedades— muestra:

```text
8 / 17 / 5 / -5 / 15 / -9
```

pero:

```text
las figuras 1 y 2 muestran 8/17/5/-5/14/-8;
las tablas muestran 8/17/5/-5/14/-8;
el workspace físico confirma 8/17/5/-5/14/-8.
```

Conclusión:

```text
FIGURE_3_CONFIGURATION:
STALE_OR_ILLUSTRATIVE

PUBLISHED_TEST_CONTRACT:
8 / 17 / 5 / -5 / 14 / -8
```

---

## 3) Qué estrategia es realmente

La estrategia no compra cada nuevo máximo ni vende cada nuevo mínimo.

Construye dos niveles:

```text
evento elemental:
breakout de un canal de 8 barras

estado acumulado:
suma neta de esos eventos durante 17 barras
```

La pregunta funcional es:

> ¿Cuántos breakouts alcistas netos frente a bajistas se han producido recientemente?

Después usa el score para:

```text
entrar sólo cuando existe suficiente acumulación direccional;
salir si la tendencia se agota y vuelve a 0;
salir si el score alcanza un extremo favorable.
```

---

## 4) Reconstrucción del canal

Para evitar auto-inclusión, la reconstrucción causal más probable es:

$$
Top_t =
\max(High_{t-8},\dots,High_{t-1})
$$

$$
Bottom_t =
\min(Low_{t-8},\dots,Low_{t-1})
$$

No puede utilizarse:

$$
High_t > Highest(High,8)_t
$$

si la función incluye `High_t`, porque sería imposible.

### Ambigüedad no resuelta

El artículo no especifica si un breakout se contabiliza con:

```text
High_t > Top_t
Low_t < Bottom_t

o

Close_t > Top_t
Close_t < Bottom_t
```

La primera interpretación es más coherente con la expresión “penetration” y con un price channel clásico, pero debe reconciliarse.

Estado:

```text
BREAKOUT_PRICE_FIELD_UNRESOLVED
```

---

## 5) Evento elemental

Reconstrucción:

$$
Up_t =
1\{High_t > Top_t\}
$$

$$
Down_t =
1\{Low_t < Bottom_t\}
$$

$$
EventScore_t =
Up_t - Down_t
$$

Valores posibles:

```text
+1:
sólo breakout superior

-1:
sólo breakout inferior

0:
ningún breakout
o ambos lados en la misma barra
```

### Barra que rompe ambos lados

Una barra de rango amplio puede romper el canal superior e inferior.

La revista no documenta si:

```text
se anulan:
+1 + (-1) = 0

se prioriza el primero intrabar:
requiere path

se contabilizan dos eventos separados:
requiere otra representación
```

La suma neta es la reconstrucción más natural, no una certeza certificada.

---

## 6) Breakout Score rolling

Con `BarSpan=17`:

$$
Score_t =
\sum_{i=0}^{16}
EventScore_{t-i}
$$

Rango teórico:

$$
-17 \le Score_t \le 17
$$

El score no es acumulativo desde el origen.

Es una ventana rolling: al entrar una barra nueva, sale la observación de hace 17 barras.

Por tanto, puede cambiar aunque la barra actual no produzca breakout:

```text
si un evento antiguo abandona la ventana.
```

Ésta es una propiedad importante para Event State.

---

## 7) Entradas

### Long

$$
Score_{t-1} \le 5
\quad\land\quad
Score_t > 5
$$

Ejecución:

```text
market at open t+1
```

### Short

$$
Score_{t-1} \ge -5
\quad\land\quad
Score_t < -5
$$

Ejecución:

```text
market at open t+1
```

### Neutral zone

```text
-5 ≤ Score ≤ 5
```

No se generan nuevas posiciones en su interior.

---

## 8) Salidas

### Long

Salir si:

```text
Score alcanza +14
o
Score vuelve a 0
```

### Short

Salir si:

```text
Score alcanza -8
o
Score vuelve a 0
```

Reconstrucción:

$$
LongExit_t =
(Score_t \ge 14)
\lor
crossDownOrTouchZero_t
$$

$$
ShortExit_t =
(Score_t \le -8)
\lor
crossUpOrTouchZero_t
$$

### Ambigüedad de “reaches”

Debe fijarse:

```text
igualdad;
cruce;
mayor/menor;
primer toque;
next-open execution.
```

Las etiquetas de las figuras sugieren una salida por evento en la barra y fill posterior.

---

## 9) Asimetría de targets

Entradas:

```text
+5 / -5
```

Targets:

```text
+14 / -8
```

Distancia desde el entry threshold:

```text
long:
9 puntos de score

short:
3 puntos de score
```

La estrategia exige mucha más persistencia antes del target long que del target short.

Esto puede reflejar:

```text
comportamiento distinto de mercados alcistas y bajistas;
optimización in-sample;
necesidad de salir rápido en shocks bajistas;
asimetría de la distribución.
```

Sin grid ni OOS, no se puede distinguir.

---

## 10) Falta de reentrada

Después de una salida a 0 o target:

```text
la estrategia no reentra mientras el score
no vuelva a cruzar el threshold desde el otro lado.
```

Ejemplo:

```text
long sale en +14;
score permanece entre +10 y +14;
la tendencia continúa;
no existe nuevo cross de +5;
no hay reentrada.
```

Esto reduce actividad, pero puede perder tendencias prolongadas.

---

## 11) Sizing

$$
Qty_t =
10
\left\lfloor
\frac{15{,}000 / ReferencePrice_t}{10}
\right\rfloor
$$

El artículo indica:

```text
máximo = 200 acciones
mínimo = 70
total acumulado = 4,630
trades = 44
```

Cantidad media:

$$
4,630 / 44
=
105.23
$$

El sizing no cambia las señales, pero sí pondera de forma distinta las épocas históricas.

### Precio de referencia no certificado

Puede ser:

```text
close de señal;
next open;
precio de fill;
propiedad interna de TradeStation.
```

Debe reconciliarse.

---

## 12) Resultados publicados

### Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $13,364.30 |
| Beneficio bruto | $20,089.30 |
| Pérdida bruta | -$6,725.00 |
| Profit Factor | 2.99 |
| Operaciones | 44 |
| Ganadoras | 25 |
| Perdedoras | 19 |
| Percent Profitable | 56.82% |
| Expectativa media | $303.73 |
| Ganancia media | $803.57 |
| Pérdida media | -$353.95 |
| Ratio ganancia/pérdida | 2.27 |
| Mayor ganancia | $4,746.00 |
| Mayor pérdida | -$827.00 |
| Máx. ganadoras consecutivas | 8 |
| Máx. perdedoras consecutivas | 4 |
| Barras medias ganadoras | 41.76 |
| Barras medias perdedoras | 15.95 |
| Máximo tamaño | 200 acciones |
| Acciones acumuladas | 4,630 |
| Account Size Required | $1,627.30 |
| Trading Period | 9 años, 9 meses y 15 días |
| Percent of Time in Market | 52.92% |

### Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $8,015.20 | $5,349.10 |
| Beneficio bruto | $11,333.00 | $8,756.30 |
| Pérdida bruta | -$3,317.80 | -$3,407.20 |
| Profit Factor | 3.42 | 2.57 |
| Operaciones | 27 | 17 |
| Percent Profitable | 62.96% | 47.06% |
| Expectativa media | $296.86 | $314.65 |
| Ganancia media | $666.65 | $1,094.54 |
| Pérdida media | -$331.78 | -$378.58 |
| Ratio ganancia/pérdida | 2.01 | 2.89 |
| Mayor ganancia | $1,976.00 | $4,746.00 |
| Mayor pérdida | -$818.10 | -$827.00 |
| Barras medias ganadoras | 55.88 | 11.75 |
| Barras medias perdedoras | 17.00 | 14.78 |

---

## 13) Dependencia del outlier short

La mayor operación short:

```text
entrada:
19/09/2008

salida:
28/10/2008

beneficio:
$4,746
```

Representa:

$$
4,746 / 13,364.30
\approx 35.51\%
$$

del neto total.

Y:

$$
4,746 / 5,349.10
\approx 88.73\%
$$

del neto short.

Sin esa operación:

$$
ShortNet =
5,349.10 - 4,746
=
603.10
$$

Profit Factor short aproximado:

$$
(8,756.30 - 4,746) / 3,407.20
\approx 1.18
$$

El sistema total seguiría positivo:

$$
13,364.30 - 4,746
=
8,618.30
$$

y su PF aproximado sería:

$$
(20,089.30 - 4,746) / 6,725
\approx 2.28
$$

Conclusión:

```text
TOTAL_STRATEGY:
no depende enteramente del outlier

SHORT_BRANCH:
casi toda su aparente calidad depende de él
```

---

## 14) Curva de capital

La curva muestra:

```text
inicio irregular;
salto extraordinario alrededor del trade 11;
tramos escalonados;
drawdowns moderados;
meseta prolongada;
recuperación final.
```

El salto del trade 11 es compatible con el short de 2008.

No debe describirse como una curva uniformemente lineal.

---

## 15) Auditoría científica

### 15.1 Sólo 44 trades

Es el principal problema estadístico.

### 15.2 Sólo 17 shorts

El lado short no admite conclusiones robustas.

### 15.3 Outlier 2008

Domina la rama short.

### 15.4 Un único activo

Sólo SPY.

### 15.5 Parámetros optimizados

No hay ledger de optimización.

### 15.6 Sin OOS

No hay holdout.

### 15.7 Sin stop

Una salida basada sólo en score puede reaccionar tarde ante gaps o shocks.

### 15.8 Corporate actions y dividendos

SPY requiere vistas coherentes; el short debe incluir dividendos pagados.

### 15.9 Constant notional

Mezcla señal y exposición temporal.

### 15.10 Asimetría de target

Puede estar seleccionada.

### 15.11 Definición de breakout no certificada

High/Low frente a Close.

### 15.12 Barras dual-break

No hay contrato.

### 15.13 Screenshot inconsistente

Refuerza la necesidad de gobernar inputs mediante artefactos, no figuras.

---

## 16) Contrato TSIS

### Datos

```text
SPY daily OHLCV
corporate actions
dividends
session calendar
borrow assumptions
next-open execution
```

### Estado

```text
channel_top_prior_8
channel_bottom_prior_8
up_break
down_break
event_score
score_17
score_prev
long_threshold
short_threshold
long_target
short_target
position
exit_reason
quantity
```

### Eventos

```text
PRICE_CHANNEL_UP_BREAK
PRICE_CHANNEL_DOWN_BREAK
DUAL_CHANNEL_BREAK
BREAKOUT_SCORE_LONG_CROSS
BREAKOUT_SCORE_SHORT_CROSS
BREAKOUT_SCORE_ZERO_EXIT
BREAKOUT_SCORE_TARGET_EXIT
```

### Estados de indisponibilidad

```text
INSUFFICIENT_CHANNEL_HISTORY
INSUFFICIENT_SCORE_HISTORY
BREAKOUT_PRICE_FIELD_UNRESOLVED
DUAL_BREAK_POLICY_UNRESOLVED
MISSING_NEXT_OPEN
CORPORATE_ACTION_UNRESOLVED
```

---

## 17) Pseudocódigo funcional

```python
channel_top = max(high[t - 8:t])
channel_bottom = min(low[t - 8:t])

up_break = high[t] > channel_top
down_break = low[t] < channel_bottom

event_score = int(up_break) - int(down_break)
score = rolling_sum(event_score, 17)

if flat:
    if score_prev <= 5 and score > 5:
        schedule_long(next_open)
    elif score_prev >= -5 and score < -5:
        schedule_short(next_open)

elif long:
    if score >= 14:
        schedule_exit(next_open, reason="LX_TARGET")
    elif score == 0:
        schedule_exit(next_open, reason="LX_ZERO")

elif short:
    if score <= -8:
        schedule_exit(next_open, reason="SX_TARGET")
    elif score == 0:
        schedule_exit(next_open, reason="SX_ZERO")
```

Es una reconstrucción. Debe reconciliarse con trades originales.

---

## 18) Plan de falsificación

### Fase 1 — Réplica

Checksums:

```text
44 trades
27 long
17 short
net ≈ $13,364.30
PF ≈ 2.99
largest short ≈ $4,746
```

### Fase 2 — Breakout definition

Comparar:

```text
High/Low;
Close;
current-inclusive;
prior-window.
```

### Fase 3 — Dual break

```text
net zero;
intrabar order;
dos eventos;
bar excluded.
```

### Fase 4 — Ablaciones

| Variante | Pregunta |
|---|---|
| price channel directo | ¿el score añade valor? |
| score cross 0 | ¿neutral zone aporta valor? |
| entradas ±5 | regla publicada |
| sólo zero exit | ¿targets aportan valor? |
| targets simétricos | ¿14/-8 está seleccionado? |
| long-only | ¿short añade evidencia? |
| fixed shares | ¿constant notional distorsiona? |

### Fase 5 — Robustez local

Preregistrar un espacio pequeño:

```text
ChannelLength:
5–20

BarSpan:
10–40

Long/Short levels:
simétricos y asimétricos

targets:
interiores al rango teórico
```

### Fase 6 — Cross-sectional

```text
SPY
QQQ
IWM
DIA
sector ETFs
liquid futures
```

### Fase 7 — Postpublicación

Desde febrero de 2016, inputs congelados.

### Fase 8 — Stops

Añadir sólo como módulo de investigación separado.

---

## 19) Decisión — Breakout Score

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
agregación rolling de eventos
+
neutral state
+
target/decay exits

PRIORIDAD:
media-alta

SIGUIENTE GATE:
SCC-028-BREAKOUT-DEFINITION-OUTLIER-AND-OOS-GATE
```

---

# Parte II — Estrategia 029: Trend Capture

## 20) Identificación

- **ID:** `SCC-2016-02-STRAT-029`
- **Artículo:** *Trend Capture Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas:** 11–15
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities y futures
- **Horizonte:** swing trading
- **Bar interval:** diario
- **Historia:** diez años terminando el 31 de diciembre de 2015
- **Portfolio:** 18 ETFs/ETNs
- **Capital inicial:** $100,000
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **Optimización:** enfoque genético en Portfolio Maestro

### Inputs

```text
Fast_EMA_Length = 50
Slow_EMA_Length = 120
Price_Ch_Length = 80
Trail_Stop_Length = 40
Enable_Position_Sizing = 2 en Portfolio Maestro
PS_Initial_Capital = 100000
PS_Perc_Equity = 0.01
PS_ATR_Multiple = 2
PS_ATR_Length = 20
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, pero requiere portfolio engine y sizing coordinado. |
| ¿Es una estrategia CTA completa? | **No.** Es una aproximación educativa. |
| ¿El 1% es una pérdida máxima? | **No.** No existe stop 2 ATR. |
| ¿El universo está correctamente documentado? | El artículo omite USO; el paquete confirma 18 símbolos. |
| ¿Existe optimization evidence completa? | **No.** Sólo configuración final. |
| ¿El resultado termina flat? | **No.** Incluye $20,804.84 de open P/L. |
| ¿El drawdown es moderado? | **No.** Aproximadamente 41% semanal. |
| ¿Está diversificada? | Por símbolos sí, pero con clusters correlacionados. |
| ¿Está científicamente validada? | **No.** Universo, parámetros y sizing fueron seleccionados in-sample. |
| ¿Merece investigación? | **Sí**, por portfolio state, sizing y cross-asset testing. |

Clasificación:

```text
MULTI_ASSET_TREND_FOLLOWING
PORTFOLIO_STATE_REQUIRED
ATR_VOLATILITY_SIZING
RISK_BUDGET_NOT_HARD_STOP
GENETIC_SELECTION_RISK
NOT_SCIENTIFICALLY_VALIDATED
```

---

## 21) Universo real de 18 instrumentos

El artículo imprime 17:

```text
IWM
SPY
EEM
QQQ
GLD
SLV
PALL
UNG
AGG
SGG
NIB
BAL
JO
FXE
FXY
FXF
FXC
```

El workspace RadarScreen y el `.pmx` confirman un instrumento adicional:

```text
USO
```

Universo físico final:

```text
1. IWM
2. SPY
3. EEM
4. QQQ
5. GLD
6. SLV
7. PALL
8. UNG
9. USO
10. AGG
11. SGG
12. NIB
13. BAL
14. JO
15. FXE
16. FXY
17. FXF
18. FXC
```

Conclusión:

```text
SOURCE_TABLE:
17 symbols

PACKAGE_AND_REPORT:
18 symbols

MISSING_EDITORIAL_SYMBOL:
USO
```

---

## 22) Riesgo de universo

La lista mezcla:

```text
equity indices;
emerging markets;
metals;
energy;
bonds;
soft commodities;
currency ETFs/ETNs.
```

Pero no es una muestra neutral de “todos los mercados”.

Posibles grados de libertad:

```text
qué familias se incluyeron;
qué productos concretos;
qué productos se excluyeron;
cuándo se congeló la lista;
disponibilidad histórica;
liquidez;
survivorship;
ETFs frente a ETNs;
series con historiales desiguales.
```

Varios productos no disponen necesariamente de los diez años completos.

El backtest es un panel con historia ragged, no 18 series homogéneas de igual longitud.

---

## 23) Régimen de tendencia

Sea `C_t` el cierre diario.

$$
Fast_t = EMA_{50}(C)_t
$$

$$
Slow_t = EMA_{120}(C)_t
$$

Bull mode:

$$
Fast_t \ge Slow_t
$$

Bear mode:

$$
Fast_t < Slow_t
$$

La igualdad sólo se asigna explícitamente al lado long.

---

## 24) Price channel

La reconstrucción causal es:

$$
Top_t =
\max(High_{t-80},\dots,High_{t-1})
$$

$$
LowBand_t =
\min(Low_{t-80},\dots,Low_{t-1})
$$

El current bar debe excluirse.

Si se incluyera:

$$
Close_t > Highest(High,80)_t
$$

sería imposible.

---

## 25) Entradas

### Long

$$
crossUp(Close, TopBand)_t
\land
Fast_t \ge Slow_t
$$

Entrada:

```text
market at next open
```

### Short

$$
crossDown(Close, LowBand)_t
\land
Fast_t < Slow_t
$$

Entrada:

```text
market at next open
```

### Ambigüedad de crossover contra un level móvil

Debe fijarse si se evalúa:

```text
Close_{t-1} <= TopBand_{t-1}
and Close_t > TopBand_t

o

Close_{t-1} <= TopBand_t
and Close_t > TopBand_t.
```

La primera es la convención natural point-in-time.

---

## 26) Salidas

Long:

$$
Low_t <
\min(Low_{t-1},\dots,Low_{t-40})
$$

Short:

$$
High_t >
\max(High_{t-1},\dots,High_{t-40})
$$

Ejecución:

```text
market at next open
```

El artículo expresa “lowest low de 40 barras”, pero la barra actual debe excluirse para que la desigualdad estricta sea posible.

No existe:

```text
stop de 2 ATR;
dollar stop;
portfolio stop;
max holding;
correlation stop.
```

---

## 27) Position sizing publicado

$$
Qty_{i,t}
=
Round
\left(
\frac{
RiskPct \times TotalEquity_t
}{
ATR_{20,i,t}
\times 2
\times BigPointValue_i
}
\right)
$$

donde:

$$
TotalEquity_t =
InitialEquity
+
ClosedPnL_t
+
OpenPnL_t
$$

Con:

```text
RiskPct = 1%
ATR multiple = 2
ATR lookback = 20
max contracts/shares = 5000
```

### Redondeo

La revista dice “rounded result”, pero no especifica:

```text
floor;
nearest;
lot size;
minimum quantity;
cero cuando no cabe una unidad.
```

Debe reconciliarse con Portfolio Maestro.

---

## 28) Hallazgo crítico: 1% no es riesgo máximo

La fórmula denomina:

```text
Percent Risk = 1%
```

pero no coloca un stop a dos ATR.

El denominador sólo determina el tamaño.

La salida real puede estar mucho más lejos:

```text
ruptura adversa de 40 barras;
gap;
evento de cola;
persistencia contra la posición.
```

Por tanto:

> Es un presupuesto de volatilidad nominal, no una garantía de pérdida máxima del 1%.

La evidencia publicada lo confirma.

Mayor pérdida:

$$
-\$44,823.79
$$

Eso equivale a:

$$
44.82\%
$$

del capital inicial de $100,000.

La equity en el momento de la pérdida podía ser mayor, pero la cifra demuestra que no existe un hard risk cap del 1%.

---

## 29) Riesgo agregado de portfolio

Cada nueva posición puede recibir aproximadamente 1% de equity nominal.

Si existen múltiples posiciones correlacionadas:

```text
SPY + QQQ + IWM + EEM
GLD + SLV + PALL
UNG + USO
FXE + FXF + FXC
```

el riesgo agregado puede apilarse.

No se publica:

```text
portfolio heat cap;
sector cap;
correlation adjustment;
gross exposure cap;
net exposure cap;
concurrent position cap;
cluster risk.
```

`Maximum Contracts=5000` evita tamaños absurdamente grandes por instrumento, pero no controla la correlación.

---

## 30) Dependencia circular del open P/L

El sizing usa:

```text
closed P/L
+
open P/L
```

Consecuencias:

```text
ganancias no realizadas aumentan nuevos tamaños;
pérdidas no realizadas reducen tamaños;
el orden temporal de señales simultáneas importa;
la valoración diaria de todas las posiciones debe ser consistente;
el portfolio state debe existir antes de cada allocation.
```

Si varias señales se ejecutan en la misma apertura, debe definirse si:

```text
todas usan la misma equity previa;
se procesan secuencialmente;
se actualiza la equity después de cada fill;
se prorratea el capital.
```

El artículo no lo especifica.

---

## 31) Dos modos de sizing y riesgo de doble aplicación

El workspace del chart confirma:

```text
Enable_Position_Sizing = 1
```

Es decir, sizing interno activado fuera de Portfolio Maestro.

El `.pmx` confirma:

```text
Enable_Position_Sizing = 2
```

porque Portfolio Maestro aplica el sizing en Strategy Group.

Contrato:

```text
standalone chart:
strategy sizing ON

Portfolio Maestro:
strategy sizing OFF
portfolio sizing ON
```

Un error de configuración podría:

```text
aplicar sizing dos veces;
ignorar sizing;
producir cantidades incompatibles.
```

TSIS debe impedir esta ambigüedad mediante un único owner del position sizing.

---

## 32) Resultados publicados

### Resumen Portfolio Maestro

| Métrica | Resultado |
|---|---:|
| Total Return | $460,492.70 |
| Total Realized Return | $439,687.86 |
| Gross Profit | $1,481,390.54 |
| Gross Loss | -$1,041,702.68 |
| Open Trade P/L | $20,804.84 |
| Número de trades | 290 |
| Ganadores | 131 |
| Perdedores | 159 |
| Percent Profitable | 45.17% |
| Average Trade | $1,516.17 |
| Average Trade (%) | 2.16% |
| Standard Deviation Trade | $14,957.24 |
| Standard Deviation Trade (%) | 14.55% |
| Largest Winning Trade | $113,850.00 |
| Largest Losing Trade | -$44,823.79 |
| Profit Factor | 1.42 |
| Average Win / Average Loss | 1.73 |
| Sharpe Ratio publicado | 0.0678 |
| K-Ratio | 0.1305 |
| Return Retracement Ratio | 1.0696 |
| Compounded Annual Return | 18.82% |
| Compounded Monthly Return | 1.43% |
| Average Annual Return | $46,049.27 |
| Average Annual Return (%) | 22.40% |
| Average Monthly Return | $3,837.44 |
| Average Monthly Return (%) | 1.83% |
| Percent Days Profitable | 53.12% |
| Percent Months Profitable | 57.50% |
| Percent Years Profitable | 70.00% |
| Equity commissions | $13,487.44 |
| Drawdown semanal aproximado | 41% |

---

## 33) Resultado realizado frente a open P/L

$$
439,687.86 + 20,804.84
=
460,492.70
$$

Por tanto:

```text
Total Return:
incluye posiciones abiertas al final

Total Realized Return:
excluye esas posiciones
```

El open P/L representa:

$$
20,804.84 / 460,492.70
\approx 4.52\%
$$

del total reportado.

No es enorme, pero debe etiquetarse.

Una comparación científica debe publicar:

```text
realized-only;
marked-to-market;
forced liquidation;
positions open;
sample-boundary policy.
```

---

## 34) Concentración y distribución

Largest win / largest loss:

$$
113,850 / 44,823.79
\approx 2.54
$$

El largest win representa:

$$
113,850 / 460,492.70
\approx 24.72\%
$$

del total return.

Es material, aunque no sostiene por sí solo toda la estrategia.

Average win / average loss:

```text
1.73
```

Win rate:

```text
45.17%
```

Son coherentes con trend following.

---

## 35) Resultado por símbolo

La figura informa:

```text
mayores contribuyentes:
FXE
FXY

contribución negativa:
AGG
EEM
NIB
```

La curva por símbolo también muestra una dispersión amplia.

Esto confirma que:

```text
el resultado no es uniforme;
algunos mercados destruyen valor;
la selección del universo importa;
el portfolio depende de pocos trends favorables.
```

---

## 36) Curva de equity

La curva:

```text
asciende por grandes escalones;
presenta mesetas;
sufre drawdowns extensos;
alcanza picos cercanos a $700k de P/L acumulado;
termina sensiblemente por debajo de máximos;
registra ~41% de drawdown semanal.
```

No es una curva suave.

El retorno compuesto del 18.82% debe leerse junto con el drawdown aproximado del 41%.

---

## 37) Genetic optimization y degrees of freedom

Parámetros de señal:

```text
Fast EMA
Slow EMA
Price channel
Exit channel
```

Parámetros de sizing:

```text
ATR length
ATR multiple
risk percentage
max quantity
```

Otros grados de libertad:

```text
universo de 18 productos;
product family;
periodo;
commission model;
position sizing owner;
genetic population;
fitness;
portfolio settings;
MaxBarsBack;
open positions at boundary.
```

Aunque sólo se publiquen cuatro parámetros de señal, el experimento completo tiene muchos grados de libertad.

El proyecto no conserva suficiente evidencia para calcular:

```text
Deflated Sharpe Ratio;
Probability of Backtest Overfitting;
número efectivo de trials;
selection-adjusted significance.
```

---

## 38) Sesgo de instrumentos e historia ragged

El universo final de 18 productos no posee necesariamente una historia uniforme de diez años.

Debe documentarse por símbolo:

```text
inception date;
first usable bar;
delisting;
ticker changes;
liquidity;
survivorship;
ETN credit risk;
corporate actions;
missing data.
```

El reporte agregado puede comenzar con menos instrumentos y añadir otros después.

Eso cambia:

```text
diversificación;
equity;
sizing;
correlation;
número de trades.
```

---

## 39) Costes

Se modelan:

```text
$0.01 por acción
```

Total:

```text
$13,487.44
```

No se publica:

```text
slippage;
bid/ask;
impact;
gaps at next open;
borrow;
ETN liquidity;
market-on-open constraints;
partial fills.
```

La comisión supone aproximadamente:

$$
13,487.44 / 460,492.70
\approx 2.93\%
$$

del retorno total publicado.

El slippage puede ser más significativo en algunos ETNs y productos menos líquidos.

---

## 40) ¿Dónde podría estar el edge?

Hipótesis principal:

> Los breakouts de un canal de 80 días presentan continuidad cuando están alineados con un régimen EMA 50/120, y un sizing inversamente proporcional al ATR distribuye mejor el riesgo entre mercados.

Mecanismos posibles:

```text
momentum cross-asset;
trend persistence;
volatility scaling;
diversificación;
crisis alpha;
positive convexity;
participación en grandes tendencias.
```

Hipótesis alternativas:

```text
selection de universe;
genetic overfitting;
ETF/ETN launch bias;
correlation stacking;
equity compounding;
few large trades;
FXE/FXY concentration;
price-channel artifact;
cost underestimation.
```

---

## 41) Auditoría científica

### 41.1 Sin OOS

No hay holdout.

### 41.2 Genetic optimization sin ledger

No puede medirse selección.

### 41.3 Universe selection

No está preregistrado.

### 41.4 Risk sizing sin matching stop

El 1% no es pérdida máxima.

### 41.5 Correlation risk

No se controla.

### 41.6 Open P/L en el resultado

Debe separarse.

### 41.7 Drawdown alto

41% puede ser incompatible con el supuesto “risk per trade”.

### 41.8 Un único portfolio

No hay portfolios alternativos preregistrados.

### 41.9 Slippage cero

Especialmente relevante para ETNs.

### 41.10 Ragged history

No todos los símbolos aportan los diez años.

### 41.11 Self-inclusion de channels

Debe resolverse.

### 41.12 Sizing temporal

Usa open P/L y compounding.

### 41.13 Owner dual de sizing

Chart frente a Portfolio Maestro.

### 41.14 No portfolio liquidation contract

El informe termina con posiciones abiertas.

### 41.15 No inflation/capital comparison

El resultado nominal no se compara con baselines de igual riesgo.

---

## 42) Contrato TSIS

### Datos por instrumento

```text
daily OHLCV
corporate actions
instrument metadata
inception/delisting
session calendar
quotes or spread model
```

### Portfolio State

```text
portfolio_timestamp
initial_equity
realized_pnl
unrealized_pnl
total_equity
gross_exposure
net_exposure
cluster_exposure
open_positions
pending_orders
risk_budget_used
```

### Signal State

```text
ema_fast_50
ema_slow_120
bull_mode
bear_mode
prior_channel_high_80
prior_channel_low_80
long_breakout
short_breakout
prior_exit_low_40
prior_exit_high_40
atr_20
```

### Allocation State

```text
risk_pct
atr_multiple
big_point_value
raw_quantity
rounded_quantity
max_quantity
sizing_owner
equity_snapshot_id
```

### Estados de indisponibilidad

```text
INSUFFICIENT_EMA_HISTORY
INSUFFICIENT_CHANNEL_HISTORY
INSUFFICIENT_ATR_HISTORY
INSTRUMENT_NOT_YET_LISTED
SYMBOL_DELISTED
CORPORATE_ACTION_UNRESOLVED
PORTFOLIO_EQUITY_UNAVAILABLE
SIMULTANEOUS_ALLOCATION_POLICY_UNRESOLVED
SIZING_OWNER_CONFLICT
MISSING_NEXT_OPEN
```

---

## 43) Pseudocódigo funcional

```python
for symbol in universe:

    fast = ema(close, 50)
    slow = ema(close, 120)

    top = max(high[t - 80:t])
    bottom = min(low[t - 80:t])

    long_signal = (
        close[t - 1] <= top_prev
        and close[t] > top
        and fast[t] >= slow[t]
    )

    short_signal = (
        close[t - 1] >= bottom_prev
        and close[t] < bottom
        and fast[t] < slow[t]
    )

    atr = average_true_range(20)

    equity_snapshot = portfolio_equity_at_decision_time()

    raw_qty = (
        0.01 * equity_snapshot
        / (atr[t] * 2.0 * big_point_value[symbol])
    )

    qty = round_according_to_portfolio_contract(raw_qty)
    qty = min(qty, 5000)

    if long_signal:
        schedule_long(symbol, qty, next_open)

    if short_signal:
        schedule_short(symbol, qty, next_open)

    if long and low[t] < min(low[t - 40:t]):
        schedule_exit(symbol, next_open)

    if short and high[t] > max(high[t - 40:t]):
        schedule_exit(symbol, next_open)
```

---

## 44) Plan de réplica y falsificación

### Fase 1 — Configuración física

Reproducir:

```text
18 símbolos;
incluidos USO y JO;
inputs 50/120/80/40;
risk 1%;
ATR 20 × 2;
max 5000;
initial 100k.
```

### Fase 2 — Checksum de portfolio

```text
290 trades
131 ganadores
159 perdedores
total return ≈ $460,492.70
realized ≈ $439,687.86
open P/L ≈ $20,804.84
PF ≈ 1.42
```

### Fase 3 — Sizing semantics

Resolver:

```text
rounding;
minimum quantity;
same-day simultaneous signals;
equity snapshot;
open P/L timing;
portfolio allocation order.
```

### Fase 4 — Risk truth

Comparar:

```text
ATR sizing sin stop — publicado
ATR sizing + hard 2 ATR stop
channel-distance sizing
volatility targeting
equal notional
equal risk by structural exit
```

### Fase 5 — Universe falsification

```text
leave-one-symbol-out;
leave-one-asset-class-out;
random comparable universe;
liquidity-filtered PIT universe;
inception-aware panel.
```

### Fase 6 — Concentration

```text
remove largest trade;
remove FXE;
remove FXY;
remove top two symbols;
bootstrap by symbol;
bootstrap by year.
```

### Fase 7 — Correlation-aware risk

```text
portfolio heat cap;
cluster cap;
gross exposure cap;
covariance targeting.
```

### Fase 8 — Ablaciones

| Variante | Pregunta |
|---|---|
| price channel sin EMA | ¿el filtro añade valor? |
| EMA regime sin channel | ¿el breakout añade valor? |
| no ATR sizing | ¿el sizing añade valor? |
| fixed shares/notional | ¿el compounding explica el resultado? |
| long-only | ¿short aporta crisis alpha? |
| realized-only | ¿open P/L cambia la conclusión? |

### Fase 9 — Postpublicación

Desde febrero de 2016, configuración congelada.

### Fase 10 — Costes

Por instrumento:

```text
spread;
slippage;
liquidity;
borrow;
gaps;
ETN execution.
```

---

## 45) Eventos para TSIS

### Event State

```text
event_type:
channel_breakout_in_ema_regime

subject_scope:
single_instrument

attributes:
direction
channel_length
ema_fast
ema_slow
atr
distance_to_exit_channel
```

### Portfolio Event State

```text
event_type:
portfolio_risk_allocation

attributes:
equity_snapshot
symbol
raw_qty
rounded_qty
risk_pct
atr_multiple
cluster_exposure_before
cluster_exposure_after
```

### Outcomes

```text
trade_return
MFE
MAE
realized_loss_vs_nominal_risk
portfolio_drawdown_contribution
symbol contribution
cluster contribution
```

---

## 46) Decisión — Trend Capture

```text
IMPLEMENTAR:
sí, como portfolio research benchmark

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
multi-asset trend
+
portfolio state
+
volatility sizing
+
risk attribution

PRIORIDAD:
alta

RIESGO PRINCIPAL:
optimization selection
y falsa interpretación del 1% risk

SIGUIENTE GATE:
SCC-029-PORTFOLIO-SIZING-UNIVERSE-RISK-AND-OOS-GATE
```

---

# Parte III — Utility Kit 1 reimpreso

## 47) Estado documental

Las páginas 17–21 son una reimpresión textual exacta del Utility Kit publicado en el Issue 13.

Incluye:

```text
TSL:Friday Exit
TSL:Close On Last Bar
TSL:Strategy Equity
TSL:3rd Friday
$MinFluc
```

No se asigna un nuevo Strategy ID.

Referencia:

```text
SCC-2016-01-UTILITY-KIT-001
```

### Binario diferente

El `.ELD` del Issue 13 tenía:

```text
21,980 bytes
SHA-256:
b74343395a1b2994a013826844a3036d210842cae88e6c7ff08e0974040728d4
```

El `.ELD` del Issue 14 tiene:

```text
25,643 bytes
SHA-256:
f3b08dbff8bfbd5802ad8053b9126b6572f9a881936a0e482b2ae2a09f50a7a1
```

Por tanto:

```text
ARTICLE_TEXT:
IDENTICAL_REPRINT

ELD_BINARY:
NOT_IDENTICAL

SOURCE_CODE_IDENTITY:
NOT_CERTIFIABLE
```

Puede tratarse de una reexportación, recompilación o revisión interna. Al no poder leerse el código, no se afirma que sean funcionalmente idénticos.

---

## 48) Contratos conservados del Utility Kit

### Friday Exit

```text
salida de riesgo de fin de semana;
depende de timestamps de barras;
debe usar calendario de sesión.
```

### Close On Last Bar

```text
sólo backtest estático;
no es una salida económica;
debe etiquetarse como sample-boundary liquidation.
```

### Strategy Equity

```text
realized P/L;
open P/L;
total equity;
high-watermark y low-watermark.
```

### 3rd Friday

```text
referencia calendario;
no equivale automáticamente a expiration operable.
```

### $MinFluc

```text
tick size;
price scale;
BigPointValue;
instrument metadata con effective date.
```

---

# Parte IV — Ideas transversales del Issue 14

## 49) Un score rolling es una representación de eventos

Breakout Score propone una idea importante:

```text
no reaccionar a cada evento aislado;
acumular evidencia reciente;
operar el estado agregado.
```

Esto encaja directamente con:

```text
Event State → rolling evidence → decision state
```

---

## 50) La salida también puede depender del estado agregado

El mismo score sirve para:

```text
entrada;
agotamiento;
target.
```

No hace falta que toda salida proceda del precio bruto.

---

## 51) Targets asimétricos implican una hipótesis adicional

`+14/-8` no es un detalle.

Es una hipótesis sobre la persistencia relativa de mercados alcistas y bajistas.

---

## 52) El nombre “risk per trade” puede ser engañoso

Sin un stop asociado:

```text
ATR sizing ≠ pérdida máxima.
```

TSIS debe diferenciar:

```text
nominal_risk_unit
hard_loss_cap
structural_exit_distance
realized_loss
```

---

## 53) El portfolio puede superar ampliamente el riesgo unitario

Varias posiciones correlacionadas pueden apilar el riesgo.

---

## 54) Open P/L forma parte del estado, no del realized edge

El resultado final debe descomponerse.

---

## 55) Configuración final no equivale a evidencia de búsqueda

Un `.pmx` permite reproducir la configuración, pero no medir overfitting si no conserva:

```text
search path;
trials;
fitness;
seed;
rankings.
```

---

## 56) El universo es un hiperparámetro

Seleccionar 18 instrumentos forma parte del proceso de modelización.

---

## 57) Ragged histories cambian el portfolio con el tiempo

La diversificación no es constante.

---

## 58) Un solo owner debe controlar el sizing

Evita doble aplicación o ausencia de sizing.

---

## 59) Las capturas pueden contener configuraciones antiguas

La figura `15/-9` frente al contrato `14/-8` lo demuestra.

---

## 60) Los captions pueden ser incorrectos

La figura de Regression Angles dentro de Trend Capture no debe contaminar la clasificación.

---

## 61) Ideas secundarias de backtesting extraídas

1. Agregar eventos antes de operar.
2. Crear neutral zones.
3. Separar zero exit y target exit.
4. Medir outlier dependence por rama.
5. Diferenciar sizing de hard risk.
6. Incorporar open P/L en Portfolio State.
7. Controlar signals simultáneas.
8. Versionar el universe.
9. Auditar inception dates.
10. Medir cluster exposure.
11. Conservar genetic optimization lineage.
12. Publicar realized y marked-to-market.
13. Impedir doble sizing.
14. Tratar captions como evidencia débil.
15. Conservar inputs físicos del workspace como evidencia más fuerte que una screenshot.

---

# Parte V — Registro consolidado para TSIS

## 62) Objetos de información afectados

### Breakout Score

```text
price_movement
volatility_range_state
price_location
event_state
```

### Trend Capture

```text
price_movement
volatility_range_state
broad_market_context
portfolio_state
instrument_metadata
```

---

## 63) Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Trend Capture risk truth | el 1% publicado no es pérdida máxima |
| 2 | Breakout Score outlier/OOS | muestra muy pequeña y short concentrado |
| 3 | Portfolio universe reconstruction | discrepancia 17/18 y ragged histories |
| 4 | Breakout event formula | High/Low vs Close y dual breaks |
| 5 | Utility Kit binary comparison | sólo si se necesita certificar cambios de código |

---

## 64) Gates propuestos

### SCC-028-A — Breakout Event Formula

Debe resolver:

```text
price field;
prior channel;
dual break;
rolling update.
```

### SCC-028-B — Exit Semantics

Debe resolver:

```text
zero touch;
target touch;
next-open fill.
```

### SCC-028-C — Outlier Dependence

Debe publicar leave-one-trade-out.

### SCC-028-D — Parameter Lineage

Debe registrar el grid nuevo.

### SCC-028-E — Postpublication OOS

Inputs congelados `8/17/5/-5/14/-8`.

### SCC-029-A — Universe Contract

Debe congelar los 18 símbolos e inception dates.

### SCC-029-B — Channel Semantics

Debe resolver prior-window.

### SCC-029-C — Sizing Owner

Debe impedir doble sizing.

### SCC-029-D — Equity Snapshot

Debe definir signals simultáneas y open P/L.

### SCC-029-E — Risk Truth

Debe comparar nominal risk y realized loss.

### SCC-029-F — Portfolio Heat

Debe introducir controles de correlación.

### SCC-029-G — Genetic Search Ledger

Debe conservar trials y fitness.

### SCC-029-H — Boundary Policy

Debe separar realized/open/forced liquidation.

### SCC-029-I — Postpublication OOS

Configuración congelada.

---

# Conclusión

El Issue 14 contiene dos estrategias nuevas y una reimpresión del Utility Kit.

## Breakout Score

La estrategia:

```text
canal de 8 barras
→ evento +1/-1
→ suma rolling de 17 barras
→ long al cruzar +5
→ short al cruzar -5
→ exit a 0 o target +14/-8
```

Publica:

```text
44 trades
$13,364.30
PF 2.99
56.82% ganadoras
```

pero:

```text
el lado short sólo contiene 17 trades;
una operación aporta 88.73% del net short;
no hay stop;
los inputs fueron optimizados;
no se conserva la búsqueda;
la screenshot de settings contiene una configuración antigua.
```

Su valor principal es representar **evidencia acumulada de eventos**, no demostrar un edge listo para uso.

## Trend Capture

La estrategia:

```text
EMA 50/120
+
breakout de canal 80
+
salida por canal 40
+
sizing inverso a ATR20 × 2
+
1% nominal de equity
+
portfolio de 18 instrumentos
```

Publica:

```text
$460,492.70 total return
290 trades
PF 1.42
CAR 18.82%
drawdown semanal ~41%
```

pero:

```text
el 1% no es un hard risk cap;
la mayor pérdida fue $44,823.79;
el portfolio apila correlaciones;
el universo fue seleccionado;
la optimización genética no tiene ledger;
el reporte incluye $20,804.84 de open P/L;
el artículo omite USO aunque el paquete confirma 18 símbolos;
no hay OOS.
```

Su mayor valor para TSIS es como laboratorio de:

```text
Portfolio State
sizing
risk attribution
universe governance
multi-asset validation
```

## Utility Kit

Es una reimpresión textual del Issue 13.

El binario es diferente y no puede afirmarse que el código sea idéntico sin abrirlo en TradeStation.

## Estado final

```text
ISSUE_14_STATUS:
DOCUMENTALLY_CLOSED

CORRECT_PDF_SOURCE:
FOUND_INSIDE_ZIP

STANDALONE_FILE:
ZONE_IDENTIFIER_ONLY

NEW_STRATEGIES_EXTRACTED:
2

UTILITY_KIT_REPRINTS:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguientes gates recomendados:

```text
1. SCC-029-PORTFOLIO-SIZING-UNIVERSE-RISK-AND-OOS-GATE
2. SCC-028-BREAKOUT-DEFINITION-OUTLIER-AND-OOS-GATE
```
