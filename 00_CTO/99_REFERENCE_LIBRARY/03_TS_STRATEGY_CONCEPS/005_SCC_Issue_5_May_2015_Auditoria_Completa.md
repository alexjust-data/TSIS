# Auditoría completa — TradeStation Strategy Concepts Club, Issue 5 (mayo de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. MACD Difference Turn Strategy
2. Directional Movement Index Strategy
3. ideas secundarias de backtesting presentes en el issue
4. auditoría temporal, matemática y metodológica
5. evidencia adicional contenida en los workspaces y .ELD
6. forense del grid de sensibilidad conservado en el workspace DMI
7. contratos de réplica para TSIS
8. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 15 páginas: `SCC Issue 5 May 2015.pdf`
- Archivo original de apoyo: `2015-05.7z`
- PDF duplicado incluido dentro del archivo comprimido
- Tres contenedores `.ELD`:
  - `TSL MACD DIFFERENCE TURN.ELD`
  - `TSL MACD DIFFERENCE_INDICATOR UPDATE.ELD`
  - `TSL DIRECTIONAL MOVEMENT INDEX.ELD`
- Dos workspaces `.tsw`:
  - `TSL.MACD Difference Turn.tsw`
  - `TSL Directional Movement Index.tsw`
- Imágenes renderizadas de las 15 páginas, incluidas:
  - los ejemplos de MACD de las páginas físicas 5–6;
  - la tabla comparativa y las dos curvas de capital de las páginas físicas 7–8;
  - el ejemplo de generación de órdenes DMI de las páginas físicas 11–12;
  - el informe de rendimiento DMI de la página física 13;
  - los tres gráficos de sensibilidad de la página física 14.
- Los Markdown de los Issues 1–4 se utilizan únicamente como **modelo de profundidad y organización**, nunca como autoridad factual para este número.

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

No se ha incorporado investigación web externa sobre las estrategias. Las fórmulas reconstruidas que no aparecen literalmente en el PDF se marcan como reconstrucciones o candidatos de implementación.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 009 | MACD Difference Turn | Reversal always-in sobre nuevos extremos del histograma MACD; EURUSD 120 minutos | frente al MACD convencional: $20,877.60 vs. -$8,297.70; PF 1.22 vs. 0.92; 491 trades | el workspace confirma la comparación, los inputs `12/26/9/8` y la ausencia de un informe de optimización; no contiene source EasyLanguage legible | candidato excelente para réplica y test postpublicación, pero no evidencia científica suficiente |
| 010 | Directional Movement Index | Trend following por capas; DMI cross + filtro ADX + entrada stop en canal + trailing/dollar stop; silver daily | $148,220.10; PF 3.26; 83 trades; 43.37% ganadoras; RINA 563.95 | el workspace conserva un grid exhaustivo **31×31 = 961 configuraciones** de `PercRangeLE` y `PercRangeSE`; el punto publicado `10/10` es el **máximo absoluto de net profit** del grid | replicar como state machine con ejecución intradía, pero tratar el resultado como ganador seleccionado y altamente concentrado en longs/outlier |

## 0.1 Veredicto global

El Issue 5 contiene dos lecciones distintas.

`MACD Difference Turn` cambia la interpretación de un indicador conocido sin cambiar sus cálculos. En vez de esperar el cruce del histograma por cero, busca un nuevo máximo o mínimo de la diferencia MACD para anticipar el giro. La comparación publicada es útil porque conserva el mismo mercado, periodo, tamaño y familia de indicador. Sin embargo, sigue siendo una comparación **in-sample, sobre un único par y durante sólo dos años**, sin costes completos ni validación fuera de muestra.

`Directional Movement Index` es una estrategia mucho más compleja de lo que su nombre sugiere. El cruce DMI no entra directamente. Primero crea un setup, exige ADX, calcula un nivel a partir de un canal, deja una orden stop para la barra siguiente y después gestiona la posición mediante dos trailing stops asimétricos y un stop monetario. El workspace añade una evidencia decisiva: el `10/10` publicado no es sólo un punto dentro de una meseta; es el mejor net profit entre 961 combinaciones almacenadas.

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

# Parte I — Estrategia 009: MACD Difference Turn Strategy

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-05-STRAT-009`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 5
- **Fecha declarada:** mayo de 2015
- **Artículo:** *MACD Difference Turn Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas del PDF:** 4–8
- **Páginas impresas del artículo:** 3–7
- **Estilo declarado:** Mean reversion
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Swing trading
- **Mercado del backtest publicado:** EURUSD
- **Frecuencia:** 120 minutos
- **Periodo publicado:** dos años, terminando el 1 de abril de 2015
- **Tamaño:** 100,000 euros
- **Comisión:** $5 por lado
- **Archivos del paquete:** estrategia, indicador actualizado y workspace

### Inputs publicados

| Input | Default | Función declarada |
|---|---:|---|
| `FastLength` | 12 | Longitud de la EMA rápida |
| `SlowLength` | 26 | Longitud de la EMA lenta |
| `MACDLength` | 9 | Longitud de la EMA de señal del MACD |
| `SignalLength` | 8 | Ventana para detectar un nuevo máximo o mínimo de `MACDDiff` |

El indicador complementario añade:

| Input | Default | Función |
|---|---:|---|
| `UseSignalLength` | `True` | Colorear por nuevos extremos de `SignalLength`; si es falso, colorear por signo respecto de cero |
| `BullColor` | Green/DarkGreen según artefacto | Color de nuevo máximo |
| `BearColor` | Red | Color de nuevo mínimo |

### Evidencia adicional del ZIP

El workspace confirma:

```text
chart:
EURUSD 120 min [FOREX]

analysis techniques:
MACD LE
MACD SE
MACD
TSL:MACD Difference
TSL:MACD Differrence Turn
```

El nombre interno conserva el error ortográfico `Differrence` en el token de la estrategia. No afecta a la lógica, pero debe preservarse en una réplica orientada a checksum.

El workspace conserva:

```text
FastLength = 12
SlowLength = 26
MACDLength = 9
SignalLength = 8
UseSignalLength = True
```

No contiene un stream `OptimizationData` con resultados. Por tanto, el paquete no prueba que estos cuatro valores fueran optimizados dentro del workspace entregado.

Los `.ELD` son contenedores propietarios. Exponen identificadores y versiones, pero no el source EasyLanguage como texto legible. La estrategia puede reconstruirse funcionalmente a partir del PDF, pero no puede certificarse una réplica bit a bit del código.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí, con facilidad relativa.** |
| ¿Puede replicarse aproximadamente con el PDF? | **Sí.** |
| ¿Puede replicarse exactamente sin source EasyLanguage? | **No del todo.** Quedan decisiones sobre igualdad, inicialización EMA y repetición de señales. |
| ¿El artículo demuestra edge? | **No.** Muestra una comparación in-sample sobre EURUSD y dos años. |
| ¿La comparación con MACD convencional es informativa? | **Sí.** Mantiene el mismo mercado, periodo, tamaño y costes declarados. |
| ¿Es realmente mean reversion? | **Sólo parcialmente.** Es un detector de inflexión/aceleración del histograma que entra en la dirección del nuevo extremo. |
| ¿Está preparada para operar? | **No.** Es always-in, no tiene stop y no se publica sensibilidad a spread/slippage. |
| ¿Merece estudiarse? | **Sí.** Es simple, falsificable y dispone de un largo periodo postpublicación. |

Clasificación TSIS:

```text
MACD_HISTOGRAM_INFLECTION_CANDIDATE
ALWAYS_IN_REVERSAL_POLICY
NEXT_BAR_OPEN_EXECUTION
NO_NATIVE_RISK_EXIT
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La descripción “MACD que gira” puede inducir a pensar que se busca un máximo o mínimo local confirmado. No es exactamente eso.

La estrategia no espera:

```text
histograma positivo → empieza a caer
histograma negativo → empieza a subir
```

Tampoco espera el cruce por cero tradicional.

Busca:

```text
nuevo máximo de MACDDiff respecto de una ventana pasada
→ señal long

nuevo mínimo de MACDDiff respecto de una ventana pasada
→ señal short
```

Es decir, detecta una **expansión extrema reciente en la dirección del cambio del histograma**.

Una interpretación funcional más precisa es:

```text
el histograma MACD ha desarrollado suficiente impulso relativo
como para superar todos sus valores recientes
→ asumir que se ha producido una inflexión alcista operable
```

Y de forma simétrica para cortos.

Por ello combina tres ideas:

```text
1. smoothing mediante EMAs
2. aceleración/desaceleración representada por MACDDiff
3. breakout temporal del propio oscilador
```

No es una reversión al promedio clásica del precio. Es un **breakout del oscilador utilizado para anticipar una reversión del precio o del momentum**.

---

## 3. Reconstrucción matemática

## 3.1 EMA rápida y lenta

Sea `C_t` el cierre de la barra de 120 minutos.

La EMA estándar puede escribirse como:

\[
EMA_t(L)=\alpha_L C_t+(1-\alpha_L)EMA_{t-1}(L)
\]

con:

\[
\alpha_L=\frac{2}{L+1}
\]

Entonces:

\[
EMA^{fast}_t=EMA_t(12)
\]

\[
EMA^{slow}_t=EMA_t(26)
\]

La forma exacta de inicialización utilizada por TradeStation debe tratarse como parte del contrato de réplica. Posibles semillas incluyen:

```text
primer precio
SMA inicial
warm-up interno anterior al periodo visible
```

## 3.2 Línea MACD

\[
MACD_t=EMA^{fast}_t-EMA^{slow}_t
\]

## 3.3 Línea de señal

\[
Signal_t=EMA_9(MACD_t)
\]

## 3.4 MACD Difference

\[
MACDDiff_t=MACD_t-Signal_t
\]

El cruce tradicional es equivalente a:

```text
MACDDiff cruza sobre 0 → long
MACDDiff cruza bajo 0 → short
```

La estrategia publicada ignora ese cruce.

## 3.5 Nuevo extremo de la ventana

Candidato de reconstrucción long:

\[
LongSignal_t = MACDDiff_t > \max(MACDDiff_{t-1},\ldots,MACDDiff_{t-L})
\]

Candidato short:

\[
ShortSignal_t = MACDDiff_t < \min(MACDDiff_{t-1},\ldots,MACDDiff_{t-L})
\]

con:

```text
L = SignalLength = 8
```

La frase del PDF “new high compared to its value on the last SignalLength bars” favorece la comparación con las ocho barras **anteriores**, excluyendo la actual.

Sin el source deben registrarse estas alternativas:

```text
A. comparación estricta > / < contra las 8 barras previas
B. igualdad permitida >= / <=
C. Highest/Lowest incluyendo la barra actual
D. HighestBar/LowestBar con reglas de empate propias de TradeStation
```

## 3.6 Temporización

La señal se conoce al cierre de la barra `t`.

```text
cierre t:
calcular EMAs, MACD, señal y MACDDiff

si hay nuevo máximo:
programar long

si hay nuevo mínimo:
programar short

apertura t+1:
ejecutar a mercado
```

No debe utilizarse el cierre de `t` como precio de ejecución.

## 3.7 Política always-in

La estrategia no contiene exits independientes.

```text
short → nueva señal long → cubrir y quedar long
long → nueva señal short → vender y quedar short
```

Una señal del mismo lado mientras ya existe una posición puede:

```text
ser ignorada
ser registrada sin nueva orden
crear una entrada adicional si pyramiding estuviera habilitado
```

La revista la presenta como reversing/always-in, por lo que la réplica principal debe usar:

```text
one net position
no pyramiding
same-side signal = no position change
```

## 3.8 Warm-up

La primera observación legal necesita historia suficiente para:

```text
EMA lenta de 26
EMA de señal de 9 sobre MACD
8 barras previas de MACDDiff
```

El warm-up exacto no se obtiene sumando mecánicamente 26+9+8, porque las EMAs pueden inicializarse incrementalmente. Para una réplica científica conviene cargar un pre-roll amplio y excluir del scoring las primeras barras hasta estabilización.

---

## 4. Reglas operativas reconstruidas

### Long

```text
si MACDDiff_t es mayor que todos los MACDDiff de las 8 barras anteriores:
    buy next bar at market
```

### Short

```text
si MACDDiff_t es menor que todos los MACDDiff de las 8 barras anteriores:
    sell short next bar at market
```

### Exit

```text
no exit independiente
la señal contraria revierte la posición
```

### Unidad temporal

```text
barra de señal:
120 minutos

execution timestamp:
apertura de la barra siguiente

holding period:
variable hasta la señal contraria

exposición:
virtualmente 100% después de la primera entrada
```

---

## 5. Resultados publicados

## 5.1 Configuración común

```text
Symbol: EURUSD
Bar interval: 120 minutos
History: 2 años terminando 01/04/2015
Trade size: 100,000 euros
Commissions: $5 por lado
Stops: ninguno
Exit: reversión en señal contraria
Inputs: defaults
```

No se publica slippage ni un modelo explícito de bid/ask.

## 5.2 Comparación completa

| Métrica | MACD convencional | MACD Difference Turn |
|---|---:|---:|
| Net Profit | -$8,297.70 | **$20,877.60** |
| Gross Profit | $90,122.40 | $113,954.70 |
| Gross Loss | -$98,420.10 | -$93,077.10 |
| Profit Factor | 0.92 | **1.22** |
| Trades | 444 | **491** |
| Percent Profitable | 34.23% | **45.82%** |
| Winning Trades | 152 | 225 |
| Losing Trades | 292 | 266 |
| Avg. Trade Net Profit | -$18.69 | **$42.52** |
| Avg. Winning Trade | $592.91 | $506.47 |
| Avg. Losing Trade | -$337.06 | -$349.91 |
| Ratio Avg. Win / Avg. Loss | 1.76 | 1.45 |
| Largest Winning Trade | $2,566.90 | $3,352.80 |
| Largest Losing Trade | -$1,765.50 | -$1,576.00 |
| Return Retracement Ratio | -0.38 | 0.70 |
| RINA Index | -38.64 | 36.81 |
| Max Equity Run-up | $12,355.90 | $28,207.50 |
| Max Intraday Drawdown | -$12,406.20 | **-$6,542.90** |
| Net Profit / Intraday DD | -66.88% | **319.09%** |
| Trade-close Drawdown | -$12,284.20 | **-$6,139.60** |
| Net Profit / Trade-close DD | -67.55% aprox. | **340.05%** |
| Max Trade Drawdown | -$2,519.00 | **-$1,691.00** |

La mejora de net profit entre ambas variantes es:

\[
20,877.60-(-8,297.70)=29,175.30
\]

## 5.3 Qué mejoró realmente

La variante Turn:

```text
aumentó el número de trades en 47
subió el win rate en 11.59 puntos porcentuales
convirtió la expectativa media de -$18.69 a +$42.52
redujo aproximadamente a la mitad el drawdown máximo
```

Pero no mejoró todos los componentes:

```text
avg winning trade:
$592.91 → $506.47

ratio win/loss:
1.76 → 1.45
```

La mejora procede principalmente de:

```text
más señales ganadoras
menos trades perdedores relativos
mejor timing de reversión
```

no de obtener ganadores individualmente mayores en promedio.

## 5.4 Curvas de capital

La página física 8 muestra:

```text
MACD convencional:
curva negativa y oscilante, sin recuperación sostenible

MACD Turn:
pendiente positiva general
pero con un periodo prolongado entre nuevos máximos
aproximadamente en la zona media-final de la muestra
```

Por tanto, incluso el ganador publicado contiene dependencia temporal y largos periodos de degradación.

---

## 6. ¿Dónde podría estar el edge?

La hipótesis funcional puede formularse así:

> Cuando la diferencia entre MACD y su señal rompe el rango de sus últimos ocho valores, el cambio de momentum contiene información sobre una reversión o una nueva fase direccional antes de que el MACD cruce su señal.

Posibles mecanismos:

```text
inflexión temprana del momentum
aceleración de corto plazo
reversión tras agotamiento
reducción del lag del cruce por cero
cambio de régimen antes de la confirmación tradicional
```

Pero el resultado también puede deberse a:

```text
particularidades del EURUSD 2013–2015
alineación fortuita con las sesiones de 120 minutos
costes incompletos
una tendencia persistente en parte del periodo
selección previa del SignalLength = 8
selección del mercado después de observar otros mercados
```

La comparación no identifica cuál de estas explicaciones es correcta.

---

## 7. Problemas científicos y técnicos

## 7.1 Sólo dos años

Para una estrategia always-in con 491 trades, dos años generan muchas operaciones, pero no necesariamente muchos regímenes independientes.

Las barras y trades comparten:

```text
mismas EMAs
mismos periodos de volatilidad
mismos ciclos macro
misma estructura de mercado
```

## 7.2 Un único par

No se publican resultados para:

```text
GBPUSD
USDJPY
equities
futuros
otros timeframes
```

La generalización declarada no se demuestra.

## 7.3 In-sample

Aunque se usen defaults tradicionales `12/26/9`, la regla adicional `SignalLength = 8` y la propia definición de nuevo extremo fueron observadas sobre datos históricos.

No se publica:

```text
training set
validation set
walk-forward
preregistro
número de variantes descartadas
```

## 7.4 Baseline no igualado en turnover

La estrategia Turn opera 491 veces frente a 444.

La comparación debería separar:

```text
mejor señal
más oportunidades
mayor turnover
mayor exposición a costes no modelados
```

## 7.5 Spread y slippage

En FX, una entrada a la apertura de una barra no existe como precio único sin especificar:

```text
bid
ask
mid
last
spread histórico
rollover/swap
```

Una expectativa media de $42.52 por 100,000 euros puede ser sensible a pocos pips adicionales de coste.

