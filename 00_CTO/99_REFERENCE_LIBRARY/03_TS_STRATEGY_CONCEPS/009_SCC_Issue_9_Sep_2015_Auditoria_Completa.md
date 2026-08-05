# Auditoría completa — TradeStation Strategy Concepts Club, Issue 9 (septiembre de 2015)

## 0. Alcance del artefacto

Este es el **único archivo Markdown de la revista completa**. Integra:

```text
1. 2+1 Moving Average Strategy
2. Adaptive VIX Bands Strategy
3. ideas secundarias de investigación y backtesting presentes en el número
4. reconstrucción matemática y temporal
5. auditoría de los resultados publicados
6. inspección forense de los archivos .ELD y workspaces .tsw
7. contratos de réplica para TSIS
8. planes de falsificación, ablación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 15 páginas: `SCC Issue 9 Sept 2015.pdf`.
- Archivo de apoyo: `2015-09.zip`.
- PDF duplicado incluido dentro del ZIP.
- Texto extraído incluido dentro del ZIP.
- Dos contenedores propietarios `.ELD`:
  - `TSL 2+1 MOVING AVERAGE.ELD`;
  - `TSL ADAPTIVE VIX BANDS.ELD`.
- Dos workspaces OLE/Compound Document `.tsw`:
  - `TSL.2+1 Moving Average.tsw`;
  - `TSL Adaptive VIX Bands.tsw`.
- Las imágenes y tablas renderizadas de las 15 páginas, incluidas:
  - las reglas y ejemplos gráficos de la estrategia 2+1;
  - los dos informes de rendimiento con sizing fijo y capital constante;
  - la curva de capital de 2+1;
  - la construcción visual de las Adaptive VIX Bands;
  - el ejemplo de entrada y salida de Adaptive VIX Bands;
  - su informe completo de rendimiento;
  - la superficie de sensibilidad `Trail_Stop_Length × Min_Long_Hold`;
  - el gráfico de beneficio medio por mes.
- Los Markdown de los Issues 1–8 se utilizan solamente como modelo de profundidad y organización, no como autoridad factual para este número.

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

Cuando la revista o el paquete no resuelven una decisión, se registra como ambigüedad. No se completa silenciosamente.

No se ha incorporado investigación web externa. Las fórmulas que no aparecen literalmente en el artículo se presentan como reconstrucciones funcionales que deben reconciliarse mediante réplica.

### Inventario forense del paquete

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `SCC Issue 9 Sept 2015.pdf` | 4,358,725 bytes | `5483215ac8fe4dded894da82170935048ae880790fcf4d7a92083ade7cb23b23` |
| `2015-09.zip` | 4,394,727 bytes | `51cb1ea4eb8e68af19c02ff54384458318f1bc1123888dcdbcaefae96d53baa2` |
| `SCC Issue 9 Sept 2015.txt` | 58,802 bytes | `084156e94ebd4536e293add07ccf796e8b932b896ebea4d4adae757df8fb9de7` |
| `TSL 2+1 MOVING AVERAGE.ELD` | 9,702 bytes | `947ccbc04481fce85a31b8457eb845cbc77cc4a842d207f651b8d150f3204000` |
| `TSL.2+1 Moving Average.tsw` | 19,968 bytes | `f027910d990f78b9e079d6967367b4459e087351cca8cba25b21d85629ce1a71` |
| `TSL ADAPTIVE VIX BANDS.ELD` | 19,611 bytes | `805105f4f1d5e7703daa2205ab1110d442fcd6698048f9924b2e0597afac346a` |
| `TSL Adaptive VIX Bands.tsw` | 65,536 bytes | `707825c9e69795243acd9136d51717f749796ced7dd3dd84c77f84a87385aa90` |

El PDF incluido dentro del ZIP es binariamente idéntico al PDF cargado por separado.

El ZIP contiene además pequeños streams `Zone.Identifier` añadidos por el sistema de archivos. No forman parte del contenido científico ni de la lógica de las estrategias.

Los `.ELD` son contenedores propietarios TradeStation. Contienen marcadores de formato y versión —incluido `TSELXF`—, pero no exponen el código EasyLanguage como texto legible. Por tanto:

```text
se puede confirmar la existencia de las técnicas;
no se puede auditar el código línea por línea;
no se puede certificar la semántica exacta de determinadas funciones;
no se puede resolver por inspección textual la prioridad exacta de órdenes.
```

Los dos workspaces son contenedores OLE válidos. Ambos contienen un stream `optdatafile`, pero su tamaño es **cero bytes**.

```text
no se conserva el grid de optimización;
no se conservan rankings completos;
no se conserva el número total de configuraciones ejecutadas;
no puede comprobarse el puesto exacto de los parámetros publicados;
no puede calcularse directamente la magnitud de la selección in-sample.
```

### Evidencia adicional del workspace 2+1 Moving Average

El workspace confirma:

```text
Serie:
IWM Daily [ARCX]
iShares Russell 2000 ETF

Técnicas aplicadas:
Mov Avg 3 Lines
TSL:2+1 Moving Average

Inputs activos del indicador:
Price = Close
FastLength = 10
MedLength = 50
SlowLength = 200
Displace = 0

Inputs activos de la estrategia:
Price = Close
FastLength = 10
MedLength = 50
SlowLength = 200
```

Los valores binarios del workspace son compatibles con:

```text
comisión = $0.01 por acción;
sizing base = 100 acciones;
capital inicial de informe = $100,000.
```

La identificación de los inputs de estrategia e indicador es directa. La interpretación de todos los campos de propiedades de backtest se considera corroborativa, porque el formato interno del workspace no está documentado públicamente en el paquete.

### Evidencia adicional del workspace Adaptive VIX Bands

El workspace confirma:

```text
Data1:
@ES=107XN Daily [CME]
E-mini S&P 500 Custom Continuous Contract

Data2:
$VIX.X Daily [CBOE]
CBOE Volatility Index

Técnicas aplicadas:
TSL:Adaptive VIX Bands Strategy
TSL:Adaptive VIX Bands Indicator

Inputs activos de la estrategia:
GSD_Num = 2
Sample_Size = 20
Trail_Stop_Length = 2
Min_Long_Hold = 5
Min_Short_Hold = 5

Inputs activos del indicador:
GSD_Num = 2
Sample_Size = 20
Wide_Band_Color = Cyan
Narrow_Band_Color = Darkblue
Base_Vol_Color = White
```

Los valores binarios del workspace son compatibles con los ajustes publicados:

```text
capital inicial = $20,000;
comisión = $2.36 por lado;
tamaño = 1 contrato.
```

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo real | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 017 | 2+1 Moving Average | Crossover 10/50 condicionado por régimen precio/SMA200, con salida en crossover contrario | IWM diario; aprox. 10 años efectivos; 32 trades; PF 2.51 con 100 acciones; PF 3.05 con $20,000 por operación | workspace confirma `Close/10/50/200`, pero no conserva optimización; la mejora del segundo test procede de sizing variable, no de nuevas señales | buen baseline de trend following y laboratorio de sizing; edge no demostrado por muestra pequeña |
| 018 | Adaptive VIX Bands | Contrarian de extremos relativos de log-VIX con bandas dinámicas y salida posterior a mínimo holding | ES diario + VIX; 10 años; $63,043.56; PF 2.51; 102 trades; 54.90% ganadoras; 31.66% en mercado | workspace confirma `2/20/2/5/5`; `optdatafile` vacío; los dos parámetros mostrados en sensibilidad son exactamente valores pico | candidato prioritario para réplica postpublicación, pero con riesgo de selección, ambigüedad de salida y concentración long |

## 0.1 Veredicto global

El Issue 9 contiene dos lecciones especialmente valiosas para TSIS:

1. **La calidad de la señal debe separarse del sizing.**
2. **Un umbral adaptativo también es una serie temporal con estado y debe respetar point-in-time.**

La primera estrategia produce exactamente las mismas 32 señales bajo dos políticas de tamaño. La segunda usa una serie informativa externa —VIX— y umbrales que cambian cada día.

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

# Parte I — Estrategia 017: 2+1 Moving Average

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-09-STRAT-017`
- **Artículo:** *2+1 Moving Average Strategy*
- **Autor:** Stanley Dash, CMT
- **Páginas físicas del PDF:** 4–8
- **Páginas impresas del artículo:** 2–6
- **Estilo declarado:** trend-following
- **Mercados declarados:** equities, futures, forex
- **Horizonte declarado:** position trading
- **Activo del test:** iShares Russell 2000 ETF
- **Símbolo:** `IWM`
- **Bar interval:** diario
- **Histórico cargado:** 11 años terminando el 30 de junio de 2015
- **Histórico efectivo:** aproximadamente 10 años después de `MaxBarsBack = 200`
- **Primera entrada indicada:** 27 de mayo de 2005
- **Comisión:** $0.01 por acción
- **Slippage publicado:** no indicado
- **Stops integrados:** ninguno
- **Inputs:** `Close / 10 / 50 / 200`

