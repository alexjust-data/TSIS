# Auditoría completa — TradeStation Strategy Concepts Club, Issue 15 (marzo de 2016)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. Overnight-Futures-Range Breakout Strategy
2. VWAP Bands MR Strategy
3. combinación VWAP Bands TF + VWAP Bands MR en Portfolio Maestro
4. Strategy Concepts Club Utility Kit 1 — reimpresión documental
5. ideas secundarias de investigación y backtesting
6. reconstrucción matemática, temporal y de máquinas de estado
7. auditoría de los resultados publicados
8. inspección forense de los archivos .ELD, .tsw y .pmx
9. análisis del OptimizationData embebido en el workspace VWAP Bands MR
10. contratos de implementación y réplica para TSIS
11. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia, portfolio ni Utility Kit.

### Fuentes examinadas

- PDF completo de 23 páginas: `SCC Issue 15 Mar 2016.pdf`.
- Archivo de apoyo: `2016-03.zip`.
- PDF idéntico incluido dentro del ZIP.
- PDF auxiliar `Strategy Concepts Club Inventory.pdf`.
- Dos contenedores propietarios:
  - `TSL OVERNIGHT FUTURES RANGE BREAKOUT.ELD`;
  - `VWAP BANDS MR.ELD`.
- Dos workspaces OLE/Compound Document:
  - `TSL.Overnight-Futures-Range Breakout.tsw`;
  - `TSL VWAP Bands MR.tsw`.
- Proyecto de Portfolio Maestro:
  - `VWAP Bands MR and TF Combined.pmx`.
- Las 23 páginas renderizadas, incluidas:
  - definición temporal del overnight range;
  - tres métodos de salida y sus informes;
  - disección long-only/short-only de las señales;
  - reglas, resultados y superficies de VWAP Bands MR;
  - resultado del portfolio combinado;
  - reimpresión completa del Utility Kit 1.
- Los streams internos de ambos workspaces:
  - `Contents`;
  - `AnalisysTechniques`;
  - `ChartSetting`;
  - `DrawingObjects`;
  - `optdatafile`;
  - `OptimizationData`, cuando existe.
- La estructura serializada del `.pmx`, sus nombres de grupos, estrategias, símbolos, sizing y propiedades de backtest recuperables.

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

Cuando una decisión no queda resuelta por la revista o el paquete, se registra como ambigüedad. No se completa silenciosamente.

Las fórmulas no publicadas literalmente se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

No se ha utilizado investigación web externa para completar reglas, resultados o fórmulas.

---

## 0.1 Integridad del paquete

El PDF cargado por separado y el PDF incluido dentro del ZIP son binariamente idénticos.

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `2016-03.zip` | 10,587,089 bytes | `05ff7f3b43b8d0c5e40cd8ebe03b090b0ad3a06e63e4f368fb6c79c4f9253f4a` |
| `SCC Issue 15 Mar 2016.pdf` | 10,491,301 bytes | `3d5409630894471f405d2e1e3b90df47451dddf3af801d323289d6102d400d5b` |
| `Strategy Concepts Club Inventory.pdf` | 27,559 bytes | `7e04c565bf39f901fbc5c5f9964276832427353bee3cf97daaaadc9e258a7a24` |
| `TSL OVERNIGHT FUTURES RANGE BREAKOUT.ELD` | 22,416 bytes | `46d40b2071854a302551174e7a60a7f4acaad97495907b8f44ab4e8127b699d5` |
| `TSL.Overnight-Futures-Range Breakout.tsw` | 28,160 bytes | `20a8115cd6b51b46ae88856b30c494fbdd779f6528c3af4bbf8ca131b7b33303` |
| `VWAP BANDS MR.ELD` | 25,816 bytes | `a2594a42b1f93d5bff2722f426606de6928ce550534162f33572cf03c04d5a01` |
| `TSL VWAP Bands MR.tsw` | 100,352 bytes | `bea603217b6ef43607ab3b23433daf6112a934b604ea65a7cef44776cd1dd0df` |
| `VWAP Bands MR and TF Combined.pmx` | 298,895 bytes | `3f3b826f87f81132b90aedf7ed8a6a982e38deddf0927065fcc2e46164d8ea71` |

Los pequeños streams `Zone.Identifier` son metadatos del sistema operativo y no forman parte del contenido científico.

El PDF `Strategy Concepts Club Inventory.pdf` es un índice de números y contenidos. No añade reglas ni resultados a las estrategias del Issue 15.

---

## 0.2 Limitación de los `.ELD`

Los `.ELD` son contenedores propietarios de TradeStation y no exponen el EasyLanguage como texto legible en este entorno.

Por tanto:

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la prioridad exacta de órdenes;
no puede resolverse únicamente por lectura:
    - el timestamp exacto del freeze del overnight range;
    - la prioridad entre entry, reversal, target y stop;
    - el precio-barra exacto empleado en el VWAP;
    - la dispersión exacta de las bandas;
    - el redondeo de las salidas parciales;
    - el conteo exacto de Max_Hold_Length;
    - la función del input interno My_Count.
```

---

## 0.3 Workspaces OLE

### Overnight-Futures-Range Breakout

Streams principales:

| Stream | Tamaño |
|---|---:|
| `Embedding 2/Contents` | 19,312 bytes |
| `Embedding 2/StatusLine` | 144 bytes |
| `Embedding 2/ChartSetting` | 1,332 bytes |
| `Embedding 2/DrawingObjects` | 571 bytes |
| `Embedding 2/AnalisysTechniques` | 359 bytes |
| `Embedding 2/optdatafile` | **0 bytes** |

### VWAP Bands MR

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 17,432 bytes |
| `Embedding 1/StatusLine` | 368 bytes |
| `Embedding 1/ChartSetting` | 666 bytes |
| `Embedding 1/DrawingObjects` | 92 bytes |
| `Embedding 1/AnalisysTechniques` | 295 bytes |
| `Embedding 1/optdatafile` | **0 bytes** |
| `Embedding 1/OptimizationData` | **69,871 bytes** |

Conclusión general:

```text
los optdatafile están vacíos;
el workspace Overnight no conserva grids;
VWAP MR conserva OptimizationData,
pero no corresponde a las superficies LX/SX publicadas.
```

---

## 0.4 Evidencia del workspace Overnight

El workspace confirma:

```text
Serie:
@ES=107XN 6 min [CME]
E-mini S&P 500 Custom Continuous Contract

Técnicas:
TSL:Overnight-Futures-Range Breakout
TSL:Overnight Futures Range

Inputs activos:
DayStartTime = 930
EntryTicks = 1
Pct_1_ATR_2_$_3 = 1
ProfitTarget = 0.5
Risk = 0.5
ATRLength = 2
```

Estos son los **defaults**, no las tres configuraciones optimizadas publicadas.

El workspace no conserva una instancia distinta para:

```text
Percent:
1.3 / 0.3

ATR:
6 / 6.6 / ATRLength 3

Dollar:
950 / 250
```

Por tanto, los informes de la revista no pueden reproducirse abriendo el workspace y ejecutándolo sin modificar los inputs.

---

## 0.5 Evidencia del workspace VWAP Bands MR

El workspace confirma:

```text
Serie:
SPY 5 min [ARCX]
SPDR S&P 500 ETF

Técnicas:
TSL:VWAP Bands MR Strategy
TSL:VWAP Bands MR Indicator

Inputs visibles:
LE_Signal_Band_Num = 2.5
SE_Signal_Band_Num = 3
LX1_Band_Num = 2
LX2_Band_Num = 2.5
SX1_Band_Num = 2.5
SX2_Band_Num = 2.5
Max_Hold_Length = 60
```

Los valores coinciden con el informe publicado.

---

## 0.6 Hallazgo forense — `OptimizationData` de VWAP Bands MR

El stream de 69,871 bytes identifica:

```text
símbolo:
SPY 5 min

único campo nombrado en el trailer:
TSL:VWAP Bands MR: My_Count
```

Junto a esa estructura aparece el valor `60`, consistente con el horizonte publicado de `Max_Hold_Length`, pero no puede certificarse que ambos campos sean equivalentes.

La estructura física contiene:

```text
tres secciones de resultados
de 23,248 bytes cada una;

las secciones 1 y 2
son duplicados binarios exactos;

