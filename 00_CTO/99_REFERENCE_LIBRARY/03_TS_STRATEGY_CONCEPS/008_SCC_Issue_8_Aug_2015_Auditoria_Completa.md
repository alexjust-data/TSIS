# Auditoría completa — TradeStation Strategy Concepts Club, Issue 8 (agosto de 2015)

## 0. Alcance del artefacto

Este es el **único Markdown de la revista completa**. Integra:

```text
1. Normalized VIX Strategy
2. Net Tick Fade Strategy
3. ideas secundarias de investigación y backtesting presentes en el número
4. auditoría temporal, matemática y metodológica
5. inspección forense de los workspaces .tsw y contenedores .ELD
6. reconstrucciones funcionales y pseudocódigo
7. contratos de réplica para TSIS
8. planes de falsificación y validación postpublicación
```

No se generan archivos separados por estrategia.

### Fuentes examinadas

- PDF completo de 13 páginas: `SCC Issue 8 Aug 2015.pdf`.
- Archivo de apoyo: `2015-08.zip`.
- PDF duplicado incluido dentro del ZIP.
- Dos contenedores propietarios `.ELD`:
  - `TSL NORMALIZED VIX.ELD`;
  - `TSL NET TICK FADE.ELD`.
- Dos workspaces OLE/Compound Document `.tsw`:
  - `TSL Normalized VIX.tsw`;
  - `TSL.Net Tick Fade.tsw`.
- Las imágenes y tablas renderizadas de las 13 páginas, incluidas:
  - la alineación de `@ES=107XN` y `$VIX.X`;
  - el ejemplo de recurrencia de señales Normalized VIX;
  - los informes completos de rendimiento;
  - la superficie de sensibilidad `GSS_High × GSS_Low`;
  - el chart de `@ES.D=107XN` con `$TICK`;
  - las bandas construidas sobre máximos y mínimos del net tick;
  - la curva de capital de Net Tick Fade.
- Los Markdown de los Issues 1–7 se utilizan únicamente como **modelo de profundidad y organización**, no como autoridad factual para este número.

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
| `SCC Issue 8 Aug 2015.pdf` | 4,238,570 bytes | `e7e080fbe4f1d107d2304ac0398e64e236446b8d8e128a4b507b8e5589542474` |
| `2015-08.zip` | 4,268,081 bytes | `6b134098e545150f46cd4db4f4eefb3ccdf755f71beb017801b4c468e2a1e37a` |
| `TSL NORMALIZED VIX.ELD` | 19,903 bytes | `6df19f48dd185892595a62ae31a57a4faefdd7af5ad81f7be2f54173a06fbf21` |
| `TSL Normalized VIX.tsw` | 65,536 bytes | `b5b5a659f51bc5cd481013603e9038ea0b5b374912dcdf64e0523cc2767b263c` |
| `TSL NET TICK FADE.ELD` | 16,055 bytes | `ab33d9b0e6144bff2c7188c6286a928615269953df85b777807c23ad3c8eb920` |
| `TSL.Net Tick Fade.tsw` | 38,912 bytes | `dc78febd0fa4f7c6f83e48a2c3c9b9cc06a7a3131ac103c2fafdf854914eed19` |

El PDF incluido dentro del ZIP es binariamente idéntico al PDF cargado por separado.

El ZIP contiene además pequeños streams `Zone.Identifier` añadidos por el sistema de archivos. No forman parte del contenido científico ni del código de las estrategias.

Los `.ELD` son contenedores propietarios. Exponen marcadores de formato y versión —incluido `TSELXF`—, pero **no el source EasyLanguage como texto legible**. Por tanto, permiten confirmar que el paquete contiene técnicas TradeStation, pero no auditar línea por línea la implementación.

Los dos workspaces son contenedores OLE válidos. Ambos contienen un stream llamado `optdatafile`, pero su tamaño es **cero bytes**. Por tanto:

```text
no se conserva el grid de optimización;
no se conservan rankings completos;
no se conserva el número total de configuraciones ejecutadas;
no se puede medir directamente la magnitud real de la selección;
no se puede comprobar el puesto exacto de los parámetros publicados.
```

### Evidencia adicional del workspace Normalized VIX

El workspace confirma:

```text
Data1:
@ES=107XN Daily [CME]
E-mini S&P 500 Custom Continuous Contract

Data2:
$VIX.X Daily [CBOE]
CBOE Volatility Index

Técnicas aplicadas:
Mov Avg 2 Lines
TSL:Normalized VIX Strategy
TSL:Normalized VIX Indicator

Inputs activos de la estrategia:
GSS_High = 1.5
GSS_Low = -1.5
Sample_Size = 40
Hold_Length = 1
Short_MRO_Length = 2
Long_MRO_Length = 4
My_Stop_Loss = 2500

Inputs activos de medias:
FastLength = 20
SlowLength = 200
Displace = 0
```

Esta evidencia resuelve una inconsistencia del texto que se analiza más adelante: el workspace confirma que el bloqueo de señales short es de **2 barras**, mientras que el bloqueo long es de **4 barras**.

### Evidencia adicional del workspace Net Tick Fade

El workspace confirma:

```text
Data1:
@ES.D=107XN, 3 minutos [CME]
E-mini S&P 500 Custom Continuous Contract, daytime only

Data2:
$TICK, 3 minutos [NYSE]
NYSE Tick

Técnicas aplicadas:
TSL:Net Tick Fade Strategy
TSL:Range Bands Indicator

Inputs activos de la estrategia:
Length = 24
NumDevsUp = 1.8
NumDevsDn = -2.3
NoTradeBODBars = 1
NoTradeEODBars = 11
RangeLength = 6
RangeMultiplePT = 5.2
RangeMultipleSL = 8.8

Inputs activos del indicador:
Length = 24
NumDevsUp = 1.8
NumDevsDn = -2.3
SignalMarkerWidth = 4
```

El `.tsw` incorpora además un RadarScreen con ocho índices de net tick:

```text
$TICK   NYSE Tick
$TIKSP  S&P 500 Tick
$TIKI   DJIA Tick Index
$TIKRL  Russell 2000 Tick
$TIKND  Nasdaq 100 Tick
$TIKQ   NASDAQ Cumulative Tick
$TIKMD  S&P MidCap 400 Tick
$TIKUS  All US Tick
```

El workspace contiene cadenas residuales como `Multi-interval Trend Detrend` y `@GC=103NN`. No están enlazadas a las series activas ni a las técnicas activas del chart. Se interpretan como residuos de plantilla, dibujos o reutilización de workspace, no como inputs ocultos de Net Tick Fade.

### Resultado ejecutivo del issue

| ID | Estrategia | Tipo real | Evidencia publicada | Hallazgo crítico del paquete | Decisión |
|---|---|---|---|---|---|
| 015 | Normalized VIX | Reversión contraria de volatilidad extrema, condicionada por régimen 20/200 y cooldown asimétrico | ES diario; 10 años; $34,800.04; PF 2.32; 143 trades; 62.24% ganadoras; 5.74% en mercado | el workspace confirma `Short_MRO=2` y `Long_MRO=4`, contradiciendo la regla textual short de “4 barras”; no conserva optimizaciones | candidato prioritario de réplica postpublicación; tesis plausible, pero edge no demostrado y fórmula exacta del GSS pendiente de reconciliación |
| 016 | Net Tick Fade | Fade intradía de extremos de amplitud de mercado con bracket de rango y cierre EOD | ES daytime 3 min + NYSE Tick; 2 años; $22,384.66; PF 1.17; 1,722 trades; 54.65% ganadoras | el workspace confirma los inputs de test, pero la expectativa es sólo $13 por trade; aproximadamente un tick total de slippage por round trip eliminaría el beneficio medio | candidato arquitectónicamente valioso para market internals, pero muy frágil a costes, sincronización, prioridad de órdenes e integridad histórica de `$TICK` |

