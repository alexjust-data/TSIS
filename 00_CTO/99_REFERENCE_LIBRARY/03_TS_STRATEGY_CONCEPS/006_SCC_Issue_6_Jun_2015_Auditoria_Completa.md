# Auditoría completa — TradeStation Strategy Concepts Club, Issue 6 (junio de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. Asymmetric Channel Breakout (ACB) Strategy
2. The Final Thirty Strategy
3. la corrección editorial relativa al indicador MACD Difference del Issue 5
4. ideas secundarias de backtesting presentes en el número
5. auditoría temporal, matemática y metodológica
6. evidencia adicional contenida en los workspaces y contenedores .ELD
7. forense del OptimizationData conservado en el workspace Final Thirty
8. contratos de réplica para TSIS
9. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 14 páginas: `SCC Issue 6 Jun 2015(1).pdf`.
- Archivo original de apoyo: `2015-06.zip`.
- PDF duplicado incluido dentro del ZIP.
- Dos contenedores `.ELD`:
  - `TSL ASYMMETRIC CHANNEL BREAKOUT.ELD`;
  - `TSL FINAL THIRTY.ELD`.
- Dos workspaces `.tsw`:
  - `TSL Asymmetric Channel Breakout.tsw`;
  - `TSL.Final Thirty.tsw`.
- Imágenes renderizadas de las 14 páginas, incluidas:
  - el ejemplo de transición trend-following → mean-reversion de ACB en la página física 5;
  - la tabla de resultados y la curva de capital ACB de la página física 7;
  - la comparación de ACB con el breakout simétrico y la superficie de sensibilidad de la página física 8;
  - la definición horaria de Final Thirty en las páginas físicas 10–11;
  - los cuatro informes de rendimiento de Final Thirty en las páginas físicas 12–14.
- Los Markdown de los Issues 1–5 se utilizan únicamente como **modelo de profundidad y organización**, nunca como autoridad factual para este número.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF, los workspaces .tsw,
los streams OLE y los contenedores .ELD

AUDIT:
inferencia técnica, crítica científica
y propuesta de implementación en TSIS
```

Cuando el PDF o el paquete no resuelven una decisión, se registra como ambigüedad. No se completa silenciosamente.

No se ha incorporado investigación web externa sobre las estrategias. Las fórmulas que no aparecen literalmente en el PDF se presentan como reconstrucciones funcionales o candidatos de implementación.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo real | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 011 | Asymmetric Channel Breakout | State machine asimétrica: breakout trend-following en una dirección y reversión mean-reversion en la contraria | NQ 180 min; $45,452.88; PF 1.34; 921 trades; RINA 92.70 | el workspace confirma `1/5/6/3/750`, pero **no conserva OptimizationData**; el resultado publicado queda a sólo $0.75 del máximo declarado de la búsqueda long-emphasis | candidato de réplica arquitectónicamente valioso, pero resultado claramente postseleccionado |
| 012 | Final Thirty | Clasificador intradía de tres estados —long, short o no trade— y operación durante la última media hora | SPY 30 min; tras optimización conjunta: $2,997; PF 1.65; 391 trades; 51.92% ganadoras | el workspace contiene SPY y `@ES.D`; conserva un grid de **29,952 candidatos** para ES, del que sólo se guardan los 200 mejores, duplicados dos veces más un bloque placeholder | prioridad alta como event study para TSIS; no aceptar el backtest optimizado como prueba de edge |

## 0.1 Veredicto global

El Issue 6 contiene dos ideas especialmente relevantes para TSIS.

`Asymmetric Channel Breakout` rompe con la costumbre de usar reglas espejo para largos y cortos. El lado enfatizado sigue un breakout; la posición contraria sólo aparece como respuesta condicionada al agotamiento de la operación primaria. Por tanto, no es una estrategia de dos lados independientes, sino una **máquina de estados con dependencia causal entre trades**.

`Final Thirty` estudia una hipótesis temporal muy concreta: si la dirección y magnitud del movimiento acumulado hasta las 15:30, junto con el volumen acumulado, ayudan a predecir los últimos 30 minutos. Esta idea encaja directamente con la futura Event Library de TSIS. Sin embargo, la revista la somete a tres rondas de optimización sobre la misma muestra. El paquete revela además un grid adicional de 29,952 combinaciones sobre `@ES.D`.

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

# Parte I — Estrategia 011: Asymmetric Channel Breakout (ACB)

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-06-STRAT-011`
- **Revista:** *Strategy Concepts Club* — TradeStation Labs
- **Issue:** 6
- **Fecha declarada:** junio de 2015
- **Artículo:** *Asymmetric Channel Breakout (ACB) Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 3–8
- **Páginas impresas del artículo:** 2–7
- **Estilo declarado:** mezcla de trend following y mean reversion
- **Mercados declarados:** equities, futures, forex
- **Horizonte declarado:** swing trading
- **Mercado del backtest publicado:** E-mini Nasdaq-100 custom continuous contract
- **Símbolo:** `@NQ=107XN`
- **Frecuencia:** 180 minutos
- **Periodo:** cinco años, terminando el 31 de marzo de 2015
- **Tamaño:** un contrato
- **Capital inicial:** $10,000
- **Comisión:** $2.36 por lado y contrato
- **Stop monetario:** $750

### Inputs publicados y confirmados por el workspace

| Input | Default | Función |
|---|---:|---|
| `Long_or_Short_Emphasis` | 1 | 1 enfatiza largos; 2 enfatiza cortos |
| `Chan_Length` | 5 | longitud del canal de precios |
| `Trail_Stop_Length` | 6 | ventana del extremo que revierte la operación primaria |
| `Secondary_Hold_Length` | 3 | duración de la operación secundaria |
| `My_Stop_Loss` | 750 | stop monetario por operación |

### Evidencia adicional del ZIP

El workspace confirma:

```text
chart:
@NQ=107XN 180 min [CME]
E-Mini NASDAQ-100 Custom Continuous Contract

analysis techniques:
TSL:Asymmetric Channel Breakout — indicador
TSL:Asymmetric Channel Breakout — estrategia

active inputs:
Long_or_Short_Emphasis = 1
Chan_Length = 5
Trail_Stop_Length = 6
Secondary_Hold_Length = 3
My_Stop_Loss = 750
```

El archivo `.tsw` no contiene un stream `OptimizationData` con las 9,600 configuraciones mencionadas por cada énfasis. El stream `optdatafile` existe, pero está vacío.

El `.ELD` es un contenedor propietario y no expone el source EasyLanguage como texto legible. La estrategia puede reconstruirse funcionalmente, pero no certificarse línea por línea.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, como máquina de estados. |
| ¿Puede replicarse aproximadamente? | **Sí**, con el PDF y el workspace. |
| ¿Puede replicarse exactamente? | **No todavía.** Faltan source, lista de trades y semántica exacta de ventanas y tiempo de salida. |
| ¿El artículo demuestra edge? | **No.** El lado de énfasis y los parámetros fueron elegidos tras búsquedas amplias. |
| ¿La idea es económicamente plausible? | **Sí:** persistencia del breakout y reversión breve tras agotamiento. |
| ¿Es realmente una estrategia long/short simétrica? | **No.** El trade contrario depende de que antes haya existido una posición primaria. |
| ¿Está preparada para operar? | **No.** Falta modelar slippage, contratos físicos, rolls y stops intrabar. |
| ¿Merece estudiarse? | **Sí.** Es una excelente prueba de state machine y de reglas asimétricas. |

Clasificación TSIS:

```text
ASYMMETRIC_CHANNEL_STATE_MACHINE
PRIMARY_TREND_FOLLOWING_LEG
CONDITIONAL_SECONDARY_MEAN_REVERSION_LEG
NEXT_BAR_OPEN_EXECUTION
TIME_EXIT_ON_SECONDARY_POSITION
DOLLAR_STOP
OPTIMIZED_IN_SAMPLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La descripción superficial sería:

```text
breakout de canal
```

Pero la política completa es:

```text
1. escoger de antemano una dirección primaria;
2. entrar por breakout sólo en esa dirección;
3. mantener la operación primaria mientras persiste;
4. cuando aparece un extremo contrario, no salir a flat:
   revertir la posición;
5. mantener la posición secundaria sólo tres barras;
6. volver a flat y esperar un nuevo breakout primario.
```

Con `Long_or_Short_Emphasis = 1`:

```text
primary leg:
long trend following

