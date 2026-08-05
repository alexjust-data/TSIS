# Auditoría completa — TradeStation Strategy Concepts Club, Issue 10 (octubre de 2015)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. Pinpoint Pullback Strategy
2. The Engulfing Candles Strategy
3. Williams E-mini Influx Strategy — artículo bonus
4. ideas secundarias de investigación y backtesting presentes en el número
5. reconstrucción matemática y temporal
6. auditoría de resultados y supuestos de ejecución
7. inspección forense de los archivos .ELD y workspaces .tsw
8. contratos de réplica para TSIS
9. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 22 páginas: `SCC Issue 10 Oct 2015(1).pdf`.
- Archivo de apoyo: `2015-10.zip`.
- PDF duplicado incluido en el ZIP.
- Tres contenedores propietarios `.ELD`:
  - `TSL PINPOINT PULLBACK.ELD`;
  - `TSL ENGULFING CANDLES.ELD`;
  - `TSL WILLIAMS E-MINI INFLUX.ELD`.
- Tres workspaces OLE/Compound Document `.tsw`:
  - `TSL Pinpoint Pullback.tsw`;
  - `TSL.Engulfing Candles.tsw`;
  - `TSL.Williams E-mini Influx.tsw`.
- Todas las tablas y figuras renderizadas del PDF, incluidas:
  - reglas y ejemplo de Pinpoint Pullback;
  - informe completo de rendimiento, curva de capital, superficie de sensibilidad y MAE;
  - definición visual y contractual de engulfing candles;
  - informe de Engulfing Candles y análisis de rachas;
  - reglas del artículo bonus de Larry Williams;
  - informe de Williams E-mini Influx, rachas y curva de capital.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman los workspaces, streams OLE y contenedores .ELD

AUDIT:
inferencia técnica, crítica científica
y propuesta de implementación en TSIS
```

Cuando una decisión no queda resuelta por la revista o el paquete, se registra como ambigüedad. No se completa silenciosamente.

No se ha añadido investigación web externa. Las fórmulas que no aparecen literalmente en el artículo se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

### Inventario forense del paquete

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `SCC Issue 10 Oct 2015(1).pdf` | 6,092,363 bytes | `58b8f98f4752d638e4e2d393e434236400d754997b62d2ab69420b0e8ab1c17d` |
| `2015-10.zip` | 6,134,430 bytes | `bcf7ac7ed3d5cf6e234e3c1081fa5de6d7f890e350f5c5f60085bddb6035a505` |
| `SCC Issue 10 Oct 2015.pdf` dentro del ZIP | 6,092,363 bytes | `58b8f98f4752d638e4e2d393e434236400d754997b62d2ab69420b0e8ab1c17d` |
| `TSL PINPOINT PULLBACK.ELD` | 10,456 bytes | `32fd8f0bce9c1286eccd75403972811b3276455e478614a7c30e8f99dbc78d7a` |
| `TSL Pinpoint Pullback.tsw` | 20,480 bytes | `d08a764233fc09ca1c0aecdf6348a0f39704221444ee36381252dd81f33ae5e2` |
| `TSL ENGULFING CANDLES.ELD` | 27,530 bytes | `f4a3ca0c574a4d4f759fee2ed9b4daae3e64cc692230f9b724c38bd11208a048` |
| `TSL.Engulfing Candles.tsw` | 29,184 bytes | `cfb5621adfb9b213acf57001fa2b141222952ede1191100f4981cb9d6ebcfb78` |
| `TSL WILLIAMS E-MINI INFLUX.ELD` | 18,805 bytes | `94ff62ae6fe0fc470f14104010f18104a40dd749b49c4b4cb9487ff60655ee6d` |
| `TSL.Williams E-mini Influx.tsw` | 26,112 bytes | `0fa90f393a55e66c96dbe1e17aabea354f623f42af20ad2a5da981d1f8977117` |

El PDF del ZIP es binariamente idéntico al PDF cargado por separado.

El ZIP también contiene pequeños streams `Zone.Identifier`. Son metadatos del sistema de archivos y no forman parte del contenido científico.

### Limitación de los `.ELD`

Los tres `.ELD` son contenedores propietarios TradeStation. Presentan marcadores internos de exportación, pero no exponen el código EasyLanguage como texto legible.

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la prioridad exacta de órdenes;
no pueden resolverse sólo por inspección las funciones Lowest/Highest,
MRO, ATR, same-close exits ni la fórmula de Williams %R.
```

### Workspaces y `optdatafile`

Los tres workspaces son documentos OLE válidos. Los tres contienen un stream denominado `optdatafile`, pero su tamaño es **cero bytes**.

```text
no se conserva ningún grid de optimización;
no se conservan rankings completos;
no se conserva el número de configuraciones probadas;
no puede comprobarse el puesto exacto de los parámetros publicados;
no puede reconstruirse la selección in-sample desde el paquete.
```

### Evidencia del workspace Pinpoint Pullback

El workspace confirma:

```text
Serie:
AAPL 65 min [NASDAQ] Apple Inc.

Estrategia:
TSL:Pinpoint Pullback

Inputs activos:
Avg_Length = 20
Displ_Length = 9
Trail_Stop_Length = 12
Exit_MRO_Length = 9

Indicadores:
Mov Avg 1 Line — Close, Length 20, Displace 0
Mov Avg 1 Line — Close, Length 20, Displace -9
```

El desplazamiento `-9` pertenece a la visualización del indicador. La estrategia causal compara la media actual con su valor histórico nueve barras atrás; no debe implementarse leyendo una línea gráficamente desplazada hacia el futuro.

### Evidencia del workspace Engulfing Candles

El workspace confirma:

```text
Serie:
GBPUSD 120 min [FOREX]
British Pound / US Dollar

Componentes activos:
TSL:Engulfing Candles
TSL:Engulfing Candles ShowMe
TSL:Strategy ATR Bands
TimeExit (Bars) LX
TimeExit (Bars) SX

Inputs activos de la estrategia:
AvgBodyLength = 3
ATR_Length = 5
ProfitTgt_ATRFactor = 2.2
Stop_ATRFactor = 4.8

Time exits:
BarToExitOn LX = 32
BarToExitOn SX = 13
```

Éste es un hallazgo contractual importante: los resultados publicados **no usan** los defaults narrativos `5/5/3/3/5`. Usan una configuración seleccionada mediante pruebas y optimizaciones, con salidas temporales fuertemente asimétricas.

### Evidencia del workspace Williams E-mini Influx

El workspace confirma:

```text
Serie:
@ES=107XN Daily [CME]
E-mini S&P 500 Custom Continuous Contract

Componentes activos:
TSL:Williams E-mini Influx
TSL:Williams E-mini Influx Exit
TSL:Williams E-mini Influx Days
%R

Inputs activos:
PctRVal = 85
PctRLen = 8
StopLossPct = 2.5
HoldDays = 1
DaysLeftToPaint = 19
```

El indicador visual `%R` del workspace también utiliza longitud 8. Sus dos referencias gráficas aparecen configuradas a 85; esto es una peculiaridad de visualización y no debe confundirse con dos filtros distintos en la estrategia.

---

## 0.1 Resultado ejecutivo del issue

