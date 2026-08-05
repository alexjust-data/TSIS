# Auditoría completa — TradeStation Strategy Concepts Club, Issue 13 (enero de 2016)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. VWAP Bands Strategy
2. Regression Angles Strategy
3. Strategy Concepts Club Utility Kit 1
4. ideas secundarias de investigación y backtesting presentes en el número
5. reconstrucción matemática, temporal y de estado
6. auditoría de los resultados publicados
7. inspección forense de los archivos .ELD y workspaces .tsw
8. análisis del OptimizationData embebido en el workspace VWAP
9. contratos de implementación y réplica para TSIS
10. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia ni por el Utility Kit.

### Fuentes examinadas

- PDF completo de 21 páginas: `SCC Issue 13 Jan 2016.pdf`.
- Archivo de apoyo: `2016-01.zip`.
- PDF de la revista incluido dentro del ZIP.
- PDF auxiliar `Strategy Concepts Club Inventory.pdf`.
- Tres contenedores propietarios `.ELD`:
  - `TSL VWAP BANDS.ELD`;
  - `TSL REGRESSION ANGLES.ELD`;
  - `UTILITY KIT 1.ELD`.
- Dos workspaces OLE/Compound Document:
  - `TSL VWAP Bands.tsw`;
  - `TSL.Regression Angles.tsw`.
- Todas las páginas del PDF renderizadas e inspeccionadas visualmente, incluidas:
  - construcción y reset intradía de VWAP y sus bandas;
  - reglas, informe completo de rendimiento, curva de capital y superficies de sensibilidad;
  - construcción de la regresión, umbrales angulares, informe y curva de capital;
  - documentación completa de los cinco elementos del Utility Kit.
- Streams internos de ambos workspaces:
  - `Contents`;
  - `AnalisysTechniques`;
  - `ChartSetting`;
  - `DrawingObjects`;
  - `optdatafile`;
  - `OptimizationData`, cuando existe.

### Regla de evidencia

Se distinguen tres capas:

```text
SOURCE:
lo que afirma, define o muestra la revista

PACKAGE:
lo que confirman el PDF, los workspaces,
los streams OLE y los contenedores .ELD

AUDIT:
inferencia técnica, crítica científica
y propuesta de implementación en TSIS
```

Cuando una decisión no queda resuelta por la revista o el paquete, se registra como ambigüedad. No se completa silenciosamente.

Las fórmulas no publicadas literalmente se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

No se ha utilizado investigación web externa para rellenar reglas o fórmulas ausentes.

---

## 0.1 Integridad del paquete

El PDF cargado por separado y el PDF incluido dentro del ZIP son binariamente idénticos.

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `2016-01.zip` | 8,968,116 bytes | `324898e9d0f1e1e61df925827a0814ca119bc790e22a7fc98f5e3ed3be408ad4` |
| `SCC Issue 13 Jan 2016.pdf` | 8,685,620 bytes | `b86c5455650f17499dedab577cb321d041d026763be5f602cc5dc9ff16ab45a0` |
| `Strategy Concepts Club Inventory.pdf` | 14,050 bytes | `38d2e65206a1481a56149aadf539640c714bfe5dd5f4485e2538fe7c3a11e8a0` |
| `TSL VWAP BANDS.ELD` | 20,442 bytes | `4d88cd95e401684a6bfd439cdec2da4a3b9f3c569464015b2afd24a87c3e6f79` |
| `TSL VWAP Bands.tsw` | 2,686,976 bytes | `f2f5052d9e4b59c69588c9d666f4a59008368dcba73d9cfa76f13c5b347e5077` |
| `TSL REGRESSION ANGLES.ELD` | 17,374 bytes | `9063333d90bc4a1f40bd2bc6ac4bedd7c9f20e75d3d4faac9da2b7d575c17b49` |
| `TSL.Regression Angles.tsw` | 21,504 bytes | `be3cb8b2a691a2f5ce00efc2bd772a443c213ee3fd545d51eaa3bbda69122362` |
| `UTILITY KIT 1.ELD` | 21,980 bytes | `b74343395a1b2994a013826844a3036d210842cae88e6c7ff08e0974040728d4` |

Los pequeños streams `Zone.Identifier` son metadatos del sistema de archivos y no forman parte del contenido científico.

`Strategy Concepts Club Inventory.pdf` es un índice documental. No añade reglas, código ni resultados a las estrategias del número.

---

## 0.2 Limitación de los `.ELD`

Los `.ELD` son contenedores propietarios de TradeStation. El paquete permite importarlos en la plataforma, pero no expone el EasyLanguage como texto legible en este entorno.

Por tanto:

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la fórmula exacta del precio-barra usado en VWAP;
no puede certificarse la dispersión exacta de las bandas;
no puede certificarse la fórmula exacta del ángulo;
no puede resolverse por lectura directa:
    - sample vs population standard deviation;
    - inclusión de la barra actual;
    - semántica de Lowest/Highest;
    - prioridad de exits de fin de sesión;
    - significado independiente de los dos inputs de salida angular;
    - reglas exactas de reentrada o bloqueo.
```

---

## 0.3 Workspaces OLE

### VWAP Bands

Streams principales:

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 16,836 bytes |
| `Embedding 1/StatusLine` | 368 bytes |
| `Embedding 1/ChartSetting` | 666 bytes |
| `Embedding 1/DrawingObjects` | 92 bytes |
| `Embedding 1/AnalisysTechniques` | 283 bytes |
| `Embedding 1/optdatafile` | 0 bytes |
| `Embedding 1/OptimizationData` | **2,576,209 bytes** |

### Regression Angles

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 13,042 bytes |
| `Embedding 1/StatusLine` | 144 bytes |
| `Embedding 1/ChartSetting` | 666 bytes |
| `Embedding 1/DrawingObjects` | 571 bytes |
| `Embedding 1/AnalisysTechniques` | 311 bytes |
| `Embedding 1/optdatafile` | 0 bytes |

Regression Angles no conserva un grid ni un stream `OptimizationData`.

---

## 0.4 Evidencia del workspace VWAP Bands

El workspace confirma:

```text
Serie:
AAPL 5 min [NASDAQ]
Apple Inc.

Técnicas:
TSL:VWAP Bands Strategy
TSL:VWAP Bands Indicator

Inputs activos:
Signal_Band_Num = 2
Trail_Stop_Length = 22
```

Estos valores coinciden con el test publicado.

El indicador y la estrategia comparten la misma técnica nominal, pero cumplen funciones distintas:

```text
indicador:
visualización de VWAP, bandas y sombreado

estrategia:
cruces, entradas, salidas y liquidación de sesión
```

---

## 0.5 Hallazgo forense: `OptimizationData` de VWAP no corresponde al modelo publicado

Aunque el workspace contiene 2.58 MB de datos de optimización, el trailer del stream identifica seis inputs distintos:

```text
TSL:VWAP Bands: Enable_Trailingstop
TSL:VWAP Bands: Trail_Stop_Length
TSL:VWAP Bands: LERule
TSL:VWAP Bands: SERule
TSL:VWAP Bands: LXRule
TSL:VWAP Bands: SXRule
```

El espacio cartesiano almacenado es:

| Input interno | Valores |
|---|---|
| `Enable_Trailingstop` | 0, 1 |
| `Trail_Stop_Length` | 2, 5, 8 |
| `LERule` | 1, 2, 3, 4, 5 |
| `SERule` | 1, 2, 3, 4, 5 |
| `LXRule` | 1, 2, 3 |
| `SXRule` | 1, 2, 3 |

Número de candidatos:

\[
2 \times 3 \times 5 \times 5 \times 3 \times 3 = 1{,}350
\]

La estructura física contiene:

```text
bloque 1:
1,350 configuraciones

bloque 2:
duplicado exacto del bloque 1