secondary leg:
short mean reversion condicionado
al agotamiento del long previo
```

Con `Long_or_Short_Emphasis = 2` ocurre lo contrario.

Esto tiene una consecuencia científica decisiva:

> Los trades secundarios no constituyen una muestra independiente de señales short o long. Son outcomes condicionados por la historia de una operación primaria.

Por ello, las columnas “Long Trades” y “Short Trades” del informe no deben interpretarse como dos estrategias direccionales paralelas.

---

## 3. Reconstrucción matemática

## 3.1 Canal de precios

Sea `L = Chan_Length`.

La reconstrucción operativamente coherente es:

\[
HighChannel_t=\max(H_{t-1},H_{t-2},\ldots,H_{t-L})
\]

\[
LowChannel_t=\min(L_{t-1},L_{t-2},\ldots,L_{t-L})
\]

La exclusión de la barra actual no está escrita de forma algebraica en el PDF, pero es la interpretación necesaria para que un cierre pueda cruzar por encima del máximo del canal o por debajo de su mínimo. Si la barra actual se incluyera, `Close_t > Highest(High_t,...)` sería prácticamente imposible.

Esta decisión debe confirmarse con source o señales históricas.

## 3.2 Breakout primario

Con énfasis long:

\[
PrimaryLongSetup_t=CrossOver(C_t,HighChannel_t)
\]

La entrada se ejecuta:

\[
EntryTime=Open_{t+1}
\]

Con énfasis short:

\[
PrimaryShortSetup_t=CrossUnder(C_t,LowChannel_t)
\]

con ejecución en la apertura siguiente.

## 3.3 Reversal del trade primario

Sea `T = Trail_Stop_Length`.

Para una posición primaria long, la revista exige:

```text
Close por debajo de HighChannel
+
Low rompe el menor low reciente
```

La reconstrucción coherente es:

\[
PriorLowest_t=\min(L_{t-1},\ldots,L_{t-T})
\]

\[
ReverseToShort_t=
Position_t=LONG
\land C_t<HighChannel_t
\land L_t<PriorLowest_t
\]

Se ejecuta una reversión en `Open_{t+1}`.

La ventana debe excluir la barra actual. De lo contrario, la condición estricta `Low_t < Lowest(Low, T)` no podría cumplirse.

Para énfasis short:

\[
PriorHighest_t=\max(H_{t-1},\ldots,H_{t-T})
\]

\[
ReverseToLong_t=
Position_t=SHORT
\land C_t>LowChannel_t
\land H_t>PriorHighest_t
\]

## 3.4 Operación secundaria

La posición secundaria no utiliza un nuevo breakout del canal. Nace únicamente de la reversión de la posición primaria.

Con `Secondary_Hold_Length = 3`, la intención editorial es:

```text
mantener la operación secundaria tres barras
y salir mediante market order
```

Queda una ambigüedad de una barra:

```text
A. salir en la apertura de la tercera barra después de entrar;
B. salir en la apertura posterior a completar tres barras;
C. utilizar BarsSinceEntry = 3, cuya traducción exacta depende del código.
```

El PDF dice “on the third bar after entry” y también “on the opening of the third bar after entry”. La réplica debe resolverlo mediante checksum contra las marcas del gráfico o la Trade List.

## 3.5 Stop monetario

Todas las posiciones pueden cerrarse por un stop de $750.

Conceptualmente:

\[
PnL^{unrealized}_t \le -750
\Rightarrow ExitStop
\]

El mayor trade perdedor publicado es:

```text
all trades:  -$809.72
long trades: -$809.72
short trades:-$754.72
```

Por tanto, el stop no limita de forma garantizada la pérdida a $750. El exceso puede proceder de gap-through, discretización por tick, comisión o lógica de fill del motor.

## 3.6 Máquina de estados

Para énfasis long:

```text
FLAT
  ↓ breakout superior
PRIMARY_LONG
  ↓ reversal condition
SECONDARY_SHORT
  ↓ time exit
FLAT
```

Cualquier estado puede transitar a `FLAT` por stop monetario.

Para énfasis short:

```text
FLAT
  ↓ breakout inferior
PRIMARY_SHORT
  ↓ reversal condition
SECONDARY_LONG
  ↓ time exit
FLAT
```

No debe implementarse como una colección de condiciones aisladas. El mismo patrón de precio tiene significados diferentes según el estado previo.

## 3.7 Warm-up

El mínimo teórico depende de:

```text
max(Chan_Length, Trail_Stop_Length)
```

pero una réplica debe incluir además:

```text
MaxBarsBack real del estudio
historial previo al periodo reportado
roll y session template
```

---

## 4. Reglas operativas reconstruidas

### Modo 1 — Long emphasis

#### Entrada primaria long

```text
si Close cruza sobre HighChannel:
    comprar en la apertura de la barra siguiente
```

#### Reversal a short

```text
si existe PRIMARY_LONG
AND Close < HighChannel
AND Low rompe el menor Low de las T barras previas:
    cerrar long
    abrir short en la apertura siguiente
```

#### Salida secundaria

```text
si existe SECONDARY_SHORT
AND se alcanza Secondary_Hold_Length:
    cubrir en market según la convención temporal fijada