| ID | Estrategia | Tipo real | Evidencia publicada | Riesgo principal | Decisión |
|---|---|---|---|---|---|
| 019 | Pinpoint Pullback | Pullback de corto horizonte dentro de una pendiente de media y movimiento de plazo mayor | AAPL 65m, 10 años, 462 trades, PF 1.67, $24,670.62 | wording 20 “day” aunque son barras; salida Lowest/Highest ambigua; sin slippage; selección in-sample | candidato de réplica y ablación, no edge aceptado |
| 020 | Engulfing Candles | Body-engulfing sin filtro de tendencia + stop entry + bracket ATR + time exits asimétricos | GBPUSD 120m, 5 años, 590 trades, PF 1.44, $55,147.90 | optimización por etapas, LIBBT insuficiente para ordenar fills, barras dependientes de zona horaria, payoff adverso | buen laboratorio de patrones y ejecución intrabar; evidencia insuficiente |
| 021 | Williams E-mini Influx | Long-only de calendario a comienzos de mes con %R, up-day y salida en primer cierre rentable | ES diario, 1997–2015, 115 trades, 80% ganadoras, PF 1.66 | entrada al “next open” y salida al mismo cierre no causalmente especificadas; dependencia extrema de win rate | hipótesis de calendario interesante, pero ejecución publicada debe reformularse |

### Veredicto global

```text
ISSUE_STATUS:
VALUABLE_SOURCE_MATERIAL

STRATEGIES_FOUND:
3

SCIENTIFICALLY_VALIDATED:
0

REPRODUCTION_PRIORITY:
HIGH

LIVE_STATUS:
NOT_ELIGIBLE
```

El número es especialmente útil porque expone tres problemas distintos:

1. **La escala temporal real de un input debe derivarse de las barras, no de su nombre narrativo.**
2. **Una estrategia compuesta incluye todos los componentes y sus prioridades de ejecución.**
3. **Un fill de backtest en el próximo open o en el cierre actual puede no ser causalmente operable.**

---

# Parte I — Estrategia 019: Pinpoint Pullback

## 1) Identificación

- **ID:** `SCC-2015-10-STRAT-019`
- **Artículo:** *Pinpoint Pullback Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas del PDF:** 4–8
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities, ETFs, futures
- **Horizonte declarado:** swing trading
- **Activo del test:** Apple Inc.
- **Símbolo:** `AAPL`
- **Intervalo:** 65 minutos
- **Periodo:** 10 años terminando el 30 de junio de 2015
- **Capital inicial:** $15,000
- **Tamaño:** $10,000 por operación, redondeado hacia abajo a una acción
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **MaxBarsBack:** 80
- **Inputs activos:** `20 / 9 / 12 / 9`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí.** |
| ¿Puede replicarse aproximadamente? | **Sí.** El workspace confirma serie, intervalo, inputs e indicadores. |
| ¿Puede replicarse exactamente? | **No todavía.** Deben reconciliarse la salida Lowest/Highest, el MRO y la plantilla de sesión. |
| ¿Es un pullback dentro de tendencia? | **Sí**, aunque la definición de tendencia y pullback está formada sólo por precios y una SMA. |
| ¿El desplazamiento introduce look-ahead? | **No si se implementa como `MA_t` frente a `MA_{t-9}`.** Sí sería incorrecto leer el plot desplazado como dato futuro. |
| ¿El artículo demuestra edge? | **No.** Hay optimización parcial, un activo y ninguna prueba OOS. |
| ¿Está preparada para operar? | **No.** Falta slippage, corporate actions, reglas exactas de salida, OOS y stress de sesión. |
| ¿Merece estudiarse? | **Sí.** Es simple, auditable y produce suficientes operaciones para una réplica útil. |

Clasificación:

```text
SOURCE_REPRODUCTION_CANDIDATE
TREND_PULLBACK_EVENT
INTRADAY_SWING_STRATEGY
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Corrección conceptual: no son “20-day”, sino 20 barras

La revista utiliza expresiones como “20-day moving average”, pero el gráfico y el workspace son de **65 minutos**.

La especificación correcta es:

```text
SMA de 20 barras de 65 minutos
no SMA de 20 días
```

Si la sesión regular de 390 minutos se divide en barras de 65 minutos:

```text
6 barras por sesión
20 barras ≈ 3.33 sesiones
9 barras ≈ 1.5 sesiones
29 barras ≈ 4.83 sesiones
12 barras ≈ 2 sesiones
```

La plantilla exacta de sesión debe confirmarse. Si el workspace incluye premarket, postmarket, cierres parciales o una alineación distinta, esas equivalencias cambian.

Este error terminológico no invalida el algoritmo, pero sí cambia por completo su horizonte económico.

---

## 3. Qué estrategia es realmente

La estrategia combina tres capas:

```text
1. pendiente de una SMA:
   determina dirección de tendencia

2. comparación del cierre en dos horizontes:
   identifica un retroceso reciente
   dentro de un movimiento mayor

3. bloqueo post-exit:
   impide reversión inmediata
   y fuerza una pausa de reentrada
```

No intenta comprar una ruptura. Compra cuando:

```text
la media sigue subiendo;
el precio ha retrocedido respecto de 9 barras atrás;
pero todavía está por encima de 29 barras atrás.
```

Por tanto:

> Es una estrategia de contramovimiento local condicionado por tendencia intermedia.

Tiene rasgos de trend following y mean reversion:

```text
trend following:
sólo opera en la dirección de la pendiente

mean reversion:
entra contra el movimiento de las últimas 9 barras
```

---

## 4. Reconstrucción matemática

Sea `C_t` el cierre de la barra de 65 minutos.

### 4.1 Media

Con `L = 20`:

\[
MA_t = SMA_{20}(C)_t
\]

### 4.2 Pendiente discreta

Con desplazamiento `d = 9`:

\[
uptrend_t = MA_t > MA_{t-d}
\]

\[
downtrend_t = MA_t < MA_{t-d}
\]

No se calcula una derivada ni un ángulo. Sólo se compara la media actual con su valor nueve barras atrás.

### 4.3 Pullback long

\[
C_t < C_{t-d}
\]

y simultáneamente:

\[
C_t > C_{t-(L+d)}
\]

Con defaults:

\[
C_t < C_{t-9}
\]

\[
C_t > C_{t-29}
\]

Interpretación:

```text
el precio ha descendido en el tramo reciente de 9 barras;
pero conserva ganancia frente a un punto 29 barras atrás.
```

### 4.4 Pullback short

\[
C_t > C_{t-9}
\]

\[
C_t < C_{t-29}
\]

Interpretación:

```text
rebote reciente dentro de un movimiento bajista mayor.
```

### 4.5 Condición flat

```text
MarketPosition = 0
```

La estrategia no abre una nueva posición mientras otra está abierta.

### 4.6 Bloqueo por MRO

Long sólo si no se ha generado una salida short durante las últimas 9 barras.

Short sólo si no se ha generado una salida long durante las últimas 9 barras.

La revista describe la intención, pero no expone la semántica exacta de la función `MRO`:

```text
¿incluye la barra actual?
¿devuelve -1 cuando no encuentra evento?
¿el evento de salida se evalúa sólo estando en posición?
¿un exit condition que aparece estando flat reinicia el bloqueo?
```

Estas preguntas deben resolverse por reconciliación de trades.

---

## 5. Reglas funcionales

### Long

```text
if flat
and SMA20_t > SMA20_t-9
and Close_t < Close_t-9
and Close_t > Close_t-29
and no short-exit event in last 9 bars:
    buy at open of next bar
```

### Short

```text
if flat
and SMA20_t < SMA20_t-9
and Close_t > Close_t-9
and Close_t < Close_t-29
and no long-exit event in last 9 bars:
    sell short at open of next bar
```

---

## 6. Salidas y ambigüedad de auto-inclusión

La regla publicada dice:

```text
long:
salir si Low está por debajo del lowest low de las últimas 12 barras

short:
salir si High está por encima del highest high de las últimas 12 barras
```

Si el mínimo incluye la barra actual:

\[
Low_t < Lowest(Low,12)_t
\]

es imposible.

La reconstrucción causal más probable es:

\[
Low_t < \min(Low_{t-1},\ldots,Low_{t-12})
\]

para long, y:

\[
High_t > \max(High_{t-1},\ldots,High_{t-12})
\]

para short.

Otra posibilidad EasyLanguage es:

```text
Low < Lowest(Low, 12)[1]
High > Highest(High, 12)[1]
```

También podría utilizarse igualdad con un extremo que incluye la barra actual.

Esto debe quedar como gate, no como detalle menor: cambia fechas de salida, holding periods, PnL y eventos que alimentan el MRO.

---

## 7. Arquitectura temporal

### 7.1 Señal

Se calcula al cierre de la barra `t`.

### 7.2 Entrada y salida

Se ejecutan a mercado en la apertura de `t+1`.

```text
bar close t:
condiciones observables