## 0.1 Veredicto global

El Issue 8 es especialmente relevante para TSIS porque introduce dos fuentes de estado que no pertenecen al precio del instrumento operado:

1. **Volatilidad implícita de opciones** como contexto de mercado externo al ES.
2. **Amplitud instantánea del universo de acciones** como market internal para operar un índice.

Ambas estrategias exigen sincronizar correctamente una serie operada con una segunda serie informativa. No basta con calcular un indicador sobre el propio activo.

```text
ISSUE_STATUS:
VALUABLE_SOURCE_MATERIAL

EDGE_STATUS:
UNPROVEN

IMPLEMENTATION_STATUS:
TWO_MULTI_DATA_REPRODUCTION_CANDIDATES

SCIENTIFIC_RISK:
HIGH

LIVE_STATUS:
NOT_ELIGIBLE
```

---

# Parte I — Estrategia 015: Normalized VIX

## 1) Identificación y alcance

- **ID de estrategia:** `SCC-2015-08-STRAT-015`
- **Artículo:** *Normalized VIX Strategy*
- **Autor:** **Frederic Palmliden, CMT**
- **Páginas físicas del PDF:** 3–7
- **Páginas impresas del artículo:** 2–6
- **Estilo declarado:** volatility based
- **Mercados declarados:** stock-index futures and ETFs
- **Horizonte declarado:** swing trading
- **Activo del test:** E-mini S&P 500
- **Símbolo operado:** `@ES=107XN`
- **Serie informativa:** `$VIX.X`
- **Bar interval:** diario
- **Periodo:** 10 años, terminando el 30 de junio de 2015
- **Capital inicial:** $10,000
- **Tamaño:** 1 contrato
- **Comisión:** $2.36 por lado y contrato
- **Stop monetario:** $2,500
- **Holding nominal:** 1 barra

### Inputs publicados y confirmados por el workspace

| Input | Valor | Función |
|---|---:|---|
| `GSS_High` | 1.5 | extremo alto del VIX normalizado; setup long |
| `GSS_Low` | -1.5 | extremo bajo del VIX normalizado; setup short |
| `Sample_Size` | 40 | ventana rolling de normalización |
| `Hold_Length` | 1 | barras de mantenimiento |
| `Short_MRO_Length` | 2 | bloqueo tras una señal short reciente |
| `Long_MRO_Length` | 4 | bloqueo tras una señal long reciente |
| `My_Stop_Loss` | 2,500 | stop monetario de seguridad |
| `FastLength` | 20 | media rápida de ES para régimen |
| `SlowLength` | 200 | media lenta de ES para régimen |

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sí.** Requiere una unión point-in-time entre ES diario y VIX diario. |
| ¿Puede replicarse aproximadamente? | **Sí.** El workspace confirma series, intervalos e inputs activos. |
| ¿Puede replicarse exactamente? | **No todavía.** El `.ELD` no expone la fórmula exacta del GSS ni la semántica precisa del MRO. |
| ¿El artículo demuestra edge? | **No.** Es un único instrumento, parámetros seleccionados in-sample y sin OOS. |
| ¿La tesis económica es plausible? | **Sí.** Extremos relativos de volatilidad pueden contener información contraria, condicionada por régimen. |
| ¿El uso de log-VIX es razonable? | **Sí como transformación**, aunque la afirmación de log-normalidad no se valida dentro del artículo. |
| ¿Está preparada para operar? | **No.** Falta réplica, ejecución realista, datos point-in-time y test postpublicación. |
| ¿Merece estudiarse? | **Sí, con prioridad alta.** El periodo 2015–actualidad ofrece una prueba postpublicación muy valiosa. |

Clasificación TSIS:

```text
EXTERNAL_MARKET_CONTEXT_CONSUMER
IMPLIED_VOLATILITY_EXTREME_EVENT
LONG_TERM_REGIME_FILTER
CONTRARIAN_ONE_BAR_HOLD
ASYMMETRIC_SIGNAL_COOLDOWN
OPTIMIZED_IN_SAMPLE
NOT_LIVE_ELIGIBLE
```

## 2. Qué estrategia es realmente

La estrategia no compra o vende el VIX. Utiliza el VIX para operar ES.

Su estructura real es:

```text
VIX diario
    ↓
normalización rolling en espacio logarítmico
    ↓
extremo alto o bajo
    ↓
filtro de régimen 20/200 sobre ES
    ↓
cooldown direccional
    ↓
entrada ES en la apertura diaria siguiente
    ↓
salida en la apertura de la barra posterior
```

No es una estrategia de tendencia pura ni una reversión pura:

- La **dirección estructural** procede de la tendencia 20/200 del ES.
- El **timing** procede de un extremo contrario del VIX.
- La operación se toma **contra el movimiento inmediato asociado a la volatilidad**, pero a favor del régimen principal.

En régimen alcista:

```text
VIX anormalmente alto
→ miedo/extremo
→ comprar ES
```

En régimen bajista:

```text
VIX anormalmente bajo
→ complacencia/extremo
→ vender ES
```

La segunda rama es conceptualmente más discutible. Un VIX bajo dentro de un mercado bajista no necesariamente representa un extremo simétrico al pánico alcista. El propio artículo reconoce que el lado short funciona peor.

## 3. Reconstrucción matemática

### 3.1 Transformación logarítmica

Sea:

```text
V_t = cierre diario del VIX disponible en la decisión t
n   = Sample_Size = 40
```

La reconstrucción funcional más probable es:

\[
y_t = \ln(V_t)
\]

\[
\mu^{(\log)}_t = \frac{1}{n}\sum_{i=0}^{n-1} y_{t-i}
\]

\[
\sigma^{(\log)}_t = SD(y_t,\ldots,y_{t-n+1})
\]

\[
GSS_t = \frac{y_t-\mu^{(\log)}_t}{\sigma^{(\log)}_t}
\]

Esto equivale a expresar el VIX actual respecto de una media geométrica y una dispersión geométrica:

\[
GM_t = \exp(\mu^{(\log)}_t)
\]

\[
GSS_t = \frac{\ln(V_t/GM_t)}{\sigma^{(\log)}_t}
\]

La revista denomina esta medida **geometric standard score**, pero no imprime el source ni la fórmula completa. Quedan pendientes:

```text
si SD usa divisor N o N-1;
si la ventana incluye la observación actual;
si usa cierre, settlement u otro campo del VIX;
si protege contra valores faltantes;
si aplica alguna corrección adicional a la desviación geométrica.
```

### 3.2 Por qué normalizar

El objetivo no es que `VIX = 20` tenga siempre el mismo significado. El objetivo es medir:

```text
qué tan extremo es el VIX actual
respecto de su propia distribución reciente
```

Eso reduce el problema de escala entre periodos de volatilidad estructuralmente distintos.

No elimina, sin embargo:

```text
cambios de régimen de volatilidad;
ventanas de 40 días dominadas por shocks;
colas gruesas persistentes;
clustering de volatilidad;
series de señales durante un VIX elevado por muchos días.
```

### 3.3 Régimen de mercado

Sobre el instrumento operado:

\[
Fast_t = SMA_{20}(Close^{ES}_t)
\]

\[
Slow_t = SMA_{200}(Close^{ES}_t)
\]

```text
bull_mode_t = Fast_t > Slow_t
bear_mode_t = Fast_t < Slow_t
```

No se define qué ocurre cuando ambas medias son exactamente iguales. La política conservadora de réplica sería `NO_SIGNAL`.

### 3.4 Umbrales

```text
high_extreme_t = GSS_t > 1.5
low_extreme_t  = GSS_t < -1.5
```

Debe reconciliarse si el código utiliza `>` o `>=`, y `<` o `<=`.

### 3.5 Cooldown mediante MRO

El artículo utiliza la expresión “most recent occurrence”. La estructura probable es:

```text
bars_since_long_signal >= Long_MRO_Length
bars_since_short_signal >= Short_MRO_Length
```

o una condición equivalente basada en una función `MRO` de EasyLanguage.

La evidencia consistente es:

```text
Long_MRO_Length  = 4
Short_MRO_Length = 2
```

Esto significa que la estrategia tolera señales short más frecuentes que long, al menos por configuración.

## 4. Inconsistencia documental crítica: short MRO 2 vs. 4

La tabla de inputs de la página física 5 muestra:

```text
Short_MRO_Length = 2
Long_MRO_Length  = 4
```

El encabezado del chart muestra la secuencia:

```text
1.5, -1.5, 40, 1, 2, 4, 2500
```

El workspace confirma exactamente:

```text
Short_MRO_Length = 2
Long_MRO_Length  = 4
```

Sin embargo, la sección de reglas de la página física 6 afirma para shorts:

```text
“no short signal has been generated for the last 4 bars”
```

Esa frase contradice las otras tres evidencias.

Decisión de réplica:

```text
SOURCE_OF_TRUTH_FOR_REPRODUCTION:
Short_MRO_Length = 2
Long_MRO_Length = 4

TEXTUAL_RULE_SHORT_4_BARS:
DOCUMENTATION_ERROR_CANDIDATE
```

No debe corregirse silenciosamente. La réplica deberá ejecutar al menos dos variantes:

```text
R1 = 2/4, confirmada por tabla, chart y workspace
R2 = 4/4, según la frase de reglas
```

La variante principal será `2/4`.

## 5. Arquitectura temporal

### 5.1 Decisión y ejecución

La señal se calcula con barras diarias cerradas.

Para ES, la revista advierte que la entrada y la salida se producen a las **6:00 p.m. ET**, apertura de la sesión diaria de futuros.

Secuencia funcional:

```text
antes de 18:00 ET:
la lectura diaria del VIX ya debe estar cerrada y disponible

18:00 ET, día t+1:
entrada ES a mercado

18:00 ET, día t+2:
salida ES a mercado
```

El retorno objetivo es, por tanto:

```text
ES daily-open to next daily-open
```

No es un simple close-to-close.

### 5.2 Regla point-in-time

La decisión sólo es válida si:

```text
VIX_timestamp <= decision_cutoff
ES_fast_sma y ES_slow_sma usan sólo barras cerradas
GSS usa sólo VIX disponible antes de la entrada
```

TSIS no debe unir filas por `date` sin considerar el timestamp real de cierre de cada serie.

### 5.3 Data-vintage

Para una réplica científica deben congelarse:

```text
fuente del VIX;
serie exacta y zona horaria;
tratamiento de festivos y sesiones parciales;
política de missing values;
versión del continuous contract;
regla de rollover;
settlement frente a last/close.
```

Un VIX histórico revisado o una serie de futuros reconstruida a posteriori puede modificar señales cercanas al umbral.

## 6. Reglas reconstruidas

### 6.1 Entrada long

En el cierre de la barra `t`:

```text
FastSMA20_t > SlowSMA200_t
AND GSS_t > 1.5
AND no hubo señal long dentro de las últimas 4 barras
```

Entonces:

```text
BUY 1 ES at market on open(t+1)
```

### 6.2 Entrada short

Versión principal confirmada por workspace:

```text
FastSMA20_t < SlowSMA200_t
AND GSS_t < -1.5
AND no hubo señal short dentro de las últimas 2 barras
```

Entonces:

```text
SELL SHORT 1 ES at market on open(t+1)
```

### 6.3 Salida temporal

```text
EXIT at market on open(t+2)
```

para `Hold_Length = 1`.

### 6.4 Stop monetario

```text
stop_loss = $2,500 por contrato
```

La revista indica que no se activó durante la muestra. No se declara Look-Inside-Bar Backtesting para este artículo.

Queda por certificar:

```text
si el stop está activo desde la apertura de entrada;
si se modela con high/low diario;
qué ocurre ante un gap más allá del stop;
qué prioridad tiene frente a la salida temporal;
si el stop se calcula por posición o por contrato.
```

## 7. Resultados publicados

### 7.1 Informe agregado

| Métrica | Total | Long | Short |
|---|---:|---:|---:|
| Beneficio neto | $34,800.04 | $25,916.02 | $8,884.02 |
| Beneficio bruto | $61,179.92 | $40,945.12 | $20,234.80 |
| Pérdida bruta | -$26,379.88 | -$15,029.10 | -$11,350.78 |
| Profit Factor | 2.32 | 2.72 | 1.78 |
| Operaciones | 143 | 84 | 59 |
| Porcentaje ganador | 62.24% | 64.29% | 59.32% |
| Ganadoras | 89 | 54 | 35 |
| Perdedoras | 54 | 30 | 24 |
| Ganancia media neta | $243.36 | $308.52 | $150.58 |
| Ganancia media ganadora | $687.41 | $758.24 | $578.14 |
| Pérdida media | -$488.52 | -$500.97 | -$472.25 |
| Ratio media win/loss | 1.41 | 1.51 | 1.22 |
| Mayor ganadora | $2,895.28 | $2,895.28 | $1,695.28 |
| Mayor perdedora | -$1,854.72 | -$1,604.72 | -$1,854.72 |
| Bars medios en ganadoras | 2.00 | 2.00 | 2.00 |
| Bars medios en perdedoras | 2.00 | 2.00 | 2.00 |

Otras métricas publicadas:

```text
Return on Initial Capital = 348.00%
Annual Rate of Return = 16.28%
Percent of Time in Market = 5.74%
RINA Index = 1,071.86
Sharpe Ratio = 0.42
K-Ratio = 6.10
Maximum weekly drawdown ≈ 12%
```

### 7.2 Concentración long

El lado long produce:

\[
\frac{25,916.02}{34,800.04}=74.47\%
\]

El lado short produce el 25.53% restante.

Esto no invalida el short, pero muestra que el resultado no es simétrico.

### 7.3 Margen de seguridad

El beneficio medio publicado es:

```text
$243.36 por trade
```

Es mucho más holgado que en varias estrategias anteriores de la revista, pero sigue dependiendo de:

```text
fills de apertura;
rolls de futuros;
slippage;
liquidez alrededor de 18:00 ET;
resolución de gaps;
comisiones reales;
```

### 7.4 Stop no observado

El artículo declara que el stop de $2,500 no fue alcanzado y que el peor trade drawdown fue aproximadamente $2,000.

Por tanto:

```text
el stop no explica el PnL observado;
no existe evidencia empírica dentro de la muestra sobre su comportamiento;
el stop actúa como protección hipotética de cola, no como componente validado.
```

## 8. ¿Dónde podría estar el edge?

Hipótesis principal:

> Dentro de un régimen alcista de largo plazo, un shock de volatilidad implícita extremadamente alto respecto de sus últimas 40 observaciones contiene una prima de reversión alcista a muy corto plazo. En un régimen bajista, un extremo bajo de volatilidad puede anticipar una reversión bajista.

Fuentes posibles:

```text
sobre-reacción de volatilidad;
demanda temporal de protección;
reversión de pánico;
reprecio rápido de opciones;
prima por absorción de riesgo;
continuidad de régimen condicionada por 20/200;
```

El artículo no demuestra cuál de ellas genera el beneficio.

Hipótesis alternativas que deben descartarse:

```text
simple buy-the-dip en ES;
exposición long condicionada por 20/200;
reversión propia del ES sin necesidad de VIX;
carry overnight del ES;
selección de parámetros;
selección favorable del periodo;
señales concentradas en unas pocas crisis;
```

## 9. Auditoría científica

### 9.1 Parámetros seleccionados in-sample

El artículo declara optimización y sensibilidad. No presenta:

```text
training period;
validation period;
out-of-sample;
walk-forward;
número de configuraciones probadas;
corrección por múltiples pruebas;
ranking de la configuración 1.5/-1.5;
```

El `optdatafile` vacío impide reconstruir la búsqueda.

### 9.2 Superficie visual insuficiente

La página 7 muestra una superficie `GSS_High × GSS_Low` y afirma que `1.5/-1.5` está en una zona relativamente estable, no en el máximo.

La imagen es evidencia cualitativa, pero no permite recuperar:

```text
cada punto del grid;
intervalos exactos;
metricas distintas de net profit;
robustez temporal;
robustez por subperiodos;
```

### 9.3 Único instrumento

El resultado principal es ES. La revista menciona SPY como posible aplicación, pero no publica una validación cruzada.

### 9.4 Muestra moderada

143 trades en diez años es una muestra mejor que muchas del corpus, pero sigue siendo insuficiente para afirmar estabilidad a través de todos los regímenes.

### 9.5 Solapamiento y dependencia

Las señales pueden agruparse durante episodios de VIX extremo. El cooldown reduce la frecuencia, pero no convierte las operaciones en observaciones independientes.

### 9.6 Asimetría no resuelta

El lado short tiene:

```text
menor PF;
menor expectativa;
menor beneficio total;
mayor mayor-pérdida;
```

La inclusión del short debe evaluarse como una hipótesis separada.

### 9.7 Riesgo de benchmark

La combinación `SMA20/SMA200` ya incorpora información de tendencia. Debe probarse si:

```text
VIX añade señal incremental
frente a comprar caídas de ES dentro de bull mode.
```

### 9.8 RINA inflado por exposición baja

El RINA de 1,071.86 es muy alto y está favorecido por sólo 5.74% de tiempo en mercado. No debe interpretarse como evidencia independiente de edge.

## 10. Contrato de implementación en TSIS

### 10.1 Fuentes necesarias

```text
ES daily governed signal view
ES executable open view
VIX daily official observation
calendar/session mapping
futures contract mapping and roll ledger
```

### 10.2 Separación de vistas

```text
signal_view:
serie diaria consistente para SMA20/SMA200 y GSS

execution_view:
contrato físico operable y precio raw de la apertura de sesión
```

No se debe ejecutar directamente sobre el continuous contract sintético.

### 10.3 Campos de estado

```text
session_id
signal_timestamp
execution_timestamp
es_close
es_sma_20
es_sma_200
market_regime
vix_close
vix_log
vix_log_mean_40
vix_log_std_40
vix_gss
long_extreme
short_extreme
bars_since_long_signal
bars_since_short_signal
cooldown_long_eligible
cooldown_short_eligible
signal_direction
hold_length
stop_amount
physical_contract
roll_state
context_status
```

### 10.4 Estados de indisponibilidad

```text
VIX_MISSING
VIX_NOT_FINAL
ES_DAILY_BAR_NOT_CLOSED
INSUFFICIENT_GSS_HISTORY
INSUFFICIENT_SMA_HISTORY
CALENDAR_MISMATCH
CONTRACT_MAPPING_UNAVAILABLE
ROLL_WINDOW_AMBIGUOUS
EXECUTION_OPEN_UNAVAILABLE
```

### 10.5 Pseudocódigo de referencia

```python
for session_t in governed_daily_sessions:
    es_bar = es_daily.asof(session_t.decision_cutoff)
    vix_bar = vix_daily.asof(session_t.decision_cutoff)

    if es_bar is None or vix_bar is None:
        mark_unavailable(session_t)
        continue

    fast = sma(es_close, 20, asof=session_t)
    slow = sma(es_close, 200, asof=session_t)

    log_vix = log(vix_close)
    gss = rolling_zscore(log_vix, length=40)

    bull_mode = fast > slow
    bear_mode = fast < slow

    long_ok = (
        bull_mode
        and gss > 1.5
        and bars_since_long_signal >= 4
    )

    short_ok = (
        bear_mode
        and gss < -1.5
        and bars_since_short_signal >= 2
    )

    if long_ok:
        schedule_entry(
            side="LONG",
            at=next_es_session_open(session_t),
            hold_bars=1,
            stop_dollars=2500,
        )
        register_long_signal(session_t)

    elif short_ok:
        schedule_entry(
            side="SHORT",
            at=next_es_session_open(session_t),
            hold_bars=1,
            stop_dollars=2500,
        )
        register_short_signal(session_t)
```

## 11. Plan para demostrar o destruir el edge

### Fase 1 — Réplica histórica

Objetivo:

```text
aproximarse a 143 trades;
reconciliar 84 long y 59 short;
reconciliar direcciones y fechas;
reconciliar $34,800.04;
```

Variantes de reconciliación:

```text
Short_MRO = 2 vs 4
SD poblacional vs muestral
ventana GSS incluyendo vs excluyendo barra actual
VIX close vs settlement
```

### Fase 2 — Test postpublicación congelado

Fecha de corte:

```text
publicación: agosto de 2015
OOS: primera sesión posterior a publicación
hasta última sesión completa disponible
```

Sin modificar:

```text
1.5 / -1.5 / 40 / 1 / 2 / 4 / 2500 / 20 / 200
```

### Fase 3 — Ablación

| Variante | Pregunta |
|---|---|
| GSS + régimen | regla original |
| GSS sin 20/200 | ¿el régimen aporta valor? |
| 20/200 + caída propia de ES | ¿VIX aporta información incremental? |
| VIX raw percentile | ¿es necesaria la fórmula GSS? |
| arithmetic z-score VIX | ¿el log mejora robustez? |
| long only | ¿la rama short destruye estabilidad? |
| short only | ¿existe edge independiente? |
| sin cooldown | ¿el MRO reduce clustering o sólo elimina trades? |
| cooldown simétrico | ¿la asimetría 2/4 fue seleccionada? |

### Fase 4 — Descomposición temporal

Separar:

```text
18:00 → siguiente regular open
regular open → regular close
regular close → siguiente 18:00
```

Así se identifica si el beneficio procede de:

```text
night session;
sesión regular;
settlement/open mechanics;
```

### Fase 5 — Robustez

Pruebas preregistradas:

```text
Sample_Size: 20, 40, 60, 90
GSS_High: 1.0–2.5
GSS_Low: -1.0 a -2.5
Fast SMA: 10–60
Slow SMA: 100–300
Hold: 1–5 barras
```

No seleccionar el máximo. Evaluar mesetas, subperiodos y PBO/DSR si se amplía la búsqueda.

