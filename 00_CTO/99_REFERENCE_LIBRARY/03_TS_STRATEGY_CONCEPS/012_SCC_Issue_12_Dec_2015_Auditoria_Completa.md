# Auditoría completa — TradeStation Strategy Concepts Club, Issue 12 (diciembre de 2015)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. Market Breadth Gauge Strategy
2. Pivot Breakout Strategy
3. identificación del artículo bonus Williams E-mini Influx como material repetido
4. ideas secundarias de investigación y backtesting presentes en el número
5. reconstrucción matemática, temporal y de máquinas de estado
6. auditoría de los resultados publicados
7. inspección forense de los archivos .ELD y workspaces .tsw
8. contratos de implementación y réplica para TSIS
9. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 21 páginas: `SCC+Issue+12+Dec+2015.pdf`.
- Archivo de apoyo: `2015-12.zip`.
- PDF de la revista incluido dentro del ZIP.
- PDF auxiliar `Strategy Concepts Club Inventory.pdf`.
- Dos contenedores propietarios correspondientes a las estrategias nuevas:
  - `TSL MARKET BREADTH GAUGE.ELD`;
  - `TSL PIVOT BREAKOUT.ELD`.
- Dos workspaces OLE/Compound Document:
  - `TSL Market Breadth Gauge.tsw`;
  - `TSL.Pivot Breakout.tsw`.
- Archivos repetidos de `Williams E-mini Influx`, ya auditados en el Issue 10.
- Todas las páginas renderizadas del PDF, incluidas:
  - fórmula conceptual, señales, resultados y superficies de sensibilidad de Market Breadth Gauge;
  - definición visual del pivot, reglas, resultados y curva de capital de Pivot Breakout;
  - páginas del artículo bonus repetido.

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

Cuando una decisión no queda resuelta por la revista o el paquete se registra como ambigüedad. No se completa silenciosamente.

Las fórmulas que no aparecen literalmente en el artículo se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

No se ha utilizado investigación web externa para completar las reglas de las estrategias.

---

## 0.1 Integridad del paquete

El PDF cargado por separado y el PDF incluido dentro del ZIP son binariamente idénticos.

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `2015-12.zip` | 6,221,150 bytes | `8eda1e49cdbc652b88cbc62d7652b9fd4a029329cd34ac2d4ef7357a09428fe4` |
| `SCC+Issue+12+Dec+2015.pdf` | 6,159,198 bytes | `7beb44e09c06fd58cc5b7e07b75ddf661c3db25cb57b264dd417bfad4c92409b` |
| `Strategy Concepts Club Inventory.pdf` | 25,584 bytes | `91b7ffa24efbc71bdc752c558e3a5f45002073e1dd1ae5651717513324655cf8` |
| `TSL MARKET BREADTH GAUGE.ELD` | 16,313 bytes | `8e53ea3cae20fb019b4c9f6e84530839a358fb30957d46045d08c6f58ce22f39` |
| `TSL Market Breadth Gauge.tsw` | 28,160 bytes | `c83204652c7b606ac8f4cda16edea115c8036db3e5407ff121a35f5213e25efd` |
| `TSL PIVOT BREAKOUT.ELD` | 15,533 bytes | `4d10fc4f01016afad4f92eb787a4cd2ba4c2a6dac6950ee56fd630e806af8096` |
| `TSL.Pivot Breakout.tsw` | 27,136 bytes | `9f7aa26f7be3c6db9a8553d51a434636a775b998297b1473a626d515496f0a6a` |
| `TSL WILLIAMS E-MINI INFLUX.ELD` repetido | 18,805 bytes | `94ff62ae6fe0fc470f14104010f18104a40dd749b49c4b4cb9487ff60655ee6d` |
| `TSL.Williams E-mini Influx.tsw` repetido | 26,112 bytes | `0fa90f393a55e66c96dbe1e17aabea354f623f42af20ad2a5da981d1f8977117` |

Los hashes de Williams E-mini Influx coinciden exactamente con los registrados en los Issues 10 y 11:

```text
PACKAGE_CARRYOVER_DUPLICATE
NOT_A_NEW_STRATEGY
```

Los pequeños streams `Zone.Identifier` son metadatos del sistema de archivos y no forman parte del contenido científico.

El PDF `Strategy Concepts Club Inventory.pdf` es un índice documental del primer año. No añade reglas, código ni resultados a las dos estrategias del número.

---

## 0.2 Limitación de los `.ELD`

Los `.ELD` son contenedores propietarios de TradeStation. No exponen el código EasyLanguage como texto legible.

Por tanto:

```text
se confirma la existencia de las técnicas;
no puede auditarse el código línea por línea;
no puede certificarse la fórmula exacta de normalización del MBG;
no puede certificarse la prioridad exacta de órdenes;
no puede resolverse por lectura directa:
    - inclusión de la observación actual en rolling statistics;
    - semántica exacta de Lowest/Highest;
    - tratamiento de igualdad en pivots;
    - contador de closes en la barra de entrada;
    - precedencia entre fill, cancelación y nuevo pivot.
```

---

## 0.3 Workspaces OLE y optimización

Los dos workspaces son contenedores OLE válidos.

### Market Breadth Gauge

Streams principales:

| Stream | Tamaño |
|---|---:|
| `Embedding 5/Contents` | 18,543 bytes |
| `Embedding 5/ChartSetting` | 1,332 bytes |
| `Embedding 5/StatusLine` | 368 bytes |
| `Embedding 5/SubgraphSetting` | 324 bytes |
| `Embedding 5/AnalisysTechniques` | 323 bytes |
| `Embedding 5/optdatafile` | **0 bytes** |

### Pivot Breakout

| Stream | Tamaño |
|---|---:|
| `Embedding 1/Contents` | 17,614 bytes |
| `Embedding 1/ChartSetting` | 1,332 bytes |
| `Embedding 1/DrawingObjects` | 595 bytes |
| `Embedding 1/AnalisysTechniques` | 374 bytes |
| `Embedding 1/optdatafile` | **0 bytes** |

En ambos casos:

```text
no se conserva el grid de optimización;
no se conservan rankings completos;
no se conserva el número de configuraciones probadas;
no puede comprobarse el puesto exacto de los parámetros publicados;
no puede medirse directamente la intensidad de la selección in-sample.
```

---

## 0.4 Evidencia del workspace Market Breadth Gauge

El workspace confirma:

```text
Data1:
QQQ Daily [NASDAQ]
PowerShares QQQ Trust Series 1

Data2:
$VALNDD
NQ100 Up-Down Value Difference

Técnicas:
TSL:Market Breadth Gauge Strategy
TSL:Market Breadth Gauge Indicator
```

Inputs activos de la estrategia:

```text
Fast_MA_Length = 5
Slow_MA_Length = 30
Sample_Size = 20
MBG_LE_Level = -0.5
MBG_SE_Level = 2
Trail_Stop_Length = 2
My_Stop_Loss = 400
```

Inputs activos del indicador:

```text
Fast_MA_Length = 5
Slow_MA_Length = 30
Sample_Size = 20
MBG_LE_Level = -0.5
MBG_SE_Level = 2
Pos_Color = Green
Neg_Color = Magenta
Base_Color = DarkGray
```