bar open t+1:
fill
```

### 7.3 Riesgo de overnight

El intervalo de 65 minutos puede generar posiciones que crucen:

```text
cierre regular;
overnight;
fin de semana;
earnings;
corporate actions.
```

El artículo no define una liquidación end-of-day.

### 7.4 Plantilla de sesión

Un cambio de plantilla altera:

```text
cierres de barra;
SMA;
Close[9];
Close[29];
señales;
salidas.
```

TSIS debe congelar:

```text
timezone
session start/end
regular vs extended hours
bar alignment
half-days
DST
```

---

## 8. Corporate actions y sizing

La estrategia usa aproximadamente $10,000 por operación:

\[
qty_t =
\left\lfloor
\frac{10{,}000}{reference\_price_t}
\right\rfloor
\]

El informe muestra un máximo de 1,620 acciones. Eso es coherente con precios históricos ajustados de AAPL muy inferiores a los precios nominales originales debido a splits.

Debe separarse:

```text
signal view:
serie ajustada coherente para indicadores

execution view:
precio raw operable y cantidad ajustada por corporate actions
```

Si se calcula el tamaño sobre un precio ajustado pero se ejecuta sobre raw sin transformar la cantidad, el PnL queda corrupto.

El `reference_price` exacto del sizing debe reconciliarse:

```text
cierre de señal;
apertura siguiente;
precio de orden;
otra propiedad de TradeStation.
```

---

## 9. Resultados publicados

### 9.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $24,670.62 |
| Beneficio bruto | $61,421.15 |
| Pérdida bruta | -$36,750.53 |
| Profit Factor | 1.67 |
| Operaciones | 462 |
| Ganadoras | 176 |
| Perdedoras | 285 |
| Even | 1 |
| Percent Profitable | 38.10% |
| Expectativa media | $53.40 |
| Ganancia media | $348.98 |
| Pérdida media | -$128.95 |
| Ratio ganancia/pérdida | 2.71 |
| Mayor ganancia | $3,121.76 |
| Mayor pérdida | -$787.52 |
| Máx. ganadoras consecutivas | 6 |
| Máx. perdedoras consecutivas | 13 |
| Barras medias ganadoras | 29.74 |
| Barras medias perdedoras | 7.11 |
| Máximo tamaño | 1,620 acciones |
| Acciones acumuladas | 191,228 |
| Return on Initial Capital | 164.47% |
| Annual Rate of Return | 9.78% |
| RINA Index | 314.69 |
| Percent of Time in Market | 47.57% |
| Drawdown semanal aproximado | 14% |

### 9.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $18,348.89 | $6,321.73 |
| Profit Factor | 1.94 | 1.37 |
| Operaciones | 248 | 214 |
| Percent Profitable | 41.53% | 34.11% |
| Expectativa media | $73.99 | $29.54 |
| Ganancia media | $367.17 | $323.33 |
| Pérdida media | -$135.20 | -$122.56 |
| Ratio ganancia/pérdida | 2.72 | 2.64 |
| Barras medias ganadoras | 32.50 | 25.84 |
| Barras medias perdedoras | 6.68 | 7.55 |

### 9.3 Concentración long

\[
18{,}348.89 / 24{,}670.62 \approx 74.38\%
\]

Casi tres cuartas partes del beneficio proceden de longs.

### 9.4 Característica trend-following

\[
29.74 / 7.11 \approx 4.18
\]

Los ganadores duran más de cuatro veces que los perdedores.

Esto es consistente con:

```text
muchos fallos pequeños;
pocas tendencias capturadas durante más tiempo.
```

### 9.5 Expectativa y costes

Promedio de acciones por operación:

\[
191{,}228 / 462 \approx 413.91
\]

La expectativa de $53.40 equivale a un margen de coste adicional aproximado de:

\[
53.40 / 413.91 \approx 0.129
\]

dólares por acción por round trip, o unos:

```text
$0.0645 por acción y lado
```

antes de eliminar la expectativa media, además de la comisión ya modelada.

No es una estrategia ultrafrágil en AAPL, pero el slippage omitido no es irrelevante.

---

## 10. ¿Dónde podría estar el edge?

Hipótesis:

> Cuando la SMA conserva pendiente, un retroceso de corto horizonte que no ha destruido el avance de horizonte mayor ofrece una entrada favorable en la dirección de la tendencia.

Mecanismos posibles:

```text
continuidad de tendencia;
liquidación temporal;
take-profit de participantes cortos;
mean reversion local;
entrada después de sobreextensión contraria;
persistencia de momentum intermedio.
```

La estrategia no identifica cuál de ellos es causal.

---

## 11. Auditoría científica

### 11.1 Parámetros parcialmente optimizados

La revista lo reconoce.

### 11.2 Un único activo

AAPL puede ser un caso especialmente favorable.

### 11.3 Diez años no equivalen a OOS

Toda la selección y el informe pertenecen a la misma historia.

### 11.4 Resultado long dominante

La rama short es claramente más débil.

### 11.5 Sin slippage

La ejecución en open de barras intradía tiene spread, gap y latencia.

### 11.6 Corporate actions

AAPL atravesó múltiples splits. Una réplica ingenua puede producir señales o tamaños falsos.

### 11.7 Salida ambigua

La auto-inclusión del mínimo/máximo debe resolverse.

### 11.8 MRO dependiente del estado

La pausa post-exit puede ser una fuente real de mejora o un filtro seleccionado.

### 11.9 Superficie de sensibilidad incompleta

La figura indica que `20/9` fue elegido en una región relativamente estable y no en el máximo. Eso es favorable, pero:

```text
no se conserva el grid;
no se publican todos los inputs;
no hay OOS;
no se corrige multiple testing.
```

### 11.10 Observación MAE de $400

El gráfico sugiere que ningún trade con MAE de al menos $400 terminó ganando.

Eso no valida automáticamente un stop de $400:

```text
es una observación in-sample;
algunos perdedores recuperaron parte de la pérdida;
la introducción del stop cambia la distribución;
la cifra fue descubierta mirando resultados.
```

Debe tratarse como una nueva hipótesis.

---

## 12. Contrato TSIS

### Campos

```text
symbol
bar_end_timestamp
session_id
close
sma_20
sma_20_lag_9
close_lag_9
close_lag_29
uptrend
downtrend
long_pullback
short_pullback
position_before
bars_since_long_exit_event
bars_since_short_exit_event
entry_signal
prior_12_low
prior_12_high
exit_signal
next_bar_open
position_size
corporate_action_state
```

### Estados de indisponibilidad

```text
INSUFFICIENT_HISTORY
SESSION_TEMPLATE_UNRESOLVED
CORPORATE_ACTION_UNRESOLVED
MRO_SEMANTICS_UNRESOLVED
EXIT_SELF_INCLUSION_UNRESOLVED
MISSING_NEXT_BAR_OPEN
```

### Pseudocódigo

```python
ma = sma(adjusted_close, 20)

uptrend = ma[t] > ma[t - 9]
downtrend = ma[t] < ma[t - 9]

long_pullback = close[t] < close[t - 9] and close[t] > close[t - 29]
short_pullback = close[t] > close[t - 9] and close[t] < close[t - 29]

if flat:
    if uptrend and long_pullback and bars_since_short_exit > 9:
        schedule_long(next_bar_open)
    elif downtrend and short_pullback and bars_since_long_exit > 9:
        schedule_short(next_bar_open)