### Inputs confirmados por workspace

| Input | Valor | Función |
|---|---:|---|
| `Price` | Close | fuente para las tres medias y comparación de régimen |
| `FastLength` | 10 | media rápida |
| `MedLength` | 50 | media intermedia |
| `SlowLength` | 200 | filtro de tendencia |

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí, fácilmente.** |
| ¿Puede replicarse aproximadamente? | **Sí.** El workspace confirma activo, intervalo e inputs. |
| ¿Puede replicarse exactamente? | **Casi.** Debe reconciliarse la convención exacta de `crosses over/under`, redondeo del sizing y ejecución en la apertura. |
| ¿El artículo demuestra edge? | **No.** Sólo hay 32 operaciones y ninguna validación fuera de muestra. |
| ¿Los parámetros fueron optimizados en este artículo? | **No se afirma que se optimicen aquí.** Se usan valores por defecto 10/50/200, pero su origen histórico no queda preregistrado. |
| ¿El segundo backtest mejora la señal? | **No.** Mantiene las mismas señales y sólo cambia el tamaño. |
| ¿La tesis es plausible? | **Sí.** Crossover intermedio a favor de un régimen lento es una forma simple de trend following condicionado. |
| ¿Está lista para operar? | **No.** Falta OOS, costes realistas, stops, borrow para shorts y análisis de robustez. |

Clasificación TSIS:

```text
SOURCE_REPRODUCTION_CANDIDATE
TREND_FILTER_BASELINE
POSITION_SIZING_LAB
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

No es una estrategia tradicional de tres medias en la que se exige:

```text
precio > media rápida > media media > media lenta
```

para comprar, ni la alineación inversa para vender.

La lógica real separa:

```text
setup / régimen:
posición del precio respecto de la media lenta

trigger:
crossover entre media rápida y media intermedia

exit:
crossover contrario entre media rápida e intermedia
```

Por tanto, puede interpretarse como:

> una estrategia de crossover 10/50 filtrada por la relación del precio con la SMA200.

La nomenclatura `2+1` es descriptiva:

```text
2 medias:
producen trigger y salida

+1 media:
define el régimen en el que el trigger es admisible
```

El filtro no exige que las medias 10 y 50 estén en el mismo lado de la SMA200. La figura 2 muestra precisamente un long en el que ambas medias rápidas están por debajo de la SMA200, pero el cierre ya está por encima de ella.

---

## 3. Reconstrucción matemática

Sea `C_t` el cierre diario de IWM.

### 3.1 Medias simples

$$
F_t = SMA_{10}(C)_t
$$

$$
M_t = SMA_{50}(C)_t
$$

$$
S_t = SMA_{200}(C)_t
$$

donde:

```text
F = fast
M = medium
S = slow
```

### 3.2 Régimen

$$
bull\_regime_t = C_t > S_t
$$

$$
bear\_regime_t = C_t < S_t
$$

El artículo no define una acción específica para igualdad exacta. La réplica debe registrar una de estas convenciones:

```text
A. igualdad = sin régimen
B. igualdad conserva el régimen anterior
C. igualdad se asigna a bull o bear
```

La interpretación más conservadora es:

```text
C_t == S_t -> no nueva entrada
```

### 3.3 Crossover

Long trigger:

$$
F_{t-1} \le M_{t-1}
\quad\land\quad
F_t > M_t
$$

Short trigger:

$$
F_{t-1} \ge M_{t-1}
\quad\land\quad
F_t < M_t
$$

Las variantes estrictas en la barra anterior deben reconciliarse con la semántica de EasyLanguage:

```text
crosses over
crosses under
```

### 3.4 Señales

$$
long\_signal_t =
(C_t > S_t)
\land
cross\_up(F,M)_t
$$

$$
short\_signal_t =
(C_t < S_t)
\land
cross\_down(F,M)_t
$$

### 3.5 Salidas

Una posición long sale cuando:

$$
cross\_down(F,M)_t
$$

Una posición short sale cuando:

$$
cross\_up(F,M)_t
$$

La relación entre precio y SMA200 **no es necesaria para salir**.

Si el crossover opuesto también satisface el régimen opuesto, la salida puede transformarse en reversión completa:

```text
long -> flat -> short
short -> flat -> long
```

todo en la apertura siguiente.

---

## 4. Arquitectura temporal

### 4.1 Decision timestamp

La decisión se forma al cierre de la sesión `t`:

```text
C_t
SMA10_t
SMA50_t
SMA200_t
crossover_t
regime_t
```

### 4.2 Ejecución

La orden se ejecuta en la apertura de `t+1`.

```text
close t:
señal conocida

open t+1:
entrada, salida o reversal
```

### 4.3 Regla point-in-time

Todas las medias deben usar únicamente cierres disponibles hasta `t`.

No puede emplearse:

```text
open t+1 en la señal;
precio ajustado con información futura;
componentes actuales de IWM para reconstruir su pasado;
datos de cierre revisados sin control de versión.
```

### 4.4 Corporate actions

Para señales sobre un ETF deben usarse precios con continuidad económica. TSIS debe mantener separado:

```text
signal_price_view:
adjusted o total-return coherent

execution_price_view:
raw tradable open
```

La réplica del artículo deberá comprobar qué vista histórica usó TradeStation.

---

## 5. Reglas funcionales

### 5.1 Entrada long

```text
if Close_t > SMA200_t
and SMA10_t crosses above SMA50_t:
    buy at open_t+1
```

### 5.2 Entrada short

```text
if Close_t < SMA200_t
and SMA10_t crosses below SMA50_t:
    sell_short at open_t+1
```

### 5.3 Salida long

```text
if long
and SMA10_t crosses below SMA50_t:
    sell at open_t+1
```

### 5.4 Salida short

```text
if short
and SMA10_t crosses above SMA50_t:
    buy_to_cover at open_t+1
```

### 5.5 Reversal

```text
if long
and cross_down
and Close_t < SMA200_t:
    exit long and establish short at open_t+1

if short
and cross_up
and Close_t > SMA200_t:
    exit short and establish long at open_t+1