```

#### Stop

```text
stop monetario de $750 en primary y secondary
```

### Modo 2 — Short emphasis

Es el espejo de estados, no un sistema simultáneo:

```text
breakout inferior → PRIMARY_SHORT
agotamiento superior → SECONDARY_LONG
time exit → FLAT
```

---

## 5. Resultados publicados

## 5.1 Configuración del backtest

```text
Símbolo: @NQ=107XN
Frecuencia: 180 minutos
Historia: 5 años, terminando 31/03/2015
Capital inicial: $10,000
Tamaño: 1 contrato
Comisión: $2.36 por lado
Stop: $750
Look-Inside-Bar Back-Testing: no utilizado
Emphasis: long
```

El continuous contract no está back-adjusted y realiza el rollover siete sesiones antes del vencimiento.

## 5.2 Resultado agregado

| Métrica | Resultado |
|---|---:|
| Net Profit | $45,452.88 |
| Gross Profit | $178,242.36 |
| Gross Loss | -$132,789.48 |
| Profit Factor | 1.34 |
| Trades | 921 |
| Percent Profitable | 47.45% |
| Winning Trades | 437 |
| Losing Trades | 484 |
| Avg. Trade Net Profit | $49.35 |
| Avg. Winning Trade | $407.88 |
| Avg. Losing Trade | -$274.36 |
| Ratio Avg. Win / Avg. Loss | 1.49 |
| Largest Winning Trade | $3,455.28 |
| Largest Losing Trade | -$809.72 |
| Max. Consecutive Wins | 8 |
| Max. Consecutive Losses | 8 |
| Avg. Bars in Winners | 9.96 |
| Avg. Bars in Losers | 4.92 |
| Account Size Required | $5,563.16 |
| Return on Initial Capital | 454.53% |
| Annual Rate of Return | 34.37% |
| Return Retracement Ratio | 0.55 |
| RINA Index | 92.70 |
| Time in Market | 59.88% |

## 5.3 Primary long frente a secondary short

| Métrica | Long / primary | Short / secondary |
|---|---:|---:|
| Net Profit | $33,443.84 | $12,009.04 |
| Profit Factor | 1.37 | 1.29 |
| Trades | 478 | 443 |
| Percent Profitable | 44.56% | 50.56% |
| Avg. Trade Net Profit | $69.97 | $27.11 |
| Avg. Winning Trade | $583.82 | $240.57 |
| Avg. Losing Trade | -$343.06 | -$191.23 |
| Avg. Bars in Winners | 17.29 | 3.00 |
| Avg. Bars in Losers | 6.62 | 2.85 |
| Largest Losing Trade | -$809.72 | -$754.72 |

El reparto del beneficio es:

```text
primary longs:   73.58%
secondary shorts:26.42%
```

La similitud de los Profit Factors no implica simetría. El trade long persigue tendencias; el short sólo aparece después de una condición de agotamiento y tiene una salida temporal.

## 5.4 Coste implícito y fragilidad

La expectativa publicada es:

```text
$49.35 por trade agregado
$69.97 por long primario
$27.11 por short secundario
```

El break-even frente a costes adicionales es, por definición, el promedio por trade.

Ejemplos de sensibilidad puramente aritmética:

| Coste adicional round trip | Reducción sobre 921 trades | Porcentaje del net profit |
|---:|---:|---:|
| $5 | $4,605 | 10.13% |
| $10 | $9,210 | 20.26% |
| $20 | $18,420 | 40.52% |

El artículo no modela slippage. La pata secundaria, con $27.11 por operación, es mucho más vulnerable.

## 5.5 Curva de capital

La curva de la página física 7 es visualmente ascendente y relativamente lineal, aunque presenta:

```text
periodos planos
retrocesos intermedios
un máximo semanal aproximado del 25%
```

La comparación de la página física 8 muestra que la versión asimétrica es más estable que un breakout de canal simétrico. El texto afirma que:

```text
los longs son casi idénticos en ambas versiones;
los shorts son negativos en la versión simétrica;
los shorts condicionados son positivos en ACB.
```

Esto sugiere que la mejora no procede de alterar el motor long, sino de reemplazar el short breakout independiente por una reversión condicionada.

---

## 6. Auditoría de la optimización publicada

## 6.1 Dos búsquedas de 9,600 configuraciones

La revista declara:

```text
9,600 combinaciones con emphasis long
9,600 combinaciones con emphasis short
```

Por tanto, la decisión de elegir el énfasis long no fue previa a la muestra. Se tomó después de comparar dos familias amplias.

## 6.2 Truncamiento a 8,000 filas

TradeStation guardaba como máximo 8,000 combinaciones por informe. La tabla del artículo utiliza esas filas guardadas.

| Métrica | Long emphasis | Short emphasis |
|---|---:|---:|
| Profitable tests entre filas guardadas | 100% | 15.26% |
| Avg. Net Profit en tests positivos | $22,166.69 | $4,381.29 |
| Avg. Net Profit en tests negativos | N/A | -$9,116.92 |
| Highest Net Profit | $45,453.63 | $31,594.53 |
| Lowest Net Profit guardado | $3,095.86 | -$28,490.60 |
| Avg. Max Intraday Drawdown | -$7,233.35 | -$20,210.72 |

La afirmación “100% profitable” no describe necesariamente las 9,600 combinaciones. Describe las 8,000 retenidas. Quedan 1,600 resultados fuera del artefacto.

Como mínimo:

```text
8,000 / 9,600 = 83.33%
```

sí están documentados como positivos en el lado long. El estado de los 1,600 omitidos no puede recuperarse.

## 6.3 El resultado publicado está prácticamente en el máximo

El informe de rendimiento muestra:

```text
$45,452.88
```

La tabla de optimización declara un máximo long de:

```text
$45,453.63
```

Diferencia:

```text
$0.75
0.00165% del máximo
```

Aunque no se puede garantizar que ambos números procedan de una ejecución bit a bit idéntica, científicamente el resultado publicado debe tratarse como una configuración **prácticamente maximizada in-sample**.

## 6.4 Sensitivity plot

La superficie de la página física 8 examina:

```text
Chan_Length
versus
Trail_Stop_Length
```

La revista describe una meseta favorable y sitúa `5/6` cerca de una pequeña cumbre. Esto es mejor que un pico aislado, pero no elimina:

```text
selección de lado
selección de parámetros
selección de mercado
selección de periodo
```

El workspace entregado no conserva la matriz numérica de esa superficie.

---

## 7. ¿Dónde podría estar el edge?

La hipótesis puede separarse en dos mecanismos.

### 7.1 Persistencia del breakout primario

```text
un cierre que supera un extremo reciente
puede identificar una tendencia con continuación
```

### 7.2 Reversión tras agotamiento

```text
tras una operación primaria extendida,
un nuevo extremo contrario
más retorno del cierre dentro del canal
puede indicar agotamiento y rebote/reversión breve
```

La combinación es coherente:

```text
trend persistence
+
conditional exhaustion reversal
```

Pero el documento no demuestra cuál aporta el resultado. Se necesita una ablation:

```text
A. primary breakout solo
B. secondary reversal solo como event study
C. ACB completo
D. breakout simétrico
E. primary exit a flat sin reversal
```

La comparación gráfica sólo cubre parcialmente C frente a D.

---

## 8. Problemas científicos y técnicos

## 8.1 Selección del énfasis

Long y short emphasis fueron optimizados por separado. Elegir el mejor es un grado de libertad adicional.

## 8.2 Múltiples pruebas

Se ejecutaron al menos 19,200 combinaciones declaradas. El resultado no incluye corrección por búsqueda múltiple.

## 8.3 Parámetros cerca del máximo

El net profit publicado está a $0.75 del máximo long declarado.

## 8.4 Ausencia de out-of-sample

No se publica:

```text
train/test split
walk-forward
purged validation
postpublication test
```

## 8.5 Continuous contract sintético

`@NQ=107XN` sirve como referencia histórica, pero no es un contrato ejecutable.

Hay que resolver:

```text
roll dates
contrato activo
trades que cruzan roll
price discontinuities
commission and slippage per physical leg
```

## 8.6 No back adjustment

Evita fills sobre precios desplazados artificialmente, pero introduce saltos de roll que pueden:

```text
crear o cancelar breakouts
activar stops
alterar la duración de una posición
```

## 8.7 Canal y look-ahead

El PDF no escribe explícitamente `[1]`. La exclusión de la barra actual es inferida. Una implementación que incluyera la barra actual produciría una estrategia distinta.

## 8.8 Trigger de reversal

La frase “lower than the lowest low for the last 6 bars” también requiere excluir la barra actual. Debe congelarse contractualmente.

## 8.9 Off-by-one del time exit

“Third bar after entry” admite más de una traducción en EasyLanguage y en un motor event-driven.

## 8.10 Stop sin LIBB

La revista dice que no usa Look-Inside-Bar porque las órdenes son market en la apertura. Sin embargo, también declara un dollar stop. Si éste es intrabar, OHLC de 180 minutos no resuelve la secuencia ni el fill real.

## 8.11 Slippage cero/no declarado

La comisión está incluida, pero no se publica slippage. Con 921 trades, pequeños costes cambian materialmente el resultado.

## 8.12 Dependencia del periodo

El backtest coincide con un periodo concreto de NQ. No se demuestra estabilidad en otros regímenes.

## 8.13 Samples acoplados

Los shorts de la versión long-emphasis sólo existen después de longs. No son comparables a una estrategia short independiente.

## 8.14 Stop no garantizado

La pérdida máxima supera el input de $750.

## 8.15 Capital inicial

Un retorno de 454.53% sobre $10,000 no debe confundirse con escalabilidad. El tamaño permanece fijo en un contrato.

## 8.16 Surface analysis sigue siendo in-sample

Una meseta ayuda a diagnosticar fragilidad, pero no prueba generalización.

---

## 9. Implementación en TSIS

## 9.1 Separar representación y política

Market State debe exponer:

```text
high_channel_L
low_channel_L
close_cross_high_channel
close_cross_low_channel
prior_lowest_T
prior_highest_T
position_state
bars_in_secondary
```

La policy decide:

```text
qué dirección es primaria
si se permite reversal
cuánto dura la secundaria
cómo se aplica el stop
```

## 9.2 Estado persistente

Campos mínimos:

```text
strategy_instance_id
emphasis
position_phase
entry_timestamp
entry_price
bars_since_entry
primary_origin_event_id
pending_action
```

## 9.3 Contratos físicos

Para futures:

```text
signal_reference = continuous governed view
execution_instrument = physical contract
roll_policy = explicit
```

## 9.4 Ejecución

Las señales de cierre se ejecutan en la apertura siguiente. El stop requiere replay intrabar gobernado.

## 9.5 Estado de indisponibilidad

```text
insufficient_warmup
roll_transition_unresolved
physical_contract_missing
bar_gap
stop_path_ambiguous
```

No deben convertirse silenciosamente en no-trade.

## 9.6 Lineage

Cada trade debe conservar:

```text
channel values
prior extrema
state before
trigger condition
state after
continuous reference row
physical fill rows
roll metadata
```

---

## 10. Pseudocódigo de referencia

```python
from enum import Enum


class Phase(str, Enum):
    FLAT = "flat"
    PRIMARY_LONG = "primary_long"
    PRIMARY_SHORT = "primary_short"
    SECONDARY_LONG = "secondary_long"
    SECONDARY_SHORT = "secondary_short"


def on_bar_close(state, bar, history, params):
    high_channel = max(x.high for x in history[-params.chan_length:])
    low_channel = min(x.low for x in history[-params.chan_length:])

    prior_lowest = min(x.low for x in history[-params.trail_length:])
    prior_highest = max(x.high for x in history[-params.trail_length:])

    if state.phase == Phase.FLAT:
        if params.emphasis == "long":
            if crossed_over(bar.close, high_channel, state.previous_close,
                            state.previous_high_channel):
                schedule_next_open("buy", role="primary")

        elif params.emphasis == "short":
            if crossed_under(bar.close, low_channel, state.previous_close,
                             state.previous_low_channel):
                schedule_next_open("sell_short", role="primary")

    elif state.phase == Phase.PRIMARY_LONG:
        if bar.close < high_channel and bar.low < prior_lowest:
            schedule_next_open("reverse_to_short", role="secondary")

    elif state.phase == Phase.PRIMARY_SHORT:
        if bar.close > low_channel and bar.high > prior_highest:
            schedule_next_open("reverse_to_long", role="secondary")

    elif state.phase in {Phase.SECONDARY_LONG, Phase.SECONDARY_SHORT}:
        if state.bars_since_entry >= params.secondary_hold_length:
            schedule_exit_according_to_frozen_time_convention()

    update_previous_values(state, bar, high_channel, low_channel)


def on_intrabar_price(state, executable_price, contract):
    unrealized = mark_to_market(state, executable_price, contract)
    if unrealized <= -state.stop_loss_dollars:
        execute_protective_stop_with_path_and_gap_rules()