bloque 3:
placeholders con net profit y trades a cero,
porcentajes sentinel y los mismos IDs de configuración
```

Por tanto:

```text
filas físicas de resultados = 4,050
configuraciones candidatas únicas = 1,350
experimentos completos distintos = 1,350
```

Dentro de cada bloque completo:

```text
1,242 configuraciones generaron trades;
108 configuraciones quedaron vacías;
ninguna configuración ejecutada fue rentable;
mejor net profit almacenado ≈ -$3,698.49;
peor net profit almacenado ≈ -$42,390.33.
```

El test publicado, en cambio, informa:

```text
Signal_Band_Num = 2
Trail_Stop_Length = 22
Net Profit = +$21,485.52
Trades = 2,282
```

Además, `Signal_Band_Num` ni siquiera aparece entre los seis inputs del stream antiguo.

Conclusión:

> `OptimizationData` pertenece a una versión anterior, experimental o internamente distinta de `TSL:VWAP Bands`. No puede utilizarse para rankear la configuración publicada ni para reconstruir la superficie `Signal_Band_Num × Trail_Stop_Length` mostrada en la revista.

Estado:

```text
OPTIMIZATION_DATA_PRESENT:
YES

CURRENT_MODEL_GRID_RECOVERABLE:
NO

STALE_OR_DIFFERENT_MODEL_EVIDENCE:
YES

DUPLICATE_RESULT_BLOCKS:
YES
```

Este hallazgo impide afirmar, a partir del paquete, cuántas combinaciones del modelo final se probaron o qué puesto ocupaba `2/22`.

---

## 0.6 Evidencia del workspace Regression Angles

El workspace confirma:

```text
Serie:
SPY 130 min [ARCX]
SPDR S&P 500 ETF

Técnicas:
TSL:Regression Angles Strategy
TSL:Regression Angles Indicator

Inputs activos de la estrategia:
LRLength = 10
LRAngleBuySignal = 2.25
LRAngleSellSignal = -2.25
ExitBarCount = 4
ExitBar_AnglesCounterTrend = 4

Inputs activos del indicador:
LRLength = 10
LRAngleBuyLevel = 2.25
LRAngleSellLevel = -2.25
DrawSignalLines = True
```

`optdatafile` está vacío y no existe `OptimizationData`.

El stream `DrawingObjects` contiene referencias gráficas residuales a `@GC=103NN`. No constituyen evidencia de que el test publicado opere oro; la serie activa y el informe son SPY.

---

## 0.7 Resultado ejecutivo del Issue 13

| ID | Estrategia | Tipo real | Resultado publicado | Hallazgo crítico | Decisión |
|---|---|---|---|---|---|
| 026 | VWAP Bands | Breakout/continuación intradía de una banda dinámica reiniciada por sesión | AAPL 5m; 2,282 trades; $21,485.52; PF 1.20 | sólo $9.42/trade; aproximadamente 2.94 centavos por acción round trip de margen adicional; fórmula y sesión no certificadas; optimización embebida es de otro modelo | excelente candidato de microestructura y session-state, no edge aceptado |
| 027 | Regression Angles | Crossover de ángulo de regresión de midpoints con salida por desaceleración angular | SPY 130m; 303 trades; $9,135; PF 1.45 | ángulo no normalizado depende del precio y timeframe; ambigüedad de exit inputs queda oculta porque ambos valen 4; no hay stop | candidato de réplica y normalización, no estrategia validada |
| UK-001 | Utility Kit 1 | Herramientas de control, calendario, reporting y metadatos | no aplica | varias utilidades son peligrosas si se usan fuera de backtest; deben transformarse en contratos del engine | admitir como referencia arquitectónica, no como edge |

Estado del número:

```text
ISSUE_13_STATUS:
DOCUMENTALLY_CLOSED

NEW_STRATEGIES:
2

UTILITY_KITS:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

---

# Parte I — Estrategia 026: VWAP Bands

## 1) Identificación

- **ID:** `SCC-2016-01-STRAT-026`
- **Artículo:** *VWAP Bands Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas del PDF:** 5–9
- **Estilo declarado:** trend-following
- **Mercado declarado:** equities
- **Horizonte:** day trading
- **Activo del test:** Apple Inc.
- **Símbolo:** `AAPL`
- **Bar interval:** 5 minutos
- **Historia:** seis años terminando el 30 de noviembre de 2015
- **Capital inicial:** $30,000
- **Tamaño:** $20,000 por trade, redondeado hacia abajo a una acción
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **Inputs activos:** `Signal_Band_Num=2`, `Trail_Stop_Length=22`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, con barras intradía, volumen, calendario y corporate actions. |
| ¿Puede replicarse exactamente con OHLCV 5m? | **No todavía.** Falta certificar precio proxy, dispersión y semántica de exits. |
| ¿Es VWAP verdadero de ticks? | **No.** Es una estimación basada en precios y volumen agregados por barra. |
| ¿La banda es fija durante la barra? | **No necesariamente.** La barra actual contribuye al VWAP y posiblemente a la desviación antes de evaluar el cierre. |
| ¿Es una estrategia mean-reversion? | **No.** Compra por encima de la banda y vende por debajo: continuación. |
| ¿El resultado tiene mucho margen por trade? | **No.** $9.42 de expectativa media. |
| ¿Los datos de optimización permiten verificar el grid final? | **No.** Corresponden a otro modelo interno. |
| ¿Está lista para operar? | **No.** Falta OOS, quotes, slippage y reconciliación de sesión. |
| ¿Merece implementación? | **Sí**, con prioridad alta para Price Location Intraday y session-state. |

Clasificación:

```text
INTRADAY_VWAP_STATE
DYNAMIC_BAND_BREAKOUT
SESSION_RESET_STRATEGY
EXECUTION_COST_SENSITIVE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2) Qué estrategia es realmente

La lógica es:

```text
inicio de regular session
→ reset de acumuladores
→ estimación acumulativa de VWAP
→ estimación acumulativa de dispersión
→ bandas ±k desviaciones
→ cruce del cierre sobre la banda superior:
      long en la apertura de la barra siguiente
→ cruce del cierre bajo la banda inferior:
      short en la apertura de la barra siguiente
→ salida por extremo de 22 barras
→ liquidación antes del final de la sesión
```

No compra precios “baratos” por debajo del VWAP.

Hace exactamente lo contrario:

```text
ruptura superior:
continuación alcista

ruptura inferior:
continuación bajista
```

El VWAP actúa como referencia intradía y las bandas como frontera dinámica de movimiento significativo.

---

## 3) VWAP estimado

Sea `s(t)` la primera barra de la regular session y `P_i` un precio representativo de la barra.

Reconstrucción general:

\[
\widehat{VWAP}_t
=
\frac{
\sum_{i=s(t)}^t P_i V_i
}{
\sum_{i=s(t)}^t V_i
}
\]

La revista advierte que es una estimación porque el VWAP verdadero requeriría:

```text
todos los trades;
precio de cada trade;
volumen de cada trade.
```

Con barras de 5 minutos se pierde la distribución intrabar.

### Ambigüedad no resuelta: `P_i`

El artículo habla de “average prices of the day’s bars”, pero no especifica inequívocamente si utiliza:

```text
(H + L + C) / 3
(O + H + L + C) / 4
(H + L) / 2
Close
AverageFC u otra función TradeStation
```

Cambiar el precio proxy altera VWAP, bandas y cruces.

Estado:

```text
BAR_PRICE_PROXY_UNRESOLVED
```

---

## 4) Dispersión y bandas

La revista indica que cada banda se encuentra a un número de desviaciones estándar de los precios medios de las barras del día respecto del VWAP.

Reconstrucción funcional:

\[
\sigma_t
=
SD\left(P_{s(t)},\dots,P_t\right)
\]

\[
Upper_{k,t}
=
VWAP_t + k\sigma_t
\]

\[
Lower_{k,t}
=
VWAP_t - k\sigma_t
\]

Con el test:

\[
k = 2
\]

### Ambigüedades

No puede certificarse:

```text
sample vs population SD;
dispersión ponderada o no por volumen;
desviación alrededor de VWAP o alrededor de la media simple;
inclusión de la barra actual;
tratamiento de volumen cero;
inicialización exacta;
redondeo a tick.
```

Una alternativa ponderada sería:

\[
\sigma_{w,t}
=
\sqrt{
\frac{\sum V_i(P_i-VWAP_t)^2}
{\sum V_i}
}
\]

No debe asumirse sin reconciliación.

---

## 5) Auto-inclusión y banda móvil

Al cierre de una barra `t`, esa misma barra aporta:

```text
precio;
volumen;
posiblemente dispersión.
```

La banda que el cierre intenta cruzar puede haberse desplazado por la propia barra.

Por tanto, existen dos variantes distintas:

```text
INCLUSIVE_DYNAMIC_BAND:
Close_t se compara con VWAP_t y Band_t