```

El artículo no documenta si TradeStation registra el reversal como una o dos operaciones económicas. La tabla de trades deberá utilizarse como checksum.

---

## 6. Dos experimentos que no deben confundirse

La revista presenta dos backtests con señales idénticas.

### Experimento A — tamaño fijo

```text
100 acciones en cada operación
```

### Experimento B — capital constante

```text
$20,000 por operación
redondeado hacia abajo al múltiplo de 20 acciones
mínimo 50 acciones
sin compounding
```

No se modifica:

```text
regla de entrada;
regla de salida;
timestamps;
número de señales;
dirección;
holding period.
```

Por tanto:

> el segundo experimento no demuestra mayor edge de la estrategia; demuestra un resultado diferente bajo otra función de exposición.

---

## 7. Auditoría del sizing de capital constante

Una reconstrucción funcional sería:

$$
raw\_qty_t = \frac{20{,}000}{P_t}
$$

$$
qty_t =
\max\left(
50,
20\left\lfloor\frac{raw\_qty_t}{20}\right\rfloor
\right)
$$

Queda por reconciliar qué precio usa TradeStation para calcular el tamaño:

```text
cierre de la barra de señal;
apertura estimada;
precio actual de la orden;
precio de ejecución.
```

Esa decisión puede cambiar el tamaño cuando hay gaps.

### 7.1 Tamaño observado

El informe de capital constante muestra:

```text
máximo = 440 acciones
mínimo declarado = 50 acciones
total acumulado = 7,880 acciones
número de trades = 32
```

Tamaño medio:

$$
7880 / 32 = 246.25
$$

Es aproximadamente `2.4625×` el tamaño fijo de 100 acciones.

### 7.2 Beneficio observado

$$
16{,}884.20 / 5{,}617.00 \approx 3.006
$$

El beneficio fue aproximadamente `3.01×`.

Si todo escalara linealmente con el tamaño medio:

$$
5{,}617 \times 2.4625 \approx 13{,}832
$$

El resultado real fue unos $3,052 superior a esa aproximación.

Esto no implica alpha de sizing. Significa que:

```text
los tamaños mayores coincidieron con trades históricamente más rentables;
los tamaños menores coincidieron con otras zonas de la muestra;
los costes por acción y la secuencia temporal alteraron la proporcionalidad.
```

Para saber si existe valor en el sizing hace falta comparar contra políticas de exposición equivalentes fuera de muestra.

---

## 8. Resultados publicados — tamaño fijo de 100 acciones

### 8.1 Informe agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $5,617.00 |
| Beneficio bruto | $9,333.00 |
| Pérdida bruta | -$3,716.00 |
| Profit Factor | 2.51 |
| Operaciones | 32 |
| Ganadoras | 16 |
| Perdedoras | 16 |
| Percent Profitable | 50.00% |
| Expectativa media | $175.53 |
| Ganancia media | $583.31 |
| Pérdida media | -$232.25 |
| Ratio ganancia/pérdida | 2.51 |
| Mayor ganancia | $2,116.00 |
| Mayor pérdida | -$795.00 |
| Máx. ganadoras consecutivas | 6 |
| Máx. perdedoras consecutivas | 5 |
| Barras medias ganadoras | 72.75 |
| Barras medias perdedoras | 32.31 |
| Exposición temporal | 64.16% |
| Máximo tamaño | 100 acciones |
| Acciones acumuladas | 3,200 |

### 8.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Operaciones | 24 | 8 |
| Beneficio neto | $2,856.00 | $2,761.00 |
| Profit Factor | 1.98 | 4.47 |
| Ganadoras | 12 | 4 |
| Perdedoras | 12 | 4 |
| Ganancia media | $481.42 | $889.00 |
| Pérdida media | -$243.42 | -$198.75 |
| Ratio ganancia/pérdida | 1.98 | 4.47 |
| Barras medias ganadoras | 74.08 | 68.75 |
| Barras medias perdedoras | 33.17 | 29.75 |

El lado short parece extraordinario por Profit Factor, pero sólo contiene:

```text
8 trades;
4 ganadores;
4 perdedores.
```

No es una muestra suficiente para concluir que el short es superior.

### 8.3 Interpretación correcta

Los ganadores duran más del doble que los perdedores:

$$
72.75 / 32.31 \approx 2.25
$$

Esto es coherente con trend following:

```text
cortar movimientos que no progresan;
mantener tendencias persistentes.
```

Pero 32 operaciones en aproximadamente 10 años significa:

```text
≈ 3.2 trades por año
```

La precisión estadística es muy limitada.

---

## 9. Resultados publicados — capital constante de $20,000

### 9.1 Informe agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $16,884.20 |
| Beneficio bruto | $25,110.80 |
| Pérdida bruta | -$8,226.60 |
| Profit Factor | 3.05 |
| Operaciones | 32 |
| Ganadoras | 16 |
| Perdedoras | 16 |
| Percent Profitable | 50.00% |
| Expectativa media | $527.63 |
| Ganancia media | $1,569.42 |
| Pérdida media | -$514.16 |
| Ratio ganancia/pérdida | 3.05 |
| Mayor ganancia | $5,924.80 |
| Mayor pérdida | -$1,749.00 |
| Máximo tamaño | 440 acciones |
| Acciones acumuladas | 7,880 |

### 9.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Operaciones | 24 | 8 |
| Beneficio neto | $8,941.40 | $7,942.80 |
| Profit Factor | 2.38 | 5.59 |
| Expectativa media | $372.56 | $992.85 |
| Mayor ganancia | $4,599.00 | $5,924.80 |
| Mayor pérdida | -$1,749.00 | -$780.00 |
| Máximo tamaño | 360 | 440 |
| Acciones acumuladas | 5,680 | 2,200 |

### 9.3 Qué sí demuestra

Demuestra que, dentro de esta secuencia histórica:

```text
una política de capital constante
produjo mayor beneficio absoluto;
el PF aumentó;
la exposición nominal varió con el precio de IWM.
```

### 9.4 Qué no demuestra

No demuestra:

```text
que las señales sean mejores;
que el sizing tenga edge fuera de muestra;
que la mejora sobreviva a otro orden temporal de trades;
que el riesgo haya mejorado;
que el drawdown por unidad de capital haya descendido;
que $20,000 sea un tamaño adecuado.
```

El informe condensado no publica una comparación completa de drawdown, volatilidad o capital requerido entre ambos sizing policies.

---

## 10. ¿Dónde podría estar el edge?

La hipótesis puede dividirse en dos componentes.

### 10.1 Edge de dirección

> Un crossover 10/50 tiene mayor probabilidad de continuidad cuando el cierre está en el mismo lado de una SMA200 que la dirección del crossover.

Esto equivale a condicionar momentum intermedio por régimen lento.

### 10.2 Edge de salida

> El crossover contrario permite permanecer en tendencias rentables más tiempo de lo que se permanece en operaciones perdedoras.

La tabla de duración es compatible con esta hipótesis, pero no la demuestra causalmente.

### 10.3 Hipótesis alternativas

El beneficio podría proceder de:

```text
beta long de IWM;
periodo favorable para trend following;
ocho shorts excepcionalmente afortunados;
parámetros 10/50/200 conocidos y seleccionados históricamente;
tratamiento de dividendos;
precio ajustado;
ejecución ideal en open;
ausencia de slippage;
concentración de beneficio en pocas operaciones.
```

---

## 11. Auditoría científica

### 11.1 Sólo 32 operaciones

Es el problema dominante.

Con 16 ganadoras y 16 perdedoras:

```text
la tasa de acierto observada es exactamente 50%;
pequeñas variaciones cambian mucho el PF;
las colas no están estimadas;
el drawdown futuro es altamente incierto.
```

### 11.2 Ocho shorts

El PF short de 4.47 o 5.59 no debe interpretarse como evidencia robusta.

### 11.3 Único instrumento

No se publican resultados sobre:

```text
SPY;
QQQ;
otros ETFs;
futuros;
acciones;
forex.
```

### 11.4 Sin out-of-sample

No existe:

```text
train/test;
walk-forward;
purged validation;
bootstrap;
postpublication holdout;
```

### 11.5 Parámetros familiares no equivalen a preregistro

`10/50/200` son combinaciones convencionales. Eso reduce la apariencia de una búsqueda exótica, pero no prueba que se eligieran antes de observar IWM.

### 11.6 Sin stops

La estrategia sólo sale por crossover contrario. Puede sufrir:

```text
gaps;
eventos de cola;
periodos largos contra la posición;
pérdidas mayores antes de que se forme el crossover.
```

### 11.7 Short friction

El backtest no documenta:

```text
borrow;
recall;
dividendos pagados en short;
restricciones regulatorias;
spread;
market impact.
```

En IWM estas fricciones son manejables, pero no nulas.

### 11.8 Sesgo por sizing temporal

En el segundo test, el tamaño depende del nivel de precio. Eso hace que distintas épocas tengan diferente peso en el PnL.

La mejora puede ser una interacción histórica accidental entre:

```text
precio de IWM;
dirección de la señal;
rentabilidad posterior;
régimen macro.
```

### 11.9 No hay comparación causal con una estrategia 2-line

Para demostrar que la SMA200 aporta información debe compararse:

```text
crossover 10/50 sin filtro
versus
crossover 10/50 con filtro 200
```

manteniendo todo lo demás idéntico.

### 11.10 No hay comparación completa con 3-line tradicional

El artículo lo propone como trabajo futuro, pero no publica la ablación.

---

## 12. Contrato de implementación en TSIS

### 12.1 Datos necesarios

```text
IWM daily adjusted signal view
IWM daily raw open execution view
corporate actions
dividend events
short availability assumptions
session calendar
```

### 12.2 Campos de estado

```text
symbol
session_date
decision_timestamp
close_signal_view
sma_fast_10
sma_medium_50
sma_slow_200
bull_regime
bear_regime
cross_up_10_50
cross_down_10_50
position_before
signal_type
scheduled_action
execution_session
execution_open_raw
sizing_policy
target_notional
raw_quantity
rounded_quantity
```

### 12.3 Estados de indisponibilidad

```text
INSUFFICIENT_HISTORY
MISSING_SIGNAL_CLOSE
MISSING_EXECUTION_OPEN
CORPORATE_ACTION_UNRESOLVED
NO_SHORT_ASSUMPTION
ROUNDING_POLICY_UNRESOLVED
```

### 12.4 Pseudocódigo de señal

```python
fast = sma(adjusted_close, 10)
medium = sma(adjusted_close, 50)
slow = sma(adjusted_close, 200)