```

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Réplica de canales

Verificar manualmente:

```text
channel excludes current bar
cross dates
reversal extrema
```

### Fase 2 — Réplica de state transitions

Reconciliar las marcas de la figura 2:

```text
primary long entry
reversal to secondary short
time exit
```

### Fase 3 — Checksum del informe

Objetivo aproximado:

```text
921 trades
478 long
443 short
$45,452.88
PF 1.34
```

### Fase 4 — Reproducir el breakout simétrico

Confirmar si la mejora procede exclusivamente de la pata secundaria.

### Fase 5 — Ablation del reversal

Comparar:

```text
exit to flat
vs.
reverse to secondary
```

### Fase 6 — Verdadero OOS postpublicación

Congelar la especificación a junio de 2015 y evaluar desde la primera sesión posterior disponible.

### Fase 7 — Contratos físicos

Repetir con contratos reales y roll policy.

### Fase 8 — Costes

Escenarios de coste round trip:

```text
$0 adicional
$5
$10
$20
$30
```

### Fase 9 — Long/short emphasis preregistrado

No volver a elegir el lado después de mirar el OOS.

### Fase 10 — Sensibilidad legítima

Evaluar mesetas sin seleccionar el nuevo máximo.

### Fase 11 — Multiple testing

Aplicar control por búsqueda a la familia completa, no sólo al punto elegido.

### Fase 12 — Regímenes

Separar:

```text
bull trend
bear trend
high volatility
low volatility
roll windows
```

### Fase 13 — Stop path

Reproducir con resoluciones intrabar crecientes.

### Fase 14 — Secondary horizon

Estudiar el event outcome antes de optimizar `Secondary_Hold_Length`.

---

## 12. Variantes posteriores a la réplica

### Variante A — Exit to flat

Eliminar el reversal y medir el valor incremental de la pata secundaria.

### Variante B — Secondary entry normalizada

Usar ruptura en ATR o volatilidad en vez de barras fijas.

### Variante C — Secondary outcome event study

No operar; medir retornos futuros tras agotamiento.

### Variante D — Emphasis dinámico preregistrado

Seleccionar dirección mediante un régimen conocido ex ante, no por optimización retrospectiva.

### Variante E — Stop ATR

Sustituir $750 fijo por riesgo normalizado.

### Variante F — Secondary exit por convergencia

Salir cuando precio vuelve al canal o a VWAP, no por una duración arbitraria.

### Variante G — No-trade en roll

Excluir ventanas próximas al rollover.

---

## 13. Encaje en Market State y Event State

### Market State

```text
high_channel_5
low_channel_5
prior_lowest_6
prior_highest_6
channel_width
close_position_in_channel
volatility_state
session_state
```

### Event State 1 — Primary breakout

```text
event_type:
price_channel_breakout

direction:
long or short

decision_timestamp:
bar_close_t
```

### Event State 2 — Conditional exhaustion

```text
event_type:
post_breakout_counter_extreme

parent_event_id:
primary breakout

required_state:
active primary position
```

### Outcome

```text
return_1_bar
return_3_bars
MFE
MAE
channel_reentry
continuation_length
secondary_reversion_return
```

La distinción clave es:

```text
fenómeno 1:
breakout

fenómeno 2:
agotamiento condicionado

policy:
seguir tendencia y después revertir
```

---

## 14. Transferencia a small caps

No trasladaría la estrategia completa directamente, pero sí sus eventos.

En small caps:

```text
breakouts pueden coincidir con noticias y halts;
los short secundarios pueden no ser borrowable;
el canal puede romperse por gaps discontinuos;
los stops monetarios pueden sufrir slippage extremo.
```

La adaptación útil sería:

```text
primary event:
HOD/channel breakout en stock in play

conditional exhaustion event:
fallo del breakout + ruptura de microestructura

outcomes:
continuation, fade, halt, liquidity collapse
```

Objetos TSIS relevantes:

```text
price_movement
volatility_range_state
liquidity
trading_activity
intraday_position
news_catalyst_context
halt_context
short_side_context
```

---

## 15. Veredicto de ACB

```text
IMPLEMENTAR:
sí, como state-machine reproduction candidate

ACEPTAR COMO EDGE:
no

OPTIMIZAR:
no antes del OOS congelado

OPERAR EN REAL:
no

MAYOR VALOR PARA TSIS:
modelar dependencia entre evento primario,
posición y evento secundario
```

Gate propuesto:

```text
ACB-ASYMMETRIC-STATE-MACHINE-PHYSICAL-CONTRACT-REPLICATION-AND-OOS-GATE
```

---

# Parte II — Estrategia 012: The Final Thirty Strategy

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-06-STRAT-012`
- **Artículo:** *The Final Thirty Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas:** 10–14
- **Páginas impresas:** 9–13
- **Estilo declarado:** Trend following
- **Mercados declarados:** ETFs e index futures broad-based
- **Horizonte:** Day trading
- **Mercado principal publicado:** SPY
- **Frecuencia:** 30 minutos
- **Periodo:** cinco años, terminando 31 de marzo de 2015
- **Tamaño:** 100 acciones
- **Comisión:** $0.01 por acción
- **Holding:** última media hora de la sesión regular
- **Overnight:** no

### Inputs

| Input | Default | Función |
|---|---:|---|
| `PositiveDayChange` | 0 | mínimo cambio porcentual para long |
| `NegativeDayChange` | 0 | máximo cambio porcentual para short |
| `UseDayChange_1_AndVolume_2` | 1 | 1 precio; 2 precio + volumen |
| `VolumePctFilter` | 100 | volumen acumulado mínimo como % del promedio diario |
| `VolumeAvgDays` | 3 | sesiones para el promedio diario, máximo 10 |

### Archivos del paquete

```text
TSL FINAL THIRTY.ELD
TSL.Final Thirty.tsw
```

El workspace contiene dos charts:

```text
SPY 30 min [ARCX]
@ES.D=107XN 30 min [CME]
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, con datos intradía y calendario de sesión. |
| ¿Puede replicarse aproximadamente? | **Sí.** |
| ¿Puede replicarse exactamente? | **No sin resolver timestamp de barras, acumulación de volumen y fill al cierre.** |
| ¿El artículo demuestra edge? | **No.** El resultado final sigue a tres búsquedas adaptativas. |
| ¿La hipótesis es clara? | **Sí:** continuidad o debilidad en la última media hora. |
| ¿Es realmente trend following puro? | **No en el resultado final.** El short puede activarse en un día ligeramente positivo. |
| ¿Es relevante para small caps? | **Mucho.** Puede convertirse directamente en un event study de cierre. |
| ¿Está lista para operar? | **No.** El edge por trade es pequeño y no hay slippage ni microestructura de cierre. |

Clasificación TSIS:

```text
FINAL_WINDOW_DIRECTIONAL_EVENT
TIME_OF_DAY_EFFECT
INTRADAY_RETURN_THRESHOLD
CUMULATIVE_VOLUME_FILTER
SAME_SESSION_ENTRY_EXIT
CLOSE_EXECUTION_SENSITIVE
ADAPTIVELY_OPTIMIZED
NOT_SCIENTIFICALLY_VALIDATED
```

---

## 2. Qué estrategia es realmente

La estrategia intenta contestar tres preguntas:

```text
1. ¿La dirección hasta las 15:30 anticipa la última media hora?
2. ¿La magnitud mejora la señal?
3. ¿El volumen acumulado filtra trades débiles?
```

Con los parámetros finales publicados:

```text
si retorno desde la apertura >= +0.35%:
    long

si retorno desde la apertura <= +0.20%:
    short

si +0.20% < retorno < +0.35%:
    no trade