---

## 0.5 Evidencia del workspace Pivot Breakout

El workspace confirma:

```text
Serie:
SPY 65 min [ARCX]
SPDR S&P 500 ETF

Técnicas:
Pivot High ShowMe
Pivot Low ShowMe
TSL:Pivot Breakout Strategy
```

Inputs activos:

```text
LeftStrength = 4
RightStrength = 2
HigherClosesSX = 4
LowerClosesLX = 4
PenetrationTicks = 1
```

El stream de dibujo contiene referencias residuales a otros símbolos y workspaces, entre ellos `@GC=103NN`. Se consideran metadatos gráficos huérfanos y no evidencia de que la estrategia publicada opere oro.

---

## 0.6 Resultado ejecutivo del Issue 12

| ID | Estrategia | Tipo real | Resultado publicado | Hallazgo crítico | Decisión |
|---|---|---|---|---|---|
| 024 | Market Breadth Gauge | Reversión/continuación de impulso de breadth normalizado, operando QQQ con una serie secundaria propietaria | 164 trades; $8,939.47; PF 2.21; 51.83% ganadoras | fórmula exacta y reconstrucción histórica del índice no certificables; 76.54% del beneficio procede de longs; sólo 26 shorts | candidato prioritario de réplica multi-data, no edge aceptado |
| 025 | Pivot Breakout | Pivot confirmado retrospectivamente + stop de ruptura + cancelación por nuevo pivot + dos exits | 865 trades; $7,336; PF 1.18; 38.50% ganadoras | expectativa total $8.48/trade y short $2.02/trade; fuerte dependencia del orden intrabar y del bull market | excelente benchmark de event/state/order lifecycle; evidencia económica débil |

Estado del número:

```text
ISSUE_12_STATUS:
DOCUMENTALLY_CLOSED

NEW_STRATEGIES:
2

DUPLICATE_PACKAGE_STRATEGIES:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

---

# Parte I — Estrategia 024: Market Breadth Gauge

## 1) Identificación

- **ID:** `SCC-2015-12-STRAT-024`
- **Artículo:** *Market Breadth Gauge Strategy*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas del PDF:** 4–9
- **Estilo declarado:** trend-following
- **Mercados declarados:** stock-index futures y ETFs
- **Horizonte:** swing trading
- **Activo operado:** QQQ
- **Serie informativa:** `$VALNDD`
- **Bar interval:** diario
- **Capital inicial:** $15,000
- **Tamaño:** $10,000 por trade, redondeado hacia abajo a una acción
- **Comisión:** $0.01 por acción
- **Historia declarada:** 5 años terminando el 30 de septiembre de 2015
- **Inputs:** `5 / 30 / 20 / -0.5 / 2 / 2 / 400`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, si se dispone o reconstruye la serie de breadth. |
| ¿Puede replicarse exactamente con datos públicos corrientes? | **No necesariamente.** `$VALNDD` es una serie calculada por el proveedor. |
| ¿Se conoce la fórmula conceptual del índice? | **Sí.** Valor de avances menos valor de descensos. |
| ¿Se conoce la fórmula exacta de normalización? | **No desde el paquete.** La reconstrucción más probable es un z-score rolling. |
| ¿Es realmente trend-following? | **Sólo parcialmente.** Las entradas son cruces de recuperación o deterioro desde niveles extremos. |
| ¿El lado short es fiable? | **No.** Sólo 26 operaciones y el test pertenece a un gran bull market. |
| ¿Los parámetros fueron elegidos in-sample? | **Sí, al menos parcialmente.** |
| ¿Está lista para operar? | **No.** Falta reproducción de Data2, OOS y atribución frente a beta long. |
| ¿Merece estudio? | **Sí.** Es una estrategia multi-data muy relevante para Broad Market Context de TSIS. |

Clasificación:

```text
MULTI_DATA_SOURCE_REPRODUCTION_CANDIDATE
BROAD_MARKET_BREADTH_EVENT
NORMALIZED_STATE_TRANSITION
PROVIDER_DEPENDENT
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2) Qué es el índice value-based breadth

La revista define el índice como:

```text
suma, para las acciones que avanzan:
    cambio de precio × volumen

menos

suma, para las acciones que caen:
    cambio de precio × volumen

multiplicado por 0.0001
```

Reconstrucción conceptual:

\[
B_t =
0.0001
\left[
\sum_{i \in Adv_t}
\Delta P_{i,t} V_{i,t}
-
\sum_{i \in Dec_t}
|\Delta P_{i,t}| V_{i,t}
\right]
\]

Una forma algebraicamente equivalente, si el signo del cambio se conserva, sería:

\[
B_t =
0.0001
\sum_{i \in U_t}
\Delta P_{i,t}V_{i,t}
\]

donde `U_t` es el universo del índice.

Para QQQ se usa:

```text
$VALNDD
NASDAQ 100 Up Value – Down Value Difference
```

La revista también relaciona:

| ETF | Índice value-based |
|---|---|
| QQQ | `$VALNDD` |
| IWM | `$VALRLD` |
| SPY | `$VALSPD` |
| DIA | `$VALID` |

---

## 3) Problema de reproducibilidad de Data2

Para reconstruir `$VALNDD` históricamente no basta con descargar QQQ.

Se necesita:

```text
composición point-in-time del Nasdaq 100;
precios de todos los componentes;
volumen de todos los componentes;
corporate actions;
cambios de ticker;
sesiones y cierres;
reglas exactas del proveedor;
tratamiento de unchanged issues;
tratamiento de missing prints;
tratamiento de componentes incorporados o eliminados;
versión histórica del índice calculado.
```

Quedan sin resolver:

```text
si el proveedor usa composición point-in-time;
si el historial fue recalculado con componentes posteriores;
si emplea precios ajustados o raw;
qué volumen utiliza;
cómo trata ADR, splits y dividendos;
si la serie fue revisada después de cada sesión.
```

Por tanto, para TSIS deben existir dos modos:

```text
PROVIDER_NATIVE_REPLAY:
usar la serie histórica original del proveedor

TSIS_RECONSTRUCTED_BREADTH:
reconstruirla con un contrato propio y point-in-time
```

Los resultados de ambos no deben mezclarse.

---

## 4) Reconstrucción matemática del Market Breadth Gauge

La revista indica que:

1. calcula una EMA rápida del breadth;
2. calcula una EMA lenta;
3. obtiene la diferencia;
4. normaliza esa diferencia con una muestra de 20;
5. produce un oscilador que suele viajar entre aproximadamente -2 y +2.

### 4.1 Medias

\[
F_t = EMA_5(B)_t
\]

\[
S_t = EMA_{30}(B)_t
\]

### 4.2 Diferencia

\[
D_t = F_t - S_t
\]

### 4.3 Normalización probable

La reconstrucción funcional más probable es:

\[
MBG_t =
\frac{D_t - \mu_{20}(D)_t}
{\sigma_{20}(D)_t}
\]

Es decir, un z-score rolling de la diferencia de EMAs.

Sin embargo, el `.ELD` no permite certificar:

```text
sample std vs population std;
inclusión de D_t en la ventana;
media simple vs otro centro;
normalización por desviación estándar de D;
normalización por otra escala;
tratamiento de sigma = 0;
warm-up exacto.
```

Estado:

```text
NORMALIZATION_FORMULA_UNRESOLVED
```

---

## 5) Semántica real de las señales

### Long

\[
MBG_{t-1} \le -0.5
\quad\land\quad
MBG_t > -0.5
\]

Entrada:

```text
buy QQQ at next daily open
```

No se exige que el breadth sea positivo.

La señal significa:

> El breadth estaba deprimido y comienza a recuperarse, aunque todavía puede permanecer por debajo de cero.

### Short

\[
MBG_{t-1} \ge 2
\quad\land\quad
MBG_t < 2
\]

Entrada:

```text
short QQQ at next daily open
```

No se exige breadth negativo.

La señal significa:

> El breadth era extremadamente fuerte y comienza a deteriorarse.

### 5.1 Clasificación más precisa

Aunque el artículo la denomina trend-following, la mecánica es una combinación de:

```text
long:
recovery / reacceleration after weak breadth

short:
deceleration after very strong breadth
```

Es un modelo de **transición de estado**, no una simple estrategia que compra breadth positivo y vende breadth negativo.

---

## 6) Asimetría de thresholds y frecuencia

Los niveles son:

```text
long cross = -0.5
short cross = +2
```

La rama long necesita una recuperación desde debilidad moderada.

La rama short necesita haber alcanzado primero un extremo positivo mucho más exigente.

Eso explica parte de la diferencia de frecuencia:

```text
138 longs
26 shorts
```

Por tanto, la comparación long/short mezcla:

```text
dirección;
umbral;
frecuencia;
régimen de mercado;
distribución del MBG.
```

No demuestra por sí sola que el mercado sea estructuralmente más predecible al alza.

---

## 7) Arquitectura temporal Data1/Data2

### Data1

```text
QQQ daily
```

### Data2

```text
$VALNDD daily
```

### Decision timestamp

La señal se forma después del cierre de la sesión `t`, cuando:

```text
está cerrado QQQ;
está finalizado el breadth de componentes;
se han calculado las EMAs y la normalización;
se ha confirmado el cruce.
```

### Ejecución

```text
open de QQQ en t+1
```

### Riesgo de alineación

Debe certificarse que el dato `$VALNDD_t`:

```text
estaba disponible antes del open t+1;
corresponde a la misma sesión de QQQ;
no fue revisado después;
no se unió sólo por fecha ignorando timestamps.
```

---

## 8) Salidas por extremo de dos barras

La revista dice:

```text
long:
salir si Low está por debajo del lowest low de las últimas 2 barras

short:
salir si High está por encima del highest high de las últimas 2 barras
```

Si la barra actual se incluye:

\[
Low_t < Lowest(Low,2)_t
\]

es imposible.

La reconstrucción más probable es:

\[
LongExit_t =
Low_t <
\min(Low_{t-1}, Low_{t-2})
\]

\[
ShortExit_t =
High_t >
\max(High_{t-1}, High_{t-2})
\]

y ejecución en:

```text
open t+1
```

Otra posibilidad es una función `Lowest/Highest` desplazada un bar.

Debe reconciliarse con la lista de operaciones.

---

## 9) Dollar stop y sizing

El tamaño nominal es aproximadamente:

\[
Notional \approx \$10,000
\]

El stop es:

\[
\$400
\]

Por tanto, salvo efectos de redondeo:

\[
400 / 10,000 = 4\%
\]

Aunque el input se expresa en dólares, bajo sizing de notional constante actúa aproximadamente como:

```text
stop del 4% sobre la posición
```

Queda por confirmar la semántica TradeStation:

```text
stop por posición;
stop por acción;
fill intrabar;
activación desde entry bar;
gap through stop.
```

El informe muestra una mayor pérdida de `-$404.43`, coherente con un stop de $400 más comisión o gap pequeño.

---

## 10) Reglas funcionales

```python
breadth_fast = ema(value_breadth, 5)
breadth_slow = ema(value_breadth, 30)
spread = breadth_fast - breadth_slow

mbg = rolling_zscore(spread, 20)  # reconstruction, to be reconciled

long_cross = mbg[t - 1] <= -0.5 and mbg[t] > -0.5
short_cross = mbg[t - 1] >= 2.0 and mbg[t] < 2.0

if flat:
    if long_cross:
        schedule_long(next_open, notional=10_000)
    elif short_cross:
        schedule_short(next_open, notional=10_000)

if long:
    if low[t] < min(low[t - 1], low[t - 2]):
        schedule_exit(next_open)
    elif position_pnl <= -400:
        exit_at_stop_model()

if short:
    if high[t] > max(high[t - 1], high[t - 2]):
        schedule_exit(next_open)
    elif position_pnl <= -400:
        exit_at_stop_model()
```

---

## 11) Resultados publicados

### 11.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $8,939.47 |
| Beneficio bruto | $16,348.04 |
| Pérdida bruta | -$7,408.57 |
| Profit Factor | 2.21 |
| Operaciones | 164 |
| Ganadoras | 85 |
| Perdedoras | 79 |
| Percent Profitable | 51.83% |
| Expectativa media | $54.51 |
| Ganancia media | $192.33 |
| Pérdida media | -$93.78 |
| Ratio ganancia/pérdida | 2.05 |
| Mayor ganancia | $1,079.04 |
| Mayor pérdida | -$404.43 |
| Máx. ganadoras consecutivas | 5 |
| Máx. perdedoras consecutivas | 6 |
| Barras medias ganadoras | 5.82 |
| Barras medias perdedoras | 3.43 |
| Máximo tamaño | 236 acciones |
| Acciones acumuladas | 23,161 |
| Return on Initial Capital | 59.60% |
| Annual Rate of Return | 8.44% |
| Return Retracement Ratio | 0.34 |
| RINA Index | 162.17 |
| Percent of Time in Market | 42.79% |
| Drawdown semanal aproximado | 5% |

### 11.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $6,841.91 | $2,097.56 |
| Profit Factor | 1.99 | 5.51 |
| Operaciones | 138 | 26 |
| Percent Profitable | 50.72% | 57.69% |
| Expectativa media | $49.58 | $80.68 |
| Ganancia media | $196.94 | $170.81 |
| Pérdida media | -$102.12 | -$42.23 |
| Ratio ganancia/pérdida | 1.93 | 4.04 |
| Mayor ganancia | $1,079.04 | $344.96 |
| Mayor pérdida | -$404.43 | -$106.20 |
| Barras medias ganadoras | 6.06 | 4.73 |
| Barras medias perdedoras | 3.56 | 2.64 |
| Acciones acumuladas | 19,625 | 3,536 |

### 11.3 Concentración long

\[
6,841.91 / 8,939.47
\approx 76.54\%
\]

Más de tres cuartas partes del neto procede del lado long.

### 11.4 Muestra short

Sólo hay:

```text
26 shorts
15 ganadores
11 perdedores
```

El PF 5.51 y ratio 4.04 no son estimaciones fiables.