## 7.6 Always-in sin stop

El modelo queda expuesto a:

```text
gaps o discontinuidades
noticias macro
periodos sin señal contraria
fallos de feed
movimientos extremos
```

El drawdown observado no representa una cota de riesgo.

## 7.7 La etiqueta mean reversion es discutible

La regla long compra un nuevo máximo del histograma; la short vende un nuevo mínimo.

Eso se parece a:

```text
breakout de momentum del oscilador
```

aunque su intención sea anticipar un giro del precio.

TSIS debe clasificar fenómeno y respuesta por separado, no heredar la etiqueta editorial sin análisis.

## 7.8 Definición de “new high/low”

Faltan reglas sobre:

```text
igualdades
NaN durante warm-up
varios nuevos máximos consecutivos
mismo valor repetido
señal simultánea imposible pero no explicitada
```

## 7.9 Inicialización de EMAs

Diferencias pequeñas en la semilla pueden desplazar los primeros eventos y, por reversión, alterar toda la secuencia posterior.

## 7.10 Session template

EURUSD cotiza casi continuamente, pero las barras de 120 minutos dependen de:

```text
zona horaria
inicio de sesión
cierre diario
DST
weekend break
```

Mover dos horas la cuadrícula cambia los OHLC y los cruces.

## 7.11 Precio de la apertura siguiente

Debe definirse si es:

```text
primer tick
open oficial de barra TradeStation
bid/ask executable
midpoint
```

## 7.12 Dependencia de secuencia

Al ser reversing, un único desacuerdo temprano entre implementación y TradeStation puede invertir todas las posiciones posteriores hasta la siguiente reconciliación.

## 7.13 Sin descomposición long/short

La tabla publicada no muestra si el beneficio procede de:

```text
longs
shorts
un único régimen tendencial
```

## 7.14 No hay sensibilidad de parámetros

No se presenta la superficie para:

```text
FastLength
SlowLength
MACDLength
SignalLength
```

No sabemos si `8` pertenece a una meseta o a un pico.

## 7.15 Data snooping de la regla

Incluso sin optimización numérica, elegir entre:

```text
cruce por cero
nuevo extremo
pendiente
segunda derivada
color del histograma
```

es una búsqueda de modelos que debe contabilizarse.

---

## 8. Cómo debe implementarse en TSIS

## 8.1 Separar indicador, evento y política

```text
indicator:
MACDDiff observable en t

event:
macd_difference_new_window_extreme

policy:
reverse position next bar open
```

## 8.2 Market State mínimo

```text
symbol
bar_interval
bar_end_timestamp
close
ema_fast_12
ema_slow_26
macd
macd_signal_9
macd_diff
rolling_macd_diff_high_8_prev
rolling_macd_diff_low_8_prev
new_high_flag
new_low_flag
warmup_status
```

## 8.3 Event State

```text
event_type:
macd_difference_turn

direction:
long | short

decision_timestamp:
bar_close_t

execution_eligible_timestamp:
bar_open_t_plus_1

reference_window:
8 completed prior bars
```

## 8.4 Estado de posición

```text
FLAT antes de la primera señal
LONG
SHORT
```

Transiciones:

```text
FLAT + long  → LONG
FLAT + short → SHORT
LONG + short → SHORT
SHORT + long → LONG
same-side signal → unchanged
```

## 8.5 Vista de precios

Para equities dentro de TSIS:

```text
señal:
serie histórica ajustada y point-in-time gobernada

ejecución:
precio raw operable de la apertura de la barra siguiente
```

Para FX se necesitaría una nueva fuente con bid/ask histórico y sesiones gobernadas.

## 8.6 Lineage

Cada señal debe conservar:

```text
input version
EMA initialization policy
bar template
price view
source rows
rolling-window members
execution source
cost model
```

---

## 9. Pseudocódigo de referencia

```python
from dataclasses import dataclass
from enum import Enum
from math import isfinite


class Position(Enum):
    FLAT = 0
    LONG = 1
    SHORT = -1


@dataclass(frozen=True)
class MacdTurnConfig:
    fast_length: int = 12
    slow_length: int = 26
    signal_length: int = 9
    extreme_length: int = 8


def ema(previous: float, value: float, length: int) -> float:
    alpha = 2.0 / (length + 1.0)
    return alpha * value + (1.0 - alpha) * previous


def detect_turn(macd_diff_history: list[float], extreme_length: int) -> int:
    """Return +1 long, -1 short, 0 no signal.

    macd_diff_history[-1] is the completed current bar.
    """
    if len(macd_diff_history) < extreme_length + 1:
        return 0

    current = macd_diff_history[-1]
    previous = macd_diff_history[-(extreme_length + 1):-1]

    if not isfinite(current) or any(not isfinite(x) for x in previous):
        return 0

    if current > max(previous):
        return 1
    if current < min(previous):
        return -1
    return 0


def target_position(current_position: Position, signal: int) -> Position:
    if signal == 1:
        return Position.LONG
    if signal == -1:
        return Position.SHORT
    return current_position
```

La semilla EMA, la política de igualdad y la apertura exacta deben parametrizarse para reconciliar la réplica.

---

## 10. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica del indicador

Reconciliar barra por barra:

```text
EMA12
EMA26
MACD
EMA9(MACD)
MACDDiff
```

### Fase 2 — Réplica de señales

Objetivos de checksum:

```text
491 trades aproximadamente
45.82% ganadoras
net profit cercano a $20,877.60
```

No debe forzarse el resultado. Toda diferencia debe explicarse por datos, sesiones, seed o ejecución.

### Fase 3 — Baseline convencional

Reproducir simultáneamente:

```text
MACD LE/SE por cruce de cero
```

sobre el mismo feed y coste.

### Fase 4 — Verdadero OOS postpublicación

Congelar:

```text
12 / 26 / 9 / 8
regla estricta
barra 120 minutos
next-bar-open
```

Y probar exclusivamente datos posteriores a mayo de 2015.

### Fase 5 — Multi-mercado

Aplicar sin optimizar a:

```text
principales pares FX
índices líquidos
ETFs
futuros líquidos
```

### Fase 6 — Costes

Escenarios:

```text
spread histórico
spread duplicado en stress
slippage 0.5, 1 y 2 pips adicionales
swap/rollover
latencia de una barra parcial
```

### Fase 7 — Ablation

Comparar:

```text
cruce por cero
nuevo extremo de 8
pendiente positiva/negativa
segunda derivada
random reversal con igual turnover
```

### Fase 8 — Horizonte del evento

Medir outcomes después de la señal:

```text
1 barra
2 barras
4 barras
8 barras
hasta cruce cero
hasta señal contraria
```

### Fase 9 — Sensibilidad de `SignalLength`

No buscar el mejor punto. Evaluar estabilidad en:

```text
3–30 barras
```

con corrección por múltiples pruebas.

### Fase 10 — Long/short y regímenes

Separar:

```text
long
short
volatilidad alta/baja
trend/range
sesiones
```

### Fase 11 — Exits

Sólo después de congelar la entrada:

```text
time exit
breakeven
ATR stop
signal decay
```

### Fase 12 — Placebos

```text
permutar timestamps por bloques
usar ventanas aleatorias con igual frecuencia
retrasar la señal una barra
```

---

## 11. Variantes posteriores a la réplica

### Variante A — Extremo condicionado por signo

```text
long sólo si MACDDiff < 0 y forma nuevo máximo
short sólo si MACDDiff > 0 y forma nuevo mínimo
```

Esto aproxima mejor una idea de reversión temprana.

### Variante B — Z-score del histograma

\[
Z_t=\frac{MACDDiff_t-\mu_t}{\sigma_t}
\]

### Variante C — Slope turn

Usar cambio de signo de la pendiente del histograma en vez de breakout.

### Variante D — SignalLength separado

```text
LongSignalLength
ShortSignalLength
```

Debe tratarse como grado de libertad adicional.

### Variante E — Time exit

Evaluar la vida útil del evento sin convertir inmediatamente la salida en una nueva entrada contraria.

### Variante F — Política flat permitida

Separar:

```text
entry signal
exit signal
reverse signal
```

### Variante G — MACD Turn como feature

No operar directamente; incorporarlo como atributo de `price_movement` o `momentum state`.

---

## 12. Encaje en Market State y Event State

### Market State

```text
macd_fast_ema
macd_slow_ema
macd_line
macd_signal
macd_difference
macd_difference_window_rank
macd_difference_distance_from_zero
macd_difference_slope
```

### Event State

```text
event_type:
macd_difference_new_extreme

subject_scope:
symbol

direction:
up | down

confirmation_timestamp:
bar_close_t

lookback:
8 completed bars
```

### Outcomes

```text
forward_return_1_2_4_8_bars
MFE
MAE
time_to_zero_cross
time_to_opposite_extreme
realized_return_until_opposite_signal
```

### Distinción clave

```text
evento:
el histograma ha roto su rango reciente

estrategia:
revertir la posición en la siguiente apertura
```