además:
volumen acumulado hasta 15:30 >= 90%
del promedio de seis sesiones
```

Esto no es una regla trend-following simétrica.

La política final es:

```text
strong up day  → continuation long
weak/non-strong day, incluso ligeramente positivo → short
zona intermedia → flat
```

El hallazgo editorial más llamativo es que el umbral short óptimo es positivo. La revista indica que 14 de los 20 mejores resultados utilizaban un `NegativeDayChange` no negativo.

---

## 3. Reconstrucción matemática

## 3.1 Cambio intradía

Sea:

```text
O_t = apertura regular de las 09:30
P_t = precio observable al cerrar la barra de las 15:30
```

Entonces:

\[
DayChange_t=100\left(\frac{P_t}{O_t}-1\right)
\]

El artículo utiliza porcentaje para mantener comparabilidad a través del cambio de nivel de SPY.

## 3.2 Volumen acumulado

La reconstrucción más probable es:

\[
CumVolume_{t,15:30}=\sum_{b\in RTH,\,b\le15:30}Volume_{t,b}
\]

\[
AvgDailyVolume_{t,N}=\frac{1}{N}\sum_{i=1}^{N}DailyVolume_{t-i}
\]

\[
VolumePct_t=100\frac{CumVolume_{t,15:30}}{AvgDailyVolume_{t,N}}
\]

No se puede certificar desde el PDF:

```text
si la barra 15:30 queda incluida;
si se usa volumen regular o total;
si el promedio incluye la sesión actual;
si el dato diario procede de otra data stream;
si futures y ETF usan exactamente la misma lógica.
```

## 3.3 Elegibilidad long

\[
LongEligible_t=DayChange_t\ge PositiveDayChange
\]

## 3.4 Elegibilidad short

\[
ShortEligible_t=DayChange_t\le NegativeDayChange
\]

## 3.5 Filtro de volumen

Si `UseDayChange_1_AndVolume_2 = 2`:

\[
VolumeEligible_t=VolumePct_t\ge VolumePctFilter
\]

## 3.6 Temporización de la barra

La revista habla de “open of the 4:00 p.m. bar” para operar la última media hora.

En un chart de 30 minutos etiquetado por hora de cierre:

```text
barra 16:00 = intervalo 15:30–16:00
```

Por tanto:

```text
decision information:
hasta 15:30

entry physical time:
15:30, apertura de la barra etiquetada 16:00

exit physical time:
16:00, cierre de esa barra
```

TSIS debe registrar tanto `bar_label_timestamp` como `physical_execution_timestamp` para evitar un off-by-one de 30 minutos.

## 3.7 Exit

```text
ETF:
salir a las 16:00

index futures .D:
salir también a las 16:00,
aunque la sesión de TradeStation continúe hasta 16:15
```

No se especifica si el fill corresponde a:

```text
last trade
bar close
closing auction
market-on-close
orden enviada segundos antes del cierre
```

---

## 4. Reglas operativas reconstruidas

```python
def final_thirty_signal(day_change, volume_pct, params):
    volume_ok = (
        params.mode == 1
        or volume_pct >= params.volume_pct_filter
    )

    if not volume_ok:
        return "flat"

    long_ok = day_change >= params.positive_day_change
    short_ok = day_change <= params.negative_day_change

    if long_ok and short_ok:
        return "AMBIGUOUS_BOTH_ELIGIBLE"
    if long_ok:
        return "long"
    if short_ok:
        return "short"
    return "flat"
```

La configuración publicada evita conflicto porque:

```text
0.35 > 0.20
```

Pero el grid de optimización contiene configuraciones con:

```text
PositiveDayChange <= NegativeDayChange
```

En ellas puede existir una zona donde ambas direcciones son elegibles. El source es necesario para conocer la prioridad real.

---

## 5. Desarrollo y resultados publicados

## 5.1 Baseline — dirección sin magnitud ni volumen

Inputs:

```text
PositiveDayChange = 0
NegativeDayChange = 0
mode = 1
```

| Métrica | All | Long | Short |
|---|---:|---:|---:|
| Net Profit | $1,616 | $519 | $1,097 |
| Profit Factor | 1.11 | 1.07 | 1.15 |
| Trades | 1,240 | 684 | 556 |
| Percent Profitable | 47.98% | 48.98% | 46.76% |
| Avg. Trade | $1.30 | $0.76 | $1.97 |
| Avg. Winner | $26.69 | $22.88 | $31.58 |
| Avg. Loser | -$22.78 | -$21.27 | -$24.53 |
| Ratio Avg. Win/Loss | 1.17 | 1.08 | 1.29 |
| Largest Winner | $312 | $312 | $197 |
| Largest Loser | -$134 | -$128 | -$134 |

La expectativa de $1.30 por 100 acciones es extremadamente pequeña frente a cualquier error de fill.

## 5.2 Optimización 1 — thresholds de precio

Grid:

```text
PositiveDayChange: -0.25 .. 1.00, step 0.05 → 26 valores
NegativeDayChange: -1.00 .. 0.25, step 0.05 → 26 valores
Total: 676 configuraciones
```

Selección:

```text
PositiveDayChange = +0.35
NegativeDayChange = -0.30
```

| Métrica | All | Long | Short |
|---|---:|---:|---:|
| Net Profit | $2,798 | $1,289 | $1,509 |
| Profit Factor | 1.37 | 1.37 | 1.36 |
| Trades | 656 | 343 | 313 |
| Percent Profitable | 50.46% | 50.15% | 50.80% |
| Avg. Trade | $4.27 | $3.76 | $4.82 |
| Ratio Avg. Win/Loss | 1.31 | 1.31 | 1.31 |

La mayor parte de la mejora editorial ocurre aquí.

## 5.3 Optimización 2 — volumen condicionado a los thresholds anteriores

Grid:

```text
VolumePctFilter: 50 .. 125, step 5 → 16 valores
VolumeAvgDays: 1 .. 10, step 1 → 10 valores
Total: 160 configuraciones
```

Selección:

```text
VolumePctFilter = 55
VolumeAvgDays = 5
```

| Métrica | All | Long | Short |
|---|---:|---:|---:|
| Net Profit | $2,808 | $1,343 | $1,465 |
| Profit Factor | 1.39 | 1.43 | 1.35 |
| Trades | 628 | 322 | 306 |
| Percent Profitable | 50.48% | 50.31% | 50.65% |
| Avg. Trade | $4.47 | $4.17 | $4.79 |
| Ratio Avg. Win/Loss | 1.33 | 1.35 | 1.31 |

Incremento sobre Optimización 1:

```text
+$10
+0.36%
```

Por sí sola, esta etapa aporta evidencia incremental muy débil para el filtro de volumen.

## 5.4 Optimización 3 — precio y volumen juntos

Grid:

```text
PositiveDayChange: -0.25 .. 0.50, step 0.05 → 16
NegativeDayChange: -0.50 .. 0.25, step 0.05 → 16
VolumePctFilter: 50 .. 110, step 5 → 13
VolumeAvgDays: 2 .. 10, step 1 → 9

Total:
16 × 16 × 13 × 9 = 29,952 configuraciones
```

Selección publicada para SPY:

```text
PositiveDayChange = +0.35
NegativeDayChange = +0.20
VolumePctFilter = 90
VolumeAvgDays = 6
```

| Métrica | All | Long | Short |
|---|---:|---:|---:|
| Net Profit | $2,997 | $1,461 | $1,536 |
| Gross Profit | $7,598 | $2,330 | $5,268 |
| Gross Loss | -$4,601 | -$869 | -$3,732 |
| Profit Factor | 1.65 | 2.68 | 1.41 |
| Trades | 391 | 95 | 296 |
| Percent Profitable | 51.92% | 58.95% | 49.66% |
| Avg. Trade | $7.66 | $15.38 | $5.19 |
| Avg. Winner | $37.43 | $41.61 | $35.84 |
| Avg. Loser | -$25.28 | -$24.14 | -$25.56 |
| Ratio Avg. Win/Loss | 1.48 | 1.72 | 1.40 |
| Largest Winner | $312 | $312 | $197 |
| Largest Loser | -$114 | -$87 | -$114 |

## 5.5 Qué mejoró realmente

De baseline a configuración final:

```text
Net Profit: +85.46%
Trades: -68.47%
Profit Factor: +48.65%
Avg. Trade: +489.23%
```

Pero:

```text
la mejora se seleccionó después de 30,788 configuraciones
publicadas entre las tres etapas
```

El total procede de:

```text
676 + 160 + 29,952 = 30,788
```

Además, las etapas posteriores usan lo aprendido en las anteriores sobre la misma muestra. No son tests independientes.

## 5.6 Asimetría del resultado final

```text
Longs:
24.30% de los trades
48.75% del beneficio
$15.38 por trade

Shorts:
75.70% de los trades
51.25% del beneficio
$5.19 por trade
```

La pata long es menos frecuente y de mayor calidad. La pata short aporta frecuencia, pero tiene menor margen frente a costes.

## 5.7 Sensibilidad a costes

El net profit final es $2,997 sobre 391 trades.

| Coste adicional por round trip | Reducción total | Efecto sobre net profit |
|---:|---:|---:|
| $2 | $782 | -26.09% |
| $4 | $1,564 | -52.19% |
| $6 | $2,346 | -78.28% |
| $8 | $3,128 | resultado negativo |

Un coste adicional medio de $7.66 por operación elimina la expectativa publicada.

---

## 6. Forense del workspace Final Thirty

## 6.1 Dos charts con configuraciones distintas

El stream `Contents` confirma:

### SPY

```text
PositiveDayChange = 0.35
NegativeDayChange = 0.20
UseDayChange_1_AndVolume_2 = 2
VolumePctFilter = 90
VolumeAvgDays = 6
```

Coincide con la configuración final publicada.

### @ES.D

```text
PositiveDayChange = 0.35
NegativeDayChange = 0.20
UseDayChange_1_AndVolume_2 = 2
VolumePctFilter = 85
VolumeAvgDays = 5
```

El workspace, por tanto, conserva una aplicación adicional sobre futuros que no aparece en las tablas principales del artículo.

## 6.2 OptimizationData

El workspace contiene:

```text
OptimizationData size:
372,366 bytes