LAGGED_FROZEN_BAND:
Close_t se compara con VWAP_t-1 y Band_t-1
```

La publicación parece compatible con la primera, pero el código no es visible.

Ambas son causales al cierre. No son el mismo evento estadístico.

---

## 6) Warm-up intradía

No se permiten señales en las dos primeras barras.

Con barras de 5 minutos:

```text
barra 1:
reset y primera observación

barra 2:
segunda observación

barra 3:
primera barra potencialmente señalable
```

Si la sesión regular comienza a las 09:30 ET, la primera decisión posible dependerá de la convención de timestamp de barra:

```text
cierre aproximado de 09:45
o equivalente según la plataforma.
```

Debe congelarse la semántica de inicio y fin.

---

## 7) Entradas

### Long

\[
Close_{t-1} \le Upper_{2,t-1}
\quad\land\quad
Close_t > Upper_{2,t}
\]

Entonces:

```text
buy at open t+1
```

### Short

\[
Close_{t-1} \ge Lower_{2,t-1}
\quad\land\quad
Close_t < Lower_{2,t}
\]

Entonces:

```text
sell short at open t+1
```

### Reentradas

La revista permite “different positions” durante el mismo día.

Debe reconciliarse:

```text
si sólo entra estando flat;
si una señal opuesta revierte;
si un nuevo cruce del mismo lado permite reentrada;
si el reset de cross requiere regresar dentro de la banda.
```

La reconstrucción conservadora es una sola posición simultánea y entrada sólo desde flat.

---

## 8) Salida de 22 barras

La publicación dice:

```text
long:
salir cuando Low está por debajo del lowest low de las últimas 22 barras

short:
salir cuando High está por encima del highest high de las últimas 22 barras
```

Si la barra actual se incluye:

\[
Low_t < Lowest(Low,22)_t
\]

es imposible.

La reconstrucción probable es:

\[
LongExit_t =
Low_t <
\min(Low_{t-1},\dots,Low_{t-22})
\]

\[
ShortExit_t =
High_t >
\max(High_{t-1},\dots,High_{t-22})
\]

y ejecución:

```text
open t+1
```

`22 × 5 = 110` minutos.

No es un trailing stop monetario convencional; es un nuevo extremo adverso respecto de una ventana intradía.

---

## 9) Liquidación de fin de día

La estrategia sale:

```text
en la apertura de la última barra
de la regular trading session
```

Esto significa que, en una sesión normal de barras de 5 minutos, no participa en la última barra completa.

No es equivalente a:

```text
market-on-close;
salida al cierre de la última barra;
salida a las 16:00 exactas.
```

### Excepción overnight

La revista registra:

```text
9 de 2,282 trades
≈ 0.4%
```

transportados overnight, principalmente por:

```text
early closes;
holidays;
trade halts;
imposibilidad de activar la salida esperada.
```

En esos casos la salida se produce en la primera barra del día siguiente.

Esto demuestra que el “no overnight” no es una intención suficiente; necesita una política operativa de excepción.

Estado TSIS:

```text
EXPECTED_EOD_EXIT
EOD_EXIT_MISSED
OVERNIGHT_EXCEPTION
NEXT_SESSION_FORCED_EXIT
```

---

## 10) Session contract

Debe congelarse:

```text
timezone = America/New_York
regular session = 09:30–16:00
bar interval = 5m
bar label convention
half-day calendar
holiday calendar
halts
missing bars
first-bar identification
last-bar identification
```

El VWAP, la desviación y la liquidación dependen del mismo session contract.

Un cambio de sesión altera todo el modelo.

---

## 11) Corporate actions

AAPL atravesó splits durante la historia.

La réplica debe mantener coherencia entre:

```text
precio;
volumen;
VWAP;
bandas;
sizing;
ejecución.
```

Un split requiere transformar inversamente precio y volumen.

No debe calcularse:

```text
VWAP con precio ajustado
y volumen raw
```

ni tamaño con una vista y PnL con otra sin un mapping explícito.

Vistas propuestas:

```text
signal_price_volume_view:
split-consistent intraday OHLCV

execution_view:
raw tradable prices and quantities