la sección 3
está compuesta mayoritariamente por
ceros, sentinels y placeholders;

cada sección declara
72 registros internos.
```

La tercera sección presenta aproximadamente un 95% de bytes a cero, frente a cerca del 39% en las dos secciones completas.

No aparecen en el trailer:

```text
LX1_Band_Num
LX2_Band_Num
SX1_Band_Num
SX2_Band_Num
LE_Signal_Band_Num
SE_Signal_Band_Num
```

Por tanto:

> El stream no es el ledger de las superficies `LX1 × LX2` ni `SX1 × SX2` mostradas en la revista.

El `.pmx` también conserva el nombre interno `My_Count`, de modo que no es ruido aleatorio del workspace. Sin el código no puede saberse si se trata de:

```text
un input auxiliar;
un contador serializado;
una versión intermedia;
un alias interno del holding period;
una prueba long-only;
o un artefacto de optimización incompleto.
```

Estado:

```text
OPTIMIZATION_DATA_PRESENT:
YES

PUBLISHED_SENSITIVITY_GRID_RECOVERABLE:
NO

UNDOCUMENTED_INTERNAL_FIELD:
My_Count

DUPLICATE_RESULT_SECTION:
YES

PLACEHOLDER_SECTION:
YES
```

No puede determinarse:

```text
cuántas combinaciones de LX/SX se probaron;
qué puesto ocuparon los defaults;
qué función objetivo se empleó;
cuántas superficies adicionales se revisaron.
```

---

## 0.7 Evidencia del proyecto Portfolio Maestro

La estructura serializada del `.pmx` confirma:

```text
Portfolio:
VWAP Bands MR and TF Combined

Strategy Groups:
VWAP Testing MR
VWAP Bands TF

Estrategias:
TSL VWAP Bands MR
TSL:VWAP Bands TF

Símbolos:
SPY
AAPL

Money management por grupo:
Fixed Amount

Fixed amount:
$20,000

Maximum Quantity:
5,000

Comisión:
$0.01 por acción

MaxBarsReferenced:
100
```

La asignación descrita por la revista es:

```text
MR:
SPY 5m

TF:
AAPL 5m
```

El `.pmx` conserva también el input interno `My_Count` dentro del schema de VWAP Bands MR.

La revista declara:

```text
capital inicial total:
$60,000

capital atribuido:
$30,000 a cada estrategia
```

No se conserva en forma legible un ledger de:

```text
órdenes;
trades individuales;
equity diaria por grupo;
correlación;
contribución marginal al drawdown.
```

---

## 0.8 Utility Kit 1

Las páginas 19–23 son una reimpresión documental de:

```text
TSL:Friday Exit
TSL:Close On Last Bar
TSL:Strategy Equity
TSL:3rd Friday
$MinFluc
```

A diferencia de los Issues 13 y 14:

```text
el ZIP del Issue 15
no incluye UTILITY KIT 1.ELD.
```

Por tanto:

```text
ARTICLE_TEXT:
REPRINT

UTILITY_BINARY_IN_PACKAGE:
NO

NEW_STRATEGY_ID:
NO
```

La referencia contractual sigue siendo:

```text
SCC-2016-01-UTILITY-KIT-001
```

---

## 0.9 Resultado ejecutivo

| ID | Estrategia | Tipo real | Resultado publicado | Hallazgo crítico | Decisión |
|---|---|---|---|---|---|
| 030 | Overnight-Futures-Range Breakout | Breakout del rango 18:00–09:30 con rearmado, reversals y tres familias de exits | Un año de ES; $12.5k–$13.7k según exits; PF 1.21–1.22 | la señal long tiene evidencia in-sample; la short-only es negativa; todas las variantes tienen sólo 2.6–3.1 ticks de expectativa media | candidato prioritario de session/event replay, no edge aceptado |
| 031 | VWAP Bands MR | Reentrada confirmada desde extremos VWAP con exits al lado opuesto, parcial long, stale exit y EOD | SPY 5m; 2,021 trades; $6,929.20; PF 1.15 | sólo $3.43/trade y ~3.48 centavos/acción RT de margen; win rate supera breakeven por sólo ~3 puntos; hidden `My_Count` | candidato de price-location y complementarity research, no estrategia validada |
| PF-001 | VWAP TF + MR | Portfolio de dos estilos y dos símbolos | $26,203.63 sobre $60k; Sharpe 0.3263; DD mostrado ~3.5% | no aísla estrategia vs símbolo; no coincide aritméticamente con los dos informes aislados; métricas de drawdown no tienen base temporal claramente igualada | evidencia descriptiva de diversificación, no prueba causal |
| UK-001-R2 | Utility Kit 1 | Reimpresión de herramientas de engine | no aplica | no se incluye el `.ELD` | conservar como referencia, no como nuevo artefacto ejecutable |

Estado:

```text
ISSUE_15_STATUS:
DOCUMENTALLY_CLOSED

NEW_STRATEGIES:
2

PORTFOLIO_EXPERIMENTS:
1

UTILITY_KIT_REPRINTS:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

---

# Parte I — Estrategia 030: Overnight-Futures-Range Breakout

## 1) Identificación

- **ID:** `SCC-2016-03-STRAT-030`
- **Artículo:** *Overnight-Futures-Range Breakout Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas:** 4–9
- **Estilo declarado:** bar pattern
- **Mercados:** stock-index futures
- **Horizonte:** day trading
- **Activo del test:** E-mini S&P 500
- **Serie:** `@ES=107XN`
- **Intervalo:** 6 minutos
- **Historia:** un año terminado el 31 de diciembre de 2015
- **Tamaño:** un contrato
- **Comisión:** $2.32 por contrato y lado
- **Slippage publicado:** no indicado
- **LIBBT:** un minuto
- **Entry penetration:** un tick
- **Session start:** 18:00 ET
- **DayStartTime:** 09:30 ET

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, como máquina de sesión, órdenes y rearmado. |
| ¿Puede reproducirse exactamente con barras 6m? | **No.** Requiere replay más fino y prioridad de órdenes. |
| ¿LIBBT de 1m resuelve todo? | **No.** Un minuto puede tocar entry, target, stop y reversal. |
| ¿El overnight range es causal? | **Sí**, si se congela tras el bar que termina a las 09:30. |
| ¿El workspace contiene los tests publicados? | **No.** Sólo defaults `0.5/0.5`. |
| ¿La entrada long tiene evidencia básica? | **Sí, in-sample:** 61.54% en el test simétrico. |
| ¿La entrada short tiene evidencia básica? | **No:** neto negativo y PF 0.99. |
| ¿Los tres exit modes producen un edge claramente distinto? | **No.** Sus PF y net profits son muy similares. |
| ¿Está lista para operar? | **No.** Falta físico, costes, OOS, timing y order arbitration. |
| ¿Merece implementación? | **Sí**, con prioridad muy alta para Event State. |

Clasificación:

```text
SESSION_RANGE_EVENT
PENDING_STOP_ORDERS
REENTRY_ARMING_STATE
INTRABAR_ARBITRATION_REQUIRED
LONG_SHORT_ASYMMETRY
NOT_SCIENTIFICALLY_VALIDATED
```

---

## 2) Session timeline

La sesión de ES utilizada por el artículo:

```text
18:00 ET:
inicio de la sesión de futuros

18:00–09:30:
construcción del overnight range

09:30:
freeze de overnight high/low
tras completarse la barra correspondiente

después de 09:30:
órdenes de breakout

fin de la regular stock-market session:
liquidación
```

### Contrato temporal propuesto

```text
range_start_timestamp:
18:00 ET de la sesión anterior

range_end_timestamp:
09:30 ET

decision_timestamp:
cierre del bar marcado 09:30

first_order_activation:
inicio de la barra siguiente

day_trading_end:
fin de la ventana regular de acciones,
pendiente de reconciliar con el código
```

La revista afirma que no se opera antes de la primera barra cerrada después de las 09:30 y que el rango incluye el bar que termina a las 09:30.

La interpretación causal es:

> El bar de 09:30 puede formar el rango, pero no puede producir un fill retrospectivo. La primera ejecución posible es posterior al freeze.

---

## 3) Por qué se usan barras de 6 minutos

La regular session de acciones dura:

\[
390 \text{ minutos}
\]

