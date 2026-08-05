# Auditoría completa — TradeStation Strategy Concepts Club, Issue 7 (julio de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. Multi-Interval Trend Detrend Strategy
2. Parabolic Plus Strategy
3. ideas secundarias de investigación y backtesting presentes en el número
4. auditoría temporal, matemática y metodológica
5. inspección forense de los workspaces .tsw y contenedores .ELD
6. reconstrucciones funcionales y pseudocódigo
7. contratos de réplica para TSIS
8. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 14 páginas: `SCC Issue 7 Jul 2015.pdf`.
- Archivo de apoyo: `2015-07.zip`.
- PDF duplicado incluido dentro del ZIP.
- Dos contenedores propietarios `.ELD`:
  - `TSL MULTI-INTERVAL TREND DETREND.ELD`;
  - `TSL PARABOLIC PLUS.ELD`.
- Dos workspaces OLE/Compound Document `.tsw`:
  - `TSL.Multi-interval Trend Detrend.tsw`;
  - `TSL Parabolic Plus.tsw`.
- Las imágenes y tablas renderizadas de las 14 páginas, incluidas:
  - la alineación visual de IWM en barras de 26 y 78 minutos;
  - los parámetros activos y el informe de rendimiento de Multi-Interval Trend Detrend;
  - las cuatro variantes comparadas de Parabolic Plus;
  - la superficie de sensibilidad `AfStep × AfLimit`.
- Los Markdown de los Issues 1–6 se utilizan únicamente como **modelo de profundidad y organización**, no como autoridad factual para este número.

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

No se ha incorporado investigación web externa. Las fórmulas que no aparecen literalmente en el artículo se presentan como reconstrucciones funcionales o candidatos a reconciliar con una réplica.

### Inventario forense del paquete

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `SCC Issue 7 Jul 2015.pdf` | 4,792,925 bytes | `fcd11d6e98b49a9eb8c5d775d2f5a3971fcf056ff5ce951215ea3d3889bccce7` |
| `2015-07.zip` | 4,821,385 bytes | `dce4082cf25ab7c3f0f3c22bacb1fdf0abdd940eead11d9e9770b437ac4b70b3` |
| `TSL MULTI-INTERVAL TREND DETREND.ELD` | 23,520 bytes | `82c463e4cf75565f0d998a60662aca535b7ff395f2bf7d180d5f24630da4789d` |
| `TSL.Multi-interval Trend Detrend.tsw` | 32,256 bytes | `0613b7732046af052e28393d266812b14f6d602ecbfd2caf8dda4c6dbf988e98` |
| `TSL PARABOLIC PLUS.ELD` | 10,721 bytes | `b6caac6f08aaaf551250b6c4f12122e7832b5901a9ba4c0736bd5d27e0b1769b` |
| `TSL Parabolic Plus.tsw` | 65,536 bytes | `e939b81bbf9c73d1d478f236196229322898c1ddbe06a416fc914726be969f43` |

El PDF incluido dentro del ZIP es binariamente idéntico al PDF cargado por separado.

Los `.ELD` son contenedores propietarios. Exponen marcadores de versión, pero **no el source EasyLanguage como texto legible**. Los workspaces sí permiten recuperar símbolos, intervalos, técnicas aplicadas e inputs activos.

Ambos `.tsw` contienen un stream denominado `optdatafile`, pero su tamaño es **cero bytes**. Por tanto:

```text
no se conserva el grid de optimización;
no se conservan rankings completos;
no se conservan todas las combinaciones probadas;
no es posible medir directamente la magnitud real de la selección.
```

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo real | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 013 | Multi-Interval Trend Detrend | Filtro de tendencia en 78 minutos + entrada contrarian en 26 minutos + sizing amplificado + bracket ATR | IWM; 2013–mayo 2015; $6,211; PF 2.71; 93 trades; 83.87% ganadoras | el workspace confirma exactamente los inputs del test, pero no conserva optimizaciones; el 84.6% del beneficio procede del lado short y 58/93 trades usan tamaño doble | candidato arquitectónicamente valioso; edge no demostrado y resultado confundido por sizing y alta tasa de acierto inducida |
| 014 | Parabolic Plus | Parabolic SAR reversible con stop monetario y dos capas opcionales que alteran la máquina de estados | Gold 60 min; $181,623.50; PF 1.29; 1,405 trades; 98.72% en mercado | el workspace activo es la versión más simple: sin canal y sin filtro de volumen; no conserva la superficie de optimización | candidato de réplica, pero exige simulación intrabar, roll físico y costes realistas; la conclusión “simple > complejo” no queda probada fuera de muestra |

## 0.1 Veredicto global

El Issue 7 es importante para TSIS porque introduce dos conceptos de arquitectura que van más allá de las reglas concretas:

1. **Representación multi-intervalo point-in-time.** Una estrategia puede consumir un estado de fondo producido por una barra lenta y decisiones producidas por barras rápidas, siempre que se utilice únicamente la última barra lenta cerrada.
2. **Separación entre señal y exposición.** El “amplifier” no crea una señal nueva; modifica el tamaño de una señal existente. Debe evaluarse como política de sizing y no atribuirse automáticamente a mayor alpha.
3. **Ablación de capas opcionales.** Parabolic Plus muestra una estructura útil —núcleo, filtro y salida opcional—, pero comparar variantes sobre la misma muestra no demuestra que la complejidad sea perjudicial en general.

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

# Parte I — Estrategia 013: Multi-Interval Trend Detrend

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-07-STRAT-013`
- **Artículo:** *Multi-Interval Trend Detrend Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas del PDF:** 3–8
- **Páginas impresas del artículo:** 2–7
- **Estilo declarado:** mean reversion
- **Mercados declarados:** equities, futures, forex
- **Horizonte declarado:** swing trading
- **Activo del test:** iShares Russell 2000 ETF
- **Símbolo:** `IWM`
- **Data1:** 26 minutos
- **Data2:** 78 minutos
- **Periodo:** 1 de enero de 2013 a 31 de mayo de 2015
- **Primer signal declarado:** 1 de febrero de 2013
- **Tamaño base:** 100 acciones
- **Tamaño amplificado:** 200 acciones
- **Comisión:** $0.01 por acción
- **MaxBarsBack:** 75, contabilizado por TradeStation respecto de la serie lenta

### Inputs por defecto publicados

| Input | Default | Función |
|---|---:|---|
| `TrendMA_Length` | 20 | media para definir tendencia en Data2 |
| `DPO_Length` | 60 | media de referencia del DPO en Data1 |
| `DPOLongLvl` | -0.5 | umbral long |
| `DPOShortLvl` | 0.5 | umbral short |
| `BaseTradeSize` | 100 | tamaño base |
| `UseAmplifiedSize` | True | habilita tamaño amplificado |
| `AmplifySize_Multiple` | 2 | multiplicador de tamaño |
| `AmpDPOLongLvl` | -0.75 | umbral long amplificado |
| `AmpDPOShortLvl` | 0.75 | umbral short amplificado |
| `ATR_Length` | 5 | longitud ATR |
| `ProfitTgt_ATRFactor` | 3 | múltiplo ATR del objetivo |
| `Stop_ATRFactor` | 3 | múltiplo ATR del stop |

### Inputs realmente utilizados en el backtest publicado

| Input | Valor del test |
|---|---:|
| `TrendMA_Length` | 19 |
| `DPO_Length` | 56 |
| `DPOLongLvl` | -0.7 |
| `DPOShortLvl` | 0.15 |
| `BaseTradeSize` | 100 |
| `UseAmplifiedSize` | True |
| `AmplifySize_Multiple` | 2 |
| `AmpDPOLongLvl` | -0.85 |
| `AmpDPOShortLvl` | 0.20 |
| `ATR_Length` | 2 |
| `ProfitTgt_ATRFactor` | 1.2 |
| `Stop_ATRFactor` | 3 |

### Evidencia adicional del workspace

El stream `AnalisysTechniques` confirma estas técnicas:

```text
Mov Avg 1 Line
TSL:DPO
TSL:Multi-interval Trend Detrend
TSL:Strategy ATR Bands
```

El workspace confirma:

```text
primary chart:
IWM 26 min [ARCX]