corporate_action_mapping:
point-in-time adjustment factors
```

---

## 12) Sizing

Capital aproximado por operación:

\[
N = \$20{,}000
\]

Cantidad funcional:

\[
Qty_t
=
\left\lfloor
\frac{20{,}000}{ReferencePrice_t}
\right\rfloor
\]

El precio de referencia exacto no queda documentado:

```text
cierre de la barra de señal;
apertura siguiente;
precio de fill;
propiedad interna de TradeStation.
```

La diferencia importa cuando hay gaps.

---

## 13) Resultados publicados

### 13.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $21,485.52 |
| Beneficio bruto | $130,594.12 |
| Pérdida bruta | -$109,108.60 |
| Profit Factor | 1.20 |
| Operaciones | 2,282 |
| Ganadoras | 1,009 |
| Perdedoras | 1,273 |
| Percent Profitable | 44.22% |
| Expectativa media | $9.42 |
| Ganancia media | $129.43 |
| Pérdida media | -$85.71 |
| Ratio ganancia/pérdida | 1.51 |
| Mayor ganancia | $750.08 |
| Mayor pérdida | -$734.31 |
| Máx. ganadoras consecutivas | 7 |
| Máx. perdedoras consecutivas | 12 |
| Barras medias ganadoras | 44.40 |
| Barras medias perdedoras | 24.02 |
| Máximo tamaño | 739 acciones |
| Acciones acumuladas | 730,419 |
| Return on Initial Capital | 71.62% |
| Annual Rate of Return | 9.01% |
| Return Retracement Ratio | 0.30 |
| RINA Index | 1,028.65 |
| Percent of Time in Market | 12.60% |
| Drawdown semanal aproximado | 6% |

### 13.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $15,303.76 | $6,181.76 |
| Profit Factor | 1.32 | 1.10 |
| Operaciones | 1,078 | 1,204 |
| Percent Profitable | 46.85% | 41.86% |
| Expectativa media | $14.20 | $5.13 |
| Ganancia media | $125.25 | $132.62 |
| Pérdida media | -$84.56 | -$86.65 |
| Ratio ganancia/pérdida | 1.49 | 1.53 |
| Mayor ganancia | $750.08 | $725.92 |
| Mayor pérdida | -$734.31 | -$548.49 |
| Máx. ganadoras consecutivas | 9 | 9 |
| Máx. perdedoras consecutivas | 8 | 10 |
| Barras medias ganadoras | 44.59 | 44.21 |
| Barras medias perdedoras | 23.79 | 24.21 |
| Acciones acumuladas | 345,706 | 384,713 |

### 13.3 Contribución direccional

\[
15{,}303.76 / 21{,}485.52
\approx 71.23\%
\]

El 71.23% del neto procede de longs.

La rama short aporta:

```text
28.77% del neto;
PF 1.10;
$5.13 por trade.
```

Debe validarse separadamente.

---

## 14) Fragilidad frente a costes

Cantidad media aproximada:

\[
730{,}419 / 2{,}282
\approx 320.08 \text{ acciones}
\]

Margen de coste adicional:

\[
9.42 / 320.08
\approx \$0.0294
\]

Es decir:

```text
≈ 2.94 centavos por acción round trip
≈ 1.47 centavos por acción y lado
```

eliminarían la expectativa agregada publicada.

La comisión modelada ya está incluida, pero no se publica:

```text
spread;
slippage;
latencia;
market impact;
partial fills;
short locate;
adverse selection en el breakout;
open-price uncertainty.
```

Para una estrategia con 2,282 operaciones y PF 1.20, la ejecución es parte del edge.

---

## 15) Duración

Ganadores:

\[
44.40 \times 5
=
222 \text{ minutos}
\]

Perdedores:

\[
24.02 \times 5
\approx 120 \text{ minutos}
\]

Los ganadores duran aproximadamente 1.85 veces más.

Esto es compatible con trend following, pero la liquidación EOD trunca la cola de holding periods.

---

## 16) Curva de capital

La curva es ascendente, pero presenta:

```text
periodos de meseta;
retrocesos intermedios;
aceleración 2012–2013;
degradación o drawdown en 2014;
recuperación al final.
```

La forma no demuestra estabilidad en distintos activos ni después de 2015.

El RINA elevado está parcialmente impulsado por sólo 12.60% de exposición temporal y no corrige el selection bias.

---

## 17) Sensibilidad

La revista muestra una superficie:

```text
Trail_Stop_Length × Signal_Band_Num
```

y describe una “rounded mount”.

Los defaults:

```text
22
2
```

están en una zona relativamente plana, no en el máximo.

La figura de equity curves muestra que valores de banda superiores a 2 terminan con más beneficio absoluto, pero peores métricas ajustadas por riesgo.

Esto sugiere un trade-off:

```text
bandas más lejanas:
menos señales;
movimientos más extremos;
mayor PnL acumulado en la muestra;
peor perfil de riesgo o concentración.
```

Sin el grid final no puede comprobarse:

```text
número de configuraciones;
ranking;
estabilidad cuantitativa;
criterio exacto de elección;
multiple testing.
```

---

## 18) ¿Dónde podría estar el edge?

Hipótesis:

> Una ruptura suficientemente alejada del VWAP intradía identifica flujo direccional persistente, y la continuación supera al coste de entrar tarde.

Mecanismos posibles:

```text
órdenes institucionales persistentes;
information flow;
momentum intradía;
ruptura de liquidez;
day trend;
participación creciente;
desplazamiento del fair-value intradía.
```

Hipótesis alternativas:

```text
tendencia alcista secular de AAPL;
corporate-action treatment;
sesgo de sesión;
breakouts de precio sin información incremental del volumen;
parámetros seleccionados;
fills optimistas;
resultado sostenido por periodos concretos.
```

---

## 19) Auditoría científica

### 19.1 Un único activo

No hay panel de equities.

### 19.2 Seis años no equivalen a OOS

La selección y el informe usan la misma historia.

### 19.3 Parámetros optimizados

El artículo lo reconoce.

### 19.4 Grid final no recuperable

El stream embebido pertenece a otro modelo.

### 19.5 PF bajo

`1.20` deja poco margen a errores.

### 19.6 Costes incompletos

Crítico a 2.94 centavos por acción RT.

### 19.7 VWAP estimado

Puede diferir del tick VWAP.

### 19.8 Bandas no certificadas

La fórmula de sigma es desconocida.

### 19.9 Self-inclusion

Puede amortiguar o desplazar cruces.

### 19.10 Session dependence

La estrategia desaparece fuera de su construcción de sesión.

### 19.11 Early-close leakage operacional

El EOD exit no cubre todos los calendarios.

### 19.12 Corporate actions

Precio y volumen deben ajustarse conjuntamente.

### 19.13 Short side débil

PF 1.10 y $5.13 por trade.

### 19.14 Sin dollar stop

La mayor pérdida se aproxima a la mayor ganancia y puede ampliarse fuera de muestra.

### 19.15 Sizing variable

Mezcla calidad de señal con nivel histórico de precio.

---

## 20) Contrato TSIS

### Datos

```text
AAPL 5m raw OHLCV
AAPL trades and quotes for validation
corporate actions
regular-session calendar
halts
early closes
```

### Estado acumulativo

```text
session_id
bar_index_in_session
is_regular_session
is_first_bar
is_last_expected_bar
cum_volume
cum_price_volume
vwap
price_proxy
dispersion
upper_band_1
upper_band_signal
upper_band_3
lower_band_1
lower_band_signal
lower_band_3
signal_band_num
warmup_complete
position
trail_stop_length
```

### Eventos

```text
VWAP_SESSION_RESET
VWAP_WARMUP_COMPLETE
VWAP_UPPER_BAND_CROSS
VWAP_LOWER_BAND_CROSS
PRIOR_WINDOW_LOW_BREAK
PRIOR_WINDOW_HIGH_BREAK
EOD_EXIT_DUE
EOD_EXIT_MISSED
OVERNIGHT_EXCEPTION
NEXT_SESSION_FORCED_EXIT
```

### Estados de indisponibilidad

```text
MISSING_VOLUME
BAR_PRICE_PROXY_UNRESOLVED
DISPERSION_FORMULA_UNRESOLVED
SESSION_TEMPLATE_UNRESOLVED
CORPORATE_ACTION_UNRESOLVED
MISSING_NEXT_BAR_OPEN
EXIT_SELF_INCLUSION_UNRESOLVED
EOD_BAR_NOT_FOUND
```

---

## 21) Pseudocódigo funcional

```python
on_regular_session_start:
    cum_volume = 0.0
    cum_price_volume = 0.0
    session_prices = []
    position = 0

for each completed 5m bar t:

    p = selected_bar_price_proxy(t)
    v = volume[t]

    cum_volume += v
    cum_price_volume += p * v
    session_prices.append(p)

    vwap = cum_price_volume / cum_volume
    sigma = selected_session_dispersion(session_prices, vwap)

    upper = vwap + 2.0 * sigma
    lower = vwap - 2.0 * sigma

    if bar_index_in_session >= 3 and flat:
        if close[t - 1] <= upper_prev and close[t] > upper:
            schedule_long(next_bar_open)
        elif close[t - 1] >= lower_prev and close[t] < lower:
            schedule_short(next_bar_open)

    if long:
        prior_low = min(low[t - 22:t])
        if low[t] < prior_low:
            schedule_exit(next_bar_open)

    if short:
        prior_high = max(high[t - 22:t])
        if high[t] > prior_high:
            schedule_exit(next_bar_open)

    if next_bar_is_last_regular_bar:
        schedule_exit(open_of_last_regular_bar)
```

Es una reconstrucción, no una transcripción del `.ELD`.

---

## 22) Plan de réplica y falsificación

### Fase 1 — Checksum histórico

```text
2,282 trades
1,078 long
1,204 short
net ≈ $21,485.52
PF ≈ 1.20
time in market ≈ 12.60%
9 overnight exceptions
```

### Fase 2 — Fórmula VWAP

Comparar:

```text
typical price;
OHLC4;
midpoint;
close;
tick VWAP.
```

### Fase 3 — Dispersión

```text
unweighted sample SD;
unweighted population SD;
volume-weighted SD;
inclusive;
lagged.
```

### Fase 4 — Session replay

```text
full regular sessions;
half-days;
halts;
missing final bars;
DST;
EOD exit.
```

### Fase 5 — Quotes y costes

```text
bid/ask;
next-open fill;
1, 2, 3, 5 centavos por acción RT adicionales;
partial fills;
short locate.
```

### Fase 6 — Ablaciones

| Variante | Pregunta |
|---|---|
| simple intraday mean bands | ¿el volumen añade información? |
| VWAP sin bandas | ¿las desviaciones son necesarias? |
| lagged bands | ¿la auto-inclusión importa? |
| long-only | ¿short añade valor? |
| fixed time exit | ¿el extreme exit aporta valor? |
| mean-reversion a 3 sigma | nueva hipótesis, no mejora automática |
| ATR-adaptive k | nueva hipótesis separada |

### Fase 7 — Cross-sectional

Parámetros congelados primero en:

```text
MSFT
NVDA
AMZN
META cuando exista
QQQ
SPY
```

### Fase 8 — Postpublicación

Desde enero de 2016 en adelante, sin modificar `2/22`.

### Fase 9 — Comparación de sizing

```text
fixed shares;
constant notional;
volatility targeting;
equal risk.
```

---

## 23) Eventos para Market State y Event State

### Market State

```text
price_to_vwap
price_to_vwap_in_sigma
vwap_slope
band_width
band_width_percentile
cumulative_volume_pace
session_progress
```

### Event State

```text
event_type:
intraday_vwap_upper_band_cross