symbol header:
@ES.D=107XN 30 min [CME]
E-mini S&P 500 Custom Continuous Contract
```

El stream no corresponde a SPY, sino a `@ES.D`.

## 6.3 Tres bloques de 200 filas

La estructura recuperada es:

```text
block 1:
200 filas completas

block 2:
200 filas completas, idénticas bit a bit en valores

block 3:
200 filas con los mismos TrialID e inputs,
pero métricas placeholder
```

El bloque placeholder utiliza, entre otros:

```text
Net Profit = 0
Profit Factor = 100
Ratio Avg Win/Loss = 100
Return on Initial Capital = -99,999
Max Equity Run-up = -99,999
```

Conclusión:

```text
unique valid optimization rows = 200
not 600
```

Los bloques duplicados no son nuevos experimentos.

## 6.4 El grid completo queda codificado en TrialID

Los cuatro rangos son los mismos de la Optimización 3:

```text
PositiveDayChange: 16 valores
NegativeDayChange: 16 valores
VolumePctFilter: 13 valores
VolumeAvgDays: 9 valores
Total: 29,952
```

Todos los TrialID de las 200 filas satisfacen exactamente:

\[
TrialID=1+i_P+16i_N+256i_V+3328i_D
\]

con:

```text
iP = índice de PositiveDayChange
iN = índice de NegativeDayChange
iV = índice de VolumePctFilter
iD = índice de VolumeAvgDays
```

Esto demuestra que el stream es una selección del grid conjunto de 29,952 candidatos.

## 6.5 Sólo se guardan los 200 mejores

Las 200 filas válidas están ordenadas de mayor a menor `Net Profit`.

```text
máximo guardado: $9,360.97
mínimo guardado: $7,919.995
mediana: $8,177.69
media: $8,282.13
```

Rango relativo top-to-bottom:

```text
15.39%
```

Estas 200 filas representan:

```text
200 / 29,952 = 0.668% del grid
```

No puede inferirse la forma de la superficie completa a partir del top 0.668%.

## 6.6 Configuración óptima guardada para ES

| Rank | TrialID | Positive | Negative | Vol% | AvgDays | Net Profit | PF | Trades | Win% | Avg Trade | Max DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12013 | 0.35 | 0.20 | 85 | 5 | $9,360.97 | 2.14 | 191 | 53.93% | $49.01 | -$1,366.16 |
| 2 | 11997 | 0.35 | 0.15 | 85 | 5 | $9,112.63 | 2.11 | 188 | 53.72% | $48.47 | -$1,361.44 |
| 3 | 12010 | 0.20 | 0.20 | 85 | 5 | $9,085.45 | 1.92 | 207 | 53.62% | $43.89 | -$1,455.32 |
| 4 | 12009 | 0.15 | 0.20 | 85 | 5 | $9,071.29 | 1.92 | 210 | 52.86% | $43.20 | -$1,460.04 |
| 5 | 12016 | 0.50 | 0.20 | 85 | 5 | $9,070.67 | 2.13 | 181 | 54.14% | $50.11 | -$1,431.72 |

El chart ES está configurado exactamente con el rank 1.

## 6.7 La configuración publicada de SPY en el grid ES

La configuración:

```text
0.35 / 0.20 / 90 / 6
```

corresponde a:

```text
TrialID = 15,597
Rank = 37 / 200 guardados
```

Resultado sobre el grid ES guardado:

| Métrica | Resultado |
|---|---:|
| Net Profit | $8,571.46 |
| Profit Factor | 2.27 |
| Trades | 157 |
| Percent Profitable | 54.78% |
| Avg. Trade | $54.60 |
| Max Intraday Drawdown | -$1,293.18 |
| RINA | 662.82 |
| Long Net Profit | $1,483.40 |
| Short Net Profit | $7,088.06 |

No es un OOS: está incluido en el mismo grid ES. Sí muestra que los thresholds de precio seleccionados para SPY aparecen también en la cola superior de ES cuando se adaptan los parámetros de volumen.

## 6.8 Concentración del top 200

Frecuencias principales:

```text
NegativeDayChange:
0.20 → 101/200
0.15 → 52/200
0.25 → 35/200

VolumePctFilter:
85 → 113/200

VolumeAvgDays:
5 → 90/200
6 → 48/200
```

En el top 20:

```text
20/20 usan NegativeDayChange no negativo
18/20 usan 0.20
```

En el top 200:

```text
199/200 usan NegativeDayChange no negativo
```

Esto refuerza la observación del artículo: en este test, el short no exige un día negativo; exige que el día no sea suficientemente fuerte.

## 6.9 Dominio del lado short en ES

En las 200 filas guardadas:

```text
Long Net Profit medio:  $1,145.24
Short Net Profit medio: $7,136.90

Short share medio del net profit: 86.16%
Rango de short share: 76.09%–94.76%
```

El patrón ES es mucho más short-dominant que el resultado SPY publicado. Esto demuestra dependencia del instrumento y desaconseja una narrativa universal.

## 6.10 Threshold overlap

En 72 de las 200 configuraciones guardadas:

```text
PositiveDayChange <= NegativeDayChange
```

Por tanto, existe una región de retornos que podría satisfacer simultáneamente long y short.

Además:

```text
9 de las 20 mejores filas presentan overlap
```

El source no está disponible. Debe aclararse si la estrategia:

```text
usa if/else;
prioriza una orden;
permite dos órdenes en la misma barra;
revierte instantáneamente;
cancela una de ellas.
```

Las métricas del grid sugieren que largos y cortos pueden contabilizarse de forma relativamente independiente, pero esto es una inferencia, no una prueba.

## 6.11 Qué no contiene el workspace

No se conserva:

```text
el grid completo de 29,952 filas
las 29,752 filas fuera del top 200
Trade Lists
source EasyLanguage
fill timestamps
closing-auction details
cumulative-volume implementation
```

---

## 7. ¿Dónde podría estar el edge?

La hipótesis long sería:

> Un mercado que llega a las 15:30 con un avance suficientemente fuerte y volumen elevado mantiene parte de esa presión durante la última media hora.

La hipótesis short final es distinta:

> Cuando a las 15:30 el mercado no ha conseguido superar un umbral positivo, especialmente en un día de volumen elevado, la última media hora presenta debilidad relativa.

Posibles mecanismos:

```text
continuidad de flujo institucional
rebalanceos de cierre
hedging
closing-auction imbalances
liquidación de posiciones intradía
momentum/failure-to-rally
```

El artículo no identifica cuál domina. Tampoco aporta datos de imbalance, quotes o auction.

---

## 8. Problemas científicos y técnicos

## 8.1 Optimización adaptativa

Las tres rondas reutilizan la misma muestra y la tercera estrecha rangos según resultados previos.

## 8.2 30,788 candidatos publicados

El resultado final es un ganador de una búsqueda grande, no un estimador neutral.

## 8.3 Grid adicional sobre ES

El paquete revela otra búsqueda de 29,952 candidatos. No puede determinarse cuándo se realizó ni si influyó en la narrativa.

## 8.4 No hay OOS

No existe un periodo independiente.

## 8.5 Expectativa pequeña

```text
SPY final: $7.66 por 100 acciones
SPY baseline: $1.30 por 100 acciones
```

El resultado depende críticamente de fills.

## 8.6 Slippage no publicado

Sólo se declara comisión.

## 8.7 Cierre de sesión

El bar close no equivale automáticamente a un fill ejecutable. Deben gobernarse:

```text
closing auction
MOC/LOC eligibility
last trade
spread
partial fill
order deadline
```

## 8.8 Timestamp de barras

Confundir la etiqueta 16:00 con una entrada física a las 16:00 eliminaría la ventana operada.

## 8.9 Volumen acumulado ambiguo

No se conoce la implementación exacta.

## 8.10 Sesión y premarket

Debe definirse si el volumen y la apertura son sólo RTH.

## 8.11 Timezone y DST

El artículo afirma que EasyLanguage ajusta a zona local. TSIS debe usar timezone de exchange, no depender del ordenador del usuario.

## 8.12 Umbrales que cruzan cero

Un long puede producirse tras un día ligeramente negativo y un short tras uno ligeramente positivo. La etiqueta trend following es insuficiente.

## 8.13 Overlap de condiciones

Parte del espacio de búsqueda permite long y short simultáneos.

## 8.14 Exit sin stop

Una ventana corta no elimina el riesgo de un shock entre 15:30 y 16:00.

## 8.15 Proactive profit exit ausente

Todo trade espera al cierre, aunque el MFE ocurra antes.

## 8.16 Bar interval fijo

Una barra de 30 minutos oculta el path y la microestructura del cierre.

## 8.17 ETF frente a futures

`SPY` y `@ES.D` tienen sesiones, volumen y mecanismos de cierre diferentes.

## 8.18 Volume filter casi no mejora en la etapa aislada

+$10 no demuestra un efecto robusto.

## 8.19 Top 200 no es superficie

Una cola superior truncada no permite evaluar estabilidad global.

## 8.20 Block duplication

Contar 600 filas inflaría tres veces la evidencia. Sólo hay 200 resultados únicos válidos.

---

## 9. Implementación en TSIS

## 9.1 Event study antes que estrategia

Primero debe estudiarse:

```text
event timestamp = 15:30 ET
features available at 15:30
outcome = return 15:30→16:00
```

Sin ejecutar la policy optimizada.

## 9.2 Market State mínimo

```text
session_open_raw
price_at_decision
open_to_decision_return
cumulative_rth_volume
average_prior_daily_volume
cumulative_volume_pct
vwap_distance
position_in_day_range
spread
liquidity state
```

## 9.3 Event State

```text
event_type:
final_window_state