strategy inputs:
19, 56, -0.7, 0.15, 100, True, 2,
-0.85, 0.20, 2, 1.2, 3

DPO indicator:
mode = 1 (difference as percent of price)
length = 56
lower level = -0.7
upper level = 0.15

ATR bands:
ATR length = 2
profit factor = 1.2
stop factor = 3
```

El stream `DrawingObjects` contiene cadenas huérfanas con `@GC=103NN`, aunque el chart activo y sus bindings son IWM. Esto se trata como metadato residual de dibujo o reutilización del workspace, **no** como una tercera fuente de datos de la estrategia.

El stream `optdatafile` está vacío. No podemos verificar:

```text
cuántas optimizaciones fueron ejecutadas;
qué rangos completos se probaron;
qué ranking ocupó 19/56/-0.7/0.15;
si se descartaron configuraciones negativas;
si existieron resultados alternativos superiores.
```

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero exige un `as-of join` multi-intervalo correcto. |
| ¿Puede replicarse aproximadamente? | **Sí.** El workspace confirma los parámetros activos. |
| ¿Puede replicarse exactamente? | **No todavía.** Falta el source para certificar la fórmula exacta del DPO y la activación intrabar de las salidas. |
| ¿El artículo demuestra edge? | **No.** Es un único activo, una muestra corta y parámetros obtenidos mediante varias optimizaciones. |
| ¿La tesis es plausible? | **Sí:** comprar debilidad dentro de una tendencia alcista y vender fortaleza dentro de una tendencia bajista. |
| ¿El amplifier demuestra mayor calidad de señal? | **No.** El informe mezcla timing y exposición. |
| ¿Está preparada para operar? | **No.** Falta reproducción, OOS, costes, lógica de gaps y control de eventos extremos. |
| ¿Merece estudiarse? | **Sí**, especialmente como patrón arquitectónico de estado lento + evento rápido. |

Clasificación TSIS:

```text
MULTI_INTERVAL_STATE_CONSUMER
SLOW_TREND_REGIME_FILTER
FAST_DETREND_MEAN_REVERSION_EVENT
CONDITIONAL_POSITION_AMPLIFIER
ATR_BRACKET
OPTIMIZED_IN_SAMPLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 2. Qué estrategia es realmente

La estrategia combina cuatro módulos distintos:

```text
1. régimen direccional lento;
2. desviación contrarian rápida;
3. selección de tamaño;
4. salida bracket basada en volatilidad.
```

Su política puede resumirse así:

```text
si la última barra de 78 minutos cerrada está sobre su SMA:
    sólo se permiten largos;
    se compra cuando el precio de 26 minutos está suficientemente
    por debajo de su propia SMA;

si la última barra de 78 minutos cerrada está bajo su SMA:
    sólo se permiten cortos;
    se vende cuando el precio de 26 minutos está suficientemente
    por encima de su propia SMA;
```

Por tanto, no es una estrategia mean-reversion pura sobre el nivel de precio. Es una estrategia:

> **contrarian en la escala rápida, pero alineada con la tendencia de la escala lenta.**

El amplifier añade una segunda hipótesis:

> Una desviación rápida más extrema dentro de la misma tendencia tendría mayor probabilidad o mayor expectativa y justificaría duplicar el tamaño.

Esta segunda hipótesis no queda separada del resultado principal en el artículo.

---

## 3. Arquitectura temporal y sincronización

### 3.1 Relación entre intervalos

La sesión regular estadounidense tiene 390 minutos:

```text
390 / 26 = 15 barras Data1 por sesión
390 / 78 = 5 barras Data2 por sesión
78 / 26 = 3
```

La relación exacta 3:1 facilita la alineación:

```text
cada barra lenta contiene tres barras rápidas;
ambas frecuencias terminan exactamente con la sesión;
no existe una barra parcial al cierre si el calendario es correcto.
```

### 3.2 Regla point-in-time

El artículo es explícito:

```text
el régimen se determina con la última barra de 78 minutos cerrada;
las señales se generan con la barra de 26 minutos;
la entrada se ejecuta en la apertura de la siguiente barra rápida.
```

La observación válida para cada decisión rápida debe ser:

```text
slow_state_asof(t) = última barra Data2 con close_timestamp <= t
```

Nunca debe utilizarse:

```text
la barra de 78 minutos todavía abierta;
el cierre final de una barra lenta reconstruido con datos futuros;
un forward-fill que se anticipe al timestamp de cierre.
```

### 3.3 Caso de frontera

Cuando una barra de 26 minutos y una de 78 minutos cierran simultáneamente:

```text
1. se cierra Data1;
2. se cierra Data2;
3. se actualiza el estado lento;
4. se evalúa la señal con ambas barras ya cerradas;
5. la orden se programa para la apertura de la siguiente Data1.
```

Este orden debe quedar fijado como contrato. Una implementación que evalúe Data1 antes de actualizar Data2 puede producir una señal distinta.

---

## 4. Reconstrucción matemática

### 4.1 Tendencia lenta

Para la última barra cerrada de Data2:

\[
MA^{slow}_t = SMA_{19}(C^{78m}_t)
\]

\[
Trend_t =
\begin{cases}
UP, & C^{78m}_t > MA^{slow}_t \\
DOWN, & C^{78m}_t < MA^{slow}_t \\
NEUTRAL, & C^{78m}_t = MA^{slow}_t
\end{cases}
\]

El PDF no define una acción para la igualdad exacta. La réplica debe usar `NEUTRAL / NO_ENTRY` salvo que el source muestre otra cosa.

### 4.2 DPO rápido

El indicador suministrado permite tres modos:

```text
1 = diferencia expresada como porcentaje del precio
2 = diferencia absoluta
3 = ratio
```