if long:
    if low[t] < min(low[t - 12:t]):
        schedule_exit_long(next_bar_open)

if short:
    if high[t] > max(high[t - 12:t]):
        schedule_exit_short(next_bar_open)
```

---

## 13. Plan de falsificación

### Fase 1 — Réplica

Checksums:

```text
462 trades
248 long
214 short
net ≈ $24,670.62
PF ≈ 1.67
time in market ≈ 47.57%
```

### Fase 2 — Salida

Comparar:

```text
prior 12 bars
current-inclusive equality
Lowest/Highest lagged
```

### Fase 3 — Ablaciones

| Variante | Pregunta |
|---|---|
| sin pendiente SMA | ¿la media aporta información? |
| sin `Close[29]` | ¿el horizonte largo aporta valor? |
| sin MRO | ¿la pausa post-exit mejora? |
| long-only | ¿short destruye robustez? |
| holding fijo | ¿la salida extrema es necesaria? |

### Fase 4 — Cross-sectional

```text
AAPL
MSFT
AMZN
GOOG
META cuando exista
QQQ
SPY
sector ETFs
```

con inputs congelados.

### Fase 5 — Bar alignment

```text
65m regular session
60m
30m
bar offset alternativo
extended hours
```

No para optimizar, sino para medir dependencia de partición.

### Fase 6 — Postpublicación

Desde la primera barra posterior a octubre de 2015.

### Fase 7 — Costes

```text
spread histórico
slippage por acción
open auction vs first print
partial fills
borrow y dividendos short
```

---

## 14. Decisión — Pinpoint Pullback

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
evento pullback dentro de tendencia
con estado post-exit

PRIORIDAD:
media-alta

SIGUIENTE GATE:
SCC-019-EXIT-MRO-AND-POSTPUBLICATION-GATE
```

---

# Parte II — Estrategia 020: Engulfing Candles

## 15) Identificación

- **ID:** `SCC-2015-10-STRAT-020`
- **Artículo:** *The Engulfing Candles Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas:** 10–15
- **Estilo declarado:** bar pattern
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** swing trading
- **Activo del test:** GBPUSD
- **Intervalo:** 120 minutos
- **Periodo:** 5 años terminando el 30 de junio de 2015
- **Tamaño:** £100,000
- **Comisión:** $2.50 por lado
- **LIBBT:** 12 minutos
- **Slippage:** no indicado

### Configuración publicada y confirmada

```text
AvgBodyLength = 3
ATR_Length = 5
ProfitTgt_ATRFactor = 2.2
Stop_ATRFactor = 4.8
BarToExitOn long = 32
BarToExitOn short = 13
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Es el engulfing clásico? | **No exactamente.** Elimina el requisito de tendencia y añade filtro de tamaño de cuerpos. |
| ¿Puede implementarse? | **Sí.** |
| ¿Puede replicarse exactamente? | **No todavía.** Falta semántica exacta de EMA corporal, ATR, fills y prioridad de órdenes. |
| ¿La estrategia está contenida en un solo `.ELD`? | **No.** El resultado depende también de dos TimeExit y del motor de ejecución. |
| ¿El resultado es atractivo? | **Moderado.** PF 1.44 con 590 trades. |
| ¿Está científicamente validada? | **No.** Optimización por etapas en la misma muestra. |
| ¿Es vulnerable a la construcción de barras? | **Mucho.** En forex, zona horaria y session boundary alteran cada candle. |
| ¿Merece estudiarse? | **Sí**, como laboratorio de patrones, órdenes stop e intrabar. |

Clasificación:

```text
BAR_PATTERN_REPRODUCTION_CANDIDATE
COMPOSITE_STRATEGY
INTRABAR_EXECUTION_REQUIRED
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 16. Qué patrón utiliza realmente

El patrón sólo exige que el **cuerpo real** actual envuelva el cuerpo real anterior.

No exige que:

```text
el high actual supere el high anterior;
el low actual sea inferior al low anterior;
exista tendencia previa;
exista gap;
la mecha sea engullida.
```

Además añade:

```text
cuerpo actual mayor que su promedio reciente;
cuerpo anterior menor que el promedio reciente.
```

Por tanto, no es simplemente “bullish engulfing” o “bearish engulfing” tradicional. Es:

> un cambio brusco desde un cuerpo pequeño de signo contrario hacia un cuerpo grande que lo envuelve.

---

## 17. Reconstrucción del cuerpo y promedio

Sea:

\[
Body_t = |Close_t - Open_t|
\]

La revista dice que se usa un promedio exponencial con `AvgBodyLength`.

Reconstrucción:

\[
AvgBody_t = EMA_n(Body)_t
\]

con `n = 3` en el test.

Queda sin resolver:

```text
si Body_t se compara con AvgBody_t incluyendo Body_t;
si se compara con AvgBody_t-1;
si Body_t-1 se compara con la misma media o con una media lagged;
cómo se inicializa la EMA.
```

Estas variantes cambian el conjunto de patrones.

---

## 18. Patrón bullish

Condiciones publicadas:

1. `Close_t > Open_t`.
2. `Body_t` supera el promedio reciente.
3. `Close_{t-1} < Open_{t-1}`.
4. `Body_{t-1}` es menor que el promedio reciente.
5. `Open_t <= Close_{t-1}`.
6. `Close_t >= Open_{t-1}`.
7. Al menos una de las dos desigualdades de engulfing es estricta.

Formalmente:

\[
C_t > O_t
\]

\[
B_t > A_t
\]

\[
C_{t-1} < O_{t-1}
\]

\[
B_{t-1} < A^\*_{t}
\]

\[
O_t \le C_{t-1}
\]

\[
C_t \ge O_{t-1}
\]

\[
(O_t < C_{t-1}) \lor (C_t > O_{t-1})
\]

`A_t` y `A*_t` deben reconciliarse.

---

## 19. Patrón bearish

Condiciones espejo:

\[
C_t < O_t
\]

\[
B_t > A_t
\]

\[
C_{t-1} > O_{t-1}
\]

\[
B_{t-1} < A^\*_{t}
\]

\[
O_t \ge C_{t-1}
\]

\[
C_t \le O_{t-1}
\]

\[
(O_t > C_{t-1}) \lor (C_t < O_{t-1})
\]

La redacción del punto 7 del artículo contiene una referencia verbal confusa al “preceding bear candle” también en el bloque bearish. La lógica espejo y el gráfico indican que debe referirse al bull candle precedente.

---

## 20. Entrada stop

### Long

\[
entry\_stop_t =
\max(High_t, High_{t-1}) + MinTick
\]

La orden sólo es válida en `t+1`.

### Short

\[
entry\_stop_t =
\min(Low_t, Low_{t-1}) - MinTick
\]

También expira al terminar `t+1`.

Esto evita entrar sólo por detectar el patrón. Exige confirmación por ruptura del extremo de las dos candles.

---

## 21. Bracket ATR

Con `ATR_Length = 5`:

\[
ATR_t = ATR_5
\]

En el test:

\[
profit\_distance = 2.2 \times ATR
\]

\[
stop\_distance = 4.8 \times ATR
\]

Ratio nominal:

\[
2.2 / 4.8 \approx 0.4583
\]

La estrategia arriesga más distancia de la que busca ganar.

Eso exige una tasa de acierto elevada o pérdidas medias recortadas por time exits.

Queda por resolver:

```text
ATR de signal bar vs entry bar;
ATR congelado al fill vs recalculado;
precio base exacto;
tratamiento de gaps;
redondeo a pip/tick;
orden de activación del bracket.
```

---

## 22. Time exits asimétricos

El artículo presenta defaults de 5 barras, pero el backtest publicado utiliza:

```text
long exit:
BarToExitOn = 32

short exit:
BarToExitOn = 13
```

El input especifica que:

```text
la barra de entrada y la barra de salida no se incluyen en el conteo.
```

Por tanto, la permanencia efectiva no se deduce sumando simplemente 32 o 13 al índice de entrada sin reproducir la semántica TradeStation.

La fuerte asimetría long/short es parte de la estrategia seleccionada, no un detalle accesorio.

---

## 23. Composición de la estrategia

El resultado publicado requiere simultáneamente:

```text
TSL:Engulfing Candles
TimeExit (Bars) LX
TimeExit (Bars) SX
```

El indicador ATR Bands sólo visualiza.

Una réplica que implemente únicamente el `.ELD` principal no reproducirá el informe.

TSIS debe modelar:

```text
signal component
entry order component
ATR exit component
long time-exit component
short time-exit component
order arbitration
```

---

## 24. Conflictos intrabar

En una barra de 120 minutos pueden tocarse:

```text
entry stop;
profit target;
stop loss;
opposite entry;
time exit.
```

LIBBT de 12 minutos mejora la precisión, pero no resuelve el orden dentro de cada subbarra de 12 minutos.

Si una subbarra toca target y stop:

```text
el resultado depende de la convención del motor;
no existe una secuencia única a partir de OHLC de 12m.
```

TSIS debe usar:

```text
datos de 1 minuto o trades;
política adversarial;
o marcar la operación como intrabar ambiguous.
```

---

## 25. Dependencia de la zona horaria

En forex no existe una vela universal de 120 minutos.

Cambiar:

```text
session anchor;
timezone;
DST;
week start;
Sunday bar;
roll diario;
```

cambia:

```text
open;
close;
real body;
engulfing pattern;
ATR;
entry stop;
resultado.
```

Una estrategia de candles debe declarar la construcción de barras como parte de la hipótesis.

---

## 26. Resultados publicados

### Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $55,147.90 |
| Beneficio bruto | $181,720.60 |
| Pérdida bruta | -$126,572.70 |
| Profit Factor | 1.44 |
| Operaciones | 590 |
| Ganadoras | 385 |
| Perdedoras | 205 |
| Percent Profitable | 65.25% |
| Expectativa media | $93.47 |
| Ganancia media | $472.00 |
| Pérdida media | -$617.43 |
| Ratio ganancia/pérdida | 0.76 |
| Mayor ganancia | $1,550.50 |
| Mayor pérdida | -$2,888.00 |
| Máx. ganadoras consecutivas | 19 |
| Máx. perdedoras consecutivas | 7 |
| Barras medias ganadoras | 8.82 |
| Barras medias perdedoras | 11.93 |
| Percent of Time in Market | 32.74% |

### Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $21,925.40 | $33,222.50 |
| Profit Factor | 1.29 | 1.65 |
| Operaciones | 299 | 291 |
| Percent Profitable | 64.21% | 66.32% |
| Expectativa media | $73.33 | $114.17 |
| Ganancia media | $506.57 | $437.61 |
| Pérdida media | -$704.08 | -$522.81 |
| Ratio ganancia/pérdida | 0.72 | 0.84 |
| Barras medias ganadoras | 10.28 | 7.36 |
| Barras medias perdedoras | 13.60 | 10.10 |

### Concentración short

\[
33{,}222.50 / 55{,}147.90 \approx 60.24\%
\]

A diferencia de muchas estrategias del club, aquí el lado short es superior.

### Win rate de equilibrio observado

Con ratio medio:

\[
R = 472 / 617.43 \approx 0.764
\]

La tasa de acierto de equilibrio es:

\[
p^\* =
\frac{617.43}{617.43 + 472}
\approx 56.68\%
\]

El 65.25% publicado supera ese umbral, pero la estrategia depende materialmente de conservar una tasa de acierto alta.

---

## 27. Fragilidad a costes en forex

Una operación de £100,000 en GBPUSD tiene un valor aproximado de $10 por pip.

Si se añade un coste no modelado de un pip por round trip:

\[
590 \times 10 = 5{,}900
\]

Eso reduciría el beneficio publicado aproximadamente un:

\[
5{,}900 / 55{,}147.90 \approx 10.70\%
\]

Dos pips por round trip reducirían cerca del 21%.

La comisión publicada ya está incluida, pero no se publica slippage ni spread variable.

---

## 28. Rachas

La tabla de series muestra:

```text
31 rachas ganadoras de 4 o más trades;
6 rachas perdedoras de 4 o más;
una racha ganadora de 19;
una racha perdedora de 7.
```

Las rachas son descriptivas, no evidencia de independencia.

Los trades pueden compartir:

```text
regímenes;
sesiones;
volatilidad;
señales solapadas;
parámetros comunes.
```

---

## 29. Auditoría científica

### 29.1 Eliminación del filtro de tendencia

El patrón deja de ser la definición clásica de reversión en tendencia.

Debe compararse:

```text
aggressive no-trend version
versus
engulfing con trend context.
```

### 29.2 Optimización por etapas

Primero:

```text
AvgBodyLength
ATR_Length
ProfitTgt_ATRFactor
Stop_ATRFactor
```

Luego:

```text
TimeExit long
TimeExit short
```

Todo sobre la misma muestra.

### 29.3 Valores muy específicos

```text
3
5
2.2
4.8
32
13
```

La precisión sugiere selección detallada.

### 29.4 Sin OOS

No hay validación separada.

### 29.5 Un único par

No se publican resultados comparables en otros cruces.

### 29.6 Dependencia de bar construction

Un cambio horario puede destruir el patrón.

### 29.7 LIBBT no resuelve la secuencia completa

12 minutos siguen siendo una agregación.

### 29.8 Sin slippage

Especialmente importante en stop entries y brackets.

### 29.9 Payoff nominal adverso

Stop 4.8 ATR frente a target 2.2 ATR.

### 29.10 Time exits descubiertos in-sample

Pueden recortar pérdidas históricas específicas.

### 29.11 Reversals

El artículo indica que puede haber reversión de posición, pero no documenta toda la prioridad entre señal opuesta, bracket y time exit.

---

## 30. Contrato TSIS

### Datos

```text
GBPUSD 120m canonical bars
GBPUSD 12m or finer replay
bid/ask
session and timezone
minimum tick/pip
```

### Campos

```text
bar_open
bar_high
bar_low
bar_close
real_body
ema_real_body
prior_real_body
bullish_engulfing
bearish_engulfing
entry_stop
entry_expiration
atr_5
profit_target
stop_level
bars_held
long_time_exit_due
short_time_exit_due
intrabar_path_status
```

### Pseudocódigo

```python
body = abs(close - open)
body_avg = ema(body, 3)

bullish = (
    close[t] > open[t]
    and body[t] > body_avg_reference
    and close[t - 1] < open[t - 1]
    and body[t - 1] < prior_body_avg_reference
    and open[t] <= close[t - 1]
    and close[t] >= open[t - 1]
    and (
        open[t] < close[t - 1]
        or close[t] > open[t - 1]
    )
)

if bullish:
    buy_stop = max(high[t], high[t - 1]) + min_tick
    valid_only_on_bar(t + 1)
```

---

## 31. Plan de falsificación

### Fase 1 — Réplica

```text
590 trades
299 long
291 short
PF ≈ 1.44
win rate ≈ 65.25%
```

### Fase 2 — Reconciliación de patrón

```text
EMA inclusive
EMA lagged
average simple
body average excluyendo las dos candles del patrón
```

### Fase 3 — Ablaciones

| Variante | Pregunta |
|---|---|
| sin body-size filter | ¿el filtro de tamaño aporta valor? |
| con filtro de tendencia | ¿la definición clásica mejora? |
| entry market next open | ¿la ruptura stop es necesaria? |
| PT/SL simétrico | ¿2.2/4.8 está sobreseleccionado? |
| sin time exits | ¿aportan valor real? |
| mismo time exit long/short | ¿la asimetría es robusta? |