La propia revista reconoce que el ratio short es poco realista.

---

## 12) Margen frente a costes

Promedio de acciones por trade:

\[
23,161 / 164
\approx 141.23
\]

La expectativa de $54.51 equivale a:

\[
54.51 / 141.23
\approx \$0.386
\]

por acción y round trip.

Es decir, haría falta aproximadamente:

```text
38.6 centavos por acción round trip adicionales
19.3 centavos por acción y lado
```

para eliminar la expectativa media agregada.

En QQQ diario, la estrategia no parece especialmente frágil frente al spread ordinario.

El principal riesgo no es el coste marginal, sino:

```text
reproducibilidad de Data2;
selección in-sample;
beta long;
calidad del periodo;
fórmula exacta.
```

---

## 13) Discrepancia de periodo

La tabla declara:

```text
5 años terminando 9/30/2015
```

La captura del informe muestra:

```text
QQQ Daily (12/31/2009–9/30/2015)
```

y el campo `Trading Period` indica:

```text
5 Yrs, 6 Mths, 14 Days
```

No son exactamente equivalentes.

Posibles causas:

```text
historia cargada adicional para warm-up;
primera operación posterior;
redondeo editorial;
diferencia entre chart span y trading span.
```

Estado:

```text
SOURCE_DATE_RANGE_MINOR_CONFLICT
```

---

## 14) Curva de capital

La curva mostrada es ascendente y relativamente suave, pero contiene:

```text
mesetas;
retrocesos;
aceleración notable al final;
periodos de performance cíclica.
```

No demuestra estabilidad fuera de muestra.

El tramo 2010–2015 es, además, un periodo fuertemente alcista en acciones estadounidenses.

Debe compararse con:

```text
QQQ buy-and-hold;
long-only random-entry matched holding;
crosses sin short;
simple breadth > 0;
QQQ trend filters.
```

---

## 15) Sensibilidad y selección

La revista ejecuta dos optimizaciones por pares.

### 15.1 Fast × Slow

```text
Fast_MA_Length
Slow_MA_Length
```

Hallazgos:

```text
ridge relativamente estable;
default 5/30 cerca de la parte alta;
caída severa cuando las longitudes convergen;
reglas invertidas cuando Fast > Slow.
```

La región `Fast >= Slow` no representa una variación comparable de la misma hipótesis: invierte la interpretación de la diferencia de medias.

En una auditoría científica debería excluirse o etiquetarse como:

```text
DIFFERENT_MODEL_CLASS
```

### 15.2 Long level × Short level

```text
MBG_LE_Level
MBG_SE_Level
```

Los defaults `-0.5 / 2` se seleccionan en una región relativamente estable, no en el pico.

Esto es mejor que seleccionar el máximo, pero sigue siendo:

```text
selección sobre la muestra reportada;
sin OOS;
sin corrección por múltiples pruebas;
sin grid conservado.
```

---

## 16) ¿Dónde podría estar el edge?

Hipótesis principal:

> La recuperación de breadth desde debilidad anticipa continuidad positiva del índice, y el deterioro desde breadth extremo anticipa una corrección.

Mecanismos posibles:

```text
participación interna precede al índice;
amplitud de mercado revela confirmación o divergencia;
volumen de componentes detecta presión institucional;
el ETF agregado reacciona con retraso;
breadth extremo revierte antes que precio.
```

Hipótesis alternativas:

```text
exposición long durante bull market;
umbral short demasiado extremo;
índice del proveedor con sesgo de construcción;
constituent survivorship;
optimización;
simple momentum de QQQ;
mean reversion del propio breadth sin información incremental.
```

---

## 17) Auditoría científica

### 17.1 Data2 propietaria

Es el principal problema de reproducción.

### 17.2 Fórmula exacta no certificada

La normalización puede cambiar señales.

### 17.3 Un único ETF

No se publica un panel comparable.

### 17.4 Periodo bull

La rama long puede capturar beta.

### 17.5 Sólo 26 shorts

No puede aceptarse el PF short.

### 17.6 Parámetros parcialmente optimizados

El artículo lo reconoce.

### 17.7 Pairwise optimization

No explora interacciones completas, pero sí introduce selección.

### 17.8 Sin OOS

No hay holdout ni walk-forward.

### 17.9 Constituents point-in-time

No queda demostrado.

### 17.10 Revisión del índice

No queda documentada.

### 17.11 Salida de dos barras ambigua

Debe reconciliarse.

### 17.12 Stop intrabar

No hay modelo explícito de gaps y fills.

### 17.13 Sizing calculado con precio desconocido

Debe fijarse qué precio determina las acciones:

```text
close de señal;
next open;
otro precio de referencia.
```

---

## 18) Contrato TSIS

### Datos

```text
QQQ daily raw/adjusted
$VALNDD native, o componentes Nasdaq 100 PIT
constituent membership
daily price and volume per constituent
corporate actions
session calendar
```

### Campos de estado

```text
decision_timestamp
breadth_source_mode
breadth_value
breadth_fast_ema
breadth_slow_ema
breadth_spread
breadth_spread_mean_20
breadth_spread_std_20
mbg_value
cross_le_up
cross_se_down
qqq_position
prior_two_low
prior_two_high
dollar_stop
position_notional
quantity
```

### Estados de indisponibilidad

```text
MISSING_BREADTH_INDEX
BREADTH_UNIVERSE_UNRESOLVED
BREADTH_REVISION_STATE_UNKNOWN
INSUFFICIENT_NORMALIZATION_HISTORY
ZERO_NORMALIZATION_SCALE
DATA1_DATA2_ALIGNMENT_FAILURE
EXIT_SELF_INCLUSION_UNRESOLVED
MISSING_NEXT_OPEN
```

---

## 19) Eventos candidatos para Event State

```text
event_type:
breadth_recovery_cross

subject_scope:
nasdaq_100_breadth

attributes:
mbg_value
threshold = -0.5
breadth_spread
overshoot
days_below_threshold
qqq_return_state
```

```text
event_type:
breadth_extreme_deterioration_cross

threshold = 2.0
```

Outcomes:

```text
next_open_return
1d / 5d / 10d returns
MFE
MAE
time_to_two-bar-exit
return_vs_QQQ_regime
```

---

## 20) Plan de réplica y falsificación

### Fase 1 — Reproducción con proveedor

Checksums:

```text
164 trades
138 long
26 short
net ≈ $8,939.47
PF ≈ 2.21
time in market ≈ 42.79%
```

### Fase 2 — Fórmula de normalización

Comparar:

```text
z-score inclusive;
z-score lagged;
sample std;
population std;
EMA spread / std;
spread / ATR-like scale.
```

### Fase 3 — Reconstrucción TSIS

Construir breadth desde componentes PIT y comparar:

```text
correlación diaria;
distribución;
cross timestamps;
trades reproducidos;
PnL.
```

### Fase 4 — Ablaciones