\[
390 / 6 = 65 \text{ barras}
\]

Además, seis minutos permite una barra que termina exactamente a las 09:30 bajo la alineación utilizada.

Cambiar el intervalo altera:

```text
freeze timestamp;
overnight high/low;
número de oportunidades;
reset bars;
orden de fills;
hora de salida.
```

No es una decisión puramente computacional.

---

## 4) Overnight range

Para la sesión `d`:

\[
ONHigh_d =
\max
\{High_t:
18{:}00 \le t \le 09{:}30\}
\]

\[
ONLow_d =
\min
\{Low_t:
18{:}00 \le t \le 09{:}30\}
\]

Debe definirse si el timestamp identifica:

```text
inicio de barra;
fin de barra;
session date;
calendar date.
```

La revista utiliza bars etiquetadas por su cierre.

---

## 5) Entradas

Con:

```text
EntryTicks = 1
TickSize_ES = 0.25
```

### Long level

\[
LongEntry_d =
ONHigh_d + 1 \times TickSize
\]

### Short level

\[
ShortEntry_d =
ONLow_d - 1 \times TickSize
\]

### Órdenes

```text
long:
buy stop

short:
sell stop
```

Ambos lados pueden estar conceptualmente activos cuando la estrategia está flat.

---

## 6) Rearmado de entradas

La estrategia evita reentrar inmediatamente después de un profit target.

### Rearmado long

Después de una entrada long:

```text
long_armed = false
```

Para permitir otra entrada long debe existir una barra completa con:

\[
High_t \le ONHigh_d
\]

Después:

```text
long_armed = true
```

y un nuevo breakout puede activar la entrada.

### Rearmado short

\[
Low_t \ge ONLow_d
\]

reactiva la entrada short.

### Implicación

El sistema no cuenta simplemente cruces.

Mantiene dos estados independientes:

```text
long_armed
short_armed
```

Una barra de reset es evidencia de que el precio ha vuelto dentro o hasta la frontera del rango.

---

## 7) Reversal y señales opuestas

La revista indica que en los tests long-only/short-only se elimina la posibilidad de “reversing signals”.

Por tanto, la estrategia completa permite que:

```text
un breakout opuesto
cierre la posición actual
y establezca la contraria.
```

Queda sin resolver:

```text
si la reversión tiene prioridad sobre target/stop;
si ambas órdenes de breakout siguen vivas tras el primer fill;
si una reversión cancela el bracket anterior antes del nuevo fill;
cómo se contabiliza en la misma subbarra.
```

---

## 8) Exit mode 1 — Percent

### Long

\[
LongPT =
ONHigh_d
\left(1+\frac{ProfitTarget}{100}\right)
\]

\[
LongSL =
ONHigh_d
\left(1-\frac{Risk}{100}\right)
\]

### Short

\[
ShortPT =
ONLow_d
\left(1-\frac{ProfitTarget}{100}\right)
\]

\[
ShortSL =
ONLow_d
\left(1+\frac{Risk}{100}\right)
\]

### Hallazgo importante

Los exits se anclan a:

```text
overnight high/low
```

no al precio real de entrada.

Por tanto, el reward/risk efectivo desde el fill cambia por:

```text
EntryTicks;
slippage;
gap;
stop-order fill.
```

En múltiples entradas de la misma dirección durante el día:

```text
los niveles PT/SL son idénticos.
```

---

## 9) Exit mode 2 — ATR

La revista especifica que el ATR utilizado es el de la barra anterior a cada entrada.

Reconstrucción:

### Long

\[
LongPT =
ONHigh_d +
ProfitTarget \times ATR_{t-1}
\]

\[
LongSL =
ONHigh_d -
Risk \times ATR_{t-1}
\]

### Short

\[
ShortPT =
ONLow_d -
ProfitTarget \times ATR_{t-1}
\]

\[
ShortSL =
ONLow_d +
Risk \times ATR_{t-1}
\]

Cada reentrada puede recibir niveles distintos porque el ATR cambia intradía.

---

## 10) Exit mode 3 — Dollar

Con `BigPointValue_ES = $50/punto`:

### Conversión

\[
PriceDistance =
DollarAmount / BigPointValue
\]

Configuración publicada:

```text
PT = $950
SL = $250
```

equivale aproximadamente a:

```text
PT:
19 puntos

SL:
5 puntos
```

Los niveles vuelven a estar anclados al overnight high/low y son constantes durante la sesión.

---

## 11) EOD exit

Toda posición restante se liquida al finalizar la ventana de day trading.

La revista centra la actividad en:

```text
regular stock-market hours
09:30–16:00 ET
```

pero el código no es visible y la sesión natural del contrato de futuros termina a las 17:00.

Debe reconciliarse:

```text
16:00 stock close;
17:00 futures session close;
open de la última barra;
close de la última barra;
built-in SetExitOnClose;
template-specific session end.
```

Estado:

```text
DAY_TRADING_EXIT_TIMESTAMP_UNRESOLVED
```

---

## 12) Tres configuraciones optimizadas de salida

| Método | ProfitTarget | Risk | ATRLength | Reward/Risk nominal |
|---|---:|---:|---:|---:|
| Percent | 1.3% | 0.3% | N/A | 4.33 |
| ATR | 6 ATR | 6.6 ATR | 3 | 0.91 |
| Dollar | $950 | $250 | N/A | 3.80 |

Los tres modelos generan perfiles de payoff muy diferentes.

---

## 13) Resultados — tres exit schemes

| Métrica | Percent | ATR | Dollar |
|---|---:|---:|---:|
| Beneficio neto | $12,732.16 | $12,545.22 | $13,702.62 |
| Beneficio bruto | $74,357.60 | $73,315.84 | $74,790.46 |
| Pérdida bruta | -$61,625.44 | -$60,770.62 | -$61,087.84 |
| Profit Factor | 1.21 | 1.21 | 1.22 |
| Trades | 381 | 327 | 417 |
| Percent Profitable | 41.99% | 51.68% | 38.61% |
| Ganadoras | 160 | 169 | 161 |
| Perdedoras | 221 | 158 | 256 |
| Avg. Trade | $33.42 | $38.36 | $32.86 |
| Avg. Win | $464.74 | $433.82 | $464.54 |
| Avg. Loss | -$278.85 | -$384.62 | -$238.62 |
| Avg. Win/Loss | 1.67 | 1.13 | 1.95 |
| Mayor ganancia | $1,345.36 | $1,607.86 | $932.86 |
| Mayor pérdida | -$342.14 | -$1,529.64 | -$267.14 |
| Máx. ganadoras consecutivas | 6 | 7 | 5 |
| Máx. perdedoras consecutivas | 9 | 7 | 13 |
| Barras medias ganadoras | 49.44 | 40.12 | 42.82 |
| Barras medias perdedoras | 19.86 | 34.51 | 15.61 |

### Interpretación

Los net profits sólo difieren en:

\[
\$1,157.40
\]

aproximadamente un 8.9% del promedio de los tres resultados.

Sin embargo, sus distribuciones son completamente distintas:

```text
Percent/Dollar:
menor win rate
mayor payoff ratio

ATR:
mayor win rate
payoff casi simétrico
mayor cola negativa
```

Esto muestra que un resultado neto parecido no identifica un único mecanismo de salida superior.

---

## 14) Fragilidad a ticks de slippage

Valor del tick ES:

\[
\$12.50
\]

Expectativa publicada:

```text
Percent:
$33.42 = 2.67 ticks

ATR:
$38.36 = 3.07 ticks

Dollar:
$32.86 = 2.63 ticks
```

Impacto adicional:

| Coste añadido por round trip | Percent | ATR | Dollar |
|---|---:|---:|---:|
| 1 tick total ($12.50) | $20.92 | $25.86 | $20.36 |
| 1 tick por lado ($25) | $8.42 | $13.36 | $7.86 |
| 2 ticks por lado ($50) | negativo | negativo | negativo |

La comisión de $4.64 por round trip ya se modela, pero no el slippage.

El edge agregado es pequeño frente a una ejecución realista adversa.

---

## 15) Disección de la señal básica

La revista realiza un test especialmente valioso:

```text
long y short por separado;
sin reversal;
target = stop;
EOD exit conservado;
optimización separada del threshold simétrico.
```

### Long-only