### Fase 6 — Ejecución

```text
ideal daily open
physical contract first tradable quote
1 tick slippage por lado
2 ticks por lado
roll days excluidos/incluidos
market-on-open compatible con sesión de futuros
```

## 12. Encaje en Market State y Event State

### Market State

```text
broad_market_context.vix_level
broad_market_context.vix_log_zscore_40
broad_market_context.es_sma20_sma200_regime
broad_market_context.vix_extreme_cluster_state
```

### Event State

```text
event_type:
market_volatility_extreme_normalized

subject_scope:
broad_equity_index

reference_subject:
CBOE_VIX

tradable_subject:
ES
```

### Outcomes

```text
es_open_to_open_return_1d
regular_session_return
night_session_return
MFE
MAE
stop_hit
regime_persistence
vix_normalization_decay
```

## 13. Decisión técnica

```text
IMPLEMENTAR:
sí

PRIORIDAD:
alta

ACEPTAR COMO EDGE:
no

VARIANTE PRINCIPAL:
Short_MRO=2, Long_MRO=4

CONDICIÓN DE APERTURA:
réplica histórica + OOS postpublicación congelado

LIVE:
no

GATE PROPUESTO:
NVIX-REPLICATION-POSTPUBLICATION-OOS-GATE
```

---

# Parte II — Estrategia 016: Net Tick Fade

## 14) Identificación y alcance

- **ID de estrategia:** `SCC-2015-08-STRAT-016`
- **Artículo:** *Net Tick Fade Strategy*
- **Autor:** **Stanley Dash, CMT**
- **Páginas físicas del PDF:** 9–13
- **Páginas impresas del artículo:** 8–12
- **Estilo declarado:** mean reversion
- **Mercados declarados:** stock-index futures and ETFs
- **Horizonte declarado:** day trading
- **Instrumento operado:** E-mini S&P 500 daytime only
- **Data1:** `@ES.D=107XN`, 3 minutos
- **Data2:** `$TICK`, 3 minutos
- **Periodo:** 2 años terminando el 30 de junio de 2015
- **Tamaño:** 1 contrato
- **Comisión:** $2.36 por lado
- **Sin exposición overnight**

### Inputs por defecto del código

| Input | Default | Función |
|---|---:|---|
| `Length` | 20 | ventana de medias y desviaciones de net tick |
| `NumDevsUp` | 2 | multiplicador de banda superior |
| `NumDevsDn` | -2 | multiplicador de banda inferior |
| `NoTradeBODBars` | 1 | barras iniciales sin entrada |
| `NoTradeEODBars` | 11 | barras finales sin entrada |
| `RangeLength` | 4 | ventana de rango medio de ES |
| `RangeMultiplePT` | 2 | múltiplo de rango para target |
| `RangeMultipleSL` | 2 | múltiplo de rango para stop |

### Inputs realmente utilizados y confirmados por workspace

| Input | Valor del test |
|---|---:|
| `Length` | 24 |
| `NumDevsUp` | 1.8 |
| `NumDevsDn` | -2.3 |
| `NoTradeBODBars` | 1 |
| `NoTradeEODBars` | 11 |
| `RangeLength` | 6 |
| `RangeMultiplePT` | 5.2 |
| `RangeMultipleSL` | 8.8 |

### Veredicto inicial

| Cuestión | Conclusión |
|---|---|
| ¿Puede implementarse en TSIS? | **Sólo si se obtiene un feed histórico fiable de market internals.** |
| ¿Puede replicarse aproximadamente? | **Sí**, porque el workspace confirma símbolos, intervalos e inputs. |
| ¿Puede replicarse exactamente? | **No todavía.** Falta source, prioridad de órdenes e histórico point-in-time de `$TICK`. |
| ¿El artículo demuestra edge? | **No.** PF 1.17 y expectativa de $13/trade son extremadamente sensibles a ejecución. |
| ¿La tesis es plausible? | **Sí:** amplitud extrema de muy corto plazo puede revertir. |
| ¿Es una señal de precio? | **No.** Es una señal de breadth construida sobre el universo NYSE. |
| ¿Está preparada para operar? | **No.** El margen de costes es insuficiente sin una simulación microestructural. |
| ¿Merece estudiarse? | **Sí**, como objeto de market internal y como test multi-data intradía. |

Clasificación TSIS:

```text
MARKET_INTERNAL_STATE_CONSUMER
INTRADAY_BREADTH_EXTREME_EVENT
CONTRARIAN_INDEX_FUTURES_SIGNAL
VOLATILITY_SCALED_BRACKET
DAY_SESSION_ONLY
EXECUTION_SENSITIVE
NOT_LIVE_ELIGIBLE
```

## 15. Qué estrategia es realmente

La estrategia no utiliza precio de ES para crear la entrada. El precio de ES sólo se usa para:

```text
ejecutar la operación;
calcular rango medio;
construir target y stop;
liquidar la posición.
```

La señal procede de la amplitud instantánea del mercado:

```text
$TICK = número de acciones NYSE en uptick
        menos
        número de acciones NYSE en downtick
```

La lógica es contraria:

```text
$TICK extremadamente bajo
→ presión vendedora amplia
→ comprar ES esperando reversión

$TICK extremadamente alto
→ presión compradora amplia
→ vender ES esperando reversión
```

## 16. Reconstrucción matemática de Range Bands

Sea para la barra de `$TICK`:

```text
H^T_t = máximo del net tick en la barra
L^T_t = mínimo del net tick en la barra
n = 24
```

Banda superior probable:

\[
Upper_t = MA_n(H^T)_t + 1.8 \cdot SD_n(H^T)_t
\]

Banda inferior probable:

\[
Lower_t = MA_n(L^T)_t - 2.3 \cdot SD_n(L^T)_t
\]

El input `NumDevsDn` ya es negativo, por lo que la implementación genérica podría escribirse como:

\[
Lower_t = MA_n(L^T)_t + (-2.3)\cdot SD_n(L^T)_t
\]

La señal:

```text
long_extreme_t  = Low_TICK_t < Lower_t
short_extreme_t = High_TICK_t > Upper_t
```

No son Bollinger Bands convencionales:

```text
la banda superior se calcula con máximos;
la banda inferior se calcula con mínimos;
no se usa el cierre;
las dos bandas tienen distribuciones distintas;
los multiplicadores son asimétricos.
```

### Ambigüedad de auto-inclusión

La revista no aclara si `Upper_t` y `Lower_t` incluyen la barra actual antes de evaluar la penetración.

Dos variantes:

```text
A. bandas calculadas incluyendo la barra t
B. bandas calculadas hasta t-1 y señal evaluada en t
```

La variante A no tiene look-ahead, pero el extremo actual ensancha su propia banda. La variante B representa mejor un umbral ex ante. Deben reconciliarse contra las fechas de trades.

## 17. Arquitectura de tiempo y sesión

### 17.1 Series sincronizadas

```text
Data1 = ES daytime, 3 minutos
Data2 = NYSE Tick, 3 minutos
```

Cada decisión debe consumir barras con el mismo cierre temporal.

No se permite:

```text
forward-fill de $TICK;
usar una barra de $TICK cerrada después de la de ES;
mezclar timezones;
mezclar sesión regular con overnight;
```

### 17.2 Ventana operativa

El artículo fija:

```text
sesión @ES.D: 09:30–16:15 ET
NoTradeBODBars = 1
NoTradeEODBars = 11
```

Según la explicación publicada:

```text
primer signal posible: barra 09:33
primera ejecución posible: barra siguiente
último signal posible: barra 15:42
última ejecución posible: barra 15:45
```

La estrategia liquida cualquier posición restante a las 16:15 ET.

### 17.3 Carryover entre sesiones

Las medias y desviaciones de `$TICK` continúan de una sesión a la siguiente. La primera parte del día utiliza una ventana que contiene observaciones del día anterior.

El propio autor sugiere investigar un warm-up intradía.

Esto crea una pregunta científica importante:

```text
¿el edge procede del extremo respecto de una distribución continua multisesión

o
respecto de la distribución del día actual?
```

## 18. Bracket de salida

### 18.1 Rango medio

Sea el rango simple de ES:

\[
R_t = High^{ES}_t - Low^{ES}_t
\]

\[
AvgRange_t = MA_6(R)_t
\]

La revista utiliza rango simple y no True Range para evitar que el gap overnight artificial del símbolo `.D` ensanche el bracket al inicio de la sesión.

### 18.2 Target y stop

Para una entrada long en `P_entry`:

\[
Target = P_{entry} + 5.2 \cdot AvgRange
\]

\[
Stop = P_{entry} - 8.8 \cdot AvgRange
\]

Para short:

\[
Target = P_{entry} - 5.2 \cdot AvgRange
\]

\[
Stop = P_{entry} + 8.8 \cdot AvgRange
\]

Ratio nominal recompensa/riesgo:

\[
\frac{5.2}{8.8}=0.5909
\]

La tasa de acierto nominal necesaria si todos los trades alcanzaran exactamente target o stop sería aproximadamente:

\[
\frac{1}{1+0.5909}=62.86\%
\]

La tasa publicada es 54.65%, pero los trades también pueden cerrarse por EOD y los resultados medios no coinciden con los múltiplos nominales. Por eso la estrategia sigue siendo ligeramente rentable.

### 18.3 Ambigüedades

```text
¿AvgRange se congela en la barra de señal o entrada?
¿se redondea target y stop al tick mínimo antes o después?
¿qué ocurre si target y stop se tocan en la misma barra de 3 minutos?
¿se usa intrabar order generation?
¿el bracket se activa en la misma barra de entrada?
¿cómo se resuelve un gap a través del stop?
```

Sin source o trade list no puede certificarse.

## 19. Reglas reconstruidas

### 19.1 Entrada long

Dentro de la ventana habilitada:

```text
if Low($TICK)_t < LowerBand_t:
    buy ES at market on open(t+1)
```

### 19.2 Entrada short

```text
if High($TICK)_t > UpperBand_t:
    sell short ES at market on open(t+1)
```

### 19.3 Salidas

```text
profit target por AvgRange × 5.2
stop loss por AvgRange × 8.8
exit EOD a las 16:15 ET
```

### 19.4 Ambigüedad de doble señal

Una barra de `$TICK` puede, en teoría, tener:

```text
Low < LowerBand
AND
High > UpperBand
```

El artículo no define prioridad.

También falta especificar qué ocurre si aparece una señal opuesta mientras existe posición:

```text
ignorar;
revertir;
cerrar y esperar;
aceptar sólo si no hay bracket pendiente;
```

TSIS debe representar estas decisiones como política contractual, no asumirlas.

## 20. Resultados publicados

### 20.1 Informe agregado

| Métrica | Total | Long | Short |
|---|---:|---:|---:|
| Beneficio neto | $22,384.66 | $10,060.42 | $12,324.24 |
| Beneficio bruto | $157,845.98 | $50,387.88 | $107,458.10 |
| Pérdida bruta | -$135,461.32 | -$40,327.46 | -$95,133.86 |
| Profit Factor | 1.17 | 1.25 | 1.13 |
| Operaciones | 1,722 | 689 | 1,033 |
| Porcentaje ganador | 54.65% | 61.10% | 50.34% |
| Ganadoras | 941 | 421 | 520 |
| Perdedoras | 781 | 268 | 513 |
| Ganancia media neta | $13.00 | $14.60 | $11.93 |
| Ganancia media ganadora | $167.74 | $119.69 | $206.65 |
| Pérdida media | -$173.45 | -$150.48 | -$185.45 |
| Ratio media win/loss | 0.97 | 0.80 | 1.11 |
| Mayor ganadora | $1,107.78 | $1,107.78 | $1,057.78 |
| Mayor perdedora | -$1,242.22 | -$817.22 | -$1,242.22 |
| Barras medias ganadoras | 25.30 | 18.99 | 30.42 |
| Barras medias perdedoras | 38.46 | 26.00 | 44.96 |
| Return Retracement Ratio | 0.91 | — | — |
| RINA Index | 329.92 | — | — |

Tiempo en mercado publicado:

```text
15% de la sesión diurna
0% overnight
```

### 20.2 Duración media

Con barras de 3 minutos:

```text
ganadoras: 25.30 × 3 ≈ 75.9 minutos
perdedoras: 38.46 × 3 ≈ 115.4 minutos
```

Las pérdidas duran aproximadamente 39.5 minutos más que las ganancias.

### 20.3 Fragilidad a slippage

La expectativa neta publicada es:

```text
$13.00 por trade
```

Un tick de ES equivale a $12.50 por contrato.

Por tanto:

```text
break-even slippage agregado ≈ 1.04 ticks por round trip
```

No significa un tick por lado; significa aproximadamente **un tick total sumando entrada y salida**.

Escenarios:

```text
0.5 tick por lado = 1 tick total
→ casi elimina toda la expectativa

1 tick por lado = 2 ticks total = $25
→ convierte la expectativa media en negativa
```

Con 1,722 trades:

```text
1 tick total por trade = $21,525 de coste
2 ticks totales por trade = $43,050 de coste
```

El beneficio publicado es $22,384.66.

Este es el hallazgo económico más importante del artículo:

> El edge publicado está prácticamente al nivel de un solo tick agregado de slippage por operación.

La revista declara comisión, pero no publica una cifra de slippage. No debe asumirse que el resultado soporta ejecución real.

### 20.4 Lado short

El lado short produce más beneficio total, pero con:

```text
PF 1.13
50.34% ganadoras
$11.93 por trade
```

Es especialmente vulnerable a costes.

### 20.5 Curva de capital

La curva asciende, pero presenta:

```text
largos estancamientos;
drawdowns visibles;
dependencia de rachas positivas;
recuperación tardía tras una caída extensa.
```

No es una curva estable a pesar del RINA publicado.

## 21. ¿Dónde podría estar el edge?

Hipótesis principal:

> Cuando una proporción excepcionalmente grande del universo NYSE cotiza simultáneamente en downtick o uptick, la presión de muy corto plazo se agota y el índice amplio revierte parcialmente.

Mecanismos plausibles:

```text
agotamiento de órdenes agresivas;
rebalanceo de market makers;
mean reversion de breadth extrema;
absorción de liquidez;
reversión después de ejecución programática;
```

El artículo no demuestra el mecanismo.

Hipótesis alternativas:

```text
reversión propia de ES sin necesidad de $TICK;
intraday seasonality;
selección favorable de horas;
selección de $TICK frente a otros índices;
selección de thresholds;
backtest con fills demasiado favorables;
```

## 22. Auditoría científica

### 22.1 Sólo dos años

La muestra es corta para una estrategia intradía y no incluye suficientes regímenes de microestructura.

### 22.2 Parámetros optimizados