| Variante | Pregunta |
|---|---|
| QQQ signal without breadth | ¿Data2 aporta información? |
| breadth spread sin normalizar | ¿normalización aporta valor? |
| MBG state, no cross | ¿el cruce aporta valor? |
| long-only | ¿short aporta algo? |
| thresholds simétricos | ¿la asimetría está seleccionada? |
| sin dollar stop | ¿el stop añade valor? |
| holding fijo | ¿la salida de 2 barras es especial? |

### Fase 5 — Otros índices

```text
SPY + $VALSPD
IWM + $VALRLD
DIA + $VALID
```

Sin retocar parámetros en el primer test.

### Fase 6 — Postpublicación

Desde diciembre de 2015 en adelante con parámetros congelados.

### Fase 7 — Baselines de régimen

```text
QQQ > SMA200
QQQ momentum 20d
advance-decline clásico
up-volume/down-volume
random entries matched by exposure
```

### Fase 8 — Attribution

Separar:

```text
breadth alpha;
equity beta;
timing;
sizing;
stop;
exit.
```

---

## 21) Decisión — Market Breadth Gauge

```text
IMPLEMENTAR:
sí, como réplica multi-data prioritaria

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
Broad Market Context
+
breadth state
+
secondary data synchronization

PRIORIDAD:
alta

RIESGO PRINCIPAL:
reproducibilidad y point-in-time de Data2

SIGUIENTE GATE:
SCC-024-BREADTH-FORMULA-DATA2-AND-OOS-GATE
```

---

# Parte II — Estrategia 025: Pivot Breakout

## 22) Identificación

- **ID:** `SCC-2015-12-STRAT-025`
- **Artículo:** *Pivot Breakout Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas:** 11–14
- **Estilo declarado:** bar pattern
- **Mercados declarados:** equities, futures, forex
- **Horizonte:** swing trading
- **Activo:** SPY
- **Intervalo:** 65 minutos
- **Historia:** 5 años terminando el 30 de septiembre de 2015
- **Tamaño:** 100 acciones
- **Comisión:** $0.01 por acción
- **LIBBT:** 5 minutos
- **Inputs:** `4 / 2 / 4 / 4 / 1`

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Usa pivots de forma causal? | **Sí, si el timestamp de señal se sitúa tras las barras de right strength.** |
| ¿El marcador gráfico repinta retrospectivamente? | **Visualmente sí.** Se dibuja sobre la pivot bar tras confirmarse. |
| ¿Puede implementarse? | **Sí**, como máquina de setup, pending order, cancelación y posición. |
| ¿Puede replicarse con OHLC 65m? | **No exactamente.** Requiere orden intrabar. |
| ¿LIBBT 5m resuelve todo? | **No.** Puede haber fill, stop y nuevo pivot dentro de 5m. |
| ¿El resultado agregado es robusto? | **No especialmente.** PF 1.18 y $8.48 por trade. |
| ¿La rama short aporta valor? | **Prácticamente no.** $888 totales y $2.02 por trade. |
| ¿El artículo demuestra edge? | **No.** Un activo, bull market, sin OOS y sin slippage. |
| ¿Merece implementación? | **Sí**, como benchmark de Event State y order lifecycle. |
| ¿Está lista para operar? | **No.** |

Clasificación:

```text
CONFIRMED_PIVOT_EVENT
PENDING_BREAKOUT_ORDER_STATE_MACHINE
INTRABAR_EXECUTION_REQUIRED
ECONOMIC_EDGE_WEAK
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 23) Pivot low: definición formal

Sea `p` la pivot bar.

Con:

```text
LeftStrength = L = 4
RightStrength = R = 2
```

Una pivot low requiere:

\[
Low_p \le Low_{p-i}
\quad
\forall i \in \{1,\dots,L\}
\]

y:

\[
Low_p < Low_{p+j}
\quad
\forall j \in \{1,\dots,R\}
\]

La igualdad está permitida en la izquierda y no en la derecha, según la descripción del input.

El patrón completo tiene:

\[
L + 1 + R = 7 \text{ barras}
\]

La pivot bar no se conoce como pivot hasta el cierre de:

\[
t = p + R
\]

En este caso:

```text
dos barras después.
```

---

## 24) Pivot high

Es el espejo:

\[
High_p \ge High_{p-i}
\quad
\forall i \in \{1,\dots,L\}
\]

\[
High_p > High_{p+j}
\quad
\forall j \in \{1,\dots,R\}
\]

La fórmula exacta de igualdad debe reconciliarse con la función TradeStation.

---

## 25) Repainting visual frente a causalidad

El ShowMe marca el punto en la pivot bar `p`.

Pero la información sólo existe en `p+R`.

Si se mira el gráfico retrospectivo puede parecer que la señal estaba disponible en el mínimo o máximo.

No lo estaba.

TSIS debe guardar:

```text
pivot_bar_timestamp = p
confirmation_timestamp = p + R
```

y utilizar como decision timestamp:

```text
confirmation_timestamp
```

Nunca la pivot bar.

---

## 26) Setup y precio de entrada

### 26.1 Setup long

Una pivot low se confirma al cerrar la última right-strength bar.

Nivel de entrada:

\[
LongEntryStop =
\max
\left(
High_p,
High_{p+1},
\dots,
High_{p+R}
\right)
+
PenetrationTicks \times TickSize
\]

Con `R=2`:

```text
máximo high de:
pivot bar
right bar 1
right bar 2
+
1 tick
```

### 26.2 Setup short

\[
ShortEntryStop =
\min
\left(
Low_p,
Low_{p+1},
\dots,
Low_{p+R}
\right)
-
1 \times TickSize
\]

---

## 27) Orden pendiente y cancelación

La orden permanece activa hasta:

```text
A. fill;
o
B. confirmación de un nuevo pivot high;
o
C. confirmación de un nuevo pivot low.
```

Por tanto, la estrategia requiere un estado pendiente:

```text
setup_id
setup_direction
pivot_price
confirmation_time
entry_stop
order_active
cancel_reason
```

No es una señal de una barra que se reevalúa de forma independiente.

---

## 28) Conflicto entre fill y nuevo pivot

Puede ocurrir que en la misma barra o subbarra:

```text
se toque el entry stop;
y se complete un nuevo pivot;
```

Queda por resolver qué ocurre primero:

```text
fill antes de cancel;
cancel antes de fill;
orden de evaluación de TradeStation;
timestamp de confirmación al cierre.
```

Una implementación causal razonable sería:

```text
la confirmación del nuevo pivot sólo existe al cierre de la barra;
un stop tocado intrabar antes del cierre puede llenarse;
la cancelación aplica después del cierre.
```

Pero debe reconciliarse con TradeStation.

---

## 29) Stop estructural

### Long

\[
LongProtectiveStop =
PivotLowPrice
-
PenetrationTicks \times TickSize
\]

### Short

\[
ShortProtectiveStop =
PivotHighPrice
+
PenetrationTicks \times TickSize
\]

El riesgo monetario no es constante.

Depende de:

```text
distancia entre breakout entry y pivot;
volatilidad;
forma del patrón;
strength;
precio.
```

Con tamaño fijo de 100 acciones, cada setup tiene distinto riesgo.

---

## 30) Exit por closes adversos

### Long

Salir cuando se acumulan:

```text
4 cierres consecutivos inferiores al cierre anterior
```

mientras la posición está long.

### Short

Salir tras:

```text
4 cierres consecutivos superiores
```

mientras está short.

La revista indica que el conteo incluye la barra de entrada.

### Ambigüedades

Debe fijarse:

```text
si la entry bar puede contar como 1;
contra qué cierre se compara la entry bar;
si una igualdad reinicia el contador;
si una barra favorable resetea a 0;
si la salida se ejecuta next bar market;
si stop estructural y count exit coinciden.
```

Reconstrucción probable:

```python
if long:
    lower_close_count = (
        lower_close_count + 1
        if close[t] < close[t - 1]
        else 0
    )