### Fase 4 — Sesiones

```text
New York close
UTC
London session
offsets de 30/60 minutos
```

### Fase 5 — Mercados

```text
EURUSD
USDJPY
AUDUSD
GBPUSD
futuros
ETFs
```

### Fase 6 — Intrabar

Reproducir con 1m o ticks y clasificar conflictos.

### Fase 7 — Postpublicación

Desde octubre de 2015 con parámetros congelados.

### Fase 8 — Multiple testing

DSR, PBO/CSCV y block bootstrap si se explora el espacio.

---

## 32. Decisión — Engulfing Candles

```text
IMPLEMENTAR:
sí, como benchmark de patrones e intrabar

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
contrato de candle pattern
+
entry stop
+
bracket
+
time exits compuestos

PRIORIDAD:
alta para engine validation

SIGUIENTE GATE:
SCC-020-BAR-CONSTRUCTION-INTRABAR-AND-OOS-GATE
```

---

# Parte III — Estrategia 021: Williams E-mini Influx

## 33) Identificación

- **ID:** `SCC-2015-10-STRAT-021`
- **Artículo bonus:** *Williams E-mini Influx Strategy*
- **Autor de la estrategia:** Larry Williams
- **Documentación:** Michael Burke
- **Páginas físicas:** 17–22
- **Estilo declarado:** cycles
- **Mercados declarados:** stock-index futures y ETFs
- **Horizonte:** swing trading
- **Dirección:** long-only
- **Activo:** ES
- **Símbolo del test:** `@ES=107XN`
- **Intervalo:** diario
- **Periodo:** 11 de septiembre de 1997 a 1 de septiembre de 2015
- **Tamaño:** 1 contrato
- **Comisión:** $2.36 por lado
- **Slippage:** $2.50 por lado

### Inputs

```text
PctRVal = 85
PctRLen = 8
StopLossPct = 2.5
HoldDays = 1
DaysLeftToPaint = 19
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿La hipótesis económica es explícita? | **Sí:** flujos hacia fondos al inicio de mes. |
| ¿La estrategia mide esos flujos? | **No.** Usa calendario y precio como proxy. |
| ¿Puede implementarse? | **Sí, pero no con los fills descritos sin definir una política causal.** |
| ¿Tiene muestra larga? | **Sí, casi 18 años.** |
| ¿Tiene muchas operaciones? | **No, 115.** |
| ¿El resultado depende de una tasa de acierto elevada? | **Mucho.** |
| ¿La entrada “limit al próximo open” es operable tal como está escrita? | **No queda demostrado.** El próximo open no se conoce antes de producirse. |
| ¿La salida al primer cierre rentable es causal? | **No si la condición utiliza ese mismo cierre y se asigna fill en él.** |
| ¿Está validada? | **No.** La ejecución y los baselines deben rehacerse. |

Clasificación:

```text
CALENDAR_EVENT_STRATEGY
LONG_ONLY_SEASONAL_CANDIDATE
EXECUTION_CONTRACT_UNRESOLVED
BACKTEST_ONLY_CLOSE_FILL_RISK
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 34. Tesis económica

La tesis declarada es:

> A comienzos de mes entran aportaciones en fondos, los gestores compran acciones y esa demanda puede favorecer un rally corto.

La estrategia no observa:

```text
suscripciones de fondos;
flujos ETF;
órdenes institucionales;
balances de fondos;
settlement de nóminas.
```

Observa únicamente:

```text
posición en el calendario;
dirección de la última barra;
Williams %R;
día de la semana.
```

Por tanto, el mecanismo económico es plausible, pero la estrategia sólo lo representa mediante proxies.

---

## 35. Ventana mensual

La estrategia evalúa señales mientras queden al menos 19 trading days en el mes.

Formalmente:

\[
days\_remaining_t \ge 19
\]

Queda por resolver:

```text
si se incluye el día actual;
cómo se cuentan feriados;
cómo se tratan half-days;
qué calendario usa TradeStation;
cómo se etiqueta la barra nocturna de ES.
```

Sólo se permite una operación por mes.

---

## 36. Filtros de entrada

### 36.1 Up day

\[
Close_t > Close_{t-1}
\]

### 36.2 Williams %R

\[
PctR_t < 85
\]

con longitud 8.

La fórmula y escala exactas deben ser las de TradeStation. El gráfico usa una escala 0–100 donde 85 actúa como zona sobrecomprada.

No debe sustituirse silenciosamente por una implementación convencional `-100..0`.

### 36.3 Día de semana

La signal bar no puede ser jueves.

Motivo del artículo:

```text
una señal del jueves produciría entrada
en la barra diaria del viernes,
cuya sesión ES comienza el jueves a las 18:00 ET.
```

Esta regla depende de cómo se fecha la barra diaria.

### 36.4 Una operación por mes

Una entrada ejecutada bloquea nuevas entradas hasta el mes siguiente.

---

## 37. Regla de entrada y problema del próximo open

La revista dice:

```text
cuando se cumplen las condiciones,
se coloca una buy limit en la barra siguiente
a un precio igual o mejor que el open de esa barra.
```

Problema:

> El open de la barra siguiente no es conocido en el momento de emitir la orden desde la signal bar.

Posibilidades:

```text
A. el código usa el open de la signal bar como límite;
B. TradeStation crea una orden evaluada al abrir la barra;
C. el backtest asigna un fill ideal al próximo open;
D. se trata de una formulación equivalente a market-on-open;
E. existe una semántica propietaria no visible en el .ELD.
```

No debe aceptarse un fill al próximo open hasta reconstruir la orden.

Variantes causalmente implementables:

```text
market-on-open enviado antes del cierre previo;
limit fijado con información de la signal bar;
market a las 18:00 ET;
limit con offset preregistrado.
```

---

## 38. Salida al primer cierre rentable

Después de al menos `HoldDays = 1`:

```text
cerrar en el primer daily close
en que la posición sea rentable.
```

El artículo explica que las reglas se separaron en dos componentes para poder salir al cierre en el backtest.

Esto introduce una dificultad causal grave.

Para saber si el cierre es rentable hace falta conocer el cierre. Si la decisión se toma con ese cierre y se asigna fill exactamente en él:

```text
la decisión y el precio de ejecución comparten timestamp;
no hay tiempo para enviar una orden real;
el fill es backtest-only salvo que se aproxime con MOC antes del cutoff.
```

Una implementación realista debe elegir:

```text
A. enviar MOC antes del cutoff usando información anterior;
B. salir en la siguiente apertura;
C. salir pocos minutos antes del cierre;
D. usar un limit intradía definido de antemano;
E. aceptar tracking error entre close observado y fill.
```

Éste es probablemente el principal riesgo de validez del resultado publicado.

---

## 39. Stop loss

El stop es el 2.5% del valor del contrato.

Con multiplicador ES `BPV`:

\[
stop\_dollars =
0.025 \times EntryPrice \times BPV
\]

Distancia en puntos:

\[
stop\_points =
\frac{stop\_dollars}{BPV}
=
0.025 \times EntryPrice
\]

Por tanto, aproximadamente:

\[
StopPrice = EntryPrice \times 0.975
\]

La revista también menciona que se calcula desde el cierre de la barra. Esa redacción debe reconciliarse con el código:

```text
entry price;
entry-bar close;
signal-bar close;
contract value dinámico.
```

El stop está activo desde la barra de entrada.

---

## 40. Reglas funcionales

```text
if flat
and no trade yet this month
and trading_days_remaining >= 19
and Close_t > Close_t-1
and WilliamsR_8_t < 85
and weekday(signal_bar) != Thursday:
    schedule long entry next session
```

Salida:

```text
if long:
    if protective_stop_hit:
        exit at stop
    elif bars_held >= 1 and current_close is profitable:
        exit at close
```