El workspace utiliza el modo 1. El artículo describe:

```text
distancia entre el cierre y una SMA,
expresada como porcentaje del precio.
```

La reconstrucción funcional más directa es:

\[
MA^{fast}_t = SMA_{56}(C^{26m}_t)
\]

\[
DPO^{pct}_t = 100\times\frac{C^{26m}_t-MA^{fast}_t}{C^{26m}_t}
\]

Sin el source quedan al menos dos formulaciones cercanas:

\[
100\times\frac{C_t-MA_t}{C_t}
\]

frente a

\[
100\times\left(\frac{C_t}{MA_t}-1\right)
\]

No son idénticas. La primera debe tratarse como **candidato de réplica**, no como código certificado.

### 4.3 Umbrales y dirección

#### Long base

```text
Trend = UP
DPO < -0.70
DPO >= -0.85
size = 100
```

#### Long amplificado

```text
Trend = UP
DPO < -0.85
size = 200
```

#### Short base

```text
Trend = DOWN
DPO > +0.15
DPO <= +0.20
size = 100
```

#### Short amplificado

```text
Trend = DOWN
DPO > +0.20
size = 200
```

La asimetría es extrema:

```text
long normal:      -0.70
long amplificado: -0.85
short normal:     +0.15
short amplificado:+0.20
```

Esto significa que la estrategia exige una caída rápida mucho mayor para comprar que la subida rápida necesaria para vender.

### 4.4 ATR y bracket

Con `ATR_Length = 2`:

\[
ATR_t = ATR_2(t)
\]

Los niveles se fijan desde el **cierre de la barra de señal**, no necesariamente desde el precio efectivo de entrada.

Para un long:

\[
Target_t = SignalClose_t + 1.2\,ATR_t
\]

\[
Stop_t = SignalClose_t - 3\,ATR_t
\]

Para un short:

\[
Target_t = SignalClose_t - 1.2\,ATR_t
\]

\[
Stop_t = SignalClose_t + 3\,ATR_t
\]

La relación nominal reward/risk es:

\[
\frac{1.2}{3}=0.4
\]

Esto requiere una tasa de acierto teórica superior aproximadamente al 71.4% antes de costes si target y stop fueran los únicos outcomes y se ejecutaran exactamente a esos niveles.

El informe presenta una tasa de acierto del 83.87%, coherente con una arquitectura deliberadamente sesgada hacia muchas ganancias pequeñas y pocas pérdidas grandes.

---

## 5. Reglas operativas reconstruidas

### 5.1 Entrada long

```text
al cierre de una barra Data1:
    obtener última Data2 cerrada;
    si Data2 close > SMA19(Data2)
    y DPO56(Data1) < -0.70:
        determinar tamaño 100/200;
        programar compra al open de la siguiente Data1.
```

### 5.2 Entrada short

```text
al cierre de una barra Data1:
    obtener última Data2 cerrada;
    si Data2 close < SMA19(Data2)
    y DPO56(Data1) > +0.15:
        determinar tamaño 100/200;
        programar short al open de la siguiente Data1.
```

### 5.3 Salidas

```text
profit target:
1.2 ATR desde el cierre de la barra de señal

stop:
3 ATR desde el cierre de la barra de señal
```

### 5.4 Ambigüedades que requieren reconciliación

1. **Fórmula exacta del DPO porcentual.**
2. **Condición persistente frente a cruce.** El artículo dice “cuando DPO está por debajo/encima”, no “cuando cruza”. Si una operación sale y la condición sigue vigente, podría existir reentrada inmediata.
3. **Activación del bracket en la barra de entrada.** La sección de mejoras afirma que la estrategia podría ser vulnerable a un movimiento extremo en la barra de entrada, lo que sugiere que las órdenes calculadas por la estrategia quizá no protegen plenamente esa misma barra.
4. **Prioridad intrabar.** Si target y stop se tocan dentro de una misma barra de 26 minutos, el resultado depende de la secuencia intrabar.
5. **Gap de entrada.** Como el bracket se ancla al cierre de la señal, un gap puede alterar profundamente el reward/risk real desde el fill.
6. **Estado al cambiar el régimen lento mientras hay una posición abierta.** El artículo no indica una salida inmediata por cambio de tendencia; sólo describe el bracket.
7. **Sesiones y extended hours.** El ejemplo parece construido sobre la sesión regular que encaja en 390 minutos. Debe fijarse explícitamente.

---

## 6. Resultados publicados

### 6.1 Informe completo

| Métrica | Total | Long | Short |
|---|---:|---:|---:|
| Beneficio neto | $6,211.00 | $956.00 | $5,255.00 |
| Beneficio bruto | $9,839.00 | $1,755.00 | $8,084.00 |
| Pérdida bruta | -$3,628.00 | -$799.00 | -$2,829.00 |
| Profit Factor | 2.71 | 2.20 | 2.86 |
| Trades | 93 | 17 | 76 |
| Porcentaje ganador | 83.87% | 76.47% | 85.53% |
| Ganadores | 78 | 13 | 65 |
| Perdedores | 15 | 4 | 11 |
| Beneficio medio por trade | $66.78 | $56.24 | $69.14 |
| Ganancia media | $126.14 | $135.00 | $124.37 |
| Pérdida media | -$241.87 | -$199.75 | -$257.18 |
| Ratio ganancia/pérdida | 0.52 | 0.68 | 0.48 |
| Mayor ganador | $336.00 | $228.00 | $336.00 |
| Mayor perdedor | -$490.00 | -$245.00 | -$490.00 |
| Máx. ganadores consecutivos | 14 | 7 | 12 |
| Máx. perdedores consecutivos | 2 | 1 | 2 |
| Barras medias en ganadores | 20.71 | 23.69 | 20.11 |
| Barras medias en perdedores | 44.87 | 31.00 | 49.91 |
| Máximo tamaño | 200 | 200 | 200 |
| Total acciones acumuladas | 15,100 | 2,400 | 12,700 |

Otros datos publicados:

```text
Percent of Time in Market = 24.73%
Total trading days ≈ 590
```

### 6.2 Concentración direccional

El lado short aporta:

\[
\frac{5255}{6211}=84.61\%\
\]

El lado long aporta sólo el 15.39%.

Además:

```text
76 de 93 trades son short = 81.72%
```

Por tanto, el resultado agregado no demuestra una regla equilibrada long/short. Demuestra principalmente el comportamiento de una versión short durante un periodo concreto de IWM.

### 6.3 Efecto del amplifier

La revista deduce a partir del total de acciones:

```text
58 de 93 trades fueron amplificados a 200 acciones;
7 de 17 longs fueron amplificados;
51 de 76 shorts fueron amplificados.
```

Equivale a:

```text
62.37% de todos los trades;
41.18% de los longs;
67.11% de los shorts.
```

El resultado publicado no separa:

```text
PnL de señales base;
PnL de señales amplificadas;
retorno por acción;
retorno por unidad de riesgo;
calidad del timing frente a efecto mecánico de tamaño doble.
```

Por tanto, no puede afirmarse que el amplifier aporte alpha incremental.

### 6.4 Dependencia de la tasa de acierto

Con los outcomes medios publicados:

\[
WinRate_{break-even}\approx
\frac{241.87}{126.14+241.87}=65.72\%
\]

La tasa observada de 83.87% deja margen in-sample, pero el sistema sigue expuesto a:

```text
regresión de la tasa de acierto;
clustering de pérdidas;
gaps más allá del stop;
slippage en targets pequeños;
periodos en que la reversión tarda más de lo esperado.
```

El hecho de que los perdedores duren aproximadamente el doble que los ganadores confirma una distribución incómoda:

```text
ganancias pequeñas y relativamente rápidas;
pérdidas mayores y más largas.
```

---

## 7. ¿Dónde podría estar el edge?

La hipótesis económica puede formularse así:

> Dentro de una tendencia de fondo, una desviación rápida contra esa tendencia suele ser temporal; cuando la desviación es extrema, la reversión hacia la tendencia ofrece una oportunidad de swing.

El potencial edge podría proceder de:

```text
persistencia de tendencia intermedia;
sobre-reacción de muy corto plazo;
reversión de liquidez intradía;
separación de escalas temporales;
filtrado de operaciones contra el régimen dominante.
```

Pero el artículo no demuestra cuál de estos mecanismos explica el PnL.

Hipótesis alternativas:

```text
el resultado procede del sesgo short del periodo;
el target pequeño induce una alta tasa de acierto sin alpha estructural;
el tamaño doble concentra el beneficio en pocas observaciones;
los intervalos 26/78 fueron seleccionados por el mismo histórico;
los umbrales asimétricos capturan una particularidad temporal de IWM;
la simulación de bracket favorece el resultado por orden intrabar.
```

---

## 8. Auditoría científica

### 8.1 Muestra corta

El periodo efectivo cubre aproximadamente 28 meses y sólo 93 operaciones.

Esto es insuficiente para establecer con confianza:

```text
estabilidad de régimen;
riesgo de cola;
comportamiento en crisis;
robustez de los umbrales;
estabilidad del amplifier;
validez en otros símbolos.
```

### 8.2 Selección de frecuencias y parámetros

El artículo describe una cadena de decisiones:

```text
observación visual de un ciclo de 62 barras;
selección de 78 minutos;
selección de 26 minutos;
optimización de MA lenta;
optimización de DPO;
optimización de umbrales;
optimización de ATR y factores.
```

Aunque cada decisión tiene una explicación técnica, en conjunto crea muchos grados de libertad. El paquete no conserva las búsquedas, por lo que no puede medirse el sesgo de selección.

### 8.3 Sin out-of-sample

No se publica:

```text
train/test split;
walk-forward;
periodo holdout;
purged cross-validation;
corrección por múltiples pruebas;
prueba postpublicación.
```

### 8.4 Sizing confundido con señal

Una comparación válida del amplifier debe mantener constante:

```text
capital promedio;
riesgo máximo;
volatilidad objetivo;
exposición por trade.
```

El artículo compara sólo el resultado combinado.

### 8.5 Riesgo de alineación multi-data

Un pequeño error temporal puede introducir anticipación:

```text
usar la barra Data2 actual antes de cerrar;
calcular la SMA lenta con un close futuro;
aplicar el estado de las 78 min a barras de 26 min anteriores;
mezclar timestamps de inicio y fin de barra.
```

Esta estrategia es un buen test del backtester precisamente porque estos errores son fáciles de ocultar.

### 8.6 Riesgo intrabar

Target y stop son órdenes intrabar. Sin secuencia de trades/quotes o una política conservadora, una barra OHLC de 26 minutos no basta para saber cuál se ejecutó primero.

### 8.7 Costes

El artículo modela comisiones, pero no documenta:

```text
spread efectivo;
slippage;
impacto;
fills parciales;
latencia;
gaps a través del stop.
```

La expectativa media de $66.78 por trade debe someterse a costes crecientes y ejecución retardada.

---

## 9. Contrato de implementación en TSIS

### 9.1 Inputs congelados para réplica

```text
symbol = IWM
session = regular US equity session
fast_interval = 26m
slow_interval = 78m
trend_ma_length = 19
dpo_length = 56
dpo_long = -0.70
dpo_short = 0.15
base_size = 100
amplifier_enabled = true
amplifier_multiple = 2
amp_long = -0.85
amp_short = 0.20
atr_length = 2
profit_atr = 1.2
stop_atr = 3.0
```

### 9.2 Campos de estado

```text
symbol
session_date
fast_bar_open_timestamp
fast_bar_close_timestamp
slow_bar_close_timestamp_asof
slow_close
slow_sma_19
trend_state
fast_close
fast_sma_56
dpo_pct
signal_direction
signal_strength_class
selected_size
atr_2_at_signal
reference_target
reference_stop
entry_timestamp
entry_price
exit_reason
exit_timestamp
exit_price
```

### 9.3 Estado de disponibilidad

```text
si no existe una barra lenta cerrada válida:
    NO_DECISION

si falta alguna barra rápida necesaria:
    NO_DECISION

si el calendario 26/78 no cierra limpiamente:
    SESSION_CONFIGURATION_ERROR
```

### 9.4 Pseudocódigo

```python
for fast_bar in fast_bars_26m:
    slow_bar = last_closed_bar_asof(
        slow_bars_78m,
        fast_bar.close_timestamp,
    )

    if slow_bar is None:
        continue

    trend_ma = sma(slow_close, 19, asof=slow_bar.close_timestamp)
    fast_ma = sma(fast_close, 56, asof=fast_bar.close_timestamp)

    dpo = 100.0 * (fast_bar.close - fast_ma) / fast_bar.close

    trend = (
        "UP" if slow_bar.close > trend_ma
        else "DOWN" if slow_bar.close < trend_ma
        else "NEUTRAL"
    )

    direction = None
    size = 0

    if trend == "UP" and dpo < -0.70:
        direction = "LONG"
        size = 200 if dpo < -0.85 else 100

    elif trend == "DOWN" and dpo > 0.15:
        direction = "SHORT"
        size = 200 if dpo > 0.20 else 100

    if direction is not None and portfolio_is_flat():
        atr = atr_wilder(fast_bars_26m, length=2, asof=fast_bar.close_timestamp)

        schedule_market_entry(
            direction=direction,
            size=size,
            timestamp=next_fast_bar_open(fast_bar),
        )

        if direction == "LONG":
            target = fast_bar.close + 1.2 * atr
            stop = fast_bar.close - 3.0 * atr
        else:
            target = fast_bar.close - 1.2 * atr
            stop = fast_bar.close + 3.0 * atr

        register_bracket_candidate(target=target, stop=stop)
```

La réplica debe parametrizar por separado:

```text
dpo_formula;
order_activation_policy;
same_bar_conflict_policy;
reentry_policy;
session template.
```

---

## 10. Plan para demostrar o destruir el edge

### Fase 1 — Réplica histórica

Objetivos:

```text
93 trades;
17 longs y 76 shorts;
78 ganadores y 15 perdedores;
58 trades de 200 acciones;
beneficio neto aproximado de $6,211;
reconciliación de fechas y razones de salida.
```

Si no se alcanzan estos checksums, no se pasa a optimización.

### Fase 2 — Test postpublicación congelado

La estrategia se publicó en julio de 2015. Debe evaluarse sin modificar parámetros desde la primera sesión posterior a la publicación hasta la última sesión completa disponible.

Informar por bloques:

```text
2015–2017
2018–2020
2021–2023
2024–actualidad
```

### Fase 3 — Ablación

| Variante | Pregunta |
|---|---|
| Sin filtro lento | ¿La Data2 añade información? |
| Sin DPO; entrada aleatoria dentro del régimen | ¿El timing rápido añade información? |
| Sin amplifier, siempre 100 acciones | ¿El sizing mejora retorno por riesgo? |
| Amplifier aleatorio con igual frecuencia | ¿El umbral extremo selecciona mejores trades? |
| Umbrales simétricos ±0.7 | ¿La asimetría es estructural o ajustada? |
| Target/stop 1:1 | ¿El edge depende de comprar tasa de acierto mediante payoff negativo? |
| Sin bracket; salida temporal | ¿Existe una vida media de la señal? |

### Fase 4 — Robustez de representación

Probar únicamente familias preregistradas de intervalos con relación entera y sesión completa:

```text
5/15
10/30
13/39
26/78
30/90, resolviendo la sesión incompleta
```

No seleccionar el máximo. Evaluar mesetas y estabilidad temporal.

### Fase 5 — Ejecución

```text
entrada ideal al open;
entrada + medio spread;
entrada + spread completo;
retraso de una barra;
stop conservador en conflictos intrabar;
resolución de 1 minuto;
quotes cuando estén disponibles.
```

### Fase 6 — Portabilidad

Probar índices/ETFs preregistrados:

```text
SPY
QQQ
IWM
DIA
```

El objetivo es determinar si existe una regularidad multi-escala general o sólo un ajuste de IWM.

---

## 11. Encaje en Market State y Event State

### Market State

```text
slow_trend_state
slow_distance_to_ma
fast_dpo_pct
fast_dpo_extremity
atr_state
session_progress
```

### Event State

```text
event_type:
fast_countertrend_deviation_within_slow_trend

subject_scope:
single_security_multi_interval

trigger_timestamp:
fast_bar_close

available_slow_state_timestamp:
last_closed_slow_bar
```

### Outcome

```text
return_to_target
return_to_stop
MFE
MAE
time_to_reversion
probability_of_target_before_stop
outcome_by_amplifier_class
outcome_by_direction
```

Esta separación permite estudiar el evento sin asumir que el bracket 1.2/3 es la respuesta óptima.

---

## 12. Decisión técnica

```text
IMPLEMENTAR:
sí, como prueba de multi-interval point-in-time

ACEPTAR COMO EDGE:
no

OPTIMIZAR:
no antes de réplica y postpublicación

OPERAR:
no

SIGUIENTE GATE:
MITD-REPLICATION-ASOF-ALIGNMENT-GATE
```

---

# Parte II — Estrategia 014: Parabolic Plus

## 13) Identificación y alcance

- **ID de estrategia:** `SCC-2015-07-STRAT-014`
- **Artículo:** *Parabolic Plus Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 10–14
- **Páginas impresas del artículo:** 9–13
- **Estilo declarado:** trend following
- **Mercados declarados:** equities, futures, forex
- **Horizonte declarado:** swing trading
- **Mercado del test:** Gold Futures Custom Continuous Contract
- **Símbolo:** `@GC=103NN`
- **Intervalo:** 60 minutos
- **Periodo:** cinco años, terminando el 31 de marzo de 2015
- **Capital inicial:** $25,000
- **Tamaño:** un contrato
- **Comisión:** $2.65 por lado y contrato
- **Stop monetario:** $2,000
- **Slippage:** no declarado

### Inputs publicados

| Input | Default | Función |
|---|---:|---|
| `AfStep` | 0.01 | incremento del factor de aceleración |
| `AfLimit` | 0.20 | límite del factor de aceleración |
| `My_Stop_Loss` | 2000 | stop monetario |
| `Enable_Price_Channel` | 2 | 1 sí; 2 no |
| `Trail_Stop_Length_LX` | 15 | canal de salida long |
| `Trail_Stop_Length_SX` | 10 | canal de salida short |
| `Enable_Volume_Filter` | 2 | 1 sí; 2 no |
| `Volume_Average_Length` | 5 | media de volumen |

### Evidencia adicional del workspace

El chart activo es:

```text
@GC=103NN 60 min [COMEX]
Gold Custom Continuous Contract
```

Las técnicas activas son:

```text
Parabolic SAR
TSL:Parabolic Plus
Volume Avg
```

Los inputs activos confirmados son:

```text
AfStep = 0.01
AfLimit = 0.20
My_Stop_Loss = 2000
Enable_Price_Channel = 2
Trail_Stop_Length_LX = 15
Trail_Stop_Length_SX = 10
Enable_Volume_Filter = 2
Volume_Average_Length = 5
```

Por tanto, el workspace está configurado en la **versión original más simple**:

```text
Parabolic SAR reversible
+
stop monetario
-
sin salida por canal
-
sin filtro de volumen
```

El `optdatafile` está vacío. La superficie `AfStep × AfLimit` sólo está disponible como imagen agregada en el PDF, no como datos reproducibles.

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí**, pero requiere motor de órdenes stop y contratos físicos de futuros. |
| ¿Puede replicarse aproximadamente? | **Sí.** Inputs y configuración activa están confirmados. |
| ¿Puede replicarse exactamente? | **No todavía.** Faltan source, trade list e historial físico del custom contract. |
| ¿El artículo demuestra edge? | **No.** Los parámetros fueron seleccionados con optimización y no existe OOS. |
| ¿La tesis es plausible? | **Sí:** persistencia de tendencia capturada por un stop-and-reverse adaptativo. |
| ¿Las capas opcionales son meros filtros? | **No.** Cambian entradas, salidas y duración; modifican la máquina de estados. |
| ¿La versión simple es científicamente superior? | **No demostrado.** Sólo fue mejor en esta muestra y parametrización. |
| ¿Está preparada para operar? | **No.** El PF es modesto y la estrategia es muy sensible a costes y ejecución. |

Clasificación TSIS:

```text
PARABOLIC_STOP_AND_REVERSE
NEAR_ALWAYS_IN
OPTIONAL_CHANNEL_EXIT
OPTIONAL_VOLUME_GATED_REVERSAL
DOLLAR_STOP
CONTINUOUS_FUTURES_REPRODUCTION_REQUIRED
OPTIMIZED_IN_SAMPLE
NOT_SCIENTIFICALLY_VALIDATED
NOT_LIVE_ELIGIBLE
```

---

## 14. Qué estrategia es realmente

La estrategia contiene un núcleo y dos capas opcionales.

### Núcleo

```text
Parabolic SAR tradicional;
orden stop en el valor parabólico;
reversión long ↔ short;
stop monetario de emergencia.
```

### Capa opcional A — Price Channel

```text
si está long y aparece el mínimo de 15 barras:
    salir al mercado en la barra siguiente;

si está short y aparece el máximo de 10 barras:
    salir al mercado en la barra siguiente.
```

Al habilitarla, la estrategia deja de ser siempre reversible porque puede salir a flat antes de un SAR contrario.

### Capa opcional B — Volume Filter

```text
sólo aceptar la nueva entrada/reversión
si el volumen actual supera la media de las 5 barras anteriores.
```

Esta capa no es un filtro inocuo. En un sistema stop-and-reverse:

> Rechazar una entrada contraria también puede impedir o retrasar la salida de la posición actual.

El propio artículo señala que entradas filtradas implican menos salidas. Por eso recomienda activar el price channel cuando se utilice volumen.

---

## 15. Reconstrucción del Parabolic SAR

La lógica estándar se basa en:

\[
SAR_{t+1}=SAR_t+AF_t(EP_t-SAR_t)
\]

donde:

```text
EP = extreme point de la tendencia activa;
AF = acceleration factor;
AF comienza en AfStep;
AF aumenta cuando aparece un nuevo extremo;
AF queda limitado por AfLimit.
```

Con los inputs publicados:

```text
AfStep = 0.01
AfLimit = 0.20
```

El PDF no especifica todos los detalles del algoritmo suministrado por TradeStation:

```text
inicialización;
clamp frente a highs/lows previos;
actualización en la barra de reversión;
redondeo al tick;
orden exacto entre SAR y stop monetario.
```

La réplica deberá reconciliarse con señales del workspace o una exportación de trades.

---

## 16. Reglas reconstruidas

### 16.1 Versión base activa en el workspace

```text
si el SAR está por debajo del precio:
    mantener/entrar long;
    colocar reversión short en el valor SAR;

si el SAR está por encima del precio:
    mantener/entrar short;
    colocar reversión long en el valor SAR;

aplicar stop monetario de $2,000.
```

### 16.2 Con canal habilitado

```text
long:
si Low_t es el mínimo de las últimas 15 barras,
salir a mercado en la siguiente barra;

short:
si High_t es el máximo de las últimas 10 barras,
salir a mercado en la siguiente barra.
```

Queda por confirmar si la ventana incluye la barra actual. La redacción sugiere que sí.

### 16.3 Con filtro de volumen habilitado

```text
volume_t > average(volume_{t-1} ... volume_{t-5})
```

Sólo entonces se permite la orden stop del SAR para la barra siguiente.

### 16.4 Ambigüedades críticas

1. **Orden stop en el mismo bar.** El SAR se ejecuta intrabar; OHLC de 60 minutos puede no bastar.
2. **Gap a través del SAR.** Debe definirse si el fill es al open o al stop teórico.
3. **Reversión y stop monetario simultáneos.** Se necesita prioridad de órdenes.
4. **Roll del contrato continuo.** Debe migrarse una posición abierta al contrato físico sin inventar PnL.
5. **Filtro de volumen y posición existente.** Debe certificarse si una reversión no validada deja la posición antigua abierta.
6. **Salida por canal y nueva entrada SAR en el mismo open.** Posible conflicto entre flat y reversal.
7. **Cálculo de volumen en futuros.** Debe usarse volumen del contrato correcto y evitar discontinuidades por roll.

---

## 17. Resultados publicados

### 17.1 Configuración base

```text
símbolo = @GC=103NN
intervalo = 60 minutos
periodo = 29/03/2010–31/03/2015 aproximadamente
capital inicial = $25,000
tamaño = 1 contrato
comisión = $2.65 por lado
stop = $2,000
canal = deshabilitado
volumen = deshabilitado
```

### 17.2 Informe de rendimiento

| Métrica | Total | Long | Short |
|---|---:|---:|---:|
| Beneficio neto | $181,623.50 | $94,679.40 | $86,944.10 |
| Beneficio bruto | $801,400.90 | $393,255.90 | $408,145.00 |
| Pérdida bruta | -$619,777.40 | -$298,576.50 | -$321,200.90 |
| Profit Factor | 1.29 | 1.32 | 1.27 |
| Trades | 1,405 | 702 | 703 |
| Porcentaje ganador | 38.93% | 42.31% | 35.56% |
| Ganadores | 547 | 297 | 250 |
| Perdedores | 858 | 405 | 453 |
| Beneficio medio por trade | $129.27 | $134.87 | $123.68 |
| Ganancia media | $1,465.08 | $1,324.09 | $1,632.58 |
| Pérdida media | -$722.35 | -$737.23 | -$709.05 |
| Ratio ganancia/pérdida | 2.03 | 1.80 | 2.30 |
| Mayor ganador | $19,474.70 | $7,094.70 | $19,474.70 |
| Mayor perdedor | -$2,005.30 | -$2,005.30 | -$2,005.30 |
| Máx. ganadores consecutivos | 6 | 6 | 7 |
| Máx. perdedores consecutivos | 10 | 12 | 11 |
| Barras medias en ganadores | 33.84 | 34.74 | 32.76 |
| Barras medias en perdedores | 15.01 | 15.88 | 14.24 |
| Máximo contratos | 1 | 1 | 1 |
| Return on Initial Capital | 726.49% | — | — |
| Annual Rate of Return | 42.25% | — | — |
| RINA Index | 180.98 | — | — |
| Tiempo en mercado | 98.72% | — | — |

### 17.3 Distribución direccional

El PnL está relativamente equilibrado:

```text
long = 52.13% del beneficio
short = 47.87% del beneficio
```

Esto es más convincente que una estrategia cuyo resultado depende de una sola dirección, aunque no elimina el sesgo de selección de parámetros.

### 17.4 Distribución de retornos

La arquitectura es la esperada en trend following:

```text
baja tasa de acierto;
ganancia media aproximadamente dos veces la pérdida media;
pocos ganadores grandes;
muchos perdedores pequeños.
```

La mayor ganancia representa aproximadamente el 10.7% del beneficio neto. No domina por completo el resultado, pero sigue siendo material.

### 17.5 Drawdown y capital

La revista indica un drawdown semanal aproximado del 45% durante el primer año. El capital inicial de $25,000 se presenta como mínimo práctico, no como sizing prudente.

La curva muestra:

```text
inicio adverso;
fuerte aceleración de 2011 a 2013;
meseta prolongada posterior;
retroceso al final de la muestra.
```