if short:
    higher_close_count = (
        higher_close_count + 1
        if close[t] > close[t - 1]
        else 0
    )
```

Cuando el contador llega a 4:

```text
exit next bar at market
```

---

## 31) Qué estrategia es realmente

No compra directamente el pivot low.

Tampoco vende directamente el pivot high.

Hace:

```text
pivot low confirmado
→ espera ruptura alcista del máximo del patrón
→ long

pivot high confirmado
→ espera ruptura bajista del mínimo del patrón
→ short
```

Es una estrategia de:

> patrón de giro confirmado + continuación en la dirección esperada.

El pivot es setup.

La ruptura es trigger.

El pivot opuesto o nuevo pivot cancela el setup.

El pivot price y los closes adversos gestionan la posición.

---

## 32) Comparación con componentes TradeStation

El artículo distingue:

### Pivot Extension

```text
entra a mercado después de completar el pivot;
opera en la dirección implícita del patrón.
```

### Pivot Reversal

```text
entra por stop más allá del pivot opuesto;
opera cuando el patrón es negado.
```

### Pivot Breakout del artículo

```text
espera ruptura del máximo/mínimo
del pivot bar y right-strength bars;
opera la confirmación del giro.
```

Esta comparación genera una ablación natural:

```text
pattern completion
vs
price confirmation
vs
pattern invalidation.
```

---

## 33) Intrabar y LIBBT

El test usa:

```text
65m bars
LIBBT 5m
```

En una subbarra de 5 minutos pueden ocurrir:

```text
entry stop;
protective stop;
nuevo high/low;
salida por count en el cierre;
reversal futuro;
gap.
```

Si entrada y stop se tocan en la misma subbarra, OHLC 5m no determina el orden.

La réplica debe usar:

```text
1m;
trades;
quotes;
o política conservadora.
```

---

## 34) Resultados publicados

### 34.1 Agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $7,336.00 |
| Beneficio bruto | $49,174.00 |
| Pérdida bruta | -$41,838.00 |
| Profit Factor | 1.18 |
| Operaciones | 865 |
| Ganadoras | 333 |
| Perdedoras | 530 |
| Even | 2 |
| Percent Profitable | 38.50% |
| Expectativa media | $8.48 |
| Ganancia media | $147.67 |
| Pérdida media | -$78.94 |
| Ratio ganancia/pérdida | 1.87 |
| Mayor ganancia | $1,398.00 |
| Mayor pérdida | -$349.00 |
| Máx. ganadoras consecutivas | 6 |
| Máx. perdedoras consecutivas | 13 |
| Barras medias ganadoras | 13.60 |
| Barras medias perdedoras | 5.66 |
| Barras medias even | 10.00 |

### 34.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Beneficio neto | $6,448.00 | $888.00 |
| Profit Factor | 1.32 | 1.04 |
| Operaciones | 425 | 440 |
| Percent Profitable | 44.94% | 32.27% |
| Expectativa media | $15.17 | $2.02 |
| Ganancia media | $138.41 | $160.12 |
| Pérdida media | -$85.79 | -$73.57 |
| Ratio ganancia/pérdida | 1.61 | 2.18 |
| Mayor ganancia | $804.00 | $1,398.00 |
| Mayor pérdida | -$349.00 | -$324.00 |
| Máx. ganadoras consecutivas | 9 | 5 |
| Máx. perdedoras consecutivas | 8 | 11 |
| Barras medias ganadoras | 14.52 | 12.37 |
| Barras medias perdedoras | 5.83 | 5.53 |

### 34.3 Concentración long

\[
6,448 / 7,336
\approx 87.90\%
\]

Casi el 88% del beneficio procede de longs.

La rama short produce:

```text
$888 en 440 trades
$2.02 por trade
PF 1.04
```

Económicamente es casi nula.

---

## 35) Fragilidad frente a costes

Con 100 acciones fijas:

### Agregado

\[
8.48 / 100 =
\$0.0848
\]

por acción y round trip.

Un coste adicional de:

```text
8.48 centavos por acción round trip
4.24 centavos por acción y lado
```

elimina la expectativa agregada.

### Short

\[
2.02 / 100 =
\$0.0202
\]

Sólo:

```text
2.02 centavos por acción round trip
1.01 centavos por acción y lado
```

eliminarían toda la rama short.

Por tanto:

```text
SHORT_BRANCH:
ECONOMICALLY_UNSUPPORTED_UNDER_REALISTIC_EXECUTION_STRESS
```

La rama long tiene más margen:

```text
15.17 centavos por acción round trip
```

pero sigue necesitando slippage y spread históricos.

---

## 36) Curva de capital

La curva no es lineal.

Muestra:

```text
pérdidas iniciales cercanas a -$2,000;
salto de rendimiento alrededor del trade 170;
ascenso posterior;
meseta prolongada;
drawdown desde aproximadamente $5,000 a $3,000;
recuperación abrupta al final.
```

El resultado final depende de bloques específicos.

Debe analizarse por:

```text
año;
régimen;
volatilidad;
long/short;
tipo de pivot;
strength;
distancia al stop;
session segment.
```

---

## 37) ¿Dónde podría estar el edge?

Hipótesis:

> Un pivot confirmado identifica un giro potencial y la ruptura posterior del extremo del patrón filtra los pivots que carecen de continuación.

El edge podría proceder de:

```text
rechazo de precio;
acumulación/distribución local;
ruptura de microestructura;
stop clustering;
continuación tras confirmación;
salida rápida cuando falla el pivot.
```

Hipótesis alternativas:

```text
beta long del SPY;
confirmación seleccionada;
pivots demasiado frecuentes;
bar partition artifact;
costes omitidos;
final-period winners;
intrabar fill optimism.
```

---

## 38) Auditoría científica

### 38.1 Un solo activo

Sólo SPY.

### 38.2 Periodo bull

Favorece longs.

### 38.3 Sin OOS

No existe holdout.

### 38.4 Expectativa baja

Especialmente short.

### 38.5 LIBBT insuficiente

No resuelve todos los paths.

### 38.6 Repainting visual

Puede inducir a un análisis manual retrospectivo erróneo.

### 38.7 Inputs no optimizados en el artículo

El artículo no presenta una superficie ni afirma optimización específica de `4/2/4/4/1`, lo que reduce pero no elimina selection risk.

Los valores pueden proceder de defaults o trabajo previo.

### 38.8 Bar alignment

65 minutos produce seis barras regulares por día.

Cambiar la hora inicial modifica los pivots.

### 38.9 Corporate actions

SPY requiere precio ajustado para patrón y raw para ejecución.

### 38.10 Igualdades

La definición izquierda/derecha no es simétrica.

### 38.11 Setup cancellation

La prioridad es parte del resultado.

### 38.12 Fixed shares

El riesgo varía por patrón.

### 38.13 Short mechanics

No se modelan dividendos, borrow ni restricciones.

### 38.14 No qualification of pivots

Todos los pivots reciben igual trato, aunque varíen en:

```text
prominence;
volumen;
distancia;
volatilidad;
contexto;
edad de tendencia.
```

---

## 39) Contrato TSIS

### Datos

```text
SPY 65m canonical bars
SPY 5m, 1m o trades
quotes
corporate actions
session calendar
tick size
```

### Estado de setup

```text
pivot_id
pivot_type
pivot_bar_timestamp
confirmation_timestamp
left_strength
right_strength
pivot_price
pattern_extreme
entry_stop
pending_order
pending_since
cancelled_by_pivot_id
```

### Estado de posición

```text
entry_setup_id
entry_price
protective_stop
lower_close_count
higher_close_count
bars_held
exit_reason
```

### Estados de indisponibilidad

```text
INSUFFICIENT_LEFT_HISTORY
RIGHT_STRENGTH_NOT_COMPLETE
SESSION_ALIGNMENT_UNRESOLVED
INTRABAR_SEQUENCE_AMBIGUOUS
PENDING_ORDER_PRIORITY_UNRESOLVED
TICK_SIZE_UNRESOLVED
MISSING_NEXT_BAR
CORPORATE_ACTION_UNRESOLVED
```

---

## 40) Pseudocódigo funcional

```python
def confirmed_pivot_low(p, left=4, right=2):
    return (
        all(low[p] <= low[p - i] for i in range(1, left + 1))
        and
        all(low[p] < low[p + j] for j in range(1, right + 1))
    )