```text
ProfitTarget = 1.1%
Risk = 1.1%
```

| Métrica | Resultado |
|---|---:|
| Net Profit | $14,261.48 |
| Profit Factor | 1.56 |
| Trades | 143 |
| Percent Profitable | 61.54% |
| Ganadoras | 88 |
| Perdedoras | 55 |
| Avg. Trade | $99.73 |
| Avg. Win | $451.75 |
| Avg. Loss | -$463.50 |
| Ratio | 0.97 |
| Mayor ganancia | $1,132.86 |
| Mayor pérdida | -$1,179.64 |

### Short-only

```text
ProfitTarget = 0.7%
Risk = 0.7%
```

| Métrica | Resultado |
|---|---:|
| Net Profit | -$395.24 |
| Profit Factor | 0.99 |
| Trades | 166 |
| Percent Profitable | 45.78% |
| Ganadoras | 76 |
| Perdedoras | 90 |
| Avg. Trade | -$2.38 |
| Avg. Win | $461.15 |
| Avg. Loss | -$393.81 |
| Ratio | 1.17 |
| Mayor ganancia | $732.86 |
| Mayor pérdida | -$754.64 |

### Conclusión

```text
LONG BREAKOUT:
contiene evidencia in-sample favorable

SHORT BREAKOUT:
no demuestra valor básico
```

El resultado de la estrategia completa puede beneficiarse de:

```text
asimetría de exits;
reversals;
interacción long/short;
bull-market regime;
optimización.
```

No debe atribuirse automáticamente al breakout short.

---

## 16) Limitación del test binario

Aunque target y stop sean simétricos, no todos los trades terminan por uno de ellos.

El EOD exit permanece activo.

Por tanto:

```text
61.54% long
no es exactamente
“probabilidad de tocar +1.1% antes de -1.1%”
para todas las observaciones.
```

Hay una tercera ruta:

```text
session end.
```

Para una disección causal completa debe publicarse:

```text
target exits;
stop exits;
EOD exits;
reversals;
fills ambiguos.
```

La revista lo propone, pero no muestra la tabla de atribución.

---

## 17) Order arbitration

Durante un minuto pueden tocarse:

```text
long entry;
short entry;
profit target;
stop loss;
reversal level;
EOD condition.
```

LIBBT de un minuto no determina el path intraminuto.

TSIS debe clasificar:

```text
UNAMBIGUOUS_FILL
ENTRY_TARGET_SAME_INTERVAL
ENTRY_STOP_SAME_INTERVAL
TARGET_STOP_SAME_INTERVAL
ENTRY_REVERSAL_SAME_INTERVAL
MULTI_EVENT_AMBIGUOUS
```

No debe resolverlos siempre a favor del backtest.

---

## 18) Contrato continuo

`@ES=107XN` es una serie analítica continua sin back adjustment.

Riesgos:

```text
el continuo no es operable;
el overnight range puede cruzar un roll;
un gap de roll puede fabricar un breakout;
el volumen/liquidez pertenecen a contratos físicos;
una posición intradía debe mapearse al contrato activo;
la regla de roll debe ser point-in-time.
```

La reproducción científica requiere:

```text
signal reference series;
physical execution series;
contract mapping;
roll state;
session mapping.
```

---

## 19) Auditoría científica

### 19.1 Sólo un año

No cubre suficientes regímenes.

### 19.2 Un único futuro

No se muestran NQ o YM.

### 19.3 Optimización de exits

Cada método fue optimizado en la misma muestra.

### 19.4 Optimización del test simétrico

También se seleccionaron los mayores thresholds simétricos rentables.

### 19.5 Sin OOS

No existe holdout.

### 19.6 Slippage cero

Crítico para stop entries.

### 19.7 Long/short asimétricos

La rama short básica es negativa.

### 19.8 EOD attribution ausente

No se sabe cuánto resultado procede de la ventana de cierre.

### 19.9 Intrabar path

No resuelto.

### 19.10 Continuous futures

No operable.

### 19.11 Session timezone

`930` depende del chart timezone.

### 19.12 Overnight-range definition

Debe congelarse frente a DST, holidays y maintenance breaks.

### 19.13 Exit anchored to range

El riesgo real no equivale exactamente al input.

### 19.14 Multiple reentries

Los trades del mismo día no son independientes.

### 19.15 Same-day dependence

Cuatro entradas en una sesión no son cuatro muestras independientes.

---

## 20) Contrato TSIS

### Datos

```text
physical ES trades/quotes
1m o tick replay
session calendar CME
stock-market calendar
roll mapping
tick size
BigPointValue
```

### Session State

```text
trading_session_id
session_open_timestamp
overnight_range_start
overnight_range_end
overnight_high
overnight_low
overnight_high_timestamp
overnight_low_timestamp
range_frozen
regular_window_active
day_exit_due
```

### Order State

```text
long_armed
short_armed
long_entry_stop
short_entry_stop
exit_mode
profit_target
stop_loss
atr_at_entry
entry_setup_id
reentry_count_today
position
```

### Eventos

```text
OVERNIGHT_RANGE_STARTED
OVERNIGHT_HIGH_UPDATED
OVERNIGHT_LOW_UPDATED
OVERNIGHT_RANGE_FROZEN
LONG_BREAKOUT_TRIGGERED
SHORT_BREAKOUT_TRIGGERED
LONG_REARMED
SHORT_REARMED
TARGET_FILLED
STOP_FILLED
REVERSAL_FILLED
DAY_EXIT
```

### Estados de indisponibilidad

```text
SESSION_TEMPLATE_UNRESOLVED
OVERNIGHT_RANGE_INCOMPLETE
DAYSTART_BAR_MISSING
PHYSICAL_CONTRACT_UNRESOLVED
ROLL_DURING_RANGE
INTRABAR_SEQUENCE_AMBIGUOUS
DAY_EXIT_TIMESTAMP_UNRESOLVED
MISSING_QUOTE_DATA
```

---

## 21) Pseudocódigo funcional

```python
on_futures_session_start:
    overnight_high = -inf
    overnight_low = +inf
    range_frozen = False
    long_armed = True
    short_armed = True
    reentry_count = 0

while timestamp <= day_start_time:
    overnight_high = max(overnight_high, high)
    overnight_low = min(overnight_low, low)

on_bar_close_at_day_start_time:
    range_frozen = True
    long_entry_stop = overnight_high + entry_ticks * tick_size
    short_entry_stop = overnight_low - entry_ticks * tick_size

after_range_freeze:

    if not long_armed and high <= overnight_high:
        long_armed = True

    if not short_armed and low >= overnight_low:
        short_armed = True

    if long_armed:
        maintain_buy_stop(long_entry_stop)

    if short_armed:
        maintain_sell_stop(short_entry_stop)

on_long_fill:
    long_armed = False
    configure_exit_levels(
        anchor=overnight_high,
        method=exit_mode,
        atr=atr_previous_bar
    )

on_short_fill:
    short_armed = False
    configure_exit_levels(
        anchor=overnight_low,
        method=exit_mode,
        atr=atr_previous_bar
    )

on_regular_window_end:
    flatten()
```

---

## 22) Plan de réplica y falsificación

### Fase 1 — Session checksum

Reproducir diariamente:

```text
overnight high;
overnight low;
timestamps;
first tradable bar;
end-of-day timestamp.
```

### Fase 2 — Entry checksum

```text
entry tick;
long/short arming;
reset bars;
reentries;
reversals.
```

### Fase 3 — Exit modes

Reproducir por separado:

```text
Percent 1.3/0.3
ATR 6/6.6/3
Dollar 950/250
```

### Fase 4 — Exit attribution

Para cada trade:

```text
target;
stop;
reversal;
EOD;
ambiguous.
```

### Fase 5 — Signal dissection

Preregistrar:

```text
long-only 1.1/1.1
short-only 0.7/0.7
```

y ejecutar postpublicación sin reoptimizar.

### Fase 6 — Cost stress

```text
0.5 tick/lado
1 tick/lado
2 ticks/lado
quotes reales
stop-order slippage
```

### Fase 7 — Physical futures

Contrato real y roll.

### Fase 8 — Other indices

```text
NQ
YM
RTY
```

con inputs congelados en el primer pass.

### Fase 9 — Regime features

Preregistrar:

```text
overnight_range / ATR
overnight_range percentile
overnight gap vs prior close
location of prior close within range
time of overnight high/low
premarket trend
day-of-week
macro-event flag
```

### Fase 10 — Postpublication

Desde marzo de 2016 en adelante.

---

## 23) Decisión — Overnight-Futures-Range Breakout

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
session state
+
range freeze
+
reentry arming
+
multi-exit comparison
+
signal dissection

PRIORIDAD:
muy alta para engine validation

SIGUIENTE GATE:
SCC-030-SESSION-ORDER-EXIT-ATTRIBUTION-AND-OOS-GATE
```

---

# Parte II — Estrategia 031: VWAP Bands MR

## 24) Identificación

- **ID:** `SCC-2016-03-STRAT-031`
- **Artículo:** *VWAP Bands MR Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas:** 12–17
- **Estilo:** mean reversion
- **Mercado:** equities
- **Horizonte:** day trading
- **Activo:** SPY
- **Intervalo:** 5 minutos
- **Historia:** seis años terminando el 31 de diciembre de 2015
- **Capital inicial:** $30,000
- **Trade size:** $20,000, redondeado hacia abajo a una acción
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **MaxBarsBack:** 100
- **Inputs:** `2.5 / 3 / 2 / 2.5 / 2.5 / 2.5 / 60`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí**, compartiendo el VWAP state del Issue 13. |
| ¿Puede replicarse exactamente? | **No todavía.** Fórmula VWAP/sigma y partial fills no certificadas. |
| ¿Entra al tocar el extremo? | **No.** Espera un cruce de regreso hacia el interior. |
| ¿Sale en VWAP? | **No.** Exige atravesar al lado opuesto de las bandas. |
| ¿Usa partial exits? | **Sí, sólo en longs bajo los defaults.** |
| ¿La muestra es grande? | En trades sí: 2,021. En independencia, no necesariamente. |
| ¿La expectativa es amplia? | **No.** $3.43 por trade. |
| ¿El win rate es robusto frente a degradación? | **No demasiado.** Sólo ~3 puntos sobre el breakeven observado. |
| ¿El portfolio demuestra complementarity? | **No causalmente.** Mezcla estilo y símbolo. |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
INTRADAY_VWAP_MEAN_REVERSION
CONFIRMED_REENTRY_FROM_EXTREME
PARTIAL_EXIT_STATE
STALE_POSITION_EXIT
COST_FRAGILE
NOT_SCIENTIFICALLY_VALIDATED
```

---

## 25) VWAP y bandas

La reconstrucción general es la misma familia del Issue 13.

\[
VWAP_t =
\frac{
\sum_{i=s(t)}^t P_i V_i
}{
\sum_{i=s(t)}^t V_i
}
\]

\[
Upper_{k,t} =
VWAP_t + k\sigma_t
\]

\[
Lower_{k,t} =
VWAP_t - k\sigma_t
\]

Quedan sin resolver:

```text
P_i:
typical price, OHLC4, midpoint o Close

sigma:
sample/population

ponderación:
con volumen o sin volumen

ventana:
inclusive o lagged

session:
regular session exacta
```

Las bandas se recalculan durante el día y se reinician cada sesión.

---

## 26) Entrada mean-reversion confirmada

### Long

\[
Close_{t-1} \le Lower_{2.5,t-1}
\]

\[
Close_t > Lower_{2.5,t}
\]

Entrada:

```text
buy at open t+1
```

La señal no compra la primera caída.

Es:

> Precio estuvo bajo la banda extrema y después cruza de regreso hacia arriba.

### Short

\[
Close_{t-1} \ge Upper_{3,t-1}
\]

\[
Close_t < Upper_{3,t}
\]

Entrada:

```text
short at open t+1
```

Es una confirmación de retorno desde sobreextensión.

---

## 27) Asimetría de entradas

```text
long:
-2.5 sigma

short:
+3 sigma
```

El lado short exige una sobreextensión mayor.

Esto afecta:

```text
frecuencia;
selección de regímenes;
holding;
cantidad de trades;
expectativa.
```

No es una simple versión simétrica de mean reversion.

---

## 28) Exits long

### Parcial

Cuando:

\[
Close
\text{ cruza sobre }
Upper_{2}
\]

se cierra:

```text
50% de la posición
en la apertura siguiente.
```

### Final

Cuando:

\[
Close
\text{ cruza sobre }
Upper_{2.5}
\]

se cierra el resto.

### Hallazgo conceptual

La estrategia no se limita a volver al VWAP.

Bajo una lectura estática, el recorrido sería:

```text
entrada:
desde debajo de -2.5 sigma

parcial:
sobre +2 sigma

final:
sobre +2.5 sigma
```

Es un desplazamiento de 4.5–5 sigmas entre fronteras.

Sin embargo, las bandas son dinámicas, así que la distancia efectiva cambia durante el trade.

---

## 29) Exits short

Defaults:

```text
SX1 = -2.5 sigma
SX2 = -2.5 sigma
```

Al ser iguales:

```text
no se utiliza un partial short exit efectivo;
la posición se cierra completamente.
```

Queda por resolver cómo TradeStation arbitra dos condiciones idénticas:

```text
partial y final en la misma barra;
orden de las órdenes;
cancelación;
cantidad.
```

---

## 30) Partial-exit rounding

El tamaño inicial se deriva de $20,000 y puede ser impar.

El informe muestra:

```text
máximo long:
195 acciones
```

Cerrar “half” requiere una convención:

```text
floor;
ceiling;
nearest;
lot residual.
```

El `.ELD` no permite certificarla.

Estado:

```text
PARTIAL_EXIT_ROUNDING_UNRESOLVED
```

---

## 31) Max holding

```text
Max_Hold_Length = 60 barras
```

Con 5 minutos:

\[
60 \times 5 =
300 \text{ minutos}
\]

La salida se programa en la apertura siguiente cuando se cumple el límite.

Debe fijarse:

```text
si la entry bar cuenta;
si se usa >60 o >=60;
cómo afectan partial exits;
si EOD tiene prioridad.
```

El informe muestra un único even trade con:

```text
63 barras de media
```

aunque el máximo declarado es 60.

Esto indica que:

```text
la métrica de barras de TradeStation;
el momento de fill;
el conteo;
o una excepción de sesión
```

no equivalen directamente al input nominal.

---

## 32) EOD exit y overnight exceptions

La regla pretende:

```text
salir en la apertura de la última barra regular.
```

Si no es posible:

```text
salir en la primera barra del día siguiente.
```

Resultado publicado:

```text
6 de 2,021 trades
≈ 0.3%
```

quedaron overnight, principalmente por:

```text
early closes;
holidays;
halts.
```

La excepción debe ser un evento explícito, no un warning manual.

---

## 33) Resultados publicados

### Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $6,929.20 |
| Beneficio bruto | $53,460.46 |
| Pérdida bruta | -$46,531.26 |
| Profit Factor | 1.15 |
| Operaciones | 2,021 |
| Ganadoras | 1,383 |
| Perdedoras | 637 |
| Even | 1 |
| Percent Profitable | 68.48% |
| Expectativa media | $3.43 |
| Ganancia media | $38.66 |
| Pérdida media | -$73.05 |
| Ratio ganancia/pérdida | 0.53 |
| Mayor ganancia | $503.96 |
| Mayor pérdida | -$456.50 |
| Máx. ganadoras consecutivas | 20 |
| Máx. perdedoras consecutivas | 8 |
| Barras medias ganadoras | 28.50 |
| Barras medias perdedoras | 45.99 |
| Barras medias even | 63.00 |
| Máximo tamaño | 195 acciones |
| Acciones acumuladas | 199,356 |
| Account Size Required | $1,550.15 |
| Return on Initial Capital | 23.10% |
| Annual Rate of Return | 3.47% |
| Return Retracement Ratio | 0.23 |
| RINA Index | 367.89 |
| Percent of Time in Market | 9.50% |
| Drawdown semanal aproximado | 4.5% |

### Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $4,780.70 | $2,148.50 |
| Profit Factor | 1.15 | 1.14 |
| Trades | 1,373 | 648 |
| Percent Profitable | 70.36% | 64.35% |
| Ganadoras | 966 | 417 |
| Perdedoras | 407 | 230 |
| Even | 0 | 1 |
| Expectativa media | $3.48 | $3.32 |
| Ganancia media | $37.32 | $41.76 |
| Pérdida media | -$76.82 | -$66.37 |
| Ratio | 0.49 | 0.63 |
| Mayor ganancia | $393.49 | $503.96 |
| Mayor pérdida | -$456.50 | -$410.80 |
| Máx. ganadoras consecutivas | 18 | 14 |
| Máx. perdedoras consecutivas | 8 | 9 |
| Barras medias ganadoras | 30.60 | 23.65 |
| Barras medias perdedoras | 46.08 | 45.82 |
| Acciones acumuladas | 131,497 | 67,859 |

### Contribución long

\[
4{,}780.70 / 6{,}929.20
\approx 68.99\%
\]

---

## 34) Fragilidad de win rate

Breakeven observado:

\[
p^\* =
\frac{AvgLoss}
{AvgWin + AvgLoss}
\]

### Agregado

\[
p^\* =
\frac{73.05}{38.66+73.05}
\approx 65.39\%
\]

Observado:

```text
68.48%
```

Margen:

```text
3.09 puntos porcentuales
```

### Long

```text
breakeven ≈ 67.30%
observado = 70.36%
margen ≈ 3.06 puntos
```

### Short

```text
breakeven ≈ 61.38%
observado = 64.35%
margen ≈ 2.97 puntos
```

Una degradación pequeña de la tasa de acierto elimina la expectativa.

---

## 35) Fragilidad frente a costes

Cantidad media:

\[
199{,}356 / 2{,}021
\approx 98.64 \text{ acciones}
\]

Margen de coste adicional:

\[
3.43 / 98.64
\approx \$0.0348
\]

Es decir:

```text
≈ 3.48 centavos por acción round trip
≈ 1.74 centavos por acción y lado
```

eliminarían la expectativa agregada.

La comisión ya está incluida.

No se publica:

```text
spread;
slippage;
partial-fill friction;
market-on-open friction;
short locate;
adverse selection;
latencia.
```

---

## 36) Duración de winners y losers

Ganadores:

\[
28.50 \times 5 =
142.5 \text{ minutos}
\]

Perdedores:

\[
45.99 \times 5
\approx 230 \text{ minutos}
\]

Los perdedores duran aproximadamente un 61% más.

Es coherente con mean reversion:

```text
los trades que revierten
lo hacen relativamente pronto;

los fallos
se quedan estancados hasta stale/EOD exit.
```

También indica que el max-hold policy forma parte importante del control de pérdidas.

---

## 37) Sensibilidad publicada

### Long exits

Superficie:

```text
LX1_Band_Num × LX2_Band_Num
```

La revista describe una superficie muy plana.

Defaults:

```text
2 / 2.5
```

no son el pico.

### Short exits

Superficie:

```text
SX1_Band_Num × SX2_Band_Num
```

Defaults:

```text
2.5 / 2.5
```

Se seleccionan por métricas ajustadas por riesgo y eliminan el partial short.

### Limitación

Las superficies:

```text
no están en OptimizationData;
no tienen tabla numérica;
no publican candidate count;
no publican ranking;
no corrigen multiple testing.
```

La apariencia plana es evidencia descriptiva favorable, no validación.

---

## 38) ¿Dónde podría estar el edge?

Hipótesis principal:

> Después de una sobreextensión intradía relativa al VWAP, el cruce de regreso hacia el interior predice una reversión suficientemente profunda como para atravesar la referencia y alcanzar bandas del lado opuesto.

Mecanismos posibles:

```text
liquidity restoration;
market-maker inventory;
exhaustion;
temporary order imbalance;
index mean reversion;
closing-auction pull;
institutional execution around VWAP.
```

Hipótesis alternativas:

```text
SPY microstructure específica;
selection de bandas;
high win-rate con tail losses;
EOD effect;
band self-movement;
sizing temporal;
cost understatement;
partial-exit accounting.
```

---

## 39) Auditoría científica

### 39.1 Un único activo

Sólo SPY.

### 39.2 Parámetros optimizados

El artículo lo reconoce.

### 39.3 Sin OOS

No existe holdout.

### 39.4 PF 1.15

Margen pequeño.

### 39.5 Expectativa $3.43

Extremadamente sensible a costes.

### 39.6 VWAP estimado

No tick VWAP.

### 39.7 Sigma no certificada

Puede cambiar señales.

### 39.8 Dynamic-band self-inclusion

El cierre mueve la banda que cruza.

### 39.9 Partial-exit rounding

No resuelto.

### 39.10 Hidden `My_Count`

No documentado.

### 39.11 Max-hold count

La métrica de 63 barras requiere reconciliación.

### 39.12 EOD exceptions

Seis overnights.

### 39.13 Long/short asymmetric thresholds

Pueden estar seleccionados.

### 39.14 Short partial disabled

Resultado específico de SPY y periodo.

### 39.15 Trades no independientes

Múltiples trades por sesión comparten estado.

---

## 40) Contrato TSIS

### Datos

```text
SPY 5m OHLCV
SPY trades/quotes
corporate actions
regular-session calendar
halts
early closes
```

### VWAP State

```text
session_id
bar_index
cum_volume
cum_price_volume
vwap
sigma
upper_2
upper_2_5
upper_3
lower_2
lower_2_5
lower_3
warmup_complete
```

### Position State

```text
entry_direction
entry_quantity
remaining_quantity
entry_band
entry_timestamp
bars_since_entry
partial_exit_completed
max_hold_length
eod_exit_due
overnight_exception
```

### Eventos

```text
LOWER_BAND_REENTRY_LONG
UPPER_BAND_REENTRY_SHORT
LONG_PARTIAL_EXIT
LONG_FINAL_EXIT
SHORT_FINAL_EXIT
STALE_EXIT
EOD_EXIT
EOD_EXIT_MISSED
NEXT_SESSION_FORCED_EXIT
```

### Estados de indisponibilidad

```text
VWAP_FORMULA_UNRESOLVED
SIGMA_FORMULA_UNRESOLVED
SESSION_TEMPLATE_UNRESOLVED
PARTIAL_EXIT_ROUNDING_UNRESOLVED
MY_COUNT_SEMANTICS_UNRESOLVED
MAX_HOLD_COUNT_UNRESOLVED
MISSING_NEXT_OPEN
CORPORATE_ACTION_UNRESOLVED
```

---

## 41) Pseudocódigo funcional

```python
on_regular_session_start:
    reset_vwap_state()
    position = 0
    remaining_qty = 0

for each completed 5m bar t:

    update_vwap_and_bands(t)

    if warmup_complete and flat:

        long_signal = (
            close[t - 1] <= lower_2_5[t - 1]
            and close[t] > lower_2_5[t]
        )

        short_signal = (
            close[t - 1] >= upper_3[t - 1]
            and close[t] < upper_3[t]
        )

        if long_signal:
            schedule_long(next_open)

        elif short_signal:
            schedule_short(next_open)

    if long:

        if not partial_exit_completed:
            if crosses_up(close, upper_2):
                schedule_partial_exit(
                    next_open,
                    fraction=0.5
                )

        if crosses_up(close, upper_2_5):
            schedule_full_exit(next_open)

    if short:

        if crosses_down(close, lower_2_5):
            schedule_full_exit(next_open)

    if bars_since_entry >= 60:
        schedule_full_exit(next_open)

    if next_bar_is_last_regular_bar:
        schedule_full_exit(open_of_last_regular_bar)
```

---

## 42) Plan de réplica y falsificación

### Fase 1 — Formula reconciliation

```text
price proxy;
volume source;
sigma;
inclusive/lagged.
```

### Fase 2 — Checksum histórico

```text
2,021 trades
1,373 long
648 short
net ≈ $6,929.20
PF ≈ 1.15
6 overnight exceptions
```

### Fase 3 — Partial exits

Reconciliar:

```text
odd quantities;
trade counting;
same-bar partial/final;
commissions;
remaining position.
```

### Fase 4 — Max hold

Determinar por qué aparece el trade de 63 barras.

### Fase 5 — Cost stress

```text
1 cent/share RT
2 cents/share RT
3.5 cents/share RT
quotes reales
```

### Fase 6 — Ablaciones