Por tanto, el beneficio agregado oculta una clara dependencia temporal.

---

## 18. Comparación de complejidad

La figura 5 compara cuatro variantes:

```text
1. original;
2. price channel enabled only;
3. volume filter enabled only;
4. price channel + volume filter.
```

La versión original termina con mayor beneficio y una curva visualmente más consistente. Sin embargo, el artículo no publica una tabla completa de métricas para cada variante.

No puede concluirse científicamente:

```text
“la simplicidad siempre gana”
```

Sólo puede afirmarse:

```text
en este activo, periodo, parametrización y simulador,
las dos capas opcionales publicadas empeoraron el resultado in-sample.
```

Causas alternativas:

```text
los filtros eliminaron ganadores y no sólo perdedores;
el filtro de volumen retrasó reversals;
las longitudes 15/10 no estaban calibradas para 60 minutos;
la comparación no normalizó exposición ni número de trades;
los módulos opcionales cambiaron la política, no sólo la complejidad.
```

---

## 19. Sensibilidad `AfStep × AfLimit`

La figura 6 muestra dos crestas de resultados favorables y una caída pronunciada entre ambas. Los parámetros elegidos:

```text
AfStep = 0.01
AfLimit = 0.20
```

se describen como situados aproximadamente en la parte media de la cresta izquierda.

Interpretación correcta:

```text
hay alguna estabilidad local;
pero la superficie no es una meseta global;
pequeños desplazamientos hacia la zona intermedia pueden destruir beneficio;
no conocemos el grid ni el ranking exacto.
```

El workspace no contiene las filas de optimización. Por tanto, no se puede verificar el grado de robustez ni aplicar correcciones por selección.

---

## 20. Auditoría científica

### 20.1 Parámetros seleccionados in-sample

El artículo reconoce optimización y sensitivity analysis. No existe OOS ni walk-forward.

### 20.2 Contrato continuo no operable

`@GC=103NN` no es un instrumento físico. La réplica real requiere:

```text
calendario de contratos;
regla de roll tres días antes del first notice date;
precio de salida del contrato saliente;
precio de entrada del contrato entrante;
comisiones y slippage del roll;
tratamiento de señales durante la transición.
```

### 20.3 No se declara slippage

Con 1,405 trades y estrategia stop-and-reverse, el número de ejecuciones es elevado. Un pequeño coste adicional por lado puede afectar materialmente a un PF de sólo 1.29.

### 20.4 Ambigüedad intrabar

Las entradas y reversals se activan por stop dentro de barras de 60 minutos. Sin resolución menor:

```text
no se conoce la secuencia exacta;
no se conoce el fill tras gaps;
no se conoce la prioridad con el stop monetario;
pueden aparecer fills demasiado favorables.
```

### 20.5 Alta exposición

El 98.72% de tiempo en mercado implica:

```text
riesgo overnight;
riesgo de fin de semana;
riesgo de eventos macro;
riesgo de gap;
uso permanente de margen.
```

### 20.6 Conclusión de simplicidad post hoc

Las capas opcionales se diseñaron y compararon sobre la misma muestra. La versión ganadora puede ser simplemente la que mejor encajó ese periodo.

### 20.7 Concentración temporal

La curva sugiere que gran parte de la rentabilidad se generó en un régimen de fuerte tendencia del oro. Debe descomponerse por años y regímenes.

---

## 21. Contrato de implementación en TSIS

### 21.1 Datos necesarios

```text
futuros GC por contrato físico;
OHLCV de 60 minutos;
calendario de sesiones;
first notice date;
expiration date;
regla de roll;
tick size y multiplicador;
spreads o quotes para slippage;
```

### 21.2 Campos de estado

```text
contract_id
continuous_reference_id
session_timestamp
parabolic_side
parabolic_value
extreme_point
acceleration_factor
price_channel_low_15
price_channel_high_10
volume
volume_avg_prev_5
volume_gate
position_state
dollar_stop_level
roll_state
```

### 21.3 Pseudocódigo funcional

```python
for bar in bars_60m:
    sar_state = update_parabolic_sar(
        bar=bar,
        af_step=0.01,
        af_limit=0.20,
    )

    volume_ok = bar.volume > mean(previous_volumes(5))

    allow_reversal = (
        True
        if not enable_volume_filter
        else volume_ok
    )

    if allow_reversal:
        place_stop_and_reverse(
            price=round_to_tick(sar_state.sar),
            direction=sar_state.opposite_direction,
            next_bar=True,
        )

    if enable_price_channel:
        if position_is_long() and bar.low <= lowest_low(15):
            schedule_market_exit(next_bar_open=True)

        if position_is_short() and bar.high >= highest_high(10):
            schedule_market_exit(next_bar_open=True)

    maintain_dollar_stop(amount=2000)

    if roll_required(bar.timestamp):
        execute_governed_contract_roll()
```

La política de órdenes debe declarar:

```text
stop gap fill;
same-bar reversal;
stop monetario frente a SAR;
canal frente a reversal;
orden de roll;
slippage por lado.
```

---

## 22. Plan de réplica y falsificación

### Fase 1 — Réplica de la versión base

Checksums:

```text
1,405 trades;
702 longs / 703 shorts;
PF ≈ 1.29;
net profit ≈ $181,623.50;
tiempo en mercado ≈ 98.72%;
mayor pérdida ≈ $2,005.30.
```

### Fase 2 — Reconciliación de contratos

Comparar:

```text
custom continuous teórico;
back-adjusted continuous;
contratos físicos con roll;
contratos físicos con slippage de roll.
```

### Fase 3 — Test postpublicación

Congelar `0.01/0.20/2000` y probar desde julio de 2015.

Reportar por:

```text
año;
régimen de tendencia;
régimen de volatilidad;
long/short;
contrato;
periodo entre rolls.
```

### Fase 4 — Ablación correctamente normalizada

| Variante | Pregunta |
|---|---|
| Base | referencia |
| Base + canal | ¿reduce cola sin destruir tendencias? |
| Base + volumen | ¿el volumen mejora señales o sólo retrasa exits? |
| Base + ambos | ¿hay interacción no lineal? |
| Volumen aplicado sólo a entrada desde flat | ¿evita el problema de bloquear reversals? |
| Canal como stop real, no salida next-bar | ¿mejora protección? |
| Sin stop monetario | ¿cuánto aporta el stop? |
| Stop por ATR | ¿el stop fijo es estable a través de precios/regímenes? |

Comparar con igual volatilidad, margen y exposición.

### Fase 5 — Costes

```text
0, 0.5, 1 y 2 ticks por lado;
spread histórico aproximado;
latencia de una barra;
fills conservadores en gaps;
roll explícito.
```

### Fase 6 — Multiplicidad

Si se reoptimiza `AfStep/AfLimit`, aplicar:

```text
walk-forward;
nested validation;
Deflated Sharpe Ratio;
PBO/CSCV;
block bootstrap;
mesetas, no máximos aislados.
```

---