decision_timestamp:
5m bar close

attributes:
signal_band_num
vwap
sigma
overshoot
session_bar_index
volume_pace
distance_to_session_high
```

y su espejo inferior.

Outcomes:

```text
next-bar fill
MFE
MAE
time_to_22-bar-exit
EOD result
overnight exception
return after costs
```

---

## 24) Decisión — VWAP Bands

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
Price Location Intraday
+
session-reset state
+
dynamic reference bands
+
execution-cost research

PRIORIDAD:
alta

SIGUIENTE GATE:
SCC-026-VWAP-FORMULA-SESSION-COST-AND-OOS-GATE
```

---

# Parte II — Estrategia 027: Regression Angles

## 25) Identificación

- **ID:** `SCC-2016-01-STRAT-027`
- **Artículo:** *Regression Angles Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas:** 11–15
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** swing trading
- **Activo:** SPY
- **Intervalo:** 130 minutos
- **Historia:** cinco años terminando el 30 de noviembre de 2015
- **Tamaño:** 100 acciones
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **Inputs activos:** `10 / 2.25 / -2.25 / 4 / 4`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse? | **Sí.** |
| ¿Puede replicarse exactamente? | **No todavía.** Falta certificar fórmula angular y semántica de los dos inputs de salida. |
| ¿Es una regresión point-in-time? | **Sí**, si sólo usa las últimas 10 barras cerradas. |
| ¿El ángulo es comparable entre activos y épocas? | **No necesariamente.** Depende de unidades de precio y timeframe. |
| ¿La muestra long/short está equilibrada? | **Bastante.** 161 longs y 142 shorts. |
| ¿Tiene stop de emergencia? | **No.** |
| ¿Tiene reentrada en la misma tendencia? | **No mientras no se produzca un nuevo crossover del threshold.** |
| ¿El artículo demuestra edge? | **No.** Optimización limitada, un activo y sin OOS. |
| ¿Merece implementación? | **Sí**, especialmente para estudiar normalización de pendiente. |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
ROLLING_LINEAR_REGRESSION_TREND
ANGLE_THRESHOLD_CROSS
COUNTERTREND_ANGLE_EXIT
PRICE_SCALE_DEPENDENT
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 26) Precio de entrada a la regresión

La estrategia usa el midpoint de cada barra:

\[
M_t =
\frac{High_t + Low_t}{2}
\]

Con `LRLength = 10`, en cada barra `t` ajusta una recta por mínimos cuadrados sobre:

\[
M_{t-9},\dots,M_t
\]

La barra actual está incluida.

---

## 27) Regresión lineal

Sea:

\[
x_j = j,\quad j=0,\dots,9
\]

y:

\[
y_j = M_{t-9+j}
\]

Pendiente:

\[
\beta_t
=
\frac{
\sum_j (x_j-\bar x)(y_j-\bar y)
}{
\sum_j (x_j-\bar x)^2
}
\]

Intercepto:

\[
\alpha_t = \bar y - \beta_t\bar x
\]

Recta:

\[
\widehat y_j = \alpha_t + \beta_t x_j
\]

La publicación indica que usa la función multi-output `LinearReg` de TradeStation.

---

## 28) Ángulo probable

La reconstrucción matemática más probable es:

\[
Angle_t =
\arctan(\beta_t)
\frac{180}{\pi}
\]

La figura muestra un ejemplo de 6.4 grados, compatible con un arctangente de una pendiente expresada en unidades de precio por barra.

Sin embargo, no puede certificarse desde el `.ELD`:

```text
grados vs otra unidad;
slope exacta devuelta por LinearReg;
convención de eje x;
redondeo;
transformación interna;
price scale;
uso del endpoint o de la slope.
```

Estado:

```text
ANGLE_FORMULA_UNRESOLVED
```

---

## 29) Problema crítico: el ángulo no está normalizado

Si:

\[
\beta_t
\]

se mide en dólares por barra, el mismo retorno porcentual genera una pendiente mayor cuando el precio es mayor.

El threshold:

\[
2.25^\circ
\]

equivale aproximadamente a:

\[
\tan(2.25^\circ)
\approx 0.03929
\]

unidades de precio por barra.

En SPY a $100:

\[
0.03929 / 100
\approx 3.93 \text{ puntos básicos por barra}
\]

En SPY a $200:

\[
0.03929 / 200
\approx 1.96 \text{ puntos básicos por barra}
\]

Por tanto:

> A medida que el precio de SPY aumenta, el mismo threshold angular exige una pendiente porcentual cada vez menor.

Esto introduce una no estacionariedad oculta.

Además, el ángulo cambia con:

```text
splits;
moneda;
multiplicador de precio;
bar interval;
instrumento;
volatilidad;
escala nominal.
```

Una configuración `±2.25` no es portable directamente a futures, forex u otras acciones.

---

## 30) Alternativas normalizadas para falsificación

No deben sustituir silenciosamente la regla original, pero sí compararse.

### Log-price regression

\[
y_t = \ln(M_t)
\]

La slope se aproxima a retorno por barra.

### Price-normalized slope

\[
\beta_t / M_t
\]

### ATR-normalized slope

\[
\beta_t / ATR_t
\]

### Volatility-normalized t-statistic

\[
\frac{\beta_t}{SE(\beta_t)}
\]

### R-squared conditioned slope

Separar:

```text
dirección;
magnitud;
calidad del ajuste.
```

La estrategia original sólo utiliza dirección y magnitud nominal.

---

## 31) Escala temporal

SPY regular session tiene 390 minutos.

Con barras de 130 minutos:

```text
3 barras por sesión
```

La regresión de 10 barras cubre aproximadamente:

\[
10 \times 130 / 390
\approx 3.33 \text{ sesiones}
\]

Aunque el artículo la denomina swing trading, su definición de tendencia es de muy corto horizonte.

---

## 32) Entradas

### Long

\[
Angle_{t-1} \le 2.25
\quad\land\quad
Angle_t > 2.25
\]

Entrada:

```text
buy at open t+1
```

### Short

\[
Angle_{t-1} \ge -2.25
\quad\land\quad
Angle_t < -2.25
\]

Entrada:

```text
sell short at open t+1
```

### Neutral zone

```text
-2.25 ≤ Angle ≤ 2.25
```

La zona intenta reducir whipsaws.

No es un filtro posterior; define cuándo debe producirse un nuevo crossover.

---

## 33) Exit por deterioro angular

La explicación conceptual correcta del ejemplo es:

```text
ExitBarCount = N:
ventana de comparaciones observadas

ExitBar_AnglesCounterTrend = K:
número mínimo de comparaciones contra tendencia
```

Para long:

\[
I_j =
1\{Angle_{t-j} < Angle_{t-j-1}\}
\]

Salir si:

\[
\sum_{j=0}^{N-1} I_j \ge K
\]

Para short:

\[
J_j =
1\{Angle_{t-j} > Angle_{t-j-1}\}
\]

Salir si:

\[
\sum_{j=0}^{N-1} J_j \ge K
\]

### Ambigüedad editorial crítica

El artículo ofrece un ejemplo:

```text
ExitBarCount = 5
ExitBar_AnglesCounterTrend = 3

→ salir si 3 de las últimas 5 comparaciones
muestran deterioro.
```

Pero la redacción posterior de las reglas intercambia los nombres:

```text
“grupo de ExitBar_AnglesCounterTrend barras”
y
“si ExitBarCount barras...”
```