| Variante | Pregunta |
|---|---|
| entry at first touch | ¿el cross-back confirma valor? |
| exit at VWAP | ¿es necesario cruzar al lado opuesto? |
| no partial exits | ¿mejoran realmente? |
| symmetric entries | ¿2.5/3 está seleccionado? |
| fixed hold | ¿la dinámica de bands aporta valor? |
| long-only | ¿short añade valor después de costes? |

### Fase 7 — Cross-sectional

```text
SPY
QQQ
IWM
DIA
liquid mega-caps
```

### Fase 8 — Postpublication

Desde marzo de 2016, inputs congelados.

---

## 43) Decisión — VWAP Bands MR

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
price-location reversal
+
dynamic reference
+
partial position state
+
stale-trade control

PRIORIDAD:
alta

SIGUIENTE GATE:
SCC-031-VWAP-MR-FORMULA-PARTIAL-COST-AND-OOS-GATE
```

---

# Parte III — Experimento de portfolio: TF + MR

## 44) Configuración

```text
Strategy Group 1:
TSL:VWAP Bands TF
AAPL 5m
$30,000 capital
$20,000 fixed amount

Strategy Group 2:
TSL:VWAP Bands MR
SPY 5m
$30,000 capital
$20,000 fixed amount

Portfolio initial capital:
$60,000
```

---

## 45) Resultado combinado

| Métrica | Resultado |
|---|---:|
| Total Return | $26,203.63 |
| Total Realized Return | $26,203.63 |
| Gross Profit | $181,735.14 |
| Gross Loss | -$155,531.51 |
| Open Trade P/L | $0 |
| Trades | 4,299 |
| Ganadores | 2,389 |
| Perdedores | 1,910 |
| Percent Profitable | 55.57% |
| Average Trade | $6.10 |
| Standard Deviation Trade | $116.85 |
| Largest Win | $750.08 |
| Largest Loss | -$734.31 |
| Profit Factor | 1.17 |
| Avg. Win / Avg. Loss | 0.93 |
| Sharpe Ratio | 0.3263 |
| K-Ratio | 0.4679 |
| Return Retracement Ratio | 6.3384 |
| Compounded Annual Return | 6.23% |
| Compounded Monthly Return | 0.50% |
| Average Annual Return | $4,367.27 |
| Average Annual Return (%) | 6.29% |
| Average Monthly Return | $363.94 |
| Average Monthly Return (%) | 0.51% |
| Positive Days | 52.12% |
| Positive Months | 69.44% |
| Positive Years | 83.33% |
| Drawdown visual aproximado | 3.5% |

Retorno sobre el capital inicial:

\[
26{,}203.63 / 60{,}000
\approx 43.67\%
\]

---

## 46) La suma no coincide con los informes aislados

Informes individuales:

```text
VWAP TF:
$21,485.52
2,282 trades
periodo termina 30/11/2015

VWAP MR:
$6,929.20
2,021 trades
periodo termina 31/12/2015
```

Suma simple:

\[
21{,}485.52 + 6{,}929.20
=
28{,}414.72
\]

Portfolio:

\[
26{,}203.63
\]

Diferencia:

\[
-2{,}211.09
\]

Trades individuales:

\[
2{,}282 + 2{,}021
=
4{,}303
\]

Portfolio:

```text
4,299
```

Diferencia:

```text
-4 trades
```

Posibles causas:

```text
periodos de fin distintos;
boundary liquidation;
Portfolio Maestro functions;
settings no idénticos;
calendar alignment;
trade-size timing;
MaxBarsBack;
commission handling;
data revision;
último mes adicional en AAPL.
```

Sin trade lists no puede reconciliarse.

Por tanto:

> El portfolio no debe tratarse como la suma mecánica de los dos informes aislados.

---

## 47) Qué demuestra realmente la combinación

Demuestra in-sample que:

```text
dos streams de P/L distintos
sobre dos símbolos distintos
pueden producir una curva agregada
aparentemente más suave.
```

No demuestra aisladamente que:

```text
mean reversion complemente trend following;
la mejora proceda del estilo;
la mejora proceda del símbolo;
la mejora sobreviva OOS;
el peso 50/50 sea óptimo o robusto.
```

El experimento confunde:

```text
strategy-style diversification
+
instrument diversification
+
different trade frequencies
+
different end dates
+
capital scaling.
```

---

## 48) Drawdown no completamente comparable

La revista compara:

```text
VWAP TF:
drawdown semanal ~6%

VWAP MR:
drawdown semanal ~4.5%

portfolio:
drawdown gráfico ~3.5%
```

No queda demostrado que las tres cifras utilicen exactamente:

```text
misma frecuencia;
misma definición;
misma equity basis;
mismo periodo;
mismo marked-to-market treatment.
```

La reducción es prometedora, pero no certificada como comparación homogénea.

---

## 49) Sharpe y complementarity

El portfolio publica:

```text
Sharpe = 0.3263
```

La revista afirma que aumentó ligeramente.

No muestra en las mismas páginas:

```text
Sharpe de TF bajo Portfolio Maestro;
Sharpe de MR bajo Portfolio Maestro;
correlación de retornos;
marginal Sharpe contribution;
confidence interval.
```

La afirmación es descriptiva, no una prueba estadística.

---

## 50) Test científico de complementarity

Debe comparar cuatro diseños:

| Diseño | Pregunta |
|---|---|
| TF AAPL + MR SPY | resultado publicado |
| TF SPY + MR SPY | ¿complementa el estilo en el mismo símbolo? |
| TF AAPL + MR AAPL | misma pregunta en AAPL |
| TF AAPL + TF SPY | ¿la mejora procede sólo de símbolos? |
| MR AAPL + MR SPY | ¿la mejora procede sólo de símbolos? |

Además:

```text
equal capital;
equal volatility;
equal drawdown budget;
equal gross exposure;
same sample;
same costs.
```

---

## 51) Contrato TSIS para portfolio

### Portfolio State

```text
portfolio_timestamp
group_id
strategy_id
symbol
allocated_capital
position_notional
realized_pnl
unrealized_pnl
daily_return
gross_exposure
net_exposure
```

### Diversification evidence

```text
return correlation
downside correlation
overlap in market time
joint drawdown
marginal contribution to risk
marginal contribution to return
diversification ratio
```

### Estados de indisponibilidad

```text
UNMATCHED_TEST_PERIODS
GROUP_SETTINGS_NOT_IDENTICAL
TRADE_LIST_RECONCILIATION_MISSING
DRAWDOWN_BASIS_UNRESOLVED
INDIVIDUAL_SHARPE_MISSING
```

---

## 52) Decisión — Portfolio TF + MR

```text
CONSERVAR:
sí, como hipótesis de diversificación

ACEPTAR COMPLEMENTARITY CAUSAL:
no

VALOR PRINCIPAL:
mostrar que el portfolio
debe evaluarse como objeto propio

PRIORIDAD:
alta después de replicar
ambas estrategias por separado

GATE:
SCC-PF-001-MATCHED-COMPLEMENTARITY-GATE
```

---

# Parte IV — Utility Kit 1 reimpreso

## 53) Estado

El texto es la misma familia documental ya auditada:

```text
Friday Exit
Close On Last Bar
Strategy Equity
3rd Friday
$MinFluc
```

No se incluye binario en el ZIP.

No se crea un nuevo ID.

### Contratos que siguen vigentes

```text
Friday Exit:
calendar/session exit, no simple weekday

Close On Last Bar:
sample-boundary liquidation,
no salida económica

Strategy Equity:
realized, unrealized y total separados

3rd Friday:
calendar reference,
no expiration universal