La regla funcional debe reescribirse con fills causalmente ejecutables antes de usarla en TSIS.

---

## 41. Resultados publicados

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $23,394.70 |
| Beneficio bruto | $58,818.26 |
| Pérdida bruta | -$35,423.56 |
| Profit Factor | 1.66 |
| Operaciones | 115 |
| Ganadoras | 92 |
| Perdedoras | 23 |
| Percent Profitable | 80.00% |
| Expectativa media | $203.43 |
| Ganancia media | $639.33 |
| Pérdida media | -$1,540.15 |
| Ratio ganancia/pérdida | 0.42 |
| Mayor ganancia | $2,427.78 |
| Mayor pérdida | -$2,122.22 |
| Máx. ganadoras consecutivas | 26 |
| Máx. perdedoras consecutivas | 3 |
| Barras medias ganadoras | 2.62 |
| Barras medias perdedoras | 2.52 |
| Percent of Time in Market | 3.72% |

### Frecuencia

Periodo aproximado:

```text
casi 18 años
```

\[
115 / 18 \approx 6.4
\]

operaciones por año.

---

## 42. Dependencia de la tasa de acierto

Con ganancia media `W = 639.33` y pérdida media `L = 1540.15`:

\[
p^\* =
\frac{L}{W+L}
=
\frac{1540.15}{639.33 + 1540.15}
\approx 70.67\%
\]

La tasa publicada es 80%.

Margen:

```text
aproximadamente 9.3 puntos porcentuales
```

Una degradación relativamente pequeña en la win rate puede eliminar la expectativa.

Comprobación:

\[
0.8(639.33)-0.2(1540.15)=203.43
\]

La estrategia es una familia clásica:

```text
muchas ganancias pequeñas;
pocas pérdidas grandes.
```

---

## 43. Costes

El backtest incluye por round trip:

```text
comisión:
$4.72

slippage:
$5.00

total explícito:
$9.72
```

Un tick adicional de ES por round trip:

\[
115 \times 12.50 = 1{,}437.50
\]

Reduciría el beneficio neto aproximadamente:

\[
1{,}437.50 / 23{,}394.70 \approx 6.15\%
\]

La estrategia tiene margen frente a costes moderados, pero el problema más importante no es el coste: es la causalidad del precio de salida al close.

---

## 44. Rachas

El informe muestra:

```text
racha ganadora máxima = 26
racha perdedora máxima = 3
```

La tabla registra una sola racha de tres pérdidas.

El artículo afirma que esa racha explicó el mayor drawdown.

Debe recordarse:

```text
115 trades son pocos;
una racha de 4–6 pérdidas es perfectamente posible fuera de muestra;
cada pérdida media es más de dos veces la ganancia media;
el drawdown futuro puede superar ampliamente el observado.
```

---

## 45. ¿Dónde podría estar el edge?

Hipótesis principal:

> La presión compradora al comienzo del mes favorece un retorno positivo de corta duración en ES.

Filtros adicionales:

```text
up day:
evita comprar contra momentum inmediato

%R < 85:
evita comprar sobrecompra

no Thursday:
evita entrada de viernes

one trade/month:
evita sobreexposición a la misma ventana
```

No se demuestra qué capa aporta valor.

---

## 46. Auditoría científica

### 46.1 Historia larga, muestra pequeña

17+ años suena amplio, pero sólo hay 115 trades.

### 46.2 Equity risk premium

Es long-only sobre ES.

### 46.3 Calendar selection

Debe compararse contra otros días del mes.

### 46.4 Mecanismo no observado

No se usan datos de fund flows.

### 46.5 Próximo open desconocido

La regla limit necesita reconstrucción.

### 46.6 Same-close exit

Puede constituir look-ahead operativo.

### 46.7 Continuous contract

No es operable y debe mapearse a contratos físicos.

### 46.8 Stop porcentual grande

Permite pérdidas amplias para conservar una win rate alta.

### 46.9 No OOS de publicación

El test termina prácticamente al publicarse.

### 46.10 Modificaciones históricas

Larry Williams indica que la idea recibió pequeñas modificaciones a lo largo del tiempo. No se publica el historial de versiones ni la fecha de congelación de cada regla.

### 46.11 Falta de ablaciones

No se muestran:

```text
calendar-only;
sin %R;
sin up-day;
sin Thursday filter;
sin one-trade limit;
distintos HoldDays.
```

---

## 47. Contrato TSIS

### Datos

```text
ES physical daily sessions
exchange trading calendar
trading days remaining
Williams %R platform-compatible
day-of-week under ES session labels
contract mapping
open and close executable prices
MOC cutoff model
```

### Campos

```text
calendar_month
session_date
trading_days_remaining_in_month
is_thursday_signal
close
prior_close
williams_r_8
trade_already_taken_month
entry_eligible
entry_order_type
entry_limit
entry_open
entry_price
bars_held
current_close
unrealized_pnl_at_close
profitable_close
stop_price
exit_order_type
execution_causality_status
```

### Estados de indisponibilidad

```text
CALENDAR_COUNT_UNRESOLVED
SESSION_DATE_UNRESOLVED
WILLIAMS_R_SEMANTICS_UNRESOLVED
NEXT_OPEN_LIMIT_NONCAUSAL
SAME_CLOSE_EXIT_NONCAUSAL
PHYSICAL_CONTRACT_UNRESOLVED
```

---

## 48. Pseudocódigo causal de investigación

```python
eligible = (
    flat
    and not traded_this_month
    and trading_days_remaining >= 19
    and close[t] > close[t - 1]
    and williams_r_8[t] < 85
    and weekday_of_signal_session[t] != THURSDAY
)

if eligible:
    # Causal variant, not assumed identical to publication
    submit_market_on_open_for_next_session()

if long:
    stop_price = entry_price * (1.0 - 0.025)

    if low[t] <= stop_price:
        exit_at_stop_model()

    elif bars_held >= 1 and close[t] > break_even_price:
        # Realistic alternatives must be tested separately
        schedule_exit_next_open()
        # or use a pre-close/MOC approximation
```

---

## 49. Plan de falsificación

### Fase 1 — Réplica documental

Checksums:

```text
115 trades
92 winners
23 losers
PF ≈ 1.66
net ≈ $23,394.70
```

### Fase 2 — Ejecución

Comparar:

```text
published close fill
next open exit
MOC proxy 5/10/15 minutes before close
predefined intraday limit at breakeven
```

### Fase 3 — Entrada

Comparar:

```text
market next open
limit at signal close
limit at signal open
published next-open interpretation
```

### Fase 4 — Ablaciones

| Variante | Pregunta |
|---|---|
| early-month only | ¿existe efecto calendario base? |
| + up-day | ¿aporta momentum? |
| + %R | ¿evita entradas malas? |
| + Thursday exclusion | ¿tiene valor? |
| + one trade/month | ¿evita duplicación? |

### Fase 5 — Placebos de calendario

```text
mismas reglas a mitad de mes
últimos 5 trading days
días aleatorios con igual frecuencia
primer Monday
primer Friday
```

### Fase 6 — Fund flow evidence

Si TSIS incorpora datos externos:

```text
mutual fund flows
ETF flows
pension contributions
payroll calendar
```

### Fase 7 — Postpublicación

Octubre de 2015 en adelante, parámetros congelados.

### Fase 8 — Contratos físicos

Roll real, slippage y posición atravesando rollover.

### Fase 9 — Stress de win rate

Simular:

```text
75%
72%
70%
65%
```

con distribución de pérdidas ampliada.

---

## 50. Decisión — Williams E-mini Influx

```text
IMPLEMENTAR:
sí, como evento de calendario

REPLICAR EL FILL PUBLICADO COMO REALISTA:
no

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
hipótesis de flujo mensual
y test de causalidad de ejecución

PRIORIDAD:
alta

SIGUIENTE GATE:
SCC-021-CALENDAR-EXECUTION-CAUSALITY-GATE
```