cross_up = fast[t - 1] <= medium[t - 1] and fast[t] > medium[t]
cross_down = fast[t - 1] >= medium[t - 1] and fast[t] < medium[t]

bull = adjusted_close[t] > slow[t]
bear = adjusted_close[t] < slow[t]

if position == 0:
    if bull and cross_up:
        schedule_buy(next_open)
    elif bear and cross_down:
        schedule_short(next_open)

elif position > 0:
    if cross_down:
        if bear:
            schedule_reverse_to_short(next_open)
        else:
            schedule_exit_long(next_open)

elif position < 0:
    if cross_up:
        if bull:
            schedule_reverse_to_long(next_open)
        else:
            schedule_exit_short(next_open)
```

### 12.5 Pseudocódigo de sizing

```python
def fixed_shares() -> int:
    return 100

def constant_notional(reference_price: float) -> int:
    raw = 20_000.0 / reference_price
    rounded = int(raw // 20) * 20
    return max(50, rounded)
```

`reference_price` debe quedar contractualmente fijado antes de la réplica.

---

## 13. Plan para demostrar o destruir el edge

### Fase 1 — Réplica histórica

```text
IWM
inputs 10/50/200
periodo publicado
100 acciones
$0.01 por acción
```

Checksums:

```text
32 trades;
24 long;
8 short;
16 ganadores;
16 perdedores;
primera entrada 27/05/2005;
PF aproximado 2.51;
beneficio aproximado $5,617.
```

### Fase 2 — Reconciliación de sizing

Reproducir:

```text
$20,000 por trade;
round down a 20;
mínimo 50;
32 trades;
7,880 acciones acumuladas;
máximo 440;
beneficio aproximado $16,884.20.
```

### Fase 3 — Ablación del filtro SMA200

| Variante | Pregunta |
|---|---|
| 10/50 sin SMA200 | ¿La tercera media añade información? |
| 10/50 + SMA200 | regla publicada |
| 10/50 + régimen de retorno | ¿SMA200 es especial? |
| 10/50 + régimen de mercado SPY | ¿el régimen propio de IWM es necesario? |

### Fase 4 — Comparación 3-line

Comparar con una regla preregistrada de alineación completa:

```text
Close > SMA10 > SMA50 > SMA200
Close < SMA10 < SMA50 < SMA200
```

### Fase 5 — Cross-sectional test

Aplicar la especificación congelada a:

```text
SPY
QQQ
DIA
IWM
EFA
EEM
sector ETFs
```

sin cambiar parámetros.

### Fase 6 — Postpublicación

Publicación: septiembre de 2015.

Test congelado:

```text
desde la primera sesión posterior a publicación
hasta la última sesión completa disponible en TSIS.
```

### Fase 7 — Robustez local

No buscar el mejor punto. Examinar mesetas:

```text
FastLength: 5–20
MedLength: 30–100
SlowLength: 150–300
```

### Fase 8 — Sizing causal

Comparar todas las políticas con igual presupuesto de riesgo:

```text
100 shares
constant notional
volatility targeting
equal risk per trade
buy-and-hold matched exposure
```

### Fase 9 — Costes

```text
open ideal
open + half spread
open + full spread
slippage por bps
borrow y dividendos short
```

---

## 14. Encaje en Market State y Event State

### Market State

```text
price_above_sma200
price_below_sma200
sma10_minus_sma50
sma10_50_cross_direction
trend_regime_age
distance_to_sma200
volatility_state
```

### Event State

```text
event_type:
moving_average_cross_in_slow_regime

subject_scope:
single_security

decision_timestamp:
daily_close_t

attributes:
cross_direction
slow_regime
distance_fast_medium
distance_price_slow
bars_since_prior_cross
```

### Outcomes

```text
next_open_execution
trade_return
holding_period
MFE
MAE
time_to_opposite_cross
return_vs_unfiltered_baseline
return_vs_buy_and_hold
```

---

## 15. Decisión técnica — 2+1 Moving Average

```text
IMPLEMENTAR:
sí, como baseline sencillo y auditable

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
separar régimen, trigger, salida y sizing

OPTIMIZAR:
no antes del OOS congelado

OPERAR:
no

PRIORIDAD:
media
```

Gate propuesto:

```text
SCC-017-REPLICATION-ABLATION-AND-SIZING-GATE
```

---

# Parte II — Estrategia 018: Adaptive VIX Bands

## 16) Identificación y alcance

- **ID de estrategia:** `SCC-2015-09-STRAT-018`
- **Artículo:** *Adaptive VIX Bands*
- **Autor:** Frederic Palmliden, CFA, CMT
- **Páginas físicas del PDF:** 10–15
- **Páginas impresas del artículo:** 8–13
- **Estilo declarado:** volatility based
- **Mercados declarados:** stock-index futures and ETFs
- **Horizonte declarado:** swing trading
- **Activo operado:** E-mini S&P 500
- **Data1:** `@ES=107XN`
- **Serie informativa:** `$VIX.X`
- **Bar interval:** diario
- **Periodo:** 10 años terminando el 30 de junio de 2015
- **Capital inicial:** $20,000
- **Tamaño:** 1 contrato
- **Comisión:** $2.36 por lado y contrato
- **Stop monetario:** no publicado
- **Slippage:** no publicado

### Inputs confirmados por workspace

| Input | Valor | Función |
|---|---:|---|
| `GSD_Num` | 2 | múltiplo de dispersión para ambas bandas |
| `Sample_Size` | 20 | ventana de media y dispersión de log-VIX |
| `Trail_Stop_Length` | 2 | lookback de salida por extremos de precio |
| `Min_Long_Hold` | 5 | mínimo de barras long |
| `Min_Short_Hold` | 5 | mínimo de barras short |

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí.** Requiere sincronización ES/VIX y estado rolling. |
| ¿Puede replicarse aproximadamente? | **Sí.** El workspace confirma series e inputs. |
| ¿Puede replicarse exactamente? | **No todavía.** Falta certificar fórmula exacta de dispersión y semántica de la salida de 2 barras. |
| ¿Demuestra edge? | **No.** Parámetros parcialmente optimizados, un solo mercado y sin OOS. |
| ¿La tesis económica es plausible? | **Sí.** Extremos relativos del VIX pueden actuar como señal contraria. |
| ¿Las bandas son verdaderamente adaptativas? | **Sí.** Su anchura cambia con la dispersión rolling de log-VIX. |
| ¿Los parámetros publicados son conservadores? | **No del todo.** `2/5` son valores pico en la superficie mostrada. |
| ¿Está lista para operar? | **No.** Falta réplica, costes, contratos físicos, OOS y control de cola. |
| ¿Merece estudiarse? | **Sí, con prioridad alta.** |

Clasificación TSIS:

```text
MULTI_DATA_SOURCE_REPRODUCTION_CANDIDATE
VOLATILITY_EXTREME_EVENT
ADAPTIVE_THRESHOLD_STATE_MACHINE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 17. Qué estrategia es realmente

Es una estrategia contraria sobre el VIX, pero no opera el VIX.

```text
serie señal:
VIX cash index

activo operado:
ES futures

entrada long:
VIX relativamente alto frente a su historia reciente

entrada short:
VIX relativamente bajo frente a su historia reciente
```

A diferencia de Normalized VIX del Issue 8:

```text
no usa umbrales fijos ±1.5;
no usa SMA20/SMA200 de ES como filtro;
no mantiene sólo una barra;
las bandas cambian cada día;
las posiciones se mantienen al menos cinco barras.
```

La lógica es:

```text
transformación logarítmica
→ recentrado rolling
→ bandas rolling
→ cruce extremo
→ entrada contraria
→ mínimo holding
→ salida por ruptura de extremo de precio
```

---

## 18. Reconstrucción matemática

Sea:

$$
V_t = VIX_t
$$

### 18.1 Transformación logarítmica

$$
X_t = \ln(V_t)
$$

Requiere:

$$
V_t > 0
$$

### 18.2 Media rolling

Con `n = 20`:

$$
\mu_t = \frac{1}{n}\sum_{i=0}^{n-1} X_{t-i}
$$

### 18.3 Lectura de volatilidad

$$
A_t = X_t - \mu_t
$$

Equivalentemente:

$$
A_t = \ln\left(\frac{V_t}{GM_t}\right)
$$

donde:

$$
GM_t = \exp(\mu_t)
$$

Por tanto, `A_t` es un log-ratio del VIX actual respecto de la media geométrica rolling.

Interpretación:

```text
A_t > 0:
VIX por encima de su nivel geométrico reciente

A_t < 0:
VIX por debajo
```

### 18.4 Dispersión rolling

La reconstrucción más probable es:

$$
\sigma_t = SD(X_{t-n+1:t})
$$

La revista la denomina “geometric standard deviation”, pero las bandas se muestran centradas en cero y con valores aproximadamente ±0.3.

En estadística, la desviación geométrica convencional suele expresarse como:

$$
GSD = \exp(\sigma)
$$

que es un factor multiplicativo mayor o igual que 1. Eso no coincide con las bandas positivas y negativas del gráfico.

Por tanto, la interpretación funcional más probable es:

> desviación estándar de los logaritmos, no el factor `exp(sigma)`.

Debe confirmarse por réplica.

### 18.5 Bandas

Con `k = 2`:

$$
Upper_t = +k\sigma_t
$$

$$
Lower_t = -k\sigma_t
$$

### 18.6 Entradas por cruce

Long:

$$
A_{t-1} \le Upper_{t-1}
\quad\land\quad
A_t > Upper_t
$$

Short:

$$
A_{t-1} \ge Lower_{t-1}
\quad\land\quad
A_t < Lower_t
$$

El cruce puede producirse por:

```text
movimiento de A_t;
contracción o expansión de la banda;
ambas cosas.
```

Ésta es una diferencia semántica importante respecto de un umbral fijo.

---

## 19. ¿Qué significa “95% dentro de las bandas”?

El artículo indica que dos desviaciones abarcan aproximadamente el 95% de las lecturas.

Eso sólo es aproximadamente cierto si:

```text
los log-residuos son razonablemente normales;
la media y dispersión son estables localmente;
la observación actual no distorsiona demasiado el estimador;
no hay colas pesadas ni autocorrelación relevante.
```

Además:

```text
las bandas usan una ventana rolling pequeña de 20 días;
la estimación de sigma es ruidosa;
el VIX presenta clustering de volatilidad;
la probabilidad empírica no tiene por qué ser 5%.
```

TSIS debe medir la tasa de excedencia real, no asumirla.

---

## 20. Auto-inclusión de la observación actual

Queda sin resolver si `X_t` participa en:

```text
mu_t
sigma_t
```

antes de evaluar el cruce de `A_t`.

Si se incluye:

```text
un VIX extremo mueve la media;
ensancha sigma;
reduce su propia extremidad medida.
```

Si se excluye:

```text
la banda representa sólo la información hasta t-1;
el extremo se compara contra una referencia preexistente.
```

Ambas implementaciones son point-in-time, pero producen señales distintas.

La réplica debe registrar dos variantes:

```text
INCLUSIVE_ROLLING_WINDOW
LAGGED_REFERENCE_WINDOW
```

y reconciliarlas contra las fechas del informe original.

---

## 21. Arquitectura temporal ES/VIX

### 21.1 Serie de señal

El VIX cash se forma durante la sesión de opciones de EE.UU. y su cierre es conocido antes de la apertura nocturna de ES.

### 21.2 Decision timestamp

La señal debe considerarse disponible después del cierre oficial del VIX de la sesión `t`.

### 21.3 Ejecución

El artículo señala que las entradas y salidas en ES ocurren a las **6 p.m. ET**, apertura de la siguiente sesión diaria del contrato.

```text
VIX close t:
señal calculable

ES open siguiente sesión, 18:00 ET:
entrada o salida
```

### 21.4 Riesgo de calendario

`$VIX.X` y ES no comparten exactamente:

```text
horario;
duración de sesión;
feriados parciales;
timestamps;
definición de session_date.
```

La unión debe ser explícita.

### 21.5 Regla point-in-time

Nunca debe asociarse a una apertura de ES:

```text
un VIX publicado después de esa apertura;
una revisión posterior;
una fecha unida sólo por etiqueta sin considerar horario.
```

---

## 22. Estado y reglas de entrada

### 22.1 Entrada long

```text
if AdaptiveVIX crosses above UpperBand:
    buy ES at next daily-session open
```

Interpretación contraria:

```text
miedo extremo relativo
→ expectativa de rebote en el índice
```

### 22.2 Entrada short

```text
if AdaptiveVIX crosses below LowerBand:
    sell short ES at next daily-session open
```

Interpretación contraria:

```text
complacencia extrema relativa
→ expectativa de caída del índice
```

### 22.3 Posición ya abierta

El artículo no especifica en detalle:

```text
si se ignoran señales del mismo lado;
si una señal opuesta revierte;
si se bloquean entradas hasta salida;
cómo se prioriza señal nueva frente a salida.
```

La curva y el conteo sugieren una única posición, pero el contrato de réplica debe confirmarlo.

---

## 23. Salida tras mínimo holding

### 23.1 Regla publicada long

Después de al menos cinco barras:

```text
si el low está por debajo del lowest low de las últimas 2 barras:
    salir long en la apertura siguiente
```

### 23.2 Regla publicada short

Después de al menos cinco barras:

```text
si el high está por encima del highest high de las últimas 2 barras:
    salir short en la apertura siguiente
```

### 23.3 Ambigüedad crítica de auto-inclusión

Si una función `Lowest(Low, 2)` incluye el low actual:

$$
Low_t < Lowest(Low,2)_t
$$

es imposible, porque el mínimo incluye `Low_t`.

Por tanto, la implementación debe ser alguna variante como:

$$
Low_t < Lowest(Low,2)_{t-1}
$$

o:

```text
low actual rompe el mínimo de las dos barras anteriores
```

Para short:

$$
High_t > Highest(High,2)_{t-1}
$$

También podría usarse igualdad y detección de nuevo extremo:

```text
Low_t = Lowest(Low, 2)
High_t = Highest(High, 2)
```

El `.ELD` no permite resolverlo. Éste es uno de los gates principales.

### 23.4 Conteo del mínimo holding

Queda por fijar:

```text
si la barra de entrada cuenta como barra 1;
si BarsSinceEntry > 5 o >= 5;
si la salida puede señalarse en la quinta barra;
si se ejecuta en la sexta o séptima apertura.
```

---

## 24. Pseudocódigo funcional

```python
log_vix = np.log(vix_close)

mean_log = rolling_mean(log_vix, 20)
std_log = rolling_std(log_vix, 20)

adaptive_vix = log_vix - mean_log
upper = 2.0 * std_log
lower = -2.0 * std_log

cross_high = adaptive_vix[t - 1] <= upper[t - 1] and adaptive_vix[t] > upper[t]
cross_low = adaptive_vix[t - 1] >= lower[t - 1] and adaptive_vix[t] < lower[t]

if position == 0:
    if cross_high:
        schedule_long(es_next_session_open)
    elif cross_low:
        schedule_short(es_next_session_open)

elif position > 0:
    if bars_held >= 5:
        prior_low = min(es_low[t - 2], es_low[t - 1])
        if es_low[t] < prior_low:
            schedule_exit_long(es_next_session_open)

elif position < 0:
    if bars_held >= 5:
        prior_high = max(es_high[t - 2], es_high[t - 1])
        if es_high[t] > prior_high:
            schedule_exit_short(es_next_session_open)
```

Este pseudocódigo es una reconstrucción, no una transcripción del `.ELD`.

---

## 25. Resultados publicados

### 25.1 Informe agregado

| Métrica | Resultado |
|---|---:|
| Beneficio neto | $63,043.56 |
| Beneficio bruto | $104,910.68 |
| Pérdida bruta | -$41,867.12 |
| Profit Factor | 2.51 |
| Operaciones | 102 |
| Ganadoras | 56 |
| Perdedoras | 46 |
| Percent Profitable | 54.90% |
| Expectativa media | $618.07 |
| Ganancia media | $1,873.40 |
| Pérdida media | -$910.15 |
| Ratio ganancia/pérdida | 2.06 |
| Mayor ganancia | $7,832.78 |
| Mayor pérdida | -$3,217.22 |
| Máx. ganadoras consecutivas | 7 |
| Máx. perdedoras consecutivas | 6 |
| Barras medias ganadoras | 10.07 |
| Barras medias perdedoras | 6.80 |
| Return on Initial Capital | 315.22% |
| Annual Rate of Return | 14.81% |
| RINA Index | 149.17 |
| Percent of Time in Market | 31.66% |
| Drawdown semanal aproximado | 19% |

### 25.2 Long frente a short

| Métrica | Long | Short |
|---|---:|---:|
| Operaciones | 67 | 35 |
| Beneficio neto | $53,021.26 | $10,022.30 |
| Profit Factor | 2.74 | 1.87 |
| Percent Profitable | 61.19% | 42.86% |
| Expectativa media | $791.36 | $286.35 |
| Ganancia media | $2,034.91 | $1,431.95 |
| Pérdida media | -$1,169.62 | -$572.85 |
| Ratio ganancia/pérdida | 1.74 | 2.50 |
| Mayor ganancia | $6,107.78 | $7,832.78 |
| Mayor pérdida | -$3,217.22 | -$1,867.22 |
| Barras medias ganadoras | 10.54 | 8.80 |
| Barras medias perdedoras | 6.42 | 7.30 |

### 25.3 Concentración long

$$
53{,}021.26 / 63{,}043.56 \approx 84.10\%
$$

El 84.1% del beneficio neto procede de long trades.

Esto es coherente con la conocida asimetría del VIX, pero plantea una pregunta:

> ¿La rama short añade alpha o sólo añade complejidad, volatilidad y exposición?

### 25.4 Resultado short

El lado short:

```text
PF = 1.87
win rate = 42.86%
35 trades
expectativa = $286.35
```

Es positivo in-sample, pero la muestra es pequeña y mucho más débil que el long.

### 25.5 Duración

Los ganadores duran más que los perdedores:

$$
10.07 / 6.80 \approx 1.48
$$

Esto es favorable y diferente de una estrategia de alta tasa de acierto con pérdidas largas.

### 25.6 Curva de capital

La curva es ascendente, pero muestra una meseta extensa aproximadamente entre 2010 y 2012.

Esto implica:

```text
riesgo de régimen;
posible degradación temporal;
necesidad de paciencia;
peligro de abandonar justo antes de una recuperación;
ausencia de estabilidad uniforme.
```

---

## 26. Sensibilidad y selección

La revista muestra una superficie:

```text
Trail_Stop_Length
×
Min_Long_Hold
```

y afirma que:

```text
Trail_Stop_Length = 2
Min_Long_Hold = 5
```

son valores pico.

Aunque el entorno visual parece razonablemente favorable, esto es una advertencia metodológica:

```text
los parámetros publicados no son simplemente un punto interior;
coinciden con el máximo observado de esa superficie;
la selección se hizo sobre la misma muestra reportada.
```

Además, no se muestra:

```text
Min_Short_Hold;
GSD_Num;
Sample_Size;
interacciones de entrada y salida;
número total de combinaciones;
ranking del punto publicado;
múltiples grids probados.
```

El workspace no conserva `OptimizationData`.

---

## 27. Seasonality: agosto negativo

La figura 6 muestra beneficio medio negativo en agosto y positivo en los demás meses.

No debe convertirse inmediatamente en una regla “apagar en verano”.

Problemas:

```text
sólo 10 años;
12 categorías mensuales;
descubrimiento post-hoc;
trades multi-día que atraviesan meses;
no se especifica si el PnL se agrupa por entrada, salida o periodo;
no hay OOS;
posible concentración de pocos trades.
```

Una regla estacional añadida después de mirar el gráfico constituye una nueva hipótesis y requiere un test independiente.

---

## 28. ¿Dónde podría estar el edge?

### 28.1 Hipótesis principal

> Un VIX extremadamente alto o bajo respecto de su propia distribución logarítmica reciente contiene información contraria sobre el retorno posterior del S&P 500.

### 28.2 Beneficio de la adaptación

Frente a umbrales fijos:

```text
la referencia se ajusta al régimen reciente;
un VIX de 20 puede ser extremo o normal según el contexto;
la anchura responde a vol-of-vol.
```

### 28.3 Beneficio del cruce

La estrategia no entra por permanecer fuera de banda, sino por cruzarla.

Esto intenta identificar:

```text
inicio de un extremo;
no cada día consecutivo extremo.
```

### 28.4 Hipótesis alternativas

El resultado podría proceder de:

```text
equity risk premium long;
compra de caídas del ES;
sesgo long dominante;
selección de exits;
rolls del contrato continuo;
entradas a 6 p.m.;
periodo favorable;
pocos grandes ganadores;
parámetros seleccionados in-sample.
```

---

## 29. Auditoría científica

### 29.1 Sin OOS

No existe separación entrenamiento/prueba.

### 29.2 Parámetros parcialmente optimizados

El artículo lo reconoce explícitamente.

### 29.3 Parámetros pico

`Trail_Stop_Length=2` y `Min_Long_Hold=5` son el máximo mostrado.

### 29.4 Único instrumento

Sólo se publica ES.

La afirmación de que futuros funcionan mejor que SPY no viene acompañada de informes completos comparables.

### 29.5 Sólo 102 trades

Es una muestra moderada, pero insuficiente para:

```text
colas;
estabilidad por régimen;
seasonality;
submuestras;
short side;
drawdown extremo.
```

### 29.6 Sin slippage

La estrategia ejecuta en la apertura nocturna de ES, donde:

```text
liquidez y spread pueden variar;
hay gaps de sesión;
pueden existir eventos entre el VIX close y 6 p.m.;
un continuous contract no es operable.
```

### 29.7 Contrato continuo

La señal puede calcularse sobre una serie continua, pero la ejecución requiere:

```text
contrato físico vigente;
roll policy;
ajuste de PnL por rollover;
regla si una posición atraviesa roll;
precio real de ejecución.
```

### 29.8 Sin stop de cola

Una posición debe mantenerse al menos cinco barras.

Puede sufrir:

```text
shock de volatilidad;
gap;
movimiento persistente contra la tesis;
pérdida mayor antes de habilitarse la salida.
```

### 29.9 Data2 y sincronización

VIX no es un dato accesorio; es parte del contrato causal. Un join incorrecto introduce look-ahead.

### 29.10 Long bias

La rama long explica la mayor parte del beneficio. Debe compararse contra baselines de compra de caídas.

### 29.11 Bandas estimadas con 20 observaciones

La desviación rolling puede ser inestable y responder fuertemente a outliers.

### 29.12 Múltiples investigaciones VIX consecutivas

Issues 2, 8 y 9 exploran variantes del VIX. La selección entre familias también forma parte del multiple testing, aunque cada artículo parezca separado.

---

## 30. Contrato de implementación en TSIS

### 30.1 Datos necesarios

```text
VIX official daily OHLC or close
ES daily continuous signal reference
ES physical futures contracts
contract calendar
roll mapping
session calendar
commission schedule
tick size and multiplier
```

### 30.2 Separación de vistas

```text
signal/reference view:
VIX cash close
ES continuous analytical series

execution view:
front physical ES contract
raw session open
```

### 30.3 Campos de estado

```text
session_date
decision_timestamp
vix_close
log_vix
rolling_mean_log_vix
rolling_std_log_vix
adaptive_vix_value
upper_adaptive_band
lower_adaptive_band
cross_upper
cross_lower
band_width
band_width_percentile_100
position
bars_since_entry
min_hold_satisfied
prior_two_low
prior_two_high
exit_break_long
exit_break_short
physical_contract
next_session_open
```

### 30.4 Estados de indisponibilidad

```text
MISSING_VIX
VIX_NON_POSITIVE
INSUFFICIENT_LOG_HISTORY
MISSING_ES_REFERENCE
NO_PHYSICAL_CONTRACT_MAPPING
ROLL_AMBIGUITY
SESSION_ALIGNMENT_FAILURE
MISSING_NEXT_SESSION_OPEN
```

### 30.5 Pseudocódigo TSIS

```python
vix_t = vix_close[session_t]

if vix_t <= 0:
    unavailable("VIX_NON_POSITIVE")

x_t = log(vix_t)

# Variant A: inclusive window
mu_t = mean(log_vix[t-19:t+1])
sd_t = std(log_vix[t-19:t+1])

adaptive_t = x_t - mu_t
upper_t = 2.0 * sd_t
lower_t = -2.0 * sd_t

cross_upper = adaptive_prev <= upper_prev and adaptive_t > upper_t
cross_lower = adaptive_prev >= lower_prev and adaptive_t < lower_t

if flat:
    if cross_upper:
        schedule_long(next_es_session_open)
    elif cross_lower:
        schedule_short(next_es_session_open)

elif long and bars_held >= 5:
    if low_t < min(low_t_minus_1, low_t_minus_2):
        schedule_exit(next_es_session_open)

elif short and bars_held >= 5:
    if high_t > max(high_t_minus_1, high_t_minus_2):
        schedule_exit(next_es_session_open)
```

---

## 31. Plan para demostrar o destruir el edge

### Fase 1 — Réplica histórica

Checksums:

```text
102 trades
67 long
35 short
56 ganadoras
PF ≈ 2.51
net profit ≈ $63,043.56
exposición ≈ 31.66%
```

### Fase 2 — Reconciliación de fórmula

Comparar:

```text
population std vs sample std
inclusive vs lagged window
log standard deviation vs geometric factor
cross dinámico vs comparación estática
```

### Fase 3 — Reconciliación de salida

Comparar:

```text
current low < lowest prior 2
current low == lowest including current
Lowest(...)[1]
BarsSinceEntry >= 5
BarsSinceEntry > 5
```

### Fase 4 — Postpublicación congelada

Periodo:

```text
primera sesión posterior a septiembre de 2015
hasta última sesión completa disponible.
```

### Fase 5 — Baselines

| Baseline | Pregunta |
|---|---|
| Long-only AVB | ¿short añade valor? |
| Buy ES after high VIX percentile | ¿las bandas log añaden valor? |
| Buy ES after large negative ES return | ¿VIX aporta información incremental? |
| Fixed VIX threshold | ¿adaptación mejora? |
| Normalized VIX Issue 8 | ¿qué familia generaliza mejor? |
| Random dates matched by regime | ¿la selección temporal supera placebo? |

### Fase 6 — Ablación de exits

```text
holding fijo 1, 5, 10 días
salida por 2-bar price break
ATR stop/target
time exit
signal reversal
```

### Fase 7 — Long/short separados

Preregistrar dos hipótesis independientes.

### Fase 8 — Instrumentos

```text
ES physical
MES, si disponible en periodo moderno
SPY
SPX total-return proxy
NQ / QQQ con VXN
RTY / IWM con RVX
```

### Fase 9 — Costes y roll

```text
spread en 18:00
slippage 0.25, 0.5, 1 y 2 ticks
roll físico
posición atravesando roll
comisiones históricas
```

### Fase 10 — Seasonality

Sólo después de validar la estrategia base:

```text
monthly returns with confidence intervals
trade-count by month
block bootstrap
pre/post 2015
August rule tested out-of-sample
```

---

## 32. Encaje en Market State y Event State

### Market State

```text
vix_log_deviation_20
vix_log_std_20
adaptive_band_width
vix_position_within_bands
vol_of_vol_regime
bars_since_extreme
es_market_regime
```

### Event State

```text
event_type:
adaptive_vix_band_break

subject_scope:
broad_market_volatility

decision_timestamp:
VIX official close

attributes:
direction
adaptive_value
band_value
band_width
overshoot
window_type
days_since_previous_break
```

### Outcomes

```text
ES next-session open return
1d / 5d / 10d forward returns
MFE
MAE
time_to_price_break_exit
roll-adjusted PnL
long-vs-short asymmetry
```

---

## 33. Decisión técnica — Adaptive VIX Bands

```text
IMPLEMENTAR:
sí, como réplica multi-data prioritaria

ACEPTAR COMO EDGE:
no

VALOR PRINCIPAL:
extremos de volatilidad con umbrales adaptativos

OPTIMIZAR:
no antes de reconciliar fórmula y salida

OPERAR:
no

PRIORIDAD:
alta
```

Gate propuesto:

```text
SCC-018-FORMULA-EXIT-AND-POSTPUBLICATION-GATE
```

---

# Parte III — Ideas transversales del Issue 9

## 34. Separar señal de sizing

El Issue 9 ofrece un ejemplo directo:

```text
mismas 32 señales
+
dos políticas de sizing
=
dos perfiles de PnL
```

TSIS debe registrar por separado:

```text
signal_id
execution_id
sizing_policy_id
risk_policy_id
```

No debe atribuir a la señal una mejora causada por exposición.

---

## 35. Setup, trigger y exit son objetos distintos

2+1 demuestra:

```text
setup:
Close vs SMA200

trigger:
SMA10 cruza SMA50

exit:
cruce contrario
```

Esta separación evita estrategias monolíticas y facilita ablaciones.

---

## 36. Un umbral adaptativo tiene estado propio

Adaptive VIX Bands no usa una constante. Cada día cambia:

```text
media;
desviación;
banda superior;
banda inferior;
anchura.
```

La señal depende tanto del VIX como del estado de la referencia.

---

## 37. Un cruce puede ser causado por el umbral

Cuando la banda se contrae:

```text
A_t puede cruzar Upper_t
aunque A_t apenas cambie.
```

Por tanto, conviene descomponer el evento:

```text
move_component
band_component
combined_cross
```

---

## 38. Log-transform no garantiza normalidad

Tomar logaritmos:

```text
reduce asimetría;
convierte ratios en diferencias;
mejora escalado.
```

No garantiza:

```text
normalidad;
independencia;
homocedasticidad;
cobertura exacta del 95%.
```

---

## 39. Parámetros pico frente a mesetas

La superficie Adaptive VIX declara que `2/5` son pico.

La elección científica preferible es:

```text
un área estable
no el máximo puntual.
```

Cuando el máximo se publica, debe considerarse postselección.

---

## 40. Capital constante no es volatility targeting

El sizing de 2+1 mantiene notional aproximado constante, pero no riesgo constante.

```text
riesgo monetario:
depende de volatilidad y stop implícito

riesgo porcentual:
cambia con el mercado

drawdown:
no queda normalizado.
```

Para comparar correctamente debe incorporarse volatilidad o distancia de stop.

---

## 41. La serie secundaria pertenece al contrato de decisión

En Adaptive VIX:

```text
ES no puede generar la señal por sí solo.
```

El VIX debe tener:

```text
source lineage;
timestamp;
version;
availability;
quality state.
```

---

## 42. Seasonality es una hipótesis de segundo orden

El gráfico mensual no es confirmación. Es generación de hipótesis.

Debe evitarse:

```text
estrategia base
→ mirar 12 meses
→ eliminar el peor
→ reportar mejora como si fuera original.
```

---

## 43. Ideas secundarias de backtesting extraídas del número

1. Comparar primero la calidad de señales con tamaño fijo.
2. Introducir sizing sólo después.
3. Usar capital constante sin confundirlo con compounding.
4. Comparar estrategias simples con variantes tradicionales.
5. Medir información incremental de cada capa.
6. Transformar variables con escala cambiante.
7. Usar umbrales adaptativos cuando el régimen cambia.
8. Inspeccionar mesetas de sensibilidad, no sólo picos.
9. Analizar resultados long y short por separado.
10. No añadir filtros estacionales sin OOS.
11. Diferenciar instrumento de señal e instrumento operado.
12. Controlar sesión, roll y apertura real del futuro.

---

# Parte IV — Registro consolidado para TSIS

## 44. Candidatos de eventos

### Evento 017-A

```text
event_type:
fast_medium_cross_in_bull_regime

subject:
IWM

decision_timestamp:
daily_close

action_candidate:
long
```

### Evento 017-B

```text
event_type:
fast_medium_cross_in_bear_regime

action_candidate:
short
```

### Evento 017-C

```text
event_type:
opposite_cross_exit

subject_scope:
open_position
```

### Evento 018-A

```text
event_type:
adaptive_vix_upper_break

semantic:
relative volatility fear extreme

action_candidate:
long equity index
```

### Evento 018-B

```text
event_type:
adaptive_vix_lower_break

semantic:
relative volatility complacency extreme

action_candidate:
short equity index
```

### Evento 018-C

```text
event_type:
post_min_hold_price_break

semantic:
exit condition after mandatory holding window
```

---

## 45. Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Adaptive VIX Bands — fórmula y OOS | señal externa, tesis plausible y periodo postpublicación amplio |
| 2 | 2+1 — ablación de SMA200 | baseline simple para medir información incremental |
| 3 | Adaptive VIX long-only | 84% del beneficio procede de longs |
| 4 | 2+1 sizing lab | excelente caso para separar alpha y exposición |
| 5 | Adaptive VIX seasonality | sólo después de validar la base |

---

## 46. Gates propuestos

### Gate 017-1 — Signal Reproduction

Debe reconciliar:

```text
32 trades
24 long
8 short
```

### Gate 017-2 — Slow Filter Ablation

Debe demostrar si SMA200 añade información incremental.

### Gate 017-3 — Sizing Separation

Debe separar:

```text
signal return
position size
capital usage
risk
```

### Gate 017-4 — Postpublication OOS

Parámetros congelados `10/50/200`.

### Gate 018-1 — Log Formula Reconciliation

Debe resolver:

```text
inclusive vs lagged
sample vs population std
log SD vs geometric factor
```

### Gate 018-2 — Exit Semantics

Debe resolver:

```text
prior-two-bar break
current-inclusive Lowest/Highest
holding count
```

### Gate 018-3 — Data2 Timing

Debe demostrar que cada VIX value era conocido antes de la apertura ES usada.

### Gate 018-4 — Physical Futures Replay

Debe sustituir el continuo por contratos físicos.

### Gate 018-5 — Long/Short Attribution

Debe medir valor incremental short.

### Gate 018-6 — Postpublication OOS

Sin modificar `2/20/2/5/5`.

### Gate 018-7 — Seasonality Falsification

Sólo si la estrategia base supera OOS.

---

# Conclusión

El Issue 9 aporta dos ideas útiles, pero con niveles de evidencia muy distintos de una validación científica.

## 2+1 Moving Average

La estrategia es:

```text
crossover 10/50
+
filtro de régimen SMA200
+
salida por crossover opuesto
```

Su sencillez es una ventaja para réplica y ablación. Sin embargo:

```text
sólo hay 32 trades;
el lado short tiene 8;
no hay OOS;
no hay slippage;
no hay stops;
la mejora del segundo informe es sizing, no señal.
```

Decisión:

```text
IMPLEMENTAR COMO BASELINE:
sí

ACEPTAR EDGE:
no
```

## Adaptive VIX Bands

La estrategia es:

```text
log-VIX recentrado
+
bandas dinámicas ±2 sigma
+
cruce contrarian
+
mínimo holding de 5 barras
+
salida por ruptura de 2 barras
```

El resultado publicado es atractivo:

```text
$63,043.56
PF 2.51
102 trades
31.66% en mercado
```

pero:

```text
84.1% del beneficio es long;
los parámetros de salida publicados son valores pico;
la fórmula exacta no está certificada;
la salida tiene una ambigüedad de auto-inclusión;
no hay slippage;
no hay OOS;
no se conservan optimizaciones.
```

Decisión:

```text
IMPLEMENTAR COMO RÉPLICA PRIORITARIA:
sí

ACEPTAR EDGE:
no

SIGUIENTE GATE:
SCC-018-FORMULA-EXIT-AND-POSTPUBLICATION-GATE
```

## Estado final del número

```text
ISSUE_9_STATUS:
DOCUMENTALLY_CLOSED

PACKAGE_INSPECTION:
COMPLETE_WITH_PROPRIETARY_CODE_LIMITATION

STRATEGIES_EXTRACTED:
2

REPRODUCTION_CANDIDATES:
2

SCIENTIFICALLY_VALIDATED:
0

LIVE_ELIGIBLE:
0
```