## 23. Encaje en TSIS

### Market State

```text
parabolic_sar_state
trend_age
acceleration_factor
price_distance_to_sar
volume_relative_to_recent
channel_extreme_state
roll_proximity
```

### Event State

```text
event_type:
parabolic_stop_reversal_candidate

subject_scope:
futures_contract

trigger:
price reaches SAR stop
```

### Outcomes

```text
trend continuation after reversal
MFE/MAE
holding period
PnL before/after roll
PnL by AF region
PnL by volume gate
PnL by channel state
```

---

## 24. Decisión técnica

```text
IMPLEMENTAR:
sí, como benchmark stop-and-reverse

ACEPTAR COMO EDGE:
no

USAR CONTRATO CONTINUO PARA PNL FINAL:
no

OPTIMIZAR:
no antes de réplica física y OOS

OPERAR:
no

SIGUIENTE GATE:
PARABOLIC-PHYSICAL-CONTRACT-EXECUTION-GATE
```

---

# Parte III — Ideas transversales del Issue 7

## 25. Multi-interval no significa multi-timeframe ingenuo

La aportación más sólida del número no es un parámetro concreto, sino esta frontera:

```text
una señal rápida puede consumir un estado lento,
pero sólo mediante la última observación lenta cerrada.
```

Para TSIS esto implica que un `MarketState` puede contener features de múltiples frecuencias, pero cada feature necesita:

```text
source_interval;
source_close_timestamp;
availability_timestamp;
asof_age;
staleness_status.
```

---

## 26. Amplifier frente a add-on

El artículo distingue correctamente:

```text
ADD-ON:
genera una nueva entrada posterior
y aumenta la posición con una señal adicional.

AMPLIFIER:
no cambia el número de señales;
selecciona un tamaño mayor en la entrada original.
```

En TSIS deben pertenecer a capas distintas:

```text
signal policy
position sizing policy
position adjustment policy
```

No debe atribuirse el PnL del sizing al edge de la señal.

---

## 27. Núcleo y capas opcionales

Parabolic Plus propone una estructura de experimentación útil:

```text
core strategy
+
optional entry filter
+
optional exit module
```

La forma científica de evaluarla es una matriz factorial preregistrada:

| Core | Filtro | Exit | Interpretación |
|---|---|---|---|
| On | Off | Off | baseline |
| On | On | Off | efecto del filtro |
| On | Off | On | efecto de salida |
| On | On | On | interacción |

Cada comparación debe realizarse out-of-sample y normalizando exposición.

---

## 28. “Simplicidad” no es una métrica

El número presenta la simplicidad como virtud, pero para backtesting debe operacionalizarse mediante:

```text
número de parámetros efectivos;
número de grados de libertad;
complejidad de la máquina de estados;
turnover;
sensibilidad local;
estabilidad OOS;
coste de ejecución;
```

Una regla con pocos inputs puede seguir siendo altamente sensible. Parabolic SAR con dos parámetros y stop-and-reverse intrabar no es necesariamente simple desde el punto de vista de ejecución.

---

## 29. Idea secundaria: Contrarian Z-Score

La página publicitaria del número describe un indicador de investigación adicional:

```text
distancia entre precio y media expresada en desviaciones estándar;
promedio del Z-score;
momentum del Z-score promedio;
oscilador no acotado;
menor tendencia a quedar “pinneado” que RSI o estocástico.
```

El issue no ofrece reglas de estrategia, parámetros completos ni resultados. Por tanto se registra únicamente como:

```text
RESEARCH_LEAD
NOT_A_STRATEGY_SPECIFICATION
NO_PUBLISHED_BACKTEST
```

Podría convertirse en un Information Object candidato dentro de `price_location_intraday` o `volatility_range_state`, pero no debe incorporarse como edge validado.

---

# Parte IV — Registro consolidado para TSIS

## 30. Candidatos de eventos

### Evento 013-A

```text
event_type:
fast_countertrend_deviation_within_slow_uptrend

condition:
slow_close > slow_sma
and fast_dpo < threshold
```

### Evento 013-B

```text
event_type:
fast_countertrend_deviation_within_slow_downtrend

condition:
slow_close < slow_sma
and fast_dpo > threshold
```

### Evento 014-A

```text
event_type:
parabolic_sar_reversal_triggered
```

### Evento 014-B

```text
event_type:
parabolic_reversal_filtered_by_relative_volume
```

### Evento 014-C

```text
event_type:
position_reaches_opposite_price_channel_extreme
```

---

## 31. Priorización

| Candidato | Valor científico | Complejidad de implementación | Riesgo de simulación | Prioridad |
|---|---:|---:|---:|---:|
| Multi-interval Trend Detrend como event study | Alto | Media | Alta | Alta |
| Amplifier DPO | Medio | Baja | Media | Media |
| Parabolic base como benchmark | Medio | Media | Muy alta | Media |
| Filtro de volumen Parabolic | Medio | Media | Muy alta | Media-baja |
| Canal opcional Parabolic | Medio | Baja | Alta | Media-baja |
| Contrarian Z-Score | Exploratorio | Baja | Media | Baja |

---

## 32. Gates propuestos

```text
SCC7-GATE-01
MULTI_INTERVAL_ASOF_ALIGNMENT

SCC7-GATE-02
DPO_FORMULA_RECONCILIATION

SCC7-GATE-03
AMPLIFIER_FIXED_RISK_ABLATION

SCC7-GATE-04
PARABOLIC_INTRABAR_ORDER_SEQUENCING

SCC7-GATE-05
GC_PHYSICAL_CONTRACT_ROLL_RECONCILIATION

SCC7-GATE-06
POSTPUBLICATION_FROZEN_OOS
```

---

# Conclusión

El Issue 7 contiene dos estrategias interesantes, pero su valor principal no reside en aceptar sus cifras publicadas.

`Multi-Interval Trend Detrend` aporta una arquitectura útil para TSIS:

```text
estado lento observable
→ evento rápido contrarian
→ sizing condicionado
→ outcome bracket
```

Su resultado, sin embargo, depende fuertemente del lado short, del tamaño amplificado y de una estructura de payoff negativo que exige una tasa de acierto muy alta.

`Parabolic Plus` sirve como benchmark de una política stop-and-reverse y como ejemplo de ablation de módulos. La versión simple produjo el mejor resultado en la muestra, pero con un PF de 1.29, 98.72% de exposición y 1,405 trades, cualquier conclusión depende críticamente de slippage, secuencia intrabar y construcción física del contrato de futuros.

La decisión global es:

```text
CONSERVAR:
sí

REPLICAR:
sí, ambas

ACEPTAR LOS RESULTADOS COMO EDGE:
no

USAR LOS INPUTS PUBLICADOS COMO HIPÓTESIS CONGELADA:
sí

OPTIMIZAR ANTES DEL TEST POSTPUBLICACIÓN:
no

LIVE ELIGIBILITY:
rechazada hasta superar los gates
```