En el test ambos valores son `4`.

En los defaults ambos son `3`.

Por tanto, la igualdad de los inputs oculta la ambigüedad y el resultado publicado no permite descubrir cuál controla:

```text
la longitud de ventana;
el número requerido.
```

Estado:

```text
EXIT_INPUT_ROLE_AMBIGUITY
```

Debe resolverse antes de utilizar valores distintos.

---

## 34) Con `4/4`, qué exige el test

La configuración publicada requiere, probablemente:

```text
long:
4 descensos consecutivos del ángulo

short:
4 ascensos consecutivos del ángulo
```

No exige que el ángulo cruce cero ni el threshold contrario.

La salida detecta desaceleración de la tendencia antes de una reversión completa.

---

## 35) Falta de reentrada

Supongamos:

```text
Angle cruza +2.25;
se abre long;
cuatro deterioros provocan salida;
Angle sigue por encima de +2.25;
la tendencia se reanuda.
```

No hay un nuevo crossover desde debajo de +2.25.

Por tanto, no hay reentrada.

La estrategia puede perder una continuación importante tras una salida temprana.

Añadir reentrada sería una nueva política, no una corrección menor.

---

## 36) Ausencia de stop

No existe:

```text
dollar stop;
ATR stop;
structural stop;
max holding;
gap protection.
```

La única salida es el patrón de ángulos.

Riesgos:

```text
gap adverso;
evento de cola;
regresión que tarda en reaccionar;
pérdida amplia antes de cuatro cambios;
posición overnight.
```

La revista recomienda considerar un stop, pero no lo prueba.

---

## 37) Resultados publicados

### 37.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $9,135.00 |
| Beneficio bruto | $29,467.00 |
| Pérdida bruta | -$20,332.00 |
| Profit Factor | 1.45 |
| Operaciones | 303 |
| Ganadoras | 154 |
| Perdedoras | 149 |
| Percent Profitable | 50.83% |
| Expectativa media | $30.15 |
| Ganancia media | $191.34 |
| Pérdida media | -$136.46 |
| Ratio ganancia/pérdida | 1.40 |
| Mayor ganancia | $2,042.00 |
| Mayor pérdida | -$623.00 |
| Máx. ganadoras consecutivas | 6 |
| Máx. perdedoras consecutivas | 6 |
| Barras medias ganadoras | 11.62 |
| Barras medias perdedoras | 7.57 |
| Acciones acumuladas | 30,400 |
| Account Size Required | $2,413.00 |
| Percent of Time in Market | 72.8% |

### 37.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $5,034.00 | $4,101.00 |
| Profit Factor | 1.51 | 1.39 |
| Operaciones | 161 | 142 |
| Percent Profitable | 57.76% | 42.96% |
| Expectativa media | $31.27 | $28.88 |
| Ganancia media | $160.98 | $237.64 |
| Pérdida media | -$146.13 | -$128.33 |
| Ratio ganancia/pérdida | 1.10 | 1.85 |
| Mayor ganancia | $782.00 | $2,042.00 |
| Mayor pérdida | -$623.00 | -$466.00 |
| Máx. ganadoras consecutivas | 7 | 4 |
| Máx. perdedoras consecutivas | 5 | 7 |
| Barras medias ganadoras | 11.10 | 12.41 |
| Barras medias perdedoras | 7.53 | 7.60 |
| Acciones acumuladas | 16,200 | 14,200 |

### 37.3 Contribución direccional

\[
5{,}034 / 9{,}135
\approx 55.11\%
\]

Long y short están bastante equilibrados en net profit.

No tienen el mismo perfil:

```text
long:
mayor win rate, payoff casi 1:1

short:
menor win rate, payoff 1.85
```

---

## 38) Concentración del mayor trade

La mayor ganancia:

\[
2{,}042 / 9{,}135
\approx 22.35\%
\]

Una sola operación representa aproximadamente el 22% del neto.

No domina el sistema como el outlier del Issue 11, pero es material y pertenece al lado short.

---

## 39) Margen frente a costes

Tamaño fijo:

```text
100 acciones
```

Expectativa:

\[
30.15 / 100
=
\$0.3015
\]

por acción y round trip.

Un coste adicional aproximado de:

```text
30.15 centavos por acción RT
15.08 centavos por acción y lado
```

eliminaría la expectativa media agregada.

El coste ordinario de SPY es mucho menor, pero faltan:

```text
slippage en next open;
gaps;
borrow y dividendos short;
market impact;
eventos de volatilidad.
```

La vulnerabilidad principal no es el spread cotidiano, sino el riesgo de cola sin stop y el scale dependence.

---

## 40) Duración económica

Ganadores:

\[
11.62 \times 130 / 390
\approx 3.87 \text{ sesiones}
\]

Perdedores:

\[
7.57 \times 130 / 390
\approx 2.52 \text{ sesiones}
\]

Los ganadores duran aproximadamente 53% más.

Esto es coherente con trend following.

---

## 41) Curva de capital

La curva muestra:

```text
drawdown inicial cercano a -$2,000;
recuperación;
ascenso escalonado;
meseta alrededor de trades 160–220;
salto fuerte;
drawdown posterior;
recuperación final.
```

No es uniformemente lineal.

Debe analizarse:

```text
por año;
por régimen de volatilidad;
por nivel de SPY;
por long/short;
por slope porcentual;
por threshold crossing density.
```

---

## 42) ¿Dónde podría estar el edge?

Hipótesis:

> Una pendiente de regresión suficientemente positiva o negativa sobre los últimos 10 midpoints identifica una tendencia de corto plazo, y una secuencia de desaceleraciones angulares anticipa su agotamiento.

Mecanismos posibles:

```text
momentum;
persistencia de flujo;
price discovery;
trend continuation;
salida por pérdida de aceleración.
```

Hipótesis alternativas:

```text
simple moving-average momentum;
price-level drift del threshold angular;
bar partition artifact;
bull market;
un gran short trade;
selección in-sample;
ausencia de stop que conserva outliers.
```

---

## 43) Auditoría científica

### 43.1 Ángulo no normalizado

Problema principal.

### 43.2 Un único activo

No prueba portabilidad.

### 43.3 Un único timeframe

130m es una partición específica.

### 43.4 Optimización limitada

El artículo la reconoce.

### 43.5 Grid ausente

No se conservan resultados de optimización.

### 43.6 Sin OOS

No hay holdout.

### 43.7 Sin stop

Riesgo de cola no medido.

### 43.8 Ambigüedad de exit inputs

Oculta por `4/4`.

### 43.9 No reentry

Puede truncar tendencias.

### 43.10 Precio ajustado

El ángulo cambia con ajustes y precio nominal.

### 43.11 Corporate actions

Deben congelarse las vistas.

### 43.12 Short mechanics

No se modelan dividendos o borrow.

### 43.13 Crossover threshold

La frecuencia depende de haber cruzado desde el otro lado, no de permanecer en régimen.

### 43.14 Inicialización

`LRLength=10` requiere warm-up y la primera slope exacta depende del método de la función.

---

## 44) Contrato TSIS

### Datos

```text
SPY 130m canonical bars
SPY raw/adjusted mapping
quotes for next-open validation
corporate actions
session calendar
```

### Estado

```text
bar_end_timestamp
midpoint
lr_length
lr_slope
lr_intercept
lr_angle
angle_threshold_long
angle_threshold_short
long_cross
short_cross
countertrend_window_length
countertrend_required_count
long_countertrend_count
short_countertrend_count
position
```

### Estados de indisponibilidad

```text
INSUFFICIENT_REGRESSION_HISTORY
ANGLE_FORMULA_UNRESOLVED
PRICE_SCALE_MODE_UNRESOLVED
EXIT_INPUT_ROLE_AMBIGUITY
SESSION_ALIGNMENT_UNRESOLVED
CORPORATE_ACTION_UNRESOLVED
MISSING_NEXT_OPEN
```

---

## 45) Pseudocódigo funcional