El evento puede tener información aunque la política always-in no sea óptima.

---

## 13. Transferencia a small caps

La lógica es implementable sobre datos de TSIS, pero no debe trasladarse sin cambios conceptuales.

En small caps intradía aparecen:

```text
gaps
halts
catalizadores
spreads extremos
sesiones cortas de información
microestructura discontinua
```

Un nuevo máximo del histograma puede significar:

```text
continuación genuina
short squeeze
respuesta a news
artefacto de un gap
```

Uso recomendado:

```text
NO como estrategia always-in inicial
SÍ como evento/feature dentro de price_movement
SÍ para estudiar timing de giros después de extensiones
```

Debe condicionarse por:

```text
news_catalyst_context
halt_context
liquidity
trading_activity
intraday_position
```

---

## 14. Veredicto de MACD Difference Turn

```text
IMPLEMENTAR:
sí

MOTIVO:
reglas simples, auditable, baseline claro y OOS largo

ACEPTAR EDGE PUBLICADO:
no

RIESGO PRINCIPAL:
resultado de un solo mercado y dos años con costes incompletos

VALOR PARA TSIS:
alto como event study y prueba de estrategias reversing

LIVE:
no
```

Gate propuesto:

```text
MACD-TURN-REPLICATION-COST-SENSITIVITY-AND-POSTPUBLICATION-OOS-GATE
```

---
# Parte II — Estrategia 010: Directional Movement Index Strategy

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-05-STRAT-010`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 5
- **Fecha declarada:** mayo de 2015
- **Artículo:** *Directional Movement Index Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 10–14
- **Páginas impresas del artículo:** 9–13
- **Estilo declarado:** Trend following
- **Mercados declarados:** Equities, futures, forex
- **Horizonte declarado:** Swing trading
- **Mercado del backtest publicado:** Silver futures
- **Símbolo de investigación:** `@SI=103NN`
- **Frecuencia:** Daily
- **Resolución Look-Inside-Bar:** 30 minutos
- **Periodo:** diez años terminando el 31 de marzo de 2015
- **Archivos:** estrategia, indicador de price channel y workspace

### Inputs publicados

| Input | Default | Función |
|---|---:|---|
| `PriceChannelLength` | 20 | Lookback del highest high / lowest low |
| `DMILength` | 12 | Longitud del DMI |
| `ADXLevel` | 15 | Umbral mínimo del ADX |
| `PercRangeLE` | 10 | Porcentaje del rango del canal añadido al cierre para entrada long |
| `PercRangeSE` | 10 | Porcentaje del rango del canal restado al cierre para entrada short |
| `MyStopLoss` | 2,000 | Stop monetario por posición |
| `LXTrailBar` | 5 | Barras para el lowest-low stop de longs |
| `SXTrailBar` | 1 | Barras para el highest-high stop de shorts |

Indicador DMI visual:

| Input | Valor |
|---|---:|
| `Length` | 12 |
| `ADXTrend` | 15 |

### Evidencia adicional del ZIP

El workspace confirma:

```text
chart:
@SI=103NN Daily [COMEX]
Silver Custom Continuous Contract

analysis techniques:
DMI
TSL:Directional Movement Index
TSL:PriceChannel (for DMI Strategy)
```

También conserva las cadenas:

```text
PriceChannelLength
DMILength
ADXLevel
PercRangeLE
PercRangeSE
MyStopLoss = 2000
LXTrailBar
SXTrailBar
```

El workspace fue guardado o abierto en distintas versiones de TradeStation 9.x. El `.ELD` contiene identificadores de una versión posterior, pero no expone el source EasyLanguage como texto. La migración de versión se trata como evidencia de contexto, no como prueba de que el paquete sea una cápsula inmutable de 2015.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero exige state machine, contratos físicos y replay intradía. |
| ¿Puede replicarse aproximadamente? | **Sí.** |
| ¿Puede replicarse exactamente sin source? | **No del todo.** Faltan prioridad intrabar, vigencia de orden y detalles de DMI/Wilder. |
| ¿El artículo demuestra edge? | **No.** El resultado está optimizado, contiene un outlier grande y es casi todo long. |
| ¿Los inputs parecen robustos? | **Parcialmente.** El PDF muestra superficies amplias, pero el `10/10` publicado es el máximo del grid guardado. |
| ¿El lado short aporta edge material? | **Muy poco:** $6,262.40 y PF 1.18. |
| ¿Está preparada para operar? | **No.** Falta validación postpublicación, contratos físicos y costes realistas. |
| ¿Merece estudiarse? | **Sí.** Es un caso valioso de setup → stop entry → exits asimétricos. |

Clasificación TSIS:

```text
DMI_ADX_PRICE_CHANNEL_TREND_CANDIDATE
MULTI_STAGE_SETUP
NEXT_BAR_STOP_ENTRY
INTRABAR_EXECUTION_REQUIRED
ASYMMETRIC_TRAILING_EXITS
DOLLAR_STOP
OPTIMIZATION_SELECTION_CRITICAL
CONTINUOUS_FUTURES_RISK
POSTPUBLICATION_OOS_AVAILABLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

No es simplemente:

```text
DMI+ cruza DMI- → comprar
DMI- cruza DMI+ → vender
```

El cruce sólo crea una autorización de dirección.

La secuencia es:

```text
1. detectar cruce DMI
2. exigir ADX > 15
3. construir un canal de 20 barras
4. fijar un precio de entrada alejado del cierre
5. dejar una orden stop para la barra siguiente
6. entrar sólo si el precio confirma el movimiento
7. gestionar con trailing stop asimétrico y dollar stop
```

La hipótesis real es:

> Un cruce direccional en un entorno suficientemente tendencial tiene mayor calidad si el precio confirma el movimiento alcanzando un umbral dentro o fuera de su canal reciente.

El filtro de precio intenta evitar entrar sólo porque dos líneas suavizadas se cruzan.

---

## 3. Reconstrucción matemática del DMI/ADX

La revista describe las funciones, pero no imprime las ecuaciones completas. La reconstrucción estándar de Wilder es la candidata de réplica.

## 3.1 True Range

\[
TR_t=\max\left(
H_t-L_t,
|H_t-C_{t-1}|,
|L_t-C_{t-1}|
\right)
\]

## 3.2 Directional Movement

\[
UpMove_t=H_t-H_{t-1}
\]

\[
DownMove_t=L_{t-1}-L_t
\]

\[
+DM_t=
\begin{cases}
UpMove_t, & UpMove_t>DownMove_t \text{ y } UpMove_t>0\\
0, & \text{en otro caso}
\end{cases}
\]

\[
-DM_t=
\begin{cases}
DownMove_t, & DownMove_t>UpMove_t \text{ y } DownMove_t>0\\
0, & \text{en otro caso}
\end{cases}
\]

## 3.3 Suavizado de Wilder

Para `N = 12`, la forma recursiva candidata es:

\[
SmoothTR_t=SmoothTR_{t-1}-\frac{SmoothTR_{t-1}}{N}+TR_t
\]

Y de manera equivalente para `+DM` y `-DM`.

## 3.4 Directional Indicators

\[
+DI_t=100\frac{Smooth(+DM)_t}{SmoothTR_t}
\]

\[
-DI_t=100\frac{Smooth(-DM)_t}{SmoothTR_t}
\]

## 3.5 DX y ADX

\[
DX_t=100\frac{|+DI_t-(-DI_t)|}{+DI_t+(-DI_t)}
\]

\[
ADX_t=WilderAverage_N(DX_t)
\]

La semilla y el tratamiento de denominadores cero deben reconciliarse con la función de TradeStation.

## 3.6 Setup long

```text
+DI_t cruza sobre -DI_t
AND
ADX_t > 15
```

El artículo no exige que ADX esté subiendo, aunque el background explique que un ADX creciente es señal de tendencia. Ésta es una distinción importante:

```text
narrativa:
rising ADX above level

regla publicada:
ADX above level
```

## 3.7 Setup short

```text
-DI_t cruza sobre +DI_t
AND
ADX_t > 15
```

---

## 4. Price channel y niveles de entrada

## 4.1 Canal

Candidato estándar:

\[
HH_t=\max(H_{t-19},\ldots,H_t)
\]

\[
LL_t=\min(L_{t-19},\ldots,L_t)
\]

\[
Range_t=HH_t-LL_t
\]

Con:

```text
PriceChannelLength = 20
```

## 4.2 Target long

En la barra de setup:

\[
BuyTarget_t=C_t+0.10\times Range_t
\]

## 4.3 Target short

\[
SellShortTarget_t=C_t-0.10\times Range_t
\]

## 4.4 Fijación temporal

La redacción y el gráfico indican que el target se **actualiza cuando ocurre el cruce DMI**. La réplica primaria debe congelar el nivel calculado con la barra de setup.

Debe evitarse recalcularlo silenciosamente durante la barra siguiente, porque eso convertiría la orden en un nivel móvil.

## 4.5 Orden