def confirmed_pivot_high(p, left=4, right=2):
    return (
        all(high[p] >= high[p - i] for i in range(1, left + 1))
        and
        all(high[p] > high[p + j] for j in range(1, right + 1))
    )

on pivot_low_confirmation at t = p + 2:
    cancel_all_pending_pivot_orders()
    entry_stop = max(high[p:t + 1]) + tick
    protective_stop = low[p] - tick
    submit_pending_long_stop(entry_stop)

on pivot_high_confirmation at t = p + 2:
    cancel_all_pending_pivot_orders()
    entry_stop = min(low[p:t + 1]) - tick
    protective_stop = high[p] + tick
    submit_pending_short_stop(entry_stop)

if long:
    if price <= protective_stop:
        exit_stop()
    elif close[t] < close[t - 1]:
        lower_close_count += 1
    else:
        lower_close_count = 0

    if lower_close_count >= 4:
        schedule_exit(next_bar_market)

if short:
    if price >= protective_stop:
        exit_stop()
    elif close[t] > close[t - 1]:
        higher_close_count += 1
    else:
        higher_close_count = 0

    if higher_close_count >= 4:
        schedule_exit(next_bar_market)
```

Este pseudocódigo es una reconstrucción. Debe reconciliarse contra TradeStation.

---

## 41) Eventos candidatos para Event State

```text
event_type:
pivot_low_confirmed

decision_timestamp:
close of right-strength completion bar

attributes:
pivot_timestamp
pivot_price
left_strength
right_strength
pattern_width
prominence
entry_stop
distance_entry_to_stop
```

```text
event_type:
pivot_high_confirmed
```

```text
event_type:
pivot_breakout_triggered
```

```text
event_type:
pivot_setup_cancelled
```

```text
event_type:
adverse_close_count_reached
```

Outcomes:

```text
fill probability
MFE
MAE
stop hit
holding period
return by prominence
return by volatility regime
```

---

## 42) Plan de réplica y falsificación

### Fase 1 — Reproducción histórica

Checksums:

```text
865 trades
425 long
440 short
net ≈ $7,336
PF ≈ 1.18
```

### Fase 2 — Pivot semantics

Comparar:

```text
left equality allowed;
right equality disallowed;
strict both sides;
TradeStation native pivot function.
```

### Fase 3 — Causal timestamp

Demostrar que la señal no se genera en la pivot bar.

### Fase 4 — Order lifecycle

Reconciliar:

```text
new pivot cancels pending order;
fill and cancel same bar;
same-direction new pivot;
opposite-direction new pivot;
order expiration.
```

### Fase 5 — Intrabar

```text
5m
1m
trades
worst-case same-bar fill
```

### Fase 6 — Ablaciones

| Variante | Pregunta |
|---|---|
| Pivot Extension | ¿esperar ruptura mejora? |
| Pivot Breakout | regla publicada |
| Pivot Reversal | ¿la negación funciona mejor? |
| sin closes exit | ¿el contador aporta valor? |
| time exit | ¿la salida depende de path? |
| ATR risk sizing | ¿fixed shares distorsiona? |
| long-only | ¿short debe eliminarse? |

### Fase 7 — Pivot quality

Preregistrar features:

```text
prominence normalizada por ATR;
volumen;
distancia al pivot anterior;
trend regime;
location vs VWAP/SMA;
right-side recovery strength.
```

No optimizarlas sobre el mismo test.

### Fase 8 — Cross-sectional

```text
SPY
QQQ
IWM
DIA
sector ETFs
liquid large caps
```

### Fase 9 — Postpublicación

Desde diciembre de 2015 en adelante con inputs congelados.

### Fase 10 — Costes

Especialmente:

```text
short branch;
stop entry slippage;
gap through protective stop;
spread at breakout.
```

---

## 43) Decisión — Pivot Breakout

```text
IMPLEMENTAR:
sí, como benchmark de Event State y órdenes pendientes

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
pivot causality
+
setup confirmation
+
pending-order cancellation
+
intrabar execution

PRIORIDAD DE INVESTIGACIÓN:
media

PRIORIDAD DE ENGINE VALIDATION:
muy alta

SIGUIENTE GATE:
SCC-025-PIVOT-CAUSALITY-ORDER-LIFECYCLE-AND-COST-GATE
```

---

# Parte III — Williams E-mini Influx repetido

## 44) Estado

El PDF vuelve a incluir el artículo bonus y el ZIP vuelve a incluir sus archivos.

Los binarios coinciden exactamente con los ya auditados:

```text
ELD SHA-256:
94ff62ae6fe0fc470f14104010f18104a40dd749b49c4b4cb9487ff60655ee6d