```python
mid = (high + low) / 2.0

slope = least_squares_slope(
    x=range(10),
    y=mid[t-9:t+1]
)

angle = degrees(arctan(slope))

long_cross = angle_prev <= 2.25 and angle > 2.25
short_cross = angle_prev >= -2.25 and angle < -2.25

if flat:
    if long_cross:
        schedule_long(next_open)
    elif short_cross:
        schedule_short(next_open)

if long:
    comparisons = [
        angle[j] < angle[j - 1]
        for j in range(t - 3, t + 1)
    ]
    if sum(comparisons) >= 4:
        schedule_exit(next_open)

if short:
    comparisons = [
        angle[j] > angle[j - 1]
        for j in range(t - 3, t + 1)
    ]
    if sum(comparisons) >= 4:
        schedule_exit(next_open)
```

La fórmula y roles de inputs deben reconciliarse.

---

## 46) Plan de réplica y falsificación

### Fase 1 — Checksum

```text
303 trades
161 long
142 short
net ≈ $9,135
PF ≈ 1.45
time in market ≈ 72.8%
```

### Fase 2 — Fórmula angular

Comparar contra señales publicadas:

```text
atan(slope) en grados;
slope directa;
endpoint-derived angle;
convenciones de x;
redondeo.
```

### Fase 3 — Exit semantics

Usar inputs deliberadamente distintos:

```text
N=5, K=3
N=3, K=5 inválido
```

para determinar qué parámetro controla cada dimensión.

### Fase 4 — Normalización

| Variante | Pregunta |
|---|---|
| precio nominal | regla publicada |
| log-price slope | ¿generaliza porcentualmente? |
| slope/price | ¿elimina drift de nivel? |
| slope/ATR | ¿controla volatilidad? |
| t-stat slope | ¿la calidad de ajuste aporta valor? |

### Fase 5 — Baselines

```text
SMA slope
EMA crossover
10-bar return
linear-regression slope without angle
random matched entries
```

### Fase 6 — Stops

Evaluar como módulos separados:

```text
ATR stop;
dollar stop;
time stop;
no stop.
```

### Fase 7 — Reentry

Preregistrar una política, no optimizarla silenciosamente.

### Fase 8 — Cross-sectional

```text
SPY
QQQ
IWM
DIA
sector ETFs
liquid futures
```

### Fase 9 — Timeframe

```text
65m
130m
daily
```

usando primero parámetros transformados por una regla preregistrada.

### Fase 10 — Postpublicación

Desde enero de 2016, inputs congelados.

---

## 47) Eventos para Market State y Event State

### Market State

```text
regression_slope
regression_angle_nominal
regression_slope_pct
regression_slope_atr
regression_r2
angle_momentum
countertrend_count
```

### Event State

```text
event_type:
regression_angle_threshold_cross

attributes:
direction
angle
slope
threshold
price_level
atr
r_squared
```

```text
event_type:
regression_angle_countertrend_sequence
```

Outcomes:

```text
next-open return
holding period
MFE
MAE
return by normalization
return by regime
```

---

## 48) Decisión — Regression Angles

```text
IMPLEMENTAR:
sí

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
trend representation
+
slope normalization research
+
proactive exit state

PRIORIDAD:
media-alta

RIESGO PRINCIPAL:
price-scale dependence

SIGUIENTE GATE:
SCC-027-ANGLE-NORMALIZATION-EXIT-STOP-AND-OOS-GATE
```

---

# Parte III — Utility Kit 1

## 49) Identificación

- **ID:** `SCC-2016-01-UTILITY-KIT-001`
- **Páginas físicas:** 17–21
- **Paquete:** `UTILITY KIT 1.ELD`
- **Contenido:**
  - strategy component `TSL:Friday Exit`;
  - strategy component `TSL:Close On Last Bar`;
  - indicator `TSL:Strategy Equity`;
  - PaintBar `TSL:3rd Friday`;
  - function `$MinFluc`.

No son estrategias con edge publicado.

Son herramientas de:

```text
control temporal;
cierre artificial;
monitorización;
calendario;
metadatos de instrumento.
```

---

## 50) TSL:Friday Exit

### Objetivo

Cerrar posiciones al final de la sesión del viernes para permitir:

```text
holding entre días laborables;
sin riesgo de fin de semana.
```

### Input

```text
MaxMinutesBeforeSessionEnd = 0
```

### Hallazgo metodológico

La lógica usa:

```text
timestamp de la barra;
no reloj del ordenador.
```

Por tanto, no garantiza salir exactamente `n` minutos antes.

En un chart de 5m, poner `3` no crea una salida tres minutos antes si no existe una barra con ese timestamp.

### Riesgos

```text
tick/volume bars sin timestamp exacto;
forex;
early close;
holiday Friday;
missing final bar;
time zone;
session template.
```

### Encaje TSIS

Debe representarse como:

```text
event_type:
weekend_risk_exit_due

calendar:
exchange session calendar

execution:
last executable event before weekly close
```

No como un simple `weekday == Friday`.

---

## 51) TSL:Close On Last Bar

### Objetivo

Forzar el cierre de posiciones abiertas al terminar el rango histórico del chart.

### Uso permitido

```text
backtest estático;
chart no actualizable en tiempo real;
comparación de runs truncados.
```

### Riesgo crítico

En tiempo real, cada nueva barra es temporalmente la “last bar”.

La técnica produciría salidas espurias.

### Riesgo científico

Forzar cierre al final de la muestra puede:

```text
alterar el PnL final;
convertir una posición abierta en trade cerrado;
afectar número de trades;
afectar drawdown;
hacer comparables runs, pero no representar una regla de estrategia.
```

TSIS debe separar:

```text
strategy_exit
sample_boundary_liquidation
mark_to_market_open_position
```

Nunca debe atribuir el cierre de frontera al edge.

---

## 52) TSL:Strategy Equity

### Plots

```text
Total Equity
Realized P/L
Open P/L
Zero Line
```

### Funciones

```text
colores por signo;
alerta de nuevo máximo de realized P/L;
alerta de nuevo mínimo;
impresión al EasyLanguage Print Log.
```

### Inputs principales

```text
PrintToLog = False
PrintLast1_PrintAll2 = 1
colores positivos y negativos
colores de nuevos extremos
```

### Encaje TSIS

La idea debe convertirse en artefactos gobernados:

```text
equity_snapshot
realized_pnl
unrealized_pnl
portfolio_timestamp
new_high_watermark
new_drawdown_low
run_id
strategy_version
```

El Print Log no es suficiente para una infraestructura científica; debe ser una tabla tipada y reproducible.

---

## 53) TSL:3rd Friday

### Objetivo

Marcar:

```text
tercer viernes del mes;
días calendario hasta el próximo tercer viernes.
```

Usa la función TradeStation `Next3rdFriday`.

### Uso

En intradía:

```text
pinta todas las barras del tercer viernes;
muestra el conteo sólo junto a la primera barra del día.
```

En diario:

```text
pinta la única barra;
muestra el conteo junto a cada barra.
```

### Riesgo semántico

“Tercer viernes” no equivale siempre a:

```text
expiration efectiva;
sesión abierta;
día de liquidación;
monthly standard expiry para todo producto.
```

Feriados y productos con calendarios distintos requieren un calendario de eventos real.

### Encaje TSIS

```text
event_type:
calendar_option_expiration_reference

attributes:
calendar_third_friday
exchange_open
actual_expiration_date
days_until
```

---

## 54) `$MinFluc`

### Objetivo

Devolver la mínima fluctuación de precio del símbolo.

Se combina con:

```text
BigPointValue
```

para convertir ticks a dinero.

### Uso histórico citado

```text
Moving Average Channel — Issue 1
Engulfing Candles — Issue 10
Pivot Breakout — Issue 12
```

### Encaje TSIS

No debe ser una función aislada sin lineage.

Debe provenir del instrumento:

```text
tick_size
price_scale
min_move
big_point_value
contract_multiplier
effective_date
```

Los metadatos pueden cambiar por contrato o fecha.

---