```text
setup al cierre t
→
orden stop activa en t+1
```

Long:

```text
buy next bar at BuyTarget stop
```

Short:

```text
sell short next bar at SellShortTarget stop
```

La frase “on the next bar” sugiere que la orden expira después de esa barra si no se ejecuta. El PDF no afirma explícitamente una vigencia de más días.

## 4.6 Gap-through

Si la barra siguiente abre más allá del target:

```text
long:
open > BuyTarget

short:
open < SellShortTarget
```

un fill realista debe ocurrir al open o peor, no en el target teórico.

---

## 5. Exits

## 5.1 Trailing stop long

\[
LongStop_t=LowestLow(HoldingWindow=5)
\]

La interpretación candidata es el lowest low de las últimas cinco barras completadas según la semántica de orden de TradeStation.

## 5.2 Trailing stop short

\[
ShortStop_t=HighestHigh(HoldingWindow=1)
\]

Con `SXTrailBar = 1`, el stop short queda extremadamente cercano al precio reciente.

## 5.3 Stop monetario

```text
MyStopLoss = $2,000 por contrato
```

En silver debe convertirse a puntos mediante:

```text
BigPointValue
contract multiplier
entry price
```

La implementación no debe confundir dólares con unidades de precio.

## 5.4 Prioridad

En una misma barra podrían tocarse:

```text
entry stop
trailing stop
dollar stop
señal contraria
```

El LIBB de 30 minutos reduce, pero no elimina, la ambigüedad de secuencia.

---

## 6. State machine temporal

Estado candidato:

```text
NO_SETUP
PENDING_LONG_FOR_NEXT_BAR
PENDING_SHORT_FOR_NEXT_BAR
LONG
SHORT
```

### Transiciones

```text
NO_SETUP
  + DMI+ cross & ADX>15
  → PENDING_LONG_FOR_NEXT_BAR

NO_SETUP
  + DMI- cross & ADX>15
  → PENDING_SHORT_FOR_NEXT_BAR

PENDING_LONG
  + target touched
  → LONG

PENDING_LONG
  + end of next bar without fill
  → NO_SETUP

PENDING_SHORT
  + target touched
  → SHORT

PENDING_SHORT
  + end of next bar without fill
  → NO_SETUP

LONG
  + trailing or dollar stop
  → FLAT

SHORT
  + trailing or dollar stop
  → FLAT
```

Ambigüedades contractuales:

```text
¿una nueva señal contraria cancela una orden pendiente?
¿puede revertirse directamente una posición?
¿se permite entry y exit en la misma barra?
¿el trailing incluye la barra actual?
¿la orden pendiente dura exactamente una barra?
```

---

## 7. Resultados publicados

## 7.1 Configuración

```text
Symbol: @SI=103NN
Bar interval: Daily
History: 10 años terminando 31/03/2015
Initial capital: $25,000
Trade size: 1 contrato
Commissions: $2.65 por lado
Look-Inside-Bar: 30 minutos
Stop loss: $2,000
Continuous contract: no back adjustment
Roll trigger: 3 días antes del first notice date
```

No se publica un slippage adicional.

## 7.2 Resultado agregado

| Métrica | Resultado |
|---|---:|
| Net Profit | **$148,220.10** |
| Gross Profit | $213,819.20 |
| Gross Loss | -$65,599.10 |
| Profit Factor | **3.26** |
| Trades | 83 |
| Percent Profitable | 43.37% |
| Winning Trades | 36 |
| Losing Trades | 47 |
| Avg. Trade Net Profit | $1,785.78 |
| Avg. Winning Trade | $5,939.42 |
| Avg. Losing Trade | -$1,395.73 |
| Ratio Avg. Win / Avg. Loss | 4.26 |
| Largest Winning Trade | **$44,644.70** |
| Largest Losing Trade | -$2,655.30 |
| Max Consecutive Winners | 4 |
| Max Consecutive Losers | 5 |
| Avg. Bars in Winning Trades | 11.83 |
| Avg. Bars in Losing Trades | 2.66 |
| Return on Initial Capital | 592.88% |
| Annual Rate of Return | 19.27% |
| Return Retracement Ratio | 0.42 |
| RINA Index | 563.95 |
| Percent of Time in Market | 19.41% |

## 7.3 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Net Profit | **$141,957.70** | $6,262.40 |
| Gross Profit | $171,888.70 | $41,930.50 |
| Gross Loss | -$29,931.00 | -$35,668.10 |
| Profit Factor | **5.74** | **1.18** |
| Trades | 41 | 42 |
| Percent Profitable | 51.22% | 35.71% |
| Winning Trades | 21 | 15 |
| Losing Trades | 20 | 27 |
| Avg. Trade | $3,462.38 | $149.10 |
| Avg. Winner | $8,185.18 | $2,795.37 |
| Avg. Loser | -$1,496.55 | -$1,321.04 |
| Ratio Win/Loss | 5.47 | 2.12 |
| Largest Winner | $44,644.70 | $8,894.70 |
| Largest Loser | -$2,005.30 | -$2,655.30 |
| Avg. Bars Winner | 17.29 | 4.20 |
| Avg. Bars Loser | 3.55 | 2.00 |

El lado long produjo aproximadamente:

\[
\frac{141,957.70}{148,220.10}=95.77\%
\]

del net profit total.

La estrategia publicada no demuestra una capacidad simétrica de trend following.

## 7.4 Outlier

El mayor ganador fue:

```text
$44,644.70
```

Equivale a:

```text
30.12% del net profit total
31.45% del net profit long
```

Eliminándolo de forma puramente diagnóstica:

```text
net profit aproximado:
$103,575.40

Profit Factor total aproximado:
2.58

Profit Factor long aproximado:
4.25
```

La estrategia seguiría siendo rentable en la muestra, pero el resultado publicado está materialmente inflado por una sola operación.

## 7.5 Equity curve

La página física 13 muestra:

```text
crecimiento moderado hasta 2010
salto extraordinario alrededor de 2010–2011
meseta prolongada posterior
pocos avances en la segunda mitad de la muestra
```

La propia revista reconoce que la inactividad aumenta en la mitad más reciente.

## 7.6 Drawdown

El artículo estima un máximo drawdown semanal cercano al 14%. Sin embargo:

```text
la curva depende del outlier
la medida semanal puede ocultar excursiones intradía
el continuous contract no es una cuenta ejecutable
```

---

## 8. Forense del workspace de optimización

Éste es el hallazgo principal del paquete del Issue 5.

## 8.1 Stream conservado

El workspace DMI contiene:

```text
OptimizationData
size = 1,741,541 bytes
```

La estructura interna conserva tres bloques de 961 registros:

```text
bloque 1:
resultados completos

bloque 2:
duplicado bit a bit del bloque 1

bloque 3:
mismos trial IDs e inputs,
con métricas placeholder/cero
```

Por tanto:

```text
NO son 2,883 optimizaciones independientes
SÍ son 961 configuraciones distintas
```

## 8.2 Inputs optimizados

El trailer del stream identifica explícitamente:

```text
+TSL:Directional Movement Index: PercRangeLE
+TSL:Directional Movement Index: PercRangeSE
```

Valores observados:

```text
PercRangeLE = 0, 1, 2, ..., 30
PercRangeSE = 0, 1, 2, ..., 30
```

Grid completo:

\[
31\times31=961
\]

configuraciones.

El trial ID sigue:

\[
TrialID=31\times PercRangeSE+PercRangeLE+1
\]

Por ejemplo:

```text
PercRangeLE = 10
PercRangeSE = 10
TrialID = 321
```

## 8.3 Configuración publicada

```text
PercRangeLE = 10
PercRangeSE = 10
```

Resultado reconstruido del workspace:

```text
Net Profit: $148,220.13
Profit Factor: 3.2595
Trades: 83
Percent Profitable: 43.3735%
Avg Trade: $1,785.78
Max drawdown almacenado en la métrica principal: ~$10,598.85
```

Las diferencias de centavos respecto del PDF son de representación/redondeo.

## 8.4 Ranking de la configuración publicada

| Métrica | Resultado | Ranking en 961 |
|---|---:|---:|
| Net Profit | $148,220.13 | **1 / 961** |
| Profit Factor | 3.2595 | 56 / 961 |
| Avg Trade | $1,785.78 | 86 / 961 |
| Percent Profitable | 43.37% | 107 / 961 |
| Menor drawdown almacenado | $10,598.85 | 254 / 961 |

El punto publicado es el **máximo absoluto de net profit** del grid guardado.

Esto no invalida que exista una meseta, pero cambia la interpretación científica:

```text
no es sólo un punto robusto elegido lejos del pico
es también el ganador por net profit de la búsqueda 31×31
```

## 8.5 Vecindario local

Net profit alrededor del `10/10`:

| PercRangeSE \ PercRangeLE | 8 | 9 | 10 | 11 | 12 |
|---:|---:|---:|---:|---:|---:|
| 8 | $138,390.66 | $145,922.44 | $147,083.03 | $134,623.93 | $108,984.53 |
| 9 | $137,681.55 | $145,213.35 | $146,373.95 | $133,914.83 | $108,275.43 |
| 10 | $140,733.05 | $147,059.53 | **$148,220.13** | $135,761.02 | $110,121.62 |
| 11 | $132,618.65 | $138,945.13 | $140,105.73 | $127,646.62 | $102,007.21 |
| 12 | $134,414.84 | $140,741.33 | $141,901.93 | $129,442.82 | $103,803.42 |

Sí existe una región fuerte alrededor de `LE = 9–10`, pero el deterioro hacia `LE = 11–12` es material.

## 8.6 Distribución del grid

```text
configuraciones: 961
net profit positivo: 856 (89.07%)
net profit negativo o cero: 105
media de net profit: $61,696.50
mediana: $65,770.92
mínimo: -$16,227.01
máximo: $148,220.13
```

Umbrales:

```text
>= 99% del máximo: 3 configuraciones
>= 97.5%: 7
>= 95%: 14
>= 90%: 51
>= 80%: 162
```

El paisaje es ampliamente positivo, pero el top es reducido.

## 8.7 Ridge direccional

La media de net profit por `PercRangeLE` alcanza sus mejores niveles en:

```text
LE = 10 → $136,580 promedio sobre todos los SE
LE = 9  → $135,450
LE = 8  → $128,762
LE = 7  → $125,645
```

Por `PercRangeSE`, los mejores promedios aparecen en:

```text
SE = 10 → $73,468
SE = 8  → $72,063
SE = 9  → $71,428
```

Esto corrobora visualmente la meseta mostrada en la página física 14, aunque la topología no es completamente plana.

## 8.8 Interacción entre lados

`PercRangeLE` gobierna la entrada long y `PercRangeSE` la short, pero sus resultados no son perfectamente separables porque:

```text
una entrada o salida short puede interrumpir un episodio long
una señal long puede afectar la duración de un short
la posición neta y la prioridad de órdenes conectan ambos lados
```

Por ello el grid no puede reducirse sin más a sumar dos curvas independientes.

## 8.9 Qué no contiene el workspace

El stream guardado corresponde a `PercRangeLE × PercRangeSE`.

No conserva los datasets completos de las otras exploraciones mostradas en la revista:

```text
MyStopLoss
DMILength × ADXLevel
LXTrailBar × SXTrailBar
```

El PDF sí muestra:

```text
sweet spot aproximado de MyStopLoss alrededor de $2,000
zona robusta DMILength≈12 / ADXLevel≈15
pico superior declarado en DMILength=12 / ADXLevel=10
```

Pero no se pueden reconstruir rankings exactos de esas búsquedas desde el paquete entregado.

## 8.10 Consecuencia científica

El resultado publicado es el producto de varias capas de búsqueda:

```text
selección de DMI/ADX
selección del canal
selección de porcentajes long/short
selección del stop monetario
selección de trailing bars asimétricos
selección del mercado silver
selección del continuous contract
```

El número 961 sólo describe una de esas capas.

---

## 9. ¿Dónde podría estar el edge?

Hipótesis funcional:

> Cuando DMI cambia de dirección en un régimen con ADX suficiente, exigir una confirmación de precio relativa al canal reduce whipsaws y permite capturar tendencias con asimetría favorable entre ganador y perdedor.

Posibles fuentes:

```text
momentum persistente en commodities
breakout después de cambio direccional
filtro ADX que reduce rangos laterales
stop entry que exige continuación
trailing stop que conserva grandes ganadores
```

Hipótesis alternativas:

```text
una sola tendencia alcista extraordinaria en silver
outlier de $44,644.70
sesgo long del periodo
roll artifacts
selección del mejor punto del grid
stop y exits ajustados al histórico
```

---

## 10. Problemas científicos y técnicos

## 10.1 Optimización múltiple

El artículo declara optimización y sensibilidad para varias familias de inputs. No se publica el número total de trials acumulados.

## 10.2 Ganador del grid

El `10/10` publicado ocupa `1/961` por net profit.

Debe tratarse como:

```text
selected winner
```

no como una hipótesis aislada.

## 10.3 Outlier

Una operación explica 30% del beneficio total.

La robustez debe evaluarse con:

```text
leave-one-trade-out
winsorization diagnóstica
bootstrap por bloques
contribución por año
```

## 10.4 Asimetría long/short

```text
long PF = 5.74
short PF = 1.18
```

El short tiene muy poco margen frente a costes adicionales.

## 10.5 Continuous contract sintético

`@SI=103NN` no es un instrumento ejecutable.

La réplica necesita:

```text
contrato activo
roll calendar
first notice date
multiplicador
price mapping
posición durante roll
```

## 10.6 No back adjustment

Evita entradas en precios artificialmente trasladados, pero introduce saltos de roll en la serie.

Esos saltos pueden contaminar:

```text
TR
DMI
ADX
price channel
stop levels
```

## 10.7 Trades que cruzan el roll

Debe definirse si una posición:

```text
se cierra antes del roll
se rueda al contrato nuevo
continúa con PnL separado
```

## 10.8 LIBB de 30 minutos

Reduce la ambigüedad frente a OHLC diario, pero 30 minutos siguen permitiendo que entry y stop se toquen dentro del mismo sub-bar.

## 10.9 Slippage ausente

El settings block publica comisiones, no slippage. En silver, stop orders durante movimientos rápidos pueden sufrir fills peores.

## 10.10 Tick rounding

Todos los targets deben redondearse a `MinMove/PriceScale` de forma direccional y gobernada.

## 10.11 Gap-through

Un stop order no garantiza fill en el nivel del stop.

## 10.12 ADX no exige pendiente

La narrativa y la regla divergen. Añadir “ADX rising” sería una variante nueva, no una corrección de la réplica.

## 10.13 Vigencia de orden ambigua

El PDF dice “on the next bar”. No debe asumirse persistencia indefinida.

## 10.14 Trailing stop y barra actual

Debe definirse si el lowest/highest incluye:

```text
barra actual parcial
barra anterior completada
barra de entrada
```

## 10.15 Stop short de una barra

`SXTrailBar = 1` es extremadamente agresivo y puede ser una adaptación específica a silver y al periodo.

## 10.16 Múltiples grados de libertad asimétricos

```text
PercRangeLE != PercRangeSE permitido
LXTrailBar != SXTrailBar
long/short performance muy distinta
```

Esto incrementa la capacidad de ajuste.

## 10.17 Capital inicial

Un contrato de silver puede representar una exposición nocional muy superior a $25,000. El ROI publicado no equivale a una política de margen conservadora.

## 10.18 RINA alto

RINA 563.95 está influido por baja exposición temporal y por el outlier. No sustituye una distribución completa de returns.

## 10.19 Periodos planos recientes

La degradación de actividad en la mitad reciente puede indicar:

```text
cambio estructural
parámetros envejecidos
menor tendencia en silver
```

## 10.20 Surface plots no corrigen data snooping

Elegir una meseta es mejor que elegir un spike, pero sigue siendo selección sobre la misma muestra.

---

## 11. Cómo debe implementarse en TSIS

## 11.1 Separar setup, orden y posición

```text
DMI cross event
ADX eligibility
frozen target
pending stop order
fill
position management
```

No deben colapsarse en una sola fila booleana.

## 11.2 Market State diario

```text
high
low
close
true_range
plus_dm
minus_dm
plus_di
minus_di
adx
price_channel_high_20
price_channel_low_20
price_channel_range_20
last_dmi_cross_direction
```

## 11.3 Event State

```text
event_type:
dmi_directional_cross

direction:
long | short

adx_at_event
adx_eligible
channel_range
frozen_target
order_valid_from
order_valid_until
```

## 11.4 Pending order contract

```text
order_type = STOP
side
stop_price_raw
stop_price_rounded
created_at = close_t
active_from = next_session
expires_at = end_of_next_session
cancel_reason
```

## 11.5 Intraday replay

El daily bar puede generar el nivel, pero no resolver el fill.

Necesita:

```text
30m mínimo para aproximar el artículo
1m/trades/quotes para prueba científica
```

## 11.6 Contratos físicos

Señal y ejecución deben mapearse a:

```text
SI delivery month
contract id
roll status
first notice
volume/open interest
```

## 11.7 Stops

Cada stop debe quedar como orden independiente:

```text
trailing_price_stop
dollar_loss_stop
```

con prioridad y timestamps.

## 11.8 Estado de indisponibilidad

```text
INSUFFICIENT_WARMUP
MISSING_CONTRACT_MAPPING
ROLL_AMBIGUITY
NO_INTRADAY_PATH
INVALID_TICK_SIZE
ADX_DENOMINATOR_ZERO
ORDER_SEQUENCE_UNRESOLVED
```

## 11.9 Lineage

```text
continuous reference series
physical execution contract
roll rule
DMI implementation version
channel members
frozen target source
intraday fill source
stop calculations
```