TSW SHA-256:
0fa90f393a55e66c96dbe1e17aabea354f623f42af20ad2a5da981d1f8977117
```

Decisión:

```text
NO_NEW_STRATEGY_ID
NO_DUPLICATE_AUDIT
REFERENCE:
SCC-2015-10-STRAT-021
```

Los hallazgos anteriores permanecen:

```text
next-open limit causality unresolved;
same-close profitable exit causality unresolved;
80% win rate with adverse payoff;
physical-futures replay required.
```

---

# Parte IV — Ideas transversales del Issue 12

## 45) La serie secundaria es parte de la estrategia

Market Breadth Gauge no puede definirse sólo con QQQ.

El contrato incluye:

```text
Data2 identity
formula
universe
timestamp
availability
revision policy
```

---

## 46) Normalizar no resuelve automáticamente escalado

Un z-score rolling hace la serie comparable localmente, pero introduce:

```text
window length;
sample definition;
outlier sensitivity;
warm-up;
regime dependence;
self-inclusion.
```

---

## 47) Un cruce contiene más información que un nivel

Market Breadth Gauge opera:

```text
dirección de transición
+
nivel
```

No basta con guardar `MBG=-0.4`.

Hay que guardar:

```text
valor previo;
dirección;
overshoot;
duración bajo/encima del threshold.
```

---

## 48) El pivot gráfico no es una señal point-in-time

El punto dibujado en retrospectiva debe separarse del timestamp de confirmación.

---

## 49) Un pending order es un objeto de estado

Pivot Breakout exige:

```text
crear;
mantener;
llenar;
cancelar;
reemplazar;
vincular al setup.
```

---

## 50) La cancelación puede cambiar más que la entrada

Un nuevo pivot cancela cualquier setup pendiente.

Por tanto, la frecuencia depende de:

```text
densidad de pivots;
right strength;
volatilidad;
bar interval.
```

---

## 51) La rama short puede ser estadísticamente o económicamente irrelevante

Market Breadth:

```text
26 shorts
```

Pivot Breakout:

```text
440 shorts
pero sólo $2.02 por trade
```

Son dos problemas diferentes:

```text
muestra insuficiente;
expectativa insuficiente.
```

---

## 52) Pairwise sensitivity no sustituye validación

Una superficie estable es evidencia descriptiva favorable, no OOS.

---

## 53) Regiones con Fast > Slow cambian la hipótesis

No deben mezclarse en la misma interpretación científica.

---

## 54) El bull market afecta ambos artículos

Los dos tests favorecen notablemente el lado long.

---

## 55) El coste debe expresarse por unidad ejecutada

Pivot Breakout parece positivo en dólares, pero el short sólo tolera aproximadamente:

```text
1.01 centavos por acción y lado adicionales.
```

---

## 56) Ideas secundarias de backtesting

1. Pair Data1 y Data2 mediante timestamps, no sólo fechas.
2. Mantener una réplica nativa y otra reconstruida.
3. Versionar el universo de breadth.
4. Tratar la normalización como una feature con contrato.
5. Separar pivot timestamp y confirmation timestamp.
6. Persistir pending orders en Event State.
7. Registrar cancel reason.
8. Usar replay fino para entry stops.
9. Medir ramas long y short por separado.
10. Aplicar baselines de beta.
11. Excluir regiones paramétricas que cambian la clase de modelo.
12. No aceptar un PF alto con 26 trades.
13. No aceptar una rama con PF 1.04 aunque tenga 440 trades.
14. Analizar expectativa después de costes por acción.
15. Conservar los grids de optimización en futuros experimentos.

---

# Parte V — Registro consolidado para TSIS

## 57) Objetos de información afectados

### Market Breadth Gauge

Principalmente:

```text
broad_market_context
trading_activity
order_flow_pressure
price_movement
```

### Pivot Breakout

Principalmente:

```text
price_movement
volatility_range_state
price_location_intraday
market_microstructure_state
```

---

## 58) Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Pivot Breakout order lifecycle | prueba directa de pending/cancel/fill/stop |
| 2 | Market Breadth Data2 reconstruction | requisito para reproducibilidad científica |
| 3 | Market Breadth postpublication long-only | rama con más evidencia |
| 4 | Pivot long-only OOS | short tiene expectativa casi nula |
| 5 | Breadth cross attribution | comprobar información incremental frente a QQQ |

---

## 59) Gates propuestos

### SCC-024-A — Provider Data2 Contract

Debe fijar:

```text
source;
symbol;
universe;
timestamp;
revisions;
availability.
```

### SCC-024-B — Normalization Formula

Debe resolver:

```text
EMA;
rolling mean;
rolling std;
inclusive/lagged;
warm-up.
```

### SCC-024-C — Breadth Reconstruction

Debe comparar proveedor y TSIS PIT.

### SCC-024-D — Exit Semantics

Debe resolver prior-two-bars.

### SCC-024-E — Beta Attribution

Debe comparar contra baselines long.

### SCC-024-F — Postpublication OOS

Inputs congelados.

### SCC-025-A — Pivot Formula

Debe reconciliar igualdad y strength.

### SCC-025-B — Confirmation Timestamp

Debe demostrar no-look-ahead.

### SCC-025-C — Pending Order Lifecycle

Debe resolver creación, cancelación y fill.

### SCC-025-D — Intrabar Arbitration

Debe resolver entry/stop en same subbar.

### SCC-025-E — Consecutive Close Counter

Debe fijar el conteo desde entry bar.

### SCC-025-F — Cost Survival

Debe mostrar long y short netos de costes.

### SCC-025-G — Postpublication OOS

Inputs congelados.

---

# Conclusión

El Issue 12 cierra el primer año de la revista con dos estrategias nuevas y un artículo bonus repetido.

## Market Breadth Gauge

La estrategia es:

```text
value-based Nasdaq 100 breadth
→ EMA5 - EMA30
→ normalización rolling de 20
→ long al recuperar -0.5
→ short al caer desde +2
→ salida por extremo de 2 barras
→ stop de $400
```

El resultado publicado es atractivo:

```text
164 trades
PF 2.21
$8,939.47
drawdown semanal aproximado 5%
```

pero:

```text
la serie Data2 es propietaria;
la fórmula exacta no está visible;
el periodo es alcista;
76.54% del beneficio es long;
sólo existen 26 shorts;
no hay OOS.
```

Es un candidato importante para TSIS por su valor arquitectónico en **Broad Market Context**, pero no una estrategia validada.

## Pivot Breakout

La estrategia es:

```text
pivot 4-left / 2-right
→ confirmación causal dos barras después
→ stop entry tras el extremo del patrón
→ pending order hasta fill o nuevo pivot
→ stop estructural en pivot
→ exit tras 4 closes adversos
```

Publica:

```text
865 trades
PF 1.18
$7,336
```

pero:

```text
87.90% del beneficio es long;
el agregado gana sólo $8.48 por trade;
el short gana $2.02 por trade;
LIBBT de 5m no resuelve todos los paths;
la curva depende de bloques concretos.
```

Su mayor valor es validar:

```text
Event State;
confirmation timestamps;
pending orders;
cancelación;
intrabar replay.
```

## Estado final

```text
ISSUE_12_STATUS:
DOCUMENTALLY_CLOSED

PACKAGE_INSPECTION:
COMPLETE_WITH_PROPRIETARY_CODE_LIMITATION

NEW_STRATEGIES_EXTRACTED:
2

DUPLICATE_STRATEGIES:
1

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```

Siguientes gates recomendados:

```text
1. SCC-025-PIVOT-CAUSALITY-ORDER-LIFECYCLE-AND-COST-GATE
2. SCC-024-BREADTH-FORMULA-DATA2-AND-OOS-GATE
```