---

# Parte IV — Ideas transversales del Issue 10

## 51. El nombre temporal de un input puede ser engañoso

“20-day moving average” en una serie 65m es una SMA de 20 barras.

TSIS debe expresar siempre:

```text
length = 20
bar_interval = 65m
effective_time_span = variable según sesión
```

---

## 52. Un desplazamiento gráfico no es dato futuro

`Displace = -9` mueve el plot hacia la derecha.

La estrategia debe calcular:

```text
MA_t vs MA_t-9
```

No debe leer un valor visual desplazado como si estuviera disponible antes.

---

## 53. Lowest/Highest exige política de auto-inclusión

Dos estrategias del issue usan lenguaje que sería imposible con comparación estricta e inclusión de la barra actual.

Debe existir un helper contractual:

```text
prior_window_low(length)
prior_window_high(length)
```

---

## 54. La construcción de candles es parte de la estrategia

Especialmente en forex:

```text
timezone
session boundary
DST
bar offset
```

son parámetros científicos.

---

## 55. Los componentes externos forman parte del modelo

Engulfing Candles depende de:

```text
estrategia principal
TimeExit LX
TimeExit SX
ATR bracket
motor de órdenes
```

No debe versionarse sólo el generador de señales.

---

## 56. LIBBT no elimina toda ambigüedad

120m → 12m reduce incertidumbre, pero no determina la secuencia dentro de 12m.

---

## 57. La precisión de parámetros revela selección

Engulfing usa:

```text
2.2 ATR
4.8 ATR
32 barras
13 barras
```

Los decimales y asimetrías requieren OOS y corrección de selección.

---

## 58. Alta win rate puede esconder payoff adverso

Engulfing:

```text
win rate 65.25%
avg win/loss 0.76
```

Influx:

```text
win rate 80%
avg win/loss 0.42
```

El win rate nunca debe analizarse solo.

---

## 59. Same-close fills requieren causalidad explícita

La condición:

```text
“si el close es rentable, salir en ese close”
```

no es directamente operable sin una regla previa al cierre.

---

## 60. El calendario necesita un objeto de información

Para Influx se necesita:

```text
trading_days_remaining
first_trading_day
session_weekday
month_trade_count
holiday state
half-day state
```

No basta con `day_of_month`.

---

## 61. El mecanismo económico debe separarse del proxy

“Fund inflows” es la tesis.

“Early month + up day + %R” es la representación.

TSIS debe comparar ambos cuando existan datos.

---

## 62. Las observaciones de MAE generan hipótesis nuevas

El corte de $400 de Pinpoint no forma parte de la estrategia original.

Debe preregistrarse antes de testarlo.

---

## 63. Ideas secundarias de backtesting del número

1. Estudiar regiones estables de parámetros.
2. Analizar MAE para generar reglas de riesgo.
3. Separar patrón de entrada, confirmación y gestión.
4. Usar time exits para medir vida útil de señales.
5. Modelar long y short de forma asimétrica.
6. Tratar el session template como parámetro.
7. Revisar la causalidad de MOC y same-close.
8. Comparar historia económica con baselines simples.
9. Conservar todos los grids y no sólo el resultado.
10. Versionar la composición completa del workspace.

---

# Parte V — Registro consolidado para TSIS

## 64. Eventos candidatos

### Pinpoint

```text
event_type:
pullback_inside_rising_average

attributes:
ma_slope_9
return_9
return_29
bars_since_opposite_exit
```

```text
event_type:
pullback_inside_falling_average
```

```text
event_type:
prior_window_extreme_break_exit
```

### Engulfing

```text
event_type:
large_body_bullish_engulfing

attributes:
body_ratio_to_ema
engulf_amount
prior_body_ratio
entry_break_level
```

```text
event_type:
large_body_bearish_engulfing
```

### Influx

```text
event_type:
early_month_inflow_proxy

attributes:
trading_days_remaining
up_day
williams_r
weekday
trade_already_taken
```

---

## 65. Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Williams Influx causal replay | puede invalidarse por ejecución same-close |
| 2 | Engulfing intrabar replay | prueba directa del motor de stop/target/conflictos |
| 3 | Pinpoint postpublicación | reglas simples y 462 trades históricos |
| 4 | Engulfing session sensitivity | patrón depende de bar construction |
| 5 | Influx fund-flow attribution | prueba del mecanismo económico |

---

## 66. Gates propuestos

### SCC-019-A — Timeframe Contract

Debe demostrar que todos los inputs son barras de 65m, no días.

### SCC-019-B — Exit and MRO Semantics

Debe resolver prior-window y MRO.

### SCC-019-C — Corporate Action Replay

Debe reconciliar AAPL adjusted/raw y sizing.

### SCC-019-D — Postpublication OOS

Inputs congelados `20/9/12/9`.

### SCC-020-A — Candle Construction

Debe congelar timezone y session anchor.

### SCC-020-B — Pattern Formula

Debe resolver promedio de cuerpos.

### SCC-020-C — Intrabar Arbitration

Debe resolver entry/PT/SL/time/reversal.

### SCC-020-D — Staged Optimization Audit

Debe registrar todos los grids nuevos.

### SCC-020-E — Postpublication OOS

Configuración `3/5/2.2/4.8/32/13`.

### SCC-021-A — Trading Calendar

Debe resolver días restantes y weekday de ES.

### SCC-021-B — Entry Causality

Debe definir un precio de limit conocido al emitir la orden.

### SCC-021-C — Exit Causality

Debe sustituir o modelar el same-close fill.

### SCC-021-D — Physical Futures Replay

Debe ejecutar contratos reales.

### SCC-021-E — Calendar Placebo

Debe superar fechas placebo.

### SCC-021-F — Postpublication OOS

Configuración `85/8/2.5/1/19`.

---

# Conclusión

El Issue 10 contiene **tres** estrategias, no sólo las dos de portada.

## Pinpoint Pullback

Es una idea coherente:

```text
pendiente SMA
+
pullback de 9 barras
+
continuidad frente a 29 barras
+
pausa post-exit
```

El resultado es interesante, pero:

```text
los inputs están optimizados parcialmente;
el artículo confunde días y barras;
la salida Lowest/Highest es ambigua;
no hay slippage;
AAPL exige corporate-action discipline;
74% del beneficio es long.
```

## Engulfing Candles

La estrategia no es el engulfing clásico. Es:

```text
engulfing de cuerpo
+
filtro de tamaño
+
entry stop de confirmación
+
PT 2.2 ATR
+
SL 4.8 ATR
+
time exit long 32
+
time exit short 13
```

Su mayor valor para TSIS es como prueba de:

```text
bar construction;
órdenes intrabar;
estrategias compuestas;
prioridad de exits.
```

No debe aceptarse el PF 1.44 sin OOS, slippage y replay más fino.

## Williams E-mini Influx

La tesis de flujos a comienzos de mes es plausible y el periodo es largo. Sin embargo, el resultado publicado depende de dos reglas de ejecución que no están causalmente resueltas:

```text
limit al próximo open;
salida en el mismo close que confirma rentabilidad.
```

Antes de discutir edge debe reformularse la ejecución.

## Estado final

```text
ISSUE_10_STATUS:
DOCUMENTALLY_CLOSED

PACKAGE_INSPECTION:
COMPLETE_WITH_PROPRIETARY_CODE_LIMITATION

STRATEGIES_EXTRACTED:
3

REPRODUCTION_CANDIDATES:
3

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguiente prioridad recomendada:

```text
1. SCC-021-CALENDAR-EXECUTION-CAUSALITY-GATE
2. SCC-020-BAR-CONSTRUCTION-INTRABAR-AND-OOS-GATE
3. SCC-019-EXIT-MRO-AND-POSTPUBLICATION-GATE
```