---

## 12. Pseudocódigo de referencia

```python
from dataclasses import dataclass
from enum import Enum


class SetupState(Enum):
    NONE = 0
    LONG_PENDING = 1
    SHORT_PENDING = -1


@dataclass(frozen=True)
class DmiConfig:
    price_channel_length: int = 20
    dmi_length: int = 12
    adx_level: float = 15.0
    perc_range_long: float = 10.0
    perc_range_short: float = 10.0
    stop_loss_usd: float = 2_000.0
    long_trail_bars: int = 5
    short_trail_bars: int = 1


def create_setup(
    plus_di_prev: float,
    minus_di_prev: float,
    plus_di: float,
    minus_di: float,
    adx: float,
    close: float,
    channel_high: float,
    channel_low: float,
    cfg: DmiConfig,
):
    channel_range = channel_high - channel_low

    long_cross = plus_di_prev <= minus_di_prev and plus_di > minus_di
    short_cross = minus_di_prev <= plus_di_prev and minus_di > plus_di

    if adx <= cfg.adx_level:
        return None

    if long_cross:
        raw_target = close + channel_range * cfg.perc_range_long / 100.0
        return {
            "direction": "LONG",
            "raw_target": raw_target,
            "ttl_bars": 1,
        }

    if short_cross:
        raw_target = close - channel_range * cfg.perc_range_short / 100.0
        return {
            "direction": "SHORT",
            "raw_target": raw_target,
            "ttl_bars": 1,
        }

    return None
```

El engine de ejecución debe resolver gap-through y secuencia intrabar; no debe asumir fill automático al target.

---

## 13. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica de DMI

Reconciliar:

```text
+DI
-DI
ADX
cross timestamps
```

### Fase 2 — Réplica de targets

Comparar los niveles `BuyTarget` y `SellShortTarget` de las figuras y del workspace.

### Fase 3 — Réplica del checksum publicado

Objetivos aproximados:

```text
83 trades
PF 3.26
$148,220 net
43.37% ganadoras
```

### Fase 4 — Reproducción del grid 31×31

Reconstruir exactamente:

```text
PercRangeLE 0–30
PercRangeSE 0–30
```

Y verificar que `10/10` vuelve a ser el máximo sólo con el mismo feed y settings.

### Fase 5 — Verdadero OOS postpublicación

Congelar todos los defaults y probar después de mayo de 2015.

### Fase 6 — Contratos físicos

Repetir con:

```text
front contract gobernado
roll real
coste de roll
positions reconciliadas
```

### Fase 7 — Outlier audit

Informar:

```text
resultado completo
resultado sin mejor trade
contribución por año
contribución por régimen
```

### Fase 8 — Long/short

Evaluar independientemente:

```text
long-only
short-only
symmetric rules
asymmetric rules
```

### Fase 9 — Ablation

| Modelo | Pregunta |
|---|---|
| DMI cross sin ADX | ¿ADX aporta información? |
| DMI + ADX, market next open | ¿El price channel mejora el timing? |
| Price channel sin DMI | ¿DMI aporta algo? |
| DMI + ADX + channel sin trailing | ¿Los exits generan el edge? |
| Long-only | ¿Todo es una tendencia secular? |
| Random stop targets | ¿La distancia 10% es especial? |

### Fase 10 — Costes

```text
slippage por stop
spread
roll cost
adverse gap fills
```

### Fase 11 — Sensibilidad legítima

En vez de escoger el máximo:

```text
preservar todo el landscape
medir continuidad local
penalizar fronteras/picos
validar regiones en OOS
```

### Fase 12 — Multiple testing

Aplicar:

```text
Deflated Sharpe Ratio
PBO / CSCV
White Reality Check o Hansen SPA
block bootstrap
```

considerando todas las familias de inputs, no sólo el grid 961.

### Fase 13 — Regímenes

```text
bull/bear silver
volatilidad
inflación/deflación
trend strength
roll proximity
```

### Fase 14 — Entry TTL

Comparar:

```text
1 barra
2 barras
hasta siguiente DMI cross
```

como hipótesis separadas.

---

## 14. Variantes posteriores a la réplica

### Variante A — ADX rising

Añadir la condición narrativa:

```text
ADX_t > ADX_{t-1}
```

### Variante B — ADX percentile

Sustituir nivel fijo por percentil point-in-time.

### Variante C — Target normalizado por ATR

Evitar dependencia directa del canal de 20 barras.

### Variante D — Target simétrico

Congelar `PercRangeLE = PercRangeSE` para reducir grados de libertad.

### Variante E — Exits simétricos

Mismo trailing lookback para ambos lados.

### Variante F — Channel breakout clásico

Entrar directamente en high/low del canal para medir qué aporta el cierre ± porcentaje.

### Variante G — No-trade alrededor del roll

Excluir ventanas próximas al cambio de contrato.

### Variante H — DMI event library

Registrar el cruce y estudiar outcomes sin imponer la política de entrada publicada.

---

## 15. Encaje en Market State y Event State

### Market State

```text
plus_di
minus_di
adx
adx_slope
channel_high
channel_low
channel_width
normalized_channel_position
roll_proximity
contract_id
```

### Event State 1 — DMI cross

```text
event_type:
dmi_cross

direction:
plus_over_minus | minus_over_plus

confirmation_timestamp:
daily_close_t
```

### Event State 2 — Eligible setup

```text
adx_above_threshold
frozen_channel
frozen_target
order_ttl
```

### Event State 3 — Activation

```text
target_touched
gap_through
fill_price
fill_timestamp
```

### Outcomes

```text
forward_return
MFE
MAE
trend_duration
time_to_trailing_stop
time_to_opposite_cross
roll_interaction
```

### Distinción clave

```text
evento:
DMI ha cruzado con ADX elegible

estrategia:
esperar confirmación de precio, entrar stop y salir con stops asimétricos
```

---

## 16. Transferencia a small caps

Los elementos pueden traducirse, pero no los parámetros.

Posibles equivalentes:

```text
DMI cross intradía
ADX como trend-strength proxy
price channel relativo a intraday range
stop entry para exigir continuación
```

Riesgos específicos:

```text
halts
spread
news discontinuas
gap-through frecuente
short locate
SSR
liquidez variable
```

En small caps, el evento debe condicionarse por:

```text
news_catalyst_context
halt_context
short_side_context
liquidity
trading_activity
intraday_position
```

Uso recomendado:

```text
primero como Event State de cambio direccional
no como estrategia trasladada literalmente desde silver daily
```

---

## 17. Veredicto de Directional Movement Index

```text
IMPLEMENTAR:
sí, como candidato de state machine y stop-entry replay

ACEPTAR EDGE:
no

FORTALEZA:
reglas claras, paisaje 31×31 ampliamente positivo y payoff asimétrico

DEBILIDAD PRINCIPAL:
configuración publicada = máximo del grid, outlier del 30% y 95.8% del PnL en longs

RIESGO DE EJECUCIÓN:
alto por continuous futures, stops y secuencia intrabar

LIVE:
no
```

Gate propuesto:

```text
DMI-ADX-CHANNEL-PHYSICAL-CONTRACT-REPLICATION-OPTIMIZATION-AUDIT-AND-OOS-GATE
```

---
# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. Comparar iteraciones lado a lado

El artículo MACD compara:

```text
baseline convencional
vs.
variación propuesta
```

con mercado, periodo, tamaño y defaults comunes.

Lección TSIS:

> Toda modificación debe enfrentarse a la versión anterior mediante una ablation explícita, no sólo mostrar su propia curva.

## 2. Una mejora puede cambiar la forma del edge

MACD Turn mejora el win rate y reduce drawdown, pero reduce el ganador medio y el ratio win/loss.

No basta con mirar net profit.

## 3. Always-in requiere un contrato de reversión

```text
entrada contraria = exit + nueva entrada
```

Debe definirse como transición de posición, no como dos órdenes ambiguas.

## 4. Un indicador puede convertirse en evento

La revista cambia la interpretación del MACD sin cambiar su cálculo.

Esto encaja con TSIS:

```text
representación estable
+
diferentes eventos/policies sobre la misma representación
```

## 5. La etiqueta editorial no es ontología

`MACD Difference Turn` se etiqueta mean reversion, pero su regla es un breakout del histograma.

TSIS debe clasificar por fenómeno observable y mecanismo, no por nombre comercial.

## 6. Sensitivity analysis no equivale a OOS

Las superficies 3-D ayudan a distinguir:

```text
pico aislado
meseta
frontera
```

pero siguen usando la misma muestra.

## 7. El workspace es evidencia científica

El PDF muestra una superficie de `PercRangeLE/SE`. El `.tsw` permite recuperar:

```text
961 configuraciones
ranking exacto
punto publicado
landscape local
```

La auditoría de un paper práctico no debe limitarse al texto impreso.

## 8. Bloques duplicados no son nuevos trials

El stream DMI contiene dos copias idénticas y un bloque placeholder. Contarlos como 2,883 tests inflaría falsamente la búsqueda.