Los valores fueron obtenidos mediante varias optimizaciones, pero no una búsqueda exhaustiva simultánea.

No se informa:

```text
número de pruebas;
orden de selección;
criterio de aceptación;
resultados descartados;
OOS;
walk-forward;
```

El `optdatafile` vacío impide recuperar el proceso.

### 22.3 Costes insuficientes

PF 1.17 y $13/trade no ofrecen margen suficiente para ignorar:

```text
slippage;
bid-ask;
latencia;
market order impact;
colas en apertura de barra;
roll de contratos;
```

### 22.4 Serie `$TICK`

La validez depende de una serie externa compleja:

```text
universo de componentes;
reglas de uptick/downtick;
proveedor;
horario;
correcciones;
missing bars;
revisión histórica;
```

La estrategia no puede validarse con un proxy reconstruido sin declarar la diferencia.

### 22.5 Sincronización

Un desfase de una barra entre `$TICK` y ES puede alterar por completo la entrada.

### 22.6 Intrabar

Target y stop pueden convivir dentro de la misma barra. Sin datos de mayor resolución no existe secuencia causal observable.

### 22.7 Multiple testing por net tick universe

El workspace muestra ocho net tick indexes alternativos. Probar todos y conservar el mejor introduce otra capa de selección.

### 22.8 Carryover de bandas

La mezcla de datos del día anterior en las primeras señales puede generar un edge aparente dependiente de la apertura, no del extremo intradía general.

## 23. Contrato de implementación en TSIS

### 23.1 Datos necesarios

```text
ES 3-minute raw/quote-guarded
NYSE Tick 3-minute point-in-time
exchange calendar
session segmentation
physical futures contract map
commission and slippage model
```

### 23.2 Encaje ontológico

No requiere crear un nuevo Information Object en la ontología v1.

La variable puede mapearse a:

```text
broad_market_context
```

porque representa breadth del mercado amplio.

No debe confundirse con:

```text
order_flow_pressure del propio ES;
market_microstructure_state del propio ES;
trading_activity del propio ES.
```

### 23.3 Campos de estado

```text
decision_timestamp
es_contract
es_open
es_high
es_low
es_close
es_range
es_avg_range_6
net_tick_symbol
net_tick_open
net_tick_high
net_tick_low
net_tick_close
net_tick_high_ma_24
net_tick_high_sd_24
net_tick_low_ma_24
net_tick_low_sd_24
upper_band
lower_band
upper_penetrated
lower_penetrated
session_bar_index
bars_to_session_end
entry_window_eligible
position_state
target_price
stop_price
exit_reason
context_status
```

### 23.4 Estados de indisponibilidad

```text
NET_TICK_MISSING
NET_TICK_TIMESTAMP_MISMATCH
NET_TICK_SESSION_MISMATCH
INSUFFICIENT_BAND_HISTORY
ES_BAR_MISSING
CONTRACT_MAPPING_UNAVAILABLE
AMBIGUOUS_INTRABAR_PATH
DUAL_SIGNAL_SAME_BAR
EXECUTION_QUOTE_UNAVAILABLE
```

### 23.5 Pseudocódigo funcional

```python
for bar_t in es_day_session_3m:
    tick_bar = net_tick_3m.exact_match(bar_t.close_timestamp)

    if tick_bar is None:
        mark_unavailable(bar_t, "NET_TICK_TIMESTAMP_MISMATCH")
        continue

    upper = mean(tick_high, 24) + 1.8 * std(tick_high, 24)
    lower = mean(tick_low, 24) - 2.3 * std(tick_low, 24)

    eligible = (
        session_bar_index(bar_t) >= 1
        and bars_to_session_end(bar_t) >= 11
    )

    if not eligible:
        continue

    long_signal = tick_bar.low < lower
    short_signal = tick_bar.high > upper

    if long_signal and short_signal:
        mark_unavailable(bar_t, "DUAL_SIGNAL_SAME_BAR")
        continue

    avg_range = mean(es_high - es_low, 6)

    if long_signal:
        schedule_market_entry(
            side="LONG",
            at=next_bar_open(bar_t),
            target_distance=5.2 * avg_range,
            stop_distance=8.8 * avg_range,
            force_exit=session_close,
        )

    elif short_signal:
        schedule_market_entry(
            side="SHORT",
            at=next_bar_open(bar_t),
            target_distance=5.2 * avg_range,
            stop_distance=8.8 * avg_range,
            force_exit=session_close,
        )
```

## 24. Plan para demostrar o destruir el edge

### Fase 1 — Réplica histórica

Objetivos:

```text
1,722 trades
689 long
1,033 short
$22,384.66 net
PF 1.17
```

Reconciliar:

```text
bandas con/sin barra actual;
SD poblacional/muestral;
AvgRange señal/entrada;
redondeo a tick;
prioridad de órdenes;
```

### Fase 2 — Ejecución realista antes de cualquier optimización

Escenarios mínimos:

```text
0 ticks adicionales
0.5 tick por lado
1 tick por lado
2 ticks por lado
spread observado
latencia de 0, 100, 500 y 1,000 ms
```

Si no sobrevive, el candidato se cierra sin optimizar.

### Fase 3 — Baselines

| Baseline | Pregunta |
|---|---|
| Fade de retorno ES | ¿$TICK añade información? |
| Fade de rango ES | ¿el evento de breadth es necesario? |
| Señales aleatorias por hora | ¿la selección temporal supera placebo? |
| Banda sobre cierre de `$TICK` | ¿high/low aporta valor? |
| Percentiles rolling | ¿la desviación estándar es necesaria? |
| Long only / short only | ¿qué lado soporta costes? |

### Fase 4 — Warm-up intradía

Probar sin optimizar al máximo:

```text
sin warm-up
6 barras
12 barras
Length/2 = 12 barras
Length = 24 barras
```

### Fase 5 — Correspondencia universe/index

```text
ES con $TICK
ES con $TIKSP
NQ con $TIKND
RTY con $TIKRL
```

La correspondencia debe preregistrarse. No seleccionar el mejor de forma retrospectiva.

### Fase 6 — Señal persistente

```text
1 barra extrema
2 barras consecutivas
2 de 3 barras
extremo + recuperación dentro de banda
```

### Fase 7 — Postpublicación

Congelar la variante publicada y evaluar desde agosto de 2015.

## 25. Encaje en Market State y Event State

### Market State

```text
broad_market_context.net_tick_level
broad_market_context.net_tick_high_low_band_state
broad_market_context.net_tick_extreme_direction
broad_market_context.net_tick_extreme_zdistance
```

### Event State

```text
event_type:
market_breadth_tick_extreme

subject_scope:
NYSE_issue_universe

tradable_subject:
ES

bar_interval:
3m
```

### Outcomes

```text
es_return_3m_15m_30m_60m
MFE
MAE
time_to_target
time_to_stop
exit_reason
same_bar_target_stop_collision
session_close_return
```

## 26. Decisión técnica

```text
IMPLEMENTAR:
sólo después de asegurar datos históricos de $TICK fiables

PRIORIDAD:
media como estrategia
alta como test arquitectónico multi-data

ACEPTAR COMO EDGE:
no

RIESGO PRINCIPAL:
costes y slippage

CONDICIÓN DE CONTINUIDAD:
sobrevivir al menos 0.5 tick por lado

LIVE:
no

GATE PROPUESTO:
NETTICK-DATA-INTEGRITY-EXECUTION-SURVIVAL-GATE
```

---

# Parte III — Ideas transversales del Issue 8