decision_timestamp:
15:30:00 America/New_York

window_end:
16:00:00 America/New_York
```

## 9.4 Execution views

```text
signal view:
bar completed at 15:30

entry view:
first executable quote/trade after decision

exit view:
explicit close policy
```

## 9.5 No look-ahead

El volumen promedio debe usar sólo sesiones completas anteriores.

## 9.6 Auction-aware outcomes

Separar:

```text
15:30→15:59:59 continuous market return
closing auction increment
full 15:30→official close return
```

## 9.7 Estado de indisponibilidad

```text
missing_open
incomplete_volume
half_day
halted_at_decision
no_valid_quote
closing_auction_missing
```

## 9.8 Half-days

La regla 15:30–16:00 no existe igual en sesiones abreviadas. Deben excluirse o parametrizarse.

---

## 10. Pseudocódigo de referencia

```python
def build_final_window_event(session, params):
    open_price = session.regular_open
    decision_price = session.price_at("15:30:00", tz="America/New_York")

    if open_price is None or decision_price is None:
        return unavailable("MISSING_DECISION_PRICE")

    day_change = 100.0 * (decision_price / open_price - 1.0)

    prior_daily_volumes = get_prior_complete_rth_volumes(
        session.date,
        n=params.volume_avg_days,
    )
    if len(prior_daily_volumes) < params.volume_avg_days:
        return unavailable("INSUFFICIENT_VOLUME_HISTORY")

    cumulative_volume = session.cumulative_rth_volume_to("15:30:00")
    average_volume = sum(prior_daily_volumes) / len(prior_daily_volumes)
    volume_pct = 100.0 * cumulative_volume / average_volume

    volume_ok = (
        params.mode == 1
        or volume_pct >= params.volume_pct_filter
    )

    long_ok = volume_ok and day_change >= params.positive_day_change
    short_ok = volume_ok and day_change <= params.negative_day_change

    if long_ok and short_ok:
        return unavailable("DIRECTION_CONFLICT")

    direction = "long" if long_ok else "short" if short_ok else "flat"

    return FinalWindowEvent(
        decision_timestamp=session.timestamp("15:30:00"),
        direction=direction,
        day_change_pct=day_change,
        cumulative_volume_pct=volume_pct,
    )
```

---

## 11. Cómo demostrar o destruir el supuesto edge

### Fase 1 — Event study no parametrizado

Bins de `open_to_15:30_return` y distribución del retorno final.

### Fase 2 — Volume ablation

Comparar exactamente las mismas fechas con y sin volumen.

### Fase 3 — Réplica baseline

Objetivo:

```text
1,240 trades
$1,616
PF 1.11
```

### Fase 4 — Réplica de las tres optimizaciones

Reproducir el número de candidatos y la configuración elegida.

### Fase 5 — Verdadero postpublication OOS

Congelar:

```text
0.35 / 0.20 / 90 / 6
```

sin retocar.

### Fase 6 — Cross-market preregistrado

SPY, ES y otros índices con reglas de sesión específicas.

### Fase 7 — Costes y microestructura

Modelar:

```text
spread
entry delay
last five minutes
closing auction
market impact
```

### Fase 8 — Decomposición del cierre

```text
15:30→15:45
15:45→15:55
15:55→continuous close
auction increment
```

### Fase 9 — Long/short independientes

No imponer thresholds simétricos.

### Fase 10 — Placebos temporales

Repetir la metodología en:

```text
14:30–15:00
15:00–15:30
otros bloques de 30 minutos
```

Si todos producen resultados parecidos, no existe edge específico “Final Thirty”.

### Fase 11 — Randomized thresholds

Evaluar cuánto del máximo surge por selección.

### Fase 12 — Multiple-testing control

Aplicar DSR/PBO/SPA o bootstrap apropiado al grid completo.

### Fase 13 — Regímenes

```text
trend day
range day
high volume
low volume
macro announcement
expiration/rebalance
```

### Fase 14 — Stability by year

El resultado agregado debe descomponerse año a año.

---

## 12. Variantes posteriores a la réplica

### Variante A — Percentiles, no thresholds fijos

Normalizar el cambio intradía por volatilidad reciente.

### Variante B — Relative volume intradía esperado

Comparar volumen acumulado con el perfil esperado a las 15:30, no con volumen diario completo.

### Variante C — Closing imbalance

Añadir imbalance cuando exista legalmente en timestamp.

### Variante D — VWAP state

Condicionar por distancia y pendiente de VWAP.

### Variante E — Trend regime previo

La propia revista lo sugiere como mejora.

### Variante F — Profit target intrabar

Sólo después de estudiar MFE.

### Variante G — Stop por volatilidad

No por dólar fijo.

### Variante H — Classifier probabilístico

Aprender `P(return_15:30_16:00 > 0 | state)` con validación temporal, no optimizar cuatro thresholds en la misma muestra.

---

## 13. Encaje en Market State y Event State

### Market State a las 15:30

```text
open_to_now_return
intraday_range
position_in_range
vwap_distance
relative_volume_to_time
spread
trade_count
volatility
market regime
```

### Event State

```text
event_type:
final_30_minute_decision_point

subject_scope:
security_session

decision_timestamp:
15:30 ET
```

### Outcomes

```text
return_to_continuous_close
return_in_closing_auction
MFE_30m
MAE_30m
close_location
volume_last_30m
```

### Distinción clave

```text
evento:
estado observable al inicio de la última media hora

estrategia publicada:
threshold classifier + entry + close exit
```

El evento puede contener información aunque la policy seleccionada no generalice.

---

## 14. Transferencia a small caps

Esta es la idea del issue con mayor relevancia directa para TSIS.

En small caps puede estudiarse:

```text
¿continúa el squeeze en los últimos 30 minutos?
¿se produce profit-taking?
¿el stock cierra cerca del HOD?
¿el volumen relativo a la hora discrimina?
¿cambia el resultado con catalyst, halt o SSR?
```

Features adicionales necesarias:

```text
gap
float
premarket volume
intraday return
HOD distance
VWAP distance
number of halts
borrow state
spread
quote depth
news catalyst
```

Riesgos específicos:

```text
halts hasta el cierre
LULD
closing prints discontinuos
borrow recall
spreads grandes
liquidez asimétrica
```

La recomendación es:

```text
EVENT STUDY FIRST
NO THRESHOLD OPTIMIZATION UNTIL REPRESENTATION IS FROZEN
```

---

## 15. Veredicto de Final Thirty

```text
IMPLEMENTAR:
sí, primero como event study

ACEPTAR COMO EDGE:
no

OPTIMIZAR:
no antes del OOS y del control de búsqueda

OPERAR EN REAL:
no