## 9. Trial ID puede codificar el grid

En este workspace:

```text
TrialID = 31 × SE + LE + 1
```

Esto permite verificar exhaustividad y ausencia de celdas faltantes.

## 10. Un ganador de grid necesita corrección de selección

`10/10` ocupa el puesto 1/961 por net profit.

El resultado debe evaluarse como máximo de una búsqueda, no como estimador insesgado.

## 11. Separar entry filter y exit engine

DMI combina:

```text
DMI/ADX = regime + direction
channel = confirmation
trailing/dollar stops = payoff shaping
```

Cada capa requiere ablation.

## 12. Narrativa y regla pueden divergir

El background habla de ADX creciente. La regla sólo pide ADX > 15.

TSIS debe registrar siempre:

```text
narrative hypothesis
formal rule
```

por separado.

## 13. Las órdenes stop exigen path intrabar

Daily OHLC no basta para saber:

```text
si entró
si salió después
si el stop monetario ocurrió antes
```

## 14. Continuous contract no es execution instrument

Debe utilizarse como referencia, nunca como fill source final.

## 15. Long/short no deben agregarse prematuramente

DMI parece excelente agregado, pero el short PF 1.18 apenas supera break-even antes de costes adicionales.

## 16. Un outlier debe etiquetarse

No se elimina automáticamente, pero se informa su contribución y se prueba estabilidad sin él.

## 17. Stop-loss landscape

La figura física 14 muestra `MyStopLoss` aproximadamente entre $500 y $4,900 y un área favorable alrededor de $2,000.

La gráfica es una idea de backtesting, no evidencia numérica recuperable exacta desde el paquete.

## 18. Overnight Ranges for Futures

La página física 3 presenta un indicador para:

```text
overnight high
overnight low
overnight close
breakout del overnight range durante day session
```

Clasificación:

```text
RESEARCH_NOTE
POTENTIAL_EVENT_STATE
NO_PUBLISHED_STRATEGY
NO_EDGE_EVIDENCE
```

Encaje potencial en TSIS:

```text
overnight_range
premarket_range
position_in_overnight_range
day_session_break
```

Para small caps, el análogo más útil sería el premarket range.

## 19. Fibonacci Retracement Channel

La página física 9 promociona canales basados en regresión lineal y niveles Fibonacci.

Clasificación:

```text
INDICATOR_CONCEPT
NO_RULESET
NO_BACKTEST
NO_EDGE_EVIDENCE
```

Posibles atributos:

```text
regression_slope
channel_width
normalized_channel_position
channel_break
```

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — MACD Turn como event-study rápido

Puede implementarse con la infraestructura actual de equities:

```text
daily o intraday bars
rolling indicators
next-bar execution
position reversal
```

Es ideal para validar:

```text
reconstrucción de indicadores
warm-up
next-bar legality
baseline ablation
postpublication OOS
```

### Prioridad B — DMI como gate de state machine y ejecución

Tiene mayor valor arquitectónico, pero exige:

```text
pending stop orders
intrabar replay
multiple exits
order priority
```

### Prioridad C — Réplica exacta en futures

Debe esperar a:

```text
physical futures data
contract reference
roll calendar
session templates
```

## 2. Estado respecto de los datos actuales de TSIS

### MACD Turn sobre equities

Posible con:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
013_ohlcv_1m_quote_guarded para ejecución intradía
```

según el timeframe elegido.

### DMI sobre equities

Posible como adaptación experimental, separando:

```text
adjusted signal view
raw execution view
```

### Réplica DMI sobre silver

No disponible hasta incorporar futures físicos.

### Overnight range

Para TSIS small caps puede reinterpretarse con:

```text
premarket OHLC
premarket volume
premarket high/low break
```

## 3. Artefactos futuros derivados

Cuando se abran los gates:

```text
SCC_2015_05_MACD_TURN_REPLICATION_CONTRACT.md
SCC_2015_05_DMI_ADX_CHANNEL_REPLICATION_CONTRACT.md
```

No deben crearse ahora como resúmenes duplicados.

## 4. Material adicional necesario para réplica exacta

El archivo `.7z` es suficiente para cerrar la auditoría documental.

Al abrir implementación sería útil solicitar o exportar:

```text
EasyLanguage source como texto
Trade Lists completas
Strategy Properties
MaxBarsBack
session templates
bid/ask settings de EURUSD
slippage settings
LIBB order sequence settings
optimization reports de MyStopLoss y DMI/ADX
physical-contract roll map
```

Sólo debe pedirse cuando se abra el gate correspondiente.

---

# Apéndice A — Integridad del paquete

## Archivos relevantes

```text
SCC Issue 5 May 2015.pdf
2015-05.7z

2015-05/MACD/TSL MACD DIFFERENCE TURN.ELD
2015-05/MACD/TSL MACD DIFFERENCE_INDICATOR UPDATE.ELD
2015-05/MACD/TSL.MACD Difference Turn.tsw

2015-05/Directional Movement/TSL DIRECTIONAL MOVEMENT INDEX.ELD
2015-05/Directional Movement/TSL Directional Movement Index.tsw
```

El PDF incluido dentro del `.7z` es bit a bit idéntico al PDF cargado por separado.

## Tamaños

```text
PDF: 5,696,069 bytes
7z: 5,930,433 bytes
MACD strategy .ELD: 16,408 bytes
MACD indicator .ELD: 16,994 bytes
MACD workspace .tsw: 27,648 bytes
DMI .ELD: 19,047 bytes
DMI workspace .tsw: 1,905,664 bytes
```

## SHA-256

```text
PDF:
1f2f083cbb722a33214c87638a2e2bbc492bfc058fd8fa7f8d2704da8e3fe240

7z:
60c4f7fb390152d4a0fc6bad492e0f70d910ff067e602e1b69369682f03a89b6

MACD strategy .ELD:
9b0ca25a6f67b8f9ee26638f584fcfe0ea44bb7b5a2f642b3f4e06a8b9d7fb09

MACD indicator .ELD:
e11bd92a8a8cd2623b9d3f94fae2ba1019bfd5d3f1938bda14c1a40de0251256

MACD workspace .tsw:
d3b9c617f24c420a126627072bd28c6c795e68a3abc359e25afd5dc0274ab953

DMI .ELD:
aeadda0be4541412d9eb882e842926ae80e9ce02d75b4d6a9fadb7696186e9db

DMI workspace .tsw:
6a5480c995ef12b2215fa228ffadcb507c5e462a2c6a747cacb481246d7be374
```

## Metadata PDF

```text
Title: no expuesto por pdfinfo
Creator: Adobe InDesign CC 2014 (Windows)
Producer: Adobe PDF Library 11.0
Pages: 15
CreationDate: 12 de mayo de 2015, 14:41:44 UTC
ModificationDate: 12 de octubre de 2015, 18:15:47 UTC
PDF version: 1.7
Encrypted: sí; impresión permitida, copia deshabilitada
```

## Evidencia binaria MACD

```text
workspace OLE size:
27,648 bytes

chart:
EURUSD 120 min

techniques:
MACD LE
MACD SE
MACD
TSL:MACD Difference
TSL:MACD Differrence Turn

OptimizationData:
no presente con resultados
```

## Evidencia binaria DMI

```text
workspace OLE size:
1,905,664 bytes

OptimizationData:
1,741,541 bytes

unique configurations:
961

lattice:
PercRangeLE 0–30
PercRangeSE 0–30

blocks:
2 completos idénticos
1 placeholder

published configuration:
10 / 10

net-profit rank:
1 / 961
```

## Limitación del paquete

```text
.tsw:
workspace OLE con metadatos, inputs y parte de la optimización recuperables

.ELD:
contenedor propietario no legible como source EasyLanguage
en este entorno
```

No contiene exportaciones legibles de:

```text
source code
trade lists
fill logs
session properties
optimization objective global
DMI/ADX sensitivity raw table
stop-loss sensitivity raw table
```

---

# Cierre del issue

El Issue 5 debe conservarse en TSIS como dos lecciones institucionales:

```text
MACD Difference Turn:
una representación conocida puede producir eventos alternativos,
pero una comparación favorable de dos años no demuestra generalización

Directional Movement Index:
un trend system por capas necesita estado persistente,
replay intradía y auditoría del espacio de búsqueda;
el punto publicado fue el ganador 1/961 por net profit
```

Decisión final:

```text
ARCHIVE_STATUS:
AUDITED_COMPLETE

MACD_TURN_STATUS:
INDICATOR_EVENT_AND_REVERSAL_REPLICATION_CANDIDATE

DMI_STATUS:
MULTI_STAGE_STOP_ENTRY_AND_PHYSICAL_FUTURES_REPLICATION_CANDIDATE

EDGE_ACCEPTED:
NO

ADDITIONAL_SOURCE_NEEDED_NOW:
NO

NEXT_ACTION:
ARCHIVE AND CONTINUE WITH ISSUE 6
```