## 27. Normalizar una señal no la vuelve estacionaria

La transformación logarítmica y el z-score rolling ayudan a comparar escalas, pero no garantizan:

```text
independencia;
normalidad;
estabilidad de parámetros;
ausencia de clustering;
invariancia de régimen;
```

La normalización es una representación, no una demostración de edge.

## 28. Una segunda serie es parte del contrato de decisión

En ambas estrategias:

```text
Data1 = instrumento operado
Data2 = fuente informativa externa
```

La segunda serie debe gobernarse con el mismo rigor que el precio de ejecución:

```text
identidad;
timestamp;
revisión;
calendario;
missingness;
latencia;
```

## 29. Cooldown no equivale a independencia

El MRO de Normalized VIX reduce señales repetidas, pero no elimina la dependencia entre operaciones generadas por el mismo episodio de volatilidad.

Debe registrarse:

```text
cluster_id
bars_since_first_extreme
bars_since_previous_signal
vix_regime_duration
```

## 30. Bandas high/low frente a bandas close

Net Tick Fade introduce una idea reusable:

```text
modelar extremos con la distribución de máximos y mínimos,
no con la distribución del cierre.
```

Puede ser útil para:

```text
halts intradía;
spreads extremos;
order-flow bursts;
volatility spikes;
market breadth extremes;
```

Pero requiere evitar auto-inclusión y definir la ventana ex ante.

## 31. Rango simple frente a True Range

La elección de rango simple en Net Tick Fade es una decisión de representación vinculada a la sesión:

```text
True Range incorpora gaps;
@Data.D omite overnight;
el gap sería un artefacto de la vista parcial;
```

Lección TSIS:

> Una feature puede ser matemáticamente válida y, aun así, semánticamente inválida para una vista de datos determinada.

## 32. Expectativa por trade antes que beneficio total

Net Tick Fade gana $22,384.66, cifra que parece atractiva. Sin embargo:

```text
1,722 trades
$13 por trade
PF 1.17
```

La auditoría correcta debe empezar por:

```text
expectancy per trade
break-even cost
capacity
turnover
```

no por el beneficio agregado.

## 33. Market internal como Information Object derivado

El net tick no es una señal del propio contrato. Es una observación agregada del universo.

En TSIS debe preservar:

```text
universe_definition
component_eligibility
exchange_scope
calculation_timestamp
provider_method
```

Sin ello, dos series llamadas `$TICK` pueden no representar exactamente el mismo fenómeno.

## 34. Ideas secundarias del número

El número sugiere varias líneas de investigación reutilizables:

```text
Bollinger Bands sobre VIX para mejorar shorts;
señales consecutivas para reducir ruido;
add-ons tras extremos repetidos;
warm-up intradía antes de activar una feature rolling;
matching entre índice operado y universo de breadth;
long-only en estrategias de volatilidad contraria;
```

La publicidad de Options Volume and Open Interest Indicators no constituye una estrategia validada, pero apunta a una familia de variables de contexto:

```text
options_volume_surprise
put_call_activity
open_interest_change
```

Estas ideas requieren artefactos separados si se convierten en candidatos formales.

---

# Parte IV — Registro consolidado para TSIS

## 35. Candidatos de eventos

### Evento 015-A

```text
event_type:
normalized_implied_volatility_high_extreme

condition:
VIX log-GSS > 1.5

context:
ES SMA20 > SMA200

response published:
LONG ES for 1 daily bar
```

### Evento 015-B

```text
event_type:
normalized_implied_volatility_low_extreme

condition:
VIX log-GSS < -1.5

context:
ES SMA20 < SMA200

response published:
SHORT ES for 1 daily bar
```

### Evento 015-C

```text
event_type:
normalized_vix_extreme_cluster

condition:
repeated extremes inside cooldown window

research use:
measure clustering, decay and regime persistence
```

### Evento 016-A

```text
event_type:
net_tick_lower_band_penetration

condition:
$TICK 3m low < low-band

response published:
LONG ES next 3m open
```

### Evento 016-B

```text
event_type:
net_tick_upper_band_penetration

condition:
$TICK 3m high > high-band

response published:
SHORT ES next 3m open
```

### Evento 016-C

```text
event_type:
net_tick_dual_extreme_bar

condition:
upper and lower penetration in same bar

research use:
resolve ambiguity and characterize breadth volatility
```

## 36. Priorización

| Prioridad | Candidato | Motivo |
|---:|---|---|
| 1 | Normalized VIX postpublicación | reglas simples, horizonte largo OOS y mejor margen por trade |
| 2 | Net Tick data integrity probe | prueba crítica de multi-data y market internals |
| 3 | Net Tick execution survival | sólo continuar si soporta slippage realista |
| 4 | Normalized VIX short ablation | lado más débil y posible fuente de volatilidad innecesaria |
| 5 | Cross-index breadth matching | requiere nuevas fuentes y control de multiplicidad |

## 37. Gates propuestos

### Gate 015-1 — GSS Formula Reconciliation

```text
PASS si:
se reconcilian fórmula, ventana, SD y señales históricas
```

### Gate 015-2 — MRO Documentation Conflict

```text
PASS si:
2/4 replica mejor que 4/4
y queda congelado contractualmente
```

### Gate 015-3 — Postpublication OOS

```text
PASS si:
la especificación 2015 conserva expectativa positiva
sin selección de nuevos parámetros
```

### Gate 016-1 — Net Tick Source Integrity

```text
PASS si:
la serie histórica tiene identidad, timestamp,
universo y missingness gobernados
```

### Gate 016-2 — Intrabar Execution

```text
PASS si:
target/stop y entradas se resuelven con datos de resolución suficiente
```

### Gate 016-3 — Cost Survival

```text
PASS si:
la estrategia sobrevive al menos 0.5 tick por lado
más comisión y spread modelado
```

### Gate 016-4 — Incremental Information

```text
PASS si:
$TICK supera baselines de reversión de ES
en OOS y con igual frecuencia de señales
```

---

# Conclusión

El Issue 8 aporta dos ideas científicamente más interesantes que sus cifras de rendimiento:

1. **Una señal externa debe normalizarse y alinearse temporalmente antes de utilizarse.**
2. **Los market internals pueden representar el estado del universo que subyace a un índice, pero su backtest depende de datos externos, sincronización y costes extremadamente exigentes.**

Normalized VIX es el candidato más sólido de los dos para una réplica prioritaria. Tiene una tesis plausible, 143 operaciones, un beneficio medio razonable y más de una década de datos posteriores a la publicación. Sin embargo, sigue siendo una estrategia optimizada in-sample y contiene una contradicción documental que debe resolverse: `Short_MRO_Length = 2` en tabla, chart y workspace, frente a “4 barras” en la prosa.

Net Tick Fade es más valioso como prueba de arquitectura y como objeto de información que como estrategia publicada. Su beneficio medio de $13 por operación queda prácticamente eliminado por un solo tick agregado de slippage. Antes de estudiar parámetros, debe demostrarse que la serie `$TICK` es reproducible point-in-time y que la estrategia sobrevive a una ejecución mínimamente realista.

Decisión consolidada:

```text
NORMALIZED_VIX:
REPRODUCE_AND_RUN_FROZEN_POSTPUBLICATION_OOS

NET_TICK_FADE:
DATA_AND_EXECUTION_GATE_BEFORE_EDGE_RESEARCH

ISSUE_8_EDGE_STATUS:
UNPROVEN

ISSUE_8_LIVE_STATUS:
NOT_ELIGIBLE
```