MAYOR VALOR PARA TSIS:
time-of-day Event State,
relative volume by clock,
y descomposición del cierre
```

Gate propuesto:

```text
FINAL-THIRTY-EVENT-STUDY-AUCTION-AWARE-REPLICATION-AND-POSTPUBLICATION-OOS-GATE
```

---

# Parte III — Ideas adicionales de backtesting contenidas en el issue

## 1. No imponer simetría por costumbre

ACB demuestra que:

```text
long rule ≠ short rule
```

puede ser una decisión legítima si está justificada y validada fuera de muestra.

## 2. Trade secundario condicionado

Una señal puede requerir:

```text
un evento previo
+
un estado de posición
+
un nuevo trigger
```

Esto exige Event Graph, no una tabla plana de señales independientes.

## 3. Un reversal no es un exit

```text
primary long → secondary short
```

son dos acciones enlazadas y deben conservar parent lineage.

## 4. Selección del lado es un hiperparámetro

Elegir long emphasis tras dos búsquedas es parte del data snooping.

## 5. Un informe truncado no describe el universo

8,000 filas guardadas de 9,600 no permiten afirmar lo ocurrido en las 1,600 omitidas.

## 6. Resultado cerca del máximo

La configuración ACB publicada está prácticamente en el máximo de net profit declarado.

## 7. Top tail no es robustness surface

Final Thirty conserva sólo el 0.668% superior del grid ES.

## 8. Bloques binarios duplicados

Dos copias completas y un placeholder no son tres experimentos.

## 9. TrialID como prueba de exhaustividad

La codificación del TrialID permite reconstruir el lattice de 29,952 candidatos.

## 10. Thresholds pueden definir un clasificador ternario

Final Thirty no es sólo long/short:

```text
long
flat band
short
```

## 11. Umbrales con signo inesperado

Un input llamado `NegativeDayChange` puede ser positivo. El nombre no sustituye a la semántica formal.

## 12. El volumen debe normalizarse por reloj

Comparar volumen parcial con volumen diario es una aproximación. Para TSIS conviene modelar el volumen esperado hasta cada minuto.

## 13. Time-of-day como objeto de investigación

La ventana horaria puede ser el evento principal y la dirección una respuesta.

## 14. Closing auction separada

El último print no debe mezclarse con el mercado continuo.

## 15. Costes frente a average trade

El average trade es el presupuesto máximo de error de ejecución.

## 16. Continuous reference frente a physical execution

ACB y la versión futures de Final Thirty confirman esta separación.

## 17. Corrección del Issue 5

El editor declara que el indicador `TSL:MACD Difference` podía dibujar marcas de señal adicionales incorrectas, aunque:

```text
el histograma era correcto
la estrategia no estaba afectada
```

La actualización supuestamente acompaña al Issue 6.

El ZIP no contiene un archivo separadamente nombrado como update. Dado que los `.ELD` son opacos, no puede certificarse si la corrección está embebida en uno de ellos.

Lección institucional:

```text
artefact_version
supersedes
bug_scope
strategy_impact
visual_only_vs_execution
```

## 18. VWAP histórico

La página física 9 presenta un indicador intradía de VWAP actual e históricos.

Clasificación:

```text
INDICATOR_CONCEPT
NO_STRATEGY_RULES
NO_EDGE_EVIDENCE
```

Para TSIS:

```text
current_session_vwap
prior_session_vwap_levels
vwap_distance
vwap_reclaim_event
```

## 19. Papers adicionales citados

El artículo menciona:

```text
Mapping Intraday Price Movement in the S&P 500 Index
Intraday Time Analysis
```

No se incluyen sus contenidos en el paquete. No se utilizan como evidencia en esta auditoría.

---

# Parte IV — Priorización para TSIS

## 1. Orden recomendado

### Prioridad A — Final Thirty como Event State

Es implementable con la infraestructura intradía de equities y responde a una pregunta clara.

Objetivo inicial:

```text
medir, no optimizar
```

### Prioridad B — ACB como máquina de estados

Útil para validar:

```text
parent events
stateful policy
reversal
secondary horizon
```

### Prioridad C — Réplica exacta de futures

Debe esperar a datos físicos, roll y sesiones.

## 2. Estado respecto de los datos actuales de TSIS

### Final Thirty sobre small caps

Posible con:

```text
013_ohlcv_1m_quote_guarded para ejecución
014_master_intraday_bar_table_candidate para features
004_master_daily_table para volumen histórico
```

### ACB sobre equities

Posible como adaptación, separando señal ajustada y ejecución raw.

### ACB exacto sobre NQ

No disponible hasta incorporar futures físicos.

### Final Thirty exacto sobre SPY

Posible si se gobiernan:

```text
session calendar
opening price
cumulative RTH volume
closing execution
```

## 3. Artefactos futuros derivados

Cuando se abran los gates:

```text
SCC_2015_06_ACB_REPLICATION_CONTRACT.md
SCC_2015_06_FINAL_THIRTY_EVENT_STUDY_CONTRACT.md
```

No deben crearse ahora como resúmenes duplicados.

## 4. Material adicional necesario para réplica exacta

El ZIP es suficiente para cerrar la auditoría documental.

Al abrir implementación sería útil solicitar:

```text
EasyLanguage source exportado como texto
Trade Lists
Strategy Properties
MaxBarsBack
session templates
full ACB optimization reports
full Final Thirty 29,952-row report
cumulative-volume implementation
closing-order behavior
physical futures roll maps
updated MACD indicator export
```

Sólo debe pedirse cuando se abra el gate correspondiente.

---

# Apéndice A — Integridad del paquete

## Archivos relevantes

```text
SCC Issue 6 Jun 2015(1).pdf
2015-06.zip

2015-06/ACB TS files/
  TSL ASYMMETRIC CHANNEL BREAKOUT.ELD
  TSL Asymmetric Channel Breakout.tsw

2015-06/Final 30 TS files/
  TSL FINAL THIRTY.ELD
  TSL.Final Thirty.tsw
```

El PDF incluido dentro del ZIP es bit a bit idéntico al PDF cargado por separado.

## Tamaños

```text
PDF: 2,257,102 bytes
ZIP: 2,363,737 bytes
ACB .ELD: 16,263 bytes
ACB .tsw: 22,528 bytes
Final Thirty .ELD: 11,166 bytes
Final Thirty .tsw: 416,256 bytes
Final Thirty OptimizationData: 372,366 bytes
```

## SHA-256

```text
PDF:
6336c60eea364e4623d9fb72c8351a4ddc3d44718278b82e8341627072bb551c

ZIP:
ca75be7b8a37decd73309b306ea15e3e91440790dfcbda3f121911c7c4aeaf90

ACB .ELD:
f07164fd639f26b2493e633481b64a1d28a975a2956fc881a5f6cf01df7c627d

ACB .tsw:
cccc2a55abe7ead3bc01ae91ac8bb4140822d8fa3a9d6dd7ced7bb758ab092b3

Final Thirty .ELD:
5d4ed018e7e0a5c5c4e2a98b57225316e8ae5e496fa9fda2639fd635a5c545d3

Final Thirty .tsw:
e1c483d00ccb53e79c820281116215fc0a857d55b9f65912b368e4c4723122d0
```

## Metadata PDF

```text
Creator: Adobe InDesign CC 2014 (Windows)
Producer: Adobe PDF Library 11.0
Pages: 14
CreationDate: 11 de junio de 2015, 14:41:08 UTC
ModificationDate: 12 de octubre de 2015, 18:34:10 UTC
Page size: US Letter
PDF version: 1.6
Encrypted: sí
Copy: no
Print: no según pdfinfo
```

## Evidencia binaria ACB

```text
workspace OLE size:
22,528 bytes

chart:
@NQ=107XN 180 min

active inputs:
1 / 5 / 6 / 3 / 750

OptimizationData:
no presente con resultados
```

## Evidencia binaria Final Thirty

```text
workspace OLE size:
416,256 bytes

charts:
SPY 30 min
@ES.D=107XN 30 min

SPY inputs:
0.35 / 0.20 / 2 / 90 / 6

ES inputs:
0.35 / 0.20 / 2 / 85 / 5

OptimizationData:
372,366 bytes

symbol:
@ES.D=107XN

candidate lattice:
29,952

saved rows per block:
200

blocks:
2 completos idénticos
1 placeholder

unique valid rows:
200

best saved ES inputs:
0.35 / 0.20 / 85 / 5

best saved ES net profit:
$9,360.97
```

## Limitación del paquete

```text
.tsw:
workspace OLE con charts, inputs
y parte de la optimización recuperables

.ELD:
contenedor propietario no legible como source EasyLanguage
en este entorno
```

No contiene exportaciones legibles de:

```text
source code
trade lists
full ACB grids
full Final Thirty grid
fill logs
session properties
closing-auction configuration
```

---

# Cierre del issue

El Issue 6 debe conservarse en TSIS como dos lecciones institucionales:

```text
ACB:
la asimetría puede ser estructuralmente válida,
pero debe modelarse como una máquina de estados
y no seleccionarse retrospectivamente sin penalización

Final Thirty:
un timestamp concreto puede definir un evento investigable,
pero 30,788 configuraciones sobre la misma muestra
y un average trade pequeño no demuestran edge operable
```

Decisión final:

```text
ARCHIVE_STATUS:
AUDITED_COMPLETE

ACB_STATUS:
ASYMMETRIC_STATE_MACHINE_REPLICATION_CANDIDATE

FINAL_THIRTY_STATUS:
HIGH_PRIORITY_TIME_OF_DAY_EVENT_STUDY_CANDIDATE

EDGE_ACCEPTED:
NO

ADDITIONAL_SOURCE_NEEDED_NOW:
NO

NEXT_ACTION:
ARCHIVE AND CONTINUE WITH ISSUE 7
```