$MinFluc:
instrument metadata con effective date
```

---

# Parte V — Ideas transversales del Issue 15

## 54) Diseccionar la señal antes de optimizar la gestión

El test long-only/short-only con targets simétricos es una de las mejores ideas metodológicas del número.

Secuencia correcta:

```text
1. congelar entrada;
2. eliminar reversals;
3. igualar target y stop;
4. separar long/short;
5. atribuir target/stop/EOD;
6. estudiar la señal;
7. sólo después diseñar exits.
```

---

## 55) Resultados netos similares pueden esconder estrategias distintas

Los tres exit modes del overnight system producen net profits parecidos, pero:

```text
win rate;
tail loss;
holding period;
trade count;
payoff ratio
```

son diferentes.

---

## 56) Un nivel de salida puede estar anclado al setup, no al fill

En Overnight:

```text
PT/SL se miden desde ONHigh/ONLow.
```

El risk contract debe indicar el anchor.

---

## 57) El rearmado es estado persistente

No puede reconstruirse sólo con el cruce actual.

---

## 58) Una mean reversion puede esperar confirmación

VWAP MR no compra mientras cae.

Compra al cruzar de regreso.

---

## 59) Una mean reversion puede cruzar más allá de la media

Los exits long están en `+2/+2.5 sigma`, no en VWAP.

---

## 60) Partial exits necesitan un ledger de cantidades

Debe conservarse:

```text
initial quantity;
partial quantity;
remaining quantity;
rounding;
commission per leg.
```

---

## 61) High win rate con payoff adverso es frágil

VWAP MR supera su breakeven observado sólo por unos tres puntos porcentuales.

---

## 62) Combinar estrategias no prueba complementarity

Hay que separar:

```text
style;
symbol;
capital;
period;
risk.
```

---

## 63) Un portfolio puede no coincidir con la suma de charts

La diferencia de $2,211.09 y cuatro trades exige reconciliación.

---

## 64) `OptimizationData` necesita lineage

Debe incluir:

```text
strategy hash;
input schema;
dataset;
side enabled;
objective;
trial id;
timestamp.
```

---

## 65) Un input interno no documentado bloquea la reproducción

`My_Count` debe resolverse antes de certificar VWAP MR.

---

## 66) El número de trades no es independencia

Overnight:

```text
reentries del mismo día
```

VWAP:

```text
múltiples trades de la misma sesión
```

comparten condiciones latentes.

---

## 67) Ideas secundarias de backtesting

1. Congelar session ranges por timestamp.
2. Separar setup anchor y fill price.
3. Comparar exit families con la misma entrada.
4. Publicar exit attribution.
5. Testar long y short como hipótesis distintas.
6. Modelar reentry arming.
7. Registrar reversal reason.
8. Separar true VWAP y bar VWAP.
9. Versionar partial-exit rounding.
10. Guardar stale-exit count.
11. Registrar EOD exceptions.
12. Exigir same-period portfolio comparisons.
13. Distinguir style y symbol diversification.
14. Reconciliar chart trades con portfolio trades.
15. Guardar optimization lineage.
16. Tratar hidden inputs como contract violations.
17. Stressar costes en ticks y por acción.
18. Evaluar correlation y joint drawdown.

---

# Parte VI — Registro consolidado para TSIS

## 68) Objetos de información afectados

### Overnight Breakout

```text
price_movement
volatility_range_state
price_location_intraday
event_state
session_state
market_microstructure_state
```

### VWAP Bands MR

```text
price_location_intraday
trading_activity
volatility_range_state
market_microstructure_state
position_state
```

### Portfolio

```text
portfolio_state
capital_allocation
risk_state
strategy_correlation
```

---

## 69) Eventos candidatos

### Overnight

```text
event_type:
overnight_range_frozen
```

```text
event_type:
regular_session_overnight_high_break
```

```text
event_type:
regular_session_overnight_low_break
```

```text
event_type:
same_direction_reentry_rearmed
```

### VWAP MR

```text
event_type:
lower_vwap_band_reentry
```

```text
event_type:
upper_vwap_band_reentry
```

```text
event_type:
cross_vwap_structure_partial_exit
```

```text
event_type:
stale_mean_reversion_exit
```

### Portfolio

```text
event_type:
strategy_group_return_aggregation
```

```text
event_type:
joint_drawdown_started
```

---

## 70) Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Overnight order/session replay | máxima carga de state y intrabar |
| 2 | VWAP MR cost/partial replay | expectativa extremadamente pequeña |
| 3 | Long-only overnight OOS | única rama con señal básica favorable |
| 4 | Portfolio matched complementarity | separar símbolo y estilo |
| 5 | `My_Count` reconciliation | bloquea reproducción exacta |

---

## 71) Gates propuestos

### SCC-030-A — Session Contract

Debe resolver:

```text
18:00;
09:30;
first tradable bar;
16:00/17:00 exit;
DST;
holidays.
```

### SCC-030-B — Range Freeze

Debe certificar que no hay retrofill.

### SCC-030-C — Rearming State

Debe reproducir reentries.

### SCC-030-D — Intrabar Arbitration

Debe resolver entry/target/stop/reversal.

### SCC-030-E — Exit Attribution

Debe publicar razones de salida.

### SCC-030-F — Physical Futures

Debe eliminar el continuo de ejecución.

### SCC-030-G — Long/Short OOS

Debe validar por separado.

### SCC-031-A — VWAP Formula

Debe resolver precio y volumen.

### SCC-031-B — Band Formula

Debe resolver sigma e inclusión.

### SCC-031-C — Partial Exit

Debe resolver cantidades y prioridades.

### SCC-031-D — Max Hold

Debe reconciliar las 63 barras.

### SCC-031-E — Hidden Input

Debe resolver `My_Count`.

### SCC-031-F — Cost Survival

Debe superar quotes y slippage.

### SCC-031-G — Postpublication OOS

Inputs congelados.

### SCC-PF-001-A — Period Matching

Mismos start/end dates.

### SCC-PF-001-B — Trade Reconciliation

Debe explicar los cuatro trades y $2,211.09.

### SCC-PF-001-C — Style vs Symbol

Diseño factorial.

### SCC-PF-001-D — Risk Matching

Capital y volatilidad comparables.

### SCC-PF-001-E — Diversification Evidence

Correlation, marginal risk y joint drawdown.

---

# Conclusión

El Issue 15 contiene dos estrategias nuevas, un experimento de portfolio y una reimpresión del Utility Kit.

## Overnight-Futures-Range Breakout

La estrategia:

```text
construye rango 18:00–09:30
→ congela ONHigh/ONLow
→ coloca stops de breakout
→ exige reset para reentrada
→ permite reversals
→ ofrece exits Percent/ATR/Dollar
→ liquida al terminar el día
```

Los tres modelos de salida producen:

```text
$12.5k–$13.7k
PF 1.21–1.22
327–417 trades
```

pero toleran sólo unos 2.6–3.1 ticks de coste adicional por trade antes de desaparecer.

La disección muestra:

```text
long-only:
PF 1.56
61.54%

short-only:
PF 0.99
net negativo
```

El candidato defendible es la señal long, no la simetría completa.

## VWAP Bands MR

La estrategia:

```text
espera sobreextensión
→ entra al cruzar de regreso
→ atraviesa VWAP
→ partial/final exits al lado opuesto
→ stale exit a 60 barras
→ EOD exit
```

Publica:

```text
2,021 trades
$6,929.20
PF 1.15
68.48% ganadoras
```

pero:

```text
sólo gana $3.43 por trade;
tolera ~3.48 centavos/acción RT adicionales;
el win rate está sólo ~3 puntos sobre breakeven;
hay partial-exit ambiguity;
seis overnights;
un hidden My_Count;
el grid publicado no está conservado.
```

## Portfolio TF + MR

Publica:

```text
$26,203.63
sobre $60,000
Sharpe 0.3263
drawdown mostrado ~3.5%
```

pero:

```text
mezcla AAPL y SPY;
mezcla estilo y símbolo;
los periodos no coinciden;
faltan cuatro trades;
el neto es $2,211.09 inferior
a la suma de los charts;
las bases de drawdown no están certificadas como idénticas.
```

Es una buena hipótesis de diversificación, no una demostración causal.

## Utility Kit

Es una reimpresión sin `.ELD` en el ZIP.

## Estado final

```text
ISSUE_15_STATUS:
DOCUMENTALLY_CLOSED

PACKAGE_INSPECTION:
COMPLETE_WITH_PROPRIETARY_CODE_LIMITATION

NEW_STRATEGIES_EXTRACTED:
2

PORTFOLIO_EXPERIMENTS:
1

UTILITY_KIT_REPRINTS:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguientes gates recomendados:

```text
1. SCC-030-SESSION-ORDER-EXIT-ATTRIBUTION-AND-OOS-GATE
2. SCC-031-VWAP-MR-FORMULA-PARTIAL-COST-AND-OOS-GATE
3. SCC-PF-001-MATCHED-COMPLEMENTARITY-GATE
```