## 55) Decisión — Utility Kit 1

```text
ADMITIR COMO REFERENCIA:
sí

TRATAR COMO EDGE:
no

VALOR PRINCIPAL:
engine controls
+
calendar events
+
equity reporting
+
instrument metadata

RIESGO PRINCIPAL:
usar herramientas de backtest como reglas live

GATE:
SCC-UK1-ENGINE-CONTROL-SEMANTICS-GATE
```

---

# Parte IV — Ideas transversales del Issue 13

## 56) Una referencia intradía debe tener lifecycle

VWAP necesita:

```text
reset;
warm-up;
update;
freeze temporal;
session close;
exception handling.
```

---

## 57) Un threshold dinámico también se mueve por la observación actual

El cruce no depende sólo del precio.

Depende de:

```text
precio;
volumen;
desviación;
movimiento de la propia banda.
```

---

## 58) True VWAP y bar VWAP no son intercambiables

La diferencia debe ser cuantificada con trades.

---

## 59) El precio nominal puede contaminar una feature

Regression angle es un ejemplo claro.

Una feature puede parecer matemática y seguir sin ser estacionaria.

---

## 60) La igualdad de inputs puede ocultar un bug contractual

`4/4` no permite saber qué input controla:

```text
window;
required count.
```

Los tests de contrato deben utilizar valores asimétricos.

---

## 61) Un stream grande no garantiza evidencia útil

El workspace VWAP contiene megabytes de optimización, pero son de otra versión.

Debe validarse:

```text
model hash;
input schema;
strategy version;
dataset;
run id.
```

antes de consumir un grid.

---

## 62) Duplicados físicos no son experimentos independientes

Dos bloques completos idénticos no duplican la evidencia.

---

## 63) El cierre por frontera de muestra no es una salida económica

`Close On Last Bar` debe etiquetarse.

---

## 64) La ausencia de última barra esperada es un estado

No debe resolverse suponiendo que el EOD exit ocurrió.

---

## 65) Calendario visual y calendario operable son distintos

Tercer viernes requiere contexto de producto y exchange.

---

## 66) Equity, realized y unrealized deben conservarse por separado

Un único valor de equity no permite reconstruir exposición ni riesgo.

---

## 67) Ideas secundarias de backtesting

1. Comparar VWAP de barras con VWAP de trades.
2. Testar bandas inclusive y lagged.
3. Versionar la sesión.
4. Registrar excepciones overnight.
5. Expresar costes por acción ejecutada.
6. Descomponer long y short.
7. Normalizar slopes por precio, ATR o error estándar.
8. Diseñar tests con inputs asimétricos.
9. Guardar model hash en cada OptimizationData.
10. Distinguir cierre estratégico de liquidación de frontera.
11. Persistir realized y open P/L.
12. Usar calendarios de exchange, no sólo weekday.
13. Mantener tick size con effective date.
14. No convertir sugerencias de mejora en reglas sin OOS.
15. No interpretar una superficie visual como validación.

---

# Parte V — Registro consolidado para TSIS

## 68) Objetos de información afectados

### VWAP Bands

Principalmente:

```text
price_location_intraday
trading_activity
volatility_range_state
price_movement
market_microstructure_state
```

### Regression Angles

Principalmente:

```text
price_movement
volatility_range_state
price_location_intraday
```

### Utility Kit

Afecta al control plane:

```text
session state
calendar state
instrument metadata
portfolio state
run boundary
```

---

## 69) Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | VWAP formula/session/cost replay | PF bajo y edge dependiente de ejecución |
| 2 | Regression angle normalization | puede invalidar portabilidad y estabilidad temporal |
| 3 | VWAP postpublication long-only | rama con mayor evidencia |
| 4 | Regression exit-contract test | ambigüedad oculta por inputs iguales |
| 5 | Utility Kit semantics | evita errores del engine y cierres falsos |

---

## 70) Gates propuestos

### SCC-026-A — VWAP Formula

Debe resolver:

```text
bar price proxy;
volume source;
cumulation;
tick comparison.
```

### SCC-026-B — Band Dispersion

Debe resolver:

```text
weighted/unweighted;
sample/population;
inclusive/lagged.
```

### SCC-026-C — Session Contract

Debe reproducir:

```text
first two bars;
last-bar open exit;
half-days;
halts;
9 overnight exceptions.
```

### SCC-026-D — Corporate Action Consistency

Debe reconciliar AAPL precio y volumen.

### SCC-026-E — Cost Survival

Debe mostrar PnL bajo quotes y slippage.

### SCC-026-F — Current Optimization Lineage

Debe impedir consumir el grid antiguo como si fuera actual.

### SCC-026-G — Postpublication OOS

Inputs congelados `2/22`.

### SCC-027-A — LinearReg Formula

Debe reconciliar slope y angle.

### SCC-027-B — Price-Scale Invariance

Debe comparar normalizaciones.

### SCC-027-C — Exit Input Roles

Debe usar valores asimétricos.

### SCC-027-D — Emergency Risk

Debe estudiar stop como módulo separado.

### SCC-027-E — Reentry Policy

Debe preregistrarse.

### SCC-027-F — Postpublication OOS

Inputs congelados `10/2.25/-2.25/4/4`.

### SCC-UK1-A — Sample Boundary Liquidation

Debe etiquetar `Close On Last Bar`.

### SCC-UK1-B — Calendar Exit

Debe utilizar exchange calendar.

### SCC-UK1-C — Equity Artifact

Debe persistir realized/unrealized.

### SCC-UK1-D — Instrument Tick Metadata

Debe versionar tick y multiplier.

---

# Conclusión

El Issue 13 contiene dos estrategias nuevas y un Utility Kit de valor arquitectónico.

## VWAP Bands

La estrategia es:

```text
VWAP intradía estimado
+
bandas dinámicas de 2 desviaciones
+
breakout al cierre
+
entrada next bar
+
salida por extremo de 22 barras
+
liquidación EOD
```

Publica:

```text
2,282 trades
$21,485.52
PF 1.20
$9.42 por trade
```

pero:

```text
la expectativa tolera sólo ≈2.94 centavos/acción RT adicionales;
la fórmula exacta de VWAP y sigma no está certificada;
la sesión y early closes son parte del modelo;
9 trades quedaron overnight;
AAPL exige coherencia precio-volumen-corporate actions;
el OptimizationData embebido es de una versión distinta.
```

Su mayor valor para TSIS es investigar **Price Location Intraday** con un estado acumulativo de sesión y ejecución realista.

## Regression Angles

La estrategia es:

```text
regresión de 10 midpoints
→ ángulo nominal
→ entrada al cruzar ±2.25°
→ salida tras 4 cambios angulares adversos
```

Publica:

```text
303 trades
$9,135
PF 1.45
50.83% ganadoras
```

pero:

```text
el ángulo depende del precio nominal y del timeframe;
la sensibilidad cambia conforme SPY sube;
los roles de los dos inputs de salida no pueden distinguirse con 4/4;
no hay stop;
no hay reentrada;
no hay OOS ni grid conservado.
```

Su mayor valor es como laboratorio de **representación de tendencia normalizada**.

## Utility Kit 1

No aporta edge, pero sí contratos esenciales:

```text
weekend exit;
sample-boundary liquidation;
equity decomposition;
calendar event;
tick metadata.
```

Deben implementarse como controles explícitos del engine, no mezclarse con las señales.

## Estado final

```text
ISSUE_13_STATUS:
DOCUMENTALLY_CLOSED

PACKAGE_INSPECTION:
COMPLETE_WITH_PROPRIETARY_CODE_LIMITATION

NEW_STRATEGIES_EXTRACTED:
2

UTILITY_KITS_EXTRACTED:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguientes gates recomendados:

```text
1. SCC-026-VWAP-FORMULA-SESSION-COST-AND-OOS-GATE
2. SCC-027-ANGLE-NORMALIZATION-EXIT-STOP-AND-OOS-GATE
3. SCC-UK1-ENGINE-CONTROL-SEMANTICS-GATE
```
